#!/usr/bin/env python3
"""
PCILeech FPGA Firmware Builder - Production System

This is a complete, production-level build system for generating PCILeech DMA firmware
for various FPGA boards using donor device configuration space information obtained via VFIO.

Features:
- VFIO-based configuration space extraction
- Advanced SystemVerilog generation
- Manufacturing variance simulation
- Device-specific optimizations
- Behavior profiling
- MSI-X capability handling
- Option ROM management
- Configuration space shadowing

Usage:
  python3 build.py --bdf 0000:03:00.0 --board pcileech_35t325_x4

Boards:
  pcileech_35t325_x4  → Artix-7 35T (PCIeSquirrel)
  pcileech_75t        → Kintex-7 75T (PCIeEnigmaX1)
  pcileech_100t       → Zynq UltraScale+ (XilinxZDMA)
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import project modules
try:
    from behavior_profiler import BehaviorProfiler
    from donor_dump_manager import DonorDumpError, DonorDumpManager
    from manufacturing_variance import (
        DeviceClass,
        ManufacturingVarianceSimulator,
        VarianceModel,
    )
    from vivado_utils import find_vivado_installation
except ImportError as e:
    # Try relative imports for container environment
    try:
        from .behavior_profiler import BehaviorProfiler
        from .donor_dump_manager import DonorDumpError, DonorDumpManager
        from .manufacturing_variance import (
            DeviceClass,
            ManufacturingVarianceSimulator,
            VarianceModel,
        )
        from .vivado_utils import find_vivado_installation
    except ImportError:
        print(f"Error importing required modules: {e}")
        print("Falling back to basic functionality...")
        DonorDumpManager = None
        ManufacturingVarianceSimulator = None
        DeviceClass = None
        VarianceModel = None
        BehaviorProfiler = None
        find_vivado_installation = None

# Try to import advanced modules (optional)
try:
    from advanced_sv_generator import AdvancedSVGenerator
except ImportError:
    try:
        from .advanced_sv_generator import AdvancedSVGenerator
    except ImportError:
        AdvancedSystemVerilogGenerator = None

try:
    from msix_capability import generate_msix_table_sv, parse_msix_capability
except ImportError:
    try:
        from .msix_capability import generate_msix_table_sv, parse_msix_capability
    except ImportError:
        MSIXCapabilityManager = None

try:
    from option_rom_manager import OptionROMManager
except ImportError:
    try:
        from .option_rom_manager import OptionROMManager
    except ImportError:
        OptionROMManager = None


# Set up logging
def setup_logging(output_dir: Optional[Path] = None):
    """Set up logging with appropriate handlers."""
    handlers = [logging.StreamHandler(sys.stdout)]

    # Add file handler if output directory exists
    if output_dir and output_dir.exists():
        log_file = output_dir / "build.log"
        handlers.append(logging.FileHandler(str(log_file), mode="a"))
    elif os.path.exists("/app/output"):
        # Container environment
        handlers.append(logging.FileHandler("/app/output/build.log", mode="a"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True,  # Override any existing configuration
    )


# Initialize basic logging (will be reconfigured in main)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class PCILeechFirmwareBuilder:
    """Main firmware builder class."""

    def __init__(self, bdf: str, board: str, output_dir: Optional[Path] = None):
        self.bdf = bdf
        self.board = board

        # Set output directory based on environment
        if output_dir:
            self.output_dir = output_dir
        elif os.path.exists("/app/output"):
            self.output_dir = Path("/app/output")
        else:
            self.output_dir = Path("./output")

        self.output_dir.mkdir(exist_ok=True)

        # Reconfigure logging with proper output directory
        setup_logging(self.output_dir)

        # Initialize components
        self.donor_manager = DonorDumpManager() if DonorDumpManager else None
        self.sv_generator = None
        self.variance_simulator = (
            ManufacturingVarianceSimulator() if ManufacturingVarianceSimulator else None
        )
        self.behavior_profiler = None
        self.msix_manager = MSIXCapabilityManager() if MSIXCapabilityManager else None
        self.option_rom_manager = OptionROMManager() if OptionROMManager else None

        logger.info(f"Initialized PCILeech firmware builder for {bdf} on {board}")

    def read_vfio_config_space(self) -> bytes:
        """Read PCI configuration space via VFIO."""
        try:
            # Find IOMMU group for the device
            iommu_group_path = f"/sys/bus/pci/devices/{self.bdf}/iommu_group"
            if not os.path.exists(iommu_group_path):
                raise RuntimeError(f"IOMMU group not found for device {self.bdf}")

            iommu_group = os.path.basename(os.readlink(iommu_group_path))
            vfio_device = f"/dev/vfio/{iommu_group}"

            if not os.path.exists(vfio_device):
                raise RuntimeError(f"VFIO device {vfio_device} not found")

            logger.info(
                f"Reading configuration space for device {self.bdf} via VFIO group {iommu_group}"
            )

            # Read actual configuration space from sysfs as fallback
            config_path = f"/sys/bus/pci/devices/{self.bdf}/config"
            if os.path.exists(config_path):
                with open(config_path, "rb") as f:
                    config_space = f.read(256)  # Read first 256 bytes
                logger.info(
                    f"Successfully read {len(config_space)} bytes of configuration space"
                )
                return config_space
            else:
                # Generate synthetic configuration space if real one not available
                logger.warning(
                    "Real config space not available, generating synthetic data"
                )
                return self._generate_synthetic_config_space()

        except Exception as e:
            logger.error(f"Failed to read VFIO config space: {e}")
            logger.info("Generating synthetic configuration space as fallback")
            return self._generate_synthetic_config_space()

    def _generate_synthetic_config_space(self) -> bytes:
        """Generate production-quality synthetic PCI configuration space with realistic device profiles."""
        config_space = bytearray(4096)  # Extended config space (4KB)

        # Determine device profile based on BDF or use intelligent defaults
        device_profiles = {
            # Network controllers
            "network": {
                "vendor_id": 0x8086,
                "device_id": 0x125C,
                "class_code": 0x020000,
                "subsys_vendor": 0x8086,
                "subsys_device": 0x0000,
                "bar_configs": [
                    0xF0000000,
                    0x00000000,
                    0xF0010000,
                    0x00000000,
                    0x0000E001,
                    0x00000000,
                ],
                "capabilities": ["msi", "msix", "pcie", "pm"],
            },
            # Storage controllers
            "storage": {
                "vendor_id": 0x1B4B,
                "device_id": 0x9230,
                "class_code": 0x010802,
                "subsys_vendor": 0x1B4B,
                "subsys_device": 0x9230,
                "bar_configs": [
                    0xF0000000,
                    0x00000000,
                    0x0000E001,
                    0x00000000,
                    0x00000000,
                    0x00000000,
                ],
                "capabilities": ["msi", "msix", "pcie", "pm"],
            },
            # Audio controllers
            "audio": {
                "vendor_id": 0x8086,
                "device_id": 0x9DC8,
                "class_code": 0x040300,
                "subsys_vendor": 0x8086,
                "subsys_device": 0x7270,
                "bar_configs": [
                    0xF0000000,
                    0x00000000,
                    0x0000E001,
                    0x00000000,
                    0x00000000,
                    0x00000000,
                ],
                "capabilities": ["msi", "pcie", "pm"],
            },
        }

        # Select profile based on device characteristics or default to network
        profile = device_profiles["network"]  # Default to most common PCILeech target

        # Standard PCI Configuration Header (0x00-0x3F)
        # Vendor ID and Device ID
        config_space[0:2] = profile["vendor_id"].to_bytes(2, "little")
        config_space[2:4] = profile["device_id"].to_bytes(2, "little")

        # Command Register - Enable memory space, bus master, disable I/O space
        config_space[4:6] = (0x0006).to_bytes(2, "little")  # Memory Space + Bus Master

        # Status Register - Capabilities list, 66MHz capable, fast back-to-back
        config_space[6:8] = (0x0210).to_bytes(2, "little")  # Cap List + Fast B2B

        # Revision ID and Class Code
        config_space[8] = 0x04  # Revision ID
        config_space[9] = profile["class_code"] & 0xFF  # Programming Interface
        config_space[10:12] = ((profile["class_code"] >> 8) & 0xFFFF).to_bytes(
            2, "little"
        )

        # Cache Line Size, Latency Timer, Header Type, BIST
        config_space[12] = 0x10  # Cache line size (16 bytes)
        config_space[13] = 0x00  # Latency timer
        config_space[14] = 0x00  # Single function device
        config_space[15] = 0x00  # BIST not supported

        # Base Address Registers (BARs)
        for i, bar_val in enumerate(profile["bar_configs"]):
            offset = 16 + (i * 4)
            config_space[offset : offset + 4] = bar_val.to_bytes(4, "little")

        # Cardbus CIS Pointer (unused)
        config_space[40:44] = (0x00000000).to_bytes(4, "little")

        # Subsystem Vendor ID and Subsystem ID
        config_space[44:46] = profile["subsys_vendor"].to_bytes(2, "little")
        config_space[46:48] = profile["subsys_device"].to_bytes(2, "little")

        # Expansion ROM Base Address (disabled)
        config_space[48:52] = (0x00000000).to_bytes(4, "little")

        # Capabilities Pointer
        config_space[52] = 0x40  # First capability at 0x40

        # Reserved fields
        config_space[53:60] = b"\x00" * 7

        # Interrupt Line, Interrupt Pin, Min_Gnt, Max_Lat
        config_space[60] = 0xFF  # Interrupt line (not connected)
        config_space[61] = 0x01  # Interrupt pin A
        config_space[62] = 0x00  # Min_Gnt
        config_space[63] = 0x00  # Max_Lat

        # Build capability chain starting at 0x40
        cap_offset = 0x40

        # Power Management Capability (always present)
        if "pm" in profile["capabilities"]:
            config_space[cap_offset] = 0x01  # PM Capability ID
            config_space[cap_offset + 1] = 0x50  # Next capability pointer
            config_space[cap_offset + 2 : cap_offset + 4] = (0x0003).to_bytes(
                2, "little"
            )  # PM Capabilities
            config_space[cap_offset + 4 : cap_offset + 6] = (0x0000).to_bytes(
                2, "little"
            )  # PM Control/Status
            cap_offset = 0x50

        # MSI Capability
        if "msi" in profile["capabilities"]:
            config_space[cap_offset] = 0x05  # MSI Capability ID
            config_space[cap_offset + 1] = 0x60  # Next capability pointer
            config_space[cap_offset + 2 : cap_offset + 4] = (0x0080).to_bytes(
                2, "little"
            )  # MSI Control (64-bit)
            config_space[cap_offset + 4 : cap_offset + 8] = (0x00000000).to_bytes(
                4, "little"
            )  # Message Address
            config_space[cap_offset + 8 : cap_offset + 12] = (0x00000000).to_bytes(
                4, "little"
            )  # Message Upper Address
            config_space[cap_offset + 12 : cap_offset + 14] = (0x0000).to_bytes(
                2, "little"
            )  # Message Data
            cap_offset = 0x60

        # MSI-X Capability
        if "msix" in profile["capabilities"]:
            config_space[cap_offset] = 0x11  # MSI-X Capability ID
            config_space[cap_offset + 1] = 0x70  # Next capability pointer
            config_space[cap_offset + 2 : cap_offset + 4] = (0x0000).to_bytes(
                2, "little"
            )  # MSI-X Control
            config_space[cap_offset + 4 : cap_offset + 8] = (0x00000000).to_bytes(
                4, "little"
            )  # Table Offset/BIR
            config_space[cap_offset + 8 : cap_offset + 12] = (0x00002000).to_bytes(
                4, "little"
            )  # PBA Offset/BIR
            cap_offset = 0x70

        # PCIe Capability (for modern devices)
        if "pcie" in profile["capabilities"]:
            config_space[cap_offset] = 0x10  # PCIe Capability ID
            config_space[cap_offset + 1] = (
                0x00  # Next capability pointer (end of chain)
            )
            config_space[cap_offset + 2 : cap_offset + 4] = (0x0002).to_bytes(
                2, "little"
            )  # PCIe Capabilities
            config_space[cap_offset + 4 : cap_offset + 8] = (0x00000000).to_bytes(
                4, "little"
            )  # Device Capabilities
            config_space[cap_offset + 8 : cap_offset + 10] = (0x0000).to_bytes(
                2, "little"
            )  # Device Control
            config_space[cap_offset + 10 : cap_offset + 12] = (0x0000).to_bytes(
                2, "little"
            )  # Device Status
            config_space[cap_offset + 12 : cap_offset + 16] = (0x00000000).to_bytes(
                4, "little"
            )  # Link Capabilities
            config_space[cap_offset + 16 : cap_offset + 18] = (0x0000).to_bytes(
                2, "little"
            )  # Link Control
            config_space[cap_offset + 18 : cap_offset + 20] = (0x0000).to_bytes(
                2, "little"
            )  # Link Status

        logger.info(
            f"Generated synthetic config space: VID={profile['vendor_id']:04x}, DID={profile['device_id']:04x}, Class={profile['class_code']:06x}"
        )
        return bytes(config_space[:256])  # Return standard 256-byte config space

    def extract_device_info(self, config_space: bytes) -> Dict[str, Any]:
        """Extract device information from configuration space."""
        if len(config_space) < 64:
            raise ValueError("Configuration space too short")

        vendor_id = int.from_bytes(config_space[0:2], "little")
        device_id = int.from_bytes(config_space[2:4], "little")
        class_code = int.from_bytes(config_space[10:12], "little")
        revision_id = config_space[8]

        # Extract BARs
        bars = []
        for i in range(6):
            bar_offset = 16 + (i * 4)
            if bar_offset + 4 <= len(config_space):
                bar_value = int.from_bytes(
                    config_space[bar_offset : bar_offset + 4], "little"
                )
                bars.append(bar_value)

        device_info = {
            "vendor_id": f"{vendor_id:04x}",
            "device_id": f"{device_id:04x}",
            "class_code": f"{class_code:04x}",
            "revision_id": f"{revision_id:02x}",
            "bdf": self.bdf,
            "board": self.board,
            "bars": bars,
            "config_space_hex": config_space.hex(),
            "config_space_size": len(config_space),
        }

        logger.info(
            f"Extracted device info: VID={device_info['vendor_id']}, DID={device_info['device_id']}"
        )
        return device_info

    def generate_systemverilog_files(
        self,
        device_info: Dict[str, Any],
        advanced_sv: bool = False,
        device_type: Optional[str] = None,
        enable_variance: bool = False,
    ) -> List[str]:
        """Generate SystemVerilog files for the firmware."""
        generated_files = []

        try:
            # Initialize advanced SystemVerilog generator if available and requested
            if advanced_sv and AdvancedSVGenerator:
                logger.info("Generating advanced SystemVerilog modules")
                self.sv_generator = AdvancedSVGenerator()
                logger.info("Advanced SystemVerilog generator initialized")

            # Discover and copy all relevant project files
            project_files = self._discover_and_copy_all_files(device_info)
            generated_files.extend(project_files)

            # Generate manufacturing variance if enabled
            if enable_variance and ManufacturingVarianceSimulator:
                logger.info("Applying manufacturing variance simulation")
                self.variance_simulator = ManufacturingVarianceSimulator()
                variance_files = self._apply_manufacturing_variance(device_info)
                generated_files.extend(variance_files)

        except Exception as e:
            logger.error(f"Error generating SystemVerilog files: {e}")
            raise

        return generated_files

    def _discover_and_copy_all_files(self, device_info: Dict[str, Any]) -> List[str]:
        """Scalable discovery and copying of all relevant project files."""
        copied_files = []
        src_dir = Path(__file__).parent

        # Discover all SystemVerilog files (including subdirectories)
        sv_files = list(src_dir.rglob("*.sv"))
        logger.info(f"Discovered {len(sv_files)} SystemVerilog files")

        # Validate and copy SystemVerilog modules
        valid_sv_files = []
        for sv_file in sv_files:
            try:
                with open(sv_file, "r") as f:
                    content = f.read()
                    # Basic validation - check for module declaration
                    if "module " in content and "endmodule" in content:
                        dest_path = self.output_dir / sv_file.name
                        with open(dest_path, "w") as dest:
                            dest.write(content)
                        copied_files.append(str(dest_path))
                        valid_sv_files.append(sv_file.name)
                        logger.info(
                            f"Copied valid SystemVerilog module: {sv_file.name}"
                        )
                    else:
                        logger.warning(
                            f"Skipping invalid SystemVerilog file: {sv_file.name}"
                        )
            except Exception as e:
                logger.error(f"Error processing {sv_file.name}: {e}")

        # Discover and copy all TCL files (preserve as-is)
        tcl_files = list(src_dir.rglob("*.tcl"))
        for tcl_file in tcl_files:
            try:
                dest_path = self.output_dir / tcl_file.name
                with open(tcl_file, "r") as src, open(dest_path, "w") as dest:
                    content = src.read()
                    dest.write(content)
                copied_files.append(str(dest_path))
                logger.info(f"Copied TCL script: {tcl_file.name}")
            except Exception as e:
                logger.error(f"Error copying TCL file {tcl_file.name}: {e}")

        # Discover and copy constraint files
        xdc_files = list(src_dir.rglob("*.xdc"))
        for xdc_file in xdc_files:
            try:
                dest_path = self.output_dir / xdc_file.name
                with open(xdc_file, "r") as src, open(dest_path, "w") as dest:
                    content = src.read()
                    dest.write(content)
                copied_files.append(str(dest_path))
                logger.info(f"Copied constraint file: {xdc_file.name}")
            except Exception as e:
                logger.error(f"Error copying constraint file {xdc_file.name}: {e}")

        # Discover and copy any Verilog files
        v_files = list(src_dir.rglob("*.v"))
        for v_file in v_files:
            try:
                dest_path = self.output_dir / v_file.name
                with open(v_file, "r") as src, open(dest_path, "w") as dest:
                    content = src.read()
                    dest.write(content)
                copied_files.append(str(dest_path))
                logger.info(f"Copied Verilog module: {v_file.name}")
            except Exception as e:
                logger.error(f"Error copying Verilog file {v_file.name}: {e}")

        # Generate device-specific configuration module
        config_module = self._generate_device_config_module(device_info)
        config_path = self.output_dir / "device_config.sv"
        with open(config_path, "w") as f:
            f.write(config_module)
        copied_files.append(str(config_path))

        # Generate top-level wrapper
        top_module = self._generate_top_level_wrapper(device_info)
        top_path = self.output_dir / "pcileech_top.sv"
        with open(top_path, "w") as f:
            f.write(top_module)
        copied_files.append(str(top_path))

        return copied_files

    def _generate_device_config_module(self, device_info: Dict[str, Any]) -> str:
        """Generate device-specific configuration module using actual device data."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        class_code = device_info["class_code"]
        revision_id = device_info["revision_id"]
        bars = device_info["bars"]

        return f"""
//==============================================================================
// Device Configuration Module - Generated for {vendor_id}:{device_id}
// Board: {device_info['board']}
//==============================================================================

module device_config #(
    parameter VENDOR_ID = 16'h{vendor_id},
    parameter DEVICE_ID = 16'h{device_id},
    parameter CLASS_CODE = 24'h{class_code}{revision_id},
    parameter SUBSYSTEM_VENDOR_ID = 16'h{vendor_id},
    parameter SUBSYSTEM_DEVICE_ID = 16'h{device_id},
    parameter BAR0_APERTURE = 32'h{bars[0]:08x},
    parameter BAR1_APERTURE = 32'h{bars[1]:08x},
    parameter BAR2_APERTURE = 32'h{bars[2]:08x},
    parameter BAR3_APERTURE = 32'h{bars[3]:08x},
    parameter BAR4_APERTURE = 32'h{bars[4]:08x},
    parameter BAR5_APERTURE = 32'h{bars[5]:08x}
) (
    // Configuration space interface
    output logic [31:0] cfg_device_id,
    output logic [31:0] cfg_class_code,
    output logic [31:0] cfg_subsystem_id,
    output logic [31:0] cfg_bar [0:5]
);

    // Device identification
    assign cfg_device_id = {{DEVICE_ID, VENDOR_ID}};
    assign cfg_class_code = {{8'h00, CLASS_CODE}};
    assign cfg_subsystem_id = {{SUBSYSTEM_DEVICE_ID, SUBSYSTEM_VENDOR_ID}};
    
    // BAR configuration
    assign cfg_bar[0] = BAR0_APERTURE;
    assign cfg_bar[1] = BAR1_APERTURE;
    assign cfg_bar[2] = BAR2_APERTURE;
    assign cfg_bar[3] = BAR3_APERTURE;
    assign cfg_bar[4] = BAR4_APERTURE;
    assign cfg_bar[5] = BAR5_APERTURE;

endmodule
"""

    def _generate_top_level_wrapper(self, device_info: Dict[str, Any]) -> str:
        """Generate top-level wrapper that integrates all modules."""
        return f"""
//==============================================================================
// PCILeech Top-Level Wrapper - Generated for {device_info['vendor_id']}:{device_info['device_id']}
// Board: {self.board}
//==============================================================================

module pcileech_top (
    // Clock and reset
    input  logic        clk,
    input  logic        reset_n,
    
    // PCIe interface (connect to PCIe hard IP)
    input  logic [31:0] pcie_rx_data,
    input  logic        pcie_rx_valid,
    output logic [31:0] pcie_tx_data,
    output logic        pcie_tx_valid,
    
    // Configuration space interface
    input  logic        cfg_ext_read_received,
    input  logic        cfg_ext_write_received,
    input  logic [9:0]  cfg_ext_register_number,
    input  logic [3:0]  cfg_ext_function_number,
    input  logic [31:0] cfg_ext_write_data,
    input  logic [3:0]  cfg_ext_write_byte_enable,
    output logic [31:0] cfg_ext_read_data,
    output logic        cfg_ext_read_data_valid,
    
    // MSI-X interrupt interface
    output logic        msix_interrupt,
    output logic [10:0] msix_vector,
    input  logic        msix_interrupt_ack,
    
    // Debug/status outputs
    output logic [31:0] debug_status,
    output logic        device_ready
);

    // Internal signals
    logic [31:0] bar_addr;
    logic [31:0] bar_wr_data;
    logic        bar_wr_en;
    logic        bar_rd_en;
    logic [31:0] bar_rd_data;
    
    // Device configuration signals
    logic [31:0] cfg_device_id;
    logic [31:0] cfg_class_code;
    logic [31:0] cfg_subsystem_id;
    logic [31:0] cfg_bar [0:5];

    // Instantiate device configuration
    device_config device_cfg (
        .cfg_device_id(cfg_device_id),
        .cfg_class_code(cfg_class_code),
        .cfg_subsystem_id(cfg_subsystem_id),
        .cfg_bar(cfg_bar)
    );

    // Instantiate BAR controller
    pcileech_tlps128_bar_controller #(
        .BAR_APERTURE_SIZE(131072),  // 128KB
        .NUM_MSIX(1),
        .MSIX_TABLE_BIR(0),
        .MSIX_TABLE_OFFSET(0),
        .MSIX_PBA_BIR(0),
        .MSIX_PBA_OFFSET(0)
    ) bar_controller (
        .clk(clk),
        .reset_n(reset_n),
        .bar_addr(bar_addr),
        .bar_wr_data(bar_wr_data),
        .bar_wr_en(bar_wr_en),
        .bar_rd_en(bar_rd_en),
        .bar_rd_data(bar_rd_data),
        .cfg_ext_read_received(cfg_ext_read_received),
        .cfg_ext_write_received(cfg_ext_write_received),
        .cfg_ext_register_number(cfg_ext_register_number),
        .cfg_ext_function_number(cfg_ext_function_number),
        .cfg_ext_write_data(cfg_ext_write_data),
        .cfg_ext_write_byte_enable(cfg_ext_write_byte_enable),
        .cfg_ext_read_data(cfg_ext_read_data),
        .cfg_ext_read_data_valid(cfg_ext_read_data_valid),
        .msix_interrupt(msix_interrupt),
        .msix_vector(msix_vector),
        .msix_interrupt_ack(msix_interrupt_ack)
    );

    // Basic PCIe TLP processing for protocol compliance
    typedef enum logic [1:0] {{
        TLP_IDLE,
        TLP_HEADER,
        TLP_PROCESSING
    }} tlp_state_t;
    
    tlp_state_t tlp_state;
    logic [31:0] tlp_header [0:3];
    logic [7:0]  tlp_header_count;
    logic [10:0] tlp_length;
    logic [6:0]  tlp_type;
    logic [31:0] tlp_address;
    
    // Simplified PCIe TLP processing for basic protocol compliance
    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            pcie_tx_data <= 32'h0;
            pcie_tx_valid <= 1'b0;
            debug_status <= 32'h0;
            device_ready <= 1'b0;
            tlp_state <= TLP_IDLE;
            tlp_header_count <= 8'h0;
        end else begin
            // Default assignments
            pcie_tx_valid <= 1'b0;
            
            case (tlp_state)
                TLP_IDLE: begin
                    if (pcie_rx_valid) begin
                        tlp_header[0] <= pcie_rx_data;
                        tlp_header_count <= 8'h1;
                        tlp_state <= TLP_HEADER;
                        
                        // Extract TLP type and length from first header
                        tlp_type <= pcie_rx_data[30:24];
                        tlp_length <= pcie_rx_data[9:0];
                    end
                    device_ready <= 1'b1;
                end
                
                TLP_HEADER: begin
                    if (pcie_rx_valid) begin
                        tlp_header[tlp_header_count] <= pcie_rx_data;
                        tlp_header_count <= tlp_header_count + 1;
                        
                        // For memory requests, capture address from header[1]
                        if (tlp_header_count == 8'h1) begin
                            tlp_address <= pcie_rx_data;
                        end
                        
                        // Basic TLP acknowledgment
                        if (tlp_header_count >= 8'h2) begin
                            tlp_state <= TLP_PROCESSING;
                        end
                    end
                end
                
                TLP_PROCESSING: begin
                    // Basic protocol compliance - acknowledge and return to idle
                    // Real DMA functionality would be implemented here by connecting
                    // to actual memory controllers or system interfaces
                    tlp_state <= TLP_IDLE;
                end
            endcase
            
            // Update debug status with device ID and current state
            debug_status <= {{16'h{device_info['vendor_id']}, 8'h{device_info['device_id'][2:]}, 5'h0, tlp_state}};
        end
    end

endmodule
"""

    def _generate_device_tcl_script(self, device_info: Dict[str, Any]) -> str:
        """Generate device-specific TCL script using build step outputs."""

        # Determine FPGA part based on board
        board_parts = {
            "pcileech_35t325_x4": "xc7a35tcsg324-2",
            "pcileech_75t": "xc7a75tfgg484-2",
            "pcileech_100t": "xczu3eg-sbva484-1-e",
        }

        fpga_part = board_parts.get(self.board, "xc7a35tcsg324-2")

        # Get device-specific parameters
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        class_code = device_info["class_code"]
        revision_id = device_info["revision_id"]

        # Generate clean TCL script with device-specific configuration
        tcl_content = f"""#==============================================================================
# PCILeech Firmware Build Script
# Generated for device {vendor_id}:{device_id} (Class: {class_code})
# Board: {self.board}
# FPGA Part: {fpga_part}
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
#==============================================================================

# Set up build environment
set project_name "pcileech_firmware"
set project_dir "./vivado_project"
set output_dir "."

# Create project directory
file mkdir $project_dir

puts "Creating Vivado project for {self.board}..."
puts "Device: {vendor_id}:{device_id} (Class: {class_code})"

# Create project with correct FPGA part
create_project $project_name $project_dir -part {fpga_part} -force

# Set project properties
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]
set_property default_lib xil_defaultlib [current_project]

#==============================================================================
# PCIe IP Core Configuration
#==============================================================================
puts "Creating PCIe IP core for device {vendor_id}:{device_id}..."
puts "FPGA Part: {fpga_part}"
puts "Board: {self.board}"
"""

        # Generate appropriate PCIe IP configuration based on FPGA family
        if "xc7a35t" in fpga_part:
            # For Artix-7 35T, use AXI PCIe IP core which is available for smaller parts
            pcie_config = self._generate_axi_pcie_config(
                vendor_id, device_id, revision_id
            )
        elif "xc7a75t" in fpga_part or "xc7k" in fpga_part:
            # For Kintex-7 and larger Artix-7 parts, use pcie_7x IP core
            pcie_config = self._generate_pcie_7x_config(
                vendor_id, device_id, revision_id
            )
        elif "xczu" in fpga_part:
            # For Zynq UltraScale+, use PCIe UltraScale IP core
            pcie_config = self._generate_pcie_ultrascale_config(
                vendor_id, device_id, revision_id
            )
        else:
            # Default fallback to pcie_7x for unknown parts
            pcie_config = self._generate_pcie_7x_config(
                vendor_id, device_id, revision_id
            )

        tcl_content += f"""

{pcie_config}

#==============================================================================
# Source File Management
#==============================================================================
puts "Adding source files..."

# Add all SystemVerilog files
set sv_files [glob -nocomplain *.sv]
if {{[llength $sv_files] > 0}} {{
    puts "Found [llength $sv_files] SystemVerilog files"
    add_files -norecurse $sv_files
    set_property file_type SystemVerilog [get_files *.sv]
    foreach sv_file $sv_files {{
        puts "  - $sv_file"
    }}
}}

# Add all Verilog files
set v_files [glob -nocomplain *.v]
if {{[llength $v_files] > 0}} {{
    puts "Found [llength $v_files] Verilog files"
    add_files -norecurse $v_files
    foreach v_file $v_files {{
        puts "  - $v_file"
    }}
}}

# Add all constraint files
set xdc_files [glob -nocomplain *.xdc]
if {{[llength $xdc_files] > 0}} {{
    puts "Found [llength $xdc_files] constraint files"
    add_files -fileset constrs_1 -norecurse $xdc_files
    foreach xdc_file $xdc_files {{
        puts "  - $xdc_file"
    }}
}}

# Set top module
set top_module ""
if {{[file exists "pcileech_top.sv"]}} {{
    set top_module "pcileech_top"
}} elseif {{[file exists "pcileech_tlps128_bar_controller.sv"]}} {{
    set top_module "pcileech_tlps128_bar_controller"
}} else {{
    set top_files [glob -nocomplain "*top*.sv"]
    if {{[llength $top_files] > 0}} {{
        set top_file [lindex $top_files 0]
        set top_module [file rootname [file tail $top_file]]
    }} else {{
        puts "ERROR: No suitable top module found!"
        exit 1
    }}
}}

if {{$top_module != ""}} {{
    set_property top $top_module [current_fileset]
    puts "Set top module: $top_module"
}} else {{
    puts "ERROR: Failed to determine top module"
    exit 1
}}

#==============================================================================
# Device-Specific Timing Constraints
#==============================================================================
puts "Adding device-specific timing constraints..."
set timing_constraints {{
    # Clock constraints
    create_clock -period 10.000 -name sys_clk [get_ports clk]
    set_input_delay -clock sys_clk 2.000 [get_ports {{reset_n pcie_rx_*}}]
    set_output_delay -clock sys_clk 2.000 [get_ports {{pcie_tx_* msix_* debug_* device_ready}}]
    
    # Device-specific constraints for {vendor_id}:{device_id}
    # Board-specific pin assignments for {self.board}
    set_property PACKAGE_PIN E3 [get_ports clk]
    set_property IOSTANDARD LVCMOS33 [get_ports clk]
    set_property PACKAGE_PIN C12 [get_ports reset_n]
    set_property IOSTANDARD LVCMOS33 [get_ports reset_n]
}}

# Write timing constraints to file
set constraints_file "$project_dir/device_constraints.xdc"
set fp [open $constraints_file w]
puts $fp $timing_constraints
close $fp
add_files -fileset constrs_1 -norecurse $constraints_file

#==============================================================================
# Synthesis & Implementation
#==============================================================================
puts "Configuring synthesis settings..."
set_property strategy "Vivado Synthesis Defaults" [get_runs synth_1]
set_property steps.synth_design.args.directive "AreaOptimized_high" [get_runs synth_1]

puts "Starting synthesis..."
reset_run synth_1
launch_runs synth_1 -jobs 8
wait_on_run synth_1

if {{[get_property PROGRESS [get_runs synth_1]] != "100%"}} {{
    puts "ERROR: Synthesis failed!"
    exit 1
}}

puts "Synthesis completed successfully"
report_utilization -file utilization_synth.rpt

puts "Configuring implementation settings..."
set_property strategy "Performance_Explore" [get_runs impl_1]

puts "Starting implementation..."
launch_runs impl_1 -jobs 8
wait_on_run impl_1

if {{[get_property PROGRESS [get_runs impl_1]] != "100%"}} {{
    puts "ERROR: Implementation failed!"
    exit 1
}}

puts "Implementation completed successfully"

#==============================================================================
# Report Generation & Bitstream
#==============================================================================
puts "Generating reports..."
open_run impl_1
report_timing_summary -file timing_summary.rpt
report_utilization -file utilization_impl.rpt
report_power -file power_analysis.rpt
report_drc -file drc_report.rpt

puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1

# Check bitstream generation
set bitstream_file "$project_dir/$project_name.runs/impl_1/[get_property top [current_fileset]].bit"
if {{[file exists $bitstream_file]}} {{
    set output_bit "pcileech_{vendor_id}_{device_id}_{self.board}.bit"
    file copy -force $bitstream_file $output_bit
    puts "SUCCESS: Bitstream generated successfully!"
    puts "Output file: $output_bit"
    
    # Generate additional files
    write_cfgmem -format mcs -size 16 -interface SPIx4 \\
        -loadbit "up 0x0 $output_bit" \\
        -file "pcileech_{vendor_id}_{device_id}_{self.board}.mcs"
    
    if {{[llength [get_debug_cores]] > 0}} {{
        write_debug_probes -file "pcileech_{vendor_id}_{device_id}_{self.board}.ltx"
    }}
    
    write_checkpoint -force "pcileech_{vendor_id}_{device_id}_{self.board}.dcp"
    
    puts "Generated files:"
    puts "  - Bitstream: pcileech_{vendor_id}_{device_id}_{self.board}.bit"
    puts "  - MCS file: pcileech_{vendor_id}_{device_id}_{self.board}.mcs"
    puts "  - Checkpoint: pcileech_{vendor_id}_{device_id}_{self.board}.dcp"
    puts "  - Reports: *.rpt"
}} else {{
    puts "ERROR: Bitstream generation failed!"
    exit 1
}}

puts "Build completed successfully!"
close_project
"""

        return tcl_content

    def _generate_separate_tcl_files(self, device_info: Dict[str, Any]) -> List[str]:
        """Generate separate TCL files for different build components."""
        tcl_files = []

        # Generate project setup TCL
        project_tcl = self._generate_project_setup_tcl(device_info)
        project_path = self.output_dir / "01_project_setup.tcl"
        with open(project_path, "w") as f:
            f.write(project_tcl)
        tcl_files.append(str(project_path))
        logger.info("Generated project setup TCL")

        # Generate IP core configuration TCL
        ip_tcl = self._generate_ip_config_tcl(device_info)
        ip_path = self.output_dir / "02_ip_config.tcl"
        with open(ip_path, "w") as f:
            f.write(ip_tcl)
        tcl_files.append(str(ip_path))
        logger.info("Generated IP configuration TCL")

        # Generate source file management TCL
        sources_tcl = self._generate_sources_tcl(device_info)
        sources_path = self.output_dir / "03_add_sources.tcl"
        with open(sources_path, "w") as f:
            f.write(sources_tcl)
        tcl_files.append(str(sources_path))
        logger.info("Generated sources management TCL")

        # Generate constraints TCL
        constraints_tcl = self._generate_constraints_tcl(device_info)
        constraints_path = self.output_dir / "04_constraints.tcl"
        with open(constraints_path, "w") as f:
            f.write(constraints_tcl)
        tcl_files.append(str(constraints_path))
        logger.info("Generated constraints TCL")

        # Generate synthesis TCL
        synth_tcl = self._generate_synthesis_tcl(device_info)
        synth_path = self.output_dir / "05_synthesis.tcl"
        with open(synth_path, "w") as f:
            f.write(synth_tcl)
        tcl_files.append(str(synth_path))
        logger.info("Generated synthesis TCL")

        # Generate implementation TCL
        impl_tcl = self._generate_implementation_tcl(device_info)
        impl_path = self.output_dir / "06_implementation.tcl"
        with open(impl_path, "w") as f:
            f.write(impl_tcl)
        tcl_files.append(str(impl_path))
        logger.info("Generated implementation TCL")

        # Generate bitstream generation TCL
        bitstream_tcl = self._generate_bitstream_tcl(device_info)
        bitstream_path = self.output_dir / "07_bitstream.tcl"
        with open(bitstream_path, "w") as f:
            f.write(bitstream_tcl)
        tcl_files.append(str(bitstream_path))
        logger.info("Generated bitstream TCL")

        # Generate master build script that sources all others
        master_tcl = self._generate_master_build_tcl(device_info)
        master_path = self.output_dir / "build_all.tcl"
        with open(master_path, "w") as f:
            f.write(master_tcl)
        tcl_files.append(str(master_path))
        logger.info("Generated master build TCL")

        return tcl_files

    def _generate_project_setup_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate project setup TCL script."""
        board_parts = {
            "pcileech_35t325_x4": "xc7a35tcsg324-2",
            "pcileech_75t": "xc7a75tfgg484-2",
            "pcileech_100t": "xczu3eg-sbva484-1-e",
        }
        fpga_part = board_parts.get(self.board, "xc7a35tcsg324-2")
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        class_code = device_info["class_code"]

        return f"""#==============================================================================
