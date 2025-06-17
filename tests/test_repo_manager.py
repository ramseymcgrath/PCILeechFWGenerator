#!/usr/bin/env python3
"""
Unit tests for the RepoManager class.

Tests repository management functionality including Git operations,
caching, and error handling.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.repo_manager import RepoManager


class TestRepoManager(unittest.TestCase):
    """Test cases for RepoManager functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_repo_dir = Path(self.temp_dir) / "test-repo"

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("src.repo_manager._run")
    def test_git_available_success(self, mock_run):
        """Test git availability check when git is available."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git", "--version"],
            returncode=0,
            stdout="git version 2.45.0",
            stderr="",
        )

        from src.repo_manager import _git_available

        result = _git_available()

        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch("src.repo_manager._run")
    def test_git_available_failure(self, mock_run):
        """Test git availability check when git is not available."""
        mock_run.side_effect = Exception("git not found")

        from src.repo_manager import _git_available

        result = _git_available()

        self.assertFalse(result)

    @patch("src.repo_manager.RepoManager._is_valid_repo")
    @patch("src.repo_manager.RepoManager._maybe_update")
    def test_ensure_repo_existing_repo(self, mock_update, mock_is_valid):
        """Test ensuring repo when repository already exists."""
        mock_is_valid.return_value = True

        with patch("pathlib.Path.mkdir"):
            result = RepoManager.ensure_repo(cache_dir=Path(self.temp_dir))

        self.assertEqual(result, Path(self.temp_dir) / "pcileech-fpga")
        mock_is_valid.assert_called_once()
        mock_update.assert_called_once()

    @patch("src.repo_manager.RepoManager._is_valid_repo")
    @patch("src.repo_manager.RepoManager._clone")
    @patch("shutil.rmtree")
    def test_ensure_repo_clone_new(self, mock_rmtree, mock_clone, mock_is_valid):
        """Test ensuring repo when repository needs to be cloned."""
        mock_is_valid.return_value = False

        with patch("pathlib.Path.mkdir"):
            with patch("pathlib.Path.exists", return_value=True):
                result = RepoManager.ensure_repo(cache_dir=Path(self.temp_dir))

        self.assertEqual(result, Path(self.temp_dir) / "pcileech-fpga")
        mock_is_valid.assert_called_once()
        mock_rmtree.assert_called_once()
        mock_clone.assert_called_once()

    @patch("src.repo_manager._git_available")
    @patch("src.repo_manager._run")
    def test_is_valid_repo_with_git(self, mock_run, mock_git_available):
        """Test repository validation when git is available."""
        mock_git_available.return_value = True
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git", "rev-parse"], returncode=0, stdout="", stderr=""
        )

        with patch("pathlib.Path.exists", return_value=True):
            result = RepoManager._is_valid_repo(Path(self.temp_dir))

        self.assertTrue(result)

    @patch("src.repo_manager._git_available")
    def test_is_valid_repo_without_git(self, mock_git_available):
        """Test repository validation when git is not available."""
        mock_git_available.return_value = False

        with patch("pathlib.Path.exists", return_value=True):
            result = RepoManager._is_valid_repo(Path(self.temp_dir))

        self.assertTrue(result)  # Should assume valid when .git exists but no git

    def test_is_valid_repo_no_git_dir(self):
        """Test repository validation when .git directory doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            result = RepoManager._is_valid_repo(Path(self.temp_dir))

        self.assertFalse(result)

    @patch("src.repo_manager._git_available")
    @patch("src.repo_manager._run")
    def test_maybe_update_fresh_repo(self, mock_run, mock_git_available):
        """Test update check for fresh repository."""
        mock_git_available.return_value = True

        # Mock fresh timestamp
        import datetime

        fresh_time = datetime.datetime.now().isoformat()

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=fresh_time):
                RepoManager._maybe_update(Path(self.temp_dir))

        # Should not call git pull for fresh repo
        mock_run.assert_not_called()

    @patch("src.repo_manager._git_available")
    @patch("src.repo_manager._run")
    def test_maybe_update_old_repo(self, mock_run, mock_git_available):
        """Test update for old repository."""
        mock_git_available.return_value = True

        # Mock old timestamp
        import datetime

        old_time = (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=old_time):
                with patch("pathlib.Path.write_text"):
                    RepoManager._maybe_update(Path(self.temp_dir))

        # Should call git pull for old repo
        mock_run.assert_called_once()

    @patch("src.repo_manager._git_available")
    def test_maybe_update_no_git(self, mock_git_available):
        """Test update when git is not available."""
        mock_git_available.return_value = False

        # Mock old timestamp
        import datetime

        old_time = (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=old_time):
                RepoManager._maybe_update(Path(self.temp_dir))

        # Should not attempt update without git

    @patch("src.repo_manager._git_available")
    @patch("src.repo_manager._run")
    def test_clone_success(self, mock_run, mock_git_available):
        """Test successful repository cloning."""
        mock_git_available.return_value = True
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git", "clone"], returncode=0, stdout="", stderr=""
        )

        with patch("pathlib.Path.write_text"):
            RepoManager._clone("https://github.com/test/repo.git", Path(self.temp_dir))

        mock_run.assert_called_once()

    @patch("src.repo_manager._git_available")
    def test_clone_no_git(self, mock_git_available):
        """Test cloning when git is not available."""
        mock_git_available.return_value = False

        with self.assertRaises(RuntimeError) as context:
            RepoManager._clone("https://github.com/test/repo.git", Path(self.temp_dir))

        self.assertIn("git executable not available", str(context.exception))

    @patch("src.repo_manager._git_available")
    @patch("src.repo_manager._run")
    @patch("shutil.rmtree")
    @patch("time.sleep")
    def test_clone_retry_logic(
        self, mock_sleep, mock_rmtree, mock_run, mock_git_available
    ):
        """Test clone retry logic on failure."""
        mock_git_available.return_value = True
        mock_run.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
            subprocess.CompletedProcess(
                args=["git", "clone"], returncode=0, stdout="", stderr=""
            ),
        ]

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.write_text"):
                RepoManager._clone(
                    "https://github.com/test/repo.git", Path(self.temp_dir)
                )

        # Should have tried 3 times
        self.assertEqual(mock_run.call_count, 3)
        # Should have slept twice (between retries)
        self.assertEqual(mock_sleep.call_count, 2)

    def test_get_board_path_valid_board(self):
        """Test getting board path for valid board type."""
        mock_repo_root = Path(self.temp_dir)

        with patch("pathlib.Path.exists", return_value=True):
            result = RepoManager.get_board_path("35t", repo_root=mock_repo_root)

        expected = mock_repo_root / "PCIeSquirrel"
        self.assertEqual(result, expected)

    def test_get_board_path_invalid_board(self):
        """Test getting board path for invalid board type."""
        mock_repo_root = Path(self.temp_dir)

        with self.assertRaises(RuntimeError) as context:
            RepoManager.get_board_path("invalid_board", repo_root=mock_repo_root)

        self.assertIn("Unknown board type", str(context.exception))

    def test_get_board_path_missing_directory(self):
        """Test getting board path when directory doesn't exist."""
        mock_repo_root = Path(self.temp_dir)

        with patch("pathlib.Path.exists", return_value=False):
            with self.assertRaises(RuntimeError) as context:
                RepoManager.get_board_path("35t", repo_root=mock_repo_root)

        self.assertIn("does not exist", str(context.exception))

    def test_get_xdc_files_found(self):
        """Test getting XDC files when files exist."""
        mock_repo_root = Path(self.temp_dir)
        mock_board_dir = mock_repo_root / "PCIeSquirrel"

        with patch.object(RepoManager, "get_board_path", return_value=mock_board_dir):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.glob", return_value=[Path("test.xdc")]):
                    result = RepoManager.get_xdc_files("35t", repo_root=mock_repo_root)

        self.assertEqual(result, [Path("test.xdc")])

    def test_get_xdc_files_not_found(self):
        """Test getting XDC files when no files exist."""
        mock_repo_root = Path(self.temp_dir)
        mock_board_dir = mock_repo_root / "PCIeSquirrel"

        with patch.object(RepoManager, "get_board_path", return_value=mock_board_dir):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.glob", return_value=[]):
                    with self.assertRaises(RuntimeError) as context:
                        RepoManager.get_xdc_files("35t", repo_root=mock_repo_root)

        self.assertIn("No .xdc files found", str(context.exception))

    def test_read_combined_xdc(self):
        """Test reading combined XDC content."""
        mock_repo_root = Path(self.temp_dir)
        mock_files = [Path("test1.xdc"), Path("test2.xdc")]

        with patch.object(RepoManager, "get_xdc_files", return_value=mock_files):
            with patch("pathlib.Path.read_text", return_value="# XDC content"):
                result = RepoManager.read_combined_xdc("35t", repo_root=mock_repo_root)

        self.assertIn("XDC constraints for 35t", result)
        self.assertIn("# XDC content", result)

    def test_repo_constants(self):
        """Test that repository constants are properly defined."""
        from src.repo_manager import (
            CACHE_DIR,
            DEFAULT_REPO_URL,
            REPO_DIR,
            UPDATE_INTERVAL_DAYS,
        )

        self.assertIsInstance(DEFAULT_REPO_URL, str)
        self.assertTrue(DEFAULT_REPO_URL.startswith("https://"))
        self.assertIsInstance(CACHE_DIR, Path)
        self.assertIsInstance(REPO_DIR, Path)
        self.assertIsInstance(UPDATE_INTERVAL_DAYS, int)


