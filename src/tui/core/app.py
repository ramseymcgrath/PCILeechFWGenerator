"""
Core PCILeech TUI application with dependency injection support.

This module provides the main PCILeech TUI application class with enhanced
testability through dependency injection and graceful degradation of features.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive

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
from src.tui.models.progress import BuildProgress
from src.tui.utils.graceful_degradation import GracefulDegradation
from src.tui.utils.search import DebouncedSearch

# Set up logging
logger = logging.getLogger(__name__)


class PCILeechTUI(App, NotificationManager):
    """Main TUI application for PCILeech firmware generation with dependency injection"""

    CSS_PATH = "styles/main.tcss"
    TITLE = "PCILeech Firmware Generator"
    SUB_TITLE = "Interactive firmware generation for PCIe devices"

    # Add keyboard bindings
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+r", "refresh_devices", "Refresh"),
        Binding("ctrl+c", "configure", "Configure"),
        Binding("ctrl+s", "start_build", "Start Build"),
        Binding("ctrl+p", "manage_profiles", "Profiles"),
        Binding("ctrl+l", "view_logs", "Logs"),
        Binding("ctrl+f", "search_filter", "Search"),
        Binding("ctrl+d", "device_details", "Details"),
        Binding("ctrl+h", "show_help", "Help"),
        Binding("f1", "show_help", "Help"),
        Binding("f5", "refresh_devices", "Refresh"),
    ]

    # Reactive attributes
    selected_device: reactive[Optional[PCIDevice]] = reactive(None)
    current_config: reactive[BuildConfiguration] = reactive(BuildConfiguration())
    build_progress: reactive[Optional[BuildProgress]] = reactive(None)
    device_filters: reactive[Dict[str, Any]] = reactive({})

    def __init__(
        self,
        *,
        device_scanner: Optional[DeviceScanner] = None,
        device_manager: Optional[DeviceManager] = None,
        config_manager: Optional[ConfigManager] = None,
        build_orchestrator: Optional[BuildOrchestrator] = None,
        ui_coordinator: Optional[UICoordinator] = None,
    ):
        """
        Initialize the PCILeech TUI application with dependency injection.

        Args:
            device_scanner: Component for scanning PCI devices.
            device_manager: Component for managing PCI devices.
            config_manager: Component for managing configuration.
            build_orchestrator: Component for orchestrating builds.
            ui_coordinator: Component for coordinating the UI.
        """
        # Initialize Textual app first to set up reactive system
        super().__init__()

        # Initialize dependencies with provided instances or defaults
        from src.tui.core.default_implementations import (
            DefaultDeviceScanner,
            DefaultDeviceManager,
            DefaultConfigManager,
            DefaultBuildOrchestrator,
            DefaultUICoordinator,
        )

        # Initialize with injected or default implementations
        self.device_scanner = device_scanner or DefaultDeviceScanner()
        self.device_manager = device_manager or DefaultDeviceManager()
        self.config_manager = config_manager or DefaultConfigManager()
        self.build_orchestrator = build_orchestrator or DefaultBuildOrchestrator()
        self.ui_coordinator = ui_coordinator or DefaultUICoordinator(self)

        # Initialize graceful degradation
        self.graceful = GracefulDegradation(self)

        # Performance optimizations
        self.debounced_search = DebouncedSearch(delay=0.3)

        # System state
        self._system_status = {}
        self._build_history = []

        # Initialize app state with default config
        initial_config = self.config_manager.load_config("default")
        self.current_config = initial_config

    # Keyboard action handlers
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()

    async def action_refresh_devices(self) -> None:
        """Refresh device list"""
        await self.graceful.try_feature("device_scanning", self._scan_devices)

    async def _scan_devices(self) -> List[PCIDevice]:
        """Scan for available devices using the device scanner."""
        devices = await self.device_scanner.scan_devices()
        self.app.notify(f"Found {len(devices)} devices", severity="info")
        return devices

    async def action_configure(self) -> None:
        """Open configuration dialog"""
        await self.graceful.try_feature(
            "configuration", self._open_configuration_dialog
        )

    async def _open_configuration_dialog(self) -> None:
        """Open the configuration dialog."""
        # Implementation would go here
        pass

    async def action_start_build(self) -> None:
        """Start build process"""
        await self.graceful.try_feature("build_start", self._handle_build_start)

    async def _handle_build_start(self) -> bool:
        """Start the build process."""
        if not self.selected_device:
            self.notify("No device selected", severity="error")
            return False

        return await self.build_orchestrator.start_build(self.current_config)

    async def action_manage_profiles(self) -> None:
        """Open profile manager"""
        await self.graceful.try_feature(
            "profile_management", self._open_profile_manager
        )

    async def _open_profile_manager(self) -> None:
        """Open the profile manager."""
        # Implementation would go here
        pass

    async def action_view_logs(self) -> None:
        """Open build logs"""
        await self.graceful.try_feature("log_viewing", self._open_build_logs)

    async def _open_build_logs(self) -> None:
        """Open the build logs."""
        # Implementation would go here
        pass

    async def action_search_filter(self) -> None:
        """Open search/filter dialog"""
        await self.graceful.try_feature("search_filter", self._open_search_filter)

    async def _open_search_filter(self) -> None:
        """Open the search/filter dialog."""
        # Implementation would go here
        pass

    async def action_device_details(self) -> None:
        """Show device details"""
        if self.selected_device:
            await self.graceful.try_feature(
                "device_details", self._show_device_details, self.selected_device
            )

    async def _show_device_details(self, device: PCIDevice) -> None:
        """Show details for a specific device."""
        # Implementation would go here
        pass

    async def action_show_help(self) -> None:
        """Show help information"""
        await self.graceful.try_feature("help_display", self._show_help)

    async def _show_help(self) -> None:
        """Show the help information."""
        # Implementation would go here
        pass

    def compose(self) -> ComposeResult:
        """Create the main UI layout"""
        # Implementation would go here
        yield from []

    def notify(self, message: str, severity: str = "info") -> None:
        """
        Show a notification to the user.

        Args:
            message: Notification message.
            severity: Severity level of the notification ("info", "warning", "error").
        """
        logger.log(
            (
                logging.ERROR
                if severity == "error"
                else logging.WARNING if severity == "warning" else logging.INFO
            ),
            message,
        )
        # In a real implementation, this would display a notification in the UI
        # self.notify(message, severity=severity)
