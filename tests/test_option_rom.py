#!/usr/bin/env python3
"""
Unit tests for Option-ROM functionality
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Optional pytest import for parametrized tests
try:
    import pytest

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

# Import the modules to test
try:
    from src.option_rom_manager import OptionROMError, OptionROMManager
except ImportError:
    # Handle import from different directory
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.option_rom_manager import OptionROMError, OptionROMManager


class TestOptionROMManager(unittest.TestCase):
    """Test the Option-ROM Manager functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
        self.manager = OptionROMManager(output_dir=self.output_dir)

        # Create a sample ROM file for testing
        self.sample_rom_path = self.output_dir / "sample.rom"
        with open(self.sample_rom_path, "wb") as f:
            # Create a minimal valid ROM with signature 0x55AA
            f.write(bytes([0x55, 0xAA]))  # ROM signature
            f.write(bytes([0x02]))  # Size in 512-byte blocks (1KB)
            f.write(bytes([0x00] * 1021))  # Padding to make it 1KB

    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()

    @patch("subprocess.run")
    def test_extract_rom_linux_success(self, mock_run):
        """Test successful ROM extraction on Linux"""
        # Mock subprocess calls
        mock_run.return_value = MagicMock(returncode=0)

        # Create a mock ROM file that the extraction would create
        rom_path = self.output_dir / "donor.rom"
        with open(rom_path, "wb") as f:
            f.write(bytes([0x55, 0xAA, 0x04, 0x00] + [0x00] * 2044))  # 2KB ROM

        # Test extraction
        success, path = self.manager.extract_rom_linux("0000:01:00.0")

        # Verify results
        self.assertTrue(success)
        self.assertEqual(path, str(rom_path))
        self.assertEqual(self.manager.rom_size, 2048)  # 2KB

    @patch("subprocess.run")
    def test_extract_rom_linux_failure(self, mock_run):
        """Test failed ROM extraction on Linux"""
        # Mock subprocess call to fail
        mock_run.side_effect = Exception("Command failed")

        # Test extraction
        success, path = self.manager.extract_rom_linux("0000:01:00.0")

        # Verify results
        self.assertFalse(success)
        self.assertEqual(path, "")

    def test_load_rom_file_success(self):
        """Test loading ROM from file"""
        # Test loading
        result = self.manager.load_rom_file(str(self.sample_rom_path))

        # Verify results
        self.assertTrue(result)
        self.assertEqual(self.manager.rom_size, 1024)  # 1KB
        self.assertIsNotNone(self.manager.rom_data)
        if self.manager.rom_data is not None:  # Add null check to satisfy type checker
            self.assertEqual(self.manager.rom_data[0], 0x55)  # Check signature
            self.assertEqual(self.manager.rom_data[1], 0xAA)

    def test_load_rom_file_failure(self):
        """Test loading ROM from non-existent file"""
        # Test loading
        result = self.manager.load_rom_file("non_existent_file.rom")

        # Verify results
        self.assertFalse(result)

    def test_save_rom_hex(self):
        """Test saving ROM in hex format"""
        # Load sample ROM first
        self.manager.load_rom_file(str(self.sample_rom_path))

        # Test saving
        hex_path = self.output_dir / "rom_init.hex"
        result = self.manager.save_rom_hex(str(hex_path))

        # Verify results
        self.assertTrue(result)
        self.assertTrue(hex_path.exists())

        # Check content format (should be 32-bit words in little-endian format)
        with open(hex_path, "r") as f:
            lines = f.readlines()
            self.assertGreaterEqual(len(lines), 1)
            # First line should contain the ROM signature (0x55AA) in little-endian format
            self.assertTrue(lines[0].strip().endswith("aa55"))

    def test_get_rom_info(self):
        """Test getting ROM information"""
        # Load sample ROM first
        self.manager.load_rom_file(str(self.sample_rom_path))

        # Test getting info
        info = self.manager.get_rom_info()

        # Verify results
        self.assertIsInstance(info, dict)
        self.assertEqual(info["rom_size"], "1024")
        self.assertEqual(info["valid_signature"], "True")
        self.assertEqual(info["rom_size_from_header"], "1024")  # 2 blocks * 512 bytes

    @patch("subprocess.run")
    def test_setup_option_rom(self, mock_run):
        """Test complete Option-ROM setup process"""
        # Mock subprocess calls
        mock_run.return_value = MagicMock(returncode=0)

        # Create a mock ROM file that the extraction would create
        rom_path = self.output_dir / "donor.rom"
        with open(rom_path, "wb") as f:
            f.write(bytes([0x55, 0xAA, 0x04, 0x00] + [0x00] * 2044))  # 2KB ROM

        # Test setup with existing ROM file
        self.manager.rom_file_path = str(self.sample_rom_path)
        info = self.manager.setup_option_rom("0000:01:00.0", use_existing_rom=True)

        # Verify results
        self.assertIsInstance(info, dict)
        self.assertEqual(info["rom_size"], "1024")

        # Check that hex file was created
        hex_path = self.output_dir / "rom_init.hex"
        self.assertTrue(hex_path.exists())


