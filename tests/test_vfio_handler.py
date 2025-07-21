#!/usr/bin/env python3
"""Comprehensive unit tests for the VFIO handler module.

This test suite covers all critical functionality of the vfio_handler module,
including device binding, error handling, security boundaries, and state management.
"""

import errno
import fcntl
import json
import os
import struct
import time
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, PropertyMock, call, mock_open, patch

import pytest

# Import the module under test
from src.cli.vfio_handler import (
    BindingState,
    DeviceInfo,
    VFIOBinder,
    VFIOBinderImpl,
    VFIOBindError,
    VFIODeviceNotFoundError,
    VFIOGroupError,
    VFIOPathManager,
    VFIOPermissionError,
    _get_current_driver,
    _get_iommu_group,
    _get_iommu_group_safe,
    render_pretty,
    run_diagnostics,
)


# Test fixtures
@pytest.fixture
def valid_bdf():
    """Provide a valid BDF identifier."""
    return "0000:01:00.0"


@pytest.fixture
def invalid_bdf():
    """Provide an invalid BDF identifier."""
    return "invalid:bdf"


@pytest.fixture
def mock_path_manager(valid_bdf):
    """Create a mock VFIOPathManager."""
    manager = VFIOPathManager(valid_bdf)
    return manager


@pytest.fixture
def mock_device_info(valid_bdf):
    """Create a mock DeviceInfo object."""
    return DeviceInfo(
        bdf=valid_bdf,
        current_driver="some_driver",
        iommu_group="42",
        binding_state=BindingState.BOUND_TO_OTHER,
    )


@pytest.fixture
def mock_vfio_device_info(valid_bdf):
    """Create a mock DeviceInfo object bound to VFIO."""
    return DeviceInfo(
        bdf=valid_bdf,
        current_driver="vfio-pci",
        iommu_group="42",
        binding_state=BindingState.BOUND_TO_VFIO,
    )


class TestVFIOPathManager:
    """Test cases for VFIOPathManager class."""

    def test_initialization(self, valid_bdf):
        """Test VFIOPathManager initialization."""
        manager = VFIOPathManager(valid_bdf)
        assert manager.bdf == valid_bdf
        assert manager.device_path == Path(f"/sys/bus/pci/devices/{valid_bdf}")
        assert manager.driver_link == Path(f"/sys/bus/pci/devices/{valid_bdf}/driver")
        assert manager.driver_override_path == Path(
            f"/sys/bus/pci/devices/{valid_bdf}/driver_override"
        )
        assert manager.iommu_group_link == Path(
            f"/sys/bus/pci/devices/{valid_bdf}/iommu_group"
        )

    def test_get_driver_unbind_path(self, mock_path_manager):
        """Test getting driver unbind path."""
        driver_name = "test_driver"
        expected_path = Path(f"/sys/bus/pci/drivers/{driver_name}/unbind")
        assert mock_path_manager.get_driver_unbind_path(driver_name) == expected_path

    def test_get_driver_bind_path(self, mock_path_manager):
        """Test getting driver bind path."""
        driver_name = "vfio-pci"
        expected_path = Path(f"/sys/bus/pci/drivers/{driver_name}/bind")
        assert mock_path_manager.get_driver_bind_path(driver_name) == expected_path

    def test_get_vfio_group_path(self, mock_path_manager):
        """Test getting VFIO group path."""
        group_id = "42"
        expected_path = Path(f"/dev/vfio/{group_id}")
        assert mock_path_manager.get_vfio_group_path(group_id) == expected_path


class TestDeviceInfo:
    """Test cases for DeviceInfo dataclass."""

    @patch("src.cli.vfio_handler._get_current_driver")
    @patch("src.cli.vfio_handler._get_iommu_group_safe")
    def test_from_bdf_unbound(self, mock_get_iommu, mock_get_driver, valid_bdf):
        """Test DeviceInfo creation for unbound device."""
        mock_get_driver.return_value = None
        mock_get_iommu.return_value = "42"

        device_info = DeviceInfo.from_bdf(valid_bdf)

        assert device_info.bdf == valid_bdf
        assert device_info.current_driver is None
        assert device_info.iommu_group == "42"
        assert device_info.binding_state == BindingState.UNBOUND

    @patch("src.cli.vfio_handler._get_current_driver")
    @patch("src.cli.vfio_handler._get_iommu_group_safe")
    def test_from_bdf_bound_to_vfio(self, mock_get_iommu, mock_get_driver, valid_bdf):
        """Test DeviceInfo creation for VFIO-bound device."""
        mock_get_driver.return_value = "vfio-pci"
        mock_get_iommu.return_value = "42"

        device_info = DeviceInfo.from_bdf(valid_bdf)

        assert device_info.bdf == valid_bdf
        assert device_info.current_driver == "vfio-pci"
        assert device_info.iommu_group == "42"
        assert device_info.binding_state == BindingState.BOUND_TO_VFIO

    @patch("src.cli.vfio_handler._get_current_driver")
    @patch("src.cli.vfio_handler._get_iommu_group_safe")
    def test_from_bdf_bound_to_other(self, mock_get_iommu, mock_get_driver, valid_bdf):
        """Test DeviceInfo creation for device bound to other driver."""
        mock_get_driver.return_value = "nvidia"
        mock_get_iommu.return_value = "42"

        device_info = DeviceInfo.from_bdf(valid_bdf)

        assert device_info.bdf == valid_bdf
        assert device_info.current_driver == "nvidia"
        assert device_info.iommu_group == "42"
        assert device_info.binding_state == BindingState.BOUND_TO_OTHER


