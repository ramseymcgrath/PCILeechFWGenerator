#!/usr/bin/env python3
"""
VFIO Configuration Checker

Standalone tool to check VFIO configuration and provide remediation guidance.
Can be run independently or integrated into PCILeech workflows.

Usage:
    python3 vfio_check.py                    # Check general VFIO setup
    python3 vfio_check.py 0000:03:00.0       # Check specific device
    python3 vfio_check.py --interactive      # Interactive remediation
"""

import argparse
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="VFIO Configuration Checker and Remediation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Check general VFIO setup
  %(prog)s 0000:03:00.0              # Check specific device
  %(prog)s --interactive             # Interactive mode with remediation
  %(prog)s 0000:00:17.0 --interactive # Check device with interactive fixes

This tool helps diagnose and fix VFIO configuration issues that prevent
PCILeech from accessing PCI devices for firmware generation.
        """,
    )

    parser.add_argument(
        "device_bdf",
        nargs="?",
        help="PCI device BDF (Bus:Device.Function) to check, e.g., 0000:03:00.0",
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Enable interactive remediation mode",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress detailed output, only show summary",
    )

    parser.add_argument(
        "--generate-script",
        action="store_true",
        help="Generate remediation script without running it",
    )

    args = parser.parse_args()

    if not args.quiet:
        print("🔧 VFIO Configuration Checker")
        print("=" * 50)
        print("Checking VFIO setup for PCILeech compatibility...")

        if args.device_bdf:
            print(f"Target Device: {args.device_bdf}")
        print()

    try:
        from src.cli.vfio_diagnostics import (VFIODiagnostics,
                                              run_vfio_diagnostic)

        # Run diagnostics
        result = run_vfio_diagnostic(
            device_bdf=args.device_bdf,
            interactive=args.interactive and not args.generate_script,
        )

        if args.quiet:
            # Just print summary for quiet mode
            status_symbol = "✅" if result.can_proceed else "❌"
            print(f"{status_symbol} VFIO Status: {result.overall_status.value.upper()}")
            if result.critical_issues:
                print(f"Critical Issues: {len(result.critical_issues)}")

        # Generate script if requested
        if args.generate_script:
            diagnostics = VFIODiagnostics(args.device_bdf)
            script = diagnostics.get_remediation_script(result)
            script_path = "vfio_remediation.sh"

            with open(script_path, "w") as f:
                f.write(script)

            os.chmod(script_path, 0o755)
            print(f"\n📝 Remediation script generated: {script_path}")
            print("To apply fixes, run:")
            print(f"   sudo ./{script_path}")

        # Exit with appropriate code
        return 0 if result.can_proceed else 1

    except ImportError:
        print("❌ Error: VFIO diagnostics module not found.")
        print("Please ensure you're running this from the PCILeech project directory.")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
