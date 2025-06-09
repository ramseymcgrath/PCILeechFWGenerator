# Configuration Space Shadow BRAM Implementation

This document describes the implementation of the full 4 KB configuration space shadow in BRAM for the PCILeech FPGA firmware generator.

## Overview

The configuration space shadow BRAM implementation provides a complete 4 KB PCI Express configuration space in block RAM (BRAM) on the FPGA. This is a critical component for PCIe device emulation, as it allows the PCILeech firmware to accurately respond to configuration space accesses from the host system.

Key features:
- Full 4 KB configuration space shadow in BRAM
- Dual-port access for simultaneous read/write operations
- Overlay RAM for writable fields (Command/Status registers)
- Initialization from donor device configuration data
- Little-endian format compatible with PCIe specification

## Architecture

The implementation consists of the following components:

1. **Configuration Space BRAM**: A 4 KB block RAM that stores the entire configuration space of the emulated PCIe device.
2. **Overlay RAM**: A smaller RAM that stores writable fields, allowing the host to modify certain configuration registers.
3. **State Machine**: Handles PCIe configuration space access requests (reads and writes).
4. **Donor Dump Extraction**: Enhanced to capture the full 4 KB configuration space from a donor device.

### SystemVerilog Modules

- `pcileech_tlps128_cfgspace_shadow.sv`: The main module implementing the configuration space shadow.
- `pcileech_tlps128_bar_controller.sv`: The BAR controller that interfaces with the configuration space shadow.

## Donor Dump Process

The donor dump process has been enhanced to extract the full 4 KB configuration space from a donor device:

1. The donor_dump kernel module extracts the full 4 KB configuration space and provides it as a hex-encoded string.
2. The donor_dump_manager.py processes this data and formats it for use with SystemVerilog's $readmemh function.
3. The formatted data is saved to a file named `config_space_init.hex` in little-endian format.
4. During FPGA synthesis, this file is used to initialize the configuration space BRAM.

## Overlay RAM for Writable Fields

The overlay RAM provides a mechanism for handling writable fields in the configuration space. When a PCIe device writes to a writable register (e.g., the Command register), the write is directed to the overlay RAM rather than the main configuration space BRAM.

When reading from a register with writable fields, the implementation combines data from both the main configuration space BRAM and the overlay RAM, using a mask to determine which bits come from which source.

The following registers have writable fields:
- Command register (offset 0x04)
- Status register (offset 0x06)
- Cache Line Size register (offset 0x0C)
- Latency Timer / BIST register (offset 0x3C)

## Integration with Build Process

The configuration space shadow is integrated into the build process:

1. The donor dump manager extracts the full 4 KB configuration space and saves it in the appropriate format.
2. The build process includes the configuration space shadow module in the generated TCL script.
3. The `config_space_init.hex` file is included in the project for BRAM initialization.

## Testing

The implementation includes comprehensive testing:

1. SystemVerilog testbench (`test_config_space_shadow.sv`) for functional verification.
2. Python unit tests (`test_config_space_extraction.py`) for donor dump extraction and formatting.

## Usage

The configuration space shadow is automatically included in the build process. No additional configuration is required to use this feature.

To verify that the configuration space shadow is working correctly, you can check the build logs for the message "Extended config space: ✓" and "Config space shadow BRAM: ✓".

## Limitations

- The current implementation supports a single PCIe function (function 0).
- Only standard PCIe capability structures are supported.
- The overlay RAM has a limited number of entries (32 by default).

## Future Enhancements

Possible future enhancements include:

- Support for multiple PCIe functions
- Dynamic reconfiguration of the configuration space
- Enhanced error handling and reporting
- Support for extended PCIe capabilities