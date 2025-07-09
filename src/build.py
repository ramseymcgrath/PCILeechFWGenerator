#!/usr/bin/env python3
"""
PCILeech FPGA Firmware Builder – Unified Edition with MSI-X Fix
================================================================
This streamlined script **always** runs the modern unified PCILeech build flow:
    • PCI configuration‑space capture via VFIO
    • SystemVerilog + TCL generation through *device_clone.pcileech_generator*
    • Optional Vivado hand‑off
    • Fixed MSI-X module generation and file extension handling


Usage
-----
python3 pcileech_firmware_builder.py \
        --bdf 0000:03:00.0 \
        --board pcileech_35t325_x4 \
        [--vivado] \
        [--preload-msix]
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

# Import from simplified structure
from src import get_board_info, validate_board
from src.device_clone import board_config
# Import msix_capability at the module level to avoid late imports
from src.device_clone.msix_capability import parse_msix_capability

from .log_config import get_logger, setup_logging
from .string_utils import safe_format

# ──────────────────────────────────────────────────────────────────────────────
# Mandatory project‑local imports – these *must* exist in production images
# ──────────────────────────────────────────────────────────────────────────────
# Constants
REQUIRED_MODULES = [
    "src.device_clone.pcileech_generator",
    "src.device_clone.behavior_profiler",
    "src.templating.tcl_builder",
]
BUFFER_SIZE = 1024 * 1024  # 1MB buffer for file operations
CONFIG_SPACE_PATH_TEMPLATE = "/sys/bus/pci/devices/{}/config"


def check_required_modules() -> None:
    """
    Check that all required modules are available.
    Provides detailed diagnostics on import failure.
    """
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
            print(
                f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}",
                file=sys.stderr,
            )
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
            print(
                f"Checking for __init__.py files in path: {module_dir}", file=sys.stderr
            )
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

            # List sys.path
            print("\nPython module search path:", file=sys.stderr)
            for path in sys.path:
                print(f"  - {path}", file=sys.stderr)

            # Exit immediately on import failure
            raise SystemExit(2) from err


# Check required modules before proceeding
check_required_modules()

from src.device_clone.behavior_profiler import BehaviorProfiler
from src.device_clone.board_config import get_pcileech_board_config
from src.device_clone.pcileech_generator import (PCILeechGenerationConfig,
                                                 PCILeechGenerator)
from src.templating.tcl_builder import BuildContext, TCLBuilder

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
    """
    Wrapper around PCILeechGenerator for unified builds with MSI-X fixes.

    This class handles the complete firmware generation process including:
    - MSI-X capability preloading before VFIO binding
    - SystemVerilog module generation
    - TCL script generation for Vivado
    - Optional behavior profiling
    - File organization with proper extensions
    """

    def __init__(
        self,
        bdf: str,
        board: str,
        out_dir: Path,
        enable_profiling: bool = True,
        preload_msix: bool = True,
    ):
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.preload_msix = preload_msix

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
        self.bdf = bdf

    def _preload_msix_data(self) -> Dict[str, Any]:
        """
        Preload MSI-X data before VFIO binding to ensure it's available.

        This method reads the PCI config space directly from sysfs before
        the device is bound to VFIO, which would make this data inaccessible.

        Returns:
            Dictionary containing MSI-X data if available, empty dict on failure

        Raises:
            No exceptions - all errors are caught and logged
        """
        if not self.preload_msix:
            return {}

        try:
            log.info("➤ Preloading MSI-X data before VFIO binding")

            # Read config space from sysfs before VFIO binding
            config_space_path = CONFIG_SPACE_PATH_TEMPLATE.format(self.bdf)
            if not os.path.exists(config_space_path):
                log.warning(
                    "Config space not accessible via sysfs, skipping MSI-X preload"
                )
                return {}

            with open(config_space_path, "rb") as f:
                config_space_bytes = f.read()

            config_space_hex = config_space_bytes.hex()
            msix_info = parse_msix_capability(config_space_hex)

            if msix_info["table_size"] > 0:
                log.info(
                    "  • Found MSI-X capability: %d vectors", msix_info["table_size"]
                )
                return {
                    "preloaded": True,
                    "msix_info": msix_info,
                    "config_space_hex": config_space_hex,
                    "config_space_bytes": config_space_bytes,
                }
            else:
                log.info("  • No MSI-X capability found")
                return {"preloaded": True, "msix_info": None}

        except Exception as e:
            log.warning("MSI-X preload failed: %s", str(e))
            # Log more details in debug mode
            if log.isEnabledFor(logging.DEBUG):
                log.debug("MSI-X preload exception details:", exc_info=True)
            return {}

    # ────────────────────────────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────────────────────────────
    def _inject_msix_data(
        self, res: Dict[str, Any], preloaded_data: Dict[str, Any]
    ) -> None:
        """
        Inject preloaded MSI-X data into the generation result if available.

        Args:
            res: The generation result dictionary to update
            preloaded_data: The preloaded MSI-X data
        """
        if not (
            preloaded_data.get("preloaded")
            and "msix_info" in preloaded_data
            and preloaded_data["msix_info"] is not None
        ):
            return

        log.info("  • Using preloaded MSI-X data")
        if "msix_data" not in res or not res["msix_data"]:
            msix_info = preloaded_data["msix_info"]
            res["msix_data"] = {
                "capability_info": msix_info,
                "table_size": msix_info["table_size"],
                "table_bir": msix_info["table_bir"],
                "table_offset": msix_info["table_offset"],
                "pba_bir": msix_info["pba_bir"],
                "pba_offset": msix_info["pba_offset"],
                "enabled": msix_info["enabled"],
                "function_mask": msix_info["function_mask"],
                "is_valid": True,
                "validation_errors": [],
            }

            # Update template context
            if "template_context" in res and "msix_config" in res["template_context"]:
                res["template_context"]["msix_config"].update(
                    {
                        "is_supported": True,
                        "num_vectors": msix_info["table_size"],
                    }
                )

    def _write_systemverilog_modules(
        self, modules: Dict[str, str]
    ) -> tuple[list[str], list[str]]:
        """
        Write SystemVerilog modules to disk with proper file extensions.

        Args:
            modules: Dictionary of module names to content

        Returns:
            Tuple of (sv_files, special_files) lists
        """
        sv_dir = self.out_dir / "src"
        sv_dir.mkdir(exist_ok=True)

        sv_files = []
        special_files = []

        for name, content in modules.items():
            # Handle special file extensions while keeping them in src/ directory
            if name.endswith(".coe") or name.endswith(".hex"):
                # Keep original extension for special files
                file_path = sv_dir / name
                special_files.append(name)
            else:
                # SystemVerilog files get .sv extension (avoid double .sv)
                if name.endswith(".sv"):
                    file_path = sv_dir / name
                    sv_files.append(name)
                else:
                    file_path = sv_dir / f"{name}.sv"
                    sv_files.append(f"{name}.sv")

            # Use buffered writing for potentially large files
            with open(file_path, "w", buffering=BUFFER_SIZE) as f:
                f.write(content)

        return sv_files, special_files

    def _json_serialize_default(self, obj: Any) -> str:
        """Default JSON serialization function for complex objects."""
        return obj.__dict__ if hasattr(obj, "__dict__") else str(obj)

    def build(self, profile_secs: int = 0) -> List[str]:
        """
        Run the full firmware generation flow with MSI-X fixes.

        This method orchestrates the complete build process:
        1. Preload MSI-X data if requested
        2. Generate PCILeech firmware
        3. Inject preloaded MSI-X data if available
        4. Write SystemVerilog modules with correct extensions
        5. Generate behavior profile if requested
        6. Build TCL scripts for Vivado
        7. Save device info for auditing

        Args:
            profile_secs: Number of seconds to run behavior profiling (0 to disable)

        Returns:
            List of generated artifact paths (relative to output directory)
        """
        # Preload MSI-X data if requested
        preloaded_data = self._preload_msix_data()

        log.info("➤ Generating PCILeech firmware …")
        res = self.gen.generate_pcileech_firmware()

        # Inject preloaded MSI-X data if available
        self._inject_msix_data(res, preloaded_data)

        # Write modules with correct file extensions
        sv_files, special_files = self._write_systemverilog_modules(
            res["systemverilog_modules"]
        )

        log.info(
            "  • Wrote %d SystemVerilog modules: %s", len(sv_files), ", ".join(sv_files)
        )
        if special_files:
            log.info(
                "  • Wrote %d special files: %s",
                len(special_files),
                ", ".join(special_files),
            )

        # Behavior profile (optional)
        if profile_secs > 0:
            profile = self.profiler.capture_behavior_profile(duration=profile_secs)
            profile_file = self.out_dir / "behavior_profile.json"
            profile_file.write_text(
                json.dumps(
                    profile,
                    indent=2,
                    default=self._json_serialize_default,
                )
            )
            log.info("  • Saved behavior profile → %s", profile_file.name)

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

        log.info("  • Emitted Vivado scripts → %s, %s", proj_tcl.name, build_tcl.name)

        # Persist config-space snapshot for auditing
        (self.out_dir / "device_info.json").write_text(
            json.dumps(
                res["config_space_data"].get("device_info", {}),
                indent=2,
                default=self._json_serialize_default,
            )
        )

        # Collect and return only file artifacts (not directories)
        artifacts = [
            str(p.relative_to(self.out_dir))
            for p in self.out_dir.rglob("*")
            if p.is_file()
        ]
        return artifacts

    # ────────────────────────────────────────────────────────────────────────
    def run_vivado(self) -> None:  # pragma: no cover – optional utility
        """
        Hand-off to Vivado in batch mode using the generated scripts.

        This method imports vivado_handling modules on demand to avoid
        dependencies when Vivado integration is not needed.

        Raises:
            RuntimeError: If Vivado is not found or the build fails
        """
        from vivado_handling import (find_vivado_installation,
                                     run_vivado_with_error_reporting)

        vivado = find_vivado_installation()
        if not vivado:
            raise RuntimeError("Vivado not found in PATH")

        build_tcl = self.out_dir / "vivado_build.tcl"
        rc, rpt = run_vivado_with_error_reporting(
            build_tcl, self.out_dir, vivado["executable"]
        )
        if rc:
            raise RuntimeError(f"Vivado failed – see {rpt}")
        log.info("Vivado implementation finished successfully ✓")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        argv: Command line arguments (uses sys.argv if None)

    Returns:
        Parsed arguments namespace
    """
    p = argparse.ArgumentParser(
        "PCILeech FPGA Firmware Builder (unified with MSI-X fixes)"
    )
    p.add_argument("--bdf", required=True, help="PCI address e.g. 0000:03:00.0")
    p.add_argument("--board", required=True, help="Target board key")
    p.add_argument(
        "--profile",
        type=int,
        default=30,
        metavar="SECONDS",
        help="Capture behavior profile",
    )
    p.add_argument("--vivado", action="store_true", help="Run Vivado after generation")
    p.add_argument(
        "--output", default="output", help="Output directory (default: ./output)"
    )
    p.add_argument(
        "--preload-msix",
        action="store_true",
        default=True,
        help="Preload MSI-X data before VFIO binding to ensure availability (default: enabled)",
    )
    return p.parse_args(argv)


# ──────────────────────────────────────────────────────────────────────────────
# Entry
# ──────────────────────────────────────────────────────────────────────────────


def main(argv: Optional[List[str]] = None) -> int:  # noqa: D401
    """
    Main entry point for the PCILeech firmware builder.

    Args:
        argv: Command line arguments (uses sys.argv if None)

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args(argv)
    out_dir = Path(args.output).resolve()

    try:
        t0 = time.perf_counter()
        enable_profiling = args.profile > 0

        # Initialize the builder
        builder = FirmwareBuilder(
            bdf=args.bdf,
            board=args.board,
            out_dir=out_dir,
            enable_profiling=enable_profiling,
            preload_msix=getattr(args, "preload_msix", True),
        )

        artifacts = builder.build(profile_secs=args.profile)
        dt = time.perf_counter() - t0
        log.info("Build finished in %.1f s ✓", dt)

        if args.vivado:
            builder.run_vivado()

        # Friendly summary
        print("\nGenerated artifacts (relative to output dir):")
        for art in artifacts:
            print("  -", art)
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
