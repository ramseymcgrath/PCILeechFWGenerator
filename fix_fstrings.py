#!/usr/bin/env python3
"""
Script to systematically fix f-string syntax errors in build.py
"""

import re
import sys
from pathlib import Path


def fix_fstring_issues(file_path):
    """Fix f-string syntax issues in the given file."""
    with open(file_path, "r") as f:
        content = f.read()

    # Pattern to find problematic f-strings that span multiple lines
    patterns_to_fix = [
        # Pattern 1: f"text {variable} more text"
        (r'f"([^"]*)\{\s*\n\s*([^}]+)\}([^"]*)"', r'safe_format("\1{\2}\3", \2=\2)'),
        # Pattern 2: logger.info(f"text {variable}")
        (
            r'logger\.info\(\s*f"([^"]*)\{\s*\n\s*([^}]+)\}([^"]*)"\s*\)',
            r'log_info_safe(logger, "\1{\2}\3", \2=\2)',
        ),
        # Pattern 3: logger.error(f"text {variable}")
        (
            r'logger\.error\(\s*f"([^"]*)\{\s*\n\s*([^}]+)\}([^"]*)"\s*\)',
            r'log_error_safe(logger, "\1{\2}\3", \2=\2)',
        ),
        # Pattern 4: logger.warning(f"text {variable}")
        (
            r'logger\.warning\(\s*f"([^"]*)\{\s*\n\s*([^}]+)\}([^"]*)"\s*\)',
            r'log_warning_safe(logger, "\1{\2}\3", \2=\2)',
        ),
        # Pattern 5: print(f"text {variable}")
        (
            r'print\(\s*f"([^"]*)\{\s*\n\s*([^}]+)\}([^"]*)"\s*\)',
            r'safe_print_format("\1{\2}\3", \2=\2)',
        ),
    ]

    # Apply fixes
    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

    # Manual fixes for specific known issues
    manual_fixes = [
        # Fix specific multi-line f-strings we know about
        (
            r'f"Applied manufacturing variance for \{\s*\n\s*device_class\.value\s*\}"',
            'safe_format("Applied manufacturing variance for {device_class}", device_class=device_class.value)',
        ),
        (
            r'f"Firmware build completed successfully in \{\s*\n\s*build_results\[\'build_time\'\]:.2f\} seconds"',
            "safe_format(\"Firmware build completed successfully in {build_time:.2f} seconds\", build_time=build_results['build_time'])",
        ),
        (
            r'f"\[✓\] Build completed successfully in \{\s*\n\s*results\[\'build_time\'\]:.2f\} seconds"',
            "safe_format(\"[✓] Build completed successfully in {build_time:.2f} seconds\", build_time=results['build_time'])",
        ),
        (
            r'f"\[✗\] Build failed after \{\s*\n\s*results\[\'build_time\'\]:.2f\} seconds"',
            "safe_format(\"[✗] Build failed after {build_time:.2f} seconds\", build_time=results['build_time'])",
        ),
    ]

    for pattern, replacement in manual_fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

    return content


def main():
    build_py_path = Path("src/build.py")

    if not build_py_path.exists():
        print(f"Error: {build_py_path} not found")
        sys.exit(1)

    print(f"Fixing f-string issues in {build_py_path}")

    # Read and fix the file
    fixed_content = fix_fstring_issues(build_py_path)

    # Write back the fixed content
    with open(build_py_path, "w") as f:
        f.write(fixed_content)

    print("F-string issues fixed!")


if __name__ == "__main__":
    main()
