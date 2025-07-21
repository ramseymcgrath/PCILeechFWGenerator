#!/usr/bin/env python3
"""
MSI-X Capability Parser

This module provides functionality to parse MSI-X capability structures from
PCI configuration space and generate SystemVerilog code for MSI-X table replication.
"""

import struct
from typing import Any, Dict, List, Optional, Tuple

# Import project logging and string utilities
from ..log_config import get_logger
from ..string_utils import (
    log_debug_safe,
    log_error_safe,
    log_info_safe,
    log_warning_safe,
)

# Import template renderer
try:
    from ..templating.template_renderer import TemplateRenderer, TemplateRenderError
except ImportError:
    try:
        from templating.template_renderer import TemplateRenderer, TemplateRenderError
    except ImportError:
        from src.templating.template_renderer import (
            TemplateRenderer,
            TemplateRenderError,
        )

logger = get_logger(__name__)


def hex_to_bytes(hex_string: str) -> bytearray:
    """
    Convert hex string to bytearray for efficient byte-level operations.

    Args:
        hex_string: Configuration space as a hex string

    Returns:
        bytearray representation of the hex string
    """
    if len(hex_string) % 2 != 0:
        raise ValueError("Hex string must have even length")
    return bytearray.fromhex(hex_string)


def read_u8(data: bytearray, offset: int) -> int:
    """
    Read an 8-bit value from bytearray.

    Args:
        data: Byte data
        offset: Byte offset to read from

    Returns:
        8-bit unsigned integer value

    Raises:
        IndexError: If offset is out of bounds
    """
    return data[offset]


def read_u16_le(data: bytearray, offset: int) -> int:
    """
    Read a 16-bit little-endian value from bytearray.

    Args:
        data: Byte data
        offset: Byte offset to read from

    Returns:
        16-bit unsigned integer value

    Raises:
        struct.error: If offset is out of bounds
    """
    return struct.unpack_from("<H", data, offset)[0]


def read_u32_le(data: bytearray, offset: int) -> int:
    """
    Read a 32-bit little-endian value from bytearray.

    Args:
        data: Byte data
        offset: Byte offset to read from

    Returns:
        32-bit unsigned integer value

    Raises:
        struct.error: If offset is out of bounds
    """
    return struct.unpack_from("<I", data, offset)[0]


def is_valid_offset(data: bytearray, offset: int, size: int) -> bool:
    """
    Check if reading 'size' bytes from 'offset' is within bounds.

    Args:
        data: Byte data
        offset: Starting offset
        size: Number of bytes to read

    Returns:
        True if the read is within bounds
    """
    return offset + size <= len(data)


# TODO: Add support for PCIe extended capabilities (offset >= 0x100)


def find_cap(cfg: str, cap_id: int) -> Optional[int]:
    """
    Find a capability in the PCI configuration space.

    Args:
        cfg: Configuration space as a hex string
        cap_id: Capability ID to find (e.g., 0x11 for MSI-X)

    Returns:
        Offset of the capability in the configuration space, or None if not found
    """
    log_debug_safe(
        logger,
        "Searching for capability ID 0x{cap_id:02x} in configuration space",
        cap_id=cap_id,
    )
    log_debug_safe(
        logger, "Configuration space length: {length} characters", length=len(cfg)
    )

    # Check if configuration space is valid (minimum 256 bytes for basic config space)
    if not cfg or len(cfg) < 512:  # 256 bytes = 512 hex chars
        log_warning_safe(logger, "Configuration space is too small (need ≥256 bytes)")
        return None

    try:
        # Convert hex string to bytes for efficient processing
        cfg_bytes = hex_to_bytes(cfg)
    except ValueError as e:
        log_error_safe(
            logger, "Invalid hex string in configuration space: {error}", error=e
        )
        return None

    # Check if capabilities are supported (Status register bit 4)
    status_offset = 0x06
    if not is_valid_offset(cfg_bytes, status_offset, 2):
        log_warning_safe(logger, "Status register not found in configuration space")
        return None

    try:
        status = read_u16_le(cfg_bytes, status_offset)
        if not (status & 0x10):  # Check capabilities bit
            log_debug_safe(logger, "Device does not support capabilities")
            return None
    except struct.error:
        log_warning_safe(logger, "Failed to read status register")
        return None

    # Get capabilities pointer (offset 0x34)
    cap_ptr_offset = 0x34
    if not is_valid_offset(cfg_bytes, cap_ptr_offset, 1):
        log_warning_safe(
            logger, "Capabilities pointer not found in configuration space"
        )
        return None

    try:
        cap_ptr = read_u8(cfg_bytes, cap_ptr_offset)
        if cap_ptr == 0:
            log_debug_safe(logger, "No capabilities present")
            return None
    except IndexError:
        log_warning_safe(logger, "Failed to read capabilities pointer")
        return None

    # Walk the capabilities list
    current_ptr = cap_ptr
    visited = set()  # To detect loops

    while current_ptr and current_ptr != 0 and current_ptr not in visited:
        visited.add(current_ptr)

        # Ensure we have enough data for capability header (ID + next pointer)
        if not is_valid_offset(cfg_bytes, current_ptr, 2):
            log_warning_safe(
                logger,
                "Capability pointer 0x{current_ptr:02x} is out of bounds",
                current_ptr=current_ptr,
            )
            return None

        # Read capability ID and next pointer
        try:
            current_cap_id = read_u8(cfg_bytes, current_ptr)
            next_ptr = read_u8(cfg_bytes, current_ptr + 1)

            if current_cap_id == cap_id:
                return current_ptr

            current_ptr = next_ptr
        except IndexError:
            log_warning_safe(
                logger,
                "Invalid capability data at offset 0x{current_ptr:02x}",
                current_ptr=current_ptr,
            )
            return None

    log_debug_safe(logger, "Capability ID 0x{cap_id:02x} not found", cap_id=cap_id)
    return None


