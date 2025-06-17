#!/usr/bin/env python3
"""
PCILeech Production Ready Integration Tests

This module contains comprehensive end-to-end tests that validate the complete
PCILeech firmware generation workflow is production-ready and functions correctly
as the primary build pattern.

Tests cover:
- Complete end-to-end PCILeech firmware generation workflow
- Dynamic data source integration validation
- Production-ready error handling and fail-fast behavior
- Integration with existing device cloning infrastructure
- No hard-coded fallbacks validation
"""

import pytest
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from device_clone.pcileech_generator import (
        PCILeechGenerator,
        PCILeechGenerationConfig,
        PCILeechGenerationError,
    )
    from device_clone.pcileech_context import (
        PCILeechContextBuilder,
        PCILeechContextError,
    )
    from device_clone.behavior_profiler import BehaviorProfile, BehaviorProfiler
    from device_clone.config_space_manager import ConfigSpaceManager
    from device_clone.msix_capability import (
        parse_msix_capability,
        validate_msix_configuration,
    )
    from templating.systemverilog_generator import AdvancedSVGenerator
    from templating.template_renderer import TemplateRenderer, TemplateRenderError

    PCILEECH_AVAILABLE = True
except ImportError as e:
    PCILEECH_AVAILABLE = False
    IMPORT_ERROR = str(e)


