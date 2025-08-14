"""
Default implementations of the protocol interfaces.

This module provides concrete implementations of the protocol interfaces
defined in protocols.py. These implementations are used as defaults when
no custom implementation is provided via dependency injection.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, cast

from src.tui.core.protocols import (
    BuildOrchestrator,
    ConfigManager,
    DeviceManager,
    DeviceScanner,
    NotificationManager,
    UICoordinator,
)
from src.tui.models.device import PCIDevice
from src.tui.models.config import BuildConfiguration

# Set up logging
logger = logging.getLogger(__name__)


class DefaultDeviceScanner:
    """Default implementation of the DeviceScanner protocol."""

    async def scan_devices(self) -> List[PCIDevice]:
        """
        Scan for available PCI devices.

        Returns:
            A list of PCIDevice objects representing discovered devices.
        """
        # In a real implementation, this would scan for real devices
        logger.info("Scanning for PCI devices...")

        # For now, return a dummy device for testing
        return [
            PCIDevice(
                id="0000:00:00.0",
                vendor_id="8086",
                device_id="1234",
                name="Test Device",
                class_id="0300",
                class_name="VGA Compatible Controller",
                is_supported=True,
            )
        ]


class DefaultDeviceManager:
    """Default implementation of the DeviceManager protocol."""

    async def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific device.

        Args:
            device_id: ID of the device.

        Returns:
            A dictionary containing device information, or None if the device is not found.
        """
        logger.info(f"Getting device info for {device_id}")

        # Return dummy device info
        return {
            "id": device_id,
            "vendor_id": "8086",
            "device_id": "1234",
            "name": "Test Device",
            "class_id": "0300",
            "class_name": "VGA Compatible Controller",
            "is_supported": True,
        }

    async def select_device(self, device_id: str) -> bool:
        """
        Select a device for further operations.

        Args:
            device_id: ID of the device to select.

        Returns:
            True if the device was selected successfully, False otherwise.
        """
        logger.info(f"Selecting device {device_id}")
        return True


class DefaultConfigManager:
    """Default implementation of the ConfigManager protocol."""

    async def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load a configuration from the given path.

        Args:
            config_path: Path to the configuration file or configuration name.

        Returns:
            A dictionary containing the configuration data.
        """
        logger.info(f"Loading configuration from {config_path}")

        # Return a default configuration
        return BuildConfiguration(
            name="Default Configuration",
            device_id="0000:00:00.0",
            board_type="default",
        )

    async def save_config(self, config_path: str, config_data: Dict[str, Any]) -> bool:
        """
        Save a configuration to the given path.

        Args:
            config_path: Path to the configuration file.
            config_data: Configuration data to save.

        Returns:
            True if the save was successful, False otherwise.
        """
        logger.info(f"Saving configuration to {config_path}")
        return True


class DefaultBuildOrchestrator:
    """Default implementation of the BuildOrchestrator protocol."""

    async def start_build(self, config: Dict[str, Any]) -> bool:
        """
        Start a build with the given configuration.

        Args:
            config: Build configuration.

        Returns:
            True if the build was started successfully, False otherwise.
        """
        logger.info(f"Starting build with configuration: {config}")
        return True

    async def get_build_status(self) -> Dict[str, Any]:
        """
        Get the current build status.

        Returns:
            A dictionary containing build status information.
        """
        logger.info("Getting build status")

        # Return a dummy status
        return {
            "status": "running",
            "progress": 50,
            "message": "Building firmware...",
        }

    async def cancel_build(self) -> bool:
        """
        Cancel the current build.

        Returns:
            True if the build was cancelled successfully, False otherwise.
        """
        logger.info("Cancelling build")
        return True


class DefaultUICoordinator:
    """Default implementation of the UICoordinator protocol."""

    def __init__(self, app: NotificationManager):
        """
        Initialize the DefaultUICoordinator.

        Args:
            app: The application instance.
        """
        self.app = app

    async def refresh(self) -> None:
        """Refresh the UI."""
        logger.info("Refreshing UI")

    async def show_screen(self, screen_name: str, **kwargs) -> None:
        """
        Show a specific screen.

        Args:
            screen_name: Name of the screen to show.
            **kwargs: Additional arguments to pass to the screen.
        """
        logger.info(f"Showing screen {screen_name} with args: {kwargs}")

    def exit(self) -> None:
        """Exit the application."""
        logger.info("Exiting application")
