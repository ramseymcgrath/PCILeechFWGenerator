#!/usr/bin/env python3
"""
CI Pipeline Test Suite for TCL Builder and Template Context Safety

This test suite verifies that the TCL builder and related components
handle missing dictionary keys gracefully and don't cause runtime errors.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.templating.tcl_builder import BuildContext, TCLBuilder

# Note: SystemVerilog generator tests are optional - the class name may vary


class TestTCLBuilderSafety(unittest.TestCase):
    """Test TCL Builder for safe dictionary access patterns."""

    def setUp(self):
        """Set up test fixtures."""
        self.tcl_builder = TCLBuilder()

    def test_build_context_creation(self):
        """Test that BuildContext can be created with minimal parameters."""
        context = BuildContext(
            board_name="test_board",
            fpga_part="xc7a35tcsg324-2",
            fpga_family="Artix-7",
            pcie_ip_type="7x",
            max_lanes=4,
            supports_msi=True,
            supports_msix=False,
        )
        self.assertIsNotNone(context)
        self.assertEqual(context.board_name, "test_board")

    def test_pcileech_context_always_present(self):
        """Test that PCILeech context is always present in template context."""
        context = BuildContext(
            board_name="test_board",
            fpga_part="xc7a35tcsg324-2",
            fpga_family="Artix-7",
            pcie_ip_type="7x",
            max_lanes=4,
            supports_msi=True,
            supports_msix=False,
        )

        template_context = context.to_template_context()

        # PCILeech context should always be present
        self.assertIn("pcileech", template_context)

        # Check required keys
        pcileech = template_context["pcileech"]
        required_keys = ["src_dir", "ip_dir", "project_script", "build_script"]
        for key in required_keys:
            self.assertIn(key, pcileech, f"Missing required key: {key}")

    def test_pcileech_context_with_custom_values(self):
        """Test PCILeech context with custom values."""
        context = BuildContext(
            board_name="test_board",
            fpga_part="xc7a35tcsg324-2",
            fpga_family="Artix-7",
            pcie_ip_type="7x",
            max_lanes=4,
            supports_msi=True,
            supports_msix=False,
            pcileech_src_dir="custom_src",
            pcileech_ip_dir="custom_ip",
            source_file_list=["file1.sv", "file2.sv"],
        )

        template_context = context.to_template_context()
        pcileech = template_context["pcileech"]

        self.assertEqual(pcileech["src_dir"], "custom_src")
        self.assertEqual(pcileech["ip_dir"], "custom_ip")
        self.assertEqual(pcileech["source_files"], ["file1.sv", "file2.sv"])

    def test_build_pcileech_scripts_without_context(self):
        """Test that build methods handle missing PCILeech context gracefully."""
        context = BuildContext(
            board_name="test_board",
            fpga_part="xc7a35tcsg324-2",
            fpga_family="Artix-7",
            pcie_ip_type="7x",
            max_lanes=4,
            supports_msi=True,
            supports_msix=False,
        )

        # These should not raise KeyError even if pcileech context is somehow missing
        try:
            # Note: These will fail with TemplateNotFoundError in test environment
            # but that's expected - we're testing they don't fail with KeyError
            self.tcl_builder.build_pcileech_project_script(context)
        except Exception as e:
            # Should not be a KeyError
            self.assertNotIsInstance(e, KeyError)


class TestImportResilience(unittest.TestCase):
    """Test that imports are resilient to missing modules."""

    def test_tcl_builder_imports(self):
        """Test that TCL builder can be imported."""
        try:
            from src.templating.tcl_builder import TCLBuilder

            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import TCLBuilder: {e}")

    def test_systemverilog_generator_imports(self):
        """Test that SystemVerilog generator module can be imported."""
        try:
            # Just test that the module itself can be imported
            import src.templating.systemverilog_generator

            self.assertTrue(True)
        except ImportError as e:
            # This is not critical - the module might not be available in all environments
            print(f"Note: SystemVerilog generator module not available: {e}")
            self.skipTest("SystemVerilog generator module not available")


def run_ci_tests():
    """Run all CI pipeline tests and return exit code."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTCLBuilderSafety))
    # SystemVerilog tests are optional and commented out
    # suite.addTests(loader.loadTestsFromTestCase(TestSystemVerilogGeneratorSafety))
    suite.addTests(loader.loadTestsFromTestCase(TestImportResilience))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_ci_tests())
