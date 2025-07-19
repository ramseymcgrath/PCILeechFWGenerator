# PCIe Capabilities and Template Architecture

This document describes the PCIe capabilities handled by the PCILeech Firmware Generator and provides detailed information about how the SystemVerilog templates are created, filled, and integrated into the final firmware.

## Overview

The PCILeech Firmware Generator creates authentic PCIe device firmware by analyzing real donor hardware and generating comprehensive SystemVerilog implementations. The system handles multiple PCIe capabilities and features through a sophisticated template-based architecture.

The generation process involves three main phases:

1. **Device Analysis**: Extract configuration space, capabilities, and behavior from donor devices
2. **Context Building**: Assemble comprehensive template context from all data sources
3. **Template Rendering**: Generate SystemVerilog modules using Jinja2 templates

## Supported PCIe Capabilities

### 1. Configuration Space Shadow (4KB BRAM)

The configuration space shadow is the foundation of PCIe device emulation, providing complete 4KB configuration space emulation in FPGA block RAM.

**Key Features:**

- **Full 4KB Configuration Space**: Complete emulation of standard and extended configuration space
- **Dual-Port Access**: Simultaneous read/write operations for performance
- **Overlay RAM**: Dedicated storage for writable fields (Command/Status registers)
- **Automatic Initialization**: Populated from real donor device data or synthetic generation
- **Hardware Integration**: Seamless integration with PCIe core configuration interface

**Implementation Details:**

- Main configuration space stored in BRAM (`config_space_ram[0:1023]`)
- Overlay RAM for writable fields (`overlay_ram[0:OVERLAY_ENTRIES-1]`)
- State machine handles PCIe configuration TLP processing
- Automatic overlay mapping detects writable registers from PCIe specifications

```systemverilog
// Configuration Space Shadow parameters
parameter CONFIG_SPACE_SIZE = 4096;
parameter OVERLAY_ENTRIES = 64;
parameter DUAL_PORT = 1;
```

### 2. MSI-X (Message Signaled Interrupts Extended)

MSI-X provides scalable interrupt handling with up to 2048 interrupt vectors, essential for modern PCIe devices.

**MSI-X Table Structure:**

- **Message Address Lower (32-bit)**: Target memory address for interrupt message
- **Message Address Upper (32-bit)**: Upper 32 bits for 64-bit addressing
- **Message Data (32-bit)**: Interrupt payload data
- **Vector Control (32-bit)**: Mask bit and reserved fields

**Features Implemented:**

- **Parameterized Table Size**: 1-2048 vectors based on donor device
- **BRAM-based Table Storage**: Efficient memory usage with block RAM attributes
- **Pending Bit Array (PBA)**: Tracks pending interrupts for masked vectors
- **Interrupt Delivery Logic**: Validates vectors and delivers interrupts
- **Byte-Enable Support**: Granular write access to table entries

**Template Integration:**

```systemverilog
// MSI-X Table parameters derived from donor device
parameter NUM_MSIX = {{ NUM_MSIX }};
parameter MSIX_TABLE_BIR = {{ MSIX_TABLE_BIR }};
parameter MSIX_TABLE_OFFSET = {{ MSIX_TABLE_OFFSET }};
parameter MSIX_PBA_BIR = {{ MSIX_PBA_BIR }};
parameter MSIX_PBA_OFFSET = {{ MSIX_PBA_OFFSET }};
```

### 3. Power Management Capability

Power management enables PCIe devices to transition between different power states (D0, D1, D2, D3hot, D3cold).

**Power States Supported:**

- **D0**: Fully operational state
- **D3hot**: Low power state with auxiliary power
- **D3cold**: No power state (requires external power cycling)

**Implementation Features:**

- **PMCSR Register**: Power Management Control and Status Register
- **PME Support**: Power Management Event signaling
- **State Transitions**: Automatic timeout-based transitions
- **Minimal Resource Usage**: <40 LUT, <50 FF implementation

### 4. PCIe Express Capability

The PCIe Express capability provides device-specific PCIe functionality and advanced features.

**Key Registers:**

- **PCIe Capabilities Register**: Device type and supported features
- **Device Control/Status**: Device-specific control and status bits
- **Link Control/Status**: Link training and status information
- **Device Capabilities 2**: Advanced device capabilities

**Template Variables:**

- Device-specific capability values extracted from donor device
- Link width and speed configuration
- ASPM (Active State Power Management) settings
- Error reporting capabilities

### 5. Base Address Registers (BARs)

BAR implementation provides memory-mapped I/O regions for device communication.

**BAR Types Supported:**

- **Memory BARs**: 32-bit and 64-bit memory regions
- **I/O BARs**: I/O port regions (legacy support)
- **Prefetchable Memory**: Optimized for bulk data transfer

**Features:**

- **Parameterized Sizes**: 4KB to 4GB regions
- **Address Decoding**: Automatic address range validation
- **Regional Memory Access**: Subdivided into functional regions
- **Burst Support**: Optimized for high-throughput operations

