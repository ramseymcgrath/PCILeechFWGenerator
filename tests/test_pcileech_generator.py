#!/usr/bin/env python3
"""
Comprehensive unit tests for PCILeech Generator module.

This test suite covers the complete PCILeech firmware generation pipeline,
including behavior profiling, configuration space analysis, MSI-X processing,
template context building, SystemVerilog generation, and security-critical
components like writemask generation.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, PropertyMock, call, mock_open, patch

import pytest

from src.device_clone.behavior_profiler import BehaviorProfile
from src.device_clone.pcileech_generator import (
    PCILeechGenerationConfig,
    PCILeechGenerator,
)
from src.exceptions import PCILeechGenerationError
from src.templating import TemplateRenderError


# Test fixtures and mock data
@pytest.fixture
def mock_config():
    """Create a test configuration for PCILeech generation."""
    return PCILeechGenerationConfig(
        device_bdf="0000:01:00.0",
        device_profile="test_device",
        enable_behavior_profiling=True,
        behavior_capture_duration=10.0,
        enable_manufacturing_variance=True,
        enable_advanced_features=True,
        template_dir=Path("/test/templates"),
        output_dir=Path("/test/output"),
        pcileech_command_timeout=1000,
        pcileech_buffer_size=4096,
        enable_dma_operations=True,
        enable_interrupt_coalescing=False,
        strict_validation=True,
        fail_on_missing_data=True,
        fallback_mode="none",
        allowed_fallbacks=[],
        denied_fallbacks=[],
    )


@pytest.fixture
def mock_behavior_profile():
    """Create a mock behavior profile."""
    profile = Mock(spec=BehaviorProfile)
    profile.total_accesses = 100
    profile.timing_patterns = [
        {"pattern": "read_burst", "frequency": 0.3},
        {"pattern": "write_sequence", "frequency": 0.2},
    ]
    profile.register_accesses = [
        {"register": "STATUS", "offset": 0x00, "operation": "read"},
        {"register": "CONTROL", "offset": 0x04, "operation": "write"},
    ]
    profile.pattern_analysis = {
        "dominant_pattern": "read_burst",
        "access_frequency": 10.5,
    }
    return profile


@pytest.fixture
def mock_config_space_data():
    """Create mock configuration space data."""
    return {
        "raw_config_space": b"\x86\x80\x00\x10" + b"\x00" * 252,  # Intel vendor ID
        "config_space_hex": "86801000" + "00" * 252,
        "device_info": {
            "vendor_id": 0x8086,
            "device_id": 0x1000,
            "class_code": 0x020000,
            "revision_id": 0x01,
            "bars": [
                {"index": 0, "address": 0xF0000000, "size": 0x10000, "type": "mem"},
                {"index": 1, "address": 0xF0010000, "size": 0x1000, "type": "mem"},
            ],
        },
        "vendor_id": "8086",
        "device_id": "1000",
        "class_code": "020000",
        "revision_id": "01",
        "bars": [
            {"index": 0, "address": 0xF0000000, "size": 0x10000, "type": "mem"},
            {"index": 1, "address": 0xF0010000, "size": 0x1000, "type": "mem"},
        ],
        "config_space_size": 256,
    }


@pytest.fixture
def mock_msix_data():
    """Create mock MSI-X capability data."""
    return {
        "capability_info": {
            "table_size": 16,
            "table_bir": 0,
            "table_offset": 0x2000,
            "pba_bir": 0,
            "pba_offset": 0x3000,
            "enabled": True,
            "function_mask": False,
        },
        "table_size": 16,
        "table_bir": 0,
        "table_offset": 0x2000,
        "pba_bir": 0,
        "pba_offset": 0x3000,
        "enabled": True,
        "function_mask": False,
        "validation_errors": [],
        "is_valid": True,
    }


@pytest.fixture
def mock_template_context(mock_config_space_data, mock_msix_data):
    """Create a comprehensive mock template context."""
    return {
        "device_config": {
            "vendor_id": "8086",
            "device_id": "1000",
            "class_code": "020000",
            "behavior_profile": None,
        },
        "config_space": {
            "raw_data": mock_config_space_data["config_space_hex"],
            "vendor_id": "8086",
            "device_id": "1000",
        },
        "config_space_data": mock_config_space_data,
        "msix_config": mock_msix_data,
        "bar_config": {
            "bars": mock_config_space_data["bars"],
            "total_bars": 2,
        },
        "timing_config": {
            "clock_frequency": 250000000,
            "timeout_cycles": 1000,
        },
        "pcileech_config": {
            "command_timeout": 1000,
            "buffer_size": 4096,
        },
        "msi_config": {},
        "interrupt_strategy": "msix",
        "interrupt_vectors": 16,
    }


@pytest.fixture
def mock_systemverilog_modules():
    """Create mock SystemVerilog modules."""
    return {
        "pcileech_tlps128_bar_controller": "module pcileech_tlps128_bar_controller(...);",
        "pcileech_cfgspace.coe": "memory_initialization_radix=16;\n00000000",
        "advanced_controller": "module advanced_controller(...);",
    }


@pytest.fixture
def mock_firmware_components():
    """Create mock firmware components."""
    return {
        "build_integration": "# Build integration code",
        "constraint_files": {
            "timing_constraints": "# Timing constraints",
            "pin_constraints": "# Pin constraints",
        },
        "tcl_scripts": {
            "build_script": "# TCL build script",
            "synthesis_script": "# TCL synthesis script",
        },
        "config_space_hex": "# Config space hex file",
        "writemask_coe": "memory_initialization_radix=16;\nFFFFFFFF",
    }


class TestPCILeechGeneratorInitialization:
    """Test PCILeechGenerator initialization."""

    def test_successful_initialization(self, mock_config):
        """Test successful generator initialization."""
        with patch(
            "src.device_clone.pcileech_generator.BehaviorProfiler"
        ) as mock_profiler:
            with patch(
                "src.device_clone.pcileech_generator.ConfigSpaceManager"
            ) as mock_manager:
                with patch(
                    "src.device_clone.pcileech_generator.TemplateRenderer"
                ) as mock_renderer:
                    with patch(
                        "src.device_clone.pcileech_generator.AdvancedSVGenerator"
                    ) as mock_sv_gen:
                        generator = PCILeechGenerator(mock_config)

                        assert generator.config == mock_config
                        assert generator.behavior_profiler is not None
                        assert generator.config_space_manager is not None
                        assert generator.template_renderer is not None
                        assert generator.sv_generator is not None
                        assert generator.context_builder is None  # Created later

                        # Verify component initialization
                        mock_profiler.assert_called_once_with(
                            bdf="0000:01:00.0",
                            debug=True,
                            enable_variance=True,
                            enable_ftrace=True,
                        )

    def test_initialization_without_behavior_profiling(self, mock_config):
        """Test initialization when behavior profiling is disabled."""
        mock_config.enable_behavior_profiling = False

        with patch("src.device_clone.pcileech_generator.ConfigSpaceManager"):
            with patch("src.device_clone.pcileech_generator.TemplateRenderer"):
                with patch("src.device_clone.pcileech_generator.AdvancedSVGenerator"):
                    generator = PCILeechGenerator(mock_config)
                    assert generator.behavior_profiler is None

    def test_initialization_failure(self, mock_config):
        """Test initialization failure handling."""
        with patch(
            "src.device_clone.pcileech_generator.BehaviorProfiler"
        ) as mock_profiler:
            mock_profiler.side_effect = Exception("Initialization failed")

            with pytest.raises(PCILeechGenerationError) as exc_info:
                PCILeechGenerator(mock_config)

            assert "Failed to initialize PCILeech generator" in str(exc_info.value)


class TestPCILeechGeneratorMainPipeline:
    """Test the main firmware generation pipeline."""

    @patch("src.device_clone.pcileech_generator.VFIOBinder")
    def test_successful_firmware_generation(
        self,
        mock_vfio_binder,
        mock_config,
        mock_behavior_profile,
        mock_config_space_data,
        mock_msix_data,
        mock_template_context,
        mock_systemverilog_modules,
        mock_firmware_components,
    ):
        """Test successful end-to-end firmware generation."""
        # Setup VFIO context manager
        mock_vfio_context = MagicMock()
        mock_vfio_context.__enter__.return_value = "/dev/vfio/1"
        mock_vfio_context.__exit__.return_value = None
        mock_vfio_binder.return_value = mock_vfio_context

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            # Mock internal methods
            generator._preload_msix_data_early = Mock(return_value=None)
            generator._capture_device_behavior = Mock(
                return_value=mock_behavior_profile
            )
            generator._analyze_configuration_space_with_vfio = Mock(
                return_value=mock_config_space_data
            )
            generator._process_msix_capabilities = Mock(return_value=mock_msix_data)
            generator._build_template_context = Mock(return_value=mock_template_context)
            generator._generate_systemverilog_modules = Mock(
                return_value=mock_systemverilog_modules
            )
            generator._generate_firmware_components = Mock(
                return_value=mock_firmware_components
            )
            generator._validate_generated_firmware = Mock()
            generator._build_generation_metadata = Mock(
                return_value={"version": "1.0.0"}
            )
            generator._get_timestamp = Mock(return_value="2024-01-01T00:00:00")

            # Execute generation
            result = generator.generate_pcileech_firmware()

            # Verify result structure
            assert result["device_bdf"] == "0000:01:00.0"
            assert result["generation_timestamp"] == "2024-01-01T00:00:00"
            assert result["behavior_profile"] == mock_behavior_profile
            assert result["config_space_data"] == mock_config_space_data
            assert result["msix_data"] == mock_msix_data
            assert result["template_context"] == mock_template_context
            assert result["systemverilog_modules"] == mock_systemverilog_modules
            assert result["firmware_components"] == mock_firmware_components
            assert result["generation_metadata"] == {"version": "1.0.0"}

            # Verify method calls
            generator._preload_msix_data_early.assert_called_once()
            generator._capture_device_behavior.assert_called_once()
            generator._analyze_configuration_space_with_vfio.assert_called_once()
            generator._process_msix_capabilities.assert_called_once_with(
                mock_config_space_data
            )
            generator._build_template_context.assert_called_once()
            generator._generate_systemverilog_modules.assert_called_once_with(
                mock_template_context
            )
            generator._generate_firmware_components.assert_called_once_with(
                mock_template_context
            )
            generator._validate_generated_firmware.assert_called_once()

    @patch("src.device_clone.pcileech_generator.VFIOBinder")
    def test_firmware_generation_with_msi_fallback(
        self, mock_vfio_binder, mock_config, mock_config_space_data
    ):
        """Test firmware generation with MSI fallback when MSI-X is not available."""
        # Setup VFIO context
        mock_vfio_context = MagicMock()
        mock_vfio_context.__enter__.return_value = "/dev/vfio/1"
        mock_vfio_binder.return_value = mock_vfio_context

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            # Mock methods to simulate MSI-X not available
            generator._preload_msix_data_early = Mock(return_value=None)
            generator._capture_device_behavior = Mock(return_value=None)
            generator._analyze_configuration_space_with_vfio = Mock(
                return_value=mock_config_space_data
            )
            generator._process_msix_capabilities = Mock(return_value=None)  # No MSI-X

            # Mock find_cap to return MSI capability
            with patch("src.device_clone.pcileech_generator.find_cap") as mock_find_cap:
                mock_find_cap.return_value = 0x50  # MSI capability offset

                # Mock remaining methods
                mock_template_context = {
                    "interrupt_strategy": "msi",
                    "interrupt_vectors": 1,
                }
                generator._build_template_context = Mock(
                    return_value=mock_template_context
                )
                generator._generate_systemverilog_modules = Mock(return_value={})
                generator._generate_firmware_components = Mock(return_value={})
                generator._validate_generated_firmware = Mock()
                generator._build_generation_metadata = Mock(return_value={})
                generator._get_timestamp = Mock(return_value="2024-01-01T00:00:00")

                result = generator.generate_pcileech_firmware()

                # Verify MSI fallback was used
                generator._build_template_context.assert_called_once()
                call_args = generator._build_template_context.call_args
                assert call_args[0][3] == "msi"  # interrupt_strategy
                assert call_args[0][4] == 1  # interrupt_vectors

    def test_firmware_generation_failure(self, mock_config):
        """Test firmware generation failure handling."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator._preload_msix_data_early = Mock(
                side_effect=Exception("Test error")
            )

            with pytest.raises(PCILeechGenerationError) as exc_info:
                generator.generate_pcileech_firmware()

            assert "Firmware generation failed" in str(exc_info.value)


