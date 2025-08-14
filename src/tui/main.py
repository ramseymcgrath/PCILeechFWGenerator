"""
Main TUI Application

The main entry point for the PCILeech Firmware Generator TUI.
"""

import asyncio
import json
import subprocess
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    RichLog,
    Select,
    Static,
    Switch,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)

from .core.background_monitor import BackgroundMonitor
from .core.build_orchestrator import BuildOrchestrator
from .core.config_manager import ConfigManager
from .core.device_manager import DeviceManager
from .core.error_handler import ErrorHandler
from .core.status_monitor import StatusMonitor
from .core.ui_coordinator import UICoordinator
from .core.app_state import AppState
from .core.app_state import AppState
from .models.config import BuildConfiguration
from .models.device import PCIDevice
from .models.progress import BuildProgress
from .utils.debounced_search import DebouncedSearch
from .widgets.virtual_device_table import VirtualDeviceTable


class DeviceDetailsDialog(ModalScreen[bool]):
    """Modal dialog for displaying detailed device information"""

    def __init__(self, device: PCIDevice) -> None:
        """Initialize the device details dialog"""
        super().__init__()
        self.device = device

    def compose(self) -> ComposeResult:
        """Create the device details dialog layout"""
        with Container(id="device-details-dialog"):
            yield Static(f"📡 Device Details: {self.device.bdf}", id="dialog-title")

            with TabbedContent():
                with TabPane("Basic Info", id="basic-info"):
                    with VerticalScroll():
                        yield Static(f"BDF: {self.device.bdf}")
                        yield Static(
                            f"Vendor: {self.device.vendor_name} ({self.device.vendor_id})"
                        )
                        yield Static(
                            f"Device: {self.device.device_name} ({self.device.device_id})"
                        )
                        yield Static(f"Class: {self.device.device_class}")
                        yield Static(f"Driver: {self.device.driver or 'None'}")
                        yield Static(f"IOMMU Group: {self.device.iommu_group}")
                        yield Static(f"Power State: {self.device.power_state}")
                        yield Static(f"Link Speed: {self.device.link_speed}")

                with TabPane("Compatibility", id="compatibility"):
                    with VerticalScroll():
                        yield Static(
                            f"Suitability Score: {self.device.suitability_score:.2f}"
                        )
                        yield Static(
                            f"Overall Status: {'✅ Suitable' if self.device.is_suitable else '❌ Not Suitable'}"
                        )

                        if self.device.compatibility_issues:
                            yield Static("Issues:", classes="text-bold")
                            for issue in self.device.compatibility_issues:
                                yield Static(f"• {issue}", classes="status-error")

                        if self.device.compatibility_factors:
                            yield Static("Compatibility Factors:", classes="text-bold")
                            for factor in self.device.compatibility_factors:
                                sign = "+" if factor["adjustment"] >= 0 else ""
                                yield Static(
                                    f"• {factor['name']}: {sign}{factor['adjustment']:.1f} - {factor['description']}"
                                )

                with TabPane("Hardware", id="hardware"):
                    with VerticalScroll():
                        yield Static(
                            "Base Address Registers (BARs):", classes="text-bold"
                        )
                        if self.device.bars:
                            for i, bar in enumerate(self.device.bars):
                                yield Static(f"BAR{i}: {bar}")
                        else:
                            yield Static("No BAR information available")

                        yield Static("Additional Hardware Info:", classes="text-bold")
                        for key, value in self.device.detailed_status.items():
                            yield Static(f"{key}: {value}")

            # Dialog Buttons
            with Horizontal(id="dialog-buttons"):
                yield Button("Export Details", id="export-details", variant="primary")
                yield Button("Close", id="close-details", variant="default")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle dialog button presses"""
        button_id = event.button.id

        if button_id == "close-details":
            self.dismiss(False)
        elif button_id == "export-details":
            await self._export_device_details()

    async def _export_device_details(self) -> None:
        """Export device details to a JSON file"""
        try:
            output_path = Path(
                f"device_details_{self.device.bdf.replace(':', '_')}.json"
            )
            with open(output_path, "w") as f:
                json.dump(self.device.to_dict(), f, indent=2)

            self.app.notify(
                f"Device details exported to {output_path}", severity="success"
            )
        except Exception as e:
            self.app.notify(f"Failed to export device details: {e}", severity="error")


class ProfileManagerDialog(ModalScreen[Optional[str]]):
    """Modal dialog for managing configuration profiles"""

    def __init__(self, config_manager) -> None:
        """Initialize the profile manager dialog"""
        super().__init__()
        self.config_manager = config_manager
        self.profiles: List[Dict[str, str]] = []

    def compose(self) -> ComposeResult:
        """Create the profile manager dialog layout"""
        with Container(id="profile-manager-dialog"):
            yield Static("📋 Configuration Profiles", id="dialog-title")

            with Horizontal():
                # Profile list
                with Vertical(id="profile-list-panel"):
                    yield Static("Available Profiles:", classes="text-bold")
                    yield DataTable(id="profiles-table")

                    with Horizontal(classes="button-row"):
                        yield Button("Load", id="load-profile-btn", variant="primary")
                        yield Button("Delete", id="delete-profile-btn", variant="error")
                        yield Button("Export", id="export-profile-btn")

                # Profile details
                with Vertical(id="profile-details-panel"):
                    yield Static("Profile Details:", classes="text-bold")
                    yield Static(
                        "Select a profile to view details", id="profile-details"
                    )

                    with Horizontal(classes="button-row"):
                        yield Button(
                            "Import", id="import-profile-btn", variant="success"
                        )
                        yield Button(
                            "Create New", id="create-profile-btn", variant="primary"
                        )

            # Dialog Buttons
            with Horizontal(id="dialog-buttons"):
                yield Button("Close", id="close-profiles", variant="default")

    def on_mount(self) -> None:
        """Initialize the profile manager"""
        self._refresh_profiles()

    def _refresh_profiles(self) -> None:
        """Refresh the profiles list"""
        try:
            self.profiles = self.config_manager.list_profiles()

            # Set up table
            table = self.query_one("#profiles-table", DataTable)
            table.clear()
            if not table.columns:
                table.add_columns("Name", "Description", "Last Used")

            for profile in self.profiles:
                table.add_row(
                    profile["name"],
                    (
                        profile["description"][:50] + "..."
                        if len(profile["description"]) > 50
                        else profile["description"]
                    ),
                    profile.get("last_used", "Never")[:10],  # Show date only
                    key=profile["name"],
                )
        except Exception as e:
            self.app.notify(f"Failed to load profiles: {e}", severity="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle dialog button presses"""
        button_id = event.button.id

        if button_id == "close-profiles":
            self.dismiss(None)
        elif button_id == "load-profile-btn":
            await self._load_selected_profile()
        elif button_id == "delete-profile-btn":
            await self._delete_selected_profile()
        elif button_id == "export-profile-btn":
            await self._export_selected_profile()
        elif button_id == "import-profile-btn":
            await self._import_profile()
        elif button_id == "create-profile-btn":
            await self._create_new_profile()

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle profile selection"""
        profile_name = event.row_key
        profile_details = self.config_manager.get_profile_summary(profile_name)

        details_text = "\n".join([f"{k}: {v}" for k, v in profile_details.items()])
        self.query_one("#profile-details", Static).update(details_text)

    async def _load_selected_profile(self) -> None:
        """Load the selected profile"""
        table = self.query_one("#profiles-table", DataTable)
        if table.cursor_row is not None:
            profile_name = table.get_row_at(table.cursor_row)[0]
            self.dismiss(profile_name)

    async def _delete_selected_profile(self) -> None:
        """Delete the selected profile"""
        table = self.query_one("#profiles-table", DataTable)
        if table.cursor_row is not None:
            profile_name = table.get_row_at(table.cursor_row)[0]

            # Confirm deletion
            should_delete = await self.app.push_screen(
                ConfirmationDialog(
                    "Delete Profile",
                    f"Are you sure you want to delete '{profile_name}'?",
                )
            )

            if should_delete:
                success = self.config_manager.delete_profile(profile_name)
                if success:
                    self.app.notify(
                        f"Profile '{profile_name}' deleted", severity="success"
                    )
                    self._refresh_profiles()
                else:
                    self.app.notify(
                        f"Failed to delete profile '{profile_name}'", severity="error"
                    )

    async def _export_selected_profile(self) -> None:
        """Export the selected profile"""
        table = self.query_one("#profiles-table", DataTable)
        if table.cursor_row is not None:
            profile_name = table.get_row_at(table.cursor_row)[0]
            export_path = Path(f"{profile_name.replace(' ', '_')}_profile.json")

            success = self.config_manager.export_profile(profile_name, export_path)
            if success:
                self.app.notify(
                    f"Profile exported to {export_path}", severity="success"
                )
            else:
                self.app.notify(f"Failed to export profile", severity="error")

    async def _import_profile(self) -> None:
        """Import a profile from file"""
        # In a real implementation, this would open a file dialog
        # For now, we'll assume a standard path
        import_path = Path("imported_profile.json")
        if import_path.exists():
            profile_name = self.config_manager.import_profile(import_path)
            if profile_name:
                self.app.notify(
                    f"Profile imported as '{profile_name}'", severity="success"
                )
                self._refresh_profiles()
            else:
                self.app.notify("Failed to import profile", severity="error")
        else:
            self.app.notify(
                "Place profile file as 'imported_profile.json' to import",
                severity="info",
            )
        # Prompt user for file path using a modal dialog
        file_path = await self.app.push_screen(
            FilePathInputDialog(
                title="Import Profile",
                prompt="Enter the path to the profile file to import:",
            )
        )
        if file_path:
            import_path = Path(file_path)
            if import_path.exists():
                profile_name = self.config_manager.import_profile(import_path)
                if profile_name:
                    self.app.notify(
                        f"Profile imported as '{profile_name}'", severity="success"
                    )
                    self._refresh_profiles()
                else:
                    self.app.notify("Failed to import profile", severity="error")
            else:
                self.app.notify(
                    f"File '{import_path}' does not exist", severity="error"
                )
        else:
            self.app.notify("Import cancelled", severity="info")

    async def _create_new_profile(self) -> None:
        """Create a new profile from current configuration"""
        # This would open the configuration dialog in "save new" mode
        self.app.notify(
            "Create new profile functionality - use main Configure button",
            severity="info",
        )


class BuildLogDialog(ModalScreen[bool]):
    """Modal dialog for displaying build logs and history"""

    def __init__(self, build_orchestrator) -> None:
        """Initialize the build log dialog"""
        super().__init__()
        self.build_orchestrator = build_orchestrator

    def compose(self) -> ComposeResult:
        """Create the build log dialog layout"""
        with Container(id="build-log-dialog"):
            yield Static("📋 Build Logs & History", id="dialog-title")

            with TabbedContent():
                with TabPane("Current Build", id="current-build"):
                    yield RichLog(id="current-build-log", auto_scroll=True)

                    with Horizontal(classes="button-row"):
                        yield Button("Refresh", id="refresh-current", variant="primary")
                        yield Button(
                            "Export Log", id="export-current", variant="default"
                        )

                with TabPane("Build History", id="build-history"):
                    yield DataTable(id="build-history-table")

                    with Horizontal(classes="button-row"):
                        yield Button(
                            "View Details", id="view-build-details", variant="primary"
                        )
                        yield Button(
                            "Export History", id="export-history", variant="default"
                        )

                with TabPane("System Info", id="system-info"):
                    with VerticalScroll():
                        yield Static("System Information:", classes="text-bold")
                        yield Static(id="system-info-content")

            # Dialog Buttons
            with Horizontal(id="dialog-buttons"):
                yield Button("Close", id="close-logs", variant="default")

    def on_mount(self) -> None:
        """Initialize the log dialog"""
        self._refresh_current_log()
        self._refresh_build_history()
        self._refresh_system_info()

    def _refresh_current_log(self) -> None:
        """Refresh current build log"""
        try:
            log_widget = self.query_one("#current-build-log", RichLog)
            log_widget.clear()

            # Get current build logs from build orchestrator
            log_lines = self.build_orchestrator.get_current_build_log()

            for line in log_lines:
                log_widget.write(line)

        except Exception as e:
            self.app.notify(f"Failed to load current log: {e}", severity="error")

    def _refresh_build_history(self) -> None:
        """Refresh build history table"""
        try:
            table = self.query_one("#build-history-table", DataTable)
            table.clear()

            if not table.columns:
                table.add_columns("Date", "Device", "Board", "Status", "Duration")

            # Mock build history data
            history_data = [
                ("2024-01-01", "0000:01:00.0", "75t", "Success", "15m 30s"),
                ("2024-01-02", "0000:02:00.0", "35t", "Failed", "8m 15s"),
                ("2024-01-03", "0000:01:00.0", "100t", "Success", "22m 45s"),
            ]

            for row in history_data:
                table.add_row(*row)

        except Exception as e:
            self.app.notify(f"Failed to load build history: {e}", severity="error")

    def _refresh_system_info(self) -> None:
        """Refresh system information"""
        try:
            import platform

            import psutil

            info_lines = [
                f"OS: {platform.system()} {platform.release()}",
                f"Architecture: {platform.machine()}",
                f"CPU Cores: {psutil.cpu_count()}",
                f"Memory: {psutil.virtual_memory().total // (1024**3)} GB",
                f"Python: {platform.python_version()}",
            ]

            info_text = "\n".join(info_lines)
            self.query_one("#system-info-content", Static).update(info_text)

        except ImportError:
            # Fallback if psutil not available
            info_text = "System information requires psutil package"
            self.query_one("#system-info-content", Static).update(info_text)
        except Exception as e:
            self.app.notify(f"Failed to load system info: {e}", severity="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle dialog button presses"""
        button_id = event.button.id

        if button_id == "close-logs":
            self.dismiss(False)
        elif button_id == "refresh-current":
            self._refresh_current_log()
        elif button_id == "export-current":
            await self._export_current_log()
        elif button_id == "export-history":
            await self._export_build_history()

    async def _export_current_log(self) -> None:
        """Export current build log"""
        try:
            log_path = Path("current_build.log")
            with open(log_path, "w") as f:
                f.write("PCILeech Build Log\n")
                f.write("================\n\n")
                # In real implementation, get actual log content
                f.write("Build log content would be here...")

            self.app.notify(f"Log exported to {log_path}", severity="success")
        except Exception as e:
            self.app.notify(f"Failed to export log: {e}", severity="error")

    async def _export_build_history(self) -> None:
        """Export build history"""
        try:
            history_path = Path("build_history.json")
            # In real implementation, get actual history data
            history_data = {"builds": []}

            with open(history_path, "w") as f:
                json.dump(history_data, f, indent=2)

            self.app.notify(f"History exported to {history_path}", severity="success")
        except Exception as e:
            self.app.notify(f"Failed to export history: {e}", severity="error")


