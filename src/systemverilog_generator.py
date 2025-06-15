#!/usr/bin/env python3
"""
Main Advanced SystemVerilog Generator

This module integrates all the advanced SystemVerilog generation components
(power management, error handling, performance counters) into a cohesive
advanced PCIe device controller.

Advanced SystemVerilog Generation feature for the PCILeechFWGenerator project.
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

# Import string utilities for safe formatting
try:
    from .string_utils import generate_sv_header_comment, safe_format
except ImportError:
    from string_utils import generate_sv_header_comment, safe_format

# Import manufacturing variance for integration
try:
    from .advanced_sv_error import ErrorHandlingConfig, ErrorHandlingGenerator
    from .advanced_sv_perf import (
        DeviceType,
        PerformanceCounterConfig,
        PerformanceCounterGenerator,
    )
    from .advanced_sv_power import PowerManagementConfig, PowerManagementGenerator
    from .manufacturing_variance import (
        DeviceClass,
        ManufacturingVarianceSimulator,
        VarianceModel,
    )
except ImportError:
    from advanced_sv_error import ErrorHandlingConfig, ErrorHandlingGenerator
    from advanced_sv_perf import (
        DeviceType,
        PerformanceCounterConfig,
        PerformanceCounterGenerator,
    )
    from advanced_sv_power import PowerManagementConfig, PowerManagementGenerator
    from manufacturing_variance import (
        DeviceClass,
        ManufacturingVarianceSimulator,
        VarianceModel,
    )


@dataclass
class DeviceSpecificLogic:
    """Configuration for device-specific logic generation."""

    device_type: DeviceType = DeviceType.GENERIC
    device_class: DeviceClass = DeviceClass.CONSUMER

    # Device capabilities
    max_payload_size: int = 256
    max_read_request_size: int = 512
    msi_vectors: int = 1
    msix_vectors: int = 0

    # Device-specific features
    enable_dma: bool = False
    enable_interrupt_coalescing: bool = False
    enable_virtualization: bool = False
    enable_sr_iov: bool = False

    # Queue management
    tx_queue_depth: int = 256
    rx_queue_depth: int = 256
    command_queue_depth: int = 64

    # Buffer sizes
    tx_buffer_size_kb: int = 64
    rx_buffer_size_kb: int = 64

    # Timing characteristics
    base_frequency_mhz: float = 100.0
    memory_frequency_mhz: float = 200.0


class AdvancedSVGenerator:
    """Main advanced SystemVerilog generator with modular components."""

    def __init__(
        self,
        power_config: Optional[PowerManagementConfig] = None,
        error_config: Optional[ErrorHandlingConfig] = None,
        perf_config: Optional[PerformanceCounterConfig] = None,
        device_config: Optional[DeviceSpecificLogic] = None,
    ):
        """Initialize the advanced SystemVerilog generator."""

        self.power_config = power_config or PowerManagementConfig()
        self.error_config = error_config or ErrorHandlingConfig()
        self.perf_config = perf_config or PerformanceCounterConfig()
        self.device_config = device_config or DeviceSpecificLogic()

        # Initialize component generators
        self.power_gen = PowerManagementGenerator(self.power_config)
        self.error_gen = ErrorHandlingGenerator(self.error_config)
        self.perf_gen = PerformanceCounterGenerator(
            self.perf_config, self.device_config.device_type
        )

        # Initialize variance simulator for realistic timing
        self.variance_simulator = ManufacturingVarianceSimulator()

    def generate_module_header(self) -> str:
        """Generate the module header with parameters and ports."""

        header = generate_sv_header_comment(
            "Advanced PCIe Device Controller with Comprehensive Features",
            generator="AdvancedSVGenerator - Advanced SystemVerilog Generation Feature",
            device_type=self.device_config.device_type.value,
            device_class=self.device_config.device_class.value,
            features="Advanced power management (D0-D3, L0-L3 states), Comprehensive error handling and recovery, Hardware performance counters, Multiple clock domain support, Manufacturing variance integration",
        )

        return safe_format(
            """{header}

