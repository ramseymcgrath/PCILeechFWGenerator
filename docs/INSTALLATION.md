# 🛠️ Installation Guide

[![PyPI version](https://badge.fury.io/py/pcileech-fw-generator.svg)](https://badge.fury.io/py/pcileech-fw-generator)
[![Python Support](https://img.shields.io/pypi/pyversions/pcileech-fw-generator.svg)](https://pypi.org/project/pcileech-fw-generator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Complete installation instructions for PCILeech Firmware Generator v0.1.2.

---

## 📑 Table of Contents

- [📋 System Requirements](#-system-requirements)
  - [Operating System](#operating-system)
  - [Software Dependencies](#software-dependencies)
  - [Hardware Requirements](#hardware-requirements)
- [🚀 Installation Methods](#-installation-methods)
  - [Method 1: pip Installation](#method-1-pip-installation-recommended)
  - [Method 2: From Source](#method-2-from-source)
  - [Method 3: Container Installation](#method-3-container-installation)
- [🛠️ System Setup](#️-system-setup)
  - [1. Install System Dependencies](#1-install-system-dependencies)
  - [2. Configure VFIO](#2-configure-vfio)
  - [3. Install Vivado](#3-install-vivado-required-for-synthesis)
  - [4. Configure Podman](#4-configure-podman-rootless)
- [🔧 Installation Verification](#-installation-verification)
  - [Basic Verification](#basic-verification)
  - [TUI Verification](#tui-verification)
  - [Container Verification](#container-verification)
  - [Hardware Verification](#hardware-verification)
- [🐛 Troubleshooting](#-troubleshooting)
  - [Common Issues](#common-issues)
  - [Getting Help](#getting-help)
- [🔄 Updating](#-updating)
  - [pip Installation](#pip-installation)
  - [Source Installation](#source-installation)
  - [Container Installation](#container-installation)
- [🗑️ Uninstallation](#️-uninstallation)
  - [pip Installation](#pip-installation-1)
  - [Source Installation](#source-installation-1)
  - [System Cleanup](#system-cleanup)
- [⚠️ Disclaimer](#️-disclaimer)

---

## 📋 System Requirements

### Operating System
- **Linux** (Ubuntu 20.04+, Debian 11+, CentOS 8+, or equivalent)
- **Architecture**: x86_64 (AMD64)
- **Kernel**: 4.15+ with VFIO support

### Software Dependencies
- **Python**: 3.9 or higher
- **Podman**: 4.0+ (rootless container runtime)
- **Vivado**: 2022.2+ (for FPGA synthesis)
- **Git**: For source installation

### Hardware Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space for builds
- **PCIe Slots**: Available slots for donor and DMA cards
- **USB**: For DMA board programming (USB-JTAG)

## 🚀 Installation Methods

### Method 1: pip Installation (Recommended)

The easiest way to install PCILeech Firmware Generator:

```bash
# Basic installation
pip install pcileech-fw-generator

# With TUI support (recommended)
pip install pcileech-fw-generator[tui]

# With all development tools
pip install pcileech-fw-generator[dev]

# Verify installation
pcileech-generate --help
pcileech-tui --help
```

### Method 2: From Source

For development or latest features:

```bash
# Clone repository
git clone https://github.com/ramseymcgrath/PCILeechFWGenerator
cd PCILeechFWGenerator

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[tui,dev]

# Verify installation
python -c "import src; print(f'Version: {src.__version__}')"
```

### Method 3: Container Installation

Using the pre-built container:

```bash
# Pull container
podman pull ghcr.io/ramseymcgrath/pcileechfwgenerator:latest

# Run container
podman run -it --privileged \
  -v /dev:/dev \
  -v $(pwd)/output:/app/output \
  ghcr.io/ramseymcgrath/pcileechfwgenerator:latest

# You can also use Docker instead of Podman
docker pull ghcr.io/ramseymcgrath/pcileechfwgenerator:latest
docker run -it --privileged \
  -v /dev:/dev \
  -v $(pwd)/output:/app/output \
  ghcr.io/ramseymcgrath/pcileechfwgenerator:latest
```

## 🛠️ System Setup

### 1. Install System Dependencies

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install required packages
sudo apt install -y \
  python3 python3-pip python3-venv \
  git curl wget \
  pciutils usbutils \
  build-essential \
  linux-headers-$(uname -r)

# Install Podman
sudo apt install -y podman

# Configure subuid/subgid for rootless Podman
echo "$USER:100000:65536" | sudo tee -a /etc/subuid
echo "$USER:100000:65536" | sudo tee -a /etc/subgid
```

#### CentOS/RHEL/Fedora

```bash
# Install required packages
sudo dnf install -y \
  python3 python3-pip \
  git curl wget \
  pciutils usbutils \
  gcc gcc-c++ make \
  kernel-devel

# Install Podman
sudo dnf install -y podman

# Configure subuid/subgid
echo "$USER:100000:65536" | sudo tee -a /etc/subuid
echo "$USER:100000:65536" | sudo tee -a /etc/subgid
```

### 2. Configure VFIO

Enable VFIO for PCIe device access:

```bash
# Load VFIO modules
sudo modprobe vfio-pci

# Make persistent
echo "vfio-pci" | sudo tee -a /etc/modules-load.d/vfio.conf

# Add user to vfio group
sudo usermod -a -G vfio $USER

# For USB-JTAG access
sudo usermod -a -G dialout $USER
```

### 3. Install Vivado (Required for Synthesis)

1. **Download Vivado** from Xilinx/AMD website
2. **Install** following vendor instructions
3. **Add to PATH**:
   ```bash
   echo 'export PATH="/tools/Xilinx/Vivado/2022.2/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```
4. **Verify installation**:
   ```bash
   vivado -version
   ```

### 4. Configure Container Engine (Rootless)

By default, the PCILeech Firmware Generator uses local builds, but you can also use container builds with either Podman (default) or Docker.

#### Podman Setup

```bash
# Re-login to pick up group changes
newgrp vfio

# Test rootless Podman
podman info | grep rootless

# Configure registries (if needed)
mkdir -p ~/.config/containers
cat > ~/.config/containers/registries.conf << EOF
[registries.search]
registries = ['docker.io', 'quay.io', 'ghcr.io']
EOF
```

#### Docker Setup

```bash
# Add user to docker group
sudo usermod -a -G docker $USER

# Re-login to pick up group changes
newgrp docker

# Test Docker
docker info
```

## 🔧 Installation Verification

### Basic Verification

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check pip installation
pip list | grep pcileech-fw-generator

# Test console scripts
pcileech-generate --help
pcileech-tui --help
pcileech-build --help
```

### TUI Verification

```bash
# Test TUI dependencies
python3 -c "
import textual
import rich
import psutil
import watchdog
print('All TUI dependencies available')
"

# Test TUI import
python3 -c "
from src.tui.main import PCILeechTUI
print('TUI import successful')
"
```

### Container Verification

```bash
# Test Podman
podman --version
podman info | grep rootless

# Test Docker (if installed)
docker --version
docker info

# Test container build
podman build -t pcileech-test .
# OR
docker build -t pcileech-test .
```

### Hardware Verification

```bash
# List PCIe devices
lspci -nn

# Check VFIO availability
ls /dev/vfio/

# Check USB devices (for DMA boards)
lsusb | grep -i concept
```

## 🐛 Troubleshooting

### Common Issues

#### Permission Denied Errors

```bash
# Check group membership
groups $USER

# Re-login or use newgrp
newgrp vfio
newgrp dialout

# Verify VFIO permissions
ls -la /dev/vfio/
```

#### TUI Dependencies Missing

```bash
# Install TUI dependencies manually
pip install textual rich psutil watchdog pydantic

# Or reinstall with TUI support
pip install --force-reinstall pcileech-fw-generator[tui]
```

#### Container Issues

```bash
# Podman: Check rootless setup
podman info | grep -E "(rootless|subuid|subgid)"

# Reset Podman if needed
podman system reset

# Reinstall Podman if necessary
sudo apt remove podman
sudo apt install podman

# Docker: Check setup
docker info

# Reset Docker if needed
docker system prune -a

# Specify container engine when building
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t --container-engine docker
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t --container-engine podman
```

#### VFIO Not Working

```bash
# Check IOMMU support
dmesg | grep -i iommu

# Enable IOMMU in GRUB (if needed)
sudo nano /etc/default/grub
# Add: GRUB_CMDLINE_LINUX="intel_iommu=on" (Intel)
# Or:  GRUB_CMDLINE_LINUX="amd_iommu=on"  (AMD)
sudo update-grub
sudo reboot
```

#### Vivado Not Found

```bash
# Check PATH
echo $PATH | grep -i vivado

# Add to PATH manually
export PATH="/tools/Xilinx/Vivado/2022.2/bin:$PATH"

# Make permanent
echo 'export PATH="/tools/Xilinx/Vivado/2022.2/bin:$PATH"' >> ~/.bashrc
```

### Getting Help

If you encounter issues:

1. **Check logs**: Look in `generate.log` for detailed error messages
2. **GitHub Issues**: [Report bugs](https://github.com/ramseymcgrath/PCILeechFWGenerator/issues)
3. **Discussions**: [Ask questions](https://github.com/ramseymcgrath/PCILeechFWGenerator/discussions)
4. **Documentation**: Check other docs in this directory

## 🔄 Updating

### pip Installation

```bash
# Update to latest version
pip install --upgrade pcileech-fw-generator[tui]

# Check version
python -c "import src; print(src.__version__)"
```

### Source Installation

```bash
# Pull latest changes
git pull origin main

# Reinstall
pip install -e .[tui,dev]
```

### Container Installation

```bash
# Pull latest container with Podman
podman pull ghcr.io/ramseymcgrath/pcileechfwgenerator:latest

# Or with Docker
docker pull ghcr.io/ramseymcgrath/pcileechfwgenerator:latest
```

## 🗑️ Uninstallation

### pip Installation

```bash
# Uninstall package
pip uninstall pcileech-fw-generator

# Clean up dependencies (optional)
pip autoremove
```

### Source Installation

```bash
# Remove from pip
pip uninstall pcileech-fw-generator

# Remove source directory
rm -rf PCILeechFWGenerator
```

### System Cleanup

```bash
# Remove user from groups (optional)
sudo deluser $USER vfio
sudo deluser $USER dialout

# Remove VFIO configuration (optional)
sudo rm /etc/modules-load.d/vfio.conf
```

## ⚠️ Disclaimer

This tool is intended for educational research and legitimate PCIe development purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors assume no liability for misuse of this software.

---

**Installation complete!** 🎉 

Next steps:
- Read the [Quick Start Guide](QUICK_START.md)
- Try the [TUI interface](TUI_README.md)
- Check the [main README](../README.md) for usage examples