class SearchFilterDialog(ModalScreen[Dict[str, Any]]):
    """Modal dialog for searching and filtering devices"""

    def __init__(self) -> None:
        """Initialize the search/filter dialog"""
        super().__init__()

    def compose(self) -> ComposeResult:
        """Create the search/filter dialog layout"""
        with Container(id="search-filter-dialog"):
            yield Static("🔍 Search & Filter Devices", id="dialog-title")

            with Vertical(id="search-form"):
                # Search criteria
                yield Label("Search by Device Name:")
                yield Input(
                    placeholder="Enter device name or vendor", id="device-search"
                )

                yield Label("Filter by Class:")
                yield Select(
                    [
                        ("all", "All Classes"),
                        ("network", "Network"),
                        ("storage", "Storage"),
                        ("display", "Display"),
                        ("multimedia", "Multimedia"),
                        ("bridge", "Bridge"),
                        ("other", "Other"),
                    ],
                    value="all",
                    id="class-filter",
                )

                yield Label("Filter by Status:")
                yield Select(
                    [
                        ("all", "All Devices"),
                        ("suitable", "Suitable Only"),
                        ("bound", "Driver Bound"),
                        ("unbound", "No Driver"),
                        ("vfio", "VFIO Compatible"),
                    ],
                    value="all",
                    id="status-filter",
                )

                yield Label("Minimum Suitability Score:")
                yield Input(placeholder="0.0 - 1.0", value="0.0", id="score-filter")

            # Dialog Buttons
            with Horizontal(id="dialog-buttons"):
                yield Button("Clear", id="clear-filters", variant="default")
                yield Button("Apply", id="apply-filters", variant="primary")
                yield Button("Cancel", id="cancel-search", variant="default")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle dialog button presses"""
        button_id = event.button.id

        if button_id == "cancel-search":
            self.dismiss(None)
        elif button_id == "clear-filters":
            self._clear_all_filters()
        elif button_id == "apply-filters":
            filters = self._get_filter_criteria()
            self.dismiss(filters)

    def _clear_all_filters(self) -> None:
        """Clear all filter inputs"""
        self.query_one("#device-search", Input).value = ""
        self.query_one("#class-filter", Select).value = "all"
        self.query_one("#status-filter", Select).value = "all"
        self.query_one("#score-filter", Input).value = "0.0"

    def _get_filter_criteria(self) -> Dict[str, Any]:
        """Get current filter criteria"""
        try:
            score_text = self.query_one("#score-filter", Input).value
            min_score = float(score_text) if score_text else 0.0
        except ValueError:
            min_score = 0.0

        return {
            "device_search": self.query_one("#device-search", Input).value,
            "class_filter": self.query_one("#class-filter", Select).value,
            "status_filter": self.query_one("#status-filter", Select).value,
            "min_score": min_score,
        }


class ConfirmationDialog(ModalScreen[bool]):
    """Modal dialog for confirming actions with warnings"""

    def __init__(self, title: str, message: str) -> None:
        """Initialize the confirmation dialog with a title and message"""
        super().__init__()
        self.title = title
        self.message = message

    def compose(self) -> ComposeResult:
        """Create the confirmation dialog layout"""
        with Container(id="confirm-dialog"):
            yield Static(self.title, id="dialog-title")

            with Vertical(id="confirm-message"):
                yield Static(self.message)

            # Dialog Buttons
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="cancel-confirm", variant="default")
                yield Button("Continue", id="confirm-action", variant="primary")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle dialog button presses"""
        button_id = event.button.id

        if button_id == "cancel-confirm":
            self.dismiss(False)

        elif button_id == "confirm-action":
            self.dismiss(True)


