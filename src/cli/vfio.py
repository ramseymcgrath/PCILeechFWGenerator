"""VFIO device binding and management with context manager support."""

import os
import re
import time
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Generator

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.shell import Shell
from utils.logging import get_logger

logger = get_logger(__name__)


def validate_bdf_format(bdf: str) -> bool:
    """Validate BDF (Bus:Device.Function) format.
    
    Args:
        bdf: BDF string to validate
        
    Returns:
        True if valid, False otherwise
    """
    bdf_pattern = re.compile(r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]$")
    return bool(bdf_pattern.match(bdf))


def check_linux_requirement(operation: str) -> None:
    """Check if operation requires Linux and raise error if not available."""
    import platform
    if platform.system().lower() != "linux":
        raise RuntimeError(
            f"{operation} requires Linux. "
            f"Current platform: {platform.system()}. "
            "Please run this on a Linux system with VFIO support."
        )


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


def read_ids(bdf: str) -> tuple[str, str]:
    """Read vendor and device IDs from a PCIe device.
    
    Args:
        bdf: Device BDF string
        
    Returns:
        Tuple of (vendor_id, device_id)
    """
    device_path = f"/sys/bus/pci/devices/{bdf}"
    
    with open(f"{device_path}/vendor", "r") as f:
        vendor = f.read().strip().replace("0x", "")
    
    with open(f"{device_path}/device", "r") as f:
        device = f.read().strip().replace("0x", "")
    
    return vendor, device


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
    shell = Shell()
    try:
        dmesg_output = shell.run("dmesg | grep -i iommu", timeout=10)
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