# Project Setup - PCILeech Firmware Build
# Generated for device {vendor_id}:{device_id} (Class: {class_code})
# Board: {self.board}
# FPGA Part: {fpga_part}
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
#==============================================================================

# Set up build environment
set project_name "pcileech_firmware"
set project_dir "./vivado_project"
set output_dir "."

# Create project directory
file mkdir $project_dir

puts "Creating Vivado project for {self.board}..."
puts "Device: {vendor_id}:{device_id} (Class: {class_code})"

# Create project with correct FPGA part
create_project $project_name $project_dir -part {fpga_part} -force

# Set project properties
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]
set_property default_lib xil_defaultlib [current_project]

puts "Project setup completed successfully"
"""

    def _generate_ip_config_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate IP core configuration TCL script."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        revision_id = device_info["revision_id"]

        # Determine FPGA part based on board
        board_parts = {
            "pcileech_35t325_x4": "xc7a35tcsg324-2",
            "pcileech_75t": "xc7a75tfgg484-2",
            "pcileech_100t": "xczu3eg-sbva484-1-e",
        }
        fpga_part = board_parts.get(self.board, "xc7a35tcsg324-2")

        # Generate appropriate PCIe IP configuration based on FPGA family
        if "xczu" in fpga_part:
            # For Zynq UltraScale+, use PCIe UltraScale IP core
            pcie_config = self._generate_pcie_ultrascale_config(
                vendor_id, device_id, revision_id
            )
        elif "xc7a35t" in fpga_part:
            # For Artix-7 35T, use custom implementation (no IP cores)
            pcie_config = self._generate_axi_pcie_config(
                vendor_id, device_id, revision_id
            )
        else:
            # For larger 7-series parts, use pcie_7x IP core
            pcie_config = self._generate_pcie_7x_config(
                vendor_id, device_id, revision_id
            )

        return f"""#==============================================================================
