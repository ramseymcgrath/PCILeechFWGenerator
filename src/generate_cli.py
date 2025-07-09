#!/usr/bin/env python3
"""
CLI entry point for pcileech-generate console script.
This module provides the main() function that setuptools will use as an entry point.
"""

import argparse
import sys
import textwrap
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Main entry point for pcileech-generate command"""
    try:
        # Check if --interactive flag is passed
        if len(sys.argv) > 1 and "--interactive" in sys.argv:
            print("=== PCILeech Firmware Generator - Interactive Mode ===\n")
            print("This will guide you through the firmware generation process.")
            print(
                "You can also use the full command-line interface with all options.\n"
            )

            # Show help for available options
            response = (
                input("Would you like to see all available options first? [y/N]: ")
                .strip()
                .lower()
            )
            if response in ["y", "yes"]:
                # Remove --interactive from args and add --help
                help_args = [arg for arg in sys.argv if arg != "--interactive"] + [
                    "--help"
                ]
                sys.argv = help_args

        # Import the pcileech_generate module from project root
        import pcileech_generate

        return pcileech_generate.main()
    except ImportError as e:
        print(f"Error importing generate module: {e}")
        print("Make sure you're running from the correct directory.")
        return 1
    except Exception as e:
        print(f"Error running generate: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
