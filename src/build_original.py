#!/usr/bin/env python3
"""
PCILeech FPGA Firmware Builder – Unified Edition
================================================
This streamlined script **always** runs the modern unified PCILeech build flow:
    • PCI configuration‑space capture via VFIO
    • SystemVerilog + TCL generation through *device_clone.pcileech_generator*
    • Optional Vivado hand‑off


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
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent  # /app/src -> /app
sys.path.insert(0, str(project_root))
from src.device_clone import board_config
from utils.logging import setup_logging, get_logger
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# ──────────────────────────────────────────────────────────────────────────────
# Mandatory project‑local imports – these *must* exist in production images
# ──────────────────────────────────────────────────────────────────────────────
REQUIRED_MODULES = [
    "src.device_clone.pcileech_generator",
    "src.device_clone.behavior_profiler",
    "src.templating.tcl_builder",
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

        # Add detailed diagnostics
        print("\n[DIAGNOSTICS] Python module import failure", file=sys.stderr)
        print(f"Python version: {sys.version}", file=sys.stderr)
        print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}", file=sys.stderr)
        print(f"Current directory: {os.getcwd()}", file=sys.stderr)

        # Check if the file exists
        module_parts = module.split(".")
        module_path = os.path.join(*module_parts) + ".py"
        alt_module_path = os.path.join(*module_parts[1:]) + ".py"

        print(f"Looking for module file at: {module_path}", file=sys.stderr)
        if os.path.exists(module_path):
            print(f"✓ File exists at {module_path}", file=sys.stderr)
        else:
            print(f"✗ File not found at {module_path}", file=sys.stderr)

        print(f"Looking for module file at: {alt_module_path}", file=sys.stderr)
        if os.path.exists(alt_module_path):
            print(f"✓ File exists at {alt_module_path}", file=sys.stderr)
        else:
            print(f"✗ File not found at {alt_module_path}", file=sys.stderr)

        # Check for __init__.py files
        module_dir = os.path.dirname(module_path)
        print(f"Checking for __init__.py files in path: {module_dir}", file=sys.stderr)
        current_dir = ""
        for part in module_dir.split(os.path.sep):
            if not part:
                continue
            current_dir = os.path.join(current_dir, part)
            init_path = os.path.join(current_dir, "__init__.py")
            if os.path.exists(init_path):
                print(f"✓ __init__.py exists in {current_dir}", file=sys.stderr)
            else:
                print(f"✗ Missing __init__.py in {current_dir}", file=sys.stderr)
                # Create the missing __init__.py file
                try:
                    os.makedirs(current_dir, exist_ok=True)
                    with open(init_path, "w") as f:
                        f.write("# Auto-generated __init__.py\n")
                    print(f"  Created {init_path}", file=sys.stderr)
                except Exception as e:
                    print(f"  Failed to create {init_path}: {e}", file=sys.stderr)

        # List sys.path
        print("\nPython module search path:", file=sys.stderr)
        for path in sys.path:
            print(f"  - {path}", file=sys.stderr)

        # Try to fix the issue by adding the current directory to sys.path
        print("\nAttempting to fix import issue...", file=sys.stderr)
        sys.path.insert(0, os.getcwd())
        try:
            __import__(module)
            print(f"✓ Successfully imported {module} after fix!", file=sys.stderr)
        except ImportError as e:
            print(f"✗ Still failed to import {module}: {e}", file=sys.stderr)
            raise SystemExit(2) from err

from src.device_clone.pcileech_generator import (
    PCILeechGenerationConfig,
    PCILeechGenerator,
)
from src.templating.tcl_builder import TCLBuilder, BuildContext
from src.device_clone.behavior_profiler import BehaviorProfiler
from src.device_clone.board_config import get_pcileech_board_config

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────
# Only setup logging if no handlers exist (avoid overriding CLI setup)
if not logging.getLogger().handlers:
    setup_logging(level=logging.INFO)
log = get_logger("pcileech_builder")


# ──────────────────────────────────────────────────────────────────────────────
# Helper classes
# ──────────────────────────────────────────────────────────────────────────────
class FirmwareBuilder:
    """Thin wrapper around *PCILeechGenerator* for unified builds."""

    def __init__(
        self, bdf: str, board: str, out_dir: Path, enable_profiling: bool = True
    ):
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.gen = PCILeechGenerator(
            PCILeechGenerationConfig(
                device_bdf=bdf,
                device_profile="generic",
                template_dir=None,
                output_dir=self.out_dir,
                enable_behavior_profiling=enable_profiling,
            )
        )

        self.tcl = TCLBuilder(output_dir=self.out_dir)
        self.profiler = BehaviorProfiler(bdf=bdf)
        self.board = board

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
            profile_file.write_text(json.dumps(profile, indent=2, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o)))
            log.info("  • Saved behaviour profile → %s", profile_file.name)

        # TCL scripts (always two‑script flow)
        ctx = res["template_context"]

        proj_tcl = self.out_dir / "vivado_project.tcl"
        build_tcl = self.out_dir / "vivado_build.tcl"

        self.tcl.build_all_tcl_scripts(
            board=self.board,
            device_id=ctx["device_config"]["device_id"],
            class_code=ctx["device_config"]["class_code"],
            revision_id=ctx["device_config"]["revision_id"],
            vendor_id=ctx["device_config"]["vendor_id"],
        )

        log.info("  • Emitted Vivado scripts → %s, %s", proj_tcl.name, build_tcl.name)

        # Persist config‑space snapshot for auditing
        (self.out_dir / "device_info.json").write_text(
            json.dumps(res["config_space_data"].get("device_info", {}), indent=2, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o))
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
        default=30,
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
        enable_profiling = args.profile > 0
        builder = FirmwareBuilder(
            args.bdf, args.board, out_dir, enable_profiling=enable_profiling
        )
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
        # Extract root cause manually to avoid import issues when run as script
        root_cause = str(exc)
        current = exc
        while hasattr(current, "__cause__") and current.__cause__:
            current = current.__cause__
            root_cause = str(current)

        log.error("Build failed: %s", root_cause)
        # Only show full traceback in debug mode
        if log.isEnabledFor(logging.DEBUG):
            log.debug("Full traceback:", exc_info=True)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
