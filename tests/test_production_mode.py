#!/usr/bin/env python3
"""
Test production mode configuration and mock implementation prevention.
"""

import os

# Import the functions we need to test
import sys
import unittest.mock
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from build import (
    ALLOW_MOCK_DATA,
    PRODUCTION_MODE,
    integrate_behavior_profile,
    scrape_driver_regs,
    validate_production_mode,
)


class TestProductionMode:
    """Test production mode configuration and validation."""

    def test_validate_production_mode_strict(self):
        """Test strict production mode validation."""
        with (
            patch("build.PRODUCTION_MODE", True),
            patch("build.ALLOW_MOCK_DATA", False),
        ):
            # Should not raise any exception
            validate_production_mode()

    def test_validate_production_mode_development(self):
        """Test development mode validation."""
        with (
            patch("build.PRODUCTION_MODE", False),
            patch("build.ALLOW_MOCK_DATA", True),
        ):
            # Should not raise any exception
            validate_production_mode()

    def test_validate_production_mode_invalid_config(self):
        """Test invalid production mode configuration."""
        with patch("build.PRODUCTION_MODE", True), patch("build.ALLOW_MOCK_DATA", True):
            # Should raise RuntimeError for invalid config
            with pytest.raises(
                RuntimeError,
                match="CRITICAL: Production mode is enabled but mock data is allowed",
            ):
                validate_production_mode()

    @patch("build.validate_hex_id")
    @patch("build.resolve_driver_module")
    @patch("build.ensure_kernel_source")
    @patch("build.find_driver_sources")
    @patch("build.extract_registers_with_analysis")
    def test_scrape_driver_regs_production_mode(
        self,
        mock_extract,
        mock_find_sources,
        mock_ensure_kernel,
        mock_resolve_driver,
        mock_validate_hex,
    ):
        """Test driver register scraping in production mode."""
        # Setup mocks for successful production mode execution
        mock_validate_hex.side_effect = lambda x, y: x.lower()
        mock_resolve_driver.return_value = "test_driver"
        mock_ensure_kernel.return_value = "/usr/src/linux-source"
        mock_find_sources.return_value = ["/path/to/driver.c"]
        mock_extract.return_value = {
            "driver_module": "test_driver",
            "registers": [
                {"name": "TEST_REG", "offset": "0x100", "value": "0x0", "rw": "rw"}
            ],
        }

        with (
            patch("build.PRODUCTION_MODE", True),
            patch("build.ALLOW_MOCK_DATA", False),
        ):

            registers, state_machine = scrape_driver_regs("8086", "1533")

            # Verify real implementation was called
            mock_validate_hex.assert_called()
            mock_resolve_driver.assert_called_with("8086", "1533")
            mock_ensure_kernel.assert_called_once()
            mock_find_sources.assert_called_once()
            mock_extract.assert_called_once()

            # Verify results
            assert len(registers) == 1
            assert registers[0]["name"] == "TEST_REG"
            assert isinstance(state_machine, dict)

    def test_scrape_driver_regs_development_mode(self):
        """Test driver register scraping in development mode with mock data."""
        with (
            patch("build.PRODUCTION_MODE", False),
            patch("build.ALLOW_MOCK_DATA", True),
        ):

            registers, state_machine = scrape_driver_regs("8086", "1533")

            # Verify mock data is returned
            assert len(registers) == 3  # Mock data has 3 registers
            assert registers[0]["name"] == "CTRL"
            assert registers[1]["name"] == "STATUS"
            assert registers[2]["name"] == "CONFIG"
            assert isinstance(state_machine, dict)
            assert "states" in state_machine

    @patch("build.BehaviorProfiler")
    def test_integrate_behavior_profile_production_mode(self, mock_profiler_class):
        """Test behavior profiling in production mode."""
        # Setup mock behavior profiler
        mock_profiler = MagicMock()
        mock_profiler_class.return_value = mock_profiler

        mock_profile = MagicMock()
        mock_profile.register_accesses = [
            MagicMock(
                register="TEST_REG", offset=0x100, operation="read", duration_us=0.1
            )
        ]
        mock_profile.timing_patterns = [
            MagicMock(registers=["TEST_REG"], frequency_hz=1000)
        ]
        mock_profiler.capture_behavior_profile.return_value = mock_profile

        test_registers = [
            {"name": "TEST_REG", "offset": 0x100, "value": 0x0, "access": "RW"}
        ]

        with (
            patch("build.PRODUCTION_MODE", True),
            patch("build.ALLOW_MOCK_DATA", False),
        ):

            enhanced_registers = integrate_behavior_profile(
                "0000:03:00.0", test_registers, 30.0
            )

            # Verify real profiler was used
            mock_profiler_class.assert_called_with(bdf="0000:03:00.0")
            mock_profiler.capture_behavior_profile.assert_called_with(duration=30.0)

            # Verify enhanced data
            assert len(enhanced_registers) == 1
            assert "timing" in enhanced_registers[0]
            assert "behavior_confidence" in enhanced_registers[0]

    def test_integrate_behavior_profile_development_mode(self):
        """Test behavior profiling in development mode with mock data."""
        test_registers = [
            {"name": "TEST_REG", "offset": 0x100, "value": 0x0, "access": "RW"}
        ]

        with (
            patch("build.PRODUCTION_MODE", False),
            patch("build.ALLOW_MOCK_DATA", True),
        ):

            enhanced_registers = integrate_behavior_profile(
                "0000:03:00.0", test_registers, 30.0
            )

            # Verify mock data is used
            assert len(enhanced_registers) == 1
            assert "timing" in enhanced_registers[0]
            assert enhanced_registers[0]["timing"]["read_latency"] == 100
            assert enhanced_registers[0]["timing"]["write_latency"] == 150
            assert (
                enhanced_registers[0]["behavior_confidence"] == 0.5
            )  # Lower confidence for mock

    @patch("build.resolve_driver_module")
    def test_scrape_driver_regs_production_failure(self, mock_resolve_driver):
        """Test production mode failure when driver resolution fails."""
        mock_resolve_driver.side_effect = RuntimeError("No driver found")

        with (
            patch("build.PRODUCTION_MODE", True),
            patch("build.ALLOW_MOCK_DATA", False),
        ):

            with pytest.raises(RuntimeError, match="Production build failed"):
                scrape_driver_regs("8086", "1533")

    @patch("build.BehaviorProfiler")
    def test_integrate_behavior_profile_production_failure(self, mock_profiler_class):
        """Test production mode failure when behavior profiling fails."""
        mock_profiler_class.side_effect = RuntimeError("Profiler unavailable")

        test_registers = [
            {"name": "TEST_REG", "offset": 0x100, "value": 0x0, "access": "RW"}
        ]

        with (
            patch("build.PRODUCTION_MODE", True),
            patch("build.ALLOW_MOCK_DATA", False),
        ):

            with pytest.raises(RuntimeError, match="Production build failed"):
                integrate_behavior_profile("0000:03:00.0", test_registers, 30.0)


