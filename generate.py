#!/usr/bin/env python3
"""
Host-side orchestrator for DMA firmware generation.

This script:
• Enumerates PCIe devices
• Allows user to select a donor device
• Re-binds donor to vfio-pci driver
• Launches Podman container (image: pcileech-fw-generator) that runs build.py
• Optionally flashes output/firmware.bin with usbloader
• Restores original driver afterwards

Requires root privileges (sudo) for driver rebinding and VFIO operations.
"""

import argparse
import logging
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import textwrap
import time
from typing import Dict, List, Optional, Tuple

# Import donor dump manager
try:
    from src.donor_dump_manager import DonorDumpError, DonorDumpManager
except ImportError:
    DonorDumpManager = None
    DonorDumpError = Exception

# Git repository information
PCILEECH_FPGA_REPO = "https://github.com/ufrisk/pcileech-fpga.git"
REPO_CACHE_DIR = os.path.expanduser("~/.cache/pcileech-fw-generator/repos")


def clear_python_cache():
    """Clear Python bytecode cache files to ensure updated code is used."""
    import glob

    cache_patterns = [
        "__pycache__",
        "src/__pycache__",
        "tests/__pycache__",
        "tests/tui/__pycache__",
        "src/tui/__pycache__",
        "src/tui/core/__pycache__",
        "src/tui/models/__pycache__",
        "src/scripts/__pycache__",
    ]

    for pattern in cache_patterns:
        for cache_dir in glob.glob(pattern):
            if os.path.exists(cache_dir):
                try:
                    shutil.rmtree(cache_dir)
                    print(f"[*] Cleared Python cache: {cache_dir}")
                except Exception as e:
                    print(f"[!] Warning: Could not clear cache {cache_dir}: {e}")


# Clear Python cache at startup to ensure updated code is used
clear_python_cache()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("generate.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


def validate_bdf_format(bdf: str) -> bool:
    """
    Validate BDF (Bus:Device.Function) format.
    Expected format: DDDD:BB:DD.F where D=hex digit, B=hex digit, F=0-7
    Example: 0000:03:00.0
    """
    bdf_pattern = re.compile(r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]$")
    return bool(bdf_pattern.match(bdf))


def run_command(cmd: str, timeout: int = 30, **kwargs) -> str:
    """Execute a shell command and return stripped output with timeout and better error handling."""
    try:
        return subprocess.check_output(
            cmd, shell=True, text=True, timeout=timeout, **kwargs
        ).strip()
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout}s: {cmd}")
        raise RuntimeError(f"Command timed out: {cmd}") from e
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed (exit code {e.returncode}): {cmd}")
        logger.error(f"Command stderr: {e.stderr}")
        raise


def is_linux() -> bool:
    """Check if running on Linux."""
    import platform

    return platform.system().lower() == "linux"


def check_linux_requirement(operation: str) -> None:
    """Check if operation requires Linux and raise error if not available."""
    if not is_linux():
        raise RuntimeError(
            f"{operation} requires Linux. "
            f"Current platform: {platform.system()}. "
            "Please run this on a Linux system with VFIO support."
        )


def list_pci_devices() -> List[Dict[str, str]]:
    """List all PCIe devices with their details."""
    check_linux_requirement("PCIe device enumeration")

    pattern = re.compile(
        r"(?P<bdf>[0-9a-fA-F:.]+) .*?\["
        r"(?P<class>[0-9a-fA-F]{4})\]: .*?\["
        r"(?P<ven>[0-9a-fA-F]{4}):(?P<dev>[0-9a-fA-F]{4})\]"
    )

    devices = []
    for line in run_command("lspci -Dnn").splitlines():
        match = pattern.match(line)
        if match:
            device_info = match.groupdict()
            device_info["pretty"] = line
            devices.append(device_info)

    return devices


def choose_device(devices: List[Dict[str, str]]) -> Dict[str, str]:
    """Interactive device selection from the list of PCIe devices."""
    print("\nSelect donor PCIe device:")
    for i, device in enumerate(devices):
        print(f" [{i}] {device['pretty']}")

    while True:
        try:
            selection = input("Enter number: ")
            index = int(selection)
            return devices[index]
        except (ValueError, IndexError):
            print("  Invalid selection — please try again.")


def get_current_driver(bdf: str) -> Optional[str]:
    """Get the current driver bound to a PCIe device."""
    check_linux_requirement("Driver detection")

    if not validate_bdf_format(bdf):
        raise ValueError(
            f"Invalid BDF format: {bdf}. Expected format: DDDD:BB:DD.F (e.g., 0000:03:00.0)"
        )

    driver_path = f"/sys/bus/pci/devices/{bdf}/driver"
    if os.path.exists(driver_path):
        return os.path.basename(os.path.realpath(driver_path))
    return None


def get_iommu_group(bdf: str) -> str:
    """Get the IOMMU group for a PCIe device."""
    check_linux_requirement("IOMMU group detection")

    if not validate_bdf_format(bdf):
        raise ValueError(
            f"Invalid BDF format: {bdf}. Expected format: DDDD:BB:DD.F (e.g., 0000:03:00.0)"
        )

    iommu_link = f"/sys/bus/pci/devices/{bdf}/iommu_group"
    return os.path.basename(os.path.realpath(iommu_link))