# IP Core Configuration - PCIe Core Setup
# Device: {vendor_id}:{device_id}
# FPGA Part: {fpga_part}
# Board: {self.board}
#==============================================================================

puts "Creating PCIe IP core for device {vendor_id}:{device_id}..."
puts "FPGA Part: {fpga_part}"
puts "Board: {self.board}"

{pcie_config}

puts "PCIe IP core configuration completed"
"""

    def _generate_axi_pcie_config(
        self, vendor_id: str, device_id: str, revision_id: str
    ) -> str:
        """Generate custom PCIe configuration for Artix-7 35T parts (no IP cores needed)."""
        return f"""# Artix-7 35T PCIe Configuration
# This part uses custom SystemVerilog modules instead of Xilinx IP cores
# Device configuration: {vendor_id}:{device_id} (Rev: {revision_id})

# Set device-specific parameters for custom PCIe implementation
set DEVICE_ID 0x{device_id}
set VENDOR_ID 0x{vendor_id}
set REVISION_ID 0x{revision_id}
set SUBSYSTEM_VENDOR_ID 0x{vendor_id}
set SUBSYSTEM_ID 0x0000

puts "Using custom PCIe implementation for Artix-7 35T"
puts "Device ID: $DEVICE_ID"
puts "Vendor ID: $VENDOR_ID"
puts "Revision ID: $REVISION_ID"

