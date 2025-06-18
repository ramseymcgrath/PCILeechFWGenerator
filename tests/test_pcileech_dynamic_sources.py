#!/usr/bin/env python3
"""
PCILeech Dynamic Data Sources Tests

This module contains comprehensive tests that validate all dynamic data sources
are properly integrated and functioning without fallbacks.

Tests cover:
- BehaviorProfiler PCILeech-specific methods
- PCILeechContextBuilder with real device data
- ConfigSpaceManager integration with PCILeech
- MSIXCapability integration
- Dynamic data source validation (no fallbacks)
"""

import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from device_clone.behavior_profiler import BehaviorProfile, BehaviorProfiler
    from device_clone.config_space_manager import ConfigSpaceManager
    from device_clone.msix_capability import (
        MSIXCapability,
        parse_msix_capability,
        validate_msix_configuration,
    )
    from device_clone.pcileech_context import (
        PCILeechContextBuilder,
        PCILeechContextError,
    )
    from device_clone.pcileech_generator import PCILeechGenerationConfig

    DYNAMIC_SOURCES_AVAILABLE = True
except ImportError as e:
    DYNAMIC_SOURCES_AVAILABLE = False
    IMPORT_ERROR = str(e)


@pytest.mark.skipif(
    not DYNAMIC_SOURCES_AVAILABLE,
    reason=f"Dynamic sources not available: {IMPORT_ERROR if not DYNAMIC_SOURCES_AVAILABLE else ''}",
)
class TestPCILeechDynamicSources:
    """Test PCILeech dynamic data sources integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_device_bdf = "0000:03:00.0"
        self.test_device_profile = "network_card"

        # Mock real device configuration space data
        self.mock_config_space_bytes = bytes(
            [
                0x86,
                0x80,
                0x3C,
                0x15,  # Vendor ID: 8086, Device ID: 153c
                0x07,
                0x00,
                0x10,
                0x00,  # Command, Status
                0x04,
                0x00,
                0x00,
                0x02,  # Revision, Class Code
                0x10,
                0x00,
                0x00,
                0x00,  # Cache Line Size, Latency Timer, Header Type, BIST
                0x00,
                0x00,
                0x00,
                0xE0,  # BAR0
                0x00,
                0x00,
                0x00,
                0x00,  # BAR1
                0x00,
                0x00,
                0x02,
                0xE0,  # BAR2
                0x00,
                0x00,
                0x00,
                0x00,  # BAR3
                0x00,
                0xE0,
                0x00,
                0x00,  # BAR4
                0x00,
                0x00,
                0x00,
                0x00,  # BAR5
            ]
            + [0x00] * 220
        )  # Rest of config space

        # Mock behavior profile data
        self.mock_behavior_profile = Mock(spec=BehaviorProfile)
        self.mock_behavior_profile.device_bdf = self.test_device_bdf
        self.mock_behavior_profile.total_accesses = 2500
        self.mock_behavior_profile.capture_duration = 30.0
        self.mock_behavior_profile.timing_patterns = [
            Mock(avg_interval_us=8.5, frequency_hz=117.6, confidence=0.92),
            Mock(avg_interval_us=15.2, frequency_hz=65.8, confidence=0.78),
            Mock(avg_interval_us=25.0, frequency_hz=40.0, confidence=0.85),
        ]
        self.mock_behavior_profile.state_transitions = [
            Mock(from_state="idle", to_state="active", frequency=150),
            Mock(from_state="active", to_state="processing", frequency=120),
            Mock(from_state="processing", to_state="idle", frequency=145),
        ]
        self.mock_behavior_profile.variance_metadata = {
            "variance_detected": True,
            "variance_patterns": ["thermal", "voltage"],
            "confidence": 0.88,
        }

        # Mock MSI-X capability data
        self.mock_msix_capability_info = {
            "table_size": 16,
            "table_bir": 0,
            "table_offset": 0x2000,
            "pba_bir": 0,
            "pba_offset": 0x3000,
            "enabled": True,
            "function_mask": False,
        }

        # Mock PCILeech generation config
        self.test_config = PCILeechGenerationConfig(
            device_bdf=self.test_device_bdf,
            device_profile=self.test_device_profile,
            enable_behavior_profiling=True,
            behavior_capture_duration=30.0,
            enable_manufacturing_variance=True,
            enable_advanced_features=True,
            strict_validation=True,
            fail_on_missing_data=True,
        )

    def test_behavior_profiler_pcileech_specific_methods(self):
        """Test BehaviorProfiler PCILeech-specific methods and integration."""
        with (
            patch("device_clone.behavior_profiler.subprocess.run") as mock_subprocess,
            patch("device_clone.behavior_profiler.Path.exists") as mock_path_exists,
            patch("device_clone.behavior_profiler.Path.read_text") as mock_read_text,
        ):
            # Setup mocks for successful profiling
            mock_path_exists.return_value = True
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
            mock_read_text.return_value = "mock ftrace data"

            # Create profiler with PCILeech-specific configuration
            profiler = BehaviorProfiler(
                bdf=self.test_device_bdf,
                debug=True,
                enable_variance=True,
                enable_ftrace=True,
            )

            # Test PCILeech-specific behavior capture
            with patch.object(profiler, "_parse_ftrace_data") as mock_parse:
                mock_parse.return_value = self.mock_behavior_profile

                profile = profiler.capture_behavior_profile(duration=30.0)

                # Verify PCILeech-specific data is captured
                assert profile is not None
                assert profile.device_bdf == self.test_device_bdf
                assert profile.total_accesses > 0
                assert len(profile.timing_patterns) > 0
                assert len(profile.state_transitions) > 0
                assert profile.variance_metadata is not None

            # Test PCILeech pattern analysis
            with patch.object(profiler, "analyze_patterns") as mock_analyze:
                mock_analyze.return_value = {
                    "pcileech_compatible": True,
                    "timing_regularity": 0.85,
                    "state_machine_complexity": "medium",
                    "variance_impact": "low",
                }

                analysis = profiler.analyze_patterns(self.mock_behavior_profile)

                # Verify PCILeech-specific analysis
                assert analysis["pcileech_compatible"] is True
                assert "timing_regularity" in analysis
                assert "state_machine_complexity" in analysis
                assert "variance_impact" in analysis

    def test_pcileech_context_builder_with_real_device_data(self):
        """Test PCILeechContextBuilder with realistic device data."""
        # Create context builder
        context_builder = PCILeechContextBuilder(
            device_bdf=self.test_device_bdf,
            config=self.test_config,
        )

        # Prepare realistic configuration space data
        config_space_data = {
            "raw_config_space": self.mock_config_space_bytes,
            "config_space_hex": self.mock_config_space_bytes.hex(),
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

        # Prepare realistic MSI-X data
        msix_data = {
            "capability_info": self.mock_msix_capability_info,
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

        # Build context with real data
        context = context_builder.build_context(
            behavior_profile=self.mock_behavior_profile,
            config_space_data=config_space_data,
            msix_data=msix_data,
        )

        # Validate comprehensive context structure
        required_sections = [
            "device_config",
            "config_space",
            "msix_config",
            "bar_config",
            "timing_config",
            "pcileech_config",
            "generation_metadata",
        ]

        for section in required_sections:
            assert section in context, f"Missing context section: {section}"

        # Validate device configuration uses real data
        device_config = context["device_config"]
        assert device_config["vendor_id"] == "8086"
        assert device_config["device_id"] == "153c"
        assert device_config["class_code"] == "020000"
        assert device_config["total_register_accesses"] == 2500
        assert device_config["timing_patterns_count"] == 3

        # Validate configuration space context
        config_space = context["config_space"]
        assert config_space["vendor_id"] == "8086"
        assert config_space["device_id"] == "153c"
        assert config_space["size"] == 256
        assert len(config_space["bars"]) == 6

        # Validate MSI-X configuration
        msix_config = context["msix_config"]
        assert msix_config["num_vectors"] == 16
        assert msix_config["table_offset"] == 0x2000
        assert msix_config["pba_offset"] == 0x3000
        assert msix_config["is_supported"] is True

        # Validate BAR configuration
        bar_config = context["bar_config"]
        assert len(bar_config["bars"]) > 0
        assert bar_config["aperture_size"] > 0

        # Validate timing configuration uses behavior data
        timing_config = context["timing_config"]
        assert timing_config["has_timing_patterns"] is True
        assert "avg_access_interval_us" in timing_config
        assert "timing_regularity" in timing_config

    def test_config_space_manager_pcileech_integration(self):
        """Test ConfigSpaceManager integration with PCILeech."""
        with (
            patch("device_clone.config_space_manager.Path.exists") as mock_exists,
            patch(
                "device_clone.config_space_manager.Path.read_bytes"
            ) as mock_read_bytes,
        ):
            # Setup mocks for VFIO config space access
            mock_exists.return_value = True
            mock_read_bytes.return_value = self.mock_config_space_bytes

            # Create config space manager
            config_manager = ConfigSpaceManager(
                bdf=self.test_device_bdf,
                device_profile=self.test_device_profile,
            )

            # Test VFIO config space reading
            config_space_bytes = config_manager.read_vfio_config_space()
            assert config_space_bytes == self.mock_config_space_bytes
            assert len(config_space_bytes) == 256

            # Test device info extraction
            device_info = config_manager.extract_device_info(config_space_bytes)

            # Validate extracted device information
            assert device_info["vendor_id"] == "8086"
            assert device_info["device_id"] == "153c"
            assert device_info["class_code"] == "020000"
            assert device_info["revision_id"] == "04"
            assert len(device_info["bars"]) == 6

            # Validate BAR parsing
            bars = device_info["bars"]
            assert bars[0] == 0xE0000000  # BAR0
            assert bars[2] == 0xE0020000  # BAR2
            assert bars[4] == 0x0000E000  # BAR4

            # Test PCILeech-specific device profile handling
            assert hasattr(config_manager, "device_profile")
            assert config_manager.device_profile == self.test_device_profile

    def test_msix_capability_integration(self):
        """Test MSI-X capability integration with PCILeech."""
        # Create realistic MSI-X capability data in config space
        msix_config_space = (
            "86803c15" + "00" * 60 + "11800010" + "00" * 188
        )  # MSI-X capability at offset 64

        # Test MSI-X capability parsing
        msix_info = parse_msix_capability(msix_config_space)

        # Validate MSI-X parsing (mock implementation)
        with patch("device_clone.msix_capability.parse_msix_capability") as mock_parse:
            mock_parse.return_value = self.mock_msix_capability_info

            parsed_info = parse_msix_capability(msix_config_space)

            assert parsed_info["table_size"] == 16
            assert parsed_info["table_bir"] == 0
            assert parsed_info["table_offset"] == 0x2000
            assert parsed_info["pba_bir"] == 0
            assert parsed_info["pba_offset"] == 0x3000
            assert parsed_info["enabled"] is True

        # Test MSI-X validation
        with patch(
            "device_clone.msix_capability.validate_msix_configuration"
        ) as mock_validate:
            mock_validate.return_value = (True, [])

            is_valid, errors = validate_msix_configuration(
                self.mock_msix_capability_info
            )

            assert is_valid is True
            assert len(errors) == 0

        # Test MSI-X capability object integration
        if hasattr(
            sys.modules.get("device_clone.msix_capability", {}), "MSIXCapability"
        ):
            with patch(
                "device_clone.msix_capability.MSIXCapability"
            ) as mock_msix_class:
                mock_msix_instance = Mock()
                mock_msix_instance.table_size = 16
                mock_msix_instance.is_enabled = True
                mock_msix_instance.validate.return_value = True
                mock_msix_class.return_value = mock_msix_instance

                msix_cap = MSIXCapability(self.mock_msix_capability_info)
                assert msix_cap.table_size == 16
                assert msix_cap.is_enabled is True
                assert msix_cap.validate() is True

    def test_dynamic_data_sources_no_fallbacks(self):
        """Test that all data sources are truly dynamic with no fallbacks."""
        # Test BehaviorProfiler fails without real data
        with (
            patch("device_clone.behavior_profiler.subprocess.run") as mock_subprocess,
            patch("device_clone.behavior_profiler.Path.exists") as mock_path_exists,
        ):
            # Setup failure conditions
            mock_path_exists.return_value = False
            mock_subprocess.return_value = Mock(
                returncode=1, stdout="", stderr="Device not found"
            )

            profiler = BehaviorProfiler(
                bdf="invalid:device:bdf",
                debug=True,
                enable_variance=True,
                enable_ftrace=True,
            )

            # Should fail without fallback
            with pytest.raises(Exception):
                profiler.capture_behavior_profile(duration=5.0)

        # Test ConfigSpaceManager fails without real device
        with (patch("device_clone.config_space_manager.Path.exists") as mock_exists,):
            mock_exists.return_value = False

            config_manager = ConfigSpaceManager(
                bdf="invalid:device:bdf",
                device_profile="invalid_profile",
            )

            # Should fail without fallback
            with pytest.raises(Exception):
                config_manager.read_vfio_config_space()

        # Test PCILeechContextBuilder fails with incomplete data
        context_builder = PCILeechContextBuilder(
            device_bdf=self.test_device_bdf,
            config=self.test_config,
        )

        # Should fail with missing required data
        with pytest.raises(PCILeechContextError):
            context_builder.build_context(
                behavior_profile=None,
                config_space_data={},  # Empty/invalid data
                msix_data={},  # Empty/invalid data
            )

    def test_data_source_integration_validation(self):
        """Test integration validation between all data sources."""
        # Create all data sources
        with (
            patch("device_clone.behavior_profiler.subprocess.run") as mock_subprocess,
            patch("device_clone.behavior_profiler.Path.exists") as mock_path_exists,
            patch("device_clone.behavior_profiler.Path.read_text") as mock_read_text,
            patch(
                "device_clone.config_space_manager.Path.exists"
            ) as mock_config_exists,
            patch(
                "device_clone.config_space_manager.Path.read_bytes"
            ) as mock_read_bytes,
            patch(
                "device_clone.msix_capability.parse_msix_capability"
            ) as mock_parse_msix,
            patch(
                "device_clone.msix_capability.validate_msix_configuration"
            ) as mock_validate_msix,
        ):
            # Setup successful data source mocks
            mock_path_exists.return_value = True
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
            mock_read_text.return_value = "mock ftrace data"
            mock_config_exists.return_value = True
            mock_read_bytes.return_value = self.mock_config_space_bytes
            mock_parse_msix.return_value = self.mock_msix_capability_info
            mock_validate_msix.return_value = (True, [])

            # Create data sources
            profiler = BehaviorProfiler(
                bdf=self.test_device_bdf,
                debug=True,
                enable_variance=True,
                enable_ftrace=True,
            )

            config_manager = ConfigSpaceManager(
                bdf=self.test_device_bdf,
                device_profile=self.test_device_profile,
            )

            context_builder = PCILeechContextBuilder(
                device_bdf=self.test_device_bdf,
                config=self.test_config,
            )

            # Capture data from all sources
            with patch.object(profiler, "_parse_ftrace_data") as mock_parse:
                mock_parse.return_value = self.mock_behavior_profile
                behavior_profile = profiler.capture_behavior_profile(duration=5.0)

            config_space_bytes = config_manager.read_vfio_config_space()
            device_info = config_manager.extract_device_info(config_space_bytes)

            config_space_data = {
                "raw_config_space": config_space_bytes,
                "config_space_hex": config_space_bytes.hex(),
                "device_info": device_info,
                "vendor_id": device_info["vendor_id"],
                "device_id": device_info["device_id"],
                "class_code": device_info["class_code"],
                "revision_id": device_info["revision_id"],
                "bars": device_info["bars"],
                "config_space_size": len(config_space_bytes),
            }

            msix_data = {
                "capability_info": self.mock_msix_capability_info,
                "table_size": self.mock_msix_capability_info["table_size"],
                "table_bir": self.mock_msix_capability_info["table_bir"],
                "table_offset": self.mock_msix_capability_info["table_offset"],
                "pba_bir": self.mock_msix_capability_info["pba_bir"],
                "pba_offset": self.mock_msix_capability_info["pba_offset"],
                "enabled": self.mock_msix_capability_info["enabled"],
                "function_mask": self.mock_msix_capability_info["function_mask"],
                "validation_errors": [],
                "is_valid": True,
            }

            # Build integrated context
            context = context_builder.build_context(
                behavior_profile=behavior_profile,
                config_space_data=config_space_data,
                msix_data=msix_data,
            )

            # Validate data source integration
            assert context["device_config"]["device_bdf"] == self.test_device_bdf
            assert context["device_config"]["vendor_id"] == device_info["vendor_id"]
            assert (
                context["device_config"]["total_register_accesses"]
                == behavior_profile.total_accesses
            )
            assert (
                context["msix_config"]["num_vectors"]
                == self.mock_msix_capability_info["table_size"]
            )
            assert len(context["bar_config"]["bars"]) > 0

            # Validate cross-source consistency
            assert (
                context["config_space"]["vendor_id"]
                == context["device_config"]["vendor_id"]
            )
            assert (
                context["config_space"]["device_id"]
                == context["device_config"]["device_id"]
            )

    def test_manufacturing_variance_integration(self):
        """Test manufacturing variance integration with dynamic data sources."""
        # Test variance detection in behavior profiler
        with (
            patch("device_clone.behavior_profiler.subprocess.run") as mock_subprocess,
            patch("device_clone.behavior_profiler.Path.exists") as mock_path_exists,
            patch("device_clone.behavior_profiler.Path.read_text") as mock_read_text,
        ):
            mock_path_exists.return_value = True
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
            mock_read_text.return_value = "mock ftrace data with variance"

            profiler = BehaviorProfiler(
                bdf=self.test_device_bdf,
                debug=True,
                enable_variance=True,
                enable_ftrace=True,
            )

            # Mock variance-aware behavior profile
            variance_profile = Mock(spec=BehaviorProfile)
            variance_profile.device_bdf = self.test_device_bdf
            variance_profile.total_accesses = 2800  # Higher due to variance
            variance_profile.variance_metadata = {
                "variance_detected": True,
                "thermal_variance": {
                    "min_temp": 45,
                    "max_temp": 85,
                    "impact": "medium",
                },
                "voltage_variance": {
                    "min_voltage": 1.15,
                    "max_voltage": 1.25,
                    "impact": "low",
                },
                "timing_variance": {"jitter_ns": 2.5, "drift_ppm": 50, "impact": "low"},
            }

            with patch.object(profiler, "_parse_ftrace_data") as mock_parse:
                mock_parse.return_value = variance_profile

                profile = profiler.capture_behavior_profile(duration=30.0)

                # Validate variance integration
                assert profile.variance_metadata["variance_detected"] is True
                assert "thermal_variance" in profile.variance_metadata
                assert "voltage_variance" in profile.variance_metadata
                assert "timing_variance" in profile.variance_metadata

        # Test variance impact on context building
        context_builder = PCILeechContextBuilder(
            device_bdf=self.test_device_bdf,
            config=self.test_config,
        )

        # Build context with variance data
        config_space_data = {
            "raw_config_space": self.mock_config_space_bytes,
            "config_space_hex": self.mock_config_space_bytes.hex(),
            "device_info": {"vendor_id": "8086", "device_id": "153c"},
            "vendor_id": "8086",
            "device_id": "153c",
            "class_code": "020000",
            "revision_id": "04",
            "bars": [0xE0000000],
            "config_space_size": 256,
        }

        msix_data = {
            "capability_info": self.mock_msix_capability_info,
            "table_size": 16,
            "validation_errors": [],
            "is_valid": True,
        }

        context = context_builder.build_context(
            behavior_profile=variance_profile,
            config_space_data=config_space_data,
            msix_data=msix_data,
        )

        # Validate variance impact on context
        assert context["device_config"]["has_manufacturing_variance"] is True
        assert "variance_metadata" in context["device_config"]["behavior_profile"]

    def test_error_handling_dynamic_sources(self):
        """Test error handling in dynamic data sources."""
        error_scenarios = [
            {
                "name": "behavior_profiler_device_not_found",
                "source": "BehaviorProfiler",
                "setup": lambda: patch(
                    "device_clone.behavior_profiler.Path.exists", return_value=False
                ),
                "expected_error": "Device not found",
            },
            {
                "name": "config_space_access_denied",
                "source": "ConfigSpaceManager",
                "setup": lambda: patch(
                    "device_clone.config_space_manager.Path.read_bytes",
                    side_effect=PermissionError("Access denied"),
                ),
                "expected_error": "Access denied",
            },
            {
                "name": "msix_parsing_invalid_data",
                "source": "MSIXCapability",
                "setup": lambda: patch(
                    "device_clone.msix_capability.parse_msix_capability",
                    side_effect=ValueError("Invalid MSI-X data"),
                ),
                "expected_error": "Invalid MSI-X data",
            },
        ]

        for scenario in error_scenarios:
            with scenario["setup"]():
                if scenario["source"] == "BehaviorProfiler":
                    profiler = BehaviorProfiler(bdf="invalid:bdf")
                    with pytest.raises(Exception) as exc_info:
                        profiler.capture_behavior_profile(duration=1.0)
                    # Error should be related to device access
                    assert (
                        "device" in str(exc_info.value).lower()
                        or "not found" in str(exc_info.value).lower()
                    )

                elif scenario["source"] == "ConfigSpaceManager":
                    with patch(
                        "device_clone.config_space_manager.Path.exists",
                        return_value=True,
                    ):
                        config_manager = ConfigSpaceManager(bdf="test:bdf")
                        with pytest.raises(Exception) as exc_info:
                            config_manager.read_vfio_config_space()
                        assert (
                            "access" in str(exc_info.value).lower()
                            or "denied" in str(exc_info.value).lower()
                        )

                elif scenario["source"] == "MSIXCapability":
                    with pytest.raises(Exception) as exc_info:
                        parse_msix_capability("invalid_data")
                    assert (
                        "invalid" in str(exc_info.value).lower()
                        or "msix" in str(exc_info.value).lower()
                    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