## Template Architecture

The PCILeech template system uses a sophisticated multi-phase approach to generate authentic PCIe device firmware.

### 1. Data Collection Phase

#### Device Binding and Analysis

The generation process begins with comprehensive device analysis:

1. **VFIO Driver Binding**: Bind target device to VFIO driver for direct access
2. **Configuration Space Reading**: Extract complete 4KB configuration space
3. **Capability Walking**: Parse and identify all PCIe capabilities
4. **BAR Size Detection**: Determine BAR sizes through write-back testing
5. **MSI-X Table Analysis**: Extract interrupt table configuration if present

#### Manufacturing Variance Application

To make generated firmware more realistic, the system applies manufacturing variance:

```python
# Manufacturing variance parameters
class VarianceParameters:
    clock_jitter_percent_min: float = 2.0
    clock_jitter_percent_max: float = 5.0
    register_timing_jitter_ns_min: float = 10.0
    register_timing_jitter_ns_max: float = 50.0
    process_variation_percent_min: float = 5.0
    process_variation_percent_max: float = 15.0
```

### 2. Context Building Phase

#### PCILeechContextBuilder Integration

The `PCILeechContextBuilder` class assembles comprehensive template context from all data sources:

```python
class PCILeechContextBuilder:
    def build_context(
        self,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
        msix_data: Optional[Dict[str, Any]],
        interrupt_strategy: str = "intx",
        interrupt_vectors: int = 1,
    ) -> Dict[str, Any]:
```

#### Context Assembly Process

1. **Device Identifiers**: Extract vendor/device IDs, class codes, revision
2. **Configuration Space Context**: Process 4KB configuration space data
3. **MSI-X Context**: Parse MSI-X table and PBA information
4. **BAR Configuration**: Analyze BAR sizes, types, and memory regions
5. **Timing Configuration**: Apply manufacturing variance and timing parameters
6. **Overlay Mapping**: Generate writable register overlay mappings

### 3. Template Processing Pipeline

#### Phase 1: Analysis and Extraction

1. **Device Binding**: Bind donor device to VFIO driver
2. **Configuration Space Reading**: Extract 4KB configuration space
3. **Capability Walking**: Parse and analyze PCIe capabilities
4. **BAR Analysis**: Determine BAR sizes and types
5. **MSI-X Table Reading**: Extract MSI-X table data if present

#### Phase 2: Context Generation

1. **Device Profile Creation**: Generate device configuration structure
2. **Capability Mapping**: Map capabilities to template parameters
3. **Overlay Mapping**: Determine writable register overlays
4. **Manufacturing Variance**: Apply deterministic timing variations
5. **Template Context Assembly**: Combine all data sources

#### Phase 3: Template Rendering

1. **Template Selection**: Choose appropriate templates based on device type
2. **Context Injection**: Apply template context to Jinja2 templates
3. **Code Generation**: Generate SystemVerilog modules
4. **File Integration**: Create project files and build scripts

### 4. Overlay Mapping System

The overlay mapping system automatically detects writable registers in PCIe configuration space:

```python
class OverlayMapper:
    def detect_overlay_registers(
        self, config_space: Dict[int, int], capabilities: Dict[str, int]
    ) -> List[Tuple[int, int]]:
        """
        Detect registers that need overlay RAM for writable fields.
        Returns list of (offset, mask) tuples for overlay entries.
        """
```

**Overlay Detection Process:**

1. **Standard Register Analysis**: Check Command/Status, BAR, and capability registers
2. **Capability-Specific Overlays**: MSI-X, Power Management, PCIe Express registers
3. **Mask Generation**: Create bit-level masks for writable fields
4. **Validation**: Ensure overlay mappings are consistent with PCIe specifications

## SystemVerilog Module Hierarchy

### 1. Top-Level Module

- **pcileech_top**: Main wrapper module
- **Responsibilities**: Clock/reset distribution, PCIe interface, module instantiation
- **Template**: `top_level_wrapper.sv.j2`

### 2. Core Controller

- **pcileech_tlps128_bar_controller**: Main device controller
- **Responsibilities**: TLP processing, BAR management, capability coordination
- **Template**: `pcileech_tlps128_bar_controller.sv.j2`

### 3. Configuration Space Shadow

- **pcileech_tlps128_cfgspace_shadow**: Configuration space implementation
- **Responsibilities**: Config space access, overlay management, capability registers
- **Template**: `cfg_shadow.sv.j2`

### 4. MSI-X Subsystem

- **msix_table**: MSI-X table and PBA implementation
- **Responsibilities**: Interrupt table management, vector delivery, masking
- **Template**: `msix_table.sv.j2`

### 5. Power Management

- **pmcsr_stub**: Power management implementation
- **Responsibilities**: D-state transitions, PME handling, power control
- **Template**: `pmcsr_stub.sv.j2`

