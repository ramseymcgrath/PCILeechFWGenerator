"""
Device-related Commands

This module contains command implementations for device-related actions.
"""

from typing import TYPE_CHECKING, List, Optional, cast

from .command import Command

if TYPE_CHECKING:
    from ...tui.models.device import PCIDevice
    from ..main import PCILeechTUI


class ScanDevicesCommand(Command):
    """Command to scan and refresh available PCI devices."""

    def __init__(self, app: "PCILeechTUI") -> None:
        """
        Initialize the command.

        Args:
            app: The main TUI application instance
        """
        self.app = app
        self._previous_devices: List["PCIDevice"] = []
        self._previous_selected: Optional["PCIDevice"] = None

    async def execute(self) -> bool:
        """
        Scan for available PCI devices and update the UI.

        Returns:
            bool: True if devices were scanned successfully, False otherwise.
        """
        try:
            # Store previous state for potential undo
            self._previous_devices = self.app.ui_state.devices.copy()
            self._previous_selected = self.app.selected_device

            # Notify user about the scan
            self.app.notify("Scanning for PCI devices...", severity="information")

            # Call the device manager to scan devices
            devices = await self.app.device_manager.scan_devices()

            if devices is not None:
                # Update UI state
                self.app.ui_state.devices = devices
                self.app.ui_state.filtered_devices = devices.copy()

                # Apply any existing filters
                self.app._apply_device_filters()

                # Update UI elements
                self.app._update_device_table()

                # Select the first device if none selected
                if not self.app.selected_device and devices:
                    self.app.selected_device = devices[0]

                self.app.notify(f"Found {len(devices)} PCI devices", severity="success")
                return True

            self.app.notify("No devices found", severity="warning")
            return False
        except Exception as e:
            self.app.notify(f"Failed to scan devices: {e}", severity="error")
            return False

    async def undo(self) -> bool:
        """
        Restore previous device list and selection.

        Returns:
            bool: True if the previous state was restored, False otherwise.
        """
        try:
            # Restore previous devices list
            self.app.ui_state.devices = self._previous_devices
            self.app.ui_state.filtered_devices = self._previous_devices.copy()

            # Apply any existing filters
            self.app._apply_device_filters()

            # Update UI elements
            self.app._update_device_table()

            # Restore previous selection
            self.app.selected_device = self._previous_selected

            self.app.notify("Restored previous device list", severity="information")
            return True
        except Exception as e:
            self.app.notify(
                f"Failed to restore previous devices: {e}", severity="error"
            )
            return False
