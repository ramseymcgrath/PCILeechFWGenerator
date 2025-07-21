#!/usr/bin/env python3
"""
MSI-X Capability Handler

This module provides MSI-X specific operations that integrate with the existing
MSI-X capability functionality while leveraging the new ConfigSpace and
CapabilityWalker infrastructure. It maintains compatibility with existing
MSI-X functionality and provides enhanced categorization through the rule engine.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

try:
    from ..string_utils import (
        log_debug_safe,
        log_error_safe,
        log_info_safe,
        log_warning_safe,
        safe_format,
    )
except ImportError:
    # Fallback for script execution
    import sys
    from pathlib import Path

    src_dir = Path(__file__).parent.parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    from string_utils import safe_format

from .constants import PCI_CAP_ID_OFFSET, PCI_CAP_NEXT_PTR_OFFSET
from .core import CapabilityWalker, ConfigSpace
from .patches import BinaryPatch, PatchEngine
from .rules import RuleEngine
from .types import (
    CapabilityInfo,
    CapabilityType,
    EmulationCategory,
    PCICapabilityID,
    PruningAction,
)

logger = logging.getLogger(__name__)


class MSIXCapabilityHandler:
    """
    Handler for MSI-X capability specific operations.

    This class provides specialized functionality for MSI-X capabilities,
    including integration with existing MSI-X parsing functionality,
    enhanced categorization through the rule engine, and efficient
    modification operations.
    """

    def __init__(
        self, config_space: ConfigSpace, rule_engine: Optional[RuleEngine] = None
    ) -> None:
        """
        Initialize MSI-X capability handler.

        Args:
            config_space: ConfigSpace instance to work with
            rule_engine: Optional RuleEngine for categorization
        """
        self.config_space = config_space
        self.rule_engine = rule_engine or RuleEngine()
        self.walker = CapabilityWalker(config_space)

    def find_msix_capabilities(self) -> List[CapabilityInfo]:
        """
        Find all MSI-X capabilities in the configuration space.

        Returns:
            List of CapabilityInfo objects for MSI-X capabilities
        """
        msix_capabilities = []

        for cap_info in self.walker.walk_standard_capabilities():
            if cap_info.cap_id == PCICapabilityID.MSI_X.value:
                msix_capabilities.append(cap_info)

        log_debug_safe(
            logger,
            "Found {count} MSI-X capabilities",
            prefix="PCI_CAP",
            count=len(msix_capabilities),
        )
        return msix_capabilities

    def get_msix_capability_info(self, offset: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an MSI-X capability.

        Args:
            offset: Offset of the MSI-X capability

        Returns:
            Dictionary with MSI-X capability details, or None if invalid
        """
        if not self.config_space.has_data(offset, 4):
            log_warning_safe(
                logger,
                "MSI-X capability at offset 0x{offset:02x} is truncated",
                prefix="PCI_CAP",
                offset=offset,
            )
            return None

        try:
            # Read MSI-X capability header
            cap_id = self.config_space.read_byte(offset + PCI_CAP_ID_OFFSET)
            next_ptr = self.config_space.read_byte(offset + PCI_CAP_NEXT_PTR_OFFSET)

            if cap_id != PCICapabilityID.MSI_X.value:
                log_warning_safe(
                    logger,
                    safe_format(
                        "Expected MSI-X capability (0x11) at offset 0x{offset:02x}, found 0x{cap_id:02x}",
                        offset=offset,
                        cap_id=cap_id,
                    ),
                    prefix="PCI_CAP",
                )
                return None

            # Read MSI-X Message Control register
            message_control = self.config_space.read_word(offset + 2)

            # Extract fields from Message Control
            table_size = (
                message_control & 0x07FF
            ) + 1  # Bits 0-10, add 1 for actual size
            function_mask = bool(message_control & 0x4000)  # Bit 14
            msix_enable = bool(message_control & 0x8000)  # Bit 15

            # Read Table Offset/BIR register
            table_offset_bir = self.config_space.read_dword(offset + 4)
            table_bir = table_offset_bir & 0x7  # Bits 0-2
            table_offset = table_offset_bir & 0xFFFFFFF8  # Bits 3-31

            # Read PBA Offset/BIR register
            pba_offset_bir = self.config_space.read_dword(offset + 8)
            pba_bir = pba_offset_bir & 0x7  # Bits 0-2
            pba_offset = pba_offset_bir & 0xFFFFFFF8  # Bits 3-31

            return {
                "offset": offset,
                "cap_id": cap_id,
                "next_ptr": next_ptr,
                "table_size": table_size,
                "function_mask": function_mask,
                "msix_enable": msix_enable,
                "table_bir": table_bir,
                "table_offset": table_offset,
                "pba_bir": pba_bir,
                "pba_offset": pba_offset,
                "message_control": message_control,
                "table_offset_bir": table_offset_bir,
                "pba_offset_bir": pba_offset_bir,
            }

        except (IndexError, ValueError) as e:
            log_error_safe(
                logger,
                safe_format(
                    "Failed to read MSI-X capability at offset 0x{offset:02x}: {e}",
                    offset=offset,
                    e=e,
                ),
            )
            return None

    def categorize_msix_capability(
        self, cap_info: CapabilityInfo, device_context: Optional[Dict[str, Any]] = None
    ) -> EmulationCategory:
        """
        Categorize an MSI-X capability using the rule engine.

        Args:
            cap_info: MSI-X capability information
            device_context: Optional device context for rule evaluation

        Returns:
            EmulationCategory for the MSI-X capability
        """
        return self.rule_engine.categorize_capability(
            cap_info, self.config_space, device_context
        )

    def create_msix_disable_patch(self, offset: int) -> Optional[BinaryPatch]:
        """
        Create a patch to disable an MSI-X capability.

        Args:
            offset: Offset of the MSI-X capability

        Returns:
            BinaryPatch to disable MSI-X, or None if failed
        """
        msix_info = self.get_msix_capability_info(offset)
        if not msix_info:
            return None

        # Create patch to clear MSI-X Enable bit (bit 15) in Message Control
        message_control = msix_info["message_control"]
        new_message_control = message_control & ~0x8000  # Clear bit 15

        if message_control == new_message_control:
            log_debug_safe(
                logger,
                "MSI-X at offset 0x{offset:02x} is already disabled",
                prefix="PCI_CAP",
                offset=offset,
            )
            return None

        patch = BinaryPatch(
            offset + 2,  # Message Control register offset
            message_control.to_bytes(2, "little"),
            new_message_control.to_bytes(2, "little"),
            safe_format(
                "Disable MSI-X at offset 0x{offset:02x}",
                offset=offset,
            ),
        )

        return patch

    def create_msix_table_size_patch(
        self, offset: int, new_table_size: int
    ) -> Optional[BinaryPatch]:
        """
        Create a patch to modify MSI-X table size.

        Args:
            offset: Offset of the MSI-X capability
            new_table_size: New table size (1-2048)

        Returns:
            BinaryPatch to modify table size, or None if failed
        """
        if not (1 <= new_table_size <= 2048):
            log_error_safe(
                logger,
                "Invalid MSI-X table size: {new_table_size} (must be 1-2048)",
                prefix="PCI_CAP",
                new_table_size=new_table_size,
            )
            return None

        msix_info = self.get_msix_capability_info(offset)
        if not msix_info:
            return None

        # Calculate new Message Control value
        message_control = msix_info["message_control"]
        # Clear table size bits (0-10) and set new size (subtract 1 for encoding)
        new_message_control = (message_control & 0xF800) | (
            (new_table_size - 1) & 0x07FF
        )

        if message_control == new_message_control:
            log_debug_safe(
                logger,
                safe_format(
                    "MSI-X table size at offset 0x{offset:02x} is already {new_table_size}",
                    offset=offset,
                    new_table_size=new_table_size,
                ),
            )
            return None

        patch = BinaryPatch(
            offset + 2,  # Message Control register offset
            message_control.to_bytes(2, "little"),
            new_message_control.to_bytes(2, "little"),
            safe_format(
                "Set MSI-X table size to {new_table_size} at offset 0x{offset:02x}",
                new_table_size=new_table_size,
                offset=offset,
            ),
        )

        return patch

    def create_msix_removal_patches(self, offset: int) -> List[BinaryPatch]:
        """
        Create patches to remove an MSI-X capability from the capability list.

        Args:
            offset: Offset of the MSI-X capability to remove

        Returns:
            List of BinaryPatch objects to remove the capability
        """
        patches = []

        msix_info = self.get_msix_capability_info(offset)
        if not msix_info:
            return patches

        next_ptr = msix_info["next_ptr"]

        # Find the capability that points to this MSI-X capability
        previous_cap_offset = self._find_previous_capability(offset)

        if previous_cap_offset is not None:
            # Update the previous capability's next pointer
            patch = BinaryPatch(
                previous_cap_offset + PCI_CAP_NEXT_PTR_OFFSET,
                bytes([offset]),  # Current pointer value
                bytes([next_ptr]),  # New pointer value
                safe_format(
                    "Update capability chain to skip MSI-X at 0x{offset:02x}",
                    offset=offset,
                ),
            )
            patches.append(patch)
        else:
            # This is the first capability, update the capabilities pointer
            from .constants import PCI_CAPABILITIES_POINTER

            patch = BinaryPatch(
                PCI_CAPABILITIES_POINTER,
                bytes([offset]),  # Current pointer value
                bytes([next_ptr]),  # New pointer value
                safe_format(
                    "Update capabilities pointer to skip MSI-X at 0x{offset:02x}",
                    offset=offset,
                ),
            )
            patches.append(patch)

        # Zero out the MSI-X capability structure (12 bytes)
        if self.config_space.has_data(offset, 12):
            current_data = bytes(self.config_space[offset : offset + 12])
            zero_data = bytes(12)  # All zeros

            patch = BinaryPatch(
                offset,
                current_data,
                zero_data,
                safe_format(
                    "Zero out MSI-X capability at 0x{offset:02x}",
                    offset=offset,
                ),
            )
            patches.append(patch)

        return patches

    def apply_msix_pruning(
        self,
        action: PruningAction,
        patch_engine: PatchEngine,
        device_context: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Apply MSI-X specific pruning operations.

        Args:
            action: Pruning action to apply
            patch_engine: PatchEngine to add patches to
            device_context: Optional device context

        Returns:
            Number of patches created
        """
        msix_capabilities = self.find_msix_capabilities()
        patches_created = 0

        for cap_info in msix_capabilities:
            category = self.categorize_msix_capability(cap_info, device_context)

            if (
                action == PruningAction.REMOVE
                and category == EmulationCategory.UNSUPPORTED
            ):
                # Remove unsupported MSI-X capabilities
                patches = self.create_msix_removal_patches(cap_info.offset)
                for patch in patches:
                    if patch_engine.add_patch(patch):
                        patches_created += 1

            elif (
                action == PruningAction.MODIFY
                and category == EmulationCategory.PARTIALLY_SUPPORTED
            ):
                # Disable partially supported MSI-X capabilities
                patch = self.create_msix_disable_patch(cap_info.offset)
                if patch and patch_engine.add_patch(patch):
                    patches_created += 1

        log_info_safe(
            logger,
            safe_format(
                "Created {patches_created} MSI-X pruning patches for action {action.name}",
                patches_created=patches_created,
            ),
        )
        return patches_created

    def get_msix_integration_info(self) -> Dict[str, Any]:
        """
        Get information for integration with existing MSI-X functionality.

        Returns:
            Dictionary with MSI-X integration information
        """
        msix_capabilities = self.find_msix_capabilities()
        integration_info = {
            "msix_count": len(msix_capabilities),
            "msix_offsets": [cap.offset for cap in msix_capabilities],
            "msix_details": [],
        }

        for cap_info in msix_capabilities:
            msix_info = self.get_msix_capability_info(cap_info.offset)
            if msix_info:
                # Add categorization information
                category = self.categorize_msix_capability(cap_info)
                msix_info["emulation_category"] = category.name
                integration_info["msix_details"].append(msix_info)

        return integration_info

    def _find_previous_capability(self, target_offset: int) -> Optional[int]:
        """
        Find the capability that points to the target offset.

        Args:
            target_offset: Offset of the target capability

        Returns:
            Offset of the previous capability, or None if target is first
        """
        for cap_info in self.walker.walk_standard_capabilities():
            if cap_info.next_ptr == target_offset:
                return cap_info.offset

        return None

    def validate_msix_capability(self, offset: int) -> Tuple[bool, List[str]]:
        """
        Validate an MSI-X capability structure.

        Args:
            offset: Offset of the MSI-X capability

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check basic structure
        if not self.config_space.has_data(offset, 12):
            errors.append(
                safe_format(
                    "MSI-X capability at 0x{offset:02x} is truncated",
                    offset=offset,
                )
            )
            return False, errors

        msix_info = self.get_msix_capability_info(offset)
        if not msix_info:
            errors.append(
                safe_format(
                    "Failed to parse MSI-X capability at 0x{offset:02x}",
                    offset=offset,
                )
            )
            return False, errors

        # Validate table size
        table_size = msix_info["table_size"]
        if not (1 <= table_size <= 2048):
            errors.append(
                safe_format(
                    "Invalid MSI-X table size: {table_size}",
                    table_size=table_size,
                )
            )

        # Validate BIR values
        table_bir = msix_info["table_bir"]
        pba_bir = msix_info["pba_bir"]
        if table_bir > 5:
            errors.append(
                safe_format(
                    "Invalid MSI-X table BIR: {table_bir}",
                    table_bir=table_bir,
                )
            )
        if pba_bir > 5:
            errors.append(
                safe_format(
                    "Invalid MSI-X PBA BIR: {pba_bir}",
                    pba_bir=pba_bir,
                )
            )

        # Validate alignment
        table_offset = msix_info["table_offset"]
        pba_offset = msix_info["pba_offset"]
        if table_offset & 0x7:
            errors.append(
                safe_format(
                    "MSI-X table offset 0x{table_offset:08x} is not 8-byte aligned",
                    table_offset=table_offset,
                )
            )
        if pba_offset & 0x7:
            errors.append(
                safe_format(
                    "MSI-X PBA offset 0x{pba_offset:08x} is not 8-byte aligned",
                    pba_offset=pba_offset,
                )
            )

        is_valid = len(errors) == 0
        return is_valid, errors

    def __repr__(self) -> str:
        msix_count = len(self.find_msix_capabilities())
        return safe_format(
            "MSIXCapabilityHandler(config_space_size={size}, msix_count={count})",
            size=len(self.config_space),
            count=msix_count,
        )
