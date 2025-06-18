#!/usr/bin/env python3
"""generate.py – thin shim around the new CLI."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

# Ensure project src in path (if invoked from repo root)
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

try:
    cli = importlib.import_module("cli")  # our new unified entrypoint (cli.py)
except ModuleNotFoundError:
    # fallback: user renamed file or running from a different location
    cli = importlib.import_module("cli")

if __name__ == "__main__":
    sys.exit(cli.main())
