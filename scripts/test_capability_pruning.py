#!/usr/bin/env python3
"""
Test script for PCI capability pruning functionality.

This script demonstrates the capability pruning feature by:
1. Creating a sample configuration space with various capabilities
2. Applying the pruning rules
3. Displaying the changes made to the configuration space
"""

import sys
import tempfile
from pathlib import Path

from src.pci_capability import (
    PCICapabilityID,
    PCIExtCapabilityID,
    find_cap,
    find_ext_cap,
    get_all_capabilities,
    get_all_ext_capabilities,
    prune_capabilities_by_rules,
)

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_sample_config_space():
    """Create a sample configuration space with various capabilities."""
    # Start with a 4KB configuration space filled with zeros
    config_space = "00" * 4096

    # Set capabilities pointer at offset 0x34
    config_space = config_space[: 0x34 * 2] + "40" + config_space[0x34 * 2 + 2 :]

    # Set capabilities bit in status register (offset 0x06, bit 4)
    status_value = int(config_space[0x06 * 2 : 0x06 * 2 + 4], 16) | 0x10
    status_hex = f"{status_value:04x}"
    config_space = config_space[: 0x06 * 2] + status_hex + config_space[0x06 * 2 + 4 :]

    # Add PCI Express capability at offset 0x40
    # Capability ID: 0x10 (PCIe)
    # Next pointer: 0x60 (next capability)
    # PCI Express Capabilities Register: 0x0002 (Endpoint device)
    pcie_cap = "10" + "60" + "0200" + "00000000" + "00000000" + "00000000"
    config_space = (
        config_space[: 0x40 * 2] + pcie_cap + config_space[0x40 * 2 + len(pcie_cap) :]
    )

    # Add Link Control Register at offset 0x50 (part of PCIe capability)
    link_control = "0001" + "0000"  # ASPM L0s enabled
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

    # Add Power Management capability at offset 0x60
    # Capability ID: 0x01 (PM)
    # Next pointer: 0x70 (next capability)
    # PM Capabilities Register: 0x03 (D0, D1, D2, D3hot supported)
    pm_cap = "01" + "70" + "0300" + "00000000"
    config_space = (
        config_space[: 0x60 * 2] + pm_cap + config_space[0x60 * 2 + len(pm_cap) :]
    )

    # Add MSI-X capability at offset 0x70
    # Capability ID: 0x11 (MSI-X)
    # Next pointer: 0x00 (end of list)
    # Message Control: 0x0007 (8 table entries, function not masked, MSI-X disabled)
    # Table offset/BIR: 0x00002000 (offset 0x2000, BIR 0)
    # PBA offset/BIR: 0x00003000 (offset 0x3000, BIR 0)
    msix_cap = "11" + "00" + "0700" + "00002000" + "00003000"
    config_space = (
        config_space[: 0x70 * 2] + msix_cap + config_space[0x70 * 2 + len(msix_cap) :]
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
    config_space = (
        config_space[: 0x100 * 2] + l1pm_cap + config_space[0x100 * 2 + len(l1pm_cap) :]
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
    config_space = (
        config_space[: 0x140 * 2]
        + sriov_cap
        + config_space[0x140 * 2 + len(sriov_cap) :]
    )

    return config_space


def print_capability_info(cap_type, cap_id, offset, name):
    """Print information about a capability."""
    print(
        f"  {cap_type} Capability: {name} (ID: 0x{
            cap_id:02x}, Offset: 0x{
            offset:03x})"
    )


