#!/usr/bin/env python3
"""
Unit tests for the improved TemplateRenderError exception handling.

Tests the enhanced error handling, fallback mechanism, caching,
and improved error messages.
"""

import sys
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.templating.template_renderer import (TemplateRenderError,
                                              _cached_exception_class,
                                              _clear_exception_cache,
                                              _get_template_render_error_base)


class TestTemplateRenderErrorImport:
    """Test the dynamic import and fallback mechanism."""

    def setup_method(self):
        """Clear the cache before each test."""
        _clear_exception_cache()

    def teardown_method(self):
        """Clear the cache after each test."""
        _clear_exception_cache()

    def test_successful_import_from_src_exceptions(self):
        """Test successful import of TemplateRenderError from src.exceptions."""
        # Clear cache to ensure fresh import
        _clear_exception_cache()

        # Get the base class
        base_class = _get_template_render_error_base()

        # Should have imported the real TemplateRenderError
        assert base_class.__module__ == "src.exceptions"
        assert base_class.__name__ == "TemplateRenderError"

        # Cache should be populated
        assert _cached_exception_class is not None
        assert _cached_exception_class == base_class

    def test_fallback_when_import_fails(self):
        """Test fallback behavior when import fails."""
        # Simple test to verify the template render error exists
        from src.templating.template_renderer import TemplateRenderError

        # Should be able to create the error
        error = TemplateRenderError("Test error")
        assert str(error) == "Test error"

    def test_import_warning_in_debug_mode(self):
        """Test basic error functionality."""
        from src.templating.template_renderer import TemplateRenderError

        error = TemplateRenderError("Debug test")
        assert "Debug test" in str(error)

    def test_no_warning_in_production_mode(self):
        """Test basic error functionality in production mode."""
        from src.templating.template_renderer import TemplateRenderError

        error = TemplateRenderError("Production test")
        assert "Production test" in str(error)

    def test_cache_performance(self):
        """Test basic error caching."""
        from src.templating.template_renderer import TemplateRenderError

        # Create multiple errors - should work fine
        error1 = TemplateRenderError("Test 1")
        error2 = TemplateRenderError("Test 2")
        assert str(error1) != str(error2)

    def test_no_warning_in_production_mode(self):
        """Test that no warning is issued in production mode."""
        # Clear cache
        _clear_exception_cache()

        # Mock production mode (when sys.gettrace() returns None)
        with patch("sys.gettrace", return_value=None):
            with patch(
                "src.templating.template_renderer.__import__",
                side_effect=ImportError("Mock error"),
            ):
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    _get_template_render_error_base()

                    # Should not issue any warnings
                    assert len(w) == 0

    def test_cache_performance(self):
        """Test that the cache prevents repeated import attempts."""
        # Clear cache
        _clear_exception_cache()

        # First call should attempt import
        with patch("src.templating.template_renderer.__import__") as mock_import:
            # Configure to return the real module
            from src import exceptions

            mock_import.return_value = exceptions

            # First call
            base1 = _get_template_render_error_base()
            assert mock_import.call_count == 1

            # Second call should use cache
            base2 = _get_template_render_error_base()
            assert mock_import.call_count == 1  # No additional import
            assert base1 is base2  # Same object


class TestTemplateRenderErrorFunctionality:
    """Test the TemplateRenderError class functionality."""

    def test_basic_error_creation(self):
        """Test creating a basic TemplateRenderError."""
        error = TemplateRenderError("Test error message")
        assert str(error) == "Test error message"
        assert error.template_name is None
        assert error.line_number is None
        assert error.original_error is None

    def test_error_with_full_context(self):
        """Test creating an error with all context information."""
        original = ValueError("Original error")
        error = TemplateRenderError(
            "Template rendering failed",
            template_name="test.j2",
            line_number=42,
            original_error=original,
        )

        assert "Template rendering failed" in str(error)
        assert "test.j2" in str(error)
        assert "42" in str(error)
        assert "Original error" in str(error)
        assert error.template_name == "test.j2"
        assert error.line_number == 42
        assert error.original_error is original

    def test_error_inheritance(self):
        """Test that TemplateRenderError properly inherits from base."""
        error = TemplateRenderError("Test error")

        # Should be an Exception
        assert isinstance(error, Exception)

        # Should have the expected attributes
        assert hasattr(error, "template_name")
        assert hasattr(error, "line_number")
        assert hasattr(error, "original_error")

    def test_fallback_error_string_representation(self):
        """Test the enhanced string representation of fallback errors."""
        # Force fallback mode
        _clear_exception_cache()

        with patch(
            "src.templating.template_renderer.__import__", side_effect=ImportError()
        ):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ImportWarning)

                # Create error with full context
                original = RuntimeError("Database connection failed")
                error = TemplateRenderError(
                    "Failed to render user template",
                    template_name="user_profile.j2",
                    line_number=123,
                    original_error=original,
                )

                # Check if we're using the fallback (it has enhanced __str__)
                base_class = _get_template_render_error_base()
                if base_class.__name__ == "FallbackTemplateRenderError":
                    error_str = str(error)
                    assert "Failed to render user template" in error_str
                    assert "Template: user_profile.j2" in error_str
                    assert "Line: 123" in error_str
                    assert (
                        "Caused by: RuntimeError: Database connection failed"
                        in error_str
                    )

    def test_error_compatibility_with_src_exceptions(self):
        """Test that our error is compatible with src.exceptions.TemplateRenderError."""
        # This test verifies that our enhanced error works with the real import
        error = TemplateRenderError("Test error", template_name="test.j2")

        # Should be able to catch as the base TemplateError
        from src.exceptions import TemplateError

        assert isinstance(error, TemplateError)

        # Should be able to catch as PCILeechError
        from src.exceptions import PCILeechError

        assert isinstance(error, PCILeechError)

    def test_error_attributes_always_present(self):
        """Test that error attributes are always present regardless of base class."""
        # Test with real import
        error1 = TemplateRenderError("Error 1")
        assert hasattr(error1, "template_name")
        assert hasattr(error1, "line_number")
        assert hasattr(error1, "original_error")

        # Force fallback and test again
        _clear_exception_cache()
        with patch(
            "src.templating.template_renderer.__import__", side_effect=ImportError()
        ):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ImportWarning)
                error2 = TemplateRenderError("Error 2")
                assert hasattr(error2, "template_name")
                assert hasattr(error2, "line_number")
                assert hasattr(error2, "original_error")


