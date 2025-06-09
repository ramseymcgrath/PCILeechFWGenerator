# 📝 Changelog

[![PyPI version](https://badge.fury.io/py/pcileech-fw-generator.svg)](https://badge.fury.io/py/pcileech-fw-generator)
[![Python Support](https://img.shields.io/pypi/pyversions/pcileech-fw-generator.svg)](https://pypi.org/project/pcileech-fw-generator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

All notable changes to the PCILeech Firmware Generator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v0.1.2.html).

---

## 📑 Table of Contents

- [Version 0.2.0 (2025-06-09)](#020---2025-06-09)
- [Version 0.2.0 (2025-01-02)](#0110---2025-01-02)
- [Release Notes](#release-notes)
- [Backward Compatibility](#backward-compatibility)
- [Future Roadmap](#future-roadmap)

---

## [0.2.0] - 2025-06-10

### ✨ Added
- **🧩 Feature Integration**: Comprehensive integration of all major features
  - Integrated documentation in `docs/INTEGRATED_FEATURES.md`
  - Comprehensive integration tests in `tests/test_feature_integration.py`
  - Seamless interoperation between all components
- **💾 Full 4 KB Config-Space Shadow in BRAM**: Complete configuration space emulation
  - Full 4 KB configuration space shadow in BRAM
  - Dual-port access for simultaneous read/write operations
  - Overlay RAM for writable fields (Command/Status registers)
  - Initialization from donor device configuration data
  - Little-endian format compatible with PCIe specification
- **🔄 Auto-Replicate MSI-X Table**: Exact MSI-X table replication
  - Automatic parsing of MSI-X capability structure from donor configuration space
  - Parameterized SystemVerilog implementation of MSI-X table and PBA
  - Support for byte-enable granularity writes
  - Interrupt delivery logic with masking support
  - Integration with the existing BAR controller and configuration space shadow
- **✂️ Capability Pruning**: Selective capability modification
  - Automatic analysis of standard and extended PCI capabilities
  - Categorization of capabilities based on emulation feasibility
  - Selective pruning of unsupported capabilities
  - Modification of partially supported capabilities
  - Preservation of capability chain integrity
- **🎲 Deterministic Variance Seeding**: Consistent hardware variance
  - Deterministic seed generation based on device serial number (DSN) and build revision
  - Consistent variance parameters for the same donor device and build revision
  - Different variance parameters for different donor devices or build revisions
  - Support for different device classes with appropriate variance ranges
- **🏗️ Build Process**: Enhanced to support all integrated features
  - Improved donor dump extraction with full 4 KB configuration space
  - Added capability pruning step to the build process
  - Added MSI-X table parameter extraction and integration
  - Added deterministic variance seeding based on DSN and build revision
- **📋 Enhanced Logging**: Improved logging for all integrated features
  - Added detailed logging for capability pruning
  - Added MSI-X table parameter logging
  - Added variance parameter logging
  - Added integration status summary at the end of the build process
- **📚 Documentation**: Comprehensive documentation for all integrated features
  - Added `docs/INTEGRATED_FEATURES.md` with detailed integration information
  - Updated feature-specific documentation with integration details
  - Added troubleshooting information for integrated features
- **🔌 MSI-X Table Integration**: Fixed issues with MSI-X table integration
  - Corrected MSI-X table parameter extraction from configuration space
  - Fixed MSI-X table and PBA memory mapping in BAR controller
  - Improved error handling for MSI-X capability parsing
- **🧩 Capability Chain Integrity**: Fixed issues with capability chain integrity
  - Ensured proper next pointer updates when removing capabilities
  - Fixed extended capability chain traversal and modification
  - Improved error handling for capability chain manipulation
- **⏱️ Timing Consistency**: Fixed issues with timing consistency
  - Ensured deterministic variance seeding produces consistent results
  - Fixed timing parameter calculation and application
  - Improved error handling for variance parameter generation

## [0.2.0] - 2025-06-09

### ✨ Added
- **💾 Option-ROM Passthrough**: Complete Option-ROM replication from donor devices
  - Extracts Option-ROM from donor PCI devices using Linux sysfs interface
  - Supports two implementation modes:
    - Mode A: BAR 5 Window (pure FPGA implementation)
    - Mode B: External SPI Flash (for larger ROMs)
  - Handles legacy 16-bit config cycles for ROM access
  - Includes caching for improved performance
  - Configurable ROM size and source
- **🔧 Build System Integration**: Enhanced build process for Option-ROM support
  - Added command-line arguments for enabling and configuring Option-ROM feature
  - Automatic ROM extraction during build process
  - Support for using pre-extracted ROM files
  - Build-time selection between implementation modes
- **🧪 Testing Infrastructure**: Comprehensive test suite for Option-ROM functionality
  - Unit tests for Option-ROM extraction and handling
  - Support for different ROM sizes and formats
  - Validation of ROM signature and content

### 🔄 Changed
- **🔢 Version Bump**: Incremented to v0.2.0 to reflect significant Option-ROM feature addition
- **🏗️ Build Process**: Updated to support Option-ROM integration
- **📋 Enhanced Logging**: Improved logging for Option-ROM extraction and processing

## [Unreleased] - Build Process Improvements

### 🔄 Changed
- **🏗️ Local Build Default**: Changed local build to be the default process
  - Local builds now run by default (no container required)
  - Container builds now require explicit opt-in with `--use-donor-dump`
  - Improved error handling for local build scenarios
  - Enhanced documentation for local build workflows
- **🔧 Container Engine Options**: Added support for multiple container engines
  - Added new `--container-engine` option to specify engine preference
  - Podman is now the default container engine
  - Docker remains fully supported as an alternative option
  - Automatic detection of available container engines
- **🔍 Vivado Location Validation**: Enhanced Vivado detection and validation
  - Improved cross-platform Vivado installation detection
  - Added support for environment variables (XILINX_VIVADO)
  - Automatic version detection and compatibility checking
  - Detailed error messages for missing or incompatible installations

### 🔧 Fixed
- **🔌 VFIO Device Binding**: Fixed an issue where binding a device already bound to vfio-pci would fail
  - Added detection for devices already bound to vfio-pci
  - Improved error handling during the binding process
  - Added comprehensive test cases for this edge case
- **📦 Container Dependency Installation**: Fixed missing Python dependencies in container build
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

### 🚀 v0.3.0 Highlights

This release integrates all major features of the PCILeech FPGA firmware generator, providing a comprehensive solution for PCIe device emulation. The integration ensures that all features work together seamlessly, providing a more realistic and functional emulation experience.

Key improvements include:
- **💾 Full 4 KB Config-Space Shadow**: Complete configuration space emulation with overlay RAM for writable fields
- **🔄 MSI-X Table Replication**: Exact replication of MSI-X tables from donor devices
- **✂️ Capability Pruning**: Selective modification of capabilities that can't be faithfully emulated
- **🎲 Deterministic Variance Seeding**: Consistent hardware variance based on device serial number and build revision

### 🚀 v0.2.0 Highlights

This release introduces the Option-ROM passthrough feature, allowing the PCILeech FPGA firmware to faithfully replicate the Option-ROM of donor PCI devices. This enables advanced functionality such as UEFI boot support and device-specific initialization.

Key improvements include:
- **💾 Complete Option-ROM Replication**: Extract and replicate Option-ROMs from donor devices
- **🔀 Dual Implementation Modes**: Choose between pure FPGA (BAR window) or SPI flash implementations
- **🔌 Legacy ROM Support**: Proper handling of legacy 16-bit config cycles for ROM access
- **🛠️ Flexible Configuration**: Command-line options for ROM source, size, and implementation mode

### 🚀 v0.2.0 Highlights

This major release introduces a modern, interactive TUI that transforms the user experience while maintaining full backward compatibility with the original command-line interface. The TUI provides guided workflows, real-time monitoring, and intelligent error handling that makes firmware generation more accessible and reliable.

Key improvements include:
- **🎯 Zero Learning Curve**: Intuitive interface guides users through the entire process
- **📊 Real-time Feedback**: Live monitoring of build progress and system resources
- **🛡️ Error Prevention**: Validation and checks prevent common configuration mistakes
- **📦 Professional Packaging**: Easy installation via pip with proper dependency management

### 🔄 Backward Compatibility

All existing command-line workflows continue to work unchanged. The new integrated features are designed to be backward compatible with existing workflows, ensuring a smooth transition for users.

### 🔮 Future Roadmap

- Web-based interface for remote build management
- Enhanced device compatibility and detection
- Advanced firmware customization options
- Integration with additional FPGA toolchains
- Cloud-based build services

## ⚠️ Disclaimer

This tool is intended for educational research and legitimate PCIe development purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors assume no liability for misuse of this software.

---

**Version 0.3.0** - Major release with integrated features for comprehensive PCIe device emulation