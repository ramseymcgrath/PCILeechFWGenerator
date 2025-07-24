#!/usr/bin/env python3
"""
Advanced SystemVerilog Features Module

This module consolidates all advanced SystemVerilog generation features including
error handling, performance monitoring, and power management into a single,
cohesive module to reduce import complexity.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set

# Import from utils instead of scattered locations
from src.string_utils import generate_sv_header_comment


class PowerState(Enum):
    """PCIe power states."""

    D0 = "D0"  # Fully operational
    D1 = "D1"  # Light sleep
    D2 = "D2"  # Deep sleep
    D3_HOT = "D3_HOT"  # Deep sleep with aux power
    D3_COLD = "D3_COLD"  # No power


class ErrorType(Enum):
    """Types of errors that can be detected and handled."""

    NONE = "none"
    PARITY = "parity"
    CRC = "crc"
    TIMEOUT = "timeout"
    OVERFLOW = "overflow"
    UNDERFLOW = "underflow"
    PROTOCOL = "protocol"
    ALIGNMENT = "alignment"
    INVALID_TLP = "invalid_tlp"
    UNSUPPORTED = "unsupported"


class PerformanceMetric(Enum):
    """Performance metrics that can be monitored."""

    TLP_COUNT = "tlp_count"
    COMPLETION_LATENCY = "completion_latency"
    BANDWIDTH_UTILIZATION = "bandwidth_utilization"
    ERROR_RATE = "error_rate"
    POWER_TRANSITIONS = "power_transitions"
    INTERRUPT_LATENCY = "interrupt_latency"


@dataclass
class ErrorHandlingConfig:
    """Configuration for error handling features."""

    enable_error_detection: bool = True
    enable_error_injection: bool = False
    enable_error_logging: bool = True
    error_log_depth: int = 256
    recoverable_errors: Set[ErrorType] = field(
        default_factory=lambda: {ErrorType.PARITY, ErrorType.CRC, ErrorType.TIMEOUT}
    )
    fatal_errors: Set[ErrorType] = field(
        default_factory=lambda: {ErrorType.PROTOCOL, ErrorType.INVALID_TLP}
    )
    error_thresholds: Dict[ErrorType, int] = field(
        default_factory=lambda: {
            ErrorType.PARITY: 10,
            ErrorType.CRC: 5,
            ErrorType.TIMEOUT: 3,
        }
    )


@dataclass
class PerformanceConfig:
    """Configuration for performance monitoring."""

    enable_performance_counters: bool = True
    counter_width: int = 32
    sampling_period: int = 1000  # Clock cycles
    metrics_to_monitor: Set[PerformanceMetric] = field(
        default_factory=lambda: {
            PerformanceMetric.TLP_COUNT,
            PerformanceMetric.COMPLETION_LATENCY,
            PerformanceMetric.BANDWIDTH_UTILIZATION,
        }
    )
    enable_histograms: bool = False
    histogram_bins: int = 16


@dataclass
class PowerManagementConfig:
    """Configuration for power management features."""

    enable_power_management: bool = True
    supported_states: Set[PowerState] = field(
        default_factory=lambda: {PowerState.D0, PowerState.D3_HOT}
    )
    transition_delays: Dict[tuple, int] = field(
        default_factory=lambda: {
            (PowerState.D0, PowerState.D3_HOT): 100,
            (PowerState.D3_HOT, PowerState.D0): 1000,
        }
    )
    enable_clock_gating: bool = True
    enable_power_gating: bool = False
    idle_threshold: int = 10000  # Clock cycles before entering low power


@dataclass
class AdvancedFeatureConfig:
    """Combined configuration for all advanced features."""

    error_handling: ErrorHandlingConfig = field(default_factory=ErrorHandlingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    power_management: PowerManagementConfig = field(
        default_factory=PowerManagementConfig
    )

    # Global settings
    enable_debug_ports: bool = True
    enable_assertions: bool = True
    enable_coverage: bool = False
    clock_frequency_mhz: int = 250


class AdvancedSVFeatureGenerator:
    """Generator for advanced SystemVerilog features."""

    def __init__(self, config: AdvancedFeatureConfig):
        self.config = config

    def generate_error_handling_module(self) -> str:
        """Generate complete error handling module."""
        if not self.config.error_handling.enable_error_detection:
            return ""

        # Import here to avoid circular imports
        from .advanced_sv_error import ErrorHandlingConfig, ErrorHandlingGenerator

        # Create error handling configuration from our config
        error_config = ErrorHandlingConfig(
            enable_ecc=self.config.error_handling.enable_error_detection,
            enable_parity_check=self.config.error_handling.enable_error_detection,
            enable_crc_check=self.config.error_handling.enable_error_detection,
            enable_timeout_detection=self.config.error_handling.enable_error_detection,
            enable_auto_retry=True,
            max_retry_count=3,
            enable_error_logging=self.config.error_handling.enable_error_logging,
            enable_error_injection=self.config.error_handling.enable_error_injection,
        )

        # Create error handling generator
        error_generator = ErrorHandlingGenerator(error_config)

        # Generate error handling components
        error_detection = error_generator.generate_error_detection()
        error_state_machine = error_generator.generate_error_state_machine()
        error_logging = error_generator.generate_error_logging()
        error_counters = error_generator.generate_error_counters()

        # Add error injection if enabled
        error_injection = ""
        if self.config.error_handling.enable_error_injection:
            error_injection = error_generator.generate_error_injection()

        # Generate the complete module
        return self._generate_module_template(
            "error_handler",
            error_detection,
            error_state_machine,
            error_logging,
            error_counters,
            error_injection,
        )

    def generate_performance_monitor_module(self) -> str:
        """Generate performance monitoring module."""
        if not self.config.performance.enable_performance_counters:
            return ""

        return self._generate_module_template(
            "performance_monitor",
            self._generate_counter_logic(),
            self._generate_sampling_logic(),
            self._generate_reporting_logic(),
        )

    def generate_power_management_module(self) -> str:
        """Generate power management module."""
        if not self.config.power_management.enable_power_management:
            return ""

        return self._generate_module_template(
            "power_manager",
            self._generate_state_machine(),
            self._generate_clock_gating_logic(),
            self._generate_transition_logic(),
        )

    def _generate_module_template(self, module_name: str, *components: str) -> str:
        """Generate a module template with the given components."""
        header = generate_sv_header_comment(
            f"{module_name.replace('_', ' ').title()} Module",
            generator="AdvancedSVFeatureGenerator",
            version="0.7.5",
        )

        module_body = "\n\n".join(filter(None, components))

        return f"""{header}