class TestBehaviorCapture:
    """Test device behavior capture functionality."""

    def test_successful_behavior_capture(self, mock_config, mock_behavior_profile):
        """Test successful behavior profile capture."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.behavior_profiler = Mock()
            generator.behavior_profiler.capture_behavior_profile.return_value = (
                mock_behavior_profile
            )
            generator.behavior_profiler.analyze_patterns.return_value = {
                "dominant_pattern": "read_burst"
            }

            result = generator._capture_device_behavior()

            assert result == mock_behavior_profile
            assert result.pattern_analysis == {"dominant_pattern": "read_burst"}
            generator.behavior_profiler.capture_behavior_profile.assert_called_once_with(
                duration=10.0
            )

    def test_behavior_capture_disabled(self, mock_config):
        """Test behavior capture when profiling is disabled."""
        mock_config.enable_behavior_profiling = False

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            result = generator._capture_device_behavior()
            assert result is None

    def test_behavior_capture_failure_with_fallback(self, mock_config):
        """Test behavior capture failure with fallback handling."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.behavior_profiler = Mock()
            generator.behavior_profiler.capture_behavior_profile.side_effect = (
                Exception("Capture failed")
            )
            generator.fallback_manager.confirm_fallback = Mock(return_value=True)

            result = generator._capture_device_behavior()

            assert result is None
            generator.fallback_manager.confirm_fallback.assert_called_once()

    def test_behavior_capture_failure_without_fallback(self, mock_config):
        """Test behavior capture failure without fallback."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.behavior_profiler = Mock()
            generator.behavior_profiler.capture_behavior_profile.side_effect = (
                Exception("Capture failed")
            )
            generator.fallback_manager.confirm_fallback = Mock(return_value=False)

            with pytest.raises(PCILeechGenerationError) as exc_info:
                generator._capture_device_behavior()

            assert "Device behavior profiling failed" in str(exc_info.value)


class TestConfigurationSpaceAnalysis:
    """Test configuration space analysis functionality."""

    def test_successful_config_space_analysis(
        self, mock_config, mock_config_space_data
    ):
        """Test successful configuration space analysis."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.config_space_manager.read_vfio_config_space.return_value = (
                mock_config_space_data["raw_config_space"]
            )
            generator.config_space_manager.extract_device_info.return_value = (
                mock_config_space_data["device_info"]
            )

            result = generator._analyze_configuration_space()

            assert result["vendor_id"] == "8086"
            assert result["device_id"] == "1000"
            assert result["class_code"] == "020000"
            assert len(result["bars"]) == 2

    def test_config_space_analysis_with_vfio(self, mock_config, mock_config_space_data):
        """Test configuration space analysis with active VFIO binding."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.config_space_manager._read_sysfs_config_space.return_value = (
                mock_config_space_data["raw_config_space"]
            )
            generator.config_space_manager.extract_device_info.return_value = (
                mock_config_space_data["device_info"]
            )

            result = generator._analyze_configuration_space_with_vfio()

            assert result["vendor_id"] == "8086"
            assert result["device_id"] == "1000"
            generator.config_space_manager._read_sysfs_config_space.assert_called_once()

    def test_config_space_analysis_failure(self, mock_config):
        """Test configuration space analysis failure."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.config_space_manager.read_vfio_config_space.side_effect = (
                Exception("Read failed")
            )
            generator.fallback_manager.is_fallback_allowed = Mock(return_value=False)

            with pytest.raises(PCILeechGenerationError) as exc_info:
                generator._analyze_configuration_space()

            assert "Configuration space analysis failed" in str(exc_info.value)