class FilePathInputDialog(ModalScreen[str]):
    """Modal dialog for file path input"""

    def __init__(
        self, title: str = "File Path", prompt: str = "Enter file path:"
    ) -> None:
        """Initialize the file path input dialog"""
        super().__init__()
        self.title = title
        self.prompt = prompt

    def compose(self) -> ComposeResult:
        """Create the file path input dialog layout"""
        with Container(id="filepath-dialog"):
            yield Static(f"📁 {self.title}", id="dialog-title")

            with Vertical(id="filepath-form"):
                yield Label(self.prompt)
                yield Input(placeholder="Enter file path...", id="path-input")

                with Horizontal(id="dialog-buttons"):
                    yield Button("OK", variant="primary", id="ok-button")
                    yield Button("Cancel", variant="default", id="cancel-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "ok-button":
            path_input = self.query_one("#path-input", Input)
            self.dismiss(path_input.value)
        elif event.button.id == "cancel-button":
            self.dismiss("")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)"""
        if event.input.id == "path-input":
            self.dismiss(event.input.value)


class ConfigurationDialog(ModalScreen[BuildConfiguration]):
    """Modal dialog for configuring build settings"""

    def compose(self) -> ComposeResult:
        """Create the configuration dialog layout"""
        with Container(id="config-dialog"):
            yield Static("⚙️ Build Configuration", id="dialog-title")

            with Vertical(id="config-form"):
                # Board Type Selection
                yield Label("Board Type:")
                yield Select(
                    [
                        # CaptainDMA boards
                        ("pcileech_75t484_x1", "CaptainDMA 75T"),
                        ("pcileech_35t484_x1", "CaptainDMA 35T 4.1"),
                        ("pcileech_35t325_x4", "CaptainDMA M2 x4"),
                        ("pcileech_35t325_x1", "CaptainDMA M2 x1"),
                        ("pcileech_100t484_x1", "CaptainDMA 100T"),
                        # Other boards
                        ("pcileech_enigma_x1", "Enigma x1"),
                        ("pcileech_squirrel", "PCIe Squirrel"),
                        ("pcileech_pciescreamer_xc7a35", "PCIeScreamer"),
                    ],
                    value="pcileech_35t325_x1",
                    id="board-type-select",
                )

                # Configuration Name
                yield Label("Configuration Name:")
                yield Input(
                    placeholder="Enter configuration name",
                    value="Default Configuration",
                    id="config-name-input",
                )

                # Description
                yield Label("Description:")
                yield Input(
                    placeholder="Enter configuration description",
                    value="Standard configuration for PCIe devices",
                    id="config-description-input",
                )

                # Feature Toggles
                yield Label("Advanced Features:")
                with Horizontal(classes="switch-row"):
                    yield Switch(value=True, id="advanced-sv-switch")
                    yield Static("Advanced SystemVerilog")

                with Horizontal(classes="switch-row"):
                    yield Switch(value=True, id="variance-switch")
                    yield Static("Manufacturing Variance")

                with Horizontal(classes="switch-row"):
                    yield Switch(value=False, id="profiling-switch")
                    yield Static("Behavior Profiling")

                with Horizontal(classes="switch-row"):
                    yield Switch(value=False, id="disable-ftrace-switch")
                    yield Static("Disable Ftrace (for CI/non-root)")

                with Horizontal(classes="switch-row"):
                    yield Switch(value=True, id="power-mgmt-switch")
                    yield Static("Power Management")

                with Horizontal(classes="switch-row"):
                    yield Switch(value=True, id="error-handling-switch")
                    yield Static("Error Handling")

                with Horizontal(classes="switch-row"):
                    yield Switch(value=True, id="perf-counters-switch")
                    yield Static("Performance Counters")

                with Horizontal(classes="switch-row"):
                    yield Switch(value=False, id="flash-after-switch")
                    yield Static("Flash After Build")

                # Donor dump configuration
                yield Label("Donor Device Analysis:")
                with Horizontal(classes="switch-row"):
                    yield Switch(value=True, id="donor-dump-switch")
                    yield Static("Extract Device Parameters (Default)")

                with Horizontal(classes="switch-row"):
                    yield Switch(value=False, id="auto-headers-switch")
                    yield Static("Auto-install Kernel Headers")

                # Local build options
                yield Label("Local Build Options (Opt-in):")
                with Horizontal(classes="switch-row"):
                    yield Switch(value=False, id="local-build-switch")
                    yield Static("Enable Local Build (Skips Donor Dump)")

                with Horizontal(classes="switch-row"):
                    yield Switch(value=False, id="skip-board-check-switch")
                    yield Static("Skip Board Check")

                # Donor info file input
                yield Label("Donor Info File (optional):")
                yield Input(
                    placeholder="Path to donor info JSON file",
                    value="",
                    id="donor-info-file-input",
                )

                # Profile Duration (only shown when profiling is enabled)
                yield Label("Profile Duration (seconds):")
                yield Input(
                    placeholder="30.0", value="30.0", id="profile-duration-input"
                )

            # Dialog Buttons
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="cancel-config", variant="default")
                yield Button("Apply", id="apply-config", variant="primary")
                yield Button("Save as Profile", id="save-config", variant="success")

    def on_mount(self) -> None:
        """Initialize dialog with current configuration"""
        # Get current configuration from parent app
        app = self.app

        # Then populate with current configuration if available
        if hasattr(app, "current_config"):
            config = app.current_config
            self._populate_form(config)

    def _populate_form(self, config: BuildConfiguration) -> None:
        """Populate form fields with configuration values"""
        try:
            # Get board type options first
            board_type_select = self.query_one("#board-type-select", Select)
            board_type_options = self._get_select_options(board_type_select)

            # Only set the value if it's valid
            board_type = config.board_type
            if board_type in board_type_options:
                board_type_select.value = board_type
            elif board_type_options:
                print(
                    f"Board type '{board_type}' not found, using '{board_type_options[0]}'"
                )
                board_type_select.value = board_type_options[0]

            self.query_one("#config-name-input", Input).value = config.name
            self.query_one("#config-description-input", Input).value = (
                config.description
            )
            self.query_one("#advanced-sv-switch", Switch).value = config.advanced_sv
            self.query_one("#variance-switch", Switch).value = config.enable_variance
            self.query_one("#profiling-switch", Switch).value = (
                config.behavior_profiling
            )
            self.query_one("#disable-ftrace-switch", Switch).value = (
                config.disable_ftrace
            )
            self.query_one("#power-mgmt-switch", Switch).value = config.power_management
            self.query_one("#error-handling-switch", Switch).value = (
                config.error_handling
            )
            self.query_one("#perf-counters-switch", Switch).value = (
                config.performance_counters
            )
            self.query_one("#flash-after-switch", Switch).value = (
                config.flash_after_build
            )
            self.query_one("#donor-dump-switch", Switch).value = config.donor_dump
            self.query_one("#auto-headers-switch", Switch).value = (
                config.auto_install_headers
            )
            self.query_one("#local-build-switch", Switch).value = config.local_build
            self.query_one("#skip-board-check-switch", Switch).value = (
                config.skip_board_check
            )
            self.query_one("#donor-info-file-input", Input).value = (
                config.donor_info_file
            )
            self.query_one("#profile-duration-input", Input).value = str(
                config.profile_duration
            )
        except Exception as e:
            # If any field fails to populate, continue with defaults
            print(f"Error populating form fields: {e}")

    def _get_select_options(self, select_widget: Select) -> list:
        """Safely get options from a Select widget

        Works with different versions of Textual by trying different approaches
        """
        try:
            # First try the standard way (newer Textual versions)
            if hasattr(select_widget, "options"):
                return [option.value for option in select_widget.options]
            # Then try the private attribute (older versions)
            elif hasattr(select_widget, "_options"):
                # Handle both tuple of values and list of objects
                if select_widget._options and hasattr(
                    select_widget._options[0], "value"
                ):
                    return [option.value for option in select_widget._options]
                else:
                    return list(select_widget._options)
            # Fallback to empty list if no options found
            return []
        except Exception as e:
            print(f"Error getting select options: {e}")
            return []

    def _sanitize_select_value(self, select: Select, fallback: str = "") -> str:
        """Ensure a select value is valid, with fallback options"""
        try:
            # Get current value (might be None or Select.BLANK)
            current_value = select.value
            if current_value == Select.BLANK:
                current_value = ""

            options = self._get_select_options(select)

            # If current value is valid, use it
            if current_value and current_value in options:
                return current_value

            # Try fallback value if provided
            if fallback and fallback in options:
                print(f"Using fallback value: {fallback}")
                return fallback

            # Otherwise use first available option
            if options:
                print(f"Using first available option: {options[0]}")
                return options[0]

            # Last resort
            print(f"No valid options found, using fallback: {fallback}")
            return fallback
        except Exception as e:
            print(f"Error sanitizing select value: {e}")
            return fallback

    def _create_config_from_form(self) -> BuildConfiguration:
        """Create BuildConfiguration from form values"""
        try:

            # Get board type safely
            board_type_select = self.query_one("#board-type-select", Select)
            board_type_options = self._get_select_options(board_type_select)

            # Use current value if valid, otherwise use default
            board_type = board_type_select.value
            if board_type == Select.BLANK and board_type_options:
                board_type = board_type_options[0]

            return BuildConfiguration(
                board_type=board_type,
                name=self.query_one("#config-name-input", Input).value,
                description=self.query_one("#config-description-input", Input).value,
                advanced_sv=self.query_one("#advanced-sv-switch", Switch).value,
                enable_variance=self.query_one("#variance-switch", Switch).value,
                behavior_profiling=self.query_one("#profiling-switch", Switch).value,
                disable_ftrace=self.query_one("#disable-ftrace-switch", Switch).value,
                power_management=self.query_one("#power-mgmt-switch", Switch).value,
                error_handling=self.query_one("#error-handling-switch", Switch).value,
                performance_counters=self.query_one(
                    "#perf-counters-switch", Switch
                ).value,
                flash_after_build=self.query_one("#flash-after-switch", Switch).value,
                donor_dump=self.query_one("#donor-dump-switch", Switch).value,
                auto_install_headers=self.query_one(
                    "#auto-headers-switch", Switch
                ).value,
                local_build=self.query_one("#local-build-switch", Switch).value,
                skip_board_check=self.query_one(
                    "#skip-board-check-switch", Switch
                ).value,
                donor_info_file=self.query_one("#donor-info-file-input", Input).value
                or None,
                profile_duration=self._parse_float_input(
                    self.query_one("#profile-duration-input", Input), 30.0
                ),
            )
        except (ValueError, TypeError) as e:
            # Return current config if form has invalid values
            print(f"Error creating configuration from form: {e}")
            app = self.app
            if hasattr(app, "current_config"):
                print("Using existing configuration as fallback")
                return app.current_config
            print("Creating default configuration as fallback")
            return BuildConfiguration()

    def _parse_float_input(
        self, input_widget: Input, default_value: float = 0.0
    ) -> float:
        """Safely parse a float value from an input widget"""
        try:
            value = input_widget.value
            if not value:
                return default_value
            return float(value)
        except (ValueError, TypeError) as e:
            print(f"Error parsing float input: {e}, using default: {default_value}")
            return default_value

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle dialog button presses"""
        button_id = event.button.id

        if button_id == "cancel-config":
            self.dismiss(None)

        elif button_id == "apply-config":
            config = self._create_config_from_form()
            self.dismiss(config)

        elif button_id == "save-config":
            config = self._create_config_from_form()
            # Save as profile through config manager
            app = self.app
            if hasattr(app, "config_manager"):
                try:
                    app.config_manager.save_profile(config.name, config)
                    app.notify(
                        f"Configuration saved as '{config.name}'",
                        severity="success",
                    )
                except Exception as e:
                    app.notify(f"Failed to save profile: {e}", severity="error")
            self.dismiss(config)


