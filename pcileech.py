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
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def check_sudo():
    """Check if running as root and warn if not."""
    if os.geteuid() != 0:
        print("Warning: PCILeech requires root privileges for hardware access.")
        print("Please run with sudo or as root user.")
        return False
    return True


def check_vfio_requirements():
    """Check if VFIO modules are loaded."""
    try:
        # Check if VFIO modules are loaded
        with open("/proc/modules", "r") as f:
            modules = f.read()
            if "vfio " not in modules or "vfio_pci " not in modules:
                print("Warning: VFIO modules not loaded. Run:")
                print("  sudo modprobe vfio vfio-pci")
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
  sudo python3 pcileech.py build --bdf 0000:03:00.0 --board 75t

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
        choices=[
            "35t",
            "75t",
            "100t",
            "pcileech_35t325_x4",
            "pcileech_75t484_x1",
            "pcileech_100t484_x1",
        ],
        help="Target board configuration",
    )
    build_parser.add_argument(
        "--device-type",
        default="network",
        choices=["generic", "network", "storage", "graphics", "audio"],
        help="Type of device being cloned",
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

    # Handle global options
    if args.verbose:
        import logging

        logging.basicConfig(level=logging.DEBUG)
    elif args.quiet:
        import logging

        logging.basicConfig(level=logging.ERROR)
    else:
        import logging

        logging.basicConfig(level=logging.INFO)

    # Check sudo requirements for hardware operations
    if args.command in ["build", "check"] and not check_sudo():
        print("Error: Root privileges required for hardware operations.")
        return 1

    # Check VFIO requirements for build operations
    if args.command == "build" and not check_vfio_requirements():
        print("Run 'sudo python3 pcileech.py check' to validate VFIO setup.")
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
    try:
        # Import and use the existing CLI build functionality
        from src.cli.cli import main as cli_main

        # Convert arguments to CLI format
        cli_args = [
            "build",
            "--bdf",
            args.bdf,
            "--board",
            args.board,
            "--device-type",
            args.device_type,
        ]

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
        print(f"Build failed: {e}")
        return 1


def handle_tui(args):
    """Handle TUI mode."""
    try:
        # Check if Textual is available
        try:
            import textual  # noqa: F401
        except ImportError:
            print("Error: Textual framework not installed.")
            print("Please install with: pip install textual rich psutil")
            return 1

        # Import and run the TUI application
        from src.tui.main import PCILeechTUI

        app = PCILeechTUI()
        app.run()
        return 0

    except KeyboardInterrupt:
        print("\nTUI application interrupted by user")
        return 1
    except Exception as e:
        print(f"TUI failed: {e}")
        return 1


def handle_flash(args):
    """Handle firmware flashing."""
    try:
        # Check if firmware file exists
        firmware_path = Path(args.firmware)
        if not firmware_path.exists():
            print(f"Error: Firmware file not found: {firmware_path}")
            return 1

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
                print(f"Flash failed: {result.stderr}")
                return 1
            print(f"Successfully flashed {firmware_path}")

        return 0

    except Exception as e:
        print(f"Flash failed: {e}")
        return 1


def handle_check(args):
    """Handle VFIO checking."""
    try:
        # Import VFIO checker functionality
        import vfio_check

        # Convert arguments to vfio_check format
        vfio_args = []
        if args.device:
            vfio_args.append(args.device)
        if args.interactive:
            vfio_args.append("--interactive")
        if args.fix:
            vfio_args.append("--fix")

        # Call the main function directly with sys.argv manipulation
        import sys

        original_argv = sys.argv
        try:
            sys.argv = ["vfio_check"] + vfio_args
            return vfio_check.main()
        finally:
            sys.argv = original_argv

    except Exception as e:
        print(f"VFIO check failed: {e}")
        return 1


def handle_version(args):
    """Handle version information."""
    print("PCILeech Firmware Generator v2.0")
    print("Copyright (c) 2024 PCILeech Project")
    print("Licensed under MIT License")

    # Show additional version info
    try:
        import pkg_resources

        version = pkg_resources.get_distribution("pcileechfwgenerator").version
        print(f"Package version: {version}")
    except:
        pass

    return 0


def handle_donor_template(args):
    """Handle donor template generation."""
    try:
        from src.device_clone.donor_info_template import \
            DonorInfoTemplateGenerator

        # If validate flag is set, validate the file instead
        if args.validate:
            try:
                validator = DonorInfoTemplateGenerator()
                is_valid, errors = validator.validate_template_file(args.validate)
                if is_valid:
                    print(f"✓ Template file '{args.validate}' is valid")
                    return 0
                else:
                    print(f"✗ Template file '{args.validate}' has errors:")
                    for error in errors:
                        print(f"  - {error}")
                    return 1
            except Exception as e:
                print(f"Error validating template: {e}")
                return 1

        # Generate template
        generator = DonorInfoTemplateGenerator()

        # If BDF is specified, try to pre-fill with device info
        if args.bdf:
            print(f"Generating template with device info from {args.bdf}...")
            try:
                template = generator.generate_template_from_device(args.bdf)
                # Check if we actually got device info
                if template["device_info"]["identification"]["vendor_id"] is None:
                    print(f"Error: Failed to read device information from {args.bdf}")
                    print("Possible causes:")
                    print("  - Device does not exist")
                    print("  - Insufficient permissions (try with sudo)")
                    print("  - lspci command not available")
                    return 1
            except Exception as e:
                print(f"Error: Could not read device info: {e}")
                return 1
        elif args.blank:
            # Generate minimal template
            template = generator.generate_minimal_template()
            print("Generating minimal donor info template...")
        else:
            # Generate full template
            template = generator.generate_blank_template()

        # Save the template
        generator.save_template_dict(
            template, Path(args.output), pretty=not args.compact
        )
        print(f"✓ Donor info template saved to: {args.output}")

        if args.bdf:
            print("\nTemplate pre-filled with device information.")
            print("Please review and complete any missing fields.")
        else:
            print("\nNext steps:")
            print("1. Fill in the device-specific values in the template")
            print("2. Run behavioral profiling to capture timing data")
            print("3. Use the completed template for advanced device cloning")

        return 0

    except Exception as e:
        print(f"Failed to generate donor template: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
