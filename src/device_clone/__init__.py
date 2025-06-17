#!/usr/bin/env python3
"""
Device Clone Module

This module contains all the device cloning related functionality including:
- Board configuration and capability management
- PCI configuration space management
- MSI-X capability handling
- Device configuration and identification
- Manufacturing variance simulation
- Behavior profiling
- PCI capability processing and manipulation

The module is organized to provide a clean separation of device cloning
functionality from the rest of the PCILeech firmware generation system.
"""

# Core device cloning functionality
from .board_config import (
    get_fpga_part,
    get_fpga_family,
    get_pcie_ip_type,
    get_pcileech_board_config,
    get_board_info,
    validate_board,
    list_supported_boards,
)

from .constants import *

from .device_config import (
    DeviceType,
    DeviceClass,
    PCIeRegisters,
    DeviceIdentification,
    DeviceCapabilities,
    DeviceConfiguration,
    DeviceConfigManager,
    get_config_manager,
    get_device_config,
    validate_hex_id,
)

from .config_space_manager import ConfigSpaceManager

from .msix_capability import (
    hex_to_bytes,
    read_u16_le,
    read_u32_le,
    is_valid_offset,
    find_cap,
    msix_size,
    parse_msix_capability,
    generate_msix_table_sv,
    validate_msix_configuration,
    generate_msix_capability_registers,
)

# Manufacturing variance and behavior profiling
from .manufacturing_variance import (
    DeviceClass as VarianceDeviceClass,
    VarianceType,
    VarianceParameters,
    VarianceModel,
    ManufacturingVarianceSimulator,
)

from .behavior_profiler import (
    RegisterAccess,
    TimingPattern,
    BehaviorProfile,
    BehaviorProfiler,
)

from .variance_manager import VarianceManager

# PCI capability processing
from .pci_capability import *

__all__ = [
    # Board configuration
    'get_fpga_part',
    'get_fpga_family', 
    'get_pcie_ip_type',
    'get_pcileech_board_config',
    'get_board_info',
    'validate_board',
    'list_supported_boards',
    
    # Device configuration
    'DeviceType',
    'DeviceClass',
    'PCIeRegisters',
    'DeviceIdentification', 
    'DeviceCapabilities',
    'DeviceConfiguration',
    'DeviceConfigManager',
    'get_config_manager',
    'get_device_config',
    'validate_hex_id',
    
    # Config space management
    'ConfigSpaceManager',
    
    # MSI-X capability
    'hex_to_bytes',
    'read_u16_le',
    'read_u32_le',
    'is_valid_offset',
    'find_cap',
    'msix_size',
    'parse_msix_capability',
    'generate_msix_table_sv',
    'validate_msix_configuration',
    'generate_msix_capability_registers',
    
    # Manufacturing variance
    'VarianceDeviceClass',
    'VarianceType',
    'VarianceParameters',
    'VarianceModel',
    'ManufacturingVarianceSimulator',
    
    # Behavior profiling
    'RegisterAccess',
    'TimingPattern',
    'BehaviorProfile',
    'BehaviorProfiler',
    'VarianceManager',
]