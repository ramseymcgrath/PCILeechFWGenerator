#!/usr/bin/env python3
"""
Comprehensive test runner for PCILeech Firmware Generator.

This script provides a unified interface for running all tests with various options
for different testing scenarios (development, CI, performance, etc.).

Usage:
    python run_tests.py [options]

Examples:
    python run_tests.py --quick          # Run only fast unit tests
    python run_tests.py --full           # Run complete test suite
    python run_tests.py --performance    # Run performance tests
    python run_tests.py --coverage       # Run with coverage reporting
    python run_tests.py --ci             # Run in CI mode
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description="", capture_output=False, check=True):
    """Run a command with optional description and error handling."""
    if description:
        print(f"\n[*] {description}")

    print(f"[+] {cmd}")

    try:
        if capture_output:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=check
            )
            return result.stdout, result.stderr, result.returncode
        else:
            result = subprocess.run(cmd, shell=True, check=check)
            return None, None, result.returncode
    except subprocess.CalledProcessError as e:
        print(f"[!] Command failed with exit code {e.returncode}")
        if capture_output and e.stderr:
            print(f"[!] Error output: {e.stderr}")
        if not check:
            return None, None, e.returncode
        raise


def check_dependencies():
    """Check that required dependencies are installed."""
    print("[*] Checking test dependencies...")

    required_packages = [
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "flake8",
        "black",
        "bandit",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"[!] Missing required packages: {', '.join(missing_packages)}")
        print("[*] Install with: pip install -r requirements-test.txt")
        return False

    print("[✓] All required dependencies are available")
    return True


def run_code_quality_checks():
    """Run code quality and linting checks."""
    print("\n" + "=" * 60)
    print("CODE QUALITY CHECKS")
    print("=" * 60)

    checks = [
        ("black --check --diff .", "Code formatting check (Black)"),
        ("isort --check-only --diff .", "Import sorting check (isort)"),
        (
            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
            "Critical linting (flake8)",
        ),
        (
            "flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics",
            "Full linting (flake8)",
        ),
        ("bandit -r src/ generate.py", "Security scanning (bandit)"),
    ]

    results = {}

    for cmd, description in checks:
        try:
            _, _, returncode = run_command(
                cmd, description, capture_output=True, check=False
            )
            results[description] = returncode == 0
        except Exception as e:
            print(f"[!] {description} failed: {e}")
            results[description] = False

    # Summary
    print("\n[*] Code Quality Summary:")
    for check, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")

    return all(results.values())


def run_unit_tests(coverage=False, verbose=False):
    """Run unit tests."""
    print("\n" + "=" * 60)
    print("UNIT TESTS")
    print("=" * 60)

    cmd_parts = ["pytest", "tests/"]

    # Add markers to exclude integration and performance tests
    cmd_parts.extend(["-m", '"not integration and not performance"'])

    if coverage:
        cmd_parts.extend(
            [
                "--cov=src",
                "--cov=generate",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=xml:coverage.xml",
            ]
        )

    if verbose:
        cmd_parts.append("-v")

    cmd_parts.extend(["--tb=short", "--durations=10", "--junit-xml=junit-unit.xml"])

    cmd = " ".join(cmd_parts)

    try:
        run_command(cmd, "Running unit tests")
        print("[✓] Unit tests passed")
        return True
    except subprocess.CalledProcessError:
        print("[✗] Unit tests failed")
        return False


def run_integration_tests(verbose=False):
    """Run integration tests."""
    print("\n" + "=" * 60)
    print("INTEGRATION TESTS")
    print("=" * 60)

    cmd_parts = ["pytest", "tests/", "-m", '"integration"']

    if verbose:
        cmd_parts.append("-v")

    cmd_parts.extend(
        ["--tb=short", "--junit-xml=junit-integration.xml", "--timeout=300"]
    )

    cmd = " ".join(cmd_parts)

    try:
        run_command(cmd, "Running integration tests")
        print("[✓] Integration tests passed")
        return True
    except subprocess.CalledProcessError:
        print("[✗] Integration tests failed")
        return False


def run_performance_tests():
    """Run performance tests."""
    print("\n" + "=" * 60)
    print("PERFORMANCE TESTS")
    print("=" * 60)

    cmd = 'pytest tests/ -m "performance" --benchmark-only --benchmark-json=benchmark.json'

    try:
        run_command(cmd, "Running performance tests")
        print("[✓] Performance tests passed")
        return True
    except subprocess.CalledProcessError:
        print("[✗] Performance tests failed")
        return False


def run_external_tests(verbose=False):
    """Run external example validation tests."""
    print("\n" + "=" * 60)
    print("EXTERNAL EXAMPLE TESTS")
    print("=" * 60)

    # Specify the external example test files directly
    external_test_files = [
        "tests/test_tcl_validation.py",
        "tests/test_sv_validation.py",
        "tests/test_external_integration.py",
        "tests/test_build_integration.py",
    ]

    cmd_parts = ["pytest"]
    cmd_parts.extend(external_test_files)

    if verbose:
        cmd_parts.append("-v")

    cmd_parts.extend(["--tb=short", "--junit-xml=junit-external.xml"])

    cmd = " ".join(cmd_parts)

    try:
        run_command(cmd, "Running external example tests")
        print("[✓] External example tests passed")
        return True
    except subprocess.CalledProcessError:
        print("[✗] External example tests failed")
        return False


def run_legacy_tests():
    """Run the original test_enhancements.py for backward compatibility."""
    print("\n" + "=" * 60)
    print("LEGACY ENHANCEMENT TESTS")
    print("=" * 60)

    if not Path("test_enhancements.py").exists():
        print("[!] test_enhancements.py not found, skipping legacy tests")
        return True

    try:
        run_command("python test_enhancements.py", "Running legacy enhancement tests")
        print("[✓] Legacy tests passed")
        return True
    except subprocess.CalledProcessError:
        print("[✗] Legacy tests failed")
        return False


def run_security_tests():
    """Run security-focused tests."""
    print("\n" + "=" * 60)
    print("SECURITY TESTS")
    print("=" * 60)

    security_checks = [
        (
            "bandit -r src/ generate.py -f json -o bandit-report.json",
            "Security vulnerability scan",
        ),
        ("safety check", "Dependency vulnerability check"),
    ]

    results = {}

    for cmd, description in security_checks:
        try:
            _, _, returncode = run_command(
                cmd, description, capture_output=True, check=False
            )
            results[description] = returncode == 0
        except Exception as e:
            print(f"[!] {description} failed: {e}")
            results[description] = False

    # Summary
    print("\n[*] Security Test Summary:")
    for check, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")

    return all(results.values())


def generate_test_report(results):
    """Generate a comprehensive test report."""
    print("\n" + "=" * 60)
    print("TEST REPORT SUMMARY")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)

    print(f"\nOverall Results: {passed_tests}/{total_tests} test suites passed")
    print(f"Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

    print("\nDetailed Results:")
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status} {test_name}")

    # Generate artifacts summary
    artifacts = []
    artifact_files = [
        "coverage.xml",
        "htmlcov/index.html",
        "junit-unit.xml",
        "junit-integration.xml",
        "junit-external.xml",
        "benchmark.json",
        "bandit-report.json",
    ]

    for artifact in artifact_files:
        if Path(artifact).exists():
            artifacts.append(artifact)

    if artifacts:
        print("\nGenerated Artifacts:")
        for artifact in artifacts:
            print(f"  - {artifact}")

    return passed_tests == total_tests


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for PCILeech Firmware Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --quick          # Fast unit tests only
  python run_tests.py --full           # Complete test suite
  python run_tests.py --ci             # CI mode (no interactive tests)
  python run_tests.py --coverage       # With coverage reporting
  python run_tests.py --performance    # Performance tests only
  python run_tests.py --external       # External example tests only
        """,
    )

    parser.add_argument("--quick", action="store_true", help="Run only fast unit tests")
    parser.add_argument("--full", action="store_true", help="Run complete test suite")
    parser.add_argument(
        "--ci", action="store_true", help="Run in CI mode (non-interactive)"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage reports"
    )
    parser.add_argument(
        "--performance", action="store_true", help="Run performance tests only"
    )
    parser.add_argument(
        "--security", action="store_true", help="Run security tests only"
    )
    parser.add_argument(
        "--legacy", action="store_true", help="Run legacy enhancement tests only"
    )
    parser.add_argument(
        "--external", action="store_true", help="Run external example tests only"
    )
    parser.add_argument(
        "--no-quality", action="store_true", help="Skip code quality checks"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Set default to quick if no specific mode is selected
    if not any(
        [
            args.quick,
            args.full,
            args.ci,
            args.performance,
            args.security,
            args.legacy,
            args.external,
        ]
    ):
        args.quick = True

    print("PCILeech Firmware Generator - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(
        f"Test Mode: {', '.join([k for k, v in vars(args).items() if v and k != 'verbose'])}"
    )

    start_time = time.time()

    # Check dependencies
    if not check_dependencies():
        return 1

    results = {}

    # Code quality checks (unless disabled)
    if not args.no_quality and not args.performance and not args.legacy:
        results["Code Quality"] = run_code_quality_checks()

    # Security tests
    if args.security or args.full or args.ci:
        results["Security Tests"] = run_security_tests()

    # Legacy tests
    if args.legacy or args.full:
        results["Legacy Enhancement Tests"] = run_legacy_tests()

    # Performance tests
    if args.performance or args.full:
        results["Performance Tests"] = run_performance_tests()

    # External example tests
    if args.external or args.full or args.ci:
        results["External Example Tests"] = run_external_tests(verbose=args.verbose)

    # Unit tests
    if args.quick or args.full or args.ci or not (args.performance or args.external):
        results["Unit Tests"] = run_unit_tests(
            coverage=args.coverage or args.full or args.ci, verbose=args.verbose
        )

    # Integration tests
    if args.full or args.ci:
        results["Integration Tests"] = run_integration_tests(verbose=args.verbose)

    # Generate final report
    elapsed_time = time.time() - start_time
    print(f"\n[*] Total execution time: {elapsed_time:.1f} seconds")

    success = generate_test_report(results)

    if success:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
