"""
Tests for VFIO binding functionality, specifically for edge cases.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import generate


class TestVFIOBindingEdgeCases:
    """Test VFIO binding edge cases."""

    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_bind_to_vfio_already_bound(self, mock_exists, mock_run, mock_get_driver):
        """Test binding when device is already bound to vfio-pci."""
        # Setup mocks
        mock_exists.return_value = True

        # Test the case where the device is already bound to vfio-pci
        generate.bind_to_vfio("0000:03:00.0", "8086", "1533", "vfio-pci")

        # Verify that no unbind or bind commands were executed
        unbind_call = call(
            "echo 0000:03:00.0 > /sys/bus/pci/devices/0000:03:00.0/driver/unbind"
        )
        bind_call = call("echo 0000:03:00.0 > /sys/bus/pci/drivers/vfio-pci/bind")

        assert unbind_call not in mock_run.call_args_list
        assert bind_call not in mock_run.call_args_list

        # Verify that we still register the device ID with vfio-pci
        register_call = call("echo 8086 1533 > /sys/bus/pci/drivers/vfio-pci/new_id")
        assert register_call not in mock_run.call_args_list  # We should skip this too

    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_bind_to_vfio_bind_error_but_already_bound(
        self, mock_exists, mock_run, mock_get_driver
    ):
        """Test handling of bind error when device is already bound to vfio-pci."""
        # Setup mocks
        mock_exists.return_value = True

        # Make the original driver something other than vfio-pci
        original_driver = "e1000e"

        # Make the bind command fail
        mock_run.side_effect = [
            None,  # First call (new_id) succeeds
            None,  # Second call (unbind) succeeds
            Exception("Device or resource busy"),  # Third call (bind) fails
        ]

        # Make get_current_driver return vfio-pci after the "failed" bind
        mock_get_driver.return_value = "vfio-pci"

        # This should not raise an exception because we check if the device
        # is bound to vfio-pci even if the bind command fails
        generate.bind_to_vfio("0000:03:00.0", "8086", "1533", original_driver)

        # Verify the expected calls were made
        expected_calls = [
            call("echo 8086 1533 > /sys/bus/pci/drivers/vfio-pci/new_id"),
            call("echo 0000:03:00.0 > /sys/bus/pci/devices/0000:03:00.0/driver/unbind"),
            call("echo 0000:03:00.0 > /sys/bus/pci/drivers/vfio-pci/bind"),
        ]

        assert mock_run.call_args_list == expected_calls
        assert mock_get_driver.call_count == 1
