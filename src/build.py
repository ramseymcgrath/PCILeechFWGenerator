#!/usr/bin/env python3
"""
FPGA firmware builder - Modular Architecture

This is the new modular build system that replaces the monolithic build.py.
It provides improved performance through async operations and better maintainability
through a clean modular architecture.

Usage:
  python3 build.py --bdf 0000:03:00.0 --board 75t

Boards:
  35t  → Squirrel   (PCIeSquirrel)
  75t  → Enigma-X1  (PCIeEnigmaX1)
  100t → ZDMA       (XilinxZDMA)
"""

import argparse
import sys
from pathlib import Path

# Import the modular build system
try:
    from build.controller import create_build_controller, run_controlled_build

    MODULAR_BUILD_AVAILABLE = True
except ImportError:
    MODULAR_BUILD_AVAILABLE = False
    print("[!] Modular build system not available")
    sys.exit(1)


def main():
    """Main entry point for the modular build system."""
    parser = argparse.ArgumentParser(
        description="FPGA firmware builder - Modular Architecture"
    )
    parser.add_argument(
        "--bdf", required=True, help="Bus:Device.Function (e.g., 0000:03:00.0)"
    )
    parser.add_argument("--board", required=True, help="Target board")
    parser.add_argument(
        "--advanced-sv", action="store_true", help="Enable advanced SystemVerilog"
    )
    parser.add_argument(
        "--enable-behavior-profiling",
        action="store_true",
        help="Enable behavior profiling",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--use-donor-dump", action="store_true", help="Use donor dump kernel module"
    )
    parser.add_argument(
        "--skip-board-check", action="store_true", help="Skip board validation"
    )
    parser.add_argument("--donor-info-file", help="Path to donor info JSON file")
    parser.add_argument("--save-analysis", help="Save analysis to file")

    args = parser.parse_args()

    print("[*] PCILeech FPGA Firmware Builder - Modular Architecture")
    print(f"[*] Target: {args.bdf} on {args.board}")

    try:
        summary = run_controlled_build(args)

        print(f"\n[✓] Build completed successfully!")
        print(f"[✓] Total time: {summary['total_time']:.2f}s")

        if "performance_improvement" in summary:
            improvement = summary["performance_improvement"][
                "estimated_improvement_percent"
            ]
            print(f"[✓] Performance improvement: {improvement:.1f}% over legacy build")

        if "output_files" in summary:
            print(f"[✓] SystemVerilog: {summary['output_files']['systemverilog']}")
            print(f"[✓] TCL script: {summary['output_files']['tcl']}")

        print(f"[✓] Processed {summary.get('register_count', 0)} registers")

        return 0

    except Exception as e:
        print(f"[!] Build failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
