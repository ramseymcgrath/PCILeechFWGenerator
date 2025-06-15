#!/usr/bin/env python3
"""
Core TCL generation tests - focused on essential functionality.
"""

import tempfile
import unittest
from pathlib import Path

from src.tcl_generator import TCLGenerator


class TestTCLGenerationCore(unittest.TestCase):
    """Core test cases for TCL script generation functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir)
        self.tcl_generator = TCLGenerator(board="75t", output_dir=self.output_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        if self.temp_dir:
            shutil.rmtree(self.temp_dir)

    def test_generate_device_tcl_script_basic(self):
        """Test basic device TCL script generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "revision_id": "0x03",
            "class_code": "0x020000",
        }

        tcl_content = self.tcl_generator.generate_device_tcl_script(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("create_project", tcl_content)
        self.assertIn("set_property", tcl_content)
        self.assertIn("0x8086", tcl_content)
        self.assertIn("0x1533", tcl_content)

    def test_generate_axi_pcie_config(self):
        """Test AXI PCIe IP configuration."""
        vendor_id = "0x8086"
        device_id = "0x1533"
        revision_id = "0x03"

        tcl_content = self.tcl_generator.generate_axi_pcie_config(
            vendor_id, device_id, revision_id
        )

        self.assertIsInstance(tcl_content, str)
        self.assertIn("custom", tcl_content.lower())
        self.assertIn(vendor_id, tcl_content)
        self.assertIn(device_id, tcl_content)
        self.assertIn("set", tcl_content)

    def test_generate_pcie_7x_config(self):
        """Test PCIe 7-series IP configuration."""
        vendor_id = "0x8086"
        device_id = "0x1533"
        revision_id = "0x03"

        tcl_content = self.tcl_generator.generate_pcie_7x_config(
            vendor_id, device_id, revision_id
        )

        self.assertIsInstance(tcl_content, str)
        self.assertIn("pcie_7x", tcl_content.lower())
        self.assertIn(vendor_id, tcl_content)
        self.assertIn(device_id, tcl_content)

    def test_generate_project_setup_tcl(self):
        """Test project setup TCL generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "class_code": "0x020000",
            "revision_id": "0x03",
        }

        tcl_content = self.tcl_generator.generate_project_setup_tcl(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("create_project", tcl_content)
        self.assertIn("set_property", tcl_content)
        self.assertIn("target_language", tcl_content.lower())

    def test_generate_ip_config_tcl(self):
        """Test IP configuration TCL generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "class_code": "0x020000",
            "revision_id": "0x03",
        }

        tcl_content = self.tcl_generator.generate_ip_config_tcl(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("create_ip", tcl_content)
        self.assertIn("set_property", tcl_content)

    def test_template_fallback_mechanism(self):
        """Test that template fallback mechanisms work correctly."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "class_code": "0x020000",
            "revision_id": "0x03",
        }

        # Test that all methods return valid strings
        methods_to_test = [
            "generate_project_setup_tcl",
            "generate_ip_config_tcl",
            "generate_sources_tcl",
            "generate_constraints_tcl",
            "generate_synthesis_tcl",
            "generate_implementation_tcl",
            "generate_bitstream_tcl",
            "generate_master_build_tcl",
        ]

        for method_name in methods_to_test:
            with self.subTest(method=method_name):
                method = getattr(self.tcl_generator, method_name)
                result = method(device_info)
                self.assertIsInstance(result, str)
                self.assertTrue(len(result) > 0)

    def test_hex_prefix_handling(self):
        """Test that hex prefixes are handled correctly."""
        # Test AXI PCIe config with various hex formats
        test_cases = [
            ("0x8086", "0x1533", "0x03"),
            ("8086", "1533", "03"),
        ]

        for vendor_id, device_id, revision_id in test_cases:
            with self.subTest(vendor_id=vendor_id, device_id=device_id):
                tcl_content = self.tcl_generator.generate_axi_pcie_config(
                    vendor_id, device_id, revision_id
                )
                # Should not have double 0x prefix
                self.assertNotIn("0x0x", tcl_content)


if __name__ == "__main__":
    unittest.main()