class PCILeechTUI(App):
    """Main TUI application for PCILeech firmware generation"""

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

    # Type hints for dependency-injected services
    device_manager: DeviceManager
    config_manager: ConfigManager
    build_orchestrator: BuildOrchestrator
    status_monitor: StatusMonitor
    error_handler: ErrorHandler
    ui_coordinator: UICoordinator
    background_monitor: BackgroundMonitor
    app_state: AppState

    def __init__(self):
        # Initialize Textual app first to set up reactive system
        super().__init__()

        # Initialize app state
        self.app_state = AppState()

        # Core services
        self.device_manager = DeviceManager()
        self.config_manager = ConfigManager()
        self.build_orchestrator = BuildOrchestrator()
        self.status_monitor = StatusMonitor()
        self.background_monitor = BackgroundMonitor(self)

        # Performance optimizations
        self.debounced_search = DebouncedSearch(delay=0.3)

        # System state that isn't part of the app state
        self._system_status = {}
        self._build_history = []

        # Initialize app state with default config
        initial_config = self.config_manager.get_current_config()
        self.app_state.set_config(initial_config)
        self.current_config = initial_config

        # Set up state change handler
        self.app_state.subscribe(self._on_state_change)

    # Keyboard action handlers
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()

    async def action_refresh_devices(self) -> None:
        """Refresh device list"""
        await self.ui_coordinator.scan_devices()

    async def action_configure(self) -> None:
        """Open configuration dialog"""
        await self._open_configuration_dialog()  # Still need a dialog opener

    async def action_start_build(self) -> None:
        """Start build process"""
        await self.ui_coordinator.handle_build_start()

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
                with Vertical(id="status-panel", classes="panel"):
                    yield Static("📊 System Status", classes="panel-title")
                    yield Static("🐳 Podman: Checking...", id="podman-status")
                    yield Static("⚡ Vivado: Checking...", id="vivado-status")
                    yield Static("🔌 USB Devices: Checking...", id="usb-status")
                    yield Static("💾 Disk Space: Checking...", id="disk-status")
                    yield Static("🔒 Root Access: Checking...", id="root-status")
                    yield Static(
                        "🧩 Donor Module: Checking...", id="donor-module-status"
                    )

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
            device_table = self.query_one("#device-table", DataTable)
            device_table.add_columns(
                "Status", "BDF", "Device", "Indicators", "Driver", "IOMMU"
            )

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
        await self.ui_coordinator.scan_devices()

        # Update UI with current config
        self._update_config_display()

        # Show welcome message with keyboard shortcuts
        self.notify(
            "Welcome! Press F1 or Ctrl+H for help, Ctrl+Q to quit", severity="info"
        )

    # Method removed - functionality moved to UICoordinator

    # Method removed - functionality moved to UICoordinator

    # Method removed - functionality moved to UICoordinator

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

    # Enhanced button handlers
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events"""
        button_id = event.button.id

        if button_id == "refresh-devices" or button_id == "scan-devices":
            await self._scan_devices()

        elif button_id == "start-build":
            await self.ui_coordinator.handle_build_start()

        elif button_id == "stop-build":
            await self.ui_coordinator.handle_build_stop()

        elif button_id == "configure":
            await self._open_configuration_dialog()

        elif button_id == "manage-profiles":
            await self._open_profile_manager()

        elif button_id == "advanced-search":
            await self._open_search_filter()

        elif button_id == "device-details":
            if self.selected_device:
                await self._show_device_details(self.selected_device)

        elif button_id == "export-devices":
            await self.ui_coordinator.export_device_list()

        elif button_id == "view-logs":
            await self._open_build_logs()

        elif button_id == "open-output":
            await self._open_output_directory()

        elif button_id == "view-report":
            await self._view_last_build_report()

        elif button_id == "backup-config":
            await self._backup_configuration()

        elif button_id == "check-donor-module":
            await self._check_donor_module_status(show_notification=True)

        elif button_id == "enable-donor-dump":
            await self._toggle_donor_dump()

        elif button_id == "generate-donor-template":
            await self._generate_donor_template()

        elif button_id == "documentation":
            await self._open_documentation()

        elif button_id == "advanced-settings":
            await self._open_advanced_settings()

    # New dialog methods
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

    async def _show_help(self) -> None:
        """Show help information"""
        help_text = """
