"""
Comprehensive tests for src/template_renderer.py - Template rendering system.

This module tests the Jinja2-based template rendering system including:
- Template loading and rendering
- Custom TCL filters
- Error handling for missing templates
- Template context variable substitution
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.templating.template_renderer import (
    TemplateRenderer,
    TemplateRenderError,
    render_tcl_template,
)


@pytest.fixture
def temp_template_dir():
    """Create a temporary directory with test templates."""
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)

        # Create TCL subdirectory
        tcl_dir = template_dir / "tcl"
        tcl_dir.mkdir()

        # Create test templates
        (tcl_dir / "test_template.j2").write_text(
            """
# Test Template for {{ board }}
# FPGA Part: {{ fpga_part }}
# Vendor ID: {{ vendor_id | hex(4) }}
# Device ID: {{ device_id | hex(4) }}
# Escaped string: {{ test_string | tcl_escape }}
# List format: {{ test_list | tcl_list }}
"""
        )

        (tcl_dir / "simple.j2").write_text("Hello {{ name }}!")

        (tcl_dir / "syntax_error.j2").write_text("{{ invalid syntax")

        yield template_dir


@pytest.fixture
def template_renderer(temp_template_dir):
    """Create a TemplateRenderer instance with test templates."""
    return TemplateRenderer(temp_template_dir)


class TestTemplateRendererInitialization:
    """Test TemplateRenderer initialization and setup."""

    def test_init_with_custom_directory(self, temp_template_dir):
        """Test initialization with custom template directory."""
        renderer = TemplateRenderer(temp_template_dir)

        assert renderer.template_dir == temp_template_dir
        assert renderer.env is not None
        assert renderer.env.loader is not None

    def test_init_with_default_directory(self):
        """Test initialization with default template directory."""
        with patch("pathlib.Path.mkdir"):
            renderer = TemplateRenderer()

            expected_dir = Path(__file__).parent.parent / "src" / "templates"
            assert str(renderer.template_dir).endswith("templates")

    def test_init_creates_directory_if_missing(self):
        """Test that initialization creates template directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_dir = Path(temp_dir) / "templates"

            renderer = TemplateRenderer(non_existent_dir)

            assert non_existent_dir.exists()
            assert renderer.template_dir == non_existent_dir

    def test_jinja_environment_configuration(self, template_renderer):
        """Test that Jinja2 environment is configured correctly."""
        env = template_renderer.env

        assert env.trim_blocks is True
        assert env.lstrip_blocks is True
        assert env.keep_trailing_newline is True


class TestCustomFilters:
    """Test custom Jinja2 filters for TCL generation."""

    def test_hex_filter_default_width(self, template_renderer):
        """Test hex filter with default width."""
        template_str = "{{ value | hex }}"
        result = template_renderer.render_string(template_str, {"value": 255})

        assert result == "00ff"

    def test_hex_filter_custom_width(self, template_renderer):
        """Test hex filter with custom width."""
        template_str = "{{ value | hex(8) }}"
        result = template_renderer.render_string(template_str, {"value": 255})

        assert result == "000000ff"

    def test_tcl_escape_filter(self, template_renderer):
        """Test TCL string escaping filter."""
        test_cases = [
            ("simple", "simple"),
            ('with"quotes', 'with\\"quotes'),
            ("with\\backslash", "with\\\\backslash"),
            ("with$variable", "with\\$variable"),
            ('complex"\\$string', 'complex\\"\\\\\\$string'),
        ]

        for input_str, expected in test_cases:
            template_str = "{{ value | tcl_escape }}"
            result = template_renderer.render_string(template_str, {"value": input_str})
            assert result == expected

    def test_tcl_list_filter(self, template_renderer):
        """Test TCL list formatting filter."""
        test_cases = [
            (["a", "b", "c"], '"a" "b" "c"'),
            (["item with spaces", "normal"], '"item with spaces" "normal"'),
            (['with"quotes', "with\\slash"], '"with\\"quotes" "with\\\\slash"'),
            ([], ""),
            ([123, 456], '"123" "456"'),
        ]

        for input_list, expected in test_cases:
            template_str = "{{ value | tcl_list }}"
            result = template_renderer.render_string(
                template_str, {"value": input_list}
            )
            assert result == expected

    def test_filters_in_template_file(self, template_renderer):
        """Test filters work correctly in template files."""
        context = {
            "board": "test_board",
            "fpga_part": "xc7a35t",
            "vendor_id": 0x1234,
            "device_id": 0x5678,
            "test_string": 'string with "quotes" and $vars',
            "test_list": ["file1.sv", "file2.sv", "file with spaces.sv"],
        }

        result = template_renderer.render_template("tcl/test_template.j2", context)

        assert "test_board" in result
        assert "xc7a35t" in result
        assert "1234" in result  # hex formatted vendor_id
        assert "5678" in result  # hex formatted device_id
        assert 'string with \\"quotes\\" and \\$vars' in result  # escaped string
        assert '"file1.sv" "file2.sv" "file with spaces.sv"' in result  # TCL list


