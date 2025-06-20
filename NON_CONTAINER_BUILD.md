# PCILeech Firmware Generator - Non-Containerized Build

This document explains how to use the `build_without_container.py` script to run PCILeech firmware generation without using a container.

## Prerequisites

- Linux system with VFIO support
- Root privileges (sudo)
- Python 3.6+
- vfio-pci kernel module loaded
- All required Python dependencies installed

## Usage

The script requires root privileges to bind devices to VFIO:

```bash
sudo ./build_without_container.py [--bdf <BDF>] [--board <BOARD>] [options]
```

If you don't provide the `--bdf` or `--board` arguments, the script will launch interactive prompts to help you select them.

### Interactive Mode

When run without required arguments, the script will:

1. Display a list of available PCI devices and prompt you to select one
2. Display a list of supported boards and prompt you to select one
3. Optionally allow you to change the device type from the default "generic"

This interactive mode makes it easy to use the script without remembering specific device identifiers or board names.

### Arguments

- `--bdf`: PCI Bus:Device.Function identifier (e.g., `0000:03:00.0`)
- `--board`: Target board configuration (one of the supported boards listed below)

#### Supported Boards
- `pcileech_75t484_x1`
- `pcileech_35t484_x1`
- `pcileech_35t325_x4`
- `pcileech_35t325_x1`
- `pcileech_100t484_x1`
- `pcileech_enigma_x1`
- `pcileech_squirrel`
- `pcileech_pciescreamer_xc7a35`

### Optional Arguments

- `--output-dir`: Output directory for generated files (default: `output`)
- `--enable-profiling`: Enable behavior profiling during generation
- `--profile-duration`: Behavior profiling duration in seconds (default: 10)
- `--enable-variance`: Enable manufacturing variance simulation
- `--enable-advanced`: Enable advanced SystemVerilog features
- `--vivado`: Run Vivado after generation
- `--verbose`: Enable verbose logging

### Fallback Control

- `--fallback-mode`: Control fallback behavior (`none`=fail-fast, `prompt`=ask, `auto`=allow)
- `--allow-fallbacks`: Comma-separated list of allowed fallbacks
- `--deny-fallbacks`: Comma-separated list of denied fallbacks

## Examples

### Interactive Mode

```bash
# Run with interactive prompts for device and board selection
sudo ./build_without_container.py
```

### Basic Usage

```bash
sudo ./build_without_container.py --bdf 0000:03:00.0 --board pcileech_35t325_x4
```

### With Profiling and Vivado

```bash
sudo ./build_without_container.py --bdf 0000:03:00.0 --board pcileech_35t325_x4 --enable-profiling --profile-duration 30 --vivado
```

### With Advanced Features

```bash
sudo ./build_without_container.py --bdf 0000:03:00.0 --board pcileech_35t325_x4 --enable-advanced --enable-variance
```

### With Custom Device Type

```bash
sudo ./build_without_container.py --bdf 0000:03:00.0 --board pcileech_35t325_x4 --device-type network
```

## Troubleshooting

If you encounter issues with VFIO binding, the script will attempt to run VFIO diagnostics and provide a report. Common issues include:

1. IOMMU not enabled in BIOS
2. vfio-pci kernel module not loaded
3. Insufficient permissions
4. Device already bound to another driver

To manually load the vfio-pci module:

```bash
sudo modprobe vfio-pci
```

## Differences from Containerized Build

The non-containerized build:

1. Runs directly on the host system without Podman/Docker
2. Requires all dependencies to be installed on the host
3. Handles VFIO binding directly
4. May require additional setup depending on your system configuration

The containerized build is generally more isolated and consistent across different environments, but the non-containerized build can be more convenient for development and debugging.