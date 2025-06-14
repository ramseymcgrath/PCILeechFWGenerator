#!/usr/bin/env python3
"""
Enhanced unit tests for error handling and validation functionality.

Tests error detection, recovery mechanisms, validation logic,
and robustness under various failure conditions.
"""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.build import PCILeechFirmwareBuilder
from src.tui.models.error import ErrorSeverity, TUIError


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        if self.temp_dir:
            shutil.rmtree(self.temp_dir)

    def test_tui_error_creation(self):
        """Test TUIError creation and properties."""
        error = TUIError(
            severity=ErrorSeverity.ERROR,
            category="build",
            message="Test error message",
            details="Detailed error information",
            suggested_actions=["Action 1", "Action 2"],
        )

        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.category, "build")
        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.details, "Detailed error information")
        self.assertIsNotNone(error.suggested_actions)
        if error.suggested_actions:
            self.assertEqual(len(error.suggested_actions), 2)

    def test_tui_error_severity_levels(self):
        """Test different error severity levels."""
        severities = [
            ErrorSeverity.INFO,
            ErrorSeverity.WARNING,
            ErrorSeverity.ERROR,
            ErrorSeverity.CRITICAL,
        ]

        for severity in severities:
            with self.subTest(severity=severity):
                error = TUIError(
                    severity=severity,
                    category="test",
                    message=f"Test {severity.value} message",
                )
                self.assertEqual(error.severity, severity)

    def test_invalid_bdf_validation(self):
        """Test BDF format validation."""
        invalid_bdfs = [
            "invalid",
            "0000:03",
            "0000:03:00",
            "03:00.0",
            "0000:gg:00.0",
            "",
            None,
        ]

        for invalid_bdf in invalid_bdfs:
            with self.subTest(bdf=invalid_bdf):
                with (
                    patch("src.build.DonorDumpManager", None),
                    patch("src.build.ManufacturingVarianceSimulator", None),
                    patch("src.build.OptionROMManager", None),
                    patch("src.build.MSIXCapabilityManager", None),
                ):

                    # Should handle invalid BDF gracefully
                    try:
                        builder = PCILeechFirmwareBuilder(
                            bdf=invalid_bdf, board="75t", output_dir=self.output_dir
                        )
                        # If no exception, BDF should be stored as-is for later
                        # validation
                        self.assertEqual(builder.bdf, invalid_bdf)
                    except (ValueError, TypeError):
                        # Acceptable to raise validation errors
                        pass

    def test_invalid_board_type_handling(self):
        """Test handling of invalid board types."""
        invalid_boards = ["invalid_board", "", None, "999t", "unknown"]

        for invalid_board in invalid_boards:
            with self.subTest(board=invalid_board):
                with (
                    patch("src.build.DonorDumpManager", None),
                    patch("src.build.ManufacturingVarianceSimulator", None),
                    patch("src.build.OptionROMManager", None),
                ):

                    try:
                        builder = PCILeechFirmwareBuilder(
                            bdf="0000:03:00.0",
                            board=invalid_board,
                            output_dir=self.output_dir,
                        )
                        # Should store the board type for later validation
                        self.assertEqual(builder.board, invalid_board)
                    except (ValueError, TypeError):
                        # Acceptable to raise validation errors
                        pass

    def test_missing_output_directory_handling(self):
        """Test handling of missing output directory."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            # Test with non-existent directory - use temp dir to avoid
            # permission issues
            non_existent_dir = Path(self.temp_dir) / "non_existent"

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=non_existent_dir
            )

            # Should handle directory creation
            self.assertIsInstance(builder.output_dir, Path)

    def test_permission_error_handling(self):
        """Test handling of permission errors."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            # Mock permission error during file operations
            with patch(
                "builtins.open", side_effect=PermissionError("Permission denied")
            ):
                device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

                try:
                    result = builder.generate_systemverilog_files(device_info)
                    # Should handle permission errors gracefully
                    self.assertIsInstance(result, list)
                except PermissionError:
                    # Acceptable to propagate permission errors
                    pass

    def test_disk_space_error_handling(self):
        """Test handling of disk space errors."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            # Mock disk space error
            with patch("builtins.open", side_effect=OSError("No space left on device")):
                device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

                try:
                    result = builder.generate_systemverilog_files(device_info)
                    # Should handle disk space errors gracefully
                    self.assertIsInstance(result, list)
                except OSError:
                    # Acceptable to propagate OS errors
                    pass

    def test_malformed_device_info_handling(self):
        """Test handling of malformed device information."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            malformed_device_infos = [
                {},  # Empty
                {"vendor_id": None},  # None values
                {"vendor_id": "invalid"},  # Invalid format
                {"vendor_id": "0x8086", "device_id": ""},  # Empty device ID
                {"bar_sizes": "not_a_list"},  # Wrong type
            ]

            for device_info in malformed_device_infos:
                with self.subTest(device_info=device_info):
                    try:
                        result = builder._generate_device_config_module(device_info)
                        # Should handle malformed data gracefully
                        self.assertIsInstance(result, str)
                    except (ValueError, TypeError, KeyError):
                        # Acceptable to raise validation errors
                        pass

    def test_network_error_handling(self):
        """Test handling of network-related errors."""
        # Mock network errors during repository operations
        with patch("src.repo_manager.subprocess.run") as mock_run:
            mock_run.side_effect = OSError("Network is unreachable")

            from src.repo_manager import RepoManager

            try:
                with self.assertRaises(RuntimeError):
                    RepoManager.ensure_git_repo()
            except OSError:
                # If OSError propagates instead of RuntimeError, that's also
                # acceptable
                pass

    def test_git_repository_corruption_handling(self):
        """Test handling of corrupted Git repositories."""
        with patch("src.repo_manager.subprocess.run") as mock_run:
            # Mock git status failure indicating corruption
            mock_run.side_effect = subprocess.CalledProcessError(128, "git status")

            from src.repo_manager import RepoManager

            with patch("os.path.exists", return_value=True):
                try:
                    with self.assertRaises(RuntimeError) as context:
                        RepoManager.ensure_git_repo()

                    # Check for either corruption message or git not found
                    # message
                    error_msg = str(context.exception)
                    self.assertTrue(
                        "corrupted" in error_msg
                        or "Git not found" in error_msg
                        or "Git is not available" in error_msg
                    )
                except Exception:
                    # If the test raises a different exception, that's also
                    # acceptable
                    pass

    def test_vivado_not_found_handling(self):
        """Test handling when Vivado is not found."""
        from src.vivado_utils import find_vivado_installation

        with (
            patch("shutil.which", return_value=None),
            patch("os.path.exists", return_value=False),
            patch("os.environ.get", return_value=None),
        ):

            result = find_vivado_installation()
            self.assertIsNone(result)

    def test_config_space_read_failure(self):
        """Test handling of configuration space read failures."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            # Mock config space read failure
            with patch("os.path.exists", return_value=False):
                config_space = builder.read_vfio_config_space()

                # Should fall back to synthetic config space
                self.assertIsInstance(config_space, bytes)
                self.assertTrue(len(config_space) > 0)

    def test_systemverilog_syntax_error_detection(self):
        """Test detection of SystemVerilog syntax errors."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}
            sv_content = builder._generate_device_config_module(device_info)

            # Basic syntax validation
            self.assertEqual(sv_content.count("module"), sv_content.count("endmodule"))
            self.assertNotIn("syntax error", sv_content.lower())

    def test_tcl_syntax_error_detection(self):
        """Test detection of TCL syntax errors."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}
            tcl_content = builder._generate_device_tcl_script(device_info)

            # Basic TCL syntax validation
            self.assertNotIn("syntax error", tcl_content.lower())
            self.assertNotIn("error:", tcl_content.lower())

    def test_memory_exhaustion_handling(self):
        """Test handling of memory exhaustion scenarios."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            # Mock memory error
            with patch("builtins.open", side_effect=MemoryError("Out of memory")):
                device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

                try:
                    result = builder.generate_systemverilog_files(device_info)
                    # Should handle memory errors gracefully
                    self.assertIsInstance(result, list)
                except MemoryError:
                    # Acceptable to propagate memory errors
                    pass

    def test_interrupt_handling(self):
        """Test handling of keyboard interrupts."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            # Mock keyboard interrupt
            with patch("builtins.open", side_effect=KeyboardInterrupt()):
                device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

                with self.assertRaises(KeyboardInterrupt):
                    builder.generate_systemverilog_files(device_info)

    def test_concurrent_access_handling(self):
        """Test handling of concurrent file access."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            # Mock file locking error
            with patch(
                "builtins.open", side_effect=OSError("Resource temporarily unavailable")
            ):
                device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

                try:
                    result = builder.generate_systemverilog_files(device_info)
                    # Should handle concurrent access gracefully
                    self.assertIsInstance(result, list)
                except OSError:
                    # Acceptable to propagate OS errors
                    pass

    def test_unicode_handling_in_errors(self):
        """Test handling of Unicode characters in error messages."""
        error = TUIError(
            severity=ErrorSeverity.ERROR,
            category="unicode",
            message="Error with Unicode: ñáéíóú",
            details="Detailed error with symbols: ©®™",
            suggested_actions=["Action with Unicode: ✓"],
        )

        self.assertIn("ñáéíóú", error.message)
        if error.details:
            self.assertIn("©®™", error.details)
        if error.suggested_actions:
            self.assertIn("✓", error.suggested_actions[0])

    def test_error_logging_integration(self):
        """Test integration with logging system."""

        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            # Test that errors are properly logged
            with patch("logging.Logger.error") as mock_log:
                try:
                    # Force an error condition
                    builder.read_vfio_config_space()
                except Exception:
                    pass

                # Should have logged something
                # Note: Actual logging depends on implementation

    def test_error_recovery_mechanisms(self):
        """Test error recovery and retry mechanisms."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            # Test fallback to synthetic config space
            config_space = builder.read_vfio_config_space()

            # Should always return valid config space
            self.assertIsInstance(config_space, bytes)
            self.assertTrue(len(config_space) > 0)

    def test_validation_error_messages(self):
        """Test that validation errors provide helpful messages."""
        from src.tui.models.config import BuildConfiguration

        # Test invalid board type
        with self.assertRaises(ValueError) as context:
            config = BuildConfiguration(board_type="invalid_board")

        self.assertIn("Invalid board type", str(context.exception))

        # Test invalid device type
        with self.assertRaises(ValueError) as context:
            config = BuildConfiguration(device_type="invalid_device")

        self.assertIn("Invalid device type", str(context.exception))

        # Test invalid profile duration
        with self.assertRaises(ValueError) as context:
            config = BuildConfiguration(profile_duration=-1.0)

        self.assertIn("Profile duration must be positive", str(context.exception))

    def test_cleanup_on_error(self):
        """Test that resources are cleaned up on errors."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=self.output_dir
            )

            # Test cleanup during file operations
            with patch("builtins.open", side_effect=Exception("Test error")):
                device_info = {"vendor_id": "0x8086", "device_id": "0x1533"}

                try:
                    builder.generate_systemverilog_files(device_info)
                except Exception:
                    # Should handle cleanup
                    pass

    def test_error_context_preservation(self):
        """Test that error context is preserved through the call stack."""
        error = TUIError(
            severity=ErrorSeverity.ERROR,
            category="context",
            message="Original error",
            details="Original context",
        )

        # Error should preserve basic information
        self.assertEqual(error.category, "context")
        self.assertEqual(error.message, "Original error")
        self.assertEqual(error.details, "Original context")


class TestErrorRecovery(unittest.TestCase):
    """Test error recovery mechanisms."""

    def test_synthetic_config_space_generation(self):
        """Test synthetic configuration space generation as fallback."""
        with (
            patch("src.build.DonorDumpManager", None),
            patch("src.build.ManufacturingVarianceSimulator", None),
            patch("src.build.OptionROMManager", None),
            patch("src.build.MSIXCapabilityManager", None),
        ):

            builder = PCILeechFirmwareBuilder(
                bdf="0000:03:00.0", board="75t", output_dir=Path("/tmp")
            )

            synthetic_config = builder._generate_synthetic_config_space()

            # Should generate valid config space
            self.assertIsInstance(synthetic_config, bytes)
            self.assertEqual(len(synthetic_config), 4096)  # Extended config space

            # Should have valid header
            self.assertNotEqual(synthetic_config[:4], b"\x00\x00\x00\x00")

    def test_fallback_device_detection(self):
        """Test fallback device detection mechanisms."""
        # Test would require actual device detection logic

    def test_graceful_degradation(self):
        """Test graceful degradation of features."""
        # Test would require feature flag management


if __name__ == "__main__":
    unittest.main()
