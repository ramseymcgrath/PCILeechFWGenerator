#!/usr/bin/env python3
"""
String utilities for safe formatting operations.

This module provides utilities to handle complex string formatting
operations safely, particularly for multi-line f-strings that can
cause syntax errors when split across lines.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional


def safe_format(template: str, prefix: Optional[str] = None, **kwargs: Any) -> str:
    """
    Safely format a string template with the given keyword arguments.

    This function provides a safe alternative to f-strings when dealing
    with complex multi-line formatting that might cause syntax errors.

    Args:
        template: The string template with {variable} placeholders
        prefix: Optional prefix to add to the formatted message
        **kwargs: Keyword arguments to substitute in the template

    Returns:
        The formatted string with all placeholders replaced

    Example:
        >>> safe_format("Hello {name}, you have {count} messages",
        ...             name="Alice", count=5)
        'Hello Alice, you have 5 messages'

        >>> safe_format(
        ...     "Device {bdf} with VID:{vid:04x} DID:{did:04x}",
        ...     bdf="0000:00:1f.3", vid=0x8086, did=0x54c8
        ... )
        'Device 0000:00:1f.3 with VID:8086 DID:54c8'

        >>> safe_format("Processing device {bdf}", prefix="VFIO", bdf="0000:01:00.0")
        '[VFIO] Processing device 0000:01:00.0'
    """
    try:
        formatted_message = template.format(**kwargs)
        if prefix:
            return f"[{prefix}] {formatted_message}"
        return formatted_message
    except KeyError as e:
        # Handle missing keys gracefully
        missing_key = str(e).strip("'\"")
        logging.warning(f"Missing key '{missing_key}' in string template")
        formatted_message = template.replace(
            f"{{{missing_key}}}", f"<MISSING:{missing_key}>"
        )
        if prefix:
            return f"[{prefix}] {formatted_message}"
        return formatted_message
    except ValueError as e:
        # Handle format specification errors
        logging.error(f"Format error in string template: {e}")
        if prefix:
            return f"[{prefix}] {template}"
        return template
    except Exception as e:
        # Handle any other unexpected errors
        logging.error(f"Unexpected error in safe_format: {e}")
        if prefix:
            return f"[{prefix}] {template}"
        return template


def safe_log_format(
    logger: logging.Logger,
    log_level: int,
    template: str,
    prefix: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Safely log a formatted message with padding and short timestamps.

    Args:
        logger: The logger instance to use
        log_level: The logging level (e.g., logging.INFO, logging.ERROR)
        template: The string template with {variable} placeholders
        prefix: Optional prefix to add to the log message (e.g., "VFIO", "BUILD")
        **kwargs: Keyword arguments to substitute in the template

    Example:
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> safe_log_format(logger, logging.INFO,
        ...                  "Processing device {bdf} with {bytes} bytes",
        ...                  prefix="VFIO", bdf="0000:00:1f.3", bytes=256)
    """
    try:
        formatted_message = safe_format(template, prefix=prefix, **kwargs)

        # Map log level to string
        level_map = {
            logging.INFO: "INFO",
            logging.WARNING: "WARNING",
            logging.DEBUG: "DEBUG",
            logging.ERROR: "ERROR",
            logging.CRITICAL: "CRITICAL",
        }
        level_str = level_map.get(log_level, "UNKNOWN")

        padded_message = format_padded_message(formatted_message, level_str)
        logger.log(log_level, padded_message)
    except Exception as e:
        # Fallback to basic logging if formatting fails
        error_msg = f"Failed to format log message: {e}"
        padded_error = format_padded_message(error_msg, "ERROR")
        logger.error(padded_error)

        fallback_message = f"Original template: {template}"
        if prefix:
            fallback_message = f"[{prefix}] {fallback_message}"
        padded_fallback = format_padded_message(fallback_message, "ERROR")
        logger.log(log_level, padded_fallback)