class TestVFIOBinderImpl:
    """Test cases for VFIOBinderImpl class."""

    @patch("os.geteuid", return_value=0)
    def test_initialization_valid(self, mock_geteuid, valid_bdf):
        """Test successful VFIOBinderImpl initialization."""
        binder = VFIOBinderImpl(valid_bdf)
        assert binder.bdf == valid_bdf
        assert binder.original_driver is None
        assert binder.group_id is None
        assert binder._bound is False
        assert binder._attach is True

    @patch("os.geteuid", return_value=1000)
    def test_initialization_permission_error(self, mock_geteuid, valid_bdf):
        """Test VFIOBinderImpl initialization without root privileges."""
        with pytest.raises(VFIOPermissionError, match="root privileges"):
            VFIOBinderImpl(valid_bdf)

    @patch("os.geteuid", return_value=0)
    def test_initialization_invalid_bdf(self, mock_geteuid, invalid_bdf):
        """Test VFIOBinderImpl initialization with invalid BDF."""
        with pytest.raises(ValueError, match="Invalid BDF format"):
            VFIOBinderImpl(invalid_bdf)

    @patch("os.geteuid", return_value=0)
    def test_validate_bdf_patterns(self, mock_geteuid):
        """Test BDF validation with various patterns."""
        # Valid patterns
        valid_patterns = [
            "0000:01:00.0",  # Full domain
            "00:01:00.0",  # Short domain
            "0000:ff:1f.7",  # Max values
            "01:00.0",  # Minimal format
        ]

        for bdf in valid_patterns:
            binder = VFIOBinderImpl(bdf)  # Should not raise
            assert binder.bdf == bdf

        # Invalid patterns
        invalid_patterns = [
            "00000:01:00.0",  # Domain too long
            "0:01:00.0",  # Domain too short
            "0000:1:00.0",  # Bus too short
            "0000:01:0.0",  # Device too short
            "0000:01:00.8",  # Function out of range
            "0000:01:00",  # Missing function
            "not-a-bdf",  # Completely invalid
        ]

        for bdf in invalid_patterns:
            with pytest.raises(ValueError, match="Invalid BDF format"):
                VFIOBinderImpl(bdf)

    @patch("os.geteuid", return_value=0)
    def test_write_sysfs_safe_success(self, mock_geteuid, valid_bdf, tmp_path):
        """Test successful sysfs write operation."""
        binder = VFIOBinderImpl(valid_bdf)
        test_file = tmp_path / "test_sysfs"
        test_file.touch()

        binder._write_sysfs_safe(test_file, "test_value")
        assert test_file.read_text() == "test_value"

    @patch("os.geteuid", return_value=0)
    def test_write_sysfs_safe_nonexistent(self, mock_geteuid, valid_bdf, tmp_path):
        """Test sysfs write to non-existent file."""
        binder = VFIOBinderImpl(valid_bdf)
        test_file = tmp_path / "nonexistent"

        with pytest.raises(VFIOBindError, match="does not exist"):
            binder._write_sysfs_safe(test_file, "test_value")

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.write_text", side_effect=PermissionError("Permission denied"))
    def test_write_sysfs_safe_permission_error(
        self, mock_write, mock_exists, mock_geteuid, valid_bdf
    ):
        """Test sysfs write with permission error."""
        binder = VFIOBinderImpl(valid_bdf)
        test_path = Path("/sys/test")

        with pytest.raises(VFIOPermissionError, match="Permission denied"):
            binder._write_sysfs_safe(test_path, "test_value")

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.write_text", side_effect=OSError("Generic OS error"))
    def test_write_sysfs_safe_os_error(
        self, mock_write, mock_exists, mock_geteuid, valid_bdf
    ):
        """Test sysfs write with generic OS error."""
        binder = VFIOBinderImpl(valid_bdf)
        test_path = Path("/sys/test")

        with pytest.raises(VFIOBindError, match="Failed to write"):
            binder._write_sysfs_safe(test_path, "test_value")

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler._get_current_driver")
    @patch("time.sleep")
    def test_wait_for_state_change_success(
        self, mock_sleep, mock_get_driver, mock_geteuid, valid_bdf
    ):
        """Test successful state change wait."""
        binder = VFIOBinderImpl(valid_bdf)
        mock_get_driver.side_effect = ["old_driver", "old_driver", "vfio-pci"]

        result = binder._wait_for_state_change("vfio-pci", timeout=1.0)
        assert result is True
        assert mock_get_driver.call_count == 3

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler._get_current_driver", return_value="old_driver")
    @patch("time.time", side_effect=[0, 0.5, 1.0, 2.1])
    @patch("time.sleep")
    def test_wait_for_state_change_timeout(
        self, mock_sleep, mock_time, mock_get_driver, mock_geteuid, valid_bdf
    ):
        """Test state change wait timeout."""
        binder = VFIOBinderImpl(valid_bdf)

        result = binder._wait_for_state_change("vfio-pci", timeout=2.0)
        assert result is False

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._write_sysfs_safe")
    @patch(
        "src.cli.vfio_handler.VFIOBinderImpl._wait_for_state_change", return_value=True
    )
    @patch("time.sleep")
    def test_unbind_current_driver_success(
        self,
        mock_sleep,
        mock_wait,
        mock_write,
        mock_exists,
        mock_geteuid,
        valid_bdf,
        mock_device_info,
    ):
        """Test successful driver unbinding."""
        binder = VFIOBinderImpl(valid_bdf)
        binder._unbind_current_driver(mock_device_info)

        mock_write.assert_called_once()
        mock_wait.assert_called_once_with(None, timeout=2.0)
        mock_sleep.assert_called_once_with(0.2)

    @patch("os.geteuid", return_value=0)
    def test_unbind_current_driver_no_driver(self, mock_geteuid, valid_bdf):
        """Test unbinding when no driver is bound."""
        binder = VFIOBinderImpl(valid_bdf)
        device_info = DeviceInfo(
            bdf=valid_bdf,
            current_driver=None,
            iommu_group="42",
            binding_state=BindingState.UNBOUND,
        )

        # Should return without doing anything
        binder._unbind_current_driver(device_info)

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists", return_value=True)
    @patch(
        "src.cli.vfio_handler.VFIOBinderImpl._write_sysfs_safe",
        side_effect=Exception("Write failed"),
    )
    @patch("time.sleep")
    def test_unbind_current_driver_failure(
        self,
        mock_sleep,
        mock_write,
        mock_exists,
        mock_geteuid,
        valid_bdf,
        mock_device_info,
    ):
        """Test driver unbinding failure handling."""
        binder = VFIOBinderImpl(valid_bdf)

        # Should not raise, just log warning
        binder._unbind_current_driver(mock_device_info)
        mock_write.assert_called_once()

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._write_sysfs_safe")
    @patch(
        "src.cli.vfio_handler.VFIOBinderImpl._wait_for_state_change", return_value=True
    )
    @patch("time.sleep")
    def test_perform_vfio_binding_success(
        self, mock_sleep, mock_wait, mock_write, mock_geteuid, valid_bdf
    ):
        """Test successful VFIO binding."""
        binder = VFIOBinderImpl(valid_bdf)
        binder._perform_vfio_binding()

        # Should write driver_override and bind
        assert mock_write.call_count == 2
        mock_wait.assert_called_once_with("vfio-pci", timeout=3.0)

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._write_sysfs_safe")
    @patch(
        "src.cli.vfio_handler.VFIOBinderImpl._wait_for_state_change", return_value=False
    )
    @patch("time.sleep")
    def test_perform_vfio_binding_timeout(
        self, mock_sleep, mock_wait, mock_write, mock_geteuid, valid_bdf
    ):
        """Test VFIO binding timeout."""
        binder = VFIOBinderImpl(valid_bdf)

        with pytest.raises(VFIOBindError, match="timed out"):
            binder._perform_vfio_binding()

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._get_device_info")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._verify_vfio_binding")
    def test_bind_to_vfio_already_bound(
        self, mock_verify, mock_get_info, mock_geteuid, valid_bdf, mock_vfio_device_info
    ):
        """Test binding when already bound to VFIO."""
        binder = VFIOBinderImpl(valid_bdf)
        mock_get_info.return_value = mock_vfio_device_info

        binder._bind_to_vfio()

        mock_verify.assert_called_once()
        assert not binder._bound  # Should not set _bound when already bound

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._get_device_info")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._unbind_current_driver")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._perform_vfio_binding")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._verify_vfio_binding")
    def test_bind_to_vfio_full_flow(
        self,
        mock_verify,
        mock_perform,
        mock_unbind,
        mock_get_info,
        mock_geteuid,
        valid_bdf,
        mock_device_info,
        mock_vfio_device_info,
    ):
        """Test complete VFIO binding flow."""
        binder = VFIOBinderImpl(valid_bdf)
        mock_get_info.side_effect = [mock_device_info, mock_vfio_device_info]

        binder._bind_to_vfio()

        mock_unbind.assert_called_once_with(mock_device_info)
        mock_perform.assert_called_once()
        mock_verify.assert_called_once()
        assert binder._bound is True
        assert binder.original_driver == "some_driver"

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler._get_iommu_group", return_value="42")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("os.access", return_value=True)
    def test_verify_vfio_binding_success(
        self, mock_access, mock_exists, mock_get_group, mock_geteuid, valid_bdf
    ):
        """Test successful VFIO binding verification."""
        binder = VFIOBinderImpl(valid_bdf)
        binder._verify_vfio_binding()

        assert binder.group_id == "42"
        mock_access.assert_called_once()

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler._get_iommu_group", return_value="42")
    @patch("pathlib.Path.exists", return_value=False)
    def test_verify_vfio_binding_no_group_device(
        self, mock_exists, mock_get_group, mock_geteuid, valid_bdf
    ):
        """Test VFIO verification when group device doesn't exist."""
        binder = VFIOBinderImpl(valid_bdf)

        with pytest.raises(VFIOBindError, match="verification failed"):
            binder._verify_vfio_binding()

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler._get_iommu_group", return_value="42")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("os.access", return_value=False)
    def test_verify_vfio_binding_no_access(
        self, mock_access, mock_exists, mock_get_group, mock_geteuid, valid_bdf
    ):
        """Test VFIO verification when group device is not accessible."""
        binder = VFIOBinderImpl(valid_bdf)

        with pytest.raises(VFIOBindError, match="verification failed"):
            binder._verify_vfio_binding()

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists")
    @patch("time.sleep")
    @patch("time.time", side_effect=[0, 0.1, 0.3, 0.7, 1.5])
    def test_wait_for_group_node_success(
        self, mock_time, mock_sleep, mock_exists, mock_geteuid, valid_bdf
    ):
        """Test successful group node wait with backoff."""
        binder = VFIOBinderImpl(valid_bdf)
        binder.group_id = "42"
        mock_exists.side_effect = [False, False, False, True]

        result = binder._wait_for_group_node()

        assert result == Path("/dev/vfio/42")
        assert mock_sleep.call_count == 3
        # Check exponential backoff
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls == [0.1, 0.2, 0.4]

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists", return_value=False)
    @patch("time.sleep")
    @patch("time.time", side_effect=lambda: time.time())
    def test_wait_for_group_node_timeout(
        self, mock_time, mock_sleep, mock_exists, mock_geteuid, valid_bdf
    ):
        """Test group node wait timeout."""
        binder = VFIOBinderImpl(valid_bdf)
        binder.group_id = "42"

        with patch("src.cli.vfio_handler.MAX_GROUP_WAIT_TIME", 0.5):
            with pytest.raises(VFIOGroupError, match="did not appear"):
                binder._wait_for_group_node()

    @patch("os.geteuid", return_value=0)
    def test_wait_for_group_node_no_group_id(self, mock_geteuid, valid_bdf):
        """Test group node wait without group ID."""
        binder = VFIOBinderImpl(valid_bdf)

        with pytest.raises(VFIOGroupError, match="No group ID"):
            binder._wait_for_group_node()

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._write_sysfs_safe")
    def test_restore_original_driver_success(
        self, mock_write, mock_exists, mock_geteuid, valid_bdf
    ):
        """Test successful original driver restoration."""
        binder = VFIOBinderImpl(valid_bdf)
        binder.original_driver = "nvidia"

        binder._restore_original_driver()

        mock_write.assert_called_once()

    @patch("os.geteuid", return_value=0)
    def test_restore_original_driver_no_driver(self, mock_geteuid, valid_bdf):
        """Test restoration when no original driver."""
        binder = VFIOBinderImpl(valid_bdf)
        binder.original_driver = None

        # Should return without doing anything
        binder._restore_original_driver()

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists", return_value=True)
    @patch(
        "src.cli.vfio_handler.VFIOBinderImpl._write_sysfs_safe",
        side_effect=Exception("Write failed"),
    )
    def test_restore_original_driver_failure(
        self, mock_write, mock_exists, mock_geteuid, valid_bdf
    ):
        """Test original driver restoration failure."""
        binder = VFIOBinderImpl(valid_bdf)
        binder.original_driver = "nvidia"

        # Should not raise, just log warning
        binder._restore_original_driver()
        mock_write.assert_called_once()

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._get_device_info")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._write_sysfs_safe")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._wait_for_state_change")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._restore_original_driver")
    def test_cleanup_success(
        self,
        mock_restore,
        mock_wait,
        mock_write,
        mock_get_info,
        mock_exists,
        mock_geteuid,
        valid_bdf,
        mock_vfio_device_info,
    ):
        """Test successful cleanup."""
        binder = VFIOBinderImpl(valid_bdf)
        binder._bound = True
        mock_get_info.return_value = mock_vfio_device_info

        binder._cleanup()

        mock_write.assert_any_call(
            Path("/sys/bus/pci/drivers/vfio-pci/unbind"), valid_bdf
        )
        mock_write.assert_any_call(binder._path_manager.driver_override_path, "")
        mock_restore.assert_called_once()

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists", return_value=False)
    def test_cleanup_device_removed(self, mock_exists, mock_geteuid, valid_bdf):
        """Test cleanup when device no longer exists."""
        binder = VFIOBinderImpl(valid_bdf)
        binder._bound = True

        binder._cleanup()
        # Should return early without errors

    @patch("os.geteuid", return_value=0)
    def test_cleanup_not_bound(self, mock_geteuid, valid_bdf):
        """Test cleanup when not bound."""
        binder = VFIOBinderImpl(valid_bdf)
        binder._bound = False

        binder._cleanup()
        # Should return early

    @patch("os.geteuid", return_value=0)
    def test_open_vfio_device_fd_attach_disabled(self, mock_geteuid, valid_bdf):
        """Test opening device FD when attach is disabled."""
        binder = VFIOBinderImpl(valid_bdf, attach=False)

        with pytest.raises(RuntimeError, match="Device-FD opening disabled"):
            binder._open_vfio_device_fd()

    @patch("os.geteuid", return_value=0)
    def test_open_vfio_device_fd_no_group_id(self, mock_geteuid, valid_bdf):
        """Test opening device FD without group ID."""
        binder = VFIOBinderImpl(valid_bdf)

        with pytest.raises(VFIOGroupError, match="No group ID"):
            binder._open_vfio_device_fd()

    @patch("os.geteuid", return_value=0)
    @patch("os.open", side_effect=[100, 101])  # container_fd, group_fd
    @patch("os.close")
    @patch("fcntl.ioctl")
    def test_open_vfio_device_fd_success(
        self, mock_ioctl, mock_close, mock_open, mock_geteuid, valid_bdf
    ):
        """Test successful device FD opening."""
        binder = VFIOBinderImpl(valid_bdf)
        binder.group_id = "42"

        # Mock ioctl to return device_fd
        mock_ioctl.side_effect = [
            None,
            None,
            102,
        ]  # SET_CONTAINER, SET_IOMMU, GET_DEVICE_FD

        device_fd, container_fd = binder._open_vfio_device_fd()

        assert device_fd == 102
        assert container_fd == 100
        mock_close.assert_called_once_with(101)  # group_fd should be closed

    @patch("os.geteuid", return_value=0)
    @patch("os.open", side_effect=[100, 101])
    @patch("fcntl.ioctl", side_effect=OSError(errno.EINVAL, "Invalid argument"))
    def test_open_vfio_device_fd_einval(
        self, mock_ioctl, mock_open, mock_geteuid, valid_bdf
    ):
        """Test device FD opening with EINVAL error."""
        binder = VFIOBinderImpl(valid_bdf)
        binder.group_id = "42"

        with pytest.raises(VFIOBindError, match="Failed to open VFIO device FD"):
            binder._open_vfio_device_fd()

    @patch("os.geteuid", return_value=0)
    @patch("os.open", side_effect=[100, 101])
    @patch("fcntl.ioctl", side_effect=OSError(errno.EBUSY, "Device busy"))
    def test_open_vfio_device_fd_ebusy(
        self, mock_ioctl, mock_open, mock_geteuid, valid_bdf
    ):
        """Test device FD opening with EBUSY error."""
        binder = VFIOBinderImpl(valid_bdf)
        binder.group_id = "42"

        with pytest.raises(VFIOBindError, match="Failed to open VFIO device FD"):
            binder._open_vfio_device_fd()

    @patch("os.geteuid", return_value=0)
    def test_get_vfio_region_info_disabled(self, mock_geteuid, valid_bdf):
        """Test that region info query is disabled."""
        binder = VFIOBinderImpl(valid_bdf)

        result = binder._get_vfio_region_info(0)
        assert result is None

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._bind_to_vfio")
    def test_rebind(self, mock_bind, mock_geteuid, valid_bdf):
        """Test manual rebind."""
        binder = VFIOBinderImpl(valid_bdf)
        binder._bound = False

        binder.rebind()

        mock_bind.assert_called_once()

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._bind_to_vfio")
    def test_rebind_already_bound(self, mock_bind, mock_geteuid, valid_bdf):
        """Test rebind when already bound."""
        binder = VFIOBinderImpl(valid_bdf)
        binder._bound = True

        binder.rebind()

        mock_bind.assert_not_called()

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._cleanup")
    def test_close(self, mock_cleanup, mock_geteuid, valid_bdf):
        """Test manual close."""
        binder = VFIOBinderImpl(valid_bdf)
        binder._bound = True

        binder.close()

        mock_cleanup.assert_called_once()
        assert binder._bound is False

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler._get_iommu_group", return_value="42")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._bind_to_vfio")
    @patch(
        "src.cli.vfio_handler.VFIOBinderImpl._open_vfio_device_fd",
        return_value=(100, 101),
    )
    @patch("os.close")
    def test_context_manager_enter_with_attach(
        self,
        mock_close,
        mock_open_fd,
        mock_bind,
        mock_get_group,
        mock_geteuid,
        valid_bdf,
    ):
        """Test context manager __enter__ with attach enabled."""
        binder = VFIOBinderImpl(valid_bdf, attach=True)

        result = binder.__enter__()

        assert result == Path("/dev/vfio/42")
        assert binder.group_id == "42"
        mock_bind.assert_called_once()
        mock_open_fd.assert_called_once()
        assert mock_close.call_count == 2  # Both fds should be closed

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler._get_iommu_group", return_value="42")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._bind_to_vfio")
    def test_context_manager_enter_without_attach(
        self, mock_bind, mock_get_group, mock_geteuid, valid_bdf
    ):
        """Test context manager __enter__ with attach disabled."""
        binder = VFIOBinderImpl(valid_bdf, attach=False)

        result = binder.__enter__()

        assert result == Path("/dev/vfio/42")
        assert binder.group_id == "42"
        mock_bind.assert_called_once()

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._cleanup")
    def test_context_manager_exit(self, mock_cleanup, mock_geteuid, valid_bdf):
        """Test context manager __exit__."""
        binder = VFIOBinderImpl(valid_bdf)

        binder.__exit__(None, None, None)

        mock_cleanup.assert_called_once()