PCILeech Firmware Generator - Keyboard Shortcuts

Navigation:
  Ctrl+Q       - Quit application
  Ctrl+R, F5   - Refresh device list
  Ctrl+F       - Search/Filter devices
  Ctrl+D       - Show device details

Configuration:
  Ctrl+C       - Open configuration dialog
  Ctrl+P       - Manage profiles

Build Operations:
  Ctrl+S       - Start build
  Ctrl+L       - View build logs

Help:
  F1, Ctrl+H   - Show this help

Mouse Controls:
  Click        - Select items
  Double-click - Open details/configure
  Right-click  - Context menu (where available)

Tips:
- Use the quick search bar to filter devices in real-time
- Green indicators show suitable devices
- Yellow indicators show devices with warnings
- Red indicators show incompatible devices
        """

        self.notify("Help information displayed in notification", severity="info")
        # In a real implementation, this would show a proper help dialog

    # Method removed - functionality moved to UICoordinator

    async def _backup_configuration(self) -> None:
        """Backup current configuration"""
        try:
            timestamp = self._get_current_timestamp().replace(":", "-")
            backup_path = Path(f"config_backup_{timestamp}.json")

            config_data = {
                "backup_time": self._get_current_timestamp(),
                "current_config": self.app_state.get_state("config").to_dict(),
                "profiles": self.config_manager.list_profiles(),
            }

            with open(backup_path, "w") as f:
                json.dump(config_data, f, indent=2)

            self.notify(f"Configuration backed up to {backup_path}", severity="success")
        except Exception as e:
            self.notify(f"Failed to backup configuration: {e}", severity="error")

    async def _open_output_directory(self) -> None:
        """Open the output directory"""
        try:
            output_dir = Path("output")
            if output_dir.exists():
                if hasattr(subprocess, "run"):
                    # Try to open with system file manager
                    try:
                        subprocess.run(["xdg-open", str(output_dir)], check=False)
                    except (FileNotFoundError, subprocess.CalledProcessError):
                        # Fallback for different operating systems
                        try:
                            subprocess.run(
                                ["open", str(output_dir)], check=False
                            )  # macOS
                        except (FileNotFoundError, subprocess.CalledProcessError):
                            try:
                                subprocess.run(
                                    ["explorer", str(output_dir)], check=False
                                )  # Windows
                            except (FileNotFoundError, subprocess.CalledProcessError):
                                self.notify(
                                    f"Please manually open: {output_dir.absolute()}",
                                    severity="info",
                                )
                else:
                    self.notify(
                        f"Output directory: {output_dir.absolute()}", severity="info"
                    )
            else:
                self.notify("Output directory does not exist yet", severity="warning")
        except Exception as e:
            self.notify(f"Failed to open output directory: {e}", severity="error")

    async def _view_last_build_report(self) -> None:
        """View the last build report"""
        try:
            report_path = Path("output/last_build_report.json")
            if report_path.exists():
                with open(report_path, "r") as f:
                    report_data = json.load(f)

                # Show summary in notification
                build_time = report_data.get("build_time", "Unknown")
                status = report_data.get("status", "Unknown")
                device = report_data.get("device", "Unknown")

                self.notify(
                    f"Last build: {device} - {status} at {build_time}", severity="info"
                )
            else:
                self.notify("No build report found", severity="warning")
        except Exception as e:
            self.notify(f"Failed to read build report: {e}", severity="error")

    async def _open_documentation(self) -> None:
        """Open documentation"""
        try:
            # Try to open local documentation first
            docs_path = Path("docs/_build/html/index.html")
            if docs_path.exists():
                webbrowser.open(f"file://{docs_path.absolute()}")
                self.notify("Opening local documentation", severity="info")
            else:
                # Fallback to online documentation
                webbrowser.open("https://github.com/ramseymcgrath/PCILeechFWGenerator")
                self.notify("Opening online documentation", severity="info")
        except Exception as e:
            self.notify(f"Failed to open documentation: {e}", severity="error")

    async def _open_advanced_settings(self) -> None:
        """Open advanced settings"""
        # This would open a more detailed configuration dialog
        self.notify(
            "Advanced settings - use Configure button for full options", severity="info"
        )

    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime

        return datetime.now().isoformat()

    # Method removed - functionality moved to UICoordinator

    # System monitoring is now handled by the BackgroundMonitor class

    def _update_status_display(self) -> None:
        """Update system status display"""
        status = self._system_status

        # Podman status
        podman = status.get("podman", {})
        podman_text = "🐳 Podman: " + (
            "Ready" if podman.get("status") == "ready" else "Not Available"
        )
        self.query_one("#podman-status", Static).update(podman_text)

        # Vivado status
        vivado = status.get("vivado", {})
        if vivado.get("status") == "detected":
            vivado_text = f"⚡ Vivado: {vivado['version']} Detected"
        else:
            vivado_text = "⚡ Vivado: Not Detected"
        self.query_one("#vivado-status", Static).update(vivado_text)

        # USB devices
        usb = status.get("usb_devices", {})
        usb_count = usb.get("count", 0)
        usb_text = f"🔌 USB Devices: {usb_count} Found"
        self.query_one("#usb-status", Static).update(usb_text)

        # Disk space
        disk = status.get("disk_space", {})
        if "free_gb" in disk:
            disk_text = f"💾 Disk Space: {disk['free_gb']} GB Free"
        else:
            disk_text = "💾 Disk Space: Unknown"
        self.query_one("#disk-status", Static).update(disk_text)

        # Root access
        root = status.get("root_access", {})
        root_text = "🔒 Root Access: " + (
            "Available" if root.get("available") else "Required"
        )
        self.query_one("#root-status", Static).update(root_text)

        # Donor module status (if available)
        if "donor_module" in status:
            donor_status = status.get("donor_module", {})
            status_text = donor_status["status"]

            # Format status with appropriate emoji
            if status_text == "installed":
                donor_text = "🧩 Donor Module: ✅ Installed"
            elif status_text == "built_not_loaded":
                donor_text = "🧩 Donor Module: ⚠️ Built but not loaded"
            elif status_text == "not_built":
                donor_text = "🧩 Donor Module: ❌ Not built"
            elif status_text == "missing_source":
                donor_text = "🧩 Donor Module: ❌ Source missing"
            elif status_text == "loaded_but_error":
                donor_text = "🧩 Donor Module: ⚠️ Loaded with errors"
            else:
                donor_text = "🧩 Donor Module: ❓ Unknown state"

            self.query_one("#donor-module-status", Static).update(donor_text)

    # Method removed - functionality moved to UICoordinator

    # Event handlers (moved to enhanced version above)
    # The on_button_pressed method has been enhanced and moved above

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle device table row selection"""
        row_key = event.row_key

        # Find selected device
        selected_device = None
        for device in self.filtered_devices:  # Use computed property
            if device.bdf == row_key:
                selected_device = device
                break

        if selected_device:
            # Update app state first
            self.app_state.set_selected_device(selected_device)
            # Then delegate to UI coordinator
            await self.ui_coordinator.handle_device_selection(selected_device)

    # Method removed - functionality moved to UICoordinator

    # Method removed - functionality moved to UICoordinator

    def _on_build_progress(self, progress: BuildProgress) -> None:
        """Handle build progress updates"""
        # Delegate to UI coordinator
        self.ui_coordinator.handle_build_progress(progress)

    async def _open_configuration_dialog(self) -> None:
        """Open the configuration dialog"""
        try:
            # Log current configuration before opening dialog
            print(
                f"Current configuration device_type: {self.app_state.get_state('config').device_type}"
            )

            result = await self.push_screen(ConfigurationDialog())
            if result is not None:
                # Update app state first
                self.app_state.set_config(result)
                # Then delegate configuration update to UI coordinator
                await self.ui_coordinator.handle_configuration_update(result)
        except Exception as e:
            if hasattr(self, "error_handler"):
                self.error_handler.handle_operation_error(
                    "opening configuration dialog", e
                )
            else:
                error_msg = f"Failed to open configuration dialog: {e}"
                print(f"ERROR: {error_msg}")
                self.notify(error_msg, severity="error")

    async def _confirm_with_warnings(self, title: str, message: str) -> bool:
        """Open a confirmation dialog with warnings and return user's choice"""
        try:
            result = await self.push_screen(ConfirmationDialog(title, message))
            return result is True
        except Exception as e:
            if hasattr(self, "error_handler"):
                self.error_handler.handle_operation_error(
                    "opening confirmation dialog", e
                )
            else:
                self.notify(
                    f"Failed to open confirmation dialog: {e}", severity="error"
                )
            return False

    async def _generate_donor_template(self) -> None:
        """Generate a donor info template file"""
        try:
            from pathlib import Path

            from ..device_clone.donor_info_template import DonorInfoTemplateGenerator

            # Default output path
            output_path = Path("donor_info_template.json")

            # Generate the template
            DonorInfoTemplateGenerator.save_template(output_path, pretty=True)

            self.notify(
                f"✓ Donor info template saved to: {output_path}", severity="success"
            )
            self.notify(
                "Fill in the device-specific values and use it for advanced cloning",
                severity="information",
            )

        except Exception as e:
            self.notify(f"Failed to generate donor template: {e}", severity="error")

    # App state handler
    def _on_state_change(
        self, old_state: Dict[str, Any], new_state: Dict[str, Any]
    ) -> None:
        """
        Handle app state changes.

        This method is called whenever the app state changes, and can be used to
        update UI elements or perform other actions in response to state changes.

        Args:
            old_state: The previous state
            new_state: The new state
        """
        # Update reactive attributes when app state changes
        if old_state.get("selected_device") != new_state.get("selected_device"):
            self.selected_device = new_state.get("selected_device")

        if old_state.get("config") != new_state.get("config"):
            self.current_config = new_state.get("config")

        if old_state.get("build_progress") != new_state.get("build_progress"):
            self.build_progress = new_state.get("build_progress")

        if old_state.get("filters") != new_state.get("filters"):
            self.device_filters = new_state.get("filters") or {}

    # Computed properties
    @property
    def devices(self) -> List[PCIDevice]:
        """Get all devices from app state."""
        return self.app_state.get_state("devices") or []

    @property
    def filtered_devices(self) -> List[PCIDevice]:
        """Get filtered devices based on search criteria and filters."""
        devices = self.devices
        filters = self.device_filters

        if not devices:
            return []

        # Apply filters if they exist
        if filters:
            # Filter by search text
            search_text = filters.get("search_text", "").lower()
            if search_text:
                devices = [
                    device
                    for device in devices
                    if search_text in device.display_name.lower()
                    or search_text in device.bdf.lower()
                    or search_text in device.vendor_name.lower()
                ]

            # Apply class filter
            if filters.get("class_filter") and filters["class_filter"] != "all":
                devices = [
                    device
                    for device in devices
                    if filters["class_filter"] in device.device_class.lower()
                ]

            # Apply status filter
            if filters.get("status_filter") and filters["status_filter"] != "all":
                status_filter = filters["status_filter"]
                if status_filter == "suitable":
                    devices = [d for d in devices if d.is_suitable]
                elif status_filter == "bound":
                    devices = [d for d in devices if d.has_driver]
                elif status_filter == "unbound":
                    devices = [d for d in devices if not d.has_driver]
                elif status_filter == "vfio":
                    devices = [d for d in devices if d.vfio_compatible]

            # Apply minimum score filter
            if filters.get("min_score", 0) > 0:
                min_score = filters["min_score"]
                devices = [
                    device
                    for device in devices
                    if device.suitability_score >= min_score
                ]

        return devices

    @property
    def can_start_build(self) -> bool:
        """Determine if a build can be started based on current state."""
        device = self.selected_device
        return device is not None and device.is_suitable and self.build_progress is None

    # Reactive watchers
    def watch_selected_device(self, device: Optional[PCIDevice]) -> None:
        """React to device selection changes"""
        if device:
            self.sub_title = f"Selected: {device.bdf} - {device.display_name}"
            self.ui_coordinator._update_compatibility_display(device)
        else:
            self.sub_title = "Interactive firmware generation for PCIe devices"
            self.ui_coordinator.clear_compatibility_display()

        # Update button states based on device selection
        try:
            start_button = self.query_one("#start-build", Button)
            start_button.disabled = not self.can_start_build
        except Exception:
            # Widget might not be available yet
            pass

    def watch_build_progress(self, progress: Optional[BuildProgress]) -> None:
        """React to build progress changes"""
        if progress:
            self.ui_coordinator._update_build_progress_display()

    async def _check_donor_module_status(
        self, show_notification: bool = True
    ) -> Dict[str, Any]:
        """
        Check donor_dump kernel module status and update UI

        Args:
            show_notification: Whether to show notification with status details

        Returns:
            Module status information dictionary
        """
        try:
            # Import donor_dump_manager
            import sys
            from pathlib import Path

            sys.path.append(str(Path(__file__).parent.parent.parent))
            from file_management.donor_dump_manager import DonorDumpManager

            # Create manager and check status
            manager = DonorDumpManager()
            module_status = manager.check_module_installation()

            # Update system status with module status
            if self._system_status is not None:
                self._system_status["donor_module"] = module_status
                self._update_status_display()

            # Show notification if requested
            if show_notification:
                status = module_status["status"]
                details = module_status["details"]

                if status == "installed":
                    self.notify(f"Donor module status: {details}", severity="success")
                elif status in ["built_not_loaded", "loaded_but_error"]:
                    self.notify(f"Donor module status: {details}", severity="warning")

                    # Show first issue and fix
                    issues = module_status.get("issues", [])
                    fixes = module_status.get("fixes", [])

                    if issues:
                        self.notify(f"Issue: {issues[0]}", severity="warning")
                    if fixes:
                        self.notify(
                            f"Suggested fix: {fixes[0]}",
                            severity="information",
                        )
                else:
                    self.notify(f"Donor module status: {details}", severity="error")

                    # Show first issue and fix
                    issues = module_status.get("issues", [])
                    fixes = module_status.get("fixes", [])

                    if issues:
                        self.notify(f"Issue: {issues[0]}", severity="error")
                    if fixes:
                        self.notify(
                            f"Suggested fix: {fixes[0]}",
                            severity="information",
                        )

            return module_status

        except Exception as e:
            if show_notification:
                self.notify(
                    f"Failed to check donor module status: {e}", severity="error"
                )

            # Update status display with error
            if self._system_status is not None:
                self._system_status["donor_module"] = {
                    "status": "error",
                    "details": f"Error checking module: {str(e)}",
                    "issues": [f"Exception occurred: {str(e)}"],
                    "fixes": [
                        "Check if src/file_management/donor_dump_manager.py is accessible"
                    ],
                }
                self._update_status_display()

            return {
                "status": "error",
                "details": f"Error checking module: {str(e)}",
                "issues": [f"Exception occurred: {str(e)}"],
                "fixes": [
                    "Check if src/file_management/donor_dump_manager.py is accessible"
                ],
            }

    async def _toggle_donor_dump(self) -> None:
        """Toggle donor dump functionality"""
        current_config = self.current_config.copy()

        if current_config.donor_dump:
            # Disable donor dump
            current_config.donor_dump = False
            current_config.local_build = True
            self.current_config = current_config
            self.config_manager.set_current_config(current_config)
            self._update_config_display()
            self._update_donor_dump_button()
            self.notify("Donor dump disabled - using local build mode", severity="info")
        else:
            # Enable donor dump
            current_config.donor_dump = True
            current_config.local_build = False
            self.current_config = current_config
            self.config_manager.set_current_config(current_config)
            self._update_config_display()
            self._update_donor_dump_button()
            self.notify(
                "Donor dump enabled - device analysis will be performed",
                severity="success",
            )

    # Method removed - functionality moved to UICoordinator