def msix_size(cfg: str) -> int:
    """
    Determine the MSI-X table size from the configuration space.

    Args:
        cfg: Configuration space as a hex string

    Returns:
        Number of MSI-X table entries, or 0 if MSI-X is not supported
    """
    # Find MSI-X capability (ID 0x11)
    cap = find_cap(cfg, 0x11)
    if cap is None:
        log_info_safe(logger, "MSI-X capability not found")
        return 0

    try:
        # Convert hex string to bytes for efficient processing
        cfg_bytes = hex_to_bytes(cfg)
    except ValueError as e:
        log_error_safe(
            logger, "Invalid hex string in configuration space: {error}", error=e
        )
        return 0

    # Read Message Control register (offset 2 from capability start)
    msg_ctrl_offset = cap + 2
    if not is_valid_offset(cfg_bytes, msg_ctrl_offset, 2):
        log_warning_safe(logger, "MSI-X Message Control register is out of bounds")
        return 0

    try:
        # Read 16-bit little-endian Message Control register
        msg_ctrl = read_u16_le(cfg_bytes, msg_ctrl_offset)

        # Table size is encoded in the lower 11 bits (Table Size field)
        table_size = (msg_ctrl & 0x7FF) + 1

        log_debug_safe(
            logger,
            "MSI-X table size: {table_size} entries (msg_ctrl=0x{msg_ctrl:04x})",
            table_size=table_size,
            msg_ctrl=msg_ctrl,
        )
        return table_size
    except struct.error:
        log_warning_safe(logger, "Failed to read MSI-X Message Control register")
        return 0


