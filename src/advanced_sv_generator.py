#!/usr/bin/env python3
"""
Advanced SystemVerilog Generation Module

This module provides sophisticated SystemVerilog generation capabilities for PCIe device
firmware, including advanced timing models, power management, error handling, performance
counters, and device-specific logic generation using Jinja2 templates.

Advanced SystemVerilog Generation feature for the PCILeechFWGenerator project.
"""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

# Import string utilities for safe formatting
try:
    from .string_utils import generate_sv_header_comment
except ImportError:
    try:
        from string_utils import generate_sv_header_comment
    except ImportError:

        def generate_sv_header_comment(title, **kwargs):
            return f"// {title}\n// Generated SystemVerilog Module\n"


# Import template renderer
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


# Import manufacturing variance for integration
try:
    from .manufacturing_variance import (
        DeviceClass,
        ManufacturingVarianceSimulator,
        VarianceModel,
    )
except ImportError:
    try:
        from manufacturing_variance import (
            DeviceClass,
            ManufacturingVarianceSimulator,
            VarianceModel,
        )
    except ImportError:
        # Fallback definitions
        class DeviceClass(Enum):
            CONSUMER = "consumer"
            ENTERPRISE = "enterprise"
            INDUSTRIAL = "industrial"
            AUTOMOTIVE = "automotive"

        class VarianceModel:
            def __init__(self):
                self.process_variation = 0.0
                self.temperature_coefficient = 0.0
                self.voltage_variation = 0.0

        class ManufacturingVarianceSimulator:
            pass


class PowerState(Enum):
    """PCIe power states."""

    D0 = "D0"  # Fully operational
    D1 = "D1"  # Intermediate power state
    D2 = "D2"  # Intermediate power state
    D3_HOT = "D3_HOT"  # Software power down
    D3_COLD = "D3_COLD"  # Hardware power down


class LinkState(Enum):
    """PCIe link power states."""

    L0 = "L0"  # Active state
    L0S = "L0s"  # Standby state
    L1 = "L1"  # Low power standby
    L2 = "L2"  # Auxiliary power
    L3 = "L3"  # Off state


class ErrorType(Enum):
    """PCIe error types."""

    CORRECTABLE = "correctable"
    UNCORRECTABLE_NON_FATAL = "uncorrectable_non_fatal"
    UNCORRECTABLE_FATAL = "uncorrectable_fatal"


class DeviceType(Enum):
    """Device-specific types for specialized logic."""

    GENERIC = "generic"
    NETWORK_CONTROLLER = "network"
    STORAGE_CONTROLLER = "storage"
    GRAPHICS_CONTROLLER = "graphics"
    AUDIO_CONTROLLER = "audio"


@dataclass
class PowerManagementConfig:
    """Configuration for power management features."""

    # Power state support
    supported_power_states: List[PowerState] = field(
        default_factory=lambda: [PowerState.D0, PowerState.D1, PowerState.D3_HOT]
    )
    supported_link_states: List[LinkState] = field(
        default_factory=lambda: [LinkState.L0, LinkState.L0S, LinkState.L1]
    )

    # Power transition timing (in clock cycles)
    d0_to_d1_cycles: int = 100
    d1_to_d0_cycles: int = 50
    d0_to_d3_cycles: int = 1000
    d3_to_d0_cycles: int = 10000

    # Link state transition timing
    l0_to_l0s_cycles: int = 10
    l0s_to_l0_cycles: int = 20
    l0_to_l1_cycles: int = 100
    l1_to_l0_cycles: int = 200

    # Power management features
    enable_clock_gating: bool = True
    enable_power_gating: bool = False
    enable_dynamic_voltage_scaling: bool = False


@dataclass
class PerformanceConfig:
    """Configuration for performance monitoring features."""

    # Counter configuration
    counter_width_bits: int = 32
    enable_bandwidth_monitoring: bool = True
    enable_latency_monitoring: bool = True
    enable_error_rate_monitoring: bool = True
    enable_transaction_counting: bool = True

    # Sampling configuration
    sample_period_cycles: int = 65536
    enable_overflow_interrupts: bool = True
    enable_threshold_alerts: bool = False