class TestTemplateRendering:
    """Test template rendering functionality."""

    def test_render_template_success(self, template_renderer):
        """Test successful template rendering."""
        context = {"name": "World"}
        result = template_renderer.render_template("tcl/simple.j2", context)

        assert result == "Hello World!"

    def test_render_template_missing_file(self, template_renderer):
        """Test rendering non-existent template file."""
        with pytest.raises(TemplateRenderError) as exc_info:
            template_renderer.render_template("nonexistent.j2", {})

        assert "Failed to render template 'nonexistent.j2'" in str(exc_info.value)

    def test_render_template_syntax_error(self, template_renderer):
        """Test rendering template with syntax error."""
        with pytest.raises(TemplateRenderError) as exc_info:
            template_renderer.render_template("tcl/syntax_error.j2", {})

        assert "Failed to render template 'tcl/syntax_error.j2'" in str(exc_info.value)

    def test_render_string_success(self, template_renderer):
        """Test successful string template rendering."""
        template_str = "Hello {{ name }}!"
        context = {"name": "World"}

        result = template_renderer.render_string(template_str, context)

        assert result == "Hello World!"

    def test_render_string_syntax_error(self, template_renderer):
        """Test string template rendering with syntax error."""
        template_str = "{{ invalid syntax"

        with pytest.raises(TemplateRenderError) as exc_info:
            template_renderer.render_string(template_str, {})

        assert "Failed to render string template" in str(exc_info.value)

    def test_render_string_missing_variable(self, template_renderer):
        """Test string template rendering with missing variable."""
        template_str = "Hello {{ missing_var }}!"

        # Jinja2 renders undefined variables as empty strings by default
        result = template_renderer.render_string(template_str, {})
        assert result == "Hello !"

    def test_render_template_complex_context(self, template_renderer):
        """Test rendering with complex context variables."""
        context = {
            "board": "pcileech_35t",
            "fpga_part": "xc7a35tcsg324-2",
            "vendor_id": 0x8086,
            "device_id": 0x1533,
            "test_string": 'complex$string\\with"quotes',
            "test_list": ["src/file1.sv", "src/file2.sv"],
            "nested": {"value": "nested_value"},
        }

        result = template_renderer.render_template("tcl/test_template.j2", context)

        # Verify all context variables are properly rendered
        assert "pcileech_35t" in result
        assert "xc7a35tcsg324-2" in result
        assert "8086" in result
        assert "1533" in result
        assert 'complex\\$string\\\\with\\"quotes' in result
        assert '"src/file1.sv" "src/file2.sv"' in result


class TestTemplateUtilities:
    """Test template utility methods."""

    def test_template_exists_true(self, template_renderer):
        """Test template_exists returns True for existing template."""
        assert template_renderer.template_exists("tcl/simple.j2") is True

    def test_template_exists_false(self, template_renderer):
        """Test template_exists returns False for non-existent template."""
        assert template_renderer.template_exists("nonexistent.j2") is False

    def test_list_templates_default_pattern(self, template_renderer):
        """Test listing templates with default pattern."""
        templates = template_renderer.list_templates()

        assert "tcl/simple.j2" in templates
        assert "tcl/test_template.j2" in templates
        assert "tcl/syntax_error.j2" in templates
        assert len(templates) >= 3

    def test_list_templates_custom_pattern(self, template_renderer):
        """Test listing templates with custom pattern."""
        templates = template_renderer.list_templates("*simple*")

        assert "tcl/simple.j2" in templates
        assert "tcl/test_template.j2" not in templates

    def test_get_template_path(self, template_renderer):
        """Test getting template file path."""
        path = template_renderer.get_template_path("tcl/simple.j2")

        assert isinstance(path, Path)
        assert path.name == "simple.j2"
        assert path.parent.name == "tcl"
        assert path.exists()


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_jinja2_import_error(self):
        """Test handling of Jinja2 import error."""
        with patch(
            "template_renderer.Environment", side_effect=ImportError("Jinja2 not found")
        ):
            with pytest.raises(ImportError) as exc_info:
                TemplateRenderer()

            assert "Jinja2 is required for template rendering" in str(exc_info.value)

    def test_template_directory_permission_error(self):
        """Test handling of template directory permission errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file where we want to create a directory
            blocked_path = Path(temp_dir) / "blocked"
            blocked_path.write_text("blocking file")

            # This should handle the error gracefully
            with pytest.raises(Exception):
                TemplateRenderer(blocked_path)

    def test_render_with_none_context(self, template_renderer):
        """Test rendering with None context values."""
        context = {"name": None, "value": None}

        result = template_renderer.render_string(
            "Hello {{ name }}! Value: {{ value }}", context
        )
        assert result == "Hello None! Value: None"

    def test_render_with_empty_context(self, template_renderer):
        """Test rendering with empty context."""
        result = template_renderer.render_string(
            "Hello {{ name | default('World') }}!", {}
        )
        assert result == "Hello World!"


class TestConvenienceFunction:
    """Test the convenience function for quick template rendering."""

    def test_render_tcl_template_success(self, temp_template_dir):
        """Test successful rendering using convenience function."""
        context = {"name": "Test"}

        result = render_tcl_template("tcl/simple.j2", context, temp_template_dir)

        assert result == "Hello Test!"

    def test_render_tcl_template_default_dir(self):
        """Test convenience function with default template directory."""
        with patch("template_renderer.TemplateRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_template.return_value = "rendered content"
            mock_renderer_class.return_value = mock_renderer

            result = render_tcl_template("test.j2", {"key": "value"})

            assert result == "rendered content"
            mock_renderer_class.assert_called_once_with(None)
            mock_renderer.render_template.assert_called_once_with(
                "test.j2", {"key": "value"}
            )


class TestTemplateRenderErrorException:
    """Test the TemplateRenderError exception class."""

    def test_template_render_error_creation(self):
        """Test creating TemplateRenderError exception."""
        error_msg = "Test error message"
        error = TemplateRenderError(error_msg)

        assert str(error) == error_msg
        assert isinstance(error, Exception)

    def test_template_render_error_with_cause(self):
        """Test TemplateRenderError with underlying cause."""
        original_error = ValueError("Original error")

        try:
            raise TemplateRenderError("Template error") from original_error
        except TemplateRenderError as e:
            assert str(e) == "Template error"
            assert e.__cause__ == original_error


class TestIntegrationScenarios:
    """Test integration scenarios and real-world usage patterns."""

    def test_tcl_project_setup_template(self, temp_template_dir):
        """Test rendering a realistic TCL project setup template."""
        # Create a realistic project setup template
        project_template = temp_template_dir / "tcl" / "project_setup.j2"
        project_template.write_text(
            """
