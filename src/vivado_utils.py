#!/usr/bin/env python3
"""
Vivado Utilities

Utilities for detecting and interacting with Xilinx Vivado.
"""

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


def find_vivado_installation() -> Optional[Dict[str, str]]:
    """
    Find Xilinx Vivado installation on the system.

    Returns:
        Optional[Dict[str, str]]: Dictionary with Vivado information if found, None otherwise.
            Keys: 'path', 'version', 'bin_path'
    """
    # Check if vivado is in PATH
    vivado_in_path = shutil.which("vivado")
    if vivado_in_path:
        # Get version and return
        version = get_vivado_version(vivado_in_path)
        bin_dir = os.path.dirname(vivado_in_path)
        install_dir = os.path.dirname(bin_dir)
        return {
            "path": install_dir,
            "bin_path": bin_dir,
            "version": version,
            "executable": vivado_in_path,
        }

    # Common installation paths by OS
    search_paths = []
    system = platform.system().lower()

    if system == "linux":
        search_paths = [
            "/opt/Xilinx/Vivado",
            "/tools/Xilinx/Vivado",
            "/usr/local/Xilinx/Vivado",
            os.path.expanduser("~/Xilinx/Vivado"),
        ]
    elif system == "windows":
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get(
            "ProgramFiles(x86)", r"C:\Program Files (x86)"
        )
        search_paths = [
            os.path.join(program_files, "Xilinx", "Vivado"),
            os.path.join(program_files_x86, "Xilinx", "Vivado"),
            r"C:\Xilinx\Vivado",
        ]
    elif system == "darwin":  # macOS
        search_paths = [
            "/Applications/Xilinx/Vivado",
            os.path.expanduser("~/Xilinx/Vivado"),
        ]

    # Check each path
    for base_path in search_paths:
        if os.path.exists(base_path):
            # If it's a directory, look for version subdirectories
            if os.path.isdir(base_path):
                # Look for version directories (e.g., 2023.1)
                try:
                    versions = [
                        d
                        for d in os.listdir(base_path)
                        if d[0].isdigit() and os.path.isdir(os.path.join(base_path, d))
                    ]
                    if versions:
                        # Sort versions and use the latest
                        latest_version = sorted(versions)[-1]
                        vivado_dir = os.path.join(base_path, latest_version)

                        # Find bin directory
                        bin_dir = os.path.join(vivado_dir, "bin")
                        if os.path.exists(bin_dir):
                            # Find vivado executable
                            vivado_exe = os.path.join(
                                bin_dir,
                                "vivado" + (".exe" if system == "windows" else ""),
                            )
                            if os.path.exists(vivado_exe):
                                return {
                                    "path": vivado_dir,
                                    "bin_path": bin_dir,
                                    "version": latest_version,
                                    "executable": vivado_exe,
                                }
                except (PermissionError, FileNotFoundError):
                    # Skip if we can't access the directory
                    continue

    # Check environment variables
    xilinx_vivado = os.environ.get("XILINX_VIVADO")
    if xilinx_vivado and os.path.exists(xilinx_vivado):
        bin_dir = os.path.join(xilinx_vivado, "bin")
        if os.path.exists(bin_dir):
            vivado_exe = os.path.join(
                bin_dir, "vivado" + (".exe" if system == "windows" else "")
            )
            if os.path.exists(vivado_exe):
                # Try to extract version from path
                path_parts = xilinx_vivado.split(os.path.sep)
                version = next(
                    (p for p in path_parts if p[0].isdigit() and "." in p), "unknown"
                )
                return {
                    "path": xilinx_vivado,
                    "bin_path": bin_dir,
                    "version": version,
                    "executable": vivado_exe,
                }

    # Not found
    return None


def get_vivado_version(vivado_path: str) -> str:
    """
    Get Vivado version from executable.

    Args:
        vivado_path (str): Path to Vivado executable

    Returns:
        str: Vivado version or "unknown" if not determined
    """
    try:
        result = subprocess.run(
            [vivado_path, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=5,  # Timeout after 5 seconds
        )

        if result.returncode == 0:
            # Parse version from output
            for line in result.stdout.splitlines():
                if "Vivado" in line and "v" in line:
                    # Extract version like "v2022.2"
                    parts = line.split()
                    for part in parts:
                        if part.startswith("v") and "." in part:
                            return part[1:]  # Remove 'v' prefix

        # Try to extract version from path if command failed
        path_parts = vivado_path.split(os.path.sep)
        for part in path_parts:
            if part[0].isdigit() and "." in part:
                return part

    except (subprocess.SubprocessError, OSError):
        pass

    return "unknown"


def run_vivado_command(
    command: str,
    tcl_file: Optional[str] = None,
    cwd: Optional[str] = None,
    timeout: Optional[int] = None,
) -> subprocess.CompletedProcess:
    """
    Run a Vivado command.

    Args:
        command (str): Vivado command to run
        tcl_file (Optional[str]): TCL file to source
        cwd (Optional[str]): Working directory
        timeout (Optional[int]): Command timeout in seconds

    Returns:
        subprocess.CompletedProcess: Result of the command

    Raises:
        FileNotFoundError: If Vivado is not found
        subprocess.SubprocessError: If the command fails
    """
    vivado_info = find_vivado_installation()
    if not vivado_info:
        raise FileNotFoundError(
            "Vivado not found. Please make sure Vivado is installed and in your PATH, "
            "or set the XILINX_VIVADO environment variable."
        )

    vivado_exe = vivado_info["executable"]

    cmd = [vivado_exe]

    # Add command arguments
    if command:
        cmd.extend(command.split())

    # Add TCL file if provided
    if tcl_file:
        cmd.extend(["-source", tcl_file])

    # Run the command
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        cwd=cwd,
        timeout=timeout,
    )


if __name__ == "__main__":
    # If run directly, print Vivado information
    vivado_info = find_vivado_installation()
    if vivado_info:
        print(f"Vivado found:")
        print(f"  Path: {vivado_info['path']}")
        print(f"  Version: {vivado_info['version']}")
        print(f"  Executable: {vivado_info['executable']}")
    else:
        print("Vivado not found on this system.")