// State machine definitions
`define S_SHADOW_CFGSPACE_IDLE  2'b00
`define S_SHADOW_CFGSPACE_TLP   2'b01
`define S_SHADOW_CFGSPACE_USB   2'b10

module advanced_pcileech_controller #(
    parameter DEVICE_TYPE = "{device_type}",
    parameter DEVICE_CLASS = "{device_class}",
    parameter MAX_PAYLOAD_SIZE = {max_payload_size},
    parameter MSI_VECTORS = {msi_vectors},
    parameter COUNTER_WIDTH = {counter_width_bits}
) (
    // Clock and reset
    input logic clk,
    input logic reset_n,

    // Additional clock domains
    input logic mem_clk,
    input logic aux_clk,

    // PCIe interface
    input logic [31:0] bar_addr,
    input logic [31:0] bar_wr_data,
    input logic bar_wr_en,
    input logic bar_rd_en,
    output logic [31:0] bar_rd_data,

    // Power management interface
    input logic [1:0] power_state_req,
    output logic [1:0] power_state_ack,
    input logic [1:0] link_state_req,
    output logic [1:0] link_state_ack,

    // Interrupt interface
    output logic msi_request,
    input logic msi_ack,
    output logic [7:0] msi_vector,
    input logic cfg_interrupt_msi_enable,
    output logic cfg_interrupt,
    input logic cfg_interrupt_ready,

    // Error reporting interface
    output logic correctable_error,
    output logic uncorrectable_error,
    output logic [7:0] error_code,

    // Performance monitoring interface
    output logic [COUNTER_WIDTH-1:0] perf_counter_0,
    output logic [COUNTER_WIDTH-1:0] perf_counter_1,
    output logic [COUNTER_WIDTH-1:0] perf_counter_2,
    output logic [COUNTER_WIDTH-1:0] perf_counter_3,

    // Device-specific interfaces
    {device_specific_ports}
);""",
            header=header,
            device_type=self.device_config.device_type.value,
            device_class=self.device_config.device_class.value,
            max_payload_size=self.device_config.max_payload_size,
            msi_vectors=self.device_config.msi_vectors,
            counter_width_bits=self.perf_config.counter_width_bits,
            device_specific_ports=self._generate_device_specific_ports(),
        )

    def _generate_device_specific_ports(self) -> str:
        """Generate device-specific port declarations."""

        if self.device_config.device_type == DeviceType.NETWORK_CONTROLLER:
            return """// Network controller ports
    output logic link_up,
    output logic [1:0] link_speed,
    input logic [7:0] phy_data,
    output logic [7:0] mac_data"""
        elif self.device_config.device_type == DeviceType.STORAGE_CONTROLLER:
            return """// Storage controller ports
    output logic storage_ready,
    output logic [7:0] queue_depth,
    input logic [31:0] sector_addr,
    output logic [31:0] data_out"""
        elif self.device_config.device_type == DeviceType.GRAPHICS_CONTROLLER:
            return """// Graphics controller ports
    output logic display_active,
    output logic [7:0] gpu_utilization,
    input logic [23:0] pixel_data,
    output logic vsync, hsync"""
        else:
            return """// Generic device ports
    output logic device_ready,
    input logic [31:0] generic_input,
    output logic [31:0] generic_output"""

    def generate_register_logic(
        self, regs: List[Dict], variance_model: Optional[VarianceModel]
    ) -> str:
        """Generate advanced register access logic with timing and variance."""

        register_logic = []

        register_logic.append("    // Advanced Register Access Logic")
        register_logic.append("    logic [31:0] register_access_timer = 32'h0;")
        register_logic.append("    logic register_write_pending = 1'b0;")
        register_logic.append("")

        # Register declarations with variance integration
        register_logic.append("    // Register Declarations")
        for reg in regs:
            name = reg["name"]
            initial_value = int(reg["value"], 16)

            # Special case for pcileech_tlps128_cfgspace_shadow_status register
            if name == "pcileech_tlps128_cfgspace_shadow_status":
                register_logic.append(f"    logic [31:0] {name}_reg = 32'h1;")
            # Apply variance to initial values if model provided
            elif variance_model:
                variance_factor = 1.0 + (random.random() - 0.5) * 0.01  # ±0.5% variance
                varied_value = int(initial_value * variance_factor) & 0xFFFFFFFF
                register_logic.append(
                    f"    logic [31:0] {name}_reg = 32'h{varied_value:08X};"
                )
            else:
                register_logic.append(
                    f"    logic [31:0] {name}_reg = 32'h{initial_value:08X};"
                )

            # Add timing control signals
            register_logic.append(f"    logic {name}_access_pending = 1'b0;")
            register_logic.append(f"    logic [7:0] {name}_timing_counter = 8'h0;")

        register_logic.append("")

        # Global register access timing
        register_logic.append("    // Global register access timing")
        register_logic.append("    always_ff @(posedge clk or negedge reset_n) begin")
        register_logic.append("        if (!reset_n) begin")
        register_logic.append("            register_access_timer <= 32'h0;")
        register_logic.append("            register_write_pending <= 1'b0;")
        register_logic.append("        end else begin")
        register_logic.append(
            "            register_access_timer <= register_access_timer + 1;"
        )
        register_logic.append("            ")
        register_logic.append(
            "            if (bar_wr_en && !register_write_pending) begin"
        )
        register_logic.append("                register_write_pending <= 1'b1;")
        register_logic.append(
            "            end else if (register_write_pending && register_access_timer[3:0] == 4'hF) begin"
        )
        register_logic.append("                register_write_pending <= 1'b0;")
        register_logic.append("            end")
        register_logic.append("        end")
        register_logic.append("    end")
        register_logic.append("")

        # Individual register write logic
        for reg in regs:
            name = reg["name"]
            offset = (
                int(reg["offset"], 16)
                if isinstance(reg["offset"], str) and reg["offset"].startswith("0x")
                else int(reg["offset"], 16)
            )

            if reg["rw"] in ["rw", "wo"]:
                register_logic.append(f"    // Write logic for {name}")
                register_logic.append(
                    "    always_ff @(posedge clk or negedge reset_n) begin"
                )
                register_logic.append("        if (!reset_n) begin")
                register_logic.append(
                    f"            {name}_reg <= 32'h{int(reg['value'], 16):08X};"
                )
                register_logic.append(f"            {name}_timing_counter <= 8'h0;")
                register_logic.append(f"            {name}_access_pending <= 1'b0;")
                register_logic.append(
                    f"        end else if (bar_wr_en && bar_addr == 32'h{offset:08X}) begin"
                )

                # Apply variance-aware timing if model provided
                if variance_model:
                    timing_variance = variance_model.register_timing_jitter_ns
                    base_delay = max(
                        1, int(timing_variance / 10)
                    )  # Convert ns to cycles
                    register_logic.append(f"            {name}_access_pending <= 1'b1;")
                    register_logic.append(
                        f"            {name}_timing_counter <= 8'd{base_delay};"
                    )
                    register_logic.append(
                        f"        end else if ({name}_access_pending) begin"
                    )
                    register_logic.append(
                        f"            if ({name}_timing_counter > 0) begin"
                    )
                    register_logic.append(
                        f"                {name}_timing_counter <= {name}_timing_counter - 1;"
                    )
                    register_logic.append("            end else begin")
                    register_logic.append(f"                {name}_reg <= bar_wr_data;")
                    register_logic.append(
                        f"                {name}_access_pending <= 1'b0;"
                    )
                    register_logic.append("            end")
                else:
                    register_logic.append(f"            {name}_reg <= bar_wr_data;")

                register_logic.append("        end")
                register_logic.append("    end")
                register_logic.append("")

        return "\n".join(register_logic)

    def generate_read_logic(self, regs: List[Dict]) -> str:
        """Generate the main read logic with advanced features."""

        read_logic = []

        read_logic.append("    // Main read logic with advanced features")
        read_logic.append("    always_comb begin")
        read_logic.append("        bar_rd_data = 32'h0;")
        read_logic.append("        ")
        read_logic.append("        unique case(bar_addr)")
        read_logic.append("            // Power management registers")
        read_logic.append(
            "            32'h00000000: bar_rd_data = {30'b0, current_power_state};"
        )
        read_logic.append(
            "            32'h00000004: bar_rd_data = {30'b0, current_link_state};"
        )
        read_logic.append("            ")
        read_logic.append("            // Error status registers")
        read_logic.append(
            "            32'h00000008: bar_rd_data = {24'b0, error_status};"
        )
        read_logic.append(
            "            32'h0000000C: bar_rd_data = {24'b0, error_code};"
        )
        read_logic.append("            ")
        read_logic.append("            // Performance counter registers")
        read_logic.append("            32'h00000010: bar_rd_data = perf_counter_0;")
        read_logic.append("            32'h00000014: bar_rd_data = perf_counter_1;")
        read_logic.append("            32'h00000018: bar_rd_data = perf_counter_2;")
        read_logic.append("            32'h0000001C: bar_rd_data = perf_counter_3;")
        read_logic.append("            ")
        read_logic.append("            // Device identification")
        read_logic.append(
            "            32'h00000020: bar_rd_data = 32'hADVANCED;  // Advanced controller signature"
        )
        read_logic.append(
            "            32'h00000024: bar_rd_data = {16'h0, DEVICE_TYPE[15:0]};"
        )
        read_logic.append("            ")
        read_logic.append("            // Advanced status registers")
        read_logic.append(
            "            32'h00000028: bar_rd_data = {24'b0, performance_grade};"
        )
        read_logic.append(
            "            32'h0000002C: bar_rd_data = {29'b0, high_bandwidth_detected, high_latency_detected, high_error_rate_detected};"
        )
        read_logic.append("            ")

        # Add register-specific read cases
        for reg in regs:
            name = reg["name"]
            offset = (
                int(reg["offset"], 16)
                if isinstance(reg["offset"], str) and reg["offset"].startswith("0x")
                else int(reg["offset"], 16)
            )
            read_logic.append(
                f"            32'h{offset:08X}: bar_rd_data = {name}_reg;"
            )

        read_logic.append("            ")
        read_logic.append("            default: bar_rd_data = 32'h0;")
        read_logic.append("        endcase")
        read_logic.append("    end")
        read_logic.append("")

        return "\n".join(read_logic)

    def generate_interrupt_logic(self) -> str:
        """Generate advanced interrupt handling logic."""

        interrupt_logic = []

        interrupt_logic.append("    // Advanced Interrupt Handling")
        interrupt_logic.append("    logic interrupt_pending = 1'b0;")
        interrupt_logic.append("    logic [7:0] interrupt_vector = 8'h0;")
        interrupt_logic.append("    logic [3:0] interrupt_priority = 4'h0;")
        interrupt_logic.append("")

        interrupt_logic.append("    // Interrupt generation logic")
        interrupt_logic.append("    always_ff @(posedge clk or negedge reset_n) begin")
        interrupt_logic.append("        if (!reset_n) begin")
        interrupt_logic.append("            interrupt_pending <= 1'b0;")
        interrupt_logic.append("            interrupt_vector <= 8'h0;")
        interrupt_logic.append("            interrupt_priority <= 4'h0;")
        interrupt_logic.append("        end else begin")
        interrupt_logic.append("            // Priority-based interrupt handling")
        interrupt_logic.append("            if (uncorrectable_error) begin")
        interrupt_logic.append("                interrupt_pending <= 1'b1;")
        interrupt_logic.append(
            "                interrupt_vector <= 8'h02;  // High priority"
        )
        interrupt_logic.append("                interrupt_priority <= 4'hF;")
        interrupt_logic.append("            end else if (correctable_error) begin")
        interrupt_logic.append("                interrupt_pending <= 1'b1;")
        interrupt_logic.append(
            "                interrupt_vector <= 8'h01;  // Medium priority"
        )
        interrupt_logic.append("                interrupt_priority <= 4'h8;")
        interrupt_logic.append("            end else if (bar_wr_en || bar_rd_en) begin")
        interrupt_logic.append("                interrupt_pending <= 1'b1;")
        interrupt_logic.append(
            "                interrupt_vector <= 8'h00;  // Low priority"
        )
        interrupt_logic.append("                interrupt_priority <= 4'h4;")
        interrupt_logic.append("            end else if (msi_ack) begin")
        interrupt_logic.append("                interrupt_pending <= 1'b0;")
        interrupt_logic.append("                interrupt_vector <= 8'h0;")
        interrupt_logic.append("                interrupt_priority <= 4'h0;")
        interrupt_logic.append("            end")
        interrupt_logic.append("        end")
        interrupt_logic.append("    end")
        interrupt_logic.append("")

        # Interrupt output assignments
        interrupt_logic.append("    // Interrupt output assignments")
        interrupt_logic.append(
            "    assign msi_request = interrupt_pending && cfg_interrupt_msi_enable;"
        )
        interrupt_logic.append("    assign msi_vector = interrupt_vector;")
        interrupt_logic.append(
            "    assign cfg_interrupt = interrupt_pending && !cfg_interrupt_msi_enable;"
        )
        interrupt_logic.append("")

        return "\n".join(interrupt_logic)

    def generate_clock_domain_logic(
        self, variance_model: Optional[VarianceModel]
    ) -> str:
        """Generate clock domain management logic."""

        clock_logic = []

        clock_logic.append("    // Clock Domain Management")
        clock_logic.append("    logic [15:0] clk_monitor_counter = 16'h0;")
        clock_logic.append("    logic [15:0] mem_clk_monitor_counter = 16'h0;")
        clock_logic.append("    logic [15:0] aux_clk_monitor_counter = 16'h0;")
        clock_logic.append("    logic [2:0] clock_domain_status = 3'b111;")
        clock_logic.append("    logic mem_clk_valid = 1'b1;")
        clock_logic.append("    logic aux_clk_valid = 1'b1;")
        clock_logic.append("")

        # Clock monitoring
        clock_logic.append("    // Clock domain monitoring")
        clock_logic.append("    always_ff @(posedge clk or negedge reset_n) begin")
        clock_logic.append("        if (!reset_n) begin")
        clock_logic.append("            clk_monitor_counter <= 16'h0;")
        clock_logic.append("        end else begin")
        clock_logic.append(
            "            clk_monitor_counter <= clk_monitor_counter + 1;"
        )
        clock_logic.append("        end")
        clock_logic.append("    end")
        clock_logic.append("")

        # Clock domain status
        clock_logic.append("    // Clock domain status")
        clock_logic.append(
            "    assign clock_domain_status = {aux_clk_valid, mem_clk_valid, 1'b1};"
        )
        clock_logic.append("")

        return "\n".join(clock_logic)

    def generate_advanced_systemverilog(
        self, regs: List[Dict], variance_model: Optional[VarianceModel] = None
    ) -> str:
        """Generate comprehensive advanced SystemVerilog module."""

        # Generate all components
        self.generate_module_header()
        self.power_gen.generate_complete_power_management()
        self.error_gen.generate_complete_error_handling()
        self.perf_gen.generate_complete_performance_counters()
        self.generate_clock_domain_logic(variance_model)
        self.generate_interrupt_logic()
        self.generate_register_logic(regs, variance_model)
        self.generate_read_logic(regs)

        # Combine into complete module using safe formatting
        module_template = """{module_header}

{power_management}

{error_handling}

{performance_counters}

{clock_domains}

{interrupt_handling}

{register_logic}

{read_logic}

endmodule

{clock_crossing_header}
module advanced_clock_crossing #(
    parameter DATA_WIDTH = 32,
    parameter SYNC_STAGES = 3
) (
    input logic src_clk,
    input logic dst_clk,
    input logic reset_n,
    input logic [DATA_WIDTH-1:0] src_data,
    input logic src_valid,
    output logic src_ready,
    output logic [DATA_WIDTH-1:0] dst_data,
    output logic dst_valid,
    input logic dst_ready
);

    // Implementation of advanced clock domain crossing with variance compensation
    logic [SYNC_STAGES-1:0] sync_reg;
    logic [DATA_WIDTH-1:0] data_reg;
    logic valid_reg;

    // Source domain logic
    always_ff @(posedge src_clk or negedge reset_n) begin
        if (!reset_n) begin
            data_reg <= '0;
            valid_reg <= 1'b0;
        end else if (src_valid && src_ready) begin
            data_reg <= src_data;
            valid_reg <= 1'b1;
        end else if (sync_reg[SYNC_STAGES-1]) begin
            valid_reg <= 1'b0;
        end
    end

    // Destination domain synchronizer
    always_ff @(posedge dst_clk or negedge reset_n) begin
        if (!reset_n) begin
            sync_reg <= '0;
        end else begin
            sync_reg <= {{sync_reg[SYNC_STAGES-2:0], valid_reg}};
        end
    end

    assign src_ready = !valid_reg || sync_reg[SYNC_STAGES-1];
    assign dst_data = data_reg;
    assign dst_valid = sync_reg[SYNC_STAGES-1] && dst_ready;

endmodule
"""

        # Format the module content using safe_format
        # Generate clock crossing header
        clock_crossing_header = generate_sv_header_comment(
            "Advanced Clock Domain Crossing Module",
            generator="AdvancedSVGenerator - Clock Domain Crossing",
        )

        module_content = safe_format(
            module_template,
            module_header=self.generate_module_header(),
            power_management=self.power_gen.generate_complete_power_management(),
            error_handling=self.error_gen.generate_complete_error_handling(),
            performance_counters=self.perf_gen.generate_complete_performance_counters(),
            clock_domains=self.generate_clock_domain_logic(variance_model),
            interrupt_handling=self.generate_interrupt_logic(),
            register_logic=self.generate_register_logic(regs, variance_model),
            read_logic=self.generate_read_logic(regs),
            clock_crossing_header=clock_crossing_header,
        )

        return module_content

    def generate_enhanced_build_integration(self) -> str:
        """Generate integration code for build.py enhancement."""

        integration_code = '''
def build_advanced_sv(
    regs: list,
    target_src: pathlib.Path,
    board_type: str = "75t",
    enable_variance: bool = True,
    variance_metadata: Optional[dict] = None,
    advanced_features: Optional[dict] = None,
) -> None:
    """Generate advanced SystemVerilog BAR controller with comprehensive features."""

    # Import classes from this module (they're defined above)
    # AdvancedSVGenerator, PowerManagementConfig, etc. are already available

    # Configure advanced features based on board type and requirements
    board_config = BOARD_INFO.get(board_type, BOARD_INFO["75t"])
    device_class_str = board_config.get("device_class", "consumer")
    base_freq = board_config.get("base_frequency_mhz", 100.0)

    # Map string to DeviceClass enum
    device_class_map = {
        "consumer": DeviceClass.CONSUMER,
        "enterprise": DeviceClass.ENTERPRISE,
        "industrial": DeviceClass.INDUSTRIAL,
        "automotive": DeviceClass.AUTOMOTIVE,
    }
    device_class = device_class_map.get(device_class_str, DeviceClass.CONSUMER)

    # Configure advanced features
    power_config = PowerManagementConfig(
        enable_clock_gating=True,
        enable_aspm=True,
        d0_to_d1_cycles=100,
        d1_to_d0_cycles=50
    )

    error_config = ErrorHandlingConfig(
        enable_ecc=True,
        enable_parity_check=True,
        enable_crc_check=True,
        enable_auto_retry=True,
        max_retry_count=3
    )

    perf_config = PerformanceCounterConfig(
        enable_transaction_counters=True,
        enable_bandwidth_monitoring=True,
        enable_latency_measurement=True,
        enable_error_rate_tracking=True
    )

    device_config = DeviceSpecificLogic(
        device_type=DeviceType.GENERIC,
        device_class=device_class,
        base_frequency_mhz=base_freq
    )

    # Override with user-provided advanced features
    if advanced_features:
        if "device_type" in advanced_features:
            device_config.device_type = DeviceType(advanced_features["device_type"])
        if "enable_power_management" in advanced_features:
            power_config.enable_clock_gating = advanced_features["enable_power_management"]
        if "enable_error_handling" in advanced_features:
            error_config.enable_auto_retry = advanced_features["enable_error_handling"]

    # Initialize variance simulator if enabled
    variance_model = None
    if enable_variance:
        variance_simulator = ManufacturingVarianceSimulator()
        device_id = variance_metadata.get("device_id", f"board_{board_type}") if variance_metadata else f"board_{board_type}"
        variance_model = variance_simulator.generate_variance_model(
            device_id=device_id,
            device_class=device_class,
            base_frequency_mhz=base_freq
        )
        print(f"[*] Advanced variance simulation enabled for {device_class.value} class device")

    # Generate advanced SystemVerilog
    generator = AdvancedSVGenerator(power_config, error_config, perf_config, device_config)
    sv_content = generator.generate_advanced_systemverilog(regs, variance_model)

    # Write to output and target locations
    (OUT / "advanced_bar_controller.sv").write_text(sv_content)
    shutil.copyfile(OUT / "advanced_bar_controller.sv", target_src)

    print("[*] Advanced SystemVerilog generation complete!")
    print(f"    - Power management: {power_config.enable_clock_gating}")
    print(f"    - Error handling: {error_config.enable_auto_retry}")
    print(f"    - Performance counters: {perf_config.enable_transaction_counters}")
    print(f"    - Device type: {device_config.device_type.value}")
'''

        return integration_code


# Backward compatibility imports
import logging
from pathlib import Path
from typing import Any, Dict, List

# Import template renderer for compatibility
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


# Import string utilities for compatibility
try:
    from .string_utils import (
        log_error_safe,
        log_info_safe,
        log_warning_safe,
    )
except ImportError:
    try:
        from string_utils import (
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


# =============================================================================
# BACKWARD COMPATIBILITY LAYER
# =============================================================================


class SystemVerilogGenerator:
    """
    Backward compatibility wrapper for the original SystemVerilogGenerator interface.

    This class maintains the original API while leveraging the advanced modular system
    underneath for enhanced functionality.
    """

    def __init__(self, output_dir: Path):
        """Initialize with output directory (original interface)."""
        self.output_dir = output_dir
        self.renderer = TemplateRenderer()

        # Initialize the advanced generator with default configurations
        self.advanced_generator = AdvancedSVGenerator()

        # Set up logger
        self.logger = logging.getLogger(__name__)

    def discover_and_copy_all_files(self, device_info: Dict[str, Any]) -> List[str]:
        """
        Scalable discovery and copying of all relevant project files.

        This method maintains the original interface while using the advanced
        generator for enhanced SystemVerilog generation.
        """
        copied_files = []
        src_dir = Path(__file__).parent

        # Discover all SystemVerilog files (including subdirectories)
        sv_files = list(src_dir.rglob("*.sv"))
        self.logger.info(f"Discovered {len(sv_files)} SystemVerilog files")

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
                            self.logger,
                            "Copied valid SystemVerilog module: {filename}",
                            filename=sv_file.name,
                        )
                    else:
                        log_warning_safe(
                            self.logger,
                            "Skipping invalid SystemVerilog file: {filename}",
                            filename=sv_file.name,
                        )
            except Exception as e:
                self.logger.error(f"Error processing {sv_file.name}: {e}")

        # Discover and copy all TCL files (preserve as-is)
        tcl_files = list(src_dir.rglob("*.tcl"))
        for tcl_file in tcl_files:
            try:
                dest_path = self.output_dir / tcl_file.name
                with open(tcl_file, "r") as src, open(dest_path, "w") as dest:
                    content = src.read()
                    dest.write(content)
                copied_files.append(str(dest_path))
                self.logger.info(f"Copied TCL script: {tcl_file.name}")
            except Exception as e:
                self.logger.error(f"Error copying TCL file {tcl_file.name}: {e}")

        # Discover and copy constraint files
        xdc_files = list(src_dir.rglob("*.xdc"))
        for xdc_file in xdc_files:
            try:
                dest_path = self.output_dir / xdc_file.name
                with open(xdc_file, "r") as src, open(dest_path, "w") as dest:
                    content = src.read()
                    dest.write(content)
                copied_files.append(str(dest_path))
                self.logger.info(f"Copied constraint file: {xdc_file.name}")
            except Exception as e:
                log_error_safe(
                    self.logger,
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
                self.logger.info(f"Copied Verilog module: {v_file.name}")
            except Exception as e:
                self.logger.error(f"Error copying Verilog file {v_file.name}: {e}")

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
            self.logger.error(f"Failed to render device config template: {e}")
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
            self.logger.error(f"Failed to render top level wrapper template: {e}")
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
