#!/usr/bin/env python3
"""cli – one front‑door for the whole tool‑chain.

Usage examples
~~~~~~~~~~~~~~
    # guided build flow (device & board pickers)
    ./cli build

    # scripted build for CI (non‑interactive)
    ./cli build --bdf 0000:01:00.0 --board pcileech_75t484_x1 \
                --device-type network --advanced-sv

    # flash an already‑generated bitstream
    ./cli flash output/firmware.bin --board pcileech_75t484_x1
"""
from __future__ import annotations

import argparse
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional

import sys
from pathlib import Path

# Add project root to path for utils imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logging import get_logger, setup_logging
from utils.shell import Shell

from .container import BuildConfig, run_build  # new unified runner

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers – PCIe enumeration & interactive pickers
# ──────────────────────────────────────────────────────────────────────────────
PCI_RE = re.compile(
    r"(?P<bdf>[0-9a-fA-F:.]+) .*?\["
    r"(?P<class>[0-9a-fA-F]{4})\]: .*?\["
    r"(?P<ven>[0-9a-fA-F]{4}):(?P<dev>[0-9a-fA-F]{4})\]"
)


def list_pci_devices() -> List[Dict[str, str]]:
    out = Shell().run("lspci -Dnn")
    devs: list[dict[str, str]] = []
    for line in out.splitlines():
        m = PCI_RE.match(line)
        if m:
            d = m.groupdict()
            d["pretty"] = line

            # Check if device has IOMMU group (VFIO compatible)
            bdf = d["bdf"]
            try:
                from .vfio_handler import _get_iommu_group_safe

                group_id = _get_iommu_group_safe(bdf)
                if group_id:
                    d["vfio_compatible"] = True
                    d["iommu_group"] = group_id
                    d["pretty"] += f" [IOMMU Group: {group_id}]"
                else:
                    d["vfio_compatible"] = False
                    d["pretty"] += " [No IOMMU Group - Not VFIO Compatible]"
            except Exception:
                d["vfio_compatible"] = False
                d["pretty"] += " [VFIO Status Unknown]"

            devs.append(d)
    return devs


def pick(lst: list[str], prompt: str) -> str:
    for i, item in enumerate(lst):
        print(f" [{i}] {item}")
    while True:
        sel = input(prompt).strip()
        if not sel and lst:
            return lst[0]
        try:
            return lst[int(sel)]
        except Exception:
            print("  Invalid selection – try again.")


def choose_device() -> Dict[str, str]:
    devs = list_pci_devices()
    if not devs:
        raise RuntimeError("No PCIe devices found – are you root?")

    # Separate VFIO-compatible and incompatible devices
    vfio_devs = [dev for dev in devs if dev.get("vfio_compatible", False)]
    non_vfio_devs = [dev for dev in devs if not dev.get("vfio_compatible", False)]

    print("\n=== VFIO-Compatible Devices (Recommended) ===")
    if vfio_devs:
        for i, dev in enumerate(vfio_devs):
            print(f" [{i}] {dev['pretty']}")
    else:
        print(" No VFIO-compatible devices found!")
        print(" This usually means IOMMU is not enabled in your system.")

    if non_vfio_devs:
        print(f"\n=== Non-VFIO Devices (Will Cause Errors) ===")
        start_idx = len(vfio_devs)
        for i, dev in enumerate(non_vfio_devs):
            print(f" [{start_idx + i}] {dev['pretty']}")
        print("\nWARNING: Selecting a non-VFIO device will cause build failures!")

    # Combine lists for selection
    all_devs = vfio_devs + non_vfio_devs

    while True:
        try:
            selection = int(input("\nSelect donor device #: "))
            if 0 <= selection < len(all_devs):
                selected_dev = all_devs[selection]

                # Warn if selecting non-VFIO device
                if not selected_dev.get("vfio_compatible", False):
                    print(
                        f"\nWARNING: Device {selected_dev['bdf']} is not VFIO-compatible!"
                    )
                    print(
                        "This will likely cause the build to fail with IOMMU group errors."
                    )
                    confirm = input("Continue anyway? (y/N): ").strip().lower()
                    if confirm not in ["y", "yes"]:
                        continue

                return selected_dev
            else:
                print(f"Invalid selection. Please choose 0-{len(all_devs)-1}")
        except (ValueError, KeyboardInterrupt):
            print("Invalid input. Please enter a number.")


