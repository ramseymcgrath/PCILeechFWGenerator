"""
Templating module for PCILeech firmware generation.

This module contains all templating-related functionality including:
- Jinja2-based template rendering
- TCL script generation
- SystemVerilog code generation
"""

# Import with fallback for missing dependencies
try:
    from .template_renderer import (
        TemplateRenderer,
        TemplateRenderError,
        render_tcl_template,
    )
except ImportError:
    TemplateRenderer = None
    TemplateRenderError = None
    render_tcl_template = None

try:
    from .tcl_builder import BuildContext, TCLBuilder, TCLScriptBuilder, TCLScriptType
except ImportError:
    TCLBuilder = None
    TCLScriptBuilder = None
    TCLScriptType = None
    BuildContext = None

try:
    from .systemverilog_generator import AdvancedSVGenerator, DeviceSpecificLogic
except ImportError:
    SystemVerilogGenerator = None
    AdvancedSVGenerator = None
    DeviceSpecificLogic = None

__all__ = [
    # Template rendering
    "TemplateRenderer",
    "TemplateRenderError",
    "render_tcl_template",
    # TCL building
    "TCLBuilder",
    "TCLScriptBuilder",
    "TCLScriptType",
    "BuildContext",
    # SystemVerilog generation
    "SystemVerilogGenerator",
    "AdvancedSVGenerator",
    "DeviceSpecificLogic",
]
