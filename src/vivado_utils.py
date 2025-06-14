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

        # Add support for /tools/Xilinx/[version]/Vivado pattern
        tools_xilinx_base = "/tools/Xilinx"
        if os.path.exists(tools_xilinx_base):
            try:
                # Look for version directories in /tools/Xilinx/
                for item in os.listdir(tools_xilinx_base):
                    item_path = os.path.join(tools_xilinx_base, item)
                    # Check if it's a version directory (starts with digit, contains dot)
                    if (
                        os.path.isdir(item_path)
                        and item
                        and item[0].isdigit()
                        and "." in item
                    ):
                        vivado_path = os.path.join(item_path, "Vivado")
                        if os.path.exists(vivado_path):
                            search_paths.append(vivado_path)
            except (PermissionError, FileNotFoundError):
                # Skip if we can't access the directory
                pass
    elif system == "windows":
        # Windows support removed as per requirements
        search_paths = []
    elif system == "darwin":  # macOS
        search_paths = [
            "/Applications/Xilinx/Vivado",
            os.path.expanduser("~/Xilinx/Vivado"),
        ]

        # Add support for /tools/Xilinx/[version]/Vivado pattern on macOS
        tools_xilinx_base = "/tools/Xilinx"
        if os.path.exists(tools_xilinx_base):
            try:
                # Look for version directories in /tools/Xilinx/
                for item in os.listdir(tools_xilinx_base):
                    item_path = os.path.join(tools_xilinx_base, item)
                    # Check if it's a version directory (starts with digit, contains dot)
                    if (
                        os.path.isdir(item_path)
                        and item
                        and item[0].isdigit()
                        and "." in item
                    ):
                        vivado_path = os.path.join(item_path, "Vivado")
                        if os.path.exists(vivado_path):
                            search_paths.append(vivado_path)
            except (PermissionError, FileNotFoundError):
                # Skip if we can't access the directory
                pass

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
                        version_dir = os.path.join(base_path, latest_version)

                        # Check for [version]/Vivado/bin/vivado structure
                        vivado_dir = os.path.join(version_dir, "Vivado")
                        if os.path.exists(vivado_dir):
                            bin_dir = os.path.join(vivado_dir, "bin")
                            if os.path.exists(bin_dir):
                                vivado_exe = os.path.join(bin_dir, "vivado")
                                if os.path.isfile(vivado_exe):
                                    return {
                                        "path": vivado_dir,
                                        "bin_path": bin_dir,
                                        "version": latest_version,
                                        "executable": vivado_exe,
                                    }

                        # Fallback: Check for [version]/bin/vivado structure (legacy)
                        bin_dir = os.path.join(version_dir, "bin")
                        if os.path.exists(bin_dir):
                            vivado_exe = os.path.join(bin_dir, "vivado")
                            if os.path.isfile(vivado_exe):
                                return {
                                    "path": version_dir,
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
        # Check for [XILINX_VIVADO]/bin/vivado structure
        bin_dir = os.path.join(xilinx_vivado, "bin")
        if os.path.exists(bin_dir):
            vivado_exe = os.path.join(bin_dir, "vivado")
            if os.path.isfile(vivado_exe):
                # Try to extract version from path
                path_parts = xilinx_vivado.split(os.path.sep)
                version = next(
                    (
                        p
                        for p in path_parts
                        if p and len(p) > 0 and p[0].isdigit() and "." in p
                    ),
                    "unknown",
                )
                return {
                    "path": xilinx_vivado,
                    "bin_path": bin_dir,
                    "version": version,
                    "executable": vivado_exe,
                }

        # Check for [XILINX_VIVADO]/../bin/vivado structure (if XILINX_VIVADO points to Vivado subdir)
        parent_bin_dir = os.path.join(os.path.dirname(xilinx_vivado), "bin")
        if os.path.exists(parent_bin_dir):
            vivado_exe = os.path.join(parent_bin_dir, "vivado")
            if os.path.isfile(vivado_exe):
                # Try to extract version from path
                path_parts = xilinx_vivado.split(os.path.sep)
                version = next(
                    (
                        p
                        for p in path_parts
                        if p and len(p) > 0 and p[0].isdigit() and "." in p
                    ),
                    "unknown",
                )
                return {
                    "path": os.path.dirname(xilinx_vivado),
                    "bin_path": parent_bin_dir,
                    "version": version,
                    "executable": vivado_exe,
                }

    # Not found
    return None


def get_vivado_search_paths() -> List[str]:
    """
    Get list of paths that would be searched for Vivado installation.

    Returns:
        List[str]: List of paths that are checked during Vivado discovery
    """
    search_paths = []

    # Check if vivado is in PATH
    search_paths.append("System PATH")

    # Common installation paths by OS
    system = platform.system().lower()

    if system == "linux":
        base_paths = [
            "/opt/Xilinx/Vivado",
            "/tools/Xilinx/Vivado",
            "/usr/local/Xilinx/Vivado",
            os.path.expanduser("~/Xilinx/Vivado"),
        ]
        search_paths.extend(base_paths)

        # Add support for /tools/Xilinx/[version]/Vivado pattern
        tools_xilinx_base = "/tools/Xilinx"
        if os.path.exists(tools_xilinx_base):
            try:
                # Look for version directories in /tools/Xilinx/
                for item in os.listdir(tools_xilinx_base):
                    item_path = os.path.join(tools_xilinx_base, item)
                    # Check if it's a version directory (starts with digit, contains dot)
                    if (
                        os.path.isdir(item_path)
                        and item
                        and item[0].isdigit()
                        and "." in item
                    ):
                        vivado_path = os.path.join(item_path, "Vivado")
                        search_paths.append(vivado_path)
            except (PermissionError, FileNotFoundError):
                # Add generic pattern if we can't list
                search_paths.append("/tools/Xilinx/[version]/Vivado")
    elif system == "darwin":  # macOS
        base_paths = [
            "/Applications/Xilinx/Vivado",
            os.path.expanduser("~/Xilinx/Vivado"),
        ]
        search_paths.extend(base_paths)

        # Add support for /tools/Xilinx/[version]/Vivado pattern on macOS
        tools_xilinx_base = "/tools/Xilinx"
        if os.path.exists(tools_xilinx_base):
            try:
                # Look for version directories in /tools/Xilinx/
                for item in os.listdir(tools_xilinx_base):
                    item_path = os.path.join(tools_xilinx_base, item)
                    # Check if it's a version directory (starts with digit, contains dot)
                    if (
                        os.path.isdir(item_path)
                        and item
                        and item[0].isdigit()
                        and "." in item
                    ):
                        vivado_path = os.path.join(item_path, "Vivado")
                        search_paths.append(vivado_path)
            except (PermissionError, FileNotFoundError):
                # Add generic pattern if we can't list
                search_paths.append("/tools/Xilinx/[version]/Vivado")

    # Check environment variables
    xilinx_vivado = os.environ.get("XILINX_VIVADO")
    if xilinx_vivado:
        search_paths.append(f"XILINX_VIVADO={xilinx_vivado}")
    else:
        search_paths.append("XILINX_VIVADO environment variable")

    return search_paths


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
                if "vivado" in line.lower() and "v" in line:
                    # Extract version like "v2022.2"
                    parts = line.split()
                    for part in parts:
                        if part.startswith("v") and "." in part and len(part) > 1:
                            return part[1:]  # Remove 'v' prefix

        # Try to extract version from path if command failed
        path_parts = vivado_path.split(os.path.sep)
        for part in path_parts:
            if part and len(part) > 0 and part[0].isdigit() and "." in part:
                return part

    except (subprocess.SubprocessError, OSError):
        pass

    return "unknown"


def run_vivado_command(
    command: str,
    tcl_file: Optional[str] = None,
    cwd: Optional[str] = None,
    timeout: Optional[int] = None,
    use_discovered_path: bool = True,
) -> subprocess.CompletedProcess:
    """
    Run a Vivado command using discovered installation or PATH.

    Args:
        command (str): Vivado command to run
        tcl_file (Optional[str]): TCL file to source
        cwd (Optional[str]): Working directory
        timeout (Optional[int]): Command timeout in seconds
        use_discovered_path (bool): Whether to use discovered Vivado path (default: True)

    Returns:
        subprocess.CompletedProcess: Result of the command

    Raises:
        FileNotFoundError: If Vivado is not found
        subprocess.SubprocessError: If the command fails
    """
    vivado_exe = None

    if use_discovered_path:
        # Try to use discovered Vivado installation first
        vivado_info = find_vivado_installation()
        if vivado_info:
            vivado_exe = vivado_info["executable"]

    # Fall back to PATH if discovery failed or was disabled
    if not vivado_exe:
        vivado_exe = shutil.which("vivado")
        if not vivado_exe:
            raise FileNotFoundError(
                "Vivado not found. Please make sure Vivado is installed and either:\n"
                "1. Add Vivado to your PATH, or\n"
                "2. Set the XILINX_VIVADO environment variable, or\n"
                "3. Install Vivado in a standard location:\n"
                "   - Linux: /opt/Xilinx/Vivado, /tools/Xilinx/Vivado\n"
                "   - macOS: /Applications/Xilinx/Vivado"
            )

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


def get_vivado_executable() -> Optional[str]:
    """
    Get the path to the Vivado executable.

    Returns:
        Optional[str]: Path to Vivado executable if found, None otherwise.
    """
    vivado_info = find_vivado_installation()
    if vivado_info:
        return vivado_info["executable"]
    return None


def debug_vivado_search() -> None:
    """
    Debug function to show detailed Vivado search information.
    """
    print("=== Vivado Detection Debug ===")

    # Check PATH first
    vivado_in_path = shutil.which("vivado")
    print(f"Vivado in PATH: {vivado_in_path or 'Not found'}")

    # Show search paths
    search_paths = get_vivado_search_paths()
    print(f"\nSearch paths being checked:")
    for i, path in enumerate(search_paths, 1):
        print(f"  {i}. {path}")

    # Check each search location
    print(f"\nDetailed search results:")
    system = platform.system().lower()

    if system == "linux":
        base_paths = [
            "/opt/Xilinx/Vivado",
            "/tools/Xilinx/Vivado",
            "/usr/local/Xilinx/Vivado",
            os.path.expanduser("~/Xilinx/Vivado"),
        ]
    elif system == "darwin":  # macOS
        base_paths = [
            "/Applications/Xilinx/Vivado",
            os.path.expanduser("~/Xilinx/Vivado"),
        ]
    else:
        base_paths = []

    for base_path in base_paths:
        print(f"  Checking: {base_path}")
        if os.path.exists(base_path):
            print(f"    ✓ Directory exists")
            try:
                contents = os.listdir(base_path)
                version_dirs = [
                    d
                    for d in contents
                    if d
                    and d[0].isdigit()
                    and os.path.isdir(os.path.join(base_path, d))
                ]
                if version_dirs:
                    print(
                        f"    ✓ Found version directories: {', '.join(sorted(version_dirs))}"
                    )
                    for version in sorted(version_dirs):
                        version_path = os.path.join(base_path, version)
                        print(f"      {version}:")

                        # Check for [version]/Vivado/bin/vivado structure (correct structure)
                        vivado_subdir = os.path.join(version_path, "Vivado")
                        vivado_bin_path = os.path.join(vivado_subdir, "bin")
                        vivado_exe_correct = os.path.join(vivado_bin_path, "vivado")
                        print(
                            f"        Vivado subdirectory: {vivado_subdir} {'✓' if os.path.exists(vivado_subdir) else '✗'}"
                        )
                        print(
                            f"        Vivado/bin directory: {vivado_bin_path} {'✓' if os.path.exists(vivado_bin_path) else '✗'}"
                        )
                        print(
                            f"        Vivado/bin/vivado executable: {vivado_exe_correct} {'✓' if os.path.isfile(vivado_exe_correct) else '✗'}"
                        )

                        # Check for [version]/bin/vivado structure (legacy)
                        legacy_bin_path = os.path.join(version_path, "bin")
                        legacy_vivado_exe = os.path.join(legacy_bin_path, "vivado")
                        print(
                            f"        Legacy bin directory: {legacy_bin_path} {'✓' if os.path.exists(legacy_bin_path) else '✗'}"
                        )
                        print(
                            f"        Legacy vivado executable: {legacy_vivado_exe} {'✓' if os.path.isfile(legacy_vivado_exe) else '✗'}"
                        )
                else:
                    print(f"    ✗ No version directories found")
                    print(
                        f"    Contents: {', '.join(contents) if contents else 'empty'}"
                    )
            except (PermissionError, FileNotFoundError) as e:
                print(f"    ✗ Cannot access directory: {e}")
        else:
            print(f"    ✗ Directory does not exist")

    # Check environment variables
    xilinx_vivado = os.environ.get("XILINX_VIVADO")
    print(f"\nEnvironment variables:")
    print(f"  XILINX_VIVADO: {xilinx_vivado or 'Not set'}")
    if xilinx_vivado:
        # Check direct bin structure
        bin_dir = os.path.join(xilinx_vivado, "bin")
        vivado_exe = os.path.join(bin_dir, "vivado")
        print(
            f"    Direct bin directory: {bin_dir} {'✓' if os.path.exists(bin_dir) else '✗'}"
        )
        print(
            f"    Direct vivado executable: {vivado_exe} {'✓' if os.path.isfile(vivado_exe) else '✗'}"
        )

        # Check parent bin structure (if XILINX_VIVADO points to Vivado subdir)
        parent_bin_dir = os.path.join(os.path.dirname(xilinx_vivado), "bin")
        parent_vivado_exe = os.path.join(parent_bin_dir, "vivado")
        print(
            f"    Parent bin directory: {parent_bin_dir} {'✓' if os.path.exists(parent_bin_dir) else '✗'}"
        )
        print(
            f"    Parent vivado executable: {parent_vivado_exe} {'✓' if os.path.isfile(parent_vivado_exe) else '✗'}"
        )

    # Final detection result
    print(f"\n=== Final Detection Result ===")
    vivado_info = find_vivado_installation()
    if vivado_info:
        print(f"✓ Vivado found:")
        print(f"  Path: {vivado_info['path']}")
        print(f"  Version: {vivado_info['version']}")
        print(f"  Executable: {vivado_info['executable']}")
        print(f"  Bin Path: {vivado_info['bin_path']}")
    else:
        print("✗ Vivado not found on this system.")
        print("\nTo install Vivado:")
        print("1. Download from: https://www.xilinx.com/support/download.html")
        print("2. Install to a standard location:")
        if system == "linux":
            print("   - /opt/Xilinx/Vivado/[version]/")
            print("   - /tools/Xilinx/Vivado/[version]/")
        elif system == "darwin":
            print("   - /Applications/Xilinx/Vivado/[version]/")
        print("3. Or set XILINX_VIVADO environment variable")
        print("4. Or add vivado to your PATH")


if __name__ == "__main__":
    # If run directly, print detailed Vivado information
    debug_vivado_search()
