#!/usr/bin/env python3
"""
Release script for PCILeech Firmware Generator.
Automates the release process including version bumping, changelog updates, and distribution building.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from git import GitCommandError, InvalidGitRepositoryError, Repo

    GIT_AVAILABLE = True
except ModuleNotFoundError:
    GIT_AVAILABLE = False
    Repo = None
    GitCommandError = InvalidGitRepositoryError = Exception

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
VERSION_FILE = PROJECT_ROOT / "src" / "__version__.py"
CHANGELOG_FILE = PROJECT_ROOT / "CHANGELOG.md"


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def get_current_version() -> str:
    """Get the current version from __version__.py."""
    with open(VERSION_FILE, "r") as f:
        content = f.read()

    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find version in __version__.py")

    return match.group(1)


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version according to semantic versioning."""
    major, minor, patch = map(int, current_version.split("."))

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return f"{major}.{minor}.{patch}"


def update_version_file(new_version: str) -> None:
    """Update the version in __version__.py."""
    with open(VERSION_FILE, "r") as f:
        content = f.read()

    # Update version
    content = re.sub(
        r'__version__ = ["\'][^"\']+["\']', f'__version__ = "{new_version}"', content
    )

    # Update version_info tuple
    major, minor, patch = map(int, new_version.split("."))
    content = re.sub(
        r"__version_info__ = \([^)]+\)",
        f"__version_info__ = ({major}, {minor}, {patch})",
        content,
    )

    with open(VERSION_FILE, "w") as f:
        f.write(content)

    print(f"Updated version to {new_version}")


def update_changelog(new_version: str, release_notes: str) -> None:
    """Update CHANGELOG.md with new release."""
    with open(CHANGELOG_FILE, "r") as f:
        content = f.read()

    # Find the position to insert new release
    lines = content.split("\n")
    insert_pos = None

    for i, line in enumerate(lines):
        if line.startswith("## [") and "Unreleased" not in line:
            insert_pos = i
            break

    if insert_pos is None:
        # Find after "# Changelog" header
        for i, line in enumerate(lines):
            if line.startswith("# Changelog"):
                insert_pos = i + 3  # Skip header and description
                break

    if insert_pos is None:
        raise ValueError("Could not find insertion point in CHANGELOG.md")

    # Create new release section
    today = datetime.now().strftime("%Y-%m-%d")
    new_section = [f"## [{new_version}] - {today}", "", release_notes, ""]

    # Insert new section
    lines[insert_pos:insert_pos] = new_section

    with open(CHANGELOG_FILE, "w") as f:
        f.write("\n".join(lines))

    print(f"Updated CHANGELOG.md with version {new_version}")


def check_git_status() -> None:
    """Check if git working directory is clean."""
    if not GIT_AVAILABLE or Repo is None:
        print("GitPython not available. Please install with: pip install GitPython")
        sys.exit(1)

    try:
        repo = Repo(PROJECT_ROOT)
        if repo.is_dirty() or repo.untracked_files:
            print("Git working directory is not clean. Please commit or stash changes.")
            sys.exit(1)
    except Exception as e:
        print(f"Error checking git status: {e}")
        sys.exit(1)


def create_git_tag(version: str) -> None:
    """Create and push git tag."""
    if not GIT_AVAILABLE or Repo is None:
        print("GitPython not available. Please install with: pip install GitPython")
        sys.exit(1)

    tag_name = f"v{version}"

    try:
        repo = Repo(PROJECT_ROOT)

        # Create tag
        repo.create_tag(tag_name, message=f"Release {version}")

        # Push tag
        origin = repo.remotes.origin
        origin.push(tag_name)

    except Exception as e:
        print(f"Error creating/pushing git tag: {e}")
        sys.exit(1)

    print(f"Created and pushed tag {tag_name}")


def build_distributions() -> None:
    """Build wheel and source distributions."""
    # Clean previous builds
    run_command("rm -rf build/ dist/ *.egg-info/", check=False)

    # Build distributions
    run_command("python -m build")

    # Check distributions
    run_command("twine check dist/*")

    print("Built and verified distributions")


def upload_to_pypi(test: bool = False) -> None:
    """Upload distributions to PyPI."""
    if test:
        repository = "--repository testpypi"
        print("Uploading to Test PyPI...")
    else:
        repository = ""
        print("Uploading to PyPI...")

    run_command(f"twine upload {repository} dist/*")
    print("Upload completed")


def main():
    """Main release script."""
    parser = argparse.ArgumentParser(description="Release PCILeech Firmware Generator")
    parser.add_argument(
        "bump_type", choices=["major", "minor", "patch"], help="Type of version bump"
    )
    parser.add_argument(
        "--release-notes", required=True, help="Release notes for this version"
    )
    parser.add_argument(
        "--test-pypi", action="store_true", help="Upload to Test PyPI instead of PyPI"
    )
    parser.add_argument(
        "--skip-upload", action="store_true", help="Skip uploading to PyPI"
    )
    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="Skip git operations (commit, tag, push)",
    )

    args = parser.parse_args()

    # Change to project root
    import os

    os.chdir(PROJECT_ROOT)

    # Check git status
    if not args.skip_git:
        check_git_status()

    # Get current version and bump it
    current_version = get_current_version()
    new_version = bump_version(current_version, args.bump_type)

    print(f"Bumping version from {current_version} to {new_version}")

    # Update version file
    update_version_file(new_version)

    # Update changelog
    update_changelog(new_version, args.release_notes)

    # Git operations
    if not args.skip_git:
        # Commit changes
        if not GIT_AVAILABLE or Repo is None:
            print("GitPython not available. Please install with: pip install GitPython")
            sys.exit(1)

        try:
            repo = Repo(PROJECT_ROOT)

            # Add all changes
            repo.git.add(A=True)

            # Commit changes
            repo.index.commit(f"chore: bump version to {new_version}")

            # Push changes
            origin = repo.remotes.origin
            origin.push()

        except Exception as e:
            print(f"Error committing/pushing changes: {e}")
            sys.exit(1)

        # Create and push tag
        create_git_tag(new_version)

    # Build distributions
    build_distributions()

    # Upload to PyPI
    if not args.skip_upload:
        upload_to_pypi(test=args.test_pypi)

    print(f"\nRelease {new_version} completed successfully!")
    print(f"- Version updated in {VERSION_FILE}")
    print(f"- Changelog updated in {CHANGELOG_FILE}")
    if not args.skip_git:
        print(f"- Git tag v{new_version} created and pushed")
    print("- Distributions built in dist/")
    if not args.skip_upload:
        pypi_name = "Test PyPI" if args.test_pypi else "PyPI"
        print(f"- Uploaded to {pypi_name}")


if __name__ == "__main__":
    main()
