#!/usr/bin/env python3
"""Run unit tests for PCILeech FW Generator core logic."""

import sys
import os
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all unit tests and display results."""
    # Discover and run tests
    loader = unittest.TestLoader()
    test_dir = Path(__file__).parent
    suite = loader.discover(str(test_dir), pattern="test_*.py")

    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_module):
    """Run a specific test module."""
    loader = unittest.TestLoader()

    try:
        # Import the test module
        module = __import__(f"test_{test_module}", fromlist=[""])
        suite = loader.loadTestsFromModule(module)

        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return 0 if result.wasSuccessful() else 1
    except ImportError as e:
        print(f"Error: Could not import test module 'test_{test_module}': {e}")
        return 1


def list_available_tests():
    """List all available test modules."""
    test_dir = Path(__file__).parent
    test_files = sorted(test_dir.glob("test_*.py"))

    print("Available test modules:")
    for test_file in test_files:
        module_name = test_file.stem.replace("test_", "")
        print(f"  - {module_name}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_available_tests()
            sys.exit(0)
        else:
            # Run specific test module
            exit_code = run_specific_test(sys.argv[1])
    else:
        # Run all tests
        print("Running all unit tests...")
        print("=" * 70)
        exit_code = run_tests()

    sys.exit(exit_code)
