"""
Build-related Commands

This module contains command implementations for build-related actions.
"""

from typing import TYPE_CHECKING, Optional

from .command import Command

if TYPE_CHECKING:
    from ...tui.models.config import BuildConfiguration
    from ...tui.models.device import PCIDevice
    from ..main import PCILeechTUI


class StartBuildCommand(Command):
    """Command to start a firmware build process."""

    def __init__(
        self, app: "PCILeechTUI", device: "PCIDevice", config: "BuildConfiguration"
    ) -> None:
        """
        Initialize the command with all required parameters.

        Args:
            app: The main TUI application instance
            device: The device to build firmware for
            config: The build configuration to use
        """
        self.app = app
        self.device = device
        self.config = config
        self._build_id: Optional[str] = None

    async def execute(self) -> bool:
        """
        Start the build process.

        Returns:
            bool: True if the build was started successfully, False otherwise.
        """
        try:
            # Update UI state
            self.app.ui_state.build_in_progress = True

            # Start the build
            self._build_id = await self.app.build_orchestrator.start_build(
                self.device, self.config
            )

            # Update UI elements
            start_btn = self.app.query_one("#start-build", expect_type=self.app.Button)
            stop_btn = self.app.query_one("#stop-build", expect_type=self.app.Button)

            start_btn.disabled = True
            stop_btn.disabled = False

            self.app.notify("Build started successfully", severity="success")
            return bool(self._build_id)
        except Exception as e:
            self.app.notify(f"Failed to start build: {e}", severity="error")
            self.app.ui_state.build_in_progress = False
            return False

    async def undo(self) -> bool:
        """
        Undo the build start by stopping the current build.

        Returns:
            bool: True if the build was stopped successfully, False otherwise.
        """
        if not self._build_id:
            return False

        stop_command = StopBuildCommand(self.app, self._build_id)
        return await stop_command.execute()


class StopBuildCommand(Command):
    """Command to stop a running firmware build process."""

    def __init__(self, app: "PCILeechTUI", build_id: str) -> None:
        """
        Initialize the command with all required parameters.

        Args:
            app: The main TUI application instance
            build_id: The ID of the build to stop
        """
        self.app = app
        self.build_id = build_id

    async def execute(self) -> bool:
        """
        Stop the build process.

        Returns:
            bool: True if the build was stopped successfully, False otherwise.
        """
        try:
            # Call the build orchestrator to stop the build
            success = await self.app.build_orchestrator.stop_build(self.build_id)

            if success:
                # Update UI state
                self.app.ui_state.build_in_progress = False

                # Update UI elements
                start_btn = self.app.query_one(
                    "#start-build", expect_type=self.app.Button
                )
                stop_btn = self.app.query_one(
                    "#stop-build", expect_type=self.app.Button
                )

                start_btn.disabled = self.app.selected_device is None
                stop_btn.disabled = True

                self.app.notify("Build stopped successfully", severity="warning")

            return success
        except Exception as e:
            self.app.notify(f"Failed to stop build: {e}", severity="error")
            return False

    async def undo(self) -> bool:
        """
        Undo the build stop by attempting to resume the build.

        Note: This is often not possible once a build is stopped, but included
        for consistency with the Command pattern.

        Returns:
            bool: True if the build was resumed successfully, False otherwise.
        """
        # Resuming builds is typically not possible once stopped
        self.app.notify("Resuming a stopped build is not supported", severity="warning")
        return False
