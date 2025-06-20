#!/usr/bin/env python3
"""
Kernel utilities for driver analysis.

This module provides utilities for working with kernel source code,
including extraction of kernel source packages and driver module resolution.

Prerequisites:
    - modprobe (Linux module utilities)
    - ripgrep (rg) for fast text searching (optional but recommended)
    - Linux kernel source packages in /usr/src/

Expected kernel layout:
    /usr/src/linux-source-*.tar.* - Compressed kernel source
    /usr/src/linux-source-*/ - Extracted kernel source directory
"""

import os
import pathlib
import platform
import subprocess
import tarfile
from typing import List, Optional


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system().lower() == "linux"


def check_linux_requirement(operation: str) -> None:
    """Check if operation requires Linux and raise error if not available."""
    if not is_linux():
        raise RuntimeError(
            f"{operation} requires Linux. "
            f"Current platform: {platform.system()}. "
            "This functionality is only available on Linux systems."
        )


def run_command(cmd: str) -> str:
    """
    Execute a shell command safely with proper error handling.

    Args:
        cmd: Command to execute

    Returns:
        Command output as string

    Raises:
        RuntimeError: If command fails with descriptive error message
    """
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Command failed: {cmd}\n"
            f"Exit code: {e.returncode}\n"
            f"Error output: {e.stderr}"
        ) from e


def setup_debugfs() -> None:
    """
    Set up debugfs mount for kernel debugging operations.

    This function ensures that debugfs is properly mounted at /sys/kernel/debug,
    which is required for kernel debugging and analysis operations.

    Raises:
        RuntimeError: If debugfs setup fails or not running on Linux
    """
    check_linux_requirement("Debugfs setup")

    try:
        # First, check if /sys/kernel exists
        try:
            result = subprocess.run(
                "ls -la /sys/kernel", shell=True, capture_output=True, text=True
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"/sys/kernel directory not accessible. "
                    f"Exit code: {result.returncode}, "
                    f"Error: {result.stderr.strip()}"
                )
        except Exception as e:
            raise RuntimeError(f"Cannot access /sys/kernel: {e}") from e

        # Check current user privileges
        try:
            result = subprocess.run("id -u", shell=True, capture_output=True, text=True)
            uid = result.stdout.strip()

            # Check if we can write to /sys/kernel/debug (privileged container check)
            can_access_sys = False
            try:
                # Test if we can access privileged paths
                test_path = "/sys/kernel/debug"
                if os.path.exists(test_path):
                    can_access_sys = os.access(test_path, os.W_OK)
                else:
                    # Try to create the directory to test privileges
                    try:
                        os.makedirs(test_path, exist_ok=True)
                        can_access_sys = True
                    except PermissionError:
                        can_access_sys = False
            except Exception:
                can_access_sys = False

            # If not root and can't access sys, try with sudo
            if uid != "0" and not can_access_sys:
                # Check if sudo is available
                sudo_available = (
                    subprocess.run(
                        "which sudo", shell=True, capture_output=True
                    ).returncode
                    == 0
                )

                if not sudo_available:
                    raise RuntimeError(
                        f"Debugfs setup requires root privileges. "
                        f"Current UID: {uid}. "
                        f"Please run with sudo or as root user."
                    )
        except Exception as e:
            raise RuntimeError(f"Cannot determine user privileges: {e}") from e

        # Check if debugfs is already mounted
        try:
            mount_output = run_command("mount | grep debugfs")
            if "/sys/kernel/debug" in mount_output:
                return  # Already mounted
        except RuntimeError:
            # grep returns non-zero if no matches found, which is expected
            pass

        # Check if debugfs is supported in kernel
        try:
            result = subprocess.run(
                "grep -q debugfs /proc/filesystems", shell=True, capture_output=True
            )
            if result.returncode != 0:
                raise RuntimeError(
                    "debugfs filesystem not supported by kernel. "
                    "Please ensure debugfs is compiled into the kernel or loaded as a module."
                )
        except Exception as e:
            raise RuntimeError(f"Cannot check debugfs kernel support: {e}") from e

        # Create the debug directory if it doesn't exist
        try:
            run_command("mkdir -p /sys/kernel/debug")
        except RuntimeError as e:
            # Provide more specific error information
            if "Permission denied" in str(e):
                raise RuntimeError(
                    f"Permission denied creating /sys/kernel/debug. "
                    f"This operation requires root privileges. "
                    f"Original error: {e}"
                ) from e
            elif "Read-only file system" in str(e):
                raise RuntimeError(
                    f"/sys filesystem is read-only. "
                    f"Cannot create debugfs mount point. "
                    f"Original error: {e}"
                ) from e
            else:
                raise RuntimeError(f"Failed to create /sys/kernel/debug: {e}") from e

        # Mount debugfs
        try:
            run_command("mount -t debugfs debugfs /sys/kernel/debug")
        except RuntimeError as e:
            error_str = str(e).lower()
            if "already mounted" in error_str or "debugfs already mounted" in error_str:
                # This is actually a success case - debugfs is already available
                return
            elif "permission denied" in error_str:
                raise RuntimeError(
                    f"Permission denied mounting debugfs. "
                    f"This operation requires root privileges. "
                    f"Original error: {e}"
                ) from e
            else:
                raise RuntimeError(f"Failed to mount debugfs: {e}") from e

    except Exception as e:
        raise RuntimeError(f"Failed to setup debugfs: {e}") from e


