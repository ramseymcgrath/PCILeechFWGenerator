from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from textual.app import App
from textual.widgets import Button, DataTable, Input, Select, Static, Switch

from tui.main import ConfigurationDialog, ConfirmationDialog, PCILeechTUI
from tui.models.config import BuildConfiguration
from tui.models.device import PCIDevice
from tui.models.progress import BuildProgress


class MockedApp:
    """Mocked app for testing dialogs"""

    def __init__(self):
        self.current_config = BuildConfiguration()
        self.config_manager = MagicMock()
        self.notify = MagicMock()


@pytest.fixture
def mocked_app():
    return MockedApp()


@pytest.fixture
def confirm_dialog():
    return ConfirmationDialog("Test Title", "Test Message")


@pytest.fixture
def tui_app():
    app = PCILeechTUI()
    # Mock all external dependencies
    app.device_manager = MagicMock()
    app.device_manager.scan_devices = AsyncMock(return_value=[])
    app.config_manager = MagicMock()
    app.config_manager.get_current_config = MagicMock(return_value=BuildConfiguration())
    app.build_orchestrator = MagicMock()
    app.status_monitor = MagicMock()
    app.status_monitor.get_system_status = AsyncMock(return_value={})
    # Mock UI methods since we don't have a real DOM
    app.query_one = MagicMock()
    app.notify = MagicMock()
    app.push_screen = AsyncMock()
    return app


def test_confirmation_dialog_compose():
    """Test that ConfirmationDialog composes correctly"""
    dialog = ConfirmationDialog("Warning Title", "This is a warning message")
    # If this doesn't raise an exception, the dialog composes correctly
    dialog.compose()


def test_configuration_dialog_compose():
    """Test that ConfigurationDialog composes correctly"""
    dialog = ConfigurationDialog()
    # If this doesn't raise an exception, the dialog composes correctly
    dialog.compose()


def test_tui_app_compose():
    """Test that PCILeechTUI composes correctly"""
    app = PCILeechTUI()
    # If this doesn't raise an exception, the app composes correctly
    app.compose()


def test_populate_form(config_dialog, mocked_app):
    """Test form population from configuration"""
    config = BuildConfiguration(
        board_type="pcileech_35t325_x1",
        name="Test Config",
        advanced_sv=True,
        profile_duration=45.0,
    )

    # Mock query_one to return appropriate widgets
    def mock_query_one(selector, widget_type):
        widget = MagicMock(spec=widget_type)
        # Set up Select widget mocks
        if selector == "#board-type-select":
            widget.value = "pcileech_35t325_x1"
        return widget

    config_dialog.query_one.side_effect = mock_query_one

    # Run the method
    config_dialog._populate_form(config)

    # Check calls
    assert config_dialog.query_one.call_count > 0
    board_type_select_calls = [
        call
        for call in config_dialog.query_one.call_args_list
        if call[0][0] == "#board-type-select"
    ]
    assert len(board_type_select_calls) > 0


