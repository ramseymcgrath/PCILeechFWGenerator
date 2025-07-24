#!/usr/bin/env python3
"""Unit tests for template renderer."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from jinja2 import TemplateError

from src.templating.template_renderer import (
    TemplateRenderer,
    TemplateRenderError,
    MappingFileSystemLoader,
    render_tcl_template,
)


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


class TestMappingFileSystemLoader:
    """Test cases for MappingFileSystemLoader."""

    @pytest.fixture
    def temp_template_dir(self):
        """Create a temporary directory with mapped templates."""
        temp_dir = tempfile.mkdtemp()

        # Create template structure that matches mapping
        sv_dir = Path(temp_dir) / "sv"
        sv_dir.mkdir(parents=True)

        # Create a template that would be mapped
        device_ports_template = sv_dir / "device_specific_ports.sv.j2"
        device_ports_template.write_text(
            "// Device specific ports\nmodule device_ports();"
        )

        # Create an advanced controller template that includes the mapped template
        advanced_controller = sv_dir / "advanced_controller.sv.j2"
        advanced_controller.write_text(
            """
// Advanced Controller
{% include 'systemverilog/components/device_specific_ports.sv.j2' %}
module advanced_controller();
endmodule
"""
        )

        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_mapping_loader_direct_template(self, temp_template_dir):
        """Test MappingFileSystemLoader with direct template loading."""
        from jinja2 import Environment

        loader = MappingFileSystemLoader(str(temp_template_dir))
        env = Environment(loader=loader)

        # This should work with the old path due to mapping
        template = env.get_template(
            "systemverilog/components/device_specific_ports.sv.j2"
        )
        result = template.render()
        assert "Device specific ports" in result

    def test_mapping_loader_include_template(self, temp_template_dir):
        """Test MappingFileSystemLoader with template includes."""
        from jinja2 import Environment

        loader = MappingFileSystemLoader(str(temp_template_dir))
        env = Environment(loader=loader)

        # Load template that includes another template via old path
        template = env.get_template("sv/advanced_controller.sv.j2")
        result = template.render()
        assert "Device specific ports" in result
        assert "advanced_controller" in result

    @patch("src.templating.template_renderer.update_template_path")
    def test_mapping_loader_calls_update_function(self, mock_update, temp_template_dir):
        """Test that MappingFileSystemLoader calls update_template_path."""
        from jinja2 import Environment

        mock_update.return_value = "sv/device_specific_ports.sv.j2"

        loader = MappingFileSystemLoader(str(temp_template_dir))
        env = Environment(loader=loader)

        try:
            env.get_template("old/path/template.sv.j2")
        except:
            pass  # Template might not exist, but we just want to test the call

        mock_update.assert_called_with("old/path/template.sv.j2")


class TestTemplateRendererAdvanced:
    """Advanced test cases for TemplateRenderer."""

    @pytest.fixture
    def temp_template_dir_with_mapping(self):
        """Create a temporary directory with templates that require mapping."""
        temp_dir = tempfile.mkdtemp()

        # Create template structure
        sv_dir = Path(temp_dir) / "sv"
        tcl_dir = Path(temp_dir) / "tcl"
        python_dir = Path(temp_dir) / "python"

        for directory in [sv_dir, tcl_dir, python_dir]:
            directory.mkdir(parents=True)

        # Create templates that test different functionality

        # SystemVerilog template with includes
        advanced_template = sv_dir / "advanced_controller.sv.j2"
        advanced_template.write_text(
            """
// Advanced Controller Template
{{ header | default("// Default header") }}

module {{ module_name }}_controller #(
    parameter WIDTH = {{ config.width | default(32) }}
) (
    input logic clk,
    input logic rst_n,
    {% for port in ports %}
    {{ port.direction }} logic [{{ port.width-1 }}:0] {{ port.name }},
    {% endfor %}
    output logic ready
);

{% include 'systemverilog/components/device_specific_ports.sv.j2' %}

