#!/usr/bin/env python3
"""
VFIO‑Assist – smarter VFIO diagnostics & auto‑fixer

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

# ──────────────────────────────────────────────────────────────────────────────
# Pretty terminal helpers
# ──────────────────────────────────────────────────────────────────────────────
try:
    from colorama import Fore, Style, init as colorama_init  # type: ignore

    colorama_init()

    def colour(txt: str, col: str) -> str:  # noqa: D401 – short lambda‑style fn
        return f"{col}{txt}{Style.RESET_ALL}"

except ImportError:  # colour optional – silently degrade

    class Fore:  # type: ignore
        RED = ""
        GREEN = ""
        YELLOW = ""
        CYAN = ""
        MAGENTA = ""
        RESET = ""

    Style = Fore  # type: ignore – dummy placeholder

    def colour(txt: str, col: str) -> str:  # noqa: D401
        return txt


# ──────────────────────────────────────────────────────────────────────────────
# Logging setup – verbose by default, override with --quiet
# ──────────────────────────────────────────────────────────────────────────────
LOG_FORMAT = "%(levelname)s: %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
log = logging.getLogger("vfio-assist")


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
        log.debug("Starting diagnostics…")
        self.checks.clear()

        self._check_linux()
        self._check_iommu_hw()
        self._check_kernel_params()
        self._check_modules()
        self._check_vfio_driver_path()

        if self.device_bdf:
            self._device_exists()
            self._device_iommu_group()
            self._device_driver_binding()
            self._device_node()

        overall = self._overall()
        can_proceed = overall in (Status.OK, Status.WARNING)
        return Report(overall, self.checks, self.device_bdf, can_proceed)

    # Private helpers ---------------------------------------------------------
    @staticmethod
    def _path_exists(path: str | Path) -> bool:
        return Path(path).exists()

    def _append(self, **kw):  # tiny helper
        self.checks.append(Check(**kw))

    # Individual checks -------------------------------------------------------
    def _check_linux(self):
        if platform.system().lower() == "linux":
            self._append(name="Platform", status=Status.OK, message="Linux detected")
        else:
            self._append(
                name="Platform",
                status=Status.ERROR,
                message=f"Unsupported OS: {platform.system()}",
                remediation="Run on a Linux system with VFIO support",
            )

    def _check_iommu_hw(self):
        try:
            cpuinfo = Path("/proc/cpuinfo").read_text()
            intel = "vmx" in cpuinfo and "ept" in cpuinfo
            amd = "svm" in cpuinfo and "npt" in cpuinfo
            if intel or amd:
                self._append(
                    name="IOMMU HW",
                    status=Status.OK,
                    message="VT‑d / AMD‑Vi supported by CPU",
                )
            else:
                self._append(
                    name="IOMMU HW",
                    status=Status.WARNING,
                    message="CPU flags missing VT‑d/AMD‑Vi – maybe disabled in BIOS",
                    remediation="Enable IOMMU in firmware setup (VT‑d, AMD‑Vi)",
                )
        except Exception as e:  # pragma: no cover – unlikely
            self._append(
                name="IOMMU HW",
                status=Status.WARNING,
                message=f"Could not parse /proc/cpuinfo: {e}",
            )

    def _check_kernel_params(self):
        try:
            cmdline = Path("/proc/cmdline").read_text()
            enabled = any(
                k in cmdline
                for k in ("intel_iommu=on", "amd_iommu=on", "iommu=pt", "iommu=on")
            )
            if enabled:
                self._append(
                    name="Kernel cmdline",
                    status=Status.OK,
                    message="IOMMU enabled in cmdline",
                )
            else:
                fix = "Enable intel_iommu=on and/or amd_iommu=on iommu=pt in grub"
                self._append(
                    name="Kernel cmdline",
                    status=Status.ERROR,
                    message="IOMMU not present in kernel parameters",
                    remediation=fix,
                    commands=self._kernel_param_commands(),
                )
        except Exception as e:
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
        required = ["vfio", "vfio_pci", "vfio_iommu_type1"]
        missing = [m for m in required if not self._path_exists(f"/sys/module/{m}")]
        if not missing:
            self._append(
                name="Kernel modules",
                status=Status.OK,
                message="All VFIO modules loaded",
            )
        else:
            self._append(
                name="Kernel modules",
                status=(
                    Status.ERROR if len(missing) == len(required) else Status.WARNING
                ),
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
        if group_link.exists():
            group = os.path.basename(os.readlink(group_link))
            self._append(name="IOMMU group", status=Status.OK, message=f"Group {group}")
        else:
            self._append(
                name="IOMMU group",
                status=Status.ERROR,
                message="Device not in an IOMMU group – IOMMU disabled?",
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
        if link.exists():
            driver = os.path.basename(os.readlink(link))
            if driver == "vfio-pci":
                self._append(
                    name="Driver", status=Status.OK, message="Already bound to vfio-pci"
                )
            else:
                self._append(
                    name="Driver",
                    status=Status.WARNING,
                    message=f"Bound to {driver}",
                    remediation="Will need to rebind to vfio-pci",
                    commands=self._bind_commands(self.device_bdf, driver),
                )
        else:
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
        if not link.exists():
            return
        group = os.path.basename(os.readlink(link))
        node = Path(f"/dev/vfio/{group}")
        if node.exists():
            self._append(
                name="/dev/vfio node", status=Status.OK, message=node.as_posix()
            )
        else:
            self._append(
                name="/dev/vfio node",
                status=Status.WARNING,
                message=f"{node} missing (will appear after binding)",
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
        "# Auto‑generated VFIO remediation script – review before running!",
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
            Most commands require *root* – either run with sudo or prefix
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
            print(colour("System already VFIO‑ready – nothing to do", Fore.GREEN))
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
        log.info("Executing remediation script (requires root)…")
        try:
            subprocess.run(["sudo", str(temp)], check=True)
        except subprocess.CalledProcessError as e:
            log.error("Script failed: %s", e)
            sys.exit(1)

        # Re‑run diagnostics after remediation
        print(colour("\nRe‑running diagnostics after remediation…", Fore.CYAN))
        new_report = Diagnostics(args.device_bdf).run()
        render(new_report)
        sys.exit(0 if new_report.can_proceed else 1)


if __name__ == "__main__":  # pragma: no cover
    main()
