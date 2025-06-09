# Cross-Platform Support

The PCILeech Firmware Generator has some cross-platform support but not much. Podman helps with a more self-contained build env but you might have issues passing through some pcie devices. The kernel module always needs to be run on a metal linux machine. 

## Overview

While the core firmware generation functionality requires Linux (due to VFIO, kernel modules, and PCI subsystem dependencies), the project now gracefully handles execution on other platforms like macOS and Windows.

## Platform Detection

All user-facing scripts include platform detection:

```python
import platform

def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system().lower() == "linux"

def check_linux_requirement(operation: str) -> None:
    """Check if operation requires Linux and raise error if not available."""
    if not is_linux():
        raise RuntimeError(
            f"{operation} requires Linux. "
            f"Current platform: {platform.system()}. "
            f"This functionality is only available on Linux systems."
        )
```

## Enhanced Scripts

### 1. Main CLI (`generate.py`)

**Linux-specific operations:**
- PCIe device enumeration (`lspci`)
- Driver detection (`/sys/bus/pci/devices/`)
- IOMMU group detection
- VFIO device binding

**Error messages:**
- "PCIe device enumeration requires Linux"
- "Driver detection requires Linux"
- "IOMMU group detection requires Linux"
- "VFIO device binding requires Linux"

### 2. Donor Dump Manager (`src/donor_dump_manager.py`)

**Cross-platform behavior:**
- ✅ Status checking works on all platforms
- ✅ Gracefully detects when `lsmod` is not available
- ✅ Reports kernel module functionality as unavailable on non-Linux

**Linux-specific operations:**
- Kernel module building, loading, unloading
- `/proc/donor_dump` interface access

### 3. Behavior Profiler (`src/behavior_profiler.py`)

**Linux-specific operations:**
- Device behavior monitoring
- ftrace integration (`/sys/kernel/debug/tracing/`)
- sysfs device monitoring (`/sys/bus/pci/devices/`)

**Error message:**
- "Device behavior monitoring requires Linux"

### 4. Driver Scraper (`src/scripts/driver_scrape.py`)

**Linux-specific operations:**
- Driver module resolution (`modprobe`)
- Kernel source analysis

**Error message:**
- "Driver module resolution requires Linux"

## Usage Examples

### Successful Cross-Platform Operations

```bash
# Status checking works on all platforms
python3 src/donor_dump_manager.py --status --bdf 0000:03:00.0

# TUI configuration works on all platforms
python3 generate.py --tui

# Help and documentation work on all platforms
python3 generate.py --help
python3 src/donor_dump_manager.py --help
```

### Linux-Required Operations

```bash
# These will show helpful error messages on non-Linux systems:
sudo python3 generate.py --board 75t
python3 src/donor_dump_manager.py --bdf 0000:03:00.0 --auto-install-headers
python3 src/scripts/driver_scrape.py 8086 1533
```

## Error Message Examples

### macOS/Darwin:
```
RuntimeError: PCIe device enumeration requires Linux. Current platform: Darwin. 
This functionality is only available on Linux systems.
```

### Windows:
```
RuntimeError: VFIO device binding requires Linux. Current platform: Windows. 
This functionality is only available on Linux systems.
```

## Development Guidelines

When adding new Linux-specific functionality:

1. **Add platform detection:**
   ```python
   import platform
   
   def check_linux_requirement(operation: str) -> None:
       if platform.system().lower() != "linux":
           raise RuntimeError(f"{operation} requires Linux...")
   ```

2. **Call check at function start:**
   ```python
   def linux_specific_function():
       check_linux_requirement("Specific operation description")
       # ... rest of function
   ```

3. **Use descriptive operation names:**
   - ✅ "PCIe device enumeration"
   - ✅ "Kernel module loading"
   - ✅ "VFIO device binding"
   - ❌ "This operation"
   - ❌ "Function"

4. **Test on multiple platforms:**
   ```bash
   # Test on macOS/Windows
   python3 script.py --help  # Should work
   python3 script.py --linux-feature  # Should show clear error
   ```

## Container Usage

The container build provides a more cohesive environment but not all pcie cards may work. You can now specify which container engine to use (docker or podman).

```bash
# Build container on Linux host (if using container image)
podman build -t dma-fw .
podman run --rm -it dma-fw --help

# Specify container engine when building firmware
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t --container-engine docker
pcileech-build-sudo --bdf 0000:03:00.0 --board 75t --container-engine podman
```

## Testing

Cross-platform safety messages are tested in the test suite:

```bash
# Run cross-platform tests
python3 -m pytest tests/test_donor_dump.py::TestDonorDumpIntegration -v
```

## Benefits

1. **Clear error messages** instead of cryptic failures
2. **Graceful degradation** for non-critical features
3. **Better developer experience** on mixed-platform teams
4. **Easier debugging** and troubleshooting
5. **Documentation** of platform requirements

## Limitations

The following operations will always require Linux:

- **Hardware access:** PCI device enumeration and control
- **Kernel modules:** Building, loading, and interacting with kernel modules
- **VFIO:** Virtual Function I/O for device passthrough
- **System interfaces:** `/sys`, `/proc`, and other Linux-specific filesystems

For these operations, use the containerized workflow or a Linux development environment.