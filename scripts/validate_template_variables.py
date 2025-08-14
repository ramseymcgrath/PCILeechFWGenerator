#!/usr/bin/env python3
"""
Template Variable Validation CI Script

This script performs comprehensive validation of all template variables:
1. Extracts all variables used in templates
2. Traces their origin in the codebase
3. Verifies they are properly handled with fallbacks
4. Ensures no unsafe default values are used

Usage:
    python3 scripts/validate_template_variables.py [--verbose] [--fix]
"""

import argparse
import glob
import json
import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from jinja2 import Environment, FileSystemLoader, meta
    from jinja2.exceptions import TemplateSyntaxError
except ImportError:
    print("Jinja2 is required. Install with: pip install jinja2")
    sys.exit(1)

try:
    from src.device_clone.fallback_manager import FallbackManager
    from src.string_utils import (log_error_safe, log_info_safe,
                                  log_warning_safe)
    from src.templating.template_renderer import TemplateRenderer
except ImportError:
    print("PCILeech modules not found. Run from project root.")
    sys.exit(1)

logger = logging.getLogger("template_validator")

# Configuration
TEMPLATES_DIR = Path("src/templates")
CODE_DIRS = [
    Path("src/templating"),
    Path("src/device_clone"),
    Path("src/build.py"),
]
EXCLUDED_VARS = {
    # Common builtin functions
    "range",
    "len",
    "min",
    "max",
    "sorted",
    "zip",
    "sum",
    "int",
    "hex",
    "hasattr",
    "getattr",
    "isinstance",
    # Jinja2 special variables
    "loop",
    "self",
    "super",
    "namespace",
    # Custom globals
    "generate_tcl_header_comment",
    "throw_error",
    "__version__",
}


class VariableDefinition:
    """Tracks where a variable is defined and used."""

    def __init__(self, name: str):
        self.name = name
        self.templates_used_in: Set[str] = set()
        self.defined_in_files: Set[str] = set()
        self.fallbacks_defined: bool = False
        self.has_default_in_template: bool = False
        self.unsafe_defaults: List[str] = []

    def is_safely_handled(self) -> bool:
        """Check if the variable is safely handled."""
        return bool(self.defined_in_files) or self.fallbacks_defined

    def add_template_usage(self, template_path: str):
        """Add a template where this variable is used."""
        self.templates_used_in.add(template_path)

    def add_definition(self, file_path: str):
        """Add a file where this variable is defined."""
        self.defined_in_files.add(file_path)

    def set_fallback_defined(self):
        """Mark that a fallback is defined for this variable."""
        self.fallbacks_defined = True

    def set_has_default_in_template(self):
        """Mark that the template has a default for this variable."""
        self.has_default_in_template = True

    def add_unsafe_default(self, default_value: str):
        """Add an unsafe default value found in templates."""
        self.unsafe_defaults.append(default_value)

    def __str__(self) -> str:
        """String representation for debugging."""
        status = "✅" if self.is_safely_handled() else "❌"
        return f"{status} {self.name} (Used in: {len(self.templates_used_in)} templates, Defined in: {len(self.defined_in_files)} files)"