# Project Setup TCL - Generated for {{ board }}
create_project {{ project_name }} ./vivado_project -part {{ fpga_part }} -force
set_property target_language Verilog [current_project]
set_property default_lib xil_defaultlib [current_project]

# Device configuration
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]

# PCI configuration
set vendor_id {{ vendor_id | hex(4) }}
set device_id {{ device_id | hex(4) }}
set revision_id {{ revision_id | hex(2) }}

puts "Project setup completed for {{ board }}"
puts "FPGA Part: {{ fpga_part }}"
puts "Device: $vendor_id:$device_id (rev $revision_id)"
"""
        )

        renderer = TemplateRenderer(temp_template_dir)
        context = {
            "board": "pcileech_35t325_x4",
            "project_name": "pcileech_firmware",
            "fpga_part": "xc7a35tcsg324-2",
            "vendor_id": 0x1234,
            "device_id": 0x5678,
            "revision_id": 0x01,
        }

        result = renderer.render_template("tcl/project_setup.j2", context)

        # Verify the rendered content
        assert "pcileech_35t325_x4" in result
        assert "pcileech_firmware" in result
        assert "xc7a35tcsg324-2" in result
        assert "1234" in result
        assert "5678" in result
        assert "01" in result
        assert "create_project" in result
        assert "set_property" in result

    def test_multiple_template_rendering(self, temp_template_dir):
        """Test rendering multiple templates with shared context."""
        # Create multiple templates
        (temp_template_dir / "tcl" / "template1.j2").write_text(
            "Template 1: {{ shared_var }}"
        )
        (temp_template_dir / "tcl" / "template2.j2").write_text(
            "Template 2: {{ shared_var }}"
        )

        renderer = TemplateRenderer(temp_template_dir)
        context = {"shared_var": "shared_value"}

        result1 = renderer.render_template("tcl/template1.j2", context)
        result2 = renderer.render_template("tcl/template2.j2", context)

        assert "Template 1: shared_value" == result1
        assert "Template 2: shared_value" == result2

    def test_template_with_conditional_logic(self, temp_template_dir):
        """Test template with conditional logic and loops."""
        conditional_template = temp_template_dir / "tcl" / "conditional.j2"
        conditional_template.write_text(
            """
{% if supports_msix %}
# MSI-X is supported
set msix_enabled 1
{% else %}
# MSI-X not supported, using MSI
set msix_enabled 0
{% endif %}

# Source files
{% for file in source_files %}
add_files {{ file }}
{% endfor %}

# Constraint files
{% if constraint_files %}
{% for file in constraint_files %}
add_files -fileset constrs_1 {{ file }}
{% endfor %}
{% else %}
puts "No constraint files specified"
{% endif %}
"""
        )

        renderer = TemplateRenderer(temp_template_dir)
        context = {
            "supports_msix": True,
            "source_files": ["src/file1.sv", "src/file2.sv"],
            "constraint_files": ["constraints/timing.xdc"],
        }

        result = renderer.render_template("tcl/conditional.j2", context)

        assert "set msix_enabled 1" in result
        assert "add_files src/file1.sv" in result
        assert "add_files src/file2.sv" in result
        assert "add_files -fileset constrs_1 constraints/timing.xdc" in result
        assert "No constraint files specified" not in result
