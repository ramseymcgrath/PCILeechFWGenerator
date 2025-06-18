#!/usr/bin/env python3
"""
Template Validation Tests

Tests for template rendering validation and error handling.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from templating.template_renderer import TemplateRenderer, TemplateRenderError

    TEMPLATE_SYSTEM_AVAILABLE = True
except ImportError as e:
    TEMPLATE_SYSTEM_AVAILABLE = False
    IMPORT_ERROR = str(e)


@pytest.mark.skipif(
    not TEMPLATE_SYSTEM_AVAILABLE,
    reason=f"Template system not available: {IMPORT_ERROR if not TEMPLATE_SYSTEM_AVAILABLE else ''}",
)
class TestTemplateValidation:
    """Test template validation and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = TemplateRenderer()

    def test_pcileech_build_integration_template_validation(self):
        """Test validation for PCILeech build integration template."""
        # Test with valid context
        valid_context = {
            "pcileech_modules": ["pcileech_fifo", "bar_controller"],
            "build_system_version": "2.0",
            "integration_type": "pcileech",
        }

        validated = self.renderer._validate_template_context(
            "python/pcileech_build_integration.py.j2", valid_context
        )

        assert validated["pcileech_modules"] == ["pcileech_fifo", "bar_controller"]
        assert validated["build_system_version"] == "2.0"
        assert validated["integration_type"] == "pcileech"

    def test_pcileech_modules_list_conversion(self):
        """Test conversion of non-list pcileech_modules to list."""
        # Test with string value
        context_with_string = {
            "pcileech_modules": "single_module",
        }

        validated = self.renderer._validate_template_context(
            "python/pcileech_build_integration.py.j2", context_with_string
        )

        assert validated["pcileech_modules"] == ["single_module"]

    def test_pcileech_modules_dict_conversion(self):
        """Test conversion of dict pcileech_modules to list."""
        # Test with dict value
        context_with_dict = {
            "pcileech_modules": {"module1": "config1", "module2": "config2"},
        }

        validated = self.renderer._validate_template_context(
            "python/pcileech_build_integration.py.j2", context_with_dict
        )

        assert set(validated["pcileech_modules"]) == {"module1", "module2"}

    def test_missing_required_keys_get_defaults(self):
        """Test that missing required keys get safe defaults."""
        minimal_context = {}

        validated = self.renderer._validate_template_context(
            "python/pcileech_build_integration.py.j2", minimal_context
        )

        assert validated["pcileech_modules"] == []
        assert validated["build_system_version"] == "2.0"
        assert validated["integration_type"] == "pcileech"

    def test_none_values_replaced_with_empty_string(self):
        """Test that None values are replaced with empty strings."""
        context_with_none = {
            "some_key": None,
            "another_key": "valid_value",
        }

        validated = self.renderer._validate_template_context(
            "some_template.j2", context_with_none
        )

        assert validated["some_key"] == ""
        assert validated["another_key"] == "valid_value"

    def test_python_list_filter(self):
        """Test the python_list filter for safe list rendering."""
        # Test with list
        result = self.renderer.env.filters["python_list"](["module1", "module2"])
        assert result == "['module1', 'module2']"

        # Test with string
        result = self.renderer.env.filters["python_list"]("single_module")
        assert result == "['single_module']"

        # Test with empty/invalid input
        result = self.renderer.env.filters["python_list"](None)
        assert result == "[]"

    def test_python_repr_filter(self):
        """Test the python_repr filter for safe value rendering."""
        # Test with string
        result = self.renderer.env.filters["python_repr"]("test_string")
        assert result == "'test_string'"

        # Test with number
        result = self.renderer.env.filters["python_repr"](42)
        assert result == "42"

        # Test with list
        result = self.renderer.env.filters["python_repr"](["a", "b"])
        assert result == "['a', 'b']"

    def test_template_rendering_with_malformed_context(self):
        """Test that template rendering handles malformed context gracefully."""
        # Create a simple test template
        test_template = "modules = {{ pcileech_modules | python_list }}"

        # Test with various malformed contexts
        malformed_contexts = [
            {"pcileech_modules": None},
            {"pcileech_modules": "single_string"},
            {"pcileech_modules": {"key": "value"}},
            {},  # Missing key entirely
        ]

        for context in malformed_contexts:
            try:
                result = self.renderer.render_string(test_template, context)
                # Should not raise an exception and should produce valid Python
                assert "modules = [" in result
                assert "]" in result
            except Exception as e:
                pytest.fail(f"Template rendering failed with context {context}: {e}")

    @patch("templating.template_renderer.logger")
    def test_validation_logging(self, mock_logger):
        """Test that validation issues are properly logged."""
        context_with_issues = {
            "pcileech_modules": "not_a_list",
            "some_none_value": None,
        }

        self.renderer._validate_template_context(
            "python/pcileech_build_integration.py.j2", context_with_issues
        )

        # Check that warnings were logged
        mock_logger.warning.assert_called()
        warning_calls = [call.args[0] for call in mock_logger.warning.call_args_list]

        assert any("pcileech_modules is not a list" in msg for msg in warning_calls)
        assert any(
            "is None, replacing with empty string" in msg for msg in warning_calls
        )


if __name__ == "__main__":
    pytest.main([__file__])
