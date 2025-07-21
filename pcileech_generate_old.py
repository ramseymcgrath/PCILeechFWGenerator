#!/usr/bin/env python3
"""
PCILeech Firmware Generator - Legacy compatibility shim.
This forwards to the new unified entrypoint.

NOTE: This script exists only for backward compatibility.
All functionality has been moved to pcileech.py with proper
logging, string formatting, and error handling utilities.
"""

import sys

# Forward to the new unified entrypoint
if __name__ == "__main__":
    # Add 'build' subcommand to arguments
    sys.argv.insert(1, "build")

    # Import and run the unified entrypoint
    from pcileech import main

    sys.exit(main())


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
    fallback_group.add_argument(
        "--legacy-compatibility",
        action="store_true",
        help="Enable legacy compatibility mode (temporarily restores old fallback behavior)",
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

    # Check if device exists
    return True


def run_pcileech_generation(args, allowed_fallbacks, denied_fallbacks):
    """Run PCILeech firmware generation."""
    try:
        # Import with proper path relative to project root
        from src.device_clone.pcileech_generator import (
            PCILeechGenerationConfig,
            PCILeechGenerator,
        )

        logger.info(
            f"Starting PCILeech firmware generation for {args.bdf} on {args.board}"
        )

        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)

        # Determine fallback mode based on legacy compatibility flag
        fallback_mode = args.fallback_mode
        if args.legacy_compatibility and fallback_mode == "none":
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
            fallback_mode=fallback_mode,
            allowed_fallbacks=allowed_fallbacks,
            denied_fallbacks=denied_fallbacks,
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
        # Import with proper path relative to project root
        from src.build import FirmwareBuilder

        logger.info(
            f"Starting legacy firmware generation for {args.bdf} on {args.board}"
        )

        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)

        # Initialize legacy builder
        builder = FirmwareBuilder(bdf=args.bdf, board=args.board, out_dir=output_dir)

        # Run legacy build
        # Run legacy build with the correct method
        profile_duration = args.profile_duration if args.enable_profiling else 0
        generated_files = builder.build(profile_secs=profile_duration)

        # Create a compatible result structure
        build_result = {
            "success": True,
            "files_generated": generated_files,
            "build_time": 0,  # Not tracked in the new API
        }

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
    args, allowed_fallbacks, denied_fallbacks = parse_arguments()

    # Setup verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("PCILeech Firmware Generator - PCILeech-first build system")
    logger.info(f"Target device: {args.bdf}")
    logger.info(f"Target board: {args.board}")
    logger.info(f"Output directory: {args.output_dir}")

    # Log fallback settings
    if args.fallback_mode != "none" or allowed_fallbacks or denied_fallbacks:
        logger.info(f"Fallback mode: {args.fallback_mode}")
        if allowed_fallbacks:
            logger.info(f"Allowed fallbacks: {', '.join(allowed_fallbacks)}")
        if denied_fallbacks:
            logger.info(f"Denied fallbacks: {', '.join(denied_fallbacks)}")

    # Validate environment
    if not validate_environment():
        return 1

    # Initialize fallback manager for high-level decisions
    try:
        from src.device_clone.fallback_manager import FallbackManager

        fallback_manager = FallbackManager(
            mode=args.fallback_mode,
            allowed_fallbacks=allowed_fallbacks,
            denied_fallbacks=denied_fallbacks,
        )
    except ImportError:
        fallback_manager = None
        logger.warning("FallbackManager not available, using legacy fallback behavior")

    # Try PCILeech generation first (unless legacy fallback is forced)
    if not args.legacy_fallback:
        logger.info("Attempting PCILeech generation (primary path)")
        if run_pcileech_generation(args, allowed_fallbacks, denied_fallbacks):
            logger.info("PCILeech generation completed successfully")
            return 0
        else:
            # Check if legacy fallback is allowed
            if fallback_manager and not fallback_manager.confirm_fallback(
                "legacy-build-system",
                "PCILeech generation failed",
                "The legacy build system uses a different approach that may work in some cases.",
            ):
                logger.error(
                    "PCILeech generation failed and legacy fallback denied by policy"
                )
                return 1
            else:
                logger.warning(
                    "PCILeech generation failed, falling back to legacy system"
                )

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
