"""
Comprehensive tests for generate.py - Main orchestrator functionality.
"""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import generate


class TestBDFValidation:
    """Test BDF format validation."""

    def test_valid_bdf_formats(self):
        """Test valid BDF formats."""
        valid_bdfs = ["0000:03:00.0", "0000:ff:1f.7", "abcd:12:34.5", "FFFF:FF:FF.7"]
        for bdf in valid_bdfs:
            assert generate.validate_bdf_format(bdf), f"BDF {bdf} should be valid"

    def test_invalid_bdf_formats(self):
        """Test invalid BDF formats."""
        invalid_bdfs = [
            "000:03:00.0",  # Too short domain
            "0000:3:00.0",  # Too short bus
            "0000:03:0.0",  # Too short device
            "0000:03:00.8",  # Invalid function
            "0000:03:00",  # Missing function
            "0000:03:00.0.1",  # Extra component
            "gggg:03:00.0",  # Invalid hex
            "",  # Empty string
            "not-a-bdf",  # Completely invalid
        ]
        for bdf in invalid_bdfs:
            assert not generate.validate_bdf_format(bdf), f"BDF {bdf} should be invalid"


class TestPCIDeviceEnumeration:
    """Test PCIe device enumeration functionality."""

    @patch("generate.run_command")
    def test_list_pci_devices_success(self, mock_run):
        """Test successful PCIe device listing."""
        mock_lspci_output = """0000:00:00.0 Host bridge [0600]: Intel Corporation Xeon E3-1200 v3/4th Gen Core Processor DRAM Controller [8086:0c00] (rev 06)
0000:03:00.0 Ethernet controller [0200]: Intel Corporation I210 Gigabit Network Connection [8086:1533] (rev 03)
0000:04:00.0 Network controller [0280]: Intel Corporation Wi-Fi 6 AX200 [8086:2723] (rev 1a)"""

        mock_run.return_value = mock_lspci_output

        devices = generate.list_pci_devices()

        assert len(devices) == 3
        assert devices[0]["bdf"] == "0000:00:00.0"
        assert devices[0]["ven"] == "8086"
        assert devices[0]["dev"] == "0c00"
        assert devices[0]["class"] == "0600"
        assert "Host bridge" in devices[0]["pretty"]

        assert devices[1]["bdf"] == "0000:03:00.0"
        assert devices[1]["ven"] == "8086"
        assert devices[1]["dev"] == "1533"

        mock_run.assert_called_once_with("lspci -Dnn")

    @patch("generate.run_command")
    def test_list_pci_devices_empty(self, mock_run):
        """Test empty PCIe device listing."""
        mock_run.return_value = ""
        devices = generate.list_pci_devices()
        assert devices == []

    @patch("generate.run_command")
    def test_list_pci_devices_malformed(self, mock_run):
        """Test handling of malformed lspci output."""
        mock_run.return_value = "malformed line without proper format"
        devices = generate.list_pci_devices()
        assert devices == []


class TestDeviceSelection:
    """Test device selection functionality."""

    @patch("builtins.input")
    def test_choose_device_valid_selection(self, mock_input, mock_pci_device):
        """Test valid device selection."""
        devices = [mock_pci_device]
        mock_input.return_value = "0"

        selected = generate.choose_device(devices)
        assert selected == mock_pci_device

    @patch("builtins.input")
    def test_choose_device_invalid_then_valid(self, mock_input, mock_pci_device):
        """Test invalid selection followed by valid selection."""
        devices = [mock_pci_device]
        mock_input.side_effect = ["invalid", "99", "0"]

        selected = generate.choose_device(devices)
        assert selected == mock_pci_device
        assert mock_input.call_count == 3


class TestDriverManagement:
    """Test driver binding and management."""

    @patch("os.path.exists")
    @patch("os.path.realpath")
    @patch("os.path.basename")
    def test_get_current_driver_exists(self, mock_basename, mock_realpath, mock_exists):
        """Test getting current driver when driver exists."""
        mock_exists.return_value = True
        mock_realpath.return_value = "/sys/bus/pci/drivers/e1000e"
        mock_basename.return_value = "e1000e"

        driver = generate.get_current_driver("0000:03:00.0")
        assert driver == "e1000e"
        mock_exists.assert_called_once_with("/sys/bus/pci/devices/0000:03:00.0/driver")

    @patch("os.path.exists")
    def test_get_current_driver_none(self, mock_exists):
        """Test getting current driver when no driver is bound."""
        mock_exists.return_value = False

        driver = generate.get_current_driver("0000:03:00.0")
        assert driver is None

    def test_get_current_driver_invalid_bdf(self):
        """Test getting current driver with invalid BDF."""
        with pytest.raises(ValueError, match="Invalid BDF format"):
            generate.get_current_driver("invalid-bdf")

    @patch("os.path.realpath")
    @patch("os.path.basename")
    def test_get_iommu_group(self, mock_basename, mock_realpath):
        """Test getting IOMMU group."""
        mock_realpath.return_value = "/sys/kernel/iommu_groups/15"
        mock_basename.return_value = "15"

        group = generate.get_iommu_group("0000:03:00.0")
        assert group == "15"
        mock_realpath.assert_called_once_with(
            "/sys/bus/pci/devices/0000:03:00.0/iommu_group"
        )

    def test_get_iommu_group_invalid_bdf(self):
        """Test getting IOMMU group with invalid BDF."""
        with pytest.raises(ValueError, match="Invalid BDF format"):
            generate.get_iommu_group("invalid-bdf")


