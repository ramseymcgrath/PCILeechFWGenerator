#!/usr/bin/env python3
"""
PCILeech Firmware Generator - Legacy compatibility shim.
This forwards to the new unified entrypoint.
"""

import sys

# Forward to the new unified entrypoint
if __name__ == "__main__":
    # Add 'build' subcommand to arguments
    sys.argv.insert(1, "build")

    # Import and run the unified entrypoint
    from pcileech import main

    sys.exit(main())
