"""
Virtual Device Table Widget

This module provides a virtualized data table implementation for handling large device lists
with optimal performance by only rendering visible rows.
"""

from typing import Any, Dict, List, Optional

from textual.binding import Binding
from textual.widgets import DataTable

from ..models.device import PCIDevice


class VirtualDeviceTable(DataTable):
    """
    A virtualized data table that efficiently handles large device lists
    by only rendering the visible portion of the table.

    This implementation significantly improves performance when dealing with
    hundreds or thousands of devices by limiting the number of rendered rows
    to only those that are currently visible in the viewport.
    """

    BINDINGS = [
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("home", "cursor_home", "Home", show=False),
        Binding("end", "cursor_end", "End", show=False),
        Binding("pageup", "cursor_page_up", "Page Up", show=False),
        Binding("pagedown", "cursor_page_down", "Page Down", show=False),
    ]

    def __init__(self, *args, **kwargs):
        """Initialize the virtual device table."""
        super().__init__(*args, **kwargs)
        self.virtual_rows = []  # All device rows
        self.visible_start = 0  # Start index of visible rows
        self.visible_count = 50  # Only render 50 rows at a time

    def set_data(self, devices: List[PCIDevice]) -> None:
        """
        Set the device data and render only the visible rows.

        Args:
            devices: List of PCIDevice objects to display
        """
        self.virtual_rows = devices
        self._render_visible_rows()

    def _render_visible_rows(self) -> None:
        """
        Render only the rows that are currently visible in the viewport.
        This is the key optimization for handling large device lists.
        """
        self.clear()
        end = min(self.visible_start + self.visible_count, len(self.virtual_rows))

        for i in range(self.visible_start, end):
            device = self.virtual_rows[i]
            self._add_device_row(device)

    def _add_device_row(self, device: PCIDevice) -> None:
        """
        Add a single device row to the table.

        Args:
            device: PCIDevice object to add as a row
        """
        # Extract device information for the row
        status_indicator = "✅" if device.is_suitable else "❌"

        # Add row with device information
        self.add_row(
            status_indicator,
            device.bdf,
            f"{device.vendor_name} {device.device_name}",
            f"Score: {device.suitability_score:.2f}",
            device.driver or "None",
            device.iommu_group or "N/A",
            key=device.bdf,
        )

    def action_cursor_down(self) -> None:
        """Handle down arrow key to navigate down and load more rows if needed."""
        super().action_cursor_down()
        self._check_viewport_change()

    def action_cursor_up(self) -> None:
        """Handle up arrow key to navigate up and load previous rows if needed."""
        super().action_cursor_up()
        self._check_viewport_change()

    def action_cursor_page_down(self) -> None:
        """Handle page down key to navigate down a page and load more rows if needed."""
        super().action_cursor_page_down()
        # After paging down, we definitely need to update the viewport
        self._update_viewport(self.cursor_row - self.visible_count // 4)

    def action_cursor_page_up(self) -> None:
        """Handle page up key to navigate up a page and load previous rows if needed."""
        super().action_cursor_page_up()
        # After paging up, we definitely need to update the viewport
        self._update_viewport(self.cursor_row - self.visible_count // 4)

    def action_cursor_home(self) -> None:
        """Handle home key to navigate to the first row."""
        super().action_cursor_home()
        self._update_viewport(0)

    def action_cursor_end(self) -> None:
        """Handle end key to navigate to the last row."""
        super().action_cursor_end()
        self._update_viewport(len(self.virtual_rows) - self.visible_count)

    def _check_viewport_change(self) -> None:
        """Check if cursor is close to viewport edge and update if necessary."""
        if self.cursor_row is None:
            return

        # If cursor is close to the top or bottom edge of the visible rows,
        # update the viewport to show more rows in that direction
        buffer_zone = self.visible_count // 4

        if self.cursor_row < self.visible_start + buffer_zone:
            # Cursor is close to top edge, move viewport up
            new_start = max(0, self.cursor_row - buffer_zone)
            self._update_viewport(new_start)
        elif self.cursor_row >= self.visible_start + self.visible_count - buffer_zone:
            # Cursor is close to bottom edge, move viewport down
            new_start = min(
                len(self.virtual_rows) - self.visible_count,
                self.cursor_row - self.visible_count + buffer_zone,
            )
            self._update_viewport(new_start)

    def _update_viewport(self, new_start: int) -> None:
        """
        Update the viewport to show rows starting from new_start.

        Args:
            new_start: New starting index for visible rows
        """
        # Ensure new_start is within valid range
        new_start = max(0, min(len(self.virtual_rows) - self.visible_count, new_start))

        if new_start != self.visible_start:
            # Save current cursor position relative to visible rows
            current_key = None
            if self.cursor_row is not None:
                row_index = self.cursor_row
                if 0 <= row_index < self.row_count:
                    current_key = self.get_row_at(row_index)[0]

            # Update visible range and re-render
            self.visible_start = new_start
            self._render_visible_rows()

            # Restore cursor position if possible
            if current_key is not None:
                for i, row in enumerate(self.rows):
                    if row[0] == current_key:
                        self.cursor_row = i
                        break
