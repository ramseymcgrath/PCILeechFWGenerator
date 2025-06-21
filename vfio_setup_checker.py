#!/usr/bin/env python3
"""
PCILeech VFIO Setup Checker and Diagnostic Tool

This comprehensive tool checks, diagnoses, and helps fix VFIO configuration issues
that prevent PCILeech from accessing PCI devices for firmware generation.

Features:
- Complete VFIO system diagnostics
- Device compatibility checking
- Interactive remediation
- Script generation for automated fixes
- Integration with PCILeech workflows

Usage:
    python3 vfio_setup_checker.py                    # Check general VFIO setup
    python3 vfio_setup_checker.py 0000:03:00.0       # Check specific device
    python3 vfio_setup_checker.py --interactive      # Interactive remediation
    python3 vfio_setup_checker.py --generate-script  # Generate fix script
    python3 vfio_setup_checker.py --list-devices     # List all PCI devices with VFIO status
"""

import argparse
import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

    @classmethod
    def disable(cls):
        """Disable colors for non-TTY output."""
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = ""
        cls.MAGENTA = cls.CYAN = cls.WHITE = cls.BOLD = ""
        cls.UNDERLINE = cls.END = ""


def run_command(
    cmd: str, capture_output: bool = True, check: bool = False
) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=capture_output, text=True, check=check
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout or "", e.stderr or ""
    except Exception as e:
        return -1, "", str(e)


def check_linux_platform() -> bool:
    """Check if running on Linux."""
    if platform.system() != "Linux":
        print(
            f"{Colors.RED}❌ Error: VFIO requires Linux. Current platform: {platform.system()}{Colors.END}"
        )
        print("Please run this tool on a Linux system with VFIO support.")
        return False
    return True


def check_root_privileges() -> bool:
    """Check if running as root."""
    if os.geteuid() != 0:
        print(f"{Colors.YELLOW}⚠️  Warning: Not running as root.{Colors.END}")
        print("Some checks and fixes require root privileges.")
        print("Consider running with sudo for complete diagnostics.")
        return False
    return True


def check_iommu_enabled() -> Tuple[bool, List[str]]:
    """Check if IOMMU is enabled in the kernel."""
    issues = []

    print(f"{Colors.BOLD}=== Checking IOMMU Status ==={Colors.END}")

    # Check kernel command line
    try:
        with open("/proc/cmdline", "r") as f:
            cmdline = f.read().strip()

        intel_iommu = "intel_iommu=on" in cmdline
        amd_iommu = "amd_iommu=on" in cmdline

        print(f"Kernel command line: {cmdline}")
        print(
            f"Intel IOMMU enabled: {Colors.GREEN if intel_iommu else Colors.RED}{intel_iommu}{Colors.END}"
        )
        print(
            f"AMD IOMMU enabled: {Colors.GREEN if amd_iommu else Colors.RED}{amd_iommu}{Colors.END}"
        )

        if not (intel_iommu or amd_iommu):
            issues.append("IOMMU not enabled in kernel parameters")
            print(f"{Colors.RED}❌ IOMMU not enabled in kernel parameters!{Colors.END}")
            print(
                "   Add 'intel_iommu=on' (Intel) or 'amd_iommu=on' (AMD) to GRUB_CMDLINE_LINUX"
            )
        else:
            print(f"{Colors.GREEN}✅ IOMMU enabled in kernel parameters{Colors.END}")

    except Exception as e:
        issues.append(f"Could not check kernel command line: {e}")
        print(f"{Colors.RED}❌ Could not check kernel command line: {e}{Colors.END}")

    # Check dmesg for IOMMU messages
    print(f"\n{Colors.BOLD}--- IOMMU Messages in dmesg ---{Colors.END}")
    ret, stdout, stderr = run_command("dmesg | grep -i iommu | head -10")
    if stdout:
        for line in stdout.strip().split("\n"):
            if "enabled" in line.lower():
                print(f"{Colors.GREEN}{line}{Colors.END}")
            elif "disabled" in line.lower() or "error" in line.lower():
                print(f"{Colors.RED}{line}{Colors.END}")
            else:
                print(line)
    else:
        print("No IOMMU messages found in dmesg")
        issues.append("No IOMMU messages in dmesg")

    return len(issues) == 0, issues


