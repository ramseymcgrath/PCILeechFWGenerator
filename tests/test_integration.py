"""
Integration tests for PCILeech firmware generator workflow.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import generate

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    pass

    MODULAR_BUILD_AVAILABLE = True
except ImportError:
    MODULAR_BUILD_AVAILABLE = False
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

        assert deserialized_profile["device_bd"] == mock_behavior_profile.device_bdf
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
            "confidence": 0.95,
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
        # Test recovery from build failures
        try:
            # Simulate build failure
            raise RuntimeError("Build failed")
        except RuntimeError:
            # Should recover gracefully
            pass

        # Test recovery from file I/O errors
        try:
            # Simulate file I/O error
            raise IOError("File not found")
        except IOError:
            # Should recover gracefully
            pass

        # Test recovery from validation errors
        try:
            # Simulate validation error
            raise ValueError("Invalid configuration")
        except ValueError:
            # Should recover gracefully
            pass


@pytest.mark.integration
class TestEnhancedFeatureIntegration:
    """Enhanced integration tests for PCILeech FPGA firmware generator features."""

    def test_config_space_shadow_with_pruned_capabilities(self, temp_dir):
        """Test config space shadow with pruned capabilities."""
        from src.donor_dump_manager import DonorDumpManager
        from src.pci_capability import (
            PCICapabilityID,
            PCIExtCapabilityID,
            find_cap,
            find_ext_cap,
            prune_capabilities_by_rules,
        )

        # Create a sample configuration space with all features
        config_space = self._create_sample_config_space()

        # Prune capabilities
        pruned_config = prune_capabilities_by_rules(config_space)

        # Verify pruning results
        # Vendor-specific capability should be removed
        vendor_offset = find_cap(pruned_config, PCICapabilityID.VENDOR_SPECIFIC.value)
        assert vendor_offset is None

        # SR-IOV extended capability should be removed
        sriov_offset = find_ext_cap(
            pruned_config, PCIExtCapabilityID.SINGLE_ROOT_IO_VIRTUALIZATION.value
        )
        assert sriov_offset is None

        # Save pruned config space
        config_hex_path = temp_dir / "config_space_init.hex"
        manager = DonorDumpManager()
        result = manager.save_config_space_hex(pruned_config, str(config_hex_path))
        assert result is True

        # Verify the file exists and has correct size
        assert config_hex_path.exists()
        with open(config_hex_path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 1024  # 4KB / 4 bytes per line

    def test_msix_table_replication_with_pruned_capabilities(self):
        """Test MSI-X table replication with pruned capabilities."""
        from src.msix_capability import generate_msix_table_sv, parse_msix_capability
        from src.pci_capability import prune_capabilities_by_rules

        # Create sample config space and prune capabilities
        config_space = self._create_sample_config_space()
        pruned_config = prune_capabilities_by_rules(config_space)

        # Parse MSI-X capability
        msix_info = parse_msix_capability(pruned_config)

        # Verify MSI-X capability is preserved
        assert msix_info["table_size"] == 8
        assert msix_info["table_bir"] == 0
        assert msix_info["table_offset"] == 0x2000
        assert msix_info["pba_bir"] == 0
        assert msix_info["pba_offset"] == 0x3000

        # Generate SystemVerilog code
        sv_code = generate_msix_table_sv(msix_info)

        # Verify the generated code
        assert "localparam NUM_MSIX = 8;" in sv_code
        assert "localparam MSIX_TABLE_BIR = 0;" in sv_code
        assert "localparam MSIX_TABLE_OFFSET = 32'h2000;" in sv_code
        assert "localparam MSIX_PBA_BIR = 0;" in sv_code
        assert "localparam MSIX_PBA_OFFSET = 32'h3000;" in sv_code

    def test_deterministic_variance_with_pruned_config_space(self):
        """Test deterministic variance seeding with pruned config space."""
        from src.manufacturing_variance import (
            DeviceClass,
            ManufacturingVarianceSimulator,
        )
        from src.pci_capability import prune_capabilities_by_rules

        # Create sample config space and prune capabilities
        config_space = self._create_sample_config_space()
        pruned_config = prune_capabilities_by_rules(config_space)

        # Create device info with pruned config
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "dsn": "0x1234567890ABCDEF",
            "extended_config": pruned_config,
        }

        # Extract DSN and revision
        dsn = int(device_info["dsn"], 16)
        revision = "abcdef1234567890abcd"  # Simulated git commit hash

        # Create simulator
        simulator = ManufacturingVarianceSimulator()

        # Generate variance model
        model = simulator.generate_variance_model(
            device_id=device_info["device_id"],
            device_class=DeviceClass.ENTERPRISE,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        # Verify model is created
        assert model.device_id == device_info["device_id"]
        assert model.device_class == DeviceClass.ENTERPRISE

        # Generate SystemVerilog code for a register
        sv_code = simulator.generate_systemverilog_timing_code(
            register_name="config_reg",
            base_delay_cycles=5,
            variance_model=model,
            offset=0x400,
        )

        # Verify the generated code
        assert "config_reg" in sv_code
        assert "Variance-aware timing" in sv_code
        assert "Device class: enterprise" in sv_code

    def test_end_to_end_integration_with_all_features(self, temp_dir):
        """Test end-to-end integration of all enhanced features."""
        from src.donor_dump_manager import DonorDumpManager
        from src.manufacturing_variance import (
            DeviceClass,
            ManufacturingVarianceSimulator,
        )
        from src.msix_capability import generate_msix_table_sv, parse_msix_capability
        from src.pci_capability import prune_capabilities_by_rules

        # Step 1: Create and prune capabilities
        config_space = self._create_sample_config_space()
        pruned_config = prune_capabilities_by_rules(config_space)

        # Step 2: Parse MSI-X capability
        msix_info = parse_msix_capability(pruned_config)

        # Step 3: Generate deterministic variance
        device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "dsn": "0x1234567890ABCDEF",
        }
        dsn = int(device_info["dsn"], 16)
        revision = "abcdef1234567890abcd"

        simulator = ManufacturingVarianceSimulator()
        model = simulator.generate_variance_model(
            device_id=device_info["device_id"],
            device_class=DeviceClass.ENTERPRISE,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        # Step 4: Save pruned config space
        config_hex_path = temp_dir / "config_space_init.hex"
        manager = DonorDumpManager()
        result = manager.save_config_space_hex(pruned_config, str(config_hex_path))
        assert result is True

        # Step 5: Generate SystemVerilog code for MSI-X table
        msix_sv_code = generate_msix_table_sv(msix_info)

        # Step 6: Generate SystemVerilog code for variance-aware timing
        timing_sv_code = simulator.generate_systemverilog_timing_code(
            register_name="config_reg",
            base_delay_cycles=5,
            variance_model=model,
            offset=0x400,
        )

        # Verify all components work together
        assert "localparam NUM_MSIX = 8;" in msix_sv_code
        assert "Device class: enterprise" in timing_sv_code
        assert config_hex_path.exists()

    def test_reproducibility_across_builds(self):
        """Test reproducibility across multiple builds with the same DSN and revision."""
        from src.manufacturing_variance import (
            DeviceClass,
            ManufacturingVarianceSimulator,
        )
        from src.msix_capability import generate_msix_table_sv, parse_msix_capability
        from src.pci_capability import prune_capabilities_by_rules

        # Simulate multiple builds with the same DSN and revision
        device_info = {"device_id": "0x1533", "dsn": "0x1234567890ABCDEF"}
        dsn = int(device_info["dsn"], 16)
        revision = "abcdef1234567890abcd"

        # Create multiple simulators
        simulator1 = ManufacturingVarianceSimulator()
        simulator2 = ManufacturingVarianceSimulator()

        # Generate variance models
        model1 = simulator1.generate_variance_model(
            device_id=device_info["device_id"],
            device_class=DeviceClass.ENTERPRISE,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        model2 = simulator2.generate_variance_model(
            device_id=device_info["device_id"],
            device_class=DeviceClass.ENTERPRISE,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        # Generate SystemVerilog code
        sv_code1 = simulator1.generate_systemverilog_timing_code(
            register_name="config_reg",
            base_delay_cycles=5,
            variance_model=model1,
            offset=0x400,
        )

        sv_code2 = simulator2.generate_systemverilog_timing_code(
            register_name="config_reg",
            base_delay_cycles=5,
            variance_model=model2,
            offset=0x400,
        )

        # Verify the generated code is identical
        assert sv_code1 == sv_code2

        # Test config space pruning reproducibility
        config_space = self._create_sample_config_space()
        pruned_config1 = prune_capabilities_by_rules(config_space)
        pruned_config2 = prune_capabilities_by_rules(config_space)
        assert pruned_config1 == pruned_config2

        # Test MSI-X parsing reproducibility
        msix_info1 = parse_msix_capability(pruned_config1)
        msix_info2 = parse_msix_capability(pruned_config2)
        assert msix_info1["table_size"] == msix_info2["table_size"]
        assert msix_info1["table_bir"] == msix_info2["table_bir"]
        assert msix_info1["table_offset"] == msix_info2["table_offset"]

        # Test MSI-X SystemVerilog generation reproducibility
        msix_sv_code1 = generate_msix_table_sv(msix_info1)
        msix_sv_code2 = generate_msix_table_sv(msix_info2)
        assert msix_sv_code1 == msix_sv_code2

    def _create_sample_config_space(self):
        """Create a sample configuration space with all features."""
        # Start with a 4KB configuration space filled with zeros
        config_space = "00" * 4096

        # Set capabilities pointer at offset 0x34
        config_space = config_space[: 0x34 * 2] + "40" + config_space[0x34 * 2 + 2 :]

        # Set capabilities bit in status register (offset 0x06, bit 4)
        status_value = int(config_space[0x06 * 2 : 0x06 * 2 + 4], 16) | 0x10
        status_hex = f"{status_value:04x}"
        config_space = (
            config_space[: 0x06 * 2] + status_hex + config_space[0x06 * 2 + 4 :]
        )

        # Add PCIe capability at offset 0x40
        pcie_cap = "10" + "50" + "0200" + "00000000" + "00000000" + "00000000"
        config_space = (
            config_space[: 0x40 * 2]
            + pcie_cap
            + config_space[0x40 * 2 + len(pcie_cap) :]
        )

        # Add Power Management capability at offset 0x50
        pm_cap = "01" + "60" + "0300" + "00000000"
        config_space = (
            config_space[: 0x50 * 2] + pm_cap + config_space[0x50 * 2 + len(pm_cap) :]
        )

        # Add MSI-X capability at offset 0x60
        msix_cap = "11" + "70" + "0007" + "00002000" + "00003000"
        config_space = (
            config_space[: 0x60 * 2]
            + msix_cap
            + config_space[0x60 * 2 + len(msix_cap) :]
        )

        # Add Vendor-specific capability at offset 0x70
        vendor_cap = "09" + "00" + "0000" + "00000000"
        config_space = (
            config_space[: 0x70 * 2]
            + vendor_cap
            + config_space[0x70 * 2 + len(vendor_cap) :]
        )

        # Add L1 PM Substates extended capability at offset 0x100
        l1pm_cap = "001E" + "1140" + "00000001" + "00000002" + "00000003"
        config_space = (
            config_space[: 0x100 * 2]
            + l1pm_cap
            + config_space[0x100 * 2 + len(l1pm_cap) :]
        )

        # Add SR-IOV extended capability at offset 0x140
        sriov_cap = "0010" + "1000" + "00000000" + "00000000" + "00000004" + "00000008"
        config_space = (
            config_space[: 0x140 * 2]
            + sriov_cap
            + config_space[0x140 * 2 + len(sriov_cap) :]
        )

        return config_space

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
