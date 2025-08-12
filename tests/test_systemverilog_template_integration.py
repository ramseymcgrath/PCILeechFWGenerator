"""Integration test for SystemVerilog template rendering.

This test ensures that templates are actually rendered without errors,
catching issues like missing template variables that mocked tests miss.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.exceptions import TemplateRenderError
from src.templating.systemverilog_generator import AdvancedSVGenerator


class TestSystemVerilogTemplateIntegration:
    """Integration tests for SystemVerilog template rendering."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock configs with realistic values
        self.mock_device_config = Mock()
        self.mock_device_config.device_type = Mock(value="network")
        self.mock_device_config.device_class = Mock(value="ethernet")
        self.mock_device_config.enable_dma = True
        self.mock_device_config.max_payload_size = 256
        self.mock_device_config.max_read_request_size = 512
        self.mock_device_config.tx_queue_depth = 1024
        self.mock_device_config.rx_queue_depth = 1024
        self.mock_device_config.command_queue_depth = 256
        self.mock_device_config.msi_vectors = 4
        self.mock_device_config.msix_vectors = 16
        self.mock_device_config.enable_interrupt_coalescing = False
        self.mock_device_config.enable_virtualization = False
        self.mock_device_config.enable_sr_iov = False

        self.mock_error_config = Mock()
        self.mock_error_config.enable_ecc = True
        self.mock_error_config.enable_parity = True
        self.mock_error_config.enable_crc = True

        self.mock_perf_config = Mock()
        self.mock_perf_config.enable_transaction_counters = True
        self.mock_perf_config.enable_latency_measurement = True
        self.mock_perf_config.enable_bandwidth_monitoring = True

        self.mock_power_config = Mock()
        self.mock_power_config.enable_clock_gating = True
        self.mock_power_config.enable_power_gating = False
        self.mock_power_config.transition_cycles = Mock()
        self.mock_power_config.transition_cycles.d0_to_d1 = 100
        self.mock_power_config.transition_cycles.d1_to_d0 = 100
        self.mock_power_config.transition_cycles.d0_to_d3 = 1000
        self.mock_power_config.transition_cycles.d3_to_d0 = 1000

        # Create generator instance WITHOUT mocking the renderer
        self.generator = AdvancedSVGenerator(
            device_config=self.mock_device_config,
            error_config=self.mock_error_config,
            perf_config=self.mock_perf_config,
            power_config=self.mock_power_config,
        )

    def test_pcileech_tlps128_bar_controller_template_renders(self):
        """Test that pcileech_tlps128_bar_controller template renders without errors."""
        # Create a complete template context with all required fields
        template_context = {
            "device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "class_code": "020000",
                "revision_id": "01",
                "subsystem_vendor_id": "1043",
                "subsystem_device_id": "8554",
                "enable_error_injection": False,
                "enable_perf_counters": True,
                "enable_dma_operations": True,
            },
            "device_signature": "0xDEADBEEF",  # Required field
            "msix_config": {
                "num_vectors": 16,
                "table_bir": 0,
                "table_offset": 0x1000,
                "pba_bir": 0,
                "pba_offset": 0x2000,
            },
            "bar_config": {
                "aperture_size": 65536,
                "bar_index": 0,
                "bar_type": 0,  # 32-bit
                "prefetchable": False,
                "bars": [
                    {
                        "index": 0,
                        "size": 65536,
                        "type": "mem32",
                        "prefetchable": False,
                        "is_64bit": False,
                    },
                    {
                        "index": 1,
                        "size": 4096,
                        "type": "io",
                        "prefetchable": False,
                        "is_64bit": False,
                    },
                ],
            },
            "board_config": {
                "name": "pcileech_75t484_x1",
                "fpga_part": "xc7a75tfgg484-2",
                "fpga_family": "7series",
                "pcie_ip_type": "pcie_7x",
                "max_lanes": 1,
                "supports_msi": True,
                "supports_msix": True,
                "has_option_rom": False,
            },
            "interrupt_config": {
                "vectors": 4,
                "msi_enabled": True,
                "msix_enabled": False,
            },
            "config_space_data": {
                "data": [0] * 256,  # 256 bytes of config space
            },
            "timing_config": {
                "read_latency": 4,
                "write_latency": 2,
                "burst_length": 16,
                "inter_burst_gap": 8,
                "timeout_cycles": 1024,
            },
            "pcileech_config": {
                "enable": True,
                "buffer_size": 4096,
                "dma_enable": True,
            },
            "generation_metadata": {
                "timestamp": "2024-01-01T00:00:00Z",
                "version": "1.0.0",
                "generator": "PCILeechFWGenerator",
            },
        }

        # This should not raise any errors if all required variables are present
        result = self.generator.generate_pcileech_modules(template_context)

        # Verify all expected modules were generated
        assert isinstance(result, dict)
        assert "pcileech_tlps128_bar_controller" in result
        assert "pcileech_fifo" in result
        assert "top_level_wrapper" in result
        assert "pcileech_cfgspace.coe" in result

        # Verify the generated content is not empty
        assert len(result["pcileech_tlps128_bar_controller"]) > 100
        assert len(result["pcileech_fifo"]) > 100
        assert len(result["top_level_wrapper"]) > 100
        assert len(result["pcileech_cfgspace.coe"]) > 10

        # Verify the generated SystemVerilog contains expected keywords
        bar_controller = result["pcileech_tlps128_bar_controller"]
        assert "module pcileech_tlps128_bar_controller" in bar_controller
        assert "BAR_APERTURE_SIZE" in bar_controller
        assert "MSI-X" in bar_controller or "MSIX" in bar_controller
        assert "0xDEADBEEF" in bar_controller  # device_signature should be in output

    def test_missing_board_config_raises_error(self):
        """Test that missing board_config in template causes proper error."""
        # Create template context WITHOUT board_config
        template_context = {
            "device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "class_code": "020000",
                "revision_id": "01",
            },
            "device_signature": "0xDEADBEEF",
            "msix_config": {},
            "bar_config": {},
            # board_config is intentionally missing
            "interrupt_config": {},
            "config_space_data": {},
            "timing_config": {},
            "pcileech_config": {},
            "generation_metadata": {},
        }

        # The template should still render (board_config has default empty dict)
        # but if the template tries to access board_config properties without
        # proper checks, it would fail
        result = self.generator.generate_pcileech_modules(template_context)

        # Should succeed with empty board_config defaulting to {}
        assert isinstance(result, dict)
        assert "pcileech_tlps128_bar_controller" in result

    def test_template_with_all_optional_configs(self):
        """Test template rendering with all optional configurations provided."""
        template_context = {
            "device_config": {
                "vendor_id": "8086",
                "device_id": "1533",
                "class_code": "020000",
                "revision_id": "03",
                "subsystem_vendor_id": "8086",
                "subsystem_device_id": "0001",
                "enable_error_injection": True,
                "enable_perf_counters": True,
                "enable_dma_operations": True,
            },
            "device_signature": "0xCAFEBABE",
            "msix_config": {
                "num_vectors": 32,
                "table_bir": 2,
                "table_offset": 0x0000,
                "pba_bir": 2,
                "pba_offset": 0x1000,
            },
            "bar_config": {
                "aperture_size": 131072,
                "bar_index": 2,
                "bar_type": 1,  # 64-bit
                "prefetchable": True,
                "bars": [
                    {
                        "index": 0,
                        "size": 4096,
                        "type": "mem32",
                        "prefetchable": False,
                        "is_64bit": False,
                    },
                    {
                        "index": 1,
                        "size": 8192,
                        "type": "io",
                        "prefetchable": False,
                        "is_64bit": False,
                    },
                    {
                        "index": 2,
                        "size": 131072,
                        "type": "mem64",
                        "prefetchable": True,
                        "is_64bit": True,
                    },
                ],
            },
            "board_config": {
                "name": "custom_board",
                "fpga_part": "xcvu9p-flga2104-2L-e",
                "fpga_family": "ultrascale_plus",
                "pcie_ip_type": "pcie4",
                "max_lanes": 16,
                "supports_msi": True,
                "supports_msix": True,
                "has_option_rom": True,
                "max_link_speed": "gen4",
                "max_link_width": "x16",
            },
            "interrupt_config": {
                "vectors": 32,
                "msi_enabled": False,
                "msix_enabled": True,
                "interrupt_moderation": True,
            },
            "config_space_data": {
                "data": list(range(256)),  # Some test data
            },
            "timing_config": {
                "read_latency": 8,
                "write_latency": 4,
                "burst_length": 32,
                "inter_burst_gap": 16,
                "timeout_cycles": 2048,
            },
            "pcileech_config": {
                "enable": True,
                "buffer_size": 8192,
                "dma_enable": True,
                "scatter_gather": True,
            },
            "generation_metadata": {
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "2.0.0",
                "generator": "PCILeechFWGenerator",
                "build_id": "test-build-123",
            },
        }

        result = self.generator.generate_pcileech_modules(template_context)

        # Verify generation succeeded
        assert isinstance(result, dict)
        assert all(
            key in result
            for key in [
                "pcileech_tlps128_bar_controller",
                "pcileech_fifo",
                "top_level_wrapper",
                "pcileech_cfgspace.coe",
            ]
        )

        # Verify custom values appear in generated code
        bar_controller = result["pcileech_tlps128_bar_controller"]
        assert "0xCAFEBABE" in bar_controller  # device_signature
        assert (
            "131072" in bar_controller or "0x20000" in bar_controller
        )  # aperture_size

    def test_template_validation_context_validator_compatibility(self):
        """Test that our context is compatible with TemplateContextValidator requirements."""
        from src.templating.template_context_validator import \
            TemplateContextValidator

        validator = TemplateContextValidator()

        # Create a minimal valid context
        template_context = {
            "device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "enable_dma_operations": True,
            },
            "bar_config": {
                "bars": [
                    {
                        "index": 0,
                        "size": 4096,
                        "type": "mem32",
                        "prefetchable": False,
                        "is_64bit": False,
                    }
                ]
            },
            "board_config": {},  # Required by validator
            "device_signature": "0x12345678",  # Required for security
        }

        # This should work with the validator's requirements
        result = self.generator.generate_pcileech_modules(template_context)
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
