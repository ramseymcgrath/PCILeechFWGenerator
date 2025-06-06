# Donor Dump Kernel Module

The `donor_dump` kernel module extracts PCI device parameters and exposes them via `/proc/donor_dump`. This module is used to gather detailed information about PCI devices for firmware generation.

**Note**: By default, the PCILeech Firmware Generator automatically builds and uses this kernel module to extract device information. If you prefer not to use the kernel module, you can use the `--skip-donor-dump` option or the "Local Build" mode in the TUI.

## Features

- Extracts Max-Payload-Capable (MPC) and Max-ReadReq-InEffect (MPR) values
- Provides vendor/device IDs, subsystem information, and revision
- Exports 24-bit class code information
- Reports BAR0 size and Device Serial Number (DSN)
- Dumps full 4KB extended configuration space
- Analyzes power management, AER, and vendor-specific capabilities

## Building the Module

**Important**: This kernel module must be built on the target system where it will be used, not in a container, because it requires kernel headers that match the running kernel.

### Prerequisites

Different Linux distributions have different ways to install kernel headers:

#### Debian/Ubuntu
```bash
# Install kernel headers for your current kernel
sudo apt-get update
sudo apt-get install linux-headers-$(uname -r) build-essential

# Verify headers are installed
ls /lib/modules/$(uname -r)/build
```

#### Fedora/CentOS/RHEL
```bash
# Install kernel headers and development tools
sudo dnf install kernel-devel-$(uname -r) gcc make

# Verify headers are installed
ls /lib/modules/$(uname -r)/build
```

#### Arch Linux/Manjaro
```bash
# Install kernel headers and development tools
sudo pacman -S linux-headers base-devel

# Verify headers are installed
ls /lib/modules/$(uname -r)/build
```

#### openSUSE
```bash
# Install kernel headers and development tools
sudo zypper install kernel-devel-$(uname -r) gcc make

# Verify headers are installed
ls /lib/modules/$(uname -r)/build
```

### Build Instructions

```bash
# Navigate to the donor_dump directory
cd src/donor_dump

# Build the module
make

# Verify the module was built
ls -la donor_dump.ko
```

## Usage

### Loading the Module

```bash
# Load with a specific PCI device (replace with your device's BDF)
sudo insmod donor_dump.ko bdf=0000:03:00.0

# Verify the module is loaded
lsmod | grep donor_dump
```

### Reading Device Information

```bash
# View extracted device parameters
cat /proc/donor_dump
```

Example output:
```
mpc:2
mpr:1
vendor_id:8086
device_id:1521
subvendor_id:8086
subsystem_id:0001
revision_id:01
class_code:020000
bar_size:131072
dsn_hi:0
dsn_lo:0
extended_config:8086152100060010...
power_mgmt:c823
aer_caps:10001
vendor_caps:0040
```

### Unloading the Module

```bash
# Unload the module
sudo rmmod donor_dump
```

## Module Parameters

- `bdf`: PCI Bus:Device.Function (e.g., "0000:03:00.0") - **Required**
- `enable_extended_config`: Enable extended configuration space extraction (default: true)
- `enable_enhanced_caps`: Enable enhanced capability analysis (default: true)

## Alternative Options

If you cannot or prefer not to use this kernel module, the PCILeech Firmware Generator provides alternative options:

1. **Using a donor info file**: You can save the output from a previous run and reuse it:
   ```bash
   # First run with donor_dump to save the info
   sudo pcileech-build --bdf 0000:03:00.0 --board 75t --donor-info-file /path/to/save/donor_info.json
   
   # Later runs using the saved file (no donor device needed)
   sudo pcileech-build --bdf 0000:03:00.0 --board 75t --skip-donor-dump --donor-info-file /path/to/saved/donor_info.json
   ```

2. **Using synthetic data**: When no donor info file is available, the system can generate synthetic data:
   ```bash
   # Generate synthetic data for a network device
   sudo pcileech-build --bdf 0000:03:00.0 --board 75t --skip-donor-dump --device-type network
   ```

3. **TUI Local Build Mode**: In the TUI, enable "Local Build" mode and disable "Donor Dump" in the configuration panel.

## Makefile Targets

- `make` or `make all`: Build the kernel module
- `make clean`: Clean build artifacts
- `make install`: Install module to system (requires root)
- `make uninstall`: Remove module from system (requires root)
- `make load BDF=0000:03:00.0`: Load module with specified BDF
- `make unload`: Unload module
- `make info`: Show module information
- `make help`: Display available targets

## Container Usage

When using the PCILeech firmware generator container, the kernel module source is included but not pre-built. To use the module:

1. Copy the module source from the container:
   ```bash
   # Create a container and copy the source
   podman create --name temp-container your-image
   podman cp temp-container:/app/src/donor_dump ./
   podman rm temp-container
   ```

2. Build on your host system:
   ```bash
   cd donor_dump
   sudo apt-get install linux-headers-$(uname -r)
   make
   ```

3. Load and use:
   ```bash
   sudo insmod donor_dump.ko bdf=YOUR_DEVICE_BDF
   cat /proc/donor_dump
   ```

## Troubleshooting

### "Kernel headers not found" Error

#### Debian/Ubuntu
```bash
# Install headers for your specific kernel
sudo apt-get update
sudo apt-get install linux-headers-$(uname -r) build-essential
```

#### Fedora/CentOS/RHEL
```bash
# Install headers for your specific kernel
sudo dnf install kernel-devel-$(uname -r) gcc make
```

#### Arch Linux/Manjaro
```bash
# Install headers for your kernel
sudo pacman -S linux-headers base-devel
```

#### openSUSE
```bash
# Install headers for your specific kernel
sudo zypper install kernel-devel-$(uname -r) gcc make
```

### "No such device" Error

- Verify the PCI device exists: `lspci | grep YOUR_DEVICE`
- Check the BDF format is correct: `0000:XX:XX.X`
- Ensure the device is accessible and not bound to another driver

### Permission Denied

- Module loading requires root privileges
- Use `sudo` for all module operations

## Compatibility

- Compatible with Linux kernel 4.x and 5.x
- GPL-compatible license
- Tested on:
  - Ubuntu 20.04+ and other Debian-based distributions
  - Fedora 34+ and other RHEL-based distributions
  - Arch Linux and Manjaro
  - openSUSE Leap and Tumbleweed

## Common Build Issues

### Module Version Mismatch

If you see errors like "version magic" or "module layout", it means the module was built for a different kernel version:

```bash
# Rebuild the module for your current kernel
make clean
make
```

### Missing Build Tools

If you encounter build errors, make sure you have the necessary build tools:

```bash
# Debian/Ubuntu
sudo apt-get install build-essential

# Fedora/CentOS/RHEL
sudo dnf groupinstall "Development Tools"

# Arch Linux/Manjaro
sudo pacman -S base-devel

# openSUSE
sudo zypper install -t pattern devel_basis
```

### Secure Boot Issues

If you're using Secure Boot, you may need to sign the module or disable Secure Boot:

```bash
# Check if Secure Boot is enabled
mokutil --sb-state

# Temporarily disable Secure Boot in your BIOS/UEFI settings
```