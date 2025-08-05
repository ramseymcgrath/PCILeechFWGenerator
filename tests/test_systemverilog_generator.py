#!/usr/bin/env python3
"""
Unit tests for the SystemVerilog Generator.

Tests the functionality of the SystemVerilog generator including proper templating system
integration, error handling, and template rendering without fallbacks.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from src.templating.systemverilog_generator import (
    AdvancedSVGenerator,
    DeviceSpecificLogic,
    PCILeechOutput,
)
from src.templating.template_renderer import TemplateRenderError
from src.templating.advanced_sv_features import (
    PowerManagementConfig,
    ErrorHandlingConfig,
    PerformanceConfig,
)
from src.device_clone.device_config import DeviceType, DeviceClass
from src.device_clone.manufacturing_variance import VarianceModel


class TestDeviceSpecificLogic:
    """Test the DeviceSpecificLogic configuration class."""

    def test_default_initialization(self):
        """Test default initialization of DeviceSpecificLogic."""
        config = DeviceSpecificLogic()

        assert config.device_type == DeviceType.GENERIC
        assert config.device_class == DeviceClass.CONSUMER
        assert config.max_payload_size == 256
        assert config.max_read_request_size == 512
        assert config.msi_vectors == 1
        assert config.msix_vectors == 0
        assert config.enable_dma is False
        assert config.enable_interrupt_coalescing is False
        assert config.enable_virtualization is False
        assert config.enable_sr_iov is False
        assert config.base_frequency_mhz == 100.0
        assert config.memory_frequency_mhz == 200.0

    def test_custom_initialization(self):
        """Test custom initialization of DeviceSpecificLogic."""
        config = DeviceSpecificLogic(
            device_type=DeviceType.NETWORK,
            device_class=DeviceClass.ENTERPRISE,
            max_payload_size=512,
            enable_dma=True,
            base_frequency_mhz=250.0,
        )

        assert config.device_type == DeviceType.NETWORK
        assert config.device_class == DeviceClass.ENTERPRISE
        assert config.max_payload_size == 512
        assert config.enable_dma is True
        assert config.base_frequency_mhz == 250.0


class TestPCILeechOutput:
    """Test the PCILeechOutput configuration class."""

    def test_default_initialization(self):
        """Test default initialization of PCILeechOutput."""
        output = PCILeechOutput()

        assert output.src_dir == "src"
        assert output.ip_dir == "ip"
        assert output.use_pcileech_structure is True
        assert output.generate_explicit_file_lists is True
        assert output.systemverilog_files == []
        assert output.ip_core_files == []
        assert output.coefficient_files == []
        assert output.constraint_files == []

    def test_custom_file_lists(self):
        """Test initialization with custom file lists."""
        sv_files = ["test1.sv", "test2.sv"]
        ip_files = ["ip1.xci", "ip2.xci"]

        output = PCILeechOutput(
            systemverilog_files=sv_files,
            ip_core_files=ip_files,
        )

        assert output.systemverilog_files == sv_files
        assert output.ip_core_files == ip_files
        assert output.coefficient_files == []  # Still default
        assert output.constraint_files == []  # Still default


class TestAdvancedSVGenerator:
    """Test the AdvancedSVGenerator class."""

    @pytest.fixture
    def mock_template_renderer(self):
        """Mock template renderer for testing."""
        with patch("src.templating.systemverilog_generator.TemplateRenderer") as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def sample_device_config(self):
        """Sample device configuration for testing."""
        return DeviceSpecificLogic(
            device_type=DeviceType.NETWORK,
            device_class=DeviceClass.CONSUMER,
            enable_dma=True,
            base_frequency_mhz=250.0,
        )

    @pytest.fixture
    def sample_power_config(self):
        """Sample power management configuration."""
        return PowerManagementConfig()

    @pytest.fixture
    def sample_error_config(self):
        """Sample error handling configuration."""
        return ErrorHandlingConfig()

    @pytest.fixture
    def sample_perf_config(self):
        """Sample performance configuration."""
        return PerformanceConfig()

    def test_initialization_with_defaults(self, mock_template_renderer):
        """Test AdvancedSVGenerator initialization with default configs."""
        generator = AdvancedSVGenerator()

        assert generator.power_config is not None
        assert generator.error_config is not None
        assert generator.perf_config is not None
        assert generator.device_config is not None
        assert generator.use_pcileech_primary is True
        assert generator.renderer is not None
        assert generator.logger is not None

    def test_initialization_with_custom_configs(
        self,
        mock_template_renderer,
        sample_device_config,
        sample_power_config,
        sample_error_config,
        sample_perf_config,
    ):
        """Test AdvancedSVGenerator initialization with custom configs."""
        generator = AdvancedSVGenerator(
            power_config=sample_power_config,
            error_config=sample_error_config,
            perf_config=sample_perf_config,
            device_config=sample_device_config,
            use_pcileech_primary=False,
        )

        assert generator.power_config == sample_power_config
        assert generator.error_config == sample_error_config
        assert generator.perf_config == sample_perf_config
        assert generator.device_config == sample_device_config
        assert generator.use_pcileech_primary is False

    def test_template_renderer_initialization(self):
        """Test that template renderer is properly initialized."""
        with patch(
            "src.templating.systemverilog_generator.TemplateRenderer"
        ) as mock_renderer_class:
            mock_instance = Mock()
            mock_renderer_class.return_value = mock_instance

            custom_template_dir = Path("/custom/templates")
            generator = AdvancedSVGenerator(template_dir=custom_template_dir)

            # Verify TemplateRenderer was called with custom directory
            mock_renderer_class.assert_called_once_with(custom_template_dir)

    def test_generate_device_specific_ports_success(
        self, mock_template_renderer, sample_device_config
    ):
        """Test successful generation of device-specific ports."""
        expected_output = "// Device-specific port declarations\nlogic test_signal;"
        mock_template_renderer.render_template.return_value = expected_output

        generator = AdvancedSVGenerator(device_config=sample_device_config)
        result = generator.generate_device_specific_ports()

        assert result == expected_output
        mock_template_renderer.render_template.assert_called_once_with(
            "systemverilog/components/device_specific_ports.sv.j2",
            {"device_config": sample_device_config},
        )

    def test_generate_device_specific_ports_template_error(
        self, mock_template_renderer, sample_device_config
    ):
        """Test that template errors are properly raised for device-specific ports."""
        mock_template_renderer.render_template.side_effect = TemplateRenderError(
            "Template not found"
        )

        generator = AdvancedSVGenerator(device_config=sample_device_config)

        with pytest.raises(TemplateRenderError, match="Template not found"):
            generator.generate_device_specific_ports()

    def test_generate_systemverilog_modules_pcileech_primary(
        self, mock_template_renderer
    ):
        """Test SystemVerilog module generation with PCILeech as primary."""
        generator = AdvancedSVGenerator(use_pcileech_primary=True)
        template_context = {"device_config": {}}

        # Mock the PCILeech module generation
        expected_modules = {"test_module": "module test_module();"}
        with patch.object(
            generator, "generate_pcileech_modules", return_value=expected_modules
        ):
            result = generator.generate_systemverilog_modules(template_context)

        assert result == expected_modules

    def test_generate_systemverilog_modules_legacy_path(self, mock_template_renderer):
        """Test SystemVerilog module generation with legacy path."""
        generator = AdvancedSVGenerator(use_pcileech_primary=False)
        template_context = {"device_config": {}}

        # Mock the legacy module generation
        expected_modules = {"legacy_module": "module legacy_module();"}
        with patch.object(
            generator, "_generate_legacy_modules", return_value=expected_modules
        ):
            result = generator.generate_systemverilog_modules(template_context)

        assert result == expected_modules

    def test_generate_legacy_modules_basic(self, mock_template_renderer):
        """Test legacy module generation."""
        # Setup mock template renderer
        mock_template_renderer.render_template.return_value = "module test();"

        generator = AdvancedSVGenerator()
        template_context = {"registers": []}

        result = generator._generate_legacy_modules(template_context)

        # Should generate multiple modules
        assert len(result) > 0
        # Verify template was called for each module
        assert mock_template_renderer.render_template.call_count > 0

    def test_generate_advanced_systemverilog_success(self, mock_template_renderer):
        """Test successful generation of advanced SystemVerilog."""
        # Mock the template renderer
        mock_template_renderer.render_template.side_effect = [
            "module advanced_controller();",  # Main module
            "module clock_crossing();",  # Clock crossing module
        ]

        # Mock the header generation
        with patch(
            "src.templating.systemverilog_generator.generate_sv_header_comment",
            return_value="// Header",
        ):
            generator = AdvancedSVGenerator()

            # Mock the device specific ports generation
            with patch.object(
                generator, "generate_device_specific_ports", return_value="// Ports"
            ):
                result = generator.generate_advanced_systemverilog([])

        assert "module advanced_controller();" in result
        assert "module clock_crossing();" in result

    def test_generate_advanced_systemverilog_template_error(
        self, mock_template_renderer
    ):
        """Test that template errors are properly raised in advanced SystemVerilog generation."""
        mock_template_renderer.render_template.side_effect = TemplateRenderError(
            "Missing template"
        )

        with patch(
            "src.templating.systemverilog_generator.generate_sv_header_comment",
            return_value="// Header",
        ):
            generator = AdvancedSVGenerator()

            with patch.object(
                generator, "generate_device_specific_ports", return_value="// Ports"
            ):
                with pytest.raises(TemplateRenderError, match="Missing template"):
                    generator.generate_advanced_systemverilog([])

    def test_generate_enhanced_build_integration_success(self, mock_template_renderer):
        """Test successful generation of build integration code."""
        expected_code = "# Build integration code\nprint('Hello')"
        mock_template_renderer.render_template.return_value = expected_code

        generator = AdvancedSVGenerator()
        result = generator.generate_enhanced_build_integration()

        assert result == expected_code
        mock_template_renderer.render_template.assert_called_once_with(
            "python/build_integration.py.j2", {}
        )

    def test_generate_enhanced_build_integration_template_error(
        self, mock_template_renderer
    ):
        """Test that template errors are properly raised in build integration generation."""
        mock_template_renderer.render_template.side_effect = TemplateRenderError(
            "Template error"
        )

        generator = AdvancedSVGenerator()

        with pytest.raises(TemplateRenderError, match="Template error"):
            generator.generate_enhanced_build_integration()

    def test_generate_pcileech_modules_basic(self, mock_template_renderer):
        """Test basic PCILeech module generation."""

        # Setup mock to return different content for different templates
        def mock_render(template_name, context):
            if "pcileech_tlps128_bar_controller" in template_name:
                return "module pcileech_tlps128_bar_controller();"
            elif "pcileech_fifo" in template_name:
                return "module pcileech_fifo();"
            elif "top_level_wrapper" in template_name:
                return "module top_level_wrapper();"
            elif "pcileech_cfgspace.coe" in template_name:
                return "memory_initialization_radix=16;"
            else:
                return f"// Template: {template_name}"

        mock_template_renderer.render_template.side_effect = mock_render

        # Mock the header generation
        with patch(
            "src.templating.systemverilog_generator.generate_sv_header_comment",
            return_value="// Header",
        ):
            generator = AdvancedSVGenerator()
            template_context = {"device_config": {}}

            result = generator.generate_pcileech_modules(template_context)

        # Should generate core PCILeech modules
        assert "pcileech_tlps128_bar_controller" in result
        assert "pcileech_fifo" in result
        assert "top_level_wrapper" in result
        assert "pcileech_cfgspace.coe" in result

    def test_generate_pcileech_modules_with_msix(self, mock_template_renderer):
        """Test PCILeech module generation with MSI-X support."""

        def mock_render(template_name, context):
            return f"// Generated: {template_name}"

        mock_template_renderer.render_template.side_effect = mock_render

        with patch(
            "src.templating.systemverilog_generator.generate_sv_header_comment",
            return_value="// Header",
        ):
            generator = AdvancedSVGenerator()

            # Mock MSI-X initialization methods
            with patch.object(
                generator, "_generate_msix_pba_init", return_value="PBA_INIT_DATA"
            ):
                with patch.object(
                    generator,
                    "_generate_msix_table_init",
                    return_value="TABLE_INIT_DATA",
                ):
                    template_context = {
                        "device_config": {},
                        "msix_config": {"is_supported": True, "num_vectors": 4},
                    }

                    result = generator.generate_pcileech_modules(template_context)

        # Should include MSI-X modules
        assert "msix_capability_registers" in result
        assert "msix_implementation" in result
        assert "msix_table" in result
        assert "msix_pba_init.hex" in result
        assert "msix_table_init.hex" in result

    def test_generate_pcileech_modules_template_error(self, mock_template_renderer):
        """Test that template errors are properly raised in PCILeech module generation."""
        mock_template_renderer.render_template.side_effect = TemplateRenderError(
            "PCILeech template error"
        )

        with patch(
            "src.templating.systemverilog_generator.generate_sv_header_comment",
            return_value="// Header",
        ):
            generator = AdvancedSVGenerator()
            template_context = {"device_config": {}}

            with pytest.raises(TemplateRenderError, match="PCILeech template error"):
                generator.generate_pcileech_modules(template_context)

    def test_extract_pcileech_registers_with_behavior_profile(self):
        """Test register extraction from behavior profile."""
        # Mock behavior profile with register accesses
        mock_access1 = Mock()
        mock_access1.register = "TEST_REG1"
        mock_access1.offset = 0x10
        mock_access1.operation = "read"

        mock_access2 = Mock()
        mock_access2.register = "TEST_REG1"
        mock_access2.offset = 0x10
        mock_access2.operation = "write"

        mock_access3 = Mock()
        mock_access3.register = "TEST_REG2"
        mock_access3.offset = 0x20
        mock_access3.operation = "read"

        mock_behavior_profile = Mock()
        mock_behavior_profile.register_accesses = [
            mock_access1,
            mock_access2,
            mock_access3,
        ]

        generator = AdvancedSVGenerator()
        registers = generator._extract_pcileech_registers(mock_behavior_profile)

        assert len(registers) == 2

        # Find TEST_REG1 (should be read/write)
        reg1 = next(r for r in registers if r["name"] == "TEST_REG1")
        assert reg1["offset"] == 0x10
        assert reg1["access_type"] == "rw"
        assert reg1["access_count"] == 2

        # Find TEST_REG2 (should be read-only)
        reg2 = next(r for r in registers if r["name"] == "TEST_REG2")
        assert reg2["offset"] == 0x20
        assert reg2["access_type"] == "ro"
        assert reg2["access_count"] == 1

    def test_extract_pcileech_registers_no_behavior_profile(self):
        """Test register extraction with no behavior profile (should return defaults)."""
        mock_behavior_profile = Mock()
        # Mock hasattr to return False for register_accesses
        with patch("builtins.hasattr", return_value=False):
            generator = AdvancedSVGenerator()
            registers = generator._extract_pcileech_registers(mock_behavior_profile)

        # Should return default PCILeech registers
        assert len(registers) == 6
        reg_names = [r["name"] for r in registers]
        assert "PCILEECH_CTRL" in reg_names
        assert "PCILEECH_STATUS" in reg_names
        assert "PCILEECH_ADDR_LO" in reg_names
        assert "PCILEECH_ADDR_HI" in reg_names
        assert "PCILEECH_LENGTH" in reg_names
        assert "PCILEECH_DATA" in reg_names

    def test_generate_msix_pba_init(self):
        """Test MSI-X PBA initialization generation."""
        generator = AdvancedSVGenerator()
        template_context = {"msix_config": {"num_vectors": 8}}

        result = generator._generate_msix_pba_init(template_context)

        # 8 vectors = 1 DWORD (8 bits, each vector is 1 bit)
        lines = result.strip().split("\n")
        assert len(lines) == 1
        assert lines[0] == "00000000"

    def test_generate_msix_pba_init_large_vector_count(self):
        """Test MSI-X PBA initialization with large vector count."""
        generator = AdvancedSVGenerator()
        template_context = {
            "msix_config": {"num_vectors": 64}  # Should require 2 DWORDs
        }

        result = generator._generate_msix_pba_init(template_context)

        lines = result.strip().split("\n")
        assert len(lines) == 2
        assert all(line == "00000000" for line in lines)

    def test_generate_msix_table_init_default(self):
        """Test MSI-X table initialization with default values."""
        generator = AdvancedSVGenerator()
        template_context = {"msix_config": {"num_vectors": 2}}

        # Mock the actual MSI-X table reading to return None (use defaults)
        with patch.object(generator, "_read_actual_msix_table", return_value=None):
            result = generator._generate_msix_table_init(template_context)

        lines = result.strip().split("\n")
        # 2 vectors * 4 DWORDs per entry = 8 lines
        assert len(lines) == 8

        # Check vector 0 entry
        assert lines[0] == "00000000"  # Message Address Low
        assert lines[1] == "00000000"  # Message Address High
        assert lines[2] == "00000000"  # Message Data (vector 0)
        assert lines[3] == "00000001"  # Vector Control (masked)

        # Check vector 1 entry
        assert lines[4] == "00000000"  # Message Address Low
        assert lines[5] == "00000000"  # Message Address High
        assert lines[6] == "00000001"  # Message Data (vector 1)
        assert lines[7] == "00000001"  # Vector Control (masked)

    def test_generate_msix_table_init_with_actual_data(self):
        """Test MSI-X table initialization with actual hardware data."""
        generator = AdvancedSVGenerator()
        template_context = {"msix_config": {"num_vectors": 1}}

        # Mock actual MSI-X table data
        actual_data = [0x12345678, 0x87654321, 0xABCDEF00, 0x00000000]
        with patch.object(
            generator, "_read_actual_msix_table", return_value=actual_data
        ):
            result = generator._generate_msix_table_init(template_context)

        lines = result.strip().split("\n")
        assert len(lines) == 4
        assert lines[0] == "12345678"
        assert lines[1] == "87654321"
        assert lines[2] == "ABCDEF00"
        assert lines[3] == "00000000"

    def test_generate_pcileech_integration_code_success(self, mock_template_renderer):
        """Test successful generation of PCILeech integration code."""
        expected_code = "# PCILeech integration\nprint('Integration successful')"
        mock_template_renderer.render_template.return_value = expected_code

        generator = AdvancedSVGenerator()
        template_context = {"device_config": {}}

        result = generator.generate_pcileech_integration_code(template_context)

        assert result == expected_code

        # Verify the template was called with enhanced context
        call_args = mock_template_renderer.render_template.call_args
        assert call_args[0][0] == "python/pcileech_build_integration.py.j2"
        context = call_args[0][1]
        assert "pcileech_modules" in context
        assert "integration_type" in context
        assert context["integration_type"] == "pcileech"

    def test_generate_pcileech_integration_code_template_error(
        self, mock_template_renderer
    ):
        """Test that template errors are properly raised in PCILeech integration code generation."""
        mock_template_renderer.render_template.side_effect = TemplateRenderError(
            "Integration template error"
        )

        generator = AdvancedSVGenerator()
        template_context = {"device_config": {}}

        with pytest.raises(TemplateRenderError, match="Integration template error"):
            generator.generate_pcileech_integration_code(template_context)


class TestErrorHandling:
    """Test that the generator properly handles errors instead of providing fallbacks."""

    @pytest.fixture
    def mock_template_renderer(self):
        """Mock template renderer for error testing."""
        with patch("src.templating.systemverilog_generator.TemplateRenderer") as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_no_fallback_on_template_error(self, mock_template_renderer):
        """Test that template errors are raised instead of falling back to defaults."""
        # Setup mock to raise TemplateRenderError
        mock_template_renderer.render_template.side_effect = TemplateRenderError(
            "Template missing"
        )

        generator = AdvancedSVGenerator()

        # All these methods should raise TemplateRenderError, not return fallback values
        with pytest.raises(TemplateRenderError):
            generator.generate_device_specific_ports()

        with pytest.raises(TemplateRenderError):
            generator.generate_enhanced_build_integration()

        template_context = {"device_config": {}}
        with pytest.raises(TemplateRenderError):
            generator.generate_pcileech_modules(template_context)

        with pytest.raises(TemplateRenderError):
            generator.generate_pcileech_integration_code(template_context)

    def test_template_renderer_properly_initialized(self):
        """Test that TemplateRenderer is properly initialized and used."""
        with patch(
            "src.templating.systemverilog_generator.TemplateRenderer"
        ) as mock_renderer_class:
            mock_instance = Mock()
            mock_renderer_class.return_value = mock_instance

            custom_template_dir = Path("/custom/templates")
            generator = AdvancedSVGenerator(template_dir=custom_template_dir)

            # Verify TemplateRenderer was initialized with correct directory
            mock_renderer_class.assert_called_once_with(custom_template_dir)

            # Verify the generator uses the renderer instance
            assert generator.renderer == mock_instance

    def test_error_logging_and_reraising(self, mock_template_renderer):
        """Test that errors are logged but still re-raised."""
        mock_template_renderer.render_template.side_effect = TemplateRenderError(
            "Test error"
        )

        generator = AdvancedSVGenerator()

        # Capture log messages
        with patch.object(generator.logger, "error") as mock_log_error:
            with pytest.raises(TemplateRenderError, match="Test error"):
                generator.generate_device_specific_ports()

            # Verify error was logged
            mock_log_error.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