def list_usb_devices() -> List[Tuple[str, str]]:
    """Return list of USB devices as (vid:pid, description) tuples."""
    try:
        output = subprocess.check_output("lsusb", shell=True, text=True).splitlines()
    except subprocess.CalledProcessError:
        return []

    devices = []
    for line in output:
        match = re.match(
            r"Bus.*Device.*ID\s+([0-9a-fA-F]{4}:[0-9a-fA-F]{4})\s+(.*)", line
        )
        if match:
            vid_pid = match.group(1)
            # Strip whitespace from description
            description = match.group(2).strip()
            devices.append((vid_pid, description))

    return devices


def select_usb_device() -> str:
    """Interactive USB device selection for flashing."""
    devices = list_usb_devices()
    if not devices:
        error_msg = "No USB devices found"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    print("\nSelect FPGA board / USB programmer:")
    for i, (vid_pid, description) in enumerate(devices):
        print(f" [{i}] {vid_pid}  {description}")

    while True:
        try:
            selection = input("Enter number: ")
            index = int(selection)
            return devices[index][0]  # Return VID:PID
        except (ValueError, IndexError):
            print("  Invalid selection — please try again.")
        except KeyboardInterrupt:
            logger.warning("USB device selection interrupted by user")
            raise


def flash_firmware(bitfile: pathlib.Path) -> None:
    """Flash firmware to FPGA board using usbloader."""
    logger.info("Starting firmware flash process")

    if shutil.which("usbloader") is None:
        error_msg = "usbloader not found in PATH — install λConcept usbloader first"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    try:
        vid_pid = select_usb_device()
        logger.info(f"Selected USB device: {vid_pid}")
        print(f"[*] Flashing firmware using VID:PID {vid_pid}")

        subprocess.run(
            f"usbloader --vidpid {vid_pid} -f {bitfile}", shell=True, check=True
        )
        logger.info("Firmware flashed successfully")
        print("[✓] Firmware flashed successfully")

    except subprocess.CalledProcessError as e:
        error_msg = f"Flash failed: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during firmware flash: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def _validate_vfio_prerequisites() -> None:
    """Validate VFIO prerequisites and system configuration."""
    # Check if VFIO modules are loaded
    vfio_modules = ["/sys/module/vfio", "/sys/module/vfio_pci"]
    loaded_modules = [mod for mod in vfio_modules if os.path.exists(mod)]

    if not loaded_modules:
        error_msg = (
            "VFIO modules not loaded. Please load VFIO modules:\n"
            "  sudo modprobe vfio\n"
            "  sudo modprobe vfio-pci"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check if vfio-pci driver is available
    if not os.path.exists("/sys/bus/pci/drivers/vfio-pci"):
        error_msg = (
            "vfio-pci driver not available. Ensure VFIO is enabled in kernel.\n"
            "Check: cat /boot/config-$(uname -r) | grep -i vfio"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check if IOMMU is enabled
    try:
        dmesg_output = run_command("dmesg | grep -i iommu", timeout=10)
        if (
            "IOMMU enabled" not in dmesg_output
            and "AMD-Vi" not in dmesg_output
            and "Intel-IOMMU" not in dmesg_output
        ):
            logger.warning(
                "IOMMU may not be enabled. Check BIOS settings and kernel parameters."
            )
    except Exception:
        logger.debug("Could not check IOMMU status from dmesg")


def _check_device_in_use(bdf: str) -> bool:
    """Check if device is currently in use by checking for open file
    descriptors."""
    try:
        # Check if device has any open file descriptors
        lsof_output = run_command(
            "lsof /dev/vfio/* 2>/dev/null | grep -v COMMAND || true", timeout=5
        )
        if bdf in lsof_output:
            logger.warning(f"Device {bdf} may be in use by another process")
            return True
    except Exception:
        logger.debug("Could not check device usage with lso")
    return False


def _wait_for_device_state(
    bdf: str, expected_driver: Optional[str], max_retries: int = 5
) -> bool:
    """Wait for device to reach expected driver state with retries."""
    import time

    for attempt in range(max_retries):
        try:
            current_driver = get_current_driver(bdf)
            if current_driver == expected_driver:
                return True

            if attempt < max_retries - 1:
                logger.debug(
                    f"Device {bdf} not in expected state (current: {current_driver}, expected: {expected_driver}), retrying in 1s..."
                )
                time.sleep(1)
        except Exception as e:
            logger.debug(
                f"Error checking device state (attempt {
                    attempt + 1}): {e}"
            )
            if attempt < max_retries - 1:
                time.sleep(1)

    return False


