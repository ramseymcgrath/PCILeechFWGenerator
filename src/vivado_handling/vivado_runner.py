#!/usr/bin/env python3
"""
VivadoRunner: Simplified Vivado Integration

A streamlined class that handles Vivado execution with minimal overhead,
designed to replace the complex container-based approach.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional


# Define error class here to avoid cyclic import with src.build
class VivadoIntegrationError(Exception):
    """Exception raised when Vivado integration fails."""

    pass


# Import logger utility function
def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


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

    def _extract_version_from_path(self, path: str) -> str:
        """Extract Vivado version from installation path."""
        # Look for version pattern like /tools/Xilinx/2025.1/Vivado
        import re

        version_match = re.search(r"(\d{4}\.\d+)", path)
        if version_match:
            return version_match.group(1)
        return "unknown"

    def _is_running_in_container(self) -> bool:
        """Check if we're running inside a container."""
        # Check for common container indicators
        container_indicators = [
            "/.dockerenv",
            "/run/.containerenv",
        ]

        for indicator in container_indicators:
            if Path(indicator).exists():
                return True

        # Check /proc/1/environ for container=podman
        try:
            with open("/proc/1/environ", "rb") as f:
                environ = f.read().decode("utf-8", errors="ignore")
                if "container=podman" in environ or "container=docker" in environ:
                    return True
        except (OSError, IOError):
            pass

        return False

    def _run_vivado_on_host(self) -> None:
        """Drop out of container and run Vivado on the host system."""
        import os
        import subprocess

        self.logger.info("Dropping out of container to run Vivado on host")

        # Prepare the host command to run Vivado
        # We need to tell the host where to find our files and what to run
        host_output_dir = Path("/app/output")  # This should be mounted from host
        host_vivado_path = os.environ.get(
            "HOST_VIVADO_PATH", "/tools/Xilinx/2025.1/Vivado"
        )

        # Create a script that the host can execute
        host_script = host_output_dir / "run_vivado_on_host.sh"

        script_content = f"""#!/bin/bash
set -e

echo "Running Vivado on host system"
echo "Vivado path: {host_vivado_path}"
echo "Output directory: {host_output_dir}"
echo "Board: {self.board}"

# Change to output directory
cd {host_output_dir}

# Run Vivado with the generated scripts
{host_vivado_path}/bin/vivado -mode batch -source vivado_build.tcl

echo "Vivado synthesis completed on host"
"""

        try:
            with open(host_script, "w") as f:
                f.write(script_content)

            # Make script executable (owner only)
            os.chmod(host_script, 0o700)

            self.logger.info(f"Created host execution script: {host_script}")
            self.logger.info("To complete Vivado synthesis, run this on the host:")
            self.logger.info(f"  chmod +x {host_script} && {host_script}")

            # For now, we'll exit here and let the user run Vivado manually
            # In the future, we could potentially use nsenter or similar to execute on host
            raise VivadoIntegrationError(
                "Container detected. Vivado must be run on host. "
                f"Please execute: {host_script}"
            )

        except Exception as e:
            raise VivadoIntegrationError(f"Failed to create host execution script: {e}")

    def run(self) -> None:
        """
        Hand-off to Vivado in batch mode using the generated scripts.
        If running in container, drop out to host for Vivado execution.

        Raises:
            VivadoIntegrationError: If Vivado integration fails
        """
        # Check if we're running in a container
        if self._is_running_in_container():
            self.logger.info(
                "Container detected - dropping out to host for Vivado execution"
            )
            self._run_vivado_on_host()
            return

        self.logger.info(f"Starting Vivado build for board: {self.board}")
        self.logger.info(f"Output directory: {self.output_dir}")

        # Import these functions dynamically to avoid circular dependencies
        try:
            # Delay these imports to avoid circular dependencies
            from .pcileech_build_integration import integrate_pcileech_build
            from .vivado_error_reporter import run_vivado_with_error_reporting
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