class TestMSIXProcessing:
    """Test MSI-X capability processing."""

    def test_successful_msix_processing(
        self, mock_config, mock_config_space_data, mock_msix_data
    ):
        """Test successful MSI-X capability processing."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch(
                "src.device_clone.pcileech_generator.parse_msix_capability"
            ) as mock_parse:
                with patch(
                    "src.device_clone.pcileech_generator.validate_msix_configuration"
                ) as mock_validate:
                    mock_parse.return_value = mock_msix_data["capability_info"]
                    mock_validate.return_value = (True, [])

                    result = generator._process_msix_capabilities(
                        mock_config_space_data
                    )

                    assert result["table_size"] == 16
                    assert result["table_bir"] == 0
                    assert result["table_offset"] == 0x2000
                    assert result["is_valid"] is True

    def test_msix_processing_no_capability(self, mock_config, mock_config_space_data):
        """Test MSI-X processing when capability is not present."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch(
                "src.device_clone.pcileech_generator.parse_msix_capability"
            ) as mock_parse:
                mock_parse.return_value = {"table_size": 0}  # No MSI-X

                result = generator._process_msix_capabilities(mock_config_space_data)
                assert result is None

    def test_msix_processing_validation_failure(
        self, mock_config, mock_config_space_data
    ):
        """Test MSI-X processing with validation failure."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch(
                "src.device_clone.pcileech_generator.parse_msix_capability"
            ) as mock_parse:
                with patch(
                    "src.device_clone.pcileech_generator.validate_msix_configuration"
                ) as mock_validate:
                    mock_parse.return_value = {
                        "table_size": 16,
                        "table_bir": 0,
                        "table_offset": 0x2000,
                    }
                    mock_validate.return_value = (False, ["Invalid table offset"])

                    result = generator._process_msix_capabilities(
                        mock_config_space_data
                    )
                    assert result is None  # Strict validation fails

    def test_msix_preload_success(self, mock_config):
        """Test successful MSI-X data preloading."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch("os.path.exists") as mock_exists:
                with patch(
                    "builtins.open",
                    mock_open(read_data=b"\x86\x80\x00\x10" + b"\x00" * 252),
                ):
                    with patch(
                        "src.device_clone.pcileech_generator.parse_msix_capability"
                    ) as mock_parse:
                        with patch(
                            "src.device_clone.pcileech_generator.validate_msix_configuration"
                        ) as mock_validate:
                            mock_exists.return_value = True
                            mock_parse.return_value = {
                                "table_size": 16,
                                "table_bir": 0,
                                "table_offset": 0x2000,
                                "pba_bir": 0,
                                "pba_offset": 0x3000,
                                "enabled": True,
                                "function_mask": False,
                            }
                            mock_validate.return_value = (True, [])

                            result = generator._preload_msix_data_early()

                            assert result is not None
                            assert result["table_size"] == 16
                            assert result["preloaded"] is True


