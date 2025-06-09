#!/usr/bin/env python3
"""
Enhanced test suite for MSI-X capability parsing and table generation.

This test suite focuses on:
1. Testing MSI-X table parsing with various table sizes
2. Testing interrupt delivery with different masking scenarios
3. Verifying PBA functionality
4. Testing edge cases and boundary conditions
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


class TestMSIXCapabilityEnhanced(unittest.TestCase):
    """Enhanced test cases for MSI-X capability parsing and table generation."""

    def setUp(self):
        """Set up test environment."""
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

    def create_msix_capability(
        self, offset, table_size, function_mask=False, msix_enable=False, next_ptr="00"
    ):
        """
        Create an MSI-X capability at the specified offset.

        Args:
            offset: Offset in the configuration space
            table_size: Number of table entries (0-2047)
            function_mask: Whether the function mask bit is set
            msix_enable: Whether the MSI-X enable bit is set
            next_ptr: Next capability pointer

        Returns:
            Updated configuration space
        """
        # Capability ID: 0x11 (MSI-X)
        # Next pointer: next_ptr
        # Message Control: table_size (bits 0-10), function_mask (bit 14), msix_enable (bit 15)
        message_control = table_size & 0x7FF  # 11 bits for table size
        if function_mask:
            message_control |= 0x4000  # Bit 14
        if msix_enable:
            message_control |= 0x8000  # Bit 15

        # Convert to little-endian byte order for the hex string
        # For example, 0x0007 becomes "0700"
        message_control_hex = (
            f"{((message_control & 0xFF) << 8) | ((message_control & 0xFF00) >> 8):04x}"
        )

        # Table offset/BIR: 0x00002000 (offset 0x2000, BIR 0)
        # PBA offset/BIR: 0x00003000 (offset 0x3000, BIR 0)
        msix_cap = "11" + next_ptr + message_control_hex + "00002000" + "00003000"

        # Insert the capability at the specified offset
        config_space = (
            self.config_space[: offset * 2]
            + msix_cap
            + self.config_space[offset * 2 + len(msix_cap) :]
        )

        return config_space

    def test_msix_table_size_variations(self):
        """Test parsing MSI-X capability with various table sizes."""
        # Test with minimum table size (1 entry)
        config_space = self.create_msix_capability(0x40, 0)  # 0 means 1 entry
        msix_info = parse_msix_capability(config_space)
        self.assertEqual(msix_info["table_size"], 1)

        # Test with medium table size (64 entries)
        config_space = self.create_msix_capability(0x40, 63)  # 63 means 64 entries
        msix_info = parse_msix_capability(config_space)
        self.assertEqual(msix_info["table_size"], 64)

        # Test with maximum table size (2048 entries)
        config_space = self.create_msix_capability(
            0x40, 2047
        )  # 2047 means 2048 entries
        msix_info = parse_msix_capability(config_space)
        self.assertEqual(msix_info["table_size"], 2048)

        # Test with invalid table size (should be capped at 2048)
        config_space = self.create_msix_capability(0x40, 4095)  # Beyond max
        msix_info = parse_msix_capability(config_space)
        self.assertEqual(msix_info["table_size"], 2048)  # Should be capped

    def test_msix_function_masking(self):
        """Test MSI-X function masking."""
        # Test with function mask bit set
        config_space = self.create_msix_capability(0x40, 7, function_mask=True)
        msix_info = parse_msix_capability(config_space)
        self.assertEqual(msix_info["table_size"], 8)
        self.assertTrue(msix_info["function_mask"])
        self.assertFalse(msix_info["enabled"])

        # Test with function mask and enable bits set
        config_space = self.create_msix_capability(
            0x40, 7, function_mask=True, msix_enable=True
        )
        msix_info = parse_msix_capability(config_space)
        self.assertEqual(msix_info["table_size"], 8)
        self.assertTrue(msix_info["function_mask"])
        self.assertTrue(msix_info["enabled"])

        # Generate SystemVerilog code for masked function
        sv_code = generate_msix_table_sv(msix_info)
        self.assertIn("localparam NUM_MSIX = 8;", sv_code)
        self.assertIn("localparam MSIX_FUNCTION_MASK = 1;", sv_code)
        self.assertIn("localparam MSIX_ENABLED = 1;", sv_code)

    def test_msix_bir_variations(self):
        """Test MSI-X with different BIR values."""
        # Create a custom MSI-X capability with different BIR values
        offset = 0x40
        table_size = 7  # 8 entries

        # Capability ID: 0x11 (MSI-X)
        # Next pointer: 0x00 (end of list)
        # Message Control: 0x0007 (8 table entries, function not masked, MSI-X disabled)
        # Table offset/BIR: 0x00002001 (offset 0x2000, BIR 1)
        # PBA offset/BIR: 0x00003002 (offset 0x3000, BIR 2)
        msix_cap = "11" + "00" + "0700" + "00002001" + "00003002"

        config_space = (
            self.config_space[: offset * 2]
            + msix_cap
            + self.config_space[offset * 2 + len(msix_cap) :]
        )

        # Parse the capability
        msix_info = parse_msix_capability(config_space)

        # Verify the BIR values
        self.assertEqual(msix_info["table_bir"], 1)
        self.assertEqual(msix_info["pba_bir"], 2)

        # Generate SystemVerilog code
        sv_code = generate_msix_table_sv(msix_info)
        self.assertIn("localparam MSIX_TABLE_BIR = 1;", sv_code)
        self.assertIn("localparam MSIX_PBA_BIR = 2;", sv_code)

    def test_msix_offset_variations(self):
        """Test MSI-X with different offset values."""
        # Create a custom MSI-X capability with different offset values
        offset = 0x40
        table_size = 7  # 8 entries

        # Capability ID: 0x11 (MSI-X)
        # Next pointer: 0x00 (end of list)
        # Message Control: 0x0007 (8 table entries, function not masked, MSI-X disabled)
        # Table offset/BIR: 0x00004000 (offset 0x4000, BIR 0)
        # PBA offset/BIR: 0x00005000 (offset 0x5000, BIR 0)
        msix_cap = "11" + "00" + "0700" + "00004000" + "00005000"

        config_space = (
            self.config_space[: offset * 2]
            + msix_cap
            + self.config_space[offset * 2 + len(msix_cap) :]
        )

        # Parse the capability
        msix_info = parse_msix_capability(config_space)

        # Verify the offset values
        self.assertEqual(msix_info["table_offset"], 0x4000)
        self.assertEqual(msix_info["pba_offset"], 0x5000)

        # Generate SystemVerilog code
        sv_code = generate_msix_table_sv(msix_info)
        self.assertIn("localparam MSIX_TABLE_OFFSET = 32'h4000;", sv_code)
        self.assertIn("localparam MSIX_PBA_OFFSET = 32'h5000;", sv_code)

    def test_msix_capability_chain(self):
        """Test MSI-X capability in a capability chain."""
        # Create a chain of capabilities
        # First capability at 0x40 (PCIe)
        pcie_cap = "10" + "50" + "0000" + "00000000"
        config_space = (
            self.config_space[: 0x40 * 2]
            + pcie_cap
            + self.config_space[0x40 * 2 + len(pcie_cap) :]
        )

        # Second capability at 0x50 (MSI-X)
        msix_cap = "11" + "60" + "0700" + "00002000" + "00003000"
        config_space = (
            config_space[: 0x50 * 2]
            + msix_cap
            + config_space[0x50 * 2 + len(msix_cap) :]
        )

        # Third capability at 0x60 (Vendor-specific)
        vendor_cap = "09" + "00" + "0000" + "00000000"
        config_space = (
            config_space[: 0x60 * 2]
            + vendor_cap
            + config_space[0x60 * 2 + len(vendor_cap) :]
        )

        # Find MSI-X capability
        msix_offset = find_cap(config_space, 0x11)
        self.assertEqual(msix_offset, 0x50)

        # Parse MSI-X capability
        msix_info = parse_msix_capability(config_space)
        self.assertEqual(msix_info["table_size"], 8)
        self.assertEqual(msix_info["table_bir"], 0)
        self.assertEqual(msix_info["table_offset"], 0x2000)

    def test_msix_table_generation_edge_cases(self):
        """Test MSI-X table generation with edge cases."""
        # Test with no MSI-X capability
        msix_info = {
            "table_size": 0,
            "table_bir": 0,
            "table_offset": 0,
            "pba_bir": 0,
            "pba_offset": 0,
            "enabled": False,
            "function_mask": False,
        }
        sv_code = generate_msix_table_sv(msix_info)
        self.assertIn("// MSI-X not supported or no entries", sv_code)

        # Test with very large table size
        msix_info = {
            "table_size": 2048,  # Maximum size
            "table_bir": 0,
            "table_offset": 0x2000,
            "pba_bir": 0,
            "pba_offset": 0x3000,
            "enabled": True,
            "function_mask": False,
        }
        sv_code = generate_msix_table_sv(msix_info)
        self.assertIn("localparam NUM_MSIX = 2048;", sv_code)

        # Test with unusual BIR and offset combinations
        msix_info = {
            "table_size": 16,
            "table_bir": 5,  # Maximum BIR value
            "table_offset": 0xFFFF0000,  # Very large offset
            "pba_bir": 5,
            "pba_offset": 0xFFFF4000,
            "enabled": True,
            "function_mask": False,
        }
        sv_code = generate_msix_table_sv(msix_info)
        self.assertIn("localparam MSIX_TABLE_BIR = 5;", sv_code)
        self.assertIn("localparam MSIX_TABLE_OFFSET = 32'hFFFF0000;", sv_code)

    def test_msix_pba_size_calculation(self):
        """Test MSI-X PBA size calculation for different table sizes."""
        # For 8 entries, PBA size should be 1 DWORD (32 bits)
        msix_info = {
            "table_size": 8,
            "table_bir": 0,
            "table_offset": 0x2000,
            "pba_bir": 0,
            "pba_offset": 0x3000,
            "enabled": True,
            "function_mask": False,
        }
        sv_code = generate_msix_table_sv(msix_info)
        self.assertIn("localparam PBA_SIZE = 1;", sv_code)

        # For 33 entries, PBA size should be 2 DWORDs (64 bits)
        msix_info["table_size"] = 33
        sv_code = generate_msix_table_sv(msix_info)
        self.assertIn("localparam PBA_SIZE = 2;", sv_code)

        # For 2048 entries, PBA size should be 64 DWORDs (2048 bits)
        msix_info["table_size"] = 2048
        sv_code = generate_msix_table_sv(msix_info)
        self.assertIn("localparam PBA_SIZE = 64;", sv_code)

    def test_msix_table_alignment(self):
        """Test MSI-X table alignment requirements."""
        # MSI-X table must be QWORD (8-byte) aligned
        # Create a capability with misaligned table offset
        offset = 0x40

        # Table offset 0x2004 is not 8-byte aligned
        msix_cap = "11" + "00" + "0700" + "00002004" + "00003000"
        config_space = (
            self.config_space[: offset * 2]
            + msix_cap
            + self.config_space[offset * 2 + len(msix_cap) :]
        )

        # Parse the capability
        msix_info = parse_msix_capability(config_space)

        # Verify the offset value (should be as specified, alignment is enforced in hardware)
        self.assertEqual(msix_info["table_offset"], 0x2004)

        # Generate SystemVerilog code
        sv_code = generate_msix_table_sv(msix_info)

        # Code should include a warning about alignment
        self.assertIn(
            "// Warning: MSI-X table offset 0x2004 is not 8-byte aligned", sv_code
        )


if __name__ == "__main__":
    unittest.main()
