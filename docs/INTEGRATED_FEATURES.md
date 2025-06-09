# PCILeech FPGA Firmware Generator - Integrated Features

This document provides a comprehensive overview of the integrated features in the PCILeech FPGA firmware generator. These features work together to create a more realistic and functional PCIe device emulation.

## Table of Contents

1. [Full 4 KB Config-Space Shadow in BRAM](#full-4-kb-config-space-shadow-in-bram)
2. [Auto-Replicate MSI-X Table](#auto-replicate-msi-x-table)
3. [Capability Pruning](#capability-pruning)
4. [Deterministic Variance Seeding](#deterministic-variance-seeding)
5. [Integration Architecture](#integration-architecture)
6. [Build Process](#build-process)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

## Full 4 KB Config-Space Shadow in BRAM

The configuration space shadow BRAM implementation provides a complete 4 KB PCI Express configuration space in block RAM (BRAM) on the FPGA. This is a critical component for PCIe device emulation, as it allows the PCILeech firmware to accurately respond to configuration space accesses from the host system.

### Key Features

- Full 4 KB configuration space shadow in BRAM
- Dual-port access for simultaneous read/write operations
- Overlay RAM for writable fields (Command/Status registers)
- Initialization from donor device configuration data
- Little-endian format compatible with PCIe specification

### Implementation

The implementation consists of the following components:

1. **Configuration Space BRAM**: A 4 KB block RAM that stores the entire configuration space of the emulated PCIe device.
2. **Overlay RAM**: A smaller RAM that stores writable fields, allowing the host to modify certain configuration registers.
3. **State Machine**: Handles PCIe configuration space access requests (reads and writes).
4. **Donor Dump Extraction**: Enhanced to capture the full 4 KB configuration space from a donor device.

For more details, see [CONFIG_SPACE_SHADOW.md](CONFIG_SPACE_SHADOW.md).

## Auto-Replicate MSI-X Table

The MSI-X table replication feature extends the PCILeech FPGA firmware generator to accurately replicate the MSI-X capability structure from donor devices. This enables the emulated device to support advanced interrupt handling capabilities, which is critical for high-performance device emulation.

### Key Features

- Automatic parsing of MSI-X capability structure from donor configuration space
- Parameterized SystemVerilog implementation of MSI-X table and PBA (Pending Bit Array)
- Support for byte-enable granularity writes
- Interrupt delivery logic with masking support
- Integration with the existing BAR controller and configuration space shadow

### Implementation

The implementation consists of the following components:

1. **MSI-X Capability Parser**: Python module that extracts MSI-X capability information from the donor's configuration space.
2. **MSI-X Table Module**: SystemVerilog module that implements the MSI-X table and PBA in BRAM.
3. **BAR Controller Integration**: Updates to the BAR controller to route MSI-X table and PBA accesses to the appropriate memory regions.
4. **Build Process Integration**: Updates to the build process to include MSI-X parameters in the generated firmware.

For more details, see [MSIX_TABLE_REPLICATION.md](MSIX_TABLE_REPLICATION.md).

## Capability Pruning

The PCI capability pruning feature extends the PCILeech FPGA firmware generator to analyze and selectively modify or remove PCI capabilities that cannot be faithfully emulated. This ensures that the emulated device presents a consistent and compatible configuration space to the host system.

### Key Features

- Automatic analysis of standard and extended PCI capabilities
- Categorization of capabilities based on emulation feasibility
- Selective pruning of unsupported capabilities
- Modification of partially supported capabilities
- Preservation of capability chain integrity

### Implementation

The implementation consists of the following components:

1. **Capability Analysis**: Python module that identifies and categorizes all capabilities in the donor's configuration space.
2. **Pruning Logic**: Functions that implement specific pruning rules for different capability types.
3. **Build Integration**: Updates to the build process to include the capability pruning step.

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

For more details, see [CAPABILITY_PRUNING.md](CAPABILITY_PRUNING.md).

## Deterministic Variance Seeding

The manufacturing variance simulation module provides realistic hardware variance simulation for PCIe device firmware generation, adding timing jitter and parameter variations to make generated firmware more realistic and harder to detect. The deterministic variance seeding feature ensures that two builds of the same donor at the same commit fall in the same timing band.

### Key Features

- Deterministic seed generation based on device serial number (DSN) and build revision
- Consistent variance parameters for the same donor device and build revision
- Different variance parameters for different donor devices or build revisions
- Support for different device classes with appropriate variance ranges

### Implementation

The implementation consists of the following components:

1. **Deterministic Seed Generation**: Function that generates a deterministic seed based on DSN and build revision.
2. **RNG Initialization**: Function that initializes the random number generator with the deterministic seed.
3. **Variance Model Generation**: Function that generates a variance model with parameters derived from the deterministic seed.
4. **SystemVerilog Code Generation**: Function that generates SystemVerilog code with variance-aware timing based on the variance model.

### Device Classes

The following device classes are supported, each with different variance characteristics:

- **Consumer**: Higher variance, typical for consumer-grade devices
- **Enterprise**: Lower variance, typical for enterprise-grade devices
- **Industrial**: Moderate variance with extended temperature range
- **Automotive**: Lowest variance with widest temperature range

## Integration Architecture

The integration of these features is designed to be modular and maintainable, with clear separation of concerns and well-defined interfaces between components.

### Component Interactions

1. **Donor Dump Manager → Config Space Shadow**: The donor dump manager extracts the full 4 KB configuration space from the donor device and provides it to the config space shadow module.

2. **Config Space Shadow → MSI-X Table Replication**: The config space shadow provides the configuration space data to the MSI-X capability parser, which extracts the MSI-X table parameters.

3. **Config Space Shadow → Capability Pruning**: The config space shadow provides the configuration space data to the capability pruning module, which analyzes and prunes capabilities.

4. **Capability Pruning → Config Space Shadow**: The capability pruning module returns the pruned configuration space to the config space shadow module.

5. **Deterministic Variance Seeding → SystemVerilog Generation**: The deterministic variance seeding module provides variance parameters to the SystemVerilog generation process.

### Data Flow

1. The donor dump manager extracts the full 4 KB configuration space from the donor device.
2. The capability pruning module analyzes and prunes capabilities that cannot be faithfully emulated.
3. The MSI-X capability parser extracts MSI-X table parameters from the configuration space.
4. The deterministic variance seeding module generates variance parameters based on the DSN and build revision.
5. The build process generates SystemVerilog code with the pruned configuration space, MSI-X table parameters, and variance-aware timing.
6. The build process generates a TCL script with the appropriate parameters for the Vivado synthesis tool.
7. The Vivado synthesis tool generates the FPGA bitstream.

## Build Process

The build process integrates all the features to generate a complete FPGA firmware image.

### Build Steps

1. **Extract Donor Information**: Extract the full 4 KB configuration space from the donor device.
2. **Apply Capability Pruning**: Analyze and prune capabilities that cannot be faithfully emulated.
3. **Parse MSI-X Capability**: Extract MSI-X table parameters from the configuration space.
4. **Generate Deterministic Variance**: Generate variance parameters based on the DSN and build revision.
5. **Generate SystemVerilog Code**: Generate SystemVerilog code with the pruned configuration space, MSI-X table parameters, and variance-aware timing.
6. **Generate TCL Script**: Generate a TCL script with the appropriate parameters for the Vivado synthesis tool.
7. **Run Vivado Synthesis**: Run the Vivado synthesis tool to generate the FPGA bitstream.

### Command Line Options

The build process supports the following command line options:

- `--bdf`: PCIe Bus:Device.Function identifier (e.g., "0000:03:00.0").
- `--board`: Target board type (e.g., "75t").
- `--disable-capability-pruning`: Disable capability pruning.
- `--skip-donor-dump`: Skip using the donor_dump kernel module.
- `--donor-info-file`: Path to a JSON file containing donor information.
- `--device-type`: Specify device type for advanced generation (default: generic).
- `--advanced-sv`: Enable advanced SystemVerilog generation with comprehensive features.

## Testing

The integration of these features is tested using a comprehensive test suite that verifies that all features work together seamlessly.

### Test Cases

1. **Config Space Shadow Integration**: Verify that the config space shadow is properly integrated into the build process.
2. **MSI-X Table Replication**: Verify that the MSI-X table replication is properly integrated into the build process.
3. **Capability Pruning**: Verify that capability pruning is properly integrated into the build process.
4. **Deterministic Variance Seeding**: Verify that deterministic variance seeding produces consistent results for the same donor device and build revision.
5. **All Features Integration**: Verify that all features work together seamlessly.

### Running Tests

To run the integration tests:

```bash
python -m unittest tests/test_feature_integration.py
```

## Troubleshooting

### Common Issues

1. **Missing Donor Information**: If the donor dump fails to extract the full 4 KB configuration space, the build process will fall back to a synthetic configuration space. This may result in incomplete or incorrect emulation.

2. **Capability Pruning Errors**: If the capability pruning module encounters an error, it will log a warning and continue with the build process. This may result in incomplete or incorrect emulation.

3. **MSI-X Table Replication Errors**: If the MSI-X capability parser encounters an error, it will log a warning and continue with the build process. This may result in incomplete or incorrect emulation.

4. **Deterministic Variance Seeding Errors**: If the deterministic variance seeding module encounters an error, it will log a warning and fall back to non-deterministic variance. This may result in inconsistent timing behavior between builds.

### Debugging

1. **Enable Verbose Output**: Use the `--verbose` command line option to enable verbose output during the build process.

2. **Save Analysis**: Use the `--save-analysis` command line option to save detailed analysis information to a file.

3. **Check Build Logs**: Check the build logs for warnings or errors related to the integrated features.

4. **Check Generated Files**: Check the generated SystemVerilog code and TCL script for correctness.

5. **Run Integration Tests**: Run the integration tests to verify that all features work together seamlessly.