class TestTemplateContextBuilding:
    """Test template context building."""

    def test_successful_context_building(
        self,
        mock_config,
        mock_behavior_profile,
        mock_config_space_data,
        mock_msix_data,
        mock_template_context,
    ):
        """Test successful template context building."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch(
                "src.device_clone.pcileech_generator.PCILeechContextBuilder"
            ) as mock_builder_class:
                mock_builder = Mock()
                mock_builder.build_context.return_value = mock_template_context
                mock_builder_class.return_value = mock_builder

                result = generator._build_template_context(
                    mock_behavior_profile,
                    mock_config_space_data,
                    mock_msix_data,
                    "msix",
                    16,
                )

                assert result == mock_template_context
                mock_builder.build_context.assert_called_once_with(
                    behavior_profile=mock_behavior_profile,
                    config_space_data=mock_config_space_data,
                    msix_data=mock_msix_data,
                    interrupt_strategy="msix",
                    interrupt_vectors=16,
                )

    def test_context_building_validation_failure(self, mock_config):
        """Test context building with validation failure."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch(
                "src.device_clone.pcileech_generator.PCILeechContextBuilder"
            ) as mock_builder_class:
                mock_builder = Mock()
                mock_builder.build_context.return_value = {}  # Missing required keys
                mock_builder_class.return_value = mock_builder

                with pytest.raises(PCILeechGenerationError) as exc_info:
                    generator._build_template_context(None, {}, None, "intx", 1)

                assert "Template context missing required keys" in str(exc_info.value)


