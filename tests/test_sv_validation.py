#!/usr/bin/env python3
"""
Test suite for validating SystemVerilog generation against real-world examples.

This test suite compares the SystemVerilog generation capabilities of the PCILeech firmware
generator against real-world examples from the pcileech-wifi-v2 project.
"""

import re
import sys
from pathlib import Path

import pytest

from advanced_sv_error import ErrorHandlingConfig
from advanced_sv_main import AdvancedSVGenerator as MainSVGenerator
from advanced_sv_main import (
    DeviceSpecificLogic,
    DeviceType,
)
from tests.utils import get_pcileech_wifi_sv_file

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestSystemVerilogValidation:
    """Test SystemVerilog generation against real-world examples."""

    @pytest.fixture
    def external_sv_example(self):
        """Load the external SystemVerilog example file from GitHub."""
        try:
            return get_pcileech_wifi_sv_file()
        except ValueError as e:
            pytest.skip(f"Failed to fetch SystemVerilog example from GitHub: {str(e)}")

    @pytest.fixture
    def mock_register_data(self):
        """Create mock register data based on the external example."""
        return [
            {
                "offset": 0x0,
                "name": "device_id",
                "value": "0x1814",
                "rw": "ro",
                "context": {
                    "function": "identification",
                    "dependencies": [],
                    "timing": "early",
                    "access_pattern": "read_only",
                },
            },
            {
                "offset": 0x4,
                "name": "status",
                "value": "0x1",
                "rw": "ro",
                "context": {
                    "function": "status_check",
                    "dependencies": [],
                    "timing": "runtime",
                    "access_pattern": "read_heavy",
                },
            },
            {
                "offset": 0x8,
                "name": "control",
                "value": "0x0",
                "rw": "rw",
                "context": {
                    "function": "device_control",
                    "dependencies": ["status"],
                    "timing": "runtime",
                    "access_pattern": "balanced",
                },
            },
        ]

    def test_sv_module_structure_matches_example(
        self, external_sv_example, mock_register_data
    ):
        """Test that our SystemVerilog generation follows the same module structure as the example."""
        # Extract module structure from the example
        self._extract_sv_modules(external_sv_example)

        # Generate SystemVerilog with our generator
        generator = MainSVGenerator()
        sv_content = generator.generate_advanced_systemverilog(mock_register_data)

        # Extract module structure from our generated SystemVerilog
        generated_modules = self._extract_sv_modules(sv_content)

        # Verify that our SystemVerilog has modules
        assert len(generated_modules) > 0, "No modules found in generated SystemVerilog"

        # Verify that our main module has similar structure to the example
        generated_modules[0]
        # The module name might not contain the word "module", so we'll check
        # the content instead
        assert "module" in sv_content
        assert "endmodule" in sv_content

        # Check for key structural elements
        assert "input logic clk" in sv_content, "Missing clock input"
        assert (
            "input logic reset" in sv_content or "input logic reset_n" in sv_content
        ), "Missing reset input"
        assert "always_" in sv_content, "Missing always block"

    def test_sv_register_handling_matches_example(
        self, external_sv_example, mock_register_data
    ):
        """Test that register handling in SystemVerilog matches the example pattern."""
        # Generate SystemVerilog with our generator
        generator = MainSVGenerator()
        sv_content = generator.generate_advanced_systemverilog(mock_register_data)

        # Check for register declarations
        for reg in mock_register_data:
            reg_name = reg["name"]
            assert (
                f"{reg_name}_reg" in sv_content
            ), f"Missing register declaration for {reg_name}"

        # Check for read logic pattern (similar to example)
        assert "always_comb" in sv_content, "Missing combinational logic block"
        assert "case" in sv_content, "Missing case statement for address decoding"

        # Check for write logic pattern (similar to example)
        assert "always_f" in sv_content, "Missing sequential logic block"

    def test_sv_clock_domain_handling(self, external_sv_example):
        """Test that clock domain handling matches the example pattern."""
        # Extract clock domain handling from the example
        clock_domains = self._extract_clock_domains(external_sv_example)

        # Generate SystemVerilog with clock domain support
        device_config = DeviceSpecificLogic(device_type=DeviceType.NETWORK_CONTROLLER)
        generator = MainSVGenerator(device_config=device_config)

        regs = [
            {
                "offset": 0x100,
                "name": "test_reg",
                "value": "0x0",
                "rw": "rw",
                "context": {
                    "function": "test",
                    "timing": "runtime",
                },
            }
        ]

        sv_content = generator.generate_advanced_systemverilog(regs)

        # Check for clock domain handling
        assert "clk" in sv_content, "Missing clock signal"

        # Check for clock domain crossing if the example has it
        if "clk_pcie" in clock_domains and "clk_sys" in clock_domains:
            assert (
                "Clock Domain" in sv_content or "clock domain" in sv_content.lower()
            ), "Missing clock domain handling"

    def test_sv_interface_compatibility(self, external_sv_example):
        """Test that our SystemVerilog interfaces are compatible with the example."""
        # Extract interfaces from the example
        example_interfaces = self._extract_interfaces(external_sv_example)

        # Generate SystemVerilog with our generator
        device_config = DeviceSpecificLogic(device_type=DeviceType.NETWORK_CONTROLLER)
        generator = MainSVGenerator(device_config=device_config)

        regs = [
            {
                "offset": 0x100,
                "name": "test_reg",
                "value": "0x0",
                "rw": "rw",
            }
        ]

        sv_content = generator.generate_advanced_systemverilog(regs)

        # Check for compatible interface signals
        if "bar_addr" in example_interfaces:
            assert "bar_addr" in sv_content, "Missing BAR address signal"

        if "bar_rd_data" in example_interfaces:
            assert (
                "bar_rd_data" in sv_content or "rd_data" in sv_content
            ), "Missing read data signal"

    def test_sv_error_handling_compatibility(self, external_sv_example):
        """Test that our error handling is compatible with the example."""
        # Check if the example has error handling
        has_error_handling = "error" in external_sv_example.lower()

        if has_error_handling:
            # Generate SystemVerilog with error handling
            error_config = ErrorHandlingConfig(
                enable_ecc=True, enable_parity_check=True, enable_crc_check=True
            )
            generator = MainSVGenerator(error_config=error_config)

            regs = [
                {
                    "offset": 0x100,
                    "name": "test_reg",
                    "value": "0x0",
                    "rw": "rw",
                }
            ]

            sv_content = generator.generate_advanced_systemverilog(regs)

            # Check for error handling signals
            assert "error" in sv_content.lower(), "Missing error handling"

    def _extract_sv_modules(self, sv_content):
        """Extract module definitions from SystemVerilog content."""
        module_pattern = r"module\s+(\w+).*?endmodule"
        return re.findall(module_pattern, sv_content, re.DOTALL)

    def _extract_clock_domains(self, sv_content):
        """Extract clock domain information from SystemVerilog content."""
        clock_signals = re.findall(r"input\s+(?:logic\s+)?(\w+clk\w*)", sv_content)
        return clock_signals

    def _extract_interfaces(self, sv_content):
        """Extract interface signals from SystemVerilog content."""
        # Extract input/output signals
        input_signals = re.findall(r"input\s+(?:logic\s+)?(\w+)", sv_content)
        output_signals = re.findall(r"output\s+(?:logic\s+)?(\w+)", sv_content)

        return input_signals + output_signals


