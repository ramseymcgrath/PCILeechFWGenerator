#!/usr/bin/env python3
"""
Advanced SystemVerilog Power Management Module

This module provides sophisticated power management logic generation for PCIe devices,
including D-states, L-states, clock gating, and ASPM support.

Advanced Power Management feature for the PCILeechFWGenerator project.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


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
    enable_power_domains: bool = True
    enable_aspm: bool = True  # Active State Power Management
    enable_wake_on_lan: bool = False

    # Power consumption estimates (mW)
    d0_power_mw: float = 1000.0
    d1_power_mw: float = 500.0
    d3_power_mw: float = 10.0


class PowerManagementGenerator:
    """Generator for advanced power management SystemVerilog logic."""

    def __init__(self, config: Optional[PowerManagementConfig] = None):
        """Initialize the power management generator."""
        self.config = config or PowerManagementConfig()

    def generate_power_declarations(self) -> str:
        """Generate power management signal declarations."""

        declarations = []

        declarations.append("    // Power Management Signals")
        declarations.append("    logic [1:0] current_power_state = 2'b00;  // D0 state")
        declarations.append("    logic [1:0] current_link_state = 2'b00;   // L0 state")
        declarations.append("    logic [15:0] power_transition_timer = 16'h0;")
        declarations.append("    logic power_state_changing = 1'b0;")
        declarations.append("    logic [15:0] link_transition_timer = 16'h0;")
        declarations.append("    logic link_state_changing = 1'b0;")

        if self.config.enable_clock_gating:
            declarations.append("    logic gated_clk;")
            declarations.append("    logic clock_enable;")

        if self.config.enable_power_domains:
            declarations.append("    logic core_power_enable = 1'b1;")
            declarations.append("    logic io_power_enable = 1'b1;")
            declarations.append("    logic memory_power_enable = 1'b1;")

        declarations.append("")

        return "\n".join(declarations)

    def generate_power_state_machine(self) -> str:
        """Generate the main power state machine logic."""

        if not self.config.supported_power_states:
            return "    // Power management disabled\n"

        power_logic = []

        power_logic.append("    // Advanced Power Management State Machine")
        power_logic.append("    typedef enum logic [2:0] {")
        power_logic.append("        PM_D0_ACTIVE    = 3'b000,")
        power_logic.append("        PM_D0_TO_D1     = 3'b001,")
        power_logic.append("        PM_D1_STANDBY   = 3'b010,")
        power_logic.append("        PM_D1_TO_D0     = 3'b011,")
        power_logic.append("        PM_D0_TO_D3     = 3'b100,")
        power_logic.append("        PM_D3_SUSPEND   = 3'b101,")
        power_logic.append("        PM_D3_TO_D0     = 3'b110,")
        power_logic.append("        PM_ERROR        = 3'b111")
        power_logic.append("    } power_state_t;")
        power_logic.append("")
        power_logic.append("    power_state_t pm_state = PM_D0_ACTIVE;")
        power_logic.append("    power_state_t pm_next_state;")
        power_logic.append("")

        # Power state transition logic
        power_logic.append("    // Power state transition logic")
        power_logic.append("    always_ff @(posedge clk or negedge reset_n) begin")
        power_logic.append("        if (!reset_n) begin")
        power_logic.append("            pm_state <= PM_D0_ACTIVE;")
        power_logic.append("            power_transition_timer <= 16'h0;")
        power_logic.append("            power_state_changing <= 1'b0;")
        power_logic.append("        end else begin")
        power_logic.append("            pm_state <= pm_next_state;")
        power_logic.append("            ")
        power_logic.append("            if (power_state_changing) begin")
        power_logic.append(
            "                power_transition_timer <= power_transition_timer + 1;"
        )
        power_logic.append("            end else begin")
        power_logic.append("                power_transition_timer <= 16'h0;")
        power_logic.append("            end")
        power_logic.append("        end")
        power_logic.append("    end")
        power_logic.append("")

        # Power state combinational logic
        power_logic.append("    // Power state combinational logic")
        power_logic.append("    always_comb begin")
        power_logic.append("        pm_next_state = pm_state;")
        power_logic.append("        power_state_changing = 1'b0;")
        power_logic.append("        ")
        power_logic.append("        case (pm_state)")
        power_logic.append("            PM_D0_ACTIVE: begin")
        power_logic.append("                if (power_state_req == 2'b01) begin")
        power_logic.append("                    pm_next_state = PM_D0_TO_D1;")
        power_logic.append("                    power_state_changing = 1'b1;")
        power_logic.append(
            "                end else if (power_state_req == 2'b11) begin"
        )
        power_logic.append("                    pm_next_state = PM_D0_TO_D3;")
        power_logic.append("                    power_state_changing = 1'b1;")
        power_logic.append("                end")
        power_logic.append("            end")
        power_logic.append("            ")
        power_logic.append("            PM_D0_TO_D1: begin")
        power_logic.append("                power_state_changing = 1'b1;")
        power_logic.append(
            f"                if (power_transition_timer >= {self.config.d0_to_d1_cycles}) begin"
        )
        power_logic.append("                    pm_next_state = PM_D1_STANDBY;")
        power_logic.append("                end")
        power_logic.append("            end")
        power_logic.append("            ")
        power_logic.append("            PM_D1_STANDBY: begin")
        power_logic.append("                if (power_state_req == 2'b00) begin")
        power_logic.append("                    pm_next_state = PM_D1_TO_D0;")
        power_logic.append("                    power_state_changing = 1'b1;")
        power_logic.append("                end")
        power_logic.append("            end")
        power_logic.append("            ")
        power_logic.append("            PM_D1_TO_D0: begin")
        power_logic.append("                power_state_changing = 1'b1;")
        power_logic.append(
            f"                if (power_transition_timer >= {
                self.config.d1_to_d0_cycles}) begin"
        )
        power_logic.append("                    pm_next_state = PM_D0_ACTIVE;")
        power_logic.append("                end")
        power_logic.append("            end")
        power_logic.append("            ")
        power_logic.append("            PM_D0_TO_D3: begin")
        power_logic.append("                power_state_changing = 1'b1;")
        power_logic.append(
            f"                if (power_transition_timer >= {
                self.config.d0_to_d3_cycles}) begin"
        )
        power_logic.append("                    pm_next_state = PM_D3_SUSPEND;")
        power_logic.append("                end")
        power_logic.append("            end")
        power_logic.append("            ")
        power_logic.append("            PM_D3_SUSPEND: begin")
        power_logic.append("                if (power_state_req == 2'b00) begin")
        power_logic.append("                    pm_next_state = PM_D3_TO_D0;")
        power_logic.append("                    power_state_changing = 1'b1;")
        power_logic.append("                end")
        power_logic.append("            end")
        power_logic.append("            ")
        power_logic.append("            PM_D3_TO_D0: begin")
        power_logic.append("                power_state_changing = 1'b1;")
        power_logic.append(
            f"                if (power_transition_timer >= {
                self.config.d3_to_d0_cycles}) begin"
        )
        power_logic.append("                    pm_next_state = PM_D0_ACTIVE;")
        power_logic.append("                end")
        power_logic.append("            end")
        power_logic.append("            ")
        power_logic.append("            default: pm_next_state = PM_D0_ACTIVE;")
        power_logic.append("        endcase")
        power_logic.append("    end")
        power_logic.append("")

        return "\n".join(power_logic)

    def generate_link_state_machine(self) -> str:
        """Generate link power state management logic."""

        if not self.config.enable_aspm:
            return "    // Link power management disabled\n"

        link_logic = []

        link_logic.append("    // Link Power State Management (ASPM)")
        link_logic.append("    typedef enum logic [1:0] {")
        link_logic.append("        LINK_L0  = 2'b00,")
        link_logic.append("        LINK_L0S = 2'b01,")
        link_logic.append("        LINK_L1  = 2'b10,")
        link_logic.append("        LINK_L2  = 2'b11")
        link_logic.append("    } link_state_t;")
        link_logic.append("")
        link_logic.append("    link_state_t link_state = LINK_L0;")
        link_logic.append("    logic [15:0] link_idle_counter = 16'h0;")
        link_logic.append("")

        # Link state transition logic
        link_logic.append("    // Link state transition logic")
        link_logic.append("    always_ff @(posedge clk or negedge reset_n) begin")
        link_logic.append("        if (!reset_n) begin")
        link_logic.append("            link_state <= LINK_L0;")
        link_logic.append("            link_idle_counter <= 16'h0;")
        link_logic.append("            link_transition_timer <= 16'h0;")
        link_logic.append("        end else begin")
        link_logic.append("            case (link_state)")
        link_logic.append("                LINK_L0: begin")
        link_logic.append("                    if (bar_wr_en || bar_rd_en) begin")
        link_logic.append("                        link_idle_counter <= 16'h0;")
        link_logic.append("                    end else begin")
        link_logic.append(
            "                        link_idle_counter <= link_idle_counter + 1;"
        )
        link_logic.append(
            f"                        if (link_idle_counter >= {
                self.config.l0_to_l0s_cycles}) begin"
        )
        link_logic.append("                            link_state <= LINK_L0S;")
        link_logic.append("                            link_transition_timer <= 16'h0;")
        link_logic.append("                        end")
        link_logic.append("                    end")
        link_logic.append("                end")
        link_logic.append("                ")
        link_logic.append("                LINK_L0S: begin")
        link_logic.append("                    if (bar_wr_en || bar_rd_en) begin")
        link_logic.append("                        link_state <= LINK_L0;")
        link_logic.append("                        link_idle_counter <= 16'h0;")
        link_logic.append("                    end else begin")
        link_logic.append(
            "                        link_transition_timer <= link_transition_timer + 1;"
        )
        link_logic.append(
            f"                        if (link_transition_timer >= {
                self.config.l0_to_l1_cycles}) begin"
        )
        link_logic.append("                            link_state <= LINK_L1;")
        link_logic.append("                        end")
        link_logic.append("                    end")
        link_logic.append("                end")
        link_logic.append("                ")
        link_logic.append("                LINK_L1: begin")
        link_logic.append("                    if (bar_wr_en || bar_rd_en) begin")
        link_logic.append("                        link_state <= LINK_L0;")
        link_logic.append("                        link_idle_counter <= 16'h0;")
        link_logic.append("                        link_transition_timer <= 16'h0;")
        link_logic.append("                    end")
        link_logic.append("                end")
        link_logic.append("                ")
        link_logic.append("                default: link_state <= LINK_L0;")
        link_logic.append("            endcase")
        link_logic.append("        end")
        link_logic.append("    end")
        link_logic.append("")

        return "\n".join(link_logic)

    def generate_clock_gating(self) -> str:
        """Generate clock gating logic for power savings."""

        if not self.config.enable_clock_gating:
            return "    // Clock gating disabled\n"

        clock_logic = []

        clock_logic.append("    // Clock Gating for Power Management")
        clock_logic.append("    always_comb begin")
        clock_logic.append("        case (pm_state)")
        clock_logic.append("            PM_D0_ACTIVE: clock_enable = 1'b1;")
        clock_logic.append(
            "            PM_D1_STANDBY: clock_enable = link_state == LINK_L0;"
        )
        clock_logic.append("            PM_D3_SUSPEND: clock_enable = 1'b0;")
        clock_logic.append("            default: clock_enable = power_state_changing;")
        clock_logic.append("        endcase")
        clock_logic.append("    end")
        clock_logic.append("    ")
        clock_logic.append("    assign gated_clk = clk & clock_enable;")
        clock_logic.append("")

        return "\n".join(clock_logic)

    def generate_power_outputs(self) -> str:
        """Generate power management output assignments."""

        outputs = []

        outputs.append("    // Power Management Outputs")
        outputs.append("    always_comb begin")
        outputs.append("        case (pm_state)")
        outputs.append(
            "            PM_D0_ACTIVE, PM_D1_TO_D0, PM_D3_TO_D0: current_power_state = 2'b00;  // D0"
        )
        outputs.append(
            "            PM_D0_TO_D1, PM_D1_STANDBY: current_power_state = 2'b01;  // D1"
        )
        outputs.append(
            "            PM_D0_TO_D3, PM_D3_SUSPEND: current_power_state = 2'b11;  // D3"
        )
        outputs.append("            default: current_power_state = 2'b00;")
        outputs.append("        endcase")
        outputs.append("    end")
        outputs.append("    ")
        outputs.append("    assign current_link_state = link_state;")
        outputs.append("    assign power_state_ack = current_power_state;")
        outputs.append("    assign link_state_ack = current_link_state;")
        outputs.append("")

        return "\n".join(outputs)

    def generate_complete_power_management(self) -> str:
        """Generate complete power management logic."""

        components = [
            self.generate_power_declarations(),
            self.generate_power_state_machine(),
            self.generate_link_state_machine(),
            self.generate_clock_gating(),
            self.generate_power_outputs(),
        ]

        return "\n".join(components)
