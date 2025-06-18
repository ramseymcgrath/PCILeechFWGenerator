"""Container management for Podman-based firmware builds."""

import os
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logging import get_logger
from utils.shell import Shell

from .config import BuildConfig

logger = get_logger(__name__)

# Container configuration constants
CONTAINER_IMAGE_NAME = "pcileech-fw-generator"
CONTAINER_IMAGE_TAG = "latest"
CONTAINER_BUILD_SCRIPT = "scripts/build_container.sh"
CONTAINER_FILE = "Containerfile"
CONTAINER_CHECK_TIMEOUT = 10


class ContainerError(Exception):
    """Custom exception for container-related errors."""

    pass


def require_podman() -> None:
    """Check if Podman is available in the system PATH."""
    if shutil.which("podman") is None:
        error_msg = "Podman not found in PATH. Please install Podman container runtime."
        logger.error(error_msg)
        raise ContainerError(error_msg)


def _image_exists(image_name: str, tag: str = "latest") -> bool:
    """Check if a container image exists locally.

    Args:
        image_name: Name of the container image
        tag: Image tag (default: latest)

    Returns:
        True if image exists, False otherwise

    Raises:
        ContainerError: If unable to check image status
    """
    full_image_name = f"{image_name}:{tag}"
    shell = Shell()

    try:
        # Use || true to prevent grep from failing when no matches are found
        result = shell.run(
            f"podman images --format '{{.Repository}}:{{.Tag}}' | grep '^{image_name}:' || true",
            timeout=CONTAINER_CHECK_TIMEOUT,
        )
        return bool(result.strip())
    except Exception as e:
        logger.warning(f"Unable to check container image status: {e}")
        return False


def _build_image(image_name: str, tag: str = "latest") -> None:
    """Build container image using build script or direct podman build.

    Args:
        image_name: Name of the container image to build
        tag: Image tag (default: latest)

    Raises:
        ContainerError: If container build fails
    """
    full_image_name = f"{image_name}:{tag}"
    logger.info(f"Building container image '{full_image_name}'...")
    print(f"[*] Building container image '{full_image_name}'...")

    # Determine build method
    if os.path.exists(CONTAINER_BUILD_SCRIPT):
        logger.info("Using build script for container creation")
        build_cmd = f"bash {CONTAINER_BUILD_SCRIPT} --tag {full_image_name}"
    else:
        logger.info("Using direct podman build")
        build_cmd = f"podman build -t {full_image_name} -f {CONTAINER_FILE} ."

    try:
        subprocess.run(
            build_cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logger.info("Container image built successfully")
        print("[✓] Container image built successfully")
    except subprocess.CalledProcessError as e:
        error_msg = (
            f"Failed to build container image '{full_image_name}': {e.stderr}\n"
            f"Please build manually with: make container"
        )
        logger.error(error_msg)
        raise ContainerError(error_msg) from e


def _validate_container_environment() -> None:
    """Validate container runtime environment and ensure image availability.

    This function:
    1. Checks if Podman is available
    2. Verifies container image exists
    3. Builds image automatically if missing

    Raises:
        ContainerError: If validation or build fails
    """
    # Check Podman availability
    require_podman()

    # Check if container image exists
    if _image_exists(CONTAINER_IMAGE_NAME, CONTAINER_IMAGE_TAG):
        logger.debug(
            f"Container image '{CONTAINER_IMAGE_NAME}:{CONTAINER_IMAGE_TAG}' found"
        )
        return

    # Image not found, attempt to build it
    logger.info(
        f"Container image '{CONTAINER_IMAGE_NAME}:{CONTAINER_IMAGE_TAG}' not found"
    )
    _build_image(CONTAINER_IMAGE_NAME, CONTAINER_IMAGE_TAG)


def _validate_vfio_device_access(vfio_device: Path, bdf: str) -> None:
    """Validate VFIO device access and permissions."""
    # Check if VFIO device exists
    if not vfio_device.exists():
        error_msg = f"VFIO device {vfio_device} not found"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check if /dev/vfio/vfio exists (VFIO container device)
    vfio_container = Path("/dev/vfio/vfio")
    if not vfio_container.exists():
        error_msg = f"VFIO container device {vfio_container} not found"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Verify device is actually bound to vfio-pci
    from .vfio import get_current_driver

    current_driver = get_current_driver(bdf)
    if current_driver != "vfio-pci":
        error_msg = (
            f"Device {bdf} not bound to vfio-pci (current: {current_driver or 'none'})"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def run_build_container(cfg: BuildConfig, vfio_dev: Path) -> None:
    """Run the firmware build in a Podman container with enhanced validation and error handling.

    Args:
        cfg: Build configuration
        vfio_dev: Path to VFIO device

    Raises:
        RuntimeError: If build fails
        ContainerError: If container setup fails
    """
    # Log advanced features being used
    advanced_features = []
    if cfg.advanced_sv:
        advanced_features.append("Advanced SystemVerilog Generation")
    if cfg.enable_variance:
        advanced_features.append("Manufacturing Variance Simulation")
    if cfg.device_type != "generic":
        advanced_features.append(f"Device-specific optimizations ({cfg.device_type})")

    if advanced_features:
        logger.info(f"Advanced features enabled: {', '.join(advanced_features)}")
        print(f"[*] Advanced features: {', '.join(advanced_features)}")

    logger.info(f"Starting container build for device {cfg.bdf} on board {cfg.board}")

    # Validate container environment
    _validate_container_environment()

    # Ensure output directory exists with proper permissions
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Check output directory permissions
    if not os.access(output_dir, os.W_OK):
        error_msg = f"Output directory {output_dir} is not writable"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Validate VFIO device access
    _validate_vfio_device_access(vfio_dev, cfg.bdf)

    # Build the build.py command with all arguments
    build_cmd_parts = [f"python3 /app/src/build.py --bdf {cfg.bdf} --board {cfg.board}"]

    # Add advanced features arguments
    if cfg.advanced_sv:
        build_cmd_parts.append("--advanced-sv")

    if cfg.device_type != "generic":
        build_cmd_parts.append(f"--device-type {cfg.device_type}")

    if cfg.enable_variance:
        build_cmd_parts.append("--enable-variance")

    if cfg.disable_power_management:
        build_cmd_parts.append("--disable-power-management")

    if cfg.disable_error_handling:
        build_cmd_parts.append("--disable-error-handling")

    if cfg.disable_performance_counters:
        build_cmd_parts.append("--disable-performance-counters")

    if cfg.behavior_profile_duration != 30:
        build_cmd_parts.append(
            f"--behavior-profile-duration {cfg.behavior_profile_duration}"
        )
    build_cmd = " ".join(build_cmd_parts)

    # Construct Podman command
    container_cmd = textwrap.dedent(
        f"""
        podman run --rm -it --privileged \
          --device={vfio_dev} \
          --device=/dev/vfio/vfio \
          -v {os.getcwd()}/output:/app/output \
          {CONTAINER_IMAGE_NAME}:{CONTAINER_IMAGE_TAG} \
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