def safe_print_format(template: str, prefix: str, **kwargs: Any) -> None:
    """
    Safely print a formatted message with padding and short timestamp.

    Args:
        template: The string template with {variable} placeholders
        prefix: Optional prefix to add to the message
        **kwargs: Keyword arguments to substitute in the template

    Example:
        >>> safe_print_format("Build completed in {time:.2f} seconds",
        ...                   prefix="BUILD", time=45.67)
        14:23:45 │  INFO  │ [BUILD] Build completed in 45.67 seconds
    """
    try:
        formatted_message = safe_format(template=template, prefix=prefix, **kwargs)
        padded_message = format_padded_message(formatted_message, "INFO")
        print(padded_message)
    except Exception as e:
        error_msg = f"Failed to format message: {e}"
        padded_error = format_padded_message(error_msg, "ERROR")
        print(padded_error)

        fallback_msg = f"Original template: {template}"
        padded_fallback = format_padded_message(fallback_msg, "ERROR")
        print(padded_fallback)


def multiline_format(template: str, prefix: str, **kwargs: Any) -> str:
    """
    Format a multi-line string template safely.

    This is particularly useful for complex multi-line strings that
    would be difficult to handle with f-strings.

    Args:
        template: Multi-line string template with {variable} placeholders
        **kwargs: Keyword arguments to substitute in the template

    Returns:
        The formatted multi-line string

    Example:
        >>> template = '''
        ... Device Information:
        ...   BDF: {bdf}
        ...   Vendor ID: {vid:04x}
        ...   Device ID: {did:04x}
        ...   Driver: {driver}
        ... '''
        >>> result = multiline_format(template.strip(),
        ...                          bdf="0000:00:1f.3", vid=0x8086,
        ...                          did=0x54c8, driver="snd_hda_intel")
    """
    return safe_format(template, prefix=prefix, **kwargs)


def build_device_info_string(device_info: Dict[str, Any]) -> str:
    """
    Build a standardized device information string.

    Args:
        device_info: Dictionary containing device information

    Returns:
        Formatted device information string
    """
    template = "VID:{vendor_id:04x}, DID:{device_id:04x}"

    # Add optional fields if present
    if "class_code" in device_info:
        template += ", Class:{class_code:04x}"
    if "subsystem_vendor_id" in device_info:
        template += ", SVID:{subsystem_vendor_id:04x}"
    if "subsystem_device_id" in device_info:
        template += ", SDID:{subsystem_device_id:04x}"

    return safe_format(template, **device_info)


def build_progress_string(
    operation: str, current: int, total: int, elapsed_time: Optional[float] = None
) -> str:
    """
    Build a standardized progress string.

    Args:
        operation: Description of the current operation
        current: Current progress value
        total: Total expected value
        elapsed_time: Optional elapsed time in seconds

    Returns:
        Formatted progress string
    """
    percentage = (current / total * 100) if total > 0 else 0
    template = "{operation}: {current}/{total} ({percentage:.1f}%)"

    if elapsed_time is not None:
        template += " - {elapsed_time:.1f}s elapsed"

    return safe_format(
        template,
        prefix="Progress",
        operation=operation,
        current=current,
        total=total,
        percentage=percentage,
        elapsed_time=elapsed_time,
    )


def build_file_size_string(size_bytes: int) -> str:
    """
    Build a human-readable file size string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB", "256 KB")
    """
    if size_bytes < 1024:
        return safe_format("{size} bytes", prefix="File Size", size=size_bytes)
    elif size_bytes < 1024 * 1024:
        size_kb = size_bytes / 1024
        return safe_format(
            "{size:.1f} KB ({bytes} bytes)",
            prefix="File Size",
            size=size_kb,
            bytes=size_bytes,
        )
    else:
        size_mb = size_bytes / (1024 * 1024)
        return safe_format(
            "{size:.1f} MB ({bytes} bytes)",
            prefix="File Size",
            size=size_mb,
            bytes=size_bytes,
        )


def get_short_timestamp() -> str:
    """
    Get a short timestamp string for logging.

    Returns:
        Short timestamp in format HH:MM:SS

    Example:
        >>> get_short_timestamp()
        '14:23:45'
    """
    return datetime.now().strftime("%H:%M:%S")


