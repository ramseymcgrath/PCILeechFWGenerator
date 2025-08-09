#!/usr/bin/env python3
"""
Test script for the automated version update functionality.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch


def run_command(cmd: str) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def test_version_parsing():
    """Test version parsing functionality."""
    print("Testing version parsing...")

    # Import the update script
    sys.path.insert(0, str(Path(__file__).parent))
    from update_version import bump_version, parse_version

    # Test version parsing
    assert parse_version("1.2.3") == (1, 2, 3)
    assert parse_version("0.9.11") == (0, 9, 11)

    try:
        parse_version("1.2")  # Should fail
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # Test version bumping
    assert bump_version("1.2.3", "patch") == "1.2.4"
    assert bump_version("1.2.3", "minor") == "1.3.0"
    assert bump_version("1.2.3", "major") == "2.0.0"

    print("✅ Version parsing tests passed")


def test_commit_analysis():
    """Test commit message analysis for auto-bump detection."""
    print("Testing commit analysis...")

    sys.path.insert(0, str(Path(__file__).parent))
    from update_version import auto_determine_bump_type

    # Test different commit types
    feat_commits = ["feat: add new feature", "feature: implement something"]
    assert auto_determine_bump_type(feat_commits) == "minor"

    fix_commits = ["fix: resolve bug", "bugfix: patch issue"]
    assert auto_determine_bump_type(fix_commits) == "patch"

    breaking_commits = [
        "feat!: breaking change",
        "feat: add feature\n\nBREAKING CHANGE: removes old API",
    ]
    assert auto_determine_bump_type(breaking_commits) == "major"

    mixed_commits = ["feat: new feature", "fix: bug fix", "docs: update readme"]
    assert (
        auto_determine_bump_type(mixed_commits) == "minor"
    )  # Feature takes precedence

    print("✅ Commit analysis tests passed")


def test_version_file_update():
    """Test version file updating functionality."""
    print("Testing version file updates...")

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
        sys.path.insert(0, str(Path(__file__).parent))
        from update_version import update_version_file

        # Update the version file
        update_version_file(temp_file, "0.9.12", "def456")

        # Read and verify the updated content
        content = temp_file.read_text()

        assert '__version__ = "0.9.12"' in content
        assert "__version_info__ = (0, 9, 12)" in content
        assert '__commit_hash__ = "def456"' in content
        assert '__build_date__ = "2025-' in content  # Should be updated to current date

        print("✅ Version file update tests passed")

    finally:
        temp_file.unlink()


def test_dry_run():
    """Test dry run functionality."""
    print("Testing dry run mode...")

    # Run the update script in dry run mode
    result = run_command("python scripts/update_version.py --dry-run --force")

    # Should not fail and should show what would be updated
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout

    print("✅ Dry run tests passed")


def test_git_integration():
    """Test git integration functionality."""
    print("Testing git integration...")

    # Check if we're in a git repository
    result = run_command("git rev-parse --git-dir")
    if result.returncode != 0:
        print("⚠️  Not in a git repository, skipping git integration tests")
        return

    sys.path.insert(0, str(Path(__file__).parent))
    from update_version import get_git_info, get_latest_tag, get_recent_commits

    # Test git info retrieval
    commit_hash, branch = get_git_info()
    assert len(commit_hash) > 0
    assert len(branch) > 0

    # Test recent commits retrieval
    commits = get_recent_commits()
    assert isinstance(commits, list)

    # Test latest tag retrieval (may be None if no tags exist)
    latest_tag = get_latest_tag()
    assert latest_tag is None or isinstance(latest_tag, str)

    print("✅ Git integration tests passed")


def main():
    """Run all tests."""
    print("🧪 Running version update tests...\n")

    try:
        test_version_parsing()
        test_commit_analysis()
        test_version_file_update()
        test_dry_run()
        test_git_integration()

        print("\n🎉 All tests passed!")
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
