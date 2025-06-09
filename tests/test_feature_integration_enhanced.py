#!/usr/bin/env python3
"""
Enhanced integration test suite for PCILeech FPGA firmware generator features.

This test suite focuses on testing the interactions between:
1. Full 4 KB Config-Space Shadow in BRAM
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

from src.donor_dump_manager import DonorDumpManager
from src.manufacturing_variance import DeviceClass, ManufacturingVarianceSimulator
from src.msix_capability import (
    find_cap,
    generate_msix_table_sv,
    msix_size,
    parse_msix_capability,
)
from src.pci_capability import (
    PCICapabilityID,
    PCIExtCapabilityID,
)
from src.pci_capability import find_cap as pci_find_cap
from src.pci_capability import (
    find_ext_cap,
    prune_capabilities_by_rules,
)


class TestFeatureIntegrationEnhanced(unittest.TestCase):
    """Enhanced integration tests for PCILeech FPGA firmware generator features."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.donor_info_path = os.path.join(self.temp_dir.name, "donor_info.json")
        self.config_hex_path = os.path.join(self.temp_dir.name, "config_space_init.hex")

        # Create a sample configuration space with all features
        self.config_space = self.create_sample_config_space()

        # Sample device info
        self.sample_device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "subvendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "revision_id": "0x03",
            "class_code": "0x020000",
            "bar_size": "0x20000",
            "dsn": "0x1234567890ABCDEF",  # Device Serial Number for deterministic seeding
            "mpc": "0x2",
            "mpr": "0x2",
            "extended_config": self.config_space,
        }

        # Save sample device info to file
        with open(self.donor_info_path, "w") as f:
            json.dump(self.sample_device_info, f)

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def create_sample_config_space(self):
        """Create a sample configuration space with all features."""
        # Start with a 4KB configuration space filled with zeros
        config_space = "00" * 4096

        # Set capabilities pointer at offset 0x34
        config_space = config_space[: 0x34 * 2] + "40" + config_space[0x34 * 2 + 2 :]

        # Set capabilities bit in status register (offset 0x06, bit 4)
        status_value = int(config_space[0x06 * 2 : 0x06 * 2 + 4], 16) | 0x10
        status_hex = f"{status_value:04x}"
        config_space = (
            config_space[: 0x06 * 2] + status_hex + config_space[0x06 * 2 + 4 :]
        )

        # Add PCIe capability at offset 0x40
        pcie_cap = "10" + "50" + "0200" + "00000000" + "00000000" + "00000000"
        config_space = (
            config_space[: 0x40 * 2]
            + pcie_cap
            + config_space[0x40 * 2 + len(pcie_cap) :]
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

        # Add Power Management capability at offset 0x50
        pm_cap = "01" + "60" + "0300" + "00000000"
        config_space = (
            config_space[: 0x50 * 2] + pm_cap + config_space[0x50 * 2 + len(pm_cap) :]
        )

        # Add MSI-X capability at offset 0x60
        msix_cap = "11" + "70" + "0007" + "00002000" + "00003000"
        config_space = (
            config_space[: 0x60 * 2]
            + msix_cap
            + config_space[0x60 * 2 + len(msix_cap) :]
        )

        # Add Vendor-specific capability at offset 0x70
        vendor_cap = "09" + "00" + "0000" + "00000000"
        config_space = (
            config_space[: 0x70 * 2]
            + vendor_cap
            + config_space[0x70 * 2 + len(vendor_cap) :]
        )

        # Add L1 PM Substates extended capability at offset 0x100
        l1pm_cap = "001E" + "1140" + "00000001" + "00000002" + "00000003"
        config_space = (
            config_space[: 0x100 * 2]
            + l1pm_cap
            + config_space[0x100 * 2 + len(l1pm_cap) :]
        )

        # Add SR-IOV extended capability at offset 0x140
        sriov_cap = "0010" + "1000" + "00000000" + "00000000" + "00000004" + "00000008"
        config_space = (
            config_space[: 0x140 * 2]
            + sriov_cap
            + config_space[0x140 * 2 + len(sriov_cap) :]
        )

        return config_space

    def test_config_space_shadow_with_pruned_capabilities(self):
        """Test config space shadow with pruned capabilities."""
        # Prune capabilities
        pruned_config = prune_capabilities_by_rules(self.config_space)

        # Verify pruning results
        # Vendor-specific capability should be removed
        vendor_offset = find_cap(pruned_config, PCICapabilityID.VENDOR_SPECIFIC.value)
        self.assertIsNone(vendor_offset)

        # SR-IOV extended capability should be removed
        sriov_offset = find_ext_cap(
            pruned_config, PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value
        )
        self.assertIsNone(sriov_offset)

        # Save pruned config space
        manager = DonorDumpManager()
        result = manager.save_config_space_hex(pruned_config, self.config_hex_path)
        self.assertTrue(result)

        # Verify the file exists
        self.assertTrue(os.path.exists(self.config_hex_path))

        # Verify file size (should be 4KB / 4 bytes per line = 1024 lines)
        with open(self.config_hex_path, "r") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 1024)

    def test_msix_table_replication_with_pruned_capabilities(self):
        """Test MSI-X table replication with pruned capabilities."""
        # Prune capabilities
        pruned_config = prune_capabilities_by_rules(self.config_space)

        # Parse MSI-X capability
        msix_info = parse_msix_capability(pruned_config)

        # Verify MSI-X capability is preserved
        self.assertEqual(msix_info["table_size"], 8)
        self.assertEqual(msix_info["table_bir"], 0)
        self.assertEqual(msix_info["table_offset"], 0x2000)
        self.assertEqual(msix_info["pba_bir"], 0)
        self.assertEqual(msix_info["pba_offset"], 0x3000)

        # Generate SystemVerilog code
        sv_code = generate_msix_table_sv(msix_info)

        # Verify the generated code
        self.assertIn("localparam NUM_MSIX = 8;", sv_code)
        self.assertIn("localparam MSIX_TABLE_BIR = 0;", sv_code)
        self.assertIn("localparam MSIX_TABLE_OFFSET = 32'h2000;", sv_code)
        self.assertIn("localparam MSIX_PBA_BIR = 0;", sv_code)
        self.assertIn("localparam MSIX_PBA_OFFSET = 32'h3000;", sv_code)

    def test_deterministic_variance_with_pruned_config_space(self):
        """Test deterministic variance seeding with pruned config space."""
        # Prune capabilities
        pruned_config = prune_capabilities_by_rules(self.config_space)

        # Create a device info with pruned config
        device_info = self.sample_device_info.copy()
        device_info["extended_config"] = pruned_config

        # Extract DSN and revision
        dsn = int(device_info["dsn"], 16)
        revision = "abcdef1234567890abcd"  # Simulated git commit hash

        # Create simulator
        simulator = ManufacturingVarianceSimulator()

        # Generate variance model
        model = simulator.generate_variance_model(
            device_id=device_info["device_id"],
            device_class=DeviceClass.ENTERPRISE,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        # Verify model is created
        self.assertEqual(model.device_id, device_info["device_id"])
        self.assertEqual(model.device_class, DeviceClass.ENTERPRISE)

        # Generate SystemVerilog code for a register
        sv_code = simulator.generate_systemverilog_timing_code(
            register_name="config_reg",
            base_delay_cycles=5,
            variance_model=model,
            offset=0x400,
        )

        # Verify the generated code
        self.assertIn("config_reg", sv_code)
        self.assertIn("Variance-aware timing", sv_code)
        self.assertIn("Device class: enterprise", sv_code)

    def test_end_to_end_integration(self):
        """Test end-to-end integration of all features."""
        # Step 1: Prune capabilities
        pruned_config = prune_capabilities_by_rules(self.config_space)

        # Step 2: Parse MSI-X capability
        msix_info = parse_msix_capability(pruned_config)

        # Step 3: Generate deterministic variance
        dsn = int(self.sample_device_info["dsn"], 16)
        revision = "abcdef1234567890abcd"  # Simulated git commit hash

        simulator = ManufacturingVarianceSimulator()
        model = simulator.generate_variance_model(
            device_id=self.sample_device_info["device_id"],
            device_class=DeviceClass.ENTERPRISE,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        # Step 4: Save pruned config space
        manager = DonorDumpManager()
        result = manager.save_config_space_hex(pruned_config, self.config_hex_path)
        self.assertTrue(result)

        # Step 5: Generate SystemVerilog code for MSI-X table
        msix_sv_code = generate_msix_table_sv(msix_info)

        # Step 6: Generate SystemVerilog code for variance-aware timing
        timing_sv_code = simulator.generate_systemverilog_timing_code(
            register_name="config_reg",
            base_delay_cycles=5,
            variance_model=model,
            offset=0x400,
        )

        # Verify all components
        # 1. Verify pruned config space
        self.assertIsNone(
            find_cap(pruned_config, PCICapabilityID.VENDOR_SPECIFIC.value)
        )
        self.assertIsNone(
            find_ext_cap(
                pruned_config, PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value
            )
        )

        # 2. Verify MSI-X table
        self.assertIn("localparam NUM_MSIX = 8;", msix_sv_code)

        # 3. Verify variance-aware timing
        self.assertIn("Device class: enterprise", timing_sv_code)

        # 4. Verify config space hex file
        with open(self.config_hex_path, "r") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 1024)

    def test_reproducibility_across_builds(self):
        """Test reproducibility across multiple builds with the same DSN and revision."""
        # Simulate multiple builds with the same DSN and revision
        dsn = int(self.sample_device_info["dsn"], 16)
        revision = "abcdef1234567890abcd"  # Simulated git commit hash

        # Create multiple simulators
        simulator1 = ManufacturingVarianceSimulator()
        simulator2 = ManufacturingVarianceSimulator()

        # Generate variance models
        model1 = simulator1.generate_variance_model(
            device_id=self.sample_device_info["device_id"],
            device_class=DeviceClass.ENTERPRISE,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        model2 = simulator2.generate_variance_model(
            device_id=self.sample_device_info["device_id"],
            device_class=DeviceClass.ENTERPRISE,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        # Generate SystemVerilog code
        sv_code1 = simulator1.generate_systemverilog_timing_code(
            register_name="config_reg",
            base_delay_cycles=5,
            variance_model=model1,
            offset=0x400,
        )

        sv_code2 = simulator2.generate_systemverilog_timing_code(
            register_name="config_reg",
            base_delay_cycles=5,
            variance_model=model2,
            offset=0x400,
        )

        # Verify the generated code is identical
        self.assertEqual(sv_code1, sv_code2)

        # Prune capabilities for both builds
        pruned_config1 = prune_capabilities_by_rules(self.config_space)
        pruned_config2 = prune_capabilities_by_rules(self.config_space)

        # Verify pruned configs are identical
        self.assertEqual(pruned_config1, pruned_config2)

        # Parse MSI-X capability for both builds
        msix_info1 = parse_msix_capability(pruned_config1)
        msix_info2 = parse_msix_capability(pruned_config2)

        # Verify MSI-X info is identical
        self.assertEqual(msix_info1["table_size"], msix_info2["table_size"])
        self.assertEqual(msix_info1["table_bir"], msix_info2["table_bir"])
        self.assertEqual(msix_info1["table_offset"], msix_info2["table_offset"])

        # Generate MSI-X SystemVerilog code for both builds
        msix_sv_code1 = generate_msix_table_sv(msix_info1)
        msix_sv_code2 = generate_msix_table_sv(msix_info2)

        # Verify MSI-X SystemVerilog code is identical
        self.assertEqual(msix_sv_code1, msix_sv_code2)


if __name__ == "__main__":
    unittest.main()
