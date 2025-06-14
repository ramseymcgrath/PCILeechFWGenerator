#!/usr/bin/env python3
"""
PCI Capability Analysis and Pruning

This module provides functionality to analyze and prune PCI capabilities
in the configuration space of a donor device. It supports both standard
and extended capabilities, and implements specific pruning rules for
capabilities that cannot be faithfully emulated.

Refactored with enhanced validation, safety checks, and performance improvements.
"""

import logging
from enum import Enum, auto
from typing import Dict, List, NamedTuple, Optional, Tuple

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration for the PCI capability module.

    Args:
        verbose: If True, enables DEBUG level logging. Otherwise uses INFO level.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


class PatchInfo(NamedTuple):
    """Information about a capability patch operation."""

    offset: int
    action: str
    before_bytes: str
    after_bytes: str


# PCI Standard Capability IDs
class PCICapabilityID(Enum):
    """Standard PCI Capability IDs as defined in the PCI specification."""

    # Missing standard IDs added as requested
    AGP = 0x02
    VPD = 0x03
    SLOT_ID = 0x04
    POWER_MANAGEMENT = 0x01
    MSI = 0x05
    COMPACT_PCI_HOT_SWAP = 0x06
    PCI_X = 0x07
    HYPERTRANSPORT = 0x08
    VENDOR_SPECIFIC = 0x09
    DEBUG_PORT = 0x0A
    COMPACT_PCI_CRC = 0x0B
    PCI_HOT_PLUG = 0x0C
    PCI_BRIDGE_SUBSYSTEM_VID = 0x0D
    AGP_8X = 0x0E
    SECURE_DEVICE = 0x0F
    PCI_EXPRESS = 0x10
    MSI_X = 0x11
    SATA_DATA_INDEX_CONF = 0x12
    AF = 0x13  # Advanced Features


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
    VF_RESIZABLE_BAR = 0x0024
    DATA_LINK_FEATURE = 0x0025
    PHYSICAL_LAYER_16_0_GT_S = 0x0026
    LANE_MARGINING_AT_RECEIVER = 0x0027
    HIERARCHY_ID = 0x0028
    NATIVE_PCIE_ENCLOSURE_MANAGEMENT = 0x0029


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


def _validate_cfg_string(cfg: str) -> bool:
    """
    Validate that the configuration string meets basic requirements.

    Args:
        cfg: Configuration space as a hex string

    Returns:
        True if valid, False otherwise
    """
    if not cfg:
        logger.error("Configuration string is empty")
        return False

    if len(cfg) % 2 != 0:
        logger.error(f"Configuration string length {len(cfg)} is odd")
        return False

    if len(cfg) < 256 * 2:  # 256 bytes minimum
        logger.error(
            f"Configuration string length {len(cfg)} is less than 512 hex chars (256 bytes)"
        )
        return False

    try:
        # Validate it's proper hex
        int(cfg, 16)
    except ValueError:
        logger.error("Configuration string contains invalid hex characters")
        return False

    return True


def _have(cfg: str, byte_ofs: int, nbytes: int) -> bool:
    """
    Check if the configuration space has enough data at the specified offset.

    Args:
        cfg: Configuration space as a hex string
        byte_ofs: Byte offset to check
        nbytes: Number of bytes needed

    Returns:
        True if enough data is available, False otherwise
    """
    hex_ofs = byte_ofs * 2
    hex_len = nbytes * 2
    return hex_ofs + hex_len <= len(cfg)


def _is_two_byte_header_cap(cap_id: int) -> bool:
    """
    Check if a standard capability has a 2-byte header instead of 1-byte.

    Args:
        cap_id: Standard capability ID

    Returns:
        True if capability has 2-byte header, False for 1-byte header
    """
    # PCI-X and Slot ID capabilities have 2-byte headers
    return cap_id in [PCICapabilityID.PCI_X.value, PCICapabilityID.SLOT_ID.value]


