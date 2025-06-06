# PCILeech Firmware Generator

[![PyPI version](https://badge.fury.io/py/pcileechfwgenerator.svg)](https://badge.fury.io/py/pcileechfwgenerator)
[![CI](https://github.com/ramseymcgrath/PCILeechFWGenerator/workflows/CI/badge.svg)](https://github.com/ramseymcgrath/PCILeechFWGenerator/actions)
[![codecov](https://codecov.io/gh/ramseymcgrath/PCILeechFWGenerator/branch/main/graph/badge.svg)](https://codecov.io/gh/ramseymcgrath/PCILeechFWGenerator)
![](https://dcbadge.limes.pink/api/shield/429866199833247744)

Generate spoofed PCIe DMA firmware from real donor hardware with a single command. The workflow rips the donor's configuration space, builds a personalized FPGA bit‑stream in an isolated container, and (optionally) flashes your DMA card over USB‑JTAG.

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
  - [Installation](#installation)
  - [Usage](#usage)
- [📋 Requirements](#-requirements)
  - [Software](#software)
  - [Hardware](#hardware)
- [🛠️ Installation & Setup](#️-installation--setup)
- [🎮 Usage](#-usage-1)
  - [Interactive TUI Mode](#interactive-tui-mode-recommended)
  - [Command Line Mode](#command-line-mode)
  - [Legacy Mode](#legacy-mode-source-installation)
- [🔌 Flashing the DMA Board](#-flashing-the-dma-board)
- [🚀 Advanced Features](#-advanced-features)
  - [Manufacturing Variance Simulation](#manufacturing-variance-simulation)
  - [Advanced SystemVerilog Generation](#advanced-systemverilog-generation)
  - [Behavioral Profiling](#behavioral-profiling)
  - [Command-Line Options](#command-line-options)
- [🧹 Cleanup & Safety](#-cleanup--safety)
- [⚠️ Disclaimer](#️-disclaimer)
- [📦 Development & Contributing](#-development--contributing)
  - [Building from Source](#building-from-source)
  - [Contributing](#contributing)
  - [Release Process](#release-process)
- [📚 Documentation](#-documentation)
- [🔧 Troubleshooting](#-troubleshooting)
- [🏆 Acknowledgments](#-acknowledgments)
- [📄 License](#-license)
- [⚠️ Legal Notice](#️-legal-notice)

---

## ✨ Features

- **🎯 Donor Hardware Analysis**: Extract real PCIe device configurations and register maps
- **📊 Behavioral Profiling**: Capture dynamic device behavior patterns for enhanced realism
- **🔧 Manufacturing Variance Simulation**: Add realistic timing jitter and parameter variations
- **⚡ Advanced SystemVerilog Generation**: Comprehensive PCIe device controller with modular architecture
- **🐳 Automated Build Pipeline**: Containerized synthesis and bit-stream generation
- **🔌 USB-JTAG Flashing**: Direct firmware deployment to DMA boards
- **🖥️ Interactive TUI**: Modern text-based interface with real-time monitoring and guided workflows
- **📦 Professional Packaging**: Easy installation via pip with proper dependency management

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install pcileechfwgenerator

# With TUI support (recommended)
pip install pcileechfwgenerator[tui]

# Development installation
pip install pcileechfwgenerator[dev]
```

### Usage

```bash
# Interactive TUI interface (recommended)
pcileech-tui

# Command line interface
pcileech-generate

# Direct build command
pcileech-build --bdf 0000:03:00.0 --board 75t
```

## 📋 Requirements

### Software

This is primarily tested in Linux, with some fiddling you could probably get it to work on Windows too.

| Tool | Why you need it | Install |
|------|----------------|---------|
| Vivado Studio | Synthesis & bit‑stream generation | Download from Xilinx (any 2022.2+ release) |
| Podman | Rootless container runtime for the build sandbox | See installation instructions below |
| Python ≥ 3.9 | Host‑side orchestrator ([`generate.py`](generate.py)) | Distro package (python3) |
| λConcept usbloader | USB flashing utility for Screamer‑class boards | See installation instructions below |
| pciutils, usbutils | lspci / lsusb helpers | Available in most Linux distributions |

> **⚠️ Security Notice**
> Never build firmware on the same operating system you plan to run the attack from. Use a separate Linux box or VM.

### Hardware

| Component | Notes |
|-----------|-------|
| Donor PCIe card | Any inexpensive NIC, sound, or capture card works. One donor → one firmware. Destroy or quarantine the donor after extraction. |
| DMA board | Supported Artix‑7 DMA boards (35T, 75T, 100T). Must expose the Screamer USB‑JTAG port. |

## 🛠️ Installation & Setup

### Method 1: pip Installation (Recommended)

```bash
# Install with TUI support
pip install pcileechfwgenerator[tui]

# Basic installation (CLI only)
pip install pcileechfwgenerator

# Development installation
git clone https://github.com/ramseymcgrath/PCILeechFWGenerator
cd PCILeechFWGenerator
pip install -e .[dev]
```

### Method 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/ramseymcgrath/PCILeechFWGenerator
cd PCILeechFWGenerator

# Install system dependencies
sudo ./install.sh

# Install Python dependencies
pip install -r requirements-tui.txt  # For TUI support
# OR
pip install -r requirements.txt      # Basic installation
```

Re‑login or run `newgrp` afterwards so rootless Podman picks up subuid/subgid mappings.

## 🎮 Usage

### Interactive TUI Mode (Recommended)

The modern text-based interface provides guided workflows and real-time monitoring:

```bash
# Launch TUI (after pip installation)
sudo pcileech-tui

# Or from source
sudo python3 tui_generate.py
```

**TUI Features:**
- 🖥️ **Visual device browser** with enhanced PCIe device information
- ⚙️ **Guided configuration** with validation and profile management
- 📊 **Real-time build monitoring** with progress tracking and resource usage
- 🔍 **Intelligent error guidance** with suggested fixes
- 📡 **System status monitoring** for Podman, Vivado, USB devices, and more

See [`docs/TUI_README.md`](docs/TUI_README.md) for detailed TUI documentation.

### Command Line Mode

For automated workflows or scripting:

```bash
# Basic generation (interactive device selection)
sudo pcileech-generate

# Direct build with specific device (uses donor_dump kernel module by default)
sudo pcileech-build --bdf 0000:03:00.0 --board 75t

# Build without using donor_dump kernel module (using synthetic data)
sudo pcileech-build --bdf 0000:03:00.0 --board 75t --skip-donor-dump

# Build using a previously saved donor information file
sudo pcileech-build --bdf 0000:03:00.0 --board 75t --donor-info-file /path/to/donor_info.json

# Advanced generation with enhanced features
sudo pcileech-build --bdf 0000:03:00.0 --board 75t --advanced-sv

# Device-specific generation with behavior profiling
sudo pcileech-build --bdf 0000:03:00.0 --board 75t --advanced-sv \
  --device-type network --enable-behavior-profiling

# Selective feature control
sudo pcileech-build --bdf 0000:03:00.0 --board 75t --advanced-sv \
  --disable-power-management --disable-performance-counters
```

**Note:** The system will automatically build the required container image (`dma-fw`) if it doesn't exist. This happens during the first run and requires an internet connection to download base images.

**Output:** `output/firmware.bin` (FPGA bit‑stream ready for flashing).

### Legacy Mode (Source Installation)

```bash
# Traditional workflow (still supported)
sudo python3 generate.py
```

## 🔌 Flashing the DMA Board

> **Note:** These steps can run on the same machine or a different PC.

1. Power down, install the DMA card, and remove the donor.

2. Connect the USB‑JTAG port.

3. Flash:

```bash
usbloader -f output/firmware.bin      # auto‑detects Screamer VID:PID 1d50:6130
```

If multiple λConcept boards are attached, add `--vidpid <vid:pid>`.

## 🚀 Advanced Features

### Manufacturing Variance Simulation

The Manufacturing Variance Simulation feature adds realistic hardware variations to make generated firmware more authentic and harder to detect. This feature models real-world manufacturing tolerances and environmental conditions.

**Key Capabilities:**
- **Device Class Support**: Consumer, Enterprise, Industrial, and Automotive grade components with appropriate variance characteristics
- **Timing Variations**: Clock jitter, register access timing, and propagation delays
- **Environmental Modeling**: Temperature drift, power supply noise, and process variations
- **Integration**: Seamlessly integrates with behavior profiling for enhanced realism

**Device Classes:**
- `CONSUMER`: Standard consumer-grade tolerances (2-5% clock jitter)
- `ENTERPRISE`: Tighter enterprise-grade specifications (1-3% variations)
- `INDUSTRIAL`: Extended temperature and reliability ranges
- `AUTOMOTIVE`: Automotive-grade specifications with enhanced stability

**Usage:**
```bash
# Enable manufacturing variance (automatically applied with --advanced-sv)
python3 src/build.py --bdf 0000:03:00.0 --board 75t --advanced-sv
```

### Advanced SystemVerilog Generation

The Advanced SystemVerilog Generation feature provides a comprehensive, modular PCIe device controller with enterprise-grade capabilities and optimizations.

**Architecture Components:**
- **Modular Design**: Specialized components for power, error handling, and performance monitoring
- **Multiple Clock Domains**: Proper clock domain crossing with variance-aware timing
- **Device-Specific Logic**: Optimizations for Network, Storage, Graphics, and Audio devices
- **Comprehensive Integration**: All components work together seamlessly

**Power Management Features:**
- **PCIe Power States**: Full D0, D1, D2, D3hot, D3cold state support
- **ASPM (Active State Power Management)**: L0s, L1, L1.1, L1.2 link states
- **Dynamic Power Scaling**: Frequency and voltage scaling based on workload
- **Wake-on-LAN/Event**: Configurable wake event handling

**Error Handling & Recovery:**
- **Comprehensive Error Detection**: Correctable and uncorrectable error handling
- **Advanced Error Reporting (AER)**: Full PCIe AER implementation
- **Recovery Mechanisms**: Automatic error recovery and link retraining
- **Error Logging**: Detailed error tracking and reporting

**Performance Monitoring:**
- **Hardware Counters**: Transaction, bandwidth, and latency monitoring
- **Device-Specific Metrics**: Tailored counters for different device types
- **Real-time Monitoring**: Live performance data collection
- **Threshold-based Alerts**: Configurable performance thresholds

**Device-Specific Optimizations:**
- **Network Devices**: Multi-queue support, interrupt coalescing, checksum offload
- **Storage Devices**: Command queuing, wear leveling, power loss protection
- **Graphics Devices**: Memory bandwidth optimization, display timing
- **Audio Devices**: Low-latency processing, sample rate conversion

**Usage Examples:**
```bash
# Enable all advanced features
python3 src/build.py --bdf 0000:03:00.0 --board 75t --advanced-sv

# Network device with specific optimizations
python3 src/build.py --bdf 0000:03:00.0 --board 75t --advanced-sv --device-type network

# Disable specific features for minimal implementation
python3 src/build.py --bdf 0000:03:00.0 --board 75t --advanced-sv \
  --disable-power-management --disable-error-handling

# Storage device with performance monitoring
python3 src/build.py --bdf 0000:03:00.0 --board 75t --advanced-sv \
  --device-type storage --enable-behavior-profiling
```

### Behavioral Profiling

Dynamic behavior profiling captures real device operation patterns to enhance firmware realism by monitoring and analyzing how the donor device behaves during normal operation.

**Capabilities:**
- **Real-time Monitoring**: Captures live device register access patterns and timing
- **Pattern Analysis**: Identifies behavioral signatures, timing characteristics, and state transitions
- **Manufacturing Variance Integration**: Combines with variance simulation for enhanced realism
- **SystemVerilog Enhancement**: Automatically integrates behavioral data into generated code
- **Configurable Duration**: Adjustable profiling periods (default: 30 seconds)

**Key Benefits:**
- **Enhanced Realism**: Generated firmware mimics actual device behavior patterns
- **Improved Timing Accuracy**: Precise register access timing based on real-world measurements
- **Optimized Performance**: Device-specific optimizations based on observed behavior
- **Reduced Detection Risk**: More authentic behavioral signatures

**Usage:**
```bash
# Enable behavior profiling with custom duration
python3 src/build.py --bdf 0000:03:00.0 --board 75t \
  --enable-behavior-profiling --profile-duration 30.0

# Enable profiling with device-specific optimizations
python3 src/build.py --bdf 0000:03:00.0 --board 75t --advanced-sv \
  --device-type network --enable-behavior-profiling
```

### Command-Line Options

**Core Options:**
- `--bdf`: PCIe Bus:Device.Function identifier (required)
- `--board`: Target board type (35t, 75t, 100t) (required)

**Donor Device Options:**
- `--skip-donor-dump`: Skip using the donor_dump kernel module (opt-in, not default)
- `--donor-info-file`: Path to a JSON file containing donor information from a previous run

**Advanced Features:**
- `--advanced-sv`: Enable advanced SystemVerilog generation
- `--device-type`: Specify device type (generic, network, storage, graphics, audio)
- `--enable-behavior-profiling`: Enable dynamic behavior profiling
- `--profile-duration`: Profiling duration in seconds (default: 30.0)

**Feature Control:**
- `--disable-power-management`: Disable power management features
- `--disable-error-handling`: Disable error handling features
- `--disable-performance-counters`: Disable performance monitoring

**Analysis & Debugging:**
- `--save-analysis`: Save detailed analysis to specified file
- `--verbose`: Enable verbose output
- `--enhanced-timing`: Enable enhanced timing models (default: enabled)

## 🧹 Cleanup & Safety

- Rebind the donor back to its original driver if you keep it around.
- Keep the generated firmware private; it contains identifiers from the donor.
- Advanced features require appropriate privileges for hardware access.

## ⚠️ Disclaimer

This tool is intended for educational research and legitimate PCIe development purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors assume no liability for misuse of this software.

## 📦 Development & Contributing

For development setup instructions, please see [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

### Building from Source

```bash
# Build distributions
python -m build

# Install locally
pip install dist/*.whl

# Test installation
pcileech-generate --help
```

### Contributing

We welcome contributions! Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed guidelines.

**Quick Start:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Release Process

For maintainers releasing new versions:

```bash
# Automated release (recommended)
python scripts/release.py minor --release-notes "Add new TUI features and improvements"

# Manual release
python -m build
twine upload dist/*
```

## 📚 Documentation

- **[TUI Documentation](docs/TUI_README.md)**: Detailed TUI interface guide
- **[TUI Design Document](docs/TUI_Design_Document.md)**: Technical architecture
- **[Contributing Guide](CONTRIBUTING.md)**: Development and contribution guidelines
- **[Changelog](CHANGELOG.md)**: Version history and release notes
- **[API Reference](https://pcileechfwgenerator.readthedocs.io/)**: Complete API documentation

## 🔧 Troubleshooting

### Common Issues

**Installation Problems:**
```bash
# If pip installation fails
pip install --upgrade pip setuptools wheel
pip install pcileechfwgenerator[tui]

# For development installation issues
pip install -e .[dev]
```

**TUI Not Starting:**
```bash
# Check TUI dependencies
python -c "import textual; print('TUI dependencies OK')"

# Install TUI dependencies manually
pip install textual rich psutil watchdog
```

**Permission Issues:**
```bash
# Ensure proper permissions for PCIe operations
sudo usermod -a -G vfio $USER
sudo usermod -a -G dialout $USER  # For USB-JTAG access
```

**Container Issues:**
```bash
# Check Podman installation
podman --version

# Verify rootless setup
podman info | grep rootless

# Test container build and dependencies
./scripts/build_container.sh --test

# Manual container dependency check
podman run --rm pcileechfwgenerator:latest python3 -c "import psutil, pydantic; print('Dependencies OK')"

# Check container file structure
podman run --rm pcileechfwgenerator:latest ls -la /app/src/

# Test with specific capabilities (recommended)
podman run --rm --cap-add=SYS_RAWIO --cap-add=SYS_ADMIN pcileechfwgenerator:latest echo "Capability test passed"
```

**Container Security Best Practices:**
- Use specific capabilities (`--cap-add=SYS_RAWIO --cap-add=SYS_ADMIN`) instead of `--privileged` when possible
- Always mount output directories to preserve generated files: `-v ./output:/app/output`
- The container runs as non-root user `appuser` by default for security
- Use the build script for automated testing: `./scripts/build_container.sh --test`

### Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/ramseymcgrath/PCILeechFWGenerator/issues)
- **GitHub Discussions**: [Community support and questions](https://github.com/ramseymcgrath/PCILeechFWGenerator/discussions)
- **Documentation**: Check the docs/ directory for detailed guides

## 🏆 Acknowledgments

- **λConcept**: For the excellent usbloader utility and Screamer hardware
- **Xilinx/AMD**: For Vivado synthesis tools
- **Textual**: For the modern TUI framework
- **PCILeech Community**: For feedback and contributions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Notice

This tool is intended for educational research and legitimate PCIe development purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors assume no liability for misuse of this software.

**Security Considerations:**
- Never build firmware on systems used for production or sensitive operations
- Use isolated build environments (VMs or dedicated hardware)
- Keep generated firmware private and secure
- Follow responsible disclosure practices for any security research

---

**Version 0.1.6** - Major release with TUI interface and professional packaging
For educational research and legitimate PCIe development only. Misuse may violate laws and void warranties. The authors assume no liability.
