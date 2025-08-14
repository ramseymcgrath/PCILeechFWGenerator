"""
Device Details Dialog

Dialog for displaying detailed device information.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static, TabbedContent, TabPane

if TYPE_CHECKING:
    from textual.app import App

    from ...tui.models.device import PCIDevice


class DeviceDetailsDialog(ModalScreen[bool]):
    """Modal dialog for displaying detailed device information"""

    def __init__(self, device: "PCIDevice") -> None:
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
