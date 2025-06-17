#!/usr/bin/env python3
"""
Test suite for integrating external examples with advanced_sv modules.

This test suite validates that the advanced_sv modules can properly handle
real-world patterns found in external PCILeech examples.
"""

import re
import sys
from pathlib import Path

import pytest

from src.templating.advanced_sv_error import (
    ErrorHandlingConfig,
    ErrorHandlingGenerator,
    ErrorType,
)
from src.templating.advanced_sv_perf import DeviceType as PerfDeviceType
from src.templating.advanced_sv_perf import (
    PerformanceCounterConfig,
    PerformanceCounterGenerator,
)
from src.templating.advanced_sv_power import (
    PowerManagementConfig,
    PowerManagementGenerator,
    PowerState,
)
from src.manufacturing_variance import DeviceClass
from src.systemverilog_generator import (
    AdvancedSVGenerator,
    DeviceSpecificLogic,
    DeviceType,
)
from tests.utils import get_pcileech_wifi_sv_file, get_pcileech_wifi_tcl_file

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestExternalPatternIntegration:
    """Test integration of external patterns with advanced_sv modules."""

    @pytest.fixture
    def external_sv_example(self):
        """Load the external SystemVerilog example file from GitHub."""
        try:
            return get_pcileech_wifi_sv_file()
        except ValueError as e:
            pytest.skip(f"Failed to fetch SystemVerilog example from GitHub: {str(e)}")

    @pytest.fixture
    def external_tcl_example(self):
        """Load the external TCL example file from GitHub."""
        try:
            return get_pcileech_wifi_tcl_file()
        except ValueError as e:
            pytest.skip(f"Failed to fetch TCL example from GitHub: {str(e)}")

    @pytest.fixture
    def extracted_sv_patterns(self, external_sv_example):
        """Extract key patterns from the external SystemVerilog example."""
        patterns = {}

        # Extract module interfaces
        module_pattern = r"module\s+(\w+)\s*\((.*?)\);"
        module_match = re.search(module_pattern, external_sv_example, re.DOTALL)
        if module_match:
            patterns["module_name"] = module_match.group(1)
            patterns["module_interface"] = module_match.group(2)

        # Extract register handling patterns
        reg_pattern = r"logic\s+\[\d+:\d+\]\s+(\w+_reg)\s*="
        patterns["registers"] = re.findall(reg_pattern, external_sv_example)

        # Extract state machine patterns
        state_pattern = r"`define\s+(\w*STATE\w*|\w*S_\w+)\s+"
        patterns["states"] = re.findall(state_pattern, external_sv_example)

        # Extract clock domain handling
        clock_pattern = r"input\s+(?:logic\s+)?(\w+clk\w*)"
        patterns["clocks"] = re.findall(clock_pattern, external_sv_example)

        return patterns

    def test_advanced_sv_generator_with_external_patterns(self, extracted_sv_patterns):
        """Test that AdvancedSVGenerator can incorporate external patterns."""
        # Create a generator with configurations that match external patterns
        device_config = DeviceSpecificLogic(
            device_type=DeviceType.NETWORK_CONTROLLER,
            device_class=DeviceClass.INDUSTRIAL,
            max_payload_size=256,
            max_read_request_size=512,
            enable_dma=True,
        )

        power_config = PowerManagementConfig(
            supported_power_states=[PowerState.D0, PowerState.D3_HOT],
            enable_clock_gating=True,
            enable_aspm=True,
        )

        error_config = ErrorHandlingConfig(
            supported_error_types=[
                ErrorType.CORRECTABLE,
                ErrorType.UNCORRECTABLE_NON_FATAL,
            ],
            enable_parity_check=True,
            enable_crc_check=True,
        )

        perf_config = PerformanceCounterConfig(
            enable_transaction_counters=True, enable_bandwidth_monitoring=True
        )

        generator = AdvancedSVGenerator(
            power_config=power_config,
            error_config=error_config,
            perf_config=perf_config,
            device_config=device_config,
        )

        # Create registers based on external patterns
        regs = []
        if "registers" in extracted_sv_patterns:
            for i, reg_name in enumerate(extracted_sv_patterns["registers"]):
                # Strip _reg suffix if present
                if reg_name.endswith("_reg"):
                    reg_name = reg_name[:-4]

                regs.append(
                    {
                        "offset": 0x100 + (i * 4),
                        "name": reg_name,
                        "value": f"0x{i:08x}",
                        "rw": "rw" if i % 2 == 0 else "ro",
                        "context": {
                            "function": f"external_pattern_{i}",
                            "timing": "runtime",
                            "access_pattern": "balanced",
                        },
                    }
                )

        # If no registers found, add some default ones
        if not regs:
            regs = [
                {
                    "offset": 0x100,
                    "name": "control",
                    "value": "0x00000000",
                    "rw": "rw",
                    "context": {
                        "function": "device_control",
                        "timing": "runtime",
                        "access_pattern": "balanced",
                    },
                },
                {
                    "offset": 0x104,
                    "name": "status",
                    "value": "0x00000001",
                    "rw": "ro",
                    "context": {
                        "function": "status_check",
                        "timing": "runtime",
                        "access_pattern": "read_heavy",
                    },
                },
            ]

        # Generate SystemVerilog
        sv_content = generator.generate_advanced_systemverilog(regs)

        # Verify that the generated SystemVerilog has key elements
        assert "module" in sv_content
        assert "endmodule" in sv_content

        # Check for register declarations
        for reg in regs:
            assert (
                f"{reg['name']}_reg" in sv_content
            ), f"Missing register {reg['name']}_reg"

        # Check for power management features
        assert "Power Management" in sv_content

        # Check for error handling features
        assert "Error Handling" in sv_content

        # Check for performance counter features
        assert "Performance Counter" in sv_content

    def test_power_management_with_external_patterns(self, extracted_sv_patterns):
        """Test that PowerManagementGenerator can incorporate external patterns."""
        # Configure power management based on external patterns
        has_clock_gating = any(
            "clk" in clock for clock in extracted_sv_patterns.get("clocks", [])
        )
        has_multiple_clocks = len(extracted_sv_patterns.get("clocks", [])) > 1

        power_config = PowerManagementConfig(
            supported_power_states=[PowerState.D0, PowerState.D3_HOT],
            enable_clock_gating=has_clock_gating,
            enable_aspm=has_multiple_clocks,
            enable_power_domains=has_multiple_clocks,
        )

        generator = PowerManagementGenerator(power_config)

        # Generate power management code
        power_declarations = generator.generate_power_declarations()
        power_state_machine = generator.generate_power_state_machine()
        link_state_machine = generator.generate_link_state_machine()
        clock_gating = generator.generate_clock_gating()

        # Combine all power management code
        power_code = (
            power_declarations
            + "\n"
            + power_state_machine
            + "\n"
            + link_state_machine
            + "\n"
            + clock_gating
        )

        # Verify that the generated code has key elements
        assert "Power Management" in power_code

        # Check for power state declarations
        assert "current_power_state" in power_code

        # Check for state machine if states were found in the example
        if extracted_sv_patterns.get("states", []):
            assert "always_f" in power_code
            assert "case" in power_code

    def test_error_handling_with_external_patterns(self, extracted_sv_patterns):
        """Test that ErrorHandlingGenerator can incorporate external patterns."""
        # Configure error handling based on external patterns
        has_error_handling = any(
            "error" in state.lower()
            for state in extracted_sv_patterns.get("states", [])
        )

        error_config = ErrorHandlingConfig(
            supported_error_types=[
                ErrorType.CORRECTABLE,
                ErrorType.UNCORRECTABLE_NON_FATAL,
            ],
            enable_parity_check=has_error_handling,
            enable_crc_check=has_error_handling,
            enable_error_logging=has_error_handling,
        )

        generator = ErrorHandlingGenerator(error_config)

        # Generate error handling code
        error_declarations = generator.generate_error_declarations()
        error_detection = generator.generate_error_detection()
        error_state_machine = generator.generate_error_state_machine()
        error_logging = generator.generate_error_logging()

        # Combine all error handling code
        error_code = (
            error_declarations
            + "\n"
            + error_detection
            + "\n"
            + error_state_machine
            + "\n"
            + error_logging
        )

        # Verify that the generated code has key elements
        assert "Error Handling" in error_code

        # Check for error status declarations
        assert "error_status" in error_code

        # Check for state machine
        assert "always_f" in error_code
        assert "case" in error_code

    def test_performance_counters_with_external_patterns(self, extracted_sv_patterns):
        """Test that PerformanceCounterGenerator can incorporate external patterns."""
        # Configure performance counters based on external patterns
        is_network_device = (
            "pcileech" in extracted_sv_patterns.get("module_name", "").lower()
        )

        perf_config = PerformanceCounterConfig(
            enable_transaction_counters=True,
            enable_bandwidth_monitoring=is_network_device,
            enable_latency_measurement=is_network_device,
            enable_device_specific_counters=is_network_device,
        )

        device_type = (
            PerfDeviceType.NETWORK_CONTROLLER
            if is_network_device
            else PerfDeviceType.GENERIC
        )

        generator = PerformanceCounterGenerator(perf_config, device_type)

        # Generate performance counter code
        perf_declarations = generator.generate_perf_declarations()
        transaction_counters = generator.generate_transaction_counters()
        bandwidth_monitoring = generator.generate_bandwidth_monitoring()
        device_specific_counters = generator.generate_device_specific_counters()
        performance_grading = generator.generate_performance_grading()

        # Combine all performance counter code
        perf_code = (
            perf_declarations
            + "\n"
            + transaction_counters
            + "\n"
            + bandwidth_monitoring
            + "\n"
            + device_specific_counters
            + "\n"
            + performance_grading
        )

        # Verify that the generated code has key elements
        assert "Performance Counter" in perf_code

        # Check for counter declarations
        assert "counter" in perf_code.lower()

        # Check for device-specific counters if it's a network device
        if is_network_device:
            assert "Network Controller" in perf_code or "packet" in perf_code.lower()


