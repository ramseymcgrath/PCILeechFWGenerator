#!/usr/bin/env python3
"""
VFIO Constants Patcher - Updates vfio_constants.py with kernel-correct values

This script:
1. Compiles and runs the vfio_helper C program to extract kernel constants
2. Parses the output to get the correct ioctl numbers
3. Updates src/cli/vfio_constants.py with the correct hard-coded values
4. Preserves all other content in the file unchanged

The approach switches from dynamic computation to hard-coded constants because:
- Dynamic computation can fail if ctypes struct sizes don't match kernel exactly
- Hard-coded values from kernel headers are guaranteed correct
- Build-time extraction ensures kernel version compatibility
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def compile_and_run_helper():
    """Compile vfio_helper.c and run it to extract constants."""

    # Compile the helper
    compile_cmd = [
        "gcc",
        "-Wall",
        "-Werror",
        "-O2",
        "-o",
        "vfio_helper",
        "vfio_helper.c",
    ]

    print("Compiling vfio_helper...")
    try:
        subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)

    # Run the helper to get constants
    print("Extracting VFIO constants...")
    try:
        result = subprocess.run(
            ["./vfio_helper"], check=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Helper execution failed: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)


def parse_constants(output):
    """Parse the helper output into a dictionary of constants."""
    constants = {}
    for line in output.split("\n"):
        if "=" in line:
            name, value = line.split("=", 1)
            constants[name.strip()] = int(value.strip())
    return constants


def update_vfio_constants_file(constants):
    """Update src/cli/vfio_constants.py with the extracted constants."""

    vfio_constants_path = Path("src/cli/vfio_constants.py")
    if not vfio_constants_path.exists():
        print(f"Error: {vfio_constants_path} not found!")
        sys.exit(1)

    # Read the current file
    with open(vfio_constants_path, "r") as f:
        content = f.read()

    # Create the new constants section
    new_constants = []
    new_constants.append(
        "# ───── Ioctl numbers – extracted from kernel headers at build time ──────"
    )

    # Add each constant with its extracted value
    for const_name, const_value in constants.items():
        new_constants.append(f"{const_name} = {const_value}")

    # Add any missing constants that weren't in the original file
    missing_constants = {
        "VFIO_SET_IOMMU": 15206,  # VFIO_BASE + 2
        "VFIO_GROUP_SET_CONTAINER": 15208,  # VFIO_BASE + 4
        "VFIO_GROUP_UNSET_CONTAINER": 15209,  # VFIO_BASE + 5
    }

    for missing, fallback_value in missing_constants.items():
        if missing not in constants:
            # Add fallback values for missing constants
            print(
                f"Warning: {missing} not found in kernel headers output, using fallback value {fallback_value}"
            )
            constants[missing] = fallback_value

    new_constants_text = "\n".join(new_constants)

    # Replace the section from "# ───── Ioctl numbers" to the end of constants
    # This preserves everything before the constants section
    pattern = r"# ───── Ioctl numbers.*?(?=\n\n# Export all constants|\n\n__all__|$)"

    if re.search(pattern, content, re.DOTALL):
        # Replace existing constants section
        new_content = re.sub(pattern, new_constants_text, content, flags=re.DOTALL)
    else:
        # If pattern not found, append before __all__ section
        all_pattern = r"(# Export all constants\n__all__)"
        if re.search(all_pattern, content):
            new_content = re.sub(all_pattern, f"{new_constants_text}\n\n\n\\1", content)
        else:
            # Fallback: append at end
            new_content = content + "\n\n" + new_constants_text

    # Write the updated file
    with open(vfio_constants_path, "w") as f:
        f.write(new_content)

    print(f"Updated {vfio_constants_path} with {len(constants)} constants")

    # Show what was updated
    for name, value in constants.items():
        print(f"  {name} = {value}")


def main():
    """Main function to orchestrate the patching process."""

    print("VFIO Constants Patcher")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("src/cli/vfio_constants.py").exists():
        print("Error: Must run from project root directory")
        print("Expected to find: src/cli/vfio_constants.py")
        sys.exit(1)

    # Check if helper source exists
    if not Path("vfio_helper.c").exists():
        print("Error: vfio_helper.c not found in current directory")
        sys.exit(1)

    # Extract constants from kernel
    output = compile_and_run_helper()
    constants = parse_constants(output)

    if not constants:
        print("Error: No constants extracted from helper")
        sys.exit(1)

    # Update the Python file
    update_vfio_constants_file(constants)

    # Cleanup
    if Path("vfio_helper").exists():
        os.unlink("vfio_helper")

    print("\nPatching complete!")
    print("The vfio_constants.py file now contains kernel-correct ioctl numbers.")


if __name__ == "__main__":
    main()
