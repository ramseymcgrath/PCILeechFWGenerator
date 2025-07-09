"""
Vivado Application Handling Module

This module contains utilities and tools for working with Xilinx Vivado:
- vivado_utils: Core utilities for finding and running Vivado
- vivado_error_reporter: Enhanced error reporting and monitoring
- vivado_build_with_errors: Build script with comprehensive error handling
"""

from .vivado_error_reporter import (VivadoErrorReporter,
                                    create_enhanced_vivado_runner,
                                    run_vivado_with_error_reporting)
from .vivado_utils import (debug_vivado_search, find_vivado_installation,
                           get_vivado_executable, get_vivado_version,
                           run_vivado_command)

__all__ = [
    # vivado_utils exports
    "find_vivado_installation",
    "get_vivado_executable",
    "get_vivado_version",
    "run_vivado_command",
    "debug_vivado_search",
    # vivado_error_reporter exports
    "VivadoErrorReporter",
    "run_vivado_with_error_reporting",
    "create_enhanced_vivado_runner",
]
