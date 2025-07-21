"""
Main TUI Application

The main entry point for the PCILeech Firmware Generator TUI.
"""

import asyncio
from typing import Any, Dict, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
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
    Select,
    Static,
    Switch,
)

from .core.build_orchestrator import BuildOrchestrator
from .core.config_manager import ConfigManager
from .core.device_manager import DeviceManager
from .core.status_monitor import StatusMonitor
from .models.config import BuildConfiguration
from .models.device import PCIDevice
from .models.progress import BuildProgress


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

    # Reactive attributes
    selected_device: reactive[Optional[PCIDevice]] = reactive(None)
    current_config: reactive[BuildConfiguration] = reactive(BuildConfiguration())
    build_progress: reactive[Optional[BuildProgress]] = reactive(None)

    def __init__(self):
        # Initialize Textual app first to set up reactive system
        super().__init__()

        # Core services
        self.device_manager = DeviceManager()
        self.config_manager = ConfigManager()
        self.build_orchestrator = BuildOrchestrator()
        self.status_monitor = StatusMonitor()

        # State
        self._devices = []
        self._system_status = {}

        # Initialize current_config from config manager
        # This must be done after super().__init__() to avoid ReactiveError
        self.current_config = self.config_manager.get_current_config()

    def compose(self) -> ComposeResult:
        """Create the main UI layout"""
        yield Header()

        with Container(id="main-container"):
            with Horizontal(id="top-section"):
                # Device Selection Panel
                with Vertical(id="device-panel", classes="panel"):
                    yield Static("📡 PCIe Device Selection", classes="panel-title")
                    yield DataTable(id="device-table")
                    with Horizontal(classes="button-row"):
                        yield Button("Refresh", id="refresh-devices", variant="primary")
                        yield Button("Details", id="device-details", disabled=True)

                # Configuration Panel
                with Vertical(id="config-panel", classes="panel"):
                    yield Static("⚙️ Build Configuration", classes="panel-title")
                    yield Static("Board Type: 75t", id="board-type")
                    yield Static("Advanced Features: Enabled", id="advanced-features")
                    yield Static("Build Mode: Standard", id="build-mode")
                    with Horizontal(classes="button-row"):
                        yield Button("Configure", id="configure", variant="primary")
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

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application"""
        try:
            # Set up the device table
            device_table = self.query_one("#device-table", DataTable)
            device_table.add_columns(
                "Status", "BDF", "Device", "Indicators", "Driver", "IOMMU"
            )

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

        # Start system status monitoring
        asyncio.create_task(self._monitor_system_status())

        # Initial device scan
        await self._scan_devices()

        # Update UI with current config
        self._update_config_display()

    async def _scan_devices(self) -> None:
        """Scan for PCIe devices"""
        try:
            self._devices = await self.device_manager.scan_devices()
            self._update_device_table()

            # Update device count in title
            device_count = len(self._devices)
            device_panel = self.query_one("#device-panel .panel-title", Static)
            device_panel.update(f"📡 PCIe Devices Found: {device_count}")

        except Exception as e:
            self.notify(f"Failed to scan devices: {e}", severity="error")

    def _update_device_table(self) -> None:
        """Update the device table with current devices"""
        device_table = self.query_one("#device-table", DataTable)
        device_table.clear()

        for device in self._devices:
            device_table.add_row(
                device.status_indicator,
                device.bdf,
                f"{device.vendor_name} {device.device_name}"[:40],
                device.compact_status,
                device.driver,
                device.iommu_group,
                key=device.bdf,
            )

    def _update_config_display(self) -> None:
        """Update configuration display"""
        config = self.current_config

        try:
            self.query_one("#board-type", Static).update(
                f"Board Type: {config.board_type}"
            )

            features = "Enabled" if config.is_advanced else "Basic"
            self.query_one("#advanced-features", Static).update(
                f"Advanced Features: {features}"
            )

            if config.local_build:
                build_mode = "Local Build (No Donor Dump)"
            else:
                build_mode = "Standard (With Donor Dump)"
            self.query_one("#build-mode", Static).update(f"Build Mode: {build_mode}")

            # Update donor dump button
            self._update_donor_dump_button()
        except Exception as e:
            # Handle any UI update errors gracefully
            print(f"Error updating configuration display: {e}")
            self.notify("Error displaying configuration", severity="error")

    async def _monitor_system_status(self) -> None:
        """Monitor system status continuously"""
        while True:
            try:
                self._system_status = await self.status_monitor.get_system_status()
                self._update_status_display()

                # Check donor module status periodically
                await self._check_donor_module_status(show_notification=False)

                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                self.notify(f"Status monitoring error: {e}", severity="warning")
                await asyncio.sleep(10)  # Retry after 10 seconds on error

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

    def _update_build_progress(self) -> None:
        """Update build progress display"""
        if not self.build_progress:
            return

        progress = self.build_progress

        # Update status
        self.query_one("#build-status", Static).update(
            f"Status: {progress.status_text}"
        )

        # Update progress bar
        progress_bar = self.query_one("#build-progress", ProgressBar)
        progress_bar.progress = progress.overall_progress

        # Update progress text
        self.query_one("#progress-text", Static).update(progress.progress_bar_text)

        # Update resource usage
        if progress.resource_usage:
            cpu = progress.resource_usage.get("cpu", 0)
            memory = progress.resource_usage.get("memory", 0)
            disk = progress.resource_usage.get("disk_free", 0)
            resource_text = f"Resources: CPU: {
                cpu:.1f}% | Memory: {
                memory:.1f}GB | Disk: {disk:.1f}GB free"
            self.query_one("#resource-usage", Static).update(resource_text)

    # Event handlers
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events"""
        button_id = event.button.id

        if button_id == "refresh-devices" or button_id == "scan-devices":
            await self._scan_devices()

        elif button_id == "start-build":
            await self._start_build()

        elif button_id == "stop-build":
            await self._stop_build()

        elif button_id == "configure":
            try:
                await self._open_configuration_dialog()
            except Exception as e:
                self.notify(f"Error opening configuration: {e}", severity="error")

        elif button_id == "open-output":
            import subprocess

            subprocess.run(["xdg-open", "output"], check=False)

        elif button_id == "check-donor-module":
            await self._check_donor_module_status(show_notification=True)

        elif button_id == "enable-donor-dump":
            await self._toggle_donor_dump()

        elif button_id == "generate-donor-template":
            await self._generate_donor_template()

        elif button_id == "documentation":
            self.notify("Opening documentation...", severity="info")

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle device table row selection"""
        event.data_table
        row_key = event.row_key

        # Find selected device
        selected_device = None
        for device in self._devices:
            if device.bdf == row_key:
                selected_device = device
                break

        if selected_device:
            self.selected_device = selected_device

            # Enable/disable buttons based on selection
            self.query_one("#device-details", Button).disabled = False
            self.query_one("#start-build", Button).disabled = (
                not selected_device.is_suitable
            )

            self.notify(
                f"Selected device: {selected_device.bdf}",
                severity="info",
            )

    async def _start_build(self) -> None:
        """Start the build process"""
        if not self.selected_device:
            self.notify("Please select a device first", severity="error")
            return

        if self.build_orchestrator.is_building():
            self.notify("Build already in progress", severity="warning")
            return

        # Check donor module status before starting build if donor_dump is
        # enabled
        if self.current_config.donor_dump and not self.current_config.local_build:
            module_status = await self._check_donor_module_status(
                show_notification=False
            )
            if module_status and module_status.get("status") != "installed":
                # Show warning dialog with issues and fixes
                self.notify(
                    "⚠️ Donor module is not properly installed. This may affect the build.",
                    severity="warning",
                )

                # Show detailed issues and fixes
                issues = module_status.get("issues", [])
                fixes = module_status.get("fixes", [])

                if issues:
                    self.notify(f"Issues: {issues[0]}", severity="warning")
                if fixes:
                    self.notify(
                        f"Suggested fix: {fixes[0]}",
                        severity="information",
                    )

                # Ask if user wants to continue anyway
                should_continue = await self._confirm_with_warnings(
                    "⚠️ Warning: Donor Module Issues",
                    "The donor module is not properly installed. This may affect the build. Do you want to continue anyway?",
                )

                if not should_continue:
                    self.notify("Build cancelled by user", severity="information")
                    return

        try:
            # Update button states
            self.query_one("#start-build", Button).disabled = True
            self.query_one("#stop-build", Button).disabled = False

            # Start build with progress callback
            success = await self.build_orchestrator.start_build(
                self.selected_device, self.current_config, self._on_build_progress
            )

            if success:
                self.notify("Build completed successfully!", severity="success")
            else:
                self.notify("Build was cancelled", severity="warning")

        except Exception as e:
            error_msg = str(e)
            # Check if this is a platform compatibility error to reduce redundant messaging
            if (
                "requires Linux" in error_msg
                or "platform incompatibility" in error_msg
                or "only available on Linux" in error_msg
            ):
                self.notify(
                    "Build skipped: Platform compatibility issue (see logs)",
                    severity="warning",
                )
            else:
                self.notify(f"Build failed: {e}", severity="error")
        finally:
            # Reset button states
            self.query_one("#start-build", Button).disabled = False
            self.query_one("#stop-build", Button).disabled = True

    async def _stop_build(self) -> None:
        """Stop the build process"""
        await self.build_orchestrator.cancel_build()
        self.notify("Build cancelled", severity="info")

    def _on_build_progress(self, progress: BuildProgress) -> None:
        """Handle build progress updates"""
        self.build_progress = progress
        self.call_after_refresh(self._update_build_progress)

    async def _open_configuration_dialog(self) -> None:
        """Open the configuration dialog"""
        try:
            # Log current configuration before opening dialog
            print(
                f"Current configuration device_type: {self.current_config.device_type}"
            )

            result = await self.push_screen(ConfigurationDialog())
            if result is not None:
                # Update current configuration
                self.current_config = result
                # Save the configuration to the config manager
                self.config_manager.set_current_config(result)
                print(
                    f"New configuration device_type: {self.current_config.device_type}"
                )
                self._update_config_display()
                self.notify("Configuration updated successfully", severity="success")
        except Exception as e:
            error_msg = f"Failed to open configuration dialog: {e}"
            print(f"ERROR: {error_msg}")
            self.notify(error_msg, severity="error")

    async def _confirm_with_warnings(self, title: str, message: str) -> bool:
        """Open a confirmation dialog with warnings and return user's choice"""
        try:
            result = await self.push_screen(ConfirmationDialog(title, message))
            return result is True
        except Exception as e:
            self.notify(f"Failed to open confirmation dialog: {e}", severity="error")
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

    # Reactive watchers
    def watch_selected_device(self, device: Optional[PCIDevice]) -> None:
        """React to device selection changes"""
        if device:
            self.sub_title = f"Selected: {device.bdf} - {device.display_name}"
            self._update_compatibility_display(device)

            # Enable build buttons for test compatibility
            try:
                start_button = self.query_one("#start-build", Button)
                start_button.disabled = False

                details_button = self.query_one("#device-details", Button)
                details_button.disabled = False
            except Exception:
                # Ignore errors in tests
                pass
        else:
            self.sub_title = "Interactive firmware generation for PCIe devices"
            self._clear_compatibility_display()

    def _update_compatibility_display(self, device: PCIDevice) -> None:
        """Update the compatibility factors display for the selected device"""
        # Update title and score
        compatibility_title = self.query_one("#compatibility-title", Static)
        compatibility_title.update(f"Device: {device.display_name}")

        compatibility_score = self.query_one("#compatibility-score", Static)
        score_text = f"Final Score: [bold]{device.suitability_score:.2f}[/bold]"
        if device.is_suitable:
            score_text = f"[green]{score_text}[/green]"
        else:
            score_text = f"[red]{score_text}[/red]"

        # Add detailed status indicators
        status_indicators = []
        status_indicators.append(f"Valid: {device.validity_indicator}")
        status_indicators.append(f"Driver: {device.driver_indicator}")
        status_indicators.append(f"VFIO: {device.vfio_indicator}")
        status_indicators.append(f"IOMMU: {device.iommu_indicator}")
        status_indicators.append(f"Ready: {device.ready_indicator}")

        status_line = " | ".join(status_indicators)
        score_text += f"\n{status_line}"
        compatibility_score.update(score_text)

        # Update factors table
        factors_table = self.query_one("#compatibility-table", DataTable)
        factors_table.clear()

        # Set up columns if not already done
        if not factors_table.columns:
            factors_table.add_columns("Status Check", "Result", "Details")

        # Add detailed status information
        self._add_detailed_status_rows(factors_table, device)

        # Add compatibility factors if available
        for factor in device.compatibility_factors:
            name = factor["name"]
            adjustment = factor["adjustment"]
            description = factor["description"]
            factor["is_positive"]

            # Format adjustment with sign and color
            if adjustment > 0:
                adj_text = f"[green]+{adjustment:.1f}[/green]"
            elif adjustment < 0:
                adj_text = f"[red]{adjustment:.1f}[/red]"
            else:
                adj_text = f"{adjustment:.1f}"

            # Add row with appropriate styling
            factors_table.add_row(name, adj_text, description)

    def _add_detailed_status_rows(self, table, device: PCIDevice) -> None:
        """Add detailed status information to the compatibility table."""
        # Device validity
        valid_status = (
            "[green]✅ Valid[/green]" if device.is_valid else "[red]❌ Invalid[/red]"
        )
        table.add_row(
            "Device Accessibility",
            valid_status,
            "Device is properly detected and accessible",
        )

        # Driver status
        if device.has_driver:
            if device.is_detached:
                driver_status = "[green]🔓 Detached[/green]"
                driver_details = f"Device detached from {device.driver} for VFIO use"
            else:
                driver_status = "[yellow]🔒 Bound[/yellow]"
                driver_details = f"Device bound to {device.driver} driver"
        else:
            driver_status = "[blue]🔌 No Driver[/blue]"
            driver_details = "No driver currently bound to device"
        table.add_row("Driver Status", driver_status, driver_details)

        # VFIO compatibility
        vfio_status = (
            "[green]🛡️ Compatible[/green]"
            if device.vfio_compatible
            else "[red]❌ Incompatible[/red]"
        )
        vfio_details = (
            "Device supports VFIO passthrough"
            if device.vfio_compatible
            else "Device cannot use VFIO passthrough"
        )
        table.add_row("VFIO Support", vfio_status, vfio_details)

        # IOMMU status
        iommu_status = (
            "[green]🔒 Enabled[/green]"
            if device.iommu_enabled
            else "[red]❌ Disabled[/red]"
        )
        iommu_details = (
            f"IOMMU group: {device.iommu_group}"
            if device.iommu_enabled
            else "IOMMU not properly configured"
        )
        table.add_row("IOMMU Configuration", iommu_status, iommu_details)

        # Overall readiness
        if device.is_valid and device.vfio_compatible and device.iommu_enabled:
            ready_status = "[green]⚡ Ready[/green]"
            ready_details = "Device is ready for firmware generation"
        elif device.is_suitable:
            ready_status = "[yellow]⚠️ Caution[/yellow]"
            ready_details = "Device may work but has some compatibility issues"
        else:
            ready_status = "[red]❌ Not Ready[/red]"
            ready_details = "Device has significant compatibility issues"
        table.add_row("Overall Status", ready_status, ready_details)

    def _clear_compatibility_display(self) -> None:
        """Clear the compatibility display when no device is selected"""
        try:
            compatibility_title = self.query_one("#compatibility-title", Static)
            compatibility_title.update("Select a device to view compatibility factors")

            compatibility_score = self.query_one("#compatibility-score", Static)
            compatibility_score.update("")

            factors_table = self.query_one("#compatibility-table", DataTable)
            factors_table.clear()
        except Exception:
            # Ignore DOM errors in tests or during initialization
            pass

    def watch_build_progress(self, progress: Optional[BuildProgress]) -> None:
        """React to build progress changes"""
        if progress:
            self._update_build_progress()

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

    def _update_donor_dump_button(self) -> None:
        """Update the donor dump button text and style based on current state"""
        try:
            button = self.query_one("#enable-donor-dump", Button)
            if self.current_config.donor_dump:
                button.label = "🚫 Disable Donor Dump"
                button.variant = "error"
            else:
                button.label = "🎯 Enable Donor Dump"
                button.variant = "success"
        except Exception:
            # Button might not exist in tests
            pass


if __name__ == "__main__":
    app = PCILeechTUI()
    app.run()
