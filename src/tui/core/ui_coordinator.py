"""
UI Coordinator for PCILeech TUI

Coordinates UI operations and business logic for the PCILeech TUI application.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..models.config import BuildConfiguration
from ..models.device import PCIDevice
from ..models.progress import BuildProgress


class UICoordinator:
    """
    Coordinates UI operations and business logic for the PCILeech TUI application.

    This class separates UI logic from business logic, making the application more
    maintainable and testable. It orchestrates interactions between the user interface
    and the underlying services.
    """

    def __init__(self, app):
        """
        Initialize the UI coordinator with the app and services.

        Args:
            app: The main TUI application instance
        """
        self.app = app
        self.device_manager = app.device_manager
        self.config_manager = app.config_manager
        self.build_orchestrator = app.build_orchestrator
        self.status_monitor = app.status_monitor

    # Device Selection and Management

    async def handle_device_selection(self, device: PCIDevice) -> None:
        """
        Handle device selection events

        Args:
            device: The selected device
        """
        # Update app state
        self.app.app_state.set_selected_device(device)
        self._update_compatibility_display(device)

        # Enable relevant buttons
        self._update_buttons_for_device_selection(device)

        # Notify user
        self.app.notify(f"Selected device: {device.bdf}", severity="info")

    async def scan_devices(self) -> List[PCIDevice]:
        """
        Scan for PCIe devices and update the UI

        Returns:
            List of discovered devices
        """
        try:
            devices = await self.device_manager.scan_devices()
            # Update app state instead of directly modifying app._devices
            self.app.app_state.set_devices(devices)
            self.apply_device_filters()
            self.update_device_table()

            # Update device count in title
            self._update_device_panel_title()

            return devices
        except Exception as e:
            if hasattr(self.app, "error_handler"):
                self.app.error_handler.handle_operation_error("scanning devices", e)
            else:
                self.app.notify(f"Failed to scan devices: {e}", severity="error")
            return []

    def apply_device_filters(self) -> None:
        """Apply current filters to device list"""
        # The filtering logic is now in PCILeechTUI.filtered_devices property
        # This method is kept for backwards compatibility, but delegates to the app state
        # Update the filters in the app state from the current UI
        try:
            search_text = self.app.query_one("#quick-search").value.lower()
            current_filters = (
                self.app.device_filters.copy() if self.app.device_filters else {}
            )

            if search_text:
                current_filters["search_text"] = search_text

            # Update app state with filters
            self.app.app_state.set_filters(current_filters)
        except Exception:
            pass  # Ignore if search widget not ready

    def update_device_table(self) -> None:
        """Update the device table with current filtered devices"""
        device_table = self.app.query_one("#device-table")
        device_table.clear()

        # Use the app's filtered_devices property which uses app_state
        for device in self.app.filtered_devices:
            device_table.add_row(
                device.status_indicator,
                device.bdf,
                f"{device.vendor_name} {device.device_name}"[:40],
                device.compact_status,
                device.driver or "None",
                device.iommu_group,
                key=device.bdf,
            )

    def _update_device_panel_title(self) -> None:
        """Update the device panel title with device count"""
        # Use the app's properties which use app_state
        device_count = len(self.app.filtered_devices)
        total_count = len(self.app.devices)
        device_panel = self.app.query_one("#device-panel .panel-title")

        if device_count == total_count:
            device_panel.update(f"📡 PCIe Devices Found: {device_count}")
        else:
            device_panel.update(
                f"📡 PCIe Devices: {device_count}/{total_count} (filtered)"
            )

    def _update_buttons_for_device_selection(self, device: PCIDevice) -> None:
        """
        Update button states based on device selection

        Args:
            device: The selected device
        """
        try:
            self.app.query_one("#device-details").disabled = False
            self.app.query_one("#start-build").disabled = not device.is_suitable
        except Exception:
            # Ignore if buttons don't exist (e.g., in tests)
            pass

    # Build Orchestration

    async def handle_build_start(self) -> None:
        """
        Start the build process with validation and error handling
        """
        if not self.app.selected_device:
            self.app.notify("Please select a device first", severity="error")
            return

        if self.build_orchestrator.is_building():
            self.app.notify("Build already in progress", severity="warning")
            return

        # Check donor module status before starting build if donor_dump is enabled
        if (
            self.app.current_config.donor_dump
            and not self.app.current_config.local_build
        ):
            await self._validate_donor_module()

        try:
            # Update button states
            self.app.query_one("#start-build").disabled = True
            self.app.query_one("#stop-build").disabled = False

            # Start build with progress callback
            success = await self.build_orchestrator.start_build(
                self.app.selected_device,
                self.app.current_config,
                self._on_build_progress,
            )

            if success:
                self.app.notify("Build completed successfully!", severity="success")
            else:
                self.app.notify("Build was cancelled", severity="warning")

        except Exception as e:
            error_msg = str(e)
            if hasattr(self.app, "error_handler"):
                self.app.error_handler.handle_operation_error("starting build", e)
            else:
                # Check if this is a platform compatibility error
                if (
                    "requires Linux" in error_msg
                    or "platform incompatibility" in error_msg
                    or "only available on Linux" in error_msg
                ):
                    self.app.notify(
                        "Build skipped: Platform compatibility issue (see logs)",
                        severity="warning",
                    )
                else:
                    self.app.notify(f"Build failed: {e}", severity="error")
        finally:
            # Reset button states
            self.app.query_one("#start-build").disabled = False
            self.app.query_one("#stop-build").disabled = True

    async def handle_build_stop(self) -> None:
        """Stop the current build process"""
        await self.build_orchestrator.cancel_build()
        self.app.notify("Build cancelled", severity="info")

    def handle_build_progress(self, progress: BuildProgress) -> None:
        """
        Handle build progress updates

        Args:
            progress: The current build progress
        """
        self.app.app_state.set_build_progress(progress)
        self._update_build_progress_display()

    def _on_build_progress(self, progress: BuildProgress) -> None:
        """
        Callback for build progress updates from build orchestrator

        Args:
            progress: The current build progress
        """
        # Forward to the main handler
        self.handle_build_progress(progress)

    def _update_build_progress_display(self) -> None:
        """Update the UI with current build progress"""
        if not self.app.build_progress:
            return

        progress = self.app.build_progress

        # Update status
        self.app.query_one("#build-status").update(f"Status: {progress.status_text}")

        # Update progress bar
        progress_bar = self.app.query_one("#build-progress")
        progress_bar.progress = progress.overall_progress

        # Update progress text
        self.app.query_one("#progress-text").update(progress.progress_bar_text)

        # Update resource usage
        if progress.resource_usage:
            cpu = progress.resource_usage.get("cpu", 0)
            memory = progress.resource_usage.get("memory", 0)
            disk = progress.resource_usage.get("disk_free", 0)
            resource_text = f"Resources: CPU: {cpu:.1f}% | Memory: {memory:.1f}GB | Disk: {disk:.1f}GB free"
            self.app.query_one("#resource-usage").update(resource_text)

    async def _validate_donor_module(self) -> bool:
        """
        Validate donor module status before starting build

        Returns:
            True if validation passed or user confirmed to continue, False otherwise
        """
        module_status = await self.app._check_donor_module_status(
            show_notification=False
        )

        if module_status and module_status.get("status") != "installed":
            # Show warning dialog with issues and fixes
            self.app.notify(
                "⚠️ Donor module is not properly installed. This may affect the build.",
                severity="warning",
            )

            # Show detailed issues and fixes
            issues = module_status.get("issues", [])
            fixes = module_status.get("fixes", [])

            if issues:
                self.app.notify(f"Issues: {issues[0]}", severity="warning")
            if fixes:
                self.app.notify(
                    f"Suggested fix: {fixes[0]}",
                    severity="information",
                )

            # Ask if user wants to continue anyway
            should_continue = await self.app._confirm_with_warnings(
                "⚠️ Warning: Donor Module Issues",
                "The donor module is not properly installed. This may affect the build. Do you want to continue anyway?",
            )

            if not should_continue:
                self.app.notify("Build cancelled by user", severity="information")
                return False

        return True

    # Configuration Management

    async def handle_configuration_update(self, config: BuildConfiguration) -> None:
        """
        Handle configuration updates from dialogs

        Args:
            config: The updated configuration
        """
        if config is not None:
            # Update app state instead of directly modifying app.current_config
            self.app.app_state.set_config(config)
            # Save the configuration to the config manager
            self.config_manager.set_current_config(config)
            self._update_config_display()
            self.app.notify("Configuration updated successfully", severity="success")

    def _update_config_display(self) -> None:
        """Update configuration display in the UI"""
        config = self.app.current_config

        try:
            self.app.query_one("#board-type").update(f"Board Type: {config.board_type}")

            features = "Enabled" if config.is_advanced else "Basic"
            self.app.query_one("#advanced-features").update(
                f"Advanced Features: {features}"
            )

            if config.local_build:
                build_mode = "Local Build (No Donor Dump)"
            else:
                build_mode = "Standard (With Donor Dump)"
            self.app.query_one("#build-mode").update(f"Build Mode: {build_mode}")

            # Update donor dump button
            self._update_donor_dump_button()
        except Exception as e:
            # Handle any UI update errors gracefully
            if hasattr(self.app, "error_handler"):
                self.app.error_handler.handle_operation_error(
                    "updating configuration display", e
                )
            else:
                print(f"Error updating configuration display: {e}")
                self.app.notify("Error displaying configuration", severity="error")

    def _update_donor_dump_button(self) -> None:
        """Update the donor dump button text and style based on current state"""
        try:
            button = self.app.query_one("#enable-donor-dump")
            if self.app.current_config.donor_dump:
                button.label = "🚫 Disable Donor Dump"
                button.variant = "error"
            else:
                button.label = "🎯 Enable Donor Dump"
                button.variant = "success"
        except Exception:
            # Button might not exist in tests
            pass

    # Compatibility Display

    def _update_compatibility_display(self, device: PCIDevice) -> None:
        """
        Update the compatibility factors display for the selected device

        Args:
            device: The selected device
        """
        # Update title and score
        compatibility_title = self.app.query_one("#compatibility-title")
        compatibility_title.update(f"Device: {device.display_name}")

        compatibility_score = self.app.query_one("#compatibility-score")
        score_text = f"Final Score: [bold]{device.suitability_score:.2f}[/bold]"
        if device.is_suitable:
            score_text = f"[green]{score_text}[/green]"
        else:
            score_text = f"[red]{score_text}[/red]"

        # Add detailed status indicators
        status_indicators = []
        status_indicators.append(f"Valid: {device.validity_indicator}")
        status_indicators.append(f"Driver: {device.driver_indicator}")
        status_indicators.append(f"VFIO: {device.vfio_indicator}")
        status_indicators.append(f"IOMMU: {device.iommu_indicator}")
        status_indicators.append(f"Ready: {device.ready_indicator}")

        status_line = " | ".join(status_indicators)
        score_text += f"\n{status_line}"
        compatibility_score.update(score_text)

        # Update factors table
        factors_table = self.app.query_one("#compatibility-table")
        factors_table.clear()

        # Set up columns if not already done
        if not factors_table.columns:
            factors_table.add_columns("Status Check", "Result", "Details")

        # Add detailed status information
        self._add_detailed_status_rows(factors_table, device)

        # Add compatibility factors if available
        for factor in device.compatibility_factors:
            name = factor["name"]
            adjustment = factor["adjustment"]
            description = factor["description"]

            # Format adjustment with sign and color
            if adjustment > 0:
                adj_text = f"[green]+{adjustment:.1f}[/green]"
            elif adjustment < 0:
                adj_text = f"[red]{adjustment:.1f}[/red]"
            else:
                adj_text = f"{adjustment:.1f}"

            # Add row with appropriate styling
            factors_table.add_row(name, adj_text, description)

    def _add_detailed_status_rows(self, table, device: PCIDevice) -> None:
        """
        Add detailed status information to the compatibility table

        Args:
            table: The DataTable to add rows to
            device: The device to display status for
        """
        # Device validity
        valid_status = (
            "[green]✅ Valid[/green]" if device.is_valid else "[red]❌ Invalid[/red]"
        )
        table.add_row(
            "Device Accessibility",
            valid_status,
            "Device is properly detected and accessible",
        )

        # Driver status
        if device.has_driver:
            if device.is_detached:
                driver_status = "[green]🔓 Detached[/green]"
                driver_details = f"Device detached from {device.driver} for VFIO use"
            else:
                driver_status = "[yellow]🔒 Bound[/yellow]"
                driver_details = f"Device bound to {device.driver} driver"
        else:
            driver_status = "[blue]🔌 No Driver[/blue]"
            driver_details = "No driver currently bound to device"
        table.add_row("Driver Status", driver_status, driver_details)

        # VFIO compatibility
        vfio_status = (
            "[green]🛡️ Compatible[/green]"
            if device.vfio_compatible
            else "[red]❌ Incompatible[/red]"
        )
        vfio_details = (
            "Device supports VFIO passthrough"
            if device.vfio_compatible
            else "Device cannot use VFIO passthrough"
        )
        table.add_row("VFIO Support", vfio_status, vfio_details)

        # IOMMU status
        iommu_status = (
            "[green]🔒 Enabled[/green]"
            if device.iommu_enabled
            else "[red]❌ Disabled[/red]"
        )
        iommu_details = (
            f"IOMMU group: {device.iommu_group}"
            if device.iommu_enabled
            else "IOMMU not properly configured"
        )
        table.add_row("IOMMU Configuration", iommu_status, iommu_details)

        # Overall readiness
        if device.is_valid and device.vfio_compatible and device.iommu_enabled:
            ready_status = "[green]⚡ Ready[/green]"
            ready_details = "Device is ready for firmware generation"
        elif device.is_suitable:
            ready_status = "[yellow]⚠️ Caution[/yellow]"
            ready_details = "Device may work but has some compatibility issues"
        else:
            ready_status = "[red]❌ Not Ready[/red]"
            ready_details = "Device has significant compatibility issues"
        table.add_row("Overall Status", ready_status, ready_details)

    def clear_compatibility_display(self) -> None:
        """Clear the compatibility display when no device is selected"""
        try:
            compatibility_title = self.app.query_one("#compatibility-title")
            compatibility_title.update("Select a device to view compatibility factors")

            compatibility_score = self.app.query_one("#compatibility-score")
            compatibility_score.update("")

            factors_table = self.app.query_one("#compatibility-table")
            factors_table.clear()
        except Exception:
            # Ignore DOM errors in tests or during initialization
            pass

    # Utility Methods

    async def export_device_list(self) -> None:
        """Export current device list to JSON"""
        try:
            devices_data = [device.to_dict() for device in self.app._filtered_devices]
            export_path = Path("pcie_devices.json")

            with open(export_path, "w") as f:
                json.dump(
                    {
                        "export_time": self.app._get_current_timestamp(),
                        "device_count": len(devices_data),
                        "devices": devices_data,
                    },
                    f,
                    indent=2,
                )

            self.app.notify(
                f"Device list exported to {export_path}", severity="success"
            )
        except Exception as e:
            if hasattr(self.app, "error_handler"):
                self.app.error_handler.handle_operation_error(
                    "exporting device list", e
                )
            else:
                self.app.notify(f"Failed to export device list: {e}", severity="error")
