# 📝 Changelog

[![PyPI version](https://badge.fury.io/py/pcileech-fw-generator.svg)](https://badge.fury.io/py/pcileech-fw-generator)
[![Python Support](https://img.shields.io/pypi/pyversions/pcileech-fw-generator.svg)](https://pypi.org/project/pcileech-fw-generator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

All notable changes to the PCILeech Firmware Generator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v0.1.2.html).

---

## 📑 Table of Contents

- [Version 0.1.9 (2025-01-02)](#200---2025-01-02)
- [Release Notes](#release-notes)
- [Backward Compatibility](#backward-compatibility)
- [Future Roadmap](#future-roadmap)

---

## [Unreleased] - Container Flow Improvements

### 🔧 Fixed
- **🔌 VFIO Device Binding**: Fixed an issue where binding a device already bound to vfio-pci would fail
  - Added detection for devices already bound to vfio-pci
  - Improved error handling during the binding process
  - Added comprehensive test cases for this edge case
- **� Container Dependency Installation**: Fixed missing Python dependencies in container build
  - Added proper `pip install` commands for `requirements.txt` and `requirements-tui.txt`
  - Fixed import errors for `psutil`, `pydantic`, and other required packages
- **📁 Container File Structure**: Corrected file paths and directory structure
  - Fixed `build.py` path from `/app/build.py` to `/app/src/build.py`
  - Updated all container usage examples and documentation
- **🔒 Container Security Improvements**: Enhanced security posture
  - Replaced `--privileged` with specific capabilities (`--cap-add=SYS_RAWIO --cap-add=SYS_ADMIN`)
  - Maintained non-root user execution while preserving functionality
- **✅ Container Health Checks**: Improved dependency validation
  - Enhanced health check to validate Python imports
  - Added comprehensive dependency testing

### ✨ Added
- **🔨 Container Build Script**: New automated build and test script
  - Added `scripts/build_container.sh` with comprehensive testing
  - Supports both Podman and Docker container engines
  - Includes security validation and usage examples
- **🚀 Container CI Pipeline**: Automated container testing workflow
  - Added `.github/workflows/container-ci.yml` for continuous integration
  - Tests container build, dependencies, security, and integration
  - Validates file structure and user permissions

### 📚 Improved
- **📖 Documentation Updates**: Enhanced container usage documentation
  - Updated `podman_demo.md` with security best practices
  - Added troubleshooting section for container issues
  - Included capability-based security examples

### 🗂️ Changed
- **📦 Container File Inclusion**: Updated `.dockerignore` configuration
  - Removed exclusion of `src/tui/` components
  - Included necessary requirements files
  - Optimized build context for better performance

---

## [0.1.9] - 2025-01-02

### ✨ Added
- **🖥️ Interactive TUI Interface**: Complete text-based user interface with real-time monitoring
  - Visual PCIe device browser with enhanced device information
  - Guided configuration workflows with validation
  - Real-time build monitoring with progress tracking
  - System status monitoring for Podman, Vivado, USB devices
  - Intelligent error guidance with suggested fixes
  - Profile management for build configurations
- **📦 Enhanced Package Structure**: Professional Python packaging with pip installability
  - Console script entry points (`pcileech-generate`, `pcileech-tui`, `pcileech-build`)
  - Proper package metadata and dependency management
  - Optional TUI dependencies for lightweight installations
- **⚡ Advanced SystemVerilog Features**: Comprehensive PCIe device controller improvements
  - Modular architecture with enhanced power management
  - Performance counters and monitoring capabilities
  - Error handling and recovery mechanisms
  - Manufacturing variance simulation for realistic behavior
- **📊 Behavioral Profiling**: Dynamic device behavior capture and simulation
  - Real-time register access pattern analysis
  - Timing characteristic profiling
  - Device-specific behavior modeling
- **🧪 Quality Assurance**: Comprehensive testing and code quality tools
  - Unit and integration test suites
  - Code formatting with Black and isort
  - Type checking with mypy
  - Pre-commit hooks for development workflow
- **🐳 Container Improvements**: Enhanced containerized build environment
  - Updated Containerfile with TUI support
  - Improved resource management and monitoring
  - Better error handling and logging

### 🔄 Changed
- **🔢 Major Version Bump**: Incremented to v0.1.2 to reflect significant TUI addition
- **📚 Improved Documentation**: Enhanced README with TUI features and installation instructions
- **🐛 Better Error Handling**: More informative error messages and recovery suggestions
- **📋 Enhanced Logging**: Improved logging throughout the application with structured output

### 🔧 Technical Details
- **📦 Dependencies**: Added Textual, Rich, Watchdog for TUI functionality
- **🐍 Python Support**: Requires Python 3.9+ with support through 3.12
- **📂 Package Structure**: Reorganized as proper Python package with setuptools/pip support
- **⌨️ Entry Points**: Added console scripts for easy command-line access
- **🧪 Testing**: Comprehensive test suite with pytest and coverage reporting

### 🚀 Installation
```bash
# Basic installation
pip install pcileech-fw-generator

# With TUI support
pip install pcileech-fw-generator[tui]

# Development installation
pip install pcileech-fw-generator[dev]
```

### 🎮 Usage
```bash
# Command line interface (traditional)
pcileech-generate

# Interactive TUI interface (new)
pcileech-tui

# Direct build command
pcileech-build --bdf 0000:03:00.0 --board 75t
```

## [1.0.0] - 2024-12-01

### ✨ Added
- Initial release of PCILeech Firmware Generator
- Basic command-line interface for firmware generation
- Donor hardware analysis and configuration extraction
- Containerized build pipeline with Vivado integration
- USB-JTAG flashing support for DMA boards
- Basic SystemVerilog generation for PCIe devices
- Podman-based isolated build environment

### 🎯 Features
- PCIe device enumeration and selection
- Configuration space extraction from donor hardware
- FPGA bitstream generation for Artix-7 boards
- Automated driver binding and VFIO operations
- Basic logging and error handling

---

## 📋 Release Notes

### 🚀 v0.1.2 Highlights

This major release introduces a modern, interactive TUI that transforms the user experience while maintaining full backward compatibility with the original command-line interface. The TUI provides guided workflows, real-time monitoring, and intelligent error handling that makes firmware generation more accessible and reliable.

Key improvements include:
- **🎯 Zero Learning Curve**: Intuitive interface guides users through the entire process
- **📊 Real-time Feedback**: Live monitoring of build progress and system resources
- **🛡️ Error Prevention**: Validation and checks prevent common configuration mistakes
- **📦 Professional Packaging**: Easy installation via pip with proper dependency management

### 🔄 Backward Compatibility

All existing command-line workflows continue to work unchanged. The TUI is an optional enhancement that requires additional dependencies, ensuring lightweight installations remain possible.

### 🔮 Future Roadmap

- Web-based interface for remote build management
- Enhanced device compatibility and detection
- Advanced firmware customization options
- Integration with additional FPGA toolchains
- Cloud-based build services

## ⚠️ Disclaimer

This tool is intended for educational research and legitimate PCIe development purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors assume no liability for misuse of this software.

---

**Version 0.1.9** - Major release with TUI interface and professional packaging