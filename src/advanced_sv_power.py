#!/usr/bin/env python3
"""
Simplified SystemVerilog Power Management Module

This module provides minimal power management logic generation for PCIe devices,
focusing on essential D-state transitions and PME support using a simplified approach
based on the pmcsr_stub.sv module design.

Simplified Power Management feature for the PCILeechFWGenerator project.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .string_utils import generate_sv_header_comment, safe_format


class PowerState(Enum):
    """PCIe power states as defined in the PCIe specification."""

    D0 = "D0"  # Fully operational
    D1 = "D1"  # Low power state 1
    D2 = "D2"  # Low power state 2
    D3_HOT = "D3hot"  # Hot reset state
    D3_COLD = "D3cold"  # Cold reset state


@dataclass
class PowerManagementConfig:
    """Configuration for power management features."""

    # Clock frequency for timing calculations
    clk_hz: int = 100_000_000  # 100 MHz default

    # Transition timeout (nanoseconds) - PCIe spec allows up to 10ms
    transition_timeout_ns: int = 10_000_000  # 10 ms

    # Enable PME (Power Management Event) support
    enable_pme: bool = True

    # Enable wake event support
    enable_wake_events: bool = False


class PowerManagementGenerator:
    """Generator for simplified power management SystemVerilog logic."""

    def __init__(self, config: Optional[PowerManagementConfig] = None):
        """Initialize the power management generator."""
        self.config = config or PowerManagementConfig()

    def generate_pmcsr_stub_module(self) -> str:
        """Generate the complete pmcsr_stub module based on the provided design."""

        # Calculate transition clock cycles
        tr_clks = (
            self.config.transition_timeout_ns * self.config.clk_hz
        ) // 1_000_000_000

        module_code = safe_format(
            """// pmcsr_stub.sv — Minimal PCIe D‑state handshake & PME generator
// Generates just enough logic for a cloned device to satisfy OS power‑management
// probes.  Resource cost: <40 LUT, <50 FF on most FPGAs.
//
//  * Exposes 16‑bit PMCSR at config‑space offset 0x44 (DW 0)
//  * Implements D0 ↔ D3hot transitions with a {timeout_ms} ms timeout
//  * Supports PME_En / PME_Status and pulses PME# when a wake event arrives
//  * No D1/D2, no ASPM state machine, no real gating — everything else handled
//    by the PCIe hard‑macro or left unimplemented.

module pmcsr_stub #(
    // Fabric clock frequency (Hz). Used only for the fake transition timer.
    parameter int CLK_HZ = {clk_hz},
    // Maximum transition time per PCIe spec ≤ 10 ms; choose a safe sub‑spec.
    parameter int TR_NS  = {tr_ns}           // {timeout_ms} ms
) (
    input  logic        clk,
    input  logic        reset_n,

    // ── Config‑space CSR handshake (boilerplate wrapper drives these) ────────
    input  logic        pmcsr_wr,              // write strobe (one clk pulse)
    input  logic [15:0] pmcsr_wdata,           // PMCSR bits [15:0]
    output logic [15:0] pmcsr_rdata,           // read‑back value

    // ── Optional external wake event input ──────────────────────────────────
    input  logic        wake_evt,              // pulse => wake request
    output logic        pme_req               // to PCIe hard‑macro PME# pin
);

    // ───────────────────────── Internal registers ───────────────────────────
    logic [1:0] pwr_state;        // 00=D0, 11=D3hot
    logic       pme_en;
    logic       pme_stat;

    // Fake transition timer — counts TR_CLKS cycles after state change.
    localparam int TR_CLKS = TR_NS * CLK_HZ / 1_000_000_000; // integer division
    typedef logic [$clog2(TR_CLKS)-1:0] t_tr_cnt;
    t_tr_cnt tr_cnt;

    // ────────────────────────── State machine ───────────────────────────────
    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            pwr_state <= 2'b00;   // D0 on reset
            pme_en    <= 1'b0;
            pme_stat  <= 1'b0;
            tr_cnt    <= '0;
        end else begin
            // Handle config‑space writes
            if (pmcsr_wr) begin
                // Power state request & PME enable latch
                pme_en    <= pmcsr_wdata[15];
                // Clear PME_Status when driver writes a 1 to bit 14 per spec
                pme_stat  <= pmcsr_wdata[14] ? 1'b0 : pme_stat;
                // If state request changed, start countdown
                if (pmcsr_wdata[1:0] != pwr_state) begin
                    pwr_state <= pmcsr_wdata[1:0];
                    tr_cnt    <= TR_CLKS[$bits(tr_cnt)-1:0];
                end
            end

            // Transition countdown logic
            if (tr_cnt != 0) begin
                tr_cnt <= tr_cnt - 1;
            end

            // External wake event sets PME_Status if enabled
            if (wake_evt && pme_en) begin
                pme_stat <= 1'b1;
            end
        end
    end

    // ───────────────────────── Outputs ──────────────────────────────────────
    assign pmcsr_rdata = {{ pme_en,         // bit 15
                           pme_stat,       // bit 14
                           13'd0,          // bits 13:2 reserved/RO
                           pwr_state }};    // bits 1:0

    // Pulse PME# (active‑low in PCIe) for one cycle when PME_Status is set.
    assign pme_req = pme_stat;

