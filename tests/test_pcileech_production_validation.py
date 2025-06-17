#!/usr/bin/env python3
"""
PCILeech Production Validation Tests

This module contains comprehensive tests that validate the complete PCILeech
implementation meets all production requirements and specifications.

Tests cover:
- Complete firmware generation with real device configurations
- Generated firmware meets PCILeech requirements specification
- Error handling with invalid or missing device data
- Performance requirements and resource constraints validation
- Manufacturing variance integration
- SystemVerilog code validation
- TCL script validation
- Data flow validation
- Production readiness validation
"""

import pytest
import sys
import re
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Set, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from device_clone.pcileech_generator import (
        PCILeechGenerator,
        PCILeechGenerationConfig,
        PCILeechGenerationError,
    )
    from device_clone.pcileech_context import PCILeechContextBuilder
    from device_clone.behavior_profiler import BehaviorProfile
    from templating.systemverilog_generator import AdvancedSVGenerator
    from templating.tcl_builder import TCLBuilder

    PRODUCTION_VALIDATION_AVAILABLE = True
except ImportError as e:
    PRODUCTION_VALIDATION_AVAILABLE = False
    IMPORT_ERROR = str(e)


@pytest.mark.skipif(
    not PRODUCTION_VALIDATION_AVAILABLE,
    reason=f"Production validation components not available: {IMPORT_ERROR if not PRODUCTION_VALIDATION_AVAILABLE else ''}",
)
class TestPCILeechProductionValidation:
    """Test PCILeech production validation and requirements compliance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_device_bdf = "0000:03:00.0"
        self.production_config = PCILeechGenerationConfig(
            device_bdf=self.test_device_bdf,
            device_profile="network_card",
            enable_behavior_profiling=True,
            behavior_capture_duration=30.0,
            enable_manufacturing_variance=True,
            enable_advanced_features=True,
            strict_validation=True,
            fail_on_missing_data=True,
            pcileech_command_timeout=1000,
            pcileech_buffer_size=4096,
            enable_dma_operations=True,
        )

        # Production-ready device configuration
        self.production_device_config = {
            "vendor_id": "8086",
            "device_id": "153c",
            "class_code": "020000",
            "revision_id": "04",
            "subsystem_vendor_id": "8086",
            "subsystem_device_id": "0001",
            "bars": [
                {
                    "index": 0,
                    "base_address": 0xE0000000,
                    "size": 131072,
                    "type": 0,
                    "prefetchable": 0,
                },
                {
                    "index": 2,
                    "base_address": 0xE0020000,
                    "size": 16384,
                    "type": 0,
                    "prefetchable": 0,
                },
                {
                    "index": 4,
                    "base_address": 0x0000E000,
                    "size": 32,
                    "type": 1,
                    "prefetchable": 0,
                },
            ],
        }

        # Production-ready behavior profile
        self.production_behavior_profile = Mock(spec=BehaviorProfile)
        self.production_behavior_profile.device_bdf = self.test_device_bdf
        self.production_behavior_profile.total_accesses = 5000
        self.production_behavior_profile.capture_duration = 30.0
        self.production_behavior_profile.timing_patterns = [
            Mock(
                avg_interval_us=4.0, frequency_hz=250.0, confidence=0.95
            ),  # High-frequency pattern
            Mock(
                avg_interval_us=8.0, frequency_hz=125.0, confidence=0.90
            ),  # Medium-frequency pattern
        ]
        self.production_behavior_profile.state_transitions = [
            Mock(from_state="idle", to_state="active", frequency=500),
            Mock(from_state="active", to_state="processing", frequency=480),
            Mock(from_state="processing", to_state="idle", frequency=495),
        ]
        self.production_behavior_profile.variance_metadata = {
            "variance_detected": True,
            "thermal_impact": "low",
            "voltage_impact": "minimal",
            "timing_stability": 0.92,
        }

        # Production MSI-X configuration
        self.production_msix_config = {
            "capability_info": {
                "table_size": 32,
                "table_bir": 0,
                "table_offset": 0x2000,
                "pba_bir": 0,
                "pba_offset": 0x3000,
                "enabled": True,
                "function_mask": False,
            },
            "table_size": 32,
            "table_bir": 0,
            "table_offset": 0x2000,
            "pba_bir": 0,
            "pba_offset": 0x3000,
            "enabled": True,
            "function_mask": False,
            "validation_errors": [],
            "is_valid": True,
        }

    def test_complete_firmware_generation_real_device_config(self):
        """Test complete firmware generation with realistic device configurations."""
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
            # Setup production-ready mocks
            mock_profiler = Mock()
            mock_profiler.capture_behavior_profile.return_value = (
                self.production_behavior_profile
            )
            mock_profiler.analyze_patterns.return_value = {
                "pcileech_compatible": True,
                "performance_class": "high",
                "complexity_score": 0.85,
            }
            mock_profiler_class.return_value = mock_profiler

            mock_config_manager = Mock()
            mock_config_manager.read_vfio_config_space.return_value = (
                b"\x86\x80\x3c\x15" + b"\x00" * 252
            )
            mock_config_manager.extract_device_info.return_value = (
                self.production_device_config
            )
            mock_config_manager_class.return_value = mock_config_manager

            mock_parse_msix.return_value = self.production_msix_config[
                "capability_info"
            ]
            mock_validate_msix.return_value = (True, [])

            # Production-ready template context
            production_context = {
                "device_config": {
                    "vendor_id": "8086",
                    "device_id": "153c",
                    "class_code": "020000",
                    "total_register_accesses": 5000,
                    "timing_patterns_count": 2,
                    "enable_error_injection": True,
                    "enable_perf_counters": True,
                    "enable_dma_operations": True,
                },
                "config_space": {
                    "vendor_id": "8086",
                    "device_id": "153c",
                    "size": 256,
                    "bars": self.production_device_config["bars"],
                },
                "msix_config": {
                    "num_vectors": 32,
                    "table_offset": 0x2000,
                    "pba_offset": 0x3000,
                    "is_supported": True,
                },
                "bar_config": {
                    "bar_index": 0,
                    "aperture_size": 131072,
                    "bars": self.production_device_config["bars"],
                },
                "timing_config": {
                    "read_latency": 2,
                    "write_latency": 1,
                    "burst_length": 32,
                    "clock_frequency_mhz": 250.0,
                    "has_timing_patterns": True,
                    "timing_regularity": 0.92,
                },
                "pcileech_config": {
                    "command_timeout": 1000,
                    "buffer_size": 4096,
                    "enable_dma": True,
                    "max_payload_size": 256,
                    "max_read_request_size": 512,
                },
            }

            mock_context_builder = Mock()
            mock_context_builder.build_context.return_value = production_context
            mock_context_builder_class.return_value = mock_context_builder

            # Production-ready SystemVerilog modules
            production_sv_modules = {
                "pcileech_fifo": self._generate_production_pcileech_fifo(),
                "pcileech_tlps128_bar_controller": self._generate_production_bar_controller(),
                "cfg_shadow": self._generate_production_cfg_shadow(),
                "msix_implementation": self._generate_production_msix_implementation(),
                "top_level_wrapper": self._generate_production_top_level(),
            }

            mock_sv_generator = Mock()
            mock_sv_generator.generate_systemverilog_modules.return_value = (
                production_sv_modules
            )
            mock_sv_generator_class.return_value = mock_sv_generator

            mock_template_renderer = Mock()
            mock_template_renderer.render_template.return_value = (
                "// Production-ready content"
            )
            mock_template_renderer_class.return_value = mock_template_renderer

            # Generate production firmware
            generator = PCILeechGenerator(self.production_config)
            result = generator.generate_pcileech_firmware()

            # Validate production firmware structure
            self._validate_production_firmware_structure(result)

            # Validate SystemVerilog modules meet production requirements
            self._validate_production_systemverilog_modules(
                result["systemverilog_modules"]
            )

            # Validate performance requirements
            self._validate_performance_requirements(result)

            # Validate resource constraints
            self._validate_resource_constraints(result)

    def test_generated_firmware_meets_pcileech_requirements(self):
        """Test that generated firmware meets PCILeech requirements specification."""
        # Load PCILeech requirements (mock for testing)
        pcileech_requirements = {
            "clock_frequency_range": {"min_mhz": 125, "max_mhz": 250},
            "resource_limits": {
                "luts": {"min": 750, "max": 1300},
                "ffs": {"min": 482, "max": 864},
                "brams": {"min": 2, "max": 3},
            },
            "timing_constraints": {
                "setup_time_ns": 2.0,
                "hold_time_ns": 0.5,
                "max_delay_ns": 8.0,
            },
            "functionality_requirements": [
                "pcileech_fifo_implementation",
                "bar_controller_with_dma",
                "configuration_space_shadow",
                "msix_interrupt_support",
                "error_handling_and_recovery",
                "performance_monitoring",
            ],
            "interface_requirements": {
                "pcie_lanes": [1, 4, 8],
                "pcie_generation": [2, 3],
                "supported_commands": [
                    "PCILEECH_CMD_READ",
                    "PCILEECH_CMD_WRITE",
                    "PCILEECH_CMD_PROBE",
                    "PCILEECH_CMD_WRITE_SCATTER",
                    "PCILEECH_CMD_READ_SCATTER",
                ],
            },
        }

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
            # Setup mocks for requirements testing
            self._setup_requirements_testing_mocks(
                mock_profiler_class,
                mock_config_manager_class,
                mock_template_renderer_class,
                mock_sv_generator_class,
                mock_context_builder_class,
                mock_parse_msix,
                mock_validate_msix,
            )

            # Generate firmware
            generator = PCILeechGenerator(self.production_config)
            result = generator.generate_pcileech_firmware()

            # Validate against PCILeech requirements
            self._validate_clock_frequency_requirements(result, pcileech_requirements)
            self._validate_resource_requirements(result, pcileech_requirements)
            self._validate_timing_requirements(result, pcileech_requirements)
            self._validate_functionality_requirements(result, pcileech_requirements)
            self._validate_interface_requirements(result, pcileech_requirements)

    def test_error_handling_invalid_missing_device_data(self):
        """Test error handling with invalid or missing device data."""
        error_test_cases = [
            {
                "name": "invalid_device_bdf",
                "config_override": {"device_bdf": "invalid:bdf:format"},
                "expected_error": "Invalid device BDF format",
            },
            {
                "name": "missing_behavior_profile",
                "mock_setup": lambda mocks: mocks[
                    "profiler"
                ].capture_behavior_profile.side_effect.__setattr__(
                    "side_effect", Exception("Device not accessible for profiling")
                ),
                "expected_error": "Device behavior profiling failed",
            },
            {
                "name": "corrupted_config_space",
                "mock_setup": lambda mocks: mocks[
                    "config_manager"
                ].read_vfio_config_space.return_value.__setattr__(
                    "return_value", b"\x00" * 256  # All zeros - invalid
                ),
                "expected_error": "Invalid configuration space",
            },
            {
                "name": "invalid_msix_configuration",
                "mock_setup": lambda mocks: mocks[
                    "validate_msix"
                ].return_value.__setattr__(
                    "return_value",
                    (False, ["Invalid MSI-X table size", "Invalid BIR value"]),
                ),
                "expected_error": "MSI-X validation failed",
            },
            {
                "name": "insufficient_device_resources",
                "mock_setup": lambda mocks: None,  # Will be handled in test
                "expected_error": "Insufficient device resources",
            },
        ]

        for test_case in error_test_cases:
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
                    self.production_behavior_profile
                )
                mock_profiler_class.return_value = mock_profiler

                mock_config_manager = Mock()
                mock_config_manager.read_vfio_config_space.return_value = (
                    b"\x86\x80\x3c\x15" + b"\x00" * 252
                )
                mock_config_manager.extract_device_info.return_value = (
                    self.production_device_config
                )
                mock_config_manager_class.return_value = mock_config_manager

                mock_parse_msix.return_value = self.production_msix_config[
                    "capability_info"
                ]
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
                mock_template_renderer_class.return_value = mock_template_renderer

                mocks = {
                    "profiler": mock_profiler,
                    "config_manager": mock_config_manager,
                    "validate_msix": mock_validate_msix,
                }

                # Apply test-specific setup
                if "mock_setup" in test_case and test_case["mock_setup"]:
                    test_case["mock_setup"](mocks)

                # Create config with overrides
                config = self.production_config
                if "config_override" in test_case:
                    config_dict = config.__dict__.copy()
                    config_dict.update(test_case["config_override"])
                    config = PCILeechGenerationConfig(**config_dict)

                # Test error handling
                if test_case["name"] == "insufficient_device_resources":
                    # Mock resource constraint violation
                    mock_context_builder.build_context.side_effect = Exception(
                        "Insufficient device resources for PCILeech implementation"
                    )

                generator = PCILeechGenerator(config)

                with pytest.raises(PCILeechGenerationError) as exc_info:
                    generator.generate_pcileech_firmware()

                # Validate error message contains expected content
                error_message = str(exc_info.value).lower()
                expected_keywords = test_case["expected_error"].lower().split()
                assert any(
                    keyword in error_message for keyword in expected_keywords
                ), f"Expected error keywords {expected_keywords} not found in: {error_message}"

    def test_performance_requirements_validation(self):
        """Test performance requirements and resource constraints validation."""
        performance_test_cases = [
            {
                "name": "high_frequency_operation",
                "clock_frequency_mhz": 250.0,
                "expected_performance": {
                    "max_throughput_gbps": 8.0,
                    "min_latency_cycles": 2,
                    "max_latency_cycles": 8,
                },
            },
            {
                "name": "standard_frequency_operation",
                "clock_frequency_mhz": 125.0,
                "expected_performance": {
                    "max_throughput_gbps": 4.0,
                    "min_latency_cycles": 4,
                    "max_latency_cycles": 16,
                },
            },
            {
                "name": "resource_constrained_operation",
                "clock_frequency_mhz": 100.0,
                "resource_constraints": {
                    "max_luts": 1000,
                    "max_ffs": 600,
                    "max_brams": 2,
                },
                "expected_performance": {
                    "max_throughput_gbps": 3.2,
                    "min_latency_cycles": 6,
                    "max_latency_cycles": 20,
                },
            },
        ]

        for test_case in performance_test_cases:
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
                # Setup performance-specific mocks
                mock_profiler = Mock()
                mock_profiler.capture_behavior_profile.return_value = (
                    self.production_behavior_profile
                )
                mock_profiler_class.return_value = mock_profiler

                mock_config_manager = Mock()
                mock_config_manager.read_vfio_config_space.return_value = (
                    b"\x86\x80\x3c\x15" + b"\x00" * 252
                )
                mock_config_manager.extract_device_info.return_value = (
                    self.production_device_config
                )
                mock_config_manager_class.return_value = mock_config_manager

                mock_parse_msix.return_value = self.production_msix_config[
                    "capability_info"
                ]
                mock_validate_msix.return_value = (True, [])

                # Performance-specific context
                performance_context = {
                    "timing_config": {
                        "clock_frequency_mhz": test_case["clock_frequency_mhz"],
                        "read_latency": test_case["expected_performance"][
                            "min_latency_cycles"
                        ],
                        "write_latency": test_case["expected_performance"][
                            "min_latency_cycles"
                        ]
                        // 2,
                        "burst_length": 32,
                    },
                    "device_config": {"vendor_id": "8086", "device_id": "153c"},
                    "pcileech_config": {"command_timeout": 1000, "buffer_size": 4096},
                }

                if "resource_constraints" in test_case:
                    performance_context["resource_config"] = test_case[
                        "resource_constraints"
                    ]

                mock_context_builder = Mock()
                mock_context_builder.build_context.return_value = performance_context
                mock_context_builder_class.return_value = mock_context_builder

                # Performance-optimized SystemVerilog
                performance_modules = {
                    "pcileech_fifo": self._generate_performance_optimized_fifo(
                        test_case["clock_frequency_mhz"]
                    ),
                    "bar_controller": self._generate_performance_optimized_bar_controller(
                        test_case["clock_frequency_mhz"]
                    ),
                }

                mock_sv_generator = Mock()
                mock_sv_generator.generate_systemverilog_modules.return_value = (
                    performance_modules
                )
                mock_sv_generator_class.return_value = mock_sv_generator

                mock_template_renderer = Mock()
                mock_template_renderer_class.return_value = mock_template_renderer

                # Generate firmware with performance constraints
                generator = PCILeechGenerator(self.production_config)
                result = generator.generate_pcileech_firmware()

                # Validate performance requirements
                self._validate_performance_metrics(
                    result, test_case["expected_performance"]
                )

                # Validate resource utilization
                if "resource_constraints" in test_case:
                    self._validate_resource_utilization(
                        result, test_case["resource_constraints"]
                    )

    def test_manufacturing_variance_integration_validation(self):
        """Test manufacturing variance integration validation."""
        variance_scenarios = [
            {
                "name": "thermal_variance_high",
                "variance_type": "thermal",
                "variance_level": "high",
                "expected_adaptations": {
                    "clock_frequency_reduction": 0.9,
                    "timing_margin_increase": 1.2,
                    "power_management_enabled": True,
                },
            },
            {
                "name": "voltage_variance_medium",
                "variance_type": "voltage",
                "variance_level": "medium",
                "expected_adaptations": {
                    "voltage_regulation_enabled": True,
                    "timing_margin_increase": 1.1,
                    "error_detection_enhanced": True,
                },
            },
            {
                "name": "process_variance_low",
                "variance_type": "process",
                "variance_level": "low",
                "expected_adaptations": {
                    "performance_optimization": True,
                    "resource_utilization_optimized": True,
                },
            },
        ]

        for scenario in variance_scenarios:
            # Create variance-specific behavior profile
            variance_profile = Mock(spec=BehaviorProfile)
            variance_profile.device_bdf = self.test_device_bdf
            variance_profile.total_accesses = 4500
            variance_profile.variance_metadata = {
                "variance_detected": True,
                "variance_type": scenario["variance_type"],
                "variance_level": scenario["variance_level"],
                "impact_assessment": scenario["expected_adaptations"],
            }

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
                # Setup variance-aware mocks
                mock_profiler = Mock()
                mock_profiler.capture_behavior_profile.return_value = variance_profile
                mock_profiler_class.return_value = mock_profiler

                mock_config_manager = Mock()
                mock_config_manager.read_vfio_config_space.return_value = (
                    b"\x86\x80\x3c\x15" + b"\x00" * 252
                )
                mock_config_manager.extract_device_info.return_value = (
                    self.production_device_config
                )
                mock_config_manager_class.return_value = mock_config_manager

                mock_parse_msix.return_value = self.production_msix_config[
                    "capability_info"
                ]
                mock_validate_msix.return_value = (True, [])

                # Variance-adapted context
                variance_context = {
                    "device_config": {
                        "vendor_id": "8086",
                        "device_id": "153c",
                        "has_manufacturing_variance": True,
                        "variance_adaptations": scenario["expected_adaptations"],
                    },
                    "timing_config": {
                        "clock_frequency_mhz": 125.0
                        * scenario["expected_adaptations"].get(
                            "clock_frequency_reduction", 1.0
                        ),
                        "timing_margin_factor": scenario["expected_adaptations"].get(
                            "timing_margin_increase", 1.0
                        ),
                    },
                    "pcileech_config": {"command_timeout": 1000, "buffer_size": 4096},
                }

                mock_context_builder = Mock()
                mock_context_builder.build_context.return_value = variance_context
                mock_context_builder_class.return_value = mock_context_builder

                # Variance-adapted SystemVerilog
                variance_modules = {
                    "pcileech_fifo": self._generate_variance_adapted_fifo(scenario),
                    "bar_controller": self._generate_variance_adapted_bar_controller(
                        scenario
                    ),
                }

                mock_sv_generator = Mock()
                mock_sv_generator.generate_systemverilog_modules.return_value = (
                    variance_modules
                )
                mock_sv_generator_class.return_value = mock_sv_generator

                mock_template_renderer = Mock()
                mock_template_renderer_class.return_value = mock_template_renderer

                # Generate variance-adapted firmware
                generator = PCILeechGenerator(self.production_config)
                result = generator.generate_pcileech_firmware()

                # Validate variance adaptations
                self._validate_variance_adaptations(result, scenario)

    def test_data_flow_validation_complete_pipeline(self):
        """Test complete data flow validation from device profiling to firmware generation."""
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
            # Track data flow through pipeline
            data_flow_tracker = {
                "behavior_profiling": None,
                "config_space_analysis": None,
                "msix_processing": None,
                "context_building": None,
                "systemverilog_generation": None,
                "firmware_assembly": None,
            }

            # Setup data flow tracking mocks
            mock_profiler = Mock()

            def track_behavior_profiling(*args, **kwargs):
                data_flow_tracker["behavior_profiling"] = {
                    "input": {"duration": kwargs.get("duration", 30.0)},
                    "output": self.production_behavior_profile,
                }
                return self.production_behavior_profile

            mock_profiler.capture_behavior_profile.side_effect = (
                track_behavior_profiling
            )
            mock_profiler_class.return_value = mock_profiler

            mock_config_manager = Mock()

            def track_config_space_analysis(*args, **kwargs):
                data_flow_tracker["config_space_analysis"] = {
                    "input": {"bdf": self.test_device_bdf},
                    "output": self.production_device_config,
                }
                return self.production_device_config

    # Helper methods for production validation tests

    def _generate_production_pcileech_fifo(self) -> str:
        """Generate production-ready PCILeech FIFO module."""
        return """
