"""
Search and Filter Dialog

Modal dialog for searching and filtering devices.
"""

from typing import TYPE_CHECKING, Any, Dict

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static


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
