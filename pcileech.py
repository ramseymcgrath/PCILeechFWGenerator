#!/usr/bin/env python3
"""
PCILeech Firmware Generator - Unified Entry Point

This is the single entry point for all PCILeech functionality:
- CLI mode for scripted builds
- TUI mode for interactive use
- VFIO checking and system validation
- Container and local environment support
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import our custom utilities
from src.log_config import setup_logging, get_logger
from src.string_utils import (
    safe_format,
    log_info_safe,
    log_error_safe,
    log_warning_safe,
)
from src.error_utils import log_error_with_root_cause, format_concise_error


def get_available_boards():
    """Get list of available board configurations."""
    try:
        from src.device_clone.board_config import list_supported_boards

        boards = list_supported_boards()
        if not boards:
            return [
                "pcileech_35t325_x4",
                "pcileech_75t484_x1",
                "pcileech_100t484_x1",
            ]
        return sorted(boards)
    except Exception:
        return [
            "pcileech_35t325_x4",
            "pcileech_75t484_x1",
            "pcileech_100t484_x1",
        ]


def check_sudo():
    """Check if running as root and warn if not."""
    logger = get_logger(__name__)
    if os.geteuid() != 0:
        log_warning_safe(
            logger,
            "PCILeech requires root privileges for hardware access.",
            prefix="SUDO",
        )
        log_warning_safe(logger, "Please run with sudo or as root user.", prefix="SUDO")
        return False
    return True


def check_vfio_requirements():
    """Check if VFIO modules are loaded."""
    logger = get_logger(__name__)
    try:
        # Check if VFIO modules are loaded
        with open("/proc/modules", "r") as f:
            modules = f.read()
            if "vfio " not in modules or "vfio_pci " not in modules:
                log_warning_safe(logger, "VFIO modules not loaded. Run:", prefix="VFIO")
                log_warning_safe(logger, "  sudo modprobe vfio vfio-pci", prefix="VFIO")
                return False
    except FileNotFoundError:
        # /proc/modules not available, skip check
        pass
    return True


def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="pcileech",
        description="PCILeech Firmware Generator - Unified Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  build          Build firmware (CLI mode)
  tui            Launch interactive TUI
  flash          Flash firmware to device
  check          Check VFIO configuration
  donor-template Generate donor info template
  version        Show version information

Examples:
  # Interactive TUI mode
  sudo python3 pcileech.py tui

  # CLI build mode
  sudo python3 pcileech.py build --bdf 0000:03:00.0 --board pcileech_35t325_x1

  # Check VFIO configuration
  sudo python3 pcileech.py check --device 0000:03:00.0

  # Flash firmware
  sudo python3 pcileech.py flash output/firmware.bin
  
  # Generate donor template
  sudo python3 pcileech.py donor-template -o my_device.json
  sudo python3 pcileech.py donor-template --blank -o minimal.json  # Minimal template
  sudo python3 pcileech.py donor-template --bdf 0000:03:00.0  # Pre-fill with device info
  
  # Build with donor template output
  sudo python3 pcileech.py build --bdf 0000:03:00.0 --board pcileech_35t325_x4 --output-template device_template.json
        """,
    )

    # Add global options
    parser.add_argument(
        "--version", action="version", version="PCILeech Firmware Generator v2.0"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress non-error output"
    )

    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Build command (CLI mode)
    build_parser = subparsers.add_parser("build", help="Build firmware (CLI mode)")
    build_parser.add_argument(
        "--bdf", required=True, help="PCI Bus:Device.Function (e.g., 0000:03:00.0)"
    )
    build_parser.add_argument(
        "--board",
        required=True,
        choices=get_available_boards(),
        help="Target board configuration",
    )
    build_parser.add_argument(
        "--advanced-sv",
        action="store_true",
        help="Enable advanced SystemVerilog features",
    )
    build_parser.add_argument(
        "--enable-variance", action="store_true", help="Enable manufacturing variance"
    )
    build_parser.add_argument(
        "--output-dir", default="output", help="Output directory for generated files"
    )
    build_parser.add_argument(
        "--output-template",
        help="Output donor info JSON template alongside build artifacts",
    )
    build_parser.add_argument(
        "--donor-template",
        help="Use donor info JSON template to override discovered values",
    )

    # TUI command
    tui_parser = subparsers.add_parser("tui", help="Launch interactive TUI")
    tui_parser.add_argument("--profile", help="Load configuration profile on startup")

    # Flash command
    flash_parser = subparsers.add_parser("flash", help="Flash firmware to device")
    flash_parser.add_argument("firmware", help="Path to firmware file")
    flash_parser.add_argument("--board", help="Board type for flashing")
    flash_parser.add_argument("--device", help="USB device for flashing")

    # Check command (VFIO)
    check_parser = subparsers.add_parser("check", help="Check VFIO configuration")
    check_parser.add_argument("--device", help="Specific device to check (BDF format)")
    check_parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive remediation mode"
    )
    check_parser.add_argument(
        "--fix", action="store_true", help="Attempt to fix issues automatically"
    )

    # Version command
    subparsers.add_parser("version", help="Show version information")

    # Donor template command
    donor_parser = subparsers.add_parser(
        "donor-template", help="Generate donor info template"
    )
    donor_parser.add_argument(
        "-o",
        "--output",
        default="donor_info_template.json",
        help="Output file path (default: donor_info_template.json)",
    )
    donor_parser.add_argument(
        "--compact",
        action="store_true",
        help="Generate compact JSON without indentation",
    )
    donor_parser.add_argument(
        "--blank",
        action="store_true",
        help="Generate minimal template with only essential fields",
    )
    donor_parser.add_argument(
        "--bdf", help="Pre-fill template with device info from specified BDF"
    )
    donor_parser.add_argument("--validate", help="Validate an existing donor info file")

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging with our custom configuration
    if args.verbose:
        setup_logging(level=logging.DEBUG)
    elif args.quiet:
        setup_logging(level=logging.ERROR)
    else:
        setup_logging(level=logging.INFO)

    logger = get_logger(__name__)

    # Check sudo requirements for hardware operations
    if args.command in ["build", "check"] and not check_sudo():
        log_error_safe(
            logger, "Root privileges required for hardware operations.", prefix="MAIN"
        )
        return 1

    # Check VFIO requirements for build operations
    if args.command == "build" and not check_vfio_requirements():
        log_error_safe(
            logger,
            "Run 'sudo python3 pcileech.py check' to validate VFIO setup.",
            prefix="MAIN",
        )
        return 1

    # Route to appropriate handler
    if args.command == "build":
        return handle_build(args)
    elif args.command == "tui":
        return handle_tui(args)
    elif args.command == "flash":
        return handle_flash(args)
    elif args.command == "check":
        return handle_check(args)
    elif args.command == "version":
        return handle_version(args)
    elif args.command == "donor-template":
        return handle_donor_template(args)
    else:
        # No command specified, show help
        parser.print_help()
        return 1


