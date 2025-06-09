#!/usr/bin/env python3
"""
Enhanced test suite for PCI capability pruning functionality.

This test suite focuses on:
1. Testing pruning of each specific capability type
2. Verifying capability chain integrity after pruning
3. Testing edge cases like empty capability chains
4. Testing complex capability configurations
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pci_capability import (
    EmulationCategory,
    PCICapabilityID,
    PCIExtCapabilityID,
    PruningAction,
    categorize_capabilities,
    determine_pruning_actions,
    find_cap,
    find_ext_cap,
    get_all_capabilities,
    get_all_ext_capabilities,
    prune_capabilities,
    prune_capabilities_by_rules,
)


class TestCapabilityPruningEnhanced(unittest.TestCase):
    """Enhanced test cases for PCI capability pruning functionality."""

    def setUp(self):
        """Set up test environment."""
        # Start with a 4KB configuration space filled with zeros
        self.config_space = "00" * 4096

        # Set capabilities pointer at offset 0x34
        self.config_space = (
            self.config_space[: 0x34 * 2] + "40" + self.config_space[0x34 * 2 + 2 :]
        )

        # Set capabilities bit in status register (offset 0x06, bit 4)
        status_value = int(self.config_space[0x06 * 2 : 0x06 * 2 + 4], 16) | 0x10
        status_hex = f"{status_value:04x}"
        self.config_space = (
            self.config_space[: 0x06 * 2]
            + status_hex
            + self.config_space[0x06 * 2 + 4 :]
        )

    def create_capability(self, offset, cap_id, next_ptr, data="0000"):
        """
        Create a standard capability at the specified offset.

        Args:
            offset: Offset in the configuration space
            cap_id: Capability ID
            next_ptr: Next capability pointer
            data: Additional capability data (hex string)

        Returns:
            Updated configuration space
        """
        # Format: cap_id (1 byte) + next_ptr (1 byte) + data (variable)
        cap = f"{cap_id:02x}{next_ptr:02x}{data}"

        # Insert the capability at the specified offset
        config_space = (
            self.config_space[: offset * 2]
            + cap
            + self.config_space[offset * 2 + len(cap) :]
        )

        return config_space

    def create_ext_capability(
        self, offset, cap_id, next_ptr, version=1, data="00000000"
    ):
        """
        Create an extended capability at the specified offset.

        Args:
            offset: Offset in the configuration space
            cap_id: Extended capability ID
            next_ptr: Next capability pointer
            version: Capability version
            data: Additional capability data (hex string)

        Returns:
            Updated configuration space
        """
        # Format: cap_id (16 bits) + version (4 bits) + next_ptr (12 bits) + data (variable)
        header = (cap_id << 16) | (version << 4) | next_ptr
        header_hex = f"{header:08x}"

        cap = header_hex + data

        # Insert the capability at the specified offset
        config_space = (
            self.config_space[: offset * 2]
            + cap
            + self.config_space[offset * 2 + len(cap) :]
        )

        return config_space

    def test_pruning_specific_capability_types(self):
        """Test pruning of each specific capability type."""
        # Create a configuration space with various capabilities
        config_space = self.config_space

        # Add PCIe capability at offset 0x40
        config_space = self.create_capability(
            0x40, PCICapabilityID.PCI_EXPRESS.value, 0x50, "0200" + "00000000"
        )

        # Add Power Management capability at offset 0x50
        config_space = self.create_capability(
            0x50, PCICapabilityID.POWER_MANAGEMENT.value, 0x60, "0300" + "00000000"
        )

        # Add MSI capability at offset 0x60
        config_space = self.create_capability(
            0x60, PCICapabilityID.MSI.value, 0x70, "0000" + "00000000"
        )

        # Add MSI-X capability at offset 0x70
        config_space = self.create_capability(
            0x70, PCICapabilityID.MSI_X.value, 0x80, "0007" + "00002000" + "00003000"
        )

        # Add Vendor-specific capability at offset 0x80
        config_space = self.create_capability(
            0x80, PCICapabilityID.VENDOR_SPECIFIC.value, 0x00, "1234" + "56789abc"
        )

        # Get all capabilities
        caps = get_all_capabilities(config_space)

        # Verify all capabilities are found
        self.assertEqual(len(caps), 5)

        # Create custom categorization to test specific pruning
        categories = {}
        for offset, cap in caps.items():
            if cap["id"] == PCICapabilityID.VENDOR_SPECIFIC.value:
                # Mark vendor-specific as unsupported
                categories[offset] = EmulationCategory.UNSUPPORTED
            elif cap["id"] == PCICapabilityID.POWER_MANAGEMENT.value:
                # Mark power management as partially supported
                categories[offset] = EmulationCategory.PARTIALLY_SUPPORTED
            else:
                # Mark others as fully supported
                categories[offset] = EmulationCategory.FULLY_SUPPORTED

        # Determine pruning actions
        actions = determine_pruning_actions(caps, categories)

        # Verify actions
        for offset, cap in caps.items():
            if cap["id"] == PCICapabilityID.VENDOR_SPECIFIC.value:
                self.assertEqual(actions[offset], PruningAction.REMOVE)
            elif cap["id"] == PCICapabilityID.POWER_MANAGEMENT.value:
                self.assertEqual(actions[offset], PruningAction.MODIFY)
            else:
                self.assertEqual(actions[offset], PruningAction.KEEP)

        # Apply pruning
        pruned_config = prune_capabilities(config_space, actions)

        # Verify pruning results
        pruned_caps = get_all_capabilities(pruned_config)

        # Should have 4 capabilities (vendor-specific removed)
        self.assertEqual(len(pruned_caps), 4)

        # Verify vendor-specific capability is removed
        vendor_offset = find_cap(pruned_config, PCICapabilityID.VENDOR_SPECIFIC.value)
        self.assertIsNone(vendor_offset)

        # Verify power management capability is modified
        pm_offset = find_cap(pruned_config, PCICapabilityID.POWER_MANAGEMENT.value)
        self.assertIsNotNone(pm_offset)
        self.assertEqual(pm_offset, 0x50)

        # Check that PM capability was modified (only D3hot support)
        if pm_offset is not None:
            pm_cap_offset = (pm_offset + 2) * 2
            pm_cap = int(pruned_config[pm_cap_offset : pm_cap_offset + 4], 16)
            self.assertEqual(pm_cap, 0x0008)  # Only D3hot bit set

    def test_capability_chain_integrity(self):
        """Test capability chain integrity after pruning."""
        # Create a configuration space with a chain of capabilities
        config_space = self.config_space

        # Add PCIe capability at offset 0x40
        config_space = self.create_capability(
            0x40, PCICapabilityID.PCI_EXPRESS.value, 0x50
        )

        # Add Power Management capability at offset 0x50
        config_space = self.create_capability(
            0x50, PCICapabilityID.POWER_MANAGEMENT.value, 0x60
        )

        # Add Vendor-specific capability at offset 0x60
        config_space = self.create_capability(
            0x60, PCICapabilityID.VENDOR_SPECIFIC.value, 0x70
        )

        # Add MSI-X capability at offset 0x70
        config_space = self.create_capability(0x70, PCICapabilityID.MSI_X.value, 0x00)

        # Get all capabilities
        caps = get_all_capabilities(config_space)

        # Create custom categorization to remove the middle capability
        categories = {}
        for offset, cap in caps.items():
            if cap["id"] == PCICapabilityID.VENDOR_SPECIFIC.value:
                # Mark vendor-specific as unsupported
                categories[offset] = EmulationCategory.UNSUPPORTED
            else:
                # Mark others as fully supported
                categories[offset] = EmulationCategory.FULLY_SUPPORTED

        # Determine pruning actions
        actions = determine_pruning_actions(caps, categories)

        # Apply pruning
        pruned_config = prune_capabilities(config_space, actions)

        # Verify pruning results
        pruned_caps = get_all_capabilities(pruned_config)

        # Should have 3 capabilities (vendor-specific removed)
        self.assertEqual(len(pruned_caps), 3)

        # Verify chain integrity
        # The next pointer of Power Management should now point to MSI-X
        pm_offset = find_cap(pruned_config, PCICapabilityID.POWER_MANAGEMENT.value)
        self.assertIsNotNone(pm_offset)
        self.assertEqual(pm_offset, 0x50)

        # Get the next pointer
        if pm_offset is not None:
            next_ptr_offset = (pm_offset + 1) * 2
            next_ptr = int(pruned_config[next_ptr_offset : next_ptr_offset + 2], 16)

            # Should point to MSI-X
            self.assertEqual(next_ptr, 0x70)

        # Verify MSI-X is still the last capability
        msix_offset = find_cap(pruned_config, PCICapabilityID.MSI_X.value)
        self.assertIsNotNone(msix_offset)
        self.assertEqual(msix_offset, 0x70)

        # Get the next pointer
        if msix_offset is not None:
            next_ptr_offset = (msix_offset + 1) * 2
            next_ptr = int(pruned_config[next_ptr_offset : next_ptr_offset + 2], 16)

            # Should be end of list
            self.assertEqual(next_ptr, 0x00)

    def test_empty_capability_chain(self):
        """Test pruning with an empty capability chain."""
        # Create a configuration space with no capabilities
        config_space = "00" * 4096

        # Set capabilities bit in status register (offset 0x06, bit 4)
        status_value = int(config_space[0x06 * 2 : 0x06 * 2 + 4], 16) | 0x10
        status_hex = f"{status_value:04x}"
        config_space = (
            config_space[: 0x06 * 2] + status_hex + config_space[0x06 * 2 + 4 :]
        )

        # Set capabilities pointer to 0 (no capabilities)
        config_space = config_space[: 0x34 * 2] + "00" + config_space[0x34 * 2 + 2 :]

        # Apply pruning
        pruned_config = prune_capabilities_by_rules(config_space)

        # Verify pruning results
        pruned_caps = get_all_capabilities(pruned_config)

        # Should have 0 capabilities
        self.assertEqual(len(pruned_caps), 0)

        # Capabilities pointer should still be 0
        cap_ptr_offset = 0x34 * 2
        cap_ptr = int(pruned_config[cap_ptr_offset : cap_ptr_offset + 2], 16)
        self.assertEqual(cap_ptr, 0x00)

    def test_extended_capability_pruning(self):
        """Test pruning of extended capabilities."""
        # Create a configuration space with extended capabilities
        config_space = self.config_space

        # Add L1 PM Substates extended capability at offset 0x100
        config_space = self.create_ext_capability(
            0x100, PCIExtCapabilityID.L1_PM_SUBSTATES.value, 0x140
        )

        # Add SR-IOV extended capability at offset 0x140
        config_space = self.create_ext_capability(
            0x140, PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value, 0x180
        )

        # Add AER extended capability at offset 0x180
        config_space = self.create_ext_capability(
            0x180, PCIExtCapabilityID.ADVANCED_ERROR_REPORTING.value, 0x1C0
        )

        # Add LTR extended capability at offset 0x1C0
        config_space = self.create_ext_capability(
            0x1C0, PCIExtCapabilityID.LATENCY_TOLERANCE_REPORTING.value, 0x000
        )

        # Get all extended capabilities
        ext_caps = get_all_ext_capabilities(config_space)

        # Verify all extended capabilities are found
        self.assertEqual(len(ext_caps), 4)

        # Apply pruning
        pruned_config = prune_capabilities_by_rules(config_space)

        # Verify pruning results
        pruned_ext_caps = get_all_ext_capabilities(pruned_config)

        # Should have fewer capabilities (L1 PM, SR-IOV, and LTR should be removed)
        self.assertLess(len(pruned_ext_caps), 4)

        # Verify L1 PM Substates is removed or zeroed out
        l1pm_offset = find_ext_cap(
            pruned_config, PCIExtCapabilityID.L1_PM_SUBSTATES.value
        )
        self.assertIsNone(l1pm_offset)

        # Verify SR-IOV is removed
        sriov_offset = find_ext_cap(
            pruned_config, PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value
        )
        self.assertIsNone(sriov_offset)

        # Verify LTR is removed
        ltr_offset = find_ext_cap(
            pruned_config, PCIExtCapabilityID.LATENCY_TOLERANCE_REPORTING.value
        )
        self.assertIsNone(ltr_offset)

        # Verify AER is still present (partially supported)
        aer_offset = find_ext_cap(
            pruned_config, PCIExtCapabilityID.ADVANCED_ERROR_REPORTING.value
        )
        self.assertIsNotNone(aer_offset)

    def test_complex_capability_configuration(self):
        """Test pruning with a complex capability configuration."""
        # Create a configuration space with a complex mix of capabilities
        config_space = self.config_space

        # Add standard capabilities
        config_space = self.create_capability(
            0x40, PCICapabilityID.PCI_EXPRESS.value, 0x50
        )
        config_space = self.create_capability(
            0x50, PCICapabilityID.POWER_MANAGEMENT.value, 0x60
        )
        config_space = self.create_capability(0x60, PCICapabilityID.MSI.value, 0x70)
        config_space = self.create_capability(0x70, PCICapabilityID.MSI_X.value, 0x80)
        config_space = self.create_capability(
            0x80, PCICapabilityID.VENDOR_SPECIFIC.value, 0x00
        )

        # Add extended capabilities
        config_space = self.create_ext_capability(
            0x100, PCIExtCapabilityID.ADVANCED_ERROR_REPORTING.value, 0x140
        )
        config_space = self.create_ext_capability(
            0x140, PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value, 0x180
        )
        config_space = self.create_ext_capability(
            0x180, PCIExtCapabilityID.L1_PM_SUBSTATES.value, 0x1C0
        )
        config_space = self.create_ext_capability(
            0x1C0, PCIExtCapabilityID.LATENCY_TOLERANCE_REPORTING.value, 0x000
        )

        # Apply pruning
        pruned_config = prune_capabilities_by_rules(config_space)

        # Verify pruning results
        pruned_std_caps = get_all_capabilities(pruned_config)
        pruned_ext_caps = get_all_ext_capabilities(pruned_config)

        # Verify standard capabilities
        # Vendor-specific should be removed
        self.assertIsNone(
            find_cap(pruned_config, PCICapabilityID.VENDOR_SPECIFIC.value)
        )

        # PCIe, PM, MSI, MSI-X should be present
        self.assertIsNotNone(find_cap(pruned_config, PCICapabilityID.PCI_EXPRESS.value))
        self.assertIsNotNone(
            find_cap(pruned_config, PCICapabilityID.POWER_MANAGEMENT.value)
        )
        self.assertIsNotNone(find_cap(pruned_config, PCICapabilityID.MSI.value))
        self.assertIsNotNone(find_cap(pruned_config, PCICapabilityID.MSI_X.value))

        # Verify extended capabilities
        # SR-IOV, L1 PM, LTR should be removed
        self.assertIsNone(
            find_ext_cap(
                pruned_config, PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value
            )
        )
        self.assertIsNone(
            find_ext_cap(pruned_config, PCIExtCapabilityID.L1_PM_SUBSTATES.value)
        )
        self.assertIsNone(
            find_ext_cap(
                pruned_config, PCIExtCapabilityID.LATENCY_TOLERANCE_REPORTING.value
            )
        )

        # AER should be present
        self.assertIsNotNone(
            find_ext_cap(
                pruned_config, PCIExtCapabilityID.ADVANCED_ERROR_REPORTING.value
            )
        )

        # Verify capability chain integrity
        # The last standard capability should have next pointer 0
        last_std_cap = max(pruned_std_caps.keys())
        next_ptr_offset = (last_std_cap + 1) * 2
        next_ptr = int(pruned_config[next_ptr_offset : next_ptr_offset + 2], 16)
        self.assertEqual(next_ptr, 0x00)

        # The last extended capability should have next pointer 0
        if pruned_ext_caps:
            last_ext_cap = max(pruned_ext_caps.keys())
            header_offset = last_ext_cap * 2
            header = int(pruned_config[header_offset : header_offset + 8], 16)
            next_ptr = header & 0xFFF
            self.assertEqual(next_ptr, 0x000)

    def test_pcie_capability_modification(self):
        """Test modification of PCIe capability."""
        # Create a configuration space with PCIe capability
        config_space = self.config_space

        # Add PCIe capability at offset 0x40 with ASPM enabled
        pcie_cap = "10" + "00" + "0200" + "00000000"
        config_space = (
            config_space[: 0x40 * 2]
            + pcie_cap
            + config_space[0x40 * 2 + len(pcie_cap) :]
        )

        # Add Link Control Register at offset 0x50 (part of PCIe capability)
        link_control = "0003" + "0000"  # ASPM L0s and L1 enabled
        config_space = (
            config_space[: 0x50 * 2]
            + link_control
            + config_space[0x50 * 2 + len(link_control) :]
        )

        # Add Device Control 2 Register at offset 0x68 (part of PCIe capability)
        dev_control2 = "6400" + "0000"  # OBFF and LTR enabled
        config_space = (
            config_space[: 0x68 * 2]
            + dev_control2
            + config_space[0x68 * 2 + len(dev_control2) :]
        )

        # Apply pruning
        pruned_config = prune_capabilities_by_rules(config_space)

        # Verify PCIe capability is still present
        pcie_offset = find_cap(pruned_config, PCICapabilityID.PCI_EXPRESS.value)
        self.assertEqual(pcie_offset, 0x40)

        # Verify Link Control register has ASPM disabled
        link_control_offset = 0x50 * 2
        link_control = int(
            pruned_config[link_control_offset : link_control_offset + 4], 16
        )
        self.assertEqual(link_control & 0x0003, 0x0000)  # ASPM bits should be cleared

        # Verify Device Control 2 register has OBFF and LTR disabled
        dev_control2_offset = 0x68 * 2
        dev_control2 = int(
            pruned_config[dev_control2_offset : dev_control2_offset + 4], 16
        )
        self.assertEqual(
            dev_control2 & 0x6400, 0x0000
        )  # OBFF and LTR bits should be cleared


if __name__ == "__main__":
    unittest.main()