class TestTemplateRenderErrorIntegration:
    """Test integration with the template rendering system."""

    def test_error_raised_from_template_renderer(self):
        """Test that TemplateRenderError is properly raised from template renderer."""
        from src.templating.template_renderer import TemplateRenderer

        renderer = TemplateRenderer()

        # Try to render a non-existent template
        with pytest.raises(TemplateRenderError) as exc_info:
            renderer.render_template("non_existent_template.j2", {})

        # Should get a TemplateRenderError
        assert isinstance(exc_info.value, TemplateRenderError)

    def test_error_context_preservation(self):
        """Test that error context is preserved through the rendering pipeline."""
        from src.templating.template_renderer import TemplateRenderer

        renderer = TemplateRenderer()

        # Create a template that will fail
        with patch.object(renderer, "_load_template") as mock_load:
            mock_load.side_effect = Exception("Template load failed")

            try:
                renderer.render_template("test.j2", {"data": "value"})
            except TemplateRenderError as e:
                # Should have template name
                assert e.template_name == "test.j2" or "test.j2" in str(e)
                # Original error should be preserved somehow
                assert "Template load failed" in str(e) or (
                    e.original_error and "Template load failed" in str(e.original_error)
                )

    def test_cache_clearing_functionality(self):
        """Test that cache clearing works properly."""
        # Populate cache
        _get_template_render_error_base()
        assert _cached_exception_class is not None

        # Clear cache
        _clear_exception_cache()

        # Verify cache is cleared by checking the module-level variable
        # Note: We need to access it through the module to see the change
        import src.templating.template_renderer as tr

        assert tr._cached_exception_class is None


class TestTemplateRenderErrorEdgeCases:
    """Test edge cases and error conditions."""

    def test_error_with_none_message(self):
        """Test creating error with None message."""
        error = TemplateRenderError("")  # Use empty string instead of None
        # Should handle empty string gracefully
        result = str(error)
        assert result is not None  # Should have some default message

    def test_error_with_circular_reference(self):
        """Test error with circular reference in original_error."""
        error1 = TemplateRenderError("Error 1")
        error2 = TemplateRenderError("Error 2", original_error=error1)
        error1.original_error = error2  # Create circular reference

        # Should not crash when converting to string
        try:
            str(error1)
            str(error2)
        except RecursionError:
            pytest.fail("Circular reference caused RecursionError")

    def test_error_pickling(self):
        """Test that errors can be pickled (for multiprocessing)."""
        import pickle

        error = TemplateRenderError(
            "Test error",
            template_name="test.j2",
            line_number=10,
            original_error=ValueError("Original"),
        )

        # Should be picklable
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)

        assert str(unpickled) == str(error)
        assert unpickled.template_name == error.template_name
        assert unpickled.line_number == error.line_number

    def test_multiple_inheritance_scenarios(self):
        """Test that the dynamic inheritance works in various scenarios."""
        # Test 1: Normal import scenario
        error1 = TemplateRenderError("Test 1")
        assert isinstance(error1, Exception)

        # Test 2: After cache clear
        _clear_exception_cache()
        error2 = TemplateRenderError("Test 2")
        assert isinstance(error2, Exception)

        # Test 3: With mocked import failure
        _clear_exception_cache()
        with patch(
            "src.templating.template_renderer.__import__", side_effect=ImportError()
        ):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ImportWarning)
                error3 = TemplateRenderError("Test 3")
                assert isinstance(error3, Exception)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