def handle_build(args):
    """Handle CLI build mode."""
    logger = get_logger(__name__)
    try:
        # Import and use the existing CLI build functionality
        from src.cli.cli import main as cli_main

        log_info_safe(
            logger,
            "Starting build for device {bdf} on board {board}",
            prefix="BUILD",
            bdf=args.bdf,
            board=args.board,
        )

        # Convert arguments to CLI format
        cli_args = ["build", "--bdf", args.bdf, "--board", args.board]

        if args.advanced_sv:
            cli_args.append("--advanced-sv")
        if args.enable_variance:
            cli_args.append("--enable-variance")

        if args.output_template:
            cli_args.extend(["--output-template", args.output_template])

        if args.donor_template:
            cli_args.extend(["--donor-template", args.donor_template])

        # Run the CLI
        return cli_main(cli_args)

    except Exception as e:
        log_error_with_root_cause(logger, "Build failed", e)
        return 1


def handle_tui(args):
    """Handle TUI mode."""
    logger = get_logger(__name__)
    try:
        # Check if Textual is available
        try:
            import textual  # noqa: F401
        except ImportError:
            log_error_safe(logger, "Textual framework not installed.", prefix="TUI")
            log_error_safe(
                logger,
                "Please install with: pip install textual rich psutil",
                prefix="TUI",
            )
            return 1

        # Import and run the TUI application
        from src.tui.main import PCILeechTUI

        log_info_safe(logger, "Launching interactive TUI", prefix="TUI")
        app = PCILeechTUI()
        app.run()
        return 0

    except KeyboardInterrupt:
        log_info_safe(logger, "TUI application interrupted by user", prefix="TUI")
        return 1
    except Exception as e:
        log_error_with_root_cause(logger, "TUI failed", e)
        return 1