def format_padded_message(message: str, log_level: str) -> str:
    """
    Format a message with padding based on log level.

    Args:
        message: The message to format
        log_level: The log level (INFO, WARNING, DEBUG, ERROR)

    Returns:
        Formatted message with appropriate padding

    Example:
        >>> format_padded_message("Device found", "INFO")
        '  INFO  │ Device found'
        >>> format_padded_message("Memory issue", "WARNING")
        ' WARNING│ Memory issue'
    """
    timestamp = get_short_timestamp()

    if log_level == "INFO":
        return f"  {timestamp} │  INFO  │ {message}"
    elif log_level == "WARNING":
        return f"  {timestamp} │ WARNING│ {message}"
    elif log_level == "DEBUG":
        return f"  {timestamp} │ DEBUG  │ {message}"
    elif log_level == "ERROR":
        return f"  {timestamp} │ ERROR  │ {message}"
    else:
        return f"  {timestamp} │ {log_level:>7}│ {message}"


# Convenience functions for common logging patterns
def log_info_safe(
    logger: logging.Logger, template: str, prefix: Optional[str] = None, **kwargs: Any
) -> None:
    """Convenience function for safe INFO level logging with padding."""
    formatted_message = safe_format(template, prefix=prefix, **kwargs)
    padded_message = format_padded_message(formatted_message, "INFO")
    logger.info(padded_message)


def log_error_safe(
    logger: logging.Logger, template: str, prefix: Optional[str] = None, **kwargs: Any
) -> None:
    """Convenience function for safe ERROR level logging with padding."""
    formatted_message = safe_format(template, prefix=prefix, **kwargs)
    padded_message = format_padded_message(formatted_message, "ERROR")
    logger.error(padded_message)


def log_warning_safe(
    logger: logging.Logger, template: str, prefix: Optional[str] = None, **kwargs: Any
) -> None:
    """Convenience function for safe WARNING level logging with padding."""
    formatted_message = safe_format(template, prefix=prefix, **kwargs)
    padded_message = format_padded_message(formatted_message, "WARNING")
    logger.warning(padded_message)


def log_debug_safe(
    logger: logging.Logger, template: str, prefix: Optional[str] = None, **kwargs: Any
) -> None:
    """Convenience function for safe DEBUG level logging with padding."""
    formatted_message = safe_format(template, prefix=prefix, **kwargs)
    padded_message = format_padded_message(formatted_message, "DEBUG")
    logger.debug(padded_message)


