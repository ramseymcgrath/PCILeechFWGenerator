#!/usr/bin/env python3
"""
PCI Capability Analysis and Pruning

This module provides functionality to analyze and prune PCI capabilities
in the configuration space of a donor device. It supports both standard
and extended capabilities, and implements specific pruning rules for
capabilities that cannot be faithfully emulated.
"""

import logging
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# PCI Standard Capability IDs
class PCICapabilityID(Enum):
    """Standard PCI Capability IDs as defined in the PCI specification."""

    POWER_MANAGEMENT = 0x01
    MSI = 0x05
    VENDOR_SPECIFIC = 0x09
    PCI_EXPRESS = 0x10
    MSI_X = 0x11


# PCI Express Extended Capability IDs
class PCIExtCapabilityID(Enum):
    """PCI Express Extended Capability IDs as defined in the PCIe specification."""

    ADVANCED_ERROR_REPORTING = 0x0001
    VIRTUAL_CHANNEL = 0x0002
    DEVICE_SERIAL_NUMBER = 0x0003
    POWER_BUDGETING = 0x0004
    ROOT_COMPLEX_LINK_DECLARATION = 0x0005
    ROOT_COMPLEX_INTERNAL_LINK_CONTROL = 0x0006
    ROOT_COMPLEX_EVENT_COLLECTOR_ENDPOINT_ASSOCIATION = 0x0007
    MULTI_FUNCTION_VIRTUAL_CHANNEL = 0x0008
    VIRTUAL_CHANNEL_MFVC = 0x0009
    ROOT_COMPLEX_REGISTER_BLOCK = 0x000A
    VENDOR_SPECIFIC_EXTENDED = 0x000B
    CONFIG_ACCESS_CORRELATION = 0x000C
    ACCESS_CONTROL_SERVICES = 0x000D
    ALTERNATIVE_ROUTING_ID_INTERPRETATION = 0x000E
    ADDRESS_TRANSLATION_SERVICES = 0x000F
    SINGLE_ROOT_IO_VIRTUALIZATION = 0x0010
    MULTI_ROOT_IO_VIRTUALIZATION = 0x0011
    MULTICAST = 0x0012
    PAGE_REQUEST = 0x0013
    RESERVED_FOR_AMD = 0x0014
    RESIZABLE_BAR = 0x0015
    DYNAMIC_POWER_ALLOCATION = 0x0016
    TPH_REQUESTER = 0x0017
    LATENCY_TOLERANCE_REPORTING = 0x0018
    SECONDARY_PCI_EXPRESS = 0x0019
    PROTOCOL_MULTIPLEXING = 0x001A
    PROCESS_ADDRESS_SPACE_ID = 0x001B
    LN_REQUESTER = 0x001C
    DOWNSTREAM_PORT_CONTAINMENT = 0x001D
    L1_PM_SUBSTATES = 0x001E
    PRECISION_TIME_MEASUREMENT = 0x001F
    PCI_EXPRESS_OVER_MPHY = 0x0020
    FRS_QUEUEING = 0x0021
    READINESS_TIME_REPORTING = 0x0022
    DESIGNATED_VENDOR_SPECIFIC = 0x0023


# Capability emulation categories
class EmulationCategory(Enum):
    """Categories for capability emulation feasibility."""

    FULLY_SUPPORTED = auto()  # Can be fully emulated
    PARTIALLY_SUPPORTED = auto()  # Can be partially emulated with modifications
    UNSUPPORTED = auto()  # Cannot be emulated, should be removed
    CRITICAL = auto()  # Critical for operation, must be preserved


# Capability pruning actions
class PruningAction(Enum):
    """Actions to take when pruning capabilities."""

    KEEP = auto()  # Keep the capability as-is
    MODIFY = auto()  # Modify specific fields in the capability
    REMOVE = auto()  # Remove the capability entirely


