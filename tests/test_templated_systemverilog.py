#!/usr/bin/env python3
"""
Test suite for the templated SystemVerilog generator.

This test verifies that the refactored SystemVerilog generator works correctly
with the new template-based approach while maintaining backward compatibility.
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from advanced_sv_error import ErrorHandlingConfig
from advanced_sv_perf import DeviceType, PerformanceCounterConfig
from advanced_sv_power import PowerManagementConfig
from manufacturing_variance import DeviceClass

from src.templating.systemverilog_generator import (
    AdvancedSVGenerator,
    DeviceSpecificLogic,
    SystemVerilogGenerator,
)


class TestTemplatedSystemVerilog(unittest.TestCase):
    """Test the templated SystemVerilog generation system."""

    def setUp(self):
        """Set up test fixtures."""
        self.device_config = DeviceSpecificLogic(
            device_type=DeviceType.GENERIC, device_class=DeviceClass.CONSUMER
        )
        self.power_config = PowerManagementConfig()
        self.error_config = ErrorHandlingConfig()
        self.perf_config = PerformanceCounterConfig()

        self.test_regs = [
            {"name": "test_reg", "offset": "0x1000", "value": "0x12345678", "rw": "rw"},
            {
                "name": "status_reg",
                "offset": "0x1004",
                "value": "0x00000000",
                "rw": "ro",
            },
            {
                "name": "control_reg",
                "offset": "0x1008",
                "value": "0xFFFFFFFF",
                "rw": "rw",
            },
        ]

    def test_advanced_sv_generator_basic(self):
        """Test basic functionality of the advanced SystemVerilog generator."""
        generator = AdvancedSVGenerator(
            self.power_config, self.error_config, self.perf_config, self.device_config
        )

        result = generator.generate_advanced_systemverilog(self.test_regs)

        # Verify the result is a non-empty string
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 1000)  # Should be substantial content

        # Verify key components are present
        self.assertIn("module advanced_pcileech_controller", result)
        self.assertIn("endmodule", result)
        self.assertIn("// Advanced PCIe Device Controller", result)

        # Verify register declarations are present
        for reg in self.test_regs:
            self.assertIn(f"{reg['name']}_reg", result)

    def test_device_specific_ports_generation(self):
        """Test device-specific port generation for different device types."""
        device_types = [
            (DeviceType.NETWORK_CONTROLLER, "link_up"),
            (DeviceType.STORAGE_CONTROLLER, "storage_ready"),
            (DeviceType.GRAPHICS_CONTROLLER, "display_active"),
            (DeviceType.GENERIC, "device_ready"),
        ]

        for device_type, expected_port in device_types:
            with self.subTest(device_type=device_type):
                device_config = DeviceSpecificLogic(device_type=device_type)
                generator = AdvancedSVGenerator(
                    self.power_config,
                    self.error_config,
                    self.perf_config,
                    device_config,
                )

                ports = generator.generate_device_specific_ports()
                self.assertIn(expected_port, ports)

    def test_power_management_config_attributes(self):
        """Test that power management config has required attributes."""
        config = PowerManagementConfig()

        # Verify transition_cycles is properly initialized
        self.assertIsNotNone(config.transition_cycles)
        self.assertIsInstance(config.transition_cycles.d0_to_d1, int)
        self.assertIsInstance(config.transition_cycles.d1_to_d0, int)
        self.assertIsInstance(config.transition_cycles.d0_to_d3, int)
        self.assertIsInstance(config.transition_cycles.d3_to_d0, int)

    def test_performance_counter_config_attributes(self):
        """Test that performance counter config has required attributes."""
        config = PerformanceCounterConfig()

        # Verify counter_width property works
        self.assertEqual(config.counter_width, config.counter_width_bits)
        self.assertIsInstance(config.counter_width, int)
        self.assertGreater(config.counter_width, 0)

    def test_backward_compatibility_layer(self):
        """Test the backward compatibility SystemVerilogGenerator class."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            generator = SystemVerilogGenerator(output_dir)

            device_info = {
                "vendor_id": "0x1234",
                "device_id": "0x5678",
                "class_code": "0x020000",
                "board": "test_board",
                "bars": [{"size": 65536, "type": "memory"}],
                "msix_count": 4,
            }

            copied_files = generator.discover_and_copy_all_files(device_info)

            # Verify files were generated
            self.assertGreater(len(copied_files), 0)

            # Verify specific files exist
            expected_files = [
                "device_config.sv",
                "pcileech_top.sv",
                "pcileech_tlps128_bar_controller.sv",
                "pcileech_tlps128_cfgspace_shadow.sv",
                "msix_table.sv",
            ]

            generated_filenames = [Path(f).name for f in copied_files]
            for expected_file in expected_files:
                self.assertIn(expected_file, generated_filenames)

    def test_template_error_handling(self):
        """Test that template errors are properly handled."""
        # Test with invalid template directory
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_template_dir = Path(temp_dir) / "nonexistent"

            generator = AdvancedSVGenerator(
                self.power_config,
                self.error_config,
                self.perf_config,
                self.device_config,
                template_dir=invalid_template_dir,
            )

            # This should handle the error gracefully
            with self.assertRaises(Exception):
                generator.generate_advanced_systemverilog(self.test_regs)

    def test_variance_model_integration(self):
        """Test integration with variance models."""
        from manufacturing_variance import ManufacturingVarianceSimulator

        variance_simulator = ManufacturingVarianceSimulator()
        variance_model = variance_simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
        )

        generator = AdvancedSVGenerator(
            self.power_config, self.error_config, self.perf_config, self.device_config
        )

        result = generator.generate_advanced_systemverilog(
            self.test_regs, variance_model
        )

        # Verify the result includes variance considerations
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 1000)

    def test_different_device_classes(self):
        """Test generation for different device classes."""
        device_classes = [
            DeviceClass.CONSUMER,
            DeviceClass.ENTERPRISE,
            DeviceClass.INDUSTRIAL,
            DeviceClass.AUTOMOTIVE,
        ]

        for device_class in device_classes:
            with self.subTest(device_class=device_class):
                device_config = DeviceSpecificLogic(device_class=device_class)
                generator = AdvancedSVGenerator(
                    self.power_config,
                    self.error_config,
                    self.perf_config,
                    device_config,
                )

                result = generator.generate_advanced_systemverilog(self.test_regs)
                self.assertIn(device_class.value, result)

    def test_register_types_handling(self):
        """Test handling of different register types (rw, ro, wo)."""
        mixed_regs = [
            {"name": "rw_reg", "offset": "0x1000", "value": "0x12345678", "rw": "rw"},
            {"name": "ro_reg", "offset": "0x1004", "value": "0x00000000", "rw": "ro"},
            {"name": "wo_reg", "offset": "0x1008", "value": "0xFFFFFFFF", "rw": "wo"},
        ]

        generator = AdvancedSVGenerator(
            self.power_config, self.error_config, self.perf_config, self.device_config
        )

        result = generator.generate_advanced_systemverilog(mixed_regs)

        # Verify all register types are handled
        for reg in mixed_regs:
            self.assertIn(f"{reg['name']}_reg", result)


if __name__ == "__main__":
    unittest.main()