def test_create_config_from_form(config_dialog):
    """Test creating a configuration from form values"""
    # Mock form elements
    board_select = MagicMock(spec=Select)
    board_select.value = "pcileech_35t325_x1"
    name_input = MagicMock(spec=Input)
    name_input.value = "Test Configuration"
    desc_input = MagicMock(spec=Input)
    desc_input.value = "Test Description"
    advanced_switch = MagicMock(spec=Switch)
    advanced_switch.value = True
    duration_input = MagicMock(spec=Input)
    duration_input.value = "45.0"

    # Set up query_one to return our mocked widgets
    def mock_query_one(selector, widget_type=None):
        if selector == "#board-type-select":
            return board_select
        elif selector == "#config-name-input":
            return name_input
        elif selector == "#config-description-input":
            return desc_input
        elif selector == "#advanced-sv-switch":
            return advanced_switch
        elif selector == "#variance-switch":
            return MagicMock(spec=Switch, value=True)
        elif selector == "#profiling-switch":
            return MagicMock(spec=Switch, value=False)
        elif selector == "#disable-ftrace-switch":
            return MagicMock(spec=Switch, value=False)
        elif selector == "#power-mgmt-switch":
            return MagicMock(spec=Switch, value=True)
        elif selector == "#error-handling-switch":
            return MagicMock(spec=Switch, value=True)
        elif selector == "#perf-counters-switch":
            return MagicMock(spec=Switch, value=True)
        elif selector == "#flash-after-switch":
            return MagicMock(spec=Switch, value=False)
        elif selector == "#donor-dump-switch":
            return MagicMock(spec=Switch, value=True)
        elif selector == "#auto-headers-switch":
            return MagicMock(spec=Switch, value=False)
        elif selector == "#local-build-switch":
            return MagicMock(spec=Switch, value=False)
        elif selector == "#skip-board-check-switch":
            return MagicMock(spec=Switch, value=False)
        elif selector == "#donor-info-file-input":
            return MagicMock(spec=Input, value="")
        elif selector == "#profile-duration-input":
            return duration_input
        return MagicMock()

    config_dialog.query_one.side_effect = mock_query_one

    # Run the method
    config = config_dialog._create_config_from_form()

    # Check configuration values
    assert config.board_type == "pcileech_35t325_x1"
    assert config.name == "Test Configuration"
    assert config.description == "Test Description"
    assert config.advanced_sv is True
    assert config.profile_duration == 45.0


@pytest.mark.asyncio
async def test_confirmation_dialog_buttons(confirm_dialog):
    """Test confirmation dialog button handling"""
    # Create mock button events
    cancel_event = MagicMock()
    cancel_event.button.id = "cancel-confirm"
    confirm_event = MagicMock()
    confirm_event.button.id = "confirm-action"

    # Mock dismiss method
    confirm_dialog.dismiss = MagicMock()

    # Test cancel button
    await confirm_dialog.on_button_pressed(cancel_event)
    confirm_dialog.dismiss.assert_called_with(False)

    # Reset mock and test confirm button
    confirm_dialog.dismiss.reset_mock()
    await confirm_dialog.on_button_pressed(confirm_event)
    confirm_dialog.dismiss.assert_called_with(True)


@pytest.mark.asyncio
async def test_configuration_dialog_buttons(config_dialog):
    """Test configuration dialog button handling"""
    # Create mock button events
    cancel_event = MagicMock()
    cancel_event.button.id = "cancel-config"
    apply_event = MagicMock()
    apply_event.button.id = "apply-config"
    save_event = MagicMock()
    save_event.button.id = "save-config"

    # Mock dismiss method
    config_dialog.dismiss = MagicMock()
    # Mock config creation
    test_config = BuildConfiguration(name="Test Config")
    config_dialog._create_config_from_form = MagicMock(return_value=test_config)

    # Test cancel button
    await config_dialog.on_button_pressed(cancel_event)
    config_dialog.dismiss.assert_called_with(None)

    # Test apply button
    config_dialog.dismiss.reset_mock()
    await config_dialog.on_button_pressed(apply_event)
    config_dialog.dismiss.assert_called_with(test_config)

    # Test save button
    config_dialog.dismiss.reset_mock()
    await config_dialog.on_button_pressed(save_event)
    assert config_dialog.app.config_manager.save_profile.called
    config_dialog.dismiss.assert_called_with(test_config)


