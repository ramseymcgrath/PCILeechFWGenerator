#!/usr/bin/env python3
"""
Comprehensive test coverage for SystemVerilog Generator critical paths.

This test module focuses on covering the uncovered critical paths identified
in the SystemVerilog generator, particularly the MSI-X table reading and
BAR matching logic that was highlighted in the attached code.
"""

import mmap
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open, call
from typing import Dict, Any, List, Optional

from src.templating.systemverilog_generator import AdvancedSVGenerator
from src.templating.template_renderer import TemplateRenderError
from src.device_clone.device_config import DeviceType, DeviceClass


class TestMSIXTableReadingCriticalPaths:
    """Test the critical MSI-X table reading paths that were uncovered."""

    @pytest.fixture
    def generator(self):
        return AdvancedSVGenerator()

    @pytest.fixture
    def complex_msix_context(self):
        """Create complex MSI-X context matching the attached code patterns."""
        return {
            "msix_config": {
                "table_bir": 2,
                "table_offset": 0x1000,
                "num_vectors": 8,
            },
            "bar_config": {
                "bars": [
                    Mock(index=0, size=4096, is_memory=True, base_address=0xE0000000),
                    Mock(index=1, size=8192, is_memory=True, base_address=0xE0001000),
                    Mock(index=2, size=16384, is_memory=True, base_address=0xF0000000),
                ]
            },
            "config_space_data": {
                "device_info": {
                    "bars": [
                        Mock(address=0xE0000000, size=4096),
                        Mock(address=0xE0001000, size=8192),
                        Mock(address=0xF0000000, size=16384),
                    ]
                },
                "bars": [  # Fallback bars array
                    Mock(address=0xE0000000, size=4096),
                    Mock(address=0xE0001000, size=8192),
                    Mock(address=0xF0000000, size=16384),
                ],
            },
            "device_config": {
                "device_bdf": "0000:01:00.0",
                "vendor_id": "1234",
                "device_id": "5678",
            },
        }

    def test_bar_matching_direct_bir_match(self, generator, complex_msix_context):
        """Test direct BIR matching logic - covers lines 783-792 in attached code."""
        # Mock the VFIO helper import
        with patch("src.cli.vfio_helpers.get_device_fd") as mock_get_fd:
            mock_get_fd.return_value = (100, 101)

            with patch("mmap.mmap") as mock_mmap:
                # Simulate successful mmap
                mock_mm = MagicMock()
                mock_mm.__enter__.return_value = bytearray(64)  # Sufficient size
                mock_mm.__len__.return_value = 64
                mock_mmap.return_value = mock_mm

                with patch("os.close"):
                    result = generator._read_actual_msix_table(complex_msix_context)

                    # Should find BAR 2 directly and succeed
                    assert result is not None
                    assert len(result) >= 0

    def test_bar_matching_no_direct_match_analysis(
        self, generator, complex_msix_context
    ):
        """Test BAR analysis when no direct match - covers lines 794-850 in attached code."""
        # Modify context to have no direct BAR match
        complex_msix_context["msix_config"]["table_bir"] = 5  # Non-existent BAR

        with patch("src.cli.vfio_helpers.get_device_fd") as mock_get_fd:
            mock_get_fd.return_value = (100, 101)

            with patch("os.close"):
                result = generator._read_actual_msix_table(complex_msix_context)

                # Should attempt analysis but fail to find suitable BAR
                assert result is None

    def test_bar_matching_by_address(self, generator, complex_msix_context):
        """Test BAR matching by address - covers lines 825-850 in attached code."""
        # Set up scenario where BIR doesn't match but address does
        bars = complex_msix_context["bar_config"]["bars"]
        # Set up VFIO bars with matching address
        for bar in bars:
            if bar.index == 2:
                bar.base_address = 0xF0000000  # Match the config space address

        complex_msix_context["msix_config"]["table_bir"] = 5  # Force no direct match

        with patch("src.cli.vfio_helpers.get_device_fd") as mock_get_fd:
            mock_get_fd.return_value = (100, 101)

            with patch("mmap.mmap") as mock_mmap:
                mock_mm = MagicMock()
                mock_mm.__enter__.return_value = bytearray(64)
                mock_mm.__len__.return_value = 64
                mock_mmap.return_value = mock_mm

                with patch("os.close"):
                    result = generator._read_actual_msix_table(complex_msix_context)

                    # Should succeed by matching address
                    assert result is not None

    def test_largest_memory_bar_fallback(self, generator, complex_msix_context):
        """Test largest memory BAR fallback - covers lines 851-871 in attached code."""
        # Remove address matching to force fallback
        for bar in complex_msix_context["config_space_data"]["device_info"]["bars"]:
            bar.address = None

        complex_msix_context["msix_config"]["table_bir"] = 5  # Force no direct match

        with patch("src.cli.vfio_helpers.get_device_fd") as mock_get_fd:
            mock_get_fd.return_value = (100, 101)

            with patch("mmap.mmap") as mock_mmap:
                mock_mm = MagicMock()
                mock_mm.__enter__.return_value = bytearray(128)
                mock_mm.__len__.return_value = 128
                mock_mmap.return_value = mock_mm

                with patch("os.close"):
                    result = generator._read_actual_msix_table(complex_msix_context)

                    # Should use largest memory BAR (BAR 2 with 16384 bytes)
                    assert result is not None

    def test_no_suitable_bar_found(self, generator):
        """Test when no suitable BAR is found - covers lines 875-879 in attached code."""
        context = {
            "msix_config": {
                "table_bir": 5,
                "table_offset": 0x1000,
                "num_vectors": 4,
            },
            "bar_config": {"bars": []},  # No BARs available
            "config_space_data": {"device_info": {"bars": []}},
            "device_config": {"device_bdf": "0000:01:00.0"},
        }

        result = generator._read_actual_msix_table(context)
        assert result is None

    def test_mmap_einval_error_handling(self, generator, complex_msix_context):
        """Test mmap EINVAL error handling - covers lines 940-950 in attached code."""
        with patch("src.cli.vfio_helpers.get_device_fd") as mock_get_fd:
            mock_get_fd.return_value = (100, 101)

            with patch("mmap.mmap") as mock_mmap:
                # Simulate EINVAL error
                einval_error = OSError()
                einval_error.errno = 22  # EINVAL
                mock_mmap.side_effect = einval_error

                with patch("os.close"):
                    result = generator._read_actual_msix_table(complex_msix_context)

                    assert result is None

    def test_msix_table_boundary_validation(self, generator, complex_msix_context):
        """Test MSI-X table boundary validation - covers lines 895-904 in attached code."""
        # Set up scenario where table extends beyond BAR boundary
        complex_msix_context["msix_config"][
            "table_offset"
        ] = 16000  # Near end of 16KB BAR
        complex_msix_context["msix_config"]["num_vectors"] = 32  # Large table

        with patch("src.cli.vfio_helpers.get_device_fd") as mock_get_fd:
            mock_get_fd.return_value = (100, 101)

            with patch("os.close"):
                result = generator._read_actual_msix_table(complex_msix_context)

                # Should fail due to boundary violation
                assert result is None

    def test_msix_table_successful_read_with_truncation(
        self, generator, complex_msix_context
    ):
        """Test successful read with truncation handling - covers lines 913-935 in attached code."""
        with patch("src.cli.vfio_helpers.get_device_fd") as mock_get_fd:
            mock_get_fd.return_value = (100, 101)

            with patch("mmap.mmap") as mock_mmap:
                # Create mock memory that's smaller than expected
                mock_data = bytearray(48)  # Only space for 3 vectors instead of 8
                for i in range(0, 48, 4):
                    mock_data[i : i + 4] = (i // 4 + 1).to_bytes(4, "little")

                mock_mm = MagicMock()
                # Make the mock behave like the actual bytearray
                mock_mm.__getitem__ = lambda self, key: mock_data.__getitem__(key)
                mock_mm.__len__ = lambda self: len(mock_data)
                mock_mm.__enter__.return_value = mock_mm
                mock_mmap.return_value = mock_mm

                with patch("os.close"):
                    result = generator._read_actual_msix_table(complex_msix_context)

                    assert result is not None
                    assert len(result) == 12  # Should stop at boundary
                    assert result[0] == 1  # First DWORD
                    assert result[11] == 12  # Last DWORD

    def test_exception_handling_in_msix_read(self, generator, complex_msix_context):
        """Test general exception handling - covers lines 957-964 in attached code."""
        with patch("src.cli.vfio_helpers.get_device_fd") as mock_get_fd:
            mock_get_fd.side_effect = RuntimeError("Unexpected VFIO error")

            result = generator._read_actual_msix_table(complex_msix_context)
            assert result is None


class TestMSIXInitializationFilesGeneration:
    """Test MSI-X initialization file generation paths."""

    @pytest.fixture
    def generator(self):
        return AdvancedSVGenerator()

    def test_msix_table_init_with_hardware_data(self, generator):
        """Test MSI-X table initialization using actual hardware data."""
        context = {
            "msix_config": {"num_vectors": 4},
            "device_config": {"device_bdf": "0000:01:00.0"},
        }

        # Mock successful hardware read
        hardware_data = [
            0x12345678,
            0x9ABCDEF0,
            0x11111111,
            0x22222222,  # Vector 0
            0x33333333,
            0x44444444,
            0x55555555,
            0x66666666,  # Vector 1
            0x77777777,
            0x88888888,
            0x99999999,
            0xAAAAAAAA,  # Vector 2
            0xBBBBBBBB,
            0xCCCCCCCC,
            0xDDDDDDDD,
            0xEEEEEEEE,  # Vector 3
        ]

        with patch.object(
            generator, "_read_actual_msix_table", return_value=hardware_data
        ):
            result = generator._generate_msix_table_init(context)

            lines = result.strip().split("\n")
            assert len(lines) == 16
            assert lines[0] == "12345678"
            assert lines[15] == "EEEEEEEE"

    def test_msix_table_init_fallback_patterns(self, generator):
        """Test fallback patterns for MSI-X table initialization."""
        context = {
            "msix_config": {"num_vectors": 3},
            "device_config": {"device_bdf": "0000:01:00.0"},
        }

        with patch.object(generator, "_read_actual_msix_table", return_value=None):
            result = generator._generate_msix_table_init(context)

            lines = result.strip().split("\n")
            assert len(lines) == 12  # 3 vectors * 4 DWORDs

            # Check vector patterns
            for vector_idx in range(3):
                base_idx = vector_idx * 4
                assert lines[base_idx] == "00000000"  # Address Low
                assert lines[base_idx + 1] == "00000000"  # Address High
                assert lines[base_idx + 2] == f"{vector_idx:08X}"  # Message Data
                assert lines[base_idx + 3] == "00000001"  # Control (masked)

    def test_msix_pba_init_edge_cases(self, generator):
        """Test MSI-X PBA initialization edge cases."""
        test_cases = [
            (0, 0),  # Zero vectors - edge case
            (1, 1),  # Single vector
            (31, 1),  # Just under 32
            (32, 1),  # Exactly 32
            (33, 2),  # Just over 32
            (63, 2),  # Just under 64
            (64, 2),  # Exactly 64
            (2048, 64),  # Maximum MSI-X vectors
        ]

        for num_vectors, expected_dwords in test_cases:
            context = {"msix_config": {"num_vectors": num_vectors}}
            result = generator._generate_msix_pba_init(context)

            if num_vectors == 0:
                assert result.strip() == ""
            else:
                lines = result.strip().split("\n")
                assert len(lines) == expected_dwords
                for line in lines:
                    assert line == "00000000"


class TestPCILeechModuleGeneration:
    """Test PCILeech module generation critical paths."""

    @pytest.fixture
    def generator(self):
        return AdvancedSVGenerator()

    def test_pcileech_modules_comprehensive_generation(self, generator):
        """Test comprehensive PCILeech module generation."""
        template_context = {
            "device_config": {
                "vendor_id": "1234",
                "device_id": "5678",
                "subsystem_vendor_id": "ABCD",
                "subsystem_device_id": "EFGH",
                "class_code": "020000",
                "revision_id": "10",
                "enable_advanced_features": True,
            },
            "msix_config": {
                "is_supported": True,
                "num_vectors": 16,
                "table_offset": 0x2000,
                "table_bir": 1,
                "pba_offset": 0x3000,
                "pba_bir": 1,
            },
            "interrupt_config": {
                "vectors": 16,
            },
            "bar_config": {
                "bars": [
                    {"index": 0, "size": 4096},
                    {"index": 1, "size": 65536},
                ]
            },
        }

        with patch.object(generator.renderer, "render_template") as mock_render:
            mock_render.return_value = "mock module content"

            result = generator.generate_pcileech_modules(template_context)

            # Should generate all core modules
            expected_modules = [
                "pcileech_tlps128_bar_controller",
                "pcileech_fifo",
                "top_level_wrapper",
                "pcileech_cfgspace.coe",
                "msix_capability_registers",
                "msix_implementation",
                "msix_table",
                "msix_pba_init.hex",
                "msix_table_init.hex",
            ]

            for module in expected_modules:
                assert module in result
                assert result[module] is not None

    def test_device_context_enhancement(self, generator):
        """Test device context enhancement logic."""
        minimal_context = {
            "device_config": {
                "vendor_id": "8086",
                "device_id": "1234",
            }
        }

        with patch.object(generator.renderer, "render_template") as mock_render:
            mock_render.return_value = "enhanced module"

            generator.generate_pcileech_modules(minimal_context)

            # Check that context was enhanced
            call_args = mock_render.call_args_list[0]
            enhanced_context = call_args[0][1]

            # Should have device info structure
            assert "device" in enhanced_context
            assert enhanced_context["device"]["vendor_id"] == "8086"
            assert enhanced_context["device"]["device_id"] == "1234"

            # Should have enable flags
            assert "enable_custom_config" in enhanced_context
            assert "enable_scatter_gather" in enhanced_context

    def test_msix_conditional_generation(self, generator):
        """Test conditional MSI-X module generation."""
        # Test with MSI-X disabled
        context_no_msix = {
            "device_config": {"vendor_id": "1234"},
            "msix_config": {"is_supported": False, "num_vectors": 0},
        }

        with patch.object(generator.renderer, "render_template") as mock_render:
            mock_render.return_value = "base module"

            result = generator.generate_pcileech_modules(context_no_msix)

            # Should not generate MSI-X specific modules
            msix_modules = [
                "msix_capability_registers",
                "msix_implementation",
                "msix_table",
            ]
            for module in msix_modules:
                assert module not in result

    def test_advanced_modules_with_behavior_profile(self, generator):
        """Test advanced module generation with behavior profile."""
        template_context = {"device_config": {"enable_advanced_features": True}}

        behavior_profile = Mock()
        behavior_profile.variance_metadata = Mock()
        behavior_profile.register_accesses = [
            Mock(register="TEST_REG", offset=0x100, operation="read"),
            Mock(register="TEST_REG", offset=0x100, operation="write"),
            Mock(register="CTRL_REG", offset=0x104, operation="read"),
        ]

        with patch.object(
            generator, "generate_advanced_systemverilog"
        ) as mock_advanced:
            mock_advanced.return_value = "advanced systemverilog"

            result = generator._generate_pcileech_advanced_modules(
                template_context, behavior_profile
            )

            assert "pcileech_advanced_controller" in result
            mock_advanced.assert_called_once()

    def test_register_extraction_from_behavior_profile(self, generator):
        """Test register extraction from behavior profile."""
        behavior_profile = Mock()
        behavior_profile.register_accesses = [
            Mock(register="REG_A", offset=0x00, operation="read"),
            Mock(register="REG_A", offset=0x00, operation="write"),
            Mock(register="REG_B", offset=0x04, operation="read"),
            Mock(register="REG_C", offset=0x08, operation="write"),
        ]

        result = generator._extract_pcileech_registers(behavior_profile)

        assert len(result) == 3  # 3 unique registers

        # Check REG_A (read/write)
        reg_a = next(r for r in result if r["name"] == "REG_A")
        assert reg_a["access_type"] == "rw"
        assert reg_a["read_count"] == 1
        assert reg_a["write_count"] == 1

        # Check REG_B (read only)
        reg_b = next(r for r in result if r["name"] == "REG_B")
        assert reg_b["access_type"] == "ro"

        # Check REG_C (write only)
        reg_c = next(r for r in result if r["name"] == "REG_C")
        assert reg_c["access_type"] == "wo"

    def test_default_register_fallback(self, generator):
        """Test fallback to default registers when none found."""
        behavior_profile = Mock()
        behavior_profile.register_accesses = []  # No register accesses

        result = generator._extract_pcileech_registers(behavior_profile)

        # Should return default PCILeech registers
        assert len(result) == 6

        reg_names = [r["name"] for r in result]
        expected_names = [
            "PCILEECH_CTRL",
            "PCILEECH_STATUS",
            "PCILEECH_ADDR_LO",
            "PCILEECH_ADDR_HI",
            "PCILEECH_LENGTH",
            "PCILEECH_DATA",
        ]

        for name in expected_names:
            assert name in reg_names


class TestTemplateRenderingRobustness:
    """Test template rendering robustness and error handling."""

    @pytest.fixture
    def generator(self):
        return AdvancedSVGenerator()

    def test_template_error_propagation_integrity(self, generator):
        """Test that template errors are properly propagated without modification."""
        context = {"device_config": {"vendor_id": "1234"}}

        original_error = TemplateRenderError("Original template error message")

        with patch.object(
            generator.renderer, "render_template", side_effect=original_error
        ):
            with pytest.raises(TemplateRenderError) as exc_info:
                generator.generate_pcileech_modules(context)

            # Error should be propagated exactly
            assert str(exc_info.value) == "Original template error message"

    def test_missing_template_handling(self, generator):
        """Test handling of missing templates."""
        context = {"device_config": {"vendor_id": "1234"}}

        with patch.object(generator.renderer, "render_template") as mock_render:
            mock_render.side_effect = TemplateRenderError(
                "Template not found: missing.j2"
            )

            with pytest.raises(TemplateRenderError, match="Template not found"):
                generator.generate_pcileech_modules(context)

    def test_integration_code_generation(self, generator):
        """Test PCILeech integration code generation."""
        template_context = {
            "device_config": {"vendor_id": "1234", "device_id": "5678"},
            "build_system_version": "0.7.5",
        }

        with patch.object(generator.renderer, "render_template") as mock_render:
            mock_render.return_value = "# PCILeech integration code\npass"

            result = generator.generate_pcileech_integration_code(template_context)

            assert "PCILeech integration code" in result

            # Check context enhancement
            call_args = mock_render.call_args_list[0]
            context = call_args[0][1]
            assert "pcileech_modules" in context
            assert "integration_type" in context
            assert context["integration_type"] == "pcileech"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
