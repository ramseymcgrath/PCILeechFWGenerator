"""
Test TUI Progress Models

Tests for the build progress tracking models in src/tui/models/progress.py.
"""

import pytest

from src.tui.models.progress import BuildProgress, BuildStage


class TestBuildStage:
    """Test BuildStage enum"""

    @pytest.mark.unit
    def test_build_stage_values(self):
        """Test BuildStage enum values"""
        assert BuildStage.ENVIRONMENT_VALIDATION.value == "Environment Validation"
        assert BuildStage.DEVICE_ANALYSIS.value == "Device Analysis"
        assert BuildStage.REGISTER_EXTRACTION.value == "Register Extraction"
        assert BuildStage.SYSTEMVERILOG_GENERATION.value == "SystemVerilog Generation"
        assert BuildStage.VIVADO_SYNTHESIS.value == "Vivado Synthesis"
        assert BuildStage.BITSTREAM_GENERATION.value == "Bitstream Generation"


class TestBuildProgress:
    """Test BuildProgress class"""

    @pytest.mark.unit
    def test_build_progress_init(self):
        """Test BuildProgress initialization."""
        progress = BuildProgress(
            stage=BuildStage.DEVICE_ANALYSIS,
            completion_percent=25.0,
            current_operation="Analyzing device capabilities",
        )

        assert progress.stage == BuildStage.DEVICE_ANALYSIS
        assert progress.completion_percent == 25.0
        assert progress.current_operation == "Analyzing device capabilities"
        assert progress.estimated_remaining is None
        assert progress.resource_usage == {}
        assert progress.warnings == []
        assert progress.errors == []
        assert len(progress.stage_completion) == len(BuildStage)
        assert all(not completed for completed in progress.stage_completion.values())

    @pytest.mark.unit
    def test_completed_stages_property(self):
        """Test completed_stages property."""
        progress = BuildProgress(
            stage=BuildStage.REGISTER_EXTRACTION,
            completion_percent=50.0,
            current_operation="Extracting registers",
        )

        # Initially no stages are completed
        assert progress.completed_stages == 0

        # Mark some stages as complete
        progress.mark_stage_complete(BuildStage.ENVIRONMENT_VALIDATION)
        progress.mark_stage_complete(BuildStage.DEVICE_ANALYSIS)

        assert progress.completed_stages == 2

    @pytest.mark.unit
    def test_total_stages_property(self):
        """Test total_stages property."""
        progress = BuildProgress(
            stage=BuildStage.DEVICE_ANALYSIS,
            completion_percent=25.0,
            current_operation="Analyzing device",
        )

        assert progress.total_stages == 6  # Number of BuildStage enum values

    @pytest.mark.unit
    def test_overall_progress_property(self):
        """Test overall_progress property calculation."""
        progress = BuildProgress(
            stage=BuildStage.REGISTER_EXTRACTION,
            completion_percent=60.0,
            current_operation="Extracting registers",
        )

        # Mark first two stages as complete
        progress.mark_stage_complete(BuildStage.ENVIRONMENT_VALIDATION)
        progress.mark_stage_complete(BuildStage.DEVICE_ANALYSIS)

        # Expected: (2/6) + (60/100 * 1/6) = 0.333 + 0.1 = 0.433 * 100 = 43.3%
        expected_progress = (2 / 6 + 60 / 100 / 6) * 100
        assert abs(progress.overall_progress - expected_progress) < 0.1

        # Test with all stages complete
        for stage in BuildStage:
            progress.mark_stage_complete(stage)
        progress.completion_percent = 100.0

        assert progress.overall_progress == 100.0

    @pytest.mark.unit
    def test_status_text_property(self):
        """Test status_text property for different states."""
        # Normal progress
        progress = BuildProgress(
            stage=BuildStage.DEVICE_ANALYSIS,
            completion_percent=25.0,
            current_operation="Analyzing device",
        )
        assert progress.status_text == "Running: Analyzing device"

        # With warnings
        progress.add_warning("Low disk space")
        assert progress.status_text == "Warning in Device Analysis"

        # With errors
        progress.add_error("Device not found")
        assert progress.status_text == "Error in Device Analysis"

        # Completed
        progress = BuildProgress(
            stage=BuildStage.BITSTREAM_GENERATION,
            completion_percent=100.0,
            current_operation="Finalizing",
        )
        for stage in BuildStage:
            progress.mark_stage_complete(stage)

        assert progress.status_text == "Build Complete"

    @pytest.mark.unit
    def test_progress_bar_text_property(self):
        """Test progress_bar_text property."""
        progress = BuildProgress(
            stage=BuildStage.REGISTER_EXTRACTION,
            completion_percent=60.0,
            current_operation="Extracting registers",
        )

        # Mark first two stages as complete
        progress.mark_stage_complete(BuildStage.ENVIRONMENT_VALIDATION)
        progress.mark_stage_complete(BuildStage.DEVICE_ANALYSIS)

        # Expected format: "43.3% (2/6 stages)"
        expected_text = f"{progress.overall_progress:.1f}% (2/6 stages)"
        assert progress.progress_bar_text == expected_text

    @pytest.mark.unit
    def test_add_warning_and_error(self):
        """Test adding warnings and errors."""
        progress = BuildProgress(
            stage=BuildStage.DEVICE_ANALYSIS,
            completion_percent=25.0,
            current_operation="Analyzing device",
        )

        # Add warnings
        progress.add_warning("Low disk space")
        progress.add_warning("Slow network connection")
        progress.add_warning("Low disk space")  # Duplicate should not be added

        assert len(progress.warnings) == 2
        assert "Low disk space" in progress.warnings
        assert "Slow network connection" in progress.warnings

        # Add errors
        progress.add_error("Device not found")
        progress.add_error("Invalid configuration")
        progress.add_error("Device not found")  # Duplicate should not be added

        assert len(progress.errors) == 2
        assert "Device not found" in progress.errors
        assert "Invalid configuration" in progress.errors

    @pytest.mark.unit
    def test_update_resource_usage(self):
        """Test updating resource usage metrics."""
        progress = BuildProgress(
            stage=BuildStage.DEVICE_ANALYSIS,
            completion_percent=25.0,
            current_operation="Analyzing device",
        )

        progress.update_resource_usage(cpu=45.2, memory=2048.5, disk_free=10240.0)

        assert progress.resource_usage["cpu"] == 45.2
        assert progress.resource_usage["memory"] == 2048.5
        assert progress.resource_usage["disk_free"] == 10240.0

    @pytest.mark.unit
    def test_to_dict(self):
        """Test conversion to dictionary for serialization."""
        progress = BuildProgress(
            stage=BuildStage.REGISTER_EXTRACTION,
            completion_percent=75.0,
            current_operation="Extracting registers",
            estimated_remaining=120.5,
        )

        progress.mark_stage_complete(BuildStage.ENVIRONMENT_VALIDATION)
        progress.mark_stage_complete(BuildStage.DEVICE_ANALYSIS)
        progress.add_warning("Low disk space")
        progress.update_resource_usage(cpu=30.0, memory=1500.0, disk_free=5000.0)

        data = progress.to_dict()

        assert data["stage"] == "Register Extraction"
        assert data["completion_percent"] == 75.0
        assert data["current_operation"] == "Extracting registers"
        assert data["estimated_remaining"] == 120.5
        assert data["resource_usage"]["cpu"] == 30.0
        assert data["resource_usage"]["memory"] == 1500.0
        assert data["resource_usage"]["disk_free"] == 5000.0
        assert "Low disk space" in data["warnings"]
        assert data["errors"] == []
        assert data["stage_completion"]["Environment Validation"] is True
        assert data["stage_completion"]["Device Analysis"] is True
        assert data["stage_completion"]["Register Extraction"] is False
        assert "overall_progress" in data
        assert "status_text" in data
