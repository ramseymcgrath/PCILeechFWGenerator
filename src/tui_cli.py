#!/usr/bin/env python3
"""
CLI entry point for pcileech-tui console script.
This module provides the main() function that setuptools will use as an entry point.
"""

import os
import site
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add site-packages directories to path to ensure modules can be found
# This helps when running with sudo which might have a different Python
# environment
for site_dir in site.getsitepackages():
    if site_dir not in sys.path:
        sys.path.insert(0, site_dir)

# Add user site-packages
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)


def main():
    """Main entry point for pcileech-tui command"""
    try:
        # Check if Textual is available
        try:
            pass
        except ImportError:
            print("Error: Textual framework not installed.")
            print(
                "Please install TUI dependencies with: pip install pcileechfwgenerator[tui]"
            )
            return 1

        # Import and run the TUI application
        # Try different import strategies to handle various installation
        # scenarios
        try:
            # First try the standard import (works when installed as package)
            from src.tui.main import PCILeechTUI
        except ImportError:
            # If that fails, try a direct import from the current directory
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            try:
                from tui.main import PCILeechTUI
            except ImportError:
                print("Error: Could not import TUI module.")
                print(
                    "This could be due to running with sudo without preserving the Python path."
                )
                print("Try using the pcileech-tui-sudo script instead.")
                return 1

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