def ensure_kernel_source() -> Optional[pathlib.Path]:
    """
    Extract /usr/src/linux-source-*.tar.* if not untarred yet.

    Returns:
        Path to extracted kernel source directory, or None if not found

    Raises:
        RuntimeError: If extraction fails
    """
    # Find the source package
    src_path = pathlib.Path("/usr/src")

    # In real execution, this will be an iterator
    # In tests, this is mocked to return a list directly
    glob_result = src_path.glob("linux-source-*.tar*")

    # Get the first source package
    # This approach works with both real iterators and mocked lists
    src_pkg = None
    for pkg in glob_result:
        src_pkg = pkg
        break

    if not src_pkg:
        return None

    untar_dir = src_pkg.with_suffix("").with_suffix("")  # strip .tar.xz
    if not (untar_dir / "drivers").exists():
        try:
            with tarfile.open(src_pkg) as t:
                # Security: validate tar members before extraction
                def is_safe_path(path: str) -> bool:
                    return not (path.startswith("/") or ".." in path)

                safe_members = [m for m in t.getmembers() if is_safe_path(m.name)]
                t.extractall("/usr/src", members=safe_members)
        except Exception as e:
            raise RuntimeError(f"Failed to extract kernel source: {e}") from e

    return untar_dir


def resolve_driver_module(vendor_id: str, device_id: str) -> str:
    """
    Resolve driver module name from vendor and device IDs.

    Args:
        vendor_id: 4-digit hex vendor ID (e.g., "8086")
        device_id: 4-digit hex device ID (e.g., "1533")

    Returns:
        Driver module name (e.g., "snd_hda_intel")

    Raises:
        RuntimeError: If no driver module found or command fails
    """
    check_linux_requirement("Driver module resolution")

    try:
        alias_line = run_command(
            f"modprobe --resolve-alias pci:v0000{vendor_id}d0000{device_id}*"
        ).splitlines()

        if not alias_line:
            raise RuntimeError(
                f"No driver module found for VID:DID {vendor_id}:{device_id} in modules.alias"
            )

        return alias_line[-1].strip()  # e.g. snd_hda_intel
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to resolve driver module: {e}") from e


def find_driver_sources(
    kernel_source_dir: pathlib.Path, driver_name: str
) -> List[pathlib.Path]:
    """
    Find source files for a specific driver in the kernel source tree.

    Args:
        kernel_source_dir: Path to the kernel source directory
        driver_name: Name of the driver module to find

    Returns:
        List of paths to source files related to the driver
    """
    # First, try to find files directly matching the driver name
    src_files = list(kernel_source_dir.rglob(f"{driver_name}*.c")) + list(
        kernel_source_dir.rglob(f"{driver_name}*.h")
    )

    # If no direct matches, try to find files containing the driver name in
    # their content
    if not src_files:
        # Look in drivers directory first as it's most likely location
        drivers_dir = kernel_source_dir / "drivers"
        if drivers_dir.exists():
            candidates = []
            for ext in [".c", ".h"]:
                for file_path in drivers_dir.rglob(f"*{ext}"):
                    try:
                        content = file_path.read_text(errors="ignore")
                        if driver_name in content:
                            candidates.append(file_path)
                            # Limit to prevent excessive searching
                            if len(candidates) >= 20:
                                break
                    except Exception:
                        continue
            src_files = candidates

    return src_files
