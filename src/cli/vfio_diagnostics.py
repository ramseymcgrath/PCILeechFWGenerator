#!/usr/bin/env python3
"""
VFIO Diagnostics and Remediation System

Provides automated checks for VFIO prerequisites and guided remediation
for common VFIO configuration issues.
"""

import logging
import os
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class VFIOStatus(Enum):
    """VFIO component status levels."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    MISSING = "missing"


@dataclass
class VFIOCheck:
    """Represents a single VFIO diagnostic check."""

    name: str
    status: VFIOStatus
    message: str
    remediation: Optional[str] = None
    commands: Optional[List[str]] = None


@dataclass
class VFIODiagnosticResult:
    """Complete VFIO diagnostic results."""

    overall_status: VFIOStatus
    checks: List[VFIOCheck]
    device_bdf: Optional[str] = None
    can_proceed: bool = False
    critical_issues: Optional[List[str]] = None


class VFIODiagnostics:
    """VFIO diagnostic and remediation system."""

    def __init__(self, device_bdf: Optional[str] = None):
        self.device_bdf = device_bdf
        self.checks = []

    def run_full_diagnostic(self) -> VFIODiagnosticResult:
        """Run complete VFIO diagnostic suite."""
        logger.info("Running comprehensive VFIO diagnostic...")

        self.checks = []

        # Core system checks
        self._check_linux_platform()
        self._check_iommu_support()
        self._check_iommu_enabled()
        self._check_vfio_modules()
        self._check_vfio_drivers()

        # Device-specific checks if BDF provided
        if self.device_bdf:
            self._check_device_exists()
            self._check_device_iommu_group()
            self._check_device_driver_status()
            self._check_vfio_device_availability()

        # Determine overall status
        overall_status = self._determine_overall_status()
        critical_issues = [
            check.message for check in self.checks if check.status == VFIOStatus.ERROR
        ]
        can_proceed = overall_status in [VFIOStatus.OK, VFIOStatus.WARNING]

        return VFIODiagnosticResult(
            overall_status=overall_status,
            checks=self.checks,
            device_bdf=self.device_bdf,
            can_proceed=can_proceed,
            critical_issues=critical_issues,
        )

    def _check_linux_platform(self) -> None:
        """Check if running on Linux platform."""
        import platform

        if platform.system().lower() == "linux":
            self.checks.append(
                VFIOCheck(
                    name="Linux Platform",
                    status=VFIOStatus.OK,
                    message="Running on Linux platform",
                )
            )
        else:
            self.checks.append(
                VFIOCheck(
                    name="Linux Platform",
                    status=VFIOStatus.ERROR,
                    message=f"VFIO requires Linux, currently on {platform.system()}",
                    remediation="Run this tool on a Linux system with VFIO support",
                )
            )

    def _check_iommu_support(self) -> None:
        """Check if IOMMU is supported by hardware."""
        try:
            # Check CPU flags for IOMMU support
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()

            intel_iommu = "vmx" in cpuinfo and "ept" in cpuinfo
            amd_iommu = "svm" in cpuinfo and "npt" in cpuinfo

            if intel_iommu or amd_iommu:
                cpu_type = "Intel VT-d" if intel_iommu else "AMD-Vi"
                self.checks.append(
                    VFIOCheck(
                        name="IOMMU Hardware Support",
                        status=VFIOStatus.OK,
                        message=f"IOMMU supported by hardware ({cpu_type})",
                    )
                )
            else:
                self.checks.append(
                    VFIOCheck(
                        name="IOMMU Hardware Support",
                        status=VFIOStatus.WARNING,
                        message="Cannot detect IOMMU support in CPU flags",
                        remediation="Verify IOMMU is enabled in BIOS/UEFI settings",
                    )
                )
        except Exception as e:
            self.checks.append(
                VFIOCheck(
                    name="IOMMU Hardware Support",
                    status=VFIOStatus.WARNING,
                    message=f"Could not check IOMMU support: {e}",
                    remediation="Manually verify IOMMU is enabled in BIOS/UEFI",
                )
            )

    def _check_iommu_enabled(self) -> None:
        """Check if IOMMU is enabled in kernel."""
        try:
            # Check kernel command line
            with open("/proc/cmdline", "r") as f:
                cmdline = f.read().strip()

            intel_enabled = "intel_iommu=on" in cmdline
            amd_enabled = "amd_iommu=on" in cmdline or "iommu=pt" in cmdline

            if intel_enabled or amd_enabled:
                self.checks.append(
                    VFIOCheck(
                        name="IOMMU Kernel Parameter",
                        status=VFIOStatus.OK,
                        message="IOMMU enabled in kernel parameters",
                    )
                )
            else:
                self.checks.append(
                    VFIOCheck(
                        name="IOMMU Kernel Parameter",
                        status=VFIOStatus.ERROR,
                        message="IOMMU not enabled in kernel parameters",
                        remediation="Add IOMMU parameters to kernel command line",
                        commands=[
                            "sudo sed -i 's/GRUB_CMDLINE_LINUX=\"/GRUB_CMDLINE_LINUX=\"intel_iommu=on iommu=pt /' /etc/default/grub",
                            "sudo update-grub",
                            "reboot",
                        ],
                    )
                )

            # Check dmesg for IOMMU initialization
            try:
                result = subprocess.run(
                    ["dmesg"], capture_output=True, text=True, timeout=10
                )
                dmesg_output = result.stdout

                if any(
                    pattern in dmesg_output
                    for pattern in ["IOMMU enabled", "Intel-IOMMU", "AMD-Vi", "DMAR"]
                ):
                    self.checks.append(
                        VFIOCheck(
                            name="IOMMU Runtime Status",
                            status=VFIOStatus.OK,
                            message="IOMMU detected as active in kernel logs",
                        )
                    )
                else:
                    self.checks.append(
                        VFIOCheck(
                            name="IOMMU Runtime Status",
                            status=VFIOStatus.WARNING,
                            message="IOMMU not detected in kernel logs",
                            remediation="Check BIOS settings and kernel parameters",
                        )
                    )
            except Exception:
                self.checks.append(
                    VFIOCheck(
                        name="IOMMU Runtime Status",
                        status=VFIOStatus.WARNING,
                        message="Could not check IOMMU status in kernel logs",
                    )
                )

        except Exception as e:
            self.checks.append(
                VFIOCheck(
                    name="IOMMU Kernel Parameter",
                    status=VFIOStatus.ERROR,
                    message=f"Could not check kernel parameters: {e}",
                )
            )

    def _check_vfio_modules(self) -> None:
        """Check if VFIO kernel modules are loaded."""
        required_modules = ["vfio", "vfio_pci", "vfio_iommu_type1"]
        loaded_modules = []
        missing_modules = []

        for module in required_modules:
            module_path = f"/sys/module/{module}"
            if os.path.exists(module_path):
                loaded_modules.append(module)
            else:
                missing_modules.append(module)

        if not missing_modules:
            self.checks.append(
                VFIOCheck(
                    name="VFIO Kernel Modules",
                    status=VFIOStatus.OK,
                    message=f"All VFIO modules loaded: {', '.join(loaded_modules)}",
                )
            )
        elif loaded_modules:
            self.checks.append(
                VFIOCheck(
                    name="VFIO Kernel Modules",
                    status=VFIOStatus.WARNING,
                    message=f"Some VFIO modules missing: {', '.join(missing_modules)}",
                    remediation="Load missing VFIO modules",
                    commands=[f"sudo modprobe {module}" for module in missing_modules],
                )
            )
        else:
            self.checks.append(
                VFIOCheck(
                    name="VFIO Kernel Modules",
                    status=VFIOStatus.ERROR,
                    message="No VFIO modules loaded",
                    remediation="Load VFIO kernel modules",
                    commands=[
                        "sudo modprobe vfio",
                        "sudo modprobe vfio-pci",
                        "sudo modprobe vfio_iommu_type1",
                    ],
                )
            )

    def _check_vfio_drivers(self) -> None:
        """Check if VFIO drivers are available."""
        vfio_pci_path = "/sys/bus/pci/drivers/vfio-pci"

        if os.path.exists(vfio_pci_path):
            self.checks.append(
                VFIOCheck(
                    name="VFIO-PCI Driver",
                    status=VFIOStatus.OK,
                    message="vfio-pci driver available",
                )
            )
        else:
            self.checks.append(
                VFIOCheck(
                    name="VFIO-PCI Driver",
                    status=VFIOStatus.ERROR,
                    message="vfio-pci driver not available",
                    remediation="Ensure VFIO is compiled into kernel or load vfio-pci module",
                    commands=["sudo modprobe vfio-pci"],
                )
            )

    def _check_device_exists(self) -> None:
        """Check if the target device exists."""
        if not self.device_bdf:
            return

        device_path = f"/sys/bus/pci/devices/{self.device_bdf}"

        if os.path.exists(device_path):
            # Get device info
            try:
                with open(f"{device_path}/vendor", "r") as f:
                    vendor = f.read().strip()
                with open(f"{device_path}/device", "r") as f:
                    device = f.read().strip()

                self.checks.append(
                    VFIOCheck(
                        name="Target Device",
                        status=VFIOStatus.OK,
                        message=f"Device {self.device_bdf} found (vendor:{vendor} device:{device})",
                    )
                )
            except Exception as e:
                self.checks.append(
                    VFIOCheck(
                        name="Target Device",
                        status=VFIOStatus.WARNING,
                        message=f"Device {self.device_bdf} found but could not read details: {e}",
                    )
                )
        else:
            self.checks.append(
                VFIOCheck(
                    name="Target Device",
                    status=VFIOStatus.ERROR,
                    message=f"Device {self.device_bdf} not found",
                    remediation="Verify device BDF is correct using 'lspci'",
                )
            )

    def _check_device_iommu_group(self) -> None:
        """Check if device has IOMMU group."""
        if not self.device_bdf:
            return

        iommu_group_path = f"/sys/bus/pci/devices/{self.device_bdf}/iommu_group"

        if os.path.exists(iommu_group_path):
            try:
                group = os.path.basename(os.readlink(iommu_group_path))
                self.checks.append(
                    VFIOCheck(
                        name="Device IOMMU Group",
                        status=VFIOStatus.OK,
                        message=f"Device {self.device_bdf} in IOMMU group {group}",
                    )
                )
            except Exception as e:
                self.checks.append(
                    VFIOCheck(
                        name="Device IOMMU Group",
                        status=VFIOStatus.ERROR,
                        message=f"Could not read IOMMU group for {self.device_bdf}: {e}",
                    )
                )
        else:
            self.checks.append(
                VFIOCheck(
                    name="Device IOMMU Group",
                    status=VFIOStatus.ERROR,
                    message=f"No IOMMU group for device {self.device_bdf}",
                    remediation="Ensure IOMMU is enabled and device supports IOMMU",
                )
            )

    def _check_device_driver_status(self) -> None:
        """Check current driver binding for device."""
        if not self.device_bdf:
            return

        driver_path = f"/sys/bus/pci/devices/{self.device_bdf}/driver"

        if os.path.exists(driver_path):
            try:
                current_driver = os.path.basename(os.readlink(driver_path))
                if current_driver == "vfio-pci":
                    self.checks.append(
                        VFIOCheck(
                            name="Device Driver Binding",
                            status=VFIOStatus.OK,
                            message=f"Device {self.device_bdf} already bound to vfio-pci",
                        )
                    )
                else:
                    self.checks.append(
                        VFIOCheck(
                            name="Device Driver Binding",
                            status=VFIOStatus.WARNING,
                            message=f"Device {self.device_bdf} bound to {current_driver}, needs rebinding to vfio-pci",
                            remediation="Device will be automatically rebound during operation",
                        )
                    )
            except Exception as e:
                self.checks.append(
                    VFIOCheck(
                        name="Device Driver Binding",
                        status=VFIOStatus.WARNING,
                        message=f"Could not determine driver for {self.device_bdf}: {e}",
                    )
                )
        else:
            self.checks.append(
                VFIOCheck(
                    name="Device Driver Binding",
                    status=VFIOStatus.WARNING,
                    message=f"Device {self.device_bdf} not bound to any driver",
                )
            )

    def _check_vfio_device_availability(self) -> None:
        """Check if VFIO device file is available."""
        if not self.device_bdf:
            return

        try:
            iommu_group_path = f"/sys/bus/pci/devices/{self.device_bdf}/iommu_group"
            if os.path.exists(iommu_group_path):
                group = os.path.basename(os.readlink(iommu_group_path))
                vfio_device = f"/dev/vfio/{group}"

                if os.path.exists(vfio_device):
                    self.checks.append(
                        VFIOCheck(
                            name="VFIO Device File",
                            status=VFIOStatus.OK,
                            message=f"VFIO device {vfio_device} available",
                        )
                    )
                else:
                    self.checks.append(
                        VFIOCheck(
                            name="VFIO Device File",
                            status=VFIOStatus.WARNING,
                            message=f"VFIO device {vfio_device} not found",
                            remediation="Device will be bound to vfio-pci during operation",
                        )
                    )
        except Exception as e:
            self.checks.append(
                VFIOCheck(
                    name="VFIO Device File",
                    status=VFIOStatus.WARNING,
                    message=f"Could not check VFIO device availability: {e}",
                )
            )

    def _determine_overall_status(self) -> VFIOStatus:
        """Determine overall VFIO status from individual checks."""
        if any(check.status == VFIOStatus.ERROR for check in self.checks):
            return VFIOStatus.ERROR
        elif any(check.status == VFIOStatus.WARNING for check in self.checks):
            return VFIOStatus.WARNING
        else:
            return VFIOStatus.OK

    def print_diagnostic_report(self, result: VFIODiagnosticResult) -> None:
        """Print formatted diagnostic report."""
        print("\n" + "=" * 60)
        print("VFIO DIAGNOSTIC REPORT")
        print("=" * 60)

        # Overall status
        status_symbols = {
            VFIOStatus.OK: "✅",
            VFIOStatus.WARNING: "⚠️",
            VFIOStatus.ERROR: "❌",
            VFIOStatus.MISSING: "❓",
        }

        symbol = status_symbols.get(result.overall_status, "❓")
        print(f"\nOverall Status: {symbol} {result.overall_status.value.upper()}")

        if result.device_bdf:
            print(f"Target Device: {result.device_bdf}")

        print(f"Can Proceed: {'Yes' if result.can_proceed else 'No'}")

        # Individual checks
        print(f"\nDetailed Checks ({len(result.checks)} total):")
        print("-" * 60)

        for check in result.checks:
            symbol = status_symbols.get(check.status, "❓")
            print(f"{symbol} {check.name}: {check.message}")

            if check.remediation:
                print(f"   💡 Remediation: {check.remediation}")

            if check.commands:
                print("   🔧 Commands:")
                for cmd in check.commands:
                    print(f"      {cmd}")
            print()

        # Critical issues summary
        if result.critical_issues:
            print("🚨 CRITICAL ISSUES REQUIRING ATTENTION:")
            print("-" * 60)
            for issue in result.critical_issues:
                print(f"❌ {issue}")
            print()

        # Next steps
        print("📋 NEXT STEPS:")
        print("-" * 60)
        if result.can_proceed:
            print("✅ System is ready for VFIO operations")
            if any(check.status == VFIOStatus.WARNING for check in result.checks):
                print("⚠️  Some warnings present - monitor for issues")
        else:
            print("❌ System requires configuration before VFIO operations")
            print("   Please address the critical issues listed above")

        print("=" * 60)

    def get_remediation_script(self, result: VFIODiagnosticResult) -> str:
        """Generate a shell script to fix identified issues."""
        script_lines = [
            "#!/bin/bash",
            "# VFIO Remediation Script",
            "# Generated automatically by PCILeech VFIO Diagnostics",
            "",
            "set -e  # Exit on any error",
            "",
            "echo 'Starting VFIO remediation...'",
            "",
        ]

        for check in result.checks:
            if (
                check.status in [VFIOStatus.ERROR, VFIOStatus.WARNING]
                and check.commands
            ):
                script_lines.extend(
                    [f"# Fix: {check.name}", f"echo 'Fixing: {check.name}'"]
                )
                script_lines.extend(check.commands)
                script_lines.append("")

        script_lines.extend(
            [
                "echo 'VFIO remediation completed!'",
                "echo 'Please reboot if kernel parameters were modified.'",
            ]
        )

        return "\n".join(script_lines)


def run_vfio_diagnostic(
    device_bdf: Optional[str] = None, interactive: bool = True
) -> VFIODiagnosticResult:
    """Run VFIO diagnostic and optionally provide interactive remediation."""
    diagnostics = VFIODiagnostics(device_bdf)
    result = diagnostics.run_full_diagnostic()

    # Always print the report
    diagnostics.print_diagnostic_report(result)

    # Interactive remediation
    if interactive and not result.can_proceed:
        print("\n🔧 AUTOMATIC REMEDIATION AVAILABLE")
        print("-" * 40)

        response = (
            input("Would you like to generate a remediation script? (y/N): ")
            .strip()
            .lower()
        )
        if response in ["y", "yes"]:
            script = diagnostics.get_remediation_script(result)
            script_path = "vfio_remediation.sh"

            with open(script_path, "w") as f:
                f.write(script)

            os.chmod(script_path, 0o755)

            print(f"✅ Remediation script saved to: {script_path}")
            print("📋 To apply fixes, run:")
            print(f"   sudo ./{script_path}")
            print("\n⚠️  WARNING: This will modify system configuration!")
            print("   Review the script before running it.")

            response = (
                input("\nWould you like to run the remediation script now? (y/N): ")
                .strip()
                .lower()
            )
            if response in ["y", "yes"]:
                try:
                    subprocess.run(["sudo", f"./{script_path}"], check=True)
                    print("✅ Remediation script completed successfully!")
                    print("🔄 Re-running diagnostics...")

                    # Re-run diagnostics
                    new_result = diagnostics.run_full_diagnostic()
                    diagnostics.print_diagnostic_report(new_result)
                    return new_result
                except subprocess.CalledProcessError as e:
                    print(f"❌ Remediation script failed: {e}")
                except KeyboardInterrupt:
                    print("\n⚠️  Remediation cancelled by user")

    return result


if __name__ == "__main__":
    import sys

    device_bdf = sys.argv[1] if len(sys.argv) > 1 else None
    result = run_vfio_diagnostic(device_bdf)

    # Exit with appropriate code
    sys.exit(0 if result.can_proceed else 1)
