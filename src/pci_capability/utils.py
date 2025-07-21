#!/usr/bin/env python3
"""
PCI Capability Utility Functions

This module provides utility functions for PCI capability analysis,
categorization, and pruning operations.
"""

import logging
from typing import Dict

from .constants import TWO_BYTE_HEADER_CAPABILITIES
from .types import (
    CapabilityInfo,
    CapabilityType,
    EmulationCategory,
    PCICapabilityID,
    PCIExtCapabilityID,
    PruningAction,
)

logger = logging.getLogger(__name__)


def is_two_byte_header_capability(cap_id: int) -> bool:
    """
    Check if a standard capability has a 2-byte header instead of 1-byte.

    Args:
        cap_id: Standard capability ID

    Returns:
        True if capability has 2-byte header, False for 1-byte header
    """
    return cap_id in TWO_BYTE_HEADER_CAPABILITIES


def categorize_capability(cap_info: CapabilityInfo) -> EmulationCategory:
    """
    Categorize a single capability based on emulation feasibility.

    Args:
        cap_info: CapabilityInfo object to categorize

    Returns:
        EmulationCategory for the capability
    """
    cap_id = cap_info.cap_id
    cap_type = cap_info.cap_type

    if cap_type == CapabilityType.STANDARD:
        # Categorize standard capabilities
        if cap_id == PCICapabilityID.POWER_MANAGEMENT.value:
            return EmulationCategory.PARTIALLY_SUPPORTED
        elif cap_id == PCICapabilityID.MSI.value:
            return EmulationCategory.FULLY_SUPPORTED
        elif cap_id == PCICapabilityID.MSI_X.value:
            return EmulationCategory.FULLY_SUPPORTED
        elif cap_id == PCICapabilityID.PCI_EXPRESS.value:
            return EmulationCategory.PARTIALLY_SUPPORTED
        elif cap_id in [
            PCICapabilityID.AGP.value,
            PCICapabilityID.VPD.value,
            PCICapabilityID.SLOT_ID.value,
            PCICapabilityID.PCI_X.value,
            PCICapabilityID.AF.value,
            PCICapabilityID.VENDOR_SPECIFIC.value,
        ]:
            return EmulationCategory.UNSUPPORTED
        else:
            # Unknown standard capability - unsupported
            return EmulationCategory.UNSUPPORTED

    elif cap_type == CapabilityType.EXTENDED:
        # Categorize extended capabilities
        if cap_id == PCIExtCapabilityID.ADVANCED_ERROR_REPORTING.value:
            return EmulationCategory.PARTIALLY_SUPPORTED
        elif cap_id == PCIExtCapabilityID.ACCESS_CONTROL_SERVICES.value:
            # ACS - partially supported as requested
            return EmulationCategory.PARTIALLY_SUPPORTED
        elif cap_id == PCIExtCapabilityID.DOWNSTREAM_PORT_CONTAINMENT.value:
            # DPC - partially supported as requested
            return EmulationCategory.PARTIALLY_SUPPORTED
        elif cap_id == PCIExtCapabilityID.RESIZABLE_BAR.value:
            return EmulationCategory.PARTIALLY_SUPPORTED
        else:
            # All other extended capabilities - unsupported
            return EmulationCategory.UNSUPPORTED

    # Default to unsupported for unknown types
    return EmulationCategory.UNSUPPORTED


def categorize_capabilities(
    capabilities: Dict[int, CapabilityInfo],
) -> Dict[int, EmulationCategory]:
    """
    Categorize multiple capabilities based on emulation feasibility.

    Args:
        capabilities: Dictionary mapping offsets to CapabilityInfo objects

    Returns:
        Dictionary mapping capability offsets to emulation categories
    """
    categories = {}

    for offset, cap_info in capabilities.items():
        categories[offset] = categorize_capability(cap_info)

    return categories


def determine_pruning_action(category: EmulationCategory) -> PruningAction:
    """
    Determine pruning action for a capability based on its category.

    Args:
        category: EmulationCategory for the capability

    Returns:
        PruningAction to take for the capability
    """
    if category == EmulationCategory.FULLY_SUPPORTED:
        return PruningAction.KEEP
    elif category == EmulationCategory.PARTIALLY_SUPPORTED:
        return PruningAction.MODIFY
    elif category == EmulationCategory.UNSUPPORTED:
        return PruningAction.REMOVE
    elif category == EmulationCategory.CRITICAL:
        return PruningAction.KEEP
    else:
        # Default to remove for unknown categories
        return PruningAction.REMOVE