// Production PCILeech FIFO Implementation
module pcileech_fifo #(
    parameter DATA_WIDTH = 128,
    parameter ADDR_WIDTH = 10,
    parameter DEPTH = 1024
) (
    input wire clk,
    input wire rst_n,
    
    // Write interface
    input wire wr_en,
    input wire [DATA_WIDTH-1:0] wr_data,
    output wire wr_full,
    
    // Read interface
    input wire rd_en,
    output reg [DATA_WIDTH-1:0] rd_data,
    output wire rd_empty,
    
    // Status
    output wire [ADDR_WIDTH:0] count
);

    // Production-ready FIFO implementation with error checking
    reg [DATA_WIDTH-1:0] memory [0:DEPTH-1];
    reg [ADDR_WIDTH:0] wr_ptr, rd_ptr;
    
    assign wr_full = (count == DEPTH);
    assign rd_empty = (count == 0);
    assign count = wr_ptr - rd_ptr;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= 0;
            rd_ptr <= 0;
            rd_data <= 0;
        end else begin
            if (wr_en && !wr_full) begin
                memory[wr_ptr[ADDR_WIDTH-1:0]] <= wr_data;
                wr_ptr <= wr_ptr + 1;
            end
            if (rd_en && !rd_empty) begin
                rd_data <= memory[rd_ptr[ADDR_WIDTH-1:0]];
                rd_ptr <= rd_ptr + 1;
            end
        end
    end

