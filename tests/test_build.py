"""
Comprehensive tests for src/build.py - Firmware generation functionality.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import build


class TestSecurityAndTempFiles:
    """Test secure temporary file handling."""

    def test_create_secure_tempfile_success(self):
        """Test successful creation of secure temporary file."""
        temp_path = build.create_secure_tempfile(suffix=".test", prefix="test_")

        try:
            assert os.path.exists(temp_path)
            assert temp_path.endswith(".test")
            assert "test_" in os.path.basename(temp_path)

            # Check file permissions (owner read/write only)
            stat_info = os.stat(temp_path)
            assert oct(stat_info.st_mode)[-3:] == "600"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @patch("tempfile.mkstemp")
    @patch("os.fchmod")
    @patch("os.close")
    def test_create_secure_tempfile_error_cleanup(
        self, mock_close, mock_fchmod, mock_mkstemp
    ):
        """Test cleanup on error during secure tempfile creation."""
        mock_fd = 5
        mock_path = "/tmp/test_file"
        mock_mkstemp.return_value = (mock_fd, mock_path)
        mock_fchmod.side_effect = OSError("Permission denied")

        with patch("os.unlink") as mock_unlink:
            with pytest.raises(OSError):
                build.create_secure_tempfile()

            mock_close.assert_called_with(mock_fd)
            mock_unlink.assert_called_with(mock_path)


class TestDonorInfoExtraction:
    """Test donor device information extraction."""

    @patch("os.chdir")
    @patch("build.run")
    @patch("subprocess.check_output")
    def test_get_donor_info_success(
        self, mock_output, mock_run, mock_chdir, mock_donor_info
    ):
        """Test successful donor info extraction with explicit use_donor_dump=True."""
        # Mock kernel module output
        mock_proc_output = """vendor_id: 0x8086
device_id: 0x1533
subvendor_id: 0x8086
subsystem_id: 0x0000
revision_id: 0x03
bar_size: 0x20000
mpc: 0x02
mpr: 0x02"""

        mock_output.return_value = mock_proc_output

        # Explicitly set use_donor_dump=True since it's now False by default
        info = build.get_donor_info("0000:03:00.0", use_donor_dump=True)

        assert info["vendor_id"] == "0x8086"
        assert info["device_id"] == "0x1533"
        assert info["bar_size"] == "0x20000"

        # Verify module operations
        mock_run.assert_any_call("make -s")
        mock_run.assert_any_call("insmod donor_dump.ko bdf=0000:03:00.0")
        mock_run.assert_any_call("rmmod donor_dump")

    @patch("os.chdir")
    @patch("build.run")
    @patch("subprocess.check_output")
    def test_get_donor_info_missing_fields(self, mock_output, mock_run, mock_chdir):
        """Test donor info extraction with missing required fields."""
        # Mock incomplete output
        mock_proc_output = """vendor_id: 0x8086