class TestHelperFunctions:
    """Test cases for module-level helper functions."""

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_symlink", return_value=True)
    @patch("pathlib.Path.resolve")
    def test_get_current_driver_success(
        self, mock_resolve, mock_is_symlink, mock_exists, valid_bdf
    ):
        """Test getting current driver successfully."""
        mock_path = Mock()
        mock_path.name = "vfio-pci"
        mock_resolve.return_value = mock_path

        result = _get_current_driver(valid_bdf)

        assert result == "vfio-pci"

    @patch("pathlib.Path.exists", return_value=False)
    def test_get_current_driver_no_link(self, mock_exists, valid_bdf):
        """Test getting current driver when link doesn't exist."""
        result = _get_current_driver(valid_bdf)
        assert result is None

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_symlink", return_value=False)
    def test_get_current_driver_not_symlink(
        self, mock_is_symlink, mock_exists, valid_bdf
    ):
        """Test getting current driver when path is not a symlink."""
        result = _get_current_driver(valid_bdf)
        assert result is None

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_symlink", return_value=True)
    @patch("pathlib.Path.resolve", side_effect=OSError("Permission denied"))
    def test_get_current_driver_permission_error(
        self, mock_resolve, mock_is_symlink, mock_exists, valid_bdf
    ):
        """Test getting current driver with permission error."""
        result = _get_current_driver(valid_bdf)
        assert result is None

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.resolve")
    def test_get_iommu_group_success(self, mock_resolve, mock_exists, valid_bdf):
        """Test getting IOMMU group successfully."""
        mock_path = Mock()
        mock_path.name = "42"
        mock_resolve.return_value = mock_path

        result = _get_iommu_group(valid_bdf)

        assert result == "42"

    @patch("pathlib.Path.exists", return_value=False)
    def test_get_iommu_group_not_found(self, mock_exists, valid_bdf):
        """Test getting IOMMU group when not found."""
        with pytest.raises(VFIODeviceNotFoundError, match="No IOMMU group found"):
            _get_iommu_group(valid_bdf)

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.resolve", side_effect=OSError("Permission denied"))
    def test_get_iommu_group_permission_error(
        self, mock_resolve, mock_exists, valid_bdf
    ):
        """Test getting IOMMU group with permission error."""
        with pytest.raises(VFIOBindError, match="Failed to read IOMMU group"):
            _get_iommu_group(valid_bdf)

    @patch("src.cli.vfio_handler._get_iommu_group", return_value="42")
    def test_get_iommu_group_safe_success(self, mock_get_group, valid_bdf):
        """Test safe IOMMU group getter success."""
        result = _get_iommu_group_safe(valid_bdf)
        assert result == "42"

    @patch("src.cli.vfio_handler._get_iommu_group", side_effect=VFIOBindError("Error"))
    def test_get_iommu_group_safe_error(self, mock_get_group, valid_bdf):
        """Test safe IOMMU group getter with error."""
        result = _get_iommu_group_safe(valid_bdf)
        assert result is None


