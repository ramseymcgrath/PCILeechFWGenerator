# 📊 Behavior Profiling

[![PyPI version](https://badge.fury.io/py/pcileech-fw-generator.svg)](https://badge.fury.io/py/pcileech-fw-generator)
[![Python Support](https://img.shields.io/pypi/pyversions/pcileech-fw-generator.svg)](https://pypi.org/project/pcileech-fw-generator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This document provides detailed information about the behavior profiling feature in PCILeech Firmware Generator.

---

## 📑 Table of Contents

- [🔍 Overview](#-overview)
- [✨ What Behavior Profiling Does](#-what-behavior-profiling-does)
- [🎯 Benefits](#-benefits)
- [🚀 How to Enable Behavior Profiling](#-how-to-enable-behavior-profiling)
- [⚙️ Configuration Options](#️-configuration-options)
- [🔄 How Profiling Enhances SystemVerilog Generation](#-how-profiling-enhances-systemverilog-generation)
- [📋 Requirements and Limitations](#-requirements-and-limitations)
- [🔌 Integration with Other Features](#-integration-with-other-features)
- [🔧 Troubleshooting](#-troubleshooting)
- [🧪 Advanced Usage](#-advanced-usage)
- [🔬 Technical Details](#-technical-details)
- [⚠️ Disclaimer](#️-disclaimer)

---

## 🔍 Overview

Behavior profiling is an advanced feature that captures and analyzes the dynamic behavior patterns of donor PCIe devices during normal operation. By monitoring register access patterns, timing characteristics, state transitions, and interrupt behavior, the profiler creates a comprehensive behavioral signature that can be integrated into the generated SystemVerilog code.

## ✨ What Behavior Profiling Does

The behavior profiler performs several key functions:

1. **Real-time Monitoring**: Captures live device register access patterns using kernel tracing facilities
2. **Timing Analysis**: Measures precise timing between register accesses and identifies periodic patterns
3. **State Transition Mapping**: Identifies sequences of register accesses that represent state changes
4. **Interrupt Pattern Analysis**: Captures and analyzes interrupt-related behavior
5. **Manufacturing Variance Integration**: Combines behavioral data with manufacturing variance simulation
6. **SystemVerilog Enhancement**: Automatically integrates behavioral data into generated code

## 🎯 Benefits

Enabling behavior profiling provides several significant benefits:

- **Enhanced Realism**: Generated firmware mimics actual device behavior patterns
- **Improved Timing Accuracy**: More precise register access timing based on real-world measurements
- **Optimized Performance**: Device-specific optimizations based on observed behavior
- **Reduced Detection Risk**: More authentic behavioral signatures that match real hardware
- **Intelligent Recommendations**: Automatic suggestions for optimizing the generated firmware

## 🚀 How to Enable Behavior Profiling

### Command Line Interface

To enable behavior profiling via the command line:

```bash
# Basic usage
pcileech-build --bdf 0000:03:00.0 --board 75t --enable-behavior-profiling

# With custom duration
pcileech-build --bdf 0000:03:00.0 --board 75t --enable-behavior-profiling --profile-duration 60.0

# With advanced SystemVerilog and device-specific optimizations
pcileech-build --bdf 0000:03:00.0 --board 75t --advanced-sv --device-type network --enable-behavior-profiling
```

### TUI Interface

To enable behavior profiling in the TUI:

1. Select a device in the Device Selection Panel
2. Open the Configuration Panel
3. Enable the "Behavior Profiling" option
4. Adjust "Profile Duration" if needed (default: 30.0 seconds)
5. Start the build process

During the build, a dedicated "Behavior Profiling" stage will appear in the progress panel, showing real-time status of the profiling process.

## ⚙️ Configuration Options

The behavior profiler supports the following configuration options:

| Option | Description | Default |
|--------|-------------|---------|
| `--enable-behavior-profiling` | Enable the behavior profiling feature | Disabled |
| `--profile-duration` | Duration of profiling in seconds | 30.0 |
| `--device-type` | Optimize profiling for specific device types (network, storage, graphics, audio) | generic |
| `--disable-ftrace` | Disable ftrace monitoring (useful for CI environments or non-root usage) | Disabled |

## 🔄 How Profiling Enhances SystemVerilog Generation

The behavior profiler enhances the generated SystemVerilog in several ways:

1. **Timing-Accurate Register Access**: Register access timing in the generated code matches the observed patterns from the real device
2. **State Machine Replication**: State transitions observed during profiling are replicated in the generated state machines
3. **Interrupt Behavior Modeling**: Interrupt patterns are accurately modeled based on observed behavior
4. **Device-Specific Optimizations**: The code generator applies optimizations based on the device type and observed behavior
5. **Variance Integration**: Behavioral data is combined with manufacturing variance simulation for enhanced realism

### Example: Register Enhancement

When behavior profiling is enabled, register definitions are enhanced with behavioral metadata:

```json
{
  "offset": 0x400,
  "name": "control",
  "value": "0x00000000",
  "rw": "rw",
  "context": {
    "function": "device_control",
    "timing": "runtime",
    "access_pattern": "balanced",
    "behavioral_timing": {
      "avg_interval_us": 100.0,
      "std_deviation_us": 5.0,
      "frequency_hz": 10000.0,
      "confidence": 0.95
    }
  }
}
```

This behavioral metadata is then used by the SystemVerilog generator to create more realistic register access patterns.

## 📋 Requirements and Limitations

### Requirements

- **Root/sudo access**: Required for kernel tracing facilities
- **Linux kernel with ftrace support**: For register access monitoring
- **Active donor device**: The device must be bound to its driver and operational
- **Sufficient profiling duration**: Longer durations provide more accurate profiles

### Limitations

- **Limited visibility**: Some device behaviors may not be visible through standard monitoring interfaces
- **Driver dependency**: Profiling effectiveness depends on driver activity during the profiling period
- **Resource intensive**: Profiling adds additional time to the build process
- **Kernel version dependency**: Some advanced profiling features require newer kernel versions

## 🔌 Integration with Other Features

Behavior profiling works seamlessly with other PCILeech Firmware Generator features:

- **Manufacturing Variance Simulation**: Behavioral data is used to enhance variance models
- **Advanced SystemVerilog Generation**: Profiling data improves the realism of generated code
- **Device-Specific Optimizations**: Profiling enhances device-type specific optimizations

## 🔧 Troubleshooting

### Common Issues

1. **No behavioral data captured**
   - Ensure the device is bound to its driver and active
   - Increase profiling duration
   - Try generating device activity (e.g., network traffic for NICs)

2. **Permission errors**
   - Ensure you're running with root/sudo privileges
   - Check that debugfs and tracefs are mounted
   - Use `--disable-ftrace` option if running in CI environments or without root access

3. **Profiling takes too long**
   - Reduce profiling duration
   - Use a more focused device type setting

### Logs and Debugging

Behavior profiling logs are included in the standard build logs. Look for entries with the `[BehaviorProfiler]` prefix for detailed information about the profiling process.

## 🧪 Advanced Usage

### Saving and Loading Profiles

You can save behavior profiles for later use:

```bash
# Save profile to file
pcileech-build --bdf 0000:03:00.0 --enable-behavior-profiling --save-profile my_device_profile.json

# Load profile from file
pcileech-build --bdf 0000:03:00.0 --load-profile my_device_profile.json
```

### Custom Analysis

For advanced users, the behavior profiler can output detailed analysis data:

```bash
pcileech-build --bdf 0000:03:00.0 --enable-behavior-profiling --save-analysis analysis.json

# Run without ftrace monitoring (no root required)
pcileech-build --bdf 0000:03:00.0 --enable-behavior-profiling --disable-ftrace
```

## 🔬 Technical Details

The behavior profiler uses multiple monitoring techniques:

1. **ftrace**: Kernel function tracing for PCI config space accesses (requires root privileges, can be disabled)
2. **sysfs**: Monitoring device state changes via sysfs
3. **debugfs**: Device register monitoring via debugfs if available

The collected data is analyzed to identify:

- Periodic access patterns
- Register access frequencies
- Read/write ratios
- State transition sequences
- Interrupt patterns
- Timing characteristics

This analysis is then used to enhance the SystemVerilog generation process with realistic behavioral patterns.

## ⚠️ Disclaimer

This tool is intended for educational research and legitimate PCIe development purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors assume no liability for misuse of this software.

---

**Version 0.2.0** - Major release with TUI interface and professional packaging