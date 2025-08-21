#!/usr/bin/env python3
"""
Complete version bump script that updates both version and changelog.
This is the main script that maintainers should use for version updates.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result


def main():
    """Main version bump and changelog update script."""
    parser = argparse.ArgumentParser(
        description="Bump version and update changelog automatically"
    )
    parser.add_argument(
        "--type",
        choices=["major", "minor", "patch", "auto"],
        default="auto",
        help="Type of version bump (default: auto-detect from commits)",
    )
    parser.add_argument(
        "--version", help="Set explicit version instead of bumping (e.g., 1.2.3)"
    )
    parser.add_argument(
        "--message", help="Custom changelog message (skips commit analysis)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--skip-changelog",
        action="store_true",
        help="Skip changelog update (only update version)",
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    if args.version:
        # Set explicit version
        print(f"Setting explicit version: {args.version}")

        if args.dry_run:
            print("DRY RUN: Would set version and update changelog")
            sys.exit(0)

        # Update version
        version_cmd = f"python3 scripts/set_version.py --version {args.version}"
        if args.dry_run:
            version_cmd += " --dry-run"

        run_command(version_cmd)

        # Update changelog (set_version.py now does this automatically)
        if not args.skip_changelog:
            print("Changelog will be updated automatically by set_version.py")

    else:
        # Bump version automatically
        print(f"Bumping version with type: {args.type}")

        if args.dry_run:
            print("DRY RUN: Would bump version and update changelog")
            sys.exit(0)

        # Update version (this will also update changelog automatically)
        bump_cmd = f"python3 scripts/update_version.py --bump-type {args.type} --force"
        run_command(bump_cmd)

        if not args.skip_changelog:
            print("Changelog will be updated automatically by update_version.py")

    print("\n✅ Version and changelog update completed!")
    print("\nNext steps:")
    print("1. Review the changes with: git diff")
    print("2. Commit the changes: git add . && git commit -m 'chore: bump version'")
    print("3. Create a tag: git tag v<version>")
    print("4. Push changes: git push && git push --tags")


if __name__ == "__main__":
    main()
