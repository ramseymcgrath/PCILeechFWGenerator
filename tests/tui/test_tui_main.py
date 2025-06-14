"""
Test TUI Main Module

Tests for the main TUI entry point and core functionality from src/tui/main.py.
"""

from unittest.mock import MagicMock, patch

import pytest

# Import pytest-asyncio for async test support if available
try:
    import pytest_asyncio

    # Use the real asyncio marker
    asyncio_mark = pytest.mark.asyncio
except ImportError:
    # If pytest_asyncio is not available, create a dummy marker
    # that will be ignored by pytest
    class DummyModule:
        @staticmethod
        def fixture(*args, **kwargs):
            return lambda f: f

    pytest_asyncio = DummyModule()

    # Create a dummy asyncio marker that just returns the function
    def asyncio_mark(f):
        return f


# Import TUI main modules
from src.tui.main import ConfigurationDialog, PCILeechTUI
from src.tui.models.config import BuildConfiguration
from src.tui.models.device import PCIDevice
from src.tui.models.progress import BuildProgress, BuildStage


class TestConfigurationDialog:
    """Test ConfigurationDialog modal"""

    @pytest.mark.unit
    def test_configuration_dialog_init(self):
        """Test ConfigurationDialog initialization"""
        dialog = ConfigurationDialog()

        # Test that dialog can be created
        assert isinstance(dialog, ConfigurationDialog)

    @pytest.mark.unit
    def test_create_config_from_form(self):
        """Test configuration creation from form"""
        dialog = ConfigurationDialog()

        # Mock form widgets
        with patch.object(dialog, "query_one") as mock_query:
            # Mock form field values
            mock_widgets = {
                "#board-type-select": MagicMock(value="100t"),
                "#device-type-select": MagicMock(value="network"),
                "#config-name-input": MagicMock(value="Test Config"),
                "#config-description-input": MagicMock(value="Test description"),
                "#advanced-sv-switch": MagicMock(value=True),
                "#variance-switch": MagicMock(value=False),
                "#profiling-switch": MagicMock(value=True),
                "#power-mgmt-switch": MagicMock(value=True),
                "#error-handling-switch": MagicMock(value=True),
                "#perf-counters-switch": MagicMock(value=False),
                "#flash-after-switch": MagicMock(value=True),
                "#profile-duration-input": MagicMock(value="45.0"),
            }

            def mock_query_side_effect(selector, widget_type=None):
                return mock_widgets.get(selector, MagicMock())

            mock_query.side_effect = mock_query_side_effect

            config = dialog._create_config_from_form()

            assert config.board_type == "100t"
            assert config.device_type == "network"
            assert config.name == "Test Config"
            assert config.description == "Test description"
            assert config.advanced_sv is True
            assert config.enable_variance is False
            assert config.behavior_profiling is True
            assert config.profile_duration == 45.0

    @pytest.mark.unit
    def test_populate_form(self):
        """Test form population with configuration"""
        dialog = ConfigurationDialog()

        config = BuildConfiguration(
            board_type="35t",
            device_type="storage",
            name="Test Profile",
            description="Test profile description",
            advanced_sv=False,
            enable_variance=True,
            behavior_profiling=False,
            power_management=False,
            error_handling=True,
            performance_counters=True,
            flash_after_build=False,
            profile_duration=60.0,
        )

        # Mock form widgets
        mock_widgets = {}
        for field_id in [
            "#board-type-select",
            "#device-type-select",
            "#config-name-input",
            "#config-description-input",
            "#advanced-sv-switch",
            "#variance-switch",
            "#profiling-switch",
            "#power-mgmt-switch",
            "#error-handling-switch",
            "#perf-counters-switch",
            "#flash-after-switch",
            "#profile-duration-input",
        ]:
            mock_widgets[field_id] = MagicMock()

        with patch.object(dialog, "query_one") as mock_query:

            def mock_query_side_effect(selector, widget_type=None):
                return mock_widgets.get(selector, MagicMock())

            mock_query.side_effect = mock_query_side_effect

            dialog._populate_form(config)

            # Verify form fields were set
            mock_widgets["#board-type-select"].value = "35t"
            mock_widgets["#device-type-select"].value = "storage"
            mock_widgets["#config-name-input"].value = "Test Profile"


