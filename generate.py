#!/usr/bin/env python3
"""
Host-side orchestrator for DMA firmware generation.

This script:
• Enumerates PCIe devices
• Allows user to select a donor device
• Re-binds donor to vfio-pci driver
• Launches Podman container (image: dma-fw) that runs build.py
• Optionally flashes output/firmware.bin with usbloader
• Restores original driver afterwards

Requires root privileges (sudo) for driver rebinding and VFIO operations.
"""

import argparse
import datetime
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


def run_command(cmd: str, **kwargs) -> str:
    """Execute a shell command and return stripped output."""
    return subprocess.check_output(cmd, shell=True, text=True, **kwargs).strip()


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
            f"Please run this on a Linux system with VFIO support."
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
            description = match.group(2)
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


def bind_to_vfio(
    bdf: str, vendor: str, device: str, original_driver: Optional[str]
) -> None:
    """Bind PCIe device to vfio-pci driver"""
    check_linux_requirement("VFIO device binding")

    if not validate_bdf_format(bdf):
        raise ValueError(
            f"Invalid BDF format: {bdf}. Expected format: DDDD:BB:DD.F (e.g., 0000:03:00.0)"
        )

    logger.info(
        f"Binding device {bdf} to vfio-pci driver (current driver: {original_driver or 'none'})"
    )
    if original_driver == "vfio-pci":
        print(
            "[*] Device already bound to vfio-pci driver, skipping binding process..."
        )
        logger.info(f"Device {bdf} already bound to vfio-pci, skipping binding process")
        return
    else:
        print("[*] Binding device to vfio-pci driver...")

    try:
        # Check if vfio-pci driver is available
        if not os.path.exists("/sys/bus/pci/drivers/vfio-pci"):
            error_msg = (
                "vfio-pci driver not available. Ensure VFIO is enabled in kernel."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Check if device ID is already registered with vfio-pci
        device_id_registered = False
        try:
            # Try to read the IDs file to check if our device ID is already registered
            ids_file = "/sys/bus/pci/drivers/vfio-pci/ids"
            if os.path.exists(ids_file):
                with open(ids_file, "r") as f:
                    registered_ids = f.read()
                    if f"{vendor} {device}" in registered_ids:
                        logger.info(
                            f"Device ID {vendor}:{device} already registered with vfio-pci"
                        )
                        device_id_registered = True
        except Exception as e:
            logger.debug(f"Error checking registered device IDs: {e}")
            # Continue with normal flow if we can't check

        # Register device ID with vfio-pci if not already registered
        if not device_id_registered:
            logger.debug(f"Registering device ID {vendor}:{device} with vfio-pci")
            try:
                run_command(
                    f"echo {vendor} {device} > /sys/bus/pci/drivers/vfio-pci/new_id"
                )
                logger.info(
                    f"Successfully registered device ID {vendor}:{device} with vfio-pci"
                )
            except subprocess.CalledProcessError as e:
                # If the error is "File exists", the device ID is already registered, which is fine
                if "File exists" in str(e):
                    logger.info(
                        f"Device ID {vendor}:{device} already registered with vfio-pci"
                    )
                else:
                    # Re-raise if it's a different error
                    logger.error(f"Failed to register device ID: {e}")
                    raise

        # Unbind from current driver if present
        if original_driver:
            logger.debug(f"Unbinding from current driver: {original_driver}")
            try:
                run_command(f"echo {bdf} > /sys/bus/pci/devices/{bdf}/driver/unbind")
                logger.info(f"Successfully unbound {bdf} from {original_driver}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to unbind from current driver: {e}")
                # Continue anyway, as the bind might still work

        # Bind to vfio-pci
        logger.debug(f"Binding {bdf} to vfio-pci")
        try:
            run_command(f"echo {bdf} > /sys/bus/pci/drivers/vfio-pci/bind")
            logger.info(f"Successfully bound {bdf} to vfio-pci")
            print("[✓] Device successfully bound to vfio-pci driver")
        except subprocess.CalledProcessError as e:
            # Check if device is already bound to vfio-pci despite the error
            current_driver = get_current_driver(bdf)
            if current_driver == "vfio-pci":
                logger.info(
                    f"Device {bdf} is already bound to vfio-pci despite bind command error"
                )
                print("[✓] Device is already bound to vfio-pci driver")
            else:
                logger.error(f"Failed to bind to vfio-pci: {e}")
                raise

    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to bind device to vfio-pci: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during vfio binding: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def restore_original_driver(bdf: str, original_driver: Optional[str]) -> None:
    """Restore the original driver binding for the PCIe device"""
    if not validate_bdf_format(bdf):
        logger.warning(f"Invalid BDF format during restore: {bdf}")
        return

    logger.info(
        f"Restoring original driver binding for {bdf} (target driver: {original_driver or 'none'})"
    )
    print("[*] Restoring original driver binding...")

    try:
        # Check if device is still bound to vfio-pci before attempting unbind
        current_driver = get_current_driver(bdf)
        if current_driver == "vfio-pci":
            logger.debug(f"Unbinding {bdf} from vfio-pci")
            run_command(f"echo {bdf} > /sys/bus/pci/drivers/vfio-pci/unbind")
        else:
            logger.info(
                f"Device {bdf} not bound to vfio-pci (current: {current_driver or 'none'})"
            )

        # Bind back to original driver if it existed
        if original_driver:
            # Check if original driver is available
            driver_path = f"/sys/bus/pci/drivers/{original_driver}"
            if os.path.exists(driver_path):
                logger.debug(f"Binding {bdf} back to {original_driver}")
                run_command(f"echo {bdf} > /sys/bus/pci/drivers/{original_driver}/bind")
                logger.info(f"Successfully restored {bdf} to {original_driver}")
            else:
                logger.warning(
                    f"Original driver {original_driver} not available for restore"
                )
        else:
            logger.info(f"No original driver to restore for {bdf}")

    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to restore original driver for {bdf}: {e}")
        print(f"Warning: Failed to restore original driver: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error during driver restore for {bdf}: {e}")
        print(f"Warning: Unexpected error during driver restore: {e}")


def run_build_container(
    bdf: str, board: str, vfio_device: str, args: argparse.Namespace
) -> None:
    """Run the firmware build in a Podman container"""
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
        logger.info(f"Advanced features enabled: {', '.join(advanced_features)}")
        print(f"[*] Advanced features: {', '.join(advanced_features)}")

    logger.info(f"Starting container build for device {bdf} on board {board}")

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # Validate VFIO device exists
    if not os.path.exists(vfio_device):
        error_msg = f"VFIO device {vfio_device} not found"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Build the build.py command with all arguments
    build_cmd_parts = [f"sudo python3 /app/build.py --bdf {bdf} --board {board}"]

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

    build_cmd = " ".join(build_cmd_parts)

    # Construct Podman command
    container_cmd = textwrap.dedent(
        f"""
        podman run --rm -it --privileged \
          --device={vfio_device} \
          --device=/dev/vfio/vfio \
          -v {os.getcwd()}/output:/app/output \
          dma-fw \
          {build_cmd}
    """
    ).strip()

    logger.debug(f"Container command: {container_cmd}")
    print("[*] Launching build container...")
    start_time = time.time()

    try:
        subprocess.run(container_cmd, shell=True, check=True)
        elapsed_time = time.time() - start_time
        logger.info(f"Build completed successfully in {elapsed_time:.1f} seconds")
        print(f"[✓] Build completed in {elapsed_time:.1f} seconds")

    except subprocess.CalledProcessError as e:
        elapsed_time = time.time() - start_time
        error_msg = f"Container build failed after {elapsed_time:.1f} seconds: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        elapsed_time = time.time() - start_time
        error_msg = f"Unexpected error during container build after {elapsed_time:.1f} seconds: {e}"
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

    # Check if repository already exists
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

                logger.info(f"Repository updated successfully: {result.stdout.strip()}")
                print(f"[✓] Repository updated successfully")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to update repository: {e.stderr}")
                print(f"[!] Warning: Failed to update repository: {e.stderr}")
    else:
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

            logger.info(f"Repository cloned successfully")
            print(f"[✓] Repository cloned successfully")
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

    # Check if container image exists
    try:
        result = run_command("podman images dma-fw --format '{{.Repository}}'")
        if "dma-fw" not in result:
            # Container image not found, try to build it
            logger.info("Container image 'dma-fw' not found. Building it now...")
            print("[*] Container image 'dma-fw' not found. Building it now...")

            try:
                build_result = subprocess.run(
                    "podman build -t dma-fw .",
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
            config_info.append(f"profile_duration={args.behavior_profile_duration}s")

        logger.info(f"Configuration: {', '.join(config_info)}")

        # List and select PCIe device
        devices = list_pci_devices()
        if not devices:
            error_msg = "No PCIe devices found"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        selected_device = choose_device(devices)
        bdf = selected_device["bdf"]
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
