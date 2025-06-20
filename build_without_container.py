#!/usr/bin/env python3
"""
PCILeech Firmware Generator - Non-containerized build script

This script runs the PCILeech firmware generation process directly on the host
without using a container. It handles VFIO binding and cleanup directly.

Usage:
    sudo python3 build_without_container.py [--bdf 0000:03:00.0] [--board pcileech_35t325_x4] [options]

If --bdf or --board are not provided, interactive prompts will be shown to select them.
"""

import argparse
import logging
import os
import re
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import and setup proper colored logging
from utils.logging import setup_logging, get_logger
from utils.shell import Shell

# Setup logging with color support
setup_logging(level=logging.INFO)
logger = get_logger(__name__)

# Supported boards
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

# Device types
DEVICE_TYPES = ["generic", "network", "storage", "graphics", "audio"]

# Regular expression for parsing lspci output
PCI_RE = re.compile(
    r"(?P<bdf>[0-9a-fA-F:.]+) .*?\["
    r"(?P<class>[0-9a-fA-F]{4})\]: .*?\["
    r"(?P<ven>[0-9a-fA-F]{4}):(?P<dev>[0-9a-fA-F]{4})\]"
)


def list_pci_devices() -> List[Dict[str, str]]:
    """List all PCI devices on the system."""
    out = Shell().run("lspci -Dnn")
    devs = []  # type: List[Dict[str, str]]
    for line in out.splitlines():
        m = PCI_RE.match(line)
        if m:
            d = m.groupdict()
            d["pretty"] = line
            devs.append(d)
    return devs


def pick(lst: List[str], prompt: str) -> str:
    """Interactive picker for selecting from a list."""
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
    """Interactive picker for selecting a PCI device."""
    devs = list_pci_devices()
    if not devs:
        raise RuntimeError("No PCIe devices found – are you root?")
    for i, dev in enumerate(devs):
        print(f" [{i}] {dev['pretty']}")
    while True:
        try:
            selection = input("Select donor device #: ").strip()
            if not selection:
                return devs[0]
            return devs[int(selection)]
        except (ValueError, IndexError):
            print("  Invalid selection – try again.")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PCILeech Firmware Generator - Non-containerized build"
    )

    parser.add_argument("--bdf", help="PCI Bus:Device.Function (e.g., 0000:03:00.0)")

    parser.add_argument(
        "--board",
        choices=SUPPORTED_BOARDS,
        help="Target board configuration",
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for generated files (default: output)",
    )

    parser.add_argument(
        "--device-type",
        default="generic",
        choices=DEVICE_TYPES,
        help="Type of device being cloned",
    )

    parser.add_argument(
        "--enable-profiling",
        action="store_true",
        help="Enable behavior profiling during generation",
    )

    parser.add_argument(
        "--profile-duration",
        type=int,
        default=10,
        help="Behavior profiling duration in seconds (default: 10)",
    )

    parser.add_argument(
        "--enable-variance",
        action="store_true",
        help="Enable manufacturing variance simulation",
    )

    parser.add_argument(
        "--enable-advanced",
        action="store_true",
        help="Enable advanced SystemVerilog features",
    )

    parser.add_argument(
        "--vivado",
        action="store_true",
        help="Run Vivado after generation",
    )

    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Let VFIOBinder auto-remediate issues",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    # Add fallback control group
    fallback_group = parser.add_argument_group("Fallback Control")
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

    args = parser.parse_args()

    # Process fallback lists
    allowed_fallbacks = []
    if args.allow_fallbacks:
        allowed_fallbacks = [f.strip() for f in args.allow_fallbacks.split(",")]

    denied_fallbacks = []
    if args.deny_fallbacks:
        denied_fallbacks = [f.strip() for f in args.deny_fallbacks.split(",")]

    return args, allowed_fallbacks, denied_fallbacks


def validate_environment():
    """Validate that the environment is properly set up."""
    if os.geteuid() != 0:
        logger.error("This script requires root privileges. Run with sudo.")
        return False

    # Check if vfio-pci module is loaded
    try:
        with open("/proc/modules", "r") as f:
            modules = f.read()
        if "vfio_pci" not in modules:
            logger.warning("vfio-pci module not loaded, attempting to load it...")
            os.system("modprobe vfio-pci")
    except Exception as e:
        logger.warning(f"Failed to check or load vfio-pci module: {e}")

    return True


