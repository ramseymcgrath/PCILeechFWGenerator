#!/usr/bin/env python3
"""
Enhanced test runner for the PCILeech firmware generator.

Runs comprehensive unit tests for important functionality areas
that were previously under-tested.
"""

import sys
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def discover_and_run_enhanced_tests():
    """Discover and run enhanced unit tests."""

    # Test modules to run
    test_modules = [
        "test_repo_manager",
        "test_config_manager_enhanced",
        "test_systemverilog_generation",
        "test_tcl_generation",
        "test_error_handling_enhanced",
    ]

    print("=" * 70)
    print("PCILeech Firmware Generator - Enhanced Unit Tests")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Load tests from each module
    for module_name in test_modules:
        try:
            print(f"Loading tests from {module_name}...")
            module_suite = loader.loadTestsFromName(module_name)
            suite.addTest(module_suite)
            print(f"  ✓ Loaded {module_suite.countTestCases()} tests")
        except Exception as e:
            print(f"  ✗ Failed to load {module_name}: {e}")

    print()
    print(f"Total tests loaded: {suite.countTestCases()}")
    print("=" * 70)
    print()

    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2, stream=sys.stdout, descriptions=True, failfast=False
    )

    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    if result.failures:
        print()
        print("FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print()
        print("ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")

    print("=" * 70)

    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0


def run_specific_test_category(category):
    """Run tests for a specific category."""

    category_modules = {
        "repo": ["test_repo_manager"],
        "config": ["test_config_manager_enhanced"],
        "systemverilog": ["test_systemverilog_generation"],
        "tcl": ["test_tcl_generation"],
        "error": ["test_error_handling_enhanced"],
        "all": [
            "test_repo_manager",
            "test_config_manager_enhanced",
            "test_systemverilog_generation",
            "test_tcl_generation",
            "test_error_handling_enhanced",
        ],
    }

    if category not in category_modules:
        print(f"Unknown category: {category}")
        print(f"Available categories: {', '.join(category_modules.keys())}")
        return False

    print(f"Running {category} tests...")
    print("=" * 50)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for module_name in category_modules[category]:
        try:
            module_suite = loader.loadTestsFromName(module_name)
            suite.addTest(module_suite)
            print(f"Loaded {module_suite.countTestCases()} tests from {module_name}")
        except Exception as e:
            print(f"Failed to load {module_name}: {e}")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return len(result.failures) == 0 and len(result.errors) == 0


def main():
    """Main entry point."""

    if len(sys.argv) > 1:
        category = sys.argv[1]
        success = run_specific_test_category(category)
    else:
        success = discover_and_run_enhanced_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