class TestVFIOBinderContextManager:
    """Test cases for VFIOBinder context manager function."""

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler._get_iommu_group", return_value="42")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._bind_to_vfio")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._cleanup")
    def test_vfio_binder_context_manager(
        self, mock_cleanup, mock_bind, mock_get_group, mock_geteuid, valid_bdf
    ):
        """Test VFIOBinder context manager wrapper."""
        with VFIOBinder(valid_bdf, attach=False) as group_path:
            assert group_path == Path("/dev/vfio/42")
            mock_bind.assert_called_once()

        mock_cleanup.assert_called_once()


class TestDiagnostics:
    """Test cases for diagnostic functions."""

    @patch("src.cli.vfio_handler.HAS_VFIO_ASSIST", False)
    def test_run_diagnostics_no_vfio_assist(self, valid_bdf):
        """Test diagnostics when vfio_assist is not available."""
        result = run_diagnostics(valid_bdf)

        assert result["overall"] == "skipped"
        assert result["can_proceed"] is True
        assert result["checks"] == []
        assert "vfio_assist module not available" in result["message"]

    @patch("src.cli.vfio_handler.HAS_VFIO_ASSIST", True)
    @patch("src.cli.vfio_handler.vfio_assist")
    def test_run_diagnostics_success(self, mock_vfio_assist, valid_bdf):
        """Test successful diagnostics run."""
        # Mock the diagnostics result
        mock_check = Mock()
        mock_check.name = "test_check"
        mock_check.status = "ok"
        mock_check.message = "All good"

        mock_result = Mock()
        mock_result.overall = "ok"
        mock_result.can_proceed = True
        mock_result.checks = [mock_check]

        mock_diagnostics = Mock()
        mock_diagnostics.run.return_value = mock_result
        mock_vfio_assist.Diagnostics.return_value = mock_diagnostics

        result = run_diagnostics(valid_bdf)

        assert result["overall"] == "ok"
        assert result["can_proceed"] is True
        assert len(result["checks"]) == 1
        assert result["checks"][0]["name"] == "test_check"
        assert result["checks"][0]["status"] == "ok"
        assert result["checks"][0]["message"] == "All good"

    @patch("src.cli.vfio_handler.HAS_VFIO_ASSIST", True)
    @patch("src.cli.vfio_handler.vfio_assist")
    def test_run_diagnostics_error(self, mock_vfio_assist, valid_bdf):
        """Test diagnostics with error."""
        mock_vfio_assist.Diagnostics.side_effect = Exception("Diagnostics failed")

        result = run_diagnostics(valid_bdf)

        assert result["overall"] == "error"
        assert result["can_proceed"] is False
        assert result["checks"] == []
        assert result["error"] == "Diagnostics failed"

    def test_render_pretty_without_vfio_assist(self):
        """Test pretty rendering without vfio_assist colors."""
        diagnostic_result = {
            "overall": "ok",
            "checks": [{"name": "Test", "status": "ok", "message": "Passed"}],
        }

        # Should fall back to JSON
        result = render_pretty(diagnostic_result)
        assert "overall" in result
        assert "ok" in result

    @patch("builtins.__import__")
    def test_render_pretty_with_colors(self, mock_import):
        """Test pretty rendering with colors."""
        # Create a mock vfio_assist module
        mock_vfio_assist = MagicMock()
        mock_vfio_assist.Fore = Mock(GREEN="GREEN", YELLOW="YELLOW", RED="RED")
        mock_vfio_assist.colour = lambda text, color: f"[{color}]{text}[/{color}]"

        # Make __import__ return our mock for vfio_assist
        def side_effect(name, *args, **kwargs):
            if name == "vfio_assist":
                return mock_vfio_assist
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = side_effect

        diagnostic_result = {
            "overall": "ok",
            "checks": [
                {"name": "Test1", "status": "ok", "message": "Passed"},
                {"name": "Test2", "status": "warning", "message": "Warning"},
                {"name": "Test3", "status": "error", "message": "Failed"},
            ],
        }

        result = render_pretty(diagnostic_result)

        assert "[GREEN]✓ VFIO Diagnostics: PASSED[/GREEN]" in result
        assert "✓ [GREEN]Test1[/GREEN]: Passed" in result
        assert "⚠ [YELLOW]Test2[/YELLOW]: Warning" in result
        assert "✗ [RED]Test3[/RED]: Failed" in result