# No IP cores required - PCIe functionality implemented in custom SystemVerilog modules"""

    def _generate_pcie_7x_config(
        self, vendor_id: str, device_id: str, revision_id: str
    ) -> str:
        """Generate PCIe 7-series IP configuration for Kintex-7 and larger parts."""
        return f"""# Create PCIe 7-series IP core
create_ip -name pcie_7x -vendor xilinx.com -library ip -module_name pcie_7x_0

# Configure PCIe IP core with device-specific settings
set_property -dict [list \\
    CONFIG.Bar0_Scale {{Kilobytes}} \\
    CONFIG.Bar0_Size {{128_KB}} \\
    CONFIG.Device_ID {{0x{device_id}}} \\
    CONFIG.Vendor_ID {{0x{vendor_id}}} \\
    CONFIG.Subsystem_Vendor_ID {{0x{vendor_id}}} \\
    CONFIG.Subsystem_ID {{0x0000}} \\
    CONFIG.Revision_ID {{0x{revision_id}}} \\
    CONFIG.Link_Speed {{2.5_GT/s}} \\
    CONFIG.Max_Link_Width {{X1}} \\
    CONFIG.Maximum_Link_Width {{X1}} \\
    CONFIG.Enable_Slot_Clock_Configuration {{false}} \\
    CONFIG.Legacy_Interrupt {{NONE}} \\
    CONFIG.MSI_Enabled {{false}} \\
    CONFIG.MSI_64b_Address_Capable {{false}} \\
    CONFIG.MSIX_Enabled {{true}} \\
] [get_ips pcie_7x_0]"""

    def _generate_pcie_ultrascale_config(
        self, vendor_id: str, device_id: str, revision_id: str
    ) -> str:
        """Generate PCIe UltraScale IP configuration for Zynq UltraScale+ parts."""
        return f"""# Create PCIe UltraScale IP core
create_ip -name pcie4_uscale_plus -vendor xilinx.com -library ip -module_name pcie4_uscale_plus_0

# Configure PCIe UltraScale IP core with device-specific settings
set_property -dict [list \\
    CONFIG.PL_LINK_CAP_MAX_LINK_SPEED {{2.5_GT/s}} \\
    CONFIG.PL_LINK_CAP_MAX_LINK_WIDTH {{X1}} \\
    CONFIG.AXISTEN_IF_EXT_512_RQ_STRADDLE {{false}} \\
    CONFIG.PF0_DEVICE_ID {{0x{device_id}}} \\
    CONFIG.PF0_VENDOR_ID {{0x{vendor_id}}} \\
    CONFIG.PF0_SUBSYSTEM_VENDOR_ID {{0x{vendor_id}}} \\
    CONFIG.PF0_SUBSYSTEM_ID {{0x0000}} \\
    CONFIG.PF0_REVISION_ID {{0x{revision_id}}} \\
    CONFIG.PF0_CLASS_CODE {{0x040300}} \\
    CONFIG.PF0_BAR0_SCALE {{Kilobytes}} \\
    CONFIG.PF0_BAR0_SIZE {{128}} \\
    CONFIG.PF0_MSI_ENABLED {{false}} \\
    CONFIG.PF0_MSIX_ENABLED {{true}} \\
] [get_ips pcie4_uscale_plus_0]"""

    def _generate_sources_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate source file management TCL script."""
        return """#==============================================================================
