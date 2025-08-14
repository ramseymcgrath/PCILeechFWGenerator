"""
Main TUI Application

The main entry point for the PCILeech Firmware Generator TUI.
"""

import asyncio
import json
import subprocess
import webbrowser
# Define UI state with comprehensive type hints
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import (Button, DataTable, Footer, Header, Input, Label,
                             ProgressBar, RichLog, Select, Static, Switch,
                             TabbedContent, TabPane)

# Import core components
from ..tui.core.background_monitor import BackgroundMonitor
from ..tui.core.build_orchestrator import BuildOrchestrator
from ..tui.core.config_manager import ConfigManager
from ..tui.core.device_manager import DeviceManager
from ..tui.core.error_handler import ErrorHandler
from ..tui.core.status_monitor import StatusMonitor
from ..tui.core.ui_coordinator import UICoordinator
# Import data models
from ..tui.models.config import BuildConfiguration
from ..tui.models.device import PCIDevice
from ..tui.models.progress import BuildProgress
from ..tui.utils.debounced_search import DebouncedSearch
from .commands.build_commands import StartBuildCommand, StopBuildCommand
# Import commands
from .commands.command import Command, CommandManager
from .commands.device_commands import ScanDevicesCommand
from .dialogs.build_logs import BuildLogDialog
from .dialogs.configuration import ConfigurationDialog
from .dialogs.confirmation import ConfirmationDialog
# Import dialog screens
from .dialogs.device_details import DeviceDetailsDialog
from .dialogs.file_path_input import FilePathInputDialog
from .dialogs.profile_manager import ProfileManagerDialog
from .dialogs.search_filter import SearchFilterDialog
# Import widgets
from .widgets.device_table import VirtualDeviceTable
from .widgets.status_panel import StatusPanel


@dataclass
class UIState:
    """State container for the TUI application."""

    selected_device: Optional[PCIDevice] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    build_in_progress: bool = False
    config: BuildConfiguration = field(default_factory=BuildConfiguration)
    devices: List[PCIDevice] = field(default_factory=list)
    filtered_devices: List[PCIDevice] = field(default_factory=list)
    system_status: Dict[str, Any] = field(default_factory=dict)
    build_history: List[Dict[str, Any]] = field(default_factory=list)


