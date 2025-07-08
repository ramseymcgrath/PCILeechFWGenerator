#!/usr/bin/env python3
"""
String utilities for device_clone module.

This module provides a local import path for string utilities within the device_clone
package, importing from the main string_utils module.
"""

# Import all functions from the main string_utils module
# Import from parent module
from ..string_utils import (
    build_device_info_string,
    build_file_size_string,
    build_progress_string,
    generate_sv_header_comment,
    generate_tcl_header_comment,
    log_debug_safe,
    log_error_safe,
    log_info_safe,
    log_warning_safe,
    multiline_format,
    safe_format,
    safe_log_format,
    safe_print_format,
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