class TestSystemVerilogGeneration:
    """Test SystemVerilog module generation."""

    def test_successful_sv_generation(
        self, mock_config, mock_template_context, mock_systemverilog_modules
    ):
        """Test successful SystemVerilog generation."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.sv_generator.generate_systemverilog_modules.return_value = (
                mock_systemverilog_modules
            )

            result = generator._generate_systemverilog_modules(mock_template_context)

            assert "pcileech_tlps128_bar_controller" in result
            assert "pcileech_cfgspace.coe" in result
            assert generator._cached_systemverilog_modules == mock_systemverilog_modules

    def test_sv_generation_failure(self, mock_config, mock_template_context):
        """Test SystemVerilog generation failure."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.sv_generator.generate_systemverilog_modules.side_effect = (
                TemplateRenderError("Render failed")
            )

            with pytest.raises(PCILeechGenerationError) as exc_info:
                generator._generate_systemverilog_modules(mock_template_context)

            assert "SystemVerilog generation failed" in str(exc_info.value)


class TestWritemaskGeneration:
    """Test security-critical writemask COE generation."""

    def test_successful_writemask_generation(self, mock_config, mock_template_context):
        """Test successful writemask COE generation."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator._cached_systemverilog_modules = {
                "pcileech_cfgspace.coe": "memory_initialization_radix=16;\n00000000"
            }

            with patch(
                "src.device_clone.pcileech_generator.WritemaskGenerator"
            ) as mock_writemask_gen:
                mock_writemask_instance = Mock()
                mock_writemask_gen.return_value = mock_writemask_instance

                # Mock file operations
                with patch("pathlib.Path.exists") as mock_exists:
                    with patch("pathlib.Path.mkdir") as mock_mkdir:
                        with patch("pathlib.Path.write_text") as mock_write:
                            with patch("pathlib.Path.read_text") as mock_read:
                                mock_exists.return_value = (
                                    False  # COE doesn't exist yet
                                )
                                mock_read.return_value = (
                                    "memory_initialization_radix=16;\nFFFFFFFF"
                                )

                                result = generator._generate_writemask_coe(
                                    mock_template_context
                                )

                                assert (
                                    result
                                    == "memory_initialization_radix=16;\nFFFFFFFF"
                                )
                                mock_writemask_instance.generate_writemask.assert_called_once()
                                mock_mkdir.assert_called_once_with(
                                    parents=True, exist_ok=True
                                )

    def test_writemask_generation_with_existing_coe(
        self, mock_config, mock_template_context
    ):
        """Test writemask generation when config space COE already exists."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch(
                "src.device_clone.pcileech_generator.WritemaskGenerator"
            ) as mock_writemask_gen:
                mock_writemask_instance = Mock()
                mock_writemask_gen.return_value = mock_writemask_instance

                with patch("pathlib.Path.exists") as mock_exists:
                    with patch("pathlib.Path.read_text") as mock_read:
                        mock_exists.return_value = True  # COE already exists
                        mock_read.return_value = (
                            "memory_initialization_radix=16;\nFFFFFFFF"
                        )

                        result = generator._generate_writemask_coe(
                            mock_template_context
                        )

                        assert result == "memory_initialization_radix=16;\nFFFFFFFF"
                        mock_writemask_instance.generate_writemask.assert_called_once()

    def test_writemask_generation_failure(self, mock_config, mock_template_context):
        """Test writemask generation failure handling."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch(
                "src.device_clone.pcileech_generator.WritemaskGenerator"
            ) as mock_writemask_gen:
                mock_writemask_gen.side_effect = Exception(
                    "Writemask generation failed"
                )

                result = generator._generate_writemask_coe(mock_template_context)

                assert result is None  # Returns None on failure


class TestConfigSpaceHexGeneration:
    """Test configuration space hex file generation."""

    def test_successful_hex_generation_from_raw_data(
        self, mock_config, mock_template_context
    ):
        """Test successful hex generation from raw config space data."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch(
                "src.device_clone.pcileech_generator.ConfigSpaceHexFormatter"
            ) as mock_formatter_class:
                mock_formatter = Mock()
                mock_formatter.format_config_space_to_hex.return_value = (
                    "# Config space hex\n86801000"
                )
                mock_formatter_class.return_value = mock_formatter

                result = generator._generate_config_space_hex(mock_template_context)

                assert result == "# Config space hex\n86801000"
                mock_formatter.format_config_space_to_hex.assert_called_once()

    def test_hex_generation_from_alternative_locations(self, mock_config):
        """Test hex generation when data is in alternative template context locations."""
        template_context = {
            "config_space": {"raw_data": "86801000" + "00" * 252}  # Hex string format
        }

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch(
                "src.device_clone.pcileech_generator.ConfigSpaceHexFormatter"
            ) as mock_formatter_class:
                mock_formatter = Mock()
                mock_formatter.format_config_space_to_hex.return_value = (
                    "# Config space hex\n86801000"
                )
                mock_formatter_class.return_value = mock_formatter

                result = generator._generate_config_space_hex(template_context)

                assert result == "# Config space hex\n86801000"
                # Verify bytes conversion happened
                call_args = mock_formatter.format_config_space_to_hex.call_args[0]
                assert isinstance(call_args[0], bytes)

    def test_hex_generation_missing_data(self, mock_config):
        """Test hex generation when config space data is missing."""
        template_context = {}  # No config space data

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with pytest.raises(PCILeechGenerationError) as exc_info:
                generator._generate_config_space_hex(template_context)

            assert "Config space hex generation failed" in str(exc_info.value)


