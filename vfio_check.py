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
import logging
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.error_utils import log_error_with_root_cause
from src.log_config import get_logger, setup_logging
from src.string_utils import log_error_safe, log_info_safe


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

    # Setup logging
    if args.quiet:
        setup_logging(level=logging.WARNING)
    else:
        setup_logging(level=logging.INFO)

    logger = get_logger(__name__)

    if not args.quiet:
        log_info_safe(logger, "🔧 VFIO Configuration Checker", prefix="VFIO")
        log_info_safe(logger, "=" * 50, prefix="VFIO")
        log_info_safe(
            logger, "Checking VFIO setup for PCILeech compatibility...", prefix="VFIO"
        )

        if args.device_bdf:
            log_info_safe(
                logger, "Target Device: {device}", prefix="VFIO", device=args.device_bdf
            )
        log_info_safe(logger, "", prefix="VFIO")

    try:
        from src.cli.vfio_diagnostics import VFIODiagnostics, run_vfio_diagnostic

        # Run diagnostics
        result = run_vfio_diagnostic(
            device_bdf=args.device_bdf,
            interactive=args.interactive and not args.generate_script,
        )

        if args.quiet:
            # Just print summary for quiet mode
            status_symbol = "✅" if result.can_proceed else "❌"
            log_info_safe(
                logger,
                "{symbol} VFIO Status: {status}",
                prefix="VFIO",
                symbol=status_symbol,
                status=result.overall_status.value.upper(),
            )
            if result.critical_issues:
                log_info_safe(
                    logger,
                    "Critical Issues: {count}",
                    prefix="VFIO",
                    count=len(result.critical_issues),
                )

        # Generate script if requested
        if args.generate_script:
            diagnostics = VFIODiagnostics(args.device_bdf)
            script = diagnostics.get_remediation_script(result)
            script_path = "vfio_remediation.sh"

            with open(script_path, "w") as f:
                f.write(script)

            os.chmod(script_path, 0o755)
            log_info_safe(
                logger,
                "\n📝 Remediation script generated: {path}",
                prefix="VFIO",
                path=script_path,
            )
            log_info_safe(logger, "To apply fixes, run:", prefix="VFIO")
            log_info_safe(logger, "   sudo ./{path}", prefix="VFIO", path=script_path)

        # Exit with appropriate code
        return 0 if result.can_proceed else 1

    except ImportError as e:
        log_error_safe(logger, "❌ VFIO diagnostics module not found.", prefix="VFIO")
        log_error_safe(
            logger,
            "Please ensure you're running this from the PCILeech project directory.",
            prefix="VFIO",
        )
        return 1
    except KeyboardInterrupt:
        log_info_safe(logger, "\n⚠️  Operation cancelled by user.", prefix="VFIO")
        return 1
    except Exception as e:
        log_error_with_root_cause(logger, "❌ Error", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
