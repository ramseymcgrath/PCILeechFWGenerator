#!/usr/bin/env python3
"""
CLI entry point for pcileech-build console script.
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
    """Main entry point for pcileech-build command"""
    try:
        # Import and run the build module
        # Try different import strategies to handle various installation
        # scenarios
        try:
            # First try the standard import (works when installed as package)
            from src.build import main as build_main
        except ImportError:
            # If that fails, try a direct import from the current directory
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            try:
                from build import main as build_main
            except ImportError:
                print("Error: Could not import build module.")
                print(
                    "This could be due to running with sudo without preserving the Python path."
                )
                print("Try using the pcileech-build-sudo script instead.")
                return 1

        return build_main()

    except KeyboardInterrupt:
        print("\nBuild process interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running build process: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