def find_cap(cfg: str, cap_id: int) -> Optional[int]:
    """
    Find a standard capability in the PCI configuration space.

    Args:
        cfg: Configuration space as a hex string
        cap_id: Capability ID to find

    Returns:
        Offset of the capability in the configuration space, or None if not found
    """
    if not _validate_cfg_string(cfg):
        return None

    # Check if capabilities are supported (Status register bit 4)
    if not _have(cfg, 0x06, 2):
        logger.warning("Status register not found in configuration space")
        return None

    try:
        status_bytes = cfg[0x06 * 2 : 0x06 * 2 + 4]
        status = int(status_bytes, 16)
        if not (status & 0x10):  # Check capabilities bit
            logger.info("Device does not support capabilities")
            return None
    except ValueError:
        logger.warning(f"Invalid status register value: {status_bytes}")
        return None

    # Get capabilities pointer (offset 0x34)
    if not _have(cfg, 0x34, 1):
        logger.warning("Capabilities pointer not found in configuration space")
        return None

    try:
        cap_ptr_bytes = cfg[0x34 * 2 : 0x34 * 2 + 2]
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

    while current_ptr != 0 and current_ptr not in visited:
        if not _have(cfg, current_ptr, 2):
            logger.warning(f"Capability pointer {current_ptr:02x} is out of bounds")
            return None

        visited.add(current_ptr)
        current_byte_offset = current_ptr * 2

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
    if not _validate_cfg_string(cfg):
        return None

    # Extended capabilities start at offset 0x100
    ext_cap_start = 0x100

    # Check if configuration space is valid and large enough
    if not _have(cfg, ext_cap_start, 4):
        logger.warning("Configuration space is too small for extended capabilities")
        return None

    # Walk the extended capabilities list
    current_ptr = ext_cap_start
    visited = set()  # To detect loops

    while current_ptr != 0 and current_ptr not in visited:
        if not _have(cfg, current_ptr, 4):
            logger.warning(
                f"Extended capability pointer {current_ptr:03x} is out of bounds"
            )
            return None

        # Check DWORD alignment for extended caps
        if current_ptr & 0x3 != 0:
            logger.warning(
                f"Extended capability pointer {current_ptr:03x} is not DWORD aligned"
            )
            return None

        visited.add(current_ptr)
        current_byte_offset = current_ptr * 2

        # Read extended capability ID and next pointer
        try:
            header_bytes = cfg[current_byte_offset : current_byte_offset + 8]

            # Check if the header is all zeros (capability has been removed)
            if header_bytes == "00000000":
                break

            # Extract the capability ID and other fields from 32-bit header
            header_val = int(header_bytes, 16)
            current_cap_id = header_val & 0xFFFF
            cap_version = (header_val >> 16) & 0xF
            next_ptr = (header_val >> 20) & 0xFFF

            # Skip if capability ID is 0 (removed capability)
            if current_cap_id == 0:
                break

            if current_cap_id == cap_id:
                return current_ptr

            # Break before adding to visited when next_ptr == 0
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

    if not _validate_cfg_string(cfg):
        return capabilities

    # Check if capabilities are supported (Status register bit 4)
    if not _have(cfg, 0x06, 2):
        logger.warning("Status register not found in configuration space")
        return capabilities

    try:
        status_bytes = cfg[0x06 * 2 : 0x06 * 2 + 4]
        status = int(status_bytes, 16)
        if not (status & 0x10):  # Check capabilities bit
            logger.info("Device does not support capabilities")
            return capabilities
    except ValueError:
        logger.warning(f"Invalid status register value: {status_bytes}")
        return capabilities

    # Get capabilities pointer (offset 0x34)
    if not _have(cfg, 0x34, 1):
        logger.warning("Capabilities pointer not found in configuration space")
        return capabilities

    try:
        cap_ptr_bytes = cfg[0x34 * 2 : 0x34 * 2 + 2]
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

    while current_ptr != 0 and current_ptr not in visited:
        if not _have(cfg, current_ptr, 2):
            logger.warning(f"Capability pointer {current_ptr:02x} is out of bounds")
            break

        visited.add(current_ptr)
        current_byte_offset = current_ptr * 2

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
                "name": _get_standard_cap_name(cap_id),
            }

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

    if not _validate_cfg_string(cfg):
        return ext_capabilities

    # Extended capabilities start at offset 0x100
    ext_cap_start = 0x100

    # Check if configuration space is valid and large enough
    if not _have(cfg, ext_cap_start, 4):
        logger.warning("Configuration space is too small for extended capabilities")
        return ext_capabilities

    # Walk the extended capabilities list
    current_ptr = ext_cap_start
    visited = set()  # To detect loops

    while current_ptr != 0 and current_ptr not in visited:
        if not _have(cfg, current_ptr, 4):
            logger.warning(
                f"Extended capability pointer {current_ptr:03x} is out of bounds"
            )
            break

        # Check DWORD alignment for extended caps
        if current_ptr & 0x3 != 0:
            logger.warning(
                f"Extended capability pointer {current_ptr:03x} is not DWORD aligned"
            )
            break

        visited.add(current_ptr)
        current_byte_offset = current_ptr * 2

        # Read extended capability ID and next pointer
        try:
            header_bytes = cfg[current_byte_offset : current_byte_offset + 8]

            # Extract the capability ID and other fields
            header_val = int(header_bytes, 16)
            cap_id = header_val & 0xFFFF
            cap_version = (header_val >> 16) & 0xF
            next_ptr = (header_val >> 20) & 0xFFF

            # Skip if capability ID is 0 (removed capability)
            if cap_id == 0:
                break

            # Store extended capability information
            ext_capabilities[current_ptr] = {
                "offset": current_ptr,
                "id": cap_id,
                "version": cap_version,
                "next_ptr": next_ptr,
                "type": "extended",
                "name": _get_extended_cap_name(cap_id),
            }

            # Break before adding to visited when next_ptr == 0
            if next_ptr == 0:
                break

            current_ptr = next_ptr
        except ValueError:
            logger.warning(
                f"Invalid extended capability data at offset {current_ptr:03x}"
            )
            break

    return ext_capabilities