def parse_msix_capability(cfg: str) -> Dict[str, Any]:
    """
    Parse the MSI-X capability structure from the configuration space.

    Args:
        cfg: Configuration space as a hex string

    Returns:
        Dictionary containing MSI-X capability information:
        - table_size: Number of MSI-X table entries
        - table_bir: BAR indicator for the MSI-X table
        - table_offset: Offset of the MSI-X table in the BAR
        - pba_bir: BAR indicator for the PBA
        - pba_offset: Offset of the PBA in the BAR
        - enabled: Whether MSI-X is enabled
        - function_mask: Whether the function is masked
    """
    result = {
        "table_size": 0,
        "table_bir": 0,
        "table_offset": 0,
        "pba_bir": 0,
        "pba_offset": 0,
        "enabled": False,
        "function_mask": False,
    }
    # Find MSI-X capability (ID 0x11)
    cap = find_cap(cfg, 0x11)
    if cap is None:
        log_info_safe(logger, "MSI-X capability not found")
        return result
    log_debug_safe(logger, "MSI-X capability found at offset 0x{cap:02x}", cap=cap)
    try:
        # Convert hex string to bytes for efficient processing
        cfg_bytes = hex_to_bytes(cfg)
    except ValueError as e:
        log_error_safe(
            logger, "Invalid hex string in configuration space: {error}", error=e
        )
        return result

    # Read Message Control register (offset 2 from capability start)
    msg_ctrl_offset = cap + 2
    if not is_valid_offset(cfg_bytes, msg_ctrl_offset, 2):
        log_warning_safe(logger, "MSI-X Message Control register is out of bounds")
        return result

    try:
        # Read 16-bit little-endian Message Control register
        msg_ctrl = read_u16_le(cfg_bytes, msg_ctrl_offset)

        # Parse Message Control fields
        table_size = (msg_ctrl & 0x7FF) + 1  # Bits 10:0
        enabled = bool(msg_ctrl & 0x8000)  # Bit 15
        function_mask = bool(msg_ctrl & 0x4000)  # Bit 14

        # Read Table Offset/BIR register (offset 4 from capability start)
        table_offset_bir_offset = cap + 4
        if not is_valid_offset(cfg_bytes, table_offset_bir_offset, 4):
            log_warning_safe(logger, "MSI-X Table Offset/BIR register is out of bounds")
            return result

        table_offset_bir = read_u32_le(cfg_bytes, table_offset_bir_offset)
        table_bir = table_offset_bir & 0x7  # Lower 3 bits
        table_offset = (
            table_offset_bir & 0xFFFFFFF8
        )  # Clear lower 3 bits for 8-byte alignment

        # Read PBA Offset/BIR register (offset 8 from capability start)
        pba_offset_bir_offset = cap + 8
        if not is_valid_offset(cfg_bytes, pba_offset_bir_offset, 4):
            log_warning_safe(logger, "MSI-X PBA Offset/BIR register is out of bounds")
            return result

        pba_offset_bir = read_u32_le(cfg_bytes, pba_offset_bir_offset)
        pba_bir = pba_offset_bir & 0x7  # Lower 3 bits
        pba_offset = (
            pba_offset_bir & 0xFFFFFFF8
        )  # Clear lower 3 bits for 8-byte alignment

        # Update result
        result.update(
            {
                "table_size": table_size,
                "table_bir": table_bir,
                "table_offset": table_offset,
                "pba_bir": pba_bir,
                "pba_offset": pba_offset,
                "enabled": enabled,
                "function_mask": function_mask,
            }
        )

        log_info_safe(
            logger,
            "MSI-X capability found: {table_size} entries, "
            "table BIR {table_bir} offset 0x{table_offset:x}, "
            "PBA BIR {pba_bir} offset 0x{pba_offset:x}",
            table_size=table_size,
            table_bir=table_bir,
            table_offset=table_offset,
            pba_bir=pba_bir,
            pba_offset=pba_offset,
        )

        # Check for alignment warnings
        if table_offset_bir & 0x7 != 0:
            log_warning_safe(
                logger,
                "MSI-X table offset 0x{table_offset_bir:x} is not 8-byte aligned "
                "(actual offset: 0x{table_offset_bir:x}, aligned: 0x{table_offset:x})",
                table_offset_bir=table_offset_bir,
                table_offset=table_offset,
            )

        return result

    except struct.error as e:
        log_warning_safe(
            logger, "Error reading MSI-X capability registers: {error}", error=e
        )
        return result


def generate_msix_table_sv(msix_info: Dict[str, Any]) -> str:
    """
    Generate SystemVerilog code for the MSI-X table and PBA.

    Args:
        msix_info: Dictionary containing MSI-X capability information

    Returns:
        SystemVerilog code for the MSI-X table and PBA
    """
    if msix_info["table_size"] == 0:
        return "MSI-X not supported or no entries"
    log_debug_safe(
        logger, "MSI-X: Found, generating SystemVerilog code for MSI-X table"
    )

    table_size = msix_info["table_size"]
    pba_size = (table_size + 31) // 32  # Number of 32-bit words needed for PBA

    # Generate alignment warning if needed
    alignment_warning = ""
    if msix_info["table_offset"] % 8 != 0:
        alignment_warning = f"// Warning: MSI-X table offset 0x{msix_info['table_offset']:x} is not 8-byte aligned"

    # Prepare template context
    context = {
        "table_size": table_size,
        "table_bir": msix_info["table_bir"],
        "table_offset": msix_info["table_offset"],
        "pba_bir": msix_info["pba_bir"],
        "pba_offset": msix_info["pba_offset"],
        "enabled_val": 1 if msix_info["enabled"] else 0,
        "function_mask_val": 1 if msix_info["function_mask"] else 0,
        "pba_size": pba_size,
        "pba_size_minus_one": pba_size - 1,
        "alignment_warning": alignment_warning,
    }

    # Use template renderer
    renderer = TemplateRenderer()
    main_template = renderer.render_template(
        "systemverilog/msix_implementation.sv.j2", context
    )
    capability_registers = generate_msix_capability_registers(msix_info)
    return main_template + "\n" + capability_registers


