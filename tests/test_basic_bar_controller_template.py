#!/usr/bin/env python3
"""
Test for the basic BAR controller template functionality.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from templating.template_renderer import TemplateRenderer


def test_basic_bar_controller_template():
    """Test that the basic BAR controller template renders correctly."""
    renderer = TemplateRenderer()

    # Test device info
    device_info = {"vendor_id": 0x10EE, "device_id": 0x0666}

    template_context = {
        "device_info": device_info,
    }

    # Render the template
    result = renderer.render_template(
        "systemverilog/basic_bar_controller.sv.j2", template_context
    )

    # Verify the template rendered correctly
    assert "module pcileech_tlps128_bar_controller" in result
    assert "parameter DEVICE_ID = 16'h0666" in result
    assert "parameter VENDOR_ID = 16'h10ee" in result
    assert "Device: 0x10EE:0x0666" in result
    assert "custom_pio_sel" in result
    assert "custom_pio_addr" in result
    assert "custom_pio_wdata" in result
    assert "custom_pio_we" in result
    assert "custom_pio_rdata" in result
    assert "device_control_sel" in result
    assert "status_regs_sel" in result
    assert "data_buffer_sel" in result
    assert "32'hDEADBEEF" in result


def test_basic_bar_controller_template_default_values():
    """Test that the template handles missing device info gracefully."""
    renderer = TemplateRenderer()

    # Empty device info to test defaults
    device_info = {}

    template_context = {
        "device_info": device_info,
    }

    # Render the template
    result = renderer.render_template(
        "systemverilog/basic_bar_controller.sv.j2", template_context
    )

    # Verify defaults are used
    assert "parameter DEVICE_ID = 16'h0000" in result
    assert "parameter VENDOR_ID = 16'h0000" in result
    assert "Device: 0x0000:0x0000" in result


if __name__ == "__main__":
    test_basic_bar_controller_template()
    test_basic_bar_controller_template_default_values()
    print("All tests passed!")
