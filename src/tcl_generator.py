#!/usr/bin/env python3
"""
TCL Script Generation Module

Handles generation of TCL build scripts for PCILeech firmware building.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List

try:
    from string_utils import generate_tcl_header_comment, log_info_safe, safe_format
except ImportError:
    # Fallback if string_utils is not available
    def log_info_safe(logger, template, **kwargs):
        logger.info(template.format(**kwargs))

    def safe_format(template, **kwargs):
        return template.format(**kwargs)

    def generate_tcl_header_comment(title, **kwargs):
        return f"#==============================================================================\n# {title}\n#=============================================================================="


logger = logging.getLogger(__name__)


class TCLGenerator:
    """Generates TCL build scripts for PCILeech firmware."""

    def __init__(self, board: str, output_dir: Path):
        self.board = board
        self.output_dir = output_dir

    def generate_device_tcl_script(self, device_info: Dict[str, Any]) -> str:
        """Generate device-specific TCL script using build step outputs."""

        # Determine FPGA part based on board
        board_parts = {
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

        fpga_part = board_parts.get(self.board, "xc7a35tcsg324-2")

        # Get device-specific parameters
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        class_code = device_info["class_code"]
        revision_id = device_info["revision_id"]

        # Generate clean TCL script with device-specific configuration
        header = generate_tcl_header_comment(
            "PCILeech Firmware Build Script",
            vendor_id=vendor_id,
            device_id=device_id,
            class_code=class_code,
            board=self.board,
            fpga_part=fpga_part,
            generated=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        tcl_header_template = safe_format(
            """{header}

# Set up build environment
set project_name "pcileech_firmware"
set project_dir "./vivado_project"
set output_dir "."

# Create project directory
file mkdir $project_dir

puts "Creating Vivado project for {board}..."
puts "Device: {vendor_id}:{device_id} (Class: {class_code})"

# Create project with correct FPGA part
create_project $project_name $project_dir -part {fpga_part} -force

# Set project properties
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]
set_property default_lib xil_defaultlib [current_project]

{pcie_header}
puts "Creating PCIe IP core for device {vendor_id}:{device_id}..."
puts "FPGA Part: {fpga_part}"
puts "Board: {board}"
""",
            header=header,
            board=self.board,
            vendor_id=vendor_id,
            device_id=device_id,
            class_code=class_code,
            fpga_part=fpga_part,
            pcie_header=generate_tcl_header_comment("PCIe IP Core Configuration"),
        )

        # Format the header using safe_format
        tcl_content = safe_format(
            tcl_header_template,
            vendor_id=vendor_id,
            device_id=device_id,
            class_code=class_code,
            board=self.board,
            fpga_part=fpga_part,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Generate appropriate PCIe IP configuration based on FPGA family
        if "xc7a35t" in fpga_part:
            # For Artix-7 35T, use AXI PCIe IP core which is available for smaller parts
            pcie_config = self.generate_axi_pcie_config(
                vendor_id, device_id, revision_id
            )
        elif "xc7a75t" in fpga_part or "xc7k" in fpga_part:
            # For Kintex-7 and larger Artix-7 parts, use pcie_7x IP core
            pcie_config = self.generate_pcie_7x_config(
                vendor_id, device_id, revision_id
            )
        elif "xczu" in fpga_part:
            # For Zynq UltraScale+, use PCIe UltraScale IP core
            pcie_config = self.generate_pcie_ultrascale_config(
                vendor_id, device_id, revision_id
            )
        else:
            # Default fallback to pcie_7x for unknown parts
            pcie_config = self.generate_pcie_7x_config(
                vendor_id, device_id, revision_id
            )

        # Add the PCIe configuration and remaining content
        tcl_content += safe_format(
            """

{pcie_config}

{generate_tcl_header_comment("Source File Management")}
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
        set top_module [file rootname [file tail [lindex $top_files 0]]]
    }}
}}