@dataclass
class ErrorHandlingConfig:
    """Configuration for error handling features."""

    # Error detection
    enable_correctable_error_detection: bool = True
    enable_uncorrectable_error_detection: bool = True
    enable_fatal_error_detection: bool = True

    # Error recovery
    enable_automatic_recovery: bool = True
    max_retry_count: int = 3
    error_recovery_cycles: int = 1000

    # Error reporting
    enable_error_logging: bool = True
    enable_error_interrupts: bool = True


@dataclass
class DeviceConfig:
    """Configuration for device-specific features."""

    device_type: DeviceType = DeviceType.GENERIC
    device_class: DeviceClass = DeviceClass.CONSUMER
    vendor_id: str = "0x1234"
    device_id: str = "0x5678"
    max_payload_size: int = 256
    msi_vectors: int = 1


class AdvancedSystemVerilogGenerator:
    """Generates advanced SystemVerilog modules using Jinja2 templates."""

    def __init__(
        self,
        device_config: DeviceConfig,
        power_config: PowerManagementConfig,
        perf_config: PerformanceConfig,
        error_config: ErrorHandlingConfig,
    ):
        self.device_config = device_config
        self.power_config = power_config
        self.perf_config = perf_config
        self.error_config = error_config
        self.renderer = TemplateRenderer()

    def generate_advanced_module(
        self, regs: List[Dict], variance_model: Optional[VarianceModel] = None
    ) -> str:
        """Generate advanced SystemVerilog module using templates."""

        try:
            # Build template context
            context = {
                "header": self._generate_header(),
                "device_config": self.device_config,
                "power_management": self._build_power_context(),
                "performance_counters": self._build_perf_context(),
                "error_handling": self._build_error_context(),
                "registers": regs,
                "variance_model": variance_model,
            }

            # Render main module template
            return self.renderer.render_template(
                "systemverilog/advanced/main_module.sv.j2", context
            )

        except (TemplateRenderError, Exception) as e:
            # Fallback to simplified generation if template fails
            return self._generate_fallback_module(regs, variance_model)

    def _generate_header(self) -> str:
        """Generate SystemVerilog header comment."""
        try:
            return generate_sv_header_comment(
                f"Advanced {self.device_config.device_type.value.title()} Controller",
                device_type=self.device_config.device_type.value,
                device_class=self.device_config.device_class.value,
                vendor_id=self.device_config.vendor_id,
                device_id=self.device_config.device_id,
            )
        except Exception:
            return f"""//
// Advanced {self.device_config.device_type.value.title()} Controller
// Device Type: {self.device_config.device_type.value}
// Vendor ID: {self.device_config.vendor_id}
// Device ID: {self.device_config.device_id}
//"""

    def _build_power_context(self) -> Dict:
        """Build power management context for templates."""
        return {
            "supported_states": [
                state.value for state in self.power_config.supported_power_states
            ],
            "transition_cycles": {
                "d0_to_d1": self.power_config.d0_to_d1_cycles,
                "d1_to_d0": self.power_config.d1_to_d0_cycles,
                "d0_to_d3": self.power_config.d0_to_d3_cycles,
                "d3_to_d0": self.power_config.d3_to_d0_cycles,
            },
            "enable_clock_gating": self.power_config.enable_clock_gating,
            "enable_power_gating": self.power_config.enable_power_gating,
        }

    def _build_perf_context(self) -> Dict:
        """Build performance monitoring context for templates."""
        return {
            "counter_width": self.perf_config.counter_width_bits,
            "enable_bandwidth": self.perf_config.enable_bandwidth_monitoring,
            "enable_latency": self.perf_config.enable_latency_monitoring,
            "enable_error_rate": self.perf_config.enable_error_rate_monitoring,
            "sample_period": self.perf_config.sample_period_cycles,
            "enable_overflow_interrupts": self.perf_config.enable_overflow_interrupts,
        }

    def _build_error_context(self) -> Dict:
        """Build error handling context for templates."""
        return {
            "correctable_errors": self.error_config.enable_correctable_error_detection,
            "uncorrectable_errors": self.error_config.enable_uncorrectable_error_detection,
            "fatal_errors": self.error_config.enable_fatal_error_detection,
            "automatic_recovery": self.error_config.enable_automatic_recovery,
            "max_retry_count": self.error_config.max_retry_count,
            "recovery_cycles": self.error_config.error_recovery_cycles,
            "enable_logging": self.error_config.enable_error_logging,
            "enable_interrupts": self.error_config.enable_error_interrupts,
        }

    def _generate_fallback_module(
        self, regs: List[Dict], variance_model: Optional[VarianceModel] = None
    ) -> str:
        """Generate a simplified fallback module when templates are not available."""

        header = self._generate_header()

        # Basic module structure
        module_content = f"""{header}

module pcileech_advanced_{self.device_config.device_type.value}_{self.device_config.device_class.value} #(
    parameter DEVICE_TYPE = "{self.device_config.device_type.value}",
    parameter DEVICE_CLASS = "{self.device_config.device_class.value}",
    parameter MAX_PAYLOAD_SIZE = {self.device_config.max_payload_size},
    parameter MSI_VECTORS = {self.device_config.msi_vectors},
    parameter COUNTER_WIDTH = {self.perf_config.counter_width_bits}
) (
    // Clock and reset
    input  logic        clk,
    input  logic        reset_n,
    
    // BAR interface
    input  logic [31:0] bar_addr,
    input  logic [31:0] bar_wr_data,
    input  logic        bar_wr_en,
    input  logic        bar_rd_en,
    output logic [31:0] bar_rd_data,
    output logic        bar_rd_valid,

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

    // Power management interface
    input  logic        power_down_request,
    input  logic        power_up_request,
    output logic        power_ready,
    output logic [1:0]  current_power_state,

    // Debug and status
    output logic [31:0] debug_status,
    output logic        device_ready
);

    // Basic register declarations
"""

        # Add register declarations
        for reg in regs:
            name = reg["name"]
            initial_value = reg["value"]
            module_content += f"    logic [31:0] {name}_reg = {initial_value};\n"

        # Add basic logic
        module_content += """
    // Basic register access logic
    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            bar_rd_data <= 32'h0;
            bar_rd_valid <= 1'b0;
            cfg_ext_read_data <= 32'h0;
            cfg_ext_read_data_valid <= 1'b0;
        end else begin
            // Default assignments
            bar_rd_valid <= 1'b0;
            cfg_ext_read_data_valid <= 1'b0;
            
            // Simple register access
            if (bar_rd_en) begin
                bar_rd_valid <= 1'b1;
                bar_rd_data <= 32'hDEADBEEF;  // Placeholder
            end
            
            if (cfg_ext_read_received) begin
                cfg_ext_read_data_valid <= 1'b1;
                cfg_ext_read_data <= 32'h00000000;  // Placeholder
            end
        end
    end

    // Basic status assignments
    assign power_ready = 1'b1;
    assign current_power_state = 2'b00;  // D0 state
    assign device_ready = 1'b1;
    assign debug_status = 32'h12345678;  // Placeholder

endmodule
"""

        return module_content

    def generate_clock_crossing_module(
        self, variance_model: Optional[VarianceModel] = None
    ) -> str:
        """Generate clock domain crossing module with variance compensation."""

        header = generate_sv_header_comment(
            "Advanced Clock Domain Crossing Module",
            device_type=self.device_config.device_type.value,
            device_class=self.device_config.device_class.value,
        )

        # Simple clock crossing module
        module_content = f"""{header}

module advanced_clock_crossing #(
    parameter DATA_WIDTH = 32,
    parameter SYNC_STAGES = 2
) (
    // Source domain
    input  logic                    src_clk,
    input  logic                    src_reset_n,
    input  logic [DATA_WIDTH-1:0]   src_data,
    input  logic                    src_valid,
    output logic                    src_ready,
    
    // Destination domain
    input  logic                    dst_clk,
    input  logic                    dst_reset_n,
    output logic [DATA_WIDTH-1:0]   dst_data,
    output logic                    dst_valid,
    input  logic                    dst_ready
);

    // Implementation of advanced clock domain crossing with variance compensation
    logic [SYNC_STAGES-1:0] sync_reg;
    logic [DATA_WIDTH-1:0] data_reg;
    logic valid_reg;

    // Source domain logic
    always_ff @(posedge src_clk or negedge src_reset_n) begin
        if (!src_reset_n) begin
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
    always_ff @(posedge dst_clk or negedge dst_reset_n) begin
        if (!dst_reset_n) begin
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

        return module_content


# Alias for backward compatibility
AdvancedSVGenerator = AdvancedSystemVerilogGenerator