def run_build(args, allowed_fallbacks, denied_fallbacks):
    """Run the PCILeech firmware generation process directly."""
    try:
        # Import VFIO handler and build components
        from src.cli.vfio_handler import VFIOBinder
        from src.build import FirmwareBuilder
        from src.device_clone.fallback_manager import FallbackManager

        # Create output directory
        output_dir = Path(args.output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize fallback manager
        fallback_manager = FallbackManager(
            mode=args.fallback_mode,
            allowed_fallbacks=allowed_fallbacks,
            denied_fallbacks=denied_fallbacks,
        )

        logger.info(
            f"Starting PCILeech firmware generation for {args.bdf} on {args.board}"
        )
        logger.info(f"Device type: {args.device_type}")
        logger.info(f"Output directory: {output_dir}")

        # Bind device to VFIO
        logger.info(f"Binding device {args.bdf} to VFIO...")
        try:
            # Note: VFIOBinder doesn't accept auto_fix parameter directly
            # If auto_fix is needed, it would need to be handled separately
            with VFIOBinder(args.bdf, attach=True):
                logger.info("Device successfully bound to VFIO")

                # Initialize firmware builder
                logger.info("Initializing firmware builder...")
                enable_profiling = args.enable_profiling
                builder = FirmwareBuilder(
                    bdf=args.bdf,
                    board=args.board,
                    out_dir=output_dir,
                    enable_profiling=enable_profiling,
                )

                # Run the build
                logger.info("Running firmware build...")
                profile_secs = args.profile_duration if enable_profiling else 0
                t0 = time.perf_counter()
                artifacts = builder.build(profile_secs=profile_secs)
                dt = time.perf_counter() - t0
                logger.info(f"Build finished in {dt:.1f} s ✓")

                # Run Vivado if requested
                if args.vivado:
                    logger.info("Running Vivado implementation...")
                    builder.run_vivado()

                # Print summary
                logger.info("\nGenerated artifacts (relative to output dir):")
                for art in artifacts:
                    logger.info(f"  - {art}")

                logger.info(
                    f"\nBuild completed successfully. Output saved to: {output_dir}"
                )
                return True
        except Exception as e:
            logger.error(f"Error during VFIO binding or build: {e}")
            if hasattr(e, "__cause__") and e.__cause__:
                logger.error(f"Root cause: {e.__cause__}")

            # Run VFIO diagnostics if available
            try:
                from src.cli.vfio_diagnostics import Diagnostics, render

                diag = Diagnostics(args.bdf)
                report = diag.run()
                logger.info("\nVFIO Diagnostics Report:")
                logger.info(render(report))
            except ImportError:
                logger.warning("VFIO diagnostics not available")

            return False

    except ImportError as e:
        logger.error(f"Required module not available: {e}")
        return False
    except Exception as e:
        logger.error(f"Build failed: {e}")
        return False


def main():
    """Main entry point."""
    args, allowed_fallbacks, denied_fallbacks = parse_arguments()

    # Setup verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("PCILeech Firmware Generator - Non-containerized build")

    # Interactive device selection if not provided
    bdf = args.bdf
    if not bdf:
        logger.info("No device specified, launching interactive device picker...")
        device = choose_device()
        bdf = device["bdf"]
        logger.info(f"Selected device: {device['pretty']}")

    # Interactive board selection if not provided
    board = args.board
    if not board:
        logger.info("No board specified, launching interactive board picker...")
        board = pick(SUPPORTED_BOARDS, "Select board #: ")
        logger.info(f"Selected board: {board}")

    # Interactive device type selection if using default
    device_type = args.device_type
    if device_type == "generic" and not args.device_type:
        logger.info("Using default device type, would you like to change it?")
        if input("Change device type? [y/N]: ").lower().startswith("y"):
            device_type = pick(DEVICE_TYPES, "Select device type #: ")
            logger.info(f"Selected device type: {device_type}")

    # Update args with interactive selections
    args.bdf = bdf
    args.board = board
    args.device_type = device_type

    logger.info(f"Target device: {args.bdf}")
    logger.info(f"Target board: {args.board}")
    logger.info(f"Device type: {args.device_type}")

    # Validate environment
    if not validate_environment():
        return 1

    # Run the build
    if run_build(args, allowed_fallbacks, denied_fallbacks):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
