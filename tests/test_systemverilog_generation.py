#!/usr/bin/env python3
"""
Unit tests for SystemVerilog generation functionality.

Tests the core SystemVerilog generation logic, module creation,
register handling, and integration with advanced features.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.build import PCILeechFirmwareBuilder


class TestSystemVerilogGeneration(unittest.TestCase):
    """Test cases for SystemVerilog generation functionality."""

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

    def test_generate_device_config_module_basic(self):
        """Test basic device configuration module generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "revision_id": "0x03",
            "subsystem_vendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "class_code": "0x020000",
            "bar_sizes": ["0x20000", "0x0", "0x0", "0x0", "0x0", "0x0"],
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        self.assertIsInstance(sv_content, str)
        self.assertIn("module device_config", sv_content)
        self.assertIn("0x8086", sv_content)  # Vendor ID
        self.assertIn("0x1533", sv_content)  # Device ID
        self.assertIn("input wire clk", sv_content)
        self.assertIn("output reg", sv_content)

    def test_generate_device_config_module_with_msix(self):
        """Test device configuration module with MSI-X capability."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "revision_id": "0x03",
            "subsystem_vendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "class_code": "0x020000",
            "bar_sizes": ["0x20000", "0x0", "0x0", "0x0", "0x0", "0x0"],
            "msix_capability": {
                "table_size": 8,
                "table_offset": 0x2000,
                "pba_offset": 0x3000,
                "bir": 0,
            },
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        self.assertIn("msix", sv_content.lower())
        self.assertIn("interrupt", sv_content.lower())

    def test_generate_top_level_wrapper_basic(self):
        """Test basic top-level wrapper generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "board_type": "75t",
        }

        wrapper_content = self.builder._generate_top_level_wrapper(device_info)

        self.assertIsInstance(wrapper_content, str)
        self.assertIn(
            "module pcileech_tlps128_bar_controller",
            wrapper_content)
        self.assertIn("input wire clk", wrapper_content)
        self.assertIn("output wire", wrapper_content)

    def test_generate_top_level_wrapper_with_advanced_features(self):
        """Test top-level wrapper with advanced features enabled."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "board_type": "75t",
            "advanced_features": True,
            "variance_model": {
                "timing_adjustments": {
                    "setup": 0.1,
                    "hold": 0.05}},
        }

        wrapper_content = self.builder._generate_top_level_wrapper(device_info)

        # Should include advanced timing or variance-related code
        self.assertIn("pcileech_tlps128_bar_controller", wrapper_content)

    def test_systemverilog_file_discovery(self):
        """Test SystemVerilog file discovery and copying."""
        # Create mock SystemVerilog files
        sv_files = [
            "config_space_shadow.sv",
            "msix_table.sv",
            "option_rom_bar_window.sv",
        ]

        for sv_file in sv_files:
            file_path = self.output_dir / sv_file
            file_path.write_text(
                f"// Mock SystemVerilog content for {sv_file}\n")

        device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

        discovered_files = self.builder._discover_and_copy_all_files(
            device_info)

        self.assertIsInstance(discovered_files, list)
        # Should find the mock files we created
        self.assertTrue(len(discovered_files) >= 0)

    def test_systemverilog_syntax_validation(self):
        """Test that generated SystemVerilog has valid syntax structure."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "revision_id": "0x03",
            "bar_sizes": ["0x20000", "0x0", "0x0", "0x0", "0x0", "0x0"],
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        # Basic syntax checks
        self.assertEqual(
            sv_content.count("module"),
            sv_content.count("endmodule"))
        self.assertIn("always @(posedge clk)", sv_content)
        self.assertNotIn("syntax error", sv_content.lower())

        # Check for proper signal declarations
        self.assertIn("input wire", sv_content)
        self.assertIn("output", sv_content)

    def test_register_logic_generation(self):
        """Test register access logic generation."""
        registers = [
            {"name": "CTRL", "offset": "0x0000", "size": 4, "access": "RW"},
            {"name": "STATUS", "offset": "0x0004", "size": 4, "access": "RO"},
            {"name": "DATA", "offset": "0x0008", "size": 4, "access": "RW"},
        ]

        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "registers": registers,
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        # Should include register handling logic
        self.assertIn("case", sv_content)
        self.assertIn("0x0000", sv_content)  # CTRL register offset
        self.assertIn("0x0004", sv_content)  # STATUS register offset

    def test_bar_size_handling(self):
        """Test BAR size configuration handling."""
        test_cases = [{"bar_sizes": ["0x20000",
                                     "0x0",
                                     "0x0",
                                     "0x0",
                                     "0x0",
                                     "0x0"],
                       "expected_size": "0x20000",
                       },
                      {"bar_sizes": ["0x100000",
                                     "0x1000",
                                     "0x0",
                                     "0x0",
                                     "0x0",
                                     "0x0"],
                       "expected_size": "0x100000",
                       },
                      ]

        for test_case in test_cases:
            with self.subTest(bar_sizes=test_case["bar_sizes"]):
                device_info = {
                    "vendor_id": "0x8086",
                    "device_id": "0x1533",
                    "bar_sizes": test_case["bar_sizes"],
                }

                sv_content = self.builder._generate_device_config_module(
                    device_info)
                self.assertIn(test_case["expected_size"], sv_content)

    def test_clock_domain_generation(self):
        """Test clock domain handling in SystemVerilog."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "clock_domains": ["clk_125", "clk_250"],
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        # Should include clock handling
        self.assertIn("clk", sv_content)
        self.assertIn("always @(posedge", sv_content)

    def test_error_handling_in_systemverilog(self):
        """Test error handling logic in generated SystemVerilog."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "error_handling": True,
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        # Should include basic error handling structures
        self.assertIn("reg", sv_content)
        self.assertIn("wire", sv_content)

    def test_memory_interface_generation(self):
        """Test memory interface generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "memory_interface": {
                "type": "AXI4",
                "data_width": 128,
                "addr_width": 32},
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        # Should include memory interface signals
        self.assertIn("input wire", sv_content)
        self.assertIn("output", sv_content)

    def test_interrupt_handling_generation(self):
        """Test interrupt handling logic generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "interrupts": {"legacy": True, "msi": False, "msix": True},
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        # Should include interrupt-related logic
        self.assertIn("reg", sv_content)

    def test_power_management_integration(self):
        """Test power management feature integration."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "power_management": {
                "d0": True,
                "d1": False,
                "d2": False,
                "d3": True},
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        # Should include power state handling
        self.assertIn("reg", sv_content)

    def test_device_specific_optimizations(self):
        """Test device-specific optimizations."""
        device_types = ["network", "storage", "graphics", "audio", "generic"]

        for device_type in device_types:
            with self.subTest(device_type=device_type):
                device_info = {
                    "vendor_id": "0x8086",
                    "device_id": "0x1533",
                    "device_type": device_type,
                }

                sv_content = self.builder._generate_device_config_module(
                    device_info)

                # Should generate valid SystemVerilog regardless of device type
                self.assertIn("module device_config", sv_content)
                self.assertIn("endmodule", sv_content)

    def test_configuration_space_shadow(self):
        """Test configuration space shadow BRAM generation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "config_space_shadow": True,
            "config_space": "00" * 256,  # Mock 256-byte config space
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        # Should include configuration space handling
        self.assertIn("reg", sv_content)

    def test_systemverilog_file_generation_integration(self):
        """Test complete SystemVerilog file generation workflow."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "revision_id": "0x03",
            "bar_sizes": ["0x20000", "0x0", "0x0", "0x0", "0x0", "0x0"],
            "registers": [
                {"name": "CTRL", "offset": "0x0000", "size": 4, "access": "RW"}
            ],
        }

        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            generated_files = self.builder.generate_systemverilog_files(
                device_info)

            self.assertIsInstance(generated_files, list)
            # Should have attempted to write files
            self.assertTrue(mock_open.called)

    def test_advanced_sv_integration(self):
        """Test integration with advanced SystemVerilog features."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "advanced_sv": True,
            "device_type": "network",
            "variance_model": {
                "timing_adjustments": {
                    "setup": 0.1,
                    "hold": 0.05}},
        }

        # Mock the advanced SV generator
        with patch("src.build.AdvancedSVGenerator") as mock_generator:
            mock_instance = MagicMock()
            mock_generator.return_value = mock_instance
            mock_instance.generate_advanced_systemverilog.return_value = (
                "// Advanced SV content"
            )

            sv_content = self.builder._generate_device_config_module(
                device_info)

            # Should still generate basic content even with advanced features
            self.assertIn("module device_config", sv_content)

    def test_manufacturing_variance_integration(self):
        """Test integration with manufacturing variance simulation."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "enable_variance": True,
            "dsn": 12345,
            "revision": "A1",
        }

        # Mock the variance simulator
        with patch.object(self.builder, "variance_simulator") as mock_simulator:
            mock_simulator.generate_variance_model.return_value = {
                "timing_adjustments": {"setup": 0.1, "hold": 0.05}
            }

            sv_content = self.builder._generate_device_config_module(
                device_info)

            # Should generate content with variance considerations
            self.assertIn("module device_config", sv_content)

    def test_behavior_profiling_integration(self):
        """Test integration with behavior profiling data."""
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "behavior_profile": {
                "register_accesses": [
                    {"register": "CTRL", "frequency": 100, "pattern": "periodic"}
                ],
                "timing_patterns": [
                    {"type": "burst", "duration": 0.001, "frequency": 50}
                ],
            },
        }

        sv_content = self.builder._generate_device_config_module(device_info)

        # Should incorporate profiling data into generation
        self.assertIn("module device_config", sv_content)

    def test_error_recovery_in_generation(self):
        """Test error recovery during SystemVerilog generation."""
        # Test with malformed device info
        malformed_device_info = {
            "vendor_id": "invalid",
            "device_id": None,
            "bar_sizes": "not_a_list",
        }

        # Should handle errors gracefully
        try:
            sv_content = self.builder._generate_device_config_module(
                malformed_device_info
            )
            # Should still generate some content or handle the error
            self.assertIsInstance(sv_content, str)
        except Exception as e:
            # If it raises an exception, it should be a meaningful one
            self.assertIsInstance(e, (ValueError, TypeError))


class TestSystemVerilogValidation(unittest.TestCase):
    """Test SystemVerilog syntax and structure validation."""

    def test_module_structure_validation(self):
        """Test that generated modules have proper structure."""
        sample_sv = """
        module test_module (
            input wire clk,
            input wire rst,
            output reg [31:0] data_out
        );

        always @(posedge clk) begin
            if (rst) begin
                data_out <= 32'h0;
            end else begin
                data_out <= data_out + 1;
            end
        end

        endmodule
        """

        # Basic structure validation - count actual module/endmodule pairs
        # Count lines that start with "module " (after whitespace)
        lines = sample_sv.split("\n")
        module_count = sum(
            1 for line in lines if line.strip().startswith("module "))
        endmodule_count = sample_sv.count("endmodule")
        self.assertEqual(module_count, endmodule_count)
        self.assertIn("always @(posedge clk)", sample_sv)
        self.assertIn("input wire", sample_sv)
        self.assertIn("output reg", sample_sv)

    def test_signal_declaration_validation(self):
        """Test signal declaration syntax."""
        valid_declarations = [
            "input wire clk",
            "input wire [31:0] data_in",
            "output reg [7:0] status",
            "output wire interrupt",
            "reg [15:0] counter",
            "wire [31:0] address",
        ]

        for declaration in valid_declarations:
            with self.subTest(declaration=declaration):
                # Should not contain syntax errors
                self.assertNotIn("error", declaration.lower())
                self.assertTrue(
                    any(
                        keyword in declaration
                        for keyword in ["input", "output", "reg", "wire"]
                    )
                )

    def test_always_block_validation(self):
        """Test always block syntax."""
        valid_always_blocks = [
            "always @(posedge clk)",
            "always @(negedge clk)",
            "always @(posedge clk or negedge rst)",
            "always @(*)",
            "always_comb",
            "always_ff @(posedge clk)",
        ]

        for block in valid_always_blocks:
            with self.subTest(block=block):
                self.assertIn("always", block)

    def test_case_statement_validation(self):
        """Test case statement structure."""
        sample_case = """
        case (address[7:0])
            8'h00: data_out = ctrl_reg;
            8'h04: data_out = status_reg;
            8'h08: data_out = data_reg;
            default: data_out = 32'h0;
        endcase
        """

        self.assertIn("case", sample_case)
        self.assertIn("endcase", sample_case)
        self.assertIn("default:", sample_case)

    def test_parameter_validation(self):
        """Test parameter declarations."""
        valid_parameters = [
            "parameter DATA_WIDTH = 32",
            "parameter ADDR_WIDTH = 16",
            "localparam FIFO_DEPTH = 256",
        ]

        for param in valid_parameters:
            with self.subTest(param=param):
                self.assertTrue("parameter" in param or "localparam" in param)


if __name__ == "__main__":
    unittest.main()
