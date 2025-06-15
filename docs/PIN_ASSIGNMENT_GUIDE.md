# Pin Assignment Guide for PCILeech Firmware Generator

## Overview

The PCILeech firmware generator automatically loads constraint files (XDC) from the official PCILeech FPGA repository that define pin assignments and I/O standards for all ports in the `pcileech_top` module. **The system uses real, tested XDC files from the PCILeech project.**

## Automatic XDC Loading

The firmware generator now automatically:

1. **Downloads the PCILeech FPGA repository** if not already available
2. **Identifies your board type** from the supported board configurations
3. **Loads the appropriate XDC files** for your specific board
4. **Integrates the constraints** into the generated firmware

## Supported Board Types

The system supports the following board configurations with their corresponding XDC files:

### Original PCILeech Boards
- **35t**: PCIeSquirrel boards
- **75t**: PCIeEnigmaX1 boards  
- **100t**: XilinxZDMA boards

### CaptainDMA Boards
- **pcileech_75t484_x1**: CaptainDMA 75T boards (484-pin, x1 PCIe)
- **pcileech_35t484_x1**: CaptainDMA 35T boards (484-pin, x1 PCIe)
- **pcileech_35t325_x4**: CaptainDMA 35T boards (325-pin, x4 PCIe)
- **pcileech_35t325_x1**: CaptainDMA 35T boards (325-pin, x1 PCIe)
- **pcileech_100t484_x1**: CaptainDMA 100T boards (484-pin, x1 PCIe)

### Other Supported Boards
- **pcileech_enigma_x1**: EnigmaX1 boards
- **pcileech_squirrel**: PCIeSquirrel boards
- **pcileech_pciescreamer_xc7a35**: PCIeScreamer boards

## How It Works

### 1. Repository Management
The `RepoManager` class automatically:
```python
# Ensures PCILeech FPGA repository is available
RepoManager.ensure_git_repo()

# Gets board-specific directory
board_path = RepoManager.get_board_path("pcileech_75t484_x1")

# Finds all XDC files for the board
xdc_files = RepoManager.get_board_xdc_files("pcileech_75t484_x1")

# Reads and combines XDC content
xdc_content = RepoManager.read_xdc_constraints("pcileech_75t484_x1")
```

### 2. Constraint Integration
The constraint template automatically:
- Loads board-specific XDC content if available
- Falls back to basic timing constraints if XDC files aren't found
- Provides clear warnings when using fallback constraints

### 3. Validation
Use the validation script to verify constraints:
```bash
python scripts/validate_constraints.py
```

## Repository Structure

The PCILeech FPGA repository is organized as:
```
~/.cache/pcileech-fw-generator/repos/pcileech-fpga/
├── CaptainDMA/
│   ├── 75t484_x1/
│   │   └── src/
│   │       └── pcileech_75t484_x1_captaindma_75t.xdc
│   ├── 35t484_x1/
│   └── ...
├── PCIeSquirrel/
├── PCIeEnigmaX1/
└── ...
```

## Custom Board Support

### Adding New Board Types
To add support for a new board:

1. **Add board mapping** in `src/repo_manager.py`:
```python
board_info = {
    # ... existing boards ...
    "your_board_name": PCILEECH_FPGA_DIR / "path" / "to" / "board",
}
```

2. **Ensure XDC files exist** in the PCILeech repository at the specified path

3. **Test the integration**:
```bash
python scripts/validate_constraints.py --board-type your_board_name
```

### Using Custom XDC Files
If you have custom XDC files:

1. **Place them in the appropriate board directory** in the PCILeech repository
2. **Follow the naming convention**: `*.xdc`
3. **The system will automatically discover and load them**

## Troubleshooting

### Common Issues

#### 1. Board Type Not Found
```
RuntimeError: Unknown board type: your_board
```
**Solution**: Check that your board type is listed in the supported boards above, or add it to the board mapping.

