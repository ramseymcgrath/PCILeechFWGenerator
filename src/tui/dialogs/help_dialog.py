from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static

DEFAULT_HELP_TEXT = """
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


class HelpDialog(ModalScreen[bool]):
    """Modal dialog that displays help text."""

    def __init__(self, help_text: Optional[str] = None) -> None:
        super().__init__()
        self.help_text = help_text or DEFAULT_HELP_TEXT

    def compose(self) -> ComposeResult:
        with Container(id="help-dialog"):
            yield Static("📚 PCILeech Help", id="dialog-title")

            with VerticalScroll():
                yield Static(self.help_text, id="help-content")

            with Horizontal(id="dialog-buttons"):
                yield Button("Close", variant="primary", id="close-help")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-help":
            self.dismiss(True)
