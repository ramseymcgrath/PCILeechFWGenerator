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
from typing import Dict, List, Optional

from log_config import get_logger, setup_logging
from shell import Shell

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
    for i, dev in enumerate(devs):
        print(f" [{i}] {dev['pretty']}")
    return devs[int(input("Select donor device #: "))]


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
