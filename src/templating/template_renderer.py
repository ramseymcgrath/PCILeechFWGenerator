#!/usr/bin/env python3
"""
Jinja2-based template rendering system for PCILeech firmware generation.

This module provides a centralized template rendering system to replace
the string formatting and concatenation currently used in build.py.
"""

import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from __version__ import __version__
from string_utils import (generate_tcl_header_comment, log_debug_safe,
                          log_error_safe, log_info_safe, log_warning_safe,
                          safe_format)
from templates.template_mapping import update_template_path

try:
    from jinja2 import (BaseLoader, Environment, FileSystemLoader,
                        StrictUndefined, Template, TemplateError,
                        TemplateNotFound, TemplateRuntimeError, Undefined,
                        meta, nodes)
    from jinja2.bccache import FileSystemBytecodeCache
    from jinja2.ext import Extension
    from jinja2.sandbox import SandboxedEnvironment
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

    def __init__(
        self,
        template_dir: Optional[Union[str, Path]] = None,
        *,
        strict: bool = True,
        sandboxed: bool = False,
        bytecode_cache_dir: Optional[Union[str, Path]] = None,
        auto_reload: bool = True,
    ):
        """
        Initialize the template renderer.

        Args:
            template_dir: Directory containing template files. If None,
                         defaults to src/templates/
            strict: Use StrictUndefined to fail on missing variables
            sandboxed: Use sandboxed environment for untrusted templates
            bytecode_cache_dir: Directory for bytecode cache (speeds up repeated renders)
            auto_reload: Auto-reload templates when changed
        """
        template_dir = Path(template_dir or Path(__file__).parent.parent / "templates")
        template_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = template_dir

        # Choose undefined class based on strict mode
        undefined_cls = StrictUndefined if strict else Undefined

        # Choose environment class based on sandboxed mode
        env_cls = SandboxedEnvironment if sandboxed else Environment

        # Setup bytecode cache if directory provided
        bcc = (
            FileSystemBytecodeCache(str(bytecode_cache_dir))
            if bytecode_cache_dir
            else None
        )

        self.env = env_cls(
            loader=MappingFileSystemLoader(str(self.template_dir)),
            undefined=undefined_cls,
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
            auto_reload=auto_reload,
            extensions=[ErrorTagExtension, "jinja2.ext.do"],
            bytecode_cache=bcc,
            autoescape=False,  # Explicit: we're not doing HTML
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
            # Enhanced TCL string escaping including brackets and braces
            return (
                value.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("$", "\\$")
                .replace("[", "\\[")
                .replace("]", "\\]")
                .replace("{", "\\{")
                .replace("}", "\\}")
            )

        def tcl_list_format(items: list) -> str:
            """Format Python list as TCL list."""
            escaped_items = [tcl_string_escape(str(item)) for item in items]
            return " ".join(f"{{{item}}}" for item in escaped_items)

        # SystemVerilog-specific filters
        def _parse_int(value) -> int:
            """Parse integer from various formats."""
            if isinstance(value, int):
                return value
            s = str(value).strip()
            try:
                # hex forms
                if s.lower().startswith("0x"):
                    return int(s, 16)
                # choose base: hex if only hex chars, else decimal
                hexdigits = set("0123456789abcdefABCDEF")
                base = 16 if all(c in hexdigits for c in s) else 10
                return int(s, base)
            except Exception as e:
                raise TemplateRenderError(
                    f"sv_hex: cannot parse int from {value!r}: {e}"
                )

        def sv_hex(value, width: int = 32) -> str:
            """Return SystemVerilog literal. width<=0 returns just hex without width."""
            iv = _parse_int(value)
            if width and width > 0:
                hex_digits = (width + 3) // 4
                return f"{width}'h{iv:0{hex_digits}X}"
            return f"{iv:#X}"

        def sv_width(msb: int, lsb: int = 0) -> str:
            """Generate SystemVerilog bit width specification."""
            if msb == lsb:
                return ""
            if msb < lsb:
                msb, lsb = lsb, msb
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

        # SystemVerilog reserved keywords
        SV_KEYWORDS = {
            "assign",
            "module",
            "endmodule",
            "begin",
            "end",
            "logic",
            "wire",
            "reg",
            "input",
            "output",
            "inout",
            "parameter",
            "localparam",
            "always",
            "always_ff",
            "always_comb",
            "always_latch",
            "if",
            "else",
            "case",
            "endcase",
            "for",
            "while",
            "do",
            "function",
            "endfunction",
            "task",
            "endtask",
            "class",
            "endclass",
            "package",
            "endpackage",
            "interface",
            "endinterface",
            "typedef",
            "enum",
            "struct",
            "union",
            "initial",
            "final",
            "generate",
            "endgenerate",
        }

        def sv_identifier(name: str) -> str:
            """Convert to valid SystemVerilog identifier."""
            import re

            s = re.sub(r"[^a-zA-Z0-9_]", "_", name)
            if not re.match(r"^[a-zA-Z_]", s):
                s = "_" + s
            if s in SV_KEYWORDS:
                s = s + "_id"
            return s

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

        def clog2(v) -> int:
            """Calculate ceiling of log2 for SystemVerilog bit width calculations."""
            n = int(v)
            return 0 if n <= 1 else int(math.ceil(math.log2(n)))

        def flog2(v) -> int:
            """Calculate floor of log2."""
            n = max(1, int(v))
            return int(math.log2(n))

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
        self.env.filters["clog2"] = clog2
        self.env.filters["log2"] = clog2  # Default to ceiling for compatibility
        self.env.filters["flog2"] = flog2

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

        def throw_error(message):
            """Throw a template runtime error."""
            raise TemplateRuntimeError(message)

        self.env.globals.update(
            {
                "generate_tcl_header_comment": generate_tcl_header_comment,
                "throw_error": throw_error,
                # Python builtins
                "len": len,
                "range": range,
                "min": min,
                "max": max,
                "sorted": sorted,
                "zip": zip,
                "sum": sum,
                "int": int,
                "hex": hex,
                "hasattr": hasattr,
                "getattr": getattr,
                "isinstance": isinstance,
                # Version info
                "__version__": __version__,
            }
        )

    def _preflight_undeclared(
        self, template_name: str, context: Dict[str, Any]
    ) -> None:
        """
        Comprehensive validation of all variables referenced in a template.

        This method enforces that all variables used in a template are properly defined
        in the context before rendering begins. It strictly prevents template rendering
        with incomplete context data to maintain security and data integrity.

        Args:
            template_name: Name of the template to validate
            context: Template context to check against

        Raises:
            TemplateRenderError: If any variable used in the template is undefined
        """
        try:
            # Get template source and parse it
            src, file_path, _ = self.env.loader.get_source(self.env, template_name)
            ast = self.env.parse(src)

            # Collect all variables that are declared/available
            declared = set(context.keys()) | set(self.env.globals.keys())

            # Find all referenced variables in the template
            referenced_vars = meta.find_undeclared_variables(ast)

            # Detect variables that are assigned/defined inside the template
            # (e.g. via {% set var = ... %} or {% set var %}...{% endset %}) and
            # treat them as declared for the purposes of preflight validation.
            import re

            assigned_in_template = set()
            try:
                # Find simple set statements: {% set var = ... %}
                # Handle whitespace-control variants like '{% set', '{%- set', '{% set -%}', etc.
                for m in re.finditer(r"\{%-?\s*set\s+([A-Za-z_][A-Za-z0-9_]*)", src):
                    assigned_in_template.add(m.group(1))
            except Exception:
                assigned_in_template = set()

            # Consider template-assigned names as declared for preflight
            declared = declared | assigned_in_template

            # Check for missing variables
            missing = referenced_vars - declared

            if missing:
                # Prepare a clear, security-focused error message
                missing_sorted = sorted(missing)
                error_msg = (
                    f"SECURITY VIOLATION: Template '{template_name}' references undefined variables: "
                    f"{', '.join(missing_sorted)}.\n"
                    f"Template path: {file_path}\n"
                    f"To maintain template integrity and security, all variables must be explicitly defined."
                )

                log_error_safe(logger, error_msg, prefix="TEMPLATE_SECURITY")
                raise TemplateRenderError(error_msg)

            # ENHANCEMENT: Also check for None values in critical variables
            none_vars = [
                k for k in referenced_vars if k in context and context[k] is None
            ]
            if none_vars:
                error_msg = (
                    f"SECURITY VIOLATION: Template '{template_name}' contains None values for "
                    f"critical variables: {', '.join(sorted(none_vars))}.\n"
                    f"Template path: {file_path}\n"
                    f"Complete initialization of all template variables is required for secure rendering."
                )
                log_error_safe(logger, error_msg, prefix="TEMPLATE_SECURITY")
                raise TemplateRenderError(error_msg)

        except TemplateNotFound as e:
            error_msg = f"Template '{template_name}' not found: {e}"
            log_error_safe(logger, error_msg, prefix="TEMPLATE_SECURITY")
            raise TemplateRenderError(error_msg) from e
        except Exception as e:
            error_msg = (
                f"Error during preflight validation of template '{template_name}': {e}"
            )
            log_error_safe(logger, error_msg, prefix="TEMPLATE_SECURITY")
            raise TemplateRenderError(error_msg) from e

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
        template_name = update_template_path(template_name)
        try:
            # First perform internal validation
            validated = self._validate_template_context(context, template_name)

            # Then use comprehensive validation with preflight check
            self._preflight_undeclared(template_name, validated)

            # Apply external validator with strict validation
            try:
                from src.templating.template_context_validator import \
                    validate_template_context

                # Validate with strict mode (security first)
                validated = validate_template_context(
                    template_name, validated, strict=True
                )
            except ImportError:
                # If validator not available, proceed with basic validation
                pass

            # Finally render the template with validated context
            template = self.env.get_template(template_name)
            return template.render(**validated)

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
            # Reuse the same validation path for consistency
            validated = self._validate_template_context(context, "<inline>")
            template = self.env.from_string(template_string)
            return template.render(**validated)

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
            self.env.get_template(update_template_path(template_name))
            return True
        except TemplateNotFound:
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
        name = update_template_path(template_name)
        src, filename, _ = self.env.loader.get_source(self.env, name)
        return Path(filename)

    def render_to_file(
        self, template_name: str, context: Dict[str, Any], out_path: Union[str, Path]
    ) -> Path:
        """
        Render template to file atomically.

        Args:
            template_name: Name of the template file
            context: Template context variables
            out_path: Output file path

        Returns:
            Path to the written file
        """
        content = self.render_template(template_name, context)
        out_path = Path(out_path)
        tmp = out_path.with_suffix(out_path.suffix + ".tmp")
        tmp.write_text(content)
        tmp.replace(out_path)
        return out_path

    def render_many(self, pairs: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, str]:
        """
        Render multiple templates efficiently.

        Args:
            pairs: List of (template_name, context) tuples

        Returns:
            Dictionary mapping template names to rendered content
        """
        results = {}
        for template_name, context in pairs:
            results[template_name] = self.render_template(template_name, context)
        return results

    def _validate_template_context(
        self,
        context: Dict[str, Any],
        template_name: Optional[str] = None,
        required_fields: Optional[list] = None,
        optional_fields: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Validate template context with strict security-first approach.

        This method enforces complete context validation before allowing template rendering.
        It rejects any missing or undefined variables rather than providing defaults,
        ensuring the integrity of rendered templates.

        Args:
            context: Original template context
            template_name: Name of the template being rendered (required for better error messages)
            required_fields: List of required fields (will be enforced)
            optional_fields: List of optional fields (validated if present)

        Returns:
            Validated context with explicit type conversions where necessary

        Raises:
            TemplateRenderError: If any required field is missing or invalid
        """
        if not context:
            raise TemplateRenderError(
                f"Template context cannot be empty for template '{template_name or 'unknown'}'"
            )

        validated_context = context.copy()

        # SECURITY ENFORCEMENT: Check for required fields and fail immediately if any are missing
        if required_fields:
            missing_fields = []
            for field in required_fields:
                if field not in validated_context or validated_context[field] is None:
                    missing_fields.append(field)

            if missing_fields:
                error_msg = safe_format(
                    "SECURITY VIOLATION: Missing required fields: {fields}",
                    fields=", ".join(missing_fields),
                )
                if template_name:
                    error_msg = safe_format(
                        "Template '{template_name}' {error_msg}",
                        template_name=template_name,
                        error_msg=error_msg,
                    )
                log_error_safe(logger, error_msg, prefix="TEMPLATE_SECURITY")
                raise TemplateRenderError(error_msg)

        # Dedicated SystemVerilog template validation with strict requirements
        if template_name and template_name.endswith(".sv.j2"):
            # Automatically enforce critical device identification parameters
            critical_sv_params = ["device_config"]
            missing_critical = [
                p
                for p in critical_sv_params
                if p not in validated_context or validated_context[p] is None
            ]

            if missing_critical:
                error_msg = safe_format(
                    "SECURITY VIOLATION: SystemVerilog template missing critical parameters: {params}. "
                    "Template rendering aborted to prevent generation of insecure firmware.",
                    params=", ".join(missing_critical),
                )
                log_error_safe(logger, error_msg, prefix="TEMPLATE_SECURITY")
                raise TemplateRenderError(error_msg)

            # Verify timing_config is properly initialized
            timing_config = validated_context.get("timing_config")
            if timing_config:
                if hasattr(timing_config, "__dataclass_fields__"):
                    # Convert dataclass to dictionary for Jinja2 access
                    from dataclasses import asdict

                    validated_context["timing_config"] = asdict(timing_config)
            elif "timing_config" in validated_context:
                # Reject None timing_config if it was explicitly provided
                raise TemplateRenderError(
                    f"SECURITY VIOLATION: Template '{template_name}' has timing_config=None. "
                    "Explicit timing configuration is required for secure template rendering."
                )

        # SECURITY ENHANCEMENT: PCILeech-specific critical validation
        if template_name and "pcileech" in template_name.lower():
            # PCILeech templates require device_signature for security
            if (
                "device_signature" not in validated_context
                or not validated_context["device_signature"]
            ):
                raise TemplateRenderError(
                    f"SECURITY VIOLATION: PCILeech template '{template_name}' missing required device_signature. "
                    "Firmware generation aborted to prevent generic device creation."
                )

            # Validate pcileech_modules if present
            if "pcileech_modules" in validated_context:
                pcileech_modules = validated_context["pcileech_modules"]
                if not isinstance(pcileech_modules, list):
                    error_msg = safe_format(
                        "SECURITY VIOLATION: pcileech_modules must be a list, got {type_name}. "
                        "Template rendering aborted to maintain data integrity.",
                        type_name=type(pcileech_modules).__name__,
                    )
                    log_error_safe(logger, error_msg, prefix="TEMPLATE_SECURITY")
                    raise TemplateRenderError(error_msg)

        # Validate string fields are properly initialized
        string_fields = ["header", "title", "description", "comment"]
        for key in string_fields:
            if key in validated_context and validated_context[key] is None:
                error_msg = safe_format(
                    "SECURITY VIOLATION: Template context key '{key}' is None. "
                    "Explicit initialization required for all template variables.",
                    key=key,
                )
                log_error_safe(logger, error_msg, prefix="TEMPLATE_SECURITY")
                raise TemplateRenderError(error_msg)

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