class TestFirmwareComponentGeneration:
    """Test firmware component generation."""

    def test_successful_component_generation(self, mock_config, mock_template_context):
        """Test successful generation of all firmware components."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            # Mock sub-methods
            generator._generate_build_integration = Mock(
                return_value="# Build integration"
            )
            generator._generate_constraint_files = Mock(
                return_value={"timing": "# Timing"}
            )
            generator._generate_tcl_scripts = Mock(
                return_value={"build": "# Build TCL"}
            )
            generator._generate_config_space_hex = Mock(return_value="# Config hex")
            generator._generate_writemask_coe = Mock(return_value="# Writemask COE")

            result = generator._generate_firmware_components(mock_template_context)

            assert result["build_integration"] == "# Build integration"
            assert result["constraint_files"] == {"timing": "# Timing"}
            assert result["tcl_scripts"] == {"build": "# Build TCL"}
            assert result["config_space_hex"] == "# Config hex"
            assert result["writemask_coe"] == "# Writemask COE"

    def test_build_integration_with_fallback(self, mock_config, mock_template_context):
        """Test build integration generation with fallback handling."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.sv_generator.generate_pcileech_integration_code.side_effect = (
                Exception("Failed")
            )
            generator.sv_generator.generate_enhanced_build_integration.return_value = (
                "# Enhanced build"
            )
            generator.fallback_manager.confirm_fallback = Mock(return_value=True)

            result = generator._generate_build_integration(mock_template_context)

            assert result == "# Enhanced build"
            generator.fallback_manager.confirm_fallback.assert_called()