#### 2. No XDC Files Found
```
RuntimeError: No XDC files found for board type: pcileech_75t484_x1
```
**Solution**: 
- Ensure the PCILeech repository is properly cloned
- Check that XDC files exist in the board directory
- Verify the board path mapping is correct

#### 3. Repository Not Available
```
RuntimeError: Git is not available or repository operations fail
```
**Solution**:
- Install Git: `sudo apt install git` (Linux) or `brew install git` (macOS)
- Check internet connectivity
- Verify repository URL is accessible

#### 4. Fallback Constraints Used
```
Warning: Using fallback pin assignments - update for your specific board!
```
**Solution**: This indicates board-specific XDC files weren't loaded. Check the board type and repository status.

### Validation Commands

```bash
# Validate constraints for specific board
python scripts/validate_constraints.py --board-type pcileech_75t484_x1

# Check available XDC files
python -c "
from src.repo_manager import RepoManager
files = RepoManager.get_board_xdc_files('pcileech_75t484_x1')
print('XDC files:', [f.name for f in files])
"

# Test repository access
python -c "
from src.repo_manager import RepoManager
RepoManager.ensure_git_repo()
print('Repository available')
"
```

## Benefits of This Approach

1. **Tested Constraints**: Uses real, tested XDC files from the PCILeech project
2. **Automatic Updates**: Gets latest constraints when repository is updated
3. **Board-Specific**: Proper pin assignments for each supported board type
4. **Fallback Safety**: Graceful degradation when XDC files aren't available
5. **Easy Validation**: Built-in tools to verify constraint completeness

## Manual Override

If you need to override the automatic XDC loading:

1. **Modify the template context** before rendering:
```python
context["board_xdc_content"] = your_custom_xdc_content
```

2. **Or provide custom constraint files** in the build process:
```python
tcl_builder.build_constraints_tcl(context, custom_constraint_files)
```

## Port Coverage

The system ensures all ports from the `pcileech_top` module have proper constraints:

### Input Ports
- `clk` - System clock
- `reset_n` - Reset signal (active low)
- `pcie_rx_data[31:0]` - PCIe receive data bus
- `pcie_rx_valid` - PCIe receive valid signal
- `cfg_ext_read_received` - Configuration read received
- `cfg_ext_write_received` - Configuration write received
- `cfg_ext_register_number[9:0]` - Configuration register number
- `cfg_ext_function_number[3:0]` - Configuration function number
- `cfg_ext_write_data[31:0]` - Configuration write data
- `cfg_ext_write_byte_enable[3:0]` - Configuration write byte enables
- `msix_interrupt_ack` - MSI-X interrupt acknowledgment

### Output Ports
- `pcie_tx_data[31:0]` - PCIe transmit data bus
- `pcie_tx_valid` - PCIe transmit valid signal
- `cfg_ext_read_data[31:0]` - Configuration read data
- `cfg_ext_read_data_valid` - Configuration read data valid
- `msix_interrupt` - MSI-X interrupt signal
- `msix_vector[10:0]` - MSI-X interrupt vector
- `debug_status[31:0]` - Debug status output
- `device_ready` - Device ready signal

All these ports will have appropriate IOSTANDARD and PACKAGE_PIN assignments loaded from the board-specific XDC files.

## Example XDC Content

Here's an example of what gets loaded from a CaptainDMA board XDC file:

```tcl
# Clock and Reset
set_property PACKAGE_PIN E3 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]
set_property PACKAGE_PIN C12 [get_ports reset_n]
set_property IOSTANDARD LVCMOS33 [get_ports reset_n]

# PCIe Interface
set_property PACKAGE_PIN A1 [get_ports {pcie_rx_data[0]}]
set_property IOSTANDARD LVCMOS18 [get_ports pcie_rx_data*]
# ... additional pin assignments
```

The system is designed to be flexible while providing sensible defaults based on the proven PCILeech FPGA designs.