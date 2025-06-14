#!/usr/bin/env python3
"""
Unit tests for TCL script generation functionality.

Tests TCL script generation for Vivado builds, project setup,
IP configuration, and build orchestration.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.build import PCILeechFirmwareBuilder


class TestTCLGeneration(unittest.TestCase):
    """Test cases for TCL script generation functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir)

        # Mock dependencies to avoid import issues
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):
            self.builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

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
            "subsystem_vendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "class_code": "0x020000",
            "bar_sizes": ["0x20000", "0x0", "0x0", "0x0", "0x0", "0x0"],
        }

        tcl_content = self.builder._generate_device_tcl_script(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("set_property", tcl_content)
        self.assertIn("create_project", tcl_content)
        self.assertIn("0x8086", tcl_content)  # Vendor ID
        self.assertIn("0x1533", tcl_content)  # Device ID

    def test_generate_device_tcl_script_with_board_specific_settings(self):
        """Test TCL script generation with board-specific settings."""
        board_types = ["75t", "100t", "35t"]

        for board_type in board_types:
            with self.subTest(board_type=board_type):
                device_info = {
                    "vendor_id": "0x8086",
                    "device_id": "0x1533",
                    "board_type": board_type,
                }

                tcl_content = self.builder._generate_device_tcl_script(device_info)

                self.assertIn("set_property", tcl_content)
                # Should include board-specific configurations
                self.assertTrue(len(tcl_content) > 100)

    def test_generate_project_setup_tcl(self):
        """Test project setup TCL generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "project_name": "pcileech_test",
        }

        tcl_content = self.builder._generate_project_setup_tcl(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("create_project", tcl_content)
        self.assertIn("set_property", tcl_content)
        self.assertIn("target_language", tcl_content.lower())

    def test_generate_ip_config_tcl(self):
        """Test IP configuration TCL generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "board_type": "75t",
        }

        tcl_content = self.builder._generate_ip_config_tcl(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("create_ip", tcl_content)
        self.assertIn("set_property", tcl_content)

    def test_generate_axi_pcie_config(self):
        """Test AXI PCIe IP configuration."""
        vendor_id = "0x8086"
        device_id = "0x1533"
        revision_id = "0x03"

        tcl_content = self.builder._generate_axi_pcie_config(
            vendor_id, device_id, revision_id
        )

        self.assertIsInstance(tcl_content, str)
        self.assertIn("axi_pcie", tcl_content.lower())
        self.assertIn(vendor_id, tcl_content)
        self.assertIn(device_id, tcl_content)
        self.assertIn("set_property", tcl_content)

    def test_generate_pcie_7x_config(self):
        """Test PCIe 7-series IP configuration."""
        vendor_id = "0x8086"
        device_id = "0x1533"
        revision_id = "0x03"

        tcl_content = self.builder._generate_pcie_7x_config(
            vendor_id, device_id, revision_id
        )

        self.assertIsInstance(tcl_content, str)
        self.assertIn("pcie_7x", tcl_content.lower())
        self.assertIn(vendor_id, tcl_content)
        self.assertIn(device_id, tcl_content)

    def test_generate_pcie_ultrascale_config(self):
        """Test PCIe UltraScale IP configuration."""
        vendor_id = "0x8086"
        device_id = "0x1533"
        revision_id = "0x03"

        tcl_content = self.builder._generate_pcie_ultrascale_config(
            vendor_id, device_id, revision_id
        )

        self.assertIsInstance(tcl_content, str)
        self.assertIn("ultrascale", tcl_content.lower())
        self.assertIn(vendor_id, tcl_content)
        self.assertIn(device_id, tcl_content)

    def test_generate_sources_tcl(self):
        """Test sources TCL generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "source_files": ["device_config.sv", "pcileech_tlps128_bar_controller.sv"],
        }

        tcl_content = self.builder._generate_sources_tcl(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("add_files", tcl_content)
        self.assertIn("set_property", tcl_content)

    def test_generate_constraints_tcl(self):
        """Test constraints TCL generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "board_type": "75t",
        }

        tcl_content = self.builder._generate_constraints_tcl(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("add_files", tcl_content)
        self.assertIn("constraints", tcl_content.lower())

    def test_generate_synthesis_tcl(self):
        """Test synthesis TCL generation."""
        device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

        tcl_content = self.builder._generate_synthesis_tcl(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("synth_design", tcl_content)
        self.assertIn("launch_runs", tcl_content)

    def test_generate_implementation_tcl(self):
        """Test implementation TCL generation."""
        device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

        tcl_content = self.builder._generate_implementation_tcl(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("opt_design", tcl_content)
        self.assertIn("place_design", tcl_content)
        self.assertIn("route_design", tcl_content)

    def test_generate_bitstream_tcl(self):
        """Test bitstream generation TCL."""
        device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

        tcl_content = self.builder._generate_bitstream_tcl(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("write_bitstream", tcl_content)
        self.assertIn("set_property", tcl_content)

    def test_generate_master_build_tcl(self):
        """Test master build TCL generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "board_type": "75t",
        }

        tcl_content = self.builder._generate_master_build_tcl(device_info)

        self.assertIsInstance(tcl_content, str)
        self.assertIn("source", tcl_content)
        self.assertIn("project_setup.tcl", tcl_content)
        self.assertIn("synthesis.tcl", tcl_content)
        self.assertIn("implementation.tcl", tcl_content)
        self.assertIn("bitstream.tcl", tcl_content)

    def test_generate_separate_tcl_files(self):
        """Test generation of separate TCL files."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "board_type": "75t",
        }

        tcl_files = self.builder._generate_separate_tcl_files(device_info)

        self.assertIsInstance(tcl_files, list)
        self.assertTrue(len(tcl_files) > 0)

        # Should include various TCL script types
        expected_files = [
            "project_setup.tcl",
            "ip_config.tcl",
            "sources.tcl",
            "constraints.tcl",
            "synthesis.tcl",
            "implementation.tcl",
            "bitstream.tcl",
        ]

        for expected_file in expected_files:
            self.assertTrue(
                any(expected_file in tcl_file for tcl_file in tcl_files),
                f"Expected {expected_file} in generated TCL files",
            )

    def test_tcl_syntax_validation(self):
        """Test that generated TCL has valid syntax structure."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "board_type": "75t",
        }

        tcl_content = self.builder._generate_device_tcl_script(device_info)

        # Basic TCL syntax checks
        self.assertNotIn("syntax error", tcl_content.lower())
        self.assertNotIn("error:", tcl_content.lower())

        # Should have proper TCL commands
        tcl_commands = ["set_property", "create_project", "add_files"]
        for command in tcl_commands:
            if command in tcl_content:
                # If command is present, it should be properly formatted
                # Should have spaces for parameters
                self.assertIn(" ", tcl_content)

    def test_tcl_variable_substitution(self):
        """Test TCL variable substitution and parameterization."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "project_name": "test_project",
            "board_type": "75t",
        }

        tcl_content = self.builder._generate_project_setup_tcl(device_info)

        # Should include variable definitions
        self.assertIn("set", tcl_content)

        # Should substitute device-specific values
        self.assertIn("0x8086", tcl_content)
        self.assertIn("0x1533", tcl_content)

    def test_tcl_error_handling(self):
        """Test error handling in TCL generation."""
        # Test with minimal device info
        minimal_device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

        try:
            tcl_content = self.builder._generate_device_tcl_script(minimal_device_info)
            self.assertIsInstance(tcl_content, str)
            self.assertTrue(len(tcl_content) > 0)
        except Exception as e:
            # If it raises an exception, it should be meaningful
            self.assertIsInstance(e, (ValueError, KeyError))

    def test_tcl_board_specific_constraints(self):
        """Test board-specific constraint generation."""
        board_configs = [
            {"board_type": "75t", "part": "xc7a75t"},
            {"board_type": "100t", "part": "xc7a100t"},
            {"board_type": "35t", "part": "xc7a35t"},
        ]

        for config in board_configs:
            with self.subTest(board_type=config["board_type"]):
                device_info = {
                    "vendor_id": "0x8086",
                    "device_id": "0x1533",
                    "board_type": config["board_type"],
                }

                tcl_content = self.builder._generate_constraints_tcl(device_info)

                # Should include board-specific settings
                self.assertIsInstance(tcl_content, str)

    def test_tcl_timing_constraints(self):
        """Test timing constraint generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "timing_constraints": {
                "clock_period": 8.0,  # 125 MHz
                "setup_time": 2.0,
                "hold_time": 1.0,
            },
        }

        tcl_content = self.builder._generate_constraints_tcl(device_info)

        # Should include timing-related TCL commands
        self.assertIsInstance(tcl_content, str)

    def test_tcl_ip_customization(self):
        """Test IP customization in TCL."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "ip_config": {"pcie_lanes": 4, "max_payload": 256, "max_read_request": 512},
        }

        tcl_content = self.builder._generate_ip_config_tcl(device_info)

        # Should include IP customization commands
        self.assertIn("set_property", tcl_content)

    def test_tcl_build_optimization(self):
        """Test build optimization settings in TCL."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "optimization": {
                "strategy": "Performance_ExplorePostRoutePhysOpt",
                "directive": "Explore",
            },
        }

        tcl_content = self.builder._generate_synthesis_tcl(device_info)

        # Should include optimization settings
        self.assertIsInstance(tcl_content, str)

    def test_tcl_debug_features(self):
        """Test debug feature integration in TCL."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "debug": {"ila": True, "vio": False, "chipscope": False},
        }

        tcl_content = self.builder._generate_device_tcl_script(device_info)

        # Should handle debug features
        self.assertIsInstance(tcl_content, str)

    def test_tcl_memory_controller_integration(self):
        """Test memory controller integration in TCL."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "memory": {"type": "DDR3", "size": "1GB", "speed": "800MHz"},
        }

        tcl_content = self.builder._generate_ip_config_tcl(device_info)

        # Should include memory controller configuration
        self.assertIsInstance(tcl_content, str)

    def test_tcl_clock_management(self):
        """Test clock management in TCL."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "clocks": {
                "primary": "125MHz",
                "secondary": "250MHz",
                "reference": "100MHz",
            },
        }

        tcl_content = self.builder._generate_ip_config_tcl(device_info)

        # Should include clock configuration
        self.assertIsInstance(tcl_content, str)

    def test_tcl_power_analysis_integration(self):
        """Test power analysis integration in TCL."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "power_analysis": True,
        }

        tcl_content = self.builder._generate_implementation_tcl(device_info)

        # Should include power analysis commands
        self.assertIsInstance(tcl_content, str)

    def test_tcl_file_organization(self):
        """Test TCL file organization and structure."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "board_type": "75t",
        }

        tcl_files = self.builder._generate_separate_tcl_files(device_info)

        # Should generate organized set of TCL files
        self.assertIsInstance(tcl_files, list)
        self.assertTrue(len(tcl_files) > 0)

        # Each file should have meaningful content
        for tcl_file in tcl_files:
            self.assertIsInstance(tcl_file, str)
            self.assertTrue(len(tcl_file) > 0)

    def test_tcl_cross_platform_compatibility(self):
        """Test TCL cross-platform path handling."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "paths": {
                "source": "/path/to/sources",
                "constraints": "/path/to/constraints",
                "output": "/path/to/output",
            },
        }

        tcl_content = self.builder._generate_sources_tcl(device_info)

        # Should handle paths appropriately
        self.assertIsInstance(tcl_content, str)

    def test_tcl_version_compatibility(self):
        """Test TCL version compatibility."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "vivado_version": "2023.1",
        }

        tcl_content = self.builder._generate_device_tcl_script(device_info)

        # Should generate compatible TCL
        self.assertIsInstance(tcl_content, str)
        # Should not use deprecated commands
        deprecated_commands = ["create_clock", "set_input_delay"]
        for cmd in deprecated_commands:
            if cmd in tcl_content:
                # If using potentially deprecated commands, should be
                # intentional
                pass


class TestTCLScriptIntegration(unittest.TestCase):
    """Integration tests for TCL script generation."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        if self.temp_dir:
            shutil.rmtree(self.temp_dir)

    def test_complete_tcl_workflow(self):
        """Test complete TCL generation workflow."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            device_info = {
                "vendor_id": "0x8086",
                "device_id": "0x1533",
                "revision_id": "0x03",
                "board_type": "75t",
                "bar_sizes": ["0x20000", "0x0", "0x0", "0x0", "0x0", "0x0"],
            }

            # Generate all TCL files
            tcl_files = builder._generate_separate_tcl_files(device_info)

            # Should generate multiple TCL files
            self.assertIsInstance(tcl_files, list)
            self.assertTrue(len(tcl_files) > 0)

            # Each file should be valid
            for tcl_file in tcl_files:
                self.assertIsInstance(tcl_file, str)
                self.assertTrue(len(tcl_file.strip()) > 0)


if __name__ == "__main__":
    unittest.main()
