"""
Device-Related Commands

This module contains commands for device operations like scanning and selecting devices.
"""

from typing import List, Optional

from ..core.device_manager import DeviceManager
from ..models.device import PCIDevice
from .command import Command


class ScanDevicesCommand(Command):
    """Command to scan for available PCI devices."""

    def __init__(self, app, device_manager: DeviceManager) -> None:
        """
        Initialize the scan devices command.

        Args:
            app: The main application instance
            device_manager: The device manager service
        """
        self.app = app
        self.device_manager = device_manager
        self.previous_devices: List[PCIDevice] = []

    async def execute(self) -> bool:
        """
        Execute the scan devices command.

        Returns:
            bool: True if devices were scanned successfully
        """
        try:
            # Store current devices for undo
            self.previous_devices = self.app.devices.copy()

            # Scan for devices
            devices = await self.device_manager.scan_devices()

            # Update app state
            self.app.app_state.set_devices(devices)

            # Refresh UI
            self.app.ui_coordinator.apply_device_filters()
            self.app.ui_coordinator.update_device_table()

            return True
        except Exception as e:
            if hasattr(self.app, "error_handler"):
                self.app.error_handler.handle_operation_error("scanning devices", e)
            else:
                self.app.notify(f"Failed to scan devices: {e}", severity="error")
            return False

    async def undo(self) -> bool:
        """
        Undo the scan devices command by restoring the previous device list.

        Returns:
            bool: True if the previous device list was restored successfully
        """
        try:
            # Restore previous devices
            self.app.app_state.set_devices(self.previous_devices)

            # Refresh UI
            self.app.ui_coordinator.apply_device_filters()
            self.app.ui_coordinator.update_device_table()

            return True
        except Exception as e:
            if hasattr(self.app, "error_handler"):
                self.app.error_handler.handle_operation_error(
                    "restoring device list", e
                )
            else:
                self.app.notify(f"Failed to restore device list: {e}", severity="error")
            return False


class SelectDeviceCommand(Command):
    """Command to select a device."""

    def __init__(self, app, device: PCIDevice) -> None:
        """
        Initialize the select device command.

        Args:
            app: The main application instance
            device: The device to select
        """
        self.app = app
        self.device = device
        self.previous_device: Optional[PCIDevice] = None

    async def execute(self) -> bool:
        """
        Execute the select device command.

        Returns:
            bool: True if the device was selected successfully
        """
        try:
            # Store current selected device for undo
            self.previous_device = self.app.selected_device

            # Update app state
            self.app.app_state.set_selected_device(self.device)

            # Update UI
            await self.app.ui_coordinator.handle_device_selection(self.device)

            return True
        except Exception as e:
            if hasattr(self.app, "error_handler"):
                self.app.error_handler.handle_operation_error("selecting device", e)
            else:
                self.app.notify(f"Failed to select device: {e}", severity="error")
            return False

    async def undo(self) -> bool:
        """
        Undo the select device command by restoring the previously selected device.

        Returns:
            bool: True if the previous selection was restored successfully
        """
        try:
            # Restore previous device selection
            self.app.app_state.set_selected_device(self.previous_device)

            # Update UI
            if self.previous_device:
                await self.app.ui_coordinator.handle_device_selection(
                    self.previous_device
                )
            else:
                self.app.ui_coordinator.clear_compatibility_display()

            return True
        except Exception as e:
            if hasattr(self.app, "error_handler"):
                self.app.error_handler.handle_operation_error(
                    "restoring device selection", e
                )
            else:
                self.app.notify(
                    f"Failed to restore device selection: {e}", severity="error"
                )
            return False