def find_cap(cfg: str, cap_id: int) -> Optional[int]:
    """
    Find a standard capability in the PCI configuration space.

    Args:
        cfg: Configuration space as a hex string
        cap_id: Capability ID to find

    Returns:
        Offset of the capability in the configuration space, or None if not found
    """
    # Check if configuration space is valid
    if not cfg or len(cfg) < 256:
        logger.warning("Configuration space is too small or invalid")
        return None

    # Check if capabilities are supported (Status register bit 4)
    status_offset = 6  # Status register is at offset 0x06
    status_byte_offset = status_offset * 2  # Each byte is 2 hex chars
    status_bytes = cfg[status_byte_offset : status_byte_offset + 4]
    if len(status_bytes) < 4:
        logger.warning("Status register not found in configuration space")
        return None

    try:
        status = int(status_bytes, 16)
        if not (status & 0x10):  # Check capabilities bit
            logger.info("Device does not support capabilities")
            return None
    except ValueError:
        logger.warning(f"Invalid status register value: {status_bytes}")
        return None

    # Get capabilities pointer (offset 0x34)
    cap_ptr_offset = 0x34
    cap_ptr_byte_offset = cap_ptr_offset * 2
    cap_ptr_bytes = cfg[cap_ptr_byte_offset : cap_ptr_byte_offset + 2]
    if len(cap_ptr_bytes) < 2:
        logger.warning("Capabilities pointer not found in configuration space")
        return None

    try:
        cap_ptr = int(cap_ptr_bytes, 16)
        if cap_ptr == 0:
            logger.info("No capabilities present")
            return None
    except ValueError:
        logger.warning(f"Invalid capabilities pointer: {cap_ptr_bytes}")
        return None

    # Walk the capabilities list
    current_ptr = cap_ptr
    visited = set()  # To detect loops

    while current_ptr and current_ptr != 0 and current_ptr not in visited:
        visited.add(current_ptr)
        current_byte_offset = current_ptr * 2

        # Ensure we have enough data
        if current_byte_offset + 4 > len(cfg):
            logger.warning(f"Capability pointer {current_ptr:02x} is out of bounds")
            return None

        # Read capability ID and next pointer
        try:
            cap_id_bytes = cfg[current_byte_offset : current_byte_offset + 2]
            next_ptr_bytes = cfg[current_byte_offset + 2 : current_byte_offset + 4]

            current_cap_id = int(cap_id_bytes, 16)
            next_ptr = int(next_ptr_bytes, 16)

            if current_cap_id == cap_id:
                return current_ptr

            current_ptr = next_ptr
        except ValueError:
            logger.warning(f"Invalid capability data at offset {current_ptr:02x}")
            return None

    logger.info(f"Capability ID 0x{cap_id:02x} not found")
    return None


def find_ext_cap(cfg: str, cap_id: int) -> Optional[int]:
    """
    Find an extended capability in the PCI Express configuration space.

    Args:
        cfg: Configuration space as a hex string
        cap_id: Extended Capability ID to find

    Returns:
        Offset of the extended capability in the configuration space, or None if not found
    """
    # Special case for L1 PM Substates capability
    # If we're looking for L1 PM Substates and the capability has been pruned,
    # we should return None even if the header is still present but zeroed
    if cap_id == PCIExtCapabilityID.L1_PM_SUBSTATES.value:
        # Check if the L1 PM Substates capability at offset 0x100 has been zeroed out
        l1pm_offset = 0x100
        l1pm_byte_offset = l1pm_offset * 2

        if len(cfg) >= l1pm_byte_offset + 8:
            header_bytes = cfg[l1pm_byte_offset : l1pm_byte_offset + 8]
            if header_bytes == "00000000":
                return None

    # Extended capabilities start at offset 0x100
    ext_cap_start = 0x100

    # Check if configuration space is valid and large enough
    if not cfg or len(cfg) < ext_cap_start * 2:
        logger.warning("Configuration space is too small for extended capabilities")
        return None

    # Walk the extended capabilities list
    current_ptr = ext_cap_start
    visited = set()  # To detect loops

    while current_ptr and current_ptr != 0 and current_ptr not in visited:
        visited.add(current_ptr)
        current_byte_offset = current_ptr * 2

        # Ensure we have enough data (at least 4 bytes for header)
        if current_byte_offset + 8 > len(cfg):
            logger.warning(
                f"Extended capability pointer {current_ptr:03x} is out of bounds"
            )
            return None

        # Read extended capability ID and next pointer
        try:
            # Extended capability header is 4 bytes:
            # [31:16] = Capability ID
            # [15:4] = Capability Version
            # [3:0] = Next Capability Offset
            header_bytes = cfg[current_byte_offset : current_byte_offset + 8]

            # Check if the header is all zeros (capability has been removed)
            if header_bytes == "00000000":
                # Skip this capability as it has been removed
                break

            # Extract the capability ID (first 2 bytes)
            current_cap_id = int(header_bytes[0:4], 16)

            # Skip if capability ID is 0 (removed capability)
            if current_cap_id == 0:
                break

            # Extract the next capability pointer (last 2 bytes, but only the lower 12 bits)
            next_ptr = int(header_bytes[4:8], 16) & 0xFFF

            if current_cap_id == cap_id:
                return current_ptr

            # If next pointer is 0, end of list
            if next_ptr == 0:
                break

            current_ptr = next_ptr
        except ValueError:
            logger.warning(
                f"Invalid extended capability data at offset {current_ptr:03x}"
            )
            return None

    logger.info(f"Extended capability ID 0x{cap_id:04x} not found")
    return None


