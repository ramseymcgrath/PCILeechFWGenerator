"""
Tests for local build functionality with donor info file support.

These tests verify that the build process works correctly with:
- The --skip-donor-dump option
- Loading donor information from a file
- Building without requiring a donor device
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import after path setup
from src import build
from src.donor_dump_manager import DonorDumpManager


class TestLocalBuild:
    """Test local build functionality without donor device."""

    def test_default_donor_dump_behavior(self, mock_donor_info):
        """Test that donor dump is disabled by default (local build is default)."""
        # Call get_donor_info without specifying use_donor_dump
        # It should default to False
        with patch.object(DonorDumpManager, "generate_donor_info") as mock_generate:
            mock_generate.return_value = mock_donor_info

            info = build.get_donor_info(bdf="0000:00:00.0")  # Only provide BDF

            # Verify generate_donor_info was called (since use_donor_dump defaults to False)
            mock_generate.assert_called_once_with("generic")

            # Verify the info matches the expected values
            assert info == mock_donor_info

    def test_get_donor_info_from_file(self, mock_donor_info):
        """Test loading donor info from a file."""
        # Path to the sample donor info file
        donor_info_path = Path(__file__).parent / "sample_donor_info.json"

        # Ensure the file exists
        assert donor_info_path.exists(), "Sample donor info file not found"

        # Load donor info from file
        info = build.get_donor_info(
            bdf="0000:00:00.0",  # Dummy BDF, shouldn't be used
            use_donor_dump=False,  # Skip donor dump
            donor_info_path=str(donor_info_path),
            device_type="generic",
        )

        # Verify the loaded info matches the expected values
        assert info["vendor_id"] == "0x8086"
        assert info["device_id"] == "0x1533"
        assert info["bar_size"] == "0x20000"
        assert info["mpc"] == "0x02"
        assert info["mpr"] == "0x02"

        # Verify all required fields are present
        required_fields = [
            "vendor_id",
            "device_id",
            "subvendor_id",
            "subsystem_id",
            "revision_id",
            "bar_size",
            "mpc",
            "mpr",
        ]
        for field in required_fields:
            assert field in info, f"Required field {field} missing from donor info"

    @patch("src.build.get_donor_info")
    @patch("src.build.scrape_driver_regs")
    @patch("src.build.build_sv")
    @patch("src.build.build_tcl")
    @patch("src.build.vivado_run")
    def test_build_with_skip_donor_dump(
        self,
        mock_vivado_run,
        mock_build_tcl,
        mock_build_sv,
        mock_scrape_driver_regs,
        mock_get_donor_info,
        mock_donor_info,
        mock_register_data,
    ):
        """Test build process with --skip-donor-dump option."""
        # Set up mocks
        mock_get_donor_info.return_value = mock_donor_info
        mock_scrape_driver_regs.return_value = mock_register_data

        # Mock TCL generation
        mock_build_tcl.return_value = ("tcl content", "test.tcl")

        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Call get_donor_info directly instead of patching main
            build.get_donor_info(
                bdf="0000:00:00.0",
                use_donor_dump=False,
                donor_info_path=str(Path(__file__).parent / "sample_donor_info.json"),
                device_type="generic",
            )

            # Verify get_donor_info was called with the right parameters
            mock_get_donor_info.assert_called_once()
            args, kwargs = mock_get_donor_info.call_args
            assert kwargs.get("use_donor_dump") is False
            assert "sample_donor_info.json" in kwargs.get("donor_info_path", "")

    @patch("src.donor_dump_manager.DonorDumpManager.generate_donor_info")
    def test_generate_synthetic_donor_info(self, mock_generate_donor_info):
        """Test generating synthetic donor info when file is missing."""
        # Mock the generate_donor_info method
        mock_donor_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "subvendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "revision_id": "0x03",
            "bar_size": "0x20000",
            "mpc": "0x02",
            "mpr": "0x02",
        }
        mock_generate_donor_info.return_value = mock_donor_info

        # Create a non-existent file path
        non_existent_file = "/tmp/non_existent_donor_info.json"
        if os.path.exists(non_existent_file):
            os.remove(non_existent_file)

        # Get donor info with non-existent file and skip_donor_dump=True
        info = build.get_donor_info(
            bdf="0000:00:00.0",
            use_donor_dump=False,
            donor_info_path=non_existent_file,
            device_type="network",
        )

        # Verify generate_donor_info was called with the right device type
        mock_generate_donor_info.assert_called_once_with("network")

        # Verify the generated info matches the expected values
        assert info == mock_donor_info

    def test_donor_info_file_validation(self):
        """Test validation of donor info file contents."""
        # Create a temporary file with incomplete donor info
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".json", delete=False
        ) as temp_file:
            incomplete_info = {
                "vendor_id": "0x8086",
                "device_id": "0x1533",
                # Missing required fields
            }
            json.dump(incomplete_info, temp_file)
            temp_file_path = temp_file.name

        try:
            # Test with incomplete file and use_donor_dump=False
            # This should generate synthetic data instead
            with patch.object(DonorDumpManager, "generate_donor_info") as mock_generate:
                mock_donor_info = {
                    "vendor_id": "0x8086",
                    "device_id": "0x1533",
                    "subvendor_id": "0x8086",
                    "subsystem_id": "0x0000",
                    "revision_id": "0x03",
                    "bar_size": "0x20000",
                    "mpc": "0x02",
                    "mpr": "0x02",
                }
                mock_generate.return_value = mock_donor_info

                info = build.get_donor_info(
                    bdf="0000:00:00.0",
                    use_donor_dump=False,
                    donor_info_path=temp_file_path,
                    device_type="generic",
                )

                # Verify generate_donor_info was called
                mock_generate.assert_called_once()

                # Verify the generated info was used
                assert info == mock_donor_info
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    @patch("src.build.get_donor_info")
    @patch("src.build.scrape_driver_regs")
    @patch("src.build.build_sv")
    @patch("src.build.build_tcl")
    @patch("src.build.vivado_run")
    def test_build_without_donor_file(
        self,
        mock_vivado_run,
        mock_build_tcl,
        mock_build_sv,
        mock_scrape_driver_regs,
        mock_get_donor_info,
        mock_donor_info,
        mock_register_data,
    ):
        """Test build process without requiring donor file."""
        # Set up mocks
        mock_get_donor_info.return_value = mock_donor_info
        mock_scrape_driver_regs.return_value = mock_register_data

        # Mock TCL generation
        mock_build_tcl.return_value = ("tcl content", "test.tcl")

        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Call get_donor_info directly instead of patching main
            build.get_donor_info(
                bdf="0000:00:00.0",
                use_donor_dump=False,
                donor_info_path=None,
                device_type="generic",
            )

            # Verify get_donor_info was called with the right parameters
            mock_get_donor_info.assert_called_once()
            args, kwargs = mock_get_donor_info.call_args
            assert kwargs.get("use_donor_dump") is False
            assert kwargs.get("donor_info_path") is None


class TestBuildOrchestratorLocalBuild:
    """Test BuildOrchestrator with local build configuration."""

    @pytest.mark.asyncio
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._run_monitored_command")
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._validate_environment")
    @patch("generate.get_current_driver")
    @patch("generate.get_iommu_group")
    async def test_orchestrator_default_behavior(
        self,
        mock_get_iommu,
        mock_get_driver,
        mock_validate_env,
        mock_run_command,
        mock_donor_info,
    ):
        """Test BuildOrchestrator with default configuration (local build is default)."""
        from src.tui.core.build_orchestrator import BuildOrchestrator
        from src.tui.models.config import BuildConfiguration
        from src.tui.models.device import PCIDevice
        from src.tui.models.progress import BuildProgress

        # Mock the validation to avoid the build.py not found error
        mock_validate_env.return_value = None

        # Mock the driver and IOMMU group functions to avoid Linux requirement
        mock_get_driver.return_value = None
        mock_get_iommu.return_value = "1"

        # Create a device
        device = PCIDevice(
            bdf="0000:00:00.0",
            vendor_id="8086",
            device_id="1533",
            vendor_name="Intel",
            device_name="I210 Gigabit Network Connection",
            device_class="0200",  # Ethernet controller
            subsystem_vendor="8086",
            subsystem_device="0000",
            driver=None,
            iommu_group="1",
            power_state="D0",
            link_speed="5 GT/s",
            bars=[{"address": "0xf0000000", "size": "128K", "type": "Memory"}],
            suitability_score=1.0,
            compatibility_issues=[],
        )

        # Create a configuration with default settings (donor_dump=False is now default)
        config = BuildConfiguration(
            board_type="75t",
            device_type="network",  # Use default behavior (donor_dump=False)
        )

        # Create a progress callback
        progress_callback = Mock()

        # Create the orchestrator
        orchestrator = BuildOrchestrator()

        # Start the build
        await orchestrator.start_build(device, config, progress_callback)

        # Verify the command was run with the right parameters
        mock_run_command.assert_called()
        cmd = mock_run_command.call_args[0][0]

        # Check that the command includes the expected arguments
        assert "--bdf 0000:00:00.0" in " ".join(cmd)
        assert "--board 75t" in " ".join(cmd)
        # Verify that --use-donor-dump is NOT present (local build is default)
        assert "--use-donor-dump" not in " ".join(cmd)

    @pytest.mark.asyncio
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._run_monitored_command")
    @patch("src.tui.core.build_orchestrator.BuildOrchestrator._validate_environment")
    @patch("generate.get_current_driver")
    @patch("generate.get_iommu_group")
    async def test_orchestrator_local_build(
        self,
        mock_get_iommu,
        mock_get_driver,
        mock_validate_env,
        mock_run_command,
        mock_donor_info,
    ):
        """Test BuildOrchestrator with local build configuration."""
        from src.tui.core.build_orchestrator import BuildOrchestrator
        from src.tui.models.config import BuildConfiguration
        from src.tui.models.device import PCIDevice
        from src.tui.models.progress import BuildProgress

        # Mock the validation to avoid the build.py not found error
        mock_validate_env.return_value = None

        # Mock the driver and IOMMU group functions to avoid Linux requirement
        mock_get_driver.return_value = None
        mock_get_iommu.return_value = "1"

        # Create a device
        device = PCIDevice(
            bdf="0000:00:00.0",
            vendor_id="8086",
            device_id="1533",
            vendor_name="Intel",
            device_name="I210 Gigabit Network Connection",
            device_class="0200",  # Ethernet controller
            subsystem_vendor="8086",
            subsystem_device="0000",
            driver=None,
            iommu_group="1",
            power_state="D0",
            link_speed="5 GT/s",
            bars=[{"address": "0xf0000000", "size": "128K", "type": "Memory"}],
            suitability_score=1.0,
            compatibility_issues=[],
        )

        # Create a configuration with local build enabled
        config = BuildConfiguration(
            board_type="75t",
            device_type="network",
            local_build=True,
            donor_dump=False,
            donor_info_file=str(Path(__file__).parent / "sample_donor_info.json"),
        )

        # Create a progress callback
        progress_callback = Mock()

        # Create the orchestrator
        orchestrator = BuildOrchestrator()

        # Start the build
        await orchestrator.start_build(device, config, progress_callback)

        # Verify the command was run with the right parameters
        mock_run_command.assert_called()
        cmd = mock_run_command.call_args[0][0]

        # Check that the command includes the expected arguments
        assert "--bdf 0000:00:00.0" in " ".join(cmd)
        assert "--board 75t" in " ".join(cmd)
        # No need to assert --skip-donor-dump since local builds are now default
        assert "--donor-info-file" in " ".join(cmd)
        assert "sample_donor_info.json" in " ".join(cmd)