class TestRepoManagerIntegration(unittest.TestCase):
    """Integration tests for RepoManager."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("src.repo_manager._git_available")
    @patch("src.repo_manager._run")
    def test_full_workflow_new_repo(self, mock_run, mock_git_available):
        """Test complete workflow for new repository setup."""
        mock_git_available.return_value = True
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git"], returncode=0, stdout="", stderr=""
        )

        with patch("pathlib.Path.exists", return_value=False):
            with patch("pathlib.Path.write_text"):
                result = RepoManager.ensure_repo(cache_dir=Path(self.temp_dir))

        # Verify git clone was called
        self.assertTrue(any("clone" in str(call) for call in mock_run.call_args_list))
        self.assertEqual(result, Path(self.temp_dir) / "pcileech-fpga")

    @patch("src.repo_manager.RepoManager._is_valid_repo")
    @patch("src.repo_manager.RepoManager._maybe_update")
    def test_full_workflow_existing_repo(self, mock_update, mock_is_valid):
        """Test complete workflow for existing repository."""
        mock_is_valid.return_value = True

        with patch("pathlib.Path.mkdir"):
            result = RepoManager.ensure_repo(cache_dir=Path(self.temp_dir))

        mock_is_valid.assert_called_once()
        mock_update.assert_called_once()
        self.assertEqual(result, Path(self.temp_dir) / "pcileech-fpga")


if __name__ == "__main__":
    unittest.main()
