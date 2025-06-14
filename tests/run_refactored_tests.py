#!/usr/bin/env python3
"""
Test runner for the refactored build system tests.

This script runs all the comprehensive tests for the refactored build system
components and provides detailed reporting on test coverage and results.
"""

import subprocess
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_test_module(module_name, description):
    """Run a specific test module and return results."""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"Module: {module_name}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        # Run pytest on the specific module
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                f"tests/{module_name}",
                "-v",  # Verbose output
                "--tb=short",  # Short traceback format
                "--durations=10",  # Show 10 slowest tests
                "--strict-markers",  # Strict marker checking
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        duration = time.time() - start_time

        print(f"Exit code: {result.returncode}")
        print(f"Duration: {duration:.2f} seconds")

        if result.stdout:
            print("\nSTDOUT:")
            print(result.stdout)

        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)

        return {
            "module": module_name,
            "description": description,
            "success": result.returncode == 0,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except Exception as e:
        print(f"Error running {module_name}: {e}")
        return {
            "module": module_name,
            "description": description,
            "success": False,
            "duration": time.time() - start_time,
            "error": str(e),
        }


def run_coverage_analysis():
    """Run coverage analysis on the refactored modules."""
    print(f"\n{'='*60}")
    print("Running Coverage Analysis")
    print(f"{'='*60}")

    try:
        # Run coverage on the refactored modules
        modules_to_cover = [
            "src/template_renderer.py",
            "src/build_helpers.py",
            "src/tcl_builder.py",
            "src/constants.py",
        ]

        coverage_cmd = [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--source=" + ",".join(modules_to_cover),
            "-m",
            "pytest",
            "tests/test_template_renderer.py",
            "tests/test_build_helpers.py",
            "tests/test_tcl_builder.py",
            "tests/test_constants.py",
            "-v",
        ]

        result = subprocess.run(
            coverage_cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            # Generate coverage report
            report_result = subprocess.run(
                [sys.executable, "-m", "coverage", "report", "-m"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            print("Coverage Report:")
            print(report_result.stdout)

            # Generate HTML coverage report
            html_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "coverage",
                    "html",
                    "--directory=tests/coverage_html",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            if html_result.returncode == 0:
                print("\nHTML coverage report generated in tests/coverage_html/")

        return result.returncode == 0

    except Exception as e:
        print(f"Error running coverage analysis: {e}")
        return False


def check_test_dependencies():
    """Check if required test dependencies are available."""
    print("Checking test dependencies...")

    required_packages = [
        "pytest",
        "coverage",
        "jinja2",  # Required for template_renderer
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing_packages.append(package)

    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False

    return True


def main():
    """Main test runner function."""
    print("PCILeech Firmware Generator - Refactored Build System Tests")
    print("=" * 60)

    # Check dependencies first
    if not check_test_dependencies():
        print("\nPlease install missing dependencies before running tests.")
        return 1

    # Define test modules to run
    test_modules = [
        ("test_template_renderer.py", "Template Rendering System Tests"),
        ("test_build_helpers.py", "Build Helper Functions Tests"),
        ("test_tcl_builder.py", "TCL Builder Class Tests"),
        ("test_constants.py", "Constants Module Tests"),
        ("test_build.py", "Build System Integration Tests (Updated)"),
    ]

    # Run all test modules
    results = []
    total_start_time = time.time()

    for module, description in test_modules:
        result = run_test_module(module, description)
        results.append(result)

    total_duration = time.time() - total_start_time

    # Run coverage analysis
    coverage_success = run_coverage_analysis()

    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")

    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)

    print(f"Total test modules: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Total duration: {total_duration:.2f} seconds")
    print(f"Coverage analysis: {'✓' if coverage_success else '✗'}")

    print(f"\nDetailed Results:")
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"{status} {result['module']} ({result['duration']:.2f}s)")
        if not result["success"] and "error" in result:
            print(f"   Error: {result['error']}")

    # Print recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print(f"{'='*60}")

    if successful_tests == total_tests:
        print("✓ All tests passed! The refactored build system is ready.")
        print("✓ Consider running integration tests with real hardware.")
        print("✓ Review coverage report for any gaps in testing.")
    else:
        print("✗ Some tests failed. Please review the failures above.")
        print("✗ Fix failing tests before deploying the refactored system.")

        # Show which tests failed
        failed_tests = [r for r in results if not r["success"]]
        for failed in failed_tests:
            print(f"   - {failed['module']}: {failed['description']}")

    if not coverage_success:
        print("✗ Coverage analysis failed. Check that coverage is installed.")

    print(f"\nNext steps:")
    print("1. Review test results and fix any failures")
    print("2. Check coverage report in tests/coverage_html/index.html")
    print("3. Run integration tests with actual FPGA boards")
    print("4. Update documentation with new API changes")

    # Return appropriate exit code
    return 0 if successful_tests == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