def _wait_for_device_state(
    bdf: str, expected_driver: Optional[str], max_retries: int = 5
) -> bool:
    """Wait for device to reach expected driver state with retries."""
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
            logger.debug(f"Error checking device state (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)

    return False


def bind_to_vfio(bdf: str, vendor: str, device: str, original_driver: Optional[str]) -> None:
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
        f"Binding device {bdf} (vendor:{vendor} device:{device}) to vfio-pci driver (current driver: {original_driver or 'none'})"
    )

    # Early exit if already bound to vfio-pci
    if original_driver == "vfio-pci":
        print("[*] Device already bound to vfio-pci driver, skipping binding process...")
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

        shell = Shell()

        # Register device ID with vfio-pci if not already registered
        logger.debug(f"Registering device ID {vendor}:{device} with vfio-pci")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                shell.write_file("/sys/bus/pci/drivers/vfio-pci/new_id", f"{vendor} {device}\n")
                logger.info(f"Successfully registered device ID {vendor}:{device} with vfio-pci")
                break
            except RuntimeError as e:
                if (
                    "File exists" in str(e)
                    or "Invalid argument" in str(e)
                    or "Device or resource busy" in str(e)
                ):
                    logger.info(f"Device ID {vendor}:{device} already registered with vfio-pci or busy")
                    break
                elif attempt < max_retries - 1:
                    logger.warning(f"Failed to register device ID (attempt {attempt + 1}): {e}, retrying...")
                    time.sleep(1)
                else:
                    logger.error(f"Failed to register device ID after {max_retries} attempts: {e}")
                    raise RuntimeError(f"Failed to register device ID: {e}")

        # Unbind from current driver if present
        if original_driver:
            logger.debug(f"Unbinding from current driver: {original_driver}")
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    shell.write_file(f"/sys/bus/pci/devices/{bdf}/driver/unbind", f"{bdf}\n")
                    logger.info(f"Successfully unbound {bdf} from {original_driver}")

                    # Wait for unbind to complete
                    if _wait_for_device_state(bdf, None, max_retries=3):
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"Device still bound after unbind (attempt {attempt + 1}), retrying...")
                        time.sleep(1)
                    else:
                        logger.warning("Device may still be bound to original driver, continuing...")
                        break

                except RuntimeError as e:
                    if "No such device" in str(e) or "No such file or directory" in str(e):
                        logger.info(f"Device {bdf} already unbound")
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"Failed to unbind from current driver (attempt {attempt + 1}): {e}, retrying...")
                        time.sleep(1)
                    else:
                        logger.warning(f"Failed to unbind from current driver after {max_retries} attempts: {e}")
                        # Continue anyway, as the bind might still work

        # Bind to vfio-pci with retries
        logger.debug(f"Binding {bdf} to vfio-pci")
        max_retries = 3
        bind_successful = False

        for attempt in range(max_retries):
            try:
                shell.write_file("/sys/bus/pci/drivers/vfio-pci/bind", f"{bdf}\n")

                # Verify binding was successful
                if _wait_for_device_state(bdf, "vfio-pci", max_retries=3):
                    logger.info(f"Successfully bound {bdf} to vfio-pci")
                    print("[✓] Device successfully bound to vfio-pci driver")
                    bind_successful = True
                    break
                elif attempt < max_retries - 1:
                    logger.warning(f"Bind command succeeded but device not bound to vfio-pci (attempt {attempt + 1}), retrying...")
                    time.sleep(1)

            except RuntimeError as e:
                if "Device or resource busy" in str(e):
                    logger.warning(f"Device {bdf} is busy (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Longer wait for busy devices
                        continue
                elif "No such device" in str(e) or "No such file or directory" in str(e):
                    logger.error(f"Device {bdf} disappeared during binding")
                    raise RuntimeError(f"Device {bdf} not found during binding")
                elif attempt < max_retries - 1:
                    logger.warning(f"Failed to bind to vfio-pci (attempt {attempt + 1}): {e}, retrying...")
                    time.sleep(1)
                else:
                    # Final attempt failed, check if device is actually bound
                    current_driver = get_current_driver(bdf)
                    if current_driver == "vfio-pci":
                        logger.info(f"Device {bdf} is bound to vfio-pci despite bind command error")
                        print("[✓] Device is bound to vfio-pci driver")
                        bind_successful = True
                        break
                    else:
                        logger.error(f"Failed to bind to vfio-pci after {max_retries} attempts: {e}")
                        raise RuntimeError(f"Failed to bind to vfio-pci: {e}")

        if not bind_successful:
            error_msg = f"Failed to bind device {bdf} to vfio-pci after {max_retries} attempts"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Final verification
        final_driver = get_current_driver(bdf)
        if final_driver != "vfio-pci":
            error_msg = f"Device {bdf} not bound to vfio-pci (current driver: {final_driver})"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    except Exception as e:
        error_msg = f"Failed to bind device to vfio-pci: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def restore_original_driver(bdf: str, original_driver: Optional[str]) -> None:
    """Restore the original driver binding for the PCIe device with enhanced error handling."""
    if not validate_bdf_format(bdf):
        logger.warning(f"Invalid BDF format during restore: {bdf}")
        return

    logger.info(f"Restoring original driver binding for {bdf} (target driver: {original_driver or 'none'})")
    print("[*] Restoring original driver binding...")

    try:
        # Check if device exists
        device_path = f"/sys/bus/pci/devices/{bdf}"
        if not os.path.exists(device_path):
            logger.warning(f"Device {bdf} not found during restore, may have been removed")
            return

        # Check current driver state
        current_driver = get_current_driver(bdf)
        logger.debug(f"Current driver for {bdf}: {current_driver or 'none'}")

        shell = Shell()

        # Unbind from vfio-pci if currently bound
        if current_driver == "vfio-pci":
            logger.debug(f"Unbinding {bdf} from vfio-pci")
            max_retries = 3
            unbind_successful = False

            for attempt in range(max_retries):
                try:
                    shell.write_file("/sys/bus/pci/drivers/vfio-pci/unbind", f"{bdf}\n")

                    # Wait for unbind to complete
                    if _wait_for_device_state(bdf, None, max_retries=3):
                        logger.info(f"Successfully unbound {bdf} from vfio-pci")
                        unbind_successful = True
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"Device still bound to vfio-pci (attempt {attempt + 1}), retrying...")
                        time.sleep(1)

                except RuntimeError as e:
                    if "No such device" in str(e) or "No such file or directory" in str(e):
                        logger.info(f"Device {bdf} already unbound from vfio-pci")
                        unbind_successful = True
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"Failed to unbind from vfio-pci (attempt {attempt + 1}): {e}, retrying...")
                        time.sleep(1)
                    else:
                        logger.warning(f"Failed to unbind from vfio-pci after {max_retries} attempts: {e}")
                        # Continue with restore attempt anyway
                        break

            if not unbind_successful and get_current_driver(bdf) == "vfio-pci":
                logger.warning(f"Device {bdf} still bound to vfio-pci, restore may fail")
        else:
            logger.info(f"Device {bdf} not bound to vfio-pci (current: {current_driver or 'none'})")

        # Bind back to original driver if it existed
        if original_driver:
            # Check if original driver is available
            driver_path = f"/sys/bus/pci/drivers/{original_driver}"
            if not os.path.exists(driver_path):
                logger.warning(f"Original driver {original_driver} not available for restore")
                print(f"Warning: Original driver {original_driver} not available")
                return

            logger.debug(f"Binding {bdf} back to {original_driver}")
            max_retries = 3
            restore_successful = False

            for attempt in range(max_retries):
                try:
                    shell.write_file(f"/sys/bus/pci/drivers/{original_driver}/bind", f"{bdf}\n")

                    # Verify restore was successful
                    if _wait_for_device_state(bdf, original_driver, max_retries=3):
                        logger.info(f"Successfully restored {bdf} to {original_driver}")
                        print(f"[✓] Device restored to {original_driver} driver")
                        restore_successful = True
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"Restore command succeeded but device not bound to {original_driver} (attempt {attempt + 1}), retrying...")
                        time.sleep(1)

                except RuntimeError as e:
                    if "Device or resource busy" in str(e):
                        logger.warning(f"Device {bdf} is busy during restore (attempt {attempt + 1})")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                    elif "No such device" in str(e) or "No such file or directory" in str(e):
                        logger.warning(f"Device {bdf} not found during restore")
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"Failed to restore to {original_driver} (attempt {attempt + 1}): {e}, retrying...")
                        time.sleep(1)
                    else:
                        logger.warning(f"Failed to restore to {original_driver} after {max_retries} attempts: {e}")
                        break

            if not restore_successful:
                final_driver = get_current_driver(bdf)
                if final_driver == original_driver:
                    logger.info(f"Device {bdf} is bound to {original_driver} despite restore errors")
                    print(f"[✓] Device is bound to {original_driver} driver")
                else:
                    logger.warning(f"Failed to restore {bdf} to {original_driver}, current driver: {final_driver or 'none'}")
                    print(f"Warning: Failed to restore to {original_driver}, current driver: {final_driver or 'none'}")
        else:
            logger.info(f"No original driver to restore for {bdf}")
            print("[*] No original driver to restore")

    except Exception as e:
        logger.warning(f"Failed to restore original driver for {bdf}: {e}")
        print(f"Warning: Failed to restore original driver: {e}")


