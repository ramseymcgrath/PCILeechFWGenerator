#!/usr/bin/env python3
"""
PCI Capability Processor

This module provides the main processing logic that orchestrates all PCI
capability operations. It integrates the RuleEngine, PatchEngine, MSI-X
handler, and other components to provide single-pass processing for finding,
categorizing, and pruning capabilities.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from ..string_utils import safe_format
except ImportError:
    # Fallback for script execution
    import sys
    from pathlib import Path

    src_dir = Path(__file__).parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    from string_utils import safe_format

from .core import CapabilityWalker, ConfigSpace
from .msix import MSIXCapabilityHandler
from .patches import PatchEngine
from .rules import RuleEngine
from .types import (CapabilityInfo, CapabilityType, EmulationCategory,
                    PatchInfo, PruningAction)

logger = logging.getLogger(__name__)


class CapabilityProcessor:
    """
    Main processor for PCI capability operations.

    The CapabilityProcessor orchestrates all capability-related operations,
    providing a unified interface for finding, categorizing, and pruning
    capabilities. It integrates with the RuleEngine for categorization,
    PatchEngine for modifications, and specialized handlers like MSI-X.
    """

    def __init__(
        self,
        config_space: ConfigSpace,
        rule_engine: Optional[RuleEngine] = None,
        patch_engine: Optional[PatchEngine] = None,
    ) -> None:
        """
        Initialize the capability processor.

        Args:
            config_space: ConfigSpace instance to process
            rule_engine: Optional RuleEngine for categorization
            patch_engine: Optional PatchEngine for modifications
        """
        self.config_space = config_space
        self.rule_engine = rule_engine or RuleEngine()
        self.patch_engine = patch_engine or PatchEngine()

        # Initialize specialized handlers
        self.walker = CapabilityWalker(config_space)
        self.msix_handler = MSIXCapabilityHandler(config_space, self.rule_engine)

        # Processing state
        self._capabilities_cache: Optional[Dict[int, CapabilityInfo]] = None
        self._categories_cache: Optional[Dict[int, EmulationCategory]] = None
        self._device_context_cache: Optional[Dict[str, Any]] = None

    def discover_all_capabilities(
        self, force_refresh: bool = False
    ) -> Dict[int, CapabilityInfo]:
        """
        Discover all capabilities in the configuration space.

        Args:
            force_refresh: Whether to force a refresh of cached results

        Returns:
            Dictionary mapping capability offsets to CapabilityInfo objects
        """
        if self._capabilities_cache is None or force_refresh:
            self._capabilities_cache = self.walker.get_all_capabilities()
            logger.info(f"Discovered {len(self._capabilities_cache)} capabilities")

        return self._capabilities_cache.copy()

    def categorize_all_capabilities(
        self,
        device_context: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False,
    ) -> Dict[int, EmulationCategory]:
        """
        Categorize all capabilities using the rule engine.

        Args:
            device_context: Optional device context for rule evaluation
            force_refresh: Whether to force a refresh of cached results

        Returns:
            Dictionary mapping capability offsets to EmulationCategory
        """
        if self._categories_cache is None or force_refresh:
            capabilities = self.discover_all_capabilities(force_refresh)

            # Use provided device context or extract from config space
            if device_context is None:
                device_context = self._get_device_context()

            self._categories_cache = self.rule_engine.categorize_capabilities(
                capabilities, self.config_space, device_context
            )
            self._device_context_cache = device_context

            logger.info(f"Categorized {len(self._categories_cache)} capabilities")

        return self._categories_cache.copy()

    def process_capabilities(
        self,
        actions: List[PruningAction],
        device_context: Optional[Dict[str, Any]] = None,
        validate_patches: bool = True,
    ) -> Dict[str, Any]:
        """
        Process capabilities with the specified actions.

        This is the main processing method that performs single-pass
        processing for finding, categorizing, and pruning capabilities.

        Args:
            actions: List of pruning actions to apply
            device_context: Optional device context for rule evaluation
            validate_patches: Whether to validate patches before applying

        Returns:
            Dictionary with processing results
        """
        logger.info(
            f"Starting capability processing with actions: {[a.name for a in actions]}"
        )

        # Discover and categorize capabilities
        capabilities = self.discover_all_capabilities()
        categories = self.categorize_all_capabilities(device_context)

        # Initialize results
        results = {
            "capabilities_found": len(capabilities),
            "categories": {},
            "patches_created": 0,
            "patches_applied": 0,
            "errors": [],
            "warnings": [],
            "processing_summary": {},
        }

        # Group capabilities by category for efficient processing
        category_groups = self._group_capabilities_by_category(capabilities, categories)
        results["categories"] = {
            cat.name: len(caps) for cat, caps in category_groups.items()
        }

        # Process each action
        for action in actions:
            action_results = self._process_action(
                action, category_groups, device_context
            )

            # Merge action results
            results["patches_created"] += action_results["patches_created"]
            results["errors"].extend(action_results["errors"])
            results["warnings"].extend(action_results["warnings"])
            results["processing_summary"][action.name] = action_results["summary"]

        # Apply patches if any were created
        if self.patch_engine.patches:
            patches_applied, patch_errors = self.patch_engine.apply_all_patches(
                self.config_space, validate_first=validate_patches
            )
            results["patches_applied"] = patches_applied
            results["errors"].extend(patch_errors)

        logger.info(
            safe_format(
                "Capability processing completed: {found} capabilities, {created} patches created, {applied} patches applied",
                found=results["capabilities_found"],
                created=results["patches_created"],
                applied=results["patches_applied"],
            )
        )

        return results

    def get_capability_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all capabilities and their categories.

        Returns:
            Dictionary with capability summary information
        """
        capabilities = self.discover_all_capabilities()
        categories = self.categorize_all_capabilities()

        # Count capabilities by type and category
        standard_count = sum(
            1
            for cap in capabilities.values()
            if cap.cap_type == CapabilityType.STANDARD
        )
        extended_count = sum(
            1
            for cap in capabilities.values()
            if cap.cap_type == CapabilityType.EXTENDED
        )

        category_counts = {}
        for category in EmulationCategory:
            category_counts[category.name] = sum(
                1 for cat in categories.values() if cat == category
            )

        # Get MSI-X specific information
        msix_info = self.msix_handler.get_msix_integration_info()

        return {
            "total_capabilities": len(capabilities),
            "standard_capabilities": standard_count,
            "extended_capabilities": extended_count,
            "category_counts": category_counts,
            "msix_info": msix_info,
            "config_space_size": len(self.config_space),
            "device_context": self._get_device_context(),
        }

    def validate_configuration_space(self) -> Tuple[bool, List[str]]:
        """
        Validate the configuration space and all capabilities.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Basic configuration space validation
        if len(self.config_space) < 256:
            errors.append(
                f"Configuration space too small: {len(self.config_space)} bytes"
            )

        # Validate all capabilities
        capabilities = self.discover_all_capabilities()

        for offset, cap_info in capabilities.items():
            # Basic capability validation
            if not self.config_space.has_data(offset, 2):
                errors.append(f"Capability at 0x{offset:02x} is truncated")
                continue

            # Validate capability ID matches
            try:
                actual_id = self.config_space.read_byte(offset)
                if actual_id != cap_info.cap_id:
                    errors.append(
                        f"Capability ID mismatch at 0x{offset:02x}: expected 0x{cap_info.cap_id:02x}, found 0x{actual_id:02x}"
                    )
            except (IndexError, ValueError) as e:
                errors.append(f"Failed to validate capability at 0x{offset:02x}: {e}")

            # MSI-X specific validation
            if cap_info.cap_id == 0x11:  # MSI-X
                is_valid, msix_errors = self.msix_handler.validate_msix_capability(
                    offset
                )
                if not is_valid:
                    errors.extend(msix_errors)

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_patch_info_list(self) -> List[PatchInfo]:
        """
        Get a list of all patches as PatchInfo objects.

        Returns:
            List of PatchInfo objects for all patches
        """
        return self.patch_engine.get_patch_info_list("capability_processing")

    def rollback_all_changes(self) -> Tuple[int, List[str]]:
        """
        Rollback all applied patches.

        Returns:
            Tuple of (patches_rolled_back, error_messages)
        """
        return self.patch_engine.rollback_all_patches(self.config_space)

    def clear_processing_state(self) -> None:
        """Clear all cached processing state."""
        self._capabilities_cache = None
        self._categories_cache = None
        self._device_context_cache = None
        self.patch_engine.clear_patches()
        logger.debug("Cleared all processing state")

    def _get_device_context(self) -> Dict[str, Any]:
        """Get or extract device context information."""
        if self._device_context_cache is None:
            self._device_context_cache = self.rule_engine._extract_device_context(
                self.config_space
            )
        return self._device_context_cache

    def _group_capabilities_by_category(
        self,
        capabilities: Dict[int, CapabilityInfo],
        categories: Dict[int, EmulationCategory],
    ) -> Dict[EmulationCategory, List[CapabilityInfo]]:
        """Group capabilities by their emulation category."""
        groups = {category: [] for category in EmulationCategory}

        for offset, cap_info in capabilities.items():
            category = categories.get(offset, EmulationCategory.UNSUPPORTED)
            groups[category].append(cap_info)

        return groups

    def _process_action(
        self,
        action: PruningAction,
        category_groups: Dict[EmulationCategory, List[CapabilityInfo]],
        device_context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Process a specific pruning action."""
        results = {
            "patches_created": 0,
            "errors": [],
            "warnings": [],
            "summary": {},
        }

        if action == PruningAction.REMOVE:
            # Remove unsupported capabilities
            unsupported_caps = category_groups.get(EmulationCategory.UNSUPPORTED, [])
            results["patches_created"] += self._create_removal_patches(unsupported_caps)
            results["summary"]["removed_capabilities"] = len(unsupported_caps)

        elif action == PruningAction.MODIFY:
            # Modify partially supported capabilities
            partial_caps = category_groups.get(
                EmulationCategory.PARTIALLY_SUPPORTED, []
            )
            results["patches_created"] += self._create_modification_patches(
                partial_caps
            )
            results["summary"]["modified_capabilities"] = len(partial_caps)

        elif action == PruningAction.KEEP:
            # Keep supported capabilities (no patches needed)
            supported_caps = category_groups.get(EmulationCategory.FULLY_SUPPORTED, [])
            critical_caps = category_groups.get(EmulationCategory.CRITICAL, [])
            results["summary"]["kept_capabilities"] = len(supported_caps) + len(
                critical_caps
            )

        # Apply MSI-X specific processing
        msix_patches = self.msix_handler.apply_msix_pruning(
            action, self.patch_engine, device_context
        )
        results["patches_created"] += msix_patches

        return results

    def _create_removal_patches(self, capabilities: List[CapabilityInfo]) -> int:
        """Create patches to remove capabilities."""
        patches_created = 0

        for cap_info in capabilities:
            if cap_info.cap_id == 0x11:  # MSI-X - handled by MSI-X handler
                continue

            # Create generic capability removal patches
            patches = self._create_generic_removal_patches(cap_info)
            for patch in patches:
                if self.patch_engine.add_patch(patch):
                    patches_created += 1

        return patches_created

    def _create_modification_patches(self, capabilities: List[CapabilityInfo]) -> int:
        """Create patches to modify capabilities."""
        patches_created = 0

        for cap_info in capabilities:
            if cap_info.cap_id == 0x11:  # MSI-X - handled by MSI-X handler
                continue

            # Create generic capability modification patches
            patches = self._create_generic_modification_patches(cap_info)
            for patch in patches:
                if self.patch_engine.add_patch(patch):
                    patches_created += 1

        return patches_created

    def _create_generic_removal_patches(self, cap_info: CapabilityInfo) -> List:
        """Create generic patches to remove a capability from the capability chain.
        1. Finding the previous capability in the chain
        2. Updating its next pointer to skip the removed capability
        3. Zeroing out the removed capability's header
        """
        from .constants import (PCI_CAP_NEXT_PTR_OFFSET,
                                PCI_CAPABILITIES_POINTER)

        patches = []

        # Find the previous capability in the chain
        prev_offset = None
        current_offset = None

        # Check if this is the first capability
        if self.config_space.has_data(PCI_CAPABILITIES_POINTER, 1):
            first_cap_offset = self.config_space.read_byte(PCI_CAPABILITIES_POINTER)
            if first_cap_offset == cap_info.offset:
                # This is the first capability - update the capabilities pointer
                if self.config_space.has_data(
                    cap_info.offset + PCI_CAP_NEXT_PTR_OFFSET, 1
                ):
                    next_ptr = self.config_space.read_byte(
                        cap_info.offset + PCI_CAP_NEXT_PTR_OFFSET
                    )
                    patch = self.patch_engine.create_byte_patch(
                        PCI_CAPABILITIES_POINTER,
                        first_cap_offset,
                        next_ptr,
                        f"Update capabilities pointer to skip {cap_info.name} at 0x{cap_info.offset:02x}",
                    )
                    if patch:
                        patches.append(patch)
            else:
                # Find the previous capability
                current_offset = first_cap_offset
                while current_offset and current_offset != cap_info.offset:
                    if self.config_space.has_data(
                        current_offset + PCI_CAP_NEXT_PTR_OFFSET, 1
                    ):
                        next_offset = self.config_space.read_byte(
                            current_offset + PCI_CAP_NEXT_PTR_OFFSET
                        )
                        if next_offset == cap_info.offset:
                            prev_offset = current_offset
                            break
                        current_offset = next_offset
                    else:
                        break

                # Update the previous capability's next pointer
                if prev_offset and self.config_space.has_data(
                    cap_info.offset + PCI_CAP_NEXT_PTR_OFFSET, 1
                ):
                    next_ptr = self.config_space.read_byte(
                        cap_info.offset + PCI_CAP_NEXT_PTR_OFFSET
                    )
                    patch = self.patch_engine.create_byte_patch(
                        prev_offset + PCI_CAP_NEXT_PTR_OFFSET,
                        cap_info.offset,
                        next_ptr,
                        f"Update next pointer to skip {cap_info.name} at 0x{cap_info.offset:02x}",
                    )
                    if patch:
                        patches.append(patch)

        # Zero out the capability header (ID and next pointer)
        if self.config_space.has_data(cap_info.offset, 2):
            # Zero the capability ID
            current_id = self.config_space.read_byte(cap_info.offset)
            patch = self.patch_engine.create_byte_patch(
                cap_info.offset,
                current_id,
                0,
                f"Zero out {cap_info.name} capability ID at 0x{cap_info.offset:02x}",
            )
            if patch:
                patches.append(patch)

            # Zero the next pointer
            current_next = self.config_space.read_byte(
                cap_info.offset + PCI_CAP_NEXT_PTR_OFFSET
            )
            patch = self.patch_engine.create_byte_patch(
                cap_info.offset + PCI_CAP_NEXT_PTR_OFFSET,
                current_next,
                0,
                f"Zero out {cap_info.name} next pointer at 0x{cap_info.offset + PCI_CAP_NEXT_PTR_OFFSET:02x}",
            )
            if patch:
                patches.append(patch)

        return patches

    def _create_generic_modification_patches(self, cap_info: CapabilityInfo) -> List:
        """Create generic patches to modify a capability."""
        patches = []

        # Handle Power Management capability specifically
        if cap_info.cap_id == 0x01:  # Power Management capability
            patches.extend(self._create_power_management_patches(cap_info))
        else:
            # For other capabilities, log that they're not implemented
            logger.debug(
                f"Generic modification for {cap_info.name} at 0x{cap_info.offset:02x} not implemented"
            )

        return patches

    def _create_power_management_patches(self, cap_info: CapabilityInfo) -> List:
        """Create patches for Power Management capability modification."""
        from .constants import PM_CAP_CAPABILITIES_OFFSET, PM_CAP_D3HOT_SUPPORT

        patches = []

        try:
            # Read Power Management Capabilities (PMC) register
            pmc_offset = cap_info.offset + PM_CAP_CAPABILITIES_OFFSET
            if not self.config_space.has_data(pmc_offset, 2):
                logger.warning(f"PMC register at 0x{pmc_offset:02x} is out of bounds")
                return patches

            current_pmc = self.config_space.read_word(pmc_offset)

            # Modify PMC to support only D0 and D3hot states
            # Clear D1 and D2 support bits (bits 9 and 10), keep D3hot support (bit 11)
            new_pmc = current_pmc & ~0x0600  # Clear D1 and D2 support
            new_pmc |= PM_CAP_D3HOT_SUPPORT  # Ensure D3hot support is set

            if new_pmc != current_pmc:
                patch = self.patch_engine.create_word_patch(
                    pmc_offset,
                    current_pmc,
                    new_pmc,
                    f"Modify Power Management Capabilities at 0x{pmc_offset:02x} - limit to D0/D3hot only",
                )
                if patch:
                    patches.append(patch)
                    logger.info(
                        f"Created power management patch: PMC 0x{current_pmc:04x} -> 0x{new_pmc:04x}"
                    )

            # Read and modify Power Management Control/Status Register (PMCSR)
            pmcsr_offset = (
                cap_info.offset + 4
            )  # PMCSR is at offset 4 from capability header
            if self.config_space.has_data(pmcsr_offset, 2):
                current_pmcsr = self.config_space.read_word(pmcsr_offset)

                # Clear PME_En and PME_Status bits for safer emulation
                # Keep power state in D0 (bits 1:0 = 00)
                new_pmcsr = (
                    current_pmcsr & ~0xC003
                )  # Clear PME_En (15), PME_Status (14), and power state (1:0)

                if new_pmcsr != current_pmcsr:
                    patch = self.patch_engine.create_word_patch(
                        pmcsr_offset,
                        current_pmcsr,
                        new_pmcsr,
                        f"Modify PMCSR at 0x{pmcsr_offset:02x} - clear PME and set D0 state",
                    )
                    if patch:
                        patches.append(patch)
                        logger.info(
                            f"Created PMCSR patch: 0x{current_pmcsr:04x} -> 0x{new_pmcsr:04x}"
                        )

        except Exception as e:
            logger.error(f"Error creating power management patches: {e}")

        return patches

    def __repr__(self) -> str:
        capabilities_count = (
            len(self._capabilities_cache) if self._capabilities_cache else "unknown"
        )
        patches_count = len(self.patch_engine)

        return safe_format(
            "CapabilityProcessor(capabilities={caps}, patches={patches}, config_size={size})",
            caps=capabilities_count,
            patches=patches_count,
            size=len(self.config_space),
        )
