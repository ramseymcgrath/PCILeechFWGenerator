"""
Status Panel Widget

This module provides a system status panel widget for displaying
system-related information relevant to the PCILeech firmware generator.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, cast

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class StatusPanel(Vertical):
    """
    A panel that displays various system status indicators relevant to the
    PCILeech firmware generator, such as container status, tool availability,
    and resource usage.
    """

    DEFAULT_CSS = """
    StatusPanel {
        width: 100%;
        height: auto;
    }
    
    StatusPanel .panel-title {
        text-style: bold;
        background: $panel-lighten-1;
        padding: 1 2;
    }
    
    StatusPanel .status-row {
        padding: 0 2;
    }
    
    StatusPanel .status-ok {
        color: $success;
    }
    
    StatusPanel .status-warning {
        color: $warning;
    }
    
    StatusPanel .status-error {
        color: $error;
    }
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the status panel with default statuses."""
        super().__init__(*args, **kwargs)
        self.status_items = {
            "podman": ("🐳 Podman", "Checking...", "status-warning"),
            "vivado": ("⚡ Vivado", "Checking...", "status-warning"),
            "usb": ("🔌 USB Devices", "Checking...", "status-warning"),
            "disk": ("💾 Disk Space", "Checking...", "status-warning"),
            "root": ("🔒 Root Access", "Checking...", "status-warning"),
            "donor_module": ("🧩 Donor Module", "Checking...", "status-warning"),
        }

    def compose(self) -> ComposeResult:
        """Create the status panel layout with all status indicators."""
        yield Static("📊 System Status", classes="panel-title")

        # Create a Static widget for each status item
        for key, (prefix, status, _) in self.status_items.items():
            widget_id = f"{key}-status"
            yield Static(f"{prefix}: {status}", id=widget_id, classes="status-row")

    def update_status(
        self, key: str, status: str, status_type: str = "status-ok"
    ) -> None:
        """
        Update a specific status indicator.

        Args:
            key: The key of the status to update
            status: The new status text
            status_type: CSS class for styling (status-ok, status-warning, status-error)
        """
        if key not in self.status_items:
            return

        prefix, _, _ = self.status_items[key]
        self.status_items[key] = (prefix, status, status_type)

        # Update the widget
        widget_id = f"{key}-status"
        widget = self.query_one(f"#{widget_id}", Static)

        # Remove existing status classes and add the new one
        for class_name in ["status-ok", "status-warning", "status-error"]:
            widget.remove_class(class_name)

        widget.add_class(status_type)
        widget.update(f"{prefix}: {status}")

    def update_all_statuses(self, statuses: Dict[str, Dict[str, Any]]) -> None:
        """
        Update all status indicators from a dictionary.

        Args:
            statuses: Dictionary with status information
                {
                    "key": {
                        "status": "Status text",
                        "type": "status-ok|status-warning|status-error"
                    },
                    ...
                }
        """
        for key, info in statuses.items():
            if key in self.status_items:
                status = info.get("status", "Unknown")
                status_type = info.get("type", "status-warning")
                self.update_status(key, status, status_type)
