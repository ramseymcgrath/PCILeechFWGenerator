#!/usr/bin/env python3
"""
VivadoRunner: Simplified Vivado Integration

A streamlined class that handles Vivado execution with minimal overhead,
designed to replace the complex container-based approach.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from ..log_config import get_logger
from ..build import VivadoIntegrationError


class VivadoRunner:
    """
    Handles everything Vivado SIMPLY

    Attributes:
        board: current target device
        output_dir: dir for generated vivado project
        vivado_path: root path to xilinx vivado installation (all paths derived from here)
        logger: attach a logger
    """

    def __init__(
        self,
        board: str,
        output_dir: Path,
        vivado_path: str,
        logger: Optional[logging.Logger] = None,
        device_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize VivadoRunner with simplified configuration.

        Args:
            board: Target board name (e.g., "pcileech_35t325_x1")
            output_dir: Directory for generated Vivado project
            vivado_path: Root path to Xilinx Vivado installation
            logger: Optional logger instance
            device_config: Optional device configuration dictionary
        """
        self.logger: logging.Logger = logger or get_logger(self.__class__.__name__)
        self.board: str = board
        self.output_dir: Path = Path(output_dir)
        self.vivado_path: str = vivado_path
        self.device_config: Optional[Dict[str, Any]] = device_config

        # Derive paths from vivado_path
        self.vivado_executable: str = f"{self.vivado_path}/bin/vivado"
        self.vivado_bin_dir: str = f"{self.vivado_path}/bin"

        # Extract version from path (simple heuristic)
        self.vivado_version: str = self._extract_version_from_path(vivado_path)

        # Validate paths
        self._validate_vivado_installation()

    def _extract_version_from_path(self, path: str) -> str:
        """Extract Vivado version from installation path."""
        # Look for version pattern like /tools/Xilinx/2025.1/Vivado
        import re

        version_match = re.search(r"(\d{4}\.\d+)", path)
        if version_match:
            return version_match.group(1)
        return "unknown"

    def _validate_vivado_installation(self) -> None:
        """Validate that Vivado installation exists and is accessible."""
        vivado_exe = Path(self.vivado_executable)
        if not vivado_exe.exists():
            raise VivadoIntegrationError(
                f"Vivado executable not found at: {self.vivado_executable}"
            )

        if not vivado_exe.is_file():
            raise VivadoIntegrationError(
                f"Vivado path exists but is not a file: {self.vivado_executable}"
            )

        self.logger.info(f"Validated Vivado installation: {self.vivado_executable}")
        self.logger.info(f"Vivado version: {self.vivado_version}")

    def run(self) -> None:
        """
        Hand-off to Vivado in batch mode using the generated scripts.

        Raises:
            VivadoIntegrationError: If Vivado integration fails
        """
        self.logger.info(f"Starting Vivado build for board: {self.board}")
        self.logger.info(f"Output directory: {self.output_dir}")

        try:
            from . import (
                integrate_pcileech_build,
                run_vivado_with_error_reporting,
            )
        except ImportError as e:
            raise VivadoIntegrationError("Vivado handling modules not available") from e

        try:
            # Use integrated build if available
            build_script = integrate_pcileech_build(
                self.board,
                self.output_dir,
                device_config=self.device_config,
            )
            self.logger.info(f"Using integrated build script: {build_script}")
            build_tcl = build_script
        except Exception as e:
            self.logger.warning(
                f"Failed to use integrated build, falling back to generated scripts: {e}"
            )
            build_tcl = self.output_dir / "vivado_build.tcl"

            # Ensure fallback script exists
            if not build_tcl.exists():
                raise VivadoIntegrationError(
                    f"No build script found at {build_tcl}. "
                    "Run the build generation step first."
                )

        # Execute Vivado with comprehensive error reporting
        return_code, report = run_vivado_with_error_reporting(
            build_tcl,
            self.output_dir,
            self.vivado_executable,
        )

        if return_code != 0:
            raise VivadoIntegrationError(
                f"Vivado build failed with return code {return_code}. "
                f"See error report: {report}"
            )

        self.logger.info("Vivado implementation finished successfully ✓")

    def get_vivado_info(self) -> Dict[str, str]:
        """Get information about the Vivado installation.

        Returns:
            Dictionary with Vivado installation details
        """
        return {
            "executable": self.vivado_executable,
            "bin_dir": self.vivado_bin_dir,
            "version": self.vivado_version,
            "installation_path": self.vivado_path,
        }

    def check_license(self) -> bool:
        """Check if Vivado license is available (basic check).

        Returns:
            True if license check passes, False otherwise
        """
        try:
            import subprocess

            result = subprocess.run(
                [self.vivado_executable, "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                self.logger.info("Vivado license check: PASSED")
                return True
            else:
                self.logger.warning("Vivado license check: FAILED")
                return False

        except Exception as e:
            self.logger.error(f"License check failed: {e}")
            return False


def create_vivado_runner(
    board: str,
    output_dir: Path,
    vivado_path: str,
    device_config: Optional[Dict[str, Any]] = None,
    logger: Optional[logging.Logger] = None,
) -> VivadoRunner:
    """Factory function to create a VivadoRunner instance.

    Args:
        board: Target board name
        output_dir: Output directory for build artifacts
        vivado_path: Path to Vivado installation
        device_config: Optional device configuration
        logger: Optional logger instance

    Returns:
        Configured VivadoRunner instance
    """
    return VivadoRunner(
        board=board,
        output_dir=output_dir,
        vivado_path=vivado_path,
        device_config=device_config,
        logger=logger,
    )