class TestVFIOBinding:
    """Test VFIO driver binding functionality."""

    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_bind_to_vfio_success(self, mock_exists, mock_run):
        """Test successful VFIO binding."""
        mock_exists.return_value = True

        generate.bind_to_vfio("0000:03:00.0", "8086", "1533", "e1000e")

        expected_calls = [
            call("echo 8086 1533 > /sys/bus/pci/drivers/vfio-pci/new_id"),
            call("echo 0000:03:00.0 > /sys/bus/pci/devices/0000:03:00.0/driver/unbind"),
            call("echo 0000:03:00.0 > /sys/bus/pci/drivers/vfio-pci/bind"),
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_bind_to_vfio_no_original_driver(self, mock_exists, mock_run):
        """Test VFIO binding with no original driver."""
        mock_exists.return_value = True

        generate.bind_to_vfio("0000:03:00.0", "8086", "1533", None)

        # Should not try to unbind from non-existent driver
        unbind_call = call(
            "echo 0000:03:00.0 > /sys/bus/pci/devices/0000:03:00.0/driver/unbind"
        )
        assert unbind_call not in mock_run.call_args_list

    @patch("os.path.exists")
    def test_bind_to_vfio_driver_not_available(self, mock_exists):
        """Test VFIO binding when vfio-pci driver is not available."""
        mock_exists.return_value = False

        with pytest.raises(RuntimeError, match="vfio-pci driver not available"):
            generate.bind_to_vfio("0000:03:00.0", "8086", "1533", "e1000e")

    def test_bind_to_vfio_invalid_bdf(self):
        """Test VFIO binding with invalid BDF."""
        with pytest.raises(ValueError, match="Invalid BDF format"):
            generate.bind_to_vfio("invalid-bdf", "8086", "1533", "e1000e")


class TestDriverRestore:
    """Test driver restoration functionality."""

    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    @patch("os.path.exists")
    def test_restore_original_driver_success(
        self, mock_exists, mock_run, mock_get_driver
    ):
        """Test successful driver restoration."""
        mock_get_driver.return_value = "vfio-pci"
        mock_exists.return_value = True

        generate.restore_original_driver("0000:03:00.0", "e1000e")

        expected_calls = [
            call("echo 0000:03:00.0 > /sys/bus/pci/drivers/vfio-pci/unbind"),
            call("echo 0000:03:00.0 > /sys/bus/pci/drivers/e1000e/bind"),
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch("generate.get_current_driver")
    @patch("generate.run_command")
    def test_restore_original_driver_not_vfio(self, mock_run, mock_get_driver):
        """Test driver restoration when device is not bound to vfio-pci."""
        mock_get_driver.return_value = "e1000e"

        generate.restore_original_driver("0000:03:00.0", "e1000e")

        # Should not try to unbind from vfio-pci
        unbind_call = call("echo 0000:03:00.0 > /sys/bus/pci/drivers/vfio-pci/unbind")
        assert unbind_call not in mock_run.call_args_list

    @patch("generate.get_current_driver")
    def test_restore_original_driver_no_original(self, mock_get_driver):
        """Test driver restoration with no original driver."""
        mock_get_driver.return_value = "vfio-pci"

        # Should not raise exception
        generate.restore_original_driver("0000:03:00.0", None)


class TestUSBDeviceManagement:
    """Test USB device management for FPGA flashing."""

    @patch("subprocess.check_output")
    def test_list_usb_devices_success(self, mock_output):
        """Test successful USB device listing."""
        mock_lsusb_output = """Bus 001 Device 002: ID 1d50:6130 OpenMoko, Inc. 
Bus 001 Device 003: ID 0403:6010 Future Technology Devices International, Ltd FT2232C/D/H Dual UART/FIFO IC
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub"""

        mock_output.return_value = mock_lsusb_output

        devices = generate.list_usb_devices()

        assert len(devices) == 3
        assert devices[0] == ("1d50:6130", "OpenMoko, Inc.")
        assert devices[1] == (
            "0403:6010",
            "Future Technology Devices International, Ltd FT2232C/D/H Dual UART/FIFO IC",
        )
        assert devices[2] == ("1d6b:0003", "Linux Foundation 3.0 root hub")

    @patch("subprocess.check_output")
    def test_list_usb_devices_command_error(self, mock_output):
        """Test USB device listing when lsusb command fails."""
        mock_output.side_effect = subprocess.CalledProcessError(1, "lsusb")

        devices = generate.list_usb_devices()
        assert devices == []

    @patch("generate.list_usb_devices")
    @patch("builtins.input")
    def test_select_usb_device_success(
        self, mock_input, mock_list_usb, mock_usb_devices
    ):
        """Test successful USB device selection."""
        mock_list_usb.return_value = mock_usb_devices
        mock_input.return_value = "0"

        selected = generate.select_usb_device()
        assert selected == "1d50:6130"

    @patch("generate.list_usb_devices")
    def test_select_usb_device_no_devices(self, mock_list_usb):
        """Test USB device selection when no devices are found."""
        mock_list_usb.return_value = []

        with pytest.raises(RuntimeError, match="No USB devices found"):
            generate.select_usb_device()


class TestFirmwareFlashing:
    """Test firmware flashing functionality."""

    @patch("generate.select_usb_device")
    @patch("subprocess.run")
    @patch("shutil.which")
    def test_flash_firmware_success(self, mock_which, mock_run, mock_select):
        """Test successful firmware flashing."""
        mock_which.return_value = "/usr/bin/usbloader"
        mock_select.return_value = "1d50:6130"
        mock_run.return_value = Mock(returncode=0)

        firmware_path = Path("/tmp/firmware.bin")
        generate.flash_firmware(firmware_path)

        mock_run.assert_called_once_with(
            f"usbloader --vidpid 1d50:6130 -f {firmware_path}", shell=True, check=True
        )

    @patch("shutil.which")
    def test_flash_firmware_no_usbloader(self, mock_which):
        """Test firmware flashing when usbloader is not available."""
        mock_which.return_value = None

        with pytest.raises(RuntimeError, match="usbloader not found in PATH"):
            generate.flash_firmware(Path("/tmp/firmware.bin"))

    @patch("generate.select_usb_device")
    @patch("subprocess.run")
    @patch("shutil.which")
    def test_flash_firmware_command_failure(self, mock_which, mock_run, mock_select):
        """Test firmware flashing when usbloader command fails."""
        mock_which.return_value = "/usr/bin/usbloader"
        mock_select.return_value = "1d50:6130"
        mock_run.side_effect = subprocess.CalledProcessError(1, "usbloader")

        with pytest.raises(RuntimeError, match="Flash failed"):
            generate.flash_firmware(Path("/tmp/firmware.bin"))


class TestContainerExecution:
    """Test container execution functionality."""

    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_run_build_container_success(self, mock_makedirs, mock_exists, mock_run):
        """Test successful container execution."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=0)

        # Create mock args with default values
        mock_args = Mock()
        mock_args.advanced_sv = False
        mock_args.device_type = "generic"
        mock_args.enable_variance = False
        mock_args.disable_power_management = False
        mock_args.disable_error_handling = False
        mock_args.disable_performance_counters = False
        mock_args.behavior_profile_duration = 30

        generate.run_build_container("0000:03:00.0", "75t", "/dev/vfio/15", mock_args)

        mock_makedirs.assert_called_once_with("output", exist_ok=True)
        mock_run.assert_called_once()

        # Check that the command contains expected elements
        call_args = mock_run.call_args[0][0]
        assert "podman run" in call_args
        assert "--device=/dev/vfio/15" in call_args
        assert "--device=/dev/vfio/vfio" in call_args
        assert "0000:03:00.0" in call_args
        assert "75t" in call_args

    @patch("os.path.exists")
    def test_run_build_container_no_vfio_device(self, mock_exists):
        """Test container execution when VFIO device doesn't exist."""
        mock_exists.return_value = False

        # Create mock args with default values
        mock_args = Mock()
        mock_args.advanced_sv = False
        mock_args.device_type = "generic"
        mock_args.enable_variance = False
        mock_args.disable_power_management = False
        mock_args.disable_error_handling = False
        mock_args.disable_performance_counters = False
        mock_args.behavior_profile_duration = 30

        with pytest.raises(RuntimeError, match="VFIO device .* not found"):
            generate.run_build_container(
                "0000:03:00.0", "75t", "/dev/vfio/15", mock_args
            )

    def test_run_build_container_invalid_bdf(self):
        """Test container execution with invalid BDF."""
        # Create mock args with default values
        mock_args = Mock()
        mock_args.advanced_sv = False
        mock_args.device_type = "generic"
        mock_args.enable_variance = False
        mock_args.disable_power_management = False
        mock_args.disable_error_handling = False
        mock_args.disable_performance_counters = False
        mock_args.behavior_profile_duration = 30

        with pytest.raises(ValueError, match="Invalid BDF format"):
            generate.run_build_container(
                "invalid-bdf", "75t", "/dev/vfio/15", mock_args
            )

    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_run_build_container_with_advanced_features(
        self, mock_makedirs, mock_exists, mock_run
    ):
        """Test container execution with advanced features enabled."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=0)

        # Create mock args with advanced features enabled
        mock_args = Mock()
        mock_args.advanced_sv = True
        mock_args.device_type = "network"
        mock_args.enable_variance = True
        mock_args.disable_power_management = True
        mock_args.disable_error_handling = False
        mock_args.disable_performance_counters = True
        mock_args.behavior_profile_duration = 60

        generate.run_build_container("0000:03:00.0", "75t", "/dev/vfio/15", mock_args)

        mock_makedirs.assert_called_once_with("output", exist_ok=True)
        mock_run.assert_called_once()

        # Check that the command contains expected advanced feature arguments
        call_args = mock_run.call_args[0][0]
        assert "podman run" in call_args
        assert "--advanced-sv" in call_args
        assert "--device-type network" in call_args
        assert "--enable-variance" in call_args
        assert "--disable-power-management" in call_args
        assert "--disable-performance-counters" in call_args
        assert "--behavior-profile-duration 60" in call_args
        # Should not contain disabled error handling since it's False
        assert "--disable-error-handling" not in call_args


class TestEnvironmentValidation:
    """Test environment validation functionality."""

    @patch("os.geteuid")
    @patch("shutil.which")
    @patch("generate.run_command")
    def test_validate_environment_success(
        self, mock_run_command, mock_which, mock_geteuid
    ):
        """Test successful environment validation."""
        mock_geteuid.return_value = 0  # Root user
        mock_which.return_value = "/usr/bin/podman"
        mock_run_command.return_value = "dma-fw"  # Simulate container image exists

        # Should not raise exception
        generate.validate_environment()

    @patch("os.geteuid")
    def test_validate_environment_not_root(self, mock_geteuid):
        """Test environment validation when not running as root."""
        mock_geteuid.return_value = 1000  # Non-root user

        with pytest.raises(RuntimeError, match="requires root privileges"):
            generate.validate_environment()

    @patch("os.geteuid")
    @patch("shutil.which")
    def test_validate_environment_no_podman(self, mock_which, mock_geteuid):
        """Test environment validation when Podman is not available."""
        mock_geteuid.return_value = 0
        # Return a valid path for git but None for podman
        mock_which.side_effect = lambda cmd: "/usr/bin/git" if cmd == "git" else None

        with pytest.raises(RuntimeError, match="Podman not found"):
            generate.validate_environment()


class TestMainWorkflow:
    """Test main workflow integration."""

    @patch("generate.validate_environment")
    @patch("generate.list_pci_devices")
    @patch("generate.choose_device")
    @patch("generate.get_iommu_group")
    @patch("generate.get_current_driver")
    @patch("generate.bind_to_vfio")
    @patch("generate.run_build_container")
    @patch("generate.restore_original_driver")
    @patch("pathlib.Path.exists")
    def test_main_success_no_flash(
        self,
        mock_path_exists,
        mock_restore,
        mock_container,
        mock_bind,
        mock_get_driver,
        mock_get_iommu,
        mock_choose,
        mock_list_devices,
        mock_validate,
        mock_pci_device,
    ):
        """Test successful main workflow without flashing."""
        # Setup mocks
        mock_list_devices.return_value = [mock_pci_device]
        mock_choose.return_value = mock_pci_device
        mock_get_iommu.return_value = "15"
        mock_get_driver.return_value = "e1000e"

        with patch("sys.argv", ["generate.py", "--board", "75t"]):
            result = generate.main()

        assert result == 0
        mock_validate.assert_called_once()
        mock_bind.assert_called_once_with("0000:03:00.0", "8086", "1533", "e1000e")
        # Pass the args parameter to run_build_container
        mock_container.assert_called_once()
        args = mock_container.call_args[0][3]
        assert args.board == "75t"
        assert args.flash is False
        mock_restore.assert_called_once_with("0000:03:00.0", "e1000e")

    @patch("generate.validate_environment")
    @patch("generate.list_pci_devices")
    @patch("generate.choose_device")
    @patch("generate.get_iommu_group")
    @patch("generate.get_current_driver")
    @patch("generate.bind_to_vfio")
    @patch("generate.run_build_container")
    @patch("generate.flash_firmware")
    @patch("generate.restore_original_driver")
    @patch("pathlib.Path.exists")
    def test_main_success_with_flash(
        self,
        mock_path_exists,
        mock_restore,
        mock_flash,
        mock_container,
        mock_bind,
        mock_get_driver,
        mock_get_iommu,
        mock_choose,
        mock_list_devices,
        mock_validate,
        mock_pci_device,
    ):
        """Test successful main workflow with flashing."""
        # Setup mocks
        mock_list_devices.return_value = [mock_pci_device]
        mock_choose.return_value = mock_pci_device
        mock_get_iommu.return_value = "15"
        mock_get_driver.return_value = "e1000e"
        mock_path_exists.return_value = True

        with patch("sys.argv", ["generate.py", "--board", "75t", "--flash"]):
            result = generate.main()

        assert result == 0
        mock_validate.assert_called_once()
        mock_bind.assert_called_once_with("0000:03:00.0", "8086", "1533", "e1000e")
        # Pass the args parameter to run_build_container
        mock_container.assert_called_once()
        args = mock_container.call_args[0][3]
        assert args.board == "75t"
        assert args.flash is True
        mock_flash.assert_called_once()
        mock_restore.assert_called_once_with("0000:03:00.0", "e1000e")

    @patch("generate.validate_environment")
    @patch("generate.list_pci_devices")
    def test_main_no_devices(self, mock_list_devices, mock_validate):
        """Test main workflow when no PCIe devices are found."""
        mock_list_devices.return_value = []

        with patch("sys.argv", ["generate.py", "--board", "75t"]):
            result = generate.main()

        assert result == 1

    @patch("generate.validate_environment")
    def test_main_keyboard_interrupt(self, mock_validate):
        """Test main workflow handling of keyboard interrupt."""
        mock_validate.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["generate.py", "--board", "75t"]):
            result = generate.main()

        assert result == 1


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_run_command_success(self):
        """Test successful command execution."""
        with patch("subprocess.check_output") as mock_output:
            mock_output.return_value = "  test output  \n"
            result = generate.run_command("echo test")
            assert result == "test output"

    def test_run_command_failure(self):
        """Test command execution failure."""
        with patch("subprocess.check_output") as mock_output:
            mock_output.side_effect = subprocess.CalledProcessError(1, "false")
            with pytest.raises(subprocess.CalledProcessError):
                generate.run_command("false")


class TestArgumentParsing:
    """Test command line argument parsing."""

    def test_default_arguments(self):
        """Test default argument values."""
        with patch("sys.argv", ["generate.py"]):
            parser = generate.argparse.ArgumentParser()
            parser.add_argument("--flash", action="store_true")
            parser.add_argument(
                "--board",
                choices=[
                    # Original boards
                    "35t",
                    "75t",
                    "100t",
                    # CaptainDMA boards
                    "pcileech_75t484_x1",
                    "pcileech_35t484_x1",
                    "pcileech_35t325_x4",
                    "pcileech_35t325_x1",
                    "pcileech_100t484_x1",
                    # Other boards
                    "pcileech_enigma_x1",
                    "pcileech_squirrel",
                    "pcileech_pciescreamer_xc7a35",
                ],
                default="35t",
            )

            args = parser.parse_args([])
            assert args.flash is False
            assert args.board == "35t"

    def test_custom_arguments(self):
        """Test custom argument values."""
        with patch("sys.argv", ["generate.py", "--board", "100t", "--flash"]):
            parser = generate.argparse.ArgumentParser()
            parser.add_argument("--flash", action="store_true")
            parser.add_argument(
                "--board",
                choices=[
                    # Original boards
                    "35t",
                    "75t",
                    "100t",
                    # CaptainDMA boards
                    "pcileech_75t484_x1",
                    "pcileech_35t484_x1",
                    "pcileech_35t325_x4",
                    "pcileech_35t325_x1",
                    "pcileech_100t484_x1",
                    # Other boards
                    "pcileech_enigma_x1",
                    "pcileech_squirrel",
                    "pcileech_pciescreamer_xc7a35",
                ],
                default="35t",
            )

            args = parser.parse_args(["--board", "100t", "--flash"])
            assert args.flash is True
            assert args.board == "100t"