def bind_to_vfio(
    bdf: str, vendor: str, device: str, original_driver: Optional[str]
) -> None:
    """Bind PCIe device to vfio-pci driver with enhanced error handling and validation."""
    check_linux_requirement("VFIO device binding")

    if not validate_bdf_format(bdf):
        raise ValueError(
            f"Invalid BDF format: {bdf}. Expected format: DDDD:BB:DD.F (e.g., 0000:03:00.0)"
        )

    # Validate vendor and device IDs
    if not re.match(r"^[0-9a-fA-F]{4}$", vendor):
        raise ValueError(f"Invalid vendor ID format: {vendor}. Expected 4-digit hex.")
    if not re.match(r"^[0-9a-fA-F]{4}$", device):
        raise ValueError(f"Invalid device ID format: {device}. Expected 4-digit hex.")

    logger.info(
        f"Binding device {bdf} (vendor:{vendor} device:{device}) to vfio-pci driver (current driver: {
            original_driver or 'none'})"
    )

    # Early exit if already bound to vfio-pci
    if original_driver == "vfio-pci":
        print(
            "[*] Device already bound to vfio-pci driver, skipping binding process..."
        )
        logger.info(f"Device {bdf} already bound to vfio-pci, skipping binding process")
        return

    print("[*] Binding device to vfio-pci driver...")

    try:
        # Validate VFIO prerequisites
        _validate_vfio_prerequisites()

        # Check if device exists
        device_path = f"/sys/bus/pci/devices/{bdf}"
        if not os.path.exists(device_path):
            error_msg = f"PCIe device {bdf} not found in sysfs"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Check if device is in use
        if _check_device_in_use(bdf):
            logger.warning(
                f"Device {bdf} appears to be in use, proceeding with caution"
            )

        # Check if device ID is already registered with vfio-pci
        device_id_registered = False
        try:
            ids_file = "/sys/bus/pci/drivers/vfio-pci/ids"
            if os.path.exists(ids_file):
                with open(ids_file, "r") as f:
                    registered_ids = f.read()
                    if f"{vendor} {device}" in registered_ids:
                        logger.info(
                            f"Device ID {vendor}:{device} already registered with vfio-pci"
                        )
                        device_id_registered = True
        except (OSError, IOError) as e:
            logger.debug(f"Error checking registered device IDs: {e}")
            # Continue with normal flow if we can't check

        # Register device ID with vfio-pci if not already registered
        if not device_id_registered:
            logger.debug(f"Registering device ID {vendor}:{device} with vfio-pci")
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Use direct file writing instead of shell redirection to
                    # avoid I/O errors
                    new_id_path = "/sys/bus/pci/drivers/vfio-pci/new_id"
                    with open(new_id_path, "w") as f:
                        f.write(f"{vendor} {device}\n")
                    logger.info(
                        f"Successfully registered device ID {vendor}:{device} with vfio-pci"
                    )
                    break
                except (OSError, IOError) as e:
                    if (
                        "File exists" in str(e)
                        or "Invalid argument" in str(e)
                        or "Device or resource busy" in str(e)
                    ):
                        logger.info(
                            f"Device ID {vendor}:{device} already registered with vfio-pci or busy"
                        )
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(
                            f"Failed to register device ID (attempt {
                                attempt + 1}): {e}, retrying..."
                        )
                        import time

                        time.sleep(1)
                    else:
                        logger.error(
                            f"Failed to register device ID after {max_retries} attempts: {e}"
                        )
                        raise RuntimeError(f"Failed to register device ID: {e}")

        # Unbind from current driver if present
        if original_driver:
            logger.debug(f"Unbinding from current driver: {original_driver}")
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Use direct file writing instead of shell redirection
                    unbind_path = f"/sys/bus/pci/devices/{bdf}/driver/unbind"
                    with open(unbind_path, "w") as f:
                        f.write(f"{bdf}\n")
                    logger.info(f"Successfully unbound {bdf} from {original_driver}")

                    # Wait for unbind to complete
                    if _wait_for_device_state(bdf, None, max_retries=3):
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(
                            f"Device still bound after unbind (attempt {
                                attempt + 1}), retrying..."
                        )
                        import time

                        time.sleep(1)
                    else:
                        logger.warning(
                            "Device may still be bound to original driver, continuing..."
                        )
                        break

                except (OSError, IOError) as e:
                    if "No such device" in str(e) or "No such file or directory" in str(
                        e
                    ):
                        logger.info(f"Device {bdf} already unbound")
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(
                            f"Failed to unbind from current driver (attempt {
                                attempt + 1}): {e}, retrying..."
                        )
                        import time

                        time.sleep(1)
                    else:
                        logger.warning(
                            f"Failed to unbind from current driver after {max_retries} attempts: {e}"
                        )
                        # Continue anyway, as the bind might still work

        # Bind to vfio-pci with retries
        logger.debug(f"Binding {bdf} to vfio-pci")
        max_retries = 3
        bind_successful = False

        for attempt in range(max_retries):
            try:
                # Use direct file writing instead of shell redirection
                bind_path = "/sys/bus/pci/drivers/vfio-pci/bind"
                with open(bind_path, "w") as f:
                    f.write(f"{bdf}\n")

                # Verify binding was successful
                if _wait_for_device_state(bdf, "vfio-pci", max_retries=3):
                    logger.info(f"Successfully bound {bdf} to vfio-pci")
                    print("[✓] Device successfully bound to vfio-pci driver")
                    bind_successful = True
                    break
                elif attempt < max_retries - 1:
                    logger.warning(
                        f"Bind command succeeded but device not bound to vfio-pci (attempt {attempt + 1}), retrying..."
                    )
                    import time

                    time.sleep(1)

            except (OSError, IOError) as e:
                if "Device or resource busy" in str(e):
                    logger.warning(
                        f"Device {bdf} is busy (attempt {
                            attempt + 1})"
                    )
                    if attempt < max_retries - 1:
                        import time

                        time.sleep(2)  # Longer wait for busy devices
                        continue
                elif "No such device" in str(e) or "No such file or directory" in str(
                    e
                ):
                    logger.error(f"Device {bdf} disappeared during binding")
                    raise RuntimeError(f"Device {bdf} not found during binding")
                elif attempt < max_retries - 1:
                    logger.warning(
                        f"Failed to bind to vfio-pci (attempt {attempt + 1}): {e}, retrying..."
                    )
                    import time

                    time.sleep(1)
                else:
                    # Final attempt failed, check if device is actually bound
                    current_driver = get_current_driver(bdf)
                    if current_driver == "vfio-pci":
                        logger.info(
                            f"Device {bdf} is bound to vfio-pci despite bind command error"
                        )
                        print("[✓] Device is bound to vfio-pci driver")
                        bind_successful = True
                        break
                    else:
                        logger.error(
                            f"Failed to bind to vfio-pci after {max_retries} attempts: {e}"
                        )
                        raise RuntimeError(f"Failed to bind to vfio-pci: {e}")

        if not bind_successful:
            error_msg = (
                f"Failed to bind device {bdf} to vfio-pci after {max_retries} attempts"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Final verification
        final_driver = get_current_driver(bdf)
        if final_driver != "vfio-pci":
            error_msg = (
                f"Device {bdf} not bound to vfio-pci (current driver: {final_driver})"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    except (OSError, IOError) as e:
        error_msg = f"Failed to bind device to vfio-pci: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during vfio binding: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def restore_original_driver(bdf: str, original_driver: Optional[str]) -> None:
    """Restore the original driver binding for the PCIe device with enhanced error handling."""
    if not validate_bdf_format(bdf):
        logger.warning(f"Invalid BDF format during restore: {bdf}")
        return

    logger.info(
        f"Restoring original driver binding for {bdf} (target driver: {
            original_driver or 'none'})"
    )
    print("[*] Restoring original driver binding...")

    try:
        # Check if device exists
        device_path = f"/sys/bus/pci/devices/{bdf}"
        if not os.path.exists(device_path):
            logger.warning(
                f"Device {bdf} not found during restore, may have been removed"
            )
            return

        # Check current driver state
        current_driver = get_current_driver(bdf)
        logger.debug(f"Current driver for {bdf}: {current_driver or 'none'}")

        # Unbind from vfio-pci if currently bound
        if current_driver == "vfio-pci":
            logger.debug(f"Unbinding {bdf} from vfio-pci")
            max_retries = 3
            unbind_successful = False

            for attempt in range(max_retries):
                try:
                    # Use direct file writing instead of shell redirection
                    unbind_path = "/sys/bus/pci/drivers/vfio-pci/unbind"
                    with open(unbind_path, "w") as f:
                        f.write(f"{bdf}\n")

                    # Wait for unbind to complete
                    if _wait_for_device_state(bdf, None, max_retries=3):
                        logger.info(f"Successfully unbound {bdf} from vfio-pci")
                        unbind_successful = True
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(
                            f"Device still bound to vfio-pci (attempt {attempt + 1}), retrying..."
                        )
                        import time

                        time.sleep(1)

                except (OSError, IOError) as e:
                    if "No such device" in str(e) or "No such file or directory" in str(
                        e
                    ):
                        logger.info(f"Device {bdf} already unbound from vfio-pci")
                        unbind_successful = True
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(
                            f"Failed to unbind from vfio-pci (attempt {attempt + 1}): {e}, retrying..."
                        )
                        import time

                        time.sleep(1)
                    else:
                        logger.warning(
                            f"Failed to unbind from vfio-pci after {max_retries} attempts: {e}"
                        )
                        # Continue with restore attempt anyway
                        break

            if not unbind_successful and get_current_driver(bdf) == "vfio-pci":
                logger.warning(
                    f"Device {bdf} still bound to vfio-pci, restore may fail"
                )
        else:
            logger.info(
                f"Device {bdf} not bound to vfio-pci (current: {current_driver or 'none'})"
            )

        # Bind back to original driver if it existed
        if original_driver:
            # Check if original driver is available
            driver_path = f"/sys/bus/pci/drivers/{original_driver}"
            if not os.path.exists(driver_path):
                logger.warning(
                    f"Original driver {original_driver} not available for restore"
                )
                print(f"Warning: Original driver {original_driver} not available")
                return

            logger.debug(f"Binding {bdf} back to {original_driver}")
            max_retries = 3
            restore_successful = False

            for attempt in range(max_retries):
                try:
                    # Use direct file writing instead of shell redirection
                    bind_path = f"/sys/bus/pci/drivers/{original_driver}/bind"
                    with open(bind_path, "w") as f:
                        f.write(f"{bdf}\n")

                    # Verify restore was successful
                    if _wait_for_device_state(bdf, original_driver, max_retries=3):
                        logger.info(f"Successfully restored {bdf} to {original_driver}")
                        print(f"[✓] Device restored to {original_driver} driver")
                        restore_successful = True
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(
                            f"Restore command succeeded but device not bound to {original_driver} (attempt {
                                attempt + 1}), retrying..."
                        )
                        import time

                        time.sleep(1)

                except (OSError, IOError) as e:
                    if "Device or resource busy" in str(e):
                        logger.warning(
                            f"Device {bdf} is busy during restore (attempt {
                                attempt + 1})"
                        )
                        if attempt < max_retries - 1:
                            import time

                            time.sleep(2)
                            continue
                    elif "No such device" in str(
                        e
                    ) or "No such file or directory" in str(e):
                        logger.warning(f"Device {bdf} not found during restore")
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(
                            f"Failed to restore to {original_driver} (attempt {
                                attempt + 1}): {e}, retrying..."
                        )
                        import time

                        time.sleep(1)
                    else:
                        logger.warning(
                            f"Failed to restore to {original_driver} after {max_retries} attempts: {e}"
                        )
                        break

            if not restore_successful:
                final_driver = get_current_driver(bdf)
                if final_driver == original_driver:
                    logger.info(
                        f"Device {bdf} is bound to {original_driver} despite restore errors"
                    )
                    print(f"[✓] Device is bound to {original_driver} driver")
                else:
                    logger.warning(
                        f"Failed to restore {bdf} to {original_driver}, current driver: {
                            final_driver or 'none'}"
                    )
                    print(
                        f"Warning: Failed to restore to {original_driver}, current driver: {
                            final_driver or 'none'}"
                    )
        else:
            logger.info(f"No original driver to restore for {bdf}")
            print("[*] No original driver to restore")

    except (OSError, IOError) as e:
        logger.warning(f"Failed to restore original driver for {bdf}: {e}")
        print(f"Warning: Failed to restore original driver: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error during driver restore for {bdf}: {e}")
        print(f"Warning: Unexpected error during driver restore: {e}")