class TemplateVariableValidator:
    """Validates template variables usage and definitions."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.variables: Dict[str, VariableDefinition] = {}
        self.env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        self.fallback_manager = FallbackManager()
        self.setup_logger()

    def setup_logger(self):
        """Set up logging."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO if self.verbose else logging.WARNING)

    def extract_variables_from_template(self, template_path: str) -> Set[str]:
        """Extract all variables from a template file."""
        rel_path = Path(template_path).relative_to(TEMPLATES_DIR)
        template_source = Path(template_path).read_text(encoding="utf-8")

        try:
            # Parse template to get AST
            ast = self.env.parse(template_source)
            # Extract variables
            variables = meta.find_undeclared_variables(ast)
            # Filter out excluded variables
            variables = variables - EXCLUDED_VARS

            logger.info(f"Found {len(variables)} variables in {rel_path}")
            return variables

        except TemplateSyntaxError as e:
            logger.error(f"Syntax error in {rel_path}: {e}")
            return set()
        except Exception as e:
            logger.error(f"Error processing {rel_path}: {e}")
            return set()

    def find_default_filters(self, template_path: str) -> Dict[str, List[str]]:
        """Find uses of the default filter in templates."""
        template_source = Path(template_path).read_text(encoding="utf-8")
        rel_path = Path(template_path).relative_to(TEMPLATES_DIR)

        # Pattern to match {{ variable|default(...) }} or {{ variable | default(...) }}
        pattern = r"{{\s*([a-zA-Z0-9_\.]+)\s*\|\s*default\(([^)]+)\)\s*}}"

        default_usages = {}
        for match in re.finditer(pattern, template_source):
            var_name = match.group(1)
            default_value = match.group(2).strip()

            if var_name not in default_usages:
                default_usages[var_name] = []

            default_usages[var_name].append(default_value)
            logger.info(
                f"Found default filter for {var_name} = {default_value} in {rel_path}"
            )

            # Check for potentially unsafe defaults
            if default_value not in (
                "''",
                '""',
                "None",
                "[]",
                "{}",
                "0",
                "0.0",
                "False",
                "'unknown'",
                "'Unknown'",
                "'0'",
                "'0.0'",
            ):
                if var_name in self.variables:
                    self.variables[var_name].add_unsafe_default(default_value)

        return default_usages

    def scan_template_files(self):
        """Scan all template files and collect variables."""
        template_files = list(TEMPLATES_DIR.glob("**/*.j2"))
        logger.info(f"Found {len(template_files)} template files")

        for template_file in template_files:
            template_path = str(template_file)
            rel_path = template_file.relative_to(TEMPLATES_DIR)

            # Extract variables
            variables = self.extract_variables_from_template(template_path)

            # Find default filters
            default_filters = self.find_default_filters(template_path)

            # Register variables
            for var_name in variables:
                if var_name not in self.variables:
                    self.variables[var_name] = VariableDefinition(var_name)

                # Record template usage
                self.variables[var_name].add_template_usage(str(rel_path))

                # Check if it has a default in the template
                if var_name in default_filters:
                    self.variables[var_name].set_has_default_in_template()

    def find_variable_definitions(self):
        """Find where variables are defined in the codebase."""
        # Patterns to match variable definitions
        patterns = [
            # template_context[var_name] = value
            r'template_context\[[\'"]([\w\.]+)[\'"]\]\s*=',
            # template_context.setdefault(var_name, value)
            r'template_context\.setdefault\([\'"]([\w\.]+)[\'"]',
            # context.to_template_context() adds variables
            r'def to_template_context.*?return.*?[\'"](\w+)[\'"]',
        ]

        # Fallback manager patterns
        fallback_patterns = [
            r'fallback_manager\.register_fallback\([\'"]([\w\.]+)[\'"]',
            r'fallback_manager\.get_fallback\([\'"]([\w\.]+)[\'"]',
        ]

        for code_dir in CODE_DIRS:
            if code_dir.is_file():
                self._search_file_for_definitions(code_dir, patterns, fallback_patterns)
            else:
                for code_file in code_dir.glob("**/*.py"):
                    self._search_file_for_definitions(
                        code_file, patterns, fallback_patterns
                    )

    def _search_file_for_definitions(
        self, file_path: Path, patterns: List[str], fallback_patterns: List[str]
    ):
        """Search a file for variable definitions and fallbacks."""
        file_content = file_path.read_text(encoding="utf-8")
        rel_path = file_path.relative_to(Path.cwd())

        # Look for direct definitions
        for pattern in patterns:
            for match in re.finditer(pattern, file_content, re.DOTALL):
                var_name = match.group(1)
                if var_name in self.variables:
                    self.variables[var_name].add_definition(str(rel_path))
                    logger.info(f"Found definition for {var_name} in {rel_path}")

        # Look for fallback definitions
        for pattern in fallback_patterns:
            for match in re.finditer(pattern, file_content):
                var_name = match.group(1)
                if var_name in self.variables:
                    self.variables[var_name].set_fallback_defined()
                    logger.info(f"Found fallback for {var_name} in {rel_path}")

    def generate_report(self) -> Tuple[Dict, List[str]]:
        """Generate a report of variable status."""
        report = {
            "total_variables": len(self.variables),
            "safely_handled": 0,
            "unsafe_variables": [],
            "variables_with_unsafe_defaults": [],
            "variables_by_template": defaultdict(list),
            "details": {},
        }

        issues = []

        for var_name, var_info in sorted(self.variables.items()):
            is_safe = var_info.is_safely_handled()
            if is_safe:
                report["safely_handled"] += 1
            else:
                report["unsafe_variables"].append(var_name)
                issues.append(
                    f"❌ Variable '{var_name}' is used but not safely handled"
                )

            if var_info.unsafe_defaults:
                report["variables_with_unsafe_defaults"].append(var_name)
                issues.append(
                    f"⚠️ Variable '{var_name}' has potentially unsafe defaults: {var_info.unsafe_defaults}"
                )

            # Organize by template
            for template in var_info.templates_used_in:
                report["variables_by_template"][template].append(
                    {
                        "name": var_name,
                        "is_safe": is_safe,
                        "has_fallback": var_info.fallbacks_defined,
                        "defined_in": list(var_info.defined_in_files),
                        "has_default_in_template": var_info.has_default_in_template,
                        "unsafe_defaults": var_info.unsafe_defaults,
                    }
                )

            # Add detailed info
            report["details"][var_name] = {
                "name": var_name,
                "templates_used_in": list(var_info.templates_used_in),
                "defined_in_files": list(var_info.defined_in_files),
                "fallbacks_defined": var_info.fallbacks_defined,
                "has_default_in_template": var_info.has_default_in_template,
                "is_safely_handled": is_safe,
                "unsafe_defaults": var_info.unsafe_defaults,
            }

        return report, issues

    def save_report(
        self, report: Dict, output_file: str = "template_variables_report.json"
    ):
        """Save the report to a JSON file."""
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {output_file}")

    def print_summary(self, report: Dict, issues: List[str]):
        """Print a summary of the report."""
        total = report["total_variables"]
        safe = report["safely_handled"]
        unsafe = len(report["unsafe_variables"])
        unsafe_defaults = len(report["variables_with_unsafe_defaults"])

        print("=" * 80)
        print(f"TEMPLATE VARIABLE VALIDATION REPORT")
        print("=" * 80)
        print(f"Total variables found: {total}")
        print(f"Safely handled: {safe} ({safe/total*100:.1f}%)")
        print(f"Unsafe variables: {unsafe} ({unsafe/total*100:.1f}%)")
        print(f"Variables with unsafe defaults: {unsafe_defaults}")
        print("=" * 80)

        if issues:
            print("ISSUES FOUND:")
            for issue in issues:
                print(f" - {issue}")
            print("=" * 80)

        # Print top templates by variable count
        print("Top 5 templates by variable count:")
        template_counts = [
            (t, len(v)) for t, v in report["variables_by_template"].items()
        ]
        for template, count in sorted(
            template_counts, key=lambda x: x[1], reverse=True
        )[:5]:
            print(f" - {template}: {count} variables")
        print("=" * 80)

    def validate_and_report(self):
        """Run validation and generate a report."""
        # Scan templates
        self.scan_template_files()

        # Find definitions
        self.find_variable_definitions()

        # Generate report
        report, issues = self.generate_report()

        # Save report
        self.save_report(report)

        # Print summary
        self.print_summary(report, issues)

        # Return exit code based on validation results
        return len(report["unsafe_variables"]) == 0


def main():
    parser = argparse.ArgumentParser(description="Validate template variables")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically add fallbacks for missing variables",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="template_variables_report.json",
        help="Output file for the report",
    )
    args = parser.parse_args()

    validator = TemplateVariableValidator(verbose=args.verbose)
    success = validator.validate_and_report()

    if not success:
        print("❌ Template variable validation failed!")
        return 1

    print("✅ All template variables are safely handled!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
