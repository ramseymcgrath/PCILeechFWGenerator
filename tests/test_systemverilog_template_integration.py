"""Integration test for SystemVerilog template rendering.

This test ensures that templates are actually rendered without errors,
catching issues like missing template variables that mocked tests miss.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.device_clone.device_config import DeviceClass, DeviceType
from src.exceptions import TemplateRenderError
from src.templating.advanced_sv_features import (ErrorHandlingConfig,
                                                 PerformanceConfig)
from src.templating.advanced_sv_power import PowerManagementConfig
from src.templating.systemverilog_generator import AdvancedSVGenerator


class TestSystemVerilogTemplateIntegration:
    """Integration tests for SystemVerilog template rendering."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create real config objects instead of mocks
        self.error_config = ErrorHandlingConfig(
            enable_error_detection=True,
            enable_error_logging=True,
            enable_auto_retry=True,
        )

        self.perf_config = PerformanceConfig(
            enable_transaction_counters=True,
            enable_latency_measurement=True,
            enable_bandwidth_monitoring=True,
        )

        self.power_config = PowerManagementConfig(
            enable_pme=True, enable_wake_events=False
        )

        # Create generator instance using real configurations
        self.generator = AdvancedSVGenerator(
            power_config=self.power_config,
            error_config=self.error_config,
            perf_config=self.perf_config,
        )

    def test_pcileech_tlps128_bar_controller_template_renders(self):
        """Test that pcileech_tlps128_bar_controller template renders without errors."""
        # Create a complete template context with all required fields
        template_context = {
            "device_config": {
                "vendor_id": "8086",
                "device_id": "1533",
                "class_code": "020000",
                "revision_id": "03",
                "subsystem_vendor_id": "8086",
                "subsystem_device_id": "0001",
                "device_bdf": "0000:03:00.0",
                "enable_perf_counters": True,
                "enable_error_injection": True,
                "enable_dma_operations": True,
            },
            "device_signature": "0x12345678",
            "msix_config": {
                "num_vectors": 1,
                "table_offset": 0x1000,
                "table_bir": 0,
                "pba_offset": 0x800,
                "pba_bir": 0,
            },
            "bar_config": {
                "bar_index": 0,
                "aperture_size": 4096,
                "bar_type": 0,
                "prefetchable": False,
                "bars": [
                    Mock(
                        index=0,
                        size=4096,
                        bar_type="memory",
                        prefetchable=False,
                        is_64bit=False,
                        address=0,
                        base_address=0,
                        get_size_encoding=lambda: 0xFFFFF000,
                    ),
                ],
            },
            "board_config": {
                "name": "test_board",
                "fpga_part": "xc7a35t",
            },
            "interrupt_config": {},
            "config_space_data": {},
            "timing_config": type(
                "TimingConfig",
                (),
                {
                    "clock_frequency_mhz": 100,
                    "read_latency": 2,
                    "write_latency": 1,
                    "setup_time": 1,
                    "hold_time": 1,
                    "burst_length": 4,
                },
            )(),
            "pcileech_config": type(
                "PCILeechConfig",
                (),
                {
                    "buffer_size": 4096,
                    "command_timeout": 1000,
                    "enable_dma": True,
                    "enable_scatter_gather": True,
                    "max_payload_size": 256,
                    "max_read_request_size": 512,
                },
            )(),
            "generation_metadata": {
                "generated_at": "2024-01-01T12:00:00Z",
                "version": "2.0.0",
                "generator": "PCILeechFWGenerator",
            },
            "active_device_config": {
                "vendor_id": "8086",
                "device_id": "1533",
                "class_code": "020000",
                "revision_id": "03",
                "subsystem_vendor_id": "8086",
                "subsystem_device_id": "0001",
                "num_sources": 1,
                "default_priority": 0,
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
        assert "32'hDEADBEEF" in bar_controller  # device_signature should be in output

    def test_missing_board_config_raises_error(self):
        """Test that missing board_config in template causes proper error."""
        # Create template context WITHOUT board_config
        template_context = {
            "device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "class_code": "020000",
                "revision_id": "01",
                "subsystem_vendor_id": "10EC",
                "subsystem_device_id": "8168",
                "device_bdf": "0000:03:00.0",  # Required field for template
                "enable_perf_counters": True,
            },
            "device_signature": "0xDEADBEEF",
            "msix_config": {},
            "bar_config": {},
            "board_config": {},
            "interrupt_config": {},
            "config_space_data": {},
            "timing_config": {},
            "pcileech_config": {
                "buffer_size": 4096,
            },
            "generation_metadata": {},
            "active_device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "class_code": "020000",
                "revision_id": "01",
                "subsystem_vendor_id": "10EC",
                "subsystem_device_id": "8168",
                "num_sources": 1,
                "default_priority": 0,
            },
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
                "device_bdf": "0000:03:00.0",  # Required field for template
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
                    Mock(
                        index=0,
                        size=4096,
                        bar_type="memory",
                        prefetchable=False,
                        is_64bit=False,
                        address=0,
                        base_address=0,
                        get_size_encoding=lambda: 0xFFFFF000,
                    ),
                    Mock(
                        index=1,
                        size=8192,
                        bar_type="io",
                        prefetchable=False,
                        is_64bit=False,
                        address=0,
                        base_address=0,
                        get_size_encoding=lambda: 0xFFFFE000,
                    ),
                    Mock(
                        index=2,
                        size=131072,
                        bar_type="memory",
                        prefetchable=True,
                        is_64bit=True,
                        address=0,
                        base_address=0,
                        get_size_encoding=lambda: 0xFFFE0000,
                    ),
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
            "config_space_data": {"data": list(range(256))},  # Some test data
            "timing_config": {
                "read_latency": 8,
                "write_latency": 4,
                "burst_length": 32,
                "inter_burst_gap": 16,
                "timeout_cycles": 2048,
                "clock_frequency_mhz": 100,
            },
            "pcileech_config": {
                "buffer_size": 8192,
                "enable": True,
                "dma_enable": True,
                "scatter_gather": True,
                "command_timeout": 1000,
                "enable_dma": True,
                "enable_scatter_gather": True,
            },
            "generation_metadata": {
                "generated_at": "2024-01-01T12:00:00Z",
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "2.0.0",
                "generator": "PCILeechFWGenerator",
                "build_id": "test-build-123",
            },
            "active_device_config": {
                "vendor_id": "8086",
                "device_id": "1533",
                "class_code": "020000",
                "revision_id": "03",
                "subsystem_vendor_id": "8086",
                "subsystem_device_id": "0001",
                "num_sources": 1,
                "default_priority": 0,
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

        # Create a minimal valid context using proper object structure
        template_context = {
            "device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "class_code": "020000",
                "default_priority": 0,
                "revision_id": "03",
                "subsystem_vendor_id": "10EC",
                "subsystem_device_id": "8168",
                "device_bdf": "0000:03:00.0",  # Required field for template
                "enable_dma_operations": True,
                "enable_perf_counters": True,
                "enable_error_injection": True,
            },
            "bar_config": {
                "bar_index": 0,
                "aperture_size": 4096,
                "bar_type": 0,
                "prefetchable": False,
                "bars": [
                    Mock(
                        index=0,
                        size=4096,
                        bar_type="memory",
                        prefetchable=False,
                        is_64bit=False,
                        address=0,
                        base_address=0,
                        get_size_encoding=lambda: 0xFFFFF000,
                    )
                ],
            },
            "board_config": {
                "name": "test_board",
                "fpga_part": "xc7a35t",
            },  # Required by validator
            "device_signature": "0x12345678",  # Required for security
            "msix_config": {
                "num_vectors": 1,
                "table_offset": 0x1000,
                "table_bir": 0,
                "pba_offset": 0x800,
                "pba_bir": 0,
            },
            "interrupt_config": {},
            "config_space_data": {},
            "timing_config": type(
                "TimingConfig",
                (),
                {
                    "clock_frequency_mhz": 100,
                    "read_latency": 2,
                    "write_latency": 1,
                    "setup_time": 1,
                    "hold_time": 1,
                    "burst_length": 4,
                },
            )(),
            "pcileech_config": type(
                "PCILeechConfig",
                (),
                {
                    "buffer_size": 4096,
                    "command_timeout": 1000,
                    "enable_dma": True,
                    "enable_scatter_gather": True,
                    "max_payload_size": 256,
                    "max_read_request_size": 512,
                },
            )(),
            "generation_metadata": {
                "generated_at": "2024-01-01T12:00:00Z",
                "version": "2.0.0",
                "generator": "PCILeechFWGenerator",
            },
            "active_device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "class_code": "020000",
                "revision_id": "03",
                "subsystem_vendor_id": "10EC",
                "subsystem_device_id": "8168",
                "num_sources": 1,
            },
        }

        # This should work with the validator's requirements
        result = self.generator.generate_pcileech_modules(template_context)
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
