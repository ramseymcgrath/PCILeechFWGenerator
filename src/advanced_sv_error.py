#!/usr/bin/env python3
"""
Advanced SystemVerilog Error Handling Module

This module provides comprehensive error detection, handling, and recovery logic
for PCIe devices, including correctable/uncorrectable errors, retry mechanisms,
and error logging.

Advanced Error Handling feature for the PCILeechFWGenerator project.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ErrorType(Enum):
    """PCIe error types."""

    CORRECTABLE = "correctable"
    UNCORRECTABLE_NON_FATAL = "uncorrectable_non_fatal"
    UNCORRECTABLE_FATAL = "uncorrectable_fatal"


@dataclass
class ErrorHandlingConfig:
    """Configuration for error detection and handling."""

    # Supported error types
    supported_error_types: List[ErrorType] = field(
        default_factory=lambda: [
            ErrorType.CORRECTABLE,
            ErrorType.UNCORRECTABLE_NON_FATAL,
        ]
    )

    # Error detection features
    enable_ecc: bool = True
    enable_parity_check: bool = True
    enable_crc_check: bool = True
    enable_timeout_detection: bool = True

    # Error recovery features
    enable_auto_retry: bool = True
    max_retry_count: int = 3
    enable_error_logging: bool = True
    enable_error_injection: bool = False  # For testing

    # Error thresholds
    correctable_error_threshold: int = 100
    uncorrectable_error_threshold: int = 10

    # Recovery timing (in clock cycles)
    error_recovery_cycles: int = 1000
    retry_delay_cycles: int = 100
    timeout_cycles: int = 1048576  # ~10ms at 100MHz


class ErrorHandlingGenerator:
    """Generator for advanced error handling SystemVerilog logic."""

    def __init__(self, config: Optional[ErrorHandlingConfig] = None):
        """Initialize the error handling generator."""
        self.config = config or ErrorHandlingConfig()

    def generate_error_declarations(self) -> str:
        """Generate error handling signal declarations."""

        declarations = []

        declarations.append("    // Error Handling Signals")
        declarations.append("    logic [7:0] error_status = 8'h0;")
        declarations.append("    logic [7:0] correctable_error_count = 8'h0;")
        declarations.append("    logic [7:0] uncorrectable_error_count = 8'h0;")
        declarations.append("    logic error_recovery_active = 1'b0;")
        declarations.append("    logic [15:0] error_recovery_timer = 16'h0;")
        declarations.append("    logic [3:0] retry_count = 4'h0;")
        declarations.append("    logic error_injection_active = 1'b0;")
        declarations.append("")

        # Error detection signals
        declarations.append("    // Error Detection Signals")
        declarations.append("    logic parity_error = 1'b0;")
        declarations.append("    logic crc_error = 1'b0;")
        declarations.append("    logic timeout_error = 1'b0;")
        declarations.append("    logic ecc_error = 1'b0;")
        declarations.append("    logic [31:0] timeout_counter = 32'h0;")

        if self.config.enable_crc_check:
            declarations.append("    logic [7:0] calculated_crc = 8'h0;")
            declarations.append("    logic [7:0] expected_crc = 8'h0;")

        if self.config.enable_error_logging:
            declarations.append("    logic [31:0] error_log [0:15];")
            declarations.append("    logic [3:0] error_log_ptr = 4'h0;")

        declarations.append("")

        return "\n".join(declarations)

    def generate_error_detection(self) -> str:
        """Generate error detection logic."""

        detection_logic = []

        detection_logic.append("    // Error Detection Logic")

        # Timeout detection
        if self.config.enable_timeout_detection:
            detection_logic.append("    // Timeout detection")
            detection_logic.append(
                "    always_ff @(posedge clk or negedge reset_n) begin"
            )
            detection_logic.append("        if (!reset_n) begin")
            detection_logic.append("            timeout_counter <= 32'h0;")
            detection_logic.append("            timeout_error <= 1'b0;")
            detection_logic.append("        end else if (bar_wr_en || bar_rd_en) begin")
            detection_logic.append("            timeout_counter <= 32'h0;")
            detection_logic.append("            timeout_error <= 1'b0;")
            detection_logic.append("        end else begin")
            detection_logic.append(
                "            timeout_counter <= timeout_counter + 1;"
            )
            detection_logic.append(
                f"            timeout_error <= (timeout_counter > 32'h{self.config.timeout_cycles:08X});"
            )
            detection_logic.append("        end")
            detection_logic.append("    end")
            detection_logic.append("")

        # Parity checking
        if self.config.enable_parity_check:
            detection_logic.append("    // Parity error detection")
            detection_logic.append(
                "    always_ff @(posedge clk or negedge reset_n) begin"
            )
            detection_logic.append("        if (!reset_n) begin")
            detection_logic.append("            parity_error <= 1'b0;")
            detection_logic.append("        end else if (bar_wr_en) begin")
            detection_logic.append(
                "            parity_error <= (^bar_wr_data != ^bar_addr[7:0]);"
            )
            detection_logic.append("        end else begin")
            detection_logic.append("            parity_error <= 1'b0;")
            detection_logic.append("        end")
            detection_logic.append("    end")
            detection_logic.append("")

        # CRC checking
        if self.config.enable_crc_check:
            detection_logic.append("    // CRC error detection")
            detection_logic.append(
                "    always_ff @(posedge clk or negedge reset_n) begin"
            )
            detection_logic.append("        if (!reset_n) begin")
            detection_logic.append("            calculated_crc <= 8'h0;")
            detection_logic.append("            crc_error <= 1'b0;")
            detection_logic.append("        end else if (bar_wr_en || bar_rd_en) begin")
            detection_logic.append(
                "            calculated_crc <= bar_addr[7:0] ^ bar_wr_data[7:0];"
            )
            detection_logic.append("            expected_crc <= bar_wr_data[15:8];")
            detection_logic.append(
                "            crc_error <= (calculated_crc != expected_crc) && bar_wr_en;"
            )
            detection_logic.append("        end else begin")
            detection_logic.append("            crc_error <= 1'b0;")
            detection_logic.append("        end")
            detection_logic.append("    end")
            detection_logic.append("")

        # ECC checking
        if self.config.enable_ecc:
            detection_logic.append("    // ECC error detection (simplified)")
            detection_logic.append("    logic [6:0] ecc_syndrome;")
            detection_logic.append(
                "    always_ff @(posedge clk or negedge reset_n) begin"
            )
            detection_logic.append("        if (!reset_n) begin")
            detection_logic.append("            ecc_syndrome <= 7'h0;")
            detection_logic.append("            ecc_error <= 1'b0;")
            detection_logic.append("        end else if (bar_wr_en || bar_rd_en) begin")
            detection_logic.append("            // Simplified ECC calculation")
            detection_logic.append(
                "            ecc_syndrome <= ^{bar_wr_data[31:0], bar_addr[6:0]};"
            )
            detection_logic.append("            ecc_error <= |ecc_syndrome;")
            detection_logic.append("        end else begin")
            detection_logic.append("            ecc_error <= 1'b0;")
            detection_logic.append("        end")
            detection_logic.append("    end")
            detection_logic.append("")

        return "\n".join(detection_logic)

    def generate_error_state_machine(self) -> str:
        """Generate error handling state machine."""

        state_machine = []

        state_machine.append("    // Error Handling State Machine")
        state_machine.append("    typedef enum logic [2:0] {")
        state_machine.append("        ERR_NORMAL      = 3'b000,")
        state_machine.append("        ERR_DETECTED    = 3'b001,")
        state_machine.append("        ERR_ANALYZING   = 3'b010,")
        state_machine.append("        ERR_RECOVERING  = 3'b011,")
        state_machine.append("        ERR_RETRY       = 3'b100,")
        state_machine.append("        ERR_FATAL       = 3'b101,")
        state_machine.append("        ERR_LOGGING     = 3'b110")
        state_machine.append("    } error_state_t;")
        state_machine.append("")
        state_machine.append("    error_state_t error_state = ERR_NORMAL;")
        state_machine.append("    error_state_t error_next_state;")
        state_machine.append("")

        # Error state machine logic
        state_machine.append("    // Error state machine logic")
        state_machine.append("    always_ff @(posedge clk or negedge reset_n) begin")
        state_machine.append("        if (!reset_n) begin")
        state_machine.append("            error_state <= ERR_NORMAL;")
        state_machine.append("            retry_count <= 4'h0;")
        state_machine.append("            error_recovery_timer <= 16'h0;")
        state_machine.append("            error_recovery_active <= 1'b0;")
        state_machine.append("        end else begin")
        state_machine.append("            error_state <= error_next_state;")
        state_machine.append("            ")
        state_machine.append("            if (error_state != ERR_NORMAL) begin")
        state_machine.append(
            "                error_recovery_timer <= error_recovery_timer + 1;"
        )
        state_machine.append("                error_recovery_active <= 1'b1;")
        state_machine.append("            end else begin")
        state_machine.append("                error_recovery_timer <= 16'h0;")
        state_machine.append("                error_recovery_active <= 1'b0;")
        state_machine.append("            end")
        state_machine.append("        end")
        state_machine.append("    end")
        state_machine.append("")

        # Error state combinational logic
        state_machine.append("    // Error state combinational logic")
        state_machine.append("    always_comb begin")
        state_machine.append("        error_next_state = error_state;")
        state_machine.append("        ")
        state_machine.append("        case (error_state)")
        state_machine.append("            ERR_NORMAL: begin")
        state_machine.append(
            "                if (parity_error || crc_error || timeout_error || ecc_error) begin"
        )
        state_machine.append("                    error_next_state = ERR_DETECTED;")
        state_machine.append("                end")
        state_machine.append("            end")
        state_machine.append("            ")
        state_machine.append("            ERR_DETECTED: begin")
        state_machine.append("                error_next_state = ERR_ANALYZING;")
        state_machine.append("            end")
        state_machine.append("            ")
        state_machine.append("            ERR_ANALYZING: begin")
        state_machine.append(
            f"                if (error_recovery_timer >= {self.config.error_recovery_cycles}) begin"
        )
        state_machine.append("                    if (timeout_error) begin")
        state_machine.append(
            "                        error_next_state = ERR_FATAL;  // Timeout is fatal"
        )
        state_machine.append(
            f"                    end else if (retry_count < {self.config.max_retry_count}) begin"
        )
        state_machine.append("                        error_next_state = ERR_RETRY;")
        state_machine.append("                    end else begin")
        state_machine.append("                        error_next_state = ERR_FATAL;")
        state_machine.append("                    end")
        state_machine.append("                end")
        state_machine.append("            end")
        state_machine.append("            ")
        state_machine.append("            ERR_RETRY: begin")
        if self.config.enable_error_logging:
            state_machine.append("                error_next_state = ERR_LOGGING;")
        else:
            state_machine.append("                error_next_state = ERR_NORMAL;")
        state_machine.append("            end")
        state_machine.append("            ")
        if self.config.enable_error_logging:
            state_machine.append("            ERR_LOGGING: begin")
            state_machine.append("                error_next_state = ERR_NORMAL;")
            state_machine.append("            end")
            state_machine.append("            ")
        state_machine.append("            ERR_FATAL: begin")
        state_machine.append("                // Stay in fatal state until reset")
        state_machine.append("            end")
        state_machine.append("            ")
        state_machine.append("            default: error_next_state = ERR_NORMAL;")
        state_machine.append("        endcase")
        state_machine.append("    end")
        state_machine.append("")

        return "\n".join(state_machine)

    def generate_error_logging(self) -> str:
        """Generate error logging logic."""

        if not self.config.enable_error_logging:
            return "    // Error logging disabled\n"

        logging_logic = []

        logging_logic.append("    // Error Logging Logic")
        logging_logic.append("    always_ff @(posedge clk or negedge reset_n) begin")
        logging_logic.append("        if (!reset_n) begin")
        logging_logic.append("            error_log_ptr <= 4'h0;")
        logging_logic.append("            for (int i = 0; i < 16; i++) begin")
        logging_logic.append("                error_log[i] <= 32'h0;")
        logging_logic.append("            end")
        logging_logic.append("        end else if (error_state == ERR_LOGGING) begin")
        logging_logic.append("            error_log[error_log_ptr] <= {")
        logging_logic.append("                8'h0,  // Reserved")
        logging_logic.append("                error_recovery_timer,")
        logging_logic.append("                retry_count,")
        logging_logic.append(
            "                timeout_error, crc_error, parity_error, ecc_error"
        )
        logging_logic.append("            };")
        logging_logic.append("            error_log_ptr <= error_log_ptr + 1;")
        logging_logic.append("        end")
        logging_logic.append("    end")
        logging_logic.append("")

        return "\n".join(logging_logic)

    def generate_error_counters(self) -> str:
        """Generate error counting logic."""

        counter_logic = []

        counter_logic.append("    // Error Counting Logic")
        counter_logic.append("    always_ff @(posedge clk or negedge reset_n) begin")
        counter_logic.append("        if (!reset_n) begin")
        counter_logic.append("            correctable_error_count <= 8'h0;")
        counter_logic.append("            uncorrectable_error_count <= 8'h0;")
        counter_logic.append("        end else if (error_state == ERR_DETECTED) begin")
        counter_logic.append("            if (parity_error || ecc_error) begin")
        counter_logic.append(
            "                correctable_error_count <= correctable_error_count + 1;"
        )
        counter_logic.append(
            "            end else if (timeout_error || crc_error) begin"
        )
        counter_logic.append(
            "                uncorrectable_error_count <= uncorrectable_error_count + 1;"
        )
        counter_logic.append("            end")
        counter_logic.append("        end")
        counter_logic.append("    end")
        counter_logic.append("")

        return "\n".join(counter_logic)

    def generate_error_injection(self) -> str:
        """Generate error injection logic for testing."""

        if not self.config.enable_error_injection:
            return "    // Error injection disabled\n"

        injection_logic = []

        injection_logic.append("    // Error Injection Logic (for testing)")
        injection_logic.append("    logic [15:0] injection_lfsr = 16'hACE1;")
        injection_logic.append("    logic inject_parity_error = 1'b0;")
        injection_logic.append("    logic inject_crc_error = 1'b0;")
        injection_logic.append("")
        injection_logic.append("    always_ff @(posedge clk or negedge reset_n) begin")
        injection_logic.append("        if (!reset_n) begin")
        injection_logic.append("            injection_lfsr <= 16'hACE1;")
        injection_logic.append("            inject_parity_error <= 1'b0;")
        injection_logic.append("            inject_crc_error <= 1'b0;")
        injection_logic.append("        end else if (error_injection_active) begin")
        injection_logic.append(
            "            injection_lfsr <= {injection_lfsr[14:0], injection_lfsr[15] ^ injection_lfsr[13] ^ injection_lfsr[12] ^ injection_lfsr[10]};"
        )
        injection_logic.append("            inject_parity_error <= injection_lfsr[0];")
        injection_logic.append("            inject_crc_error <= injection_lfsr[1];")
        injection_logic.append("        end else begin")
        injection_logic.append("            inject_parity_error <= 1'b0;")
        injection_logic.append("            inject_crc_error <= 1'b0;")
        injection_logic.append("        end")
        injection_logic.append("    end")
        injection_logic.append("")

        return "\n".join(injection_logic)

    def generate_error_outputs(self) -> str:
        """Generate error output assignments."""

        outputs = []

        outputs.append("    // Error Output Assignments")
        outputs.append(
            "    assign correctable_error = (error_state == ERR_DETECTED) && "
        )
        outputs.append(
            "                               (parity_error || ecc_error) && !timeout_error;"
        )
        outputs.append(
            "    assign uncorrectable_error = (error_state == ERR_FATAL) || "
        )
        outputs.append("                                 (timeout_error || crc_error);")
        outputs.append("    assign error_code = {")
        outputs.append("        3'b0,")
        outputs.append("        error_state == ERR_FATAL,")
        outputs.append("        timeout_error,")
        outputs.append("        crc_error,")
        outputs.append("        parity_error,")
        outputs.append("        ecc_error")
        outputs.append("    };")
        outputs.append("")

        return "\n".join(outputs)

    def generate_complete_error_handling(self) -> str:
        """Generate complete error handling logic."""

        components = [
            self.generate_error_declarations(),
            self.generate_error_detection(),
            self.generate_error_state_machine(),
            self.generate_error_logging(),
            self.generate_error_counters(),
            self.generate_error_injection(),
            self.generate_error_outputs(),
        ]

        return "\n".join(components)
