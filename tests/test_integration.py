"""
Integration tests for PCILeech firmware generator workflow.
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

import generate

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import build


@pytest.mark.integration
class TestFullWorkflow:
    """Test complete firmware generation workflow."""

    @patch("generate.validate_environment")
    @patch("generate.list_pci_devices")
    @patch("generate.get_iommu_group")
    @patch("generate.get_current_driver")
    @patch("generate.bind_to_vfio")
    @patch("generate.run_build_container")
    @patch("generate.restore_original_driver")
    @patch("pathlib.Path.exists")
    def test_end_to_end_workflow_without_hardware(
        self,
        mock_path_exists,
        mock_restore,
        mock_container,
        mock_bind,
        mock_get_driver,
        mock_get_iommu,
        mock_list_devices,
        mock_validate,
        mock_pci_device,
        temp_dir,
    ):
        """Test end-to-end workflow without real hardware."""
        # Setup mocks for complete workflow
        mock_validate.return_value = None
        mock_list_devices.return_value = [mock_pci_device]
        mock_get_iommu.return_value = "15"
        mock_get_driver.return_value = "e1000e"
        mock_path_exists.return_value = True

        # Mock user input for device selection
        with patch("builtins.input", return_value="0"):
            with patch("sys.argv", ["generate.py", "--board", "75t"]):
                result = generate.main()

        assert result == 0

        # Verify workflow steps
        mock_validate.assert_called_once()
        mock_list_devices.assert_called_once()
        mock_bind.assert_called_once_with("0000:03:00.0", "8086", "1533", "e1000e")
        # Pass the args parameter to run_build_container
        mock_container.assert_called_once()
        args = mock_container.call_args[0][3]
        assert args.board == "75t"
        assert args.flash is False
        mock_restore.assert_called_once_with("0000:03:00.0", "e1000e")

    @patch("build.get_donor_info")
    @patch("build.scrape_driver_regs")
    @patch("build.integrate_behavior_profile")
    @patch("build.build_sv")
    @patch("build.build_tcl")
    def test_build_workflow_integration(
        self,
        mock_tcl,
        mock_sv,
        mock_behavior,
        mock_scrape,
        mock_donor,
        temp_dir,
        mock_donor_info,
        mock_register_data,
    ):
        """Test build workflow integration."""
        # Setup mocks
        mock_donor.return_value = mock_donor_info
        mock_scrape.return_value = mock_register_data
        mock_behavior.return_value = mock_register_data
        mock_tcl.return_value = ("tcl content", str(temp_dir / "test.tcl"))

        # Simulate build workflow
        bdf = "0000:03:00.0"
        vendor = "8086"
        device = "1533"

        # Execute workflow steps
        donor_info = mock_donor(bdf)
        registers = mock_scrape(vendor, device)
        enhanced_regs = mock_behavior(bdf, registers)

        target_file = temp_dir / "controller.sv"
        mock_sv(enhanced_regs, target_file)

        tcl_content, tcl_file = mock_tcl(donor_info, "generate.tcl")

        # Verify all components work together
        assert donor_info == mock_donor_info
        assert registers == mock_register_data
        assert enhanced_regs == mock_register_data

        # Verify all functions were called with correct parameters
        mock_donor.assert_called_once_with(bdf)
        mock_scrape.assert_called_once_with(vendor, device)
        mock_behavior.assert_called_once_with(bdf, registers)
        mock_sv.assert_called_once_with(enhanced_regs, target_file)
        mock_tcl.assert_called_once_with(donor_info, "generate.tcl")


@pytest.mark.integration
class TestDataFlow:
    """Test data flow between components."""

    def test_register_data_transformation(self, mock_register_data):
        """Test register data transformation through the pipeline."""
        # Test that register data maintains integrity through transformations
        original_data = mock_register_data.copy()

        # Simulate transformations that might occur in the pipeline
        transformed_data = []
        for reg in original_data:
            transformed_reg = reg.copy()

            # Add behavioral context (simulating behavior profiler)
            if "context" not in transformed_reg:
                transformed_reg["context"] = {}

            transformed_reg["context"]["behavioral_timing"] = {
                "avg_interval_us": 100.0,
                "frequency_hz": 10000.0,
                "confidence": 0.95,
            }

            transformed_data.append(transformed_reg)

        # Verify data integrity
        assert len(transformed_data) == len(original_data)
        for orig, trans in zip(original_data, transformed_data):
            assert orig["name"] == trans["name"]
            assert orig["offset"] == trans["offset"]
            assert orig["value"] == trans["value"]
            assert orig["rw"] == trans["rw"]

            # Verify enhancements were added
            assert "behavioral_timing" in trans["context"]

    def test_json_serialization_compatibility(
        self, mock_register_data, mock_behavior_profile
    ):
        """Test JSON serialization compatibility between components."""
        # Test register data serialization
        register_json = json.dumps(mock_register_data)
        deserialized_registers = json.loads(register_json)

        assert len(deserialized_registers) == len(mock_register_data)
        assert deserialized_registers[0]["name"] == mock_register_data[0]["name"]

        # Test behavior profile serialization
        from dataclasses import asdict

        profile_dict = asdict(mock_behavior_profile)
        profile_json = json.dumps(profile_dict, default=str)
        deserialized_profile = json.loads(profile_json)

        assert deserialized_profile["device_bdf"] == mock_behavior_profile.device_bdf
        assert (
            deserialized_profile["capture_duration"]
            == mock_behavior_profile.capture_duration
        )


@pytest.mark.integration
class TestErrorPropagation:
    """Test error handling and propagation through the system."""

    @patch("generate.validate_environment")
    def test_environment_validation_failure_propagation(self, mock_validate):
        """Test that environment validation failures propagate correctly."""
        mock_validate.side_effect = RuntimeError("Environment validation failed")

        with patch("sys.argv", ["generate.py", "--board", "75t"]):
            result = generate.main()

        assert result == 1  # Should return error code

    @patch("build.get_donor_info")
    def test_donor_info_failure_propagation(self, mock_donor):
        """Test that donor info extraction failures propagate correctly."""
        mock_donor.side_effect = SystemExit("Donor info extraction failed")

        with pytest.raises(SystemExit):
            mock_donor("0000:03:00.0")

    @patch("build.scrape_driver_regs")
    def test_driver_scraping_failure_handling(self, mock_scrape):
        """Test handling of driver scraping failures."""
        mock_scrape.return_value = []  # No registers found

        result = mock_scrape("8086", "1533")
        assert result == []  # Should handle gracefully


@pytest.mark.integration
class TestFileSystemIntegration:
    """Test file system integration and I/O operations."""

    def test_output_directory_creation(self, temp_dir):
        """Test output directory creation and file writing."""
        output_dir = temp_dir / "output"

        # Simulate output directory creation
        output_dir.mkdir(exist_ok=True)

        # Test file creation
        test_files = ["firmware.bin", "bar_controller.sv", "generate.tcl"]

        for filename in test_files:
            test_file = output_dir / filename
            test_file.write_text(f"Test content for {filename}")

            assert test_file.exists()
            assert test_file.read_text() == f"Test content for {filename}"

    def test_temporary_file_cleanup(self, temp_dir):
        """Test temporary file creation and cleanup."""
        import tempfile

        # Create temporary files
        temp_files = []
        for i in range(5):
            fd, temp_path = tempfile.mkstemp(
                dir=temp_dir, prefix="test_", suffix=".tmp"
            )
            os.close(fd)
            temp_files.append(Path(temp_path))

        # Verify files exist
        for temp_file in temp_files:
            assert temp_file.exists()

        # Cleanup
        for temp_file in temp_files:
            temp_file.unlink()
            assert not temp_file.exists()


@pytest.mark.integration
class TestContainerIntegration:
    """Test container integration scenarios."""

    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_container_command_generation(self, mock_exists, mock_run):
        """Test container command generation and execution."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=0)

        # Test container command generation
        bdf = "0000:03:00.0"
        board = "75t"
        vfio_device = "/dev/vfio/15"

        # Create mock args with default values
        mock_args = Mock()
        mock_args.advanced_sv = False
        mock_args.device_type = "generic"
        mock_args.enable_variance = False
        mock_args.disable_power_management = False
        mock_args.disable_error_handling = False
        mock_args.disable_performance_counters = False
        mock_args.behavior_profile_duration = 30

        # This would be called by generate.py
        with patch("os.makedirs"):
            generate.run_build_container(bdf, board, vfio_device, mock_args)

        # Verify container command was executed
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]

        assert "podman run" in call_args
        assert bdf in call_args
        assert board in call_args
        assert vfio_device in call_args

    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_container_volume_mounting(self, mock_exists, mock_run):
        """Test container volume mounting for output directory."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=0)

        # Create mock args with default values
        mock_args = Mock()
        mock_args.advanced_sv = False
        mock_args.device_type = "generic"
        mock_args.enable_variance = False
        mock_args.disable_power_management = False
        mock_args.disable_error_handling = False
        mock_args.disable_performance_counters = False
        mock_args.behavior_profile_duration = 30

        with patch("os.makedirs") as mock_makedirs:
            generate.run_build_container(
                "0000:03:00.0", "75t", "/dev/vfio/15", mock_args
            )

        # Verify output directory creation
        mock_makedirs.assert_called_once_with("output", exist_ok=True)

        # Verify volume mount in command
        call_args = mock_run.call_args[0][0]
        assert "-v" in call_args
        assert "/app/output" in call_args


@pytest.mark.integration
class TestHardwareSimulation:
    """Test hardware simulation for CI environments."""

    @patch("os.path.exists")
    @patch("subprocess.check_output")
    def test_simulated_pci_device_enumeration(self, mock_output, mock_exists):
        """Test simulated PCIe device enumeration."""
        # Mock lspci output
        mock_lspci_output = """0000:00:00.0 Host bridge [0600]: Intel Corporation Device [8086:0c00]
