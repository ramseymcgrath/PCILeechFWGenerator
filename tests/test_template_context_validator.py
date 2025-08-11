"""
Tests for the Template Context Validator

This module tests the functionality that ensures all template variables
are properly defined with appropriate defaults.
"""

import pytest
from pathlib import Path
from typing import Dict, Any
import tempfile
import os

from src.templating.template_context_validator import (
    TemplateContextValidator,
    TemplateVariableRequirements,
    validate_template_context,
    get_template_requirements,
    analyze_template_variables,
)


class TestTemplateContextValidator:
    """Test suite for the TemplateContextValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TemplateContextValidator()

    def test_get_template_requirements_sv_template(self):
        """Test getting requirements for SystemVerilog templates."""
        requirements = self.validator.get_template_requirements(
            "sv/pcileech_fifo.sv.j2"
        )

        # Check that required variables are identified
        assert "device_config" in requirements.required_vars
        assert "board_config" in requirements.required_vars

        # Check that optional variables are identified
        assert "supports_msix" in requirements.optional_vars
        assert "enable_clock_crossing" in requirements.optional_vars

        # Check that defaults are provided
        assert requirements.default_values["supports_msix"] is False
        assert requirements.default_values["device_signature"] == "32'hDEADBEEF"

    def test_get_template_requirements_tcl_template(self):
        """Test getting requirements for TCL templates."""
        requirements = self.validator.get_template_requirements("tcl/constraints.j2")

        # Check required variables
        assert "board" in requirements.required_vars
        assert "device" in requirements.required_vars

        # Check optional variables
        assert "supports_msix" in requirements.optional_vars
        assert "generated_xdc_path" in requirements.optional_vars

        # Check defaults
        assert requirements.default_values["top_module"] == "pcileech_top"
        assert requirements.default_values["max_lanes"] == 1

    def test_validate_and_complete_context_adds_defaults(self):
        """Test that validation adds default values for missing variables."""
        template_name = "sv/msix_table.sv.j2"
        context = {
            "NUM_MSIX": 32,  # Provide required variable
        }

        validated = self.validator.validate_and_complete_context(
            template_name, context, strict=False
        )

        # Check that defaults were added
        assert validated["NUM_MSIX"] == 32  # Original value preserved
        assert validated["RESET_CLEAR"] is True  # Default added
        assert validated["USE_BYTE_ENABLES"] is True  # Default added
        assert validated["WRITE_PBA_ALLOWED"] is False  # Default added
        assert validated["INIT_TABLE"] is False  # Default added

    def test_validate_and_complete_context_strict_mode(self):
        """Test that strict mode raises error for missing required variables."""
        template_name = "sv/pcileech_fifo.sv.j2"
        context = {}  # Missing required variables

        with pytest.raises(ValueError) as exc_info:
            self.validator.validate_and_complete_context(
                template_name, context, strict=True
            )

        assert "missing required variables" in str(exc_info.value).lower()
        assert "device_config" in str(exc_info.value)

    def test_pattern_matching(self):
        """Test that template pattern matching works correctly."""
        # Test wildcard matching
        assert self.validator._matches_pattern("sv/test.sv.j2", "sv/*.sv.j2")
        assert self.validator._matches_pattern(
            "sv/power_management.sv.j2", "sv/power_*.sv.j2"
        )
        assert self.validator._matches_pattern("sv/msix_table.sv.j2", "sv/msix_*.sv.j2")

        # Test non-matching patterns
        assert not self.validator._matches_pattern("tcl/test.j2", "sv/*.sv.j2")
        assert not self.validator._matches_pattern("sv/test.sv.j2", "tcl/*.j2")

    def test_analyze_template_for_variables(self):
        """Test analyzing a template file for variable references."""
        # Create a temporary template file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".j2", delete=False) as f:
            f.write(
                """
            {% if supports_msix %}
            module msix_handler #(
                parameter NUM_VECTORS = {{ NUM_MSIX }}
            );
            {% endif %}
            
            {% for reg in registers %}
            assign {{ reg.name }} = {{ reg.value }};
            {% endfor %}
            
            {% if device_config.vendor_id is defined %}
            localparam VENDOR_ID = {{ device_config.vendor_id }};
            {% endif %}
            """
            )
            temp_path = Path(f.name)

        try:
            variables = self.validator.analyze_template_for_variables(temp_path)

            # Check that all variables were found
            assert "supports_msix" in variables
            assert "NUM_MSIX" in variables
            assert "registers" in variables
            assert "device_config" in variables

        finally:
            # Clean up
            os.unlink(temp_path)

    def test_generate_context_documentation(self):
        """Test generating documentation for template context."""
        doc = self.validator.generate_context_documentation("sv/msix_table.sv.j2")

        # Check that documentation includes required sections
        assert "Template: sv/msix_table.sv.j2" in doc
        assert "Required Variables:" in doc or "Optional Variables:" in doc
        assert "Default Values:" in doc

        # Check that specific variables are documented
        assert "NUM_MSIX" in doc
        assert "RESET_CLEAR" in doc

    def test_template_cache(self):
        """Test that template requirements are cached."""
        template_name = "sv/test.sv.j2"

        # First call should create and cache requirements
        req1 = self.validator.get_template_requirements(template_name)

        # Second call should return cached requirements
        req2 = self.validator.get_template_requirements(template_name)

        # Should be the same object
        assert req1 is req2

    def test_power_management_template_defaults(self):
        """Test that power management templates get correct defaults."""
        template_name = "sv/power_management.sv.j2"
        context = {}

        validated = self.validator.validate_and_complete_context(
            template_name, context, strict=False
        )

        # Check power-specific defaults
        assert validated["enable_wake_events"] is False
        assert validated["enable_pme"] is False

    def test_performance_counter_template_defaults(self):
        """Test that performance counter templates get correct defaults."""
        template_name = "sv/performance_counters.sv.j2"
        context = {}

        validated = self.validator.validate_and_complete_context(
            template_name, context, strict=False
        )

        # Check performance-specific defaults
        assert validated["enable_transaction_counters"] is False
        assert validated["enable_bandwidth_monitoring"] is False
        assert validated["enable_error_rate_tracking"] is False
        assert validated["error_signals_available"] is False

    def test_option_rom_template_defaults(self):
        """Test that option ROM templates get correct defaults."""
        template_name = "sv/option_rom_spi_flash.sv.j2"
        context = {}

        validated = self.validator.validate_and_complete_context(
            template_name, context, strict=False
        )

        # Check option ROM-specific defaults
        assert validated["USE_QSPI"] is False
        assert validated["ENABLE_CACHE"] is False
        assert validated["SPI_FAST_CMD"] == "0Bh"
        assert validated["FLASH_ADDR_OFFSET"] == "24'h000000"

    def test_global_functions(self):
        """Test the global helper functions."""
        # Test validate_template_context
        context = {"NUM_MSIX": 16}
        validated = validate_template_context("sv/msix_table.sv.j2", context)
        assert validated["RESET_CLEAR"] is True

        # Test get_template_requirements
        requirements = get_template_requirements("sv/pcileech_fifo.sv.j2")
        assert "device_config" in requirements.required_vars

    def test_context_preservation(self):
        """Test that existing context values are preserved."""
        template_name = "sv/msix_table.sv.j2"
        context = {
            "NUM_MSIX": 64,
            "RESET_CLEAR": False,  # Override default
            "custom_field": "custom_value",  # Extra field
        }

        validated = self.validator.validate_and_complete_context(
            template_name, context, strict=False
        )

        # Original values should be preserved
        assert validated["NUM_MSIX"] == 64
        assert validated["RESET_CLEAR"] is False
        assert validated["custom_field"] == "custom_value"

        # Defaults should still be added for missing fields
        assert validated["USE_BYTE_ENABLES"] is True

    def test_nested_template_patterns(self):
        """Test that multiple patterns can apply to the same template."""
        template_name = "sv/msix_implementation.sv.j2"
        context = {}

        validated = self.validator.validate_and_complete_context(
            template_name, context, strict=False
        )

        # Should get defaults from both sv/*.sv.j2 and sv/msix_*.sv.j2
        assert "device_config" in validated  # From sv/*.sv.j2
        assert "NUM_MSIX" in validated  # From sv/msix_*.sv.j2
        assert validated["supports_msix"] is False  # From sv/*.sv.j2
        assert validated["RESET_CLEAR"] is True  # From sv/msix_*.sv.j2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
