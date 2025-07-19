#!/usr/bin/env python3
"""generate.py - Legacy compatibility shim."""
from __future__ import annotations

import sys
from pathlib import Path

# Forward to the new unified entrypoint
if __name__ == "__main__":
    # Add 'build' subcommand to arguments
    sys.argv.insert(1, "build")

    # Import and run the unified entrypoint
    from pcileech import main

    sys.exit(main())