def _get_standard_cap_name(cap_id: int) -> str:
    """Get the name of a standard capability."""
    cap_names = {
        0x01: "Power Management",
        0x02: "AGP",
        0x03: "VPD",
        0x04: "Slot ID",
        0x05: "MSI",
        0x06: "CompactPCI Hot Swap",
        0x07: "PCI-X",
        0x08: "HyperTransport",
        0x09: "Vendor-Specific",
        0x0A: "Debug Port",
        0x0B: "CompactPCI CRC",
        0x0C: "PCI Hot Plug",
        0x0D: "PCI Bridge Subsystem VID",
        0x0E: "AGP 8x",
        0x0F: "Secure Device",
        0x10: "PCI Express",
        0x11: "MSI-X",
        0x12: "SATA Data Index Conf",
        0x13: "Advanced Features",
    }
    return cap_names.get(cap_id, f"Unknown (0x{cap_id:02x})")


def _get_extended_cap_name(cap_id: int) -> str:
    """Get the name of an extended capability."""
    cap_names = {
        0x0001: "Advanced Error Reporting",
        0x0002: "Virtual Channel",
        0x0003: "Device Serial Number",
        0x0004: "Power Budgeting",
        0x0005: "Root Complex Link Declaration",
        0x0006: "Root Complex Internal Link Control",
        0x0007: "Root Complex Event Collector Endpoint Association",
        0x0008: "Multi-Function Virtual Channel",
        0x0009: "Virtual Channel (MFVC)",
        0x000A: "Root Complex Register Block",
        0x000B: "Vendor-Specific Extended",
        0x000C: "Config Access Correlation",
        0x000D: "Access Control Services",
        0x000E: "Alternative Routing-ID Interpretation",
        0x000F: "Address Translation Services",
        0x0010: "Single Root I/O Virtualization",
        0x0011: "Multi-Root I/O Virtualization",
        0x0012: "Multicast",
        0x0013: "Page Request",
        0x0014: "Reserved for AMD",
        0x0015: "Resizable BAR",
        0x0016: "Dynamic Power Allocation",
        0x0017: "TPH Requester",
        0x0018: "Latency Tolerance Reporting",
        0x0019: "Secondary PCI Express",
        0x001A: "Protocol Multiplexing",
        0x001B: "Process Address Space ID",
        0x001C: "LN Requester",
        0x001D: "Downstream Port Containment",
        0x001E: "L1 PM Substates",
        0x001F: "Precision Time Measurement",
        0x0020: "PCI Express over M-PHY",
        0x0021: "FRS Queueing",
        0x0022: "Readiness Time Reporting",
        0x0023: "Designated Vendor-Specific",
        0x0024: "VF Resizable BAR",
        0x0025: "Data Link Feature",
        0x0026: "Physical Layer 16.0 GT/s",
        0x0027: "Lane Margining at Receiver",
        0x0028: "Hierarchy ID",
        0x0029: "Native PCIe Enclosure Management",
    }
    name = cap_names.get(cap_id, f"Unknown Extended (0x{cap_id:04x})")
    if cap_id not in cap_names and cap_id <= 0x0029:
        logger.info(f"Unknown capability ID 0x{cap_id:04x} encountered")
    return name


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
                categories[offset] = EmulationCategory.PARTIALLY_SUPPORTED
            elif cap_id == PCICapabilityID.MSI.value:
                categories[offset] = EmulationCategory.FULLY_SUPPORTED
            elif cap_id == PCICapabilityID.MSI_X.value:
                categories[offset] = EmulationCategory.FULLY_SUPPORTED
            elif cap_id == PCICapabilityID.PCI_EXPRESS.value:
                categories[offset] = EmulationCategory.PARTIALLY_SUPPORTED
            elif cap_id in [
                PCICapabilityID.AGP.value,
                PCICapabilityID.VPD.value,
                PCICapabilityID.SLOT_ID.value,
                PCICapabilityID.PCI_X.value,
                PCICapabilityID.AF.value,
                PCICapabilityID.VENDOR_SPECIFIC.value,
            ]:
                categories[offset] = EmulationCategory.UNSUPPORTED
            else:
                # Unknown standard capability - unsupported
                categories[offset] = EmulationCategory.UNSUPPORTED

        elif cap_type == "extended":
            # Categorize extended capabilities
            if cap_id == PCIExtCapabilityID.ADVANCED_ERROR_REPORTING.value:
                categories[offset] = EmulationCategory.PARTIALLY_SUPPORTED
            elif cap_id == PCIExtCapabilityID.ACCESS_CONTROL_SERVICES.value:
                # ACS - partially supported as requested
                categories[offset] = EmulationCategory.PARTIALLY_SUPPORTED
            elif cap_id == PCIExtCapabilityID.DOWNSTREAM_PORT_CONTAINMENT.value:
                # DPC - partially supported as requested
                categories[offset] = EmulationCategory.PARTIALLY_SUPPORTED
            elif cap_id == PCIExtCapabilityID.RESIZABLE_BAR.value:
                categories[offset] = EmulationCategory.PARTIALLY_SUPPORTED
            else:
                # All other extended capabilities - unsupported
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

        if category == EmulationCategory.FULLY_SUPPORTED:
            actions[offset] = PruningAction.KEEP
        elif category == EmulationCategory.PARTIALLY_SUPPORTED:
            actions[offset] = PruningAction.MODIFY
        elif category == EmulationCategory.UNSUPPORTED:
            actions[offset] = PruningAction.REMOVE
        elif category == EmulationCategory.CRITICAL:
            actions[offset] = PruningAction.KEEP

    return actions


