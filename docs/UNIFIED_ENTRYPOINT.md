# PCILeech Firmware Generator - Unified Entry Point

## Summary of Changes

This update consolidates all entry points into a single unified command-line interface to eliminate confusion and improve usability.

## Before (Multiple Entry Points)
- `generate.py` - Legacy CLI shim
- `tui_generate.py` - Separate TUI launcher
- `pcileech_generate.py` - PCILeech-specific build system
- `vfio_check.py` - VFIO configuration checker
- Various wrapper scripts

## After (Single Entry Point)
- `pcileech.py` - Unified entry point with subcommands

## New Usage

### Interactive TUI Mode
```bash
sudo python3 pcileech.py tui
```

### CLI Build Mode
```bash
sudo python3 pcileech.py build --bdf 0000:03:00.0 --board pcileech_35t325_x1
```

### VFIO Configuration Check
```bash
sudo python3 pcileech.py check --device 0000:03:00.0 --interactive
```

### Flash Firmware
```bash
sudo python3 pcileech.py flash output/firmware.bin
```

### Version Information
```bash
sudo python3 pcileech.py version
```

## Key Features

1. **Automatic Sudo Checks**: Warns and validates root privileges for hardware operations
2. **Integrated VFIO Validation**: Built-in VFIO setup checking and remediation
3. **Consistent Interface**: All functionality through a single entry point
4. **Backward Compatibility**: Legacy scripts forward to new unified interface
5. **Container Integration**: Updated container entry point uses unified interface

## Benefits

- **Simplified Usage**: One command to remember instead of multiple scripts
- **Better Error Handling**: Integrated checks for common issues
- **Cleaner Documentation**: Single interface to document and explain
- **Easier Maintenance**: Centralized command handling and validation
- **Improved User Experience**: Consistent command structure and help system

## Migration

All existing scripts (`generate.py`, `tui_generate.py`, `pcileech_generate.py`) remain as compatibility shims that forward to the new unified entry point, ensuring existing workflows continue to work.
