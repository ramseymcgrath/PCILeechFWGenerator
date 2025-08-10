#!/usr/bin/env python3
"""
Unit tests for template rendering with various data formats.

Tests that templates handle different data structures correctly:
- String values from enum.value conversions
- Dictionary objects with nested value keys
- Objects with .value attributes
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.templating.template_renderer import TemplateRenderer


class TestTemplateRendering:
    """Test template rendering with various data formats."""

    @pytest.fixture
    def renderer(self):
        """Create a template renderer instance."""
        return TemplateRenderer()

    @pytest.fixture
    def base_context(self):
        """Base context with required fields for templates."""
        return {
            "header": "// Test header",
            "device_config": {
                "device_type": "network",  # String value (from enum.value)
                "device_class": "enterprise",  # String value (from enum.value)
                "max_payload_size": 256,
                "msi_vectors": 4,
                "device_bdf": "0000:06:00.0",
                "device_id": "0x1234",
                "vendor_id": "0x10EE",
                "class_code": "0x020000",
            },
            "registers": [],
            "power_management": False,
            "error_handling": False,
        }

    def test_device_specific_ports_with_string_values(self, renderer, base_context):
        """Test device_specific_ports template with string device_type."""
        result = renderer.render_template(
            "sv/device_specific_ports.sv.j2", base_context
        )

        # Should render network-specific ports
        assert "Network controller ports" in result or "link_up" in result
        assert (
            base_context["device_config"]["device_type"] in result.lower()
            or "network" in result.lower()
        )

    def test_main_module_with_string_values(self, renderer, base_context):
        """Test main_module template with string device_type and device_class."""
        result = renderer.render_template("sv/main_module.sv.j2", base_context)

        # Should include device type and class in module name
        assert "pcileech_advanced_network_enterprise" in result
        assert 'DEVICE_TYPE = "network"' in result
        assert 'DEVICE_CLASS = "enterprise"' in result

    def test_main_module_with_optional_performance_counters(
        self, renderer, base_context
    ):
        """Test main_module template handles missing performance_counters."""
        # Don't include performance_counters in context
        result = renderer.render_template("sv/main_module.sv.j2", base_context)

        # Should use default counter width
        assert "COUNTER_WIDTH = 32" in result

    def test_main_module_with_performance_counters(self, renderer, base_context):
        """Test main_module template with performance_counters defined."""
        base_context["performance_counters"] = {"counter_width": 64}
        result = renderer.render_template("sv/main_module.sv.j2", base_context)

        # Should use specified counter width
        assert "COUNTER_WIDTH = 64" in result

    def test_register_declarations_with_string_values(self, renderer, base_context):
        """Test register_declarations template with string values."""
        result = renderer.render_template(
            "sv/register_declarations.sv.j2", base_context
        )

        # Should render without errors
        assert result is not None
        assert len(result) > 0

    def test_template_with_dict_value_keys(self, renderer):
        """Test templates handle dictionaries with nested value keys."""
        context = {
            "header": "// Test header",
            "device_config": {
                "device_type": {"value": "storage", "name": "storage"},
                "device_class": {"value": "industrial", "name": "industrial"},
                "max_payload_size": 512,
                "msi_vectors": 8,
                "device_id": "0x5678",
                "vendor_id": "0x10EE",
                "class_code": "0x010000",
            },
            "registers": [],
        }

        result = renderer.render_template("sv/device_specific_ports.sv.j2", context)

        # Should extract value from dictionary
        assert "Storage-specific ports" in result or "storage" in result.lower()

    def test_error_recovery_template_with_various_formats(self, renderer):
        """Test error_recovery template handles different error type formats."""
        context = {
            "header": "// Test header",
            "config": {
                "max_retry_count": 3,
            },
            "recoverable_errors": [
                "ERROR_TIMEOUT",  # String
                {"value": "ERROR_CRC", "name": "CRC Error"},  # Dict
            ],
            "fatal_errors": [
                "ERROR_FATAL",
                {"value": "ERROR_SYSTEM", "name": "System Error"},
            ],
            "error_types": [],
            "error_thresholds": {},  # Add empty error_thresholds
        }

        # Template should handle both string and dict formats
        result = renderer.render_template("sv/error_recovery.sv.j2", context)
        assert "ERROR_TIMEOUT" in result
        assert "ERROR_CRC" in result

    def test_clock_gating_template_with_state_handling(self, renderer):
        """Test clock_gating template handles state objects correctly."""
        context = {
            "header": "// Test header",
            "config": {
                "supported_states": [
                    "D0",  # String
                    {"value": "D1", "name": "D1_STATE"},  # Dict
                    {"value": "D3_HOT", "name": "D3_HOT_STATE"},
                ]
            },
        }

        result = renderer.render_template("sv/clock_gating.sv.j2", context)
        # Should handle all state formats
        assert result is not None

    def test_register_logic_with_value_handling(self, renderer):
        """Test register_logic template handles register values correctly."""
        context = {
            "header": "// Test header",
            "registers": [
                {"name": "control_reg", "value": 0x1234},  # Direct value
                {
                    "name": "status_reg",
                    "value": {"value": 0x5678, "default": 0},
                },  # Dict with value
                {"name": "data_reg", "value": "0xABCD"},  # String value
            ],
            "variance_model": None,
        }

        result = renderer.render_template("sv/register_logic.sv.j2", context)
        # Should handle all value formats
        assert "control_reg" in result
        assert "status_reg" in result
        assert "data_reg" in result

    def test_advanced_controller_template(self, renderer, base_context):
        """Test advanced_controller template with complete context."""
        base_context.update(
            {
                "device_type": "network",
                "device_class": "enterprise",
                "perf_config": {"counter_width": 32},
                "power_config": None,
                "error_config": None,
            }
        )

        result = renderer.render_template("sv/advanced_controller.sv.j2", base_context)

        # Should render module with parameters
        assert "advanced_pcileech_controller" in result
        assert 'DEVICE_TYPE = "network"' in result
        assert 'DEVICE_CLASS = "enterprise"' in result

    def test_template_undefined_variable_handling(self, renderer, base_context):
        """Test that templates handle undefined variables gracefully."""
        # Remove optional fields to test undefined handling
        minimal_context = {
            "header": "// Test header",
            "device_config": base_context["device_config"],
            "registers": [],
        }

        # Should not raise errors for undefined optional variables
        result = renderer.render_template("sv/main_module.sv.j2", minimal_context)
        assert result is not None
        assert "pcileech_advanced" in result


class TestTemplateFilters:
    """Test custom template filters."""

    @pytest.fixture
    def renderer(self):
        """Create a template renderer instance."""
        return TemplateRenderer()

    def test_sv_hex_filter(self, renderer):
        """Test SystemVerilog hex formatting filter."""
        template_str = "{{ value | sv_hex(32) }}"
        template = renderer.env.from_string(template_str)
        result = template.render(value=0x1234)
        assert result == "32'h00001234"

    def test_sv_hex_filter_with_width(self, renderer):
        """Test SystemVerilog hex formatting with different widths."""
        template_str = "{{ value | sv_hex(16) }}"
        template = renderer.env.from_string(template_str)
        result = template.render(value=0xABCD)
        # The sv_hex filter produces uppercase hex
        assert result == "16'hABCD"

    def test_hex_filter(self, renderer):
        """Test basic hex formatting filter."""
        template_str = "{{ value | hex(8) }}"
        template = renderer.env.from_string(template_str)
        result = template.render(value=255)
        assert result == "000000ff"
