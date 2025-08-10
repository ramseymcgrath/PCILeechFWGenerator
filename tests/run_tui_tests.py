#!/usr/bin/env python3
"""
TUI Test Runner

Runs TUI-specific tests with proper markers and configuration.
"""

import subprocess
import sys
from pathlib import Path


def run_tui_tests():
    """Run TUI tests with proper configuration"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent

    # Run pytest with TUI-specific markers
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(project_root / "tests" / "test_tui_enhanced_features.py"),
        "-v",
        "--tb=short",
        "-m",
        "tui or unit",
        "--no-cov",  # Skip coverage for TUI tests to avoid import issues
    ]

    print("Running TUI Enhanced Features Tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def run_unit_tests_only():
    """Run only unit tests to verify basic functionality"""
    project_root = Path(__file__).parent.parent

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(project_root / "tests" / "test_tui_enhanced_features.py"),
        "-v",
        "--tb=short",
        "-m",
        "unit",
        "--no-cov",
    ]

    print("Running TUI Unit Tests Only...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run TUI tests")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")

    args = parser.parse_args()

    if args.unit_only:
        exit_code = run_unit_tests_only()
    else:
        exit_code = run_tui_tests()

    sys.exit(exit_code)
