#!/usr/bin/env python3
"""
Test suite for PCI capability analysis and pruning.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

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


class TestPCICapability(unittest.TestCase):
    """Test cases for PCI capability analysis and pruning."""

    def setUp(self):
        """Set up test environment."""
        # Create a sample configuration space with capabilities

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

        # Add PCI Express capability at offset 0x40
        # Capability ID: 0x10 (PCIe)
        # Next pointer: 0x60 (next capability)
        # PCI Express Capabilities Register: 0x0002 (Endpoint device)
        pcie_cap = "10" + "60" + "0200" + "00000000" + "00000000" + "00000000"
        self.config_space = (
            self.config_space[: 0x40 * 2]
            + pcie_cap
            + self.config_space[0x40 * 2 + len(pcie_cap) :]
        )

        # Add Link Control Register at offset 0x50 (part of PCIe capability)
        link_control = "0001" + "0000"  # ASPM L0s enabled
        self.config_space = (
            self.config_space[: 0x50 * 2]
            + link_control
            + self.config_space[0x50 * 2 + len(link_control) :]
        )

        # Add Device Control 2 Register at offset 0x68 (part of PCIe capability)
        dev_control2 = "6400" + "0000"  # OBFF and LTR enabled
        self.config_space = (
            self.config_space[: 0x68 * 2]
            + dev_control2
            + self.config_space[0x68 * 2 + len(dev_control2) :]
        )

        # Add Power Management capability at offset 0x60
        # Capability ID: 0x01 (PM)
        # Next pointer: 0x70 (next capability)
        # PM Capabilities Register: 0x03 (D0, D1, D2, D3hot supported)
        pm_cap = "01" + "70" + "0300" + "00000000"
        self.config_space = (
            self.config_space[: 0x60 * 2]
            + pm_cap
            + self.config_space[0x60 * 2 + len(pm_cap) :]
        )

        # Add MSI-X capability at offset 0x70
        # Capability ID: 0x11 (MSI-X)
        # Next pointer: 0x00 (end of list)
        # Message Control: 0x0007 (8 table entries, function not masked, MSI-X disabled)
        # Table offset/BIR: 0x00002000 (offset 0x2000, BIR 0)
        # PBA offset/BIR: 0x00003000 (offset 0x3000, BIR 0)
        msix_cap = "11" + "00" + "0700" + "00002000" + "00003000"
        self.config_space = (
            self.config_space[: 0x70 * 2]
            + msix_cap
            + self.config_space[0x70 * 2 + len(msix_cap) :]
        )

        # Add Extended capabilities

        # Add L1 PM Substates extended capability at offset 0x100
        # Extended Capability ID: 0x001E (L1 PM Substates)
        # Capability Version: 0x1
        # Next Capability Offset: 0x140
        # L1 Substates Capabilities: 0x00000001 (L1.1 supported)
        # L1 Substates Control 1: 0x00000002
        # L1 Substates Control 2: 0x00000003
        l1pm_cap = "001E" + "1140" + "00000001" + "00000002" + "00000003"
        self.config_space = (
            self.config_space[: 0x100 * 2]
            + l1pm_cap
            + self.config_space[0x100 * 2 + len(l1pm_cap) :]
        )

        # Add SR-IOV extended capability at offset 0x140
        # Extended Capability ID: 0x0010 (SR-IOV)
        # Capability Version: 0x1
        # Next Capability Offset: 0x000 (end of list)
        # SR-IOV Control: 0x00000000
        # SR-IOV Status: 0x00000000
        # Initial VFs: 0x00000004
        # Total VFs: 0x00000008
        sriov_cap = "0010" + "1000" + "00000000" + "00000000" + "00000004" + "00000008"
        self.config_space = (
            self.config_space[: 0x140 * 2]
            + sriov_cap
            + self.config_space[0x140 * 2 + len(sriov_cap) :]
        )

    def test_find_cap(self):
        """Test finding a standard capability in the configuration space."""
        # Find PCIe capability (ID 0x10)
        cap_offset = find_cap(self.config_space, 0x10)
        self.assertEqual(cap_offset, 0x40)

        # Find PM capability (ID 0x01)
        cap_offset = find_cap(self.config_space, 0x01)
        self.assertEqual(cap_offset, 0x60)

        # Find MSI-X capability (ID 0x11)
        cap_offset = find_cap(self.config_space, 0x11)
        self.assertEqual(cap_offset, 0x70)

        # Try to find a non-existent capability
        cap_offset = find_cap(self.config_space, 0x12)
        self.assertIsNone(cap_offset)

    def test_find_ext_cap(self):
        """Test finding an extended capability in the configuration space."""
        # Find L1 PM Substates extended capability (ID 0x001E)
        cap_offset = find_ext_cap(self.config_space, 0x001E)
        self.assertEqual(cap_offset, 0x100)

        # Find SR-IOV extended capability (ID 0x0010)
        cap_offset = find_ext_cap(self.config_space, 0x0010)
        self.assertEqual(cap_offset, 0x140)

        # Try to find a non-existent extended capability
        cap_offset = find_ext_cap(self.config_space, 0x0011)
        self.assertIsNone(cap_offset)

    def test_get_all_capabilities(self):
        """Test getting all standard capabilities in the configuration space."""
        capabilities = get_all_capabilities(self.config_space)

        # Check that we found all three standard capabilities
        self.assertEqual(len(capabilities), 3)

        # Check that the capabilities are at the expected offsets
        self.assertIn(0x40, capabilities)
        self.assertIn(0x60, capabilities)
        self.assertIn(0x70, capabilities)

        # Check the capability IDs
        self.assertEqual(capabilities[0x40]["id"], PCICapabilityID.PCI_EXPRESS.value)
        self.assertEqual(
            capabilities[0x60]["id"], PCICapabilityID.POWER_MANAGEMENT.value
        )
        self.assertEqual(capabilities[0x70]["id"], PCICapabilityID.MSI_X.value)

        # Check the next pointers
        self.assertEqual(capabilities[0x40]["next_ptr"], 0x60)
        self.assertEqual(capabilities[0x60]["next_ptr"], 0x70)
        self.assertEqual(capabilities[0x70]["next_ptr"], 0x00)

    def test_get_all_ext_capabilities(self):
        """Test getting all extended capabilities in the configuration space."""
        ext_capabilities = get_all_ext_capabilities(self.config_space)

        # Check that we found both extended capabilities
        self.assertEqual(len(ext_capabilities), 2)

        # Check that the capabilities are at the expected offsets
        self.assertIn(0x100, ext_capabilities)
        self.assertIn(0x140, ext_capabilities)

        # Check the capability IDs
        self.assertEqual(
            ext_capabilities[0x100]["id"], PCIExtCapabilityID.L1_PM_SUBSTATES.value
        )
        self.assertEqual(
            ext_capabilities[0x140]["id"],
            PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value,
        )

        # Check the next pointers
        self.assertEqual(ext_capabilities[0x100]["next_ptr"], 0x140)
        self.assertEqual(ext_capabilities[0x140]["next_ptr"], 0x000)

    def test_categorize_capabilities(self):
        """Test categorizing capabilities based on emulation feasibility."""
        # Get all capabilities
        std_caps = get_all_capabilities(self.config_space)
        ext_caps = get_all_ext_capabilities(self.config_space)

        # Categorize standard capabilities
        std_categories = categorize_capabilities(std_caps)

        # Check that PCIe is partially supported
        self.assertEqual(std_categories[0x40], EmulationCategory.PARTIALLY_SUPPORTED)

        # Check that PM is partially supported
        self.assertEqual(std_categories[0x60], EmulationCategory.PARTIALLY_SUPPORTED)

        # Check that MSI-X is fully supported
        self.assertEqual(std_categories[0x70], EmulationCategory.FULLY_SUPPORTED)

        # Categorize extended capabilities
        ext_categories = categorize_capabilities(ext_caps)

        # Check that L1 PM Substates is unsupported
        self.assertEqual(ext_categories[0x100], EmulationCategory.UNSUPPORTED)

        # Check that SR-IOV is unsupported
        self.assertEqual(ext_categories[0x140], EmulationCategory.UNSUPPORTED)

    def test_determine_pruning_actions(self):
        """Test determining pruning actions for capabilities."""
        # Get all capabilities
        std_caps = get_all_capabilities(self.config_space)
        ext_caps = get_all_ext_capabilities(self.config_space)

        # Categorize capabilities
        std_categories = categorize_capabilities(std_caps)
        ext_categories = categorize_capabilities(ext_caps)

        # Determine pruning actions
        std_actions = determine_pruning_actions(std_caps, std_categories)
        ext_actions = determine_pruning_actions(ext_caps, ext_categories)

        # Check standard capability actions
        self.assertEqual(
            std_actions[0x40], PruningAction.MODIFY
        )  # PCIe should be modified
        self.assertEqual(
            std_actions[0x60], PruningAction.MODIFY
        )  # PM should be modified
        self.assertEqual(std_actions[0x70], PruningAction.KEEP)  # MSI-X should be kept

        # Check extended capability actions
        self.assertEqual(
            ext_actions[0x100], PruningAction.REMOVE
        )  # L1 PM Substates should be removed
        self.assertEqual(
            ext_actions[0x140], PruningAction.REMOVE
        )  # SR-IOV should be removed

    def test_prune_capabilities(self):
        """Test pruning capabilities in the configuration space."""
        # Get all capabilities
        std_caps = get_all_capabilities(self.config_space)
        ext_caps = get_all_ext_capabilities(self.config_space)

        # Categorize capabilities
        std_categories = categorize_capabilities(std_caps)
        ext_categories = categorize_capabilities(ext_caps)

        # Determine pruning actions
        std_actions = determine_pruning_actions(std_caps, std_categories)
        ext_actions = determine_pruning_actions(ext_caps, ext_categories)

        # Combine actions
        all_actions = {**std_actions, **ext_actions}

        # Apply pruning
        pruned_cfg = prune_capabilities(self.config_space, all_actions)

        # Check that the pruned configuration space is still valid
        self.assertEqual(len(pruned_cfg), len(self.config_space))

        # Check that PCIe capability is still present but modified
        pcie_offset = find_cap(pruned_cfg, 0x10)
        self.assertEqual(pcie_offset, 0x40)

        # Check that ASPM bits are cleared in Link Control register
        link_control_offset = 0x50 * 2
        link_control = int(
            pruned_cfg[link_control_offset : link_control_offset + 4], 16
        )
        self.assertEqual(link_control & 0x0003, 0)  # ASPM bits should be cleared

        # Check that OBFF and LTR bits are cleared in Device Control 2 register
        dev_control2_offset = 0x68 * 2
        dev_control2 = int(
            pruned_cfg[dev_control2_offset : dev_control2_offset + 4], 16
        )
        self.assertEqual(
            dev_control2 & 0x6400, 0
        )  # OBFF and LTR bits should be cleared

        # Check that PM capability is still present but modified
        pm_offset = find_cap(pruned_cfg, 0x01)
        self.assertIsNotNone(pm_offset)
        self.assertEqual(pm_offset, 0x60)

        # Check that only D0 and D3hot are supported in PM capability
        if pm_offset is not None:
            pm_cap_offset = (pm_offset + 2) * 2
            pm_cap = int(pruned_cfg[pm_cap_offset : pm_cap_offset + 4], 16)
            self.assertEqual(
                pm_cap & 0x0007, 0
            )  # D1, D2, D3cold bits should be cleared
            self.assertEqual(pm_cap & 0x0008, 0x0008)  # D3hot bit should be set
            self.assertEqual(
                pm_cap & 0x0F70, 0
            )  # PME support bits should be cleared (excluding D3hot bit)

        # Check that MSI-X capability is still present and unchanged
        msix_offset = find_cap(pruned_cfg, 0x11)
        self.assertEqual(msix_offset, 0x70)

        # Check that L1 PM Substates extended capability is removed
        l1pm_offset = find_ext_cap(pruned_cfg, 0x001E)
        self.assertIsNone(l1pm_offset)

        # Check that SR-IOV extended capability is removed
        sriov_offset = find_ext_cap(pruned_cfg, 0x0010)
        self.assertIsNone(sriov_offset)

    def test_prune_capabilities_by_rules(self):
        """Test pruning capabilities based on predefined rules."""
        # Apply pruning
        pruned_cfg = prune_capabilities_by_rules(self.config_space)

        # Check that the pruned configuration space is still valid
        self.assertEqual(len(pruned_cfg), len(self.config_space))

        # Check that PCIe capability is still present but modified
        pcie_offset = find_cap(pruned_cfg, 0x10)
        self.assertEqual(pcie_offset, 0x40)

        # Check that ASPM bits are cleared in Link Control register
        link_control_offset = 0x50 * 2
        link_control = int(
            pruned_cfg[link_control_offset : link_control_offset + 4], 16
        )
        self.assertEqual(link_control & 0x0003, 0)  # ASPM bits should be cleared

        # Check that OBFF and LTR bits are cleared in Device Control 2 register
        dev_control2_offset = 0x68 * 2
        dev_control2 = int(
            pruned_cfg[dev_control2_offset : dev_control2_offset + 4], 16
        )
        self.assertEqual(
            dev_control2 & 0x6400, 0
        )  # OBFF and LTR bits should be cleared

        # Check that PM capability is still present but modified
        pm_offset = find_cap(pruned_cfg, 0x01)
        self.assertIsNotNone(pm_offset)
        self.assertEqual(pm_offset, 0x60)

        # Check that only D0 and D3hot are supported in PM capability
        if pm_offset is not None:
            pm_cap_offset = (pm_offset + 2) * 2
            pm_cap = int(pruned_cfg[pm_cap_offset : pm_cap_offset + 4], 16)
            self.assertEqual(
                pm_cap & 0x0007, 0
            )  # D1, D2, D3cold bits should be cleared
            self.assertEqual(pm_cap & 0x0008, 0x0008)  # D3hot bit should be set
            self.assertEqual(
                pm_cap & 0x0F70, 0
            )  # PME support bits should be cleared (excluding D3hot bit)

        # Check that MSI-X capability is still present and unchanged
        msix_offset = find_cap(pruned_cfg, 0x11)
        self.assertEqual(msix_offset, 0x70)

        # Check that L1 PM Substates extended capability is removed
        l1pm_offset = find_ext_cap(pruned_cfg, 0x001E)
        self.assertIsNone(l1pm_offset)

        # Check that SR-IOV extended capability is removed
        sriov_offset = find_ext_cap(pruned_cfg, 0x0010)
        self.assertIsNone(sriov_offset)


if __name__ == "__main__":
    unittest.main()
