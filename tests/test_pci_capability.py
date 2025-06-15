#!/usr/bin/env python3
"""
Test suite for PCI capability analysis and pruning - Updated for Phase 3 Integration.
"""

import unittest

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
        # Use 256 bytes (512 hex chars) as minimum size for new implementation

        # Start with a 256-byte configuration space filled with zeros
        self.config_space = "00" * 256

        # Set capabilities pointer at offset 0x34
        self.config_space = (
            self.config_space[: 0x34 * 2] + "40" + self.config_space[0x34 * 2 + 2 :]
        )

        # Set capabilities bit in status register (offset 0x06, bit 4)
        # Status register is little-endian, so bit 4 is in the low byte
        status_low = int(self.config_space[0x06 * 2 : 0x06 * 2 + 2], 16) | 0x10
        status_high = int(self.config_space[0x06 * 2 + 2 : 0x06 * 2 + 4], 16)
        status_hex = f"{status_low:02x}{status_high:02x}"
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

        # Create extended configuration space for extended capabilities
        # Extended config space is 4KB total, so we need 4096 bytes = 8192 hex chars
        self.ext_config_space = "00" * 4096

        # Copy the standard config space to the beginning
        self.ext_config_space = (
            self.config_space + self.ext_config_space[len(self.config_space) :]
        )

        # Add L1 PM Substates extended capability at offset 0x100
        # Extended Capability Header format (32-bit little-endian):
        # Bits [15:0] = Capability ID (0x001E)
        # Bits [19:16] = Capability Version (0x1)
        # Bits [31:20] = Next Capability Offset (0x140)
        # Header = (0x140 << 20) | (0x1 << 16) | 0x001E = 0x1401001E
        # Store in little-endian format
        l1pm_header_value = 0x1401001E
        l1pm_header = f"{l1pm_header_value & 0xFF:02x}{(l1pm_header_value >> 8) & 0xFF:02x}{(l1pm_header_value >> 16) & 0xFF:02x}{(l1pm_header_value >> 24) & 0xFF:02x}"
        l1pm_cap = l1pm_header + "01000000" + "02000000" + "03000000"
        self.ext_config_space = (
            self.ext_config_space[: 0x100 * 2]
            + l1pm_cap
            + self.ext_config_space[0x100 * 2 + len(l1pm_cap) :]
        )

        # Add SR-IOV extended capability at offset 0x140
        # Extended Capability Header format (32-bit little-endian):
        # Bits [15:0] = Capability ID (0x0010)
        # Bits [19:16] = Capability Version (0x1)
        # Bits [31:20] = Next Capability Offset (0x000 - end of list)
        # Header = (0x000 << 20) | (0x1 << 16) | 0x0010 = 0x00010010
        # Store in little-endian format
        sriov_header_value = 0x00010010
        sriov_header = f"{sriov_header_value & 0xFF:02x}{(sriov_header_value >> 8) & 0xFF:02x}{(sriov_header_value >> 16) & 0xFF:02x}{(sriov_header_value >> 24) & 0xFF:02x}"
        sriov_cap = sriov_header + "04000000" + "05000000" + "06000000"
        self.ext_config_space = (
            self.ext_config_space[: 0x140 * 2]
            + sriov_cap
            + self.ext_config_space[0x140 * 2 + len(sriov_cap) :]
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
        cap_offset = find_ext_cap(self.ext_config_space, 0x001E)
        self.assertEqual(cap_offset, 0x100)

        # Find SR-IOV extended capability (ID 0x0010)
        cap_offset = find_ext_cap(self.ext_config_space, 0x0010)
        self.assertEqual(cap_offset, 0x140)

        # Try to find a non-existent extended capability
        cap_offset = find_ext_cap(self.ext_config_space, 0x0020)
        self.assertIsNone(cap_offset)

    def test_get_all_capabilities(self):
        """Test getting all standard capabilities in the configuration space."""
        capabilities = get_all_capabilities(self.config_space)

        # Should find 3 capabilities
        self.assertEqual(len(capabilities), 3)

        # Check that all expected offsets are present
        self.assertIn(0x40, capabilities)
        self.assertIn(0x60, capabilities)
        self.assertIn(0x70, capabilities)

        # Check the capability IDs
        self.assertEqual(capabilities[0x40]["id"], PCICapabilityID.PCI_EXPRESS.value)
        self.assertEqual(
            capabilities[0x60]["id"], PCICapabilityID.POWER_MANAGEMENT.value
        )
        self.assertEqual(capabilities[0x70]["id"], PCICapabilityID.MSI_X.value)

    def test_get_all_ext_capabilities(self):
        """Test getting all extended capabilities in the configuration space."""
        ext_capabilities = get_all_ext_capabilities(self.ext_config_space)

        # Should find 2 extended capabilities
        self.assertEqual(len(ext_capabilities), 2)

        # Check that all expected offsets are present
        self.assertIn(0x100, ext_capabilities)
        self.assertIn(0x140, ext_capabilities)

        # Check the capability IDs
        self.assertEqual(ext_capabilities[0x100]["id"], 0x001E)  # L1 PM Substates
        self.assertEqual(ext_capabilities[0x140]["id"], 0x0010)  # SR-IOV

    def test_categorize_capabilities(self):
        """Test categorizing capabilities based on emulation feasibility."""
        # Get all capabilities
        std_caps = get_all_capabilities(self.config_space)
        ext_caps = get_all_ext_capabilities(self.ext_config_space)

        # Categorize capabilities
        std_categories = categorize_capabilities(std_caps)
        ext_categories = categorize_capabilities(ext_caps)

        # Check that PCIe is partially supported
        self.assertEqual(std_categories[0x40], EmulationCategory.PARTIALLY_SUPPORTED)

        # Check that PM is partially supported
        self.assertEqual(std_categories[0x60], EmulationCategory.PARTIALLY_SUPPORTED)

        # Check that MSI-X is fully supported
        self.assertEqual(std_categories[0x70], EmulationCategory.FULLY_SUPPORTED)

        # Check that L1 PM Substates is unsupported
        self.assertEqual(ext_categories[0x100], EmulationCategory.UNSUPPORTED)

        # Check that SR-IOV is unsupported
        self.assertEqual(ext_categories[0x140], EmulationCategory.UNSUPPORTED)

    def test_determine_pruning_actions(self):
        """Test determining pruning actions based on capability categories."""
        # Get all capabilities
        std_caps = get_all_capabilities(self.config_space)
        ext_caps = get_all_ext_capabilities(self.ext_config_space)

        # Categorize capabilities
        std_categories = categorize_capabilities(std_caps)
        ext_categories = categorize_capabilities(ext_caps)

        # Determine pruning actions
        std_actions = determine_pruning_actions(std_caps, std_categories)
        ext_actions = determine_pruning_actions(ext_caps, ext_categories)

        # Check pruning actions for standard capabilities
        self.assertEqual(
            std_actions[0x40], PruningAction.MODIFY
        )  # PCIe - partially supported
        self.assertEqual(
            std_actions[0x60], PruningAction.MODIFY
        )  # PM - partially supported
        self.assertEqual(
            std_actions[0x70], PruningAction.KEEP
        )  # MSI-X - fully supported

        # Check pruning actions for extended capabilities
        self.assertEqual(
            ext_actions[0x100], PruningAction.REMOVE
        )  # L1 PM Substates - unsupported
        self.assertEqual(
            ext_actions[0x140], PruningAction.REMOVE
        )  # SR-IOV - unsupported

    def test_prune_capabilities(self):
        """Test pruning capabilities from the configuration space."""
        # Get all capabilities
        std_caps = get_all_capabilities(self.config_space)
        ext_caps = get_all_ext_capabilities(self.ext_config_space)

        # Categorize capabilities
        std_categories = categorize_capabilities(std_caps)
        ext_categories = categorize_capabilities(ext_caps)

        # Determine pruning actions
        std_actions = determine_pruning_actions(std_caps, std_categories)
        ext_actions = determine_pruning_actions(ext_caps, ext_categories)

        # Combine actions for both standard and extended capabilities
        all_actions = {**std_actions, **ext_actions}

        # Prune capabilities
        pruned_cfg = prune_capabilities(self.ext_config_space, all_actions)

        # Check that PCIe capability is still present but modified
        pcie_offset = find_cap(pruned_cfg, 0x10)
        self.assertEqual(pcie_offset, 0x40)

        # Verify that ASPM is disabled in Link Control register
        link_control_offset = 0x40 + 0x10  # PCIe cap + Link Control offset
        link_control_value = int(
            pruned_cfg[link_control_offset * 2 : link_control_offset * 2 + 4], 16
        )
        aspm_bits = link_control_value & 0x0003
        self.assertEqual(aspm_bits, 0)  # ASPM should be disabled

        # Check that PM capability is still present but modified
        pm_offset = find_cap(pruned_cfg, 0x01)
        self.assertIsNotNone(pm_offset)

        # Verify that D3hot support is disabled in PM Capabilities register
        if pm_offset is not None:
            pm_cap_offset = pm_offset + 2  # PM cap + PMC register offset
            pm_cap_value = int(
                pruned_cfg[pm_cap_offset * 2 : pm_cap_offset * 2 + 4], 16
            )
            d3hot_bit = pm_cap_value & 0x0008
            self.assertEqual(d3hot_bit, 0)  # D3hot support should be disabled

        # Check that MSI-X capability is still present and unchanged
        msix_offset = find_cap(pruned_cfg, 0x11)
        self.assertEqual(msix_offset, 0x70)

        # Check that extended capabilities are removed
        l1pm_offset = find_ext_cap(pruned_cfg, 0x001E)
        self.assertIsNone(l1pm_offset)

        sriov_offset = find_ext_cap(pruned_cfg, 0x0010)
        self.assertIsNone(sriov_offset)

    def test_prune_capabilities_by_rules(self):
        """Test pruning capabilities using the rule-based approach."""
        # Prune capabilities using rules
        pruned_cfg = prune_capabilities_by_rules(self.ext_config_space)

        # Check that PCIe capability is still present but modified
        pcie_offset = find_cap(pruned_cfg, 0x10)
        self.assertEqual(pcie_offset, 0x40)

        # Verify that ASPM is disabled in Link Control register
        link_control_offset = 0x40 + 0x10  # PCIe cap + Link Control offset
        link_control_value = int(
            pruned_cfg[link_control_offset * 2 : link_control_offset * 2 + 4], 16
        )
        aspm_bits = link_control_value & 0x0003
        self.assertEqual(aspm_bits, 0)  # ASPM should be disabled

        # Verify that OBFF and LTR are disabled in Device Control 2 register
        dev_control2_offset = 0x40 + 0x28  # PCIe cap + Device Control 2 offset
        dev_control2_value = int(
            pruned_cfg[dev_control2_offset * 2 : dev_control2_offset * 2 + 4], 16
        )
        obff_ltr_bits = dev_control2_value & 0x6400
        self.assertEqual(obff_ltr_bits, 0)  # OBFF and LTR should be disabled

        # Check that PM capability is still present but modified
        pm_offset = find_cap(pruned_cfg, 0x01)
        self.assertIsNotNone(pm_offset)

        # Verify that D3hot support is disabled in PM Capabilities register
        if pm_offset is not None:
            pm_cap_offset = pm_offset + 2  # PM cap + PMC register offset
            pm_cap_value = int(
                pruned_cfg[pm_cap_offset * 2 : pm_cap_offset * 2 + 4], 16
            )
            d3hot_bit = pm_cap_value & 0x0008
            self.assertEqual(d3hot_bit, 0)  # D3hot support should be disabled

        # Check that MSI-X capability is still present and unchanged
        msix_offset = find_cap(pruned_cfg, 0x11)
        self.assertEqual(msix_offset, 0x70)

        # Check that extended capabilities are removed
        l1pm_offset = find_ext_cap(pruned_cfg, 0x001E)
        self.assertIsNone(l1pm_offset)

        sriov_offset = find_ext_cap(pruned_cfg, 0x0010)
        self.assertIsNone(sriov_offset)


if __name__ == "__main__":
    unittest.main()
