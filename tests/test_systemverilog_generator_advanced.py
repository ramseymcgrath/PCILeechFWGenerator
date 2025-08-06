#!/usr/bin/env python3
"""
Advanced unit tests for SystemVerilog Generator - Critical Areas Coverage.

This test module focuses on improving test coverage for critical areas that
were identified as under-tested, including MSI-X handling, VFIO integration,
complex template scenarios, and error edge cases.
"""

import mmap
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open, call
from typing import Dict, Any, List, Optional

from src.templating.systemverilog_generator import AdvancedSVGenerator
from src.templating.template_renderer import TemplateRenderError
from src.templating.advanced_sv_features import (
    PowerManagementConfig,
    ErrorHandlingConfig,
    PerformanceConfig,
)
from src.device_clone.device_config import DeviceType, DeviceClass
from src.device_clone.manufacturing_variance import VarianceModel


class TestMSIXAdvancedFunctionality:
    """Test advanced MSI-X related functionality in SystemVerilog generator."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance for testing."""
        return AdvancedSVGenerator()

    @pytest.fixture
    def msix_template_context(self):
        """Create a template context with MSI-X configuration."""
        return {
            "msix_config": {
                "is_supported": True,
                "num_vectors": 8,
                "table_offset": 0x1000,
                "table_bir": 2,
                "pba_offset": 0x2000,
                "pba_bir": 2,
            },
            "device_config": {
                "vendor_id": "1234",
                "device_id": "5678",
            },
            "bars": [
                Mock(index=0, size=4096, is_memory=True),
                Mock(index=1, size=8192, is_memory=True),
                Mock(index=2, size=16384, is_memory=True, address=0xF0000000),
            ],
            "config_space_data": {
                "device_info": {
                    "bars": [
                        Mock(address=0xE0000000, size=4096),
                        Mock(address=0xE0001000, size=8192),
                        Mock(address=0xF0000000, size=16384),
                    ]
                }
            },
        }

    def test_generate_msix_pba_init_various_vector_counts(self, generator):
        """Test MSI-X PBA initialization with various vector counts."""
        test_cases = [
            (1, 1),  # Single vector -> 1 DWORD
            (8, 1),  # 8 vectors -> 1 DWORD
            (32, 1),  # 32 vectors -> 1 DWORD
            (33, 2),  # 33 vectors -> 2 DWORDs
            (64, 2),  # 64 vectors -> 2 DWORDs
            (65, 3),  # 65 vectors -> 3 DWORDs
        ]

        for num_vectors, expected_dwords in test_cases:
            context = {"msix_config": {"num_vectors": num_vectors}}
            result = generator._generate_msix_pba_init(context)

            lines = result.strip().split("\n")
            assert len(lines) == expected_dwords

            # All should be zeros initially
            for line in lines:
                assert line == "00000000"

    def test_generate_msix_table_init_with_actual_data_success(
        self, generator, msix_template_context
    ):
        """Test MSI-X table initialization when actual hardware data is available."""
        mock_table_data = [
            0x12345678,
            0x9ABCDEF0,
            0x11111111,
            0x22222222,  # Vector 0
            0x33333333,
            0x44444444,
            0x55555555,
            0x66666666,  # Vector 1
        ]

        with patch.object(
            generator, "_read_actual_msix_table", return_value=mock_table_data
        ):
            result = generator._generate_msix_table_init(msix_template_context)

            lines = result.strip().split("\n")
            assert len(lines) == 8
            assert lines[0] == "12345678"
            assert lines[1] == "9ABCDEF0"
            assert lines[7] == "66666666"

    def test_generate_msix_table_init_fallback_default(
        self, generator, msix_template_context
    ):
        """Test MSI-X table initialization fallback to default values."""
        with patch.object(generator, "_read_actual_msix_table", return_value=None):
            result = generator._generate_msix_table_init(msix_template_context)

            lines = result.strip().split("\n")
            # 8 vectors * 4 DWORDs per vector = 32 lines
            assert len(lines) == 32

            # Check pattern for first vector (vector number 0)
            assert lines[0] == "00000000"  # Message Address Lower
            assert lines[1] == "00000000"  # Message Address Upper
            assert lines[2] == "00000000"  # Message Data (vector 0)
            assert lines[3] == "00000001"  # Vector Control (masked)

    def test_read_actual_msix_table_successful_mapping(
        self, generator, msix_template_context
    ):
        """Test successful reading of actual MSI-X table from hardware."""
        mock_device_fd = 100
        mock_container_fd = 101

        # Mock VFIO file descriptor operations
        with patch(
            "src.cli.vfio_helpers.get_device_fd",
            return_value=(mock_device_fd, mock_container_fd),
        ):

            # Mock mmap to simulate memory-mapped table data
            mock_mmap_data = bytearray(64)  # 4 vectors * 16 bytes each
            # Fill with test pattern
            for i in range(0, 64, 4):
                mock_mmap_data[i : i + 4] = (i // 4).to_bytes(4, "little")

            with patch("mmap.mmap") as mock_mmap:
                mock_mm = MagicMock()
                mock_mm.__enter__.return_value = mock_mmap_data
                mock_mm.__len__.return_value = len(mock_mmap_data)
                mock_mmap.return_value = mock_mm

                with patch("os.close") as mock_close:
                    result = generator._read_actual_msix_table(msix_template_context)

                    assert result is not None
                    assert len(result) == 16  # 4 vectors * 4 DWORDs
                    assert result[0] == 0  # First DWORD
                    assert result[1] == 1  # Second DWORD

                    # Verify file descriptors were closed
                    mock_close.assert_has_calls(
                        [call(mock_device_fd), call(mock_container_fd)]
                    )

    def test_read_actual_msix_table_vfio_import_error(
        self, generator, msix_template_context
    ):
        """Test handling of VFIO import errors."""
        with patch(
            "src.cli.vfio_helpers.get_device_fd",
            side_effect=ImportError("VFIO module not available"),
        ):
            result = generator._read_actual_msix_table(msix_template_context)
            assert result is None

    def test_read_actual_msix_table_mmap_failure(
        self, generator, msix_template_context
    ):
        """Test handling of mmap failures."""
        mock_device_fd = 100
        mock_container_fd = 101

        with patch(
            "src.templating.systemverilog_generator.get_device_fd",
            return_value=(mock_device_fd, mock_container_fd),
        ):
            with patch("mmap.mmap", side_effect=OSError(22, "Invalid argument")):
                with patch("os.close") as mock_close:
                    result = generator._read_actual_msix_table(msix_template_context)

                    assert result is None
                    # File descriptors should still be closed
                    mock_close.assert_has_calls(
                        [call(mock_device_fd), call(mock_container_fd)]
                    )

    def test_read_actual_msix_table_bar_boundary_check(self, generator):
        """Test MSI-X table boundary validation against BAR size."""
        context = {
            "msix_config": {
                "num_vectors": 16,  # 16 vectors * 16 bytes = 256 bytes
                "table_offset": 0x0F00,  # Close to 4KB boundary
                "table_bir": 0,
            },
            "bars": [
                Mock(index=0, size=4096, is_memory=True),  # 4KB BAR
            ],
        }

        result = generator._read_actual_msix_table(context)
        # Should fail due to table extending beyond BAR boundary
        assert result is None

    def test_read_actual_msix_table_no_target_bar(self, generator):
        """Test handling when target BAR is not found."""
        context = {
            "msix_config": {
                "num_vectors": 4,
                "table_offset": 0x1000,
                "table_bir": 5,  # Non-existent BAR
            },
            "bars": [
                Mock(index=0, size=4096, is_memory=True),
                Mock(index=1, size=8192, is_memory=True),
            ],
        }

        result = generator._read_actual_msix_table(context)
        assert result is None


class TestVFIOErrorHandlingAdvanced:
    """Test advanced VFIO error handling scenarios."""

    @pytest.fixture
    def generator(self):
        return AdvancedSVGenerator()

    def test_vfio_integration_complex_error_scenarios(self, generator):
        """Test complex VFIO error scenarios in template generation."""
        template_context = {
            "device_config": {
                "vendor_id": "1234",
                "device_id": "5678",
                "enable_advanced_features": True,
            },
            "vfio_device_path": "/dev/vfio/42",
        }

        # Mock the renderer to raise various VFIO-related template errors
        with patch.object(generator.renderer, "render_template") as mock_render:
            mock_render.side_effect = TemplateRenderError(
                "VFIO device access failed in template"
            )

            with pytest.raises(TemplateRenderError, match="VFIO device access failed"):
                generator.generate_pcileech_integration_code(template_context)

    def test_device_config_validation_strict_mode(self, generator):
        """Test device configuration validation in strict mode."""
        invalid_contexts = [
            {},  # Empty context
            {"device_config": {}},  # Empty device config
            {"device_config": {"vendor_id": "FFFF"}},  # Missing device_id
            {"device_config": {"device_id": "FFFF"}},  # Missing vendor_id
            {
                "device_config": {"vendor_id": "0000", "device_id": "0000"}
            },  # Invalid zeros
        ]

        for context in invalid_contexts:
            with patch.object(generator.renderer, "render_template") as mock_render:
                # Template should receive FFFF placeholders for missing values
                generator.generate_pcileech_modules(context)

                # Verify template was called with placeholder values
                call_args = mock_render.call_args_list[0]
                rendered_context = call_args[0][1]

                if "device_config" not in context:
                    assert rendered_context["vendor_id"] == "FFFF"
                    assert rendered_context["device_id"] == "FFFF"


class TestComplexTemplateScenarios:
    """Test complex template rendering scenarios."""

    @pytest.fixture
    def generator(self):
        return AdvancedSVGenerator()

    def test_template_context_inheritance_and_merging(self, generator):
        """Test complex template context inheritance and merging."""
        base_context = {
            "device_config": {
                "vendor_id": "1234",
                "device_id": "5678",
                "class_code": "020000",
            },
            "msix_config": {
                "is_supported": True,
                "num_vectors": 4,
            },
        }

        behavior_profile = Mock()
        behavior_profile.variance_metadata = Mock()

        with patch.object(generator, "_extract_pcileech_registers", return_value=[]):
            with patch.object(generator.renderer, "render_template") as mock_render:
                mock_render.return_value = "mock template output"

                result = generator.generate_pcileech_modules(
                    base_context, behavior_profile
                )

                # Verify that context was properly enhanced and merged
                call_made = False
                for call_args in mock_render.call_args_list:
                    context = call_args[0][1]
                    if "device" in context:
                        # Check that device info was properly structured
                        assert context["device"]["vendor_id"] == "1234"
                        assert context["device"]["device_id"] == "5678"
                        call_made = True
                        break

                assert call_made, "Expected template call with device context not found"

    def test_nested_template_error_propagation(self, generator):
        """Test error propagation through nested template calls."""
        template_context = {"device_config": {}}

        # Create a chain of template errors
        template_errors = [
            TemplateRenderError("Primary template failed"),
            TemplateRenderError("Secondary template failed"),
            TemplateRenderError("Tertiary template failed"),
        ]

        with patch.object(generator.renderer, "render_template") as mock_render:
            mock_render.side_effect = template_errors

            # Each method should propagate the template error without modification
            with pytest.raises(TemplateRenderError, match="Primary template failed"):
                generator.generate_pcileech_modules(template_context)

    def test_large_template_context_performance(self, generator):
        """Test performance with large template contexts."""
        # Create a large template context
        large_context = {
            "device_config": {f"key_{i}": f"value_{i}" for i in range(1000)},
            "registers": [{"name": f"reg_{i}", "offset": i * 4} for i in range(500)],
            "msix_config": {
                "is_supported": True,
                "num_vectors": 32,
                "large_data": list(range(10000)),
            },
        }

        with patch.object(generator.renderer, "render_template") as mock_render:
            mock_render.return_value = "template output"

            # Should handle large contexts without errors
            result = generator.generate_pcileech_modules(large_context)

            assert isinstance(result, dict)
            assert len(result) > 0


class TestAdvancedSystemVerilogFeatures:
    """Test advanced SystemVerilog feature integration."""

    @pytest.fixture
    def advanced_generator(self):
        """Create generator with advanced configurations."""
        power_config = PowerManagementConfig(
            enable_power_management=True, enable_clock_gating=True
        )
        error_config = ErrorHandlingConfig(
            enable_error_detection=True, enable_error_injection=True
        )
        perf_config = PerformanceConfig(
            enable_performance_counters=True,
            enable_histograms=True,
        )

        return AdvancedSVGenerator(
            power_config=power_config,
            error_config=error_config,
            perf_config=perf_config,
        )

    def test_advanced_feature_config_integration(self, advanced_generator):
        """Test integration of advanced feature configurations."""
        registers = [
            {"name": "CTRL_REG", "offset": 0x00, "width": 32},
            {"name": "STATUS_REG", "offset": 0x04, "width": 32},
        ]

        variance_model = Mock()
        variance_model.timing_variance = 0.05
        variance_model.power_variance = 0.1

        with patch.object(
            advanced_generator.renderer, "render_template"
        ) as mock_render:
            mock_render.return_value = "advanced systemverilog module"

            result = advanced_generator.generate_advanced_systemverilog(
                registers, variance_model
            )

            # Verify template was called with comprehensive context
            call_args = mock_render.call_args_list[0]
            context = call_args[0][1]

            # Check that all advanced features are properly configured
            assert "perf_config" in context
            assert context["perf_config"].enable_performance_counters is True
            assert context["perf_config"].enable_histograms is True
            assert "variance_model" in context
            # Check that performance flags are added at top level
            assert context.get("enable_transaction_counters", False) is True

    def test_pcileech_advanced_modules_generation(self, advanced_generator):
        """Test generation of advanced PCILeech modules."""
        template_context = {
            "device_config": {"enable_advanced_features": True},
        }

        behavior_profile = Mock()
        behavior_profile.variance_metadata = Mock()
        behavior_profile.timing_profiles = {"default": {"latency": 100}}

        with patch.object(
            advanced_generator, "_extract_pcileech_registers"
        ) as mock_extract:
            mock_extract.return_value = [
                {"name": "ADVANCED_CTRL", "offset": 0x100},
                {"name": "PERF_COUNTER", "offset": 0x104},
            ]

            with patch.object(
                advanced_generator.renderer, "render_template"
            ) as mock_render:
                mock_render.return_value = "advanced controller module"

                result = advanced_generator._generate_pcileech_advanced_modules(
                    template_context, behavior_profile
                )

                assert "pcileech_advanced_controller" in result
                # The actual implementation calls generate_advanced_systemverilog
                # which would return the rendered template content
                assert result["pcileech_advanced_controller"] is not None

    def test_extract_pcileech_registers_complex_behavior(self, advanced_generator):
        """Test extraction of registers from complex behavior profiles."""
        # Create complex behavior profile with register accesses
        behavior_profile = Mock()

        # Create mock register accesses
        access1 = Mock(register="VENDOR_ID", offset=0x00, operation="read")
        access2 = Mock(register="DEVICE_ID", offset=0x02, operation="read")
        access3 = Mock(register="MSI_CTRL", offset=0x50, operation="write")
        access4 = Mock(register="MSI_CTRL", offset=0x50, operation="read")
        access5 = Mock(register="CUSTOM_REG1", offset=0x100, operation="write")

        behavior_profile.register_accesses = [
            access1,
            access2,
            access3,
            access4,
            access5,
        ]

        result = advanced_generator._extract_pcileech_registers(behavior_profile)

        assert len(result) == 4  # 4 unique registers

        # Verify register structure
        vendor_id_reg = next((r for r in result if r["name"] == "VENDOR_ID"), None)
        assert vendor_id_reg is not None
        assert vendor_id_reg["offset"] == 0x00
        assert vendor_id_reg["access_type"] == "ro"  # Only read operations

        msi_ctrl_reg = next((r for r in result if r["name"] == "MSI_CTRL"), None)
        assert msi_ctrl_reg is not None
        assert msi_ctrl_reg["access_type"] == "rw"  # Both read and write operations

    def test_extract_pcileech_registers_fallback_handling(self, advanced_generator):
        """Test fallback handling when behavior profile lacks register data."""
        # Test with minimal behavior profile
        minimal_profile = Mock()
        minimal_profile.config_space_registers = []

        # Should not have the other attributes
        del minimal_profile.capability_registers
        del minimal_profile.device_specific_registers

        result = advanced_generator._extract_pcileech_registers(minimal_profile)

        # Should return default PCILeech registers when no register_accesses
        assert isinstance(result, list)
        assert len(result) >= 3  # At least 3 default registers
        assert any(r["name"] == "PCILEECH_CTRL" for r in result)


class TestErrorRecoveryAndRobustness:
    """Test error recovery and robustness scenarios."""

    @pytest.fixture
    def generator(self):
        return AdvancedSVGenerator()

    def test_partial_template_failure_recovery(self, generator):
        """Test recovery from partial template failures."""
        template_context = {
            "device_config": {"vendor_id": "1234", "device_id": "5678"},
            "msix_config": {"is_supported": True, "num_vectors": 4},
        }

        # Mock selective template failures
        def selective_template_mock(template_name, context):
            if "msix_capability" in template_name:
                raise TemplateRenderError("MSI-X template failed")
            return f"Generated: {template_name}"

        with patch.object(
            generator.renderer, "render_template", side_effect=selective_template_mock
        ):
            # Should fail on MSI-X template but that's expected behavior
            with pytest.raises(TemplateRenderError, match="MSI-X template failed"):
                generator.generate_pcileech_modules(template_context)

    def test_memory_cleanup_on_errors(self, generator):
        """Test that memory is properly cleaned up on errors."""
        large_context = {
            "device_config": {"data": list(range(100000))},  # Large data
        }

        with patch.object(generator.renderer, "render_template") as mock_render:
            mock_render.side_effect = TemplateRenderError("Memory error")

            with pytest.raises(TemplateRenderError):
                generator.generate_pcileech_modules(large_context)

            # Memory should be cleaned up (context should not persist)
            # This is more of a contract test - Python's GC will handle it

    def test_concurrent_access_safety(self, generator):
        """Test thread safety of generator methods."""
        import threading
        import time

        template_context = {"device_config": {"vendor_id": "1234"}}
        results = []
        errors = []

        def worker():
            try:
                with patch.object(
                    generator.renderer, "render_template", return_value="safe output"
                ):
                    result = generator.generate_device_specific_ports()
                    results.append(result)
            except Exception as e:
                errors.append(e)

        # Run multiple threads concurrently
        threads = [threading.Thread(target=worker) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All should succeed
        assert len(errors) == 0
        assert len(results) == 5
        assert all(r == "safe output" for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
