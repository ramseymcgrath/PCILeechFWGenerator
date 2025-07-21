
## Device Cloning

The device cloning process creates an FPGA-based replica of a PCIe device through systematic hardware analysis and template generation. This section details the multi-stage process and error handling mechanisms.

### Prerequisites and System Requirements

Before cloning begins, the system must meet specific requirements:

- **IOMMU Support**: Intel VT-d or AMD-Vi must be enabled in BIOS/UEFI
- **Kernel Configuration**: VFIO modules loaded (`vfio`, `vfio-pci`, `vfio_iommu_type1`)
- **Root Privileges**: Required for VFIO device binding operations
- **Fallback Mode**: For testing environments without IOMMU, use `iommu=pt` or `vfio.enable_unsafe_noiommu_mode=1`

### Stage 1: VFIO Device Acquisition

The generator establishes exclusive control over the target PCIe device through Linux VFIO:

1. **IOMMU Group Discovery**: Identifies all devices sharing the same IOMMU group as the target BDF (e.g., `0000:01:00.0`)
2. **Driver Unbinding**: Safely unbinds existing kernel drivers from all group members
3. **VFIO Binding**: Rebinds devices to the `vfio-pci` driver for userspace access
4. **Handle Creation**: Establishes `/dev/vfio/<group>` interface for safe device interaction

**Error Handling**:

- **IOMMU Unavailable**: Falls back to heuristic size estimation (requires explicit enablement)
- **Driver Conflicts**: Automatically handles in-use drivers with graceful fallback
- **Permission Errors**: Provides clear diagnostic messages for privilege escalation

### Stage 2: Configuration Space Analysis

The generator performs comprehensive configuration space extraction:

#### Standard PCI Header (0x00-0xFF)

- **Device Identity**: Vendor ID, Device ID, Subsystem IDs, Class Code, Revision
- **Command/Status**: Capability flags, error status, device state
- **BAR Registers**: Base Address Registers 0-5 with size and type information
- **Interrupt Configuration**: Legacy INTx pin assignments

#### Extended Configuration Space (0x100-0xFFF)

- **Capability Structures**: MSI/MSI-X, Power Management, PCIe-specific capabilities
- **Vendor-Specific**: Custom capability blocks preserved byte-for-byte
- **Advanced Features**: AER, VC, PASID, and other modern PCIe capabilities

**Validation and Security**:

- **Checksum Generation**: SHA-256 hash of configuration space prevents generic firmware
- **Signature Verification**: Ensures unique firmware per donor device
- **Sanitization**: Removes potentially sensitive vendor-specific data when requested

### Stage 3: BAR Discovery and Memory Mapping

Systematic analysis of Base Address Registers determines memory layout:

```
For each BAR index (0-5):
├── Issue VFIO_DEVICE_GET_REGION_INFO ioctl
├── Extract: size, read/write permissions, mmap capability
├── Filter: Ignore I/O ports and zero-sized regions
├── Record: All valid MMIO BARs with metadata
└── Select: Largest MMIO BAR as primary window
```

**Advanced BAR Handling**:

- **64-bit BARs**: Properly handles paired 32-bit registers
- **Prefetchable Memory**: Preserves caching hints and optimization flags
- **Size Validation**: Ensures BAR sizes are power-of-2 aligned
- **Conflict Resolution**: Handles overlapping or invalid BAR configurations

**Fallback Mechanisms**:

- **Heuristic Sizing**: When VFIO fails, estimates BAR sizes from register patterns
- **Conservative Defaults**: Uses safe minimum sizes for critical BARs
- **Manual Override**: Allows explicit BAR configuration via command-line parameters

### Stage 4: Interrupt Architecture Analysis

The generator determines optimal interrupt emulation strategy:

#### Priority Order (Highest to Lowest)

1. **MSI-X**: Multi-vector message signaled interrupts
   - Validates table size > 0
   - Preserves vector count and table structure
   - Maps interrupt vectors to FPGA resources

2. **MSI**: Single-vector message signaled interrupts
   - Fallback when MSI-X unavailable
   - Simpler implementation with single interrupt line

3. **Legacy INTx**: Pin-based interrupts
   - Last resort for older devices
   - Emulates traditional interrupt sharing

**Capability Validation**:

- **Table Size Verification**: Ensures MSI-X table is properly sized
- **Vector Count Limits**: Respects hardware and software constraints
- **Interrupt Routing**: Validates interrupt pin assignments

### Stage 5: Template Context Generation

All extracted data is consolidated into a comprehensive template context:

#### Core Components

- **Device Identity**: Complete PCI configuration header
- **Memory Layout**: BAR map with sizes, types, and access patterns
- **Interrupt Configuration**: Selected interrupt mechanism with parameters
- **Timing Parameters**: Clock domains, reset sequences, power states
- **Feature Flags**: DMA capabilities, error handling, debug interfaces

#### Validation Pipeline

```
Context Validation:
├── Required Fields Check
│   ├── Non-zero Vendor ID
│   ├── Valid Device Class
│   └── Usable MMIO BAR present
├── Consistency Verification
│   ├── BAR size alignment
│   ├── Capability chain integrity
│   └── Interrupt configuration validity
└── Security Validation
    ├── Signature uniqueness
    ├── No default/generic patterns
    └── Sanitized vendor data
```

**Error Recovery**:

- **Missing BARs**: Provides synthetic minimal BAR configuration
- **Invalid Capabilities**: Gracefully degrades to simpler interrupt modes
- **Corrupted Data**: Attempts repair or fails with detailed diagnostics

### Stage 6: Firmware Generation

The validated context drives the Jinja2/SystemVerilog template engine:

#### Output Artifacts

- **FPGA Bitstream**: Device-specific `.bit` or `.bin` file
- **Configuration Headers**: C/C++ headers for host software integration
- **JSON Metadata**: Machine-readable device description
- **Build Reports**: Synthesis timing, resource utilization, verification results

#### Quality Assurance

- **Template Validation**: Ensures generated Verilog is syntactically correct
- **Resource Estimation**: Predicts FPGA utilization before synthesis
- **Timing Analysis**: Validates clock domain crossings and setup/hold times

### Quick Start Command

```bash
# Enable IOMMU and run generator
sudo python3 pcileech.py build --bdf 0000:01:00.0 --board pcileech_35t325_x4
```