def get_all_capabilities(cfg: str) -> Dict[int, Dict]:
    """
    Get all standard capabilities in the PCI configuration space.

    Args:
        cfg: Configuration space as a hex string

    Returns:
        Dictionary mapping capability offsets to capability information
    """
    capabilities = {}

    # Check if configuration space is valid
    if not cfg or len(cfg) < 256:
        logger.warning("Configuration space is too small or invalid")
        return capabilities

    # Check if capabilities are supported (Status register bit 4)
    status_offset = 6  # Status register is at offset 0x06
    status_byte_offset = status_offset * 2  # Each byte is 2 hex chars
    status_bytes = cfg[status_byte_offset : status_byte_offset + 4]
    if len(status_bytes) < 4:
        logger.warning("Status register not found in configuration space")
        return capabilities

    try:
        status = int(status_bytes, 16)
        if not (status & 0x10):  # Check capabilities bit
            logger.info("Device does not support capabilities")
            return capabilities
    except ValueError:
        logger.warning(f"Invalid status register value: {status_bytes}")
        return capabilities

    # Get capabilities pointer (offset 0x34)
    cap_ptr_offset = 0x34
    cap_ptr_byte_offset = cap_ptr_offset * 2
    cap_ptr_bytes = cfg[cap_ptr_byte_offset : cap_ptr_byte_offset + 2]
    if len(cap_ptr_bytes) < 2:
        logger.warning("Capabilities pointer not found in configuration space")
        return capabilities

    try:
        cap_ptr = int(cap_ptr_bytes, 16)
        if cap_ptr == 0:
            logger.info("No capabilities present")
            return capabilities
    except ValueError:
        logger.warning(f"Invalid capabilities pointer: {cap_ptr_bytes}")
        return capabilities

    # Walk the capabilities list
    current_ptr = cap_ptr
    visited = set()  # To detect loops

    while current_ptr and current_ptr != 0 and current_ptr not in visited:
        visited.add(current_ptr)
        current_byte_offset = current_ptr * 2

        # Ensure we have enough data
        if current_byte_offset + 4 > len(cfg):
            logger.warning(f"Capability pointer {current_ptr:02x} is out of bounds")
            break

        # Read capability ID and next pointer
        try:
            cap_id_bytes = cfg[current_byte_offset : current_byte_offset + 2]
            next_ptr_bytes = cfg[current_byte_offset + 2 : current_byte_offset + 4]

            cap_id = int(cap_id_bytes, 16)
            next_ptr = int(next_ptr_bytes, 16)

            # Store capability information
            capabilities[current_ptr] = {
                "offset": current_ptr,
                "id": cap_id,
                "next_ptr": next_ptr,
                "type": "standard",
            }

            # Read capability-specific data
            if cap_id == PCICapabilityID.POWER_MANAGEMENT.value:
                # Power Management Capability
                if current_byte_offset + 8 <= len(cfg):
                    pm_cap_bytes = cfg[
                        current_byte_offset + 4 : current_byte_offset + 8
                    ]
                    pm_cap = int(pm_cap_bytes, 16)
                    capabilities[current_ptr]["pm_cap"] = pm_cap
                    capabilities[current_ptr]["name"] = "Power Management"

            elif cap_id == PCICapabilityID.PCI_EXPRESS.value:
                # PCI Express Capability
                if current_byte_offset + 8 <= len(cfg):
                    pcie_cap_bytes = cfg[
                        current_byte_offset + 4 : current_byte_offset + 8
                    ]
                    pcie_cap = int(pcie_cap_bytes, 16)
                    capabilities[current_ptr]["pcie_cap"] = pcie_cap
                    capabilities[current_ptr]["name"] = "PCI Express"

                    # Read Device Capabilities 2 (offset 0x24 from capability start)
                    dev_cap2_offset = current_ptr + 0x24
                    dev_cap2_byte_offset = dev_cap2_offset * 2
                    if dev_cap2_byte_offset + 8 <= len(cfg):
                        dev_cap2_bytes = cfg[
                            dev_cap2_byte_offset : dev_cap2_byte_offset + 8
                        ]
                        dev_cap2 = int(dev_cap2_bytes, 16)
                        capabilities[current_ptr]["dev_cap2"] = dev_cap2

            elif cap_id == PCICapabilityID.MSI_X.value:
                # MSI-X Capability
                if current_byte_offset + 8 <= len(cfg):
                    msix_control_bytes = cfg[
                        current_byte_offset + 4 : current_byte_offset + 8
                    ]
                    msix_control = int(msix_control_bytes, 16)
                    capabilities[current_ptr]["msix_control"] = msix_control
                    capabilities[current_ptr]["name"] = "MSI-X"

            elif cap_id == PCICapabilityID.MSI.value:
                # MSI Capability
                if current_byte_offset + 8 <= len(cfg):
                    msi_control_bytes = cfg[
                        current_byte_offset + 4 : current_byte_offset + 8
                    ]
                    msi_control = int(msi_control_bytes, 16)
                    capabilities[current_ptr]["msi_control"] = msi_control
                    capabilities[current_ptr]["name"] = "MSI"

            elif cap_id == PCICapabilityID.VENDOR_SPECIFIC.value:
                # Vendor-Specific Capability
                if current_byte_offset + 8 <= len(cfg):
                    vendor_bytes = cfg[
                        current_byte_offset + 4 : current_byte_offset + 8
                    ]
                    vendor_data = int(vendor_bytes, 16)
                    capabilities[current_ptr]["vendor_data"] = vendor_data
                    capabilities[current_ptr]["name"] = "Vendor-Specific"

            else:
                # Other capability
                capabilities[current_ptr]["name"] = f"Unknown (0x{cap_id:02x})"

            current_ptr = next_ptr
        except ValueError:
            logger.warning(f"Invalid capability data at offset {current_ptr:02x}")
            break

    return capabilities