class TestExternalExampleBasedRegisters:
    """Test register generation based on external examples."""

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

    def test_extract_registers_from_example(self, external_sv_example):
        """Test extracting register definitions from external example."""
        # Try different patterns for register definitions
        patterns = [
            # Original pattern
            r"logic\s+\[31:0\]\s+(\w+_reg)\s*=\s*32\'h([0-9a-fA-F]+);",
            # Alternative pattern for registers without initialization
            r"logic\s+\[31:0\]\s+(\w+_reg);",
            # Pattern for input/output registers
            r"(input|output)\s+logic\s+\[31:0\]\s+(\w+)",
            # Pattern for registers with different bit widths
            r"logic\s+\[\d+:\d+\]\s+(\w+)(?:_reg)?",
            # Pattern for parameters that might be used as registers
            r"parameter\s+(\w+)\s*=\s*([0-9a-fA-F]+)",
        ]

        registers = []
        for pattern in patterns:
            found_regs = re.findall(pattern, external_sv_example)
            if found_regs:
                # Handle different patterns with different group structures
                if pattern.startswith("(input|output)"):
                    # For input/output registers, the register name is in group
                    # 2
                    registers.extend([(reg[1], "0") for reg in found_regs])
                elif pattern.startswith("parameter"):
                    # For parameters, we have name and value
                    registers.extend(found_regs)
                elif "=" not in pattern:
                    # For registers without initialization, add a default value
                    registers.extend([(reg, "0") for reg in found_regs])
                else:
                    # For the original pattern, we already have name and value
                    registers.extend(found_regs)

        # If no registers found with any pattern, create some mock registers
        # based on module name
        if not registers:
            module_match = re.search(r"module\s+(\w+)", external_sv_example)
            if module_match:
                module_name = module_match.group(1)
                registers = [
                    (f"{module_name}_ctrl", "0"),
                    (f"{module_name}_status", "1"),
                ]
            else:
                registers = [("mock_ctrl", "0"), ("mock_status", "1")]

        # Log what we found
        print(f"Found {len(registers)} registers in the SystemVerilog file")

        # Convert to register definitions for our generator
        reg_defs = []
        for i, reg_info in enumerate(registers):
            if isinstance(reg_info, tuple) and len(reg_info) >= 1:
                reg_name = reg_info[0]
                reg_value = reg_info[1] if len(reg_info) > 1 else "0"

                # Strip _reg suffix if present
                if reg_name.endswith("_reg"):
                    reg_name = reg_name[:-4]

                # Extract register access type based on example patterns
                rw_type = "rw"
                if "status" in reg_name.lower():
                    rw_type = "ro"

                # Convert reg_value to proper hex format
                if reg_value == "0":
                    # Use index + 327 to generate a meaningful value for
                    # testing
                    hex_value = f"0x{(i + 327):08x}"
                else:
                    try:
                        # Try to parse as hex
                        val = (
                            int(reg_value, 16)
                            if isinstance(reg_value, str)
                            else reg_value
                        )
                        hex_value = f"0x{val:08x}"
                    except (ValueError, TypeError):
                        hex_value = f"0x{(i + 327):08x}"

                reg_defs.append(
                    {
                        "offset": 0x400
                        + (
                            i * 4
                        ),  # Assuming 4-byte aligned registers starting at 0x400
                        "name": reg_name,
                        "value": hex_value,
                        "rw": rw_type,
                        "context": {
                            "function": f"example_derived_{reg_name}",
                            "timing": "runtime",
                            "access_pattern": (
                                "read_heavy" if rw_type == "ro" else "balanced"
                            ),
                        },
                    }
                )

        # Generate SystemVerilog using these register definitions
        generator = AdvancedSVGenerator()
        sv_content = generator.generate_advanced_systemverilog(reg_defs)

        # Verify that the generated SystemVerilog includes all registers
        for reg_def in reg_defs:
            assert (
                f"{reg_def['name']}_reg" in sv_content
            ), f"Missing register {reg_def['name']}_reg"

            # Check for register value
            hex_value = reg_def["value"].replace("0x", "")
            assert (
                f"32'h{hex_value}" in sv_content or f"32'h0{hex_value}" in sv_content
            ), f"Register {reg_def['name']} doesn't have correct value"

    def test_register_access_patterns_from_example(self, external_sv_example):
        """Test register access patterns derived from external example."""
        # Extract register access patterns from the example
        read_pattern = r"case\((\w+)\)(.*?)endcase"
        read_match = re.search(read_pattern, external_sv_example, re.DOTALL)

        if read_match:
            read_match.group(1)
            read_cases = read_match.group(2)

            # Extract individual read cases
            case_pattern = r"32\'h([0-9a-fA-F]+):\s*(\w+)\s*=\s*(\w+);"
            cases = re.findall(case_pattern, read_cases)

            # Verify that cases were found
            assert len(cases) > 0, "No read cases found in external example"

            # Create register definitions based on these cases
            reg_defs = []
            for addr_hex, target, source in cases:
                addr = int(addr_hex, 16)
                reg_name = source
                if reg_name.endswith("_reg"):
                    reg_name = reg_name[:-4]

                reg_defs.append(
                    {
                        "offset": addr,
                        "name": reg_name,
                        "value": "0x00000000",  # Default value
                        "rw": "rw",  # Default access type
                        "context": {
                            "function": f"example_derived_{reg_name}",
                            "timing": "runtime",
                            "access_pattern": "read_heavy",
                        },
                    }
                )

            # Generate SystemVerilog using these register definitions
            generator = AdvancedSVGenerator()
            sv_content = generator.generate_advanced_systemverilog(reg_defs)

            # Verify that the generated SystemVerilog includes address decoding
            assert "case" in sv_content
            assert "bar_addr" in sv_content or "addr" in sv_content

            # Check for register addresses
            for reg_def in reg_defs:
                addr_hex = f"{reg_def['offset']:08x}"
                assert (
                    f"32'h{addr_hex}" in sv_content or f"32'h00{addr_hex}" in sv_content
                ), f"Register address 0x{addr_hex} not found"


