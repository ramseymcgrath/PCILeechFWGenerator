#!/usr/bin/env python3
"""
TUI version of PCILeech firmware generator.
Provides an interactive interface for the generate.py workflow.
"""

import argparse
import sys
import textwrap
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the interactive functions from generate.py
try:
    from generate import (choose_board, choose_device_type,
                          interactive_configuration, prompt_integer,
                          prompt_yes_no)

    INTERACTIVE_AVAILABLE = True
except ImportError:
    # Fallback if imports fail
    INTERACTIVE_AVAILABLE = False
    choose_board = None
    choose_device_type = None
    prompt_yes_no = None
    prompt_integer = None
    interactive_configuration = None


def main():
    """Main entry point for TUI application"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description="PCILeech TUI - Interactive firmware generator",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent(
                """
                Examples:
                  # Launch TUI interface
                  sudo python3 tui_generate.py

                  # Launch with interactive configuration first
                  sudo python3 tui_generate.py --interactive

                  # Quick start with prompts
                  sudo python3 tui_generate.py --quick-config
                """
            ),
        )

        parser.add_argument(
            "--interactive",
            action="store_true",
            help="Launch interactive configuration mode before TUI",
        )

        parser.add_argument(
            "--quick-config",
            action="store_true",
            help="Quick configuration prompts for common settings",
        )

        args = parser.parse_args()

        # Handle interactive configuration
        if args.interactive:
            if not INTERACTIVE_AVAILABLE or not interactive_configuration:
                print(
                    "[!] Interactive configuration not available. Launching TUI directly..."
                )
            else:
                try:
                    print("=== Pre-TUI Interactive Configuration ===\n")
                    config = interactive_configuration()
                    print(
                        f"\n[✓] Configuration saved. Launching TUI with your settings..."
                    )
                    # The TUI will pick up the configuration
                except KeyboardInterrupt:
                    print("\n[!] Configuration cancelled by user")
                    return 1
                except Exception as e:
                    print(f"[✗] Configuration error: {e}")
                    return 1

        # Handle quick configuration
        elif args.quick_config:
            if not INTERACTIVE_AVAILABLE:
                print(
                    "[!] Interactive functions not available. Launching TUI directly..."
                )
            else:
                try:
                    print("=== Quick Configuration ===\n")
                    # Type ignore for mypy since we check INTERACTIVE_AVAILABLE
                    board = choose_board()  # type: ignore
                    device_type = choose_device_type()  # type: ignore
                    advanced_sv = prompt_yes_no("Enable advanced SystemVerilog generation?")  # type: ignore
                    flash_after = prompt_yes_no("Flash firmware after build?")  # type: ignore

                    print(f"\n=== Quick Config Summary ===")
                    print(f"Board: {board}")
                    print(f"Device Type: {device_type}")
                    print(f"Advanced SystemVerilog: {advanced_sv}")
                    print(f"Flash After Build: {flash_after}")
                    print(f"\n[✓] Quick configuration complete. Launching TUI...")

                except KeyboardInterrupt:
                    print("\n[!] Quick configuration cancelled by user")
                    return 1
                except Exception as e:
                    print(f"[✗] Quick configuration error: {e}")
                    return 1

        # Check if Textual is available
        try:
            pass
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
        print(f"Error starting TUI application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
