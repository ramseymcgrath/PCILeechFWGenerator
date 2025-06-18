#!/usr/bin/env python3
"""
PCILeech FPGA Firmware Builder – Unified Edition
================================================
This streamlined script **always** runs the modern unified PCILeech build flow:
    • PCI configuration‑space capture via VFIO
    • SystemVerilog + TCL generation through *device_clone.pcileech_generator*
    • Optional Vivado hand‑off

All legacy fall‑backs, mock implementations, and compatibility shims have been
*removed*.  If a required module is missing we **fail fast** with a clear error
message.

Usage
-----
python3 pcileech_firmware_builder.py \
        --bdf 0000:03:00.0 \
        --board pcileech_35t325_x4 \
        [--vivado]
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# ──────────────────────────────────────────────────────────────────────────────
# Mandatory project‑local imports – these *must* exist in production images
# ──────────────────────────────────────────────────────────────────────────────
REQUIRED_MODULES = [
    "device_clone.pcileech_generator",
    "device_clone.behavior_profiler",
    "templating.tcl_builder",
]
for module in REQUIRED_MODULES:
    try:
        __import__(module)
    except ImportError as err:  # pragma: no cover
        print(
            f"[FATAL] Required module `{module}` is missing. "
            "Ensure the production container/image is built correctly.",
            file=sys.stderr,
        )
        raise SystemExit(2) from err

from device_clone.pcileech_generator import (
    PCILeechGenerationConfig,
    PCILeechGenerator,
)
from templating.tcl_builder import TCLBuilder
from device_clone.behavior_profiler import BehaviorProfiler

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
log = logging.getLogger("pcileech_builder")


# ──────────────────────────────────────────────────────────────────────────────
# Helper classes
# ──────────────────────────────────────────────────────────────────────────────
class FirmwareBuilder:
    """Thin wrapper around *PCILeechGenerator* for unified builds."""

    def __init__(self, bdf: str, board: str, out_dir: Path):
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.gen = PCILeechGenerator(
            PCILeechGenerationConfig(
                device_bdf=bdf,
                device_profile="generic",
                template_dir=None,
                output_dir=self.out_dir,
            )
        )
        self.tcl = TCLBuilder(output_dir=self.out_dir)
        self.profiler = BehaviorProfiler(bdf=bdf)

    # ────────────────────────────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────────────────────────────
    def build(self, profile_secs: int = 0) -> List[str]:
        """Run the full firmware generation flow.  Returns list of artifacts."""
        log.info("➤ Generating PCILeech firmware …")
        res = self.gen.generate_pcileech_firmware()

        # Write SV modules
        sv_dir = self.out_dir / "src"
        sv_dir.mkdir(exist_ok=True)
        for name, content in res["systemverilog_modules"].items():
            (sv_dir / f"{name}.sv").write_text(content)
        log.info(
            "  • Wrote %d SystemVerilog modules", len(res["systemverilog_modules"])
        )

        # Behaviour profile (optional)
        if profile_secs > 0:
            profile = self.profiler.capture_behavior_profile(duration=profile_secs)
            profile_file = self.out_dir / "behavior_profile.json"
            profile_file.write_text(profile.json(indent=2))  # type: ignore[attr-defined]
            log.info("  • Saved behaviour profile → %s", profile_file.name)

        # TCL scripts (always two‑script flow)
        ctx = res["template_context"]
        proj_tcl = self.out_dir / "vivado_project.tcl"
        build_tcl = self.out_dir / "vivado_build.tcl"
        proj_tcl.write_text(self.tcl.build_pcileech_project_script(ctx))
        build_tcl.write_text(self.tcl.build_pcileech_build_script(ctx))
        log.info("  • Emitted Vivado scripts → %s, %s", proj_tcl.name, build_tcl.name)

        # Persist config‑space snapshot for auditing
        (self.out_dir / "device_info.json").write_text(
            json.dumps(res["config_space_data"].get("device_info", {}), indent=2)
        )

        artifacts = [str(p.relative_to(self.out_dir)) for p in self.out_dir.rglob("*")]
        return artifacts

    # ────────────────────────────────────────────────────────────────────────
    def run_vivado(self) -> None:  # pragma: no cover – optional utility
        """Hand‑off to Vivado in batch mode using the generated scripts."""
        from vivado_handling import (
            run_vivado_with_error_reporting,
            find_vivado_installation,
        )

        vivado = find_vivado_installation()
        if not vivado:
            raise RuntimeError("Vivado not found in PATH")

        build_tcl = self.out_dir / "vivado_build.tcl"
        rc, rpt = run_vivado_with_error_reporting(
            build_tcl, self.out_dir, vivado["executable"]
        )
        if rc:
            raise RuntimeError(f"Vivado failed – see {rpt}")
        log.info("Vivado implementation finished successfully ✓")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser("PCILeech FPGA Firmware Builder (unified)")
    p.add_argument("--bdf", required=True, help="PCI address e.g. 0000:03:00.0")
    p.add_argument("--board", required=True, help="Target board key")
    p.add_argument(
        "--profile",
        type=int,
        default=0,
        metavar="SECONDS",
        help="Capture behaviour profile",
    )
    p.add_argument("--vivado", action="store_true", help="Run Vivado after generation")
    p.add_argument(
        "--output", default="output", help="Output directory (default: ./output)"
    )
    return p.parse_args(argv)


# ──────────────────────────────────────────────────────────────────────────────
# Entry
# ──────────────────────────────────────────────────────────────────────────────


def main(argv: List[str] | None = None) -> int:  # noqa: D401
    args = parse_args(argv)
    out_dir = Path(args.output).resolve()

    try:
        t0 = time.perf_counter()
        builder = FirmwareBuilder(args.bdf, args.board, out_dir)
        artifacts = builder.build(profile_secs=args.profile)
        dt = time.perf_counter() - t0
        log.info("Build finished in %.1f s ✓", dt)

        if args.vivado:
            builder.run_vivado()

        # Friendly summary
        print("\nGenerated artifacts (relative to output dir):")
        for art in artifacts:
            print("  –", art)
        return 0

    except Exception as exc:  # pragma: no cover
        log.error("Build failed: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
