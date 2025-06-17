#!/usr/bin/env python3
"""
Advanced SystemVerilog Performance Counter Module

This module provides hardware performance monitoring capabilities for PCIe devices,
including transaction counters, bandwidth monitoring, latency measurement, and
device-specific performance metrics.

Performance Counter feature for the PCILeechFWGenerator project.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from ..string_utils import generate_sv_header_comment, safe_format

__all__ = [
    "DeviceType",
    "PerformanceCounterConfig",
    "PerformanceCounterGenerator",
]


class DeviceType(Enum):
    """Device-specific types for specialized performance counters."""

    GENERIC = "generic"
    NETWORK_CONTROLLER = "network"
    STORAGE_CONTROLLER = "storage"
    GRAPHICS_CONTROLLER = "graphics"
    AUDIO_CONTROLLER = "audio"


@dataclass
class PerformanceCounterConfig:
    """Configuration for performance monitoring counters."""

    # Counter types to implement
    enable_transaction_counters: bool = True
    enable_bandwidth_monitoring: bool = True
    enable_latency_measurement: bool = True
    enable_error_rate_tracking: bool = True
    enable_device_specific_counters: bool = True

    # Counter specifications
    counter_width_bits: int = 32
    timestamp_width_bits: int = 64

    @property
    def counter_width(self) -> int:
        """Alias for counter_width_bits for template compatibility."""
        return self.counter_width_bits

    # Measurement windows
    bandwidth_window_cycles: int = 100000  # ~1ms at 100MHz
    latency_sample_rate: int = 1000  # Sample every 1000 transactions

    # Counter sets based on device type
    network_counters: List[str] = field(
        default_factory=lambda: [
            "rx_packets",
            "tx_packets",
            "rx_bytes",
            "tx_bytes",
            "rx_errors",
            "tx_errors",
        ]
    )
    storage_counters: List[str] = field(
        default_factory=lambda: [
            "read_ops",
            "write_ops",
            "read_bytes",
            "write_bytes",
            "io_errors",
            "queue_depth",
        ]
    )
    graphics_counters: List[str] = field(
        default_factory=lambda: [
            "frame_count",
            "pixel_count",
            "memory_bandwidth",
            "gpu_utilization",
        ]
    )

    # Performance thresholds
    high_bandwidth_threshold: int = 1000000  # bytes per window
    high_latency_threshold: int = 1000  # cycles
    error_rate_threshold: float = 0.01  # 1% error rate
    msi_threshold: int = 1000  # MSI interrupt threshold for perf_stub


class PerformanceCounterGenerator:
    """Generator for advanced performance counter SystemVerilog logic."""

    def __init__(
        self,
        config: Optional[PerformanceCounterConfig] = None,
        device_type: DeviceType = DeviceType.GENERIC,
        renderer=None,
    ):
        """Initialize the performance counter generator."""
        self.config = config or PerformanceCounterConfig()
        self.device_type = device_type

        # Initialize template renderer
        if renderer is None:
            from .template_renderer import TemplateRenderer

            self.renderer = TemplateRenderer()
        else:
            self.renderer = renderer

    def generate_perf_declarations(self) -> str:
        """Generate performance counter signal declarations."""
        return safe_format(
            "    // Lightweight performance counter declarations\n"
            "    // See perf_stub module for implementation\n"
        )

    def _generate_device_specific_declarations(self) -> List[str]:
        """Generate device-specific counter declarations."""
        return [safe_format("    // Device-specific declarations in perf_stub\n")]

    def generate_transaction_counters(self) -> str:
        """Generate transaction counting logic."""
        context = {
            "enable_transaction_counters": self.config.enable_transaction_counters,
        }
        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

    def generate_bandwidth_monitoring(self) -> str:
        """Generate bandwidth monitoring logic."""
        context = {
            "enable_bandwidth_monitoring": self.config.enable_bandwidth_monitoring,
            "bandwidth_sample_period": 100000,
            "transfer_width": 4,
            "bandwidth_shift": 10,
        }
        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

    def generate_latency_measurement(self) -> str:
        """Generate latency measurement logic."""
        context = {
            "enable_latency_measurement": self.config.enable_latency_measurement,
        }
        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

    def generate_error_rate_tracking(self) -> str:
        """Generate error rate tracking logic."""
        context = {
            "enable_error_rate_tracking": self.config.enable_error_rate_tracking,
            "min_operations_for_error_rate": 100,
        }
        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

    def generate_device_specific_counters(self) -> str:
        """Generate device-specific performance counters."""
        context = {
            "device_type": self.device_type.value.lower(),
            "avg_packet_size": 1500,  # For network devices
        }
        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

    def _generate_network_counters(self) -> str:
        """Generate network-specific performance counters."""
        context = {"device_type": "network", "avg_packet_size": 1500}
        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

    def _generate_storage_counters(self) -> str:
        """Generate storage-specific performance counters."""
        context = {"device_type": "storage"}
        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

    def _generate_graphics_counters(self) -> str:
        """Generate graphics-specific performance counters."""
        context = {"device_type": "graphics"}
        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

    def generate_performance_grading(self) -> str:
        """Generate overall performance grading logic."""
        context = {
            "enable_performance_grading": True,
            "enable_transaction_counters": self.config.enable_transaction_counters,
            "enable_bandwidth_monitoring": self.config.enable_bandwidth_monitoring,
            "enable_latency_measurement": self.config.enable_latency_measurement,
            "enable_error_rate_tracking": self.config.enable_error_rate_tracking,
            "high_performance_threshold": 1000,
            "medium_performance_threshold": 100,
            "high_bandwidth_threshold": 100,
            "medium_bandwidth_threshold": 50,
            "low_latency_threshold": 10,
            "medium_latency_threshold": 50,
            "low_error_threshold": 1,
            "medium_error_threshold": 5,
        }
        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

    def generate_perf_outputs(self) -> str:
        """Generate performance counter output assignments."""
        context = {"enable_perf_outputs": True}
        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

    def generate_complete_performance_counters(self) -> str:
        """Generate complete performance counter logic."""

        # Create comprehensive context for the template
        context = {
            # Enable flags
            "enable_transaction_counters": self.config.enable_transaction_counters,
            "enable_bandwidth_monitoring": self.config.enable_bandwidth_monitoring,
            "enable_latency_measurement": self.config.enable_latency_measurement,
            "enable_error_rate_tracking": self.config.enable_error_rate_tracking,
            "enable_performance_grading": True,
            "enable_perf_outputs": True,
            # Device type
            "device_type": self.device_type.value.lower(),
            # Configuration parameters
            "bandwidth_sample_period": 100000,
            "transfer_width": 4,
            "bandwidth_shift": 10,
            "min_operations_for_error_rate": 100,
            # Performance thresholds
            "high_performance_threshold": 1000,
            "medium_performance_threshold": 100,
            "high_bandwidth_threshold": 100,
            "medium_bandwidth_threshold": 50,
            "low_latency_threshold": 10,
            "medium_latency_threshold": 50,
            "low_error_threshold": 1,
            "medium_error_threshold": 5,
            # Device-specific parameters
            "avg_packet_size": 1500,  # For network devices
        }

        return self.renderer.render_template(
            "systemverilog/advanced/performance_counters.sv.j2", context
        )

        stub_template = """
