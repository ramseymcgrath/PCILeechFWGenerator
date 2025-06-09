#!/usr/bin/env python3
"""
Enhanced test suite for the configuration space shadow BRAM implementation.
This test suite focuses on edge cases, extended configuration space access,
and overlay RAM functionality.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.donor_dump_manager import DonorDumpManager


class TestConfigSpaceShadowEnhanced(unittest.TestCase):
    """Enhanced test cases for the configuration space shadow BRAM implementation."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.donor_info_path = os.path.join(self.temp_dir.name, "donor_info.json")
        self.config_hex_path = os.path.join(self.temp_dir.name, "config_space_init.hex")

        # Create a more complex configuration space with specific patterns
        # for testing edge cases
        self.config_space = bytearray(4096)

        # Fill with pattern that makes it easy to identify each DWORD
        for i in range(1024):  # 1024 DWORDs in 4KB
            # Each DWORD contains its index as a pattern
            self.config_space[i * 4] = i & 0xFF
            self.config_space[i * 4 + 1] = (i >> 8) & 0xFF
            self.config_space[i * 4 + 2] = 0xAA
            self.config_space[i * 4 + 3] = 0xBB

        # Convert to hex string
        self.sample_config_space = "".join(f"{b:02x}" for b in self.config_space)

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

    def test_extended_config_space_access(self):
        """Test accessing the extended configuration space (beyond 256 bytes)."""
        manager = DonorDumpManager()

        # Save the configuration space
        result = manager.save_config_space_hex(
            self.sample_config_space, self.config_hex_path
        )
        self.assertTrue(result)

        # Verify the file exists
        self.assertTrue(os.path.exists(self.config_hex_path))

        # Verify extended configuration space is properly saved
        with open(self.config_hex_path, "r") as f:
            lines = f.readlines()

        # Check a few specific offsets in the extended configuration space
        # Offset 0x100 (256 bytes, start of extended config space)
        # In our pattern, this would be DWORD 64 (0x40)
        # Expected little-endian value: 0xBBAA4000
        self.assertEqual(lines[64].strip(), "bbaa4000")

        # Offset 0x400 (1024 bytes)
        # In our pattern, this would be DWORD 256 (0x100)
        # Expected little-endian value: 0xBBAA0001
        self.assertEqual(lines[256].strip(), "bbaa0001")

        # Offset 0xFFC (4092 bytes, last DWORD)
        # In our pattern, this would be DWORD 1023 (0x3FF)
        # Expected little-endian value: 0xBBAA3F03
        self.assertEqual(lines[1023].strip(), "bbaa3f03")

    def test_config_space_boundary_conditions(self):
        """Test boundary conditions for configuration space access."""
        manager = DonorDumpManager()

        # Test with configuration space smaller than 4KB
        small_config = self.sample_config_space[:2048]  # 1KB

        # Save the small configuration space
        result = manager.save_config_space_hex(small_config, self.config_hex_path)
        self.assertTrue(result)

        # Verify the file exists
        self.assertTrue(os.path.exists(self.config_hex_path))

        # Verify file size (should be padded to 4KB)
        with open(self.config_hex_path, "r") as f:
            lines = f.readlines()

        # Should still have 1024 lines (4KB / 4 bytes per line)
        self.assertEqual(len(lines), 1024)

        # Test with configuration space larger than 4KB
        large_config = self.sample_config_space + "0123456789abcdef" * 256  # 4KB + 4KB

        # Save the large configuration space
        result = manager.save_config_space_hex(large_config, self.config_hex_path)
        self.assertTrue(result)

        # Verify the file exists
        self.assertTrue(os.path.exists(self.config_hex_path))

        # Verify file size (should be truncated to 4KB)
        with open(self.config_hex_path, "r") as f:
            lines = f.readlines()

        # Should have 1024 lines (4KB / 4 bytes per line)
        self.assertEqual(len(lines), 1024)

    def test_overlay_ram_fields(self):
        """Test that writable fields are correctly identified for overlay RAM."""
        # This test verifies that the correct fields are identified as writable
        # and mapped to overlay RAM in the configuration space

        # Create a configuration space with specific values in writable fields
        config_space = bytearray(4096)

        # Set Command register (offset 0x04) to 0x0147
        config_space[0x04] = 0x47
        config_space[0x05] = 0x01

        # Set Status register (offset 0x06) to 0x0290
        config_space[0x06] = 0x90
        config_space[0x07] = 0x02

        # Set Cache Line Size register (offset 0x0C) to 0x40
        config_space[0x0C] = 0x40

        # Set Latency Timer register (offset 0x0D) to 0x20
        config_space[0x0D] = 0x20

        # Convert to hex string
        config_space_hex = "".join(f"{b:02x}" for b in config_space)

        # Create device info with this configuration space
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "extended_config": config_space_hex,
        }

        # Save the configuration space
        manager = DonorDumpManager()
        result = manager.save_donor_info(device_info, self.donor_info_path)
        self.assertTrue(result)

        # Verify the config hex file exists
        self.assertTrue(os.path.exists(self.config_hex_path))

        # Verify the writable fields are correctly saved
        with open(self.config_hex_path, "r") as f:
            lines = f.readlines()

        # Command register (offset 0x04, DWORD 1)
        # Expected little-endian value: 0x02900147
        self.assertEqual(lines[1].strip(), "02900147")

        # Cache Line Size and Latency Timer (offset 0x0C, DWORD 3)
        # Expected little-endian value: 0x00002040
        self.assertEqual(lines[3].strip(), "00002040")

    @patch("src.donor_dump_manager.DonorDumpManager.read_device_info")
    def test_synthetic_config_space_with_specific_fields(self, mock_read):
        """Test synthetic configuration space generation with specific fields."""
        # Create device info without extended_config but with specific fields
        device_info_no_config = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "subvendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "revision_id": "0x03",
            "class_code": "0x020000",
            "command": "0x0147",  # Specific command register value
            "status": "0x0290",  # Specific status register value
            "cache_line_size": "0x40",  # Specific cache line size
            "latency_timer": "0x20",  # Specific latency timer
            "bar_size": "0x20000",
            "mpc": "0x2",
            "mpr": "0x2",
        }
        mock_read.return_value = device_info_no_config

        # Create a manager with mocked methods
        manager = DonorDumpManager()

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

        # Save the configuration space
        result = manager.save_config_space_hex(
            device_info["extended_config"], self.config_hex_path
        )
        self.assertTrue(result)

        # Verify the file exists
        self.assertTrue(os.path.exists(self.config_hex_path))

        # Verify the specific fields are correctly set in the configuration space
        with open(self.config_hex_path, "r") as f:
            lines = f.readlines()

        # Extract the command and status registers (DWORD 1)
        dword1 = int(lines[1].strip(), 16)
        command = dword1 & 0xFFFF
        status = (dword1 >> 16) & 0xFFFF

        # Extract the cache line size and latency timer (DWORD 3)
        dword3 = int(lines[3].strip(), 16)
        cache_line_size = dword3 & 0xFF
        latency_timer = (dword3 >> 8) & 0xFF

        # Verify the values match what we specified
        self.assertEqual(command, 0x0147)
        self.assertEqual(status, 0x0290)
        self.assertEqual(cache_line_size, 0x40)
        self.assertEqual(latency_timer, 0x20)


if __name__ == "__main__":
    unittest.main()
