#!/usr/bin/env python3
"""
Set the exact package version in src/__version__.py.

Usage examples:
  # Set explicit version
  python scripts/set_version.py --version 1.2.3

  # Dry run
  python scripts/set_version.py --version 1.2.3 --dry-run

This is a small, explicit helper for maintainers who want to set the
version string directly instead of relying on `update_version.py`'s
automatic bump detection.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_cmd(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def get_git_commit_short() -> str:
    try:
        res = run_cmd("git rev-parse --short HEAD")
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "unknown"


def parse_version_tuple(version: str):
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError("Version must be in MAJOR.MINOR.PATCH format")
    return tuple(int(p) for p in parts)


def update_version_file(
    version_file: Path, new_version: str, dry_run: bool = False
) -> None:
    if not version_file.exists():
        raise FileNotFoundError(f"Version file not found: {version_file}")

    content = version_file.read_text()

    # Replace __version__
    content_new = re.sub(
        r'__version__ = ["\'][^"\']+["\']', f'__version__ = "{new_version}"', content
    )

    # Replace __version_info__ tuple if present
    try:
        major, minor, patch = parse_version_tuple(new_version)
        content_new = re.sub(
            r"__version_info__ = \([^)]+\)",
            f"__version_info__ = ({major}, {minor}, {patch})",
            content_new,
        )
    except ValueError:
        # If parse fails, leave __version_info__ untouched
        pass

    # Update build metadata if present
    build_date = datetime.utcnow().isoformat()
    content_new = re.sub(
        r'__build_date__ = ["\'][^"\']+["\']',
        f'__build_date__ = "{build_date}"',
        content_new,
    )

    commit = get_git_commit_short()
    content_new = re.sub(
        r'__commit_hash__ = ["\'][^"\']+["\']',
        f'__commit_hash__ = "{commit}"',
        content_new,
    )

    if dry_run:
        print("DRY RUN - proposed changes to", version_file)
        print("--- before ---")
        print(content)
        print("--- after ---")
        print(content_new)
        return

    version_file.write_text(content_new)
    print(f"Updated {version_file} -> {new_version} (commit: {commit})")

    # Update changelog
    try:
        changelog_script = (
            version_file.parent.parent / "scripts" / "update_changelog.py"
        )
        if changelog_script.exists():
            print(f"Updating changelog for version {new_version}...")
            import subprocess

            result = subprocess.run(
                [
                    "python3",
                    str(changelog_script),
                    "--version",
                    new_version,
                    "--message",
                    "Version update.",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("Changelog updated successfully")
            else:
                print(f"Warning: Changelog update failed: {result.stderr}")
        else:
            print("Changelog update script not found, skipping changelog update")
    except Exception as e:
        print(f"Warning: Failed to update changelog: {e}")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Set explicit package version in src/__version__.py"
    )
    p.add_argument(
        "--version", required=True, help="Version to set (MAJOR.MINOR.PATCH)"
    )
    p.add_argument(
        "--dry-run", action="store_true", help="Show changes but don't write file"
    )
    args = p.parse_args()

    project_root = Path(__file__).parent.parent
    version_file = project_root / "src" / "__version__.py"

    try:
        update_version_file(version_file, args.version, dry_run=args.dry_run)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