// perf_stub.sv — auto-generated lightweight perf counter block
module perf_stub #(
    parameter int MSI_TH = {msi_th},
    parameter int DEV_KIND = {dev_kind}  // 0=GEN, 1=NET, 2=STO, 3=GFX, 4=AUD
)(
    input  logic        clk,
    input  logic        reset_n,
    input  logic        bar_wr_en,
    input  logic        bar_rd_en,
    input  logic        correctable_error,
    input  logic        uncorrectable_error,
    // CSR read port
    input  logic        csr_rd_en,
    input  logic [1:0]  csr_addr,
    output logic [31:0] csr_rdata,
    // MSI pulse
    output logic        msi_req
);
    // Device type enum
    typedef enum logic [2:0] {{
        GEN = 3'd0,  // Generic
        NET = 3'd1,  // Network
        STO = 3'd2,  // Storage
        GFX = 3'd3,  // Graphics
        AUD = 3'd4   // Audio
    }} dev_type_e;
    
    // Common counters
    logic [31:0] cycle_ctr, err_ctr, msi_cnt;
    
    // Device-specific counters
    logic [31:0] tx_ctr, rx_ctr;           // Network: tx/rx packets
    logic [31:0] wr_ctr, rd_ctr;           // Storage: write/read ops
    logic [31:0] frame_cnt, pixel_cnt;     // Graphics: frames/pixels
    logic [15:0] frame_timer;              // Graphics: frame timing
    logic [31:0] out_samples, in_samples;  // Audio: output/input samples
    logic [31:0] clip_events;              // Audio: clipping events
    
    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            cycle_ctr <= 0; err_ctr <= 0; msi_cnt <= 0;
            tx_ctr <= 0; rx_ctr <= 0; wr_ctr <= 0; rd_ctr <= 0;
            frame_cnt <= 0; pixel_cnt <= 0; frame_timer <= 0;
            out_samples <= 0; in_samples <= 0; clip_events <= 0;
        end else begin
            cycle_ctr <= cycle_ctr + 1;
            msi_cnt   <= (msi_cnt == MSI_TH-1) ? 0 : msi_cnt + 1;
            
            // Common error tracking
            if (correctable_error | uncorrectable_error)
                err_ctr <= err_ctr + 1;
            
            // Device-specific logic
            case (DEV_KIND)
                NET: begin
                    if (bar_wr_en)  tx_ctr <= tx_ctr + 1;
                    if (bar_rd_en)  rx_ctr <= rx_ctr + 1;
                end
                STO: begin
                    if (bar_wr_en)  wr_ctr <= wr_ctr + 1;
                    if (bar_rd_en)  rd_ctr <= rd_ctr + 1;
                end
                GFX: begin
                    frame_timer <= frame_timer + 1;
                    if (frame_timer == 16'h3FFF) begin
                        frame_cnt   <= frame_cnt + 1;
                        pixel_cnt   <= pixel_cnt + 32'd1920 * 32'd1080;  // 1080p
                        frame_timer <= 0;
                    end
                end
                AUD: begin
                    // Assume 48-kHz, 32-bit writes = 4 bytes
                    if (bar_wr_en)  out_samples <= out_samples + 1;
                    if (bar_rd_en)  in_samples  <= in_samples + 1;
                    if (correctable_error) clip_events <= clip_events + 1;
                end
                default: begin  // GEN
                    if (bar_wr_en | bar_rd_en) tx_ctr <= tx_ctr + 1;
                end
            endcase
        end
    end
    
    assign msi_req = (msi_cnt == MSI_TH-1);
    
    // Device-specific CSR read mux
    always_comb begin
{csr_mappings}
    end
endmodule"""

        return safe_format(
            header + stub_template,
            msi_th=msi_th,
            dev_kind=dev_kind,
            csr_mappings=csr_mappings,
        )

    def _generate_device_csr_mappings(self) -> str:
        """Generate device-specific CSR read mappings."""

        # Define CSR mappings per device type
        if self.device_type == DeviceType.NETWORK_CONTROLLER:
            csr_map = [
                ("tx_packets", "tx_ctr"),
                ("rx_packets", "rx_ctr"),
                ("err_counter", "err_ctr"),
                ("cycle_counter", "cycle_ctr"),
            ]
        elif self.device_type == DeviceType.STORAGE_CONTROLLER:
            csr_map = [
                ("write_ops", "wr_ctr"),
                ("read_ops", "rd_ctr"),
                ("err_counter", "err_ctr"),
                ("cycle_counter", "cycle_ctr"),
            ]
        elif self.device_type == DeviceType.GRAPHICS_CONTROLLER:
            csr_map = [
                ("frame_count", "frame_cnt"),
                ("pixel_count", "pixel_cnt"),
                ("err_counter", "err_ctr"),
                ("cycle_counter", "cycle_ctr"),
            ]
        elif self.device_type == DeviceType.AUDIO_CONTROLLER:
            csr_map = [
                ("out_samples", "out_samples"),
                ("in_samples", "in_samples"),
                ("clip_events", "clip_events"),
                ("cycle_counter", "cycle_ctr"),
            ]
        else:  # GENERIC
            csr_map = [
                ("tx_counter", "tx_ctr"),
                ("reserved1", "32'h0"),
                ("err_counter", "err_ctr"),
                ("cycle_counter", "cycle_ctr"),
            ]

        # Generate the case statement
        read_mux_lines = []
        read_mux_lines.append("        unique case (csr_addr)")

        for idx, (name, signal) in enumerate(csr_map):
            read_mux_lines.append(
                safe_format(
                    "            2'd{idx}: csr_rdata = {signal};  // {name}",
                    idx=idx,
                    signal=signal,
                    name=name,
                )
            )

        read_mux_lines.append("            default: csr_rdata = 32'hDEAD_BEEF;")
        read_mux_lines.append("        endcase")

        return "\n".join(read_mux_lines)

    def generate(self) -> str:
        """Alias for generate_complete_performance_counters."""
        return self.generate_complete_performance_counters()
