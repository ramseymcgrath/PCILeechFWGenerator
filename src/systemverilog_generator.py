#!/usr/bin/env python3
"""
SystemVerilog Generation Module

Handles generation of SystemVerilog files for PCILeech firmware building.
Uses Jinja2 templates for clean separation of logic and SystemVerilog code.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

try:
    from string_utils import (
        generate_sv_header_comment,
        log_error_safe,
        log_info_safe,
        log_warning_safe,
    )
except ImportError:
    # Fallback for when string_utils is not available
    def log_info_safe(logger, template, **kwargs):
        logger.info(template.format(**kwargs))

    def log_warning_safe(logger, template, **kwargs):
        logger.warning(template.format(**kwargs))

    def log_error_safe(logger, template, **kwargs):
        logger.error(template.format(**kwargs))


try:
    from .template_renderer import TemplateRenderer, TemplateRenderError
except ImportError:
    try:
        from template_renderer import TemplateRenderer, TemplateRenderError
    except ImportError:
        # Fallback if template renderer is not available
        class TemplateRenderer:
            def render_template(self, template_name, context):
                raise ImportError("Template renderer not available")

        class TemplateRenderError(Exception):
            pass


logger = logging.getLogger(__name__)


class SystemVerilogGenerator:
    """Generates SystemVerilog files for PCILeech firmware using Jinja2 templates."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.renderer = TemplateRenderer()

    def discover_and_copy_all_files(self, device_info: Dict[str, Any]) -> List[str]:
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
                        log_info_safe(
                            logger,
                            "Copied valid SystemVerilog module: {filename}",
                            filename=sv_file.name,
                        )
                    else:
                        log_warning_safe(
                            logger,
                            "Skipping invalid SystemVerilog file: {filename}",
                            filename=sv_file.name,
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
                log_error_safe(
                    logger,
                    "Error copying constraint file {filename}: {error}",
                    filename=xdc_file.name,
                    error=e,
                )

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

        # Generate device-specific configuration module using template
        config_module = self.generate_device_config_module(device_info)
        config_path = self.output_dir / "device_config.sv"
        with open(config_path, "w") as f:
            f.write(config_module)
        copied_files.append(str(config_path))

        # Generate top-level wrapper using template
        top_module = self.generate_top_level_wrapper(device_info)
        top_path = self.output_dir / "pcileech_top.sv"
        with open(top_path, "w") as f:
            f.write(top_module)
        copied_files.append(str(top_path))

        return copied_files

    def generate_device_config_module(self, device_info: Dict[str, Any]) -> str:
        """Generate device-specific configuration module using template."""
        try:
            context = {
                "header": self._generate_header(device_info),
                "vendor_id": device_info["vendor_id"],
                "device_id": device_info["device_id"],
                "class_code": device_info["class_code"],
                "bars": device_info["bars"],
            }

            return self.renderer.render_template(
                "systemverilog/device_config.sv.j2", context
            )

        except (TemplateRenderError, Exception) as e:
            logger.error(f"Failed to render device config template: {e}")
            # Fallback to original string-based generation
            return self._generate_device_config_fallback(device_info)

    def generate_top_level_wrapper(self, device_info: Dict[str, Any]) -> str:
        """Generate top-level wrapper using template."""
        try:
            context = {
                "header": self._generate_header(device_info),
                "vendor_id": device_info["vendor_id"],
                "device_id": device_info["device_id"],
                "board": device_info.get("board", "unknown"),
            }

            return self.renderer.render_template(
                "systemverilog/top_level_wrapper.sv.j2", context
            )

        except (TemplateRenderError, Exception) as e:
            logger.error(f"Failed to render top level wrapper template: {e}")
            # Fallback to original string-based generation
            return self._generate_top_level_wrapper_fallback(device_info)

    def _generate_header(self, device_info: Dict[str, Any]) -> str:
        """Generate SystemVerilog header comment."""
        try:
            return generate_sv_header_comment(
                "Generated SystemVerilog Module",
                vendor_id=device_info["vendor_id"],
                device_id=device_info["device_id"],
                board=device_info.get("board", "unknown"),
            )
        except Exception:
            # Simple fallback header
            return f"""//
// Generated SystemVerilog Module
// Vendor ID: {device_info["vendor_id"]}
// Device ID: {device_info["device_id"]}
// Board: {device_info.get("board", "unknown")}
//"""

    def _generate_device_config_fallback(self, device_info: Dict[str, Any]) -> str:
        """Fallback device config generation using string formatting."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        class_code = device_info["class_code"]
        revision_id = device_info["revision_id"]
        bars = device_info["bars"]
        board = device_info.get("board", "unknown")
        header = self._generate_header(device_info)

        template = f"""{header}

module device_config #(
    parameter VENDOR_ID = 16'h{vendor_id[2:]},
    parameter DEVICE_ID = 16'h{device_id[2:]},
    parameter CLASS_CODE = 24'h{class_code[2:]}{revision_id[2:]},
    parameter SUBSYSTEM_VENDOR_ID = 16'h{vendor_id[2:]},
    parameter SUBSYSTEM_DEVICE_ID = 16'h{device_id[2:]},
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
        return template

    def _generate_top_level_wrapper_fallback(self, device_info: Dict[str, Any]) -> str:
        """Fallback top-level wrapper generation using string formatting."""
        vendor_id = device_info["vendor_id"]
        device_id = device_info["device_id"]
        board = device_info.get("board", "unknown")
        header = self._generate_header(device_info)

        template = f"""{header}

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
            debug_status <= {{16'h{vendor_id[2:]}, 8'h{device_id[2:4]}, 5'h0, tlp_state}};
        end
    end

endmodule
"""
        return template