class PCILeechTUI(App[None]):
    """Main TUI application for PCILeech firmware generation"""

    CSS_PATH = "../tui/styles/main.tcss"
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

    # Type hints for dependency-injected services
    device_manager: DeviceManager
    config_manager: ConfigManager
    build_orchestrator: BuildOrchestrator
    status_monitor: StatusMonitor
    error_handler: ErrorHandler
    ui_coordinator: UICoordinator
    background_monitor: BackgroundMonitor
    command_manager: CommandManager

    def __init__(self) -> None:
        # Initialize Textual app first to set up reactive system
        super().__init__()

        # Core services
        self.device_manager = DeviceManager()
        self.config_manager = ConfigManager()
        self.build_orchestrator = BuildOrchestrator()
        self.status_monitor = StatusMonitor()
        self.background_monitor = BackgroundMonitor(self)
        self.command_manager = CommandManager()

        # Performance optimizations
        self.debounced_search = DebouncedSearch(delay=0.3)

        # UI state
        self.ui_state = UIState()

        # Initialize current_config from config manager
        # This must be done after super().__init__() to avoid ReactiveError
        self.current_config = self.config_manager.get_current_config()

    # Keyboard action handlers
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()

    async def action_refresh_devices(self) -> None:
        """Refresh device list"""
        command = ScanDevicesCommand(self)
        await self.command_manager.execute(command)

    async def action_configure(self) -> None:
        """Open configuration dialog"""
        await self._open_configuration_dialog()

    async def action_start_build(self) -> None:
        """Start build process"""
        if self.selected_device and not self.ui_state.build_in_progress:
            command = StartBuildCommand(self, self.selected_device, self.current_config)
            await self.command_manager.execute(command)

    async def action_manage_profiles(self) -> None:
        """Open profile manager"""
        await self._open_profile_manager()

    async def action_view_logs(self) -> None:
        """Open build logs"""
        await self._open_build_logs()

    async def action_search_filter(self) -> None:
        """Open search/filter dialog"""
        await self._open_search_filter()

    async def action_device_details(self) -> None:
        """Show device details"""
        if self.selected_device:
            await self._show_device_details(self.selected_device)

    async def action_show_help(self) -> None:
        """Show help information"""
        await self._show_help()

    def compose(self) -> ComposeResult:
        """Create the main UI layout"""
        yield Header()

        with Container(id="main-container"):
            with Horizontal(id="top-section"):
                # Device Selection Panel
                with Vertical(id="device-panel", classes="panel"):
                    yield Static("📡 PCIe Device Selection", classes="panel-title")

                    # Add search bar
                    with Horizontal(classes="search-bar"):
                        yield Input(
                            placeholder="Search devices... (debounced)",
                            id="quick-search",
                        )
                        yield Button("🔍", id="advanced-search", variant="primary")

                    yield VirtualDeviceTable(id="device-table")
                    with Horizontal(classes="button-row"):
                        yield Button("Refresh", id="refresh-devices", variant="primary")
                        yield Button("Details", id="device-details", disabled=True)
                        yield Button(
                            "Export List", id="export-devices", variant="default"
                        )

                # Configuration Panel
                with Vertical(id="config-panel", classes="panel"):
                    yield Static("⚙️ Build Configuration", classes="panel-title")
                    yield Static("Board Type: 75t", id="board-type")
                    yield Static("Advanced Features: Enabled", id="advanced-features")
                    yield Static("Build Mode: Standard", id="build-mode")
                    with Horizontal(classes="button-row"):
                        yield Button("Configure", id="configure", variant="primary")
                        yield Button("Profiles", id="manage-profiles")
                        yield Button("Load Profile", id="load-profile")
                        yield Button("Save Profile", id="save-profile")

                # Compatibility Panel
                with Vertical(id="compatibility-panel", classes="panel"):
                    yield Static("🔄 Compatibility Factors", classes="panel-title")
                    yield Static(
                        "Select a device to view compatibility factors",
                        id="compatibility-title",
                    )
                    yield Static("", id="compatibility-score")
                    yield DataTable(id="compatibility-table")

            with Horizontal(id="middle-section"):
                # Build Progress Panel
                with Vertical(id="build-panel", classes="panel"):
                    yield Static("🔨 Build Progress", classes="panel-title")
                    yield Static("Status: Ready to Build", id="build-status")
                    yield ProgressBar(total=100, id="build-progress")
                    yield Static("Progress: 0% (0/6 stages)", id="progress-text")
                    yield Static(
                        "Resources: CPU: 0% | Memory: 0GB | Disk: 0GB free",
                        id="resource-usage",
                    )
                    with Horizontal(classes="button-row"):
                        yield Button(
                            "▶ Start Build",
                            id="start-build",
                            variant="success",
                            disabled=True,
                        )
                        yield Button("⏸ Pause", id="pause-build", disabled=True)
                        yield Button("⏹ Stop", id="stop-build", disabled=True)
                        yield Button("📋 View Logs", id="view-logs")

            with Horizontal(id="bottom-section"):
                # System Status Panel
                yield StatusPanel(id="status-panel")

                # Quick Actions Panel
                with Vertical(id="actions-panel", classes="panel"):
                    yield Static("🚀 Quick Actions", classes="panel-title")
                    yield Button(
                        "🔍 Scan Devices", id="scan-devices", variant="primary"
                    )
                    yield Button("📁 Open Output Dir", id="open-output")
                    yield Button("📊 View Last Build Report", id="view-report")
                    yield Button("🧩 Check Donor Module", id="check-donor-module")
                    yield Button(
                        "🎯 Enable Donor Dump",
                        id="enable-donor-dump",
                        variant="success",
                    )
                    yield Button(
                        "📝 Generate Donor Template",
                        id="generate-donor-template",
                        variant="primary",
                    )
                    yield Button("⚙️ Advanced Settings", id="advanced-settings")
                    yield Button("📖 Documentation", id="documentation")
                    yield Button("💾 Backup Config", id="backup-config")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application"""
        try:
            # Set up the device table
            device_table = self.query_one("#device-table", VirtualDeviceTable)

            # Set up quick search
            search_input = self.query_one("#quick-search", Input)
            search_input.placeholder = "Type to filter devices..."

            # Start background tasks
            self.call_after_refresh(self._initialize_app)
        except Exception as e:
            # Handle initialization errors gracefully for tests
            print(f"Warning: Failed to initialize TUI: {e}")

    async def _initialize_app(self) -> None:
        """Initialize the application with data"""
        # Load default configuration profiles with error handling
        success = self.config_manager.create_default_profiles()
        if not success:
            self.notify(
                "Warning: Failed to create default profiles", severity="warning"
            )

            # No longer have error object with suggested actions
            self.notify(
                "Check configuration directory permissions", severity="information"
            )

        # Start system status monitoring using the optimized background monitor
        self.background_monitor.start_monitoring()

        # Initial device scan
        scan_command = ScanDevicesCommand(self)
        await self.command_manager.execute(scan_command)

        # Update UI with current config
        self._update_config_display()

        # Show welcome message with keyboard shortcuts
        self.notify(
            "Welcome! Press F1 or Ctrl+H for help, Ctrl+Q to quit", severity="info"
        )

    # Input event handlers
    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for real-time search using DebouncedSearch"""
        if event.input.id == "quick-search":
            # Use the debounced search implementation for improved performance
            search_query = event.input.value
            await self.debounced_search.search(search_query, self._perform_search)

    async def _perform_search(self, query: str) -> None:
        """Callback for debounced search to perform the actual search operation"""
        self.ui_coordinator.apply_device_filters()
        self.ui_coordinator.update_device_table()

    # Basic dialog methods that we'll keep in the main class
    async def _open_profile_manager(self) -> None:
        """Open the profile manager dialog"""
        try:
            result = await self.push_screen(ProfileManagerDialog(self.config_manager))
            if result:
                # Load the selected profile
                config = self.config_manager.load_profile(result)
                if config:
                    self.current_config = config
                    self.config_manager.set_current_config(config)
                    self._update_config_display()
                    self.notify(f"Loaded profile: {result}", severity="success")
        except Exception as e:
            self.notify(f"Failed to open profile manager: {e}", severity="error")

    async def _open_search_filter(self) -> None:
        """Open the search/filter dialog"""
        try:
            result = await self.push_screen(SearchFilterDialog())
            if result:
                self.device_filters = result
                self._apply_device_filters()
                self._update_device_table()
                self.notify("Filters applied", severity="success")
        except Exception as e:
            self.notify(f"Failed to open search dialog: {e}", severity="error")

    async def _show_device_details(self, device: PCIDevice) -> None:
        """Show detailed device information"""
        try:
            await self.push_screen(DeviceDetailsDialog(device))
        except Exception as e:
            self.notify(f"Failed to show device details: {e}", severity="error")

    async def _open_build_logs(self) -> None:
        """Open the build logs dialog"""
        try:
            await self.push_screen(BuildLogDialog(self.build_orchestrator))
        except Exception as e:
            self.notify(f"Failed to open build logs: {e}", severity="error")

    async def _open_configuration_dialog(self) -> None:
        """Open the configuration dialog"""
        try:
            result = await self.push_screen(ConfigurationDialog(self.current_config))
            if result:
                self.current_config = result
                self.config_manager.set_current_config(result)
                self._update_config_display()
                self.notify("Configuration updated", severity="success")
        except Exception as e:
            self.notify(f"Failed to open configuration dialog: {e}", severity="error")

    # Other UI utility methods
    def _update_config_display(self) -> None:
        """Update the configuration display in the UI"""
        try:
            self.query_one("#board-type", Static).update(
                f"Board Type: {self.current_config.board_type}"
            )
            self.query_one("#advanced-features", Static).update(
                f"Features: {self.current_config.feature_summary[:50]}..."
                if len(self.current_config.feature_summary) > 50
                else f"Features: {self.current_config.feature_summary}"
            )
            self.query_one("#build-mode", Static).update(
                f"Mode: {'Advanced' if self.current_config.is_advanced else 'Standard'}"
            )
        except Exception as e:
            self.notify(f"Failed to update config display: {e}", severity="error")

    def _update_device_table(self) -> None:
        """Update the device table in the UI"""
        try:
            device_table = self.query_one("#device-table", VirtualDeviceTable)
            device_table.update_devices(self.ui_state.filtered_devices)

            # Enable/disable buttons based on selection
            details_btn = self.query_one("#device-details", Button)
            start_build_btn = self.query_one("#start-build", Button)

            details_btn.disabled = self.selected_device is None
            start_build_btn.disabled = (
                self.selected_device is None
                or self.ui_state.build_in_progress
                or (self.selected_device and not self.selected_device.is_suitable)
            )
        except Exception as e:
            self.notify(f"Failed to update device table: {e}", severity="error")

    def _apply_device_filters(self) -> None:
        """Apply filters to the device list"""
        try:
            if not self.device_filters:
                self.ui_state.filtered_devices = self.ui_state.devices.copy()
                return

            filtered_devices = []
            search_text = self.device_filters.get("device_search", "").lower()
            class_filter = self.device_filters.get("class_filter", "all")
            status_filter = self.device_filters.get("status_filter", "all")
            min_score = float(self.device_filters.get("min_score", 0.0))

            for device in self.ui_state.devices:
                # Apply text search
                if search_text and search_text not in device.display_name.lower():
                    continue

                # Apply class filter
                if class_filter != "all" and not device.device_class.lower().startswith(
                    class_filter
                ):
                    continue

                # Apply status filter
                if status_filter == "suitable" and not device.is_suitable:
                    continue
                elif status_filter == "bound" and not device.has_driver:
                    continue
                elif status_filter == "unbound" and device.has_driver:
                    continue
                elif status_filter == "vfio" and not device.vfio_compatible:
                    continue

                # Apply score filter
                if device.suitability_score < min_score:
                    continue

                filtered_devices.append(device)

            self.ui_state.filtered_devices = filtered_devices
        except Exception as e:
            self.notify(f"Failed to apply device filters: {e}", severity="error")
            self.ui_state.filtered_devices = self.ui_state.devices.copy()

    def watch_selected_device(self, device: Optional[PCIDevice]) -> None:
        """React to device selection changes"""
        # Update device details when selection changes
        if device:
            # Update UI elements that show device details
            compatibility_title = self.query_one("#compatibility-title", Static)
            compatibility_score = self.query_one("#compatibility-score", Static)

            compatibility_title.update(f"Compatibility: {device.display_name}")
            compatibility_score.update(
                f"Score: {device.suitability_score:.2f} - "
                + ("✅ Suitable" if device.is_suitable else "❌ Not Suitable")
            )

            # Update the compatibility factors table
            factors_table = self.query_one("#compatibility-table", DataTable)
            factors_table.clear()

            if not factors_table.columns:
                factors_table.add_columns("Factor", "Impact", "Description")

            # Add rows for compatibility factors
            for factor in device.compatibility_factors:
                sign = "+" if factor["adjustment"] >= 0 else ""
                factors_table.add_row(
                    factor["name"],
                    f"{sign}{factor['adjustment']:.2f}",
                    factor["description"],
                )

            # Update button states
            self.query_one("#device-details", Button).disabled = False
            start_build_btn = self.query_one("#start-build", Button)
            start_build_btn.disabled = (
                not device.is_suitable or self.ui_state.build_in_progress
            )
        else:
            # Reset UI when no device is selected
            self.query_one("#compatibility-title", Static).update(
                "Select a device to view compatibility factors"
            )
            self.query_one("#compatibility-score", Static).update("")

            # Clear the factors table
            factors_table = self.query_one("#compatibility-table", DataTable)
            factors_table.clear()

            # Disable buttons
            self.query_one("#device-details", Button).disabled = True
            self.query_one("#start-build", Button).disabled = True