def generate_sv_header_comment(
    title: str,
    vendor_id: Optional[str] = None,
    device_id: Optional[str] = None,
    board: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """
    Generate a standardized SystemVerilog header comment block.

    This function creates a consistent header format used across SystemVerilog
    modules with device-specific information.

    Args:
        title: The main title/description for the module
        vendor_id: Optional vendor ID (will be included if provided)
        device_id: Optional device ID (will be included if provided)
        board: Optional board name (will be included if provided)
        **kwargs: Additional key-value pairs to include in the header

    Returns:
        Formatted SystemVerilog header comment block

    Example:
        >>> generate_sv_header_comment(
        ...     "Device Configuration Module",
        ...     vendor_id="1234", device_id="5678", board="AC701"
        ... )
        '//==============================================================================\\n// Device Configuration Module - Generated for 1234:5678\\n// Board: AC701\\n//=============================================================================='

        >>> generate_sv_header_comment("PCIe Controller Module")
        '//==============================================================================\\n// PCIe Controller Module\\n//=============================================================================='
    """
    lines = [
        "//=============================================================================="
    ]

    # Build the main title line
    if vendor_id and device_id:
        title_line = f"// {title} - Generated for {vendor_id}:{device_id}"
    else:
        title_line = f"// {title}"
    lines.append(title_line)

    # Add board information if provided
    if board:
        lines.append(f"// Board: {board}")

    # Add any additional key-value pairs
    for key, value in kwargs.items():
        if value is not None:
            # Convert key from snake_case to Title Case for display
            display_key = key.replace("_", " ").title()
            lines.append(f"// {display_key}: {value}")

    lines.append(
        "//=============================================================================="
    )

    return "\n".join(lines)


def generate_tcl_header_comment(
    title: str,
    vendor_id: Optional[str] = None,
    device_id: Optional[str] = None,
    class_code: Optional[str] = None,
    board: Optional[str] = None,
    fpga_part: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """
    Generate a standardized TCL header comment block.

    This function creates a consistent header format used across TCL build scripts
    with device-specific information.

    Args:
        title: The main title/description for the script
        vendor_id: Optional vendor ID (will be included if provided)
        device_id: Optional device ID (will be included if provided)
        class_code: Optional class code (will be included if provided)
        board: Optional board name (will be included if provided)
        fpga_part: Optional FPGA part number (will be included if provided)
        **kwargs: Additional key-value pairs to include in the header

    Returns:
        Formatted TCL header comment block

    Example:
        >>> generate_tcl_header_comment(
        ...     "PCILeech Firmware Build Script",
        ...     vendor_id="1234", device_id="5678",
        ...     class_code="0200", board="AC701"
        ... )
        '#==============================================================================\\n# PCILeech Firmware Build Script\\n# Generated for device 1234:5678 (Class: 0200)\\n# Board: AC701\\n#=============================================================================='
    """
    lines = [
        "#=============================================================================="
    ]

    # Build the main title line
    lines.append(f"# {title}")

    # Add device information if provided
    if vendor_id and device_id:
        device_line = f"# Generated for device {vendor_id}:{device_id}"
        if class_code:
            device_line += f" (Class: {class_code})"
        lines.append(device_line)

    # Add board information if provided
    if board:
        lines.append(f"# Board: {board}")

    # Add FPGA part information if provided
    if fpga_part:
        lines.append(f"# FPGA Part: {fpga_part}")

    # Add any additional key-value pairs
    for key, value in kwargs.items():
        if value is not None:
            # Convert key from snake_case to Title Case for display
            display_key = key.replace("_", " ").title()
            lines.append(f"# {display_key}: {value}")

    lines.append(
        "#=============================================================================="
    )

    return "\n".join(lines)


def format_bar_table(bar_configs: List[Any], primary_bar: Any = None) -> str:
    """
    Format BAR configuration data into a nice ASCII table.

    Args:
        bar_configs: List of BarConfiguration objects
        primary_bar: Optional primary BAR to highlight

    Returns:
        Formatted ASCII table string
    """
    if not bar_configs:
        return "No BAR configurations found"

    # Table headers
    headers = [
        "BAR",
        "Address",
        "Size",
        "Size (MB)",
        "Type",
        "Prefetch",
        "Memory",
        "Candidate",
        "Primary",
    ]

    # Calculate column widths
    col_widths = [len(h) for h in headers]

    # Prepare data rows
    rows = []
    for bar_info in bar_configs:
        is_candidate = bar_info.is_memory and bar_info.size > 0
        is_primary = primary_bar and bar_info.index == primary_bar.index

        size_mb = bar_info.size / (1024 * 1024) if bar_info.size > 0 else 0

        row = [
            str(bar_info.index),
            f"0x{bar_info.base_address:08X}",
            f"{bar_info.size:,}",
            f"{size_mb:.2f}" if size_mb > 0 else "0.00",
            "memory" if bar_info.is_memory else "io",
            "yes" if bar_info.prefetchable else "no",
            "yes" if bar_info.is_memory else "no",
            "yes" if is_candidate else "no",
            "★" if is_primary else "",
        ]
        rows.append(row)

        # Update column widths
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Build the table
    lines = []

    # Top border
    border = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    lines.append(border)

    # Header row
    header_row = (
        "│"
        + "│".join(f" {headers[i]:<{col_widths[i]}} " for i in range(len(headers)))
        + "│"
    )
    lines.append(header_row)

    # Header separator
    separator = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    lines.append(separator)

    # Data rows
    for row in rows:
        data_row = (
            "│"
            + "│".join(f" {row[i]:<{col_widths[i]}} " for i in range(len(row)))
            + "│"
        )
        lines.append(data_row)

    # Bottom border
    bottom_border = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
    lines.append(bottom_border)

    return "\n".join(lines)


def format_bar_summary_table(bar_configs: List[Any], primary_bar: Any = None) -> str:
    """
    Format a compact BAR summary table showing only essential information.

    Args:
        bar_configs: List of BarConfiguration objects
        primary_bar: Optional primary BAR to highlight

    Returns:
        Formatted ASCII table string
    """
    if not bar_configs:
        return "No BAR configurations found"

    # Table headers for summary
    headers = ["BAR", "Address", "Size (MB)", "Type", "Status"]

    # Calculate column widths
    col_widths = [len(h) for h in headers]

    # Prepare data rows
    rows = []
    for bar_info in bar_configs:
        is_candidate = bar_info.is_memory and bar_info.size > 0
        is_primary = primary_bar and bar_info.index == primary_bar.index

        size_mb = bar_info.size / (1024 * 1024) if bar_info.size > 0 else 0

        # Determine status
        if is_primary:
            status = "PRIMARY ★"
        elif is_candidate:
            status = "candidate"
        elif bar_info.size == 0:
            status = "empty"
        elif not bar_info.is_memory:
            status = "I/O port"
        else:
            status = "skipped"

        row = [
            str(bar_info.index),
            f"0x{bar_info.base_address:08X}",
            f"{size_mb:.2f}" if size_mb > 0 else "0.00",
            "memory" if bar_info.is_memory else "io",
            status,
        ]
        rows.append(row)

        # Update column widths
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Build the table
    lines = []

    # Top border
    border = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    lines.append(border)

    # Header row
    header_row = (
        "│"
        + "│".join(f" {headers[i]:<{col_widths[i]}} " for i in range(len(headers)))
        + "│"
    )
    lines.append(header_row)

    # Header separator
    separator = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    lines.append(separator)

    # Data rows
    for row in rows:
        data_row = (
            "│"
            + "│".join(f" {row[i]:<{col_widths[i]}} " for i in range(len(row)))
            + "│"
        )
        lines.append(data_row)

    # Bottom border
    bottom_border = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
    lines.append(bottom_border)

    return "\n".join(lines)


def format_raw_bar_table(bars: List[Any], device_bdf: str) -> str:
    """
    Format raw BAR data from config space into a nice ASCII table.

    Args:
        bars: List of raw BAR data (dict or int values)
        device_bdf: Device BDF for context

    Returns:
        Formatted ASCII table string
    """
    if not bars:
        return "No BAR data found"

    # Table headers
    headers = ["BAR", "Type", "Address", "Size", "Prefetchable", "64-bit"]

    # Calculate column widths
    col_widths = [len(h) for h in headers]

    # Prepare data rows
    rows = []
    for i, bar_data in enumerate(bars[:6]):  # Only show first 6 BARs
        if isinstance(bar_data, dict):
            row = [
                str(i),
                bar_data.get("type", "unknown"),
                f"0x{bar_data.get('address', 0):08X}",
                str(bar_data.get("size", 0)),
                "Yes" if bar_data.get("prefetchable", False) else "No",
                "Yes" if bar_data.get("is_64bit", False) else "No",
            ]
        else:
            # Simple address value
            row = [
                str(i),
                "unknown",
                f"0x{bar_data:08X}",
                "unknown",
                "unknown",
                "unknown",
            ]

        rows.append(row)

        # Update column widths
        for j, cell in enumerate(row):
            col_widths[j] = max(col_widths[j], len(cell))

    # Build the table
    lines = []

    # Top border
    top_border = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    lines.append(top_border)

    # Header row
    header_row = (
        "│"
        + "│".join(f" {headers[i]:<{col_widths[i]}} " for i in range(len(headers)))
        + "│"
    )
    lines.append(header_row)

    # Header separator
    header_sep = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    lines.append(header_sep)

    # Data rows
    for row in rows:
        data_row = (
            "│"
            + "│".join(f" {row[i]:<{col_widths[i]}} " for i in range(len(row)))
            + "│"
        )
        lines.append(data_row)

    # Bottom border
    bottom_border = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
    lines.append(bottom_border)

    return "\n".join(lines)
