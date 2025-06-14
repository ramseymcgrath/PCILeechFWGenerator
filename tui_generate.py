#!/usr/bin/env python3
"""
TUI version of PCILeech firmware generator.
Provides an interactive interface for the generate.py workflow.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Main entry point for TUI application"""
    try:
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