class TestEnvironmentVariables:
    """Test environment variable configuration."""

    def test_production_mode_env_var_true(self):
        """Test PCILEECH_PRODUCTION_MODE=true."""
        with patch.dict(os.environ, {"PCILEECH_PRODUCTION_MODE": "true"}):
            # Re-import to pick up environment variable
            import importlib

            import build

            importlib.reload(build)
            assert build.PRODUCTION_MODE is True

    def test_production_mode_env_var_false(self):
        """Test PCILEECH_PRODUCTION_MODE=false."""
        with patch.dict(os.environ, {"PCILEECH_PRODUCTION_MODE": "false"}):
            import importlib

            import build

            importlib.reload(build)
            assert build.PRODUCTION_MODE is False

    def test_allow_mock_data_env_var_false(self):
        """Test PCILEECH_ALLOW_MOCK_DATA=false."""
        with patch.dict(os.environ, {"PCILEECH_ALLOW_MOCK_DATA": "false"}):
            import importlib

            import build

            importlib.reload(build)
            assert build.ALLOW_MOCK_DATA is False

    def test_allow_mock_data_env_var_true(self):
        """Test PCILEECH_ALLOW_MOCK_DATA=true."""
        with patch.dict(os.environ, {"PCILEECH_ALLOW_MOCK_DATA": "true"}):
            import importlib

            import build

            importlib.reload(build)
            assert build.ALLOW_MOCK_DATA is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
