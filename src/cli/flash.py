"""USB device management and firmware flashing utilities."""

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from log_config import get_logger
from shell import Shell

logger = get_logger(__name__)


def list_usb_devices() -> List[Tuple[str, str]]:
    """Return list of USB devices as (vid:pid, description) tuples.

    Returns:
        List of tuples containing (vid:pid, description) for each USB device
    """
    shell = Shell()

    try:
        output = shell.run("lsusb").splitlines()
    except Exception:
        logger.warning("Failed to list USB devices")
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
    """Interactive USB device selection for flashing.

    Returns:
        Selected device VID:PID string

    Raises:
        RuntimeError: If no USB devices found or selection fails
    """
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


def flash_firmware(bin_path: Path) -> None:
    """Flash firmware to FPGA board using usbloader.

    Args:
        bin_path: Path to firmware binary file

    Raises:
        RuntimeError: If flashing fails or usbloader not found
    """
    logger.info("Starting firmware flash process")

    if shutil.which("usbloader") is None:
        error_msg = "usbloader not found in PATH — install λConcept usbloader first"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    if not bin_path.exists():
        error_msg = f"Firmware file not found: {bin_path}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    try:
        vid_pid = select_usb_device()
        logger.info(f"Selected USB device: {vid_pid}")
        print(f"[*] Flashing firmware using VID:PID {vid_pid}")

        subprocess.run(
            f"usbloader --vidpid {vid_pid} -f {bin_path}", shell=True, check=True
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
