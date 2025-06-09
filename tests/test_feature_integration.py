#!/usr/bin/env python3
"""
Integration test for all PCILeech FPGA firmware generator features.

This test verifies that all implemented features work together seamlessly:
1. Full 4 KB config-space shadow in BRAM
2. Auto-replicate MSI-X table exactly
3. Prune capabilities that can't be faithfully emulated
4. Deterministic variance seeding
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.build import build_tcl, get_donor_info
from src.donor_dump_manager import DonorDumpManager
from src.manufacturing_variance import DeviceClass, ManufacturingVarianceSimulator
from src.msix_capability import parse_msix_capability
from src.pci_capability import prune_capabilities_by_rules


class TestFeatureIntegration(unittest.TestCase):
    """Test cases for integration of all PCILeech FPGA firmware generator features."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.donor_info_path = os.path.join(self.temp_dir.name, "donor_info.json")
        self.config_hex_path = os.path.join(self.temp_dir.name, "config_space_init.hex")

        # Sample configuration space data (simplified for testing)
        self.sample_config_space = "".join(["0123456789abcdef"] * 256)  # 4096 bytes

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
            "dsn_hi": "0x12345678",
            "dsn_lo": "0x90ABCDEF",
            "donor_info_path": self.donor_info_path,
        }

        # Save sample device info to file
        with open(self.donor_info_path, "w") as f:
            json.dump(self.sample_device_info, f)

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_config_space_shadow_integration(self):
        """Test that config space shadow is properly integrated."""
        # Call build_tcl
        tcl_content, tcl_path = build_tcl(
            self.sample_device_info, "vivado_generate_project_75t.tcl"
        )

        # Verify the TCL content includes config_space_init.hex
        self.assertIn("config_space_init.hex", tcl_content)

        # Clean up
        if os.path.exists(tcl_path):
            os.unlink(tcl_path)

    def test_msix_table_replication(self):
        """Test that MSI-X table replication is properly integrated."""
        # Parse MSI-X capability
        msix_info = parse_msix_capability(self.config_space)

        # Verify MSI-X capability was correctly parsed
        self.assertEqual(msix_info["table_size"], 8)
        self.assertEqual(msix_info["table_bir"], 0)
        self.assertEqual(msix_info["table_offset"], 0x2000)
        self.assertEqual(msix_info["pba_bir"], 0)
        self.assertEqual(msix_info["pba_offset"], 0x3000)

        # Call build_tcl
        tcl_content, tcl_path = build_tcl(
            self.sample_device_info, "vivado_generate_project_75t.tcl"
        )

        # Verify MSI-X parameters are included in TCL
        self.assertIn("MSIX_CAP_ENABLE", tcl_content)
        self.assertIn("MSIX_CAP_TABLE_SIZE", tcl_content)
        self.assertIn("MSIX_CAP_TABLE_BIR", tcl_content)
        self.assertIn("MSIX_CAP_TABLE_OFFSET", tcl_content)
        self.assertIn("MSIX_CAP_PBA_BIR", tcl_content)
        self.assertIn("MSIX_CAP_PBA_OFFSET", tcl_content)

        # Clean up
        if os.path.exists(tcl_path):
            os.unlink(tcl_path)

    def test_capability_pruning(self):
        """Test that capability pruning is properly integrated."""
        # Apply capability pruning
        pruned_config = prune_capabilities_by_rules(self.config_space)

        # Verify that pruning was applied
        self.assertNotEqual(pruned_config, self.config_space)

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

        # Update sample device info with pruned config
        self.sample_device_info["extended_config"] = pruned_config

        # Save updated device info to file
        with open(self.donor_info_path, "w") as f:
            json.dump(self.sample_device_info, f)

        # Call build_tcl
        tcl_content, tcl_path = build_tcl(
            self.sample_device_info, "vivado_generate_project_75t.tcl"
        )

        # Clean up
        if os.path.exists(tcl_path):
            os.unlink(tcl_path)

    def test_deterministic_variance_seeding(self):
        """Test that deterministic variance seeding is properly integrated."""
        # Create a variance simulator
        simulator = ManufacturingVarianceSimulator()

        # Extract DSN from device info
        dsn_hi = int(self.sample_device_info["dsn_hi"], 16)
        dsn_lo = int(self.sample_device_info["dsn_lo"], 16)
        dsn = (dsn_hi << 32) | dsn_lo

        # Use a fixed revision for testing
        revision = "abcdef1234567890abcd"

        # Generate a variance model with deterministic seeding
        model1 = simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        # Create a second simulator and generate another model with the same parameters
        simulator2 = ManufacturingVarianceSimulator()
        model2 = simulator2.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        # Verify that both models have identical variance parameters
        self.assertEqual(model1.clock_jitter_percent, model2.clock_jitter_percent)
        self.assertEqual(
            model1.register_timing_jitter_ns, model2.register_timing_jitter_ns
        )
        self.assertEqual(model1.power_noise_percent, model2.power_noise_percent)
        self.assertEqual(
            model1.temperature_drift_ppm_per_c, model2.temperature_drift_ppm_per_c
        )
        self.assertEqual(
            model1.process_variation_percent, model2.process_variation_percent
        )
        self.assertEqual(model1.propagation_delay_ps, model2.propagation_delay_ps)
        self.assertEqual(model1.operating_temp_c, model2.operating_temp_c)
        self.assertEqual(model1.supply_voltage_v, model2.supply_voltage_v)

        # Generate a model with different DSN
        different_dsn = dsn + 1
        different_model = simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=different_dsn,
            revision=revision,
        )

        # Verify that the model with different DSN has different variance parameters
        self.assertNotEqual(
            model1.clock_jitter_percent, different_model.clock_jitter_percent
        )

    def test_all_features_integration(self):
        """Test that all features work together seamlessly."""
        # Mock command line arguments
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

        # Import the build module
        from src import build

        # Mock the necessary functions
        with patch("src.build.get_donor_info", return_value=self.sample_device_info):
            with patch(
                "src.build.build_tcl", return_value=("tcl_content", "patch_tcl_path")
            ):
                with patch("src.build.vivado_run"):
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
                            "src.build.scrape_driver_regs",
                            return_value=(sample_regs, {}),
                        ):
                            with patch("src.build.build_sv"):
                                # Mock the build_tcl function to create the config_hex_path file
                                original_build_tcl = build.build_tcl

                                def patched_build_tcl(info, gen_tcl, args=None):
                                    # Apply capability pruning
                                    pruned_config = prune_capabilities_by_rules(
                                        info["extended_config"]
                                    )

                                    # Update the donor info with the pruned configuration
                                    info["extended_config"] = pruned_config

                                    # Create a serializable copy of the info dictionary
                                    serializable_info = {}
                                    for key, value in info.items():
                                        # Skip MagicMock objects or replace them with a serializable value
                                        if not isinstance(value, MagicMock):
                                            serializable_info[key] = value
                                        else:
                                            # Replace MagicMock with a placeholder string
                                            serializable_info[key] = "mock_value"

                                    # Save the serializable donor info to a file
                                    with open(self.donor_info_path, "w") as f:
                                        json.dump(serializable_info, f)

                                    # Create the config_hex_path file
                                    with open(self.config_hex_path, "w") as f:
                                        f.write(pruned_config)

                                    # Call the original function
                                    return original_build_tcl(info, gen_tcl, args)

                                with patch(
                                    "src.build.build_tcl", side_effect=patched_build_tcl
                                ):
                                    # Call the main function with mocked arguments
                                    with patch(
                                        "sys.argv",
                                        [
                                            "build.py",
                                            "--bdf",
                                            "0000:03:00.0",
                                            "--board",
                                            "75t",
                                        ],
                                    ):
                                        with patch(
                                            "argparse.ArgumentParser.parse_args",
                                            return_value=args,
                                        ):
                                            # Capture print output
                                            with patch("builtins.print"):
                                                try:
                                                    build.main()
                                                except SystemExit:
                                                    pass  # Ignore SystemExit

        # Verify that the pruned configuration space was saved
        self.assertTrue(os.path.exists(self.config_hex_path))

        # Read the pruned configuration space from the donor info
        with open(self.donor_info_path, "r") as f:
            donor_info = json.load(f)

        pruned_config = donor_info["extended_config"]

        # Verify that PCIe capability is still present but modified
        from src.pci_capability import PCICapabilityID, find_cap

        pcie_offset = find_cap(pruned_config, PCICapabilityID.PCI_EXPRESS.value)
        self.assertIsNotNone(pcie_offset)

        # Check that MSI-X capability is still present and unchanged
        msix_offset = find_cap(pruned_config, PCICapabilityID.MSI_X.value)
        self.assertIsNotNone(msix_offset)

        # Parse MSI-X capability from the pruned configuration
        msix_info = parse_msix_capability(pruned_config)
        self.assertEqual(msix_info["table_size"], 8)


if __name__ == "__main__":
    unittest.main()
