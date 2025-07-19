# Supported Devices

PCILeech Firmware Generator supports a wide range of PCIe devices as donors for firmware generation. This page provides detailed information about device compatibility, requirements, and recommendations.

## Device Categories

### Network Interface Cards (NICs)

Network cards are excellent donors due to their simple PCIe implementation and widespread availability.

**Recommended Models:**

- **Realtek RTL8111/8168/8411** - Common Gigabit Ethernet controllers
- **Intel 82574L/82579LM** - Enterprise-grade NICs with good documentation
- **Broadcom NetXtreme** - High-performance network controllers

### Audio Devices

Sound cards and audio interfaces provide good donor material with well-documented PCIe implementations.

**Recommended Models:**

- **Creative Sound Blaster** series - Professional audio cards
- **ASUS Xonar** series - High-quality audio interfaces
- **M-Audio** interfaces - Professional audio equipment
- **Generic USB audio controllers** - Simple PCIe-to-USB bridges

### Capture Cards

Video capture devices offer diverse PCIe configurations and are readily available.

**Recommended Models:**

- **Blackmagic DeckLink** series - Professional video capture
- **AVerMedia Live Gamer** series - Gaming capture cards
- **Elgato Capture Cards** - Streaming-focused devices
- **Hauppauge WinTV** series - TV tuner cards

### Other Suitable Devices

Various other PCIe devices can serve as effective donors.

**Additional Categories:**

- **SATA/SAS Controllers** - Storage interface cards
- **USB 3.0/3.1 Controllers** - PCIe-to-USB expansion cards
- **Serial/Parallel Port Cards** - Legacy interface adapters
- **GPIO/Digital I/O Cards** - Industrial control interfaces

## Device Requirements

### Hardware Requirements

- **PCIe Interface** - Must be a standard PCIe device (not PCIe-to-PCI bridges)
- **Standard Form Factor** - x1, x4, x8, or x16 slots supported
- **Accessible Configuration Space** - Device must respond to PCIe configuration reads
- **VFIO Compatible** - Must be bindable to VFIO driver

### Software Requirements

- **Linux IOMMU Support** - Device must be in a separate IOMMU group
- **VFIO Driver Binding** - Must support vfio-pci driver binding
- **Configuration Space Access** - Full 4KB configuration space must be readable

## Device Selection Guidelines

### Ideal Donor Characteristics

1. **Simple Implementation** - Devices with straightforward PCIe logic
2. **Good Documentation** - Well-documented devices are easier to analyze
3. **Standard Compliance** - Devices that follow PCIe specifications closely
4. **Stable Operation** - Devices that don't require complex initialization

### Devices to Avoid

- **On-board Devices** - Integrated audio, network, or storage controllers
- **Critical System Components** - Graphics cards, primary storage controllers
- **Complex Multi-function Devices** - Devices with multiple PCIe functions
- **Proprietary Implementations** - Devices with non-standard PCIe behavior

## Compatibility Testing

### Pre-selection Verification

Before using a device as a donor, verify compatibility:

```bash
# Check device PCIe configuration
lspci -vvv -s [device_id]

# Verify IOMMU group isolation
./vfio_check.py [device_id]

# Test VFIO binding
sudo ./force_vfio_binds.sh [device_id]
```

### Configuration Analysis

The generator analyzes several key aspects of donor devices:

- **Vendor/Device ID** - Unique device identification
- **Configuration Space Layout** - Register organization and capabilities
- **BAR Configuration** - Memory and I/O resource requirements
- **MSI/MSI-X Support** - Interrupt handling capabilities
- **Power Management** - PCIe power states and control

## Target FPGA Boards

### Supported PCILeech Boards

The generator supports firmware generation for these PCILeech-compatible boards:

- **pcileech_75t484_x1** - Xilinx Spartan-7 XC7S75T, x1 PCIe
- **pcileech_35t325_x4** - Xilinx Spartan-6 XC6SLX25, x4 PCIe
- **pcileech_100t484_x1** - Xilinx Spartan-7 XC7S100T, x1 PCIe

### Board-specific Considerations

Each target board has specific resource constraints:

- **Logic Resources** - LUT and flip-flop availability
- **Memory Resources** - Block RAM for configuration space shadow
- **I/O Resources** - PCIe transceivers and general-purpose I/O
- **Clock Resources** - PCIe clock domains and user clocks

## Troubleshooting Device Issues

### Common Problems

1. **VFIO Binding Failures** - Device in use by another driver
2. **IOMMU Group Conflicts** - Device shares IOMMU group with critical components
3. **Configuration Space Errors** - Incomplete or corrupted configuration data
4. **Power Management Issues** - Device doesn't respond after power state changes

### Diagnostic Tools

Use the included tools to diagnose device issues:

```bash
# Comprehensive device analysis
./vfio_setup_checker.py --device [device_id] --verbose

# Interactive troubleshooting
./vfio_setup_checker.py --interactive

# Generate automated fix scripts
./vfio_setup_checker.py --generate-script
```

## Best Practices

### Security Considerations

- **Isolated Testing** - Use dedicated hardware for donor analysis
- **Firmware Privacy** - Keep generated firmware private and secure
- **Clean Environment** - Use isolated build environments

### Performance Optimization

- **Device Selection** - Choose devices with appropriate complexity
- **Resource Planning** - Consider target board resource constraints
- **Testing Methodology** - Implement comprehensive testing procedures

### Development Workflow

1. **Device Identification** - Catalog available donor devices
2. **Compatibility Testing** - Verify VFIO and IOMMU compatibility
3. **Configuration Analysis** - Extract and analyze device configuration
4. **Firmware Generation** - Generate custom firmware for target board
5. **Validation Testing** - Test generated firmware functionality

## Contributing Device Support

### Adding New Devices

To add support for new device types:

1. **Test Compatibility** - Verify device works with existing tools
2. **Document Configuration** - Record device-specific requirements
3. **Submit Examples** - Provide working configuration examples
4. **Update Documentation** - Add device to compatibility lists

### Reporting Issues

When reporting device compatibility issues:

1. **Provide Device Information** - Include lspci output and device details
2. **Include Error Messages** - Capture complete error logs
3. **Describe Environment** - Document system configuration
4. **Test Isolation** - Verify issue isn't system-specific

---

For more information about device selection and configuration, see the [Device Cloning Guide](device-cloning) and [Development Setup](development) documentation.
