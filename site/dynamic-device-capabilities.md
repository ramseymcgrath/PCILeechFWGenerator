---
layout: default
title: "Dynamic Device Capabilities"
description: "Advanced PCIe device capability generation with realistic network, storage, media, and USB function emulation"
---

## Overview

The PCILeech Firmware Generator includes advanced dynamic device capability generation that creates realistic PCIe device configurations based on build-time provided vendor and device IDs. This system generates authentic device capabilities without hardcoding, ensuring unique and secure firmware generation.

The dynamic capability system analyzes vendor/device ID patterns to generate realistic PCIe capabilities, BARs, and device features for multiple device categories:

- **Network Functions**: Ethernet, WiFi, Bluetooth, Cellular controllers
- **Storage Functions**: NVMe, SATA, RAID, SCSI, IDE controllers  
- **Media Functions**: HD Audio, Video, Multimedia controllers
- **USB Functions**: USB4, xHCI, EHCI, UHCI, OHCI controllers

## Key Features

### Pattern-Based Analysis

- **No Hardcoded Devices**: Uses vendor-specific patterns and device ID ranges
- **Dynamic Scaling**: Higher device IDs generate more advanced capabilities
- **Vendor Recognition**: Intel, AMD, NVIDIA, Broadcom, Realtek patterns
- **Security-Focused**: Prevents signature duplication through dynamic generation

### Realistic Capabilities

- **SR-IOV**: Up to 64 Virtual Functions for enterprise devices
- **MSI-X**: Appropriate vector counts based on device complexity
- **Advanced Error Reporting**: For storage and high-reliability devices
- **Modern Features**: PTM, LTR, ACS for time-sensitive and isolated functions

### Production Ready

- **Build Integration**: Single function call with vendor/device IDs from build process
- **Error Handling**: Comprehensive logging with existing infrastructure
- **Type Safety**: Full type hints and structured output
- **Fallback Handling**: Generic capabilities for unknown device types

## Device Categories

### Network Functions

Generate realistic network controller capabilities:

```python
from pci_capability.dynamic_functions import get_network_capabilities

# Generate network capabilities from build-time IDs
config = get_network_capabilities(vendor_id=0x8086, device_id=0x1572)
```

**Supported Features:**

- **Ethernet Controllers**: 1GbE to 100GbE with queue scaling
- **WiFi Controllers**: 802.11ac/ax/be with MIMO support
- **Advanced Capabilities**: SR-IOV, ACS, LTR, PTM for enterprise devices
- **Realistic BARs**: Register spaces, MSI-X tables, flash/EEPROM regions
- **Feature Scaling**: Queue counts, VF counts, link speeds based on device ID

**Example Output:**

- Intel X710 pattern (0x8086:0x1572): 10GbE, SR-IOV (32 VFs), MSI-X (64 vectors)
- Realtek RTL8111 pattern (0x10ec:0x8168): 1GbE, basic MSI, standard features

### Storage Functions

Generate comprehensive storage controller capabilities:

```python
from pci_capability.dynamic_functions import get_storage_capabilities

config = get_storage_capabilities(vendor_id=0x144d, device_id=0xa808)
```

**Supported Categories:**

- **NVMe Controllers**: Multiple namespaces, admin/IO queues, TRIM support
- **SATA AHCI**: NCQ, hotplug, multi-port configurations
- **RAID Controllers**: Multiple RAID levels, cache, battery backup for enterprise
- **SCSI Controllers**: Tagged queuing, multiple targets, version scaling
- **Legacy IDE**: UDMA, DMA support for older systems

**Dynamic Features:**

- **Queue Depths**: 16-1024 based on device complexity
- **Namespace Counts**: 16-1024 for NVMe based on device ID
- **Port Counts**: 4-8 SATA ports for controllers
- **Cache Sizes**: 512MB-2GB for RAID controllers

### Media Functions

Generate audio and video controller capabilities:

```python
from pci_capability.dynamic_functions import get_media_capabilities

config = get_media_capabilities(vendor_id=0x8086, device_id=0x0c0c)
```

**Supported Types:**

- **HD Audio Controllers**: Multi-channel, high sample rates, codec support
- **Basic Audio**: Legacy stereo with power management
- **Video Controllers**: Hardware acceleration, frame buffers, resolution scaling

**Dynamic Scaling:**

- **Channel Counts**: 2-8 channels based on device capability
- **Sample Rates**: 44.1kHz-192kHz for high-end devices
- **Video Memory**: 64MB-512MB based on device ID
- **Resolutions**: 720p-4K support scaling

### USB Functions

Generate USB controller capabilities for all USB standards:

```python
from pci_capability.dynamic_functions import get_usb_capabilities

config = get_usb_capabilities(vendor_id=0x1912, device_id=0x0015)
```

**Controller Types:**

- **USB4**: 40Gbps, Thunderbolt compatibility, advanced features
- **xHCI**: USB 3.x, streams, multiple interrupters
- **EHCI**: USB 2.0, companion controller support
- **Legacy**: UHCI/OHCI for USB 1.1 compatibility

**Port Scaling:**

- **USB4**: 2-4 ports based on device complexity
- **xHCI**: 4-16 ports with MSI-X support
- **EHCI**: 4-8 ports with companion controllers
- **Legacy**: 2-4 ports with basic interrupt handling

## Integration Guide

### Automatic Detection

The system can automatically detect device function type:

```python
from pci_capability.dynamic_functions import create_dynamic_device_capabilities

# Auto-detect and generate appropriate capabilities
config = create_dynamic_device_capabilities(
    vendor_id=build_vendor_id,    # From your build process
    device_id=build_device_id,    # From your build process
    class_code=build_class_code   # Optional PCI class code
)
```

### Build Process Integration

For direct integration into your firmware build process:

```python
# Example build integration
def generate_firmware_config(vendor_id: int, device_id: int, board_type: str):
    """Generate firmware configuration with dynamic capabilities."""
    
    # Generate device capabilities
    device_config = create_dynamic_device_capabilities(vendor_id, device_id)
    
    # Extract for firmware generation
    capabilities = device_config['capabilities']
    bars = device_config['bars']
    features = device_config['features']
    
    # Generate SystemVerilog templates
    return render_firmware_template(
        board_type=board_type,
        vendor_id=vendor_id,
        device_id=device_id,
        class_code=device_config['class_code'],
        capabilities=capabilities,
        bars=bars,
        features=features
    )
```

### Configuration Output

The dynamic system generates structured configuration:

```json
{
  "vendor_id": 32902,
  "device_id": 5746,
  "class_code": 131072,
  "capabilities": [
    {
      "cap_id": 1,
      "version": 3,
      "d3_support": true,
      "aux_current": 0
    },
    {
      "cap_id": 5,
      "multi_message_capable": 3,
      "supports_64bit": true,
      "supports_per_vector_masking": true
    }
  ],
  "bars": [
    {
      "bar": 0,
      "type": "memory",
      "size": 131072,
      "prefetchable": false,
      "description": "Device registers"
    }
  ],
  "features": {
    "category": "ethernet",
    "queue_count": 32,
    "supports_sriov": true,
    "max_vfs": 32
  }
}
```

## Security Considerations

### Anti-Duplication Design

The dynamic system prevents signature duplication:

- **Pattern-Based**: No hardcoded device lists that could create identical signatures
- **ID-Based Scaling**: Device capabilities scale with vendor/device ID characteristics
- **Entropy Sources**: Multiple device ID bits used for feature determination
- **Vendor Variations**: Different algorithms for different vendors

### Authenticity Features

Generated devices maintain authenticity:

- **Realistic Ranges**: Capabilities stay within vendor-typical ranges
- **Proper Relationships**: MSI-X vectors match queue counts appropriately
- **Standard Compliance**: All generated capabilities follow PCIe specifications
- **Error Handling**: Graceful fallbacks for unknown or unusual device IDs

## Implementation Details

### Vendor Pattern Recognition

The system recognizes vendor-specific patterns:

```python
# Intel network device patterns
if vendor_id == 0x8086:
    if device_upper_byte in [0x15, 0x16, 0x17]:  # Ethernet ranges
        return "network"
    elif device_upper_byte in [0x24, 0x25, 0x27]:  # WiFi ranges  
        return "wifi"
```

### Dynamic Feature Scaling

Features scale based on device ID analysis:

```python
def _calculate_queue_count(self) -> int:
    """Calculate queue count based on device ID."""
    if self.device_id > 0x3000:
        return 64  # High-end device
    elif self.device_id > 0x2000:
        return 32  # Mid-range device
    else:
        return 16  # Entry-level device
```

### Capability Relationships

The system maintains realistic capability relationships:

- **SR-IOV + ACS**: Access Control Services enabled with SR-IOV
- **MSI-X + Queues**: Vector counts match queue requirements
- **Power Management**: Appropriate aux current for device types
- **BAR Layouts**: Realistic register space and table layouts

## Advanced Usage

### Custom Function Hints

Override automatic detection with explicit hints:

```python
# Force specific function type
config = create_dynamic_device_capabilities(
    vendor_id=0x8086,
    device_id=0x1234,
    function_hint="storage"  # Force storage analysis
)
```

### Capability Filtering

Filter capabilities for specific use cases:

```python
def filter_basic_capabilities(config):
    """Keep only basic capabilities for simple devices."""
    basic_caps = [0x01, 0x05, 0x10]  # PM, MSI, PCIe
    config['capabilities'] = [
        cap for cap in config['capabilities'] 
        if cap['cap_id'] in basic_caps
    ]
    return config
```

### Template Integration

Integrate with existing template systems:

```python
def render_device_template(vendor_id, device_id, template_name):
    """Render device template with dynamic capabilities."""
    
    # Generate capabilities
    config = create_dynamic_device_capabilities(vendor_id, device_id)
    
    # Render with template engine
    return template_engine.render(
        template_name,
        **config,
        timestamp=datetime.now(),
        generator_version="1.0.0"
    )
```

## Troubleshooting

### Common Issues

**Unknown Device Type:**

```bash
WARNING: Unknown function type for device 1234:5678, using generic capabilities
```

*Solution*: The device ID pattern wasn't recognized. Generic capabilities will be used, or provide a function hint.

**Missing Capabilities:**

```python
# Add explicit capability checks
if required_capability not in [cap['cap_id'] for cap in config['capabilities']]:
    # Add required capability manually
```

**BAR Configuration Issues:**

```python
# Validate BAR layout
total_bars = len(config['bars'])
if total_bars > 6:  # PCIe max BARs
    config['bars'] = config['bars'][:6]
```

## See Also

- [Device Cloning Process](device-cloning.md) - Hardware-based device extraction
- [Template Architecture](template-architecture.md) - SystemVerilog template system
- [Configuration Space Shadow](config-space-shadow.md) - Configuration space emulation
- [Supported Devices](supported-devices.md) - Compatible hardware list