# Source File Management
#==============================================================================

puts "Adding source files..."

# Add all SystemVerilog files
set sv_files [glob -nocomplain *.sv]
if {[llength $sv_files] > 0} {
    puts "Found [llength $sv_files] SystemVerilog files"
    add_files -norecurse $sv_files
    set_property file_type SystemVerilog [get_files *.sv]
    foreach sv_file $sv_files {
        puts "  - $sv_file"
    }
}

# Add all Verilog files
set v_files [glob -nocomplain *.v]
if {[llength $v_files] > 0} {
    puts "Found [llength $v_files] Verilog files"
    add_files -norecurse $v_files
    foreach v_file $v_files {
        puts "  - $v_file"
    }
}

# Set top module
set top_module ""
if {[file exists "pcileech_top.sv"]} {
    set top_module "pcileech_top"
} elseif {[file exists "pcileech_tlps128_bar_controller.sv"]} {
    set top_module "pcileech_tlps128_bar_controller"
} else {
    set top_files [glob -nocomplain "*top*.sv"]
    if {[llength $top_files] > 0} {
        set top_file [lindex $top_files 0]
        set top_module [file rootname [file tail $top_file]]
    } else {
        puts "ERROR: No suitable top module found!"
        exit 1
    }
}

if {$top_module != ""} {
    set_property top $top_module [current_fileset]
    puts "Set top module: $top_module"
} else {
    puts "ERROR: Failed to determine top module"
    exit 1
}

puts "Source file management completed"
"""

    def _generate_constraints_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate constraints TCL script."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]

        return f"""#==============================================================================
# Constraints Management
# Device: {vendor_id}:{device_id}
# Board: {self.board}
#==============================================================================

puts "Adding constraint files..."

# Add all constraint files
set xdc_files [glob -nocomplain *.xdc]
if {{[llength $xdc_files] > 0}} {{
    puts "Found [llength $xdc_files] constraint files"
    add_files -fileset constrs_1 -norecurse $xdc_files
    foreach xdc_file $xdc_files {{
        puts "  - $xdc_file"
    }}
}}

# Generate device-specific timing constraints
puts "Adding device-specific timing constraints..."
set timing_constraints {{
    # Clock constraints
    create_clock -period 10.000 -name sys_clk [get_ports clk]
    set_input_delay -clock sys_clk 2.000 [get_ports {{reset_n pcie_rx_*}}]
    set_output_delay -clock sys_clk 2.000 [get_ports {{pcie_tx_* msix_* debug_* device_ready}}]
    
    # Device-specific constraints for {vendor_id}:{device_id}
    # Board-specific pin assignments for {self.board}
    set_property PACKAGE_PIN E3 [get_ports clk]
    set_property IOSTANDARD LVCMOS33 [get_ports clk]
    set_property PACKAGE_PIN C12 [get_ports reset_n]
    set_property IOSTANDARD LVCMOS33 [get_ports reset_n]
}}

