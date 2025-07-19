## Firmware Authenticity & Stability

_"If the OS can't tell the difference, you win."_

## Table of Contents
- [Overview](#overview)
- [Deep-Cloned Device Anatomy](#deep-cloned-device-anatomy)
- [Build-Time Security Features](#build-time-security-features)
- [Detection-Resistance Validation](#detection-resistance-validation)
- [Immutable Core Architecture](#immutable-core-architecture)
- [Performance Metrics](#performance-metrics)
- [Security & Research Applications](#security--research-applications)
- [Troubleshooting & Error Handling](#troubleshooting--error-handling)
- [Best Practices](#best-practices)
- [Legal & Ethical Considerations](#legal--ethical-considerations)

---

## Overview

The PCILeech firmware generator creates authentic hardware clones by performing byte-perfect replication of donor device characteristics while maintaining a stable, reusable core architecture. The result is hardware that appears identical to the original device from the host OS perspective while providing consistent, predictable behavior across builds.

### Key Benefits
- **Perfect Stealth**: Identical PCIe fingerprints to donor hardware
- **Build Consistency**: Same core IP across all generated firmware
- **Research Flexibility**: Safe testing environment for security research
- **Driver Compatibility**: Native vendor driver support without modifications

---

## Deep-Cloned Device Anatomy

The cloning process replicates critical hardware characteristics across multiple layers:

| Layer | Cloned Components | Security Impact | Implementation Notes |
|-------|------------------|-----------------|---------------------|
| **PCIe Config Space** | 256-byte header + Extended Capabilities (PM, MSI/MSI-X, PCIe, VSEC) | Driver whitelisting, BIOS compatibility | Missing capabilities trigger Code 10 errors |
| **BAR & Memory Map** | BAR0-BAR5 sizes, flags, alignment, prefetch settings | Fingerprint resistance | BAR entropy analysis defeated |
| **Interrupt Topology** | MSI/MSI-X tables, indices, masks, PBA configuration | IRQ behavior matching | BRAM-mirrored for consistency |
| **Link Behavior** | L0s/L1 timings, Max_Read_Request, advanced PCIe features | Advanced fingerprinting | ASPM, OBFF, Hot-plug states |
| **Power & Error Handling** | ASPM policies, PME support, D-states, AER masks | Enterprise compliance | Byte-perfect POST auditing |

### Configuration Space Layout
```
Offset 0x00-0xFF: Standard PCIe Header (256 bytes)
├── 0x00-0x3F: Type 0/1 Configuration Header
├── 0x40-0xFF: Capability Structures
└── 0x100+:    Extended Capability Structures

Extended Capabilities Chain:
├── Power Management (PM)
├── Message Signaled Interrupts (MSI/MSI-X)  
├── PCIe Capability Structure
├── Vendor Specific Extended Capability (VSEC)
└── Advanced Error Reporting (AER)
```

---

## Build-Time Security Features

### Entropy Generation
- **Unique Bitstreams**: SHA-256 hash of donor configuration salted into unused BRAM
- **Forensic Tracking**: Vivado version and build timestamp embedded in hidden VSEC
- **P&R Randomization**: IO placement randomized within timing constraints
- **Anti-Analysis**: Defeats simple bitstream diffing and pattern recognition

### Implementation Details
```verilog
// Example: Build-time entropy injection
localparam [255:0] BUILD_ENTROPY = 256'h{SHA256_HASH};
localparam [63:0]  BUILD_TIMESTAMP = 64'h{UNIX_TIMESTAMP};

// Hidden in unused VSEC register space
assign vsec_entropy_reg = BUILD_ENTROPY[31:0];
assign vsec_timestamp_reg = BUILD_TIMESTAMP[31:0];
```

---

## Detection-Resistance Validation

### Automated Testing Matrix

| Test Category | Tool/Method | Expected Behavior | Failure Indicators |
|---------------|-------------|-------------------|-------------------|
| **Basic Enumeration** | [`lspci -vvv`](https://linux.die.net/man/8/lspci), [`pcieutils`](https://github.com/billfarrow/pcieutils) | Identical vendor/device IDs, capability offsets | Mismatched PCI IDs, capability gaps |
| **Driver Loading** | Windows Device Manager, Linux modprobe | Native vendor driver loads without warnings | Code 10 errors, unsigned driver prompts |
| **Stress Testing** | MSI flood tests, hot-reset cycles | Stable operation under load | System hangs, IRQ storms |
| **Security Scanning** | Anti-tamper suites (Falcon, Ranger) | No anomaly alerts | Link state mismatches, timing deviations |
| **Power Management** | ASPM state transitions, D-state cycling | Identical power behavior to donor | PME assertion failures, ASPM violations |

### Validation Scripts
```bash
#!/bin/bash
# Basic validation suite
echo "=== PCIe Device Validation ==="

# Check PCI configuration space
lspci -s $DEVICE_BDF -vvv > current_config.txt
diff -u donor_config.txt current_config.txt

# Verify driver loading
if lsmod | grep -q $EXPECTED_DRIVER; then
    echo "✓ Driver loaded successfully"
else
    echo "✗ Driver loading failed"
fi

# Test MSI-X functionality  
echo "Testing interrupt handling..."
./test_msix_vectors $DEVICE_BDF
```

---

## Immutable Core Architecture

The firmware maintains a stable core while adapting the peripheral interface:

```
┌─────────────────────────────────────────┐
│           Donor-Specific Shell          │ ← Cloned: IDs, BARs, MSI-X
├─────────────────────────────────────────┤
│              Stable Core IP             │ ← Consistent across builds
│  ┌─────────────────────────────────────┐ │
│  │        AXI-PCIe Bridge              │ │ ← Single timing closure
│  │  • TLP packet processing           │ │
│  │  • Configuration space handler     │ │
│  │  • Completion timeout logic        │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │        DMA Scatter-Gather           │ │ ← Shared test benches
│  │  • Descriptor ring management      │ │
│  │  • Memory protection checks        │ │
│  │  • Bandwidth throttling            │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │      Debug & Monitoring             │ │ ← Identical CSR map
│  │  • UART/JTAG interfaces            │ │
│  │  • Performance counters            │ │
│  │  • ECC status registers            │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Core IP Benefits
- **Timing Closure**: Single PLL domain, pre-verified timing constraints
- **Test Coverage**: Shared test benches across all device variants
- **Debug Consistency**: Identical register map for all builds
- **Maintenance**: Core updates propagate to all device types

---

## Performance Metrics

### Resource Utilization

| Metric | Artix-7 35T | Artix-7 75T | Artix-7 100T | Variation | Notes |
|--------|-------------|-------------|--------------|-----------|-------|
| **Fmax** | 150 MHz | 165 MHz | 175 MHz | ±5% | Single PLL domain |
| **LUT Utilization** | 85% | 45% | 35% | ±3% donor variance | BAR decode depth only |
| **BRAM Usage** | 44 × 36Kb | 44 × 36Kb | 44 × 36Kb | Fixed | MSI-X tables + buffers |
| **DSP Slices** | 12 | 12 | 12 | Fixed | DMA checksum engines |
| **Static Power** | 180mW | 200mW | 220mW | ±20mW | Temperature dependent |

### Timing Analysis
```tcl
# Critical path constraints
create_clock -period 6.667 -name pcie_clk [get_ports pcie_clk_p]
set_input_delay -clock pcie_clk -max 2.0 [get_ports pcie_rx_p]
set_output_delay -clock pcie_clk -max 2.0 [get_ports pcie_tx_p]

# Cross-clock domain constraints
set_clock_groups -asynchronous -group [get_clocks pcie_clk] -group [get_clocks user_clk]
```

---

## Security & Research Applications

### Use Case Matrix

| Role | Application | Implementation | Risk Mitigation |
|------|-------------|----------------|-----------------|
| **Red Team** | Hardware implants, DMA attacks | Covert data exfiltration via cloned capture cards | Air-gapped testing, legal authorization |
| **Blue Team** | SIEM tuning, anomaly detection | Generate realistic traffic without production risk | Isolated lab networks, controlled scenarios |
| **Academia** | PCIe security research | TLP poisoning, IOMMU bypass studies | Ethical review, responsible disclosure |
| **Tool Vendors** | Legacy hardware validation | Driver testing against discontinued hardware | Licensing compliance, IP protection |
| **Forensics** | Evidence preservation | Bit-perfect hardware replication for analysis | Chain of custody, legal admissibility |

### Research Scenarios
```python
# Example: DMA attack simulation
class DMAAttackSimulator:
    def __init__(self, target_device):
        self.device = target_device
        self.memory_map = self.scan_physical_memory()
    
    def extract_credentials(self):
        """Simulate credential extraction via DMA"""
        for region in self.memory_map:
            if self.contains_sensitive_data(region):
                yield self.extract_region(region)
    
    def inject_payload(self, payload):
        """Simulate code injection via DMA writes"""
        target_addr = self.find_executable_region()
        return self.device.dma_write(target_addr, payload)
```

---

## Troubleshooting & Error Handling

### Common Issues & Solutions

#### Build-Time Errors
| Error | Cause | Solution | Prevention |
|-------|-------|----------|-----------|
| **Timing Closure Failure** | Complex donor BAR decode logic | Reduce Fmax target, pipeline critical paths | Pre-validate donor complexity |
| **Resource Overflow** | Large MSI-X tables on small FPGAs | Use external memory for tables | Check resource requirements early |
| **P&R Failure** | IO pin conflicts | Adjust pin assignments, use different package | Validate pinout before synthesis |

#### Runtime Issues
| Symptom | Likely Cause | Diagnostic Steps | Fix |
|---------|--------------|------------------|-----|
| **Code 10 Error** | Missing/incorrect capabilities | Compare [`lspci`](https://linux.die.net/man/8/lspci) output with donor | Update capability chain |
| **IRQ Storm** | MSI-X table corruption | Check interrupt vectors with [`/proc/interrupts`](https://www.kernel.org/doc/Documentation/filesystems/proc.txt) | Rebuild MSI-X configuration |
| **DMA Timeout** | Incorrect BAR mapping | Verify memory regions with [`/proc/iomem`](https://www.kernel.org/doc/Documentation/filesystems/proc.txt) | Fix BAR size/alignment |
| **Link Training Failure** | PCIe electrical issues | Check link status with [`setpci`](https://linux.die.net/man/8/setpci) | Verify signal integrity |

### Debug Infrastructure
```verilog
// Integrated debug features
module debug_controller (
    input wire clk,
    input wire rst_n,
    
    // Debug interfaces
    output wire [31:0] debug_status,
    output wire [63:0] error_counters,
    input wire [31:0] debug_control,
    
    // UART debug output
    output wire uart_tx,
    input wire uart_rx
);

// Performance monitoring
always @(posedge clk) begin
    if (!rst_n) begin
        pcie_tlp_count <= 0;
        dma_transfer_count <= 0;
        error_count <= 0;
    end else begin
        if (tlp_valid) pcie_tlp_count <= pcie_tlp_count + 1;
        if (dma_done) dma_transfer_count <= dma_transfer_count + 1;
        if (error_detected) error_count <= error_count + 1;
    end
end
```

### Diagnostic Tools
```bash
#!/bin/bash
# Comprehensive diagnostic script

echo "=== PCILeech Firmware Diagnostics ==="

# Check PCIe link status
DEVICE_BDF="01:00.0"  # Update with actual BDF
LINK_STATUS=$(setpci -s $DEVICE_BDF CAP_EXP+12.w)
echo "Link Status: 0x$LINK_STATUS"

# Monitor interrupt activity
echo "Interrupt activity:"
grep $DEVICE_BDF /proc/interrupts

# Check DMA coherency
echo "Testing DMA coherency..."
./dma_coherency_test $DEVICE_BDF

# Validate configuration space
echo "Configuration space validation:"
./validate_config_space.py $DEVICE_BDF donor_config.json
```

---

## Best Practices

### Development Workflow
1. **Donor Analysis**: Thoroughly characterize donor device before cloning
2. **Incremental Testing**: Validate each capability block individually
3. **Regression Testing**: Maintain test suite for all supported donors
4. **Version Control**: Tag bitstreams with donor fingerprints
5. **Documentation**: Maintain detailed build logs and test results

### Security Considerations
- **Isolation**: Test in air-gapped environments
- **Backup**: Always preserve original donor firmware
- **Validation**: Verify cloned behavior matches donor exactly
- **Monitoring**: Log all device interactions for analysis
- **Updates**: Regularly update against new detection methods

### Code Quality
```python
# Example: Robust configuration validation
class ConfigSpaceValidator:
    def __init__(self, donor_config, generated_config):
        self.donor = donor_config
        self.generated = generated_config
        self.errors = []
    
    def validate(self):
        """Comprehensive configuration validation"""
        self._validate_header()
        self._validate_capabilities()
        self._validate_bars()
        self._validate_msix()
        
        if self.errors:
            raise ValidationError(f"Validation failed: {self.errors}")
        
        return True
    
    def _validate_header(self):
        """Validate standard PCIe header"""
        critical_fields = ['vendor_id', 'device_id', 'class_code', 'revision']
        for field in critical_fields:
            if self.donor[field] != self.generated[field]:
                self.errors.append(f"Header mismatch: {field}")
```

---

## Legal & Ethical Considerations

### ⚠️ Critical Warnings

| Risk Category | Concern | Mitigation |
|---------------|---------|------------|
| **Legal Compliance** | Hardware impersonation may violate local laws | Consult legal counsel, obtain proper authorization |
| **Network Security** | Unauthorized device deployment | Use only in authorized test environments |
| **Intellectual Property** | Donor firmware may be copyrighted | Respect vendor IP rights, fair use only |
| **Safety** | Malformed firmware can damage hardware | Maintain serial console access, backup procedures |

### Responsible Use Guidelines
- **Authorization**: Obtain explicit permission before deploying on any network
- **Disclosure**: Follow responsible disclosure for security vulnerabilities
- **Documentation**: Maintain detailed logs of all testing activities
- **Isolation**: Use dedicated test hardware and networks
- **Backup**: Always preserve original firmware before modifications

### Emergency Procedures
```bash
#!/bin/bash
# Emergency recovery procedures

echo "=== Emergency Recovery ==="

# Restore original firmware
if [ -f "donor_backup.bin" ]; then
    echo "Restoring donor firmware..."
    flashrom -p internal -w donor_backup.bin
fi

# Reset PCIe subsystem
echo "Resetting PCIe..."
echo 1 > /sys/bus/pci/devices/$DEVICE_BDF/remove
echo 1 > /sys/bus/pci/rescan

# Check system stability
dmesg | tail -20
```

---

## Conclusion

The PCILeech firmware generator provides a robust foundation for security research and hardware analysis through authentic device cloning. By maintaining perfect external compatibility while ensuring internal consistency, it enables safe, reproducible testing scenarios that would be impossible with original hardware.

**Key Takeaways:**
- Byte-perfect cloning ensures undetectable operation
- Immutable core architecture provides build consistency  
- Comprehensive validation prevents deployment issues
- Responsible use requires proper authorization and safety measures

*Remember: With great power comes great responsibility. Use these capabilities ethically and legally.*

---

**Related Documentation:**
- [Configuration Space Shadow](config-space-shadow.md) - Deep dive into PCIe configuration cloning
- [Manual Donor Dump](manual-donor-dump.md) - Step-by-step donor analysis procedures
- [Development Guide](development.md) - Build system and development workflow