def determine_pruning_actions(
    capabilities: Dict[int, CapabilityInfo], categories: Dict[int, EmulationCategory]
) -> Dict[int, PruningAction]:
    """
    Determine pruning actions for multiple capabilities based on their categories.

    Args:
        capabilities: Dictionary mapping offsets to CapabilityInfo objects
        categories: Dictionary mapping capability offsets to emulation categories

    Returns:
        Dictionary mapping capability offsets to pruning actions
    """
    actions = {}

    for offset, cap_info in capabilities.items():
        category = categories.get(offset, EmulationCategory.UNSUPPORTED)
        actions[offset] = determine_pruning_action(category)

    return actions


def get_capability_name(cap_id: int, cap_type: CapabilityType) -> str:
    """
    Get the human-readable name for a capability.

    Args:
        cap_id: Capability ID
        cap_type: Type of capability (standard or extended)

    Returns:
        Human-readable capability name
    """
    if cap_type == CapabilityType.STANDARD:
        from .constants import STANDARD_CAPABILITY_NAMES

        return STANDARD_CAPABILITY_NAMES.get(cap_id, safe_format(
                    "Unknown (0x{cap_id:02x})",
                    cap_id=cap_id,
                ))
    else:
        from .constants import EXTENDED_CAPABILITY_NAMES

        name = EXTENDED_CAPABILITY_NAMES.get(
            cap_id, safe_format(
                    "Unknown Extended (0x{cap_id:04x})",
                    cap_id=cap_id,
                )
        )
        if cap_id not in EXTENDED_CAPABILITY_NAMES and cap_id <= 0x0029:
            log_info_safe(
                logger,
                "Unknown extended capability ID 0x{cap_id:04x} encountered",
                prefix="PCI_CAP",
                cap_id=cap_id,
            )
        return name


def validate_capability_offset(offset: int, cap_type: CapabilityType) -> bool:
    """
    Validate that a capability offset is reasonable for its type.

    Args:
        offset: Capability offset to validate
        cap_type: Type of capability (standard or extended)

    Returns:
        True if offset is valid, False otherwise
    """
    if cap_type == CapabilityType.STANDARD:
        # Standard capabilities should be in the first 256 bytes
        # and typically start after the standard header (0x40+)
        return 0x40 <= offset < 0x100
    else:
        # Extended capabilities start at 0x100 and should be DWORD aligned
        from .constants import (
            PCI_EXT_CAP_ALIGNMENT,
            PCI_EXT_CAP_START,
            PCI_EXT_CONFIG_SPACE_END,
        )

        return (
            PCI_EXT_CAP_START <= offset < PCI_EXT_CONFIG_SPACE_END
            and offset & PCI_EXT_CAP_ALIGNMENT == 0
        )


def format_capability_info(cap_info: CapabilityInfo) -> str:
    """
    Format capability information for display.

    Args:
        cap_info: CapabilityInfo object to format

    Returns:
        Formatted string representation of the capability
    """
    if cap_info.cap_type == CapabilityType.STANDARD:
        return safe_format("Standard Cap @ 0x{cap_info.offset:02x}: {cap_info.name} (ID: 0x{cap_info.cap_id:02x})")
    else:
        return safe_format("Extended Cap @ 0x{cap_info.offset:03x}: {cap_info.name} (ID: 0x{cap_info.cap_id:04x}, Ver: {cap_info.version})")


def get_capability_size_estimate(cap_info: CapabilityInfo) -> int:
    """
    Estimate the size of a capability structure.

    This provides rough estimates for common capabilities to help with
    bounds checking and space calculations.

    Args:
        cap_info: CapabilityInfo object

    Returns:
        Estimated size in bytes
    """
    cap_id = cap_info.cap_id
    cap_type = cap_info.cap_type

    if cap_type == CapabilityType.STANDARD:
        # Standard capability size estimates
        if cap_id == PCICapabilityID.POWER_MANAGEMENT.value:
            return 8  # PM capability is typically 8 bytes
        elif cap_id == PCICapabilityID.MSI.value:
            return 24  # MSI can be 10-24 bytes depending on features
        elif cap_id == PCICapabilityID.MSI_X.value:
            return 12  # MSI-X capability structure is 12 bytes
        elif cap_id == PCICapabilityID.PCI_EXPRESS.value:
            return 60  # PCIe capability can be quite large
        else:
            return 16  # Default estimate for unknown standard capabilities

    else:
        # Extended capability size estimates
        if cap_id == PCIExtCapabilityID.ADVANCED_ERROR_REPORTING.value:
            return 48  # AER is typically 48 bytes
        elif cap_id == PCIExtCapabilityID.ACCESS_CONTROL_SERVICES.value:
            return 8  # ACS is typically 8 bytes
        elif cap_id == PCIExtCapabilityID.DOWNSTREAM_PORT_CONTAINMENT.value:
            return 16  # DPC is typically 16 bytes
        elif cap_id == PCIExtCapabilityID.RESIZABLE_BAR.value:
            return 16  # Resizable BAR varies, but 16 bytes is common
        else:
            return 32  # Default estimate for unknown extended capabilities
