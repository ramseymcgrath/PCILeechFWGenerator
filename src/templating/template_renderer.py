"""
Jinja2-based template rendering system for PCILeech firmware generation.

This module provides a centralized template rendering system to replace
the string formatting and concatenation currently used in build.py.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Handle both package and direct imports
try:
    from ..__version__ import __version__
except ImportError:
    # Fallback for direct imports
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from __version__ import __version__
    except ImportError:
        __version__ = "unknown"

# Import string utilities for safe logging
try:
    from ..string_utils import (
        log_debug_safe,
        log_error_safe,
        log_info_safe,
        log_warning_safe,
        safe_format,
        generate_tcl_header_comment,
    )
except ImportError:
    # Fallback for direct imports
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from string_utils import (
        log_debug_safe,
        log_error_safe,
        log_info_safe,
        log_warning_safe,
        safe_format,
        generate_tcl_header_comment,
    )

# Import template mapping for backward compatibility
try:
    from ..templates.template_mapping import update_template_path
except ImportError:
    # Fallback for direct imports
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from templates.template_mapping import update_template_path

try:
    from jinja2 import (
        BaseLoader,
        Environment,
        FileSystemLoader,
        StrictUndefined,
        Template,
        TemplateError,
        TemplateRuntimeError,
        nodes,
    )
    from jinja2.ext import Extension
except ImportError:
    raise ImportError(
        "Jinja2 is required for template rendering. Install with: pip install jinja2"
    )


class MappingFileSystemLoader(FileSystemLoader):
    """
    Custom Jinja2 loader that applies template path mapping for both direct
    template loading and includes/extends.
    """

    def get_source(self, environment, template):
        """Override get_source to apply template path mapping."""
        # Apply template mapping
        mapped_template = update_template_path(template)
        return super().get_source(environment, mapped_template)


logger = logging.getLogger(__name__)


class ErrorTagExtension(Extension):
    """Custom Jinja2 extension to handle {% error %} tags for template validation."""

    tags = {"error"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        # Parse the string expression after the tag
        args = [parser.parse_expression()]
        return nodes.CallBlock(
            self.call_method("_raise_error", args), [], [], []
        ).set_lineno(lineno)

    def _raise_error(self, message, caller=None):
        raise TemplateRuntimeError(message)


class TemplateRenderer:
    """
    Jinja2-based template renderer for TCL scripts and other text files.

    This class provides a clean interface for rendering templates with
    proper error handling and context management.
    """

    def __init__(self, template_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the template renderer.

        Args:
            template_dir: Directory containing template files. If None,
                         defaults to src/templates/
        """
        if template_dir is None:
            # Default to the templates directory
            template_dir = Path(__file__).parent.parent / "templates"

        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Jinja2 environment
        # Use default Undefined instead of StrictUndefined to allow checking for undefined variables
        # This allows templates to use 'is defined' checks properly
        self.env = Environment(
            loader=MappingFileSystemLoader(str(self.template_dir)),
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
            extensions=[ErrorTagExtension],
            # undefined=StrictUndefined,  # Removed to allow optional variables
        )

        # Add custom filters if needed
        self._setup_custom_filters()

        # Add global functions
        self._setup_global_functions()

        log_debug_safe(
            logger,
            "Template renderer initialized with directory: {template_dir}",
            prefix="TEMPLATE",
            template_dir=self.template_dir,
        )

    def _setup_custom_filters(self):
        """Setup custom Jinja2 filters for TCL and SystemVerilog generation."""

        def hex_format(value: int, width: int = 4) -> str:
            """Format integer as hex string with specified width."""
            return f"{value:0{width}x}"

        def tcl_string_escape(value: str) -> str:
            """Escape string for safe use in TCL."""
            # Basic TCL string escaping
            return value.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")

        def tcl_list_format(items: list) -> str:
            """Format Python list as TCL list."""
            escaped_items = [tcl_string_escape(str(item)) for item in items]
            return " ".join(f"{{{item}}}" for item in escaped_items)

        # SystemVerilog-specific filters
        def sv_hex(value, width: int = 32) -> str:
            """Format value as SystemVerilog hex literal with proper width."""
            if isinstance(value, str):
                # Handle hex strings like "0x1234"
                if value.startswith("0x") or value.startswith("0X"):
                    int_value = int(value, 16)
                else:
                    int_value = (
                        int(value, 16)
                        if all(c in "0123456789abcdefABCDEF" for c in value)
                        else int(value, 16)
                    )
            else:
                int_value = int(value)

            hex_digits = (width + 3) // 4  # Round up to nearest hex digit
            return f"{width}'h{int_value:0{hex_digits}X}"

        def sv_width(msb: int, lsb: int = 0) -> str:
            """Generate SystemVerilog bit width specification."""
            if msb == lsb:
                return ""
            return f"[{msb}:{lsb}]"

        def sv_param(name: str, value, width: Optional[int] = None) -> str:
            """Format SystemVerilog parameter declaration."""
            if width:
                return f"parameter {name} = {sv_hex(value, width)}"
            return f"parameter {name} = {value}"

        def sv_signal(name: str, width: Optional[int] = None, initial=None) -> str:
            """Format SystemVerilog signal declaration."""
            width_str = f"[{width-1}:0] " if width and width >= 1 else ""
            if initial is not None:
                if width:
                    init_str = f" = {sv_hex(initial, width)}"
                else:
                    init_str = f" = {initial}"
            else:
                init_str = ""
            return f"logic {width_str}{name}{init_str};"

        def sv_identifier(name: str) -> str:
            """Convert to valid SystemVerilog identifier."""
            import re

            # Replace invalid characters with underscores
            sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)

            # Ensure it starts with a letter or underscore
            if not re.match(r"^[a-zA-Z_]", sanitized):
                sanitized = "_" + sanitized

            return sanitized

        def sv_comment(text: str, style: str = "//") -> str:
            """Format SystemVerilog comment."""
            if style == "//":
                return f"// {text}"
            elif style == "/*":
                return f"/* {text} */"
            else:
                return f"// {text}"

        def sv_bool(value) -> str:
            """Convert Python boolean to SystemVerilog boolean."""
            if isinstance(value, bool):
                return "1" if value else "0"
            return str(value)

        def log2(value: int) -> int:
            """Calculate log2 (ceiling) of a value for SystemVerilog bit width calculations."""
            import math

            if value <= 0:
                return 0
            return int(math.ceil(math.log2(value)))

        def python_list(value) -> str:
            """Format value as Python list literal."""
            if isinstance(value, list):
                # Format as Python list with integers/numbers as-is
                formatted_items = []
                for item in value:
                    if isinstance(item, (int, float)):
                        formatted_items.append(str(item))
                    else:
                        formatted_items.append(repr(str(item)))
                return "[" + ", ".join(formatted_items) + "]"
            elif isinstance(value, (str, int, float)):
                return repr([value])
            else:
                return "[]"

        def python_repr(value) -> str:
            """Format value as Python representation."""
            return repr(value)

        def calc_log2(value) -> int:
            """Calculate log base 2 of a value."""
            import math

            return int(math.log2(max(1, int(value))))

        def dataclass_to_dict(value):
            """Convert dataclass objects to dictionaries for template access."""
            if hasattr(value, "__dataclass_fields__"):
                from dataclasses import asdict

                return asdict(value)
            return value

        # Register filters
        self.env.filters["hex"] = hex_format
        self.env.filters["tcl_string_escape"] = tcl_string_escape
        self.env.filters["tcl_list_format"] = tcl_list_format

        # Python code generation filters
        self.env.filters["python_list"] = python_list
        self.env.filters["python_repr"] = python_repr

        # Math filters
        self.env.filters["log2"] = calc_log2

        # Utility filters
        self.env.filters["dataclass_to_dict"] = dataclass_to_dict

        # SystemVerilog filters
        self.env.filters["sv_hex"] = sv_hex
        self.env.filters["sv_width"] = sv_width
        self.env.filters["sv_param"] = sv_param
        self.env.filters["sv_signal"] = sv_signal
        self.env.filters["sv_identifier"] = sv_identifier
        self.env.filters["sv_comment"] = sv_comment
        self.env.filters["sv_bool"] = sv_bool

    def _setup_global_functions(self):
        """Setup global functions available in templates."""
        # Add global functions to template environment
        self.env.globals["generate_tcl_header_comment"] = generate_tcl_header_comment

        # Add Python built-in functions that are commonly used in templates
        self.env.globals["hasattr"] = hasattr
        self.env.globals["getattr"] = getattr
        self.env.globals["isinstance"] = isinstance
        self.env.globals["len"] = len
        self.env.globals["range"] = range
        self.env.globals["min"] = min
        self.env.globals["max"] = max
        self.env.globals["hex"] = hex

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.

        Args:
            template_name: Name of the template file (with path mapping support)
            context: Dictionary of variables to pass to the template

        Returns:
            Rendered template as string

        Raises:
            TemplateRenderError: If template rendering fails
        """
        # Map old template paths to new structure
        template_name = update_template_path(template_name)
        try:
            # Validate and sanitize context before rendering
            validated_context = self._validate_template_context(context, template_name)

            template = self.env.get_template(template_name)
            rendered = template.render(**validated_context)
            log_debug_safe(
                logger,
                "Successfully rendered template: {template_name}",
                prefix="TEMPLATE",
                template_name=template_name,
            )
            return rendered

        except TemplateError as e:
            error_msg = safe_format(
                "Failed to render template '{template_name}': {error}",
                template_name=template_name,
                error=e,
            )
            log_error_safe(logger, error_msg, prefix="TEMPLATE")
            raise TemplateRenderError(error_msg) from e
        except Exception as e:
            error_msg = safe_format(
                "Unexpected error rendering template '{template_name}': {error}",
                template_name=template_name,
                error=e,
            )
            log_error_safe(logger, error_msg, prefix="TEMPLATE")
            raise TemplateRenderError(error_msg) from e

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template from a string with the given context.

        Args:
            template_string: Template content as string
            context: Dictionary of variables to pass to the template

        Returns:
            Rendered template content as string

        Raises:
            TemplateRenderError: If template rendering fails
        """
        try:
            template = self.env.from_string(template_string)
            rendered = template.render(**context)
            log_debug_safe(
                logger, "Successfully rendered string template", prefix="TEMPLATE"
            )
            return rendered

        except TemplateError as e:
            error_msg = safe_format(
                "Failed to render string template: {error}", error=e
            )
            log_error_safe(logger, error_msg, prefix="TEMPLATE")
            raise TemplateRenderError(error_msg) from e
        except Exception as e:
            error_msg = safe_format(
                "Unexpected error rendering string template: {error}", error=e
            )
            log_error_safe(logger, error_msg, prefix="TEMPLATE")
            raise TemplateRenderError(error_msg) from e

    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template file exists.

        Args:
            template_name: Name of the template file

        Returns:
            True if template exists, False otherwise
        """
        try:
            # Use the Jinja2 loader to check existence (applies mapping)
            self.env.get_template(template_name)
            return True
        except TemplateError:
            return False

    def list_templates(self, pattern: str = "*.j2") -> list[str]:
        """
        List available template files.

        Args:
            pattern: Glob pattern to match template files

        Returns:
            List of template file names
        """
        templates = []
        for template_path in self.template_dir.rglob(pattern):
            # Get relative path from template directory
            rel_path = template_path.relative_to(self.template_dir)
            templates.append(str(rel_path))

        return sorted(templates)

    def get_template_path(self, template_name: str) -> Path:
        """
        Get the full path to a template file.

        Args:
            template_name: Name of the template file

        Returns:
            Full path to the template file
        """
        return self.template_dir / template_name

    def _validate_template_context(
        self,
        context: Dict[str, Any],
        template_name: Optional[str] = None,
        required_fields: Optional[list] = None,
        optional_fields: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Validate and sanitize template context to prevent rendering errors.

        Args:
            context: Original template context
            template_name: Name of the template being rendered (optional)
            required_fields: List of required fields (optional)
            optional_fields: List of optional fields (optional)

        Returns:
            Validated and sanitized context

        Raises:
            TemplateRenderError: If context validation fails
        """
        validated_context = context.copy()

        # Check for required fields if specified
        if required_fields:
            missing_fields = []
            for field in required_fields:
                if field not in validated_context or validated_context[field] is None:
                    missing_fields.append(field)

            if missing_fields:
                error_msg = safe_format(
                    "Missing required fields: {fields}",
                    fields=", ".join(missing_fields),
                )
                if template_name:
                    error_msg = safe_format(
                        "Template '{template_name}' {error_msg}",
                        template_name=template_name,
                        error_msg=error_msg,
                    )
                raise TemplateRenderError(error_msg)

        # Special validation for PCILeech build integration template
        if template_name == "python/pcileech_build_integration.py.j2":
            # Ensure pcileech_modules is a proper list
            pcileech_modules = validated_context.get("pcileech_modules", [])
            if not isinstance(pcileech_modules, list):
                log_warning_safe(
                    logger,
                    "pcileech_modules is not a list: {module_type}, converting to list",
                    prefix="TEMPLATE",
                    module_type=type(pcileech_modules),
                )
                if isinstance(pcileech_modules, (str, dict)):
                    # Convert single string to list, or extract from dict
                    if isinstance(pcileech_modules, str):
                        validated_context["pcileech_modules"] = [pcileech_modules]
                    else:
                        # If it's a dict, try to extract a list from common keys
                        validated_context["pcileech_modules"] = (
                            list(pcileech_modules.keys()) if pcileech_modules else []
                        )
                else:
                    validated_context["pcileech_modules"] = []

            # Ensure all required context keys have safe defaults
            safe_defaults = {
                "build_system_version": __version__,  # Use dynamic version from package
                "integration_type": "pcileech",
                "pcileech_modules": [],
            }

            for key, default_value in safe_defaults.items():
                if key not in validated_context or validated_context[key] is None:
                    validated_context[key] = default_value
                    log_debug_safe(
                        logger,
                        "Set default value for {key}: {value}",
                        prefix="TEMPLATE",
                        key=key,
                        value=default_value,
                    )

        # Special validation for SystemVerilog templates that use timing_config
        if template_name and template_name.endswith(".sv.j2"):
            timing_config = validated_context.get("timing_config")
            if timing_config and hasattr(timing_config, "__dataclass_fields__"):
                # Convert dataclass to dictionary for Jinja2 access
                log_debug_safe(
                    logger,
                    "Converting timing_config dataclass to dictionary for template access",
                    prefix="TEMPLATE",
                )
                from dataclasses import asdict

                validated_context["timing_config"] = asdict(timing_config)
            elif timing_config is None:
                # Provide default timing config if missing
                log_warning_safe(
                    logger,
                    "timing_config is missing, providing default values",
                    prefix="TEMPLATE",
                )
                validated_context["timing_config"] = {
                    "read_latency": 4,
                    "write_latency": 2,
                    "burst_length": 16,
                    "inter_burst_gap": 8,
                    "timeout_cycles": 1024,
                    "clock_frequency_mhz": 100.0,
                    "timing_regularity": 0.8,
                }

        # General validation for all templates
        # Only replace None values with empty strings for basic string fields
        # Complex objects like configs should be left as None if that's their intended value
        string_fields = ["header", "title", "description", "comment"]
        for key, value in validated_context.items():
            if value is None and key in string_fields:
                log_warning_safe(
                    logger,
                    "Template context key '{key}' is None, replacing with empty string",
                    prefix="TEMPLATE",
                    key=key,
                )
                validated_context[key] = ""

        return validated_context


class TemplateRenderError(Exception):
    """Exception raised when template rendering fails."""

    pass


# Convenience function for quick template rendering
def render_tcl_template(
    template_name: str,
    context: Dict[str, Any],
    template_dir: Optional[Union[str, Path]] = None,
) -> str:
    """
    Convenience function to render a TCL template.

    Args:
        template_name: Name of the template file
        context: Template context variables
        template_dir: Template directory (optional)

    Returns:
        Rendered template content
    """
    renderer = TemplateRenderer(template_dir)
    return renderer.render_template(template_name, context)