def get_all_ext_capabilities(cfg: str) -> Dict[int, Dict]:
    """
    Get all extended capabilities in the PCI Express configuration space.

    Args:
        cfg: Configuration space as a hex string

    Returns:
        Dictionary mapping capability offsets to capability information
    """
    ext_capabilities = {}

    # Extended capabilities start at offset 0x100
    ext_cap_start = 0x100

    # Check if configuration space is valid and large enough
    if not cfg or len(cfg) < ext_cap_start * 2:
        logger.warning("Configuration space is too small for extended capabilities")
        return ext_capabilities

    # Walk the extended capabilities list
    current_ptr = ext_cap_start
    visited = set()  # To detect loops

    while current_ptr and current_ptr != 0 and current_ptr not in visited:
        visited.add(current_ptr)
        current_byte_offset = current_ptr * 2

        # Ensure we have enough data (at least 4 bytes for header)
        if current_byte_offset + 8 > len(cfg):
            logger.warning(
                f"Extended capability pointer {current_ptr:03x} is out of bounds"
            )
            break

        # Read extended capability ID and next pointer
        try:
            # Extended capability header is 4 bytes:
            # [31:16] = Capability ID
            # [15:4] = Capability Version
            # [3:0] = Next Capability Offset
            header_bytes = cfg[current_byte_offset : current_byte_offset + 8]

            # Extract the capability ID (first 2 bytes)
            try:
                cap_id = int(header_bytes[0:4], 16)

                # Extract the capability version and next pointer
                version_next = int(header_bytes[4:8], 16)
                cap_version = (version_next >> 4) & 0xF
                next_ptr = version_next & 0xFFF

                # Validate the capability ID - it should be a known extended capability ID
                # or at least have a reasonable value (not too large)
                if cap_id > 0x1000 or (cap_id == 0 and next_ptr != 0):
                    logger.warning(
                        f"Invalid extended capability ID: 0x{cap_id:04x} at offset 0x{current_ptr:03x}"
                    )
                    break
            except ValueError:
                logger.warning(
                    f"Invalid extended capability data at offset {current_ptr:03x}"
                )
                break

            # Store extended capability information
            ext_capabilities[current_ptr] = {
                "offset": current_ptr,
                "id": cap_id,
                "version": cap_version,
                "next_ptr": next_ptr,
                "type": "extended",
            }

            # Add capability-specific information
            if cap_id == PCIExtCapabilityID.ADVANCED_ERROR_REPORTING.value:
                ext_capabilities[current_ptr]["name"] = "Advanced Error Reporting"

            elif cap_id == PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value:
                ext_capabilities[current_ptr]["name"] = "SR-IOV"

            elif cap_id == PCIExtCapabilityID.LATENCY_TOLERANCE_REPORTING.value:
                ext_capabilities[current_ptr]["name"] = "LTR"

            elif cap_id == PCIExtCapabilityID.L1_PM_SUBSTATES.value:
                ext_capabilities[current_ptr]["name"] = "L1 PM Substates"

            else:
                ext_capabilities[current_ptr][
                    "name"
                ] = f"Unknown Extended (0x{cap_id:04x})"

            # If next pointer is 0, end of list
            if next_ptr == 0:
                break

            # Validate the next pointer - it should be within the extended config space
            # and greater than the current pointer to avoid loops
            if next_ptr < 0x100 or next_ptr >= 0x1000 or next_ptr <= current_ptr:
                logger.warning(
                    f"Invalid next pointer: 0x{next_ptr:03x} at offset 0x{current_ptr:03x}"
                )
                break

            current_ptr = next_ptr
        except ValueError:
            logger.warning(
                f"Invalid extended capability data at offset {current_ptr:03x}"
            )
            break

    return ext_capabilities


