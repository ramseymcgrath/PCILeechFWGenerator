#!/usr/bin/env python3
"""
MSI-X Capability Parser

This module provides functionality to parse MSI-X capability structures from
PCI configuration space and generate SystemVerilog code for MSI-X table replication.
"""

import logging
import struct
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


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


def find_cap(cfg: str, cap_id: int) -> Optional[int]:
    """
    Find a capability in the PCI configuration space.

    Args:
        cfg: Configuration space as a hex string
        cap_id: Capability ID to find (e.g., 0x11 for MSI-X)

    Returns:
        Offset of the capability in the configuration space, or None if not found
    """
    # Check if configuration space is valid (minimum 128 bytes for basic config space)
    if not cfg or len(cfg) < 256:
        logger.warning("Configuration space is too small or invalid")
        return None

    try:
        # Convert hex string to bytes for efficient processing
        cfg_bytes = hex_to_bytes(cfg)
    except ValueError as e:
        logger.error(f"Invalid hex string in configuration space: {e}")
        return None

    # Check if capabilities are supported (Status register bit 4)
    status_offset = 0x06
    if not is_valid_offset(cfg_bytes, status_offset, 2):
        logger.warning("Status register not found in configuration space")
        return None

    try:
        status = read_u16_le(cfg_bytes, status_offset)
        if not (status & 0x10):  # Check capabilities bit
            logger.debug("Device does not support capabilities")
            return None
    except struct.error:
        logger.warning("Failed to read status register")
        return None

    # Get capabilities pointer (offset 0x34)
    cap_ptr_offset = 0x34
    if not is_valid_offset(cfg_bytes, cap_ptr_offset, 1):
        logger.warning("Capabilities pointer not found in configuration space")
        return None

    try:
        cap_ptr = cfg_bytes[cap_ptr_offset]
        if cap_ptr == 0:
            logger.debug("No capabilities present")
            return None
    except IndexError:
        logger.warning("Failed to read capabilities pointer")
        return None

    # Walk the capabilities list
    current_ptr = cap_ptr
    visited = set()  # To detect loops

    while current_ptr and current_ptr != 0 and current_ptr not in visited:
        visited.add(current_ptr)

        # Ensure we have enough data for capability header (ID + next pointer)
        if not is_valid_offset(cfg_bytes, current_ptr, 2):
            logger.warning(f"Capability pointer 0x{current_ptr:02x} is out of bounds")
            return None

        # Read capability ID and next pointer
        try:
            current_cap_id = cfg_bytes[current_ptr]
            next_ptr = cfg_bytes[current_ptr + 1]

            if current_cap_id == cap_id:
                return current_ptr

            current_ptr = next_ptr
        except IndexError:
            logger.warning(f"Invalid capability data at offset 0x{current_ptr:02x}")
            return None

    logger.debug(f"Capability ID 0x{cap_id:02x} not found")
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
        logger.debug("MSI-X capability not found")
        return 0

    try:
        # Convert hex string to bytes for efficient processing
        cfg_bytes = hex_to_bytes(cfg)
    except ValueError as e:
        logger.error(f"Invalid hex string in configuration space: {e}")
        return 0

    # Read Message Control register (offset 2 from capability start)
    msg_ctrl_offset = cap + 2
    if not is_valid_offset(cfg_bytes, msg_ctrl_offset, 2):
        logger.warning("MSI-X Message Control register is out of bounds")
        return 0

    try:
        # Read 16-bit little-endian Message Control register
        msg_ctrl = read_u16_le(cfg_bytes, msg_ctrl_offset)

        # Table size is encoded in the lower 11 bits (Table Size field)
        table_size = (msg_ctrl & 0x7FF) + 1

        logger.debug(
            f"MSI-X table size: {table_size} entries (msg_ctrl=0x{msg_ctrl:04x})"
        )
        return table_size
    except struct.error:
        logger.warning("Failed to read MSI-X Message Control register")
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
        logger.debug("MSI-X capability not found")
        return result

    try:
        # Convert hex string to bytes for efficient processing
        cfg_bytes = hex_to_bytes(cfg)
    except ValueError as e:
        logger.error(f"Invalid hex string in configuration space: {e}")
        return result

    # Read Message Control register (offset 2 from capability start)
    msg_ctrl_offset = cap + 2
    if not is_valid_offset(cfg_bytes, msg_ctrl_offset, 2):
        logger.warning("MSI-X Message Control register is out of bounds")
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
            logger.warning("MSI-X Table Offset/BIR register is out of bounds")
            return result

        table_offset_bir = read_u32_le(cfg_bytes, table_offset_bir_offset)
        table_bir = table_offset_bir & 0x7  # Lower 3 bits
        table_offset = (
            table_offset_bir & ~0x7
        )  # Clear lower 3 bits for 8-byte alignment

        # Read PBA Offset/BIR register (offset 8 from capability start)
        pba_offset_bir_offset = cap + 8
        if not is_valid_offset(cfg_bytes, pba_offset_bir_offset, 4):
            logger.warning("MSI-X PBA Offset/BIR register is out of bounds")
            return result

        pba_offset_bir = read_u32_le(cfg_bytes, pba_offset_bir_offset)
        pba_bir = pba_offset_bir & 0x7  # Lower 3 bits
        pba_offset = pba_offset_bir & ~0x7  # Clear lower 3 bits for 8-byte alignment

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

        logger.info(
            f"MSI-X capability found: {table_size} entries, "
            f"table BIR {table_bir} offset 0x{table_offset:x}, "
            f"PBA BIR {pba_bir} offset 0x{pba_offset:x}"
        )

        # Check for alignment warnings
        if table_offset_bir & 0x7 != 0:
            logger.warning(
                f"MSI-X table offset 0x{table_offset_bir:x} is not 8-byte aligned "
                f"(actual offset: 0x{table_offset_bir:x}, aligned: 0x{table_offset:x})"
            )

        return result

    except struct.error as e:
        logger.warning(f"Error reading MSI-X capability registers: {e}")
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
        return "// MSI-X not supported or no entries"

    table_size = msix_info["table_size"]
    pba_size = (table_size + 31) // 32  # Number of 32-bit words needed for PBA

    # Generate alignment warning if needed
    alignment_warning = ""
    if msix_info["table_offset"] % 8 != 0:
        alignment_warning = f"// Warning: MSI-X table offset 0x{msix_info['table_offset']:x} is not 8-byte aligned"

    # Template for SystemVerilog code
    sv_template = """
// MSI-X Table and PBA implementation
// Table size: {table_size} entries
// Table BIR: {table_bir}
// Table offset: 0x{table_offset:x}
// PBA BIR: {pba_bir}
// PBA offset: 0x{pba_offset:x}

// MSI-X Table parameters
localparam NUM_MSIX = {table_size};
localparam MSIX_TABLE_BIR = {table_bir};
localparam MSIX_TABLE_OFFSET = 32'h{table_offset:X};
localparam MSIX_PBA_BIR = {pba_bir};
localparam MSIX_PBA_OFFSET = 32'h{pba_offset:X};
localparam MSIX_ENABLED = {enabled_val};
localparam MSIX_FUNCTION_MASK = {function_mask_val};
localparam PBA_SIZE = {pba_size};  // Number of 32-bit words needed for PBA

{alignment_warning}

// MSI-X Table storage
(* ram_style="block" *) reg [31:0] msix_table[0:NUM_MSIX*4-1];  // 4 DWORDs per entry

// MSI-X PBA storage
reg [31:0] msix_pba[0:{pba_size_minus_one}];

// MSI-X control registers - connected to configuration space capability registers
// These signals should be driven by the actual MSI-X capability registers in config space
// rather than being hardcoded values
wire msix_enabled;        // Connected to MSI-X Message Control Enable bit
wire msix_function_mask;  // Connected to MSI-X Message Control Function Mask bit

// MSI-X Table access logic
function logic is_msix_table_access(input logic [31:0] addr, input logic [2:0] bar_index);
    return (bar_index == MSIX_TABLE_BIR) &&
           (addr >= MSIX_TABLE_OFFSET) &&
           (addr < (MSIX_TABLE_OFFSET + NUM_MSIX * 16));
endfunction

// MSI-X PBA access logic
function logic is_msix_pba_access(input logic [31:0] addr, input logic [2:0] bar_index);
    return (bar_index == MSIX_PBA_BIR) &&
           (addr >= MSIX_PBA_OFFSET) &&
           (addr < (MSIX_PBA_OFFSET + {pba_size} * 4));
endfunction

// MSI-X Table read logic
function logic [31:0] msix_table_read(input logic [31:0] addr);
    logic [31:0] table_addr;
    table_addr = (addr - MSIX_TABLE_OFFSET) >> 2;  // Convert to DWORD index
    return msix_table[table_addr];
endfunction

// MSI-X Table write logic with byte enables
task msix_table_write(input logic [31:0] addr, input logic [31:0] data, input logic [3:0] byte_enable);
    logic [31:0] table_addr;
    logic [31:0] current_value;

    table_addr = (addr - MSIX_TABLE_OFFSET) >> 2;  // Convert to DWORD index
    current_value = msix_table[table_addr];

    // Apply byte enables
    if (byte_enable[0]) current_value[7:0] = data[7:0];
    if (byte_enable[1]) current_value[15:8] = data[15:8];
    if (byte_enable[2]) current_value[23:16] = data[23:16];
    if (byte_enable[3]) current_value[31:24] = data[31:24];

    msix_table[table_addr] = current_value;
endtask

// MSI-X PBA read logic
function logic [31:0] msix_pba_read(input logic [31:0] addr);
    logic [31:0] pba_addr;
    pba_addr = (addr - MSIX_PBA_OFFSET) >> 2;  // Convert to DWORD index
    return msix_pba[pba_addr];
endfunction

// MSI-X PBA write logic (typically read-only, but implemented for completeness)
task msix_pba_write(input logic [31:0] addr, input logic [31:0] data, input logic [3:0] byte_enable);
    logic [31:0] pba_addr;
    logic [31:0] current_value;

    pba_addr = (addr - MSIX_PBA_OFFSET) >> 2;  // Convert to DWORD index
    current_value = msix_pba[pba_addr];

    // Apply byte enables
    if (byte_enable[0]) current_value[7:0] = data[7:0];
    if (byte_enable[1]) current_value[15:8] = data[15:8];
    if (byte_enable[2]) current_value[23:16] = data[23:16];
    if (byte_enable[3]) current_value[31:24] = data[31:24];

    msix_pba[pba_addr] = current_value;
endtask

// MSI-X interrupt delivery logic
task msix_deliver_interrupt(input logic [10:0] vector);
    logic vector_masked;
    logic [31:0] table_addr;
    logic [31:0] control_dword;
    logic [31:0] pba_dword;
    logic [4:0] pba_bit;

    // Check if vector is valid
    if (vector >= NUM_MSIX) return;

    // Get control DWORD (third DWORD in the entry)
    table_addr = vector * 4 + 3;
    control_dword = msix_table[table_addr];

    // Check if vector is masked
    vector_masked = control_dword[0];

    if (msix_enabled && !msix_function_mask && !vector_masked) begin
        // Vector is enabled and not masked - deliver interrupt
        // Generate MSI-X message according to PCIe specification
        logic [63:0] message_address;
        logic [31:0] message_data;

        // Extract message address from MSI-X table entry (first two DWORDs)
        message_address[31:0] = msix_table[vector * 4];      // Lower address DWORD
        message_address[63:32] = msix_table[vector * 4 + 1]; // Upper address DWORD

        // Extract message data from MSI-X table entry (third DWORD)
        message_data = msix_table[vector * 4 + 2];

        // Trigger MSI-X interrupt delivery through PCIe core interface
        // Set interrupt request signal and vector information
        msix_interrupt <= 1'b1;
        msix_vector <= vector;

        // Log the MSI-X message details for debugging
        $display("MSI-X message: addr=0x%016h, data=0x%08h, vector=%0d",
                 message_address, message_data, vector);
    end else begin
        // Vector is masked - set pending bit
        pba_dword = vector >> 5;  // Divide by 32 to get DWORD index
        pba_bit = vector & 5'h1F;  // Modulo 32 to get bit position

        // Set the pending bit
        msix_pba[pba_dword] = msix_pba[pba_dword] | (1 << pba_bit);
    end
endtask

// Initialize MSI-X table and PBA
initial begin
    // Initialize MSI-X table to zeros
    for (int i = 0; i < NUM_MSIX * 4; i++) begin
        msix_table[i] = 32'h0;
    end

    // Initialize MSI-X PBA to zeros
    for (int i = 0; i < {pba_size}; i++) begin
        msix_pba[i] = 32'h0;
    end
end
"""

    # Format the template with the MSI-X information
    return sv_template.format(
        table_size=table_size,
        table_bir=msix_info["table_bir"],
        table_offset=msix_info["table_offset"],
        pba_bir=msix_info["pba_bir"],
        pba_offset=msix_info["pba_offset"],
        enabled_val=1 if msix_info["enabled"] else 0,
        function_mask_val=1 if msix_info["function_mask"] else 0,
        pba_size=pba_size,
        pba_size_minus_one=pba_size - 1,
        alignment_warning=alignment_warning,
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