class TestSecurityScenarios:
    """Test cases for security-related scenarios."""

    @patch("os.geteuid", return_value=1000)
    def test_non_root_access_denied(self, mock_geteuid, valid_bdf):
        """Test that non-root users cannot use VFIOBinder."""
        with pytest.raises(VFIOPermissionError, match="root privileges"):
            VFIOBinderImpl(valid_bdf)

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.write_text", side_effect=PermissionError("Access denied"))
    def test_sysfs_write_permission_denied(
        self, mock_write, mock_exists, mock_geteuid, valid_bdf
    ):
        """Test handling of permission errors when writing to sysfs."""
        binder = VFIOBinderImpl(valid_bdf)

        with pytest.raises(VFIOPermissionError, match="Permission denied"):
            binder._write_sysfs_safe(Path("/sys/test"), "value")

    @patch("os.geteuid", return_value=0)
    @patch("os.access", return_value=False)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("src.cli.vfio_handler._get_iommu_group", return_value="42")
    def test_vfio_group_access_denied(
        self, mock_get_group, mock_exists, mock_access, mock_geteuid, valid_bdf
    ):
        """Test handling when VFIO group device is not accessible."""
        binder = VFIOBinderImpl(valid_bdf)

        with pytest.raises(VFIOBindError, match="verification failed"):
            binder._verify_vfio_binding()


