#!/usr/bin/env python3
"""
Test suite for the configuration space shadow BRAM implementation.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.donor_dump_manager import DonorDumpManager


class TestConfigSpaceShadow(unittest.TestCase):
    """Test cases for the configuration space shadow BRAM implementation."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.donor_info_path = os.path.join(self.temp_dir.name, "donor_info.json")
        self.config_hex_path = os.path.join(self.temp_dir.name, "config_space_init.hex")

        # Sample configuration space data (simplified for testing)
        self.sample_config_space = "".join(["0123456789abcdef"] * 256)  # 4096 bytes

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
            "extended_config": self.sample_config_space,
        }

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_save_config_space_hex(self):
        """Test saving configuration space in hex format for $readmemh."""
        manager = DonorDumpManager()

        # Save the configuration space
        result = manager.save_config_space_hex(
            self.sample_config_space, self.config_hex_path
        )
        self.assertTrue(result)

        # Verify the file exists
        self.assertTrue(os.path.exists(self.config_hex_path))

        # Verify the file content
        with open(self.config_hex_path, "r") as f:
            lines = f.readlines()

        # Should have 1024 lines (4096 bytes / 4 bytes per line)
        self.assertEqual(len(lines), 1024)

        # Verify the format of the first line (little-endian conversion)
        # Original: "01234567" -> Little-endian: "67452301"
        self.assertEqual(lines[0].strip(), "67452301")

    def test_save_donor_info_with_config_space(self):
        """Test saving donor info with configuration space extraction."""
        manager = DonorDumpManager()

        # Save the donor info
        result = manager.save_donor_info(self.sample_device_info, self.donor_info_path)
        self.assertTrue(result)

        # Verify both files exist
        self.assertTrue(os.path.exists(self.donor_info_path))
        self.assertTrue(os.path.exists(self.config_hex_path))

        # Verify the donor info content
        with open(self.donor_info_path, "r") as f:
            donor_info = json.load(f)

        self.assertEqual(donor_info["vendor_id"], "0x8086")
        self.assertEqual(donor_info["device_id"], "0x1533")
        self.assertTrue("extended_config" in donor_info)

    @patch("src.donor_dump_manager.DonorDumpManager.read_device_info")
    @patch("src.donor_dump_manager.DonorDumpManager.load_module")
    @patch("src.donor_dump_manager.DonorDumpManager.build_module")
    @patch("src.donor_dump_manager.DonorDumpManager.check_kernel_headers")
    def test_setup_module_with_config_extraction(
        self, mock_headers, mock_build, mock_load, mock_read
    ):
        """Test setup_module with configuration space extraction."""
        # Mock the necessary methods
        mock_headers.return_value = (True, "5.10.0-generic")
        mock_build.return_value = True
        mock_load.return_value = True
        mock_read.return_value = self.sample_device_info

        manager = DonorDumpManager()

        # Call setup_module with config extraction
        device_info = manager.setup_module(
            "0000:03:00.0", save_to_file=self.donor_info_path, extract_full_config=True
        )

        # Verify the result
        self.assertEqual(device_info["vendor_id"], "0x8086")
        self.assertEqual(device_info["device_id"], "0x1533")
        self.assertTrue("extended_config" in device_info)

        # Verify the methods were called
        mock_headers.assert_called_once()
        mock_build.assert_called_once()
        mock_load.assert_called_once()
        mock_read.assert_called_once()

    @patch("src.donor_dump_manager.DonorDumpManager.generate_donor_info")
    def test_synthetic_config_space_generation(self, mock_generate):
        """Test synthetic configuration space generation when real data is unavailable."""
        # Create device info without extended_config
        device_info_no_config = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "subvendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "revision_id": "0x03",
            "class_code": "0x020000",
            "bar_size": "0x20000",
            "mpc": "0x2",
            "mpr": "0x2",
        }
        mock_generate.return_value = device_info_no_config

        # Create a manager with mocked methods
        manager = DonorDumpManager()

        # Simulate a failure that triggers synthetic generation
        with patch.object(manager, "build_module") as mock_build:
            mock_build.side_effect = Exception("Simulated failure")

            # Call setup_module with fallback generation
            device_info = manager.setup_module(
                "0000:03:00.0",
                save_to_file=self.donor_info_path,
                generate_if_unavailable=True,
                extract_full_config=True,
            )

        # Verify extended_config was added
        self.assertTrue("extended_config" in device_info)
        self.assertEqual(
            len(device_info["extended_config"]), 4096 * 2
        )  # 4096 bytes = 8192 hex chars


if __name__ == "__main__":
    unittest.main()