class TestFirmwareValidation:
    """Test firmware validation functionality."""

    def test_successful_validation(
        self, mock_config, mock_systemverilog_modules, mock_firmware_components
    ):
        """Test successful firmware validation."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            # Should not raise any exceptions
            generator._validate_generated_firmware(
                mock_systemverilog_modules, mock_firmware_components
            )

    def test_validation_missing_modules(self, mock_config, mock_firmware_components):
        """Test validation failure when required modules are missing."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            incomplete_modules = {
                "some_other_module": "module code"
            }  # Missing required module

            with pytest.raises(PCILeechGenerationError) as exc_info:
                generator._validate_generated_firmware(
                    incomplete_modules, mock_firmware_components
                )

            assert "Missing required SystemVerilog modules" in str(exc_info.value)

    def test_validation_empty_module(self, mock_config, mock_firmware_components):
        """Test validation failure when module content is empty."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            modules_with_empty = {
                "pcileech_tlps128_bar_controller": "   \n   ",  # Empty content
            }

            with pytest.raises(PCILeechGenerationError) as exc_info:
                generator._validate_generated_firmware(
                    modules_with_empty, mock_firmware_components
                )

            assert "is empty" in str(exc_info.value)

    def test_validation_disabled(
        self, mock_config, mock_systemverilog_modules, mock_firmware_components
    ):
        """Test validation when strict validation is disabled."""
        mock_config.strict_validation = False

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            # Should not validate when strict_validation is False
            generator._validate_generated_firmware({}, {})  # Empty modules should pass


class TestSaveGeneratedFirmware:
    """Test saving generated firmware to disk."""

    def test_successful_firmware_save(self, mock_config):
        """Test successful saving of all firmware components."""
        generation_result = {
            "systemverilog_modules": {
                "pcileech_tlps128_bar_controller": "module code",
                "advanced_controller.sv": "advanced module code",
                "pcileech_cfgspace.coe": "COE content",
            },
            "firmware_components": {
                "writemask_coe": "writemask COE content",
                "config_space_hex": "hex content",
            },
            "generation_metadata": {"version": "1.0.0"},
        }

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch("pathlib.Path.mkdir") as mock_mkdir:
                with patch("pathlib.Path.write_text") as mock_write_text:
                    with patch("builtins.open", mock_open()) as mock_file:
                        result = generator.save_generated_firmware(generation_result)

                        assert result == mock_config.output_dir
                        # Verify directories were created
                        assert mock_mkdir.call_count >= 2  # output_dir and sv_dir
                        # Verify files were written
                        assert (
                            mock_write_text.call_count >= 4
                        )  # SV modules + components

    def test_save_with_custom_output_dir(self, mock_config):
        """Test saving firmware to custom output directory."""
        generation_result = {
            "systemverilog_modules": {},
            "firmware_components": {},
            "generation_metadata": {},
        }
        custom_dir = Path("/custom/output")

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch("pathlib.Path.mkdir") as mock_mkdir:
                with patch("pathlib.Path.write_text"):
                    with patch("builtins.open", mock_open()):
                        result = generator.save_generated_firmware(
                            generation_result, custom_dir
                        )

                        assert result == custom_dir

    def test_save_failure(self, mock_config):
        """Test handling of save failures."""
        generation_result = {
            "systemverilog_modules": {"test": "code"},
            "firmware_components": {},
            "generation_metadata": {},
        }

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch("pathlib.Path.mkdir") as mock_mkdir:
                mock_mkdir.side_effect = OSError("Permission denied")

                with pytest.raises(PCILeechGenerationError) as exc_info:
                    generator.save_generated_firmware(generation_result)

                assert "Failed to save generated firmware" in str(exc_info.value)


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios."""

    def test_vfio_binding_cleanup_on_error(self, mock_config):
        """Test VFIO binding cleanup when generation fails."""
        with patch(
            "src.device_clone.pcileech_generator.VFIOBinder"
        ) as mock_vfio_binder:
            mock_vfio_context = MagicMock()
            mock_vfio_context.__enter__.return_value = "/dev/vfio/1"
            mock_vfio_context.__exit__.return_value = None
            mock_vfio_binder.return_value = mock_vfio_context

            with patch.multiple(
                "src.device_clone.pcileech_generator",
                BehaviorProfiler=Mock(),
                ConfigSpaceManager=Mock(),
                TemplateRenderer=Mock(),
                AdvancedSVGenerator=Mock(),
            ):
                generator = PCILeechGenerator(mock_config)
                generator._preload_msix_data_early = Mock(return_value=None)
                generator._capture_device_behavior = Mock(return_value=None)
                generator._analyze_configuration_space_with_vfio = Mock(
                    side_effect=Exception("Analysis failed")
                )

                with pytest.raises(PCILeechGenerationError):
                    generator.generate_pcileech_firmware()

                # Verify VFIO cleanup was called
                mock_vfio_context.__exit__.assert_called_once()

    def test_fallback_manager_integration(self, mock_config):
        """Test integration with fallback manager for error recovery."""
        mock_config.fallback_mode = "prompt"
        mock_config.allowed_fallbacks = ["behavior-profiling"]

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.behavior_profiler = Mock()
            generator.behavior_profiler.capture_behavior_profile.side_effect = (
                Exception("Capture failed")
            )

            # Mock user confirming fallback
            generator.fallback_manager.confirm_fallback = Mock(return_value=True)

            result = generator._capture_device_behavior()

            assert result is None  # Fallback to None
            generator.fallback_manager.confirm_fallback.assert_called_once_with(
                "behavior-profiling",
                "Capture failed",
                implications="Without behavior profiling, the generated firmware may not accurately reflect device timing patterns and behavior.",
            )