endmodule""",
            clk_hz=self.config.clk_hz,
            tr_ns=self.config.transition_timeout_ns,
            timeout_ms=self.config.transition_timeout_ns // 1_000_000,
        )

        return module_code

    def generate_power_management_integration(self) -> str:
        """Generate integration code for the power management module."""

        integration_code = safe_format(
            """
    // ── Power Management Integration ─────────────────────────────────────────
    
    // PMCSR (Power Management Control/Status Register) signals
    logic        pmcsr_wr;
    logic [15:0] pmcsr_wdata;
    logic [15:0] pmcsr_rdata;
    logic        wake_evt;
    logic        pme_req;
    
    // Instantiate minimal power management stub
    pmcsr_stub #(
        .CLK_HZ({clk_hz}),
        .TR_NS({tr_ns})
    ) u_pmcsr_stub (
        .clk(clk),
        .reset_n(reset_n),
        .pmcsr_wr(pmcsr_wr),
        .pmcsr_wdata(pmcsr_wdata),
        .pmcsr_rdata(pmcsr_rdata),
        .wake_evt(wake_evt),
        .pme_req(pme_req)
    );
    
    // Connect PMCSR to config space at offset 0x44
    always_comb begin
        pmcsr_wr = cfg_wr_en && (cfg_addr[7:0] == 8'h44);
        pmcsr_wdata = cfg_wr_data[15:0];
        
        // Wake event can be triggered by external signals or internal logic
        wake_evt = 1'b0;  // Connect to actual wake sources as needed
    end
    
    // Integrate PMCSR read data into config space
    always_comb begin
        if (cfg_addr[7:0] == 8'h44) begin
            cfg_rd_data[15:0] = pmcsr_rdata;
            cfg_rd_data[31:16] = 16'h0;  // Upper 16 bits reserved
        end
    end""",
            clk_hz=self.config.clk_hz,
            tr_ns=self.config.transition_timeout_ns,
        )

        return integration_code

    def generate_power_declarations(self) -> str:
        """Generate minimal power management signal declarations."""

        declarations = """    // ── Minimal Power Management Declarations ──────────────────────────────
    // Power state tracking (simplified)
    logic [1:0] current_power_state;  // 00=D0, 11=D3hot
    logic       power_management_enabled;
    
    // PME (Power Management Event) signals
    logic       pme_enable;
    logic       pme_status;"""

        return declarations

    def generate_complete_power_management(self) -> str:
        """Generate complete simplified power management logic."""

        header = generate_sv_header_comment(
            "Simplified Power Management Module",
            description="Based on minimal pmcsr_stub design for essential PCIe power management",
        )

        components = [
            header,
            "",
            self.generate_power_declarations(),
            "",
            self.generate_power_management_integration(),
            "",
            "    // ── Power State Monitoring ──────────────────────────────────────────",
            "    assign current_power_state = pmcsr_rdata[1:0];",
            "    assign pme_enable = pmcsr_rdata[15];",
            "    assign pme_status = pmcsr_rdata[14];",
            "    assign power_management_enabled = 1'b1;",
            "",
            "    // ── Power Management Status Outputs ─────────────────────────────────",
            "    // These can be used by other modules to check power state",
            "    assign power_state_d0 = (current_power_state == 2'b00);",
            "    assign power_state_d3 = (current_power_state == 2'b11);",
            "    assign power_event_pending = pme_status;",
            "",
        ]

        return "\n".join(components)

    def get_module_dependencies(self) -> list:
        """Return list of module dependencies."""
        return ["pmcsr_stub"]

    def get_config_space_requirements(self) -> dict:
        """Return config space requirements for power management."""
        return {
            "pmcsr_offset": "0x44",
            "pmcsr_size": "16 bits",
            "description": "Power Management Control/Status Register",
        }
