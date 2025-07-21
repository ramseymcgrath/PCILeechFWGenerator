#!/usr/bin/env python3
"""Unit tests for template renderer."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.templating.template_renderer import TemplateRenderer, TemplateRenderError


class TestTemplateRenderer:
    """Test cases for TemplateRenderer."""

    @pytest.fixture
    def temp_template_dir(self):
        """Create a temporary directory with test templates."""
        temp_dir = tempfile.mkdtemp()

        # Create test templates
        test_template = Path(temp_dir) / "test.j2"
        test_template.write_text("Hello {{ name }}!")

        tcl_template = Path(temp_dir) / "tcl_test.j2"
        tcl_template.write_text("set var {{ value | tcl_string_escape }}")

        sv_template = Path(temp_dir) / "sv_test.j2"
        sv_template.write_text("parameter {{ name | sv_param(value, 32) }}")

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def renderer(self, temp_template_dir):
        """Create a TemplateRenderer instance with test templates."""
        return TemplateRenderer(template_dir=temp_template_dir)

    def test_initialization_default_dir(self):
        """Test TemplateRenderer initialization with default directory."""
        renderer = TemplateRenderer()
        assert renderer.template_dir.exists()
        assert "templates" in str(renderer.template_dir)

    def test_initialization_custom_dir(self, temp_template_dir):
        """Test TemplateRenderer initialization with custom directory."""
        renderer = TemplateRenderer(template_dir=temp_template_dir)
        assert renderer.template_dir == Path(temp_template_dir)

    def test_render_template_basic(self, renderer):
        """Test basic template rendering."""
        result = renderer.render_template("test.j2", {"name": "World"})
        assert result == "Hello World!"

    def test_render_template_missing_variable(self, renderer):
        """Test rendering with missing variable."""
        with pytest.raises(TemplateRenderError) as exc_info:
            renderer.render_template("test.j2", {})
        assert "name" in str(exc_info.value)

    def test_render_template_nonexistent(self, renderer):
        """Test rendering nonexistent template."""
        with pytest.raises(TemplateRenderError) as exc_info:
            renderer.render_template("nonexistent.j2", {})
        assert "not found" in str(exc_info.value)

    def test_render_string_basic(self, renderer):
        """Test rendering template from string."""
        template_str = "Hello {{ name }}!"
        result = renderer.render_string(template_str, {"name": "World"})
        assert result == "Hello World!"

    def test_render_string_with_filters(self, renderer):
        """Test rendering string with custom filters."""
        template_str = "{{ value | sv_hex(16) }}"
        result = renderer.render_string(template_str, {"value": 255})
        assert "16'h00ff" in result or "16'h00FF" in result

    def test_template_exists(self, renderer):
        """Test checking if template exists."""
        assert renderer.template_exists("test.j2")
        assert not renderer.template_exists("nonexistent.j2")

    def test_list_templates(self, renderer):
        """Test listing templates."""
        templates = renderer.list_templates()
        assert "test.j2" in templates
        assert "tcl_test.j2" in templates
        assert "sv_test.j2" in templates

    def test_list_templates_with_pattern(self, renderer):
        """Test listing templates with pattern."""
        tcl_templates = renderer.list_templates("tcl_*.j2")
        assert "tcl_test.j2" in tcl_templates
        assert "test.j2" not in tcl_templates

    def test_get_template_path(self, renderer):
        """Test getting template path."""
        path = renderer.get_template_path("test.j2")
        assert path.exists()
        assert path.name == "test.j2"

    def test_tcl_string_escape_filter(self, renderer):
        """Test TCL string escape filter."""
        template_str = "{{ text | tcl_string_escape }}"
        result = renderer.render_string(template_str, {"text": 'test "quoted" string'})
        assert '\\"' in result

    def test_tcl_list_format_filter(self, renderer):
        """Test TCL list format filter."""
        template_str = "{{ items | tcl_list_format }}"
        result = renderer.render_string(template_str, {"items": ["a", "b", "c"]})
        assert result == "{a} {b} {c}"

    def test_sv_hex_filter(self, renderer):
        """Test SystemVerilog hex filter."""
        template_str = "{{ value | sv_hex(32) }}"
        result = renderer.render_string(template_str, {"value": 0xDEADBEEF})
        assert "32'h" in result
        assert "deadbeef" in result.lower()

    def test_sv_width_filter(self, renderer):
        """Test SystemVerilog width filter."""
        template_str = "{{ msb | sv_width(lsb) }}"
        result = renderer.render_string(template_str, {"msb": 31, "lsb": 0})
        assert result == "[31:0]"

    def test_sv_param_filter(self, renderer):
        """Test SystemVerilog parameter filter."""
        template_str = '{{ "TEST_PARAM" | sv_param(value, 16) }}'
        result = renderer.render_string(template_str, {"value": 100})
        assert "parameter TEST_PARAM = 16'h" in result

    def test_sv_signal_filter(self, renderer):
        """Test SystemVerilog signal filter."""
        template_str = '{{ "test_signal" | sv_signal(8, 0) }}'
        result = renderer.render_string(template_str, {})
        assert "logic [7:0] test_signal = 8'h00" in result

    def test_sv_identifier_filter(self, renderer):
        """Test SystemVerilog identifier filter."""
        template_str = "{{ name | sv_identifier }}"
        result = renderer.render_string(template_str, {"name": "test-signal-123"})
        assert result == "test_signal_123"

    def test_sv_comment_filter(self, renderer):
        """Test SystemVerilog comment filter."""
        template_str = "{{ text | sv_comment }}"
        result = renderer.render_string(template_str, {"text": "This is a comment"})
        assert result == "// This is a comment"

    def test_sv_comment_filter_block(self, renderer):
        """Test SystemVerilog block comment filter."""
        template_str = '{{ text | sv_comment("/*") }}'
        result = renderer.render_string(template_str, {"text": "Block comment"})
        assert result == "/* Block comment */"

    def test_log2_filter(self, renderer):
        """Test log2 filter."""
        template_str = "{{ value | log2 }}"
        result = renderer.render_string(template_str, {"value": 256})
        assert result == "8"

    def test_python_list_filter(self, renderer):
        """Test Python list filter."""
        template_str = "{{ items | python_list }}"
        result = renderer.render_string(template_str, {"items": [1, 2, 3]})
        assert result == "[1, 2, 3]"

    def test_validate_template_context_missing_required(self, renderer):
        """Test template context validation with missing required fields."""
        with pytest.raises(TemplateRenderError) as exc_info:
            renderer._validate_template_context(
                {"optional": "value"}, required_fields=["required_field"]
            )
        assert "required_field" in str(exc_info.value)

    def test_validate_template_context_all_present(self, renderer):
        """Test template context validation with all fields present."""
        # Should not raise
        renderer._validate_template_context(
            {"required": "value", "optional": "value2"},
            required_fields=["required"],
            optional_fields=["optional"],
        )

    def test_global_functions_available(self, renderer):
        """Test that global functions are available in templates."""
        template_str = "{{ hex(value) }}"
        result = renderer.render_string(template_str, {"value": 255})
        assert result == "0xff"

    def test_complex_template_rendering(self, renderer):
        """Test rendering a complex template with multiple features."""
        template_str = """
        module {{ module_name | sv_identifier }};
            {{ "CLK_PERIOD" | sv_param(period, 32) }}
            {% for signal in signals %}
            {{ signal.name | sv_signal(signal.width) }}
            {% endfor %}
            
            // {{ comment | sv_comment }}
            
            initial begin
                {% for value in test_values %}
                #{{ period }} test_signal = {{ value | sv_hex(8) }};
                {% endfor %}
            end
        endmodule
        """

        context = {
            "module_name": "test-module",
            "period": 10,
            "signals": [
                {"name": "test_signal", "width": 8},
                {"name": "control_signal", "width": 1},
            ],
            "comment": "Test module",
            "test_values": [0x00, 0xFF, 0xAA, 0x55],
        }

        result = renderer.render_string(template_str, context)

        assert "module test_module;" in result
        assert "parameter CLK_PERIOD = 32'h" in result
        assert "logic [7:0] test_signal" in result
        assert "logic [0:0] control_signal" in result
        assert "// Test module" in result
        assert "8'h00" in result
        assert "8'hff" in result.lower()


class TestTemplateRenderError:
    """Test TemplateRenderError exception."""

    def test_template_render_error(self):
        """Test TemplateRenderError creation."""
        error = TemplateRenderError("Test error message")
        assert str(error) == "Test error message"

    def test_template_render_error_inheritance(self):
        """Test that TemplateRenderError inherits from Exception."""
        error = TemplateRenderError("Test")
        assert isinstance(error, Exception)
