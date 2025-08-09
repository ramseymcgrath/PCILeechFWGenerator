"""
Unit tests for version automation functionality.
"""

import pytest
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from update_version import (
    parse_version,
    bump_version,
    auto_determine_bump_type,
    update_version_file,
    get_git_info,
    get_recent_commits,
    get_latest_tag,
)


class TestVersionParsing:
    """Test version parsing functionality."""

    def test_parse_version_valid(self):
        """Test parsing valid version strings."""
        assert parse_version("1.2.3") == (1, 2, 3)
        assert parse_version("0.9.11") == (0, 9, 11)
        assert parse_version("10.20.30") == (10, 20, 30)

    def test_parse_version_invalid(self):
        """Test parsing invalid version strings."""
        with pytest.raises(ValueError):
            parse_version("1.2")  # Too few parts

        with pytest.raises(ValueError):
            parse_version("1.2.3.4")  # Too many parts

        with pytest.raises(ValueError):
            parse_version("1.2.x")  # Non-numeric parts

    def test_bump_version_patch(self):
        """Test patch version bumping."""
        assert bump_version("1.2.3", "patch") == "1.2.4"
        assert bump_version("0.9.11", "patch") == "0.9.12"

    def test_bump_version_minor(self):
        """Test minor version bumping."""
        assert bump_version("1.2.3", "minor") == "1.3.0"
        assert bump_version("0.9.11", "minor") == "0.10.0"

    def test_bump_version_major(self):
        """Test major version bumping."""
        assert bump_version("1.2.3", "major") == "2.0.0"
        assert bump_version("0.9.11", "major") == "1.0.0"

    def test_bump_version_invalid_type(self):
        """Test invalid bump type."""
        with pytest.raises(ValueError):
            bump_version("1.2.3", "invalid")


class TestCommitAnalysis:
    """Test commit message analysis for auto-bump detection."""

    def test_feature_commits(self):
        """Test feature commit detection."""
        commits = ["feat: add new feature", "feature: implement something"]
        assert auto_determine_bump_type(commits) == "minor"

    def test_fix_commits(self):
        """Test fix commit detection."""
        commits = ["fix: resolve bug", "bugfix: patch issue"]
        assert auto_determine_bump_type(commits) == "patch"

    def test_breaking_commits(self):
        """Test breaking change detection."""
        commits = ["feat!: breaking change"]
        assert auto_determine_bump_type(commits) == "major"

        commits = ["feat: add feature\n\nBREAKING CHANGE: removes old API"]
        assert auto_determine_bump_type(commits) == "major"

    def test_mixed_commits(self):
        """Test mixed commit types."""
        # Feature takes precedence over fix
        commits = ["feat: new feature", "fix: bug fix", "docs: update readme"]
        assert auto_determine_bump_type(commits) == "minor"

        # Breaking change takes precedence over everything
        commits = ["feat!: breaking", "feat: feature", "fix: bug"]
        assert auto_determine_bump_type(commits) == "major"

    def test_other_commits(self):
        """Test other commit types default to patch."""
        commits = ["docs: update readme", "chore: update deps"]
        assert auto_determine_bump_type(commits) == "patch"

    def test_empty_commits(self):
        """Test empty commit list defaults to patch."""
        assert auto_determine_bump_type([]) == "patch"


class TestVersionFileUpdate:
    """Test version file updating functionality."""

    def test_update_version_file(self):
        """Test updating version file with new version and metadata."""
        # Create a temporary version file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                '''"""Version information for test."""

__version__ = "0.9.11"
__version_info__ = (0, 9, 11)

# Release information
__title__ = "Test Package"
__description__ = "Test package description"
__author__ = "Test Author"
__author_email__ = "test@example.com"
__license__ = "MIT"
__url__ = "https://github.com/test/test"