def check_iommu_groups() -> Tuple[bool, List[str], Dict[str, List[str]]]:
    """Check available IOMMU groups and return device mapping."""
    issues = []
    device_groups = {}

    print(f"\n{Colors.BOLD}=== Checking IOMMU Groups ==={Colors.END}")

    iommu_groups_path = Path("/sys/kernel/iommu_groups")
    if not iommu_groups_path.exists():
        issues.append("/sys/kernel/iommu_groups does not exist")
        print(f"{Colors.RED}❌ /sys/kernel/iommu_groups does not exist{Colors.END}")
        print("   This means IOMMU is not working properly")
        return False, issues, device_groups

    groups = list(iommu_groups_path.glob("*"))
    if not groups:
        issues.append("No IOMMU groups found")
        print(f"{Colors.RED}❌ No IOMMU groups found{Colors.END}")
        return False, issues, device_groups

    print(f"{Colors.GREEN}✅ Found {len(groups)} IOMMU groups{Colors.END}")

    # Map devices to groups
    for group_path in sorted(groups):
        group_num = group_path.name
        devices_path = group_path / "devices"
        if devices_path.exists():
            devices = [device.name for device in devices_path.glob("*")]
            device_groups[group_num] = devices

            if len(groups) <= 10:  # Show details for small number of groups
                print(f"  Group {group_num}: {len(devices)} devices")
                for device in devices[:3]:  # Show first 3 devices per group
                    try:
                        ret, desc, _ = run_command(f"lspci -s {device}")
                        if desc:
                            desc = desc.strip().split("\n")[0]
                            print(f"    {device}: {desc}")
                    except:
                        print(f"    {device}")
                if len(devices) > 3:
                    print(f"    ... and {len(devices) - 3} more devices")

    if len(groups) > 10:
        print(f"  ... showing first 10 groups, {len(groups) - 10} more available")

    return True, issues, device_groups


def check_vfio_modules() -> Tuple[bool, List[str]]:
    """Check if VFIO modules are loaded."""
    issues = []

    print(f"\n{Colors.BOLD}=== Checking VFIO Modules ==={Colors.END}")

    required_modules = ["vfio", "vfio_pci", "vfio_iommu_type1"]

    ret, stdout, stderr = run_command("lsmod")
    loaded_modules = stdout.lower()

    all_loaded = True
    for module in required_modules:
        if module in loaded_modules:
            print(f"{Colors.GREEN}✅ {module} is loaded{Colors.END}")
        else:
            print(f"{Colors.RED}❌ {module} is not loaded{Colors.END}")
            issues.append(f"Module {module} is not loaded")
            all_loaded = False

    if not all_loaded:
        print(f"\n{Colors.YELLOW}To load VFIO modules:{Colors.END}")
        for module in required_modules:
            print(f"  sudo modprobe {module}")

    return all_loaded, issues