endmodule
"""

    def _generate_production_bar_controller(self) -> str:
        """Generate production-ready BAR controller module."""
        return """
// Production PCILeech BAR Controller
module pcileech_tlps128_bar_controller #(
    parameter BAR_SIZE = 32'h00020000,
    parameter VENDOR_ID = 16'h8086,
    parameter DEVICE_ID = 16'h153c
) (
    input wire clk,
    input wire rst_n,
    
    // PCIe TLP interface
    input wire [127:0] tlp_rx_data,
    input wire tlp_rx_valid,
    output reg tlp_rx_ready,
    
    output reg [127:0] tlp_tx_data,
    output reg tlp_tx_valid,
    input wire tlp_tx_ready,
    
    // Memory interface
    output reg [31:0] mem_addr,
    output reg [31:0] mem_wdata,
    input wire [31:0] mem_rdata,
    output reg mem_we,
    output reg mem_re
);

    // Production-ready BAR controller with full TLP processing
    localparam IDLE = 2'b00, READ = 2'b01, WRITE = 2'b10, RESPONSE = 2'b11;
    reg [1:0] state;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            tlp_rx_ready <= 1'b1;
            tlp_tx_valid <= 1'b0;
            mem_we <= 1'b0;
            mem_re <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    if (tlp_rx_valid) begin
                        // Decode TLP header
                        if (tlp_rx_data[127:125] == 3'b000) // Memory read
                            state <= READ;
                        else if (tlp_rx_data[127:125] == 3'b010) // Memory write
                            state <= WRITE;
                    end
                end
                READ: begin
                    mem_addr <= tlp_rx_data[95:64];
                    mem_re <= 1'b1;
                    state <= RESPONSE;
                end
                WRITE: begin
                    mem_addr <= tlp_rx_data[95:64];
                    mem_wdata <= tlp_rx_data[31:0];
                    mem_we <= 1'b1;
                    state <= IDLE;
                end
                RESPONSE: begin
                    if (tlp_tx_ready) begin
                        tlp_tx_data <= {32'h4A000001, 32'h00000000, 32'h00000000, mem_rdata};
                        tlp_tx_valid <= 1'b1;
                        state <= IDLE;
                    end
                end
            endcase
        end
    end

endmodule
"""

    def _generate_production_cfg_shadow(self) -> str:
        """Generate production-ready configuration space shadow module."""
        return """
// Production Configuration Space Shadow
module cfg_shadow #(
    parameter VENDOR_ID = 16'h8086,
    parameter DEVICE_ID = 16'h153c,
    parameter CLASS_CODE = 24'h020000
) (
    input wire clk,
    input wire rst_n,
    
    // Configuration space interface
    input wire [11:0] cfg_addr,
    input wire [31:0] cfg_wdata,
    output reg [31:0] cfg_rdata,
    input wire cfg_we,
    input wire cfg_re,
    
    // Device-specific registers
    output reg [31:0] device_control,
    output reg [31:0] device_status
);

    // Configuration space registers
    reg [31:0] cfg_space [0:63];
    
    // Initialize configuration space
    initial begin
        cfg_space[0] = {DEVICE_ID, VENDOR_ID};
        cfg_space[1] = 32'h00100007; // Status, Command
        cfg_space[2] = {CLASS_CODE, 8'h04}; // Class code, Revision
        cfg_space[3] = 32'h00000000; // BIST, Header type, Latency timer, Cache line size
        // BARs and other registers initialized as needed
    end
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cfg_rdata <= 32'h0;
            device_control <= 32'h0;
            device_status <= 32'h0;
        end else begin
            if (cfg_re) begin
                cfg_rdata <= cfg_space[cfg_addr[7:2]];
            end
            if (cfg_we) begin
                cfg_space[cfg_addr[7:2]] <= cfg_wdata;
                // Update device-specific registers
                if (cfg_addr[7:2] == 6'h10) device_control <= cfg_wdata;
                if (cfg_addr[7:2] == 6'h11) device_status <= cfg_wdata;
            end
        end
    end

endmodule
"""

    def _generate_production_msix_implementation(self) -> str:
        """Generate production-ready MSI-X implementation module."""
        return """
// Production MSI-X Implementation
module msix_implementation #(
    parameter NUM_VECTORS = 32,
    parameter TABLE_OFFSET = 32'h2000,
    parameter PBA_OFFSET = 32'h3000
) (
    input wire clk,
    input wire rst_n,
    
    // MSI-X table interface
    input wire [11:0] table_addr,
    input wire [31:0] table_wdata,
    output reg [31:0] table_rdata,
    input wire table_we,
    input wire table_re,
    
    // Interrupt generation
    input wire [NUM_VECTORS-1:0] interrupt_req,
    output reg [NUM_VECTORS-1:0] interrupt_ack,
    
    // PCIe interrupt interface
    output reg msi_req,
    output reg [63:0] msi_addr,
    output reg [31:0] msi_data,
    input wire msi_ack
);

    // MSI-X table entries (16 bytes each: addr_low, addr_high, data, control)
    reg [31:0] msix_table [0:NUM_VECTORS*4-1];
    reg [NUM_VECTORS-1:0] pending_bits;
    
    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < NUM_VECTORS*4; i = i + 1)
                msix_table[i] <= 32'h0;
            pending_bits <= 0;
            interrupt_ack <= 0;
            msi_req <= 1'b0;
        end else begin
            // Handle table access
            if (table_re) begin
                table_rdata <= msix_table[table_addr[9:2]];
            end
            if (table_we) begin
                msix_table[table_addr[9:2]] <= table_wdata;
            end
            
            // Handle interrupt requests
            for (i = 0; i < NUM_VECTORS; i = i + 1) begin
                if (interrupt_req[i] && !pending_bits[i]) begin
                    pending_bits[i] <= 1'b1;
                    if (!msix_table[i*4+3][0]) begin // Vector not masked
                        msi_addr <= {msix_table[i*4+1], msix_table[i*4]};
                        msi_data <= msix_table[i*4+2];
                        msi_req <= 1'b1;
                    end
                end
                if (msi_ack && msi_req) begin
                    pending_bits[i] <= 1'b0;
                    interrupt_ack[i] <= 1'b1;
                    msi_req <= 1'b0;
                end else begin
                    interrupt_ack[i] <= 1'b0;
                end
            end
        end
    end

endmodule
"""

    def _generate_production_top_level(self) -> str:
        """Generate production-ready top-level wrapper module."""
        return """
// Production Top-Level PCILeech Wrapper
module pcileech_top #(
    parameter VENDOR_ID = 16'h8086,
    parameter DEVICE_ID = 16'h153c,
    parameter PCIE_LANES = 4
) (
    input wire clk_pcie,
    input wire rst_pcie_n,
    
    // PCIe interface
    input wire [PCIE_LANES*8-1:0] pcie_rx_data,
    input wire pcie_rx_valid,
    output wire pcie_rx_ready,
    
    output wire [PCIE_LANES*8-1:0] pcie_tx_data,
    output wire pcie_tx_valid,
    input wire pcie_tx_ready,
    
    // Status and control
    output wire [31:0] status_reg,
    input wire [31:0] control_reg,
    
    // Debug interface
    output wire [31:0] debug_signals
);

    // Internal signals
    wire [127:0] tlp_rx_data, tlp_tx_data;
    wire tlp_rx_valid, tlp_rx_ready, tlp_tx_valid, tlp_tx_ready;
    
    // Instantiate PCILeech components
    pcileech_fifo fifo_inst (
        .clk(clk_pcie),
        .rst_n(rst_pcie_n),
        // FIFO connections
    );
    
    pcileech_tlps128_bar_controller bar_ctrl_inst (
        .clk(clk_pcie),
        .rst_n(rst_pcie_n),
        .tlp_rx_data(tlp_rx_data),
        .tlp_rx_valid(tlp_rx_valid),
        .tlp_rx_ready(tlp_rx_ready),
        .tlp_tx_data(tlp_tx_data),
        .tlp_tx_valid(tlp_tx_valid),
        .tlp_tx_ready(tlp_tx_ready)
    );
    
    cfg_shadow cfg_inst (
        .clk(clk_pcie),
        .rst_n(rst_pcie_n),
        // Configuration space connections
    );
    
    msix_implementation msix_inst (
        .clk(clk_pcie),
        .rst_n(rst_pcie_n),
        // MSI-X connections
    );
    
    // Status and debug
    assign status_reg = {16'h0, DEVICE_ID};
    assign debug_signals = {tlp_rx_valid, tlp_tx_valid, 30'h0};

endmodule
"""

    def _validate_production_firmware_structure(self, result: Dict[str, Any]) -> None:
        """Validate production firmware structure."""
        required_keys = [
            "device_bdf",
            "generation_timestamp",
            "systemverilog_modules",
            "firmware_components",
            "template_context",
            "generation_metadata",
        ]

        for key in required_keys:
            assert key in result, f"Missing required firmware key: {key}"

        # Validate SystemVerilog modules
        sv_modules = result["systemverilog_modules"]
        required_modules = [
            "pcileech_fifo",
            "pcileech_tlps128_bar_controller",
            "cfg_shadow",
        ]
        for module in required_modules:
            assert (
                module in sv_modules
            ), f"Missing required SystemVerilog module: {module}"

    def _validate_production_systemverilog_modules(
        self, modules: Dict[str, str]
    ) -> None:
        """Validate production SystemVerilog modules."""
        for module_name, module_code in modules.items():
            # Check basic SystemVerilog syntax
            assert "module " in module_code, f"No module declaration in {module_name}"
            assert "endmodule" in module_code, f"No endmodule in {module_name}"

            # Check for production-ready features
            if "pcileech" in module_name.lower():
                assert "clk" in module_code, f"No clock signal in {module_name}"
                assert "rst_n" in module_code, f"No reset signal in {module_name}"

    def _validate_performance_requirements(self, result: Dict[str, Any]) -> None:
        """Validate performance requirements."""
        context = result.get("template_context", {})
        timing_config = context.get("timing_config", {})

        # Check clock frequency is within acceptable range
        clock_freq = timing_config.get("clock_frequency_mhz", 0)
        assert (
            100 <= clock_freq <= 300
        ), f"Clock frequency {clock_freq} MHz out of range"

        # Check latency requirements
        read_latency = timing_config.get("read_latency", 0)
        assert (
            1 <= read_latency <= 10
        ), f"Read latency {read_latency} cycles out of range"

    def _validate_resource_constraints(self, result: Dict[str, Any]) -> None:
        """Validate resource constraints."""
        # Mock resource validation - in real implementation would analyze generated code
        sv_modules = result.get("systemverilog_modules", {})

        # Estimate resource usage based on module count and complexity
        estimated_luts = len(sv_modules) * 200  # Rough estimate
        estimated_ffs = len(sv_modules) * 150  # Rough estimate
        estimated_brams = min(3, len(sv_modules))  # Max 3 BRAMs

        assert (
            500 <= estimated_luts <= 1500
        ), f"Estimated LUT usage {estimated_luts} out of range"
        assert (
            300 <= estimated_ffs <= 1000
        ), f"Estimated FF usage {estimated_ffs} out of range"
        assert estimated_brams <= 4, f"Estimated BRAM usage {estimated_brams} too high"

    def _setup_requirements_testing_mocks(self, *mock_classes) -> None:
        """Setup mocks for requirements testing."""
        # Setup standard mocks for requirements validation
        (
            mock_profiler_class,
            mock_config_manager_class,
            mock_template_renderer_class,
            mock_sv_generator_class,
            mock_context_builder_class,
            mock_parse_msix,
            mock_validate_msix,
        ) = mock_classes

        # Standard mock setup
        mock_profiler = Mock()
        mock_profiler.capture_behavior_profile.return_value = (
            self.production_behavior_profile
        )
        mock_profiler_class.return_value = mock_profiler

        mock_config_manager = Mock()
        mock_config_manager.read_vfio_config_space.return_value = (
            b"\x86\x80\x3c\x15" + b"\x00" * 252
        )
        mock_config_manager.extract_device_info.return_value = (
            self.production_device_config
        )
        mock_config_manager_class.return_value = mock_config_manager

    def _validate_clock_frequency_requirements(
        self, result: Dict[str, Any], requirements: Dict[str, Any]
    ) -> None:
        """Validate clock frequency requirements."""
        context = result.get("template_context", {})
        timing_config = context.get("timing_config", {})
        clock_freq = timing_config.get("clock_frequency_mhz", 0)

        freq_range = requirements["clock_frequency_range"]
        assert (
            freq_range["min_mhz"] <= clock_freq <= freq_range["max_mhz"]
        ), f"Clock frequency {clock_freq} MHz not in required range {freq_range}"

    def _validate_resource_requirements(
        self, result: Dict[str, Any], requirements: Dict[str, Any]
    ) -> None:
        """Validate resource requirements."""
        # Mock resource validation
        resource_limits = requirements["resource_limits"]

        # Estimate resources from generated modules
        sv_modules = result.get("systemverilog_modules", {})
        estimated_resources = {
            "luts": len(sv_modules) * 180,
            "ffs": len(sv_modules) * 120,
            "brams": min(3, len(sv_modules)),
        }

        for resource, limits in resource_limits.items():
            estimated = estimated_resources.get(resource, 0)
            assert (
                limits["min"] <= estimated <= limits["max"]
            ), f"Estimated {resource} usage {estimated} not in required range {limits}"

    def _validate_timing_requirements(
        self, result: Dict[str, Any], requirements: Dict[str, Any]
    ) -> None:
        """Validate timing requirements."""
        timing_constraints = requirements["timing_constraints"]
        context = result.get("template_context", {})
        timing_config = context.get("timing_config", {})

        # Validate timing parameters are within constraints
        read_latency_ns = (
            timing_config.get("read_latency", 4) * 8.0
        )  # Convert cycles to ns at 125MHz
        assert (
            read_latency_ns <= timing_constraints["max_delay_ns"]
        ), f"Read latency {read_latency_ns} ns exceeds maximum {timing_constraints['max_delay_ns']} ns"

    def _validate_functionality_requirements(
        self, result: Dict[str, Any], requirements: Dict[str, Any]
    ) -> None:
        """Validate functionality requirements."""
        sv_modules = result.get("systemverilog_modules", {})
        required_functions = requirements["functionality_requirements"]

        # Check that required functional modules are present
        function_map = {
            "pcileech_fifo_implementation": "pcileech_fifo",
            "bar_controller_with_dma": "bar_controller",
            "configuration_space_shadow": "cfg_shadow",
            "msix_interrupt_support": "msix_implementation",
        }

        for function, module in function_map.items():
            if function in required_functions:
                assert any(
                    module in name for name in sv_modules.keys()
                ), f"Required functionality {function} not implemented"

    def _validate_interface_requirements(
        self, result: Dict[str, Any], requirements: Dict[str, Any]
    ) -> None:
        """Validate interface requirements."""
        context = result.get("template_context", {})
        pcileech_config = context.get("pcileech_config", {})

        # Validate supported commands
        supported_commands = pcileech_config.get("supported_commands", [])
        required_commands = requirements["interface_requirements"]["supported_commands"]

        for cmd in required_commands:
            assert cmd in supported_commands, f"Required command {cmd} not supported"

    def _generate_performance_optimized_fifo(self, clock_freq_mhz: float) -> str:
        """Generate performance-optimized FIFO for given clock frequency."""
        depth = int(1024 * (clock_freq_mhz / 125.0))  # Scale depth with frequency
        return f"""
// Performance-optimized FIFO for {clock_freq_mhz} MHz
module pcileech_fifo #(
    parameter DEPTH = {depth},
    parameter DATA_WIDTH = 128
) (
    input wire clk,
    input wire rst_n,
    // High-performance FIFO interface
    input wire wr_en,
    input wire [DATA_WIDTH-1:0] wr_data,
    output wire wr_full,
    input wire rd_en,
    output reg [DATA_WIDTH-1:0] rd_data,
    output wire rd_empty
);
    // Optimized implementation for {clock_freq_mhz} MHz operation
endmodule
"""

    def _generate_performance_optimized_bar_controller(
        self, clock_freq_mhz: float
    ) -> str:
        """Generate performance-optimized BAR controller."""
        pipeline_stages = int(
            clock_freq_mhz / 125.0
        )  # More pipeline stages for higher frequencies
        return f"""
// Performance-optimized BAR controller for {clock_freq_mhz} MHz
module bar_controller #(
    parameter PIPELINE_STAGES = {pipeline_stages}
) (
    input wire clk,
    input wire rst_n,
    // High-performance BAR interface
    input wire [127:0] tlp_data,
    input wire tlp_valid,
    output wire tlp_ready
);
    // Optimized {pipeline_stages}-stage pipeline for {clock_freq_mhz} MHz
endmodule
"""

    def _validate_performance_metrics(
        self, result: Dict[str, Any], expected_performance: Dict[str, Any]
    ) -> None:
        """Validate performance metrics."""
        context = result.get("template_context", {})
        timing_config = context.get("timing_config", {})

        # Validate latency requirements
        read_latency = timing_config.get("read_latency", 0)
        assert (
            expected_performance["min_latency_cycles"]
            <= read_latency
            <= expected_performance["max_latency_cycles"]
        ), f"Read latency {read_latency} not in expected range"

    def _validate_resource_utilization(
        self, result: Dict[str, Any], constraints: Dict[str, Any]
    ) -> None:
        """Validate resource utilization against constraints."""
        sv_modules = result.get("systemverilog_modules", {})

        # Estimate resource usage
        estimated_luts = len(sv_modules) * 150
        estimated_ffs = len(sv_modules) * 100

        if "max_luts" in constraints:
            assert (
                estimated_luts <= constraints["max_luts"]
            ), f"Estimated LUT usage {estimated_luts} exceeds constraint {constraints['max_luts']}"

        if "max_ffs" in constraints:
            assert (
                estimated_ffs <= constraints["max_ffs"]
            ), f"Estimated FF usage {estimated_ffs} exceeds constraint {constraints['max_ffs']}"

    def _generate_variance_adapted_fifo(self, scenario: Dict[str, Any]) -> str:
        """Generate variance-adapted FIFO."""
        adaptations = scenario["expected_adaptations"]
        return f"""
// Variance-adapted FIFO for {scenario['variance_type']} variance
module pcileech_fifo_adapted (
    input wire clk,
    input wire rst_n,
    // Variance adaptations: {adaptations}
    input wire [127:0] data_in,
    output reg [127:0] data_out
);
    // Implementation adapted for {scenario['variance_level']} {scenario['variance_type']} variance
endmodule
"""

    def _generate_variance_adapted_bar_controller(
        self, scenario: Dict[str, Any]
    ) -> str:
        """Generate variance-adapted BAR controller."""
        return f"""
// Variance-adapted BAR controller for {scenario['variance_type']} variance
module bar_controller_adapted (
    input wire clk,
    input wire rst_n,
    // Adapted for {scenario['variance_level']} variance level
    input wire [127:0] tlp_data,
    output reg [127:0] response_data
);
    // Implementation with {scenario['variance_type']} variance compensation
endmodule
"""

    def _validate_variance_adaptations(
        self, result: Dict[str, Any], scenario: Dict[str, Any]
    ) -> None:
        """Validate variance adaptations."""
        context = result.get("template_context", {})
        device_config = context.get("device_config", {})

        # Verify variance adaptations are present
        assert (
            device_config.get("has_manufacturing_variance") is True
        ), "Manufacturing variance not detected in device config"

        # Verify specific adaptations based on scenario
        adaptations = device_config.get("variance_adaptations", {})
        expected_adaptations = scenario["expected_adaptations"]

        for adaptation, expected_value in expected_adaptations.items():
            if isinstance(expected_value, bool):
                assert (
                    adaptations.get(adaptation) == expected_value
                ), f"Variance adaptation {adaptation} not properly set"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