def handle_flash(args):
    """Handle firmware flashing."""
    logger = get_logger(__name__)
    try:
        # Check if firmware file exists
        firmware_path = Path(args.firmware)
        if not firmware_path.exists():
            log_error_safe(
                logger,
                "Firmware file not found: {path}",
                prefix="FLASH",
                path=firmware_path,
            )
            return 1

        log_info_safe(
            logger, "Flashing firmware: {path}", prefix="FLASH", path=firmware_path
        )

        # Try to use the flash utility
        try:
            from src.cli.flash import flash_firmware

            flash_firmware(firmware_path)
        except ImportError:
            # Fallback to direct usbloader if available
            import subprocess

            result = subprocess.run(
                ["usbloader", "-f", str(firmware_path)], capture_output=True, text=True
            )
            if result.returncode != 0:
                log_error_safe(
                    logger, "Flash failed: {error}", prefix="FLASH", error=result.stderr
                )
                return 1
            log_info_safe(
                logger,
                "Successfully flashed {path}",
                prefix="FLASH",
                path=firmware_path,
            )

        return 0

    except Exception as e:
        log_error_with_root_cause(logger, "Flash failed", e)
        return 1


def handle_check(args):
    """Handle VFIO checking."""
    logger = get_logger(__name__)
    try:
        # Import the VFIO diagnostics functionality
        from src.cli.vfio_diagnostics import (
            Diagnostics,
            Status,
            render,
            remediation_script,
        )
        import subprocess
        from pathlib import Path

        log_info_safe(
            logger,
            "Running VFIO diagnostics{device}",
            prefix="CHECK",
            device=f" for device {args.device}" if args.device else "",
        )

        # Create diagnostics instance and run checks
        diag = Diagnostics(args.device)
        report = diag.run()

        # Render the report
        render(report)

        # Handle fix option
        if args.fix:
            if report.overall == Status.OK:
                log_info_safe(
                    logger,
                    "✅ System already VFIO-ready - nothing to do",
                    prefix="CHECK",
                )
                return 0

            # Generate remediation script
            script_text = remediation_script(report)
            temp = Path("/tmp/vfio_fix.sh")
            temp.write_text(script_text)
            temp.chmod(0o755)

            log_info_safe(
                logger,
                "📝 Remediation script written to {path}",
                prefix="CHECK",
                path=temp,
            )

            if args.interactive:
                confirm = input("Run remediation script now? [y/N]: ").strip().lower()
                if confirm not in ("y", "yes"):
                    log_info_safe(logger, "Aborted.", prefix="CHECK")
                    return 1

            log_info_safe(
                logger,
                "Executing remediation script (requires root)...",
                prefix="CHECK",
            )
            try:
                subprocess.run(["sudo", str(temp)], check=True)

                # Re-run diagnostics after remediation
                log_info_safe(
                    logger,
                    "Re-running diagnostics after remediation...",
                    prefix="CHECK",
                )
                new_report = Diagnostics(args.device).run()
                render(new_report)
                return 0 if new_report.can_proceed else 1
            except subprocess.CalledProcessError as e:
                log_error_safe(
                    logger, "Script failed: {error}", prefix="CHECK", error=str(e)
                )
                return 1

        # Exit with appropriate code
        return 0 if report.can_proceed else 1

    except ImportError as e:
        log_error_safe(logger, "❌ VFIO diagnostics module not found.", prefix="CHECK")
        log_error_safe(
            logger,
            "Please ensure you're running this from the PCILeech project directory.",
            prefix="CHECK",
        )
        log_error_safe(logger, "Details: {error}", prefix="CHECK", error=str(e))
        return 1
    except Exception as e:
        log_error_with_root_cause(logger, "VFIO check failed", e)
        import traceback

        if logger.isEnabledFor(logging.DEBUG):
            traceback.print_exc()
        return 1


