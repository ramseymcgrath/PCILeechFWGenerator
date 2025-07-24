#!/usr/bin/env python3
"""
Validate SystemVerilog generation patterns to prevent template rendering issues.

This script checks for common generation issues that could cause SystemVerilog
syntax errors or module generation failures, similar to the MSI-X issues that
were previously found and fixed.

Usage:
    python scripts/validate_generation_patterns.py

Exit codes:
    0: All checks passed
    1: Critical issues found that must be fixed
    2: Script error or configuration issue
"""

import os
import re
import sys
from pathlib import Path


def find_critical_generation_issues():
    """Find critical generation issues that must fail CI."""

    print("=== Validating SystemVerilog Generation Patterns ===\n")

    # Simple patterns to catch critical issues
    critical_patterns = [
        # Pattern 1: Functions returning comment strings instead of modules
        {
            "name": "Functions returning comment strings instead of modules",
            "pattern": r'return\s+["\']//[^"\']*["\']',
            "severity": "CRITICAL",
            "description": "Functions returning comment strings instead of proper SystemVerilog modules",
        },
        # Pattern 2: SystemVerilog syntax errors like NUM_MSIX4 instead of NUM_MSIX*4
        {
            "name": "Missing operators in SystemVerilog expressions",
            "pattern": r"NUM_[A-Z_]+\d+(?!\*|_)",
            "severity": "CRITICAL",
            "description": "Missing multiplication operators in array size expressions (e.g., NUM_MSIX4 should be NUM_MSIX*4)",
        },
    ]

    # Files to check - focus on generation modules
    src_dir = Path("src")
    python_files = [
        *src_dir.rglob("**/msix_capability.py"),
        *src_dir.rglob("**/systemverilog_generator.py"),
        *src_dir.rglob("**/advanced_sv_*.py"),
        *src_dir.rglob("**/template_renderer.py"),
    ]

    # If specific files don't exist, check all Python files in relevant directories
    if not python_files:
        python_files = [
            *src_dir.rglob("device_clone/**/*.py"),
            *src_dir.rglob("templating/**/*.py"),
        ]

    critical_issues = []

    for pattern_info in critical_patterns:
        pattern = pattern_info["pattern"]
        compiled_pattern = re.compile(pattern, re.MULTILINE)

        print(f"Checking for: {pattern_info['name']} ({pattern_info['severity']})")
        print(f"Description: {pattern_info['description']}")
        print("-" * 60)

        pattern_issues = []

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                matches = compiled_pattern.finditer(content)
                for match in matches:
                    # Get line number
                    line_num = content[: match.start()].count("\n") + 1

                    issue = {
                        "file": str(file_path),
                        "line": line_num,
                        "pattern": pattern_info["name"],
                        "severity": pattern_info["severity"],
                        "match": match.group(0),
                    }
                    pattern_issues.append(issue)

            except Exception as e:
                print(f"  Error reading {file_path}: {e}")

        if pattern_issues:
            print(f"  ❌ Found {len(pattern_issues)} issues:")
            for issue in pattern_issues:
                print(f"    {issue['file']}:{issue['line']} - {issue['match'][:60]}...")
        else:
            print(f"  ✅ No issues found for this pattern")

        print()
        critical_issues.extend(pattern_issues)

    return critical_issues


def validate_template_variables():
    """Check for critical template variable issues that could cause syntax errors."""

    print("=== Validating Template Variable Usage ===\n")

    # Find all SystemVerilog template files
    template_files = []
    template_dirs = [Path("src/templates"), Path("templates")]

    for template_dir in template_dirs:
        if template_dir.exists():
            for ext in [".sv.j2", ".svh.j2", ".v.j2"]:
                template_files.extend(template_dir.rglob(f"*{ext}"))

    critical_issues = []

    for template_file in template_files:
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for critical SystemVerilog syntax issues in templates
            checks = [
                {
                    "pattern": r"NUM_[A-Z_]+\d+(?!\*|_|\s*\}|\s*\-)",  # NUM_MSIX4 instead of NUM_MSIX*4
                    "issue": "Missing operator in array size expression",
                    "severity": "CRITICAL",
                    "example": "NUM_MSIX4 should be NUM_MSIX*4",
                }
            ]

            for check in checks:
                pattern = re.compile(check["pattern"])
                matches = pattern.finditer(content)

                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    critical_issues.append(
                        {
                            "file": str(template_file),
                            "line": line_num,
                            "issue": check["issue"],
                            "severity": check["severity"],
                            "match": match.group(0),
                            "example": check["example"],
                        }
                    )

        except Exception as e:
            print(f"Error reading template {template_file}: {e}")

    if critical_issues:
        print(f"❌ Found {len(critical_issues)} critical template issues:")
        for issue in critical_issues:
            print(f"  {issue['file']}:{issue['line']} - {issue['issue']}")
            print(f"    Found: {issue['match']}")
            print(f"    {issue['example']}")
            print()
        return critical_issues
    else:
        print("✅ No critical template variable issues found")
        return []


def main():
    """Main function to run critical validation checks."""

    # Change to the project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent  # Go up one level from scripts/
    os.chdir(project_dir)

    print("PCILeech Generation Pattern Validator")
    print("=" * 50)
    print()

    exit_code = 0

    try:
        # Run critical checks only
        critical_issues = find_critical_generation_issues()
        template_issues = validate_template_variables()

        total_critical = len(
            [i for i in critical_issues if i["severity"] in ["CRITICAL"]]
        )
        total_template_critical = len(
            [i for i in template_issues if i["severity"] in ["CRITICAL"]]
        )

        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)

        if total_critical > 0 or total_template_critical > 0:
            print(
                f"❌ CRITICAL ISSUES FOUND: {total_critical + total_template_critical}"
            )
            print("These issues MUST be fixed before merging.")
            exit_code = 1

            if total_critical > 0:
                print(f"\nGeneration Pattern Issues (CRITICAL): {total_critical}")
            if total_template_critical > 0:
                print(f"Template Variable Issues (CRITICAL): {total_template_critical}")

        else:
            print("✅ All validation checks passed!")
            print("No critical generation pattern issues found.")

    except Exception as e:
        print(f"❌ Validation script error: {e}", file=sys.stderr)
        return 2

    return exit_code


if __name__ == "__main__":
    exit(main())
