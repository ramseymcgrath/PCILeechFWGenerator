#!/usr/bin/env python3
"""
PCILeech Integration Test Runner

This script runs all PCILeech integration tests and provides comprehensive
validation of the PCILeech integration implementation.
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any

# Add src directory to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


class PCILeechTestRunner:
    """Test runner for PCILeech integration tests."""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0

    def run_test_file(self, test_file: Path) -> Dict[str, Any]:
        """Run a single test file and return results."""
        print(f"\n{'='*60}")
        print(f"Running: {test_file.name}")
        print(f"{'='*60}")

        start_time = time.time()

        try:
            # Try to run with pytest first
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                status = "PASSED"
                self.passed_tests += 1
            else:
                status = "FAILED"
                self.failed_tests += 1

        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
            self.failed_tests += 1
            result = None
        except FileNotFoundError:
            # Pytest not available, try running directly
            try:
                result = subprocess.run(
                    [sys.executable, str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode == 0:
                    status = "PASSED"
                    self.passed_tests += 1
                else:
                    status = "FAILED"
                    self.failed_tests += 1

            except Exception as e:
                status = "ERROR"
                self.failed_tests += 1
                result = None
                print(f"Error running {test_file.name}: {e}")

        end_time = time.time()
        duration = end_time - start_time

        test_result = {
            "file": test_file.name,
            "status": status,
            "duration": duration,
            "result": result,
        }

        # Print immediate results
        print(f"Status: {status}")
        print(f"Duration: {duration:.2f}s")

        if result and result.stdout:
            print("STDOUT:")
            print(result.stdout)

        if result and result.stderr and status != "PASSED":
            print("STDERR:")
            print(result.stderr)

        return test_result

    def run_manual_integration_tests(self) -> Dict[str, Any]:
        """Run manual integration tests that don't require pytest."""
        print(f"\n{'='*60}")
        print("Running Manual Integration Tests")
        print(f"{'='*60}")

        start_time = time.time()

        try:
            # Import and run the original integration test
            from test_pcileech_integration import main as run_integration_test

            result_code = run_integration_test()

            if result_code == 0:
                status = "PASSED"
                self.passed_tests += 1
            else:
                status = "FAILED"
                self.failed_tests += 1

        except Exception as e:
            status = "ERROR"
            self.failed_tests += 1
            print(f"Error running manual integration tests: {e}")

        end_time = time.time()
        duration = end_time - start_time

        test_result = {
            "file": "manual_integration_tests",
            "status": status,
            "duration": duration,
            "result": None,
        }

        print(f"Status: {status}")
        print(f"Duration: {duration:.2f}s")

        return test_result

    def validate_pcileech_components(self) -> Dict[str, Any]:
        """Validate PCILeech components are properly integrated."""
        print(f"\n{'='*60}")
        print("Validating PCILeech Components")
        print(f"{'='*60}")

        start_time = time.time()
        validation_results = []

        # Test 1: Validate constants
        try:
            from src.device_clone.constants import (
                PCILEECH_TCL_SCRIPT_FILES,
                PCILEECH_PROJECT_SCRIPT,
                PCILEECH_BUILD_SCRIPT,
            )

            assert len(PCILEECH_TCL_SCRIPT_FILES) == 2
            assert PCILEECH_PROJECT_SCRIPT == "vivado_generate_project.tcl"
            assert PCILEECH_BUILD_SCRIPT == "vivado_build.tcl"

            validation_results.append("✓ PCILeech constants validation passed")

        except Exception as e:
            validation_results.append(f"✗ PCILeech constants validation failed: {e}")

        # Test 2: Validate board configurations
        try:
            from src.device_clone.board_config import (
                get_pcileech_board_config,
                PCILEECH_BOARD_CONFIG,
            )

            expected_boards = [
                "pcileech_35t325_x4",
                "pcileech_75t484_x1",
                "pcileech_100t484_x1",
            ]

            for board in expected_boards:
                assert board in PCILEECH_BOARD_CONFIG
                config = get_pcileech_board_config(board)
                assert "fpga_part" in config
                assert "fpga_family" in config
                assert "pcie_ip_type" in config

            validation_results.append(
                "✓ PCILeech board configurations validation passed"
            )

        except Exception as e:
            validation_results.append(
                f"✗ PCILeech board configurations validation failed: {e}"
            )

        # Test 3: Validate SystemVerilog generator integration
        try:
            from src.templating.systemverilog_generator import PCILeechOutput

            output = PCILeechOutput(
                src_dir="src",
                ip_dir="ip",
                use_pcileech_structure=True,
                generate_explicit_file_lists=True,
            )

            assert output.src_dir == "src"
            assert output.ip_dir == "ip"
            assert output.use_pcileech_structure is True
            assert isinstance(output.systemverilog_files, list)

            validation_results.append(
                "✓ SystemVerilog generator PCILeech integration validation passed"
            )

        except Exception as e:
            validation_results.append(
                f"✗ SystemVerilog generator PCILeech integration validation failed: {e}"
            )

        # Test 4: Validate TCL builder integration
        try:
            from src.templating.tcl_builder import BuildContext, TCLScriptType

            context = BuildContext(
                board_name="pcileech_35t325_x4",
                fpga_part="xc7a35tcsg324-2",
                fpga_family="7series",
                pcie_ip_type="axi_pcie",
                max_lanes=4,
                supports_msi=True,
                supports_msix=False,
            )

            template_context = context.to_template_context()
            assert "pcileech" in template_context
            assert template_context["pcileech"]["src_dir"] == "src"
            assert template_context["pcileech"]["ip_dir"] == "ip"

            validation_results.append(
                "✓ TCL builder PCILeech integration validation passed"
            )

        except Exception as e:
            validation_results.append(
                f"✗ TCL builder PCILeech integration validation failed: {e}"
            )

        # Test 5: Validate file manager integration
        try:
            import tempfile
            from src.file_management.file_manager import FileManager

            with tempfile.TemporaryDirectory() as temp_dir:
                manager = FileManager(Path(temp_dir))
                directories = manager.create_pcileech_structure()

                assert "src" in directories
                assert "ip" in directories
                assert directories["src"].exists()
                assert directories["ip"].exists()

            validation_results.append(
                "✓ File manager PCILeech integration validation passed"
            )

        except Exception as e:
            validation_results.append(
                f"✗ File manager PCILeech integration validation failed: {e}"
            )

        # Test 6: Validate template files exist
        try:
            template_dir = Path(__file__).parent.parent / "src" / "templates" / "tcl"

            pcileech_templates = ["pcileech_generate_project.j2", "pcileech_build.j2"]

            for template in pcileech_templates:
                template_path = template_dir / template
                assert template_path.exists(), f"Template {template} not found"

            validation_results.append("✓ PCILeech template files validation passed")

        except Exception as e:
            validation_results.append(
                f"✗ PCILeech template files validation failed: {e}"
            )

        end_time = time.time()
        duration = end_time - start_time

        # Print validation results
        for result in validation_results:
            print(result)

        # Determine overall status
        failed_validations = [r for r in validation_results if r.startswith("✗")]
        if len(failed_validations) == 0:
            status = "PASSED"
            self.passed_tests += 1
        else:
            status = "FAILED"
            self.failed_tests += 1

        test_result = {
            "file": "component_validation",
            "status": status,
            "duration": duration,
            "result": validation_results,
        }

        print(f"Status: {status}")
        print(f"Duration: {duration:.2f}s")

        return test_result

    def run_all_tests(self) -> None:
        """Run all PCILeech integration tests."""
        print("PCILeech Integration Test Suite")
        print("=" * 80)

        start_time = time.time()

        # Find all test files
        test_files = [
            self.test_dir / "test_pcileech_integration.py",
            self.test_dir / "test_pcileech_tcl_templates.py",
            self.test_dir / "test_pcileech_systemverilog.py",
            self.test_dir / "test_pcileech_board_config.py",
        ]

        # Run component validation first
        self.results["component_validation"] = self.validate_pcileech_components()
        self.total_tests += 1

        # Run manual integration tests
        self.results["manual_integration"] = self.run_manual_integration_tests()
        self.total_tests += 1

        # Run pytest-based tests
        for test_file in test_files:
            if test_file.exists():
                self.results[test_file.name] = self.run_test_file(test_file)
                self.total_tests += 1
            else:
                print(f"Warning: Test file {test_file.name} not found")

        end_time = time.time()
        total_duration = end_time - start_time

        # Print summary
        self.print_summary(total_duration)

    def print_summary(self, total_duration: float) -> None:
        """Print test summary."""
        print(f"\n{'='*80}")
        print("PCILeech Integration Test Summary")
        print(f"{'='*80}")

        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Skipped: {self.skipped_tests}")
        print(f"Total Duration: {total_duration:.2f}s")

        print(f"\nDetailed Results:")
        print("-" * 40)

        for test_name, result in self.results.items():
            status_symbol = "✓" if result["status"] == "PASSED" else "✗"
            print(
                f"{status_symbol} {test_name:<30} {result['status']:<10} ({result['duration']:.2f}s)"
            )

        # Print overall result
        if self.failed_tests == 0:
            print(f"\n🎉 ALL PCILEECH INTEGRATION TESTS PASSED!")
            print("PCILeech integration is working correctly.")
        else:
            print(f"\n❌ {self.failed_tests} PCILEECH INTEGRATION TESTS FAILED!")
            print("Please review the failed tests and fix the issues.")

        print(f"{'='*80}")

    def get_exit_code(self) -> int:
        """Get exit code based on test results."""
        return 0 if self.failed_tests == 0 else 1


def main():
    """Main entry point."""
    runner = PCILeechTestRunner()
    runner.run_all_tests()
    return runner.get_exit_code()


if __name__ == "__main__":
    sys.exit(main())