class TestPCILeechTUI:
    """Test PCILeechTUI main application"""

    @pytest.mark.unit
    def test_tui_app_init(self):
        """Test TUI application initialization"""
        app = PCILeechTUI()

        # Test core services are initialized
        assert app.device_manager is not None
        assert app.config_manager is not None
        assert app.build_orchestrator is not None
        assert app.status_monitor is not None

        # Test initial state
        assert app._devices == []
        assert app._system_status == {}
        assert app.selected_device is None
        assert isinstance(app.current_config, BuildConfiguration)
        assert app.build_progress is None

    @pytest.mark.unit
    def test_app_properties(self):
        """Test app properties and reactive attributes"""
        app = PCILeechTUI()

        # Test CSS and title
        assert app.CSS_PATH == "styles/main.tcss"
        assert app.TITLE == "PCILeech Firmware Generator"
        assert app.SUB_TITLE == "Interactive firmware generation for PCIe devices"

        # Test reactive attributes
        assert hasattr(app, "selected_device")
        assert hasattr(app, "current_config")
        assert hasattr(app, "build_progress")

    @pytest.mark.unit
    @asyncio_mark
    @patch("src.tui.main.PCILeechTUI._scan_devices")
    @patch("src.tui.main.PCILeechTUI._monitor_system_status")
    async def test_initialize_app(self, mock_monitor, mock_scan):
        """Test application initialization"""
        app = PCILeechTUI()

        # Mock async methods
        mock_scan.return_value = None
        mock_monitor.return_value = None

        with patch.object(
            app.config_manager, "create_default_profiles"
        ) as mock_profiles:
            await app._initialize_app()

            mock_profiles.assert_called_once()
            mock_scan.assert_called_once()

    @pytest.mark.unit
    @asyncio_mark
    @patch("src.tui.main.PCILeechTUI._update_device_table")
    async def test_scan_devices(self, mock_update_table):
        """Test device scanning"""
        app = PCILeechTUI()

        # Mock device manager
        mock_devices = [
            PCIDevice(
                bdf="0000:03:00.0",
                vendor_id="8086",
                device_id="10d3",
                vendor_name="Intel Corporation",
                device_name="Network Controller",
                device_class="0200",
                subsystem_vendor="",
                subsystem_device="",
                driver=None,
                iommu_group="13",
                power_state="D0",
                link_speed="2.5 GT/s",
                bars=[],
                suitability_score=0.8,
                compatibility_issues=[],
            )
        ]

        with patch.object(
            app.device_manager, "scan_devices", return_value=mock_devices
        ):
            with patch.object(app, "query_one") as mock_query:
                mock_panel = MagicMock()
                mock_query.return_value = mock_panel

                await app._scan_devices()

                assert app._devices == mock_devices
                mock_update_table.assert_called_once()

    @pytest.mark.unit
    def test_update_device_table(self):
        """Test device table updating"""
        app = PCILeechTUI()

        # Mock devices
        app._devices = [
            PCIDevice(
                bdf="0000:03:00.0",
                vendor_id="8086",
                device_id="10d3",
                vendor_name="Intel Corporation",
                device_name="Network Controller",
                device_class="0200",
                subsystem_vendor="",
                subsystem_device="",
                driver="e1000e",
                iommu_group="13",
                power_state="D0",
                link_speed="2.5 GT/s",
                bars=[],
                suitability_score=0.8,
                compatibility_issues=[],
            )
        ]

        # Mock DataTable widget
        mock_table = MagicMock()
        with patch.object(app, "query_one", return_value=mock_table):
            app._update_device_table()

            mock_table.clear.assert_called_once()
            mock_table.add_row.assert_called_once()

    @pytest.mark.unit
    def test_update_config_display(self):
        """Test configuration display updating"""
        app = PCILeechTUI()

        # Set test configuration
        app.current_config = BuildConfiguration(
            board_type="100t", device_type="network", advanced_sv=True
        )

        # Mock Static widgets
        mock_widgets = {
            "#board-type": MagicMock(),
            "#device-type": MagicMock(),
            "#advanced-features": MagicMock(),
        }

        with patch.object(app, "query_one") as mock_query:

            def mock_query_side_effect(selector, widget_type=None):
                return mock_widgets.get(selector, MagicMock())

            mock_query.side_effect = mock_query_side_effect

            app._update_config_display()

            # Verify updates were called
            mock_widgets["#board-type"].update.assert_called_with("Board Type: 100t")
            mock_widgets["#device-type"].update.assert_called_with(
                "Device Type: network"
            )
            mock_widgets["#advanced-features"].update.assert_called_with(
                "Advanced Features: Enabled"
            )

    @pytest.mark.unit
    def test_update_status_display(self):
        """Test system status display updating"""
        app = PCILeechTUI()

        # Mock system status
        app._system_status = {
            "podman": {"status": "ready"},
            "vivado": {"status": "detected", "version": "2023.1"},
            "usb_devices": {"count": 5},
            "disk_space": {"free_gb": 150.5},
            "root_access": {"available": True},
        }

        # Mock Static widgets
        mock_widgets = {
            "#podman-status": MagicMock(),
            "#vivado-status": MagicMock(),
            "#usb-status": MagicMock(),
            "#disk-status": MagicMock(),
            "#root-status": MagicMock(),
        }

        with patch.object(app, "query_one") as mock_query:

            def mock_query_side_effect(selector, widget_type=None):
                return mock_widgets.get(selector, MagicMock())

            mock_query.side_effect = mock_query_side_effect

            app._update_status_display()

            # Verify status updates
            mock_widgets["#podman-status"].update.assert_called()
            mock_widgets["#vivado-status"].update.assert_called()
            mock_widgets["#usb-status"].update.assert_called()
            mock_widgets["#disk-status"].update.assert_called()
            mock_widgets["#root-status"].update.assert_called()

    @pytest.mark.unit
    def test_update_build_progress(self):
        """Test build progress display updating"""
        app = PCILeechTUI()

        # Set test progress
        app.build_progress = BuildProgress(
            stage=BuildStage.VIVADO_SYNTHESIS,
            completion_percent=75.0,
            current_operation="Running synthesis",
        )
        app.build_progress.update_resource_usage(cpu=50.0, memory=8.0, disk_free=100.0)

        # Mock widgets
        mock_widgets = {
            "#build-status": MagicMock(),
            "#build-progress": MagicMock(),
            "#progress-text": MagicMock(),
            "#resource-usage": MagicMock(),
        }

        with patch.object(app, "query_one") as mock_query:

            def mock_query_side_effect(selector, widget_type=None):
                return mock_widgets.get(selector, MagicMock())

            mock_query.side_effect = mock_query_side_effect

            app._update_build_progress()

            # Verify progress updates
            mock_widgets["#build-status"].update.assert_called()
            mock_widgets["#progress-text"].update.assert_called()
            mock_widgets["#resource-usage"].update.assert_called()

    @pytest.mark.unit
    @asyncio_mark
    @patch("src.tui.main.PCILeechTUI._scan_devices")
    @patch("src.tui.main.PCILeechTUI._start_build")
    @patch("src.tui.main.PCILeechTUI._stop_build")
    @patch("src.tui.main.PCILeechTUI._open_configuration_dialog")
    async def test_button_press_handlers(
        self, mock_config, mock_stop, mock_start, mock_scan
    ):
        """Test button press event handlers"""
        app = PCILeechTUI()

        # Mock button events
        mock_scan.return_value = None
        mock_start.return_value = None
        mock_stop.return_value = None
        mock_config.return_value = None

        # Test refresh devices
        mock_button = MagicMock()
        mock_button.id = "refresh-devices"
        mock_event = MagicMock()
        mock_event.button = mock_button

        await app.on_button_pressed(mock_event)
        mock_scan.assert_called_once()

        # Test start build
        mock_button.id = "start-build"
        await app.on_button_pressed(mock_event)
        mock_start.assert_called_once()

        # Test stop build
        mock_button.id = "stop-build"
        await app.on_button_pressed(mock_event)
        mock_stop.assert_called_once()

        # Test configure
        mock_button.id = "configure"
        await app.on_button_pressed(mock_event)
        mock_config.assert_called_once()

    @pytest.mark.unit
    @asyncio_mark
    async def test_data_table_row_selection(self):
        """Test device table row selection"""
        app = PCILeechTUI()

        # Mock devices
        test_device = PCIDevice(
            bdf="0000:03:00.0",
            vendor_id="8086",
            device_id="10d3",
            vendor_name="Intel Corporation",
            device_name="Network Controller",
            device_class="0200",
            subsystem_vendor="",
            subsystem_device="",
            driver=None,
            iommu_group="13",
            power_state="D0",
            link_speed="2.5 GT/s",
            bars=[],
            suitability_score=0.8,
            compatibility_issues=[],
        )
        app._devices = [test_device]

        # Mock event
        mock_event = MagicMock()
        mock_event.row_key = "0000:03:00.0"

        # Mock button widget
        mock_button = MagicMock()
        with patch.object(app, "query_one", return_value=mock_button):
            await app.on_data_table_row_selected(mock_event)

            assert app.selected_device == test_device
            assert mock_button.disabled is False

    @pytest.mark.unit
    @asyncio_mark
    @patch("src.tui.main.PCILeechTUI._update_build_progress")
    async def test_start_build(self, mock_update_progress):
        """Test build start process"""
        app = PCILeechTUI()

        # Set up test device and config
        test_device = PCIDevice(
            bdf="0000:03:00.0",
            vendor_id="8086",
            device_id="10d3",
            vendor_name="Intel Corporation",
            device_name="Network Controller",
            device_class="0200",
            subsystem_vendor="",
            subsystem_device="",
            driver=None,
            iommu_group="13",
            power_state="D0",
            link_speed="2.5 GT/s",
            bars=[],
            suitability_score=0.8,
            compatibility_issues=[],
        )
        app.selected_device = test_device

        # Mock build orchestrator
        with patch.object(
            app.build_orchestrator, "start_build", return_value=True
        ) as mock_build:
            with patch.object(app, "notify") as mock_notify:
                await app._start_build()

                mock_build.assert_called_once_with(
                    test_device, app.current_config, app._on_build_progress
                )

    @pytest.mark.unit
    @asyncio_mark
    async def test_stop_build(self):
        """Test build stop process"""
        app = PCILeechTUI()

        # Mock build orchestrator
        with patch.object(app.build_orchestrator, "cancel_build") as mock_cancel:
            with patch.object(app, "notify") as mock_notify:
                await app._stop_build()

                mock_cancel.assert_called_once()
                mock_notify.assert_called_once()

    @pytest.mark.unit
    def test_build_progress_callback(self):
        """Test build progress callback"""
        app = PCILeechTUI()

        # Create test progress
        progress = BuildProgress(
            stage=BuildStage.SYSTEMVERILOG_GENERATION,
            completion_percent=50.0,
            current_operation="Generating SystemVerilog",
        )

        # Mock update method
        with patch.object(app, "_update_build_progress") as mock_update:
            app._on_build_progress(progress)

            assert app.build_progress == progress
            mock_update.assert_called_once()

    @pytest.mark.unit
    def test_reactive_watchers(self):
        """Test reactive attribute watchers"""
        app = PCILeechTUI()

        # Test device selection watcher
        test_device = PCIDevice(
            bdf="0000:03:00.0",
            vendor_id="8086",
            device_id="10d3",
            vendor_name="Intel Corporation",
            device_name="Network Controller",
            device_class="0200",
            subsystem_vendor="",
            subsystem_device="",
            driver=None,
            iommu_group="13",
            power_state="D0",
            link_speed="2.5 GT/s",
            bars=[],
            suitability_score=0.8,
            compatibility_issues=[],
        )

        # Mock button widgets
        mock_buttons = {"#start-build": MagicMock(), "#device-details": MagicMock()}

        with patch.object(app, "query_one") as mock_query:

            def mock_query_side_effect(selector, widget_type=None):
                return mock_buttons.get(selector, MagicMock())

            mock_query.side_effect = mock_query_side_effect

            app.watch_selected_device(test_device)

            # Verify buttons were enabled
            assert mock_buttons["#start-build"].disabled is False

    @pytest.mark.unit
    def test_build_progress_watcher(self):
        """Test build progress watcher"""
        app = PCILeechTUI()

        # Create test progress
        progress = BuildProgress(
            stage=BuildStage.VIVADO_SYNTHESIS,
            completion_percent=80.0,
            current_operation="Running synthesis",
        )

        with patch.object(app, "_update_build_progress") as mock_update:
            app.watch_build_progress(progress)

            mock_update.assert_called_once()

    @pytest.mark.unit
    @asyncio_mark
    async def test_open_configuration_dialog(self):
        """Test configuration dialog opening"""
        app = PCILeechTUI()

        # Mock dialog and push_screen
        mock_config = BuildConfiguration(board_type="100t", name="Test")

        with patch.object(app, "push_screen") as mock_push:
            mock_push.return_value = mock_config

            await app._open_configuration_dialog()

            mock_push.assert_called_once()

    @pytest.mark.unit
    @asyncio_mark
    async def test_monitor_system_status(self):
        """Test system status monitoring"""
        app = PCILeechTUI()

        # Mock status monitor
        mock_status = {"podman": {"status": "ready"}, "vivado": {"status": "detected"}}

        with patch.object(
            app.status_monitor, "get_system_status", return_value=mock_status
        ):
            with patch.object(app, "_update_status_display") as mock_update:
                with patch("asyncio.sleep", side_effect=[None, Exception("Stop")]):
                    try:
                        await app._monitor_system_status()
                    except Exception:
                        pass  # Expected to stop the loop

                    assert app._system_status == mock_status
                    mock_update.assert_called()
