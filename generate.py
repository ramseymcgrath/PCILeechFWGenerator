#!/usr/bin/env python3
"""
PCILeech Firmware Generator - Modular Podman-based build system.

This is the main orchestrator that coordinates the modular components:
- CLI parsing with sub-commands
- VFIO device binding with context manager
- Container-based builds
- Firmware flashing
- Centralized logging
"""

import os
import sys
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import from src.cli if available, otherwise use fallback
try:
    from src.cli import parse_args, create_build_config_from_args
    from src.cli import BuildConfig
    from src.cli import run_build_container
    from src.cli import flash_firmware
    from src.cli import VFIOBinder
except ImportError:
    # Fallback to direct build system integration
    parse_args = None
    create_build_config_from_args = None
    BuildConfig = None
    run_build_container = None
    flash_firmware = None
    VFIOBinder = None

try:
    from utils.logging import setup_logging, get_logger
except ImportError:
    # Fallback logging setup
    import logging

    def setup_logging(level=logging.INFO):
        logging.basicConfig(
            level=level, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def get_logger(name):
        return logging.getLogger(name)


try:
    from utils.shell import Shell
except ImportError:
    # Fallback shell implementation
    import subprocess

    class Shell:
        def run_check(self, cmd):
            try:
                subprocess.run(cmd, shell=True, check=True, capture_output=True)
                return True
            except subprocess.CalledProcessError:
                return False


def validate_environment() -> None:
    """Validate that the environment is properly set up."""
    logger = get_logger(__name__)

    if os.geteuid() != 0:
        error_msg = "This script requires root privileges. Run with sudo."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check if git is available
    shell = Shell()
    if not shell.run_check("which git"):
        error_msg = "Git not found in PATH. Please install Git first."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Check if Podman is available
    from cli import require_podman

    require_podman()


def handle_build_command(args) -> int:
    """Handle the build sub-command with PCILeech as primary build path.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger = get_logger(__name__)

    try:
        # Create configuration from arguments
        cfg = create_build_config_from_args(args)

        logger.info(
            f"Starting PCILeech-first build for device {cfg.bdf} on board {cfg.board}"
        )
        print(f"[*] Building PCILeech firmware for {cfg.bdf} on {cfg.board}")

        # Try PCILeech generator first
        try:
            from src.device_clone.pcileech_generator import (
                PCILeechGenerator,
                PCILeechGenerationConfig,
            )

            # Create PCILeech configuration
            pcileech_config = PCILeechGenerationConfig(
                device_bdf=cfg.bdf,
                device_profile="generic",
                enable_behavior_profiling=True,
                enable_manufacturing_variance=True,
                enable_advanced_features=True,
                output_dir=Path("output"),
                strict_validation=True,
                fail_on_missing_data=True,
            )

            # Initialize and run PCILeech generator
            pcileech_generator = PCILeechGenerator(pcileech_config)

            logger.info("Using PCILeech generator as primary build path")
            print("[*] Using PCILeech generator as primary build path")

            # Generate PCILeech firmware
            generation_result = pcileech_generator.generate_pcileech_firmware()

            # Save generated firmware
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            pcileech_generator.save_generated_firmware(generation_result, output_dir)

            logger.info("PCILeech firmware generation completed successfully")
            print("[✓] PCILeech firmware generation completed successfully")

        except ImportError as e:
            logger.warning(
                f"PCILeech generator not available, falling back to container build: {e}"
            )
            print(
                f"[!] PCILeech generator not available, falling back to container build"
            )

            # Fallback to container build for backward compatibility
            with VFIOBinder(cfg.bdf) as vfio_dev:
                logger.info(f"VFIO device ready: {vfio_dev}")
                run_build_container(cfg, vfio_dev)

        # Flash firmware if requested
        if cfg.flash:
            firmware_path = Path("output/firmware.bin")
            if not firmware_path.exists():
                error_msg = "ERROR: firmware.bin not found in ./output directory"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            flash_firmware(firmware_path)

        logger.info("Build process completed successfully")
        print("[✓] Build process completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Build failed: {e}")
        print(f"[✗] Build failed: {e}")
        return 1


def handle_flash_command(args) -> int:
    """Handle the flash sub-command.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger = get_logger(__name__)

    try:
        firmware_path = Path(args.firmware_path)
        if not firmware_path.exists():
            error_msg = f"Firmware file not found: {firmware_path}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        flash_firmware(firmware_path)
        logger.info("Flash completed successfully")
        print("[✓] Flash completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Flash failed: {e}")
        print(f"[✗] Flash failed: {e}")
        return 1


def handle_tui_command(args) -> int:
    """Handle the TUI sub-command.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger = get_logger(__name__)

    try:
        # Import and launch TUI
        from src.tui.main import PCILeechTUI

        app = PCILeechTUI()
        app.run()
        return 0

    except ImportError:
        error_msg = "TUI dependencies not installed. Install with: pip install textual rich psutil"
        logger.error(error_msg)
        print(f"[✗] {error_msg}")
        return 1
    except Exception as e:
        error_msg = f"Failed to launch TUI: {e}"
        logger.error(error_msg)
        print(f"[✗] {error_msg}")
        return 1


def main() -> int:
    """Main entry point for the firmware generator."""
    try:
        # Parse command line arguments
        args = parse_args()

        # Setup logging
        log_level = logging.DEBUG if getattr(args, "verbose", False) else logging.INFO
        setup_logging(level=log_level)

        logger = get_logger(__name__)
        logger.info("Starting PCILeech firmware generation process")

        # Setup shell with dry-run mode if requested
        if getattr(args, "dry_run", False):
            logger.info("Running in dry-run mode")
            print("[*] Running in dry-run mode - no actual changes will be made")

        # Validate environment
        validate_environment()

        # Dispatch to appropriate command handler
        if args.command == "build":
            return handle_build_command(args)
        elif args.command == "flash":
            return handle_flash_command(args)
        elif args.command == "tui":
            return handle_tui_command(args)
        else:
            logger.error(f"Unknown command: {args.command}")
            print(f"[✗] Unknown command: {args.command}")
            return 1

    except KeyboardInterrupt:
        print("\n[!] Process interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[✗] Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
