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
import glob
import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Configure noisy loggers to be less verbose
for noisy_logger in ["paramiko", "urllib3", "matplotlib", "PIL"]:
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)

# Regular expression for parsing lspci output
PCI_RE = re.compile(
    r"(?P<bdf>[0-9a-fA-F:.]+) .*?\["
    r"(?P<class>[0-9a-fA-F]{4})\]: .*?\["
    r"(?P<ven>[0-9a-fA-F]{4}):(?P<dev>[0-9a-fA-F]{4})\]"
)

# Device profile names - these match the actual profiles in the system
DEVICE_PROFILES = ["network_card", "storage_controller", "generic", "audio_controller"]

# For backward compatibility with command line arguments
DEVICE_TYPES = ["network", "storage", "graphics", "audio"]

# Map device types to profile names
DEVICE_TYPE_TO_PROFILE = {
    "network": "network_card",
    "storage": "storage_controller",
    "graphics": "generic",  # No specific graphics profile available
    "audio": "audio_controller",
}


def discover_supported_boards() -> List[str]:
    """Dynamically discover supported boards from the boards directory."""
    # Find all YAML files in the boards directory
    repo_root = Path(__file__).resolve().parent
    board_files = glob.glob(str(repo_root / "boards" / "*.yaml"))

    # Extract board names from filenames
    boards = [Path(f).stem for f in board_files]

    if not boards:
        # Fallback to hardcoded list if no boards found
        logger.warning("No board files found in boards directory, using fallback list")
        return [
            "pcileech_75t484_x1",
            "pcileech_35t484_x1",
            "pcileech_35t325_x4",
            "pcileech_35t325_x1",
            "pcileech_100t484_x1",
            "pcileech_enigma_x1",
            "pcileech_squirrel",
            "pcileech_pciescreamer_xc7a35",
        ]

    logger.debug(f"Discovered {len(boards)} boards: {', '.join(boards)}")
    return sorted(boards)


def list_pci_devices() -> List[Dict[str, str]]:
    """List all PCI devices on the system."""
    try:
        # Import shell utility with proper path resolution
        repo_root = Path(__file__).resolve().parent
        sys.path.insert(0, str(repo_root))

        try:
            from utils.shell import Shell

            out = Shell().run("lspci -Dnn")
        except ImportError:
            # Fallback if Shell class is not available
            logger.debug("Shell class not available, using subprocess directly")
            out = subprocess.check_output(
                "lspci -Dnn", shell=True, text=True, stderr=subprocess.STDOUT
            ).strip()

        devs = []  # type: List[Dict[str, str]]
        for line in out.splitlines():
            m = PCI_RE.match(line)
            if m:
                d = m.groupdict()
                d["pretty"] = line
                devs.append(d)
        return devs
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logger.error(f"Failed to list PCI devices: {e}")
        logger.error(
            "Please ensure 'pciutils' package is installed (apt install pciutils)"
        )
        return []


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
        raise RuntimeError("No PCIe devices found. Is pciutils installed?")
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

    # Dynamically discover supported boards
    supported_boards = discover_supported_boards()
    parser.add_argument(
        "--board",
        choices=supported_boards,
        help="Target board configuration",
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for generated files (default: output)",
    )

    parser.add_argument(
        "--device-type",
        default="network",  # For compatibility only
        choices=DEVICE_TYPES,
        help="Type of device being cloned (generic not allowed) - for compatibility only",
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

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate everything but skip binding + Vivado",
    )

    # Add fallback control group - but force "none" mode
    fallback_group = parser.add_argument_group("Fallback Control")
    fallback_group.add_argument(
        "--fallback-mode",
        choices=["none"],  # Only allow "none" mode
        default="none",
        help="Control fallback behavior (only none=fail-fast is allowed)",
    )
    # These arguments are kept for compatibility but will be ignored
    fallback_group.add_argument(
        "--allow-fallbacks",
        type=str,
        help="[DISABLED] Comma-separated list of allowed fallbacks",
    )
    fallback_group.add_argument(
        "--deny-fallbacks",
        type=str,
        help="[DISABLED] Comma-separated list of denied fallbacks",
    )

    args = parser.parse_args()

    # Force no fallbacks regardless of command line arguments
    allowed_fallbacks = []
    denied_fallbacks = ["all"]  # Deny all fallbacks

    # Force fallback mode to "none" regardless of what was passed
    args.fallback_mode = "none"

    logger.info("Fallbacks to generic code have been disabled")
    return args, allowed_fallbacks, denied_fallbacks


