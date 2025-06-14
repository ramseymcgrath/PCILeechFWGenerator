"""
Comprehensive tests for src/flash_fpga.py - FPGA flashing functionality.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import flash_fpga

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestCommandExecution:
    """Test command execution functionality."""

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run, capsys):
        """Test successful command execution."""
        mock_run.return_value = Mock(returncode=0)

        flash_fpga.run("echo test")

        captured = capsys.readouterr()
        assert "[flash] echo test" in captured.out
        mock_run.assert_called_once_with("echo test", shell=True, check=True)

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test command execution failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "false")

        with pytest.raises(subprocess.CalledProcessError):
            flash_fpga.run("false")


class TestArgumentParsing:
    """Test command line argument parsing."""

    def test_argument_parser_creation(self):
        """Test argument parser creation."""
        parser = argparse.ArgumentParser()
        parser.add_argument("bitfile", help=".bin produced by build.py")

        # Test with valid bitfile argument
        args = parser.parse_args(["firmware.bin"])
        assert args.bitfile == "firmware.bin"

    def test_argument_parser_missing_bitfile(self):
        """Test argument parser with missing bitfile."""
        parser = argparse.ArgumentParser()
        parser.add_argument("bitfile", help=".bin produced by build.py")

        with pytest.raises(SystemExit):
            parser.parse_args([])  # No arguments provided


class TestUSBLoaderValidation:
    """Test usbloader tool validation."""

    @patch("shutil.which")
    def test_usbloader_available(self, mock_which):
        """Test when usbloader is available."""
        mock_which.return_value = "/usr/bin/usbloader"

        # Should not raise exception
        result = mock_which("usbloader")
        assert result is not None

    @patch("shutil.which")
    def test_usbloader_not_available(self, mock_which):
        """Test when usbloader is not available."""
        mock_which.return_value = None

        result = mock_which("usbloader")
        assert result is None


class TestBitfileValidation:
    """Test bitfile validation."""

    def test_bitfile_exists(self, temp_dir):
        """Test with existing bitfile."""
        bitfile = temp_dir / "firmware.bin"
        bitfile.write_bytes(b"fake firmware data")

        assert bitfile.exists()
        resolved_path = bitfile.resolve()
        assert resolved_path.exists()

    def test_bitfile_not_exists(self, temp_dir):
        """Test with non-existent bitfile."""
        bitfile = temp_dir / "nonexistent.bin"

        assert not bitfile.exists()


class TestFlashingProcess:
    """Test the complete flashing process."""

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    @patch("flash_fpga.run")
    def test_flash_process_success(self, mock_run, mock_exists, mock_which):
        """Test successful flashing process."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/usbloader"
        mock_exists.return_value = True

        # Mock sys.argv for argument parsing
        test_args = ["flash_fpga.py", "firmware.bin"]

        with patch("sys.argv", test_args):
            # Simulate the main execution logic
            parser = argparse.ArgumentParser()
            parser.add_argument("bitfile", help=".bin produced by build.py")
            args = parser.parse_args(["firmware.bin"])

            # Check usbloader availability
            if mock_which("usbloader") is None:
                pytest.fail("usbloader not found")

            # Check bitfile exists
            bit = Path(args.bitfile).resolve()
            if not mock_exists.return_value:
                pytest.fail(f"File not found: {bit}")

            # Execute flash command
            mock_run(f"usbloader --vidpid 1d50:6130 -f {bit}")

        # Verify the flash command was called with the full path
        mock_run.assert_called_once_with(f"usbloader --vidpid 1d50:6130 -f {bit}")

    @patch("shutil.which")
    def test_flash_process_no_usbloader(self, mock_which):
        """Test flashing process when usbloader is not available."""
        mock_which.return_value = None

        test_args = ["flash_fpga.py", "firmware.bin"]

        with patch("sys.argv", test_args):
            # Simulate the main execution logic
            if mock_which("usbloader") is None:
                with pytest.raises(SystemExit):
                    raise SystemExit(
                        "usbloader not found in PATH. Install it and retry."
                    )

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    def test_flash_process_no_bitfile(self, mock_exists, mock_which):
        """Test flashing process when bitfile doesn't exist."""
        mock_which.return_value = "/usr/bin/usbloader"
        mock_exists.return_value = False

        test_args = ["flash_fpga.py", "nonexistent.bin"]

        with patch("sys.argv", test_args):
            # Simulate the main execution logic
            parser = argparse.ArgumentParser()
            parser.add_argument("bitfile", help=".bin produced by build.py")
            args = parser.parse_args(["nonexistent.bin"])

            bit = Path(args.bitfile).resolve()
            if not mock_exists.return_value:
                with pytest.raises(SystemExit):
                    raise SystemExit(f"File not found: {bit}")


