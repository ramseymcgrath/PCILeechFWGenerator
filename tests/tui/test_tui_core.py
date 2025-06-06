"""
Test TUI Core Modules

Tests for the TUI core modules (build_orchestrator, config_manager, device_manager, status_monitor).
"""

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from src.tui.core.build_orchestrator import BuildOrchestrator
from src.tui.core.config_manager import ConfigManager

# Import TUI core modules
from src.tui.core.device_manager import DeviceManager
from src.tui.core.status_monitor import StatusMonitor
from src.tui.models.config import BuildConfiguration
from src.tui.models.device import PCIDevice
from src.tui.models.progress import BuildProgress, BuildStage


class TestDeviceManager:
    """Test DeviceManager class"""

    @pytest.mark.unit
    def test_device_manager_init(self):
        """Test DeviceManager initialization"""
        manager = DeviceManager()

        assert manager._device_cache == []
        assert isinstance(manager._vendor_db, dict)
        assert "8086" in manager._vendor_db  # Intel
        assert "10de" in manager._vendor_db  # NVIDIA

    @pytest.mark.unit
    def test_vendor_database_loading(self):
        """Test vendor database loading"""
        manager = DeviceManager()

        # Check some known vendors
        assert manager._vendor_db["8086"] == "Intel Corporation"
        assert manager._vendor_db["10de"] == "NVIDIA Corporation"
        assert manager._vendor_db["1002"] == "Advanced Micro Devices"

    @pytest.mark.unit
    @patch("src.tui.core.device_manager.DeviceManager._get_raw_devices")
    @patch("src.tui.core.device_manager.DeviceManager._enhance_device_info")
    async def test_scan_devices_success(self, mock_enhance, mock_get_raw):
        """Test successful device scanning"""
        # Mock raw device data
        raw_devices = [
            {
                "bdf": "0000:03:00.0",
                "ven": "8086",
                "dev": "10d3",
                "class": "0200",
                "pretty": "0000:03:00.0 Ethernet controller [0200]: Intel Corporation 82574L [8086:10d3]",
            }
        ]
        mock_get_raw.return_value = raw_devices

        # Mock enhanced device
        enhanced_device = PCIDevice(
            bdf="0000:03:00.0",
            vendor_id="8086",
            device_id="10d3",
            vendor_name="Intel Corporation",
            device_name="82574L",
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
        mock_enhance.return_value = enhanced_device

        manager = DeviceManager()
        devices = await manager.scan_devices()

        assert len(devices) == 1
        assert devices[0].bdf == "0000:03:00.0"
        assert devices[0].vendor_name == "Intel Corporation"
        assert manager._device_cache == devices

    @pytest.mark.unit
    @patch("src.tui.core.device_manager.DeviceManager._get_raw_devices")
    async def test_scan_devices_failure(self, mock_get_raw):
        """Test device scanning failure"""
        mock_get_raw.side_effect = Exception("Scan failed")

        manager = DeviceManager()

        with pytest.raises(RuntimeError, match="Failed to scan PCIe devices"):
            await manager.scan_devices()

    @pytest.mark.unit
    def test_extract_device_name(self):
        """Test device name extraction from lspci output"""
        manager = DeviceManager()

        # Test normal case
        pretty = "0000:03:00.0 Ethernet controller [0200]: Intel Corporation 82574L Gigabit Network Connection [8086:10d3]"
        name = manager._extract_device_name(pretty)
        assert name == "Intel Corporation 82574L Gigabit Network Connection"

        # Test fallback case
        pretty = "0000:03:00.0 Network controller [0280]: Some Device"
        name = manager._extract_device_name(pretty)
        assert name == "Some Device"

        # Test unknown case
        pretty = "0000:03:00.0 Unknown device"
        name = manager._extract_device_name(pretty)
        assert name == "Unknown Device"

    @pytest.mark.unit
    def test_assess_device_suitability(self):
        """Test device suitability assessment"""
        manager = DeviceManager()

        # Test network device (good)
        score, issues = manager._assess_device_suitability(
            "0200",  # Network controller
            None,  # No driver
            [{"index": 0, "size": 131072, "type": "memory"}],  # Good BARs
        )
        assert score > 0.8
        assert len(issues) == 0

        # Test device with driver bound
        score, issues = manager._assess_device_suitability(
            "0200",
            "e1000e",  # Driver bound
            [{"index": 0, "size": 131072, "type": "memory"}],
        )
        assert score < 1.0
        assert any("bound to e1000e" in issue for issue in issues)

        # Test device with no BARs
        score, issues = manager._assess_device_suitability("0200", None, [])  # No BARs
        assert score < 0.8
        assert any("No memory BARs" in issue for issue in issues)

    @pytest.mark.unit
    def test_cached_operations(self):
        """Test cached device operations"""
        manager = DeviceManager()

        # Test empty cache
        assert manager.get_cached_devices() == []
        assert manager.find_device_by_bdf("0000:03:00.0") is None
        assert manager.get_suitable_devices() == []

        # Add device to cache
        device = PCIDevice(
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
        manager._device_cache = [device]

        # Test cache operations
        cached = manager.get_cached_devices()
        assert len(cached) == 1
        assert cached[0].bdf == "0000:03:00.0"

        found = manager.find_device_by_bdf("0000:03:00.0")
        assert found is not None
        assert found.bdf == "0000:03:00.0"

        suitable = manager.get_suitable_devices()
        assert len(suitable) == 1


class TestConfigManager:
    """Test ConfigManager class"""

    @pytest.mark.unit
    def test_config_manager_init(self):
        """Test ConfigManager initialization"""
        manager = ConfigManager()

        assert manager.config_dir.exists()
        assert manager._current_config is None

    @pytest.mark.unit
    def test_current_config_management(self):
        """Test current configuration management"""
        manager = ConfigManager()

        # Test getting default config
        config = manager.get_current_config()
        assert isinstance(config, BuildConfiguration)
        assert config.board_type == "75t"

        # Test setting current config
        new_config = BuildConfiguration(board_type="100t", name="Test Config")
        manager.set_current_config(new_config)

        current = manager.get_current_config()
        assert current.board_type == "100t"
        assert current.name == "Test Config"
        assert current.last_used is not None

    @pytest.mark.unit
    def test_create_default_profiles(self):
        """Test default profile creation"""
        with TemporaryDirectory() as temp_dir:
            manager = ConfigManager()
            manager.config_dir = Path(temp_dir)

            manager.create_default_profiles()

            # Check that profile files were created
            profile_files = list(manager.config_dir.glob("*.json"))
            assert len(profile_files) >= 4  # At least 4 default profiles

            # Check specific profiles exist
            profiles = manager.list_profiles()
            profile_names = [p["name"] for p in profiles]
            assert "Network Device Standard" in profile_names
            assert "Storage Device Optimized" in profile_names

    @pytest.mark.unit
    def test_save_and_load_profile(self):
        """Test profile save and load operations"""
        with TemporaryDirectory() as temp_dir:
            manager = ConfigManager()
            manager.config_dir = Path(temp_dir)

            # Create test configuration
            config = BuildConfiguration(
                name="Test Profile",
                description="Test configuration",
                board_type="100t",
                device_type="storage",
            )

            # Save profile
            manager.save_profile("Test Profile", config)

            # Check file was created
            profile_file = manager.config_dir / "Test_Profile.json"
            assert profile_file.exists()

            # Test loading profile
            loaded_config = manager.load_profile("Test Profile")
            assert loaded_config.name == "Test Profile"
            assert loaded_config.board_type == "100t"
            assert loaded_config.device_type == "storage"

    @pytest.mark.unit
    def test_profile_operations(self):
        """Test profile operations"""
        with TemporaryDirectory() as temp_dir:
            manager = ConfigManager()
            manager.config_dir = Path(temp_dir)

            # Test profile existence check
            assert not manager.profile_exists("Non-existent")

            # Add a profile
            config = BuildConfiguration(name="Test", board_type="35t")
            manager.save_profile("Test", config)

            # Test profile exists
            assert manager.profile_exists("Test")

            # Test profile summary
            summary = manager.get_profile_summary("Test")
            assert summary["name"] == "Test"
            assert summary["board_type"] == "35t"

    @pytest.mark.unit
    def test_list_profiles(self):
        """Test profile listing"""
        with TemporaryDirectory() as temp_dir:
            manager = ConfigManager()
            manager.config_dir = Path(temp_dir)

            # Empty initially
            profiles = manager.list_profiles()
            assert profiles == []

            # Add profiles
            config1 = BuildConfiguration(name="Profile 1")
            config2 = BuildConfiguration(name="Profile 2")
            manager.save_profile("Profile 1", config1)
            manager.save_profile("Profile 2", config2)

            # Check listing
            profiles = manager.list_profiles()
            assert len(profiles) == 2
            profile_names = [p["name"] for p in profiles]
            assert "Profile 1" in profile_names
            assert "Profile 2" in profile_names

    @pytest.mark.unit
    def test_delete_profile(self):
        """Test profile deletion"""
        with TemporaryDirectory() as temp_dir:
            manager = ConfigManager()
            manager.config_dir = Path(temp_dir)

            # Add a profile
            config = BuildConfiguration(name="To Delete")
            manager.save_profile("To Delete", config)

            # Verify it exists
            assert manager.profile_exists("To Delete")

            # Delete it
            success = manager.delete_profile("To Delete")
            assert success is True

            # Verify it's gone
            assert not manager.profile_exists("To Delete")

            # Test deleting non-existent profile
            success = manager.delete_profile("Non-existent")
            assert success is False

    @pytest.mark.unit
    def test_config_validation(self):
        """Test configuration validation"""
        manager = ConfigManager()

        # Valid configuration
        valid_config = BuildConfiguration()
        issues = manager.validate_config(valid_config)
        assert len(issues) == 0

        # Invalid configuration
        invalid_config = BuildConfiguration(
            behavior_profiling=True, profile_duration=5.0  # Too short
        )
        issues = manager.validate_config(invalid_config)
        assert len(issues) > 0
        assert any("10 seconds" in issue for issue in issues)


class TestBuildOrchestrator:
    """Test BuildOrchestrator class"""

    @pytest.mark.unit
    def test_build_orchestrator_init(self):
        """Test BuildOrchestrator initialization"""
        orchestrator = BuildOrchestrator()

        assert orchestrator._current_progress is None
        assert orchestrator._build_process is None
        assert orchestrator._progress_callback is None
        assert orchestrator._is_building is False
        assert orchestrator._should_cancel is False

    @pytest.mark.unit
    def test_progress_management(self):
        """Test progress management"""
        orchestrator = BuildOrchestrator()

        # Test getting current progress
        progress = orchestrator.get_current_progress()
        assert progress is None

        # Test building status
        assert not orchestrator.is_building()

    @pytest.mark.unit
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._validate_environment")
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._analyze_device")
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._extract_registers")
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._generate_systemverilog")
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._run_vivado_synthesis")
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._generate_bitstream")
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._ensure_git_repo")
    async def test_start_build_success(
        self,
        mock_ensure_git,
        mock_bitstream,
        mock_vivado,
        mock_sv,
        mock_registers,
        mock_analyze,
        mock_validate,
    ):
        """Test successful build start"""
        orchestrator = BuildOrchestrator()

        # Mock all build stages to succeed
        mock_validate.return_value = None
        mock_analyze.return_value = None
        mock_registers.return_value = None
        mock_sv.return_value = None
        mock_vivado.return_value = None
        mock_bitstream.return_value = None
        mock_ensure_git.return_value = None

        device = PCIDevice(
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

        config = BuildConfiguration(name="Test Build")

        # Mock progress callback
        progress_updates = []

        def progress_callback(progress):
            progress_updates.append(progress)

        result = await orchestrator.start_build(device, config, progress_callback)

        assert result is True
        assert not orchestrator.is_building()  # Should be done
        assert len(progress_updates) > 0  # Should have received progress updates

    @pytest.mark.unit
    async def test_build_already_running(self):
        """Test starting build when already running"""
        orchestrator = BuildOrchestrator()
        orchestrator._is_building = True

        device = PCIDevice(
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

        config = BuildConfiguration()

        with pytest.raises(RuntimeError, match="Build already in progress"):
            await orchestrator.start_build(device, config)

    @pytest.mark.unit
    async def test_cancel_build(self):
        """Test build cancellation"""
        orchestrator = BuildOrchestrator()

        # Mock running build process
        mock_process = MagicMock()
        mock_process.terminate = MagicMock()
        mock_process.kill = MagicMock()
        mock_process.returncode = None
        orchestrator._build_process = mock_process

        await orchestrator.cancel_build()

        assert orchestrator._should_cancel is True
        mock_process.terminate.assert_called_once()
    
    @pytest.mark.unit
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._run_command")
    async def test_ensure_git_repo(self, mock_run_command, mock_makedirs, mock_exists):
        """Test git repository cloning and updating"""
        orchestrator = BuildOrchestrator()
        
        # Mock progress tracking
        orchestrator._current_progress = BuildProgress(
            stage=BuildStage.ENVIRONMENT_VALIDATION,
            completion_percent=0.0,
            current_operation="Testing",
        )
        orchestrator._notify_progress = AsyncMock()
        
        # Case 1: Repository doesn't exist yet
        mock_exists.return_value = False
        mock_run_command.return_value = MagicMock(returncode=0, stdout="Cloning into...")
        
        await orchestrator._ensure_git_repo()
        
        # Should create cache directory and clone repo
        mock_makedirs.assert_called_once()
        mock_run_command.assert_called_once()
        assert "git clone" in mock_run_command.call_args[0][0]
        
        # Case 2: Repository exists but needs update
        mock_exists.return_value = True
        mock_run_command.reset_mock()
        mock_makedirs.reset_mock()
        
        # Mock last update file to be old
        with patch("builtins.open", mock_open(read_data="2020-01-01T00:00:00")):
            with patch("os.chdir"):
                await orchestrator._ensure_git_repo()
                
                # Should not create directory but should run git pull
                mock_makedirs.assert_called_once()
                mock_run_command.assert_called_once()
                assert "git pull" in mock_run_command.call_args[0][0]


class TestStatusMonitor:
    """Test StatusMonitor class"""

    @pytest.mark.unit
    def test_status_monitor_init(self):
        """Test StatusMonitor initialization"""
        monitor = StatusMonitor()

        assert monitor._status_cache == {}
        assert monitor._monitoring is False

    @pytest.mark.unit
    @patch("shutil.which")
    @patch("src.tui.core.status_monitor.StatusMonitor._run_command")
    async def test_check_podman_status(self, mock_run_command, mock_which):
        """Test Podman status checking"""
        monitor = StatusMonitor()

        # Test Podman available
        mock_which.return_value = "/usr/bin/podman"
        mock_run_command.return_value = MagicMock(
            returncode=0, stdout='{"version": "4.0.0"}'
        )

        status = await monitor._check_podman_status()
        assert status["status"] == "ready"

        # Test Podman not found
        mock_which.return_value = None
        status = await monitor._check_podman_status()
        assert status["status"] == "not_found"

    @pytest.mark.unit
    @patch("os.path.exists")
    @patch("src.tui.core.status_monitor.StatusMonitor._run_command")
    async def test_check_vivado_status(self, mock_run_command, mock_exists):
        """Test Vivado status checking"""
        monitor = StatusMonitor()

        # Test Vivado detected
        mock_exists.return_value = True
        mock_run_command.return_value = MagicMock(returncode=0, stdout="Vivado v2023.1")

        status = await monitor._check_vivado_status()
        assert status["status"] == "detected"

        # Test Vivado not found
        mock_exists.return_value = False
        status = await monitor._check_vivado_status()
        assert status["status"] == "not_found"

    @pytest.mark.unit
    @patch("psutil.disk_usage")
    async def test_get_disk_space(self, mock_disk_usage):
        """Test disk space checking"""
        monitor = StatusMonitor()

        # Mock disk usage (total, used, free) in bytes
        mock_usage = MagicMock()
        mock_usage.total = 1000000000000  # 1TB
        mock_usage.used = 500000000000  # 500GB
        mock_usage.free = 500000000000  # 500GB
        mock_disk_usage.return_value = mock_usage

        status = await monitor._get_disk_space()

        assert status["free_gb"] == 465.7  # 500GB in GiB
        assert status["total_gb"] == 931.3  # 1TB in GiB
        assert status["used_percent"] == 50.0

    @pytest.mark.unit
    @patch("os.geteuid")
    async def test_check_root_access(self, mock_geteuid):
        """Test root access checking"""
        monitor = StatusMonitor()

        # Test as root
        mock_geteuid.return_value = 0
        status = await monitor._check_root_access()
        assert status["available"] is True

        # Test as regular user
        mock_geteuid.return_value = 1000
        status = await monitor._check_root_access()
        assert status["available"] is False

    @pytest.mark.unit
    @patch("src.tui.core.status_monitor.StatusMonitor._check_podman_status")
    @patch("src.tui.core.status_monitor.StatusMonitor._check_vivado_status")
    @patch("src.tui.core.status_monitor.StatusMonitor._get_usb_device_count")
    @patch("src.tui.core.status_monitor.StatusMonitor._get_disk_space")
    @patch("src.tui.core.status_monitor.StatusMonitor._check_root_access")
    @patch("src.tui.core.status_monitor.StatusMonitor._check_container_image")
    @patch("src.tui.core.status_monitor.StatusMonitor._check_vfio_support")
    @patch("src.tui.core.status_monitor.StatusMonitor._get_resource_usage")
    async def test_get_system_status(
        self,
        mock_resources,
        mock_vfio,
        mock_container,
        mock_root,
        mock_disk,
        mock_usb,
        mock_vivado,
        mock_podman,
    ):
        """Test complete system status gathering"""
        monitor = StatusMonitor()

        # Mock all status checks
        mock_podman.return_value = {"status": "ready"}
        mock_vivado.return_value = {"status": "detected"}
        mock_usb.return_value = {"count": 5}
        mock_disk.return_value = {"free_gb": 100.0}
        mock_root.return_value = {"available": True}
        mock_container.return_value = {"available": True}
        mock_vfio.return_value = {"supported": True}
        mock_resources.return_value = {"cpu_percent": 25.0}

        status = await monitor.get_system_status()

        assert "podman" in status
        assert "vivado" in status
        assert "usb_devices" in status
        assert "disk_space" in status
        assert "root_access" in status
        assert "container_image" in status
        assert "vfio_support" in status
        assert "resources" in status

        assert status["podman"]["status"] == "ready"
        assert status["vivado"]["status"] == "detected"
        assert status["usb_devices"]["count"] == 5
        assert status["disk_space"]["free_gb"] == 100.0
        assert status["root_access"]["available"] is True

    @pytest.mark.unit
    def test_monitoring_control(self):
        """Test monitoring start/stop control"""
        monitor = StatusMonitor()

        # Initially not monitoring
        assert not monitor.is_monitoring()

        # Test stop monitoring
        monitor.stop_monitoring()
        assert not monitor.is_monitoring()

        # Test cached status
        cached = monitor.get_cached_status()
        assert isinstance(cached, dict)

    @pytest.mark.unit
    def test_status_summary(self):
        """Test status summary generation"""
        monitor = StatusMonitor()

        # Mock some status data
        monitor._status_cache = {
            "podman": {"status": "ready"},
            "vivado": {"status": "detected", "version": "2023.1"},
            "usb_devices": {"count": 3},
            "disk_space": {"free_gb": 150.5},
            "root_access": {"available": True},
        }

        summary = monitor.get_status_summary()

        assert "podman" in summary
        assert "vivado" in summary
        assert "usb" in summary
        assert "disk" in summary
        assert "root" in summary

        assert "Ready" in summary["podman"]
        assert "2023.1" in summary["vivado"]
        assert "3 USB" in summary["usb"]
        assert "150.5 GB" in summary["disk"]
        assert "Available" in summary["root"]
