#!/usr/bin/env python3
"""
MSI-X Capability Parser

This module provides functionality to parse MSI-X capability structures from
PCI configuration space and generate SystemVerilog code for MSI-X table replication.
"""

import logging
import struct
from typing import Any, Dict, List, Optional, Tuple

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

// MSI-X control registers - dynamically connected to configuration space
// These signals are properly driven by the actual MSI-X capability registers
input wire msix_enabled;        // Connected to MSI-X Message Control Enable bit (bit 15)
input wire msix_function_mask;  // Connected to MSI-X Message Control Function Mask bit (bit 14)
input wire [10:0] msix_table_size; // Connected to MSI-X Message Control Table Size field (bits 10:0)

// MSI-X capability register interface for dynamic control
input wire        msix_cap_wr;     // Write strobe for MSI-X capability registers
input wire [31:0] msix_cap_addr;   // Address within MSI-X capability space
input wire [31:0] msix_cap_wdata;  // Write data for MSI-X capability registers
input wire [3:0]  msix_cap_be;     // Byte enables for MSI-X capability writes
output reg [31:0] msix_cap_rdata;  // Read data from MSI-X capability registers

// MSI-X interrupt generation interface
output reg        msix_interrupt;  // MSI-X interrupt request
output reg [10:0] msix_vector;     // MSI-X vector number
output reg [63:0] msix_msg_addr;   // MSI-X message address
output reg [31:0] msix_msg_data;   // MSI-X message data

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

// Legacy MSI-X interrupt delivery logic (deprecated - use msix_deliver_interrupt_validated)
task msix_deliver_interrupt(input logic [10:0] vector);
    // Redirect to validated version for backward compatibility
    msix_deliver_interrupt_validated(vector);
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

    # Generate the complete MSI-X implementation including capability registers
    capability_registers = generate_msix_capability_registers(msix_info)

    # Format the template with the MSI-X information
    formatted_template = sv_template.format(
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

    # Combine the main template with capability register management
    return formatted_template + "\n" + capability_registers


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
        pba_size = (table_size + 31) // 32 * 4  # PBA size in bytes
        pba_end = pba_offset + pba_size

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

    sv_template = """
// MSI-X Capability Register Management
// Handles dynamic configuration and control of MSI-X functionality

// MSI-X Message Control register fields
reg        msix_enable_reg;           // MSI-X Enable bit
reg        msix_function_mask_reg;    // Function Mask bit
reg [10:0] msix_table_size_reg;       // Table Size field (read-only)

// MSI-X Table Offset/BIR and PBA Offset/BIR registers (read-only)
reg [31:0] msix_table_offset_bir;
reg [31:0] msix_pba_offset_bir;

// Initialize MSI-X capability registers
initial begin
    msix_enable_reg = 1'b0;
    msix_function_mask_reg = 1'b0;
    msix_table_size_reg = {table_size_minus_one};  // Table size - 1
    msix_table_offset_bir = {{table_offset_bir}};
    msix_pba_offset_bir = {{pba_offset_bir}};
end

// MSI-X capability register read/write logic
always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
        msix_enable_reg <= 1'b0;
        msix_function_mask_reg <= 1'b0;
    end else if (msix_cap_wr) begin
        // Handle writes to MSI-X Message Control register
        case (msix_cap_addr[3:0])
            4'h2: begin  // Message Control register (offset 2)
                if (msix_cap_be[1]) msix_enable_reg <= msix_cap_wdata[15];
                if (msix_cap_be[1]) msix_function_mask_reg <= msix_cap_wdata[14];
                // Table size is read-only, ignore writes
            end
            // Table Offset/BIR and PBA Offset/BIR are read-only
            default: begin
                // Other offsets are read-only or reserved
            end
        endcase
    end
end

// MSI-X capability register read data multiplexer
always_comb begin
    case (msix_cap_addr[3:0])
        4'h0: msix_cap_rdata = {{8'h00, 8'h11}};  // Next pointer and Capability ID
        4'h2: msix_cap_rdata = {{msix_enable_reg, msix_function_mask_reg, 3'b000, msix_table_size_reg}};
        4'h4: msix_cap_rdata = msix_table_offset_bir;
        4'h8: msix_cap_rdata = msix_pba_offset_bir;
        default: msix_cap_rdata = 32'h00000000;
    endcase
end

// Connect control signals to the registers
assign msix_enabled = msix_enable_reg;
assign msix_function_mask = msix_function_mask_reg;
assign msix_table_size = msix_table_size_reg;

// MSI-X vector validation
function logic is_valid_msix_vector(input logic [10:0] vector);
    return (vector < NUM_MSIX) && msix_enabled && !msix_function_mask;
endfunction

// Enhanced MSI-X interrupt delivery with proper validation
task msix_deliver_interrupt_validated(input logic [10:0] vector);
    logic vector_masked;
    logic [31:0] table_addr;
    logic [31:0] control_dword;
    logic [31:0] pba_dword_idx;
    logic [4:0] pba_bit_idx;

    // Validate vector number
    if (!is_valid_msix_vector(vector)) begin
        $display("MSI-X Error: Invalid vector %0d or MSI-X disabled", vector);
        return;
    end

    // Get control DWORD (fourth DWORD in the entry)
    table_addr = vector * 4 + 3;
    control_dword = msix_table[table_addr];

    // Check if vector is masked (bit 0 of control DWORD)
    vector_masked = control_dword[0];

    if (!vector_masked) begin
        // Vector is enabled and not masked - deliver interrupt
        logic [63:0] message_address;
        logic [31:0] message_data;

        // Extract message address from MSI-X table entry
        message_address[31:0] = msix_table[vector * 4];      // Lower address DWORD
        message_address[63:32] = msix_table[vector * 4 + 1]; // Upper address DWORD

        // Extract message data from MSI-X table entry
        message_data = msix_table[vector * 4 + 2];

        // Set interrupt outputs
        msix_interrupt <= 1'b1;
        msix_vector <= vector;
        msix_msg_addr <= message_address;
        msix_msg_data <= message_data;

        $display("MSI-X Interrupt: vector=%0d, addr=0x%016h, data=0x%08h",
                 vector, message_address, message_data);
    end else begin
        // Vector is masked - set pending bit in PBA
        pba_dword_idx = vector >> 5;  // Divide by 32 to get DWORD index
        pba_bit_idx = vector & 5'h1F;  // Modulo 32 to get bit position

        if (pba_dword_idx < PBA_SIZE) begin
            msix_pba[pba_dword_idx] <= msix_pba[pba_dword_idx] | (32'h1 << pba_bit_idx);
            $display("MSI-X Pending: vector=%0d set in PBA[%0d][%0d]",
                     vector, pba_dword_idx, pba_bit_idx);
        end
    end
endtask
"""

    # Format the template with MSI-X information
    return sv_template.format(
        table_size_minus_one=table_size - 1,
        table_offset_bir=f"32'h{(msix_info['table_offset'] | msix_info['table_bir']):08X}",
        pba_offset_bir=f"32'h{(msix_info['pba_offset'] | msix_info['pba_bir']):08X}",
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
