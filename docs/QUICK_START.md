# 🚀 Quick Start Guide

[![PyPI version](https://badge.fury.io/py/pcileechfwgenerator.svg)](https://badge.fury.io/py/pcileechfwgenerator)
[![Python Support](https://img.shields.io/pypi/pyversions/pcileechfwgenerator.svg)](https://pypi.org/project/pcileechfwgenerator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Get up and running with PCILeech Firmware Generator in minutes.

---

## 📑 Table of Contents

- [🔧 Installation](#-installation)
  - [Option 1: pip Installation](#option-1-pip-installation-recommended)
  - [Option 2: From Source](#option-2-from-source)
- [🎯 First Run](#-first-run)
  - [1. System Setup](#1-system-setup)
  - [2. Hardware Setup](#2-hardware-setup)
  - [3. Generate Firmware](#3-generate-firmware)
- [📋 Common Workflows](#-common-workflows)
  - [Basic Firmware Generation](#basic-firmware-generation)
  - [Advanced Features](#advanced-features)
  - [PCI Configuration Validation](#pci-configuration-validation)
  - [Donor Dump Options](#donor-dump-options)
  - [Flashing DMA Board](#flashing-dma-board)
- [🐛 Troubleshooting](#-troubleshooting)
  - [Permission Issues](#permission-issues)
  - [TUI Not Starting](#tui-not-starting)
  - [Container Issues](#container-issues)
  - [Device Not Found](#device-not-found)
- [📚 Next Steps](#-next-steps)
- [🆘 Getting Help](#-getting-help)
- [⚠️ Important Notes](#️-important-notes)

---

## 🔧 Installation

### Option 1: pip Installation (Recommended)

```bash
# Install with TUI support
pip install pcileechfwgenerator[tui]

# Install sudo wrapper scripts (recommended)
./install-sudo-wrapper.sh

# Verify installation
pcileech-tui --help
```

### Option 2: From Source

```bash
git clone https://github.com/ramseymcgrath/PCILeechFWGenerator
cd PCILeechFWGenerator
pip install -e .[tui]
```

## 🎯 First Run

### 1. System Setup

```bash
# Install system dependencies (one-time setup)
sudo ./install.sh

# Re-login or run newgrp for Podman permissions
newgrp
```

### 2. Hardware Setup

1. **Insert donor PCIe card** into your Linux build system
2. **Boot Linux** and ensure the donor loads its vendor driver
3. **Connect DMA board** (optional, for direct flashing)

### 3. Generate Firmware

#### Interactive TUI (Recommended)

```bash
# Using the sudo wrapper (recommended)
pcileech-tui-sudo

# Or directly with sudo (may have module import issues)
sudo pcileech-tui
```

The TUI will guide you through:
- 🔍 **Device Discovery**: Automatically detect PCIe devices
- ⚙️ **Configuration**: Set board type and options
- 🏗️ **Build Process**: Monitor real-time progress
- 📦 **Output**: Get your firmware.bin file

#### Command Line

```bash
# Interactive device selection
sudo pcileech-generate

# Direct build (if you know the device BDF)
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t  # Using sudo wrapper
# OR
sudo pcileech-build --bdf 0000:03:00.0 --board 75t  # Direct sudo
```

## 📋 Common Workflows

### Basic Firmware Generation

```bash
# 1. Launch TUI
pcileech-tui-sudo  # Using sudo wrapper (recommended)

# 2. Select your donor device from the list
#    (Look for ✅ or ⚠️ indicators for suitable devices)
# 3. Choose board type (35t, 75t, 100t)
# 4. Click "Start Build"
# 5. Wait for completion
# 6. Find firmware in output/firmware.bin
```

### Device Suitability Indicators

In the TUI, devices are evaluated for firmware generation compatibility:

| Indicator | Meaning |
|-----------|---------|
| ✅ | **Suitable**: Device is compatible and not bound to a driver |
| ⚠️ | **Suitable with Warning**: Device is compatible but bound to a driver |
| ❌ | **Not Suitable**: Device is not compatible for firmware generation |

A device is considered suitable when its suitability score is ≥ 0.7 and it has no compatibility issues.

### Advanced Features

```bash
# Enable all advanced features (using sudo wrapper)
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t --advanced-sv

# Network device with behavior profiling
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t --advanced-sv \
  --device-type network --enable-behavior-profiling

# Custom profiling duration
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t \
  --enable-behavior-profiling --profile-duration 30.0
```

### PCI Configuration Validation

The firmware generator now includes a validation step that confirms PCI configuration values exist and match the donor card. This ensures that the generated firmware accurately represents the donor device's characteristics.

#### Validated PCI Configuration Values

The validation process checks for the following values:

**Critical Values (Required):**
- Device ID (0xXXXX): A 16-bit identifier unique to the device model
- Vendor ID (0xYYYY): A 16-bit identifier assigned to the manufacturer
- Subsystem ID (0xZZZZ): Identifies the specific subsystem or variant
- Subsystem Vendor ID (0xWWWW): Identifies the vendor of the subsystem
- Revision ID (0xRR): Indicates the hardware revision level of the device
- BAR Size: Size of the Base Address Register
- MPC: Max Payload Capable
- MPR: Max Read Request

**Extended Values (Recommended):**
- Class Code (0xCCCCCC): A 24-bit code that defines the primary function/type of device
- Extended Configuration Space: Full 4KB extended configuration space
- Enhanced Capabilities: Support for enhanced capabilities

**Optional Values:**
- Device Serial Number (DSN): A 64-bit unique identifier
- Power Management Capabilities: Power state information
- Advanced Error Reporting (AER) Capabilities: Error handling features
- Vendor-specific Capabilities: Custom vendor features

#### Validation Process

The validation occurs during the build process:
1. When using a donor card, values are extracted and validated automatically
2. When using a donor info file, values are validated against the file
3. When generating synthetic data, basic validation ensures proper format

If validation fails for critical values, the build will abort with an error message. For non-critical values, warnings will be displayed but the build will continue.

### Donor Dump Options

By default, the system performs local builds without using the donor_dump kernel module. You can use these options for alternative workflows:

```bash
# Opt-in to using the donor_dump kernel module
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t --use-donor-dump

# Save donor information to a file for future use
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t --donor-info-file /path/to/save/donor_info.json

# Use a previously saved donor information file (no donor device needed)
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t --donor-info-file /path/to/saved/donor_info.json

# Specify container engine (docker or podman)
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t --container-engine docker
```

In the TUI, you can:
1. Local builds are enabled by default in the Configuration panel
2. Optionally enable "Donor Dump" option if needed
3. Optionally specify a "Donor Info File" path
4. Select your preferred container engine (docker or podman)

### Flashing DMA Board

```bash
# Flash the generated firmware
usbloader -f output/firmware.bin

# For multiple boards, specify VID:PID
usbloader -f output/firmware.bin --vidpid 1d50:6130
```

## 🐛 Troubleshooting

### Permission Issues

```bash
# Add user to required groups
sudo usermod -a -G vfio $USER
sudo usermod -a -G dialout $USER

# Re-login or use newgrp
newgrp vfio
```

### TUI Not Starting

```bash
# Check TUI dependencies
python -c "import textual; print('TUI OK')"

# Install missing dependencies
pip install textual rich psutil watchdog
```

### Container Issues

```bash
# Check Podman
podman --version
podman info | grep rootless

# If issues, reinstall Podman
sudo ./install.sh
```

### Device Already Bound to vfio-pci

If a device is already bound to the vfio-pci driver, the firmware generator will now detect this and skip the binding process automatically. This is useful in scenarios where:

- You're running multiple builds for the same device
- Another tool has already bound the device to vfio-pci
- You manually bound the device to vfio-pci before running the generator

The system will display a message like:
```
[*] Device already bound to vfio-pci driver, skipping binding process...
```

No action is required on your part - the build will proceed normally.

### Device Not Found

```bash
# List PCIe devices
lspci -nn

# Check if device is bound to vfio-pci
lspci -k -s 0000:03:00.0

# Manually bind to vfio-pci if needed
echo "0000:03:00.0" | sudo tee /sys/bus/pci/drivers/vfio-pci/bind
```

## 📚 Next Steps

- **[TUI Documentation](TUI_README.md)**: Detailed TUI interface guide
- **[Advanced Features](../README.md#advanced-features)**: Power user features
- **[Contributing](../CONTRIBUTING.md)**: Help improve the project
- **[Troubleshooting](../README.md#troubleshooting)**: Detailed problem solving

## 🆘 Getting Help

- **GitHub Issues**: [Report problems](https://github.com/ramseymcgrath/PCILeechFWGenerator/issues)
- **Discussions**: [Ask questions](https://github.com/ramseymcgrath/PCILeechFWGenerator/discussions)
- **Documentation**: Check the docs/ directory

## ⚠️ Important Notes

- **Security**: Never build on the same system you'll use for attacks
- **Privacy**: Keep generated firmware private (contains donor identifiers)
- **Legal**: Use only for educational research and legitimate development
- **Hardware**: Donor card should be quarantined after extraction

---

**Happy firmware generating!** 🎉