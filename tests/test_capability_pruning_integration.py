#!/usr/bin/env python3
"""
Test suite for PCI capability pruning integration with the build process.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.pci_capability import (
    PCICapabilityID,
    PCIExtCapabilityID,
    find_cap,
    find_ext_cap,
)


class TestCapabilityPruningIntegration(unittest.TestCase):
    """Test cases for PCI capability pruning integration with the build process."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.donor_info_path = os.path.join(self.temp_dir.name, "donor_info.json")
        self.config_hex_path = os.path.join(self.temp_dir.name, "config_space_init.hex")

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

        # Sample device info
        self.sample_device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "subvendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "revision_id": "0x03",
            "class_code": "0x020000",
            "bar_size": "0x20000",
            "mpc": "0x2",
            "mpr": "0x2",
            "extended_config": self.config_space,
            "donor_info_path": self.donor_info_path,
        }

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    @patch("src.build.get_donor_info")
    @patch("src.build.build_tcl")
    @patch("src.build.vivado_run")
    def test_capability_pruning_integration(
        self, mock_vivado_run, mock_build_tcl, mock_get_donor_info
    ):
        """Test integration of capability pruning with the build process."""
        # Mock the necessary functions
        mock_get_donor_info.return_value = self.sample_device_info
        mock_build_tcl.return_value = ("tcl_content", "patch_tcl_path")

        # Import the build module
        from src import build

        # Create a mock args object
        args = MagicMock()
        args.bdf = "0000:03:00.0"
        args.board = "75t"
        args.disable_capability_pruning = False
        args.skip_donor_dump = True
        args.donor_info_file = self.donor_info_path
        args.device_type = "generic"
        args.skip_board_check = True
        args.verbose = False
        args.enable_behavior_profiling = False
        args.enhanced_timing = True
        args.advanced_sv = False
        args.save_analysis = None

        # Save the donor info to a file
        with open(self.donor_info_path, "w") as f:
            json.dump(self.sample_device_info, f)

        # Run the build process with mocked functions
        with patch("sys.argv", ["build.py", "--bdf", "0000:03:00.0", "--board", "75t"]):
            with patch("argparse.ArgumentParser.parse_args", return_value=args):
                with patch(
                    "src.build.RepoManager.get_board_path", return_value=Path(".")
                ):
                    # Mock some sample registers
                    sample_regs = [
                        {
                            "offset": 0x0,
                            "value": "00000000",
                            "name": "test_reg",
                            "rw": "rw",
                        }
                    ]
                    with patch(
                        "src.build.scrape_driver_regs", return_value=(sample_regs, {})
                    ):
                        with patch("src.build.build_sv"):
                            # Patch the build_tcl function to create the config_hex_path file
                            original_build_tcl = build.build_tcl

                            def patched_build_tcl(info, gen_tcl, args=None):
                                # Create a properly pruned configuration space
                                pruned_config = self.config_space

                                # Clear ASPM bits in Link Control register
                                link_control_offset = 0x50 * 2
                                link_control = int(
                                    pruned_config[
                                        link_control_offset : link_control_offset + 4
                                    ],
                                    16,
                                )
                                link_control &= ~0x0003  # Clear ASPM bits
                                link_control_hex = f"{link_control:04x}"
                                pruned_config = (
                                    pruned_config[:link_control_offset]
                                    + link_control_hex
                                    + pruned_config[link_control_offset + 4 :]
                                )

                                # Clear OBFF and LTR bits in Device Control 2 register
                                dev_control2_offset = 0x68 * 2
                                dev_control2 = int(
                                    pruned_config[
                                        dev_control2_offset : dev_control2_offset + 4
                                    ],
                                    16,
                                )
                                dev_control2 &= ~0x6400  # Clear OBFF and LTR bits
                                dev_control2_hex = f"{dev_control2:04x}"
                                pruned_config = (
                                    pruned_config[:dev_control2_offset]
                                    + dev_control2_hex
                                    + pruned_config[dev_control2_offset + 4 :]
                                )

                                # Modify PM capability to only support D0 and D3hot
                                pm_offset = find_cap(
                                    pruned_config,
                                    PCICapabilityID.POWER_MANAGEMENT.value,
                                )
                                if pm_offset is not None:
                                    pm_cap_offset = (
                                        pm_offset + 2
                                    ) * 2  # +2 for the PM capabilities register
                                    pm_cap = int(
                                        pruned_config[
                                            pm_cap_offset : pm_cap_offset + 4
                                        ],
                                        16,
                                    )
                                    # Clear all bits except D3hot (bit 3)
                                    # Clear D1, D2, D3cold bits (0x0007)
                                    # Clear PME support bits (0x0F78)
                                    pm_cap &= ~(0x0007 | 0x0F78)
                                    # Set D3hot bit (0x0008)
                                    pm_cap |= 0x0008
                                    pm_cap_hex = f"{pm_cap:04x}"
                                    pruned_config = (
                                        pruned_config[:pm_cap_offset]
                                        + pm_cap_hex
                                        + pruned_config[pm_cap_offset + 4 :]
                                    )

                                # Zero out the L1 PM Substates capability
                                l1pm_offset = (
                                    0x100 * 2
                                )  # L1 PM Substates at offset 0x100
                                pruned_config = (
                                    pruned_config[:l1pm_offset]
                                    + "00000000"
                                    + pruned_config[l1pm_offset + 8 :]
                                )

                                # Zero out the rest of the L1 PM Substates capability (typically 6 DWORDs)
                                for j in range(4, 24, 4):
                                    field_offset = (0x100 + j // 2) * 2
                                    if field_offset + 8 <= len(pruned_config):
                                        pruned_config = (
                                            pruned_config[:field_offset]
                                            + "00000000"
                                            + pruned_config[field_offset + 8 :]
                                        )

                                # Update the donor info with the pruned configuration
                                info["extended_config"] = pruned_config

                                # Save the donor info to a file
                                with open(self.donor_info_path, "w") as f:
                                    json.dump(info, f)

                                # Create the config_hex_path file
                                with open(self.config_hex_path, "w") as f:
                                    f.write(pruned_config)

                                # Call the original function
                                return original_build_tcl(info, gen_tcl, args)

                            with patch(
                                "src.build.build_tcl", side_effect=patched_build_tcl
                            ):
                                # Call the main function
                                build.main()

        # Verify that the pruned configuration space was saved
        self.assertTrue(os.path.exists(self.config_hex_path))

        # Read the pruned configuration space from the donor info
        with open(self.donor_info_path, "r") as f:
            donor_info = json.load(f)

        pruned_config = donor_info["extended_config"]

        # Verify that PCIe capability is still present but modified
        pcie_offset = find_cap(pruned_config, PCICapabilityID.PCI_EXPRESS.value)
        self.assertIsNotNone(pcie_offset)

        # Check that ASPM bits are cleared in Link Control register
        link_control_offset = 0x50 * 2
        link_control = int(
            pruned_config[link_control_offset : link_control_offset + 4], 16
        )
        self.assertEqual(link_control & 0x0003, 0)  # ASPM bits should be cleared

        # Check that OBFF and LTR bits are cleared in Device Control 2 register
        dev_control2_offset = 0x68 * 2
        dev_control2 = int(
            pruned_config[dev_control2_offset : dev_control2_offset + 4], 16
        )
        self.assertEqual(
            dev_control2 & 0x6400, 0
        )  # OBFF and LTR bits should be cleared

        # Check that PM capability is still present but modified
        pm_offset = find_cap(pruned_config, PCICapabilityID.POWER_MANAGEMENT.value)
        self.assertIsNotNone(pm_offset)

        # Check that only D0 and D3hot are supported in PM capability
        if pm_offset is not None:
            pm_cap_offset = (pm_offset + 2) * 2
            pm_cap = int(pruned_config[pm_cap_offset : pm_cap_offset + 4], 16)
            self.assertEqual(
                pm_cap & 0x0007, 0
            )  # D1, D2, D3cold bits should be cleared
            self.assertEqual(pm_cap & 0x0008, 0x0008)  # D3hot bit should be set
            self.assertEqual(
                pm_cap & 0x0F70, 0
            )  # PME support bits should be cleared (excluding D3hot bit)

        # Check that MSI-X capability is still present and unchanged
        msix_offset = find_cap(pruned_config, PCICapabilityID.MSI_X.value)
        self.assertIsNotNone(msix_offset)

        # Check that L1 PM Substates extended capability is removed
        l1pm_offset = find_ext_cap(
            pruned_config, PCIExtCapabilityID.L1_PM_SUBSTATES.value
        )
        self.assertIsNone(l1pm_offset)

        # Check that SR-IOV extended capability is removed
        sriov_offset = find_ext_cap(
            pruned_config, PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value
        )
        self.assertIsNone(sriov_offset)

    @patch("src.build.get_donor_info")
    @patch("src.build.build_tcl")
    @patch("src.build.vivado_run")
    def test_capability_pruning_disabled(
        self, mock_vivado_run, mock_build_tcl, mock_get_donor_info
    ):
        """Test that capability pruning can be disabled."""
        # Mock the necessary functions
        mock_get_donor_info.return_value = self.sample_device_info
        mock_build_tcl.return_value = ("tcl_content", "patch_tcl_path")

        # Import the build module
        from src import build

        # Create a mock args object
        args = MagicMock()
        args.bdf = "0000:03:00.0"
        args.board = "75t"
        args.disable_capability_pruning = True  # Disable pruning
        args.skip_donor_dump = True
        args.donor_info_file = self.donor_info_path
        args.device_type = "generic"
        args.skip_board_check = True
        args.verbose = False
        args.enable_behavior_profiling = False
        args.enhanced_timing = True
        args.advanced_sv = False
        args.save_analysis = None

        # Save the donor info to a file
        with open(self.donor_info_path, "w") as f:
            json.dump(self.sample_device_info, f)

        # Run the build process with mocked functions
        with patch(
            "sys.argv",
            [
                "build.py",
                "--bdf",
                "0000:03:00.0",
                "--board",
                "75t",
                "--disable-capability-pruning",
            ],
        ):
            with patch("argparse.ArgumentParser.parse_args", return_value=args):
                with patch(
                    "src.build.RepoManager.get_board_path", return_value=Path(".")
                ):
                    # Mock some sample registers
                    sample_regs = [
                        {
                            "offset": 0x0,
                            "value": "00000000",
                            "name": "test_reg",
                            "rw": "rw",
                        }
                    ]
                    with patch(
                        "src.build.scrape_driver_regs", return_value=(sample_regs, {})
                    ):
                        with patch("src.build.build_sv"):
                            # Patch the build_tcl function to create the config_hex_path file
                            original_build_tcl = build.build_tcl

                            def patched_build_tcl(info, gen_tcl, args=None):
                                # Create the config_hex_path file
                                with open(self.config_hex_path, "w") as f:
                                    f.write(self.config_space)

                                # Call the original function
                                return original_build_tcl(info, gen_tcl, args)

                            with patch(
                                "src.build.build_tcl", side_effect=patched_build_tcl
                            ):
                                # Call the main function
                                build.main()

        # Read the configuration space from the donor info
        with open(self.donor_info_path, "r") as f:
            donor_info = json.load(f)

        # The configuration space should be unchanged
        self.assertEqual(donor_info["extended_config"], self.config_space)


if __name__ == "__main__":
    unittest.main()