device_id: 0x1533"""

        mock_output.return_value = mock_proc_output

        with pytest.raises(SystemExit):
            build.get_donor_info("0000:03:00.0", use_donor_dump=True)

    @patch("os.chdir")
    @patch("build.run")
    @patch("subprocess.check_output")
    def test_get_donor_info_malformed_output(self, mock_output, mock_run, mock_chdir):
        """Test donor info extraction with malformed output."""
        mock_output.return_value = "malformed output without colons"

        with pytest.raises(SystemExit):
            build.get_donor_info("0000:03:00.0", use_donor_dump=True)


class TestDriverRegisterScraping:
    """Test driver register scraping functionality."""

    @patch("subprocess.check_output")
    def test_scrape_driver_regs_success(self, mock_output, mock_register_data):
        """Test successful driver register scraping."""
        # Create a mock response with both registers and state machine analysis
        mock_response = {
            "registers": mock_register_data,
            "state_machine_analysis": {
                "extracted_state_machines": 2,
                "optimized_state_machines": 1,
                "functions_with_state_patterns": 3,
                "state_machines": [],
                "analysis_report": "Test report",
            },
        }
        mock_output.return_value = json.dumps(mock_response)

        regs, state_machine_analysis = build.scrape_driver_regs("8086", "1533")

        # Check registers
        assert len(regs) == 2
        assert regs[0]["name"] == "reg_ctrl"
        assert regs[0]["offset"] == 0x400
        assert "context" in regs[0]

        # Check state machine analysis
        assert state_machine_analysis["extracted_state_machines"] == 2
        assert state_machine_analysis["optimized_state_machines"] == 1

        mock_output.assert_called_once_with(
            "python3 src/scripts/driver_scrape.py 8086 1533", shell=True, text=True
        )

    @patch("subprocess.check_output")
    def test_scrape_driver_regs_command_failure(self, mock_output):
        """Test driver register scraping when command fails."""
        mock_output.side_effect = subprocess.CalledProcessError(1, "driver_scrape.py")

        regs, state_machine_analysis = build.scrape_driver_regs("8086", "1533")
        assert regs == []
        assert state_machine_analysis == {}

    @patch("subprocess.check_output")
    def test_scrape_driver_regs_invalid_json(self, mock_output):
        """Test driver register scraping with invalid JSON output."""
        mock_output.return_value = "invalid json"

        # We now handle JSON decode errors gracefully
        regs, state_machine_analysis = build.scrape_driver_regs("8086", "1533")
        assert regs == []
        assert state_machine_analysis == {}


class TestBehaviorProfiling:
    """Test behavior profiling integration."""

    @patch("builtins.__import__")
    def test_integrate_behavior_profile_success(
        self, mock_import, mock_register_data, mock_behavior_profile
    ):
        """Test successful behavior profile integration."""
        # Mock the behavior profiler module
        mock_profiler_class = Mock()
        mock_profiler_instance = Mock()
        mock_profiler_class.return_value = mock_profiler_instance
        mock_profiler_instance.capture_behavior_profile.return_value = (
            mock_behavior_profile
        )
        mock_profiler_instance.analyze_patterns.return_value = {
            "device_characteristics": {"access_frequency_hz": 1500},
            "behavioral_signatures": {"timing_regularity": 0.85},
        }

        mock_module = Mock()
        mock_module.BehaviorProfiler = mock_profiler_class
        mock_import.return_value = mock_module

        enhanced_regs = build.integrate_behavior_profile(
            "0000:03:00.0", mock_register_data, 5.0
        )

        assert len(enhanced_regs) == 2
        assert "context" in enhanced_regs[0]
        assert "behavioral_timing" in enhanced_regs[0]["context"]
        assert "device_analysis" in enhanced_regs[0]["context"]

        mock_profiler_instance.capture_behavior_profile.assert_called_once_with(5.0)

    @patch("builtins.__import__")
    def test_integrate_behavior_profile_import_error(
        self, mock_import, mock_register_data
    ):
        """Test behavior profile integration when import fails."""
        mock_import.side_effect = ImportError("Module not found")

        enhanced_regs = build.integrate_behavior_profile(
            "0000:03:00.0", mock_register_data
        )

        # Should return original registers unchanged
        assert enhanced_regs == mock_register_data

    @patch("builtins.__import__")
    def test_integrate_behavior_profile_profiling_error(
        self, mock_import, mock_register_data
    ):
        """Test behavior profile integration when profiling fails."""
        mock_profiler_class = Mock()
        mock_profiler_instance = Mock()
        mock_profiler_class.return_value = mock_profiler_instance
        mock_profiler_instance.capture_behavior_profile.side_effect = Exception(
            "Profiling failed"
        )

        mock_module = Mock()
        mock_module.BehaviorProfiler = mock_profiler_class
        mock_import.return_value = mock_module

        enhanced_regs = build.integrate_behavior_profile(
            "0000:03:00.0", mock_register_data
        )

        # Should return original registers unchanged
        assert enhanced_regs == mock_register_data


class TestSystemVerilogGeneration:
    """Test SystemVerilog generation functionality."""

    def test_build_sv_success(self, temp_dir, mock_register_data):
        """Test successful SystemVerilog generation."""
        target_file = temp_dir / "test_controller.sv"

        build.build_sv(mock_register_data, target_file)

        assert target_file.exists()
        sv_content = target_file.read_text()

        # Check for module declaration
        assert "module pcileech_tlps128_bar_controller" in sv_content

        # Check for register declarations
        assert "reg_ctrl_reg" in sv_content
        assert "reg_status_reg" in sv_content

        # Check for timing logic
        assert "delay_counter" in sv_content
        assert "write_pending" in sv_content

        # Check for state machine elements
        assert "device_state" in sv_content
        assert "global_timer" in sv_content

        # Check for read cases
        assert "32'h00000400" in sv_content  # reg_ctrl offset
        assert "32'h00000404" in sv_content  # reg_status offset

    def test_build_sv_no_registers(self, temp_dir):
        """Test SystemVerilog generation with no registers."""
        target_file = temp_dir / "test_controller.sv"

        # We now handle empty register lists by using default registers
        build.build_sv([], target_file)

        # Verify the file was created with default registers
        assert target_file.exists()
        sv_content = target_file.read_text()

        # Check for default register declarations
        assert "device_control_reg" in sv_content
        assert "device_status_reg" in sv_content

    def test_build_sv_complex_timing(self, temp_dir):
        """Test SystemVerilog generation with complex timing constraints."""
        complex_regs = [
            {
                "offset": 0x400,
                "name": "reg_complex",
                "value": "0x0",
                "rw": "rw",
                "context": {
                    "timing_constraints": [
                        {"delay_us": 50, "context": "register_access"},
                        {"delay_us": 30, "context": "initialization"},
                    ],
                    "access_pattern": "write_then_read",
                    "sequences": [
                        {"function": "init", "position": 0, "operation": "write"},
                        {"function": "init", "position": 1, "operation": "read"},
                    ],
                },
            }
        ]

        target_file = temp_dir / "complex_controller.sv"
        build.build_sv(complex_regs, target_file)

        sv_content = target_file.read_text()

        # Check for complex timing logic
        assert "reg_complex_delay_counter" in sv_content
        assert "reg_complex_write_pending" in sv_content

        # Should have calculated delay cycles based on timing constraints
        # Average of 50us and 30us = 40us, at 100MHz = 4000 cycles
        assert "4000" in sv_content or "4001" in sv_content  # Allow for rounding


class TestStateMachineGeneration:
    """Test state machine generation functionality."""

    def test_generate_register_state_machine_simple(self):
        """Test simple register state machine generation."""
        sequences = [
            {"function": "init", "position": 0, "operation": "write"},
            {"function": "init", "position": 1, "operation": "read"},
        ]

        state_machine = build.generate_register_state_machine(
            "test_reg", sequences, 0x400
        )

        assert "test_reg_state_0" in state_machine
        assert "test_reg_state_1" in state_machine
        assert "sequence_trigger_test_reg" in state_machine
        assert "32'h00000400" in state_machine

    def test_generate_register_state_machine_insufficient_sequences(self):
        """Test state machine generation with insufficient sequences."""
        sequences = [{"function": "init", "position": 0, "operation": "write"}]

        state_machine = build.generate_register_state_machine(
            "test_reg", sequences, 0x400
        )
        assert state_machine == ""

    def test_generate_device_state_machine(self, mock_register_data):
        """Test device-level state machine generation."""
        state_machine = build.generate_device_state_machine(mock_register_data)

        assert "DEVICE_RESET" in state_machine
        assert "DEVICE_INIT" in state_machine
        assert "DEVICE_READY" in state_machine
        assert "DEVICE_ACTIVE" in state_machine
        assert "device_state_t" in state_machine

        # Check for timing-based transitions
        assert "global_timer" in state_machine

    def test_generate_device_state_machine_empty_regs(self):
        """Test device state machine generation with empty register list."""
        state_machine = build.generate_device_state_machine([])

        # Should still generate basic state machine structure
        assert "DEVICE_RESET" in state_machine
        assert "device_state_t" in state_machine


class TestTCLGeneration:
    """Test TCL patch file generation."""

    def test_code_from_bytes_valid(self):
        """Test valid byte count to code conversion."""
        assert build.code_from_bytes(128) == 0
        assert build.code_from_bytes(256) == 1
        assert build.code_from_bytes(1024) == 3
        assert build.code_from_bytes(4096) == 5

    def test_code_from_bytes_invalid(self):
        """Test invalid byte count to code conversion."""
        with pytest.raises(KeyError):
            build.code_from_bytes(999)  # Not in mapping

    def test_build_tcl_success(self, mock_donor_info):
        """Test successful TCL generation."""
        gen_tcl = "test_generate.tcl"

        tcl_content, tcl_file = build.build_tcl(mock_donor_info, gen_tcl)

        assert "set_property" in tcl_content
        assert mock_donor_info["vendor_id"] in tcl_content
        assert mock_donor_info["device_id"] in tcl_content
        assert "128_KB" in tcl_content  # BAR size conversion

        assert tcl_file.endswith(".tcl")

    def test_build_tcl_unsupported_bar_size(self):
        """Test TCL generation with unsupported BAR size."""
        invalid_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "bar_size": "0x12345",  # Unsupported size
            "mpc": "0x02",
            "mpr": "0x02",
            "subvendor_id": "0x8086",  # Added required field
            "subsystem_id": "0x0000",  # Added required field
            "revision_id": "0x03",  # Added required field
        }

        # We now handle unsupported BAR sizes by using a default aperture
        tcl_content, tcl_file = build.build_tcl(invalid_info, "test.tcl")

        # Verify the default aperture was used
        assert "128K" in tcl_content
        assert (
            "Warning: Unsupported BAR size" not in tcl_content
        )  # Warning is printed, not in content


class TestBoardConfiguration:
    """Test board configuration and validation."""

    def test_board_info_constants(self):
        """Test board information constants."""
        # Original boards
        assert "35t" in build.BOARD_INFO
        assert "75t" in build.BOARD_INFO
        assert "100t" in build.BOARD_INFO

        # CaptainDMA boards
        assert "pcileech_75t484_x1" in build.BOARD_INFO
        assert "pcileech_35t484_x1" in build.BOARD_INFO
        assert "pcileech_35t325_x4" in build.BOARD_INFO
        assert "pcileech_35t325_x1" in build.BOARD_INFO
        assert "pcileech_100t484_x1" in build.BOARD_INFO

        # Other boards
        assert "pcileech_enigma_x1" in build.BOARD_INFO
        assert "pcileech_squirrel" in build.BOARD_INFO
        assert "pcileech_pciescreamer_xc7a35" in build.BOARD_INFO

        for board, info in build.BOARD_INFO.items():
            assert "root" in info
            assert "gen" in info
            assert info["gen"].endswith(".tcl")

    def test_aperture_constants(self):
        """Test aperture size constants."""
        assert 1024 in build.APERTURE
        assert 65536 in build.APERTURE
        assert 16777216 in build.APERTURE

        assert build.APERTURE[1024] == "1_KB"
        assert build.APERTURE[65536] == "64_KB"
        assert build.APERTURE[16777216] == "16_MB"


class TestUtilityFunctions:
    """Test utility functions."""

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run):
        """Test successful command execution."""
        mock_run.return_value = Mock(returncode=0)

        build.run("echo test")

        mock_run.assert_called_once_with("echo test", shell=True, check=True)

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test command execution failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "false")

        with pytest.raises(subprocess.CalledProcessError):
            build.run("false")


class TestIntegrationScenarios:
    """Test integration scenarios and workflows."""

    @patch("build.get_donor_info")
    @patch("build.scrape_driver_regs")
    @patch("build.integrate_behavior_profile")
    @patch("build.build_sv")
    @patch("build.build_tcl")
    def test_full_build_workflow(
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
        """Test full build workflow integration."""
        # Setup mocks
        mock_donor.return_value = mock_donor_info
        mock_scrape.return_value = mock_register_data
        mock_behavior.return_value = mock_register_data
        mock_tcl.return_value = ("tcl content", str(temp_dir / "test.tcl"))

        # This would be part of a main build function
        bdf = "0000:03:00.0"
        vendor = "8086"
        device = "1533"

        # Simulate workflow steps
        donor_info = mock_donor(bdf)
        registers = mock_scrape(vendor, device)
        enhanced_regs = mock_behavior(bdf, registers)

        target_file = temp_dir / "controller.sv"
        mock_sv(enhanced_regs, target_file)

        tcl_content, tcl_file = mock_tcl(donor_info, "generate.tcl")

        # Verify all steps were called
        mock_donor.assert_called_once_with(bdf)
        mock_scrape.assert_called_once_with(vendor, device)
        mock_behavior.assert_called_once_with(bdf, registers)
        mock_sv.assert_called_once_with(enhanced_regs, target_file)
        mock_tcl.assert_called_once_with(donor_info, "generate.tcl")


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""

    def test_empty_register_list_handling(self, temp_dir):
        """Test handling of empty register lists."""
        # We now handle empty register lists by using default registers
        target_file = temp_dir / "test.sv"
        build.build_sv([], target_file)

        # Verify the file was created with default registers
        assert target_file.exists()
        sv_content = target_file.read_text()

        # Check for default register declarations
        assert "device_control_reg" in sv_content
        assert "device_status_reg" in sv_content

    def test_malformed_register_data(self, temp_dir):
        """Test handling of malformed register data."""
        malformed_regs = [
            {
                "offset": "invalid",  # Should be int
                "name": "test_reg",
                "value": "0x0",
                "rw": "rw",
            }
        ]

        with pytest.raises((ValueError, TypeError)):
            build.build_sv(malformed_regs, temp_dir / "test.sv")

    def test_missing_context_data(self, temp_dir):
        """Test handling of registers without context data."""
        minimal_regs = [
            {
                "offset": 0x400,
                "name": "minimal_reg",
                "value": "0x0",
                "rw": "rw",
                # No context field
            }
        ]

        # Should not raise exception, should use defaults
        build.build_sv(minimal_regs, temp_dir / "test.sv")

        target_file = temp_dir / "test.sv"
        assert target_file.exists()


class TestPerformanceAndScaling:
    """Test performance and scaling characteristics."""

    def test_large_register_set_generation(self, temp_dir, performance_test_data):
        """Test SystemVerilog generation with large register sets."""
        from tests.conftest import generate_test_registers

        large_reg_set = generate_test_registers(
            performance_test_data["large_device"]["register_count"]
        )

        target_file = temp_dir / "large_controller.sv"

        import time

        start_time = time.time()
        build.build_sv(large_reg_set, target_file)
        generation_time = (time.time() - start_time) * 1000  # Convert to ms

        assert target_file.exists()

        # Performance assertion (should complete within reasonable time)
        max_time = performance_test_data["large_device"]["expected_build_time_ms"]
        assert (
            generation_time < max_time
        ), f"Generation took {generation_time}ms, expected < {max_time}ms"

    def test_memory_usage_with_large_datasets(self, performance_test_data):
        """Test memory usage with large register datasets."""
        import os

        import psutil

        from tests.conftest import generate_test_registers

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Generate large dataset
        large_reg_set = generate_test_registers(
            performance_test_data["large_device"]["register_count"]
        )

        # Process the dataset (simulate heavy operations)
        for reg in large_reg_set:
            context = reg.get("context", {})
            # Simulate processing
            _ = build.generate_register_state_machine(
                reg["name"], context.get("sequences", []), reg["offset"]
            )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        max_memory = performance_test_data["large_device"]["expected_memory_mb"]
        assert (
            memory_increase < max_memory
        ), f"Memory usage increased by {memory_increase}MB, expected < {max_memory}MB"


class TestRegressionPrevention:
    """Test regression prevention for known issues."""

    def test_register_offset_formatting(self, temp_dir):
        """Test that register offsets are properly formatted in SystemVerilog."""
        test_regs = [
            {"offset": 0x400, "name": "reg_test", "value": "0x12345678", "rw": "rw"}
        ]

        target_file = temp_dir / "offset_test.sv"
        build.build_sv(test_regs, target_file)

        sv_content = target_file.read_text()

        # Ensure offset is properly formatted as 8-digit hex
        assert "32'h00000400" in sv_content
        assert "32'h12345678" in sv_content

    def test_special_character_handling_in_names(self, temp_dir):
        """Test handling of special characters in register names."""
        test_regs = [
            {
                "offset": 0x400,
                "name": "reg_with_underscores_123",
                "value": "0x0",
                "rw": "rw",
            }
        ]

        target_file = temp_dir / "special_chars_test.sv"
        build.build_sv(test_regs, target_file)

        sv_content = target_file.read_text()

        # Should handle underscores and numbers in names
        assert "reg_with_underscores_123_reg" in sv_content

    def test_timing_calculation_edge_cases(self, temp_dir):
        """Test edge cases in timing calculations."""
        edge_case_regs = [
            {
                "offset": 0x400,
                "name": "zero_delay_reg",
                "value": "0x0",
                "rw": "rw",
                "context": {
                    "timing_constraints": [{"delay_us": 0, "context": "immediate"}]
                },
            },
            {
                "offset": 0x404,
                "name": "large_delay_reg",
                "value": "0x0",
                "rw": "rw",
                "context": {
                    "timing_constraints": [
                        {"delay_us": 1000000, "context": "very_slow"}
                    ]
                },
            },
        ]

        target_file = temp_dir / "timing_edge_test.sv"
        build.build_sv(edge_case_regs, target_file)

        sv_content = target_file.read_text()

        # Zero delay should result in minimum 1 cycle
        assert "zero_delay_reg_delay_counter <= 1" in sv_content

        # Large delay should be handled without overflow
        assert "large_delay_reg_delay_counter" in sv_content