# Only define pytest tests if pytest is available
if PYTEST_AVAILABLE:

    @pytest.mark.parametrize("rom_size", [65536, 131072, 262144])
    def test_option_rom_size_variants(rom_size):
        """Test Option-ROM with different sizes"""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            manager = OptionROMManager(output_dir=output_dir)

            # Create a sample ROM file with specified size
            sample_rom_path = output_dir / "sample.rom"
            with open(sample_rom_path, "wb") as f:
                # Create a valid ROM with signature 0x55AA
                f.write(bytes([0x55, 0xAA]))  # ROM signature (2 bytes)

                # Size in 512-byte blocks, handle large sizes properly
                size_blocks = rom_size // 512
                if size_blocks <= 255:
                    f.write(bytes([size_blocks]))  # Size in 512-byte blocks (1 byte)
                else:
                    # For larger sizes, use a fixed value and rely on actual file size
                    f.write(bytes([0xFF]))  # Maximum size indicator (1 byte)

                # Padding to reach the desired size
                # We've already written 3 bytes (signature + size), so subtract 3
                f.write(bytes([0x00] * (rom_size - 3)))  # Padding

            # Load the ROM
            manager.load_rom_file(str(sample_rom_path))

            # Verify size
            # The ROM size should be exactly rom_size bytes
            # We've adjusted the padding to account for the signature and size byte
            assert manager.rom_size == rom_size

            # Save as hex and verify
            hex_path = output_dir / "rom_init.hex"
            manager.save_rom_hex(str(hex_path))
            assert hex_path.exists()

            # Count lines in hex file (should be rom_size/4 for 32-bit words)
            with open(hex_path, "r") as f:
                lines = f.readlines()
                assert len(lines) == rom_size // 4

else:
    # Add a placeholder class for when pytest is not available
    class TestOptionROMSizes(unittest.TestCase):
        """Test Option-ROM with different sizes"""

        def test_option_rom_sizes(self):
            """Test with different ROM sizes"""
            for rom_size in [65536, 131072, 262144]:
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_dir = Path(temp_dir)
                    manager = OptionROMManager(output_dir=output_dir)

                    # Create a sample ROM file with specified size
                    sample_rom_path = output_dir / "sample.rom"
                    with open(sample_rom_path, "wb") as f:
                        # Create a valid ROM with signature 0x55AA
                        f.write(bytes([0x55, 0xAA]))  # ROM signature
                        f.write(bytes([rom_size // 512]))  # Size in 512-byte blocks
                        f.write(bytes([0x00] * (rom_size - 2)))  # Padding

                    # Load the ROM
                    manager.load_rom_file(str(sample_rom_path))

                    # Verify size
                    self.assertEqual(manager.rom_size, rom_size)

                    # Save as hex and verify
                    hex_path = output_dir / "rom_init.hex"
                    manager.save_rom_hex(str(hex_path))
                    self.assertTrue(hex_path.exists())

                    # Count lines in hex file (should be rom_size/4 for 32-bit words)
                    with open(hex_path, "r") as f:
                        lines = f.readlines()
                        self.assertEqual(len(lines), rom_size // 4)


if __name__ == "__main__":
    unittest.main()
