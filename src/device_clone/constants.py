"""
Shared constants for PCILeech firmware generation.

This module consolidates board mappings and other constants that were
previously duplicated across the build system.
"""

# Board to FPGA part mapping
BOARD_PARTS = {
    # Original boards
    "35t": "xc7a35tcsg324-2",
    "75t": "xc7a75tfgg484-2",
    "100t": "xczu3eg-sbva484-1-e",
    # CaptainDMA boards
    "pcileech_75t484_x1": "xc7a75tfgg484-2",
    "pcileech_35t484_x1": "xc7a35tfgg484-2",
    "pcileech_35t325_x4": "xc7a35tcsg324-2",
    "pcileech_35t325_x1": "xc7a35tcsg324-2",
    "pcileech_100t484_x1": "xczu3eg-sbva484-1-e",
    # Other boards
    "pcileech_enigma_x1": "xc7a75tfgg484-2",
    "pcileech_squirrel": "xc7a35tcsg324-2",
    "pcileech_pciescreamer_xc7a35": "xc7a35tcsg324-2",
}

# Default FPGA part for unknown boards
DEFAULT_FPGA_PART = "xc7a35tcsg324-2"

# Vivado project configuration constants
VIVADO_PROJECT_NAME = "pcileech_firmware"
VIVADO_PROJECT_DIR = "./vivado_project"
VIVADO_OUTPUT_DIR = "."

# Legacy TCL script file names (7-script approach - deprecated)
LEGACY_TCL_SCRIPT_FILES = [
    "01_project_setup.tcl",
    "02_ip_config.tcl",
    "03_add_sources.tcl",
    "04_constraints.tcl",
    "05_synthesis.tcl",
    "06_implementation.tcl",
    "07_bitstream.tcl",
]

# PCILeech TCL script file names (2-script approach - current)
PCILEECH_TCL_SCRIPT_FILES = [
    "vivado_generate_project.tcl",
    "vivado_build.tcl",
]

# For backward compatibility
TCL_SCRIPT_FILES = LEGACY_TCL_SCRIPT_FILES

# Master build script name (legacy)
MASTER_BUILD_SCRIPT = "build_all.tcl"

# PCILeech build scripts
PCILEECH_PROJECT_SCRIPT = "vivado_generate_project.tcl"
PCILEECH_BUILD_SCRIPT = "vivado_build.tcl"

# Synthesis and implementation strategies
SYNTHESIS_STRATEGY = "Vivado Synthesis Defaults"
IMPLEMENTATION_STRATEGY = "Performance_Explore"

# FPGA family detection patterns
FPGA_FAMILIES = {
    "ZYNQ_ULTRASCALE": "xczu",
    "ARTIX7_35T": "xc7a35t",
    "ARTIX7_75T": "xc7a75t",
    "KINTEX7": "xc7k",
}

# Legacy TCL files to clean up
LEGACY_TCL_FILES = [
    "build_unified.tcl",
    "unified_build.tcl",
    "build_firmware.tcl",
]

# Production mode defaults - enable all advanced features by default
PRODUCTION_DEFAULTS = {
    "ADVANCED_SV": True,
    "MANUFACTURING_VARIANCE": True,
    "BEHAVIOR_PROFILING": True,
    "POWER_MANAGEMENT": True,
    "ERROR_HANDLING": True,
    "PERFORMANCE_COUNTERS": True,
    "CONFIG_SPACE_SHADOW": True,
    "MSIX_CAPABILITY": True,
    "OPTION_ROM_SUPPORT": True,
    "DEFAULT_DEVICE_TYPE": "network",
}