def validate_environment() -> bool:
    """Validate that the environment is properly set up."""
    # Check if vfio-pci module is loaded
    try:
        with open("/proc/modules", "r") as f:
            modules = f.read()
        if "vfio_pci" not in modules:
            logger.warning("vfio-pci module not loaded, attempting to load it...")
            result = subprocess.run(
                ["modprobe", "vfio-pci"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error(f"Failed to load vfio-pci module (rc={result.returncode})")
                logger.error(f"Error: {result.stderr.strip()}")
                return False
            logger.info("Successfully loaded vfio-pci module")
    except Exception as e:
        logger.warning(f"Failed to check or load vfio-pci module: {e}")
        return False

    return True


def run_build(args, allowed_fallbacks, denied_fallbacks) -> Tuple[bool, Dict[str, Any]]:
    """Run the PCILeech firmware generation process directly.

    Returns:
        Tuple of (success, build_metadata)
    """
    build_metadata = {
        "bdf": args.bdf,
        "board": args.board,
        "device_type": args.device_type,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "git_commit": None,  # Will be populated if available
    }

    try:
        # Try to get git commit hash
        try:
            git_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
            ).strip()
            build_metadata["git_commit"] = git_hash
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        # Validate device type is in the allowed list
        if args.device_type not in DEVICE_TYPES:
            logger.error(
                f"Device type '{args.device_type}' not in supported types: {DEVICE_TYPES}"
            )
            logger.info("Please use one of the supported device types")
            return False, build_metadata

        logger.info(f"Device type '{args.device_type}' is used for compatibility only")
        logger.info(
            f"Will use 'generic' as the device profile (matching container approach)"
        )

        # Import VFIO handler and build components
        from src.cli.vfio_handler import VFIOBinder
        from src.device_clone.pcileech_generator import (
            PCILeechGenerationConfig,
            PCILeechGenerator,
        )

        # Create output directory
        output_dir = Path(args.output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize fallback manager with strict settings to prevent fallbacks
        try:
            from src.device_clone.fallback_manager import FallbackManager

            # Force strict settings regardless of what was passed
            fallback_manager = FallbackManager(
                mode="none",  # Force "none" mode
                allowed_fallbacks=[],  # Allow no fallbacks
                denied_fallbacks=[
                    "all",
                    "generic",
                    "config-space",
                    "msix",
                    "behavior-profiling",
                ],  # Deny all fallbacks
            )
            logger.info(
                "Fallback manager initialized in strict mode (no fallbacks allowed)"
            )
        except ImportError:
            logger.warning(
                "FallbackManager not available, continuing without fallback management"
            )
            fallback_manager = None

        logger.info(
            f"Starting PCILeech firmware generation for {args.bdf} on {args.board}"
        )
        logger.info(f"Device type: {args.device_type} (for compatibility only)")
        logger.info(f"Output directory: {output_dir}")

        # Check if we're in dry-run mode
        if args.dry_run:
            logger.info("DRY RUN MODE: Skipping VFIO binding and Vivado execution")
            # Create PCILeech configuration with the specific device type
            # Simplify by using "generic" as the device_profile, matching the container approach
            device_profile = "generic"
            logger.info(
                f"Using device profile: '{device_profile}' (matching container approach)"
            )

            pcileech_config = PCILeechGenerationConfig(
                device_bdf=args.bdf,
                device_profile=device_profile,  # Using "generic" to match container approach
                enable_behavior_profiling=args.enable_profiling,
                behavior_capture_duration=float(args.profile_duration),
                enable_manufacturing_variance=args.enable_variance,
                enable_advanced_features=args.enable_advanced,
                output_dir=output_dir,
                strict_validation=True,
                fail_on_missing_data=True,
                fallback_mode="none",  # Force "none" mode
                allowed_fallbacks=[],  # Allow no fallbacks
                denied_fallbacks=["all"],  # Deny all fallbacks
            )

            # Initialize PCILeech generator
            pcileech_generator = PCILeechGenerator(pcileech_config)

            # Generate PCILeech firmware
            logger.info("Generating PCILeech firmware...")
            t0 = time.perf_counter()
            generation_result = pcileech_generator.generate_pcileech_firmware()
            dt = time.perf_counter() - t0
            logger.info(f"Build finished in {dt:.1f} s ✓")

            # Save generated firmware
            pcileech_generator.save_generated_firmware(generation_result, output_dir)

            # Get list of generated files
            artifacts = [
                str(p.relative_to(output_dir))
                for p in output_dir.rglob("*")
                if p.is_file()
            ]

            # Print summary
            logger.info("\nGenerated artifacts (relative to output dir):")
            for art in artifacts:
                logger.info(f"  - {art}")

            logger.info(
                f"\nBuild completed successfully. Output saved to: {output_dir}"
            )

            # Save build metadata
            build_metadata["artifacts"] = artifacts
            build_metadata["success"] = True
            build_metadata_path = output_dir / "build_meta.json"
            with open(build_metadata_path, "w") as f:
                json.dump(build_metadata, f, indent=2)
            logger.info(f"Build metadata saved to: {build_metadata_path}")

            return True, build_metadata

        # Bind device to VFIO
        logger.info(f"Binding device {args.bdf} to VFIO...")
        try:
            # Note: VFIOBinder doesn't accept auto_fix parameter directly
            # If auto_fix is needed, it would need to be handled separately
            with VFIOBinder(args.bdf, attach=True):
                logger.info("Device successfully bound to VFIO")

                # Create PCILeech configuration with the specific device type
                # Map device type to profile name
                # Determine device profile to use
                # Simplify by using "generic" as the device_profile, matching the container approach
                device_profile = "generic"
                logger.info(
                    f"Using device profile: '{device_profile}' (matching container approach)"
                )

                pcileech_config = PCILeechGenerationConfig(
                    device_bdf=args.bdf,
                    device_profile=device_profile,  # Using "generic" to match container approach
                    enable_behavior_profiling=args.enable_profiling,
                    behavior_capture_duration=float(args.profile_duration),
                    enable_manufacturing_variance=args.enable_variance,
                    enable_advanced_features=args.enable_advanced,
                    output_dir=output_dir,
                    strict_validation=True,
                    fail_on_missing_data=True,
                    fallback_mode="none",  # Force "none" mode
                    allowed_fallbacks=[],  # Allow no fallbacks
                    denied_fallbacks=["all"],  # Deny all fallbacks
                )

                # Initialize PCILeech generator
                pcileech_generator = PCILeechGenerator(pcileech_config)

                # Generate PCILeech firmware
                logger.info("Generating PCILeech firmware...")
                t0 = time.perf_counter()
                generation_result = pcileech_generator.generate_pcileech_firmware()
                dt = time.perf_counter() - t0
                logger.info(f"Build finished in {dt:.1f} s ✓")

                # Save generated firmware
                pcileech_generator.save_generated_firmware(
                    generation_result, output_dir
                )

                # Get list of generated files
                artifacts = [
                    str(p.relative_to(output_dir))
                    for p in output_dir.rglob("*")
                    if p.is_file()
                ]

                # Run Vivado if requested
                if args.vivado:
                    logger.info("Running Vivado implementation...")
                    from src.build import FirmwareBuilder

                    builder = FirmwareBuilder(
                        bdf=args.bdf,
                        board=args.board,
                        out_dir=output_dir,
                        enable_profiling=args.enable_profiling,
                    )
                    try:
                        builder.run_vivado()
                        logger.info("Vivado implementation completed successfully")
                    except Exception as e:
                        logger.error(f"Vivado implementation failed: {e}")
                        if hasattr(e, "__cause__") and e.__cause__:
                            logger.error(f"Root cause: {e.__cause__}")
                        return False, build_metadata

                # Print summary
                logger.info("\nGenerated artifacts (relative to output dir):")
                for art in artifacts:
                    logger.info(f"  - {art}")

                logger.info(
                    f"\nBuild completed successfully. Output saved to: {output_dir}"
                )

                # Save build metadata
                build_metadata["artifacts"] = artifacts
                build_metadata["success"] = True
                build_metadata_path = output_dir / "build_meta.json"
                with open(build_metadata_path, "w") as f:
                    json.dump(build_metadata, f, indent=2)
                logger.info(f"Build metadata saved to: {build_metadata_path}")

                return True, build_metadata
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

            build_metadata["success"] = False
            build_metadata["error"] = str(e)
            return False, build_metadata

    except ImportError as e:
        logger.error(f"Required module not available: {e}")
        build_metadata["success"] = False
        build_metadata["error"] = f"Required module not available: {e}"
        return False, build_metadata
    except Exception as e:
        logger.error(f"Build failed: {e}")
        build_metadata["success"] = False
        build_metadata["error"] = f"Build failed: {e}"
        return False, build_metadata


def check_root_privileges() -> bool:
    """Check if the script is running with root privileges."""
    if os.geteuid() != 0:
        logger.error("This script requires root privileges. Run with sudo.")
        return False
    return True


def main():
    """Main entry point."""
    args, allowed_fallbacks, denied_fallbacks = parse_arguments()

    # Setup verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        # But keep noisy loggers at INFO level
        for noisy_logger in ["paramiko", "urllib3", "matplotlib", "PIL"]:
            logging.getLogger(noisy_logger).setLevel(logging.INFO)

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
        board = pick(discover_supported_boards(), "Select board #: ")
        logger.info(f"Selected board: {board}")

    # Get device type first
    device_type = args.device_type

    # Interactive device type selection if needed
    if not device_type or device_type == "":
        logger.info(
            "No device type specified, launching interactive device type picker..."
        )
        device_type = pick(DEVICE_TYPES, "Select device type #: ")
        logger.info(f"Selected device type: {device_type}")

    # Validate device type is one of the supported types
    if device_type not in DEVICE_TYPES:
        logger.warning(
            f"Device type '{device_type}' not in supported types: {DEVICE_TYPES}"
        )
        logger.info("Defaulting to 'network' device type")
        device_type = "network"

    # We're using "generic" as the device_profile in run_build, so this is just for logging
    logger.info(
        f"Note: Using 'generic' as device profile (matching container approach)"
    )

    # Update args with interactive selections
    args.bdf = bdf
    args.board = board
    args.device_type = device_type

    logger.info(f"Target device: {args.bdf}")
    logger.info(f"Target board: {args.board}")
    logger.info(f"Device type: {args.device_type} (for compatibility only)")

    # Check for root privileges AFTER interactive selection
    if not args.dry_run and not check_root_privileges():
        return 1

    # Validate environment
    if not args.dry_run and not validate_environment():
        return 1

    # Run the build
    success, build_metadata = run_build(args, allowed_fallbacks, denied_fallbacks)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