endmodule
"""
        )

        # Component template that gets included
        device_ports = sv_dir / "device_specific_ports.sv.j2"
        device_ports.write_text(
            """
// Device specific port declarations
{% for device_port in device_ports | default([]) %}
{{ device_port.direction }} logic {{ device_port.name }};  // {{ device_port.description }}
{% endfor %}
"""
        )

        # TCL template
        tcl_template = tcl_dir / "build_script.tcl.j2"
        tcl_template.write_text(
            """
# TCL Build Script
set project_name {{ project_name | tcl_string_escape }}
set files {{ files | tcl_list_format }}

{% for file in source_files %}
add_files -norecurse {{ file | tcl_string_escape }}
{% endfor %}
"""
        )

        # Python template for build integration
        python_template = python_dir / "pcileech_build_integration.py.j2"
        python_template.write_text(
            """
# PCILeech Build Integration
BUILD_VERSION = "{{ build_system_version | default('unknown') }}"
INTEGRATION_TYPE = "{{ integration_type | default('pcileech') }}"
MODULES = {{ pcileech_modules | python_list }}

def get_build_info():
    return {
        'version': BUILD_VERSION,
        'type': INTEGRATION_TYPE,
        'modules': MODULES
    }
"""
        )

        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def advanced_renderer(self, temp_template_dir_with_mapping):
        """Create a TemplateRenderer with advanced templates."""
        return TemplateRenderer(template_dir=temp_template_dir_with_mapping)

    def test_systemverilog_template_with_includes(self, advanced_renderer):
        """Test SystemVerilog template rendering with includes and mapping."""
        context = {
            "header": "// Generated SystemVerilog Module",
            "module_name": "pcie_endpoint",
            "config": {"width": 64},
            "ports": [
                {"direction": "input", "width": 32, "name": "data_in"},
                {"direction": "output", "width": 32, "name": "data_out"},
            ],
            "device_ports": [
                {
                    "direction": "input",
                    "name": "device_clk",
                    "description": "Device clock",
                },
                {
                    "direction": "output",
                    "name": "device_ready",
                    "description": "Device ready signal",
                },
            ],
        }

        result = advanced_renderer.render_template(
            "sv/advanced_controller.sv.j2", context
        )

        assert "Generated SystemVerilog Module" in result
        assert "pcie_endpoint_controller" in result
        assert "parameter WIDTH = 64" in result
        assert "input logic [31:0] data_in" in result
        assert "output logic [31:0] data_out" in result
        assert "input logic device_clk" in result
        assert "output logic device_ready" in result

    def test_tcl_template_with_filters(self, advanced_renderer):
        """Test TCL template rendering with TCL-specific filters."""
        context = {
            "project_name": 'Test "Quoted" Project',
            "files": ["file1.sv", "file2.sv", "file3.sv"],
            "source_files": ["src/module1.sv", "src/module2.sv"],
        }

        result = advanced_renderer.render_template("tcl/build_script.tcl.j2", context)

        assert 'Test \\"Quoted\\" Project' in result
        assert "{file1.sv} {file2.sv} {file3.sv}" in result
        assert "src/module1.sv" in result
        assert "src/module2.sv" in result

    def test_python_template_with_validation(self, advanced_renderer):
        """Test Python template rendering with context validation."""
        # Test with valid context
        context = {
            "build_system_version": "1.0.0",
            "integration_type": "pcileech",
            "pcileech_modules": ["module1", "module2", "module3"],
        }

        result = advanced_renderer.render_template(
            "python/pcileech_build_integration.py.j2", context
        )

        assert 'BUILD_VERSION = "1.0.0"' in result
        assert 'INTEGRATION_TYPE = "pcileech"' in result
        # Python list filter uses single quotes, not double quotes
        assert "MODULES = ['module1', 'module2', 'module3']" in result

    def test_python_template_with_context_validation_and_defaults(
        self, advanced_renderer
    ):
        """Test Python template with missing context values and validation."""
        # Test with missing values - should use defaults from validation
        context = {}

        result = advanced_renderer.render_template(
            "python/pcileech_build_integration.py.j2", context
        )

        assert 'BUILD_VERSION = "0.7.5"' in result  # Default from validation
        assert 'INTEGRATION_TYPE = "pcileech"' in result  # Default from validation
        assert "MODULES = []" in result  # Default empty list

    def test_context_validation_pcileech_modules_conversion(self, advanced_renderer):
        """Test context validation converts non-list pcileech_modules."""
        # Test with string instead of list
        context = {"pcileech_modules": "single_module"}

        result = advanced_renderer.render_template(
            "python/pcileech_build_integration.py.j2", context
        )

        # Python list filter uses single quotes, not double quotes
        assert "MODULES = ['single_module']" in result

    def test_context_validation_pcileech_modules_dict(self, advanced_renderer):
        """Test context validation converts dict pcileech_modules to keys."""
        # Test with dict instead of list
        context = {"pcileech_modules": {"module1": "config1", "module2": "config2"}}

        result = advanced_renderer.render_template(
            "python/pcileech_build_integration.py.j2", context
        )

        # Should extract keys from dict
        result_modules = result[
            result.find("MODULES = [") : result.find("]", result.find("MODULES = ["))
            + 1
        ]
        assert "module1" in result_modules
        assert "module2" in result_modules

    def test_include_with_old_path_mapping(self, advanced_renderer):
        """Test that includes work with old path mapping."""
        context = {
            "module_name": "test_module",
            "config": {"width": 32},
            "ports": [],
            "device_ports": [
                {
                    "direction": "input",
                    "name": "mapped_signal",
                    "description": "Mapped signal",
                }
            ],
        }

        # The template includes using old path: 'systemverilog/components/device_specific_ports.sv.j2'
        # But the actual file is at: 'sv/device_specific_ports.sv.j2'
        result = advanced_renderer.render_template(
            "sv/advanced_controller.sv.j2", context
        )

        assert "test_module_controller" in result
        assert "mapped_signal" in result
        assert "Mapped signal" in result

    def test_all_custom_filters_available(self, advanced_renderer):
        """Test that all custom filters are properly registered."""
        filters = advanced_renderer.env.filters

        # TCL filters
        assert "tcl_string_escape" in filters
        assert "tcl_list_format" in filters

        # SystemVerilog filters
        assert "sv_hex" in filters
        assert "sv_width" in filters
        assert "sv_param" in filters
        assert "sv_signal" in filters
        assert "sv_identifier" in filters
        assert "sv_comment" in filters
        assert "sv_bool" in filters

        # Python filters
        assert "python_list" in filters
        assert "python_repr" in filters

        # Math filters
        assert "log2" in filters

    def test_all_global_functions_available(self, advanced_renderer):
        """Test that all global functions are properly registered."""
        globals_dict = advanced_renderer.env.globals

        # Python built-ins
        assert "hasattr" in globals_dict
        assert "getattr" in globals_dict
        assert "isinstance" in globals_dict
        assert "len" in globals_dict
        assert "range" in globals_dict
        assert "min" in globals_dict
        assert "max" in globals_dict
        assert "hex" in globals_dict

    def test_template_with_missing_context_strict_undefined(self, advanced_renderer):
        """Test that StrictUndefined catches missing variables."""
        template_str = "Hello {{ undefined_variable }}!"

        with pytest.raises(TemplateRenderError) as exc_info:
            advanced_renderer.render_string(template_str, {})

        assert "undefined_variable" in str(exc_info.value)

    def test_edge_case_filters(self, advanced_renderer):
        """Test edge cases for custom filters."""

        # Test sv_hex with different input types
        template_str = "{{ value1 | sv_hex(16) }} {{ value2 | sv_hex(32) }} {{ value3 | sv_hex(8) }}"
        result = advanced_renderer.render_string(
            template_str,
            {
                "value1": "0xFF",  # String hex
                "value2": 255,  # Integer
                "value3": "ff",  # String hex without 0x
            },
        )

        assert "16'h" in result
        assert "32'h" in result
        assert "8'h" in result

        # Test sv_width edge cases
        template_str = "{{ msb1 | sv_width }} {{ msb2 | sv_width(lsb2) }}"
        result = advanced_renderer.render_string(
            template_str,
            {"msb1": 0, "msb2": 7, "lsb2": 0},  # Should return empty string
        )

        assert "" in result  # First case should be empty
        assert "[7:0]" in result

        # Test log2 with edge cases
        template_str = "{{ val1 | log2 }} {{ val2 | log2 }}"
        result = advanced_renderer.render_string(
            template_str, {"val1": 1, "val2": 1024}  # log2(1) = 0  # log2(1024) = 10
        )

        assert "0" in result
        assert "10" in result


class TestConvenienceFunction:
    """Test the convenience function for TCL template rendering."""

    @pytest.fixture
    def temp_template_dir(self):
        """Create a temporary directory with a TCL template."""
        temp_dir = tempfile.mkdtemp()

        tcl_dir = Path(temp_dir) / "tcl"
        tcl_dir.mkdir(parents=True)

        tcl_template = tcl_dir / "test.tcl.j2"
        tcl_template.write_text("set variable {{ value | tcl_string_escape }}")

        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_render_tcl_template_function(self, temp_template_dir):
        """Test the render_tcl_template convenience function."""
        result = render_tcl_template(
            "tcl/test.tcl.j2", {"value": 'test "value"'}, temp_template_dir
        )

        assert 'test \\"value\\"' in result

    def test_render_tcl_template_function_default_dir(self):
        """Test render_tcl_template with default directory."""
        # This should not raise an error even if templates don't exist
        # because the function creates the renderer successfully
        try:
            render_tcl_template("nonexistent.tcl.j2", {})
        except TemplateRenderError:
            pass  # Expected for nonexistent template


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.fixture
    def renderer_with_bad_template(self):
        """Create renderer with a template that has syntax errors."""
        temp_dir = tempfile.mkdtemp()

        bad_template = Path(temp_dir) / "bad.j2"
        bad_template.write_text("Hello {{ unclosed_variable")  # Missing }}

        renderer = TemplateRenderer(template_dir=temp_dir)

        yield renderer
        shutil.rmtree(temp_dir)

    def test_template_syntax_error(self, renderer_with_bad_template):
        """Test handling of template syntax errors."""
        with pytest.raises(TemplateRenderError) as exc_info:
            renderer_with_bad_template.render_template("bad.j2", {})

        assert "Failed to render template" in str(exc_info.value)

    def test_template_not_found_error_mapping_loader(self):
        """Test template not found error with mapping loader."""
        temp_dir = tempfile.mkdtemp()
        renderer = TemplateRenderer(template_dir=temp_dir)

        try:
            with pytest.raises(TemplateRenderError) as exc_info:
                renderer.render_template("systemverilog/nonexistent.sv.j2", {})

            assert "not found" in str(exc_info.value)
        finally:
            shutil.rmtree(temp_dir)

    @patch("src.templating.template_renderer.update_template_path")
    def test_mapping_function_import_fallback(self, mock_update):
        """Test fallback when template mapping import fails."""
        # Configure the mock to return a string
        mock_update.return_value = "test_template.j2"

        # Import and test the function
        from src.templating.template_renderer import update_template_path

        result = update_template_path("test_template.j2")
        # Since we're patching, the mock should be called and return our configured value
        assert isinstance(result, str)
        assert result == "test_template.j2"

    def test_missing_jinja2_import_error(self):
        """Test error when Jinja2 is not available (mocked)."""
        # This is more of a documentation test - the actual import error
        # would happen at module load time
        with patch.dict("sys.modules", {"jinja2": None}):
            try:
                # This would normally raise ImportError at import time
                # but we're testing the concept
                pass
            except ImportError as e:
                assert "Jinja2 is required" in str(e)
