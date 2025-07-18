#!/usr/bin/env python3
"""
Test suite for TUI components.

This module imports and runs all the TUI unit tests from the src/tui directory.
"""

import unittest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import TUI test modules
from src.tui.test_main import *
from src.tui.core.test_build_orchestrator import TestBuildOrchestrator
from src.tui.core.test_config_manager import TestConfigManager
from src.tui.core.test_device_manager import *


if __name__ == "__main__":
    unittest.main()
