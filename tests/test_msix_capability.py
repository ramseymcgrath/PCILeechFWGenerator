#!/usr/bin/env python3
"""
Test suite for MSI-X capability parsing and table generation.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.msix_capability import (
    find_cap,
    generate_msix_table_sv,
    msix_size,
    parse_msix_capability,
)


class TestMSIXCapability(unittest.TestCase):
    """Test cases for MSI-X capability parsing and table generation."""

    def setUp(self):
        """Set up test environment."""
        # Sample configuration space with MSI-X capability
        # This is a simplified version for testing

        # Create a 4KB configuration space filled with zeros
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

        # Add MSI-X capability at offset 0x40
        # Capability ID: 0x11 (MSI-X)
        # Next pointer: 0x00 (end of list)
        # Message Control: 0x0007 (8 table entries, function not masked, MSI-X disabled)
        # Note: In little-endian byte order, 0x0007 is represented as "0700" in the hex string
        # Table offset/BIR: 0x00002000 (offset 0x2000, BIR 0)
        # PBA offset/BIR: 0x00003000 (offset 0x3000, BIR 0)
        msix_cap = "11" + "00" + "0700" + "00002000" + "00003000"
        self.config_space = (
            self.config_space[: 0x40 * 2]
            + msix_cap
            + self.config_space[0x40 * 2 + len(msix_cap) :]
        )

    def test_find_cap(self):
        """Test finding a capability in the configuration space."""
        # Find MSI-X capability (ID 0x11)
        cap_offset = find_cap(self.config_space, 0x11)
        self.assertEqual(cap_offset, 0x40)

        # Try to find a non-existent capability
        cap_offset = find_cap(self.config_space, 0x12)
        self.assertIsNone(cap_offset)

        # Test with invalid configuration space
        cap_offset = find_cap("", 0x11)
        self.assertIsNone(cap_offset)

        # Test with configuration space that doesn't support capabilities
        config_space_no_caps = (
            self.config_space[: 0x06 * 2] + "0000" + self.config_space[0x06 * 2 + 4 :]
        )
        cap_offset = find_cap(config_space_no_caps, 0x11)
        self.assertIsNone(cap_offset)

    def test_msix_size(self):
        """Test determining the MSI-X table size."""
        # Get MSI-X table size
        size = msix_size(self.config_space)
        self.assertEqual(size, 8)  # 7 + 1 = 8 entries

        # Test with invalid configuration space
        size = msix_size("")
        self.assertEqual(size, 0)

        # Test with configuration space without MSI-X
        config_space_no_msix = (
            self.config_space[: 0x40 * 2] + "10" + self.config_space[0x40 * 2 + 2 :]
        )
        size = msix_size(config_space_no_msix)
        self.assertEqual(size, 0)

    def test_parse_msix_capability(self):
        """Test parsing the MSI-X capability structure."""
        # Parse MSI-X capability
        msix_info = parse_msix_capability(self.config_space)

        # Verify the parsed information
        self.assertEqual(msix_info["table_size"], 8)
        self.assertEqual(msix_info["table_bir"], 0)
        self.assertEqual(msix_info["table_offset"], 0x2000)
        self.assertEqual(msix_info["pba_bir"], 0)
        self.assertEqual(msix_info["pba_offset"], 0x3000)
        self.assertFalse(msix_info["enabled"])
        self.assertFalse(msix_info["function_mask"])

        # Test with invalid configuration space
        msix_info = parse_msix_capability("")
        self.assertEqual(msix_info["table_size"], 0)

        # Test with configuration space without MSI-X
        config_space_no_msix = (
            self.config_space[: 0x40 * 2] + "10" + self.config_space[0x40 * 2 + 2 :]
        )
        msix_info = parse_msix_capability(config_space_no_msix)
        self.assertEqual(msix_info["table_size"], 0)

    def test_generate_msix_table_sv(self):
        """Test generating SystemVerilog code for the MSI-X table."""
        # Parse MSI-X capability
        msix_info = parse_msix_capability(self.config_space)

        # Generate SystemVerilog code
        sv_code = generate_msix_table_sv(msix_info)

        # Verify the generated code
        self.assertIn("localparam NUM_MSIX = 8;", sv_code)
        self.assertIn("localparam MSIX_TABLE_BIR = 0;", sv_code)
        self.assertIn("localparam MSIX_TABLE_OFFSET = 32'h2000;", sv_code)
        self.assertIn("localparam MSIX_PBA_BIR = 0;", sv_code)
        self.assertIn("localparam MSIX_PBA_OFFSET = 32'h3000;", sv_code)

        # Test with MSI-X not supported
        msix_info["table_size"] = 0
        sv_code = generate_msix_table_sv(msix_info)
        self.assertIn("// MSI-X not supported or no entries", sv_code)


if __name__ == "__main__":
    unittest.main()