def analyze_config_space(config_space, title):
    """Analyze and print information about capabilities in the configuration space."""
    print(f"\n{title}")
    print("=" * len(title))

    # Get standard capabilities
    std_caps = get_all_capabilities(config_space)
    print(f"Standard Capabilities: {len(std_caps)}")
    for offset, cap in sorted(std_caps.items()):
        print_capability_info("Standard", cap["id"], offset, cap["name"])

    # Get extended capabilities
    ext_caps = get_all_ext_capabilities(config_space)
    print(f"\nExtended Capabilities: {len(ext_caps)}")
    for offset, cap in sorted(ext_caps.items()):
        print_capability_info("Extended", cap["id"], offset, cap["name"])

    # Check specific capabilities of interest

    # PCIe capability
    pcie_offset = find_cap(config_space, PCICapabilityID.PCI_EXPRESS.value)
    if pcie_offset is not None:
        # Check Link Control register
        link_control_offset = 0x50 * 2
        link_control = int(
            config_space[link_control_offset : link_control_offset + 4], 16
        )
        aspm_enabled = link_control & 0x0003
        print(
            f"\nPCIe Link Control: ASPM {
                'enabled' if aspm_enabled else 'disabled'}"
        )

        # Check Device Control 2 register
        dev_control2_offset = 0x68 * 2
        dev_control2 = int(
            config_space[dev_control2_offset : dev_control2_offset + 4], 16
        )
        obff_ltr_enabled = dev_control2 & 0x6400
        print(
            f"PCIe Device Control 2: OBFF/LTR {'enabled' if obff_ltr_enabled else 'disabled'}"
        )

    # Power Management capability
    pm_offset = find_cap(config_space, PCICapabilityID.POWER_MANAGEMENT.value)
    if pm_offset is not None:
        pm_cap_offset = (pm_offset + 2) * 2
        pm_cap = int(config_space[pm_cap_offset : pm_cap_offset + 4], 16)
        d1_support = pm_cap & 0x0002
        d2_support = pm_cap & 0x0004
        d3hot_support = pm_cap & 0x0008
        pme_support = pm_cap & 0x0F78
        print(
            f"\nPower Management: D1 {
                'supported' if d1_support else 'not supported'}, "
            f"D2 {
                'supported' if d2_support else 'not supported'}, "
            f"D3hot {
                'supported' if d3hot_support else 'not supported'}, "
            f"PME {
                    'supported' if pme_support else 'not supported'}"
        )

    # L1 PM Substates extended capability - direct check since find_ext_cap
    # might fail due to invalid next pointer
    l1pm_present = False
    l1pm_offset = 0x100  # Known offset from our test data
    if len(config_space) >= (l1pm_offset + 2) * 2:
        header_bytes = config_space[l1pm_offset * 2 : l1pm_offset * 2 + 4]
        try:
            cap_id = int(header_bytes, 16)
            if cap_id == PCIExtCapabilityID.L1_PM_SUBSTATES.value:
                l1pm_present = True
        except ValueError:
            pass

    print(f"\nL1 PM Substates: {'present' if l1pm_present else 'not present'}")

    # SR-IOV extended capability
    sriov_offset = find_ext_cap(
        config_space, PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value
    )
    print(f"SR-IOV: {'present' if sriov_offset is not None else 'not present'}")


def main():
    """Main function."""
    # Create a sample configuration space
    original_config = create_sample_config_space()

    # Analyze the original configuration space
    analyze_config_space(original_config, "Original Configuration Space")

    # Apply capability pruning
    pruned_config = prune_capabilities_by_rules(original_config)

    # Analyze the pruned configuration space
    analyze_config_space(pruned_config, "Pruned Configuration Space")

    # Save the configuration spaces to temporary files
    with tempfile.NamedTemporaryFile(suffix=".hex", delete=False) as f_original:
        original_path = f_original.name
        for i in range(0, len(original_config), 8):
            if i + 8 <= len(original_config):
                f_original.write(f"{original_config[i:i + 8]}\n".encode())

    with tempfile.NamedTemporaryFile(suffix=".hex", delete=False) as f_pruned:
        pruned_path = f_pruned.name
        for i in range(0, len(pruned_config), 8):
            if i + 8 <= len(pruned_config):
                f_pruned.write(f"{pruned_config[i:i + 8]}\n".encode())

    print(f"\nOriginal configuration space saved to: {original_path}")
    print(f"Pruned configuration space saved to: {pruned_path}")
    print(
        "\nYou can compare these files with a diff tool to see the exact changes made."
    )


if __name__ == "__main__":
    main()