def _get_capability_patches(
    cfg_bytes: bytearray, actions: Dict[int, PruningAction]
) -> List[PatchInfo]:
    """
    Generate a list of patches for capability modifications.

    Args:
        cfg_bytes: Configuration space as a bytearray
        actions: Dictionary mapping capability offsets to pruning actions

    Returns:
        List of PatchInfo objects describing the changes
    """
    patches = []

    # Convert back to hex string for existing functions
    cfg = cfg_bytes.hex()

    # Get all capabilities
    std_caps = get_all_capabilities(cfg)
    ext_caps = get_all_ext_capabilities(cfg)

    # Process standard capabilities
    std_cap_offsets = sorted(std_caps.keys())
    for i, offset in enumerate(std_cap_offsets):
        action = actions.get(offset, PruningAction.KEEP)
        cap = std_caps[offset]

        if action == PruningAction.REMOVE:
            # Record the removal patch
            before_bytes = cfg_bytes[offset : offset + 2].hex()
            patches.append(PatchInfo(offset, "REMOVE_STD_CAP", before_bytes, "0000"))

            # Update pointer chain
            if i > 0:
                prev_offset = std_cap_offsets[i - 1]
                next_ptr = cap["next_ptr"]

                # Detect header size for previous capability
                prev_cap = std_caps[prev_offset]
                header_offset_adj = 2 if _is_two_byte_header_cap(prev_cap["id"]) else 1

                ptr_offset = prev_offset + header_offset_adj
                before_bytes = cfg_bytes[ptr_offset : ptr_offset + 1].hex()
                patches.append(
                    PatchInfo(
                        ptr_offset, "UPDATE_STD_PTR", before_bytes, f"{next_ptr:02x}"
                    )
                )
            else:
                # Update capabilities pointer at 0x34
                next_ptr = cap["next_ptr"]
                before_bytes = cfg_bytes[0x34:0x35].hex()
                patches.append(
                    PatchInfo(0x34, "UPDATE_CAP_PTR", before_bytes, f"{next_ptr:02x}")
                )

                # Zero the original 2-byte header of first cap
                before_bytes = cfg_bytes[offset : offset + 2].hex()
                patches.append(
                    PatchInfo(offset, "ZERO_FIRST_CAP_HEADER", before_bytes, "0000")
                )

        elif action == PruningAction.MODIFY:
            # Record modification patches based on capability type
            if cap["id"] == PCICapabilityID.POWER_MANAGEMENT.value:
                pm_cap_offset = offset + 2
                before_bytes = cfg_bytes[pm_cap_offset : pm_cap_offset + 2].hex()
                patches.append(
                    PatchInfo(pm_cap_offset, "MODIFY_PM_CAP", before_bytes, "0008")
                )

    # Process extended capabilities
    ext_cap_offsets = sorted(ext_caps.keys())
    for offset in ext_cap_offsets:
        action = actions.get(offset, PruningAction.KEEP)
        cap = ext_caps[offset]

        if action == PruningAction.REMOVE:
            # Find the range to zero
            next_cap_offset = 0x1000  # Default to end of extended config space
            for other_offset in ext_cap_offsets:
                if other_offset > offset:
                    next_cap_offset = other_offset
                    break

            zero_len = next_cap_offset - offset
            before_bytes = cfg_bytes[offset : offset + zero_len].hex()
            after_bytes = "00" * zero_len
            patches.append(
                PatchInfo(offset, "REMOVE_EXT_CAP", before_bytes, after_bytes)
            )

        elif action == PruningAction.MODIFY:
            if cap["id"] == PCIExtCapabilityID.ACCESS_CONTROL_SERVICES.value:
                # ACS - keep header + control regs, zero feature bits
                control_offset = offset + 6  # ACS Control Register
                before_bytes = cfg_bytes[control_offset : control_offset + 2].hex()
                # Clear feature bits but keep control structure
                patches.append(
                    PatchInfo(control_offset, "MODIFY_ACS", before_bytes, "0000")
                )

            elif cap["id"] == PCIExtCapabilityID.DOWNSTREAM_PORT_CONTAINMENT.value:
                # DPC - similar to ACS
                control_offset = offset + 6  # DPC Control Register
                before_bytes = cfg_bytes[control_offset : control_offset + 2].hex()
                patches.append(
                    PatchInfo(control_offset, "MODIFY_DPC", before_bytes, "0000")
                )

            elif cap["id"] == PCIExtCapabilityID.RESIZABLE_BAR.value:
                # Resizable BAR - clamp size bits to 128 MB and below
                cap_offset = offset + 8  # First BAR capability register
                if cap_offset + 4 <= len(cfg_bytes):
                    before_bytes = cfg_bytes[cap_offset : cap_offset + 4].hex()
                    # Read current value and clamp size bits
                    current_val = int.from_bytes(
                        cfg_bytes[cap_offset : cap_offset + 4], "little"
                    )
                    # Clear size bits above 128MB (bit 27 and above)
                    clamped_val = current_val & 0xF7FFFFFF  # Clear bits 27-31
                    after_bytes = clamped_val.to_bytes(4, "little").hex()
                    patches.append(
                        PatchInfo(cap_offset, "MODIFY_RBAR", before_bytes, after_bytes)
                    )

    return patches


