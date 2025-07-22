import pytest

# Import your TUI app
from src.tui.main import PCILeechTUI

# Mark all tests as TUI tests
pytestmark = pytest.mark.tui


@pytest.mark.asyncio
async def test_tui_launch_and_quit():
    """Test that the TUI launches successfully and displays main panels."""
    app = PCILeechTUI()
    async with app.run_test() as pilot:
        await pilot.pause(1.0)  # Allow initialization

        # Check that main panels are displayed
        assert app.query("#device-panel").first() is not None
        assert app.query("#config-panel").first() is not None
        assert app.query("#build-panel").first() is not None
        assert app.query("#status-panel").first() is not None

        # Exit the app
        app.exit()


@pytest.mark.asyncio
async def test_device_scanning():
    """Test PCIe device scanning functionality."""
    app = PCILeechTUI()
    async with app.run_test() as pilot:
        await pilot.pause(1.0)

        # Click the "Refresh" or "Scan Devices" button
        await pilot.click("#refresh-devices")
        await pilot.pause(0.5)

        # Check that device table exists and may have data
        device_table = app.query_one("#device-table")
        assert device_table is not None

        app.exit()


@pytest.mark.asyncio
async def test_configuration_dialog():
    """Test opening and interacting with the configuration dialog."""
    app = PCILeechTUI()
    async with app.run_test() as pilot:
        await pilot.pause(1.0)

        # Click the "Configure" button
        await pilot.click("#configure")
        await pilot.pause(0.5)

        # Verify configuration dialog opened
        config_dialog = app.screen
        assert config_dialog is not None

        # Test board type selection
        board_select = app.query_one("#board-type-select")
        assert board_select is not None

        # Test configuration name input
        await pilot.click("#config-name-input")
        await pilot.type("Test Configuration")

        # Test toggling advanced SystemVerilog switch
        await pilot.click("#advanced-sv-switch")

        # Test toggling variance switch
        await pilot.click("#variance-switch")

        # Cancel the dialog
        await pilot.click("#cancel-config")

        app.exit()


@pytest.mark.asyncio
async def test_donor_dump_configuration():
    """Test donor dump configuration options in the config dialog."""
    app = PCILeechTUI()
    async with app.run_test() as pilot:
        await pilot.pause(1.0)

        # Open configuration dialog
        await pilot.click("#configure")
        await pilot.pause(0.5)

        # Test donor dump switch
        await pilot.click("#donor-dump-switch")

        # Test auto headers switch
        await pilot.click("#auto-headers-switch")

        # Test local build switch
        await pilot.click("#local-build-switch")

        # Test donor info file input
        await pilot.click("#donor-info-file-input")
        await pilot.type("/path/to/donor_info.json")

        # Apply configuration
        await pilot.click("#apply-config")

        app.exit()


@pytest.mark.asyncio
async def test_device_table_selection():
    """Test selecting devices in the device table."""
    app = PCILeechTUI()
    async with app.run_test() as pilot:
        await pilot.pause(1.0)

        # First scan for devices
        await pilot.click("#scan-devices")
        await pilot.pause(0.5)

        # Try to interact with device table
        device_table = app.query_one("#device-table")

        # Navigate the table with arrow keys
        await pilot.click("#device-table")
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("up")

        # Check if start build button state changes based on selection
        start_build_btn = app.query_one("#start-build")
        assert start_build_btn is not None

        app.exit()


@pytest.mark.asyncio
async def test_quick_actions_panel():
    """Test quick actions panel buttons."""
    app = PCILeechTUI()
    async with app.run_test() as pilot:
        await pilot.pause(1.0)

        # Test check donor module button
        await pilot.click("#check-donor-module")
        await pilot.pause(0.5)

        # Test enable donor dump button
        await pilot.click("#enable-donor-dump")
        await pilot.pause(0.5)

        # Test generate donor template button
        await pilot.click("#generate-donor-template")
        await pilot.pause(0.5)

        app.exit()


@pytest.mark.asyncio
async def test_build_workflow_simulation():
    """Test simulating a build workflow (without actual build)."""
    app = PCILeechTUI()
    async with app.run_test() as pilot:
        await pilot.pause(1.0)

        # Step 1: Scan for devices
        await pilot.click("#scan-devices")
        await pilot.pause(0.5)

        # Step 2: Configure build settings
        await pilot.click("#configure")
        await pilot.pause(0.5)

        # Select a board type
        board_select = app.query_one("#board-type-select")
        # Note: In real tests, you'd select a specific board value

        # Enable some features
        await pilot.click("#profiling-switch")

        # Apply configuration
        await pilot.click("#apply-config")
        await pilot.pause(0.5)

        # Step 3: Try to start build (will likely be disabled without valid device)
        start_build_btn = app.query_one("#start-build")
        # In a real scenario, this would start the build process

        app.exit()


@pytest.mark.asyncio
async def test_profile_management():
    """Test configuration profile save/load functionality."""
    app = PCILeechTUI()
    async with app.run_test() as pilot:
        await pilot.pause(1.0)

        # Open configuration dialog
        await pilot.click("#configure")
        await pilot.pause(0.5)

        # Modify some settings
        await pilot.click("#config-name-input")
        await pilot.type("Test Profile")

        # Save as profile
        await pilot.click("#save-config")
        await pilot.pause(0.5)

        # Test load profile button from main UI
        await pilot.click("#load-profile")

        app.exit()


@pytest.mark.asyncio
async def test_system_status_monitoring():
    """Test that system status indicators are displayed."""
    app = PCILeechTUI()
    async with app.run_test() as pilot:
        await pilot.pause(2.0)  # Allow time for status checks

        # Check that status indicators exist
        podman_status = app.query_one("#podman-status")
        vivado_status = app.query_one("#vivado-status")
        usb_status = app.query_one("#usb-status")
        disk_status = app.query_one("#disk-status")
        root_status = app.query_one("#root-status")

        assert podman_status is not None
        assert vivado_status is not None
        assert usb_status is not None
        assert disk_status is not None
        assert root_status is not None

        app.exit()