class TestEdgeCases:
    """Test cases for edge cases and boundary conditions."""

    @patch("os.geteuid", return_value=0)
    def test_empty_bdf(self, mock_geteuid):
        """Test with empty BDF string."""
        with pytest.raises(ValueError, match="Invalid BDF format"):
            VFIOBinderImpl("")

    @patch("os.geteuid", return_value=0)
    @patch("os.close")
    @patch("fcntl.ioctl")
    @patch("os.open")
    def test_device_name_too_long(
        self, mock_open, mock_ioctl, mock_close, mock_geteuid
    ):
        """Test with device name that's too long for ioctl."""
        long_bdf = "0000:" + "a" * 50 + ":00.0"
        binder = VFIOBinderImpl("0000:01:00.0")  # Use valid BDF for init
        binder.bdf = long_bdf  # Override with long BDF
        binder.group_id = "42"

        # Mock file descriptor returns
        mock_open.side_effect = [100, 101]  # container_fd, group_fd

        # Mock ioctl calls to succeed up to the device name check
        mock_ioctl.side_effect = [None, None]  # GROUP_SET_CONTAINER, SET_IOMMU

        with pytest.raises(VFIOBindError, match=r"Device name .* too long"):
            binder._open_vfio_device_fd()

    @patch("os.geteuid", return_value=0)
    @patch("pathlib.Path.exists")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._get_device_info")
    @patch(
        "src.cli.vfio_handler.VFIOBinderImpl._write_sysfs_safe",
        side_effect=Exception("Cleanup error"),
    )
    def test_cleanup_with_errors(
        self,
        mock_write,
        mock_get_info,
        mock_exists,
        mock_geteuid,
        valid_bdf,
        mock_vfio_device_info,
    ):
        """Test cleanup continues despite errors."""
        binder = VFIOBinderImpl(valid_bdf)
        binder._bound = True
        mock_exists.return_value = True
        mock_get_info.return_value = mock_vfio_device_info

        # Should not raise despite write errors
        binder._cleanup()

    @patch("os.geteuid", return_value=0)
    @patch("time.time", side_effect=[0, 0.1, 0.2, 0.3, 0.4, 0.5])
    @patch("src.cli.vfio_handler._get_current_driver", return_value="old_driver")
    def test_wait_for_state_change_never_changes(
        self, mock_get_driver, mock_time, mock_geteuid, valid_bdf
    ):
        """Test waiting for state change that never happens."""
        binder = VFIOBinderImpl(valid_bdf)

        result = binder._wait_for_state_change("vfio-pci", timeout=0.5)

        assert result is False
        assert mock_get_driver.call_count >= 4