def check_sudo():
    """Check if running as root/sudo and warn if not."""
    import os

    try:
        # On Unix-like systems (Linux, macOS)
        if hasattr(os, "geteuid"):
            if os.geteuid() != 0:
                print(
                    "⚠️  Warning: PCILeech requires root privileges for hardware access."
                )
                print("⚠️  Warning: Please run with sudo or as root user.")
                return False
            return True
        # On Windows, just return True (will handle UAC elsewhere)
        return True
    except Exception as e:
        print(f"⚠️  Error checking sudo access: {e}")
        return False


def check_os_compatibility():
    """Check if the current OS is compatible with PCILeech operations."""
    import platform
    import sys

    system = platform.system()
    if system == "Linux":
        # Check if VFIO modules are loaded
        try:
            with open("/proc/modules", "r") as f:
                modules = f.read()
                if "vfio " not in modules or "vfio_pci " not in modules:
                    print("⚠️  Warning: VFIO modules not loaded. Run:")
                    print("⚠️  Warning:   sudo modprobe vfio vfio-pci")
        except FileNotFoundError:
            # /proc/modules not available, skip check
            pass

        return True, None
    elif system == "Darwin":  # macOS
        return (
            False,
            "PCILeech requires Linux. macOS is not supported for firmware generation.",
        )
    elif system == "Windows":
        return False, "PCILeech requires Linux. Windows is not supported."
    else:
        return (
            False,
            f"Unsupported operating system: {system}. PCILeech requires Linux.",
        )


if __name__ == "__main__":
    # Check OS compatibility
    is_compatible, os_message = check_os_compatibility()
    if not is_compatible:
        print(f"❌ Error: {os_message}")
        print("PCILeech requires Linux for full functionality.")
        import sys

        sys.exit(1)
    elif os_message:
        print(f"⚠️  Warning: {os_message}")

    # Check sudo/root access
    if not check_sudo():
        print("⚠️  Warning: Continuing without root privileges - limited functionality.")

    # Run the application
    app = PCILeechTUI()
    app.run()