class TestAdvancedSVFeatureValidation:
    """Test advanced SystemVerilog features against real-world examples."""

    @pytest.fixture
    def external_sv_example(self):
        """Load the external SystemVerilog example file from GitHub."""
        try:
            return get_pcileech_wifi_sv_file()
        except ValueError as e:
            pytest.skip(
                f"Failed to fetch SystemVerilog example from GitHub: {
                    str(e)}"
            )

    def test_state_machine_generation(self, external_sv_example):
        """Test that our state machine generation is compatible with real-world examples."""
        # Check if the example has state machines
        has_state_machine = "state" in external_sv_example.lower()

        if has_state_machine:
            # Extract state machine pattern from example
            states = self._extract_states(external_sv_example)

            # Generate SystemVerilog with state machine
            generator = MainSVGenerator()

            regs = [
                {
                    "offset": 0x100,
                    "name": "state_reg",
                    "value": "0x0",
                    "rw": "rw",
                    "context": {
                        "function": "state_control",
                        "timing": "runtime",
                        "sequences": [
                            {"function": "init", "position": 0, "operation": "write"},
                            {"function": "init", "position": 1, "operation": "read"},
                        ],
                    },
                }
            ]

            sv_content = generator.generate_advanced_systemverilog(regs)

            # Check for state machine elements
            assert "state" in sv_content.lower(), "Missing state machine"

            # If example has specific state encoding, check for similar pattern
            if len(states) > 0:
                state_pattern_found = False
                for state in states:
                    if state.lower() in sv_content.lower():
                        state_pattern_found = True
                        break

                assert state_pattern_found, "No compatible state pattern found"

    def test_memory_interface_compatibility(self, external_sv_example):
        """Test that our memory interface is compatible with real-world examples."""
        # Check if the example has memory interfaces
        has_memory = (
            "bram" in external_sv_example.lower()
            or "memory" in external_sv_example.lower()
        )

        if has_memory:
            # Generate SystemVerilog with memory interface
            generator = MainSVGenerator()

            regs = [
                {
                    "offset": 0x100,
                    "name": "mem_ctrl",
                    "value": "0x0",
                    "rw": "rw",
                },
                {
                    "offset": 0x104,
                    "name": "mem_data",
                    "value": "0x0",
                    "rw": "rw",
                },
            ]

            sv_content = generator.generate_advanced_systemverilog(regs)

            # Check for memory-related signals
            assert (
                "mem" in sv_content.lower() or "memory" in sv_content.lower()
            ), "Missing memory interface"

    def _extract_states(self, sv_content):
        """Extract state definitions from SystemVerilog content."""
        # Look for state definitions like `S_IDLE`, `STATE_IDLE`, etc.
        state_pattern = r"`define\s+(\w*STATE\w*|\w*S_\w+)\s+"
        states = re.findall(state_pattern, sv_content)

        # Also look for enum state definitions
        enum_pattern = r"typedef\s+enum\s+.*?{(.*?)}\s+\w+;"
        enum_match = re.search(enum_pattern, sv_content, re.DOTALL)
        if enum_match:
            enum_states = re.findall(r"\b(\w+)\b", enum_match.group(1))
            states.extend(enum_states)

        return states