@contextmanager
def VFIOBinder(bdf: str) -> Generator[Path, None, None]:
    """Context manager for VFIO device binding with guaranteed cleanup.
    
    Args:
        bdf: Device BDF string
        
    Yields:
        Path to VFIO device (/dev/vfio/{group})
        
    Example:
        with VFIOBinder("0000:03:00.0") as vfio_dev:
            # Use vfio_dev for container operations
            run_build_container(cfg, vfio_dev)
    """
    if not validate_bdf_format(bdf):
        raise ValueError(f"Invalid BDF format: {bdf}")
    
    # Get device information
    vendor, device = read_ids(bdf)
    original_driver = get_current_driver(bdf)
    iommu_group = get_iommu_group(bdf)
    vfio_device_path = Path(f"/dev/vfio/{iommu_group}")
    
    logger.info(f"Starting VFIO binding for {bdf} (group: {iommu_group})")
    
    try:
        # Bind to VFIO
        bind_to_vfio(bdf, vendor, device, original_driver)
        
        # Verify VFIO device exists
        if not vfio_device_path.exists():
            raise RuntimeError(f"VFIO device {vfio_device_path} not found after binding")
        
        logger.info(f"VFIO binding successful, yielding {vfio_device_path}")
        yield vfio_device_path
        
    finally:
        # Always attempt to restore original driver
        logger.info(f"Restoring original driver for {bdf}")
        try:
            restore_original_driver(bdf, original_driver)
            logger.info("Driver restoration completed successfully")
        except Exception as e:
            logger.error(f"Failed to restore driver during cleanup: {e}")
            print(f"[!] Warning: Failed to restore driver during cleanup: {e}")