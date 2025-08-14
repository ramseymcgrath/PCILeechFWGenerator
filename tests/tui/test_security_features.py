"""
Tests for the PCILeech TUI application security features.

This module tests the input validation and privilege management
functionality added to enhance security.
"""

import asyncio
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.tui.utils.input_validator import InputValidator
from src.tui.utils.privilege_manager import PrivilegeManager


class TestInputValidator(unittest.TestCase):
    """Test the InputValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary test file and directory
        self.test_dir = Path("test_dir")
        self.test_file = self.test_dir / "test_file.txt"

        if not self.test_dir.exists():
            self.test_dir.mkdir()

        if not self.test_file.exists():
            self.test_file.touch()

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove test file and directory
        if self.test_file.exists():
            self.test_file.unlink()

        if self.test_dir.exists():
            self.test_dir.rmdir()

    def test_validate_file_path(self):
        """Test file path validation."""
        # Test valid file path
        is_valid, error = InputValidator.validate_file_path(str(self.test_file))
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Test non-existent file
        is_valid, error = InputValidator.validate_file_path("nonexistent_file.txt")
        self.assertFalse(is_valid)
        self.assertIn("does not exist", error)

        # Test directory as file
        is_valid, error = InputValidator.validate_file_path(str(self.test_dir))
        self.assertFalse(is_valid)
        self.assertIn("not a file", error)

    def test_validate_directory_path(self):
        """Test directory path validation."""
        # Test valid directory path
        is_valid, error = InputValidator.validate_directory_path(str(self.test_dir))
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Test non-existent directory
        is_valid, error = InputValidator.validate_directory_path("nonexistent_dir")
        self.assertFalse(is_valid)
        self.assertIn("does not exist", error)

        # Test file as directory
        is_valid, error = InputValidator.validate_directory_path(str(self.test_file))
        self.assertFalse(is_valid)
        self.assertIn("not a directory", error)

    def test_validate_bdf(self):
        """Test BDF validation."""
        # Test valid BDF
        is_valid, error = InputValidator.validate_bdf("0000:01:00.0")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Test invalid BDF format
        is_valid, error = InputValidator.validate_bdf("01:00.0")
        self.assertFalse(is_valid)
        self.assertIn("Invalid BDF format", error)

        is_valid, error = InputValidator.validate_bdf("0000:XX:00.0")
        self.assertFalse(is_valid)
        self.assertIn("Invalid BDF format", error)

    def test_validate_non_empty(self):
        """Test non-empty validation."""
        # Test non-empty string
        is_valid, error = InputValidator.validate_non_empty("test", "Field")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Test empty string
        is_valid, error = InputValidator.validate_non_empty("", "Field")
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", error)

        # Test whitespace string
        is_valid, error = InputValidator.validate_non_empty("  ", "Field")
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", error)

    def test_validate_numeric(self):
        """Test numeric validation."""
        # Test valid numeric string
        is_valid, error = InputValidator.validate_numeric("123.45", "Field")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Test invalid numeric string
        is_valid, error = InputValidator.validate_numeric("abc", "Field")
        self.assertFalse(is_valid)
        self.assertIn("must be a number", error)

    def test_validate_in_range(self):
        """Test range validation."""
        # Test in range
        is_valid, error = InputValidator.validate_in_range("5", 0, 10, "Field")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Test out of range
        is_valid, error = InputValidator.validate_in_range("15", 0, 10, "Field")
        self.assertFalse(is_valid)
        self.assertIn("must be between", error)

        # Test invalid number
        is_valid, error = InputValidator.validate_in_range("abc", 0, 10, "Field")
        self.assertFalse(is_valid)
        self.assertIn("must be a number", error)

    def test_validate_in_choices(self):
        """Test choices validation."""
        choices = ["option1", "option2", "option3"]

        # Test valid choice
        is_valid, error = InputValidator.validate_in_choices(
            "option2", choices, "Field"
        )
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Test invalid choice
        is_valid, error = InputValidator.validate_in_choices(
            "option4", choices, "Field"
        )
        self.assertFalse(is_valid)
        self.assertIn("must be one of", error)

    def test_validate_config(self):
        """Test configuration validation."""
        # Set up a mock directory for testing
        with patch.object(
            InputValidator, "validate_directory_path", return_value=(True, "")
        ):
            # Test valid config
            config = {
                "device_id": "0000:01:00.0",
                "board_type": "test_board",
                "output_directory": str(self.test_dir),
            }
            is_valid, error = InputValidator.validate_config(config)
            self.assertTrue(is_valid)
            self.assertEqual(error, "")

            # Test missing required field
            config = {
                "device_id": "0000:01:00.0",
                "board_type": "test_board",
                # Missing output_directory
            }
            is_valid, error = InputValidator.validate_config(config)
            self.assertFalse(is_valid)
            self.assertIn("Missing required field", error)


class TestPrivilegeManager(unittest.TestCase):
    """Test the PrivilegeManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.privilege_manager = PrivilegeManager()

        # Mock os.geteuid() to control root status for testing
        self.geteuid_patcher = patch("os.geteuid")
        self.mock_geteuid = self.geteuid_patcher.start()

        # Mock subprocess.run to control sudo availability
        self.subprocess_patcher = patch("subprocess.run")
        self.mock_subprocess = self.subprocess_patcher.start()

    def tearDown(self):
        """Clean up test fixtures."""
        self.geteuid_patcher.stop()
        self.subprocess_patcher.stop()

    def test_check_root(self):
        """Test root privilege checking."""
        # Test as root
        self.mock_geteuid.return_value = 0
        self.assertTrue(self.privilege_manager._check_root())

        # Test as non-root
        self.mock_geteuid.return_value = 1000
        self.assertFalse(self.privilege_manager._check_root())

    def test_check_sudo(self):
        """Test sudo availability checking."""
        # Mock successful sudo check
        mock_result = MagicMock()
        mock_result.returncode = 0
        self.mock_subprocess.return_value = mock_result

        # Test sudo available
        self.assertTrue(self.privilege_manager._check_sudo())

        # Test sudo requires password
        mock_result.returncode = 1
        self.assertTrue(self.privilege_manager._check_sudo())

        # Test sudo not available
        mock_result.returncode = 127  # Command not found
        self.assertFalse(self.privilege_manager._check_sudo())

    @patch("shutil.which", return_value=None)
    def test_check_sudo_not_installed(self, mock_which):
        """Test sudo not installed."""
        self.assertFalse(self.privilege_manager._check_sudo())

    @patch("asyncio.create_subprocess_exec")
    async def test_run_with_privileges(self, mock_exec):
        """Test running commands with elevated privileges."""
        # Mock process result
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"stdout", b"stderr")
        mock_exec.return_value = mock_process

        # Test as root
        self.mock_geteuid.return_value = 0
        self.privilege_manager.has_root = True

        result, stdout, stderr = await self.privilege_manager.run_with_privileges(
            ["test", "command"], "test_operation"
        )

        self.assertTrue(result)
        self.assertEqual(stdout, "stdout")
        self.assertEqual(stderr, "stderr")

        # Verify command was executed directly, not with sudo
        mock_exec.assert_called_with(
            "test",
            "command",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Test as non-root with sudo
        self.mock_geteuid.return_value = 1000
        self.privilege_manager.has_root = False
        self.privilege_manager.can_sudo = True

        # Mock successful privilege request
        with patch.object(
            self.privilege_manager, "request_privileges", return_value=True
        ):
            result, stdout, stderr = await self.privilege_manager.run_with_privileges(
                ["test", "command"], "test_operation"
            )

            self.assertTrue(result)

            # Verify command was executed with sudo
            mock_exec.assert_called_with(
                "sudo",
                "test",
                "command",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )


if __name__ == "__main__":
    unittest.main()
