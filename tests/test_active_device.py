#!/usr/bin/env python3
"""
Test script for active device interrupt functionality.

This test verifies:
1. Active device configuration parsing
2. SystemVerilog generation with active device features
3. Proper module instantiation and parameter configuration
4. Timer-based interrupt generation logic
5. MSI/MSI-X TLP construction
"""

import re
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from src.templating.template_renderer import TemplateRenderer


class TestActiveDeviceInterrupt:
    """Test cases for active device interrupt functionality."""

    @pytest.fixture
    def template_renderer(self):
        """Create a TemplateRenderer instance."""
        template_dir = Path(__file__).parent.parent / "src" / "templates"
        return TemplateRenderer(template_dir=template_dir)

    @pytest.fixture
    def basic_device_config(self):
        """Create a basic device configuration with active device disabled."""
        return {
            "name": "test_device",
            "device_type": "network",
            "device_class": "consumer",
            "identification": {
                "vendor_id": 0x8086,
                "device_id": 0x10D3,
                "class_code": 0x020000,
                "revision_id": 0x00,
            },
            "registers": {
                "command": 0x0006,
                "status": 0x0210,
                "revision_id": 0x01,
                "cache_line_size": 0x10,
                "latency_timer": 0x00,
                "header_type": 0x00,
                "bist": 0x00,
            },
            "capabilities": {
                "max_payload_size": 256,
                "msi_vectors": 1,
                "msix_vectors": 0,
                "supports_msi": True,
                "supports_msix": False,
                "supports_power_management": True,
                "supports_advanced_error_reporting": False,
                "link_width": 1,
                "link_speed": "2.5GT/s",
            },
        }

    @pytest.fixture
    def active_device_config_msi(self, basic_device_config):
        """Create device configuration with MSI-based active device interrupts."""
        config = basic_device_config.copy()
        config["capabilities"]["active_device"] = {
            "enabled": True,
            "timer_period": 100000,
            "timer_enable": True,
            "interrupt_mode": "msi",
            "interrupt_vector": 0,
            "priority": 15,
            "msi_vector_width": 5,
            "msi_64bit_addr": False,
            "num_interrupt_sources": 8,
            "default_source_priority": 8,
            "num_sources": 8,
            "device_id": "16'h10D3",
            "vendor_id": "16'h8086",
            "completer_id": "16'h0100",
            "num_msix": 0,
            "msix_table_bir": 0,
            "msix_table_offset": 0,
            "msix_pba_bir": 0,
            "msix_pba_offset": 0,
            "default_priority": 8,
        }
        return config

    @pytest.fixture
    def active_device_config_msix(self, basic_device_config):
        """Create device configuration with MSI-X based active device interrupts."""
        config = basic_device_config.copy()
        config["capabilities"]["supports_msix"] = True
        config["capabilities"]["msix_vectors"] = 16
        config["capabilities"]["active_device"] = {
            "enabled": True,
            "timer_period": 50000,
            "timer_enable": True,
            "interrupt_mode": "msix",
            "interrupt_vector": 0,
            "priority": 15,
            "msi_vector_width": 0,
            "msi_64bit_addr": False,
            "num_interrupt_sources": 16,
            "default_source_priority": 8,
            "num_sources": 16,
            "device_id": "16'h10D3",
            "vendor_id": "16'h8086",
            "completer_id": "16'h0100",
            "num_msix": 16,
            "msix_table_bir": 2,
            "msix_table_offset": "32'h1000",
            "msix_pba_bir": 2,
            "msix_pba_offset": "32'h2000",
            "default_priority": 8,
        }
        return config

    def test_active_device_disabled(self, template_renderer, basic_device_config):
        """Test that active device module is not instantiated when disabled."""
        # Render the top-level wrapper
        context = {
            "header": "// Test header",
            "active_device_config": None,  # No active device config
            "vendor_id": hex(basic_device_config["identification"]["vendor_id"]),
            "device_id": hex(basic_device_config["identification"]["device_id"]),
        }

        result = template_renderer.render_template(
            "sv/top_level_wrapper.sv.j2", context
        )

        # Verify active_device_interrupt module is not instantiated
        assert "active_device_interrupt" not in result
        assert "timer_interrupt" not in result

    def test_active_device_msi_generation(
        self, template_renderer, active_device_config_msi
    ):
        """Test SystemVerilog generation with MSI-based active device interrupts."""
        # Prepare context for template rendering
        active_config = active_device_config_msi["capabilities"]["active_device"]
        context = {
            "header": "// Test header for MSI active device",
            "active_device_config": active_config,
        }

        # Render the active device interrupt module
        result = template_renderer.render_template(
            "sv/active_device_interrupt.sv.j2", context
        )

        # Verify module declaration
        assert "module active_device_interrupt" in result

        # Verify parameters
        assert f"parameter TIMER_PERIOD = {active_config['timer_period']}" in result
        assert (
            f"parameter TIMER_ENABLE = {1 if active_config['timer_enable'] else 0}"
            in result
        )
        assert (
            f"parameter MSI_VECTOR_WIDTH = {active_config['msi_vector_width']}"
            in result
        )
        assert (
            f"parameter NUM_INTERRUPT_SOURCES = {active_config['num_interrupt_sources']}"
            in result
        )

        # Verify timer logic
        assert "timer_counter" in result
        assert "timer_expired" in result
        assert "if (timer_counter >= TIMER_PERIOD)" in result

        # Verify MSI state machine
        assert "INTR_MSI_SETUP" in result
        assert "INTR_MSI_SEND" in result
        assert "INTR_MSI_WAIT" in result
        assert "cfg_interrupt_msienable" in result

        # Verify interrupt arbitration
        assert "pending_interrupts" in result
        assert "selected_source" in result
        assert "selected_priority" in result

    def test_active_device_msix_generation(
        self, template_renderer, active_device_config_msix
    ):
        """Test SystemVerilog generation with MSI-X based active device interrupts."""
        # Prepare context for template rendering
        active_config = active_device_config_msix["capabilities"]["active_device"]
        context = {
            "header": "// Test header for MSI-X active device",
            "active_device_config": active_config,
        }

        # Render the active device interrupt module
        result = template_renderer.render_template(
            "sv/active_device_interrupt.sv.j2", context
        )

        # Verify MSI-X specific parameters
        assert f"parameter NUM_MSIX = {active_config['num_msix']}" in result
        assert f"parameter MSIX_TABLE_BIR = {active_config['msix_table_bir']}" in result
        assert (
            f"parameter MSIX_TABLE_OFFSET = {active_config['msix_table_offset']}"
            in result
        )

        # Verify MSI-X table memory
        assert "msix_table_mem" in result
        assert "msix_pba_mem" in result

        # Verify MSI-X TLP generation
        assert "INTR_MSIX_SETUP" in result
        assert "INTR_MSIX_TLP_HDR" in result
        assert "INTR_MSIX_TLP_DATA" in result
        assert "tlp_tx_valid" in result
        assert "tlp_tx_data" in result

        # Verify MSI-X entry structure
        assert "msix_entry_t" in result
        assert "msg_addr_lo" in result
        assert "msg_addr_hi" in result
        assert "msg_data" in result
        assert "vector_ctrl" in result

    def test_top_level_integration(self, template_renderer, active_device_config_msi):
        """Test integration of active device interrupt in top-level wrapper."""
        # Prepare context
        active_config = active_device_config_msi["capabilities"]["active_device"]
        context = {
            "header": "// Top-level wrapper test",
            "active_device_config": active_config,
            "vendor_id": hex(active_device_config_msi["identification"]["vendor_id"]),
            "device_id": hex(active_device_config_msi["identification"]["device_id"]),
        }

        # Render top-level wrapper
        result = template_renderer.render_template(
            "sv/top_level_wrapper.sv.j2", context
        )

        # Verify instantiation
        assert "active_device_interrupt #(" in result
        assert "active_device_int (" in result

        # Verify parameter connections
        assert f".TIMER_PERIOD({active_config['timer_period']})" in result
        assert (
            f".NUM_INTERRUPT_SOURCES({active_config['num_interrupt_sources']})"
            in result
        )

        # Verify signal connections
        assert ".interrupt_sources(interrupt_sources)" in result
        assert ".interrupt_ack(interrupt_ack)" in result
        assert ".timer_interrupt_pending()" in result
        assert ".interrupt_count()" in result

    def test_interrupt_priority_arbitration(
        self, template_renderer, active_device_config_msi
    ):
        """Test interrupt priority arbitration logic."""
        active_config = active_device_config_msi["capabilities"]["active_device"]
        context = {
            "header": "// Priority arbitration test",
            "active_device_config": active_config,
        }

        result = template_renderer.render_template(
            "sv/active_device_interrupt.sv.j2", context
        )

        # Verify priority logic
        assert "source_priority" in result
        assert "selected_priority" in result
        assert (
            "if (!interrupt_pending || source_priority[i] > selected_priority)"
            in result
        )

        # Verify timer has highest priority
        assert "selected_priority = 4'hF;  // Highest priority" in result

    def test_performance_counters(self, template_renderer, active_device_config_msi):
        """Test performance counter implementation."""
        active_config = active_device_config_msi["capabilities"]["active_device"]
        context = {
            "header": "// Performance counter test",
            "active_device_config": active_config,
        }

        result = template_renderer.render_template(
            "sv/active_device_interrupt.sv.j2", context
        )

        # Verify performance counters
        assert "interrupt_count_reg" in result
        assert "msi_count" in result
        assert "msix_count" in result
        assert "legacy_count" in result

        # Verify counter increments
        assert "interrupt_count_reg <= interrupt_count_reg + 1'b1" in result
        assert "msi_count <= msi_count + 1'b1" in result

    def test_error_handling(self, template_renderer, active_device_config_msix):
        """Test error handling and assertions."""
        active_config = active_device_config_msix["capabilities"]["active_device"]
        context = {
            "header": "// Error handling test",
            "active_device_config": active_config,
        }

        result = template_renderer.render_template(
            "sv/active_device_interrupt.sv.j2", context
        )

        # Verify error state
        assert "INTR_ERROR" in result

        # Verify assertions
        assert "property p_no_simultaneous_interrupts" in result
        assert "property p_valid_msix_vector" in result
        assert "assert property" in result

    def verify_sv_syntax(self, sv_content: str) -> bool:
        """Basic SystemVerilog syntax verification."""
        import re

        # More precise regex for SystemVerilog begin/end
        begin_pattern = r"\bbegin\b"
        end_pattern = r"\bend\b"

        # Check for balanced begin/end
        begin_count = len(re.findall(begin_pattern, sv_content))
        end_count = len(re.findall(end_pattern, sv_content))
        if begin_count != end_count:
            return False

        # Check for module/endmodule (more precise)
        module_pattern = r"^\s*module\s+\w+"
        endmodule_pattern = r"^\s*endmodule\s*$"
        module_count = len(re.findall(module_pattern, sv_content, re.MULTILINE))
        endmodule_count = len(re.findall(endmodule_pattern, sv_content, re.MULTILINE))
        if module_count != endmodule_count:
            return False

        # Check for balanced parentheses
        if sv_content.count("(") != sv_content.count(")"):
            return False

        # Check for balanced brackets
        if sv_content.count("[") != sv_content.count("]"):
            return False

        return True

    def test_generated_sv_syntax(self, template_renderer, active_device_config_msi):
        """Test that generated SystemVerilog has valid syntax."""
        active_config = active_device_config_msi["capabilities"]["active_device"]
        context = {"header": "// Syntax test", "active_device_config": active_config}

        result = template_renderer.render_template(
            "sv/active_device_interrupt.sv.j2", context
        )

        assert self.verify_sv_syntax(
            result
        ), "Generated SystemVerilog has syntax errors"

    def test_tlp_construction(self, template_renderer, active_device_config_msix):
        """Test TLP (Transaction Layer Packet) construction for MSI-X."""
        active_config = active_device_config_msix["capabilities"]["active_device"]
        context = {
            "header": "// TLP construction test",
            "active_device_config": active_config,
        }

        result = template_renderer.render_template(
            "sv/active_device_interrupt.sv.j2", context
        )

        # Verify TLP header construction
        assert "3'b010,           // Format: 3DW header with data" in result
        assert "5'b00000,         // Type: Memory Write" in result
        assert "10'h001           // Length: 1 DW" in result

        # Verify TLP data fields
        assert "COMPLETER_ID,     // Requester ID" in result
        assert "msix_entry.msg_addr_lo" in result
        assert "msix_entry.msg_data" in result


def test_example_configurations():
    """Test that example configurations are valid."""
    example_path = (
        Path(__file__).parent.parent
        / "configs"
        / "devices"
        / "active_device_minimal.yaml"
    )

    # Verify example file exists
    assert example_path.exists(), f"Example configuration not found at {example_path}"

    # Load and validate configuration
    with open(example_path, "r") as f:
        config = yaml.safe_load(f)

    # Verify required fields
    assert "capabilities" in config
    assert "active_device" in config["capabilities"]

    active_config = config["capabilities"]["active_device"]

    # Verify all required active device fields
    required_fields = [
        "enabled",
        "timer_period",
        "timer_enable",
        "interrupt_mode",
        "interrupt_vector",
        "priority",
        "msi_vector_width",
        "msi_64bit_addr",
        "num_interrupt_sources",
        "default_source_priority",
    ]

    for field in required_fields:
        assert field in active_config, f"Missing required field: {field}"

    # Verify field values are reasonable
    assert active_config["timer_period"] > 0
    assert active_config["priority"] >= 0 and active_config["priority"] <= 15
    assert active_config["num_interrupt_sources"] > 0
    assert active_config["interrupt_mode"] in ["msi", "msix", "legacy"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
