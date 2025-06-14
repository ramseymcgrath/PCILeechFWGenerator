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


class PerformanceCounterGenerator:
    """Generator for advanced performance counter SystemVerilog logic."""

    def __init__(
        self,
        config: Optional[PerformanceCounterConfig] = None,
        device_type: DeviceType = DeviceType.GENERIC,
    ):
        """Initialize the performance counter generator."""
        self.config = config or PerformanceCounterConfig()
        self.device_type = device_type

    def generate_perf_declarations(self) -> str:
        """Generate performance counter signal declarations."""

        declarations = []

        declarations.append("    // Performance Counter Signals")
        declarations.append(
            f"    logic [{
                self.config.counter_width_bits -
                1}:0] transaction_counter = {
                self.config.counter_width_bits}'h0;")
        declarations.append(
            f"    logic [{
                self.config.counter_width_bits -
                1}:0] bandwidth_counter = {
                self.config.counter_width_bits}'h0;")
        declarations.append(
            f"    logic [{
                self.config.counter_width_bits -
                1}:0] latency_accumulator = {
                self.config.counter_width_bits}'h0;")
        declarations.append(
            f"    logic [{
                self.config.counter_width_bits -
                1}:0] error_rate_counter = {
                self.config.counter_width_bits}'h0;")
        declarations.append("")

        # Timing and control signals
        declarations.append("    // Performance Monitoring Control")
        declarations.append("    logic [31:0] perf_window_counter = 32'h0;")
        declarations.append("    logic [15:0] latency_sample_counter = 16'h0;")
        declarations.append(
            f"    logic [{
                self.config.timestamp_width_bits -
                1}:0] latency_start_time = {
                self.config.timestamp_width_bits}'h0;")
        declarations.append("    logic transaction_active = 1'b0;")
        declarations.append("    logic bandwidth_window_reset = 1'b0;")
        declarations.append("    logic latency_measurement_active = 1'b0;")
        declarations.append("")

        # Device-specific counter declarations
        if self.config.enable_device_specific_counters:
            declarations.extend(self._generate_device_specific_declarations())

        # Performance status signals
        declarations.append("    // Performance Status Signals")
        declarations.append("    logic high_bandwidth_detected = 1'b0;")
        declarations.append("    logic high_latency_detected = 1'b0;")
        declarations.append("    logic high_error_rate_detected = 1'b0;")
        declarations.append(
            "    logic [7:0] performance_grade = 8'hFF;  // 255 = excellent"
        )
        declarations.append("")

        return "\n".join(declarations)

    def _generate_device_specific_declarations(self) -> List[str]:
        """Generate device-specific counter declarations."""

        declarations = []
        declarations.append("    // Device-Specific Performance Counters")

        if self.device_type == DeviceType.NETWORK_CONTROLLER:
            for counter in self.config.network_counters:
                declarations.append(
                    f"    logic [{
                        self.config.counter_width_bits -
                        1}:0] {counter} = {
                        self.config.counter_width_bits}'h0;")
            declarations.append("    logic link_utilization_high = 1'b0;")
            declarations.append("    logic [7:0] packet_loss_rate = 8'h0;")

        elif self.device_type == DeviceType.STORAGE_CONTROLLER:
            for counter in self.config.storage_counters:
                declarations.append(
                    f"    logic [{
                        self.config.counter_width_bits -
                        1}:0] {counter} = {
                        self.config.counter_width_bits}'h0;")
            declarations.append("    logic [7:0] current_queue_depth = 8'h0;")
            declarations.append("    logic [15:0] average_io_latency = 16'h0;")

        elif self.device_type == DeviceType.GRAPHICS_CONTROLLER:
            for counter in self.config.graphics_counters:
                declarations.append(
                    f"    logic [{
                        self.config.counter_width_bits -
                        1}:0] {counter} = {
                        self.config.counter_width_bits}'h0;")
            declarations.append(
                "    logic [7:0] frame_rate = 8'h3C;  // 60 FPS")
            declarations.append("    logic [15:0] render_time = 16'h0;")

        declarations.append("")
        return declarations

    def generate_transaction_counters(self) -> str:
        """Generate transaction counting logic."""

        if not self.config.enable_transaction_counters:
            return "    // Transaction counters disabled\n"

        counter_logic = []

        counter_logic.append("    // Transaction Counting Logic")
        counter_logic.append(
            "    always_ff @(posedge clk or negedge reset_n) begin")
        counter_logic.append("        if (!reset_n) begin")
        counter_logic.append("            transaction_counter <= 32'h0;")
        counter_logic.append("            transaction_active <= 1'b0;")
        counter_logic.append("        end else begin")
        counter_logic.append("            if (bar_wr_en || bar_rd_en) begin")
        counter_logic.append(
            "                transaction_counter <= transaction_counter + 1;"
        )
        counter_logic.append("                transaction_active <= 1'b1;")
        counter_logic.append(
            "            end else if (transaction_active && msi_ack) begin"
        )
        counter_logic.append("                transaction_active <= 1'b0;")
        counter_logic.append("            end")
        counter_logic.append("        end")
        counter_logic.append("    end")
        counter_logic.append("")

        return "\n".join(counter_logic)

    def generate_bandwidth_monitoring(self) -> str:
        """Generate bandwidth monitoring logic."""

        if not self.config.enable_bandwidth_monitoring:
            return "    // Bandwidth monitoring disabled\n"

        bandwidth_logic = []

        bandwidth_logic.append("    // Bandwidth Monitoring Logic")
        bandwidth_logic.append(
            "    always_ff @(posedge clk or negedge reset_n) begin")
        bandwidth_logic.append("        if (!reset_n) begin")
        bandwidth_logic.append("            bandwidth_counter <= 32'h0;")
        bandwidth_logic.append("            perf_window_counter <= 32'h0;")
        bandwidth_logic.append("            bandwidth_window_reset <= 1'b0;")
        bandwidth_logic.append("            high_bandwidth_detected <= 1'b0;")
        bandwidth_logic.append("        end else begin")
        bandwidth_logic.append(
            f"            if (perf_window_counter >= {
                self.config.bandwidth_window_cycles}) begin")
        bandwidth_logic.append("                // End of measurement window")
        bandwidth_logic.append(
            f"                high_bandwidth_detected <= (bandwidth_counter >= {
                self.config.high_bandwidth_threshold});")
        bandwidth_logic.append("                bandwidth_counter <= 32'h0;")
        bandwidth_logic.append("                perf_window_counter <= 32'h0;")
        bandwidth_logic.append(
            "                bandwidth_window_reset <= 1'b1;")
        bandwidth_logic.append("            end else begin")
        bandwidth_logic.append(
            "                perf_window_counter <= perf_window_counter + 1;"
        )
        bandwidth_logic.append(
            "                bandwidth_window_reset <= 1'b0;")
        bandwidth_logic.append("                ")
        bandwidth_logic.append("                // Count bytes transferred")
        bandwidth_logic.append("                if (bar_wr_en) begin")
        bandwidth_logic.append(
            "                    bandwidth_counter <= bandwidth_counter + 4;  // 4 bytes per write"
        )
        bandwidth_logic.append("                end else if (bar_rd_en) begin")
        bandwidth_logic.append(
            "                    bandwidth_counter <= bandwidth_counter + 4;  // 4 bytes per read"
        )
        bandwidth_logic.append("                end")
        bandwidth_logic.append("            end")
        bandwidth_logic.append("        end")
        bandwidth_logic.append("    end")
        bandwidth_logic.append("")

        return "\n".join(bandwidth_logic)

    def generate_latency_measurement(self) -> str:
        """Generate latency measurement logic."""

        if not self.config.enable_latency_measurement:
            return "    // Latency measurement disabled\n"

        latency_logic = []

        latency_logic.append("    // Latency Measurement Logic")
        latency_logic.append(
            "    always_ff @(posedge clk or negedge reset_n) begin")
        latency_logic.append("        if (!reset_n) begin")
        latency_logic.append("            latency_accumulator <= 32'h0;")
        latency_logic.append("            latency_sample_counter <= 16'h0;")
        latency_logic.append("            latency_start_time <= 64'h0;")
        latency_logic.append("            latency_measurement_active <= 1'b0;")
        latency_logic.append("            high_latency_detected <= 1'b0;")
        latency_logic.append("        end else begin")
        latency_logic.append("            // Start latency measurement")
        latency_logic.append(
            "            if ((bar_wr_en || bar_rd_en) && !latency_measurement_active) begin"
        )
        latency_logic.append(
            f"                if (latency_sample_counter >= {
                self.config.latency_sample_rate}) begin")
        latency_logic.append(
            "                    latency_start_time <= {32'h0, perf_window_counter};"
        )
        latency_logic.append(
            "                    latency_measurement_active <= 1'b1;")
        latency_logic.append(
            "                    latency_sample_counter <= 16'h0;")
        latency_logic.append("                end else begin")
        latency_logic.append(
            "                    latency_sample_counter <= latency_sample_counter + 1;"
        )
        latency_logic.append("                end")
        latency_logic.append("            end")
        latency_logic.append("            ")
        latency_logic.append("            // End latency measurement")
        latency_logic.append(
            "            else if (latency_measurement_active && msi_ack) begin"
        )
        latency_logic.append("                logic [31:0] measured_latency;")
        latency_logic.append(
            "                measured_latency = perf_window_counter - latency_start_time[31:0];"
        )
        latency_logic.append(
            "                latency_accumulator <= latency_accumulator + measured_latency;"
        )
        latency_logic.append(
            f"                high_latency_detected <= (measured_latency >= {
                self.config.high_latency_threshold});")
        latency_logic.append(
            "                latency_measurement_active <= 1'b0;")
        latency_logic.append("            end")
        latency_logic.append("        end")
        latency_logic.append("    end")
        latency_logic.append("")

        return "\n".join(latency_logic)

    def generate_error_rate_tracking(self) -> str:
        """Generate error rate tracking logic."""

        if not self.config.enable_error_rate_tracking:
            return "    // Error rate tracking disabled\n"

        error_logic = []

        error_logic.append("    // Error Rate Tracking Logic")
        error_logic.append("    logic [31:0] total_operations = 32'h0;")
        error_logic.append("    logic [15:0] error_rate_percent = 16'h0;")
        error_logic.append("")
        error_logic.append(
            "    always_ff @(posedge clk or negedge reset_n) begin")
        error_logic.append("        if (!reset_n) begin")
        error_logic.append("            error_rate_counter <= 32'h0;")
        error_logic.append("            total_operations <= 32'h0;")
        error_logic.append("            error_rate_percent <= 16'h0;")
        error_logic.append("            high_error_rate_detected <= 1'b0;")
        error_logic.append("        end else begin")
        error_logic.append("            // Count total operations")
        error_logic.append("            if (bar_wr_en || bar_rd_en) begin")
        error_logic.append(
            "                total_operations <= total_operations + 1;")
        error_logic.append("            end")
        error_logic.append("            ")
        error_logic.append("            // Count errors")
        error_logic.append(
            "            if (correctable_error || uncorrectable_error) begin"
        )
        error_logic.append(
            "                error_rate_counter <= error_rate_counter + 1;"
        )
        error_logic.append("            end")
        error_logic.append("            ")
        error_logic.append("            // Calculate error rate (simplified)")
        error_logic.append("            if (total_operations > 1000) begin")
        error_logic.append(
            "                error_rate_percent <= (error_rate_counter * 10000) / total_operations;"
        )
        error_logic.append(
            f"                high_error_rate_detected <= (error_rate_percent >= {
                int(
                    self.config.error_rate_threshold *
                    10000)});")
        error_logic.append("            end")
        error_logic.append("        end")
        error_logic.append("    end")
        error_logic.append("")

        return "\n".join(error_logic)

    def generate_device_specific_counters(self) -> str:
        """Generate device-specific performance counters."""

        if not self.config.enable_device_specific_counters:
            return "    // Device-specific counters disabled\n"

        if self.device_type == DeviceType.NETWORK_CONTROLLER:
            return self._generate_network_counters()
        elif self.device_type == DeviceType.STORAGE_CONTROLLER:
            return self._generate_storage_counters()
        elif self.device_type == DeviceType.GRAPHICS_CONTROLLER:
            return self._generate_graphics_counters()
        else:
            return "    // Generic device counters\n"

    def _generate_network_counters(self) -> str:
        """Generate network-specific performance counters."""

        network_logic = []

        network_logic.append("    // Network Controller Performance Counters")
        network_logic.append(
            "    always_ff @(posedge clk or negedge reset_n) begin")
        network_logic.append("        if (!reset_n) begin")
        network_logic.append("            rx_packets <= 32'h0;")
        network_logic.append("            tx_packets <= 32'h0;")
        network_logic.append("            rx_bytes <= 32'h0;")
        network_logic.append("            tx_bytes <= 32'h0;")
        network_logic.append("            rx_errors <= 32'h0;")
        network_logic.append("            tx_errors <= 32'h0;")
        network_logic.append("            packet_loss_rate <= 8'h0;")
        network_logic.append("        end else begin")
        network_logic.append(
            "            // Simulate network activity based on register access patterns"
        )
        network_logic.append(
            "            if (bar_wr_en && bar_addr[15:8] == 8'h10) begin  // TX registers"
        )
        network_logic.append("                tx_packets <= tx_packets + 1;")
        network_logic.append(
            "                tx_bytes <= tx_bytes + bar_wr_data[15:0];"
        )
        network_logic.append(
            "                if (correctable_error) tx_errors <= tx_errors + 1;"
        )
        network_logic.append("            end")
        network_logic.append("            ")
        network_logic.append(
            "            if (bar_rd_en && bar_addr[15:8] == 8'h20) begin  // RX registers"
        )
        network_logic.append("                rx_packets <= rx_packets + 1;")
        network_logic.append(
            "                rx_bytes <= rx_bytes + 1500;  // Typical packet size"
        )
        network_logic.append(
            "                if (correctable_error) rx_errors <= rx_errors + 1;"
        )
        network_logic.append("            end")
        network_logic.append("            ")
        network_logic.append("            // Calculate packet loss rate")
        network_logic.append(
            "            if ((rx_packets + tx_packets) > 1000) begin")
        network_logic.append(
            "                packet_loss_rate <= ((rx_errors + tx_errors) * 100) / (rx_packets + tx_packets);"
        )
        network_logic.append("            end")
        network_logic.append("        end")
        network_logic.append("    end")
        network_logic.append("")

        return "\n".join(network_logic)

    def _generate_storage_counters(self) -> str:
        """Generate storage-specific performance counters."""

        storage_logic = []

        storage_logic.append("    // Storage Controller Performance Counters")
        storage_logic.append(
            "    always_ff @(posedge clk or negedge reset_n) begin")
        storage_logic.append("        if (!reset_n) begin")
        storage_logic.append("            read_ops <= 32'h0;")
        storage_logic.append("            write_ops <= 32'h0;")
        storage_logic.append("            read_bytes <= 32'h0;")
        storage_logic.append("            write_bytes <= 32'h0;")
        storage_logic.append("            io_errors <= 32'h0;")
        storage_logic.append("            current_queue_depth <= 8'h0;")
        storage_logic.append("            average_io_latency <= 16'h0;")
        storage_logic.append("        end else begin")
        storage_logic.append("            // Simulate storage operations")
        storage_logic.append("            if (bar_wr_en) begin")
        storage_logic.append(
            "                if (bar_addr[15:12] == 4'h1) begin  // Write command"
        )
        storage_logic.append("                    write_ops <= write_ops + 1;")
        storage_logic.append(
            "                    write_bytes <= write_bytes + bar_wr_data[15:0];"
        )
        storage_logic.append(
            "                    current_queue_depth <= current_queue_depth + 1;"
        )
        storage_logic.append(
            "                end else if (bar_addr[15:12] == 4'h2) begin  // Read command"
        )
        storage_logic.append("                    read_ops <= read_ops + 1;")
        storage_logic.append(
            "                    read_bytes <= read_bytes + bar_wr_data[15:0];"
        )
        storage_logic.append(
            "                    current_queue_depth <= current_queue_depth + 1;"
        )
        storage_logic.append("                end")
        storage_logic.append("            end")
        storage_logic.append("            ")
        storage_logic.append("            // Process queue and update metrics")
        storage_logic.append(
            "            if (current_queue_depth > 0 && perf_window_counter[7:0] == 8'hFF) begin"
        )
        storage_logic.append(
            "                current_queue_depth <= current_queue_depth - 1;"
        )
        storage_logic.append(
            "                average_io_latency <= (average_io_latency + perf_window_counter[15:0]) / 2;"
        )
        storage_logic.append("            end")
        storage_logic.append("            ")
        storage_logic.append("            // Count I/O errors")
        storage_logic.append("            if (uncorrectable_error) begin")
        storage_logic.append("                io_errors <= io_errors + 1;")
        storage_logic.append("            end")
        storage_logic.append("        end")
        storage_logic.append("    end")
        storage_logic.append("")

        return "\n".join(storage_logic)

    def _generate_graphics_counters(self) -> str:
        """Generate graphics-specific performance counters."""

        graphics_logic = []

        graphics_logic.append(
            "    // Graphics Controller Performance Counters")
        graphics_logic.append("    logic [15:0] frame_timer = 16'h0;")
        graphics_logic.append("    logic [15:0] render_start_time = 16'h0;")
        graphics_logic.append("")
        graphics_logic.append(
            "    always_ff @(posedge clk or negedge reset_n) begin")
        graphics_logic.append("        if (!reset_n) begin")
        graphics_logic.append("            frame_count <= 32'h0;")
        graphics_logic.append("            pixel_count <= 32'h0;")
        graphics_logic.append("            memory_bandwidth <= 32'h0;")
        graphics_logic.append(
            "            gpu_utilization <= 32'h50;  // 50% utilization"
        )
        graphics_logic.append("            frame_timer <= 16'h0;")
        graphics_logic.append("            frame_rate <= 8'h3C;  // 60 FPS")
        graphics_logic.append("            render_time <= 16'h0;")
        graphics_logic.append("        end else begin")
        graphics_logic.append("            frame_timer <= frame_timer + 1;")
        graphics_logic.append("            ")
        graphics_logic.append("            // Simulate frame rendering")
        graphics_logic.append(
            "            if (frame_timer >= 16'h4000) begin  // ~60 FPS at 100MHz"
        )
        graphics_logic.append(
            "                frame_count <= frame_count + 1;")
        graphics_logic.append(
            "                pixel_count <= pixel_count + 32'd1920 * 32'd1080;  // 1080p"
        )
        graphics_logic.append("                frame_timer <= 16'h0;")
        graphics_logic.append("                render_time <= frame_timer;")
        graphics_logic.append("                ")
        graphics_logic.append("                // Update frame rate")
        graphics_logic.append(
            "                frame_rate <= (frame_timer < 16'h3000) ? 8'h4B :  // 75 FPS"
        )
        graphics_logic.append(
            "                              (frame_timer < 16'h4000) ? 8'h3C :  // 60 FPS"
        )
        graphics_logic.append(
            "                                                         8'h1E;   // 30 FPS"
        )
        graphics_logic.append("            end")
        graphics_logic.append("            ")
        graphics_logic.append(
            "            // Update memory bandwidth based on activity"
        )
        graphics_logic.append("            if (bar_wr_en || bar_rd_en) begin")
        graphics_logic.append(
            "                memory_bandwidth <= memory_bandwidth + 4;"
        )
        graphics_logic.append(
            "            end else if (bandwidth_window_reset) begin")
        graphics_logic.append("                memory_bandwidth <= 32'h0;")
        graphics_logic.append("            end")
        graphics_logic.append("        end")
        graphics_logic.append("    end")
        graphics_logic.append("")

        return "\n".join(graphics_logic)

    def generate_performance_grading(self) -> str:
        """Generate overall performance grading logic."""

        grading_logic = []

        grading_logic.append("    // Performance Grading Logic")
        grading_logic.append(
            "    always_ff @(posedge clk or negedge reset_n) begin")
        grading_logic.append("        if (!reset_n) begin")
        grading_logic.append("            performance_grade <= 8'hFF;")
        grading_logic.append("        end else begin")
        grading_logic.append(
            "            // Calculate performance grade (0-255, higher is better)"
        )
        grading_logic.append("            logic [7:0] grade = 8'hFF;")
        grading_logic.append("            ")
        grading_logic.append(
            "            // Deduct points for performance issues")
        grading_logic.append(
            "            if (high_latency_detected) grade = grade - 8'h20;"
        )
        grading_logic.append(
            "            if (high_error_rate_detected) grade = grade - 8'h40;"
        )
        grading_logic.append(
            "            if (!high_bandwidth_detected && bandwidth_counter > 0) grade = grade - 8'h10;"
        )
        grading_logic.append("            ")
        grading_logic.append("            performance_grade <= grade;")
        grading_logic.append("        end")
        grading_logic.append("    end")
        grading_logic.append("")

        return "\n".join(grading_logic)

    def generate_perf_outputs(self) -> str:
        """Generate performance counter output assignments."""

        outputs = []

        outputs.append("    // Performance Counter Outputs")
        outputs.append("    assign perf_counter_0 = transaction_counter;")
        outputs.append("    assign perf_counter_1 = bandwidth_counter;")
        outputs.append("    assign perf_counter_2 = latency_accumulator;")
        outputs.append("    assign perf_counter_3 = error_rate_counter;")
        outputs.append("")

        return "\n".join(outputs)

    def generate_complete_performance_counters(self) -> str:
        """Generate complete performance counter logic."""

        components = [
            self.generate_perf_declarations(),
            self.generate_transaction_counters(),
            self.generate_bandwidth_monitoring(),
            self.generate_latency_measurement(),
            self.generate_error_rate_tracking(),
            self.generate_device_specific_counters(),
            self.generate_performance_grading(),
            self.generate_perf_outputs(),
        ]

        return "\n".join(components)
