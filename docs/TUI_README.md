# 🖥️ PCILeech Firmware Generator TUI

[![PyPI version](https://badge.fury.io/py/pcileechfwgenerator.svg)](https://badge.fury.io/py/pcileechfwgenerator)
[![Python Support](https://img.shields.io/pypi/pyversions/pcileechfwgenerator.svg)](https://pypi.org/project/pcileechfwgenerator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Text User Interface (TUI) for the PCILeech firmware generation workflow, built with the Textual framework.

---

## 📑 Table of Contents

- [🔍 Overview](#-overview)
- [🚀 Installation](#-installation)
  - [Prerequisites](#prerequisites)
  - [Install TUI Dependencies](#install-tui-dependencies)
- [🎮 Usage](#-usage)
  - [Launch TUI Mode](#launch-tui-mode)
  - [TUI Interface Overview](#tui-interface-overview)
- [✨ Features](#-features)
  - [Device Management](#device-management)
  - [Configuration Management](#configuration-management)
  - [Build Monitoring](#build-monitoring)
  - [System Integration](#system-integration)
- [⚙️ Configuration Profiles](#️-configuration-profiles)
  - [Profile Locations](#profile-locations)
  - [Default Profiles](#default-profiles)
  - [Creating Custom Profiles](#creating-custom-profiles)
- [⌨️ Keyboard Shortcuts](#️-keyboard-shortcuts)
- [🔧 Error Handling](#-error-handling)
  - [Common Errors and Solutions](#common-errors-and-solutions)
- [🚀 Advanced Features](#-advanced-features)
  - [Behavior Profiling](#behavior-profiling)
  - [System Status Monitoring](#system-status-monitoring)
  - [Build Process Integration](#build-process-integration)
  - [Configuration Validation](#configuration-validation)
- [🐛 Troubleshooting](#-troubleshooting)
  - [TUI Won't Start](#tui-wont-start)
  - [Device Detection Issues](#device-detection-issues)
  - [Build Failures](#build-failures)
- [🛠️ Development](#️-development)
  - [Architecture](#architecture)
  - [Key Components](#key-components)
  - [Extending the TUI](#extending-the-tui)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [⚠️ Disclaimer](#️-disclaimer)

---

## 🔍 Overview

The TUI provides an interactive, user-friendly interface that addresses the key pain points of the command-line workflow:

- **Enhanced Device Discovery**: Visual PCIe device browser with detailed information
- **Guided Configuration**: Intuitive configuration wizard with validation
- **Real-time Build Monitoring**: Live progress tracking with resource usage
- **Error Guidance**: Intelligent error analysis with suggested fixes
- **Profile Management**: Save and load configuration profiles

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- Root/sudo access (required for device binding)
- Podman container runtime
- PCILeech firmware generation environment

### Install TUI Dependencies

```bash
# Install TUI-specific dependencies
pip install -r requirements-tui.txt

# Or install individual packages
pip install textual rich psutil watchdog pydantic
```

## 🎮 Usage

### Launch TUI Mode

There are several ways to launch the TUI:

```bash
# Method 1: Using the dedicated TUI script
python3 tui_generate.py

# Method 2: Using the --tui flag with generate.py
sudo python3 generate.py --tui

# Method 3: Direct execution
sudo python3 -m src.tui.main
```

### TUI Interface Overview

The TUI is organized into several panels:

#### 1. Device Selection Panel (Top Left)
- Lists all detected PCIe devices
- Shows device status, BDF address, name, driver, and IOMMU group
- Provides device suitability indicators
- Refresh and details buttons

#### 2. Configuration Panel (Top Right)
- Displays current build configuration
- Shows board type, device type, and enabled features
- Configure, load profile, and save profile buttons

#### 3. Build Progress Panel (Middle)
- Real-time build progress with stage tracking
- Resource usage monitoring (CPU, memory, disk)
- Build control buttons (start, pause, stop)
- Log viewing capability

#### 4. System Status Panel (Bottom Left)
- Podman availability and status
- Vivado detection and version
- USB device count
- Disk space information
- Root access status

#### 5. Quick Actions Panel (Bottom Right)
- Device scanning
- Output directory access
- Build report viewing
- Advanced settings
- Documentation links

## ✨ Features

### Device Management

- **Auto-discovery**: Automatically scans and lists PCIe devices
- **Enhanced Information**: Shows vendor names, driver status, IOMMU groups
- **Suitability Assessment**: Rates devices for firmware generation compatibility
- **Driver Status**: Indicates if devices are bound to drivers

### Configuration Management

- **Profile System**: Save and load configuration profiles
- **Default Profiles**: Pre-configured profiles for common scenarios:
  - Network Device Standard
  - Storage Device Optimized
  - Quick Development
  - Full Featured
- **Validation**: Real-time configuration validation with error messages

### Build Monitoring

- **Stage Tracking**: Visual progress through 6 build stages:
  1. Environment Validation
  2. Device Analysis
  3. Register Extraction
  4. SystemVerilog Generation
  5. Vivado Synthesis
  6. Bitstream Generation
- **Resource Monitoring**: Real-time CPU, memory, and disk usage
- **Error Detection**: Automatic error detection with guided recovery

### System Integration

- **Backward Compatibility**: Maintains all existing CLI functionality
- **Container Integration**: Seamless integration with Podman containers
- **Log Management**: Integrated log viewing and analysis
- **USB Device Support**: Automatic USB device detection for flashing

## ⚙️ Configuration Profiles

### Profile Locations

Profiles are stored in `~/.pcileech/profiles/` as JSON files.

### Default Profiles

#### Network Device Standard
```json
{
  "name": "Network Device Standard",
  "board_type": "75t",
  "device_type": "network",
  "advanced_sv": true,
  "enable_variance": true,
  "behavior_profiling": true,
  "profile_duration": 30.0,
  "donor_dump": true
}
```

#### Quick Development
```json
{
  "name": "Quick Development",
  "board_type": "35t",
  "device_type": "generic",
  "advanced_sv": false,
  "enable_variance": false,
  "flash_after_build": true,
  "donor_dump": true
}
```

#### Local Build
```json
{
  "name": "Local Build",
  "board_type": "75t",
  "device_type": "generic",
  "advanced_sv": true,
  "enable_variance": true,
  "donor_dump": false,
  "local_build": true,
  "donor_info_file": "~/.pcileech/donor_info.json"
}
```

### Creating Custom Profiles

1. Configure settings in the TUI
2. Click "Save Profile"
3. Enter a profile name
4. Profile is saved to `~/.pcileech/profiles/`

## ⌨️ Keyboard Shortcuts

- `Ctrl+C`: Exit application
- `Tab`: Navigate between panels
- `Enter`: Activate selected button/item
- `Space`: Toggle checkboxes
- `↑/↓`: Navigate lists and tables
- `F1`: Help (if implemented)

## 🔧 Error Handling

The TUI provides intelligent error analysis and guidance:

### Common Errors and Solutions

#### VFIO Binding Failed
- **Cause**: IOMMU not enabled or vfio-pci module not loaded
- **Solutions**:
  - Enable IOMMU in BIOS
  - Load vfio-pci module: `modprobe vfio-pci`
  - Unbind current driver first

#### Container Image Not Found
- **Cause**: DMA firmware container not built
- **Solutions**:
  - The container is now automatically built when needed
  - If automatic build fails, manually build with: `podman build -t dma-fw .`
  - Check Podman installation and internet connectivity

#### Insufficient Permissions
- **Cause**: Not running with root privileges
- **Solutions**:
  - Run with sudo: `sudo python3 tui_generate.py`
  - Add user to required groups

## 🚀 Advanced Features

### Donor Device Configuration

The TUI provides options for configuring how donor device information is obtained:

- **Default Mode**: By default, the system builds and uses the donor_dump kernel module to extract real device information from the selected PCIe device. This provides the most accurate firmware generation.

- **Local Build Mode**: When enabled, this mode skips using the donor_dump kernel module and instead uses either:
  - A previously saved donor information file (specified via the "Donor Info File" option)
  - Synthetic donor information generated based on the selected device type

**Configuration Options:**
- **Donor Dump**: Enable/disable using the donor_dump kernel module (enabled by default)
- **Local Build**: Enable to use a donor info file or synthetic data instead of a real device
- **Donor Info File**: Path to a JSON file containing donor information from a previous run

**Benefits of Local Build Mode:**
- **No Kernel Module**: Useful in environments where building kernel modules is restricted
- **No Physical Device**: Generate firmware without requiring the donor device to be present
- **Reproducible Builds**: Use the same donor information across multiple builds

**Usage:**
1. Select a device in the Device Selection Panel
2. Open the Configuration Panel
3. To use the default mode (recommended), ensure "Donor Dump" is enabled
4. To use Local Build mode:
   - Enable "Local Build" option
   - Disable "Donor Dump" option
   - Optionally specify a "Donor Info File" path
5. Start the build process

![TUI Configuration Panel](../docs/images/tui_config_panel.png)

### Behavior Profiling

The TUI provides a seamless interface for enabling and configuring behavior profiling:

- **Enable/Disable**: Toggle behavior profiling in the configuration panel
- **Duration Control**: Set custom profiling duration (in seconds)
- **Real-time Monitoring**: Track profiling progress in the build progress panel
- **Profile Integration**: Automatically integrates profiling data into the build process

**Configuration Options:**
- **Behavior Profiling**: Enable/disable the profiling feature
- **Profile Duration**: Set the duration for capturing device behavior (default: 30.0 seconds)
- **Device Type**: Select specific device type for optimized profiling

**Benefits:**
- **Enhanced Realism**: Generated firmware mimics actual device behavior patterns
- **Improved Timing**: More accurate register access timing based on real measurements
- **Optimized Performance**: Device-specific optimizations based on observed behavior

**Usage:**
1. Select a device in the Device Selection Panel
2. Open the Configuration Panel
3. Enable "Behavior Profiling" option
4. Adjust "Profile Duration" if needed
5. Start the build process

During the build, a dedicated "Behavior Profiling" stage will appear in the progress panel, showing real-time status of the profiling process.

### System Status Monitoring

The TUI continuously monitors:
- Podman service status
- Vivado installation and version
- Available USB devices
- System resources (CPU, memory, disk)
- VFIO support status

### Build Process Integration

- **Container Orchestration**: Manages Podman container lifecycle
- **Progress Parsing**: Parses build output for progress indicators
- **Resource Tracking**: Monitors system resource usage during builds
- **Log Analysis**: Analyzes build logs for errors and warnings

### Configuration Validation

- **Real-time Validation**: Validates configuration as you type
- **Compatibility Checks**: Warns about incompatible settings
- **Resource Requirements**: Estimates resource requirements

## 🐛 Troubleshooting

### TUI Won't Start

1. **Check Dependencies**:
   ```bash
   pip install -r requirements-tui.txt
   ```

2. **Check Python Version**:
   ```bash
   python3 --version  # Should be 3.8+
   ```

3. **Check Terminal Compatibility**:
   - Ensure terminal supports ANSI colors
   - Try different terminal emulator

### Device Detection Issues

1. **Run as Root**:
   ```bash
   sudo python3 tui_generate.py
   ```

2. **Check lspci**:
   ```bash
   lspci -Dnn
   ```

3. **Verify IOMMU**:
   ```bash
   dmesg | grep -i iommu
   ```

### Build Failures

1. **Check Container Image**:
   ```bash
   podman images | grep dma-fw
   ```

2. **Verify Device Binding**:
   ```bash
   ls -la /dev/vfio/
   ```

3. **Check Logs**:
   - Use "View Logs" button in TUI
   - Check `generate.log` file

## 🛠️ Development

### Architecture

The TUI follows a modular architecture:

```
src/tui/
├── main.py              # Main application
├── models/              # Data models
├── core/                # Business logic services
├── widgets/             # Custom UI widgets
├── screens/             # Screen components
└── styles/              # CSS styling
```

### Key Components

- **DeviceManager**: PCIe device discovery and management
- **ConfigManager**: Configuration and profile management
- **BuildOrchestrator**: Build process orchestration
- **StatusMonitor**: System status monitoring

### Extending the TUI

1. **Add New Widgets**: Create custom widgets in `src/tui/widgets/`
2. **Add New Screens**: Create screen components in `src/tui/screens/`
3. **Extend Models**: Add new data models in `src/tui/models/`
4. **Add Services**: Create new services in `src/tui/core/`

## 🤝 Contributing

1. Follow the existing code structure
2. Add type hints to all functions
3. Include docstrings for public methods
4. Test with various PCIe devices
5. Ensure backward compatibility

## 📄 License

Same as the main PCILeech project.

## ⚠️ Disclaimer

This tool is intended for educational research and legitimate PCIe development purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors assume no liability for misuse of this software.

---

**Version 2.0.0** - Major release with TUI interface and professional packaging