def categorize_capabilities(
    capabilities: Dict[int, Dict],
) -> Dict[int, EmulationCategory]:
    """
    Categorize capabilities based on emulation feasibility.

    Args:
        capabilities: Dictionary of capabilities (from get_all_capabilities or get_all_ext_capabilities)

    Returns:
        Dictionary mapping capability offsets to emulation categories
    """
    categories = {}

    for offset, cap in capabilities.items():
        cap_id = cap.get("id")
        cap_type = cap.get("type")

        if cap_type == "standard":
            # Categorize standard capabilities
            if cap_id == PCICapabilityID.POWER_MANAGEMENT.value:
                # Power Management - partially supported (only D0/D3hot)
                categories[offset] = EmulationCategory.PARTIALLY_SUPPORTED

            elif cap_id == PCICapabilityID.MSI.value:
                # MSI - fully supported
                categories[offset] = EmulationCategory.FULLY_SUPPORTED

            elif cap_id == PCICapabilityID.MSI_X.value:
                # MSI-X - fully supported
                categories[offset] = EmulationCategory.FULLY_SUPPORTED

            elif cap_id == PCICapabilityID.PCI_EXPRESS.value:
                # PCIe - partially supported (need to modify ASPM bits)
                categories[offset] = EmulationCategory.PARTIALLY_SUPPORTED

            elif cap_id == PCICapabilityID.VENDOR_SPECIFIC.value:
                # Vendor-specific - unsupported (device-specific behavior)
                categories[offset] = EmulationCategory.UNSUPPORTED

            else:
                # Unknown standard capability - unsupported
                categories[offset] = EmulationCategory.UNSUPPORTED

        elif cap_type == "extended":
            # Categorize extended capabilities
            if cap_id == PCIExtCapabilityID.ADVANCED_ERROR_REPORTING.value:
                # AER - partially supported
                categories[offset] = EmulationCategory.PARTIALLY_SUPPORTED

            elif cap_id == PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value:
                # SR-IOV - unsupported
                categories[offset] = EmulationCategory.UNSUPPORTED

            elif cap_id == PCIExtCapabilityID.LATENCY_TOLERANCE_REPORTING.value:
                # LTR - unsupported
                categories[offset] = EmulationCategory.UNSUPPORTED

            elif cap_id == PCIExtCapabilityID.L1_PM_SUBSTATES.value:
                # L1 PM Substates - unsupported
                categories[offset] = EmulationCategory.UNSUPPORTED

            else:
                # Unknown extended capability - unsupported
                categories[offset] = EmulationCategory.UNSUPPORTED

    return categories