if {{$top_module ne ""}} {{
    puts "Setting top module: $top_module"
    set_property top $top_module [current_fileset]
}} else {{
    puts "WARNING: No top module found, using default"
}}

{generate_tcl_header_comment("Synthesis")}
puts "Starting synthesis..."
launch_runs synth_1 -jobs 8
wait_on_run synth_1

if {{[get_property PROGRESS [get_runs synth_1]] != "100%"}} {{
    puts "ERROR: Synthesis failed!"
    exit 1
}}

{generate_tcl_header_comment("Implementation")}
puts "Starting implementation..."
launch_runs impl_1 -jobs 8
wait_on_run impl_1

if {{[get_property PROGRESS [get_runs impl_1]] != "100%"}} {{
    puts "ERROR: Implementation failed!"
    exit 1
}}

{generate_tcl_header_comment("Bitstream Generation")}
puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1

if {{[get_property PROGRESS [get_runs impl_1]] != "100%"}} {{
    puts "ERROR: Bitstream generation failed!"
    exit 1
}}

puts "Build completed successfully!"
close_project
""",
            pcie_config=pcie_config,
        )

        return tcl_content

    def generate_separate_tcl_files(self, device_info: Dict[str, Any]) -> List[str]:
        """Generate separate TCL files for different build components."""
        tcl_files = []

        # Generate project setup TCL
        project_tcl = self.generate_project_setup_tcl(device_info)
        project_path = self.output_dir / "01_project_setup.tcl"
        with open(project_path, "w") as f:
            f.write(project_tcl)
        tcl_files.append(str(project_path))
        logger.info("Generated project setup TCL")

        # Generate IP core configuration TCL
        ip_tcl = self.generate_ip_config_tcl(device_info)
        ip_path = self.output_dir / "02_ip_config.tcl"
        with open(ip_path, "w") as f:
            f.write(ip_tcl)
        tcl_files.append(str(ip_path))
        logger.info("Generated IP configuration TCL")

        # Generate source file management TCL
        sources_tcl = self.generate_sources_tcl(device_info)
        sources_path = self.output_dir / "03_add_sources.tcl"
        with open(sources_path, "w") as f:
            f.write(sources_tcl)
        tcl_files.append(str(sources_path))
        logger.info("Generated sources management TCL")

        # Generate constraints TCL
        constraints_tcl = self.generate_constraints_tcl(device_info)
        constraints_path = self.output_dir / "04_constraints.tcl"
        with open(constraints_path, "w") as f:
            f.write(constraints_tcl)
        tcl_files.append(str(constraints_path))
        logger.info("Generated constraints TCL")

        # Generate synthesis TCL
        synth_tcl = self.generate_synthesis_tcl(device_info)
        synth_path = self.output_dir / "05_synthesis.tcl"
        with open(synth_path, "w") as f:
            f.write(synth_tcl)
        tcl_files.append(str(synth_path))
        logger.info("Generated synthesis TCL")

        # Generate implementation TCL
        impl_tcl = self.generate_implementation_tcl(device_info)
        impl_path = self.output_dir / "06_implementation.tcl"
        with open(impl_path, "w") as f:
            f.write(impl_tcl)
        tcl_files.append(str(impl_path))
        logger.info("Generated implementation TCL")

        # Generate bitstream generation TCL
        bitstream_tcl = self.generate_bitstream_tcl(device_info)
        bitstream_path = self.output_dir / "07_bitstream.tcl"
        with open(bitstream_path, "w") as f:
            f.write(bitstream_tcl)
        tcl_files.append(str(bitstream_path))
        logger.info("Generated bitstream TCL")

        # Generate master build script that sources all others
        master_tcl = self.generate_master_build_tcl(device_info)
        master_path = self.output_dir / "build_all.tcl"
        with open(master_path, "w") as f:
            f.write(master_tcl)
        tcl_files.append(str(master_path))
        logger.info("Generated master build TCL")

        return tcl_files

    def generate_project_setup_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate project setup TCL script."""
        board_parts = {
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
        fpga_part = board_parts.get(self.board, "xc7a35tcsg324-2")
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        class_code = device_info["class_code"]

        header = generate_tcl_header_comment(
            "Project Setup - PCILeech Firmware Build",
            vendor_id=vendor_id,
            device_id=device_id,
            class_code=class_code,
            board=self.board,
            fpga_part=fpga_part,
            generated=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        return f"""{header}

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

    def generate_ip_config_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate IP core configuration TCL script."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        revision_id = device_info["revision_id"]

        # Determine FPGA part based on board
        board_parts = {
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
        fpga_part = board_parts.get(self.board, "xc7a35tcsg324-2")

        # Generate appropriate PCIe IP configuration based on FPGA family
        if "xczu" in fpga_part:
            # For Zynq UltraScale+, use PCIe UltraScale IP core
            pcie_config = self.generate_pcie_ultrascale_config(
                vendor_id, device_id, revision_id
            )
        elif "xc7a35t" in fpga_part:
            # For Artix-7 35T, use custom implementation (no IP cores)
            pcie_config = self.generate_axi_pcie_config(
                vendor_id, device_id, revision_id
            )
        else:
            # For larger 7-series parts, use pcie_7x IP core
            pcie_config = self.generate_pcie_7x_config(
                vendor_id, device_id, revision_id
            )

        header = generate_tcl_header_comment(
            "IP Core Configuration - PCIe Core Setup",
            vendor_id=vendor_id,
            device_id=device_id,
            fpga_part=fpga_part,
            board=self.board,
        )

        return f"""{header}

puts "Creating PCIe IP core for device {vendor_id}:{device_id}..."
puts "FPGA Part: {fpga_part}"
puts "Board: {self.board}"

{pcie_config}

puts "PCIe IP core configuration completed"
"""

    def generate_axi_pcie_config(
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

    def generate_pcie_7x_config(
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

    def generate_pcie_ultrascale_config(
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

    def generate_sources_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate source file management TCL script."""
        return safe_format(
            """{header}

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

puts "Source files added successfully"
""",
            header=generate_tcl_header_comment("Source File Management"),
        )

    def generate_constraints_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate constraints TCL script."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]

        header = generate_tcl_header_comment(
            "Constraints Management",
            vendor_id=vendor_id,
            device_id=device_id,
            board=self.board,
        )

        return f"""{header}

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
set constraints_file "./device_constraints.xdc"
set fp [open $constraints_file w]
puts $fp $timing_constraints
close $fp
add_files -fileset constrs_1 -norecurse $constraints_file

puts "Constraints setup completed"
"""

    def generate_synthesis_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate synthesis TCL script."""
        return safe_format(
            """{header}

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
""",
            header=generate_tcl_header_comment("Synthesis Configuration and Execution"),
        )

    def generate_implementation_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate implementation TCL script."""
        return safe_format(
            """{header}

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

# Generate implementation reports
puts "Generating reports..."
open_run impl_1
report_timing_summary -file timing_summary.rpt
report_utilization -file utilization_impl.rpt
report_power -file power_analysis.rpt
report_drc -file drc_report.rpt
""",
            header=generate_tcl_header_comment(
                "Implementation Configuration and Execution"
            ),
        )

    def generate_bitstream_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate bitstream generation TCL script."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]

        header = generate_tcl_header_comment(
            "Bitstream Generation",
            vendor_id=vendor_id,
            device_id=device_id,
            board=self.board,
        )

        return f"""{header}

puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1

# Check bitstream generation
set bitstream_file "./vivado_project/pcileech_firmware.runs/impl_1/[get_property top [current_fileset]].bit"
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

    def generate_master_build_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate master build script that sources all other TCL files."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        class_code = device_info["class_code"]

        header = generate_tcl_header_comment(
            "Master Build Script - PCILeech Firmware",
            vendor_id=vendor_id,
            device_id=device_id,
            class_code=class_code,
            board=self.board,
            generated=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        return f"""{header}

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
