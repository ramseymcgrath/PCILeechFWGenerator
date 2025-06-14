#!/usr/bin/env python3
"""
Test suite for MSI-X capability parsing and table generation.
"""

import unittest

from src.msix_capability import (
    find_cap,
    generate_msix_table_sv,
    hex_to_bytes,
    is_valid_offset,
    msix_size,
    parse_msix_capability,
    read_u16_le,
    read_u32_le,
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
        # Status register is little-endian, so 0x0010 becomes "1000"
        self.config_space = (
            self.config_space[: 0x06 * 2] + "1000" + self.config_space[0x06 * 2 + 4 :]
        )

        # Add MSI-X capability at offset 0x40
        # Capability ID: 0x11 (MSI-X)
        # Next pointer: 0x00 (end of list)
        # Message Control: 0x0007 (8 table entries, function not masked, MSI-X disabled)
        # Note: In little-endian byte order, 0x0007 is represented as "0700" in the hex string
        # Table offset/BIR: 0x00002000 (offset 0x2000, BIR 0) - little-endian: "00200000"
        # PBA offset/BIR: 0x00003000 (offset 0x3000, BIR 0) - little-endian: "00300000"
        msix_cap = "11" + "00" + "0700" + "00200000" + "00300000"
        self.config_space = (
            self.config_space[: 0x40 * 2]
            + msix_cap
            + self.config_space[0x40 * 2 + len(msix_cap) :]
        )

    def test_helper_functions(self):
        """Test the new helper functions."""
        # Test hex_to_bytes
        hex_string = "1100070000200000"
        byte_data = hex_to_bytes(hex_string)
        self.assertEqual(len(byte_data), 8)
        self.assertEqual(byte_data[0], 0x11)
        self.assertEqual(byte_data[1], 0x00)

        # Test invalid hex string
        with self.assertRaises(ValueError):
            hex_to_bytes("123")  # Odd length

        # Test read_u16_le
        test_data = bytearray([0x07, 0x00, 0x11, 0x22])
        value = read_u16_le(test_data, 0)
        self.assertEqual(value, 0x0007)  # Little-endian

        value = read_u16_le(test_data, 2)
        self.assertEqual(value, 0x2211)  # Little-endian

        # Test read_u32_le
        test_data = bytearray([0x00, 0x20, 0x00, 0x00, 0x11, 0x22, 0x33, 0x44])
        value = read_u32_le(test_data, 0)
        self.assertEqual(value, 0x00002000)  # Little-endian

        value = read_u32_le(test_data, 4)
        self.assertEqual(value, 0x44332211)  # Little-endian

        # Test is_valid_offset
        test_data = bytearray(10)
        self.assertTrue(is_valid_offset(test_data, 0, 5))
        self.assertTrue(is_valid_offset(test_data, 5, 5))
        self.assertFalse(is_valid_offset(test_data, 6, 5))
        self.assertFalse(is_valid_offset(test_data, 0, 11))

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

        # Test with invalid hex string
        cap_offset = find_cap("invalid_hex", 0x11)
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
        self.assertIn("localparam MSIX_ENABLED = 0;", sv_code)
        self.assertIn("localparam MSIX_FUNCTION_MASK = 0;", sv_code)
        self.assertIn("localparam PBA_SIZE = 1;", sv_code)  # (8 + 31) // 32 = 1

        # Test with MSI-X not supported
        msix_info_empty = {"table_size": 0}
        sv_code = generate_msix_table_sv(msix_info_empty)
        self.assertIn("// MSI-X not supported or no entries", sv_code)

        # Test alignment warning
        msix_info_unaligned = msix_info.copy()
        msix_info_unaligned["table_offset"] = 0x2004  # Not 8-byte aligned
        sv_code = generate_msix_table_sv(msix_info_unaligned)
        self.assertIn(
            "// Warning: MSI-X table offset 0x2004 is not 8-byte aligned", sv_code
        )

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test with very short config space
        short_config = "1234"
        self.assertEqual(msix_size(short_config), 0)
        self.assertEqual(parse_msix_capability(short_config)["table_size"], 0)

        # Test with config space that has capabilities but no MSI-X
        config_no_msix = (
            self.config_space[: 0x40 * 2] + "1000" + self.config_space[0x40 * 2 + 4 :]
        )
        self.assertEqual(msix_size(config_no_msix), 0)
        self.assertEqual(parse_msix_capability(config_no_msix)["table_size"], 0)

        # Test with truncated MSI-X capability
        config_truncated = self.config_space[
            : 0x44 * 2
        ]  # Cut off after message control
        self.assertEqual(msix_size(config_truncated), 0)
        self.assertEqual(parse_msix_capability(config_truncated)["table_size"], 0)

    def test_different_table_sizes(self):
        """Test with different MSI-X table sizes."""
        # Test with 1 entry (table size field = 0)
        config_1_entry = (
            self.config_space[: 0x42 * 2] + "0000" + self.config_space[0x42 * 2 + 4 :]
        )
        self.assertEqual(msix_size(config_1_entry), 1)
        msix_info = parse_msix_capability(config_1_entry)
        self.assertEqual(msix_info["table_size"], 1)

        # Test with maximum entries (table size field = 0x7FF)
        config_max_entries = (
            self.config_space[: 0x42 * 2] + "FF07" + self.config_space[0x42 * 2 + 4 :]
        )
        self.assertEqual(msix_size(config_max_entries), 2048)  # 0x7FF + 1
        msix_info = parse_msix_capability(config_max_entries)
        self.assertEqual(msix_info["table_size"], 2048)


if __name__ == "__main__":
    unittest.main()