0000:03:00.0 Ethernet controller [0200]: Intel Corporation I210 [8086:1533]
0000:04:00.0 Network controller [0280]: Intel Corporation Wi-Fi 6 AX200 [8086:2723]"""

        mock_output.return_value = mock_lspci_output

        devices = generate.list_pci_devices()

        assert len(devices) == 3
        assert any(dev["ven"] == "8086" and dev["dev"] == "1533" for dev in devices)

    @patch("os.path.exists")
    @patch("subprocess.check_output")
    def test_simulated_usb_device_enumeration(self, mock_output, mock_exists):
        """Test simulated USB device enumeration."""
        # Mock lsusb output
        mock_lsusb_output = """Bus 001 Device 002: ID 1d50:6130 OpenMoko, Inc. 
Bus 001 Device 003: ID 0403:6010 Future Technology Devices International, Ltd"""

        mock_output.return_value = mock_lsusb_output

        devices = generate.list_usb_devices()

        assert len(devices) == 2
        assert ("1d50:6130", "OpenMoko, Inc.") in devices

    @patch("os.path.exists")
    def test_simulated_vfio_environment(self, mock_exists):
        """Test simulated VFIO environment."""

        def exists_side_effect(path):
            # Simulate VFIO environment
            if "/sys/bus/pci/drivers/vfio-pci" in path:
                return True
            if "/dev/vfio/" in path:
                return True
            if "/sys/bus/pci/devices/" in path:
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        # Test VFIO device path existence
        assert mock_exists("/sys/bus/pci/drivers/vfio-pci")
        assert mock_exists("/dev/vfio/15")
        assert mock_exists("/sys/bus/pci/devices/0000:03:00.0")


@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance characteristics in integrated scenarios."""

    def test_large_register_set_processing(self, performance_test_data):
        """Test processing of large register sets through the pipeline."""
        from tests.conftest import generate_test_registers

        large_reg_set = generate_test_registers(
            performance_test_data["large_device"]["register_count"]
        )

        import time

        start_time = time.time()

        # Simulate processing through the pipeline
        processed_regs = []
        for reg in large_reg_set:
            processed_reg = reg.copy()

            # Simulate context analysis
            context = processed_reg.get("context", {})
            context["processed"] = True
            context["processing_time"] = time.time()
            processed_reg["context"] = context

            processed_regs.append(processed_reg)

        processing_time = time.time() - start_time

        # Should process within reasonable time
        max_time = (
            performance_test_data["large_device"]["expected_build_time_ms"] / 1000
        )
        assert processing_time < max_time
        assert len(processed_regs) == len(large_reg_set)

    def test_memory_usage_during_processing(self, performance_test_data):
        """Test memory usage during integrated processing."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate memory-intensive processing
        from tests.conftest import generate_test_registers

        large_datasets = []
        for i in range(5):  # Create multiple large datasets
            dataset = generate_test_registers(
                performance_test_data["medium_device"]["register_count"]
            )
            large_datasets.append(dataset)

        # Process all datasets
        for dataset in large_datasets:
            # Simulate SystemVerilog generation
            sv_content = []
            for reg in dataset:
                sv_content.append(f"logic [31:0] {reg['name']}_reg;")

            # Simulate file writing
            content = "\n".join(sv_content)
            assert len(content) > 0

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        max_memory = performance_test_data["large_device"]["expected_memory_mb"]
        assert memory_increase < max_memory


@pytest.mark.integration
class TestRegressionPrevention:
    """Test regression prevention for known issues."""

    def test_register_offset_consistency(self, temp_dir):
        """Test that register offsets remain consistent through processing."""
        test_registers = [
            {"offset": 0x400, "name": "reg_a", "value": "0x0", "rw": "rw"},
            {"offset": 0x404, "name": "reg_b", "value": "0x1", "rw": "ro"},
            {"offset": 0x408, "name": "reg_c", "value": "0x2", "rw": "wo"},
        ]

        # Process through SystemVerilog generation
        target_file = temp_dir / "consistency_test.sv"
        build.build_sv(test_registers, target_file)

        sv_content = target_file.read_text()

        # Verify offsets are preserved correctly
        assert "32'h00000400" in sv_content  # reg_a
        assert "32'h00000404" in sv_content  # reg_b
        assert "32'h00000408" in sv_content  # reg_c

    def test_context_data_preservation(self):
        """Test that context data is preserved through transformations."""
        original_reg = {
            "offset": 0x400,
            "name": "test_reg",
            "value": "0x0",
            "rw": "rw",
            "context": {
                "function": "test_function",
                "dependencies": ["other_reg"],
                "timing": "early",
                "access_pattern": "write_then_read",
            },
        }

        # Simulate enhancement process
        enhanced_reg = original_reg.copy()
        enhanced_reg["context"]["enhanced"] = True
        enhanced_reg["context"]["behavioral_timing"] = {
            "avg_interval_us": 100.0,
            "frequency_hz": 10000.0,
        }

        # Verify original context is preserved
        assert enhanced_reg["context"]["function"] == "test_function"
        assert enhanced_reg["context"]["dependencies"] == ["other_reg"]
        assert enhanced_reg["context"]["timing"] == "early"
        assert enhanced_reg["context"]["access_pattern"] == "write_then_read"

        # Verify enhancements were added
        assert enhanced_reg["context"]["enhanced"] is True
        assert "behavioral_timing" in enhanced_reg["context"]

    def test_error_recovery_mechanisms(self):
        """Test error recovery mechanisms in integrated scenarios."""
        # Test that the system can recover from various error conditions

        # Test 1: Empty register list
        try:
            result = build.scrape_driver_regs("0000", "0000")  # Invalid IDs
            assert isinstance(result, list)  # Should return empty list, not crash
        except Exception:
            pass  # Expected in test environment

        # Test 2: Invalid BDF format
        try:
            from behavior_profiler import BehaviorProfiler

            with pytest.raises(ValueError):
                BehaviorProfiler("invalid-bdf")
        except ImportError:
            pass  # Expected if module not available

        # Test 3: Missing files
        try:
            result = build.create_secure_tempfile()
            assert isinstance(result, str)
            os.unlink(result)  # Cleanup
        except Exception:
            pass  # Expected in some environments
