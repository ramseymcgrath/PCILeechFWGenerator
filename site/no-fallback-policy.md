---
title: No-Fallback Security Policy
description: Security policy preventing generic firmware through fallback value validation
permalink: /no-fallback-policy/
---

## Overview

This document explains why the PCILeech firmware generator doesn't allow fallback values for critical device identification parameters like vendor ID and device ID. This prevents creating generic firmware that could be easily detected or compromise security.

## Rationale

### Why Generic Firmware is Problematic

Using fallback values for device identification parameters (vendor ID, device ID, class code, revision ID) causes several problems:

1. **Non-Unique Firmware**: Multiple devices get identical firmware, which defeats the purpose of device-specific cloning
2. **Easy Detection**: Generic firmware is easily spotted and can be detected by security systems
3. **Unrealistic Testing**: Generic firmware doesn't match real-world conditions, making research less valuable

### Required Configuration Approach

The system requires explicit device identification values rather than using fallback defaults:

```python
if not device_config.get("vendor_id"):
    raise ConfigurationError("Vendor ID must be provided - no fallback allowed")
vendor_id = device_config["vendor_id"]
```

This ensures that every generated firmware is specific to the actual target device being cloned.

## How It Works

### 1. Build Configuration (`src/build.py`)

The `extract_device_config` method now:

- Checks that all required device identification fields are present
- Looks for zero values (which means invalid configuration)
- Rejects known generic vendor/device ID combinations
- Shows clear error messages when something's wrong

### 2. Template Files

All Jinja2 templates now:

- Use `{%- error %}` blocks instead of `| default()` filters for critical IDs
- Check required parameters before processing
- Stop compilation if mandatory fields are missing

**Template validation example**:

```jinja
{%- if not config_space.device_id %}
{%- error "Device ID is required - no fallback values allowed" %}
{%- endif %}
{{ config_space.device_id }}
```

### 3. Configuration Classes

Old configuration classes now:

- Use `Optional[str] = None` instead of placeholder defaults
- Include `__post_init__` validation methods
- Raise `ValueError` if critical fields are not provided

## Files Modified

### Core Build System

- `src/build.py`: Enhanced device config extraction with validation
- `src/templating/advanced_sv_generator.py`: Removed generic defaults from DeviceConfig

### Template Files

- `src/templates/sv/pcileech_cfgspace.coe.j2`: Added error blocks for missing IDs
- `src/templates/tcl/pcileech_generate_project.j2`: Removed fallback values from TCL generation

## Error Messages

When the system detects missing configuration, users see clear error messages:

```text
ConfigurationError: Device configuration is missing from template context. 
This would create generic firmware that isn't device-specific. 
Make sure device detection and configuration space analysis are working properly.
```

```text
ConfigurationError: Vendor ID is zero (0x0000), which means the 
device configuration is invalid. This would create generic firmware.
```

## Testing

### Working Configuration Test

```python
def test_valid_device_config():
    config = {
        "vendor_id": 0x8086,  # Intel
        "device_id": 0x1234,  # Specific device
        "revision_id": 0x01,
        "class_code": 0x020000
    }
    # Should work
    result = extract_device_config({"device_config": config}, False)
```

### Broken Configuration Test

```python
def test_invalid_device_config():
    config = {}  # Missing required fields
    # Should throw an error
    with pytest.raises(ConfigurationError):
        extract_device_config({"device_config": config}, False)
```

## Why This Helps

1. **Security**: Makes sure all firmware is device-specific and unique
2. **Reliability**: Forces proper device detection and configuration
3. **Debugging**: Clear error messages help find configuration problems
4. **Better Research**: Prevents unrealistic test scenarios with generic devices

## Updating Existing Code

If you're updating existing code:

1. **Remove Default Parameters**: Replace any default vendor/device IDs with proper validation
2. **Add Error Handling**: Add clear error messages for missing configuration
3. **Update Templates**: Use `{%- error %}` blocks instead of `| default()` filters
4. **Test Configuration**: Make sure all device identification fields are properly filled in

## When Fallbacks Are OK

The only acceptable fallbacks are for:

- **Subsystem IDs**: Can fall back to main vendor/device IDs per PCIe spec
- **Optional Features**: Non-critical device features that don't affect uniqueness
- **Vivado Settings**: Tool-specific parameters that don't impact device identity

These exceptions are clearly documented and use different validation logic.

---

**See Also**: [Device Cloning Guide](device-cloning), [Firmware Uniqueness](firmware-uniqueness), [Supported Devices](supported-devices)