@pytest.mark.skipif(
    not PCILEECH_AVAILABLE,
    reason=f"PCILeech components not available: {IMPORT_ERROR if not PCILEECH_AVAILABLE else ''}",
)
class TestPCILeechProductionReady:
    """Test complete PCILeech production readiness."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_device_bdf = "0000:03:00.0"
        self.test_config = PCILeechGenerationConfig(
            device_bdf=self.test_device_bdf,
            device_profile="network_card",
            enable_behavior_profiling=True,
            behavior_capture_duration=5.0,
            enable_manufacturing_variance=True,
            enable_advanced_features=True,
            strict_validation=True,
            fail_on_missing_data=True,
        )

        # Mock behavior profile data
        self.mock_behavior_profile = Mock(spec=BehaviorProfile)
        self.mock_behavior_profile.total_accesses = 1500
        self.mock_behavior_profile.capture_duration = 5.0
        self.mock_behavior_profile.timing_patterns = [
            Mock(avg_interval_us=10.5, frequency_hz=95.2, confidence=0.85)
        ]
        self.mock_behavior_profile.state_transitions = [Mock(), Mock(), Mock()]
        self.mock_behavior_profile.variance_metadata = {"variance_detected": True}
        self.mock_behavior_profile.pattern_analysis = {"complex_patterns": True}

        # Mock configuration space data
        self.mock_config_space_data = {
            "raw_config_space": b"\x86\x80\x3c\x15" + b"\x00" * 252,
            "config_space_hex": "86803c15" + "00" * 252,
            "device_info": {
                "vendor_id": "8086",
                "device_id": "153c",
                "class_code": "020000",
                "revision_id": "04",
                "bars": [
                    0xE0000000,
                    0x00000000,
                    0xE0020000,
                    0x00000000,
                    0x0000E000,
                    0x00000000,
                ],
            },
            "vendor_id": "8086",
            "device_id": "153c",
            "class_code": "020000",
            "revision_id": "04",
            "bars": [
                0xE0000000,
                0x00000000,
                0xE0020000,
                0x00000000,
                0x0000E000,
                0x00000000,
            ],
            "config_space_size": 256,
        }

        # Mock MSI-X data
        self.mock_msix_data = {
            "capability_info": {
                "table_size": 8,
                "table_bir": 0,
                "table_offset": 0x2000,
                "pba_bir": 0,
                "pba_offset": 0x3000,
                "enabled": True,
                "function_mask": False,
            },
            "table_size": 8,
            "table_bir": 0,
            "table_offset": 0x2000,
            "pba_bir": 0,
            "pba_offset": 0x3000,
            "enabled": True,
            "function_mask": False,
            "validation_errors": [],
            "is_valid": True,
        }

    def test_complete_end_to_end_workflow(self):
        """Test complete end-to-end PCILeech firmware generation workflow."""
        with (
            patch(
                "device_clone.pcileech_generator.BehaviorProfiler"
            ) as mock_profiler_class,
            patch(
                "device_clone.pcileech_generator.ConfigSpaceManager"
            ) as mock_config_manager_class,
            patch(
                "device_clone.pcileech_generator.TemplateRenderer"
            ) as mock_template_renderer_class,
            patch(
                "device_clone.pcileech_generator.AdvancedSVGenerator"
            ) as mock_sv_generator_class,
            patch(
                "device_clone.pcileech_generator.PCILeechContextBuilder"
            ) as mock_context_builder_class,
            patch(
                "device_clone.pcileech_generator.parse_msix_capability"
            ) as mock_parse_msix,
            patch(
                "device_clone.pcileech_generator.validate_msix_configuration"
            ) as mock_validate_msix,
        ):
            # Setup mocks
            mock_profiler = Mock()
            mock_profiler.capture_behavior_profile.return_value = (
                self.mock_behavior_profile
            )
            mock_profiler.analyze_patterns.return_value = {"complex_patterns": True}
            mock_profiler_class.return_value = mock_profiler

            mock_config_manager = Mock()
            mock_config_manager.read_vfio_config_space.return_value = (
                self.mock_config_space_data["raw_config_space"]
            )
            mock_config_manager.extract_device_info.return_value = (
                self.mock_config_space_data["device_info"]
            )
            mock_config_manager_class.return_value = mock_config_manager

            mock_parse_msix.return_value = self.mock_msix_data["capability_info"]
            mock_validate_msix.return_value = (True, [])

            mock_context_builder = Mock()
            mock_context_builder.build_context.return_value = {
                "device_config": {"vendor_id": "8086", "device_id": "153c"},
                "config_space": {"raw_data": "86803c15"},
                "msix_config": {"num_vectors": 8},
                "bar_config": {"bar_index": 0, "aperture_size": 65536},
                "timing_config": {"read_latency": 4, "write_latency": 2},
                "pcileech_config": {"command_timeout": 1000},
            }
            mock_context_builder_class.return_value = mock_context_builder

            mock_sv_generator = Mock()
            mock_sv_generator.generate_systemverilog_modules.return_value = {
                "pcileech_fifo": "module pcileech_fifo();",
                "bar_controller": "module bar_controller();",
                "cfg_shadow": "module cfg_shadow();",
            }
            mock_sv_generator_class.return_value = mock_sv_generator

            mock_template_renderer = Mock()
            mock_template_renderer.render_template.return_value = "generated_content"
            mock_template_renderer_class.return_value = mock_template_renderer

            # Create generator and run complete workflow
            generator = PCILeechGenerator(self.test_config)
            result = generator.generate_pcileech_firmware()

            # Validate complete workflow execution
            assert result is not None
            assert result["device_bdf"] == self.test_device_bdf
            assert "generation_timestamp" in result
            assert "behavior_profile" in result
            assert "config_space_data" in result
            assert "msix_data" in result
            assert "template_context" in result
            assert "systemverilog_modules" in result
            assert "firmware_components" in result
            assert "generation_metadata" in result

            # Validate all components were called
            mock_profiler.capture_behavior_profile.assert_called_once()
            mock_profiler.analyze_patterns.assert_called_once()
            mock_config_manager.read_vfio_config_space.assert_called_once()
            mock_config_manager.extract_device_info.assert_called_once()
            mock_parse_msix.assert_called_once()
            mock_validate_msix.assert_called_once()
            mock_context_builder.build_context.assert_called_once()
            mock_sv_generator.generate_systemverilog_modules.assert_called_once()

    def test_dynamic_data_sources_integration(self):
        """Test that all dynamic data sources are properly integrated."""
        with (
            patch(
                "device_clone.pcileech_generator.BehaviorProfiler"
            ) as mock_profiler_class,
            patch(
                "device_clone.pcileech_generator.ConfigSpaceManager"
            ) as mock_config_manager_class,
            patch(
                "device_clone.pcileech_generator.TemplateRenderer"
            ) as mock_template_renderer_class,
            patch(
                "device_clone.pcileech_generator.AdvancedSVGenerator"
            ) as mock_sv_generator_class,
            patch(
                "device_clone.pcileech_generator.PCILeechContextBuilder"
            ) as mock_context_builder_class,
            patch(
                "device_clone.pcileech_generator.parse_msix_capability"
            ) as mock_parse_msix,
            patch(
                "device_clone.pcileech_generator.validate_msix_configuration"
            ) as mock_validate_msix,
        ):
            # Setup mocks to return dynamic data
            mock_profiler = Mock()
            mock_profiler.capture_behavior_profile.return_value = (
                self.mock_behavior_profile
            )
            mock_profiler.analyze_patterns.return_value = {"dynamic_analysis": True}
            mock_profiler_class.return_value = mock_profiler

            mock_config_manager = Mock()
            mock_config_manager.read_vfio_config_space.return_value = (
                self.mock_config_space_data["raw_config_space"]
            )
            mock_config_manager.extract_device_info.return_value = (
                self.mock_config_space_data["device_info"]
            )
            mock_config_manager_class.return_value = mock_config_manager

            mock_parse_msix.return_value = self.mock_msix_data["capability_info"]
            mock_validate_msix.return_value = (True, [])

            # Mock context builder to verify dynamic data integration
            mock_context_builder = Mock()
            expected_context = {
                "device_config": {
                    "vendor_id": "8086",  # From dynamic config space
                    "device_id": "153c",  # From dynamic config space
                    "total_register_accesses": 1500,  # From dynamic behavior profile
                    "timing_patterns_count": 1,  # From dynamic behavior profile
                },
                "config_space": {
                    "raw_data": "86803c15" + "00" * 252,  # From dynamic config space
                    "vendor_id": "8086",  # From dynamic config space
                },
                "msix_config": {
                    "num_vectors": 8,  # From dynamic MSI-X parsing
                    "table_offset": 0x2000,  # From dynamic MSI-X parsing
                },
                "bar_config": {
                    "bars": [  # From dynamic config space
                        {"index": 0, "base_address": 0xE0000000},
                        {"index": 2, "base_address": 0xE0020000},
                        {"index": 4, "base_address": 0x0000E000},
                    ]
                },
                "timing_config": {
                    "avg_access_interval_us": 10.5,  # From dynamic behavior analysis
                    "avg_access_frequency_hz": 95.2,  # From dynamic behavior analysis
                },
            }
            mock_context_builder.build_context.return_value = expected_context
            mock_context_builder_class.return_value = mock_context_builder

            mock_sv_generator = Mock()
            mock_sv_generator.generate_systemverilog_modules.return_value = {
                "test": "module"
            }
            mock_sv_generator_class.return_value = mock_sv_generator

            mock_template_renderer = Mock()
            mock_template_renderer_class.return_value = mock_template_renderer

            # Generate firmware
            generator = PCILeechGenerator(self.test_config)
            result = generator.generate_pcileech_firmware()

            # Verify context builder was called with all dynamic data
            mock_context_builder.build_context.assert_called_once()
            call_args = mock_context_builder.build_context.call_args[1]

            # Verify behavior profile data is dynamic
            assert call_args["behavior_profile"] == self.mock_behavior_profile
            assert call_args["behavior_profile"].total_accesses == 1500

            # Verify config space data is dynamic
            assert call_args["config_space_data"]["vendor_id"] == "8086"
            assert call_args["config_space_data"]["device_id"] == "153c"

            # Verify MSI-X data is dynamic
            assert call_args["msix_data"]["table_size"] == 8
            assert call_args["msix_data"]["table_offset"] == 0x2000

    def test_no_hard_coded_fallbacks_validation(self):
        """Test that no hard-coded fallbacks are used anywhere in the pipeline."""
        # Test with fail_on_missing_data=True to ensure no fallbacks
        strict_config = PCILeechGenerationConfig(
            device_bdf=self.test_device_bdf,
            fail_on_missing_data=True,
            strict_validation=True,
        )

        with (
            patch(
                "device_clone.pcileech_generator.BehaviorProfiler"
            ) as mock_profiler_class,
            patch(
                "device_clone.pcileech_generator.ConfigSpaceManager"
            ) as mock_config_manager_class,
            patch(
                "device_clone.pcileech_generator.TemplateRenderer"
            ) as mock_template_renderer_class,
            patch(
                "device_clone.pcileech_generator.AdvancedSVGenerator"
            ) as mock_sv_generator_class,
        ):
            # Setup mocks to fail and verify no fallbacks are used
            mock_profiler = Mock()
            mock_profiler.capture_behavior_profile.side_effect = Exception(
                "Behavior profiling failed"
            )
            mock_profiler_class.return_value = mock_profiler

            mock_config_manager = Mock()
            mock_config_manager.read_vfio_config_space.side_effect = Exception(
                "Config space read failed"
            )
            mock_config_manager_class.return_value = mock_config_manager

            mock_template_renderer = Mock()
            mock_template_renderer_class.return_value = mock_template_renderer

            mock_sv_generator = Mock()
            mock_sv_generator_class.return_value = mock_sv_generator

            # Should fail fast without fallbacks
            generator = PCILeechGenerator(strict_config)

            with pytest.raises(
                PCILeechGenerationError, match="Behavior profiling failed"
            ):
                generator.generate_pcileech_firmware()

            # Verify no fallback data was used
            mock_profiler.capture_behavior_profile.assert_called_once()

    def test_production_ready_error_handling(self):
        """Test production-ready error handling and fail-fast behavior."""
        test_cases = [
            {
                "name": "behavior_profiler_failure",
                "mock_setup": lambda mocks: mocks[
                    "profiler"
                ].capture_behavior_profile.side_effect.__setattr__(
                    "side_effect", Exception("Device not accessible")
                ),
                "expected_error": "Device behavior profiling failed",
            },
            {
                "name": "config_space_failure",
                "mock_setup": lambda mocks: mocks[
                    "config_manager"
                ].read_vfio_config_space.side_effect.__setattr__(
                    "side_effect", Exception("VFIO access denied")
                ),
                "expected_error": "Configuration space analysis failed",
            },
            {
                "name": "msix_validation_failure",
                "mock_setup": lambda mocks: None,  # Will be handled in test
                "expected_error": "MSI-X validation failed",
            },
            {
                "name": "context_building_failure",
                "mock_setup": lambda mocks: mocks[
                    "context_builder"
                ].build_context.side_effect.__setattr__(
                    "side_effect", Exception("Context validation failed")
                ),
                "expected_error": "Template context building failed",
            },
        ]

        for test_case in test_cases:
            with (
                patch(
                    "device_clone.pcileech_generator.BehaviorProfiler"
                ) as mock_profiler_class,
                patch(
                    "device_clone.pcileech_generator.ConfigSpaceManager"
                ) as mock_config_manager_class,
                patch(
                    "device_clone.pcileech_generator.TemplateRenderer"
                ) as mock_template_renderer_class,
                patch(
                    "device_clone.pcileech_generator.AdvancedSVGenerator"
                ) as mock_sv_generator_class,
                patch(
                    "device_clone.pcileech_generator.PCILeechContextBuilder"
                ) as mock_context_builder_class,
                patch(
                    "device_clone.pcileech_generator.parse_msix_capability"
                ) as mock_parse_msix,
                patch(
                    "device_clone.pcileech_generator.validate_msix_configuration"
                ) as mock_validate_msix,
            ):
                # Setup base mocks
                mock_profiler = Mock()
                mock_profiler.capture_behavior_profile.return_value = (
                    self.mock_behavior_profile
                )
                mock_profiler_class.return_value = mock_profiler

                mock_config_manager = Mock()
                mock_config_manager.read_vfio_config_space.return_value = (
                    self.mock_config_space_data["raw_config_space"]
                )
                mock_config_manager.extract_device_info.return_value = (
                    self.mock_config_space_data["device_info"]
                )
                mock_config_manager_class.return_value = mock_config_manager

                mock_context_builder = Mock()
                mock_context_builder.build_context.return_value = {"test": "context"}
                mock_context_builder_class.return_value = mock_context_builder

                mock_parse_msix.return_value = self.mock_msix_data["capability_info"]
                mock_validate_msix.return_value = (True, [])

                mock_template_renderer = Mock()
                mock_template_renderer_class.return_value = mock_template_renderer

                mock_sv_generator = Mock()
                mock_sv_generator_class.return_value = mock_sv_generator

                mocks = {
                    "profiler": mock_profiler,
                    "config_manager": mock_config_manager,
                    "context_builder": mock_context_builder,
                }

                # Apply test-specific mock setup
                if test_case["name"] == "behavior_profiler_failure":
                    mock_profiler.capture_behavior_profile.side_effect = Exception(
                        "Device not accessible"
                    )
                elif test_case["name"] == "config_space_failure":
                    mock_config_manager.read_vfio_config_space.side_effect = Exception(
                        "VFIO access denied"
                    )
                elif test_case["name"] == "msix_validation_failure":
                    mock_validate_msix.return_value = (
                        False,
                        ["Invalid MSI-X table size"],
                    )
                elif test_case["name"] == "context_building_failure":
                    mock_context_builder.build_context.side_effect = Exception(
                        "Context validation failed"
                    )

                # Test fail-fast behavior
                generator = PCILeechGenerator(self.test_config)

                with pytest.raises(PCILeechGenerationError) as exc_info:
                    generator.generate_pcileech_firmware()

                assert test_case["expected_error"] in str(exc_info.value)

    def test_integration_with_existing_infrastructure(self):
        """Test integration with existing device cloning infrastructure."""
        with (
            patch(
                "device_clone.pcileech_generator.BehaviorProfiler"
            ) as mock_profiler_class,
            patch(
                "device_clone.pcileech_generator.ConfigSpaceManager"
            ) as mock_config_manager_class,
            patch(
                "device_clone.pcileech_generator.TemplateRenderer"
            ) as mock_template_renderer_class,
            patch(
                "device_clone.pcileech_generator.AdvancedSVGenerator"
            ) as mock_sv_generator_class,
            patch(
                "device_clone.pcileech_generator.PCILeechContextBuilder"
            ) as mock_context_builder_class,
        ):
            # Verify integration with existing components
            mock_profiler_class.assert_not_called()
            mock_config_manager_class.assert_not_called()
            mock_template_renderer_class.assert_not_called()
            mock_sv_generator_class.assert_not_called()
            mock_context_builder_class.assert_not_called()

            # Create generator - should initialize existing infrastructure
            generator = PCILeechGenerator(self.test_config)

            # Verify existing infrastructure components were initialized
            mock_profiler_class.assert_called_once_with(
                bdf=self.test_device_bdf,
                debug=True,
                enable_variance=True,
                enable_ftrace=True,
            )
            mock_config_manager_class.assert_called_once_with(
                bdf=self.test_device_bdf,
                device_profile="network_card",
            )
            mock_template_renderer_class.assert_called_once()
            mock_sv_generator_class.assert_called_once()

            # Verify no duplicate infrastructure was created
            assert hasattr(generator, "behavior_profiler")
            assert hasattr(generator, "config_space_manager")
            assert hasattr(generator, "template_renderer")
            assert hasattr(generator, "sv_generator")

    def test_comprehensive_logging_and_status_reporting(self):
        """Test comprehensive logging and status reporting throughout pipeline."""
        with (
            patch(
                "device_clone.pcileech_generator.BehaviorProfiler"
            ) as mock_profiler_class,
            patch(
                "device_clone.pcileech_generator.ConfigSpaceManager"
            ) as mock_config_manager_class,
            patch(
                "device_clone.pcileech_generator.TemplateRenderer"
            ) as mock_template_renderer_class,
            patch(
                "device_clone.pcileech_generator.AdvancedSVGenerator"
            ) as mock_sv_generator_class,
            patch(
                "device_clone.pcileech_generator.PCILeechContextBuilder"
            ) as mock_context_builder_class,
            patch(
                "device_clone.pcileech_generator.parse_msix_capability"
            ) as mock_parse_msix,
            patch(
                "device_clone.pcileech_generator.validate_msix_configuration"
            ) as mock_validate_msix,
            patch("device_clone.pcileech_generator.log_info_safe") as mock_log_info,
            patch("device_clone.pcileech_generator.log_error_safe") as mock_log_error,
            patch(
                "device_clone.pcileech_generator.log_warning_safe"
            ) as mock_log_warning,
        ):
            # Setup successful mocks
            mock_profiler = Mock()
            mock_profiler.capture_behavior_profile.return_value = (
                self.mock_behavior_profile
            )
            mock_profiler.analyze_patterns.return_value = {"patterns": True}
            mock_profiler_class.return_value = mock_profiler

            mock_config_manager = Mock()
            mock_config_manager.read_vfio_config_space.return_value = (
                self.mock_config_space_data["raw_config_space"]
            )
            mock_config_manager.extract_device_info.return_value = (
                self.mock_config_space_data["device_info"]
            )
            mock_config_manager_class.return_value = mock_config_manager

            mock_parse_msix.return_value = self.mock_msix_data["capability_info"]
            mock_validate_msix.return_value = (True, [])

            mock_context_builder = Mock()
            mock_context_builder.build_context.return_value = {"test": "context"}
            mock_context_builder_class.return_value = mock_context_builder

            mock_sv_generator = Mock()
            mock_sv_generator.generate_systemverilog_modules.return_value = {
                "test": "module"
            }
            mock_sv_generator_class.return_value = mock_sv_generator

            mock_template_renderer = Mock()
            mock_template_renderer.render_template.return_value = "content"
            mock_template_renderer_class.return_value = mock_template_renderer

            # Generate firmware
            generator = PCILeechGenerator(self.test_config)
            result = generator.generate_pcileech_firmware()

            # Verify comprehensive logging occurred
            expected_log_messages = [
                "Initializing PCILeech generator for device",
                "PCILeech generator components initialized successfully",
                "Starting PCILeech firmware generation for device",
                "Capturing device behavior profile for",
                "Captured",
                "Analyzing configuration space for device",
                "Configuration space analyzed:",
                "Processing MSI-X capabilities",
                "MSI-X capabilities processed:",
                "Building comprehensive template context",
                "Template context built successfully with",
                "PCILeech firmware generation completed successfully",
            ]

            # Check that logging was called with expected messages
            log_calls = [call.args[1] for call in mock_log_info.call_args_list]
            for expected_msg in expected_log_messages:
                assert any(
                    expected_msg in msg for msg in log_calls
                ), f"Missing log message: {expected_msg}"

    def test_firmware_generation_metadata_validation(self):
        """Test that generated firmware includes comprehensive metadata."""
        with (
            patch(
                "device_clone.pcileech_generator.BehaviorProfiler"
            ) as mock_profiler_class,
            patch(
                "device_clone.pcileech_generator.ConfigSpaceManager"
            ) as mock_config_manager_class,
            patch(
                "device_clone.pcileech_generator.TemplateRenderer"
            ) as mock_template_renderer_class,
            patch(
                "device_clone.pcileech_generator.AdvancedSVGenerator"
            ) as mock_sv_generator_class,
            patch(
                "device_clone.pcileech_generator.PCILeechContextBuilder"
            ) as mock_context_builder_class,
            patch(
                "device_clone.pcileech_generator.parse_msix_capability"
            ) as mock_parse_msix,
            patch(
                "device_clone.pcileech_generator.validate_msix_configuration"
            ) as mock_validate_msix,
        ):
            # Setup mocks
            mock_profiler = Mock()
            mock_profiler.capture_behavior_profile.return_value = (
                self.mock_behavior_profile
            )
            mock_profiler.analyze_patterns.return_value = {"patterns": True}
            mock_profiler_class.return_value = mock_profiler

            mock_config_manager = Mock()
            mock_config_manager.read_vfio_config_space.return_value = (
                self.mock_config_space_data["raw_config_space"]
            )
            mock_config_manager.extract_device_info.return_value = (
                self.mock_config_space_data["device_info"]
            )
            mock_config_manager_class.return_value = mock_config_manager

            mock_parse_msix.return_value = self.mock_msix_data["capability_info"]
            mock_validate_msix.return_value = (True, [])

            mock_context_builder = Mock()
            mock_context_builder.build_context.return_value = {"test": "context"}
            mock_context_builder_class.return_value = mock_context_builder

            mock_sv_generator = Mock()
            mock_sv_generator.generate_systemverilog_modules.return_value = {
                "pcileech_fifo": "module pcileech_fifo();",
                "bar_controller": "module bar_controller();",
            }
            mock_sv_generator_class.return_value = mock_sv_generator

            mock_template_renderer = Mock()
            mock_template_renderer.render_template.return_value = "content"
            mock_template_renderer_class.return_value = mock_template_renderer

            # Generate firmware
            generator = PCILeechGenerator(self.test_config)
            result = generator.generate_pcileech_firmware()

            # Validate comprehensive metadata
            required_metadata_keys = [
                "device_bdf",
                "generation_timestamp",
                "behavior_profile",
                "config_space_data",
                "msix_data",
                "template_context",
                "systemverilog_modules",
                "firmware_components",
                "generation_metadata",
            ]

            for key in required_metadata_keys:
                assert key in result, f"Missing required metadata key: {key}"

            # Validate generation metadata structure
            gen_metadata = result["generation_metadata"]
            assert "generator_version" in gen_metadata
            assert "generation_config" in gen_metadata
            assert "component_versions" in gen_metadata
            assert "validation_status" in gen_metadata

            # Validate SystemVerilog modules
            sv_modules = result["systemverilog_modules"]
            assert isinstance(sv_modules, dict)
            assert len(sv_modules) > 0
            assert "pcileech_fifo" in sv_modules
            assert "bar_controller" in sv_modules


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