# Write timing constraints to file
set constraints_file "$project_dir/device_constraints.xdc"
set fp [open $constraints_file w]
puts $fp $timing_constraints
close $fp
add_files -fileset constrs_1 -norecurse $constraints_file

puts "Constraints setup completed"
"""

    def _generate_synthesis_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate synthesis TCL script."""
        return """#==============================================================================
# Synthesis Configuration and Execution
#==============================================================================

puts "Configuring synthesis settings..."
set_property strategy "Vivado Synthesis Defaults" [get_runs synth_1]
set_property steps.synth_design.args.directive "AreaOptimized_high" [get_runs synth_1]

puts "Starting synthesis..."
reset_run synth_1
launch_runs synth_1 -jobs 8
wait_on_run synth_1

if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {
    puts "ERROR: Synthesis failed!"
    exit 1
}

puts "Synthesis completed successfully"
report_utilization -file utilization_synth.rpt
"""

    def _generate_implementation_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate implementation TCL script."""
        return """#==============================================================================
# Implementation Configuration and Execution
#==============================================================================

puts "Configuring implementation settings..."
set_property strategy "Performance_Explore" [get_runs impl_1]

puts "Starting implementation..."
launch_runs impl_1 -jobs 8
wait_on_run impl_1

if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {
    puts "ERROR: Implementation failed!"
    exit 1
}

puts "Implementation completed successfully"

# Generate implementation reports
puts "Generating reports..."
open_run impl_1
report_timing_summary -file timing_summary.rpt
report_utilization -file utilization_impl.rpt
report_power -file power_analysis.rpt
report_drc -file drc_report.rpt
"""

    def _generate_bitstream_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate bitstream generation TCL script."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]

        return f"""#==============================================================================
# Bitstream Generation
# Device: {vendor_id}:{device_id}
# Board: {self.board}
#==============================================================================

puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1

# Check bitstream generation
set bitstream_file "$project_dir/$project_name.runs/impl_1/[get_property top [current_fileset]].bit"
if {{[file exists $bitstream_file]}} {{
    set output_bit "pcileech_{vendor_id}_{device_id}_{self.board}.bit"
    file copy -force $bitstream_file $output_bit
    puts "SUCCESS: Bitstream generated successfully!"
    puts "Output file: $output_bit"
    
    # Generate additional files
    write_cfgmem -format mcs -size 16 -interface SPIx4 \\
        -loadbit "up 0x0 $output_bit" \\
        -file "pcileech_{vendor_id}_{device_id}_{self.board}.mcs"
    
    if {{[llength [get_debug_cores]] > 0}} {{
        write_debug_probes -file "pcileech_{vendor_id}_{device_id}_{self.board}.ltx"
    }}
    
    write_checkpoint -force "pcileech_{vendor_id}_{device_id}_{self.board}.dcp"
    
    puts "Generated files:"
    puts "  - Bitstream: pcileech_{vendor_id}_{device_id}_{self.board}.bit"
    puts "  - MCS file: pcileech_{vendor_id}_{device_id}_{self.board}.mcs"
    puts "  - Checkpoint: pcileech_{vendor_id}_{device_id}_{self.board}.dcp"
    puts "  - Reports: *.rpt"
}} else {{
    puts "ERROR: Bitstream generation failed!"
    exit 1
}}

puts "Bitstream generation completed successfully!"
"""

    def _generate_master_build_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate master build script that sources all other TCL files."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        class_code = device_info["class_code"]

        return f"""#==============================================================================
# Master Build Script - PCILeech Firmware
# Generated for device {vendor_id}:{device_id} (Class: {class_code})
# Board: {self.board}
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
#==============================================================================

puts "Starting PCILeech firmware build process..."
puts "Device: {vendor_id}:{device_id} (Class: {class_code})"
puts "Board: {self.board}"
puts ""

# Source all build scripts in order
set build_scripts [list \\
    "01_project_setup.tcl" \\
    "02_ip_config.tcl" \\
    "03_add_sources.tcl" \\
    "04_constraints.tcl" \\
    "05_synthesis.tcl" \\
    "06_implementation.tcl" \\
    "07_bitstream.tcl" \\
]

foreach script $build_scripts {{
    if {{[file exists $script]}} {{
        puts "Executing: $script"
        source $script
        puts "Completed: $script"
        puts ""
    }} else {{
        puts "ERROR: Required script not found: $script"
        exit 1
    }}
}}