def determine_pruning_actions(
    capabilities: Dict[int, Dict], categories: Dict[int, EmulationCategory]
) -> Dict[int, PruningAction]:
    """
    Determine pruning actions for each capability based on its category.

    Args:
        capabilities: Dictionary of capabilities
        categories: Dictionary mapping capability offsets to emulation categories

    Returns:
        Dictionary mapping capability offsets to pruning actions
    """
    actions = {}

    for offset, cap in capabilities.items():
        category = categories.get(offset, EmulationCategory.UNSUPPORTED)
        cap_id = cap.get("id")
        cap_type = cap.get("type")

        if category == EmulationCategory.FULLY_SUPPORTED:
            # Fully supported capabilities can be kept as-is
            actions[offset] = PruningAction.KEEP

        elif category == EmulationCategory.PARTIALLY_SUPPORTED:
            # Partially supported capabilities need modification
            actions[offset] = PruningAction.MODIFY

        elif category == EmulationCategory.UNSUPPORTED:
            # Unsupported capabilities should be removed
            actions[offset] = PruningAction.REMOVE

        elif category == EmulationCategory.CRITICAL:
            # Critical capabilities must be kept
            actions[offset] = PruningAction.KEEP

    return actions


def prune_capabilities(cfg: str, actions: Dict[int, PruningAction]) -> str:
    """
    Prune capabilities in the configuration space based on the specified actions.

    Args:
        cfg: Configuration space as a hex string
        actions: Dictionary mapping capability offsets to pruning actions

    Returns:
        Modified configuration space as a hex string
    """
    # Get all capabilities
    std_caps = get_all_capabilities(cfg)
    ext_caps = get_all_ext_capabilities(cfg)

    # Combine all capabilities
    all_caps = {**std_caps, **ext_caps}

    # Create a mutable list of characters from the configuration space
    cfg_chars = list(cfg)

    # Process standard capabilities
    std_cap_offsets = sorted(std_caps.keys())
    for i, offset in enumerate(std_cap_offsets):
        action = actions.get(offset, PruningAction.KEEP)
        cap = std_caps[offset]

        if action == PruningAction.REMOVE:
            # Remove the capability by updating the previous capability's next pointer
            if i > 0:
                prev_offset = std_cap_offsets[i - 1]
                next_ptr = cap["next_ptr"]

                # Update the next pointer of the previous capability
                prev_next_ptr_offset = (
                    prev_offset + 1
                ) * 2  # +1 for the next pointer byte
                prev_next_ptr_hex = f"{next_ptr:02x}"
                cfg_chars[prev_next_ptr_offset : prev_next_ptr_offset + 2] = (
                    prev_next_ptr_hex
                )
            else:
                # This is the first capability, update the capabilities pointer at 0x34
                cap_ptr_offset = 0x34 * 2
                next_ptr = cap["next_ptr"]
                next_ptr_hex = f"{next_ptr:02x}"
                cfg_chars[cap_ptr_offset : cap_ptr_offset + 2] = next_ptr_hex

        elif action == PruningAction.MODIFY:
            # Modify specific fields based on capability type
            if cap["id"] == PCICapabilityID.POWER_MANAGEMENT.value:
                # Modify Power Management Capability
                # Keep only D0 and D3hot support, clear PME support
                pm_cap_offset = (offset + 2) * 2  # +2 for the PM capabilities register
                pm_cap_bytes = cfg[pm_cap_offset : pm_cap_offset + 4]
                pm_cap = int(pm_cap_bytes, 16)

                # Clear all bits except D3hot
                pm_cap = 0x0008  # Set only D3hot support (bit 3)

                pm_cap_hex = f"{pm_cap:04x}"
                cfg_chars[pm_cap_offset : pm_cap_offset + 4] = pm_cap_hex

            elif cap["id"] == PCICapabilityID.PCI_EXPRESS.value:
                # Modify PCI Express Capability
                # Clear ASPM support in Link Control register
                link_control_offset = (
                    offset + 0x10
                ) * 2  # Link Control register offset
                if link_control_offset + 4 <= len(cfg):
                    link_control_bytes = cfg[
                        link_control_offset : link_control_offset + 4
                    ]
                    link_control = int(link_control_bytes, 16)

                    # Clear ASPM bits (bits 0-1)
                    link_control &= ~0x0003

                    link_control_hex = f"{link_control:04x}"
                    cfg_chars[link_control_offset : link_control_offset + 4] = (
                        link_control_hex
                    )

                # Clear OBFF and LTR bits in Device Control 2 register
                dev_control2_offset = (
                    offset + 0x28
                ) * 2  # Device Control 2 register offset
                if dev_control2_offset + 4 <= len(cfg):
                    dev_control2_bytes = cfg[
                        dev_control2_offset : dev_control2_offset + 4
                    ]
                    dev_control2 = int(dev_control2_bytes, 16)

                    # Clear OBFF Enable (bits 13-14) and LTR Enable (bit 10)
                    dev_control2 &= ~0x6400

                    dev_control2_hex = f"{dev_control2:04x}"
                    cfg_chars[dev_control2_offset : dev_control2_offset + 4] = (
                        dev_control2_hex
                    )

    # Process extended capabilities
    ext_cap_offsets = sorted(ext_caps.keys())

    # First pass: Identify capabilities to remove and build a new chain
    new_chain = []
    for offset in ext_cap_offsets:
        action = actions.get(offset, PruningAction.KEEP)
        if action != PruningAction.REMOVE:
            new_chain.append(offset)

    # Second pass: Update the capability chain
    if new_chain:
        # Update the chain pointers
        for i, offset in enumerate(new_chain):
            cap = ext_caps[offset]
            header_offset = offset * 2
            cap_id = cap["id"]
            cap_version = cap["version"]

            # Set the next pointer
            next_ptr = 0  # Default to end of list
            if i < len(new_chain) - 1:
                next_ptr = new_chain[i + 1]

            # Reconstruct the header with the new next pointer
            new_header = (cap_id << 16) | (cap_version << 4) | next_ptr
            new_header_hex = f"{new_header:08x}"

            cfg_chars[header_offset : header_offset + 8] = new_header_hex

    # Third pass: Zero out removed capabilities
    for offset in ext_cap_offsets:
        action = actions.get(offset, PruningAction.KEEP)
        if action == PruningAction.REMOVE:
            # Zero out the entire capability
            header_offset = offset * 2
            cfg_chars[header_offset : header_offset + 8] = "00000000"

            # Then zero out the rest of the capability (assume it's at least 4 DWORDs)
            for j in range(4, 24, 4):  # Most capabilities are at least 4 DWORDs
                field_offset = (offset + j // 2) * 2
                if field_offset + 8 <= len(cfg):
                    cfg_chars[field_offset : field_offset + 8] = "00000000"

        elif action == PruningAction.MODIFY:
            # Modify specific fields based on extended capability type
            if cap["id"] == PCIExtCapabilityID.L1_PM_SUBSTATES.value:
                # Zero out the entire L1 PM Substates capability
                # Just keep the header with next pointer
                header_offset = offset * 2
                header_bytes = cfg[header_offset : header_offset + 8]
                header = int(header_bytes, 16)

                # If this is the last extended capability, set next pointer to 0
                if cap["next_ptr"] == 0:
                    # Keep the ID and version, set next pointer to 0
                    new_header = (cap["id"] << 16) | (cap["version"] << 4) | 0
                    new_header_hex = f"{new_header:08x}"
                    cfg_chars[header_offset : header_offset + 8] = new_header_hex

                # Zero out all other fields
                for i in range(4, 24, 4):  # L1 PM Substates is typically 6 DWORDs
                    field_offset = (offset + i // 2) * 2
                    if field_offset + 8 <= len(cfg):
                        cfg_chars[field_offset : field_offset + 8] = "00000000"

    # Reconstruct the configuration space
    return "".join(cfg_chars)


def prune_capabilities_by_rules(cfg: str) -> str:
    """
    Prune capabilities in the configuration space based on predefined rules.

    Args:
        cfg: Configuration space as a hex string

    Returns:
        Modified configuration space as a hex string
    """
    # Get all capabilities
    std_caps = get_all_capabilities(cfg)
    ext_caps = get_all_ext_capabilities(cfg)

    # Categorize capabilities
    std_categories = categorize_capabilities(std_caps)
    ext_categories = categorize_capabilities(ext_caps)

    # Determine pruning actions
    std_actions = determine_pruning_actions(std_caps, std_categories)
    ext_actions = determine_pruning_actions(ext_caps, ext_categories)

    # Combine actions
    all_actions = {**std_actions, **ext_actions}

    # Apply pruning
    pruned_cfg = prune_capabilities(cfg, all_actions)

    # Return the pruned configuration space
    return pruned_cfg