def validate_msix_configuration(msix_info: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate MSI-X configuration for correctness and compliance.

    Args:
        msix_info: Dictionary containing MSI-X capability information

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check table size validity
    table_size = msix_info.get("table_size", 0)
    if table_size == 0:
        errors.append("MSI-X table size is zero")
    elif table_size > 2048:  # PCIe spec maximum
        errors.append(f"MSI-X table size {table_size} exceeds maximum of 2048")

    # Check BIR validity (must be 0-5 for standard BARs)
    table_bir = msix_info.get("table_bir", 0)
    pba_bir = msix_info.get("pba_bir", 0)

    if table_bir > 5:
        errors.append(f"MSI-X table BIR {table_bir} is invalid (must be 0-5)")
    if pba_bir > 5:
        errors.append(f"MSI-X PBA BIR {pba_bir} is invalid (must be 0-5)")

    # Check alignment requirements
    table_offset = msix_info.get("table_offset", 0)
    pba_offset = msix_info.get("pba_offset", 0)

    if table_offset % 8 != 0:
        errors.append(f"MSI-X table offset 0x{table_offset:x} is not 8-byte aligned")
    if pba_offset % 8 != 0:
        errors.append(f"MSI-X PBA offset 0x{pba_offset:x} is not 8-byte aligned")

    # Check for overlap if table and PBA are in the same BAR
    if table_bir == pba_bir:
        table_end = table_offset + (table_size * 16)  # 16 bytes per entry
        pba_size = (
            (table_size + 31) // 32
        ) * 4  # PBA size in bytes (parenthesized for clarity)
        pba_end = pba_offset + pba_size

        # TODO: Enhance overlap detection for 64-bit BARs
        # Current implementation assumes 32-bit addresses; for 64-bit BARs above 4GiB,
        # we would need to parse BAR size bits and handle 64-bit math properly

        if table_offset < pba_end and table_end > pba_offset:
            errors.append("MSI-X table and PBA overlap in the same BAR")

    is_valid = len(errors) == 0
    return is_valid, errors


def generate_msix_capability_registers(msix_info: Dict[str, Any]) -> str:
    """
    Generate SystemVerilog code for MSI-X capability register handling.

    Args:
        msix_info: Dictionary containing MSI-X capability information

    Returns:
        SystemVerilog code for MSI-X capability register management
    """
    if msix_info["table_size"] == 0:
        return "// MSI-X capability registers not generated - no MSI-X support"

    table_size = msix_info["table_size"]

    # Prepare template context
    context = {
        "table_size_minus_one": table_size - 1,
        "table_offset_bir": f"32'h{(msix_info['table_offset'] | msix_info['table_bir']):08X}",
        "pba_offset_bir": f"32'h{(msix_info['pba_offset'] | msix_info['pba_bir']):08X}",
    }

    # Use template renderer
    renderer = TemplateRenderer()
    return renderer.render_template(
        "systemverilog/msix_capability_registers.sv.j2", context
    )


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python msix_capability.py <config_space_hex_file>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        config_space = f.read().strip()

    msix_info = parse_msix_capability(config_space)
    print(f"MSI-X Table Size: {msix_info['table_size']}")
    print(f"MSI-X Table BIR: {msix_info['table_bir']}")
    print(f"MSI-X Table Offset: 0x{msix_info['table_offset']:x}")
    print(f"MSI-X PBA BIR: {msix_info['pba_bir']}")
    print(f"MSI-X PBA Offset: 0x{msix_info['pba_offset']:x}")
    print(f"MSI-X Enabled: {msix_info['enabled']}")
    print(f"MSI-X Function Mask: {msix_info['function_mask']}")

    sv_code = generate_msix_table_sv(msix_info)
    print("\nSystemVerilog Code:")
    print(sv_code)
