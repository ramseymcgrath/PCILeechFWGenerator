# PCILeech Firmware Generator

[![CI](https://github.com/ramseymcgrath/PCILeechFWGenerator/workflows/CI/badge.svg)](https://github.com/ramseymcgrath/PCILeechFWGenerator/actions)
[![codecov](https://codecov.io/gh/ramseymcgrath/PCILeechFWGenerator/branch/main/graph/badge.svg)](https://codecov.io/gh/ramseymcgrath/PCILeechFWGenerator)
![](https://dcbadge.limes.pink/api/shield/429866199833247744)

Generate authentic PCIe DMA firmware from real donor hardware with a single command. This tool extracts donor configurations from a local device and generates unique PCILeech FPGA bitstreams (and optionally flashes a DMA card over USB-JTAG).

> [!WARNING]
> This tool requires *real* hardware. The templates are built using the device identifiers directly from a donor card and placeholder values are explicitly avoided. Using your own donor device ensures your firmware will be unique.

## ✨ Key Features

- **Donor Hardware Analysis**: Extract real PCIe device configurations and register maps
- **Full 4KB Config-Space Shadow**: Complete configuration space emulation with overlay RAM
- **MSI-X Table Replication**: Exact replication of MSI-X tables from donor devices
- **Deterministic Variance Seeding**: Consistent hardware variance based on device serial number
- **Advanced SystemVerilog Generation**: Comprehensive PCIe device controller with modular architecture
- **Interactive TUI**: Modern text-based interface with real-time monitoring and guided workflows
- **Automated Build Pipeline**: Containerized synthesis and bitstream generation
- **USB-JTAG Flashing**: Direct firmware deployment to DMA boards

📚 **[Complete Documentation](../../wiki)** | 🏗️ **[Device Cloning Guide](../../wiki/device-cloning)** | 🔧 **[Development Setup](../../wiki/development)**

## 🚀 Quick Start

### Installation

```bash
# Install with TUI support (recommended)
pip install pcileechfwgenerator[tui]

# Install sudo wrapper scripts for easier usage
wget https://raw.githubusercontent.com/ramseymcgrath/PCILeechFWGenerator/refs/heads/main/install-sudo-wrapper.sh
./install-sudo-wrapper.sh

# Load required kernel modules
sudo modprobe vfio vfio-pci
```

### Requirements

- **Podman** (_not Docker_ - required for proper PCIe device mounting)
- **Vivado Studio** (2022.2+ for synthesis and bitstream generation)
- **Python ≥ 3.9**
- **Donor PCIe card** (any inexpensive NIC, sound, or capture card)
- **DMA board** (pcileech_75t484_x1, pcileech_35t325_x4, or pcileech_100t484_x1)

### Basic Usage

```bash
# Interactive TUI (recommended for first-time users)
pcileech-tui-sudo

# CLI interface
pcileech-generate build

# Development from repository
git clone https://github.com/ramseymcgrath/PCILeechFWGenerator.git
cd PCILeechFWGenerator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
sudo -E python3 generate.py
```

### Flashing Firmware

```bash
# Flash to DMA board
pcileech-generate flash output/firmware.bin --board pcileech_75t484_x1

# Or use usbloader directly
usbloader -f output/firmware.bin

```

## 🔧 Troubleshooting

### VFIO Setup Issues

> [!WARNING]
> Avoid using on-board devices (audio, graphics cards) for donor info. The VFIO process can lock the bus during extraction and cause system reboots.


The most common issues involve VFIO (Virtual Function I/O) configuration. Use the built-in diagnostic tool:

```bash
# Check VFIO setup and device compatibility
./vfio_setup_checker.py

# Check a specific device
./vfio_setup_checker.py 0000:03:00.0

# Interactive mode with guided fixes
./vfio_setup_checker.py --interactive

# Generate automated fix script
./vfio_setup_checker.py --generate-script
```

### Common VFIO Problems

**1. IOMMU not enabled in BIOS/UEFI**
```bash
# Enable VT-d (Intel) or AMD-Vi (AMD) in BIOS settings
# Then add to /etc/default/grub GRUB_CMDLINE_LINUX:
# For Intel: intel_iommu=on
# For AMD: amd_iommu=on
sudo update-grub && sudo reboot
```

**2. VFIO modules not loaded**
```bash
sudo modprobe vfio vfio_pci vfio_iommu_type1
```

**3. Device not in IOMMU group**
```bash
# Check IOMMU groups
find /sys/kernel/iommu_groups/ -name '*' -type l | grep YOUR_DEVICE_BDF
```

**4. Permission issues**
```bash
# Add user to required groups
sudo usermod -a -G vfio $USER
sudo usermod -a -G dialout $USER  # For USB-JTAG access
```

### Installation Issues

```bash
# If pip installation fails
pip install --upgrade pip setuptools wheel
pip install pcileechfwgenerator[tui]

# For TUI dependencies
pip install textual rich psutil watchdog

# Container issues
podman --version
podman info | grep rootless
```

### Templating issues

If you run into issues with your vivado project file formatting, first clear out all your cached files and rerun. Otherwise try pulling a copy of the pcileech repo directly and then inserting the generator output in. 

## 📚 Documentation

For detailed information, please visit our **[Wiki](../../wiki)**:

- **[Device Cloning Process](../../wiki/device-cloning)** - Complete guide to the cloning workflow
- **[Firmware Uniqueness](../../wiki/firmware-uniqueness)** - How authenticity is achieved
- **[Manual Donor Dump](../../wiki/manual-donor-dump)** - Step-by-step manual extraction
- **[Development Setup](../../wiki/development)** - Contributing and development guide
- **[TUI Documentation](docs/TUI_README.md)** - Interactive interface guide

## 🧹 Cleanup & Safety

- **Rebind donors**: Use TUI/CLI to rebind donor devices to original drivers
- **Keep firmware private**: Generated firmware contains real device identifiers
- **Use isolated build environments**: Never build on production systems
- **Container cleanup**: `podman rmi pcileechfwgenerator:latest`

> [!IMPORTANT]
> This tool is intended for educational research and legitimate PCIe development purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors assume no liability for misuse of this software.

## 🏆 Acknowledgments

- **Xilinx/AMD**: For Vivado synthesis tools
- **Textual**: For the modern TUI framework
- **PCILeech Community**: For feedback and contributions

## 📄 License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Notice

*AGAIN* This tool is intended for educational research and legitimate PCIe development purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors assume no liability for misuse of this software.

**Security Considerations:**

- Never build firmware on systems used for production or sensitive operations
- Use isolated build environments (Seperate dedicated hardware)
- Keep generated firmware private and secure
- Follow responsible disclosure practices for any security research
- Use the SECURITY.md template to raise security concerns

---
