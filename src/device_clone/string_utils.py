#!/usr/bin/env python3
"""
String utilities for device_clone module.

This module provides a local import path for string utilities within the device_clone
package, importing from the main string_utils module.
"""

# Import all functions from the main string_utils module
try:
    # Try relative import first (when used as package)
    from ..string_utils import (
        safe_format,
        safe_log_format,
        safe_print_format,
        multiline_format,
        build_device_info_string,
        build_progress_string,
        build_file_size_string,
        log_info_safe,
        log_error_safe,
        log_warning_safe,
        log_debug_safe,
        generate_sv_header_comment,
        generate_tcl_header_comment,
    )
except ImportError:
    # Fallback to absolute import (when used as script)
    import sys
    import os
    from pathlib import Path

    # Add the src directory to the path
    src_dir = Path(__file__).parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from string_utils import (
        safe_format,
        safe_log_format,
        safe_print_format,
        multiline_format,
        build_device_info_string,
        build_progress_string,
        build_file_size_string,
        log_info_safe,
        log_error_safe,
        log_warning_safe,
        log_debug_safe,
        generate_sv_header_comment,
        generate_tcl_header_comment,
    )

# Re-export all functions for local use
__all__ = [
    "safe_format",
    "safe_log_format",
    "safe_print_format",
    "multiline_format",
    "build_device_info_string",
    "build_progress_string",
    "build_file_size_string",
    "log_info_safe",
    "log_error_safe",
    "log_warning_safe",
    "log_debug_safe",
    "generate_sv_header_comment",
    "generate_tcl_header_comment",
]
