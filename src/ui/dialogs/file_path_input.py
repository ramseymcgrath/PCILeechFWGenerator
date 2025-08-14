"""
File Path Input Dialog

Modal dialog for file path input.
"""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


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
