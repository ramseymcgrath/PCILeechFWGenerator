#!/usr/bin/env python3
"""
Script to validate and report on template variable usage.

This script analyzes all Jinja2 templates to identify potentially undefined
variables and suggests fixes to ensure all variables are properly defined.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import re
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.templating.template_context_validator import (
    TemplateContextValidator,
    analyze_template_variables,
    get_template_requirements,
)


class TemplateVariableAnalyzer:
    """Analyzes templates for undefined variable issues."""

    def __init__(self, template_dir: Path):
        """
        Initialize the analyzer.

        Args:
            template_dir: Root directory containing templates
        """
        self.template_dir = template_dir
        self.validator = TemplateContextValidator()
        self.issues: List[Dict[str, Any]] = []

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
        }

        # Find all Jinja2 templates
        templates = list(self.template_dir.rglob("*.j2"))
        results["total_templates"] = len(templates)

        for template_path in templates:
            rel_path = template_path.relative_to(self.template_dir)
            template_name = str(rel_path)

            issues = self.analyze_template(template_path, template_name)
            if issues:
                results["templates_with_issues"] += 1
                results["issues_by_template"][template_name] = issues
                results["total_issues"] += len(issues)

                for issue in issues:
                    if issue["type"] == "undefined_variable":
                        results["undefined_variables"].add(issue["variable"])
                    elif issue["type"] == "conditional_check":
                        results["conditional_checks"].append(
                            {
                                "template": template_name,
                                "variable": issue["variable"],
                                "line": issue["line"],
                            }
                        )

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

    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a human-readable report of the analysis.

        Args:
            results: Analysis results

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("Template Variable Analysis Report")
        report.append("=" * 80)
        report.append("")

        # Summary
        report.append("Summary:")
        report.append(f"  Total templates analyzed: {results['total_templates']}")
        report.append(f"  Templates with issues: {results['templates_with_issues']}")
        report.append(f"  Total issues found: {results['total_issues']}")
        report.append("")

        # Conditional checks that should be removed
        if results["conditional_checks"]:
            report.append("Conditional Variable Checks (should be removed):")
            report.append("-" * 40)
            for check in results["conditional_checks"]:
                report.append(f"  Template: {check['template']}")
                report.append(
                    f"    Variable: {check['variable']} (line {check['line']})"
                )
            report.append("")

        # Undefined variables
        if results["undefined_variables"]:
            report.append("Potentially Undefined Variables:")
            report.append("-" * 40)
            for var in sorted(results["undefined_variables"]):
                report.append(f"  - {var}")
            report.append("")

        # Detailed issues by template
        if results["issues_by_template"]:
            report.append("Detailed Issues by Template:")
            report.append("-" * 40)
            for template_name, issues in sorted(results["issues_by_template"].items()):
                report.append(f"\n{template_name}:")
                for issue in issues:
                    if issue["type"] == "conditional_check":
                        report.append(
                            f"  Line {issue['line']}: Conditional check for '{issue['variable']}'"
                        )
                        report.append(f"    Code: {issue['content']}")
                        report.append(f"    Fix: {issue['suggestion']}")
                    elif issue["type"] == "undefined_variable":
                        report.append(f"  Undefined variable: '{issue['variable']}'")
                        report.append(f"    Fix: {issue['suggestion']}")
                    elif issue["type"] == "potentially_undefined":
                        report.append(
                            f"  Line {issue['line']}: Potentially undefined '{issue['variable']}'"
                        )
                        report.append(f"    Code: {issue['content']}")
                        report.append(f"    Fix: {issue['suggestion']}")

        # Recommendations
        report.append("")
        report.append("Recommendations:")
        report.append("-" * 40)
        report.append(
            "1. Fix template rendering code to provide all required variables"
        )
        report.append("2. Remove conditional 'is defined' checks from templates")
        report.append(
            "3. Add validation to ensure all required variables are present before rendering"
        )
        report.append(
            "4. Use strict mode validation in CI/CD pipeline to catch missing variables"
        )

        return "\n".join(report)

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


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Analyze templates for undefined variable issues"
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=project_root / "src" / "templates",
        help="Directory containing templates (default: src/templates)",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
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
        help="Exit with error code if issues are found",
    )

    args = parser.parse_args()

    if not args.template_dir.exists():
        print(f"Error: Template directory '{args.template_dir}' does not exist")
        sys.exit(1)

    # Run analysis
    analyzer = TemplateVariableAnalyzer(args.template_dir)
    results = analyzer.analyze_all_templates()

    # Output results
    if args.output == "json":
        # Convert sets to lists for JSON serialization
        results["undefined_variables"] = list(results["undefined_variables"])
        print(json.dumps(results, indent=2))
    else:
        report = analyzer.generate_report(results)
        print(report)

    # Generate fixes if requested
    if args.generate_fixes:
        fixes = analyzer.generate_fixes(results)
        print("\n" + "=" * 80)
        print("Required Fixes:")
        print("=" * 80)

        if fixes["missing_variables"]:
            print("\nMissing Variables by Template:")
            print("-" * 40)
            for template, variables in sorted(fixes["missing_variables"].items()):
                print(f"\n{template}:")
                print(f"  Missing: {', '.join(sorted(set(variables)))}")

        if fixes["context_fixes"]:
            print("\nContext Fixes Required:")
            print("-" * 40)
            for template, fixes_list in sorted(fixes["context_fixes"].items()):
                print(f"\n{template}:")
                for fix in fixes_list[:3]:  # Show first 3
                    print(f"  - {fix}")
                if len(fixes_list) > 3:
                    print(f"  ... and {len(fixes_list) - 3} more variables")

        if fixes["template_updates"]:
            print("\nTemplate Updates Needed (remove conditional checks):")
            print("-" * 40)
            for update in fixes["template_updates"][:5]:  # Show first 5
                print(f"  {update['template']} (line {update['line']})")
                print(f"    Old: {update['old']}")
                print(f"    New: {update['new']}")
            if len(fixes["template_updates"]) > 5:
                print(f"  ... and {len(fixes['template_updates']) - 5} more")

    # Exit with error if strict mode and issues found
    if args.strict and results["total_issues"] > 0:
        sys.exit(1)

    return 0


if __name__ == "__main__":
    main()