SUPPORTED_BOARDS = [
    "pcileech_75t484_x1",
    "pcileech_35t484_x1",
    "pcileech_35t325_x4",
    "pcileech_35t325_x1",
    "pcileech_100t484_x1",
    "pcileech_enigma_x1",
    "pcileech_squirrel",
    "pcileech_pciescreamer_xc7a35",
]


# ──────────────────────────────────────────────────────────────────────────────
# CLI setup
# ──────────────────────────────────────────────────────────────────────────────


def build_sub(parser: argparse._SubParsersAction):
    p = parser.add_parser("build", help="Build firmware (guided or scripted)")
    p.add_argument("--bdf", help="PCI BDF (skip for interactive picker)")
    p.add_argument("--board", choices=SUPPORTED_BOARDS, help="FPGA board")
    p.add_argument(
        "--device-type",
        default="generic",
        choices=["generic", "network", "storage", "graphics", "audio"],
        help="Type of device being cloned",
    )
    p.add_argument(
        "--advanced-sv", action="store_true", help="Enable advanced SV features"
    )
    p.add_argument("--enable-variance", action="store_true", help="Enable variance")
    p.add_argument(
        "--auto-fix", action="store_true", help="Let VFIOBinder auto-remediate issues"
    )

    # Add fallback control group
    fallback_group = p.add_argument_group("Fallback Control")
    fallback_group.add_argument(
        "--fallback-mode",
        choices=["none", "prompt", "auto"],
        default="none",
        help="Control fallback behavior (none=fail-fast, prompt=ask, auto=allow)",
    )
    fallback_group.add_argument(
        "--allow-fallbacks", type=str, help="Comma-separated list of allowed fallbacks"
    )
    fallback_group.add_argument(
        "--deny-fallbacks", type=str, help="Comma-separated list of denied fallbacks"
    )
    fallback_group.add_argument(
        "--legacy-compatibility",
        action="store_true",
        help="Enable legacy compatibility mode (temporarily restores old fallback behavior)",
    )


def flash_sub(parser: argparse._SubParsersAction):
    p = parser.add_parser("flash", help="Flash a firmware binary via usbloader")
    p.add_argument("firmware", help="Path to .bin")
    p.add_argument(
        "--board", required=True, choices=SUPPORTED_BOARDS, help="FPGA board"
    )


def get_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser("cli", description=__doc__)
    sub = ap.add_subparsers(
        dest="cmd",
        required=True,
        help="Command to run (build/flash)",
    )
    build_sub(sub)
    flash_sub(sub)
    return ap


def flash_bin(path: Path):
    from .flash import flash_firmware

    flash_firmware(path)

    logger.info("Firmware flashed successfully ✓")


# ──────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ──────────────────────────────────────────────────────────────────────────────


def main(argv: Optional[List[str]] = None):
    # Setup proper logging with color support
    setup_logging(level=logging.INFO)

    args = get_parser().parse_args(argv)

    if args.cmd == "build":
        bdf = args.bdf or choose_device()["bdf"]
        board = args.board or pick(SUPPORTED_BOARDS, "Board #: ")
        # Process fallback lists
        allowed_fallbacks = []
        if hasattr(args, "allow_fallbacks") and args.allow_fallbacks:
            allowed_fallbacks = [f.strip() for f in args.allow_fallbacks.split(",")]

        denied_fallbacks = []
        if hasattr(args, "deny_fallbacks") and args.deny_fallbacks:
            denied_fallbacks = [f.strip() for f in args.deny_fallbacks.split(",")]

        # Determine fallback mode based on legacy compatibility flag
        fallback_mode = getattr(args, "fallback_mode", "none")
        if (
            hasattr(args, "legacy_compatibility")
            and args.legacy_compatibility
            and fallback_mode == "none"
        ):
            logger.warning(
                "Legacy compatibility mode enabled - using 'auto' fallback mode"
            )
            fallback_mode = "auto"
            if not allowed_fallbacks:
                allowed_fallbacks = [
                    "config-space",
                    "msix",
                    "behavior-profiling",
                    "build-integration",
                ]

        cfg = BuildConfig(
            bdf=bdf,
            board=board,
            device_type=args.device_type,
            advanced_sv=args.advanced_sv,
            enable_variance=args.enable_variance,
            auto_fix=args.auto_fix,
            fallback_mode=fallback_mode,
            allowed_fallbacks=allowed_fallbacks,
            denied_fallbacks=denied_fallbacks,
        )
        run_build(cfg)

    elif args.cmd == "flash":
        flash_bin(Path(args.firmware))


if __name__ == "__main__":
    main()