class TestStateManagement:
    """Test cases for device state management."""

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._get_device_info")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._unbind_current_driver")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._perform_vfio_binding")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._verify_vfio_binding")
    def test_bind_state_transitions(
        self,
        mock_verify,
        mock_perform,
        mock_unbind,
        mock_get_info,
        mock_geteuid,
        valid_bdf,
    ):
        """Test proper state transitions during binding."""
        binder = VFIOBinderImpl(valid_bdf)

        # Mock state transitions
        unbound_info = DeviceInfo(
            bdf=valid_bdf,
            current_driver=None,
            iommu_group="42",
            binding_state=BindingState.UNBOUND,
        )
        vfio_info = DeviceInfo(
            bdf=valid_bdf,
            current_driver="vfio-pci",
            iommu_group="42",
            binding_state=BindingState.BOUND_TO_VFIO,
        )
        mock_get_info.side_effect = [unbound_info, vfio_info]

        binder._bind_to_vfio()

        assert binder._bound is True
        assert binder.original_driver is None
        mock_unbind.assert_called_once()
        mock_perform.assert_called_once()
        mock_verify.assert_called_once()

    @patch("os.geteuid", return_value=0)
    @patch("src.cli.vfio_handler.VFIOBinderImpl._get_device_info")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._perform_vfio_binding")
    @patch("src.cli.vfio_handler.VFIOBinderImpl._verify_vfio_binding")
    def test_bind_failure_state_not_changed(
        self,
        mock_verify,
        mock_perform,
        mock_get_info,
        mock_geteuid,
        valid_bdf,
        mock_device_info,
    ):
        """Test that _bound state is not changed on binding failure."""
        binder = VFIOBinderImpl(valid_bdf)

        # Mock binding failure
        mock_get_info.side_effect = [
            mock_device_info,
            mock_device_info,
        ]  # State doesn't change

        with pytest.raises(VFIOBindError, match="Failed to bind"):
            binder._bind_to_vfio()

        assert binder._bound is False


# Module constants test
def test_module_exports():
    """Test that all expected exports are available."""
    from src.cli.vfio_handler import __all__

    expected_exports = [
        "VFIOBinder",
        "VFIOBindError",
        "VFIODeviceNotFoundError",
        "VFIOPermissionError",
        "VFIOGroupError",
        "BindingState",
        "DeviceInfo",
        "VFIOPathManager",
        "run_diagnostics",
        "render_pretty",
    ]

    assert set(__all__) == set(expected_exports)