def handle_version(args):
    """Handle version information."""
    logger = get_logger(__name__)
    log_info_safe(logger, "PCILeech Firmware Generator v2.0", prefix="VERSION")
    log_info_safe(logger, "Copyright (c) 2024 PCILeech Project", prefix="VERSION")
    log_info_safe(logger, "Licensed under MIT License", prefix="VERSION")

    # Show additional version info
    try:
        import pkg_resources

        version = pkg_resources.get_distribution("pcileechfwgenerator").version
        log_info_safe(
            logger, "Package version: {version}", prefix="VERSION", version=version
        )
    except:
        pass

    return 0


def handle_donor_template(args):
    """Handle donor template generation."""
    logger = get_logger(__name__)
    try:
        from src.device_clone.donor_info_template import DonorInfoTemplateGenerator

        # If validate flag is set, validate the file instead
        if args.validate:
            try:
                validator = DonorInfoTemplateGenerator()
                is_valid, errors = validator.validate_template_file(args.validate)
                if is_valid:
                    log_info_safe(
                        logger,
                        "✓ Template file '{file}' is valid",
                        prefix="DONOR",
                        file=args.validate,
                    )
                    return 0
                else:
                    log_error_safe(
                        logger,
                        "✗ Template file '{file}' has errors:",
                        prefix="DONOR",
                        file=args.validate,
                    )
                    for error in errors:
                        log_error_safe(
                            logger, "  - {error}", prefix="DONOR", error=error
                        )
                    return 1
            except Exception as e:
                log_error_with_root_cause(logger, "Error validating template", e)
                return 1

        # Generate template
        generator = DonorInfoTemplateGenerator()

        # If BDF is specified, try to pre-fill with device info
        if args.bdf:
            log_info_safe(
                logger,
                "Generating template with device info from {bdf}...",
                prefix="DONOR",
                bdf=args.bdf,
            )
            try:
                template = generator.generate_template_from_device(args.bdf)
                # Check if we actually got device info
                if template["device_info"]["identification"]["vendor_id"] is None:
                    log_error_safe(
                        logger,
                        "Failed to read device information from {bdf}",
                        prefix="DONOR",
                        bdf=args.bdf,
                    )
                    log_error_safe(logger, "Possible causes:", prefix="DONOR")
                    log_error_safe(logger, "  - Device does not exist", prefix="DONOR")
                    log_error_safe(
                        logger,
                        "  - Insufficient permissions (try with sudo)",
                        prefix="DONOR",
                    )
                    log_error_safe(
                        logger, "  - lspci command not available", prefix="DONOR"
                    )
                    return 1
            except Exception as e:
                log_error_with_root_cause(logger, "Could not read device info", e)
                return 1
        elif args.blank:
            # Generate minimal template
            template = generator.generate_minimal_template()
            log_info_safe(
                logger, "Generating minimal donor info template...", prefix="DONOR"
            )
        else:
            # Generate full template
            template = generator.generate_blank_template()

        # Save the template
        generator.save_template_dict(
            template, Path(args.output), pretty=not args.compact
        )
        log_info_safe(
            logger,
            "✓ Donor info template saved to: {output}",
            prefix="DONOR",
            output=args.output,
        )

        if args.bdf:
            log_info_safe(
                logger, "Template pre-filled with device information.", prefix="DONOR"
            )
            log_info_safe(
                logger, "Please review and complete any missing fields.", prefix="DONOR"
            )
        else:
            log_info_safe(logger, "Next steps:", prefix="DONOR")
            log_info_safe(
                logger,
                "1. Fill in the device-specific values in the template",
                prefix="DONOR",
            )
            log_info_safe(
                logger,
                "2. Run behavioral profiling to capture timing data",
                prefix="DONOR",
            )
            log_info_safe(
                logger,
                "3. Use the completed template for advanced device cloning",
                prefix="DONOR",
            )

        return 0

    except Exception as e:
        log_error_with_root_cause(logger, "Failed to generate donor template", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
