# PCI Capability Pruning Feature

This document describes the implementation of the PCI capability pruning feature for the PCILeech FPGA firmware generator.

## Overview

The PCI capability pruning feature extends the PCILeech FPGA firmware generator to analyze and selectively modify or remove PCI capabilities that cannot be faithfully emulated. This ensures that the emulated device presents a consistent and compatible configuration space to the host system.

Key features:
- Automatic analysis of standard and extended PCI capabilities
- Categorization of capabilities based on emulation feasibility
- Selective pruning of unsupported capabilities
- Modification of partially supported capabilities
- Preservation of capability chain integrity

## Architecture

The implementation consists of the following components:

1. **Capability Analysis**: Python module that identifies and categorizes all capabilities in the donor's configuration space.
2. **Pruning Logic**: Functions that implement specific pruning rules for different capability types.
3. **Build Integration**: Updates to the build process to include the capability pruning step.

### Capability Analysis

The `pci_capability.py` module provides functions to:
- Find and traverse both standard and extended capability chains
- Categorize capabilities based on emulation feasibility
- Determine appropriate pruning actions for each capability

### Pruning Rules

The following specific pruning rules are implemented:

1. **ASPM / L1SS**:
   - Clear LinkCtl ASPM bits in the PCIe capability
   - Remove the entire L1SS extended capability

2. **OBFF / LTR**:
   - Zero OBFF & LTR bits in Device Control 2 register
   - Remove the LTR extended capability if present

3. **SR-IOV**:
   - Remove the entire SR-IOV extended capability
   - Fix next_cap pointer of previous node to maintain chain integrity

4. **Advanced PM**:
   - Keep only D0/D3hot power states
   - Clear PME support bits

### Build Integration

The capability pruning feature is integrated into the build process:
- The pruning is applied after extracting the donor configuration space
- The pruned configuration space is used for initializing the BRAM
- Configuration options allow enabling/disabling the pruning feature

## Capability Categories

Capabilities are categorized into the following groups:

1. **Fully Supported**: Capabilities that can be completely emulated (e.g., MSI-X)
2. **Partially Supported**: Capabilities that can be partially emulated with modifications (e.g., PCIe, Power Management)
3. **Unsupported**: Capabilities that cannot be emulated and should be removed (e.g., SR-IOV, L1SS)
4. **Critical**: Capabilities that are essential for operation and must be preserved

## Usage

The capability pruning feature is automatically included in the build process. By default, it will analyze and prune capabilities according to the predefined rules.

To disable capability pruning, use the `--disable-capability-pruning` flag:

```
python build.py --bdf 0000:03:00.0 --board 75t --disable-capability-pruning
```

To verify that the capability pruning is working correctly, you can check the build logs for the message "Capability pruning: ✓".

## Testing

The implementation includes comprehensive testing:
- Python unit tests (`test_pci_capability.py`) for the capability analysis and pruning functionality
- Integration tests to verify the pruned configuration space works correctly with the FPGA firmware

## Limitations

- The current implementation focuses on the most common capabilities
- Some vendor-specific capabilities may not be properly categorized
- The pruning logic assumes standard capability structures as defined in the PCIe specification

## Future Enhancements

Possible future enhancements include:
- Support for more capability types
- More granular control over which capabilities are pruned
- Dynamic capability emulation based on host system requirements
- Enhanced reporting of pruned capabilities

## References

- PCI Express Base Specification, Revision 3.0
- PCI Local Bus Specification, Revision 3.0