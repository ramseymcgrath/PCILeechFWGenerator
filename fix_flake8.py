#!/usr/bin/env python3
"""
Script to automatically fix common flake8 issues.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def run_autopep8():
    """Run autopep8 to fix line length and other formatting issues."""
    print("Running autopep8 to fix formatting issues...")
    try:
        subprocess.run(
            [
                "autopep8",
                "--in-place",
                "--recursive",
                "--aggressive",
                "--aggressive",
                "--max-line-length=79",
                ".",
            ],
            check=True,
        )
        print("✓ autopep8 completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ autopep8 failed: {e}")
    except FileNotFoundError:
        print("autopep8 not found, installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "autopep8"], check=True)
        subprocess.run(
            [
                "autopep8",
                "--in-place",
                "--recursive",
                "--aggressive",
                "--aggressive",
                "--max-line-length=79",
                ".",
            ],
            check=True,
        )


def run_autoflake():
    """Run autoflake to remove unused imports and variables."""
    print("Running autoflake to remove unused imports...")
    try:
        subprocess.run(
            [
                "autoflake",
                "--in-place",
                "--recursive",
                "--remove-all-unused-imports",
                "--remove-unused-variables",
                "--remove-duplicate-keys",
                ".",
            ],
            check=True,
        )
        print("✓ autoflake completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ autoflake failed: {e}")
    except FileNotFoundError:
        print("autoflake not found, installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "autoflake"], check=True
        )
        subprocess.run(
            [
                "autoflake",
                "--in-place",
                "--recursive",
                "--remove-all-unused-imports",
                "--remove-unused-variables",
                "--remove-duplicate-keys",
                ".",
            ],
            check=True,
        )


def fix_f_strings():
    """Fix f-strings that don't have placeholders."""
    print("Fixing f-strings without placeholders...")

    for root, dirs, files in os.walk("."):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Find f-strings without placeholders
                    original_content = content

                    # Pattern to match f-strings without {} placeholders
                    pattern = r'"([^"]*)"'

                    def replace_f_string(match):
                        string_content = match.group(1)
                        if "{" not in string_content:
                            return f'"{string_content}"'
                        return match.group(0)

                    content = re.sub(pattern, replace_f_string, content)

                    # Also handle single quotes
                    pattern = r"f'([^']*)'"
                    content = re.sub(pattern, replace_f_string, content)

                    if content != original_content:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"  Fixed f-strings in {filepath}")

                except Exception as e:
                    print(f"  Error processing {filepath}: {e}")


def fix_whitespace_issues():
    """Fix whitespace issues like blank lines with whitespace."""
    print("Fixing whitespace issues...")

    for root, dirs, files in os.walk("."):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    # Remove trailing whitespace from blank lines
                    fixed_lines = []
                    changed = False

                    for line in lines:
                        if line.strip() == "" and line != "\n":
                            fixed_lines.append("\n")
                            changed = True
                        else:
                            fixed_lines.append(line)

                    if changed:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.writelines(fixed_lines)
                        print(f"  Fixed whitespace in {filepath}")

                except Exception as e:
                    print(f"  Error processing {filepath}: {e}")


def main():
    """Main function to run all fixes."""
    print("Starting flake8 fixes...")

    # Run autoflake first to remove unused imports
    run_autoflake()

    # Run autopep8 to fix formatting
    run_autopep8()

    # Fix f-strings manually
    fix_f_strings()

    # Fix whitespace issues
    fix_whitespace_issues()

    print("\nRunning flake8 to check remaining issues...")
    try:
        result = subprocess.run(["flake8", "."], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ All flake8 issues fixed!")
        else:
            print("Remaining flake8 issues:")
            print(result.stdout)
    except FileNotFoundError:
        print("flake8 not found, please install it to check results")


if __name__ == "__main__":
    main()
