"""Shell command execution utilities with dry-run support."""

import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


class Shell:
    """Wrapper around subprocess supporting dry_run mode."""

    def __init__(self, dry_run: bool = False):
        """Initialize shell wrapper.

        Args:
            dry_run: If True, commands will be logged but not executed
        """
        self.dry_run = dry_run

    def run(self, *parts: str, timeout: int = 30) -> str:
        """Execute a shell command and return stripped output.

        Args:
            *parts: Command parts to join with spaces
            timeout: Command timeout in seconds

        Returns:
            Command output as string

        Raises:
            RuntimeError: If command fails or times out
        """
        cmd = " ".join(str(part) for part in parts)

        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {cmd}")
            return ""

        logger.debug(f"Executing command: {cmd}")

        try:
            result = subprocess.check_output(
                cmd, shell=True, text=True, timeout=timeout, stderr=subprocess.STDOUT
            ).strip()
            logger.debug(f"Command output: {result}")
            return result

        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout}s: {cmd}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed (exit code {e.returncode}): {cmd}"
            if e.output:
                error_msg += f"\nOutput: {e.output}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def run_check(self, *parts: str, timeout: int = 30) -> bool:
        """Execute a command and return True if successful, False otherwise.

        Args:
            *parts: Command parts to join with spaces
            timeout: Command timeout in seconds

        Returns:
            True if command succeeded, False otherwise
        """
        try:
            self.run(*parts, timeout=timeout)
            return True
        except RuntimeError:
            return False

    def write_file(self, path: str, content: str) -> None:
        """Write content to a file (respects dry_run mode).

        Args:
            path: File path to write to
            content: Content to write
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would write to file: {path}")
            logger.debug(f"[DRY RUN] Content: {content}")
            return

        try:
            with open(path, "w") as f:
                f.write(content)
            logger.debug(f"Wrote content to file: {path}")
        except (OSError, IOError) as e:
            error_msg = f"Failed to write file {path}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