module {module_name} #(
    parameter FEATURE_ENABLED = 1
) (
    input  logic        clk,
    input  logic        rst_n,
    // Additional ports would be defined here
);

{module_body}

endmodule
"""

    def _generate_error_recovery_logic(self) -> str:
        """Generate error recovery logic."""
        return """
    // Error recovery logic
    logic error_detected;
    logic recovery_active;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            recovery_active <= 1'b0;
        end else if (error_detected) begin
            recovery_active <= 1'b1;
        end else begin
            recovery_active <= 1'b0;
        end
    end"""

    def _generate_error_logging_logic(self) -> str:
        """Generate error logging logic."""
        return """
    // Error logging logic
    logic [31:0] error_count;
    logic [7:0] last_error_type;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            error_count <= 32'h0;
            last_error_type <= 8'h0;
        end else if (error_detected) begin
            error_count <= error_count + 1'b1;
            last_error_type <= error_type;
        end
    end"""

    def _generate_counter_logic(self) -> str:
        """Generate performance counter logic."""
        return """
    // Performance counter logic
    logic [31:0] transaction_count;
    logic [31:0] cycle_count;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            transaction_count <= 32'h0;
            cycle_count <= 32'h0;
        end else begin
            cycle_count <= cycle_count + 1'b1;
            if (transaction_valid) begin
                transaction_count <= transaction_count + 1'b1;
            end
        end
    end"""

    def _generate_sampling_logic(self) -> str:
        """Generate sampling logic."""
        return """
    // Sampling logic
    logic sample_trigger;
    logic [31:0] sample_data;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sample_data <= 32'h0;
        end else if (sample_trigger) begin
            sample_data <= performance_data;
        end
    end"""

    def _generate_reporting_logic(self) -> str:
        """Generate reporting logic."""
        return """
    // Reporting logic
    logic report_ready;
    logic [31:0] report_data;
    
    always_comb begin
        report_ready = (error_count > 0) || (transaction_count > threshold);
        report_data = {error_count[15:0], transaction_count[15:0]};
    end"""

    def _generate_state_machine(self) -> str:
        """Generate power state machine."""
        return """
    // Power state machine
    typedef enum logic [1:0] {
        POWER_ON  = 2'b00,
        POWER_LOW = 2'b01,
        POWER_OFF = 2'b10
    } power_state_t;
    
    power_state_t current_state, next_state;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= POWER_ON;
        end else begin
            current_state <= next_state;
        end
    end
    
    always_comb begin
        case (current_state)
            POWER_ON:  next_state = power_down_req ? POWER_LOW : POWER_ON;
            POWER_LOW: next_state = power_up_req ? POWER_ON : (power_off_req ? POWER_OFF : POWER_LOW);
            POWER_OFF: next_state = power_up_req ? POWER_ON : POWER_OFF;
            default:   next_state = POWER_ON;
        endcase
    end"""

    def _generate_clock_gating_logic(self) -> str:
        """Generate clock gating logic."""
        return """
    // Clock gating logic
    logic gated_clk;
    logic clock_enable;
    
    always_comb begin
        clock_enable = (current_state == POWER_ON) && !power_save_mode;
    end
    
    // Clock gating cell (implementation depends on target technology)
    assign gated_clk = clk & clock_enable;"""

    def _generate_transition_logic(self) -> str:
        """Generate power transition logic."""
        return """
    // Power transition logic
    logic transition_complete;
    logic [7:0] transition_counter;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            transition_counter <= 8'h0;
            transition_complete <= 1'b0;
        end else if (current_state != next_state) begin
            transition_counter <= 8'h0;
            transition_complete <= 1'b0;
        end else if (transition_counter < 8'hFF) begin
            transition_counter <= transition_counter + 1'b1;
        end else begin
            transition_complete <= 1'b1;
        end
    end"""


# Export the main components
__all__ = [
    "PowerState",
    "ErrorType",
    "PerformanceMetric",
    "ErrorHandlingConfig",
    "PerformanceConfig",
    "PowerManagementConfig",
    "AdvancedFeatureConfig",
    "AdvancedSVFeatureGenerator",
]
