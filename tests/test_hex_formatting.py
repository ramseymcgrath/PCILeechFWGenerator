#!/usr/bin/env python3
"""
Unit tests for hex value formatting functionality.

This module tests the hex value sanitization function that prevents
double "0x" prefix issues in TCL generation for Vivado builds.
"""

import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from build import sanitize_hex_value


class TestHexValueSanitization:
    """Test cases for hex value sanitization function."""

    def test_normal_hex_with_prefix(self):
        """Test normal hex values that already have 0x prefix."""
        assert sanitize_hex_value("0x8086") == "0x8086"
        assert sanitize_hex_value("0x1234") == "0x1234"
        assert sanitize_hex_value("0xABCD") == "0xABCD"
        assert sanitize_hex_value("0xabcd") == "0xabcd"
        assert sanitize_hex_value("0x0") == "0x0"
        assert sanitize_hex_value("0x00") == "0x00"

    def test_hex_without_prefix(self):
        """Test hex values without 0x prefix."""
        assert sanitize_hex_value("8086") == "0x8086"
        assert sanitize_hex_value("1234") == "0x1234"
        assert sanitize_hex_value("ABCD") == "0xABCD"
        assert sanitize_hex_value("abcd") == "0xabcd"
        assert sanitize_hex_value("0") == "0x0"
        assert sanitize_hex_value("00") == "0x00"

    def test_uppercase_prefix_handling(self):
        """Test handling of uppercase 0X prefix."""
        assert sanitize_hex_value("0X8086") == "0x8086"
        assert sanitize_hex_value("0X1234") == "0x1234"
        assert sanitize_hex_value("0XABCD") == "0xABCD"
        assert sanitize_hex_value("0Xabcd") == "0xabcd"

    def test_double_prefix_handling(self):
        """Test handling of double 0x prefixes (the main bug fix)."""
        assert sanitize_hex_value("0x0x8086") == "0x8086"
        assert sanitize_hex_value("0X0x1234") == "0x1234"
        assert sanitize_hex_value("0x0X5678") == "0x5678"
        assert sanitize_hex_value("0X0X9ABC") == "0x9ABC"

    def test_multiple_prefix_handling(self):
        """Test handling of multiple 0x prefixes."""
        assert sanitize_hex_value("0x0x0x8086") == "0x8086"
        assert sanitize_hex_value("0X0x0X1234") == "0x1234"

    def test_numeric_inputs(self):
        """Test numeric inputs."""
        assert sanitize_hex_value(32902) == "0x8086"  # 0x8086 in decimal
        assert sanitize_hex_value(4660) == "0x1234"  # 0x1234 in decimal
        assert sanitize_hex_value(0) == "0x0"
        assert sanitize_hex_value(255) == "0xff"
        assert sanitize_hex_value(65535) == "0xffff"

    def test_edge_cases(self):
        """Test edge cases like None, empty strings, invalid formats."""
        assert sanitize_hex_value(None) == "0x0"
        assert sanitize_hex_value("") == "0x0"
        assert sanitize_hex_value("   ") == "0x0"  # whitespace only
        assert sanitize_hex_value("0x") == "0x0"  # prefix only
        assert sanitize_hex_value("0X") == "0x0"  # uppercase prefix only

    def test_invalid_hex_characters(self):
        """Test handling of invalid hex characters."""
        assert sanitize_hex_value("0xGHIJ") == "0x0"  # completely invalid
        assert sanitize_hex_value("0x123G") == "0x123"  # partial valid
        assert sanitize_hex_value("G123") == "0x123"  # extract valid portion
        assert sanitize_hex_value("12G34") == "0x12"  # extract first valid portion
        assert sanitize_hex_value("GHIJ") == "0x0"  # no valid hex chars

    def test_whitespace_handling(self):
        """Test handling of whitespace in input."""
        assert sanitize_hex_value("  0x8086  ") == "0x8086"
        assert sanitize_hex_value("  8086  ") == "0x8086"
        assert sanitize_hex_value("\t0x1234\n") == "0x1234"

    def test_non_string_non_int_inputs(self):
        """Test handling of non-string, non-integer inputs."""
        assert sanitize_hex_value([]) == "0x0"
        assert sanitize_hex_value({}) == "0x0"
        assert sanitize_hex_value(3.14) == "0x0"

    def test_case_preservation(self):
        """Test that hex case is preserved in the output."""
        assert sanitize_hex_value("0xABCD") == "0xABCD"
        assert sanitize_hex_value("0xabcd") == "0xabcd"
        assert sanitize_hex_value("0xAbCd") == "0xAbCd"
        assert sanitize_hex_value("ABCD") == "0xABCD"
        assert sanitize_hex_value("abcd") == "0xabcd"