# Build metadata
__build_date__ = "2025-01-01T00:00:00.000000"
__commit_hash__ = "abc123"
'''
            )
            temp_file = Path(f.name)

        try:
            # Update the version file
            update_version_file(temp_file, "0.9.12", "def456")

            # Read and verify the updated content
            content = temp_file.read_text()

            assert '__version__ = "0.9.12"' in content
            assert "__version_info__ = (0, 9, 12)" in content
            assert '__commit_hash__ = "def456"' in content
            assert (
                '__build_date__ = "2025-' in content
            )  # Should be updated to current date

            # Verify other content is preserved
            assert '__title__ = "Test Package"' in content
            assert '__author__ = "Test Author"' in content

        finally:
            temp_file.unlink()

    def test_update_version_file_missing_fields(self):
        """Test updating version file with missing optional fields."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                '''"""Minimal version file."""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
'''
            )
            temp_file = Path(f.name)

        try:
            # This should not fail even with missing build metadata
            update_version_file(temp_file, "1.0.1", "xyz789")

            content = temp_file.read_text()
            assert '__version__ = "1.0.1"' in content
            assert "__version_info__ = (1, 0, 1)" in content

        finally:
            temp_file.unlink()


class TestGitIntegration:
    """Test git integration functionality."""

    @patch("subprocess.run")
    def test_get_git_info_success(self, mock_run):
        """Test successful git info retrieval."""
        # Mock successful git commands
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="abc123\n"),  # git rev-parse --short HEAD
            MagicMock(returncode=0, stdout="main\n"),  # git rev-parse --abbrev-ref HEAD
        ]

        commit_hash, branch = get_git_info()
        assert commit_hash == "abc123"
        assert branch == "main"

    @patch("subprocess.run")
    def test_get_git_info_failure(self, mock_run):
        """Test git info retrieval failure."""
        # Mock failed git commands
        mock_run.side_effect = Exception("Git not available")

        commit_hash, branch = get_git_info()
        assert commit_hash == "unknown"
        assert branch == "unknown"

    @patch("subprocess.run")
    def test_get_recent_commits(self, mock_run):
        """Test recent commits retrieval."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="feat: add feature\nfix: bug fix\ndocs: update\n"
        )

        commits = get_recent_commits()
        expected = ["feat: add feature", "fix: bug fix", "docs: update"]
        assert commits == expected

    @patch("subprocess.run")
    def test_get_recent_commits_failure(self, mock_run):
        """Test recent commits retrieval failure."""
        mock_run.side_effect = Exception("Git not available")

        commits = get_recent_commits()
        assert commits == []

    @patch("subprocess.run")
    def test_get_latest_tag_success(self, mock_run):
        """Test successful latest tag retrieval."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v1.0.0\n")

        tag = get_latest_tag()
        assert tag == "v1.0.0"

    @patch("subprocess.run")
    def test_get_latest_tag_no_tags(self, mock_run):
        """Test latest tag retrieval when no tags exist."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        tag = get_latest_tag()
        assert tag is None


class TestVersionChecker:
    """Test enhanced version checker functionality."""

    def test_get_build_info_success(self):
        """Test successful build info retrieval."""
        # Import the function from version_checker
        sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "cli"))
        from version_checker import get_build_info

        build_info = get_build_info()
        assert isinstance(build_info, dict)
        assert "build_date" in build_info
        assert "commit_hash" in build_info

    @patch("src.cli.version_checker.get_build_info")
    def test_prompt_for_update_with_build_info(self, mock_get_build_info):
        """Test update prompt includes build information."""
        mock_get_build_info.return_value = {
            "build_date": "2025-01-01T12:00:00.000000",
            "commit_hash": "abc123",
        }

        # Import and test the prompt function
        sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "cli"))
        from version_checker import prompt_for_update

        # This should not raise an exception
        with patch("src.cli.version_checker.log_warning_safe"):
            prompt_for_update("1.0.0")


if __name__ == "__main__":
    pytest.main([__file__])