def _validate_vfio_device_access(vfio_device: str, bdf: str) -> None:
    """Validate VFIO device access and permissions."""
    # Check if VFIO device exists
    if not os.path.exists(vfio_device):
        error_msg = f"VFIO device {vfio_device} not found"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check if /dev/vfio/vfio exists (VFIO container device)
    vfio_container = "/dev/vfio/vfio"
    if not os.path.exists(vfio_container):
        error_msg = f"VFIO container device {vfio_container} not found"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check device permissions
    try:
        import stat

        vfio_stat = os.stat(vfio_device)
        if not (vfio_stat.st_mode & stat.S_IRGRP) or not (
            vfio_stat.st_mode & stat.S_IWGRP
        ):
            logger.warning(
                f"VFIO device {vfio_device} may not have proper group permissions"
            )
    except OSError as e:
        logger.warning(f"Could not check VFIO device permissions: {e}")

    # Verify device is actually bound to vfio-pci
    current_driver = get_current_driver(bdf)
    if current_driver != "vfio-pci":
        error_msg = (
            f"Device {bdf} not bound to vfio-pci (current: {current_driver or 'none'})"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def _validate_container_environment() -> None:
    """Validate container runtime environment."""
    # Check if podman is available
    if shutil.which("podman") is None:
        error_msg = "Podman not found in PATH. Please install Podman container runtime."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check if container image exists
    try:
        result = run_command(
            "podman images --format '{{.Repository}}:{{.Tag}}' | grep '^pcileech-fw-generator:'",
            timeout=10,
        )
        if not result:
            # Container image not found, try to build it automatically
            logger.info(
                "Container image 'pcileech-fw-generator' not found. Building it now..."
            )
            print(
                "[*] Container image 'pcileech-fw-generator' not found. Building it now..."
            )

            try:
                # Use the proper build script which handles the container
                # building correctly
                build_script_path = "scripts/build_container.sh"
                if os.path.exists(build_script_path):
                    logger.info("Using build script for container creation")
                    build_result = subprocess.run(
                        f"bash {build_script_path} --tag pcileech-fw-generator:latest",
                        shell=True,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                else:
                    # Fallback to direct container build
                    build_result = subprocess.run(
                        "podman build -t pcileech-fw-generator:latest -f Containerfile .",
                        shell=True,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                logger.info("Container image built successfully")
                print("[✓] Container image built successfully")
            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to build container image automatically: {
                    e.stderr}\nPlease build manually with: make container"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
    except subprocess.CalledProcessError:
        # If we can't check, try to build anyway
        logger.info("Could not check container image status. Attempting to build...")
        print("[*] Could not check container image status. Attempting to build...")

        try:
            build_script_path = "scripts/build_container.sh"
            if os.path.exists(build_script_path):
                logger.info("Using build script for container creation")
                build_result = subprocess.run(
                    f"bash {build_script_path} --tag pcileech-fw-generator:latest",
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            else:
                # Fallback to direct container build
                subprocess.run(
                    "podman build -t pcileech-fw-generator:latest -f Containerfile .",
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            logger.info("Container image built successfully")
            print("[✓] Container image built successfully")
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to build container image: {
                e.stderr}\nPlease build manually with: make container"
            logger.error(error_msg)
            raise RuntimeError(error_msg)


def run_build_container(
    bdf: str, board: str, vfio_device: str, args: argparse.Namespace
) -> None:
    """Run the firmware build in a Podman container with enhanced validation and error handling."""
    if not validate_bdf_format(bdf):
        raise ValueError(
            f"Invalid BDF format: {bdf}. Expected format: DDDD:BB:DD.F (e.g., 0000:03:00.0)"
        )

    # Log advanced features being used
    advanced_features = []
    if args.advanced_sv:
        advanced_features.append("Advanced SystemVerilog Generation")
    if args.enable_variance:
        advanced_features.append("Manufacturing Variance Simulation")
    if args.device_type != "generic":
        advanced_features.append(f"Device-specific optimizations ({args.device_type})")

    if advanced_features:
        logger.info(
            f"Advanced features enabled: {
                ', '.join(advanced_features)}"
        )
        print(f"[*] Advanced features: {', '.join(advanced_features)}")

    logger.info(f"Starting container build for device {bdf} on board {board}")

    # Validate container environment
    _validate_container_environment()

    # Ensure output directory exists with proper permissions
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Check output directory permissions
    if not os.access(output_dir, os.W_OK):
        error_msg = f"Output directory {output_dir} is not writable"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Validate VFIO device access
    _validate_vfio_device_access(vfio_device, bdf)

    # Build the build.py command with all arguments - use modular build system
    # if available
    build_cmd_parts = [f"sudo python3 /app/src/build.py --bdf {bdf} --board {board}"]

    # Add advanced features arguments
    if args.advanced_sv:
        build_cmd_parts.append("--advanced-sv")

    if args.device_type != "generic":
        build_cmd_parts.append(f"--device-type {args.device_type}")

    if args.enable_variance:
        build_cmd_parts.append("--enable-variance")

    if args.disable_power_management:
        build_cmd_parts.append("--disable-power-management")

    if args.disable_error_handling:
        build_cmd_parts.append("--disable-error-handling")

    if args.disable_performance_counters:
        build_cmd_parts.append("--disable-performance-counters")

    if args.behavior_profile_duration != 30:
        build_cmd_parts.append(
            f"--behavior-profile-duration {args.behavior_profile_duration}"
        )

    " ".join(build_cmd_parts)

    # Construct Podman command
    container_cmd = textwrap.dedent(
        """
        podman run --rm -it --privileged \
          --device={vfio_device} \
          --device=/dev/vfio/vfio \
          -v {os.getcwd()}/output:/app/output \
          pcileech-fw-generator:latest \
          {build_cmd}
    """
    ).strip()

    logger.debug(f"Container command: {container_cmd}")
    print("[*] Launching build container...")
    start_time = time.time()

    try:
        subprocess.run(container_cmd, shell=True, check=True)
        elapsed_time = time.time() - start_time
        logger.info(
            f"Build completed successfully in {
                elapsed_time:.1f} seconds"
        )
        print(f"[✓] Build completed in {elapsed_time:.1f} seconds")

    except subprocess.CalledProcessError as e:
        elapsed_time = time.time() - start_time
        error_msg = f"Container build failed after {
            elapsed_time:.1f} seconds: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        elapsed_time = time.time() - start_time
        error_msg = f"Unexpected error during container build after {
            elapsed_time:.1f} seconds: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def ensure_git_repo(repo_url: str, local_dir: str, update: bool = False) -> str:
    """
    Ensure that the git repository is available locally.

    Args:
        repo_url (str): URL of the git repository
        local_dir (str): Local directory to clone/pull the repository
        update (bool): Whether to update the repository if it already exists

    Returns:
        str: Path to the local repository
    """
    # Create cache directory if it doesn't exist
    os.makedirs(os.path.dirname(local_dir), exist_ok=True)

    # Check if repository already exists as a valid git repository
    if os.path.exists(os.path.join(local_dir, ".git")):
        logger.info(f"Repository already exists at {local_dir}")

        # Update repository if requested
        if update:
            try:
                logger.info(f"Updating repository at {local_dir}")
                print(f"[*] Updating repository at {local_dir}")

                # Get current directory
                current_dir = os.getcwd()

                # Change to repository directory
                os.chdir(local_dir)

                # Pull latest changes
                result = subprocess.run(
                    "git pull",
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                # Change back to original directory
                os.chdir(current_dir)

                logger.info(
                    f"Repository updated successfully: {
                        result.stdout.strip()}"
                )
                print("[✓] Repository updated successfully")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to update repository: {e.stderr}")
                print(f"[!] Warning: Failed to update repository: {e.stderr}")
    else:
        # Check if directory exists but is not a git repository
        if os.path.exists(local_dir):
            logger.info(f"Directory exists but is not a git repository: {local_dir}")
            print(f"[*] Removing existing directory: {local_dir}")

            # Remove the directory to allow fresh clone
            import shutil

            try:
                shutil.rmtree(local_dir)
            except Exception as e:
                logger.warning(f"Failed to remove directory: {e}")
                print(f"[!] Warning: Failed to remove directory: {e}")
                # Continue anyway, git clone might still work

        # Clone repository
        try:
            logger.info(f"Cloning repository {repo_url} to {local_dir}")
            print(f"[*] Cloning repository {repo_url} to {local_dir}")

            result = subprocess.run(
                f"git clone {repo_url} {local_dir}",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            logger.info("Repository cloned successfully")
            print("[✓] Repository cloned successfully")
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to clone repository: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    # Return path to repository
    return local_dir


def validate_environment() -> None:
    """Validate that the environment is properly set up."""
    if os.geteuid() != 0:
        error_msg = "This script requires root privileges. Run with sudo."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check if git is available
    if shutil.which("git") is None:
        error_msg = "Git not found in PATH. Please install Git first."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check if Podman is available
    if shutil.which("podman") is None:
        error_msg = "Podman not found in PATH. Please install Podman first."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check if Vivado is available
    try:
        # Import vivado_utils from src directory
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from src.vivado_utils import find_vivado_installation, get_vivado_search_paths

        vivado_info = find_vivado_installation()
        if vivado_info:
            logger.info(
                f"Found Vivado {
                    vivado_info['version']} at {
                    vivado_info['path']}"
            )
            print(f"[✓] Vivado {vivado_info['version']} detected")
        else:
            # Show what paths were checked using the utility function
            checked_paths = get_vivado_search_paths()
            error_msg = "Vivado not found. Checked paths:\n" + "\n".join(
                f"  • {path}" for path in checked_paths
            )
            logger.error(error_msg)
            print(f"[✗] {error_msg}")

            # Allow user to skip
            try:
                response = (
                    input("\nWould you like to continue without Vivado? (y/N): ")
                    .strip()
                    .lower()
                )
                if response in ["y", "yes"]:
                    print("[!] Continuing without Vivado - some features may not work")
                    logger.warning("User chose to continue without Vivado")
                else:
                    raise RuntimeError(
                        "Vivado is required. Please install Vivado and try again."
                    )
            except (KeyboardInterrupt, EOFError):
                raise RuntimeError(
                    "Vivado is required. Please install Vivado and try again."
                )
    except ImportError:
        error_msg = (
            "Could not import vivado_utils. Please ensure Vivado is properly installed."
        )
        logger.error(error_msg)
        print(f"[✗] {error_msg}")

        # Allow user to skip
        try:
            response = (
                input("\nWould you like to continue without Vivado? (y/N): ")
                .strip()
                .lower()
            )
            if response in ["y", "yes"]:
                print("[!] Continuing without Vivado - some features may not work")
                logger.warning("User chose to continue without Vivado")
            else:
                raise RuntimeError(
                    "Vivado is required. Please install Vivado and try again."
                )
        except (KeyboardInterrupt, EOFError):
            raise RuntimeError(
                "Vivado is required. Please install Vivado and try again."
            )

    # Check if container image exists
    try:
        result = run_command(
            "podman images pcileech-fw-generator --format '{{.Repository}}'"
        )
        if "pcileech-fw-generator" not in result:
            # Container image not found, try to build it
            logger.info(
                "Container image 'pcileech-fw-generator' not found. Building it now..."
            )
            print(
                "[*] Container image 'pcileech-fw-generator' not found. Building it now..."
            )

            try:
                # Use the proper build script which handles the container
                # building correctly
                build_script_path = "scripts/build_container.sh"
                if os.path.exists(build_script_path):
                    logger.info("Using build script for container creation")
                    build_result = subprocess.run(
                        f"bash {build_script_path} --tag pcileech-fw-generator:latest",
                        shell=True,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                else:
                    # Fallback to direct container build
                    build_result = subprocess.run(
                        "podman build -t pcileech-fw-generator:latest -f Containerfile .",
                        shell=True,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                logger.info("Container image built successfully")
                print("[✓] Container image built successfully")
            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to build container image: {e.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Error checking container image: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def main() -> int:
    """Main entry point for the firmware generator"""
    bdf = None
    original_driver = None

    try:
        logger.info("Starting PCILeech firmware generation process")
        validate_environment()

        # Ensure pcileech-fpga repository is available
        repo_dir = os.path.join(REPO_CACHE_DIR, "pcileech-fpga")
        pcileech_fpga_dir = ensure_git_repo(PCILEECH_FPGA_REPO, repo_dir, update=False)
        logger.info(f"Using pcileech-fpga repository at {pcileech_fpga_dir}")

        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description="Generate DMA firmware from donor PCIe device",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent(
                """
                Examples:
                  # Basic usage
                  sudo python3 generate.py --board 75t
                  sudo python3 generate.py --board 100t --flash

                  # Advanced SystemVerilog generation
                  sudo python3 generate.py --board 75t --advanced-sv --device-type network

                  # Manufacturing variance simulation
                  sudo python3 generate.py --board 100t --enable-variance --behavior-profile-duration 60

                  # Advanced features with selective disabling
                  sudo python3 generate.py --board 75t --advanced-sv --disable-power-management --disable-error-handling

                  # Full advanced configuration
                  sudo python3 generate.py --board 100t --advanced-sv --device-type storage --enable-variance --behavior-profile-duration 45 --flash
            """
            ),
        )

        # Basic options
        parser.add_argument(
            "--tui",
            action="store_true",
            help="Launch TUI (Text User Interface) mode",
        )

        parser.add_argument(
            "--flash",
            action="store_true",
            help="Flash output/firmware.bin with usbloader after build",
        )

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
            help="Target FPGA board type (default: 35t/Squirrel)",
        )

        # Advanced SystemVerilog Generation
        parser.add_argument(
            "--advanced-sv",
            action="store_true",
            help="Enable advanced SystemVerilog generation with enhanced features",
        )

        parser.add_argument(
            "--device-type",
            choices=["network", "storage", "graphics", "audio", "generic"],
            default="generic",
            help="Device type for specialized optimizations (default: generic)",
        )

        # Manufacturing Variance Simulation
        parser.add_argument(
            "--enable-variance",
            action="store_true",
            help="Enable manufacturing variance simulation for realistic timing",
        )

        # Feature Control
        parser.add_argument(
            "--disable-power-management",
            action="store_true",
            help="Disable power management features in advanced generation",
        )

        parser.add_argument(
            "--disable-error-handling",
            action="store_true",
            help="Disable error handling features in advanced generation",
        )

        parser.add_argument(
            "--disable-performance-counters",
            action="store_true",
            help="Disable performance counter features in advanced generation",
        )

        # Behavior Profiling
        parser.add_argument(
            "--behavior-profile-duration",
            type=int,
            default=30,
            help="Duration for behavior profiling in seconds (default: 30)",
        )

        # Donor dump functionality
        parser.add_argument(
            "--donor-dump",
            action="store_true",
            help="Extract donor device parameters using kernel module before generation",
        )

        parser.add_argument(
            "--auto-install-headers",
            action="store_true",
            help="Automatically install kernel headers if missing (for donor dump)",
        )

        args = parser.parse_args()

        # Check if TUI mode is requested
        if args.tui:
            try:
                # Import and launch TUI
                from src.tui.main import PCILeechTUI

                app = PCILeechTUI()
                app.run()
                return 0
            except ImportError:
                error_msg = "TUI dependencies not installed. Install with: pip install textual rich psutil"
                logger.error(error_msg)
                print(f"[✗] {error_msg}")
                return 1
            except Exception as e:
                error_msg = f"Failed to launch TUI: {e}"
                logger.error(error_msg)
                print(f"[✗] {error_msg}")
                return 1

        # Enhanced logging with advanced features
        config_info = [f"board={args.board}", f"flash={args.flash}"]
        if args.advanced_sv:
            config_info.append("advanced_sv=True")
        if args.device_type != "generic":
            config_info.append(f"device_type={args.device_type}")
        if args.enable_variance:
            config_info.append("variance=True")
        if args.disable_power_management:
            config_info.append("no_power_mgmt=True")
        if args.disable_error_handling:
            config_info.append("no_error_handling=True")
        if args.disable_performance_counters:
            config_info.append("no_perf_counters=True")
        if args.behavior_profile_duration != 30:
            config_info.append(
                f"profile_duration={
                    args.behavior_profile_duration}s"
            )

        logger.info(f"Configuration: {', '.join(config_info)}")

        # List and select PCIe device
        devices = list_pci_devices()
        if not devices:
            error_msg = "No PCIe devices found"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        selected_device = choose_device(devices)
        bdf = selected_device["bd"]
        vendor = selected_device["ven"]
        device = selected_device["dev"]

        logger.info(f"Selected device: {bdf} (VID:{vendor} DID:{device})")
        print(f"\nSelected device: {bdf} (VID:{vendor} DID:{device})")

        # Get device information
        iommu_group = get_iommu_group(bdf)
        vfio_device = f"/dev/vfio/{iommu_group}"
        original_driver = get_current_driver(bdf)

        logger.info(
            f"Device info - IOMMU group: {iommu_group}, Current driver: {original_driver or 'none'}"
        )
        print(f"IOMMU group: {iommu_group}")
        print(f"Current driver: {original_driver or 'none'}")

        # Extract donor device parameters if requested
        donor_info = None
        if args.donor_dump:
            if DonorDumpManager is None:
                error_msg = "Donor dump functionality not available. Check src/donor_dump_manager.py"
                logger.error(error_msg)
                print(f"[✗] {error_msg}")
                return 1

            try:
                print(f"\n[•] Extracting donor device parameters for {bdf}...")
                logger.info(f"Starting donor dump extraction for {bdf}")

                dump_manager = DonorDumpManager()
                donor_info = dump_manager.setup_module(
                    bdf, auto_install_headers=args.auto_install_headers
                )

                print("[✓] Donor device parameters extracted successfully")
                logger.info("Donor dump extraction completed successfully")

                # Log key parameters
                key_params = [
                    "vendor_id",
                    "device_id",
                    "class_code",
                    "bar_size",
                    "mpc",
                    "mpr",
                ]
                for param in key_params:
                    if param in donor_info:
                        logger.info(f"  {param}: {donor_info[param]}")

                # Save donor info to file for container use
                import json

                donor_info_path = pathlib.Path("output/donor_info.json")
                donor_info_path.parent.mkdir(exist_ok=True)
                with open(donor_info_path, "w") as f:
                    json.dump(donor_info, f, indent=2)
                logger.info(f"Donor info saved to {donor_info_path}")

            except DonorDumpError as e:
                error_msg = f"Donor dump failed: {e}"
                logger.error(error_msg)
                print(f"[✗] {error_msg}")

                # Ask user if they want to continue without donor dump
                response = input("Continue without donor dump? [y/N]: ").strip().lower()
                if response not in ["y", "yes"]:
                    return 1
                print("[•] Continuing without donor dump...")
            except Exception as e:
                error_msg = f"Unexpected error during donor dump: {e}"
                logger.error(error_msg)
                print(f"[✗] {error_msg}")
                return 1

        # Bind device to vfio-pci
        bind_to_vfio(bdf, vendor, device, original_driver)

        # Run the build container
        run_build_container(bdf, args.board, vfio_device, args)

        # Flash firmware if requested
        if args.flash:
            firmware_path = pathlib.Path("output/firmware.bin")
            if not firmware_path.exists():
                error_msg = "ERROR: firmware.bin not found in ./output directory"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            flash_firmware(firmware_path)

        logger.info("Firmware generation process completed successfully")
        print("[✓] Process completed successfully")
        return 0

    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        print("\n[!] Process interrupted by user")
        # Don't use sys.exit() - let finally block handle cleanup
        return 1
    except Exception as e:
        logger.error(f"Fatal error during firmware generation: {e}")
        print(f"\n[✗] Fatal error: {e}")
        # Don't use sys.exit() - let finally block handle cleanup
        return 1
    finally:
        # Always attempt to restore the original driver if we have the info
        if bdf and original_driver is not None:
            try:
                restore_original_driver(bdf, original_driver)
                logger.info("Driver restoration completed successfully")
            except Exception as e:
                logger.error(f"Failed to restore driver during cleanup: {e}")
                print(f"[!] Warning: Failed to restore driver during cleanup: {e}")

        # Ensure any temporary files are cleaned up
        try:
            # Clean up any temporary VFIO state if needed
            logger.debug("Cleanup completed")
        except Exception as e:
            logger.warning(f"Minor cleanup issue: {e}")


if __name__ == "__main__":
    sys.exit(main())