class TestExternalExampleBasedStateMachines:
    """Test state machine generation based on external examples."""

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

    def test_extract_state_machines_from_example(self, external_sv_example):
        """Test extracting state machine definitions from external example."""
        # Extract state definitions from the example
        state_define_pattern = r"`define\s+(\w+)\s+(\w+)"
        re.findall(state_define_pattern, external_sv_example)

        # Extract state machine logic
        state_machine_pattern = r"(case\s*\(\w+\).*?endcase)"
        state_machines = re.findall(
            state_machine_pattern, external_sv_example, re.DOTALL
        )

        # Create a generator with state machine support
        power_config = PowerManagementConfig(
            supported_power_states=[PowerState.D0, PowerState.D3_HOT],
            enable_clock_gating=True,
        )

        error_config = ErrorHandlingConfig(
            supported_error_types=[
                ErrorType.CORRECTABLE,
                ErrorType.UNCORRECTABLE_NON_FATAL,
            ],
            enable_error_logging=True,
        )

        generator = AdvancedSVGenerator(
            power_config=power_config, error_config=error_config
        )

        # Create registers with state machine sequences
        regs = [
            {
                "offset": 0x100,
                "name": "state_ctrl",
                "value": "0x00000000",
                "rw": "rw",
                "context": {
                    "function": "state_control",
                    "timing": "runtime",
                    "sequences": [
                        {"function": "init", "position": 0, "operation": "write"},
                        {"function": "init", "position": 1, "operation": "read"},
                        {"function": "transition", "position": 0, "operation": "write"},
                        {"function": "transition", "position": 1, "operation": "read"},
                    ],
                },
            },
            {
                "offset": 0x104,
                "name": "state_status",
                "value": "0x00000001",
                "rw": "ro",
                "context": {
                    "function": "state_status",
                    "timing": "runtime",
                    "access_pattern": "read_heavy",
                },
            },
        ]

        # Generate SystemVerilog
        sv_content = generator.generate_advanced_systemverilog(regs)

        # Verify that the generated SystemVerilog has state machine elements
        assert "state" in sv_content.lower()
        assert "case" in sv_content

        # Check for power state machine
        assert "Power Management State Machine" in sv_content

        # Check for error state machine
        assert "Error Handling State Machine" in sv_content

        # Check for register-specific state machine
        assert "state_ctrl" in sv_content
