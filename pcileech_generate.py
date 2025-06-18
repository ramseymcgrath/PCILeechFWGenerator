#!/usr/bin/env python3
"""
PCILeech Firmware Generator - PCILeech-first build system.

This is the main entry point that uses PCILeech as the primary build pattern:
- PCILeech generator as primary build path
- Direct build system integration
- Fallback to legacy builds when needed
- Production-ready error handling
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PCILeech Firmware Generator - PCILeech-first build system"
    )

    parser.add_argument(
        "--bdf", required=True, help="PCI Bus:Device.Function (e.g., 0000:03:00.0)"
    )

    parser.add_argument(
        "--board",
        required=True,
        choices=["pcileech_35t325_x4", "pcileech_75t484_x1", "pcileech_100t484_x1"],
        help="Target board configuration",
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for generated files (default: output)",
    )

    parser.add_argument(
        "--enable-profiling",
        action="store_true",
        help="Enable behavior profiling during generation",
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
        "--profile-duration",
        type=int,
        default=10,
        help="Behavior profiling duration in seconds (default: 10)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    parser.add_argument(
        "--legacy-fallback",
        action="store_true",
        help="Force use of legacy build system",
    )

    return parser.parse_args()


def validate_environment():
    """Validate that the environment is properly set up."""
    if os.geteuid() != 0:
        logger.error("This script requires root privileges. Run with sudo.")
        return False

    # Check if device exists
    return True


def run_pcileech_generation(args):
    """Run PCILeech firmware generation."""
    try:
        from device_clone.pcileech_generator import (
            PCILeechGenerationConfig,
            PCILeechGenerator,
        )

        logger.info(
            f"Starting PCILeech firmware generation for {args.bdf} on {args.board}"
        )

        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)

        # Create PCILeech configuration
        pcileech_config = PCILeechGenerationConfig(
            device_bdf=args.bdf,
            device_profile="generic",
            enable_behavior_profiling=args.enable_profiling,
            behavior_capture_duration=float(args.profile_duration),
            enable_manufacturing_variance=args.enable_variance,
            enable_advanced_features=args.enable_advanced,
            output_dir=output_dir,
            strict_validation=True,
            fail_on_missing_data=True,
        )

        # Initialize PCILeech generator
        pcileech_generator = PCILeechGenerator(pcileech_config)

        # Generate PCILeech firmware
        logger.info("Generating PCILeech firmware...")
        generation_result = pcileech_generator.generate_pcileech_firmware()

        # Save generated firmware
        pcileech_generator.save_generated_firmware(generation_result, output_dir)

        # Print summary
        systemverilog_count = len(generation_result.get("systemverilog_modules", {}))
        firmware_components = generation_result.get("firmware_components", {})

        logger.info(f"PCILeech firmware generation completed successfully")
        logger.info(f"Generated {systemverilog_count} SystemVerilog modules")
        logger.info(f"Generated {len(firmware_components)} firmware components")
        logger.info(f"Output saved to: {output_dir}")

        return True

    except ImportError as e:
        logger.error(f"PCILeech generator not available: {e}")
        return False
    except Exception as e:
        logger.error(f"PCILeech generation failed: {e}")
        return False


def run_legacy_generation(args):
    """Run legacy firmware generation as fallback."""
    try:
        from build import PCILeechFirmwareBuilder

        logger.info(
            f"Starting legacy firmware generation for {args.bdf} on {args.board}"
        )

        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)

        # Initialize legacy builder
        builder = PCILeechFirmwareBuilder(
            bdf=args.bdf, board=args.board, output_dir=output_dir
        )

        # Run legacy build
        build_result = builder.build_firmware(
            advanced_sv=args.enable_advanced,
            enable_variance=args.enable_variance,
            behavior_profile_duration=(
                args.profile_duration if args.enable_profiling else 0
            ),
        )

        if build_result.get("success", False):
            files_generated = len(build_result.get("files_generated", []))
            logger.info(f"Legacy firmware generation completed successfully")
            logger.info(f"Generated {files_generated} files")
            logger.info(f"Build time: {build_result.get('build_time', 0):.2f} seconds")
            return True
        else:
            logger.error("Legacy firmware generation failed")
            for error in build_result.get("errors", []):
                logger.error(f"  - {error}")
            return False

    except ImportError as e:
        logger.error(f"Legacy build system not available: {e}")
        return False
    except Exception as e:
        logger.error(f"Legacy generation failed: {e}")
        return False


def main():
    """Main entry point."""
    args = parse_arguments()

    # Setup verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("PCILeech Firmware Generator - PCILeech-first build system")
    logger.info(f"Target device: {args.bdf}")
    logger.info(f"Target board: {args.board}")
    logger.info(f"Output directory: {args.output_dir}")

    # Validate environment
    if not validate_environment():
        return 1

    # Try PCILeech generation first (unless legacy fallback is forced)
    if not args.legacy_fallback:
        logger.info("Attempting PCILeech generation (primary path)")
        if run_pcileech_generation(args):
            logger.info("PCILeech generation completed successfully")
            return 0
        else:
            logger.warning("PCILeech generation failed, falling back to legacy system")

    # Fallback to legacy generation
    logger.info("Using legacy build system")
    if run_legacy_generation(args):
        logger.info("Legacy generation completed successfully")
        return 0
    else:
        logger.error("Both PCILeech and legacy generation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