def get_device_info(bdf: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a PCI device."""
    try:
        ret, stdout, stderr = run_command(f"lspci -s {bdf} -v")
        if ret != 0 or not stdout:
            return None

        info: Dict[str, Any] = {
            "bdf": bdf,
            "description": stdout.strip().split("\n")[0],
        }

        # Check IOMMU group
        iommu_group_path = Path(f"/sys/bus/pci/devices/{bdf}/iommu_group")
        if iommu_group_path.exists():
            try:
                group_id = iommu_group_path.resolve().name
                info["iommu_group"] = group_id
                info["vfio_compatible"] = True
            except:
                info["vfio_compatible"] = False
        else:
            info["vfio_compatible"] = False

        # Check current driver
        driver_path = Path(f"/sys/bus/pci/devices/{bdf}/driver")
        if driver_path.exists() and driver_path.is_symlink():
            try:
                info["current_driver"] = driver_path.resolve().name
            except:
                info["current_driver"] = "unknown"
        else:
            info["current_driver"] = "none"

        return info
    except Exception:
        return None


def list_all_devices() -> List[Dict[str, Any]]:
    """List all PCI devices with their VFIO compatibility status."""
    devices = []

    ret, stdout, stderr = run_command("lspci -D")
    if ret != 0:
        return devices

    for line in stdout.strip().split("\n"):
        if line:
            bdf = line.split()[0]
            device_info = get_device_info(bdf)
            if device_info:
                devices.append(device_info)

    return devices


def check_device_vfio_compatibility(
    bdf: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    """Check if devices are VFIO compatible."""
    issues = []

    print(f"\n{Colors.BOLD}=== Checking Device VFIO Compatibility ==={Colors.END}")

    if bdf:
        device_info = get_device_info(bdf)
        if not device_info:
            issues.append(f"Device {bdf} not found")
            print(f"{Colors.RED}❌ Device {bdf} not found{Colors.END}")
            return False, issues

        print(f"Device: {device_info['description']}")
        print(f"Current driver: {device_info.get('current_driver', 'none')}")

        if device_info.get("vfio_compatible", False):
            group = device_info.get("iommu_group", "unknown")
            print(
                f"{Colors.GREEN}✅ VFIO compatible (IOMMU Group: {group}){Colors.END}"
            )
            return True, issues
        else:
            issues.append(f"Device {bdf} is not VFIO compatible")
            print(f"{Colors.RED}❌ Not VFIO compatible (no IOMMU group){Colors.END}")
            return False, issues
    else:
        # Check all devices
        devices = list_all_devices()
        vfio_compatible = [d for d in devices if d.get("vfio_compatible", False)]
        non_vfio = [d for d in devices if not d.get("vfio_compatible", False)]

        if vfio_compatible:
            print(
                f"{Colors.GREEN}✅ VFIO-Compatible Devices: {len(vfio_compatible)}{Colors.END}"
            )
            for device in vfio_compatible[:5]:  # Show first 5
                group = device.get("iommu_group", "unknown")
                print(f"  {device['bdf']} (Group {group}): {device['description']}")
            if len(vfio_compatible) > 5:
                print(f"  ... and {len(vfio_compatible) - 5} more")

        if non_vfio:
            print(f"\n{Colors.YELLOW}⚠️  Non-VFIO Devices: {len(non_vfio)}{Colors.END}")
            if len(non_vfio) <= 5:
                for device in non_vfio:
                    print(f"  {device['bdf']}: {device['description']}")

        return len(vfio_compatible) > 0, issues


def generate_remediation_script(issues: List[str]) -> str:
    """Generate a shell script to fix identified issues."""
    script_lines = [
        "#!/bin/bash",
        "# PCILeech VFIO Remediation Script",
        "# Generated automatically - review before running",
        "",
        "set -euo pipefail",
        "",
        "echo '🔧 PCILeech VFIO Remediation Script'",
        "echo '=================================='",
        "",
    ]

    # Check for IOMMU kernel parameter issues
    if any("IOMMU not enabled" in issue for issue in issues):
        script_lines.extend(
            [
                "echo '📝 Adding IOMMU kernel parameters...'",
                "",
                "# Backup GRUB config",
                "cp /etc/default/grub /etc/default/grub.backup.$(date +%Y%m%d_%H%M%S)",
                "",
                "# Detect CPU vendor and add appropriate IOMMU parameter",
                "if grep -q 'vendor_id.*Intel' /proc/cpuinfo; then",
                "    echo 'Detected Intel CPU, adding intel_iommu=on'",
                '    sed -i \'s/GRUB_CMDLINE_LINUX="\\(.*\\)"/GRUB_CMDLINE_LINUX="\\1 intel_iommu=on"/\' /etc/default/grub',
                "elif grep -q 'vendor_id.*AMD' /proc/cpuinfo; then",
                "    echo 'Detected AMD CPU, adding amd_iommu=on'",
                '    sed -i \'s/GRUB_CMDLINE_LINUX="\\(.*\\)"/GRUB_CMDLINE_LINUX="\\1 amd_iommu=on"/\' /etc/default/grub',
                "fi",
                "",
                "# Update GRUB",
                "if command -v update-grub >/dev/null 2>&1; then",
                "    update-grub",
                "elif command -v grub2-mkconfig >/dev/null 2>&1; then",
                "    grub2-mkconfig -o /boot/grub2/grub.cfg",
                "else",
                "    echo 'Warning: Could not update GRUB automatically'",
                "fi",
                "",
            ]
        )

    # Check for module loading issues
    if any("Module" in issue and "not loaded" in issue for issue in issues):
        script_lines.extend(
            [
                "echo '📦 Loading VFIO modules...'",
                "modprobe vfio",
                "modprobe vfio_pci",
                "modprobe vfio_iommu_type1",
                "",
                "echo '📝 Adding modules to /etc/modules for persistent loading...'",
                "echo 'vfio' >> /etc/modules",
                "echo 'vfio_pci' >> /etc/modules",
                "echo 'vfio_iommu_type1' >> /etc/modules",
                "",
            ]
        )

    script_lines.extend(
        [
            "echo '✅ Remediation complete!'",
            "echo ''",
            "echo 'Next steps:'",
            "echo '1. Reboot your system to apply kernel parameter changes'",
            "echo '2. Run this checker again to verify the fixes'",
            "echo '3. Try running PCILeech with a VFIO-compatible device'",
            "",
        ]
    )

    return "\n".join(script_lines)


def interactive_remediation(issues: List[str]) -> bool:
    """Interactively guide user through fixing issues."""
    if not issues:
        print(f"{Colors.GREEN}✅ No issues found that require remediation!{Colors.END}")
        return True

    print(f"\n{Colors.BOLD}=== Interactive Remediation ==={Colors.END}")
    print(f"Found {len(issues)} issues that can be fixed:")

    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

    print(
        f"\n{Colors.YELLOW}Would you like to generate a remediation script? (y/N):{Colors.END} ",
        end="",
    )
    response = input().strip().lower()

    if response in ["y", "yes"]:
        script_content = generate_remediation_script(issues)
        script_path = "vfio_remediation.sh"

        with open(script_path, "w") as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)
        print(
            f"\n{Colors.GREEN}📝 Remediation script generated: {script_path}{Colors.END}"
        )
        print("To apply fixes, run:")
        print(f"   sudo ./{script_path}")

        print(
            f"\n{Colors.YELLOW}Would you like to run the script now? (y/N):{Colors.END} ",
            end="",
        )
        run_response = input().strip().lower()

        if run_response in ["y", "yes"]:
            if os.geteuid() != 0:
                print(
                    f"{Colors.RED}❌ Root privileges required to run remediation script{Colors.END}"
                )
                return False

            print(f"\n{Colors.BLUE}🚀 Running remediation script...{Colors.END}")
            ret, stdout, stderr = run_command(f"bash {script_path}")

            if ret == 0:
                print(
                    f"{Colors.GREEN}✅ Remediation script completed successfully{Colors.END}"
                )
                return True
            else:
                print(f"{Colors.RED}❌ Remediation script failed{Colors.END}")
                if stderr:
                    print(f"Error: {stderr}")
                return False

    return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="PCILeech VFIO Setup Checker and Diagnostic Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Check general VFIO setup
  %(prog)s 0000:03:00.0              # Check specific device
  %(prog)s --interactive             # Interactive mode with remediation
  %(prog)s --list-devices            # List all devices with VFIO status
  %(prog)s --generate-script         # Generate remediation script
  %(prog)s 0000:00:17.0 --interactive # Check device with interactive fixes

This tool helps diagnose and fix VFIO configuration issues that prevent
PCILeech from accessing PCI devices for firmware generation.
        """,
    )

    parser.add_argument(
        "device_bdf",
        nargs="?",
        help="PCI device BDF (Bus:Device.Function) to check, e.g., 0000:03:00.0",
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Enable interactive remediation mode",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress detailed output, only show summary",
    )

    parser.add_argument(
        "--generate-script",
        action="store_true",
        help="Generate remediation script without running it",
    )

    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List all PCI devices with VFIO compatibility status",
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    args = parser.parse_args()

    # Disable colors if requested or not a TTY
    if args.no_color or not sys.stdout.isatty():
        Colors.disable()

    # Handle device listing
    if args.list_devices:
        print(f"{Colors.BOLD}PCILeech VFIO Device Compatibility Report{Colors.END}")
        print("=" * 50)

        devices = list_all_devices()
        vfio_devices = [d for d in devices if d.get("vfio_compatible", False)]
        non_vfio_devices = [d for d in devices if not d.get("vfio_compatible", False)]

        if vfio_devices:
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}✅ VFIO-Compatible Devices ({len(vfio_devices)}):{Colors.END}"
            )
            for device in vfio_devices:
                group = device.get("iommu_group", "unknown")
                driver = device.get("current_driver", "none")
                print(
                    f"  {device['bdf']} [Group {group}] [{driver}]: {device['description']}"
                )

        if non_vfio_devices:
            print(
                f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Non-VFIO Devices ({len(non_vfio_devices)}):{Colors.END}"
            )
            for device in non_vfio_devices:
                driver = device.get("current_driver", "none")
                print(f"  {device['bdf']} [{driver}]: {device['description']}")

        return 0

    # Main diagnostic flow
    if not args.quiet:
        print(f"{Colors.BOLD}{Colors.BLUE}🔧 PCILeech VFIO Setup Checker{Colors.END}")
        print("=" * 50)
        print("Checking VFIO setup for PCILeech compatibility...")

        if args.device_bdf:
            print(f"Target Device: {args.device_bdf}")
        print()

    # Platform check
    if not check_linux_platform():
        return 1

    # Root privilege check
    is_root = check_root_privileges()

    # Run all checks
    all_issues = []

    iommu_ok, iommu_issues = check_iommu_enabled()
    all_issues.extend(iommu_issues)

    groups_ok, group_issues, device_groups = check_iommu_groups()
    all_issues.extend(group_issues)

    modules_ok, module_issues = check_vfio_modules()
    all_issues.extend(module_issues)

    devices_ok, device_issues = check_device_vfio_compatibility(args.device_bdf)
    all_issues.extend(device_issues)

    # Summary
    print(f"\n{Colors.BOLD}=== Summary ==={Colors.END}")
    overall_ok = iommu_ok and groups_ok and modules_ok and devices_ok

    if overall_ok:
        print(
            f"{Colors.GREEN}✅ Your system appears to be properly configured for VFIO!{Colors.END}"
        )
        print("   You should be able to use PCILeech with VFIO devices.")

        if args.device_bdf:
            device_info = get_device_info(args.device_bdf)
            if device_info and device_info.get("vfio_compatible", False):
                print(f"   Device {args.device_bdf} is ready for use with PCILeech.")
    else:
        print(f"{Colors.RED}❌ Your system has VFIO configuration issues.{Colors.END}")
        print(f"   Found {len(all_issues)} issues that need to be resolved.")

    # Handle remediation
    if all_issues:
        if args.generate_script:
            script_content = generate_remediation_script(all_issues)
            script_path = "vfio_remediation.sh"

            with open(script_path, "w") as f:
                f.write(script_content)

            os.chmod(script_path, 0o755)
            print(
                f"\n{Colors.GREEN}📝 Remediation script generated: {script_path}{Colors.END}"
            )
            print("To apply fixes, run:")
            print(f"   sudo ./{script_path}")

        elif args.interactive:
            interactive_remediation(all_issues)

        else:
            print(f"\n{Colors.YELLOW}💡 Recommendations:{Colors.END}")
            print("1. Enable IOMMU in BIOS/UEFI:")
            print("   - Look for 'VT-d' (Intel) or 'AMD-Vi' (AMD) settings")
            print("   - Enable 'Virtualization Technology for Directed I/O'")
            print("\n2. Add IOMMU to kernel parameters:")
            print("   - Edit /etc/default/grub")
            print("   - Add 'intel_iommu=on' or 'amd_iommu=on' to GRUB_CMDLINE_LINUX")
            print("   - Run: sudo update-grub && sudo reboot")
            print("\n3. Load VFIO modules:")
            print("   sudo modprobe vfio vfio_pci vfio_iommu_type1")
            print(f"\n4. Run with --interactive for guided remediation")
            print(f"5. Run with --generate-script to create an automated fix script")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Operation cancelled by user.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
        sys.exit(1)
