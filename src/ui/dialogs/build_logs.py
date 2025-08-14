"""
Build Log Dialog

Dialog for displaying build logs and history.
"""

import json
import platform
from pathlib import Path
from typing import TYPE_CHECKING, List

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (Button, DataTable, RichLog, Static, TabbedContent,
                             TabPane)

if TYPE_CHECKING:
    from ...tui.core.build_orchestrator import BuildOrchestrator


class BuildLogDialog(ModalScreen[bool]):
    """Modal dialog for displaying build logs and history"""

    def __init__(self, build_orchestrator: "BuildOrchestrator") -> None:
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

            # Get build history data from orchestrator
            history_data = self.build_orchestrator.get_build_history()

            if not history_data:
                # Fallback to mock data if real data not available
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
        elif button_id == "view-build-details":
            await self._view_build_details()

    async def _export_current_log(self) -> None:
        """Export current build log"""
        try:
            # Get log content from orchestrator
            log_content = self.build_orchestrator.get_current_build_log_text()
            if not log_content:
                log_content = (
                    "PCILeech Build Log\n================\n\nNo log content available."
                )

            log_path = Path("current_build.log")
            with open(log_path, "w") as f:
                f.write(log_content)

            self.app.notify(f"Log exported to {log_path}", severity="success")
        except Exception as e:
            self.app.notify(f"Failed to export log: {e}", severity="error")

    async def _export_build_history(self) -> None:
        """Export build history"""
        try:
            # Get build history from orchestrator
            history_data = self.build_orchestrator.get_build_history_data()
            if not history_data:
                history_data = {"builds": []}

            history_path = Path("build_history.json")
            with open(history_path, "w") as f:
                json.dump(history_data, f, indent=2)

            self.app.notify(f"History exported to {history_path}", severity="success")
        except Exception as e:
            self.app.notify(f"Failed to export history: {e}", severity="error")

    async def _view_build_details(self) -> None:
        """View details of the selected build"""
        try:
            table = self.query_one("#build-history-table", DataTable)
            if table.cursor_row is not None:
                # Get selected build info
                build_date = table.get_row_at(table.cursor_row)[0]
                build_device = table.get_row_at(table.cursor_row)[1]

                # Get build details from orchestrator
                build_details = self.build_orchestrator.get_build_details(
                    build_date, build_device
                )

                # Show details in a notification for now
                # In a full implementation, this would display a detailed view
                self.app.notify(
                    f"Build details for {build_device} on {build_date}: {build_details}",
                    severity="information",
                )
        except Exception as e:
            self.app.notify(f"Failed to view build details: {e}", severity="error")