### 6. Memory Regions

- **region_device_ctrl**: Device control region
- **region_data_buffer**: Data buffer region
- **region_custom_pio**: Custom PIO region
- **Templates**: Various region-specific templates

## Configuration Space Structure

### Standard Configuration Space (0x00-0xFF)

- **0x00-0x03**: Vendor ID / Device ID
- **0x04-0x07**: Command / Status
- **0x08-0x0B**: Class Code / Revision ID
- **0x0C-0x0F**: Cache Line Size / Latency Timer / Header Type / BIST
- **0x10-0x27**: Base Address Registers (BARs 0-5)
- **0x28-0x2B**: Cardbus CIS Pointer
- **0x2C-0x2F**: Subsystem Vendor ID / Subsystem ID
- **0x30-0x33**: Expansion ROM Base Address
- **0x34-0x3B**: Capabilities Pointer / Reserved
- **0x3C-0x3F**: Interrupt Line / Pin / Min_Gnt / Max_Lat

### Capability Structures (0x40-0xFF)

- **0x40-0x47**: Power Management Capability
- **0x48-0x4F**: MSI Capability (if not using MSI-X)
- **0x50-0x5B**: MSI-X Capability (if supported)
- **0x60-0x9F**: PCIe Express Capability

### Extended Configuration Space (0x100-0xFFF)

- **0x100-0x2FF**: MSI-X Table (if supported)
- **0x300-0x3FF**: MSI-X PBA (if supported)
- **0x400-0xFFF**: Extended capabilities and vendor-specific regions

## Memory Organization

### BAR Memory Layout

```text
BAR0 Memory Map (example):
0x0000-0x00FF: Device Control Region
0x0100-0x01FF: Status Registers
0x0200-0x03FF: Data Buffer
0x0400-0x0FFF: Custom PIO Region
0x1000-0x1FFF: MSI-X Table (if applicable)
0x2000-0x2FFF: MSI-X PBA (if applicable)
```

### BRAM Allocation

- **Configuration Space**: 4KB block RAM for complete config space
- **Overlay RAM**: Variable size based on writable register count
- **MSI-X Table**: Sized based on interrupt vector count
- **Data Buffers**: Parameterized based on device requirements

## Build Integration

### 1. Project File Generation

The template system generates complete Vivado project files:

- **TCL Scripts**: Project creation and configuration
- **Constraint Files**: Timing and placement constraints
- **Memory Initialization**: Configuration space and MSI-X table data

### 2. Synthesis Optimization

Templates include synthesis-specific optimizations:

- **RAM Style Attributes**: Force block RAM inference
- **Timing Constraints**: Critical path optimization
- **Resource Sharing**: Efficient multiplexer generation

### 3. Simulation Support

Generated code includes simulation features:

- **Testbench Integration**: Automatic test pattern generation
- **Debug Outputs**: Comprehensive status and debug signals
- **Assertion Checking**: SystemVerilog assertions for verification

## Manufacturing Variance

### Deterministic Variance Application

The system applies realistic manufacturing variance to make generated firmware less detectable:

```python
class ManufacturingVarianceSimulator:
    def apply_timing_variance(
        self, base_timing: float, variance_percent: float
    ) -> float:
        """Apply deterministic timing variance based on device characteristics."""
```

### Variance Categories

1. **Clock Jitter**: 2-5% variation in clock timing
2. **Register Timing**: 10-50ns jitter in register access
3. **Power Noise**: 1-3% supply voltage variation effects
4. **Process Variation**: 5-15% parameter variation
5. **Temperature Drift**: 10-100 ppm/°C timing drift

## Testing and Validation

### Template Validation

1. **Syntax Checking**: Validate generated SystemVerilog syntax
2. **Simulation Testing**: Verify functionality with test patterns
3. **Timing Analysis**: Ensure timing constraints are met
4. **Resource Utilization**: Verify efficient FPGA resource usage

### Capability Testing

1. **Configuration Space Access**: Test all configuration registers
2. **MSI-X Functionality**: Verify interrupt table operation
3. **Power Management**: Test D-state transitions
4. **BAR Access**: Validate memory region access patterns

## Future Extensions

### Planned Capabilities

- **SR-IOV**: Single Root I/O Virtualization support
- **AER**: Advanced Error Reporting capability
- **ATS**: Address Translation Services
- **ACS**: Access Control Services

### Template System Enhancements

- **Multi-Function Support**: Multiple PCIe functions per device
- **Dynamic Reconfiguration**: Runtime capability modification
- **Enhanced Debugging**: Improved debug and trace capabilities
- **Performance Optimization**: Advanced timing and resource optimization

---

For more detailed information about specific capabilities, see the individual documentation pages for [Configuration Space Shadow](config-space-shadow), [MSI-X Implementation](msix-implementation), and [Device Cloning Process](device-cloning).