def prune_capabilities(cfg: str, actions: Dict[int, PruningAction]) -> str:
    """
    Prune capabilities in the configuration space based on the specified actions.
    Uses bytearray for improved performance.

    Args:
        cfg: Configuration space as a hex string
        actions: Dictionary mapping capability offsets to pruning actions

    Returns:
        Modified configuration space as a hex string
    """
    if not _validate_cfg_string(cfg):
        return cfg

    # Parse cfg once into bytearray for performance
    try:
        cfg_bytes = bytearray.fromhex(cfg)
    except ValueError:
        logger.error("Failed to parse configuration string as hex")
        return cfg

    # Get all capabilities
    std_caps = get_all_capabilities(cfg)
    ext_caps = get_all_ext_capabilities(cfg)

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

                # Detect header size for previous capability
                prev_cap = std_caps[prev_offset]
                header_offset_adj = 2 if _is_two_byte_header_cap(prev_cap["id"]) else 1

                # Update the next pointer of the previous capability
                ptr_offset = prev_offset + header_offset_adj
                cfg_bytes[ptr_offset] = next_ptr
            else:
                # This is the first capability, update the capabilities pointer at 0x34
                next_ptr = cap["next_ptr"]
                cfg_bytes[0x34] = next_ptr

                # Zero the original 2-byte header of the first cap
                cfg_bytes[offset : offset + 2] = b"\x00\x00"

        elif action == PruningAction.MODIFY:
            # Modify specific fields based on capability type
            if cap["id"] == PCICapabilityID.POWER_MANAGEMENT.value:
                # Modify Power Management Capability
                # Keep only D0 and D3hot support, clear PME support
                pm_cap_offset = offset + 2
                if pm_cap_offset + 2 <= len(cfg_bytes):
                    # Set only D3hot support (bit 3)
                    cfg_bytes[pm_cap_offset : pm_cap_offset + 2] = (0x0008).to_bytes(
                        2, "little"
                    )

            elif cap["id"] == PCICapabilityID.PCI_EXPRESS.value:
                # Modify PCI Express Capability
                # Clear ASPM support in Link Control register
                link_control_offset = offset + 0x10
                if link_control_offset + 2 <= len(cfg_bytes):
                    link_control = int.from_bytes(
                        cfg_bytes[link_control_offset : link_control_offset + 2],
                        "little",
                    )
                    # Clear ASPM bits (bits 0-1)
                    link_control &= ~0x0003
                    cfg_bytes[link_control_offset : link_control_offset + 2] = (
                        link_control.to_bytes(2, "little")
                    )

                # Clear OBFF and LTR bits in Device Control 2 register
                dev_control2_offset = offset + 0x28
                if dev_control2_offset + 2 <= len(cfg_bytes):
                    dev_control2 = int.from_bytes(
                        cfg_bytes[dev_control2_offset : dev_control2_offset + 2],
                        "little",
                    )
                    # Clear OBFF Enable (bits 13-14) and LTR Enable (bit 10)
                    dev_control2 &= ~0x6400
                    cfg_bytes[dev_control2_offset : dev_control2_offset + 2] = (
                        dev_control2.to_bytes(2, "little")
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
            header_offset = offset
            cap_id = cap["id"]
            cap_version = cap["version"]

            # Set the next pointer
            next_ptr = 0  # Default to end of list
            if i < len(new_chain) - 1:
                next_ptr = new_chain[i + 1]

            # Reconstruct the header with the new next pointer
            new_header = (next_ptr << 20) | (cap_version << 16) | cap_id
            cfg_bytes[header_offset : header_offset + 4] = new_header.to_bytes(
                4, "little"
            )

    # Third pass: Zero out removed capabilities and apply modifications
    for offset in ext_cap_offsets:
        action = actions.get(offset, PruningAction.KEEP)
        cap = ext_caps[offset]

        if action == PruningAction.REMOVE:
            # Find the range to zero - from this cap to the next cap or end of extended space
            next_cap_offset = 0x1000  # Default to end of extended config space
            for other_offset in ext_cap_offsets:
                if other_offset > offset:
                    next_cap_offset = other_offset
                    break

            # Zero out from header through the byte before the next capability
            zero_len = next_cap_offset - offset
            cfg_bytes[offset : offset + zero_len] = b"\x00" * zero_len

        elif action == PruningAction.MODIFY:
            # Modify specific fields based on extended capability type
            if cap["id"] == PCIExtCapabilityID.ACCESS_CONTROL_SERVICES.value:
                # ACS - keep header + control regs, zero feature bits
                control_offset = offset + 6  # ACS Control Register
                if control_offset + 2 <= len(cfg_bytes):
                    # Clear feature bits but keep control structure
                    cfg_bytes[control_offset : control_offset + 2] = b"\x00\x00"

            elif cap["id"] == PCIExtCapabilityID.DOWNSTREAM_PORT_CONTAINMENT.value:
                # DPC - similar to ACS
                control_offset = offset + 6  # DPC Control Register
                if control_offset + 2 <= len(cfg_bytes):
                    cfg_bytes[control_offset : control_offset + 2] = b"\x00\x00"

            elif cap["id"] == PCIExtCapabilityID.RESIZABLE_BAR.value:
                # Resizable BAR - clamp size bits to 128 MB and below
                cap_reg_offset = offset + 8  # First BAR capability register
                if cap_reg_offset + 4 <= len(cfg_bytes):
                    current_val = int.from_bytes(
                        cfg_bytes[cap_reg_offset : cap_reg_offset + 4], "little"
                    )
                    # Clear size bits above 128MB (bit 27 and above)
                    clamped_val = current_val & 0xF7FFFFFF  # Clear bits 27-31
                    cfg_bytes[cap_reg_offset : cap_reg_offset + 4] = (
                        clamped_val.to_bytes(4, "little")
                    )

    # Write back with cfg_bytes.hex() at the end
    return cfg_bytes.hex()


def get_capability_patches(
    cfg: str, actions: Dict[int, PruningAction]
) -> List[PatchInfo]:
    """
    Get a list of patches that would be applied for capability modifications.
    Helper function for easier unit testing.

    Args:
        cfg: Configuration space as a hex string
        actions: Dictionary mapping capability offsets to pruning actions

    Returns:
        List of PatchInfo objects describing the changes that would be made
    """
    if not _validate_cfg_string(cfg):
        return []

    try:
        cfg_bytes = bytearray.fromhex(cfg)
    except ValueError:
        logger.error("Failed to parse configuration string as hex")
        return []

    return _get_capability_patches(cfg_bytes, actions)


def prune_capabilities_by_rules(cfg: str) -> str:
    """
    Prune capabilities in the configuration space based on predefined rules.
    This is a wrapper around the new implementation that maintains backward compatibility.

    Args:
        cfg: Configuration space as a hex string

    Returns:
        Modified configuration space as a hex string
    """
    if not _validate_cfg_string(cfg):
        return cfg

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

    # Apply pruning using the new implementation
    pruned_cfg = prune_capabilities(cfg, all_actions)

    return pruned_cfg
