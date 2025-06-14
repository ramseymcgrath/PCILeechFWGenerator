"""
Test TUI Data Models

Tests for the TUI data models (config, device, error, progress).
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# Import TUI models
from src.tui.models.config import BuildConfiguration
from src.tui.models.device import PCIDevice
from src.tui.models.error import ErrorSeverity, ErrorTemplates, TUIError
from src.tui.models.progress import BuildProgress, BuildStage


class TestBuildConfiguration:
    """Test BuildConfiguration model"""

    @pytest.mark.unit
    def test_default_configuration(self):
        """Test default configuration creation"""
        config = BuildConfiguration()

        assert config.board_type == "75t"
        assert config.device_type == "generic"
        assert config.advanced_sv is True
        assert config.enable_variance is True
        assert config.behavior_profiling is False
        assert config.profile_duration == 30.0
        assert config.power_management is True
        assert config.error_handling is True
        assert config.performance_counters is True
        assert config.flash_after_build is False
        assert config.name == "Default Configuration"
        assert config.description == "Standard configuration for PCIe devices"

    @pytest.mark.unit
    def test_configuration_validation(self):
        """Test configuration validation"""
        # Test invalid board type
        with pytest.raises(ValueError, match="Invalid board type"):
            BuildConfiguration(board_type="invalid")

        # Test invalid device type
        with pytest.raises(ValueError, match="Invalid device type"):
            BuildConfiguration(device_type="invalid")

        # Test invalid profile duration
        with pytest.raises(ValueError, match="Profile duration must be positive"):
            BuildConfiguration(profile_duration=-1.0)

    @pytest.mark.unit
    def test_is_advanced_property(self):
        """Test is_advanced property"""
        # Basic configuration
        config = BuildConfiguration(
            advanced_sv=False,
            enable_variance=False,
            behavior_profiling=False,
            device_type="generic",
        )
        assert not config.is_advanced

        # Advanced configuration
        config = BuildConfiguration(advanced_sv=True)
        assert config.is_advanced

        config = BuildConfiguration(enable_variance=True)
        assert config.is_advanced

        config = BuildConfiguration(behavior_profiling=True)
        assert config.is_advanced

        config = BuildConfiguration(device_type="network")
        assert config.is_advanced

    @pytest.mark.unit
    def test_feature_summary(self):
        """Test feature summary generation"""
        config = BuildConfiguration(
            advanced_sv=False,
            enable_variance=False,
            behavior_profiling=False,
            device_type="generic",
        )
        assert config.feature_summary == "Basic Configuration"

        config = BuildConfiguration(
            advanced_sv=True,
            enable_variance=True,
            behavior_profiling=True,
            device_type="network",
        )
        summary = config.feature_summary
        assert "Advanced SystemVerilog" in summary
        assert "Manufacturing Variance" in summary
        assert "Behavior Profiling" in summary
        assert "Network Optimizations" in summary

    @pytest.mark.unit
    def test_to_cli_args(self):
        """Test CLI arguments conversion"""
        config = BuildConfiguration(
            board_type="100t",
            flash_after_build=True,
            advanced_sv=False,
            device_type="network",
            enable_variance=False,
            power_management=False,
            error_handling=False,
            performance_counters=False,
            profile_duration=60.0,
        )

        args = config.to_cli_args()
        assert args["board"] == "100t"
        assert args["flash"] is True
        assert args["advanced_sv"] is False
        assert args["device_type"] == "network"
        assert args["enable_variance"] is False
        assert args["disable_power_management"] is True
        assert args["disable_error_handling"] is True
        assert args["disable_performance_counters"] is True
        assert args["behavior_profile_duration"] == 60

    @pytest.mark.unit
    def test_serialization(self):
        """Test configuration serialization/deserialization"""
        config = BuildConfiguration(
            name="Test Config",
            description="Test description",
            board_type="35t",
            device_type="storage",
        )

        # Test to_dict
        data = config.to_dict()
        assert data["name"] == "Test Config"
        assert data["board_type"] == "35t"
        assert data["device_type"] == "storage"

        # Test from_dict
        restored = BuildConfiguration.from_dict(data)
        assert restored.name == config.name
        assert restored.board_type == config.board_type
        assert restored.device_type == config.device_type

    @pytest.mark.unit
    def test_file_operations(self):
        """Test file save/load operations"""
        config = BuildConfiguration(name="File Test Config", board_type="100t")

        with TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "test_config.json"

            # Test save
            config.save_to_file(filepath)
            assert filepath.exists()

            # Test load
            loaded = BuildConfiguration.load_from_file(filepath)
            assert loaded.name == config.name
            assert loaded.board_type == config.board_type

    @pytest.mark.unit
    def test_copy(self):
        """Test configuration copying"""
        config = BuildConfiguration(name="Original", board_type="35t")
        copy_config = config.copy()

        assert copy_config.name == config.name
        assert copy_config.board_type == config.board_type
        assert copy_config is not config  # Different objects


class TestPCIDevice:
    """Test PCIDevice model"""

    @pytest.mark.unit
    def test_device_creation(self):
        """Test PCIDevice creation"""
        device = PCIDevice(
            bdf="0000:03:00.0",
            vendor_id="8086",
            device_id="10d3",
            vendor_name="Intel Corporation",
            device_name="82574L Gigabit Network Connection",
            device_class="0200",
            subsystem_vendor="8086",
            subsystem_device="a01",
            driver="e1000e",
            iommu_group="13",
            power_state="D0",
            link_speed="2.5 GT/s",
            bars=[{"index": 0, "size": 131072, "type": "memory"}],
            suitability_score=0.8,
            compatibility_issues=[],
        )

        assert device.bdf == "0000:03:00.0"
        assert device.vendor_name == "Intel Corporation"
        assert device.device_name == "82574L Gigabit Network Connection"

    @pytest.mark.unit
    def test_display_name(self):
        """Test display name property"""
        device = PCIDevice(
            bdf="0000:03:00.0",
            vendor_id="8086",
            device_id="10d3",
            vendor_name="Intel Corporation",
            device_name="82574L Gigabit Network Connection",
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

        assert (device.display_name ==
                "Intel Corporation 82574L Gigabit Network Connection")

    @pytest.mark.unit
    def test_is_suitable(self):
        """Test device suitability assessment"""
        # Suitable device
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
        assert device.is_suitable

        # Unsuitable device (low score)
        device.suitability_score = 0.5
        assert not device.is_suitable

        # Unsuitable device (compatibility issues)
        device.suitability_score = 0.8
        device.compatibility_issues = ["Driver conflict"]
        assert not device.is_suitable

    @pytest.mark.unit
    def test_status_indicator(self):
        """Test status indicator property"""
        # Suitable device without driver
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
        assert device.status_indicator == "✅"

        # Suitable device with driver
        device.driver = "e1000e"
        assert device.status_indicator == "⚠️"

        # Unsuitable device
        device.suitability_score = 0.5
        assert device.status_indicator == "❌"

    @pytest.mark.unit
    def test_serialization(self):
        """Test device serialization"""
        device = PCIDevice(
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
            bars=[{"index": 0, "size": 131072}],
            suitability_score=0.8,
            compatibility_issues=["Driver bound"],
        )

        # Test to_dict
        data = device.to_dict()
        assert data["bd"] == "0000:03:00.0"
        assert data["vendor_name"] == "Intel Corporation"
        assert data["driver"] == "e1000e"

        # Test from_dict
        restored = PCIDevice.from_dict(data)
        assert restored.bdf == device.bdf
        assert restored.vendor_name == device.vendor_name
        assert restored.driver == device.driver


class TestTUIError:
    """Test TUIError model"""

    @pytest.mark.unit
    def test_error_creation(self):
        """Test TUIError creation"""
        error = TUIError(
            severity=ErrorSeverity.ERROR,
            category="device",
            message="Device binding failed",
            details="VFIO binding error",
            suggested_actions=["Check IOMMU", "Verify driver"],
            documentation_link="https://example.com/docs",
            auto_fix_available=True,
        )

        assert error.severity == ErrorSeverity.ERROR
        assert error.category == "device"
        assert error.message == "Device binding failed"
        assert error.auto_fix_available is True

    @pytest.mark.unit
    def test_severity_properties(self):
        """Test severity-related properties"""
        error = TUIError(
            severity=ErrorSeverity.WARNING,
            category="config",
            message="Configuration warning",
        )

        assert error.severity_icon == "⚠️"
        assert error.severity_color == "yellow"
        assert "Warning:" in error.title

    @pytest.mark.unit
    def test_add_action(self):
        """Test adding suggested actions"""
        error = TUIError(
            severity=ErrorSeverity.INFO,
            category="system",
            message="Information message",
        )

        error.add_action("First action")
        error.add_action("Second action")
        error.add_action("First action")  # Duplicate

        assert error.suggested_actions is not None
        assert len(error.suggested_actions) == 2
        assert "First action" in error.suggested_actions
        assert "Second action" in error.suggested_actions

    @pytest.mark.unit
    def test_serialization(self):
        """Test error serialization"""
        error = TUIError(
            severity=ErrorSeverity.CRITICAL,
            category="system",
            message="Critical error",
            suggested_actions=["Action 1", "Action 2"],
        )

        # Test to_dict
        data = error.to_dict()
        assert data["severity"] == "critical"
        assert data["category"] == "system"
        assert data["message"] == "Critical error"

        # Test from_dict
        restored = TUIError.from_dict(data)
        assert restored.severity == ErrorSeverity.CRITICAL
        assert restored.category == error.category
        assert restored.message == error.message


class TestErrorTemplates:
    """Test ErrorTemplates class"""

    @pytest.mark.unit
    def test_vfio_binding_failed(self):
        """Test VFIO binding error template"""
        error = ErrorTemplates.vfio_binding_failed("Test details")

        assert error.severity == ErrorSeverity.ERROR
        assert error.category == "device"
        assert "VFIO binding failed" in error.message
        assert error.details == "Test details"
        assert error.auto_fix_available is True
        assert error.suggested_actions is not None
        assert len(error.suggested_actions) > 0

    @pytest.mark.unit
    def test_container_not_found(self):
        """Test container not found error template"""
        error = ErrorTemplates.container_not_found()

        assert error.severity == ErrorSeverity.ERROR
        assert error.category == "system"
        assert "Container image" in error.message
        assert error.auto_fix_available is True

    @pytest.mark.unit
    def test_insufficient_permissions(self):
        """Test insufficient permissions error template"""
        error = ErrorTemplates.insufficient_permissions()

        assert error.severity == ErrorSeverity.CRITICAL
        assert error.category == "system"
        assert "Insufficient permissions" in error.message
        assert error.details is not None
        assert "Root privileges" in error.details

    @pytest.mark.unit
    def test_build_failed(self):
        """Test build failed error template"""
        error = ErrorTemplates.build_failed("synthesis", "Vivado error")

        assert error.severity == ErrorSeverity.ERROR
        assert error.category == "build"
        assert "synthesis" in error.message
        assert error.details == "Vivado error"

    @pytest.mark.unit
    def test_device_not_suitable(self):
        """Test device not suitable error template"""
        issues = ["Driver bound", "No memory BARs"]
        error = ErrorTemplates.device_not_suitable(issues)

        assert error.severity == ErrorSeverity.WARNING
        assert error.category == "device"
        assert "not be suitable" in error.message
        assert error.details is not None
        assert "Driver bound" in error.details
        assert "No memory BARs" in error.details


class TestBuildProgress:
    """Test BuildProgress model"""

    @pytest.mark.unit
    def test_progress_creation(self):
        """Test BuildProgress creation"""
        progress = BuildProgress(
            stage=BuildStage.DEVICE_ANALYSIS,
            completion_percent=50.0,
            current_operation="Analyzing device registers",
        )

        assert progress.stage == BuildStage.DEVICE_ANALYSIS
        assert progress.completion_percent == 50.0
        assert progress.current_operation == "Analyzing device registers"

    @pytest.mark.unit
    def test_stage_tracking(self):
        """Test stage completion tracking"""
        progress = BuildProgress(
            stage=BuildStage.SYSTEMVERILOG_GENERATION,
            completion_percent=25.0,
            current_operation="Generating SystemVerilog",
        )

        # Initially no stages completed
        assert progress.completed_stages == 0
        assert progress.total_stages == len(BuildStage)

        # Mark some stages complete
        progress.mark_stage_complete(BuildStage.ENVIRONMENT_VALIDATION)
        progress.mark_stage_complete(BuildStage.DEVICE_ANALYSIS)

        assert progress.completed_stages == 2

    @pytest.mark.unit
    def test_overall_progress(self):
        """Test overall progress calculation"""
        progress = BuildProgress(
            stage=BuildStage.SYSTEMVERILOG_GENERATION,
            completion_percent=50.0,
            current_operation="Generating SystemVerilog",
        )

        # Mark first two stages complete
        progress.mark_stage_complete(BuildStage.ENVIRONMENT_VALIDATION)
        progress.mark_stage_complete(BuildStage.DEVICE_ANALYSIS)

        # Should be: (2/6 completed stages) + (0.5/6 current stage progress)
        expected = (2.0 / 6.0 + 0.5 / 6.0) * 100.0
        assert abs(progress.overall_progress - expected) < 0.1

    @pytest.mark.unit
    def test_status_text(self):
        """Test status text generation"""
        progress = BuildProgress(
            stage=BuildStage.VIVADO_SYNTHESIS,
            completion_percent=75.0,
            current_operation="Running synthesis",
        )

        # Normal operation
        assert progress.status_text == "Running: Running synthesis"

        # With warnings
        progress.add_warning("Timing warning")
        assert "Warning in" in progress.status_text

        # With errors
        progress.add_error("Synthesis error")
        assert "Error in" in progress.status_text

        # Build complete
        progress.completion_percent = 100.0
        progress.stage_completion = {stage: True for stage in BuildStage}
        progress.errors = []  # Clear errors for complete test
        progress.warnings = []  # Clear warnings for complete test
        assert progress.status_text == "Build Complete"

    @pytest.mark.unit
    def test_progress_bar_text(self):
        """Test progress bar text"""
        progress = BuildProgress(
            stage=BuildStage.REGISTER_EXTRACTION,
            completion_percent=30.0,
            current_operation="Extracting registers",
        )

        progress.mark_stage_complete(BuildStage.ENVIRONMENT_VALIDATION)

        text = progress.progress_bar_text
        assert "%" in text
        assert "stages" in text
        assert "1/6" in text

    @pytest.mark.unit
    def test_warning_and_error_management(self):
        """Test warning and error management"""
        progress = BuildProgress(
            stage=BuildStage.VIVADO_SYNTHESIS,
            completion_percent=50.0,
            current_operation="Synthesis",
        )

        # Add warnings
        progress.add_warning("Warning 1")
        progress.add_warning("Warning 2")
        progress.add_warning("Warning 1")  # Duplicate

        assert len(progress.warnings) == 2
        assert "Warning 1" in progress.warnings
        assert "Warning 2" in progress.warnings

        # Add errors
        progress.add_error("Error 1")
        progress.add_error("Error 2")
        progress.add_error("Error 1")  # Duplicate

        assert len(progress.errors) == 2
        assert "Error 1" in progress.errors
        assert "Error 2" in progress.errors

    @pytest.mark.unit
    def test_resource_usage_update(self):
        """Test resource usage tracking"""
        progress = BuildProgress(
            stage=BuildStage.VIVADO_SYNTHESIS,
            completion_percent=50.0,
            current_operation="Synthesis",
        )

        progress.update_resource_usage(cpu=75.5, memory=8.2, disk_free=120.0)

        assert progress.resource_usage["cpu"] == 75.5
        assert progress.resource_usage["memory"] == 8.2
        assert progress.resource_usage["disk_free"] == 120.0

    @pytest.mark.unit
    def test_serialization(self):
        """Test progress serialization"""
        progress = BuildProgress(
            stage=BuildStage.BITSTREAM_GENERATION,
            completion_percent=90.0,
            current_operation="Generating bitstream",
            estimated_remaining=120.0,
        )

        progress.add_warning("Test warning")
        progress.update_resource_usage(50.0, 4.0, 100.0)

        data = progress.to_dict()

        assert data["stage"] == "Bitstream Generation"
        assert data["completion_percent"] == 90.0
        assert data["current_operation"] == "Generating bitstream"
        assert data["estimated_remaining"] == 120.0
        assert "Test warning" in data["warnings"]
        assert data["resource_usage"]["cpu"] == 50.0
        assert "overall_progress" in data
        assert "status_text" in data


class TestBuildStage:
    """Test BuildStage enum"""

    @pytest.mark.unit
    def test_build_stages(self):
        """Test BuildStage enum values"""
        stages = list(BuildStage)

        assert BuildStage.ENVIRONMENT_VALIDATION in stages
        assert BuildStage.DEVICE_ANALYSIS in stages
        assert BuildStage.REGISTER_EXTRACTION in stages
        assert BuildStage.SYSTEMVERILOG_GENERATION in stages
        assert BuildStage.VIVADO_SYNTHESIS in stages
        assert BuildStage.BITSTREAM_GENERATION in stages

        # Check that we have the expected number of stages
        assert len(stages) == 6

        # Check stage values
        assert BuildStage.ENVIRONMENT_VALIDATION.value == "Environment Validation"
        assert BuildStage.VIVADO_SYNTHESIS.value == "Vivado Synthesis"