class TestMetadataAndUtilities:
    """Test metadata generation and utility methods."""

    def test_build_generation_metadata(self, mock_config):
        """Test generation metadata building."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            metadata = generator._build_generation_metadata()

            assert metadata["generator_version"] == "1.0.0"
            assert metadata["config"]["device_bdf"] == "0000:01:00.0"
            assert metadata["config"]["device_profile"] == "test_device"
            assert "BehaviorProfiler" in metadata["components_used"]

    def test_get_timestamp(self, mock_config):
        """Test timestamp generation."""
        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            with patch("src.device_clone.pcileech_generator.datetime") as mock_datetime:
                mock_now = Mock()
                mock_now.isoformat.return_value = "2024-01-01T00:00:00"
                mock_datetime.now.return_value = mock_now

                timestamp = generator._get_timestamp()

                assert timestamp == "2024-01-01T00:00:00"


class TestAdvancedFeatures:
    """Test advanced feature generation."""

    def test_advanced_module_generation(self, mock_config, mock_template_context):
        """Test generation of advanced SystemVerilog modules."""
        mock_template_context["device_config"]["behavior_profile"] = {
            "register_accesses": [
                {"register": "STATUS", "offset": 0x00, "operation": "read"},
            ]
        }

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)
            generator.sv_generator.generate_advanced_systemverilog.return_value = (
                "advanced module"
            )

            result = generator._generate_advanced_modules(mock_template_context)

            assert "advanced_controller" in result
            assert result["advanced_controller"] == "advanced module"

    def test_register_extraction(self, mock_config, mock_template_context):
        """Test register definition extraction from behavior profile."""
        mock_template_context["device_config"]["behavior_profile"] = {
            "register_accesses": [
                {"register": "STATUS", "offset": 0x00, "operation": "read"},
                {"register": "CONTROL", "offset": 0x04, "operation": "write"},
            ]
        }

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
        ):
            generator = PCILeechGenerator(mock_config)

            registers = generator._extract_register_definitions(mock_template_context)

            assert len(registers) == 2
            assert registers[0]["name"] == "STATUS"
            assert registers[0]["offset"] == 0x00
            assert registers[1]["name"] == "CONTROL"
            assert registers[1]["offset"] == 0x04


# Integration test for complete workflow
class TestIntegration:
    """Integration tests for complete PCILeech generation workflow."""

    @patch("src.device_clone.pcileech_generator.VFIOBinder")
    def test_complete_generation_workflow(
        self,
        mock_vfio_binder,
        mock_config,
        mock_behavior_profile,
        mock_config_space_data,
        mock_msix_data,
    ):
        """Test complete firmware generation workflow with all components."""
        # Setup VFIO context
        mock_vfio_context = MagicMock()
        mock_vfio_context.__enter__.return_value = "/dev/vfio/1"
        mock_vfio_context.__exit__.return_value = None
        mock_vfio_binder.return_value = mock_vfio_context

        with patch.multiple(
            "src.device_clone.pcileech_generator",
            BehaviorProfiler=Mock(),
            ConfigSpaceManager=Mock(),
            TemplateRenderer=Mock(),
            AdvancedSVGenerator=Mock(),
            PCILeechContextBuilder=Mock(),
            WritemaskGenerator=Mock(),
            ConfigSpaceHexFormatter=Mock(),
        ):
            # Create generator
            generator = PCILeechGenerator(mock_config)

            # Setup all mocks for complete workflow
            generator.behavior_profiler.capture_behavior_profile.return_value = (
                mock_behavior_profile
            )
            generator.behavior_profiler.analyze_patterns.return_value = {
                "pattern": "test"
            }
            generator.config_space_manager._read_sysfs_config_space.return_value = (
                mock_config_space_data["raw_config_space"]
            )
            generator.config_space_manager.extract_device_info.return_value = (
                mock_config_space_data["device_info"]
            )

            # Mock MSI-X parsing
            with patch(
                "src.device_clone.pcileech_generator.parse_msix_capability"
            ) as mock_parse:
                with patch(
                    "src.device_clone.pcileech_generator.validate_msix_configuration"
                ) as mock_validate:
                    mock_parse.return_value = mock_msix_data["capability_info"]
                    mock_validate.return_value = (True, [])

                    # Mock context builder
                    mock_context_builder = Mock()
                    mock_context_builder.build_context.return_value = {
                        "device_config": {},
                        "config_space": {},
                        "msix_config": {},
                        "bar_config": {},
                        "timing_config": {},
                        "pcileech_config": {},
                    }
                    generator.context_builder = mock_context_builder

                    # Mock SV generation
                    generator.sv_generator.generate_systemverilog_modules.return_value = {
                        "pcileech_tlps128_bar_controller": "module code",
                    }
                    generator.sv_generator.generate_pcileech_integration_code.return_value = (
                        "integration"
                    )

                    # Execute complete workflow
                    result = generator.generate_pcileech_firmware()

                    # Verify all major components were generated
                    assert result["device_bdf"] == "0000:01:00.0"
                    assert result["behavior_profile"] is not None
                    assert result["config_space_data"] is not None
                    assert result["msix_data"] is not None
                    assert result["template_context"] is not None
                    assert result["systemverilog_modules"] is not None
                    assert result["firmware_components"] is not None
                    assert result["generation_metadata"] is not None

                    # Verify VFIO was properly managed
                    mock_vfio_context.__enter__.assert_called_once()
                    mock_vfio_context.__exit__.assert_called_once()