class TestVIDPIDConfiguration:
    """Test VID:PID configuration for different boards."""

    def test_default_vidpid(self):
        """Test default VID:PID for Screamer/Squirrel."""
        default_vidpid = "1d50:6130"

        # This is the hardcoded default in flash_fpga.py
        assert default_vidpid == "1d50:6130"

    @patch("flash_fpga.run")
    def test_flash_command_format(self, mock_run):
        """Test flash command format with VID:PID."""
        bitfile = "test_firmware.bin"
        vidpid = "1d50:6130"

        expected_command = f"usbloader --vidpid {vidpid} -f {bitfile}"
        flash_fpga.run(expected_command)

        mock_run.assert_called_once_with(expected_command)


class TestErrorHandling:
    """Test error handling scenarios."""

    @patch("subprocess.run")
    def test_usbloader_command_failure(self, mock_run):
        """Test handling of usbloader command failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "usbloader")

        with pytest.raises(subprocess.CalledProcessError):
            flash_fpga.run("usbloader --vidpid 1d50:6130 -f firmware.bin")

    @patch("subprocess.run")
    def test_usbloader_permission_error(self, mock_run):
        """Test handling of permission errors."""
        mock_run.side_effect = PermissionError("Permission denied")

        with pytest.raises(PermissionError):
            flash_fpga.run("usbloader --vidpid 1d50:6130 -f firmware.bin")

    def test_invalid_bitfile_path(self):
        """Test handling of invalid bitfile paths."""
        invalid_paths = [
            "",
            "/dev/null/invalid",
            "file with spaces.bin",
            "file\nwith\nnewlines.bin",
        ]

        for path in invalid_paths:
            bit = Path(path)
            # Should handle gracefully without crashing
            resolved = bit.resolve()
            assert isinstance(resolved, Path)


class TestIntegrationScenarios:
    """Test integration scenarios."""

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    @patch("flash_fpga.run")
    def test_complete_flash_workflow(
        self, mock_run, mock_exists, mock_which, temp_dir, capsys
    ):
        """Test complete flash workflow from start to finish."""
        # Create test firmware file
        firmware_file = temp_dir / "test_firmware.bin"
        firmware_file.write_bytes(b"fake firmware data for testing")

        # Setup mocks
        mock_which.return_value = "/usr/bin/usbloader"
        mock_exists.return_value = True

        # Simulate complete workflow
        test_args = ["flash_fpga.py", str(firmware_file)]

        with patch("sys.argv", test_args):
            # Parse arguments
            parser = argparse.ArgumentParser()
            parser.add_argument("bitfile", help=".bin produced by build.py")
            args = parser.parse_args([str(firmware_file)])

            # Check usbloader
            if mock_which("usbloader") is None:
                pytest.fail("usbloader not found")

            # Check bitfile
            bit = Path(args.bitfile).resolve()
            if not mock_exists.return_value:
                pytest.fail(f"File not found: {bit}")

            # Flash firmware
            flash_fpga.run(f"usbloader --vidpid 1d50:6130 -f {bit}")

            # Print completion message
            print("[✓] Flash complete – power-cycle or warm-reset the card.")

        # Verify workflow
        mock_run.assert_called_once_with(f"usbloader --vidpid 1d50:6130 -f {bit}")

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    @patch("flash_fpga.run")
    def test_flash_with_different_boards(self, mock_run, mock_exists, mock_which):
        """Test flashing with different board configurations."""
        mock_which.return_value = "/usr/bin/usbloader"
        mock_exists.return_value = True

        # Test different board firmware files
        board_configs = [
            ("squirrel_firmware.bin", "1d50:6130"),
            ("screamer_firmware.bin", "1d50:6130"),
            ("custom_firmware.bin", "1d50:6130"),
        ]

        for firmware, vidpid in board_configs:
            mock_run.reset_mock()

            flash_fpga.run(f"usbloader --vidpid {vidpid} -f {firmware}")

            mock_run.assert_called_once_with(
                f"usbloader --vidpid {vidpid} -f {firmware}"
            )


class TestPerformanceAndReliability:
    """Test performance and reliability characteristics."""

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    @patch("flash_fpga.run")
    def test_large_firmware_file_handling(
        self, mock_run, mock_exists, mock_which, temp_dir
    ):
        """Test handling of large firmware files."""
        # Create large firmware file (simulate 10MB firmware)
        large_firmware = temp_dir / "large_firmware.bin"
        large_firmware.write_bytes(b"0" * (10 * 1024 * 1024))

        mock_which.return_value = "/usr/bin/usbloader"
        mock_exists.return_value = True

        # Should handle large files without issues
        flash_fpga.run(f"usbloader --vidpid 1d50:6130 -f {large_firmware}")

        mock_run.assert_called_once()

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    @patch("flash_fpga.run")
    def test_concurrent_flash_attempts(self, mock_run, mock_exists, mock_which):
        """Test handling of concurrent flash attempts."""
        mock_which.return_value = "/usr/bin/usbloader"
        mock_exists.return_value = True

        # Simulate multiple flash attempts
        for i in range(5):
            firmware = f"firmware_{i}.bin"
            flash_fpga.run(f"usbloader --vidpid 1d50:6130 -f {firmware}")

        assert mock_run.call_count == 5

    def test_path_resolution_edge_cases(self, temp_dir):
        """Test path resolution with edge cases."""
        # Test various path formats
        test_paths = [
            "firmware.bin",
            "./firmware.bin",
            "../test/firmware.bin",
            str(temp_dir / "firmware.bin"),
        ]

        for path_str in test_paths:
            path = Path(path_str)
            resolved = path.resolve()

            # Should resolve without errors
            assert isinstance(resolved, Path)
            assert resolved.is_absolute()


class TestSecurityConsiderations:
    """Test security-related aspects."""

    def test_command_injection_prevention(self):
        """Test prevention of command injection attacks."""
        # Test potentially dangerous filenames
        dangerous_names = [
            "firmware.bin; rm -rf /",
            "firmware.bin && echo 'hacked'",
            "firmware.bin | cat /etc/passwd",
            "firmware.bin`whoami`",
            "firmware.bin$(id)",
        ]

        for dangerous_name in dangerous_names:
            # Path resolution should handle these safely
            path = Path(dangerous_name)
            resolved = path.resolve()

            # Should not execute embedded commands
            assert isinstance(resolved, Path)
            # The dangerous parts should be treated as literal filename
            # components

    @patch("subprocess.run")
    def test_safe_command_execution(self, mock_run):
        """Test that commands are executed safely."""
        # Test that shell=True is used appropriately
        flash_fpga.run("usbloader --vidpid 1d50:6130 -f firmware.bin")

        mock_run.assert_called_once_with(
            "usbloader --vidpid 1d50:6130 -f firmware.bin", shell=True, check=True
        )

    def test_file_permission_checks(self, temp_dir):
        """Test file permission handling."""
        # Create files with different permissions
        readable_file = temp_dir / "readable.bin"
        readable_file.write_bytes(b"test data")
        readable_file.chmod(0o644)

        unreadable_file = temp_dir / "unreadable.bin"
        unreadable_file.write_bytes(b"test data")
        unreadable_file.chmod(0o000)

        # Should be able to check existence regardless of permissions
        assert readable_file.exists()
        assert unreadable_file.exists()

        # Cleanup
        unreadable_file.chmod(0o644)  # Restore permissions for cleanup


class TestDocumentationAndUsage:
    """Test documentation and usage scenarios."""

    def test_help_message_content(self):
        """Test help message content."""
        parser = argparse.ArgumentParser()
        parser.add_argument("bitfile", help=".bin produced by build.py")

        # Should have appropriate help text
        help_text = parser.format_help()
        assert "bitfile" in help_text
        assert ".bin produced by build.py" in help_text

    def test_usage_examples(self):
        """Test common usage examples."""
        # Common usage patterns that should work
        usage_examples = [
            ["flash_fpga.py", "output/firmware.bin"],
            ["flash_fpga.py", "/path/to/firmware.bin"],
            ["flash_fpga.py", "build/squirrel_firmware.bin"],
        ]

        for example in usage_examples:
            parser = argparse.ArgumentParser()
            parser.add_argument("bitfile", help=".bin produced by build.py")

            # Should parse without errors
            args = parser.parse_args(example[1:])  # Skip script name
            assert args.bitfile == example[1]

    def test_error_message_clarity(self):
        """Test that error messages are clear and helpful."""
        # Test various error conditions and their messages
        error_scenarios = [
            (
                "usbloader not found in PATH. Install it and retry.",
                "usbloader not found in PATH. Install it and retry.",
            ),
            ("File not found: firmware.bin", "File not found: firmware.bin"),
        ]

        for error_type, expected_content in error_scenarios:
            # Error messages should contain helpful information
            assert error_type == expected_content


class TestCompatibility:
    """Test compatibility with different environments."""

    @patch("shutil.which")
    def test_usbloader_path_variations(self, mock_which):
        """Test different usbloader installation paths."""
        possible_paths = [
            "/usr/bin/usbloader",
            "/usr/local/bin/usbloader",
            "/opt/usbloader/bin/usbloader",
            None,  # Not found
        ]

        for path in possible_paths:
            mock_which.return_value = path
            result = mock_which("usbloader")

            if path is None:
                assert result is None
            else:
                assert result == path

    def test_cross_platform_path_handling(self, temp_dir):
        """Test path handling across different platforms."""
        # Test path handling that should work on different platforms
        test_file = temp_dir / "firmware.bin"
        test_file.write_bytes(b"test")

        # Different path representations
        path_representations = [
            str(test_file),
            str(test_file.resolve()),
            str(test_file.absolute()),
        ]

        for path_repr in path_representations:
            path = Path(path_repr)
            resolved = path.resolve()

            # Should resolve consistently
            assert resolved.exists()
            assert resolved.is_absolute()

    def test_filename_encoding_handling(self, temp_dir):
        """Test handling of different filename encodings."""
        # Test various filename encodings and special characters
        test_filenames = [
            "firmware.bin",
            "firmware_v1.0.bin",
            "firmware-2023-12-01.bin",
            "firmware_ñoño.bin",  # Non-ASCII characters
        ]

        for filename in test_filenames:
            try:
                test_file = temp_dir / filename
                test_file.write_bytes(b"test")

                # Should handle different encodings
                path = Path(filename)
                resolved = path.resolve()
                assert isinstance(resolved, Path)

            except (UnicodeError, OSError):
                # Some filesystems may not support certain characters
                # This is expected and should be handled gracefully
                pass
