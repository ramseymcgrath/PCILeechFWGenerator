# PCILeech Firmware Templates

This directory contains Jinja2 templates for generating TCL scripts and other configuration files used in the PCILeech firmware build process.

## Directory Structure

```
src/templates/
├── README.md           # This file
└── tcl/               # TCL script templates
    ├── project_setup.j2    # Vivado project setup template
    └── synthesis.j2        # Synthesis configuration template
```

## Template System

The template system uses Jinja2 for rendering TCL scripts with device-specific and build-specific parameters. This replaces the previous string formatting approach with a more maintainable and flexible solution.

### Key Features

- **Jinja2 templating**: Full Jinja2 syntax support with conditionals, loops, and filters
- **Custom filters**: TCL-specific filters for hex formatting, string escaping, and list formatting
- **Error handling**: Comprehensive error handling with detailed error messages
- **Template validation**: Built-in template existence checking and listing

### Custom Filters

The template renderer provides several custom filters for TCL generation:

- `hex(width)`: Format integers as hex strings with specified width
- `tcl_escape`: Escape strings for safe use in TCL
- `tcl_list`: Format Python lists as TCL lists

### Usage Example

```python
from src.template_renderer import TemplateRenderer
from src.constants import BOARD_PARTS, DEFAULT_FPGA_PART

# Initialize renderer
renderer = TemplateRenderer()

# Prepare context
context = {
    'fpga_part': BOARD_PARTS.get('35t', DEFAULT_FPGA_PART),
    'vendor_id': 0x1234,
    'device_id': 0x5678,
    'class_code': 0x020000,
    'project_name': 'pcileech_firmware',
    'project_dir': './vivado_project',
    'output_dir': '.',
    'header_comment': '# Generated project setup script'
}

# Render template
tcl_content = renderer.render_template('tcl/project_setup.j2', context)
```

## Template Naming Convention

- Use `.j2` extension for Jinja2 templates
- Use descriptive names that match their purpose
- Group related templates in subdirectories (e.g., `tcl/` for TCL scripts)

## Adding New Templates

1. Create the template file in the appropriate subdirectory
2. Use Jinja2 syntax for variable substitution and logic
3. Document expected context variables in template comments
4. Test the template with the `TemplateRenderer` class

## Migration from String Formatting

When migrating from the old string formatting approach:

1. Extract the template content to a `.j2` file
2. Replace `{variable}` with `{{ variable }}`
3. Use Jinja2 conditionals instead of Python string concatenation
4. Update the calling code to use `TemplateRenderer`

## Template Context Variables

Common context variables used across templates:

- `fpga_part`: FPGA part number (from BOARD_PARTS mapping)
- `vendor_id`: PCI vendor ID
- `device_id`: PCI device ID
- `class_code`: PCI class code
- `revision_id`: PCI revision ID
- `project_name`: Vivado project name
- `project_dir`: Project directory path
- `output_dir`: Output directory path
- `header_comment`: Generated header comment for the script
- `synthesis_strategy`: Synthesis strategy name
- `implementation_strategy`: Implementation strategy name