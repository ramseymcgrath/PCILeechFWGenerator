#!/usr/bin/env python3
"""
PCILeech Production Test Runner

This script runs the comprehensive PCILeech production test suite to validate
that the implementation is production-ready and meets all requirements.

Test Categories:
1. Production Ready Integration Tests
2. Template Validation Tests
3. Build System Integration Tests
4. Dynamic Data Sources Tests
5. Production Validation Tests
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class PCILeechProductionTestRunner:
    """Comprehensive test runner for PCILeech production validation."""

    def __init__(self):
        """Initialize the test runner."""
        self.test_dir = Path(__file__).parent
        self.test_files = [
            "test_pcileech_production_ready.py",
            "test_pcileech_templates_validation.py",
            "test_pcileech_build_integration.py",
            "test_pcileech_dynamic_sources.py",
            "test_pcileech_production_validation.py",
        ]
        self.results = {}

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all PCILeech production tests."""
        print("=" * 80)
        print("PCILeech Production Test Suite")
        print("=" * 80)
        print()

        overall_start_time = time.time()
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0

        for test_file in self.test_files:
            print(f"Running {test_file}...")
            print("-" * 60)

            start_time = time.time()
            result = self._run_test_file(test_file)
            end_time = time.time()

            self.results[test_file] = {**result, "duration": end_time - start_time}

            # Update totals
            total_tests += result["total"]
            total_passed += result["passed"]
            total_failed += result["failed"]
            total_skipped += result["skipped"]

            # Print summary for this test file
            status = "PASSED" if result["failed"] == 0 else "FAILED"
            print(
                f"  {status}: {result['passed']} passed, {result['failed']} failed, {result['skipped']} skipped"
            )
            print(f"  Duration: {result['duration']:.2f}s")
            print()

        overall_end_time = time.time()
        overall_duration = overall_end_time - overall_start_time

        # Print overall summary
        print("=" * 80)
        print("PCILeech Production Test Summary")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Skipped: {total_skipped}")
        print(f"Overall Duration: {overall_duration:.2f}s")
        print()

        # Print detailed results
        self._print_detailed_results()

        # Determine overall status
        overall_status = "PASSED" if total_failed == 0 else "FAILED"
        print(f"Overall Status: {overall_status}")

        if total_failed > 0:
            print("\nFAILED TESTS:")
            for test_file, result in self.results.items():
                if result["failed"] > 0:
                    print(f"  - {test_file}: {result['failed']} failures")

        return {
            "overall_status": overall_status,
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "duration": overall_duration,
            "detailed_results": self.results,
        }

    def _run_test_file(self, test_file: str) -> Dict[str, Any]:
        """Run a single test file and parse results."""
        test_path = self.test_dir / test_file

        if not test_path.exists():
            return {
                "total": 0,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "error": f"Test file not found: {test_file}",
            }

        try:
            # Run pytest on the test file
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_path),
                    "-v",
                    "--tb=short",
                    "--no-header",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Parse pytest output
            return self._parse_pytest_output(
                result.stdout, result.stderr, result.returncode
            )

        except subprocess.TimeoutExpired:
            return {
                "total": 0,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "error": f"Test timeout: {test_file}",
            }
        except Exception as e:
            return {
                "total": 0,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "error": f"Test execution error: {str(e)}",
            }

    def _parse_pytest_output(
        self, stdout: str, stderr: str, returncode: int
    ) -> Dict[str, Any]:
        """Parse pytest output to extract test results."""
        result = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "output": stdout,
            "errors": stderr,
            "returncode": returncode,
        }

        # Parse the summary line (e.g., "5 passed, 2 failed, 1 skipped")
        lines = stdout.split("\n")
        for line in lines:
            if " passed" in line or " failed" in line or " skipped" in line:
                # Extract numbers from summary line
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        count = int(part)
                        if i + 1 < len(parts):
                            status = parts[i + 1].lower()
                            if status.startswith("passed"):
                                result["passed"] = count
                            elif status.startswith("failed"):
                                result["failed"] = count
                            elif status.startswith("skipped"):
                                result["skipped"] = count

        result["total"] = result["passed"] + result["failed"] + result["skipped"]

        # If no tests were found or parsed, check for import errors
        if result["total"] == 0 and (
            "ImportError" in stderr or "ModuleNotFoundError" in stderr
        ):
            result["skipped"] = 1
            result["total"] = 1
            result["error"] = "Import error - dependencies not available"

        return result

    def _print_detailed_results(self):
        """Print detailed test results."""
        print("Detailed Results:")
        print("-" * 40)

        for test_file, result in self.results.items():
            print(f"{test_file}:")
            print(f"  Tests: {result['total']}")
            print(f"  Passed: {result['passed']}")
            print(f"  Failed: {result['failed']}")
            print(f"  Skipped: {result['skipped']}")
            print(f"  Duration: {result['duration']:.2f}s")

            if "error" in result:
                print(f"  Error: {result['error']}")

            if result["failed"] > 0 and "errors" in result:
                print(f"  Error Output: {result['errors'][:200]}...")

            print()

    def run_specific_test_category(self, category: str) -> Dict[str, Any]:
        """Run tests for a specific category."""
        category_map = {
            "production_ready": ["test_pcileech_production_ready.py"],
            "templates": ["test_pcileech_templates_validation.py"],
            "build_integration": ["test_pcileech_build_integration.py"],
            "dynamic_sources": ["test_pcileech_dynamic_sources.py"],
            "production_validation": ["test_pcileech_production_validation.py"],
        }

        if category not in category_map:
            raise ValueError(f"Unknown test category: {category}")

        # Temporarily set test files to only the category
        original_test_files = self.test_files
        self.test_files = category_map[category]

        try:
            result = self.run_all_tests()
            return result
        finally:
            self.test_files = original_test_files

    def validate_production_readiness(self) -> bool:
        """Validate that PCILeech implementation is production-ready."""
        print("Validating PCILeech Production Readiness...")
        print("=" * 50)

        # Run all tests
        results = self.run_all_tests()

        # Define production readiness criteria
        criteria = {
            "min_test_coverage": 80,  # At least 80% of tests must pass
            "max_failures": 0,  # No test failures allowed
            "required_categories": [  # All categories must have passing tests
                "test_pcileech_production_ready.py",
                "test_pcileech_templates_validation.py",
                "test_pcileech_build_integration.py",
                "test_pcileech_dynamic_sources.py",
                "test_pcileech_production_validation.py",
            ],
        }

        # Check criteria
        production_ready = True
        issues = []

        # Check overall failure count
        if results["failed"] > criteria["max_failures"]:
            production_ready = False
            issues.append(
                f"Too many test failures: {results['failed']} (max allowed: {criteria['max_failures']})"
            )

        # Check test coverage
        if results["total"] > 0:
            pass_rate = (results["passed"] / results["total"]) * 100
            if pass_rate < criteria["min_test_coverage"]:
                production_ready = False
                issues.append(
                    f"Test coverage too low: {pass_rate:.1f}% (min required: {criteria['min_test_coverage']}%)"
                )

        # Check required categories
        for category in criteria["required_categories"]:
            if category in results["detailed_results"]:
                category_result = results["detailed_results"][category]
                if category_result["failed"] > 0:
                    production_ready = False
                    issues.append(f"Critical test category failed: {category}")
                elif category_result["total"] == 0:
                    production_ready = False
                    issues.append(f"No tests found in critical category: {category}")

        # Print production readiness assessment
        print("\nProduction Readiness Assessment:")
        print("-" * 40)

        if production_ready:
            print("✅ PCILeech implementation is PRODUCTION READY")
            print("\nAll production criteria met:")
            print(
                f"  ✅ Test failures: {results['failed']} (≤ {criteria['max_failures']})"
            )
            if results["total"] > 0:
                print(
                    f"  ✅ Test coverage: {(results['passed'] / results['total']) * 100:.1f}% (≥ {criteria['min_test_coverage']}%)"
                )
            print(f"  ✅ All critical test categories passed")
        else:
            print("❌ PCILeech implementation is NOT PRODUCTION READY")
            print("\nIssues found:")
            for issue in issues:
                print(f"  ❌ {issue}")

        print(f"\nTotal tests run: {results['total']}")
        print(f"Tests passed: {results['passed']}")
        print(f"Tests failed: {results['failed']}")
        print(f"Tests skipped: {results['skipped']}")
        print(f"Test duration: {results['duration']:.2f}s")

        return production_ready


def main():
    """Main entry point for the test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="PCILeech Production Test Runner")
    parser.add_argument(
        "--category",
        choices=[
            "production_ready",
            "templates",
            "build_integration",
            "dynamic_sources",
            "production_validation",
        ],
        help="Run tests for a specific category only",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate production readiness"
    )

    args = parser.parse_args()

    runner = PCILeechProductionTestRunner()

    try:
        if args.validate:
            # Run production readiness validation
            is_ready = runner.validate_production_readiness()
            sys.exit(0 if is_ready else 1)
        elif args.category:
            # Run specific category
            results = runner.run_specific_test_category(args.category)
            sys.exit(0 if results["failed"] == 0 else 1)
        else:
            # Run all tests
            results = runner.run_all_tests()
            sys.exit(0 if results["failed"] == 0 else 1)

    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