@pytest.mark.asyncio
async def test_scan_devices(tui_app):
    """Test device scanning functionality"""
    # Create a mock device
    mock_device = MagicMock(spec=PCIDevice)
    mock_device.bdf = "0000:00:00.0"
    mock_device.vendor_name = "Test Vendor"
    mock_device.device_name = "Test Device"
    mock_device.status_indicator = "✅"
    mock_device.compact_status = "Valid"
    mock_device.driver = "test_driver"
    mock_device.iommu_group = "1"

    # Configure mock to return our test device
    tui_app.device_manager.scan_devices.return_value = [mock_device]

    # Mock the device table
    mock_table = MagicMock(spec=DataTable)
    tui_app.query_one.return_value = mock_table

    # Mock panel title
    mock_panel_title = MagicMock(spec=Static)
    tui_app.query_one.side_effect = lambda selector, *args: (
        mock_panel_title if selector == "#device-panel .panel-title" else mock_table
    )

    # Run the scan
    await tui_app._scan_devices()

    # Verify the device manager was called
    tui_app.device_manager.scan_devices.assert_called_once()

    # Verify the table was updated
    mock_table.clear.assert_called_once()
    assert mock_table.add_row.called

    # Verify device count in title was updated
    assert mock_panel_title.update.called


@pytest.mark.asyncio
async def test_open_configuration_dialog(tui_app):
    """Test opening configuration dialog"""
    # Mock the result from push_screen
    mock_config = BuildConfiguration(name="Dialog Result")
    tui_app.push_screen.return_value = mock_config

    # Run the method
    await tui_app._open_configuration_dialog()

    # Check that push_screen was called with ConfigurationDialog
    assert tui_app.push_screen.called
    # Check that config was updated
    assert tui_app.current_config == mock_config
    # Check that config manager was updated
    assert tui_app.config_manager.set_current_config.called
    # Check notification
    assert tui_app.notify.called


@pytest.mark.asyncio
async def test_toggle_donor_dump(tui_app):
    """Test toggling donor dump setting"""
    # Set initial state
    initial_config = BuildConfiguration(donor_dump=True, local_build=False)
    tui_app.current_config = initial_config

    # Mock update methods
    tui_app._update_config_display = MagicMock()
    tui_app._update_donor_dump_button = MagicMock()

    # Test disabling donor dump
    await tui_app._toggle_donor_dump()

    # Verify config was updated
    assert tui_app.current_config.donor_dump is False
    assert tui_app.current_config.local_build is True

    # Verify config manager was updated
    tui_app.config_manager.set_current_config.assert_called_once()

    # Verify UI was updated
    assert tui_app._update_config_display.called
    assert tui_app._update_donor_dump_button.called

    # Verify notification
    assert tui_app.notify.called

    # Reset mocks
    tui_app.config_manager.set_current_config.reset_mock()
    tui_app._update_config_display.reset_mock()
    tui_app._update_donor_dump_button.reset_mock()
    tui_app.notify.reset_mock()

    # Test enabling donor dump
    tui_app.current_config = BuildConfiguration(donor_dump=False, local_build=True)
    await tui_app._toggle_donor_dump()

    # Verify config was updated
    assert tui_app.current_config.donor_dump is True
    assert tui_app.current_config.local_build is False


def test_update_build_progress(tui_app):
    """Test updating build progress display"""
    # Create mock progress
    progress = BuildProgress(
        stage="Building",
        status_text="Processing configuration",
        overall_progress=50,
        progress_bar_text="Progress: 50% (3/6 stages)",
        resource_usage={"cpu": 25.5, "memory": 2.1, "disk_free": 10.5},
    )

    # Mock UI elements
    status_text = MagicMock(spec=Static)
    progress_bar = MagicMock(spec=Static)
    progress_text = MagicMock(spec=Static)
    resource_text = MagicMock(spec=Static)

    def mock_query(selector, *args):
        if selector == "#build-status":
            return status_text
        elif selector == "#build-progress":
            return progress_bar
        elif selector == "#progress-text":
            return progress_text
        elif selector == "#resource-usage":
            return resource_text
        return MagicMock()

    tui_app.query_one.side_effect = mock_query

    # Set progress and run update
    tui_app.build_progress = progress
    tui_app._update_build_progress()

    # Verify UI elements were updated
    status_text.update.assert_called_once_with("Status: Processing configuration")
    assert progress_bar.progress == 50
    progress_text.update.assert_called_once_with("Progress: 50% (3/6 stages)")
    assert resource_text.update.called


