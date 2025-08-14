"""
Configuration Dialog

Dialog for configuring build settings.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static, Switch

if TYPE_CHECKING:
    from ...tui.models.config import BuildConfiguration


class ConfigurationDialog(ModalScreen[Optional["BuildConfiguration"]]):
    """Modal dialog for configuring build settings"""

    def __init__(self, current_config: Optional["BuildConfiguration"] = None) -> None:
        """
        Initialize the configuration dialog.

        Args:
            current_config: Current configuration to populate the form with
        """
        super().__init__()
        self.current_config = current_config

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
        if self.current_config:
            self._populate_form(self.current_config)

    def _populate_form(self, config: "BuildConfiguration") -> None:
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
                config.donor_info_file or ""
            )
            self.query_one("#profile-duration-input", Input).value = str(
                config.profile_duration
            )
        except Exception as e:
            # If any field fails to populate, continue with defaults
            print(f"Error populating form fields: {e}")

    def _get_select_options(self, select_widget: Select) -> List[str]:
        """
        Safely get options from a Select widget

        Works with different versions of Textual by trying different approaches

        Returns:
            List of option values
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
                    return [option[0] for option in select_widget._options]
            # Fallback to empty list if no options found
            return []
        except Exception as e:
            print(f"Error getting select options: {e}")
            return []

    def _sanitize_select_value(self, select: Select, fallback: str = "") -> str:
        """
        Ensure a select value is valid, with fallback options

        Args:
            select: The Select widget to check
            fallback: Fallback value if current value is invalid

        Returns:
            A valid select value
        """
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

    def _create_config_from_form(self) -> "BuildConfiguration":
        """Create BuildConfiguration from form values"""
        try:
            # Import here to avoid circular imports
            from ...tui.models.config import BuildConfiguration

            # Get board type safely
            board_type_select = self.query_one("#board-type-select", Select)
            board_type = self._sanitize_select_value(
                board_type_select, "pcileech_35t325_x1"
            )

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
            if self.current_config:
                print("Using existing configuration as fallback")
                return self.current_config

            # Import for fallback
            from ...tui.models.config import BuildConfiguration

            print("Creating default configuration as fallback")
            return BuildConfiguration()

    def _parse_float_input(
        self, input_widget: Input, default_value: float = 0.0
    ) -> float:
        """
        Safely parse a float value from an input widget

        Args:
            input_widget: The Input widget to parse
            default_value: Default value if parsing fails

        Returns:
            Parsed float value or default
        """
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
