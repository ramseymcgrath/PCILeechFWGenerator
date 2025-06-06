"""
Tests for PCI configuration validation functionality.

These tests verify that the validation of PCI configuration values works correctly.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import after path setup
from src import build
from src.donor_dump_manager import DonorDumpManager


class TestPCIValidation:
    """Test PCI configuration validation functionality."""

    def test_validate_donor_info_complete(self):
        """Test validation with complete donor info."""
        # Create a complete donor info dictionary
        complete_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "subvendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "revision_id": "0x03",
            "bar_size": "0x20000",
            "mpc": "0x02",
            "mpr": "0x02",
            "class_code": "020000",
            "extended_config_space": "1",
            "enhanced_caps": "1",
            "dsn_hi": "0x00000000",
            "dsn_lo": "0x00000000",
            "power_mgmt": "0xc823",
            "aer_caps": "0x10001",
            "vendor_caps": "0x0040",
        }

        # Validation should pass without raising exceptions
        result = build.validate_donor_info(complete_info)
        assert result is True

    def test_validate_donor_info_missing_critical(self):
        """Test validation with missing critical fields."""
        # Create an incomplete donor info dictionary missing critical fields
        incomplete_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            # Missing subvendor_id
            # Missing subsystem_id
            "revision_id": "0x03",
            "bar_size": "0x20000",
            "mpc": "0x02",
            # Missing mpr
        }

        # Validation should raise SystemExit
        with pytest.raises(SystemExit):
            build.validate_donor_info(incomplete_info)

    def test_validate_donor_info_missing_extended(self):
        """Test validation with missing extended fields."""
        # Create a donor info dictionary with only critical fields
        basic_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "subvendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "revision_id": "0x03",
            "bar_size": "0x20000",
            "mpc": "0x02",
            "mpr": "0x02",
            # Missing extended fields
        }

        # Validation should pass but return warnings
        result = build.validate_donor_info(basic_info)
        assert result is True

    def test_validate_donor_info_invalid_format(self):
        """Test validation with invalid format fields."""
        # Create a donor info dictionary with invalid format
        invalid_info = {
            "vendor_id": "8086",  # Missing 0x prefix
            "device_id": "0xXYZ",  # Invalid hex
            "subvendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "revision_id": "0x03",
            "bar_size": "0x20000",
            "mpc": "0x02",
            "mpr": "0x02",
            "class_code": "XYZ",  # Invalid class code
        }

        # Validation should pass but return warnings
        result = build.validate_donor_info(invalid_info)
        assert result is False

    @patch("src.build.validate_donor_info")
    def test_get_donor_info_calls_validation(self, mock_validate):
        """Test that get_donor_info calls validate_donor_info."""
        # Mock the validate_donor_info function
        mock_validate.return_value = True

        # Mock the DonorDumpManager
        with patch.object(DonorDumpManager, "setup_module") as mock_setup:
            mock_donor_info = {
                "vendor_id": "0x8086",
                "device_id": "0x1533",
                "subvendor_id": "0x8086",
                "subsystem_id": "0x0000",
                "revision_id": "0x03",
                "bar_size": "0x20000",
                "mpc": "0x02",
                "mpr": "0x02",
            }
            mock_setup.return_value = mock_donor_info

            # Call get_donor_info
            info = build.get_donor_info(bdf="0000:00:00.0")

            # Verify validate_donor_info was called
            mock_validate.assert_called_once_with(mock_donor_info)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