puts "Build process completed successfully!"
close_project
"""

    def _apply_manufacturing_variance(self, device_info: Dict[str, Any]) -> List[str]:
        """Apply manufacturing variance simulation."""
        variance_files = []

        try:
            if not DeviceClass or not VarianceModel:
                logger.warning("Manufacturing variance modules not available")
                return variance_files

            # Determine device class based on actual enum values
            class_code = int(device_info["class_code"], 16)
            if class_code == 0x0200:  # Ethernet
                device_class = DeviceClass.ENTERPRISE
            elif class_code == 0x0403:  # Audio
                device_class = DeviceClass.CONSUMER
            else:
                device_class = DeviceClass.CONSUMER

            # Create variance model
            variance_model = VarianceModel(
                device_id=device_info["device_id"],
                device_class=device_class,
                base_frequency_mhz=100.0,  # Default frequency
                clock_jitter_percent=2.5,
                register_timing_jitter_ns=25.0,
                power_noise_percent=2.0,
                temperature_drift_ppm_per_c=50.0,
                process_variation_percent=10.0,
                propagation_delay_ps=100.0,
            )

            # Save variance data
            variance_data = {
                "device_class": device_class.value,
                "variance_model": {
                    "device_id": variance_model.device_id,
                    "device_class": variance_model.device_class.value,
                    "base_frequency_mhz": variance_model.base_frequency_mhz,
                    "clock_jitter_percent": variance_model.clock_jitter_percent,
                    "register_timing_jitter_ns": variance_model.register_timing_jitter_ns,
                    "power_noise_percent": variance_model.power_noise_percent,
                    "temperature_drift_ppm_per_c": variance_model.temperature_drift_ppm_per_c,
                    "process_variation_percent": variance_model.process_variation_percent,
                    "propagation_delay_ps": variance_model.propagation_delay_ps,
                },
            }

            variance_file = self.output_dir / "manufacturing_variance.json"
            with open(variance_file, "w") as f:
                json.dump(variance_data, f, indent=2)
            variance_files.append(str(variance_file))

            logger.info(f"Applied manufacturing variance for {device_class.value}")

        except Exception as e:
            logger.error(f"Error applying manufacturing variance: {e}")

        return variance_files

    def run_behavior_profiling(
        self, device_info: Dict[str, Any], duration: int = 30
    ) -> Optional[str]:
        """Run behavior profiling if available."""
        if not BehaviorProfiler:
            logger.warning("Behavior profiler not available")
            return None

        try:
            logger.info(f"Starting behavior profiling for {duration} seconds")
            self.behavior_profiler = BehaviorProfiler(self.bdf)

            # Capture behavior profile
            profile_data = self.behavior_profiler.capture_behavior_profile(duration)

            # Convert to serializable format
            profile_dict = {
                "device_bdf": profile_data.device_bdf,
                "capture_duration": profile_data.capture_duration,
                "total_accesses": profile_data.total_accesses,
                "register_accesses": [
                    {
                        "timestamp": access.timestamp,
                        "register": access.register,
                        "offset": access.offset,
                        "operation": access.operation,
                        "value": access.value,
                        "duration_us": access.duration_us,
                    }
                    for access in profile_data.register_accesses
                ],
                "timing_patterns": [
                    {
                        "pattern_type": pattern.pattern_type,
                        "registers": pattern.registers,
                        "avg_interval_us": pattern.avg_interval_us,
                        "std_deviation_us": pattern.std_deviation_us,
                        "frequency_hz": pattern.frequency_hz,
                        "confidence": pattern.confidence,
                    }
                    for pattern in profile_data.timing_patterns
                ],
                "state_transitions": profile_data.state_transitions,
                "power_states": profile_data.power_states,
                "interrupt_patterns": profile_data.interrupt_patterns,
            }

            # Save profile data
            profile_file = self.output_dir / "behavior_profile.json"
            with open(profile_file, "w") as f:
                json.dump(profile_dict, f, indent=2)

            logger.info(f"Behavior profiling completed, saved to {profile_file}")
            return str(profile_file)

        except Exception as e:
            logger.error(f"Error during behavior profiling: {e}")
            return None

    def generate_build_files(self, device_info: Dict[str, Any]) -> List[str]:
        """Generate separate build files (TCL scripts, makefiles, etc.)."""
        build_files = []

        # Clean up any old unified TCL files first
        old_unified_files = [
            self.output_dir / "build_unified.tcl",
            self.output_dir / "unified_build.tcl",
            self.output_dir
            / "build_firmware.tcl",  # Remove the old monolithic file too
        ]
        for old_file in old_unified_files:
            if old_file.exists():
                old_file.unlink()
                logger.info(f"Removed old unified file: {old_file.name}")

        # Generate separate TCL files for different components
        tcl_files = self._generate_separate_tcl_files(device_info)
        build_files.extend(tcl_files)

        # Generate project file
        project_file = self._generate_project_file(device_info)
        proj_file = self.output_dir / "firmware_project.json"
        with open(proj_file, "w") as f:
            json.dump(project_file, f, indent=2)
        build_files.append(str(proj_file))

        # Generate file manifest for verification
        manifest = self._generate_file_manifest(device_info)
        manifest_file = self.output_dir / "file_manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)
        build_files.append(str(manifest_file))

        logger.info(f"Generated {len(build_files)} build files")
        return build_files

    def _generate_project_file(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project configuration file."""
        return {
            "project_name": "pcileech_firmware",
            "board": self.board,
            "device_info": device_info,
            "build_timestamp": time.time(),
            "build_version": "1.0.0",
            "features": {
                "advanced_sv": hasattr(self, "sv_generator")
                and self.sv_generator is not None,
                "manufacturing_variance": hasattr(self, "variance_simulator")
                and self.variance_simulator is not None,
                "behavior_profiling": hasattr(self, "behavior_profiler")
                and self.behavior_profiler is not None,
            },
        }

    def _generate_file_manifest(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a manifest of all files for verification."""
        manifest = {
            "project_info": {
                "device": f"{device_info['vendor_id']}:{device_info['device_id']}",
                "board": self.board,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "files": {
                "systemverilog": [],
                "verilog": [],
                "constraints": [],
                "tcl_scripts": [],
                "generated": [],
            },
            "validation": {
                "required_files_present": True,
                "top_module_identified": False,
                "build_script_ready": False,
            },
        }

        # Check for files in output directory
        output_files = list(self.output_dir.glob("*"))

        for file_path in output_files:
            if file_path.suffix == ".sv":
                manifest["files"]["systemverilog"].append(file_path.name)
                if "top" in file_path.name.lower():
                    manifest["validation"]["top_module_identified"] = True
            elif file_path.suffix == ".v":
                manifest["files"]["verilog"].append(file_path.name)
            elif file_path.suffix == ".xdc":
                manifest["files"]["constraints"].append(file_path.name)
            elif file_path.suffix == ".tcl":
                manifest["files"]["tcl_scripts"].append(file_path.name)
                if "build" in file_path.name:
                    manifest["validation"]["build_script_ready"] = True
            elif file_path.suffix == ".json":
                manifest["files"]["generated"].append(file_path.name)

        # Validate required files
        required_files = ["device_config.sv", "pcileech_top.sv"]
        manifest["validation"]["required_files_present"] = all(
            f in manifest["files"]["systemverilog"] for f in required_files
        )

        return manifest

    def _cleanup_intermediate_files(self) -> List[str]:
        """Clean up intermediate files, keeping only final outputs and logs."""
        preserved_files = []
        cleaned_files = []

        # Define patterns for files to preserve
        preserve_patterns = [
            "*.bit",  # Final bitstream
            "*.mcs",  # Flash memory file
            "*.ltx",  # Debug probes
            "*.dcp",  # Design checkpoint
            "*.log",  # Log files
            "*.rpt",  # Report files
            "build_firmware.tcl",  # Final TCL build script
            "*.tcl",  # All TCL files (preserve in-place)
            "*.sv",  # SystemVerilog source files (needed for build)
            "*.v",  # Verilog source files (needed for build)
            "*.xdc",  # Constraint files (needed for build)
        ]

        # Define patterns for files/directories to clean
        cleanup_patterns = [
            "vivado_project/",  # Vivado project directory
            "project_dir/",  # Alternative project directory
            "*.json",  # JSON files (intermediate)
            "*.jou",  # Vivado journal files
            "*.str",  # Vivado strategy files
            ".Xil/",  # Xilinx temporary directory
        ]

        logger.info("Starting cleanup of intermediate files...")

        try:
            import fnmatch
            import shutil

            # Get all files in output directory
            all_files = list(self.output_dir.rglob("*"))

            for file_path in all_files:
                should_preserve = False

                # Check if file should be preserved
                for pattern in preserve_patterns:
                    if fnmatch.fnmatch(file_path.name, pattern):
                        should_preserve = True
                        preserved_files.append(str(file_path))
                        break

                # If not preserved, check if it should be cleaned
                if not should_preserve:
                    # Handle cleanup patterns
                    for pattern in cleanup_patterns:
                        if pattern.endswith("/"):
                            # Directory pattern
                            if file_path.is_dir() and fnmatch.fnmatch(
                                file_path.name + "/", pattern
                            ):
                                try:
                                    shutil.rmtree(file_path)
                                    cleaned_files.append(str(file_path))
                                    logger.info(f"Cleaned directory: {file_path.name}")
                                except Exception as e:
                                    logger.warning(
                                        f"Could not clean directory {file_path.name}: {e}"
                                    )
                                break
                        else:
                            # File pattern
                            if file_path.is_file() and fnmatch.fnmatch(
                                file_path.name, pattern
                            ):
                                try:
                                    file_path.unlink()
                                    cleaned_files.append(str(file_path))
                                    logger.debug(f"Cleaned file: {file_path.name}")
                                except Exception as e:
                                    logger.warning(
                                        f"Could not clean file {file_path.name}: {e}"
                                    )
                                break

            logger.info(
                f"Cleanup completed: preserved {len(preserved_files)} files, cleaned {len(cleaned_files)} items"
            )

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

        return preserved_files

    def _validate_final_outputs(self) -> Dict[str, Any]:
        """Validate and provide information about final output files."""
        validation_results = {
            "bitstream_info": None,
            "flash_file_info": None,
            "debug_file_info": None,
            "tcl_file_info": None,
            "reports_info": [],
            "validation_status": "unknown",
            "file_sizes": {},
            "checksums": {},
            "build_mode": "unknown",
        }

        try:
            import hashlib

            # Check for TCL build file (main output when Vivado not available)
            tcl_files = list(self.output_dir.glob("build_firmware.tcl"))
            if tcl_files:
                tcl_file = tcl_files[0]
                file_size = tcl_file.stat().st_size

                with open(tcl_file, "r") as f:
                    content = f.read()
                    file_hash = hashlib.sha256(content.encode()).hexdigest()

                validation_results["tcl_file_info"] = {
                    "filename": tcl_file.name,
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 2),
                    "sha256": file_hash,
                    "has_device_config": "CONFIG.Device_ID" in content,
                    "has_synthesis": "launch_runs synth_1" in content,
                    "has_implementation": "launch_runs impl_1" in content,
                }
                validation_results["file_sizes"][tcl_file.name] = file_size
                validation_results["checksums"][tcl_file.name] = file_hash

            # Check for bitstream file (only if Vivado was run)
            bitstream_files = list(self.output_dir.glob("*.bit"))
            if bitstream_files:
                bitstream_file = bitstream_files[0]
                file_size = bitstream_file.stat().st_size

                # Calculate checksum
                with open(bitstream_file, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()

                validation_results["bitstream_info"] = {
                    "filename": bitstream_file.name,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "sha256": file_hash,
                    "created": bitstream_file.stat().st_mtime,
                }
                validation_results["file_sizes"][bitstream_file.name] = file_size
                validation_results["checksums"][bitstream_file.name] = file_hash
                validation_results["build_mode"] = "full_vivado"
            else:
                validation_results["build_mode"] = "tcl_only"

            # Check for MCS flash file
            mcs_files = list(self.output_dir.glob("*.mcs"))
            if mcs_files:
                mcs_file = mcs_files[0]
                file_size = mcs_file.stat().st_size

                with open(mcs_file, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()

                validation_results["flash_file_info"] = {
                    "filename": mcs_file.name,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "sha256": file_hash,
                }
                validation_results["file_sizes"][mcs_file.name] = file_size
                validation_results["checksums"][mcs_file.name] = file_hash

            # Check for debug file
            ltx_files = list(self.output_dir.glob("*.ltx"))
            if ltx_files:
                ltx_file = ltx_files[0]
                file_size = ltx_file.stat().st_size

                validation_results["debug_file_info"] = {
                    "filename": ltx_file.name,
                    "size_bytes": file_size,
                }
                validation_results["file_sizes"][ltx_file.name] = file_size

            # Check for report files
            report_files = list(self.output_dir.glob("*.rpt"))
            for report_file in report_files:
                file_size = report_file.stat().st_size
                validation_results["reports_info"].append(
                    {
                        "filename": report_file.name,
                        "size_bytes": file_size,
                        "type": self._determine_report_type(report_file.name),
                    }
                )
                validation_results["file_sizes"][report_file.name] = file_size

            # Determine overall validation status
            if validation_results["tcl_file_info"]:
                if validation_results["build_mode"] == "full_vivado":
                    # Full Vivado build - check bitstream
                    if validation_results["bitstream_info"]:
                        if (
                            validation_results["bitstream_info"]["size_bytes"] > 1000000
                        ):  # > 1MB
                            validation_results["validation_status"] = (
                                "success_full_build"
                            )
                        else:
                            validation_results["validation_status"] = (
                                "warning_small_bitstream"
                            )
                    else:
                        validation_results["validation_status"] = "failed_no_bitstream"
                else:
                    # TCL-only build - check TCL file quality (this is the main output)
                    tcl_info = validation_results["tcl_file_info"]
                    if tcl_info["has_device_config"] and tcl_info["size_bytes"] > 1000:
                        validation_results["validation_status"] = "success_tcl_ready"
                    else:
                        validation_results["validation_status"] = (
                            "warning_incomplete_tcl"
                        )
            else:
                validation_results["validation_status"] = "failed_no_tcl"

        except Exception as e:
            logger.error(f"Error during output validation: {e}")
            validation_results["validation_status"] = "error"

        return validation_results

    def _determine_report_type(self, filename: str) -> str:
        """Determine the type of report based on filename."""
        if "timing" in filename.lower():
            return "timing_analysis"
        elif "utilization" in filename.lower():
            return "resource_utilization"
        elif "power" in filename.lower():
            return "power_analysis"
        elif "drc" in filename.lower():
            return "design_rule_check"
        else:
            return "general"

    def build_firmware(
        self,
        advanced_sv: bool = False,
        device_type: Optional[str] = None,
        enable_variance: bool = False,
        behavior_profile_duration: int = 30,
    ) -> Dict[str, Any]:
        """Main firmware build process."""
        logger.info("Starting firmware build process")
        build_results = {
            "success": False,
            "files_generated": [],
            "errors": [],
            "build_time": 0,
        }

        start_time = time.time()

        try:
            # Step 1: Read configuration space
            logger.info("Step 1: Reading device configuration space")
            config_space = self.read_vfio_config_space()

            # Step 2: Extract device information
            logger.info("Step 2: Extracting device information")
            device_info = self.extract_device_info(config_space)

            # Step 3: Generate SystemVerilog files
            logger.info("Step 3: Generating SystemVerilog files")
            sv_files = self.generate_systemverilog_files(
                device_info, advanced_sv, device_type, enable_variance
            )
            build_results["files_generated"].extend(sv_files)

            # Step 4: Run behavior profiling if requested
            if behavior_profile_duration > 0:
                logger.info("Step 4: Running behavior profiling")
                profile_file = self.run_behavior_profiling(
                    device_info, behavior_profile_duration
                )
                if profile_file:
                    build_results["files_generated"].append(profile_file)

            # Step 5: Generate build files
            logger.info("Step 5: Generating build files")
            build_files = self.generate_build_files(device_info)
            build_results["files_generated"].extend(build_files)

            # Step 6: Save device info
            device_info_file = self.output_dir / "device_info.json"
            with open(device_info_file, "w") as f:
                json.dump(device_info, f, indent=2)
            build_results["files_generated"].append(str(device_info_file))

            # Step 7: Clean up intermediate files
            logger.info("Step 7: Cleaning up intermediate files")
            preserved_files = self._cleanup_intermediate_files()

            # Step 8: Validate final outputs
            logger.info("Step 8: Validating final outputs")
            validation_results = self._validate_final_outputs()

            build_results["success"] = True
            build_results["build_time"] = time.time() - start_time
            build_results["preserved_files"] = preserved_files
            build_results["validation"] = validation_results

            logger.info(
                f"Firmware build completed successfully in {build_results['build_time']:.2f} seconds"
            )
            logger.info(f"Generated {len(build_results['files_generated'])} files")
            logger.info(f"Preserved {len(preserved_files)} final output files")

            # Print detailed validation information
            self._print_final_output_info(validation_results)

        except Exception as e:
            error_msg = f"Build failed: {e}"
            logger.error(error_msg)
            build_results["errors"].append(error_msg)
            build_results["build_time"] = time.time() - start_time

        return build_results

    def _print_final_output_info(self, validation_results: Dict[str, Any]):
        """Print detailed information about final output files."""
        print("\n" + "=" * 80)
        print("FINAL BUILD OUTPUT VALIDATION")
        print("=" * 80)

        build_mode = validation_results.get("build_mode", "unknown")
        status = validation_results["validation_status"]

        # Display build status
        if status == "success_full_build":
            print("✅ BUILD STATUS: SUCCESS (Full Vivado Build)")
        elif status == "success_tcl_ready":
            print("✅ BUILD STATUS: SUCCESS (TCL Build Script Ready)")
        elif status == "warning_small_bitstream":
            print("⚠️  BUILD STATUS: WARNING - Bitstream file is unusually small")
        elif status == "warning_incomplete_tcl":
            print("⚠️  BUILD STATUS: WARNING - TCL script may be incomplete")
        elif status == "failed_no_bitstream":
            print("❌ BUILD STATUS: FAILED - No bitstream file generated")
        elif status == "failed_no_tcl":
            print("❌ BUILD STATUS: FAILED - No TCL build script generated")
        else:
            print("❌ BUILD STATUS: ERROR - Validation failed")

        print(f"\n🔧 BUILD MODE: {build_mode.replace('_', ' ').title()}")

        # TCL file information (always show if present)
        if validation_results.get("tcl_file_info"):
            info = validation_results["tcl_file_info"]
            print(f"\n📜 BUILD SCRIPT:")
            print(f"   File: {info['filename']}")
            print(f"   Size: {info['size_kb']} KB ({info['size_bytes']:,} bytes)")
            print(f"   SHA256: {info['sha256'][:16]}...")

            # TCL script validation
            features = []
            if info["has_device_config"]:
                features.append("✅ Device-specific configuration")
            else:
                features.append("❌ Missing device configuration")

            if info["has_synthesis"]:
                features.append("✅ Synthesis commands")
            else:
                features.append("⚠️  No synthesis commands")

            if info["has_implementation"]:
                features.append("✅ Implementation commands")
            else:
                features.append("⚠️  No implementation commands")

            print("   Features:")
            for feature in features:
                print(f"     {feature}")

        # Bitstream information (only if Vivado was run)
        if validation_results.get("bitstream_info"):
            info = validation_results["bitstream_info"]
            print(f"\n📁 BITSTREAM FILE:")
            print(f"   File: {info['filename']}")
            print(f"   Size: {info['size_mb']} MB ({info['size_bytes']:,} bytes)")
            print(f"   SHA256: {info['sha256'][:16]}...")

            # Validate bitstream size
            if info["size_mb"] < 0.5:
                print("   ⚠️  WARNING: Bitstream is very small, may be incomplete")
            elif info["size_mb"] > 10:
                print("   ⚠️  WARNING: Bitstream is very large, check for issues")
            else:
                print("   ✅ Bitstream size looks normal")

        # Flash file information
        if validation_results.get("flash_file_info"):
            info = validation_results["flash_file_info"]
            print(f"\n💾 FLASH FILE:")
            print(f"   File: {info['filename']}")
            print(f"   Size: {info['size_mb']} MB ({info['size_bytes']:,} bytes)")
            print(f"   SHA256: {info['sha256'][:16]}...")

        # Debug file information
        if validation_results.get("debug_file_info"):
            info = validation_results["debug_file_info"]
            print(f"\n🔍 DEBUG FILE:")
            print(f"   File: {info['filename']}")
            print(f"   Size: {info['size_bytes']:,} bytes")

        # Report files
        if validation_results.get("reports_info"):
            print(f"\n📊 ANALYSIS REPORTS:")
            for report in validation_results["reports_info"]:
                print(
                    f"   {report['filename']} ({report['type']}) - {report['size_bytes']:,} bytes"
                )

        # File checksums for verification
        if validation_results.get("checksums"):
            print(f"\n🔐 FILE CHECKSUMS (for verification):")
            for filename, checksum in validation_results["checksums"].items():
                print(f"   {filename}: {checksum}")

        print("\n" + "=" * 80)
        if build_mode == "tcl_only":
            print("TCL build script is ready! Run with Vivado to generate bitstream.")
        else:
            print("Build output files are ready for deployment!")
        print("=" * 80 + "\n")


def main():
    """Main entry point for the build system."""
    parser = argparse.ArgumentParser(
        description="PCILeech FPGA Firmware Builder - Production System"
    )
    parser.add_argument(
        "--bdf", required=True, help="Bus:Device.Function (e.g., 0000:03:00.0)"
    )
    parser.add_argument("--board", required=True, help="Target board")
    parser.add_argument(
        "--advanced-sv",
        action="store_true",
        help="Enable advanced SystemVerilog generation",
    )
    parser.add_argument(
        "--device-type",
        help="Device type for optimizations (network, audio, storage, etc.)",
    )
    parser.add_argument(
        "--enable-variance",
        action="store_true",
        help="Enable manufacturing variance simulation",
    )
    parser.add_argument(
        "--behavior-profile-duration",
        type=int,
        default=30,
        help="Duration for behavior profiling in seconds (0 to disable)",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize builder
        builder = PCILeechFirmwareBuilder(args.bdf, args.board)

        # Run build process
        results = builder.build_firmware(
            advanced_sv=args.advanced_sv,
            device_type=args.device_type,
            enable_variance=args.enable_variance,
            behavior_profile_duration=args.behavior_profile_duration,
        )

        # Print results
        if results["success"]:
            print(
                f"[✓] Build completed successfully in {results['build_time']:.2f} seconds"
            )

            # Show preserved files (final outputs)
            if "preserved_files" in results and results["preserved_files"]:
                print(f"[✓] Final output files ({len(results['preserved_files'])}):")
                for file_path in results["preserved_files"]:
                    print(f"    - {file_path}")

            # Validation results are already printed by _print_final_output_info

            return 0
        else:
            print(f"[✗] Build failed after {results['build_time']:.2f} seconds")
            for error in results["errors"]:
                print(f"    Error: {error}")
            return 1

    except KeyboardInterrupt:
        print("\n[!] Build interrupted by user")
        return 130
    except Exception as e:
        print(f"[✗] Fatal error: {e}")
        logger.exception("Fatal error during build")
        return 1


if __name__ == "__main__":
    sys.exit(main())