class TestTCLIntegration:
    """Test integration with TCL generation."""

    def test_tcl_generation_with_sanitized_values(self):
        """Test that TCL generation uses sanitized hex values."""
        # Import the build_tcl function
        from build import build_tcl

        # Create test donor info with various hex formats
        test_info = {
            "vendor_id": "0x0x8086",  # Double prefix (main bug)
            "device_id": "1234",  # No prefix
            "subvendor_id": "0X5678",  # Uppercase prefix
            "subsystem_id": "0x9ABC",  # Normal prefix
            "revision_id": "0x0xDEF0",  # Double prefix
            "bar_size": "0x1000",  # 4KB
            "mpc": "0x2",  # Max payload size code
            "mpr": "0x2",  # Max read request size code
        }

        # Generate TCL content
        tcl_content, _ = build_tcl(test_info, "dummy_path")

        # Verify that the generated TCL has properly formatted hex values
        assert 'set_property -name "VENDOR_ID" -value "0x8086"' in tcl_content
        assert 'set_property -name "DEVICE_ID" -value "0x1234"' in tcl_content
        assert 'set_property -name "SUBSYSTEM_VENDOR_ID" -value "0x5678"' in tcl_content
        assert 'set_property -name "SUBSYSTEM_ID" -value "0x9ABC"' in tcl_content
        assert 'set_property -name "REVISION_ID" -value "0xDEF0"' in tcl_content

        # Verify no double prefixes exist
        assert "0x0x" not in tcl_content
        assert "0X0x" not in tcl_content
        assert "0x0X" not in tcl_content

    def test_tcl_generation_with_edge_cases(self):
        """Test TCL generation with edge case hex values."""
        from build import build_tcl

        # Test with edge case values
        test_info = {
            "vendor_id": "",  # Empty string
            "device_id": None,  # None value (shouldn't happen but test anyway)
            "subvendor_id": "0x",  # Prefix only
            "subsystem_id": "GHIJ",  # Invalid hex
            "revision_id": "0x0x0x1234",  # Multiple prefixes
            "bar_size": "0x1000",
            "mpc": "0x2",
            "mpr": "0x2",
        }

        # This should not raise an exception and should generate valid TCL
        try:
            tcl_content, _ = build_tcl(test_info, "dummy_path")

            # All values should be sanitized to valid hex
            assert 'set_property -name "VENDOR_ID" -value "0x0"' in tcl_content
            assert (
                'set_property -name "SUBSYSTEM_VENDOR_ID" -value "0x0"' in tcl_content
            )
            assert 'set_property -name "SUBSYSTEM_ID" -value "0x0"' in tcl_content
            assert 'set_property -name "REVISION_ID" -value "0x1234"' in tcl_content

            # No double prefixes should exist
            assert "0x0x" not in tcl_content

        except Exception as e:
            pytest.fail(f"TCL generation failed with edge case values: {e}")


class TestRealWorldScenarios:
    """Test real-world scenarios that could cause the double prefix bug."""

    def test_donor_info_with_mixed_formats(self):
        """Test with donor info that has mixed hex formats (realistic scenario)."""
        # This simulates what might come from different sources:
        # - Some values from lspci (with 0x prefix)
        # - Some values from config space dumps (without prefix)
        # - Some values from user input (various formats)

        mixed_format_values = [
            ("0x8086", "0x8086"),  # Intel vendor ID (normal)
            ("10de", "0x10de"),  # NVIDIA vendor ID (no prefix)
            ("0X1234", "0x1234"),  # Uppercase prefix
            ("0x0x5678", "0x5678"),  # Double prefix (the bug)
            ("0x0X9ABC", "0x9ABC"),  # Mixed case double prefix
            ("DEF0", "0xDEF0"),  # No prefix, uppercase
            ("0x0", "0x0"),  # Zero value
            ("FF", "0xFF"),  # Max byte value
        ]

        for input_val, expected in mixed_format_values:
            result = sanitize_hex_value(input_val)
            assert (
                result == expected
            ), f"Input '{input_val}' should produce '{expected}', got '{result}'"

    def test_common_pci_vendor_device_ids(self):
        """Test with common PCI vendor/device IDs that might cause issues."""
        common_ids = {
            # Intel
            "8086": "0x8086",
            "0x8086": "0x8086",
            "0x0x8086": "0x8086",
            # NVIDIA
            "10de": "0x10de",
            "0x10de": "0x10de",
            "0X10DE": "0x10DE",
            # AMD
            "1002": "0x1002",
            "0x1002": "0x1002",
            # Broadcom
            "14e4": "0x14e4",
            "0x14e4": "0x14e4",
        }

        for input_val, expected in common_ids.items():
            result = sanitize_hex_value(input_val)
            assert (
                result == expected
            ), f"Common ID '{input_val}' should produce '{expected}', got '{result}'"

    def test_subsystem_ids_edge_cases(self):
        """Test subsystem IDs which often have different formats."""
        subsystem_cases = [
            ("0000", "0x0000"),  # Common subsystem ID
            ("0x0000", "0x0000"),  # With prefix
            ("FFFF", "0xFFFF"),  # Max value
            ("0xFFFF", "0xFFFF"),  # Max with prefix
            ("0x0xFFFF", "0xFFFF"),  # Double prefix bug
        ]

        for input_val, expected in subsystem_cases:
            result = sanitize_hex_value(input_val)
            assert (
                result == expected
            ), f"Subsystem ID '{input_val}' should produce '{expected}', got '{result}'"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
