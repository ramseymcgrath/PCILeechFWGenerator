#!/usr/bin/env python3
"""
Lightweight IOMMU viewer for debugging bundled with the repo.

This script is a portable Python alternative to the separate "IOMMU-viewer" shell
script. It enumerates /sys/kernel/iommu_groups and /sys/bus/pci/devices to
show which PCI devices belong to which IOMMU groups and their current driver.

It intentionally has zero external dependencies and should be runnable on Linux
systems with a mounted /sys filesystem. Run as root for access to driver info
and device binding state.

Usage:
  scripts/iommu_viewer.py           # list all groups and devices
  scripts/iommu_viewer.py -g 25     # show only group 25
  scripts/iommu_viewer.py --json    # output JSON

"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


def read_sysfs_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return None


def get_driver_for_device(device_path: Path) -> Optional[str]:
    driver_link = device_path / "driver"
    try:
        if driver_link.exists() and driver_link.is_symlink():
            return os.path.basename(os.readlink(driver_link))
    except Exception:
        pass
    return None


def pci_lspci_info(bdf: str) -> Optional[str]:
    # Try to call lspci for human-friendly output if available
    try:
        out = subprocess.check_output(
            ["lspci", "-s", bdf, "-nnk"], stderr=subprocess.DEVNULL
        )
        return out.decode("utf-8", errors="replace").strip()
    except Exception:
        return None


def format_device_line(
    bdf: str, vendor: Optional[str], device: Optional[str], driver: Optional[str]
) -> str:
    parts = [f"{bdf}"]
    if vendor and device:
        parts.append(f"[{vendor}:{device}]")
    if driver:
        parts.append(f"Driver: {driver}")
    return " ".join(parts)


def gather_iommu_groups() -> Dict[str, List[Dict[str, Optional[str]]]]:
    groups_dir = Path("/sys/kernel/iommu_groups")
    result: Dict[str, List[Dict[str, Optional[str]]]] = {}

    if not groups_dir.exists():
        raise RuntimeError(
            "/sys/kernel/iommu_groups not found. Are you on Linux with sysfs mounted?"
        )

    for group_entry in sorted(
        groups_dir.iterdir(), key=lambda p: int(p.name) if p.name.isdigit() else p.name
    ):
        if not group_entry.is_dir():
            continue
        group_id = group_entry.name
        devices_dir = group_entry / "devices"
        devices: List[Dict[str, Optional[str]]] = []
        if devices_dir.exists():
            for dev in sorted(devices_dir.iterdir()):
                bdf = dev.name
                device_path = Path(f"/sys/bus/pci/devices/{bdf}")
                vendor = read_sysfs_text(device_path / "vendor")
                device = read_sysfs_text(device_path / "device")
                vendor_hex = (
                    vendor[2:] if vendor and vendor.startswith("0x") else vendor
                )
                device_hex = (
                    device[2:] if device and device.startswith("0x") else device
                )
                driver = get_driver_for_device(device_path)
                devices.append(
                    {
                        "bdf": bdf,
                        "vendor": vendor_hex,
                        "device": device_hex,
                        "driver": driver,
                    }
                )
        result[group_id] = devices
    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="iommu_viewer.py")
    parser.add_argument("-g", "--group", help="Show only specified IOMMU group id")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--lspci",
        action="store_true",
        help="Attempt to call lspci for verbose device info",
    )

    args = parser.parse_args(argv)

    try:
        groups = gather_iommu_groups()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if args.group:
        groups = {k: v for k, v in groups.items() if k == args.group}

    if args.json:
        print(json.dumps(groups, indent=2))
        return 0

    for gid, devices in sorted(
        groups.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else kv[0]
    ):
        if not devices:
            print(f"Group: {gid}  (no devices)")
            continue
        for idx, dev in enumerate(devices):
            # Try to present a concise single-line summary. If lspci requested and available,
            # prefer the lspci line.
            bdf = dev.get("bdf") or "unknown"
            vendor = dev.get("vendor")
            device = dev.get("device")
            driver = dev.get("driver")

            human = pci_lspci_info(bdf) if args.lspci else None
            if human:
                # print first line of lspci output for brevity
                first_line = human.splitlines()[0]
                print(f"Group: {gid}  {first_line}")
            else:
                print(
                    f"Group: {gid}  {format_device_line(bdf, vendor, device, driver)}"
                )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
