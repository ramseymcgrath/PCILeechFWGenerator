"""
Enhanced tests for VFIO binding functionality with improved error handling and stability.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, call, mock_open, patch

import pytest

import generate

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


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


class TestVFIOBindingEnhanced:
    """Test enhanced VFIO binding functionality."""

    @patch("generate.check_linux_requirement")
    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_validate_vfio_prerequisites_success(
        self, mock_exists, mock_run, mock_get_driver, mock_linux_check
    ):
        """Test successful VFIO prerequisites validation."""

        # Mock all required paths exist
        def exists_side_effect(path):
            return path in [
                "/sys/module/vfio",
                "/sys/module/vfio_pci",
                "/sys/bus/pci/drivers/vfio-pci",
            ]

        mock_exists.side_effect = exists_side_effect
        mock_run.return_value = "IOMMU enabled"

        # Should not raise any exception
        generate._validate_vfio_prerequisites()

    @patch("generate.check_linux_requirement")
    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_validate_vfio_prerequisites_missing_modules(
        self, mock_exists, mock_run, mock_linux_check
    ):
        """Test VFIO prerequisites validation with missing modules."""
        mock_exists.return_value = False

        with pytest.raises(RuntimeError, match="VFIO modules not loaded"):
            generate._validate_vfio_prerequisites()

    @patch("generate.check_linux_requirement")
    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_validate_vfio_prerequisites_missing_driver(
        self, mock_exists, mock_run, mock_linux_check
    ):
        """Test VFIO prerequisites validation with missing driver."""

        def exists_side_effect(path):
            if "vfio-pci" in path:
                return False
            return "/sys/module/vfio" in path

        mock_exists.side_effect = exists_side_effect

        with pytest.raises(RuntimeError, match="vfio-pci driver not available"):
            generate._validate_vfio_prerequisites()

    @patch("generate.check_linux_requirement")
    @patch("generate.run_command")
    def test_check_device_in_use(self, mock_run, mock_linux_check):
        """Test device in use checking."""
        mock_run.return_value = "0000:03:00.0 some process"

        result = generate._check_device_in_use("0000:03:00.0")
        assert result is True

    @patch("generate.check_linux_requirement")
    @patch("generate.run_command")
    def test_check_device_not_in_use(self, mock_run, mock_linux_check):
        """Test device not in use checking."""
        mock_run.return_value = ""

        result = generate._check_device_in_use("0000:03:00.0")
        assert result is False

    @patch("generate.check_linux_requirement")
    @patch("generate.get_current_driver")
    @patch("time.sleep")
    def test_wait_for_device_state_success(
        self, mock_sleep, mock_get_driver, mock_linux_check
    ):
        """Test successful device state waiting."""
        mock_get_driver.return_value = "vfio-pci"

        result = generate._wait_for_device_state("0000:03:00.0", "vfio-pci")
        assert result is True

    @patch("generate.check_linux_requirement")
    @patch("generate.get_current_driver")
    @patch("time.sleep")
    def test_wait_for_device_state_timeout(
        self, mock_sleep, mock_get_driver, mock_linux_check
    ):
        """Test device state waiting timeout."""
        mock_get_driver.return_value = "e1000e"

        result = generate._wait_for_device_state(
            "0000:03:00.0", "vfio-pci", max_retries=2
        )
        assert result is False
        assert mock_sleep.call_count == 1  # Should sleep between retries

    @patch("generate.check_linux_requirement")
    @patch("generate._validate_vfio_prerequisites")
    @patch("generate._check_device_in_use")
    @patch("generate._wait_for_device_state")
    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="8086 1533\n")
    def test_bind_to_vfio_enhanced_success(
        self,
        mock_file,
        mock_exists,
        mock_run,
        mock_get_driver,
        mock_wait,
        mock_check_in_use,
        mock_validate,
        mock_linux_check,
    ):
        """Test enhanced VFIO binding with all improvements."""
        # Setup mocks
        mock_exists.return_value = True
        mock_check_in_use.return_value = False
        mock_wait.return_value = True
        mock_get_driver.return_value = "vfio-pci"

        generate.bind_to_vfio("0000:03:00.0", "8086", "1533", "e1000e")

        # Verify prerequisites were validated
        mock_validate.assert_called_once()

        # Verify device usage was checked
        mock_check_in_use.assert_called_once_with("0000:03:00.0")

        # Verify state waiting was called
        assert mock_wait.call_count >= 1

    @patch("generate.check_linux_requirement")
    @patch("generate._validate_vfio_prerequisites")
    @patch("generate._check_device_in_use")
    @patch("generate._wait_for_device_state")
    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_bind_to_vfio_device_busy_retry(
        self,
        mock_exists,
        mock_run,
        mock_get_driver,
        mock_wait,
        mock_check_in_use,
        mock_validate,
        mock_linux_check,
    ):
        """Test VFIO binding with device busy retry logic."""
        mock_exists.return_value = True
        mock_check_in_use.return_value = False
        mock_validate.return_value = None

        # First bind attempt fails with busy, second succeeds
        mock_run.side_effect = [
            None,  # new_id succeeds
            None,  # unbind succeeds
            subprocess.CalledProcessError(
                1, "bind", "Device or resource busy"
            ),  # bind fails
            None,  # retry bind succeeds
        ]

        # Mock wait states
        mock_wait.side_effect = [True, True]  # unbind wait, bind wait
        mock_get_driver.return_value = "vfio-pci"

        generate.bind_to_vfio("0000:03:00.0", "8086", "1533", "e1000e")

        # Should have retried the bind command
        assert mock_run.call_count == 4

    @patch("generate.check_linux_requirement")
    def test_bind_to_vfio_invalid_vendor_id(self, mock_linux_check):
        """Test VFIO binding with invalid vendor ID."""
        with pytest.raises(ValueError, match="Invalid vendor ID format"):
            generate.bind_to_vfio("0000:03:00.0", "invalid", "1533", "e1000e")

    @patch("generate.check_linux_requirement")
    def test_bind_to_vfio_invalid_device_id(self, mock_linux_check):
        """Test VFIO binding with invalid device ID."""
        with pytest.raises(ValueError, match="Invalid device ID format"):
            generate.bind_to_vfio("0000:03:00.0", "8086", "invalid", "e1000e")

    @patch("generate.check_linux_requirement")
    @patch("generate._validate_vfio_prerequisites")
    @patch("os.path.exists")
    def test_bind_to_vfio_device_not_found(
        self, mock_exists, mock_validate, mock_linux_check
    ):
        """Test VFIO binding when device doesn't exist."""
        mock_validate.return_value = None

        def exists_side_effect(path):
            if "/sys/bus/pci/devices/0000:03:00.0" in path:
                return False
            return True

        mock_exists.side_effect = exists_side_effect

        with pytest.raises(RuntimeError, match="PCIe device .* not found in sysfs"):
            generate.bind_to_vfio("0000:03:00.0", "8086", "1533", "e1000e")

    @patch("generate._wait_for_device_state")
    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_restore_original_driver_enhanced_success(
        self, mock_exists, mock_run, mock_get_driver, mock_wait
    ):
        """Test enhanced driver restoration."""
        mock_exists.return_value = True
        mock_get_driver.side_effect = ["vfio-pci", "e1000e"]  # before and after restore
        mock_wait.side_effect = [True, True]  # unbind wait, bind wait

        generate.restore_original_driver("0000:03:00.0", "e1000e")

        # Should have called unbind and bind
        expected_calls = [
            call(
                "echo 0000:03:00.0 > /sys/bus/pci/drivers/vfio-pci/unbind", timeout=10
            ),
            call("echo 0000:03:00.0 > /sys/bus/pci/drivers/e1000e/bind", timeout=10),
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch("generate._wait_for_device_state")
    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_restore_original_driver_device_disappeared(
        self, mock_exists, mock_run, mock_get_driver, mock_wait
    ):
        """Test driver restoration when device disappears."""

        def exists_side_effect(path):
            if "/sys/bus/pci/devices/0000:03:00.0" in path:
                return False
            return True

        mock_exists.side_effect = exists_side_effect

        # Should return early without error
        generate.restore_original_driver("0000:03:00.0", "e1000e")

        # Should not attempt any driver operations
        mock_run.assert_not_called()

    @patch("generate._wait_for_device_state")
    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_restore_original_driver_retry_logic(
        self, mock_exists, mock_run, mock_get_driver, mock_wait
    ):
        """Test driver restoration retry logic."""
        mock_exists.return_value = True
        mock_get_driver.side_effect = [
            "vfio-pci",
            "vfio-pci",
            "e1000e",
        ]  # still bound, then restored

        # First restore attempt fails, second succeeds
        mock_run.side_effect = [
            None,  # unbind succeeds
            subprocess.CalledProcessError(
                1, "bind", "Device or resource busy"
            ),  # bind fails
            None,  # retry bind succeeds
        ]

        mock_wait.side_effect = [
            True,
            False,
            True,
        ]  # unbind wait, failed bind wait, success bind wait

        generate.restore_original_driver("0000:03:00.0", "e1000e")

        # Should have retried the bind command
        assert mock_run.call_count == 3


class TestVFIOBindingStressTests:
    """Stress tests for VFIO binding under various failure conditions."""

    @patch("generate._validate_vfio_prerequisites")
    @patch("generate._check_device_in_use")
    @patch("generate._wait_for_device_state")
    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    @patch("time.sleep")
    def test_bind_to_vfio_maximum_retries(
        self,
        mock_sleep,
        mock_exists,
        mock_run,
        mock_get_driver,
        mock_wait,
        mock_check_in_use,
        mock_validate,
    ):
        """Test VFIO binding with maximum retry attempts."""
        mock_exists.return_value = True
        mock_check_in_use.return_value = False
        mock_validate.return_value = None

        # All bind attempts fail
        mock_run.side_effect = [
            None,  # new_id succeeds
            None,  # unbind succeeds
            subprocess.CalledProcessError(
                1, "bind", "Device or resource busy"
            ),  # bind fails
            subprocess.CalledProcessError(
                1, "bind", "Device or resource busy"
            ),  # retry 1 fails
            subprocess.CalledProcessError(
                1, "bind", "Device or resource busy"
            ),  # retry 2 fails
        ]

        mock_wait.side_effect = [True]  # unbind wait succeeds
        mock_get_driver.return_value = "e1000e"  # Final check shows not bound

        with pytest.raises(
            RuntimeError, match="Failed to bind to vfio-pci after .* attempts"
        ):
            generate.bind_to_vfio("0000:03:00.0", "8086", "1533", "e1000e")

    @patch("generate._wait_for_device_state")
    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    @patch("time.sleep")
    def test_restore_original_driver_maximum_retries(
        self, mock_sleep, mock_exists, mock_run, mock_get_driver, mock_wait
    ):
        """Test driver restoration with maximum retry attempts."""
        mock_exists.return_value = True
        mock_get_driver.side_effect = ["vfio-pci"] + [
            "vfio-pci"
        ] * 10  # Always bound to vfio-pci

        # All restore attempts fail
        mock_run.side_effect = [
            None,  # unbind succeeds
            subprocess.CalledProcessError(
                1, "bind", "Device or resource busy"
            ),  # bind fails
            subprocess.CalledProcessError(
                1, "bind", "Device or resource busy"
            ),  # retry 1 fails
            subprocess.CalledProcessError(
                1, "bind", "Device or resource busy"
            ),  # retry 2 fails
        ]

        mock_wait.side_effect = [True] + [False] * 10  # unbind succeeds, all binds fail

        with pytest.raises(
            RuntimeError, match="Failed to restore original driver after .* attempts"
        ):
            generate.restore_original_driver("0000:03:00.0", "e1000e")
