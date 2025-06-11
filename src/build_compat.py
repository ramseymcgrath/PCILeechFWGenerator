#!/usr/bin/env python3
"""
Compatibility module for legacy build functions.

This module provides backward compatibility for tests and other code
that depends on the old build.py functions.
"""

import os
import stat
import tempfile
from typing import Any, Dict, List, Tuple


def create_secure_tempfile(suffix: str = "", prefix: str = "build_") -> str:
    """Create a secure temporary file."""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    try:
        # Set secure permissions (owner read/write only)
        os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
        os.close(fd)
        return path
    except Exception:
        os.close(fd)
        if os.path.exists(path):
            os.unlink(path)
        raise


def get_donor_info(bdf: str, use_donor_dump: bool = False) -> Dict[str, Any]:
    """Mock donor info extraction for compatibility."""
    return {
        "vendor_id": "0x8086",
        "device_id": "0x1533",
        "subvendor_id": "0x8086",
        "subsystem_id": "0x0000",
        "revision_id": "0x03",
        "bar_size": "0x20000",
        "mpc": "0x02",
        "mpr": "0x02",
        "bdf": bdf,
    }


def scrape_driver_regs(
    vendor_id: str, device_id: str
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Mock driver register scraping for compatibility."""
    registers = [
        {
            "offset": 0x0,
            "name": "device_control",
            "value": "0x00000000",
            "rw": "rw",
            "context": {"function": "device_control"},
        },
        {
            "offset": 0x4,
            "name": "device_status",
            "value": "0x00000001",
            "rw": "ro",
            "context": {"function": "status_check"},
        },
    ]

    state_machine_analysis = {
        "extracted_state_machines": 1,
        "optimized_state_machines": 1,
        "functions_with_state_patterns": 2,
    }

    return registers, state_machine_analysis


def integrate_behavior_profile(
    bdf: str, registers: List[Dict[str, Any]], duration: float = 10.0
) -> List[Dict[str, Any]]:
    """Mock behavior profile integration for compatibility."""
    # Just return the registers unchanged for compatibility
    return registers


def build_sv(registers: List[Dict[str, Any]], output_file: str) -> None:
    """Mock SystemVerilog generation for compatibility."""
    # Generate basic SystemVerilog content
    content = """//
// PCILeech FPGA BAR Controller - Compatibility Mode
//

module pcileech_tlps128_bar_controller(
    input               rst,
    input               clk,
    input               bar_en,
    input  [31:0]       bar_addr,
    input               bar_wr_en,
    input  [31:0]       bar_wr_data,
    input  [3:0]        bar_wr_be,
    output [31:0]       bar_rd_data,
    output              bar_rd_valid
);

    // Register declarations
"""

    for reg in registers:
        reg_name = reg["name"]
        reg_value = reg.get("value", "0x00000000").replace("0x", "")
        content += f"    logic [31:0] {reg_name}_reg = 32'h{reg_value};\n"

    content += """
    // Read logic
    assign bar_rd_data = 32'h0;
    assign bar_rd_valid = bar_en && !bar_wr_en;

endmodule
"""

    with open(output_file, "w") as f:
        f.write(content)


def build_tcl(device_info: Dict[str, Any], output_file: str) -> Tuple[str, str]:
    """Mock TCL generation for compatibility."""
    content = f"""#
# PCILeech FPGA Build Script - Compatibility Mode
#

# Device configuration
# Vendor ID: {device_info.get("vendor_id", "0x0000")}
# Device ID: {device_info.get("device_id", "0x0000")}

create_project test_project . -force
"""

    return content, output_file


def run(command: str) -> None:
    """Mock command execution for compatibility."""
    # Just print the command for compatibility
    print(f"[COMPAT] Would run: {command}")


def code_from_bytes(size_bytes: int) -> int:
    """Mock code from bytes conversion for compatibility."""
    size_map = {128: 0, 256: 1, 1024: 3, 4096: 5}
    return size_map.get(size_bytes, 0)


def generate_register_state_machine(
    name: str, sequences: List[Dict[str, Any]], offset: int
) -> str:
    """Mock state machine generation for compatibility."""
    if len(sequences) < 2:
        return ""

    return f"""
    // State machine for {name}
    typedef enum logic [1:0] {{
        {name.upper()}_IDLE,
        {name.upper()}_ACTIVE
    }} {name}_state_t;
    
    {name}_state_t {name}_state;
"""


def generate_device_state_machine(registers: List[Dict[str, Any]]) -> str:
    """Mock device state machine generation for compatibility."""
    return """
    // Device state machine
    typedef enum logic [2:0] {
        DEVICE_RESET,
        DEVICE_INIT,
        DEVICE_READY,
        DEVICE_ACTIVE
    } device_state_t;
    
    device_state_t device_state;
    logic [31:0] global_timer;
"""


# Board and aperture constants for compatibility
BOARD_INFO = {
    "35t": {"root": "pcileech_35t", "gen": "pcileech_35t.tcl"},
    "75t": {"root": "pcileech_75t", "gen": "pcileech_75t.tcl"},
    "100t": {"root": "pcileech_100t", "gen": "pcileech_100t.tcl"},
    "pcileech_75t484_x1": {
        "root": "pcileech_75t484_x1",
        "gen": "pcileech_75t484_x1.tcl",
    },
    "pcileech_35t484_x1": {
        "root": "pcileech_35t484_x1",
        "gen": "pcileech_35t484_x1.tcl",
    },
    "pcileech_35t325_x4": {
        "root": "pcileech_35t325_x4",
        "gen": "pcileech_35t325_x4.tcl",
    },
    "pcileech_35t325_x1": {
        "root": "pcileech_35t325_x1",
        "gen": "pcileech_35t325_x1.tcl",
    },
    "pcileech_100t484_x1": {
        "root": "pcileech_100t484_x1",
        "gen": "pcileech_100t484_x1.tcl",
    },
    "pcileech_enigma_x1": {
        "root": "pcileech_enigma_x1",
        "gen": "pcileech_enigma_x1.tcl",
    },
    "pcileech_squirrel": {"root": "pcileech_squirrel", "gen": "pcileech_squirrel.tcl"},
    "pcileech_pciescreamer_xc7a35": {
        "root": "pcileech_pciescreamer_xc7a35",
        "gen": "pcileech_pciescreamer_xc7a35.tcl",
    },
}

APERTURE = {1024: "1_KB", 65536: "64_KB", 16777216: "16_MB"}
