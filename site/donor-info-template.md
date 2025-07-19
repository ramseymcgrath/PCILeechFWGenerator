---
layout: default
title: Donor Info Template
nav_order: 8
---

# Donor Info Template

The Donor Info Template feature allows you to generate comprehensive JSON templates for capturing detailed device information, behavioral profiles, and advanced configuration parameters. This enables more precise device cloning and optimization.

## Overview

The donor info template is a structured JSON file that captures:
- Device identification and capabilities
- Behavioral profiling data
- Timing characteristics
- Access patterns
- Interrupt and DMA configurations
- PCILeech-specific optimizations
- Manufacturing variance data

## Generating a Template

### Using the CLI

Generate a donor info template using the command line:

```bash
# Generate with default settings (pretty-printed JSON)
python3 pcileech.py donor-template

# Generate minimal template with only essential fields
python3 pcileech.py donor-template --blank -o minimal.json

# Generate compact JSON (no formatting)
python3 pcileech.py donor-template --compact

# Specify custom output path
python3 pcileech.py donor-template -o /path/to/my_device_template.json

# Pre-fill template with device information (requires sudo and valid device)
sudo python3 pcileech.py donor-template --bdf 0000:03:00.0 -o my_device.json

# Validate an existing donor info file
python3 pcileech.py donor-template --validate my_device.json
```

### Generating Template During Build

You can also generate a pre-filled donor info template as part of the build process:

```bash
# Build firmware and output a donor template with extracted device info
sudo python3 pcileech.py build --bdf 0000:03:00.0 --board 75t --output-template device_template.json
```

This is particularly useful because:
- The template is automatically populated with actual device values extracted during the build
- You get both the firmware and a template for future customization in one step
- The template includes all discovered device capabilities and configuration

### Using the TUI

In the TUI interface:
1. Navigate to the "Quick Actions" panel
2. Click "📝 Generate Donor Template"
3. The template will be saved as `donor_info_template.json` in the current directory

### Programmatic Usage

```python
from src.device_clone.donor_info_template import DonorInfoTemplateGenerator

# Generate full template dictionary
template = DonorInfoTemplateGenerator.generate_blank_template()

# Generate minimal template dictionary
minimal_template = DonorInfoTemplateGenerator.generate_minimal_template()

# Save to file
DonorInfoTemplateGenerator.save_template("my_template.json", pretty=True)
```

## Template Types

### Full Template
The default template includes comprehensive sections for:
- Complete device identification and capabilities
- Behavioral profiling and timing characteristics
- Access patterns and interrupt configurations
- DMA characteristics and performance profiles
- Advanced features (virtualization, security, error handling)
- PCILeech-specific optimizations
- Manufacturing variance data

Use the full template when you need:
- Detailed behavioral profiling
- Advanced performance tuning
- Complete device emulation
- Manufacturing variance simulation

### Minimal Template
The minimal template (generated with `--blank` flag) includes only essential fields:
- Basic device identification (vendor/device IDs, class code)
- Core PCIe capabilities (version, link width/speed)
- BAR configuration

Use the minimal template when you need:
- Quick device cloning without advanced features
- Simple device identification
- Basic functionality testing
- A starting point for custom configurations

## Template Structure

The template contains the following main sections:

### 1. Metadata

Contains information about when and how the template was generated:

```json
{
  "metadata": {
    "generated_at": "2025-01-19T12:30:45Z",
    "device_bdf": "",  // Fill in: e.g., "0000:03:00.0"
    "kernel_version": "",  // Fill in: e.g., "6.1.0-15-amd64"
    "generator_version": "enhanced-v2.0",
    "behavioral_data_included": true,
    "profile_capture_duration": null,  // Fill in: seconds
    "comments": ""  // Any additional notes
  }
}
```

### 2. Device Info

Comprehensive device identification and configuration:

```json
{
  "device_info": {
    "identification": {
      "vendor_id": null,  // e.g., 0x8086 for Intel
      "device_id": null,
      "subsystem_vendor_id": null,
      "subsystem_device_id": null,
      "class_code": null,  // e.g., 0x020000 for Ethernet
      "revision_id": null,
      "device_name": "",  // Human-readable name
      "manufacturer": ""
    },
    "capabilities": {
      "max_payload_size": null,  // 128, 256, 512, etc.
      "link_width": null,  // 1, 2, 4, 8, 16
      "link_speed": "",  // "2.5GT/s", "5GT/s", etc.
      "supports_msi": null,
      "msi_vectors": null,
      "supports_msix": null,
      "msix_vectors": null,
      // ... more capabilities
    },
    "bars": {
      "bar0": {
        "enabled": null,
        "size": null,
        "type": "",  // "memory" or "io"
        "prefetchable": null,
        "64bit": null,
        "purpose": ""  // Description of BAR usage
      },
      // ... bar1 through bar5 and expansion_rom
    }
  }
}
```

### 3. Behavioral Profile

Captures runtime behavior and performance characteristics:

```json
{
  "behavioral_profile": {
    "timing_characteristics": {
      "register_access_latency_us": {
        "min": null,
        "max": null,
        "average": null,
        "std_deviation": null
      },
      "interrupt_response_time_us": {
        "min": null,
        "max": null,
        "average": null
      },
      // ... more timing data
    },
    "access_patterns": {
      "frequent_registers": [
        {
          "offset": null,
          "name": "",
          "access_count": null,
          "read_write_ratio": null,
          "typical_values": []
        }
      ],
      // ... access sequences and patterns
    },
    "interrupt_patterns": {
      "interrupt_type": "",  // "msi", "msix", or "intx"
      "vector_count": null,
      "coalescing_enabled": null,
      // ... interrupt configuration
    },
    "dma_characteristics": {
      "supports_dma": null,
      "max_dma_size_bytes": null,
      "scatter_gather_support": null,
      // ... DMA configuration
    }
  }
}
```

### 4. PCILeech Optimizations

Specific optimizations for PCILeech firmware:

```json
{
  "pcileech_optimizations": {
    "recommended_payload_size": null,
    "optimal_read_strategy": "",  // "burst", "sequential", etc.
    "optimal_write_strategy": "",
    "tlp_processing_hints": {
      "prefer_32bit_addresses": null,
      "support_64bit_addresses": null,
      "max_outstanding_requests": null,
      "completion_timeout_us": null
    },
    "memory_window_strategy": {
      "window_size": null,
      "window_count": null,
      "access_pattern": ""  // "linear", "random", etc.
    }
  }
}
```

### 5. Advanced Features

Support for virtualization, security, and performance features:

```json
{
  "advanced_features": {
    "virtualization": {
      "sr_iov_capable": null,
      "max_vfs": null,
      // ... SR-IOV configuration
    },
    "security_features": {
      "ats_support": null,
      "pri_support": null,
      "pasid_support": null,
      // ... security features
    },
    "error_handling": {
      "aer_support": null,
      "ecrc_support": null,
      // ... error handling
    },
    "performance_features": {
      "relaxed_ordering": null,
      "no_snoop": null,
      // ... performance features
    }
  }
}
```

## Filling Out the Template

### Step 1: Basic Device Information

Start by filling in the device identification:
- Use `lspci -nn` to get vendor/device IDs
- Use `lspci -vvv` for detailed capability information
- Check `/sys/bus/pci/devices/[BDF]/` for additional details

### Step 2: Behavioral Profiling

Run behavioral profiling to capture timing and access patterns:

```bash
# Enable behavioral profiling in your build
./cli build --bdf 0000:03:00.0 --behavior-profiling
```

### Step 3: Manual Testing

For advanced features:
- Test interrupt behavior under load
- Measure DMA transfer characteristics
- Profile register access patterns
- Document any device-specific quirks

### Step 4: Validation

Validate your completed template:
- Ensure all critical fields are filled
- Test with actual device cloning
- Verify timing parameters are realistic
- Document any assumptions or limitations

## Using the Completed Template

Once filled out, the donor info template can be used for:

1. **Advanced Device Cloning**: Provide the template during build for optimized firmware
2. **Performance Tuning**: Use timing data to optimize access patterns
3. **Compatibility Testing**: Share templates for similar devices
4. **Documentation**: Maintain a library of device profiles

### Using Templates During Build

You can use a donor template to override discovered values during the build process:

```bash
# Use donor template during build
sudo python3 pcileech.py build --bdf 0000:03:00.0 --board 75t --donor-template my_device_profile.json
```

When using `--donor-template`:
- Template values override any discovered values when there's a conflict
- Null values in the template are ignored (discovered values are used)
- This allows you to selectively override specific device characteristics
- The template is only used for new builds, not for existing firmware

Example scenarios:
```bash
# Override device IDs while keeping discovered BAR configuration
# (set device IDs in template, leave BARs as null)
sudo python3 pcileech.py build --bdf 0000:03:00.0 --board 75t --donor-template custom_ids.json

# Use template and also output a new template with merged values
sudo python3 pcileech.py build --bdf 0000:03:00.0 --board 75t \
    --donor-template input_template.json \
    --output-template merged_template.json
```

## Best Practices

1. **Version Control**: Keep templates in version control to track changes
2. **Device Variations**: Create separate templates for different device revisions
3. **Testing**: Validate templates with actual hardware before production use
4. **Documentation**: Add detailed comments in the "comments" field
5. **Sharing**: Consider contributing templates for common devices

## Template Examples

Example templates for common devices can be found in:
- `configs/donor_templates/` directory
- Community contributions on GitHub
- Device manufacturer documentation

## Troubleshooting

### Common Issues

1. **Invalid JSON**: Use a JSON validator to check syntax
2. **Missing Required Fields**: Some fields may be required for specific features
3. **Incorrect Data Types**: Ensure numbers aren't quoted as strings
4. **Timing Values**: Use appropriate units (microseconds, milliseconds)

### Getting Help

- Check existing templates for examples
- Use `--with-comments` flag for field explanations
- Consult device datasheets for capability details
- Ask in community forums for device-specific guidance

## Related Documentation

- [Device Cloning](device-cloning.md)
- [Behavioral Profiling](firmware-uniqueness.md)
- [Manual Donor Dump](manual-donor-dump.md)
- [Template Architecture](template-architecture.md)