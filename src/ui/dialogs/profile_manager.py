"""
Profile Manager Dialog

Dialog for managing configuration profiles.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static

if TYPE_CHECKING:
    from ...tui.core.config_manager import ConfigManager
    from .confirmation import ConfirmationDialog
    from .file_path_input import FilePathInputDialog


class ProfileManagerDialog(ModalScreen[Optional[str]]):
    """Modal dialog for managing configuration profiles"""

    def __init__(self, config_manager: "ConfigManager") -> None:
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
            export_path = f"{profile_name.replace(' ', '_')}_profile.json"

            success = self.config_manager.export_profile(profile_name, export_path)
            if success:
                self.app.notify(
                    f"Profile exported to {export_path}", severity="success"
                )
            else:
                self.app.notify(f"Failed to export profile", severity="error")

    async def _import_profile(self) -> None:
        """Import a profile from file"""
        # Prompt user for file path using a modal dialog
        file_path = await self.app.push_screen(
            FilePathInputDialog(
                title="Import Profile",
                prompt="Enter the path to the profile file to import:",
            )
        )

        if file_path:
            import_path = file_path
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
