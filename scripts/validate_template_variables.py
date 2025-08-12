#!/usr/bin/env python3
"""
Template Variable Validation Script

This script analyzes all Jinja2 templates to identify potentially undefined
variables and ensures all templates have proper variable definitions.

Usage:
    python scripts/validate_template_variables.py [options]

CI Usage:
    python scripts/validate_template_variables.py --strict --format json
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.templating.template_context_validator import (
        TemplateContextValidator,
        analyze_template_variables,
        get_template_requirements,
    )
except ImportError as e:
    print(f"Error: Failed to import template validation modules: {e}")
    print("Make sure you're running this script from the project root.")
    sys.exit(1)


class TemplateVariableAnalyzer:
    """Analyzes templates for undefined variable issues with improved error handling."""

    def __init__(self, template_dir: Path):
        """
        Initialize the analyzer.

        Args:
            template_dir: Root directory containing templates
        """
        self.template_dir = template_dir
        self.validator = TemplateContextValidator()

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

    def analyze_all_templates(self) -> Dict[str, Any]:
        """
        Analyze all templates in the directory.

        Returns:
            Dictionary with analysis results
        """
        results = {
            "total_templates": 0,
            "templates_with_issues": 0,
            "total_issues": 0,
            "issues_by_template": {},
            "undefined_variables": set(),
            "conditional_checks": [],
            "critical_issues": 0,
            "warnings": 0,
            "errors": 0,
        }

        if not self.template_dir.exists():
            self.logger.error(f"Template directory does not exist: {self.template_dir}")
            return results

        # Find all Jinja2 templates
        template_patterns = ["*.j2", "*.jinja", "*.jinja2"]
        templates = []
        for pattern in template_patterns:
            templates.extend(self.template_dir.rglob(pattern))

        results["total_templates"] = len(templates)
        self.logger.info(f"Found {len(templates)} templates to analyze")

        for template_path in templates:
            try:
                rel_path = template_path.relative_to(self.template_dir)
                template_name = str(rel_path)

                issues = self.analyze_template(template_path, template_name)
                if issues:
                    results["templates_with_issues"] += 1
                    results["issues_by_template"][template_name] = issues
                    results["total_issues"] += len(issues)

                    # Categorize issues
                    for issue in issues:
                        if issue["type"] == "undefined_variable":
                            results["undefined_variables"].add(issue["variable"])
                            results["warnings"] += 1  # Changed from critical_issues
                        elif issue["type"] == "conditional_check":
                            results["conditional_checks"].append(
                                {
                                    "template": template_name,
                                    "variable": issue["variable"],
                                    "line": issue["line"],
                                }
                            )
                            results["warnings"] += 1
                        elif issue["type"] == "potentially_undefined":
                            results["warnings"] += 1
                        elif issue["type"] == "error":
                            results["errors"] += 1  # Real errors (file parsing, etc.)
                            results["critical_issues"] += 1

            except Exception as e:
                self.logger.error(f"Failed to analyze {template_path}: {e}")
                results["errors"] += 1
                results["critical_issues"] += 1

        return results

    def analyze_template(
        self, template_path: Path, template_name: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze a single template for variable issues.

        Args:
            template_path: Path to the template file
            template_name: Relative name of the template

        Returns:
            List of issues found
        """
        issues = []

        try:
            with open(template_path, "r") as f:
                content = f.read()
                lines = content.split("\n")

            # Get expected variables from validator
            requirements = self.validator.get_template_requirements(template_name)
            all_expected_vars = (
                requirements.required_vars
                | requirements.optional_vars
                | set(requirements.default_values.keys())
            )

            # Find all variable references in the template
            found_vars = analyze_template_variables(template_path)

            # Check for conditional variable checks ({% if var is defined %})
            for i, line in enumerate(lines, 1):
                # Look for conditional checks
                if_defined_match = re.search(
                    r"\{%\s*if\s+(\w+)(?:\.\w+)*\s*is\s+(?:defined|undefined)", line
                )
                if if_defined_match:
                    var_name = if_defined_match.group(1)
                    issues.append(
                        {
                            "type": "conditional_check",
                            "variable": var_name,
                            "line": i,
                            "content": line.strip(),
                            "suggestion": f"Ensure '{var_name}' is always defined in context with a default value",
                        }
                    )

                # Look for simple {% if var %} without 'is defined'
                simple_if_match = re.search(r"\{%\s*if\s+(\w+)\s*%\}", line)
                if simple_if_match:
                    var_name = simple_if_match.group(1)
                    if var_name not in all_expected_vars:
                        issues.append(
                            {
                                "type": "potentially_undefined",
                                "variable": var_name,
                                "line": i,
                                "content": line.strip(),
                                "suggestion": f"Variable '{var_name}' may be undefined. Add to template requirements.",
                            }
                        )

            # Check for variables used but not in requirements
            for var in found_vars:
                if var not in all_expected_vars and not var.startswith("_"):
                    # Skip loop variables and internal variables
                    if not self._is_loop_variable(var, content):
                        issues.append(
                            {
                                "type": "undefined_variable",
                                "variable": var,
                                "suggestion": f"Ensure '{var}' is provided in template context when rendering",
                            }
                        )

        except Exception as e:
            issues.append(
                {
                    "type": "error",
                    "message": f"Failed to analyze template: {e}",
                }
            )

        return issues

    def _is_loop_variable(self, var_name: str, content: str) -> bool:
        """
        Check if a variable is defined in a for loop.

        Args:
            var_name: Variable name to check
            content: Template content

        Returns:
            True if variable is a loop variable
        """
        # Check if variable is defined in a for loop
        for_pattern = r"\{%\s*for\s+" + re.escape(var_name) + r"\s+in\s+"
        return bool(re.search(for_pattern, content))

    def generate_report(
        self, results: Dict[str, Any], format_type: str = "text"
    ) -> str:
        """
        Generate a formatted report of the analysis.

        Args:
            results: Analysis results
            format_type: Output format ('text' or 'summary')

        Returns:
            Formatted report string
        """
        if format_type == "summary":
            return self._generate_summary_report(results)

        report = []
        report.append("=" * 80)
        report.append("Template Variable Analysis Report")
        report.append("=" * 80)
        report.append("")

        # Summary with color coding for CI
        status_icon = "✅" if results["critical_issues"] == 0 else "❌"
        report.append(f"{status_icon} Summary:")
        report.append(f"  Total templates analyzed: {results['total_templates']}")
        report.append(f"  Templates with issues: {results['templates_with_issues']}")
        report.append(f"  Critical errors: {results['critical_issues']}")
        report.append(f"  Warnings: {results['warnings']}")
        report.append(f"  Total issues: {results['total_issues']}")
        report.append("")

        # Quick status for CI
        if results["critical_issues"] == 0:
            if results["warnings"] == 0:
                report.append("🎉 No template variable issues found!")
            else:
                report.append(
                    f"✅ No critical issues! ({results['warnings']} warnings that can be addressed later)"
                )
        else:
            report.append("❌ Critical errors require attention before deployment.")
        report.append("")

        # Conditional checks that should be removed
        if results["conditional_checks"]:
            report.append("🔍 Conditional Variable Checks (consider removing):")
            report.append("-" * 50)
            for check in results["conditional_checks"]:
                report.append(f"  📄 Template: {check['template']}")
                report.append(
                    f"    🔗 Variable: {check['variable']} (line {check['line']})"
                )
            report.append("")

        # Undefined variables
        if results["undefined_variables"]:
            report.append("⚠️  Potentially Undefined Variables:")
            report.append("-" * 50)
            for var in sorted(results["undefined_variables"]):
                report.append(f"  - {var}")
            report.append("")

        # Detailed issues by template
        if results["issues_by_template"]:
            report.append("📋 Detailed Issues by Template:")
            report.append("-" * 50)
            for template_name, issues in sorted(results["issues_by_template"].items()):
                report.append(f"\n📄 {template_name}:")
                for issue in issues:
                    if issue["type"] == "conditional_check":
                        report.append(
                            f"  ⚠️  Line {issue['line']}: Conditional check for '{issue['variable']}'"
                        )
                        report.append(f"      Code: {issue['content']}")
                        report.append(f"      💡 Fix: {issue['suggestion']}")
                    elif issue["type"] == "undefined_variable":
                        report.append(f"  ⚠️  Undefined variable: '{issue['variable']}'")
                        report.append(f"      💡 Fix: {issue['suggestion']}")
                    elif issue["type"] == "potentially_undefined":
                        report.append(
                            f"  ⚠️  Line {issue['line']}: Potentially undefined '{issue['variable']}'"
                        )
                        report.append(f"      Code: {issue['content']}")
                        report.append(f"      💡 Fix: {issue['suggestion']}")
                    elif issue["type"] == "error":
                        report.append(f"  💥 Error: {issue['message']}")

        # Actionable recommendations
        report.append("")
        report.append("🛠️  Recommended Actions:")
        report.append("-" * 50)
        if results["critical_issues"] > 0:
            report.append("1. ⚡ URGENT: Fix critical errors before deployment")
        if results["warnings"] > 0:
            report.append(
                "2. 🔧 Consider updating template rendering code to provide all variables"
            )
            report.append(
                "3. 🧹 Consider removing conditional 'is defined' checks from templates"
            )
        report.append(
            "4. ✅ Add validation to ensure all required variables are present"
        )
        report.append(
            "5. 🚀 Use strict mode validation in CI/CD pipeline for stricter checks"
        )

        return "\n".join(report)

    def _generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate a concise summary report suitable for CI logs."""
        lines = []

        status = "PASS" if results["critical_issues"] == 0 else "FAIL"
        lines.append(f"Template Validation: {status}")
        lines.append(f"Templates: {results['total_templates']}")
        lines.append(f"Critical Errors: {results['critical_issues']}")
        lines.append(f"Warnings: {results['warnings']}")

        if results["undefined_variables"]:
            # Limit the list to avoid overly long output
            vars_list = sorted(results["undefined_variables"])
            if len(vars_list) > 10:
                vars_display = (
                    ", ".join(vars_list[:10]) + f", ... ({len(vars_list) - 10} more)"
                )
            else:
                vars_display = ", ".join(vars_list)
            lines.append(f"Undefined Variables: {vars_display}")

        return "\n".join(lines)

    def generate_fixes(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate suggested fixes for missing variables.

        Args:
            results: Analysis results

        Returns:
            Dictionary with suggested fixes
        """
        fixes = {
            "missing_variables": {},
            "template_updates": [],
            "context_fixes": {},
        }

        # Group undefined variables by template
        for template_name, issues in results["issues_by_template"].items():
            for issue in issues:
                if issue["type"] == "undefined_variable":
                    var_name = issue["variable"]

                    if template_name not in fixes["missing_variables"]:
                        fixes["missing_variables"][template_name] = []
                    fixes["missing_variables"][template_name].append(var_name)

                    # Suggest where to add the variable in context
                    if template_name not in fixes["context_fixes"]:
                        fixes["context_fixes"][template_name] = []
                    fixes["context_fixes"][template_name].append(
                        f"Add '{var_name}' to context when calling render_template('{template_name}', context)"
                    )

                elif issue["type"] == "conditional_check":
                    fixes["template_updates"].append(
                        {
                            "template": template_name,
                            "line": issue["line"],
                            "old": issue["content"],
                            "new": issue["content"]
                            .replace(" is defined", "")
                            .replace(" is undefined", " not"),
                        }
                    )

        return fixes

    def format_fixes(self, fixes: Dict[str, Any]) -> str:
        """
        Format fixes into a readable string.

        Args:
            fixes: Dictionary of fixes from generate_fixes()

        Returns:
            Formatted string with fix recommendations
        """
        lines = []
        lines.append("=" * 80)
        lines.append("🔧 Required Fixes")
        lines.append("=" * 80)

        if fixes["missing_variables"]:
            lines.append("\n⚠️  Missing Variables by Template:")
            lines.append("-" * 50)
            for template, variables in sorted(fixes["missing_variables"].items()):
                lines.append(f"\n📄 {template}:")
                unique_vars = sorted(set(variables))
                lines.append(f"  Missing: {', '.join(unique_vars)}")

        if fixes["context_fixes"]:
            lines.append("\n🔧 Context Fixes Required:")
            lines.append("-" * 50)
            for template, fixes_list in sorted(fixes["context_fixes"].items()):
                lines.append(f"\n📄 {template}:")
                for fix in fixes_list[:3]:  # Show first 3
                    lines.append(f"  💡 {fix}")
                if len(fixes_list) > 3:
                    lines.append(f"  ... and {len(fixes_list) - 3} more variables")

        if fixes["template_updates"]:
            lines.append("\n📝 Template Updates Needed (remove conditional checks):")
            lines.append("-" * 50)
            for update in fixes["template_updates"][:5]:  # Show first 5
                lines.append(f"  📄 {update['template']} (line {update['line']})")
                lines.append(f"    ❌ Old: {update['old']}")
                lines.append(f"    ✅ New: {update['new']}")
            if len(fixes["template_updates"]) > 5:
                lines.append(f"  ... and {len(fixes['template_updates']) - 5} more")

        return "\n".join(lines)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Analyze templates for undefined variable issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  python scripts/validate_template_variables.py
  
  # CI mode with strict validation
  python scripts/validate_template_variables.py --strict --format json
  
  # Generate detailed fixes
  python scripts/validate_template_variables.py --generate-fixes --verbose
        """,
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=PROJECT_ROOT / "src" / "templates",
        help="Directory containing templates (default: src/templates)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "summary"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--generate-fixes",
        action="store_true",
        help="Generate suggested fixes for the validator",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code if critical errors are found",
    )
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Treat warnings (like undefined variables) as errors",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Write output to file instead of stdout",
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    if not args.template_dir.exists():
        print(f"❌ Error: Template directory '{args.template_dir}' does not exist")
        return 1

    try:
        # Run analysis
        analyzer = TemplateVariableAnalyzer(args.template_dir)
        results = analyzer.analyze_all_templates()

        # Prepare output
        output_content = ""

        if args.format == "json":
            # Convert sets to lists for JSON serialization
            json_results = results.copy()
            json_results["undefined_variables"] = list(results["undefined_variables"])
            output_content = json.dumps(json_results, indent=2)
        else:
            output_content = analyzer.generate_report(results, args.format)

        # Generate fixes if requested
        if args.generate_fixes:
            fixes = analyzer.generate_fixes(results)
            if args.format == "json":
                output_content = json.dumps(
                    {"analysis": json_results, "fixes": fixes}, indent=2
                )
            else:
                output_content += "\n" + analyzer.format_fixes(fixes)

        # Output results
        if args.output_file:
            args.output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output_file, "w") as f:
                f.write(output_content)
            print(f"✅ Results written to {args.output_file}")
        else:
            print(output_content)

        # Exit with appropriate code
        if args.strict and results["critical_issues"] > 0:
            print(
                f"\n❌ Exiting with error: {results['critical_issues']} critical errors found"
            )
            return 1

        if args.warnings_as_errors and results["warnings"] > 0:
            print(
                f"\n❌ Exiting with error: {results['warnings']} warnings treated as errors"
            )
            return 1

        if results["critical_issues"] == 0:
            if results["warnings"] == 0:
                print(f"\n✅ Template validation passed with no issues!")
            else:
                print(
                    f"\n✅ Template validation passed! ({results['warnings']} warnings)"
                )
        else:
            print(f"\n❌ Found {results['critical_issues']} critical errors")

        return 0

    except Exception as e:
        print(f"❌ Template validation failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    main()