def test_watch_selected_device(tui_app):
    """Test device selection reactive watcher"""
    # Create mock device
    mock_device = MagicMock(spec=PCIDevice)
    mock_device.bdf = "0000:00:00.0"
    mock_device.display_name = "Test Device"

    # Mock methods
    tui_app._update_compatibility_display = MagicMock()
    tui_app._clear_compatibility_display = MagicMock()

    # Test with device selected
    tui_app.watch_selected_device(mock_device)
    assert (
        tui_app.sub_title == f"Selected: {mock_device.bdf} - {mock_device.display_name}"
    )
    tui_app._update_compatibility_display.assert_called_once_with(mock_device)

    # Test with no device
    tui_app.watch_selected_device(None)
    assert tui_app.sub_title == "Interactive firmware generation for PCIe devices"
    tui_app._clear_compatibility_display.assert_called_once()


@pytest.mark.asyncio
async def test_start_build(tui_app):
    """Test starting the build process"""
    # Create mock device
    mock_device = MagicMock(spec=PCIDevice)
    mock_device.bdf = "0000:00:00.0"
    mock_device.is_suitable = True
    tui_app.selected_device = mock_device

    # Mock buttons
    start_button = MagicMock(spec=Button)
    stop_button = MagicMock(spec=Button)

    def mock_query(selector, *args):
        if selector == "#start-build":
            return start_button
        elif selector == "#stop-build":
            return stop_button
        return MagicMock()

    tui_app.query_one.side_effect = mock_query

    # Mock build orchestrator
    tui_app.build_orchestrator.is_building.return_value = False
    tui_app.build_orchestrator.start_build.return_value = True

    # Mock donor module check to return "installed" status
    tui_app._check_donor_module_status = AsyncMock(return_value={"status": "installed"})

    # Run the build
    await tui_app._start_build()

    # Verify buttons were updated
    assert start_button.disabled is True
    assert stop_button.disabled is False

    # Verify build was started
    assert tui_app.build_orchestrator.start_build.called

    # Verify success notification
    tui_app.notify.assert_called_with(
        "Build completed successfully!", severity="success"
    )


@pytest.mark.asyncio
async def test_stop_build(tui_app):
    """Test stopping the build process"""
    # Run the method
    await tui_app._stop_build()

    # Verify build was cancelled
    tui_app.build_orchestrator.cancel_build.assert_called_once()

    # Verify notification
    tui_app.notify.assert_called_with("Build cancelled", severity="info")


@pytest.mark.asyncio
async def test_check_donor_module_status(tui_app):
    """Test checking donor module status"""
    # Mock the donor dump manager
    mock_manager = MagicMock()
    mock_manager.check_module_installation.return_value = {
        "status": "installed",
        "details": "Module is properly installed",
        "issues": [],
        "fixes": [],
    }

    # Mock sys.path.append and import
    with patch("sys.path.append"), patch.dict(
        "sys.modules",
        {
            "file_management.donor_dump_manager": MagicMock(),
        },
    ), patch(
        "file_management.donor_dump_manager.DonorDumpManager", return_value=mock_manager
    ):

        # Run the check
        result = await tui_app._check_donor_module_status(show_notification=True)

        # Verify manager was called
        assert mock_manager.check_module_installation.called

        # Verify system status was updated
        assert "donor_module" in tui_app._system_status

        # Verify notification was shown
        assert tui_app.notify.called

        # Verify correct result
        assert result["status"] == "installed"


def test_update_donor_dump_button(tui_app):
    """Test updating donor dump button state"""
    # Mock the button
    button = MagicMock(spec=Button)
    tui_app.query_one.return_value = button

    # Test with donor dump enabled
    tui_app.current_config.donor_dump = True
    tui_app._update_donor_dump_button()
    assert button.label == "🚫 Disable Donor Dump"
    assert button.variant == "error"

    # Test with donor dump disabled
    tui_app.current_config.donor_dump = False
    tui_app._update_donor_dump_button()
    assert button.label == "🎯 Enable Donor Dump"
    assert button.variant == "success"
