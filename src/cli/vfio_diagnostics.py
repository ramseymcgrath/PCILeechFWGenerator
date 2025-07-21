#!/usr/bin/env python3
"""
VFIO‑Assist - smarter VFIO diagnostics & auto‑fixer

Usage (examples)
----------------
```bash
# Full diagnostic with coloured TTY output
sudo ./vfio_assist.py diagnose --device 0000:01:00.0

# Attempt automatic remediation non‑interactively
sudo ./vfio_assist.py fix --device 0000:01:00.0 --yes

# Generate a remediation script only
./vfio_assist.py script > vfio_fix.sh && chmod +x vfio_fix.sh

# Machine‑readable JSON for a GitHub Action step
./vfio_assist.py json --device 0000:01:00.0
```
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

# Add project root to path for utils imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from log_config import get_logger, setup_logging
from src.string_utils import (
    log_debug_safe,
    log_error_safe,
    log_info_safe,
    log_warning_safe,
)

# ──────────────────────────────────────────────────────────────────────────────
# Pretty terminal helpers
# ──────────────────────────────────────────────────────────────────────────────
try:
    from colorama import Fore, Style
    from colorama import init as colorama_init  # type: ignore

    colorama_init()

    def colour(txt: str, col: str) -> str:  # noqa: D401 - short lambda‑style fn
        return f"{col}{txt}{Style.RESET_ALL}"

except ImportError:  # colour optional - silently degrade

    class Fore:  # type: ignore
        RED = ""
        GREEN = ""
        YELLOW = ""
        CYAN = ""
        MAGENTA = ""
        RESET = ""

    class Style:  # type: ignore - dummy placeholder
        RESET_ALL = ""

    def colour(txt: str, col: str) -> str:  # noqa: D401
        return txt


# ──────────────────────────────────────────────────────────────────────────────
# Logging setup - verbose by default, override with --quiet
# ──────────────────────────────────────────────────────────────────────────────
# Initialize with INFO level by default, will be adjusted based on CLI args
# Only setup logging if no handlers exist (avoid overriding CLI setup)
if not logging.getLogger().handlers:
    setup_logging(level=logging.INFO, log_file="vfio_diagnostics.log")
log = get_logger("vfio-assist")


# ──────────────────────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────────────────────
class Status(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    MISSING = "missing"


@dataclass
class Check:
    name: str
    status: Status
    message: str
    remediation: Optional[str] = None
    commands: Optional[List[str]] = None


@dataclass
class Report:
    overall: Status
    checks: List[Check]
    device_bdf: Optional[str] = None
    can_proceed: bool = False

    # Serialize for JSON output / CI integration
    def as_dict(self) -> dict:
        return {
            "overall": self.overall.value,
            "device_bdf": self.device_bdf,
            "can_proceed": self.can_proceed,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "remediation": c.remediation,
                    "commands": c.commands,
                }
                for c in self.checks
            ],
        }


# ──────────────────────────────────────────────────────────────────────────────
# Core diagnostic engine
# ──────────────────────────────────────────────────────────────────────────────
class Diagnostics:
    def __init__(self, device_bdf: Optional[str] = None):
        self.device_bdf = device_bdf
        self.checks: List[Check] = []

    # Public API --------------------------------------------------------------
    def run(self) -> Report:
        log_info_safe(
            log,
            "Starting VFIO diagnostics for device: {device}",
            prefix="VFIO",
            device=self.device_bdf or "system-wide",
        )
        self.checks.clear()

        try:
            # System-wide checks
            log_debug_safe(log, "Running system-wide VFIO checks", prefix="VFIO")
            self._check_linux()
            self._check_iommu_hw()
            self._check_kernel_params()
            self._check_modules()
            self._check_vfio_driver_path()

            # Device-specific checks
            if self.device_bdf:
                log_debug_safe(
                    log,
                    "Running device-specific checks for {device}",
                    prefix="VFIO",
                    device=self.device_bdf,
                )
                self._device_exists()
                self._device_iommu_group()
                self._device_driver_binding()
                self._device_node()
            else:
                log_debug_safe(
                    log,
                    "No device specified, skipping device-specific checks",
                    prefix="VFIO",
                )

            overall = self._overall()
            can_proceed = overall in (Status.OK, Status.WARNING)

            log_info_safe(
                log,
                "Diagnostics completed. Overall status: {status}, Can proceed: {can_proceed}",
                prefix="VFIO",
                status=overall.value,
                can_proceed=can_proceed,
            )
            return Report(overall, self.checks, self.device_bdf, can_proceed)

        except Exception as e:
            log_error_safe(
                log,
                "Unexpected error during diagnostics: {error}",
                prefix="VFIO",
                error=str(e),
            )
            log.error("Full exception details:", exc_info=True)
            # Add an error check to indicate the diagnostic failure
            self._append(
                name="Diagnostic Engine",
                status=Status.ERROR,
                message=f"Diagnostic engine failed: {e}",
                remediation="Check system logs and retry",
            )
            return Report(Status.ERROR, self.checks, self.device_bdf, False)

    # Private helpers ---------------------------------------------------------
    @staticmethod
    def _path_exists(path: str | Path) -> bool:
        return Path(path).exists()

    def _append(self, **kw):  # tiny helper
        self.checks.append(Check(**kw))

    # Individual checks -------------------------------------------------------
    def _check_linux(self):
        """Check if running on Linux platform."""
        platform_name = platform.system().lower()
        log_debug_safe(
            log, "Detected platform: {platform}", prefix="VFIO", platform=platform_name
        )

        if platform_name == "linux":
            log_debug_safe(log, "Linux platform confirmed", prefix="VFIO")
            self._append(name="Platform", status=Status.OK, message="Linux detected")
        else:
            log_warning_safe(
                log,
                "Unsupported platform detected: {platform}",
                prefix="VFIO",
                platform=platform_name,
            )
            self._append(
                name="Platform",
                status=Status.ERROR,
                message=f"Unsupported OS: {platform.system()}",
                remediation="Run on a Linux system with VFIO support",
            )

    def _check_iommu_hw(self):
        """Check for IOMMU hardware support in CPU."""
        log_debug_safe(log, "Checking IOMMU hardware support")

        try:
            cpuinfo_path = Path("/proc/cpuinfo")
            if not cpuinfo_path.exists():
                log_warning_safe(log, "/proc/cpuinfo not found")
                self._append(
                    name="IOMMU HW",
                    status=Status.WARNING,
                    message="/proc/cpuinfo not found - cannot verify IOMMU support",
                )
                return

            cpuinfo = cpuinfo_path.read_text()
            intel = "vmx" in cpuinfo and "ept" in cpuinfo
            amd = "svm" in cpuinfo and "npt" in cpuinfo

            log_debug_safe(
                log,
                "CPU flags check - Intel VT-d: {intel}, AMD-Vi: {amd}",
                intel=intel,
                amd=amd,
            )

            if intel or amd:
                cpu_type = "Intel VT-d" if intel else "AMD-Vi"
                log_debug_safe(
                    log,
                    "IOMMU hardware support confirmed: {cpu_type}",
                    cpu_type=cpu_type,
                )
                self._append(
                    name="IOMMU HW",
                    status=Status.OK,
                    message="VT‑d / AMD‑Vi supported by CPU",
                )
            else:
                log_warning_safe(log, "IOMMU hardware flags not found in CPU info")
                self._append(
                    name="IOMMU HW",
                    status=Status.WARNING,
                    message="CPU flags missing VT‑d/AMD‑Vi - maybe disabled in BIOS",
                    remediation="Enable IOMMU in firmware setup (VT‑d, AMD‑Vi) or echo 1 > /sys/module/vfio/parameters/enable_unsafe_noiommu_mode if you can't in BIOS (unsafe)",
                )
        except Exception as e:
            log_error_safe(
                log, "Failed to check IOMMU hardware support: {error}", error=str(e)
            )
            log.error("Full exception details:", exc_info=True)
            self._append(
                name="IOMMU HW",
                status=Status.WARNING,
                message=f"Could not parse /proc/cpuinfo: {e}",
            )

    def _check_kernel_params(self):
        """Check kernel command line for IOMMU parameters."""
        log_debug_safe(log, "Checking kernel command line parameters")

        try:
            cmdline_path = Path("/proc/cmdline")
            if not cmdline_path.exists():
                log_error_safe(log, "/proc/cmdline not found")
                self._append(
                    name="Kernel cmdline",
                    status=Status.ERROR,
                    message="/proc/cmdline not found",
                )
                return

            cmdline = cmdline_path.read_text().strip()
            log_debug_safe(log, "Kernel cmdline: {cmdline}", cmdline=cmdline)

            iommu_params = ["intel_iommu=on", "amd_iommu=on", "iommu=pt", "iommu=on"]
            found_params = [param for param in iommu_params if param in cmdline]

            log_debug_safe(log, "Found IOMMU parameters: {params}", params=found_params)

            if found_params:
                log_debug_safe(log, "IOMMU enabled in kernel cmdline")
                self._append(
                    name="Kernel cmdline",
                    status=Status.OK,
                    message=f"IOMMU enabled in cmdline: {', '.join(found_params)}",
                )
            else:
                log_warning_safe(log, "No IOMMU parameters found in kernel cmdline")
                fix = "Enable intel_iommu=on and/or amd_iommu=on iommu=pt in grub"
                self._append(
                    name="Kernel cmdline",
                    status=Status.ERROR,
                    message="IOMMU not present in kernel parameters",
                    remediation=fix,
                    commands=self._kernel_param_commands(),
                )
        except Exception as e:
            log_error_safe(
                log, "Failed to check kernel parameters: {error}", error=str(e)
            )
            log.error("Full exception details:", exc_info=True)
            self._append(
                name="Kernel cmdline",
                status=Status.ERROR,
                message=f"Failed to read /proc/cmdline: {e}",
            )

    @staticmethod
    def _kernel_param_commands() -> List[str]:
        cmd: list[str] = []
        if shutil.which("grubby"):
            cmd.append(
                'sudo grubby --update-kernel=ALL --args "intel_iommu=on amd_iommu=on iommu=pt"'
            )
        elif Path("/etc/default/grub").exists():
            # Minimal fallback; user should still review
            cmd.extend(
                [
                    'sudo sed -Ei \'s/GRUB_CMDLINE_LINUX=("[^"]*)/GRUB_CMDLINE_LINUX="\\1 intel_iommu=on amd_iommu=on iommu=pt"/\' /etc/default/grub',
                    "sudo update-grub",
                ]
            )
        elif Path(
            "/etc/kernel/cmdline"
        ).exists():  # systemd‑boot (Fedora Silverblue, etc.)
            cmd.extend(
                [
                    "echo 'intel_iommu=on amd_iommu=on iommu=pt' | sudo tee -a /etc/kernel/cmdline",
                    "sudo rpm-ostree initramfs --enable",
                ]
            )
        cmd.append("sudo reboot # required for kernel param changes")
        return cmd

    def _check_modules(self):
        """Check if required VFIO kernel modules are loaded."""
        log_debug_safe(log, "Checking VFIO kernel modules")

        required = ["vfio", "vfio_pci", "vfio_iommu_type1"]
        missing = []
        loaded = []

        for module in required:
            module_path = f"/sys/module/{module}"
            if self._path_exists(module_path):
                loaded.append(module)
                log_debug_safe(log, "Module {module} is loaded", module=module)
            else:
                missing.append(module)
                log_debug_safe(log, "Module {module} is missing", module=module)

        log_debug_safe(
            log,
            "Loaded modules: {loaded}, Missing modules: {missing}",
            loaded=loaded,
            missing=missing,
        )

        if not missing:
            log_debug_safe(log, "All required VFIO modules are loaded")
            self._append(
                name="Kernel modules",
                status=Status.OK,
                message=f"All VFIO modules loaded: {', '.join(loaded)}",
            )
        else:
            severity = Status.ERROR if len(missing) == len(required) else Status.WARNING
            log_warning_safe(
                log,
                "Missing VFIO modules: {missing} (severity: {severity})",
                missing=missing,
                severity=severity.value,
            )
            self._append(
                name="Kernel modules",
                status=severity,
                message="Missing modules: " + ", ".join(missing),
                remediation="Load required modules with modprobe",
                commands=[f"sudo modprobe {m.replace('_', '-')}" for m in missing],
            )

    def _check_vfio_driver_path(self):
        path = Path("/sys/bus/pci/drivers/vfio-pci")
        if path.exists():
            self._append(
                name="vfio-pci driver", status=Status.OK, message="vfio-pci registered"
            )
        else:
            self._append(
                name="vfio-pci driver",
                status=Status.ERROR,
                message="vfio-pci driver not present in sysfs",
                remediation="Ensure kernel has VFIO support compiled or module present",
                commands=["sudo modprobe vfio-pci"],
            )

    # Device‑specific ---------------------------------------------------------
    def _device_exists(self):
        device_path = Path(f"/sys/bus/pci/devices/{self.device_bdf}")
        if device_path.exists():
            vendor = (device_path / "vendor").read_text().strip()
            device = (device_path / "device").read_text().strip()
            self._append(
                name="Device",
                status=Status.OK,
                message=f"{self.device_bdf} ({vendor}:{device}) present",
            )
        else:
            self._append(
                name="Device",
                status=Status.ERROR,
                message=f"PCI device {self.device_bdf} not found",
                remediation="Check BDF with lspci ‑D",
            )

    def _device_iommu_group(self):
        group_link = Path(f"/sys/bus/pci/devices/{self.device_bdf}/iommu_group")
        log_debug_safe(
            log,
            "Checking IOMMU group link: {group_link}",
            group_link=group_link,
            prefix="VFIO",
        )

        if group_link.exists():
            try:
                group_target = os.readlink(group_link)
                group = os.path.basename(group_target)
                log_debug_safe(
                    log,
                    "IOMMU group link target: {group_target}, group: {group}",
                    group_target=group_target,
                    group=group,
                    prefix="VFIO",
                )

                # Check if the group directory exists
                group_dir = Path(f"/sys/kernel/iommu_groups/{group}")
                if group_dir.exists():
                    # List devices in the group for debugging
                    devices_dir = group_dir / "devices"
                    if devices_dir.exists():
                        try:
                            devices = list(devices_dir.iterdir())
                            device_names = [d.name for d in devices]
                            log_debug_safe(
                                log,
                                "Devices in IOMMU group {group}: {device_names}",
                                group=group,
                                device_names=device_names,
                                prefix="VFIO",
                            )
                        except Exception as e:
                            log_debug_safe(
                                log,
                                "Could not list devices in IOMMU group {group}: {error}",
                                group=group,
                                error=str(e),
                                prefix="VFIO",
                            )

                self._append(
                    name="IOMMU group", status=Status.OK, message=f"Group {group}"
                )
            except OSError as e:
                log_debug_safe(
                    log,
                    "Failed to read IOMMU group symlink: {error}",
                    error=str(e),
                    prefix="VFIO",
                )
                self._append(
                    name="IOMMU group",
                    status=Status.ERROR,
                    message=f"Failed to read IOMMU group symlink: {e}",
                )
        else:
            # Check if device exists at all
            device_path = Path(f"/sys/bus/pci/devices/{self.device_bdf}")
            if device_path.exists():
                log_debug_safe(
                    log,
                    "Device {device} exists but has no IOMMU group",
                    device=self.device_bdf,
                    prefix="VFIO",
                )
                self._append(
                    name="IOMMU group",
                    status=Status.ERROR,
                    message="Device exists but not in an IOMMU group - IOMMU disabled?",
                    prefix="VFIO",
                )
            else:
                log_debug_safe(
                    log,
                    "Device {device} does not exist in sysfs",
                    device=self.device_bdf,
                    prefix="VFIO",
                )
                self._append(
                    name="IOMMU group",
                    status=Status.ERROR,
                    message=f"Device {self.device_bdf} not found in sysfs",
                    prefix="VFIO",
                )

    def _device_driver_binding(self):
        if self.device_bdf is None:
            self._append(
                name="Driver",
                status=Status.ERROR,
                message="Cannot check driver binding without device BDF",
            )
            return

        link = Path(f"/sys/bus/pci/devices/{self.device_bdf}/driver")
        log_debug_safe(
            log,
            "Checking driver binding for {device} at {link}",
            device=self.device_bdf,
            link=link,
            prefix="VFIO",
        )

        if link.exists():
            try:
                driver_target = os.readlink(link)
                driver = os.path.basename(driver_target)
                log_debug_safe(
                    log,
                    "Driver link target: {driver_target}, driver: {driver}",
                    driver_target=driver_target,
                    driver=driver,
                    prefix="VFIO",
                )

                if driver == "vfio-pci":
                    self._append(
                        name="Driver",
                        status=Status.OK,
                        message="Already bound to vfio-pci",
                    )
                else:
                    log_debug_safe(
                        log,
                        "Device {device} bound to {driver}, needs rebinding to vfio-pci",
                        device=self.device_bdf,
                        driver=driver,
                    )
                    self._append(
                        name="Driver",
                        status=Status.WARNING,
                        message=f"Bound to {driver}",
                        remediation="Will need to rebind to vfio-pci",
                        commands=self._bind_commands(self.device_bdf, driver),
                    )
            except OSError as e:
                log_debug_safe(
                    log,
                    "Failed to read driver symlink for {device}: {error}",
                    device=self.device_bdf,
                    error=str(e),
                    prefix="VFIO",
                )
                self._append(
                    name="Driver",
                    status=Status.ERROR,
                    message=f"Failed to read driver symlink: {e}",
                )
        else:
            log_debug_safe(
                log,
                "No driver bound to device {device}",
                device=self.device_bdf,
                prefix="VFIO",
            )
            self._append(
                name="Driver",
                status=Status.WARNING,
                message="No driver bound",
                commands=self._bind_commands(self.device_bdf, None),
            )

    @staticmethod
    def _bind_commands(bdf: str, current: Optional[str]) -> List[str]:
        cmds: list[str] = [
            (
                f"echo '{bdf}' | sudo tee /sys/bus/pci/devices/{bdf}/driver/unbind"
                if current
                else ""
            ),
            f"echo '{bdf}' | sudo tee /sys/bus/pci/drivers/vfio-pci/bind",
        ]
        return [c for c in cmds if c]

    def _device_node(self):
        link = Path(f"/sys/bus/pci/devices/{self.device_bdf}/iommu_group")
        log_debug_safe(
            log,
            "Checking VFIO device node for {device}",
            device=self.device_bdf,
            prefix="VFIO",
        )

        if not link.exists():
            log_debug_safe(
                log,
                "IOMMU group link does not exist for {device}",
                device=self.device_bdf,
                prefix="VFIO",
            )
            return

        try:
            group_target = os.readlink(link)
            group = os.path.basename(group_target)
            log_debug_safe(
                log,
                "IOMMU group for {device}: {group}",
                device=self.device_bdf,
                group=group,
                prefix="VFIO",
            )

            node = Path(f"/dev/vfio/{group}")
            log_debug_safe(log, "Checking VFIO node: {node}", node=node, prefix="VFIO")

            if node.exists():
                # Check node permissions and properties
                try:
                    stat_info = node.stat()
                    log_debug_safe(
                        log,
                        "VFIO node {node} permissions: {permissions}",
                        node=node,
                        permissions=oct(stat_info.st_mode),
                    )
                except Exception as e:
                    log_debug_safe(
                        log,
                        "Could not stat VFIO node {node}: {error}",
                        node=node,
                        error=str(e),
                    )

                self._append(
                    name="/dev/vfio node", status=Status.OK, message=node.as_posix()
                )
            else:
                log_debug_safe(
                    log, "VFIO node {node} does not exist", node=node, prefix="VFIO"
                )

                # Check if /dev/vfio directory exists
                vfio_dir = Path("/dev/vfio")
                if vfio_dir.exists():
                    try:
                        vfio_entries = list(vfio_dir.iterdir())
                        log_debug_safe(
                            log,
                            "Available VFIO entries: {entries}",
                            entries=[e.name for e in vfio_entries],
                            prefix="VFIO",
                        )
                    except Exception as e:
                        log_debug_safe(
                            log,
                            "Could not list /dev/vfio entries: {error}",
                            prefix="VFIO",
                            error=str(e),
                        )
                else:
                    log_debug_safe(
                        log, "/dev/vfio directory does not exist", prefix="VFIO"
                    )

                self._append(
                    name="/dev/vfio node",
                    status=Status.WARNING,
                    message=f"{node} missing (will appear after binding)",
                )
        except OSError as e:
            log_debug_safe(
                log,
                "Failed to read IOMMU group symlink for device node check: {error}",
                prefix="VFIO",
                error=str(e),
            )
            self._append(
                name="/dev/vfio node",
                status=Status.ERROR,
                message=f"Failed to determine VFIO node: {e}",
            )

    # Overall --------------------------------------------------------------
    def _overall(self) -> Status:
        if any(c.status == Status.ERROR for c in self.checks):
            return Status.ERROR
        if any(c.status == Status.WARNING for c in self.checks):
            return Status.WARNING
        return Status.OK


# ──────────────────────────────────────────────────────────────────────────────
# Remediation script generator
# ──────────────────────────────────────────────────────────────────────────────
def remediation_script(report: Report) -> str:
    lines = [
        "#!/bin/bash",
        "# Auto‑generated VFIO remediation script - review before running!",
        "set -euo pipefail",
        "echo '>> VFIO remediation started'",
    ]
    for c in report.checks:
        if c.commands and c.status in (Status.ERROR, Status.WARNING):
            lines.append(f"# — {c.name}")
            lines += c.commands
            lines.append("")
    lines += [
        "echo '>> Remediation completed. Reboot if kernel params changed.'",
    ]
    return "\n".join(lines) + "\n"


# ──────────────────────────────────────────────────────────────────────────────
# Human‑readable renderer
# ──────────────────────────────────────────────────────────────────────────────
SYMBOLS = {
    Status.OK: colour("✔", Fore.GREEN),
    Status.WARNING: colour("⚠", Fore.YELLOW),
    Status.ERROR: colour("✖", Fore.RED),
    Status.MISSING: colour("?", Fore.MAGENTA),
}


def render(report: Report):
    print(colour("\n=== VFIO DIAGNOSTIC REPORT ===", Fore.CYAN))
    print(f"Overall: {SYMBOLS[report.overall]} {report.overall.value.upper()}")
    if report.device_bdf:
        print(f"Device : {report.device_bdf}")
    print(f"Proceed: {'yes' if report.can_proceed else 'no'}\n")
    for ck in report.checks:
        sym = SYMBOLS.get(ck.status, "?")
        print(f"{sym} {ck.name}: {ck.message}")
        if ck.remediation:
            print("   · " + ck.remediation)
    print()


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry‑point
# ──────────────────────────────────────────────────────────────────────────────


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="vfio-assist",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            Smart VFIO diagnostics & remediation tool.
            --------------------------------------------------------------------
            Most commands require *root* - either run with sudo or prefix
            privileged sub‑steps with sudo when prompted.
            """,
        ),
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "-d", "--device", dest="device_bdf", help="Target PCIe BDF (0000:01:00.0)"
    )
    common.add_argument(
        "--quiet", action="store_true", help="Silence info logs (warnings still shown)"
    )

    sub.add_parser(
        "diagnose", parents=[common], help="Run diagnostics and print report"
    )
    fix_p = sub.add_parser(
        "fix", parents=[common], help="Attempt automatic remediation"
    )
    fix_p.add_argument(
        "-y", "--yes", action="store_true", help="Run fixes without confirmation"
    )

    sub.add_parser(
        "script", parents=[common], help="Output a shell script that would fix issues"
    )
    sub.add_parser(
        "json", parents=[common], help="Machine‑readable JSON report (stdout)"
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None):
    args = parse_args(argv or sys.argv[1:])
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    diag = Diagnostics(args.device_bdf)
    report = diag.run()

    if args.cmd == "diagnose":
        render(report)
        sys.exit(0 if report.can_proceed else 1)

    if args.cmd == "script":
        script = remediation_script(report)
        print(script, end="")
        return

    if args.cmd == "json":
        print(json.dumps(report.as_dict(), indent=2))
        return

    if args.cmd == "fix":
        if report.overall == Status.OK:
            render(report)
            print(colour("System already VFIO‑ready - nothing to do", Fore.GREEN))
            return

        script_text = remediation_script(report)
        temp = Path("/tmp/vfio_fix.sh")
        temp.write_text(script_text)
        temp.chmod(0o755)
        render(report)
        print(colour(f"Remediation script written to {temp}", Fore.CYAN))

        if not args.yes:
            confirm = input("Run remediation script now? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Aborted.")
                return
        log_info_safe(log, "Executing remediation script (requires root)…")
        try:
            subprocess.run(["sudo", str(temp)], check=True)
        except subprocess.CalledProcessError as e:
            log_error_safe(log, "Script failed: {error}", error=str(e))
            sys.exit(1)

        # Re‑run diagnostics after remediation
        print(colour("\nRe‑running diagnostics after remediation…", Fore.CYAN))
        new_report = Diagnostics(args.device_bdf).run()
        render(new_report)
        sys.exit(0 if new_report.can_proceed else 1)


if __name__ == "__main__":  # pragma: no cover
    main()
