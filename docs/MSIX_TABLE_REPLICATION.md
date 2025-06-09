# MSI-X Table Replication Feature

This document describes the implementation of the MSI-X table replication feature for the PCILeech FPGA firmware generator.

## Overview

The MSI-X table replication feature extends the PCILeech FPGA firmware generator to accurately replicate the MSI-X capability structure from donor devices. This enables the emulated device to support advanced interrupt handling capabilities, which is critical for high-performance device emulation.

Key features:
- Automatic parsing of MSI-X capability structure from donor configuration space
- Parameterized SystemVerilog implementation of MSI-X table and PBA (Pending Bit Array)
- Support for byte-enable granularity writes
- Interrupt delivery logic with masking support
- Integration with the existing BAR controller and configuration space shadow

## Architecture

The implementation consists of the following components:

1. **MSI-X Capability Parser**: Python module that extracts MSI-X capability information from the donor's configuration space.
2. **MSI-X Table Module**: SystemVerilog module that implements the MSI-X table and PBA in BRAM.
3. **BAR Controller Integration**: Updates to the BAR controller to route MSI-X table and PBA accesses to the appropriate memory regions.
4. **Build Process Integration**: Updates to the build process to include MSI-X parameters in the generated firmware.

### MSI-X Capability Parser

The `msix_capability.py` module provides functions to:
- Find the MSI-X capability structure in the configuration space
- Extract the table size, BIR indicators, and offsets for both table and PBA
- Generate SystemVerilog code for the MSI-X table implementation

### MSI-X Table Module

The `msix_table.sv` module implements:
- Parameterized MSI-X table and PBA storage in BRAM
- BAR access interface for reading and writing MSI-X table entries
- Interrupt delivery logic with support for vector and function masking
- PBA functionality for tracking pending interrupts

### BAR Controller Integration

The BAR controller has been updated to:
- Instantiate the MSI-X table module
- Route MSI-X table and PBA accesses to the appropriate module
- Extract MSI-X control information from the configuration space
- Provide an interface for triggering MSI-X interrupts

### Build Process Integration

The build process has been updated to:
- Parse MSI-X capability information from the donor's configuration space
- Include MSI-X parameters in the generated TCL script
- Report MSI-X table replication status in the build summary

## MSI-X Table Structure

The MSI-X table consists of entries, each containing:
- Address field (64-bit, split into two 32-bit DWORDs)
- Data field (32-bit)
- Control field (32-bit, with bit 0 being the vector mask bit)

The PBA consists of bit flags indicating which vectors have pending interrupts.

## Usage

The MSI-X table replication feature is automatically included in the build process when a donor device with MSI-X capability is detected. No additional configuration is required to use this feature.

To verify that the MSI-X table replication is working correctly, you can check the build logs for the message "MSI-X table replication: ✓".

## Interrupt Delivery

When an interrupt is triggered:
1. The MSI-X table module checks if the vector is masked (either individually or by function mask)
2. If not masked, it asserts the `msix_interrupt` signal and provides the vector number
3. If masked, it sets the corresponding bit in the PBA
4. When the interrupt is acknowledged, the pending bit is cleared

## Testing

The implementation includes comprehensive testing:
1. Python unit tests (`test_msix_capability.py`) for the MSI-X capability parsing functionality
2. SystemVerilog testbench (`msix_table_tb.sv`) for the MSI-X table module

## Limitations

- The current implementation supports a maximum of 2048 MSI-X table entries (limited by the 11-bit vector field)
- The MSI-X table and PBA must be in the same BAR (typically BAR0)
- The implementation assumes little-endian byte ordering

## Future Enhancements

Possible future enhancements include:
- Support for MSI-X tables in different BARs
- Enhanced error handling and reporting
- Performance optimizations for large MSI-X tables
- Support for MSI-X in multi-function devices

## References

- PCI Express Base Specification, Revision 3.0
- MSI-X ECN for PCI Local Bus Specification, Revision 3.0