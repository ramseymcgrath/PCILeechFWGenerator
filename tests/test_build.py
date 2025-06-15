"""
Comprehensive tests for src/build.py - Firmware generation functionality.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    pass

    MODULAR_BUILD_AVAILABLE = True
except ImportError:
    MODULAR_BUILD_AVAILABLE = False

# Import compatibility module for legacy build functions
try:
    from src import build_compat as build
except ImportError:
    # Fallback to legacy build if available
    try:
        from src import build
    except ImportError:
        # Create minimal mock for tests
        build = type(
            "build",
            (),
            {
                "create_secure_tempfile": lambda *args, **kwargs: "/tmp/test_file",
                "get_donor_info": lambda *args, **kwargs: {},
                "scrape_driver_regs": lambda *args, **kwargs: ([], {}),
                "integrate_behavior_profile": lambda *args, **kwargs: [],
                "build_sv": lambda *args, **kwargs: None,
                "build_tcl": lambda *args, **kwargs: ("", ""),
                "run": lambda *args, **kwargs: None,
                "code_from_bytes": lambda x: 0,
                "BOARD_INFO": {},
                "APERTURE": {},
            },
        )()


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
    @patch("build_compat.run")
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
    @patch("build_compat.run")
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
    @patch("build_compat.run")
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


class TestRefactoredBuildSystem:
    """Test integration with the refactored build system components."""

    @patch("build.TemplateRenderer")
    @patch("build.TCLBuilder")
    def test_template_based_tcl_generation(
        self, mock_tcl_builder_class, mock_template_renderer_class
    ):
        """Test that refactored build.py uses template-based TCL generation."""
        # Mock the template renderer and TCL builder
        mock_renderer = Mock()
        mock_builder = Mock()
        mock_template_renderer_class.return_value = mock_renderer
        mock_tcl_builder_class.return_value = mock_builder

        # Mock successful TCL generation
        mock_builder.build_all_tcl_scripts.return_value = {
            "01_project_setup.tcl": True,
            "02_ip_config.tcl": True,
            "build_all.tcl": True,
        }

        # Test data
        donor_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "bar_size": "0x20000",
            "mpc": "0x02",
            "mpr": "0x02",
            "subvendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "revision_id": "0x03",
        }

        # This would be called by the refactored build.py
        if hasattr(build, "build_tcl_with_templates"):
            tcl_content, tcl_file = build.build_tcl_with_templates(
                donor_info, "test.tcl"
            )

            # Verify template-based generation was used
            mock_tcl_builder_class.assert_called_once()
            mock_builder.build_all_tcl_scripts.assert_called_once()

    def test_backward_compatibility_api(self):
        """Test that refactored build.py maintains backward compatibility."""
        # Test that original API functions still exist and work
        assert hasattr(build, "build_tcl")
        assert hasattr(build, "build_sv")
        assert hasattr(build, "get_donor_info")
        assert hasattr(build, "scrape_driver_regs")

        # Test that they're callable
        assert callable(build.build_tcl)
        assert callable(build.build_sv)
        assert callable(build.get_donor_info)
        assert callable(build.scrape_driver_regs)

    @patch("build.safe_import_with_fallback")
    def test_safe_import_integration(self, mock_safe_import):
        """Test integration with safe import helper."""
        # Mock successful import
        mock_safe_import.return_value = {
            "TemplateRenderer": Mock(),
            "TCLBuilder": Mock(),
            "ConfigSpaceManager": Mock(),
        }

        # This would be used in refactored build.py initialization
        if hasattr(build, "initialize_refactored_components"):
            components = build.initialize_refactored_components()

            mock_safe_import.assert_called_once()
            assert "TemplateRenderer" in components
            assert "TCLBuilder" in components

    def test_template_vs_legacy_output_equivalence(self, temp_dir, mock_donor_info):
        """Test that template-based and legacy TCL generation produce equivalent output."""
        # Generate TCL using legacy method
        legacy_content, legacy_file = build.build_tcl(mock_donor_info, "legacy.tcl")

        # If template-based method exists, compare outputs
        if hasattr(build, "build_tcl_with_templates"):
            template_content, template_file = build.build_tcl_with_templates(
                mock_donor_info, "template.tcl"
            )

            # Key elements should be present in both
            key_elements = [
                mock_donor_info["vendor_id"],
                mock_donor_info["device_id"],
                "set_property",
                "create_project",
            ]

            for element in key_elements:
                assert element in legacy_content
                if template_content:  # Only check if template method returned content
                    assert element in template_content

    @patch("build.validate_fpga_part")
    @patch("build.select_pcie_ip_core")
    def test_fpga_strategy_integration(self, mock_select_ip, mock_validate):
        """Test integration with FPGA strategy helpers."""
        mock_validate.return_value = True
        mock_select_ip.return_value = "axi_pcie"

        # Test FPGA part validation in build process
        fpga_part = "xc7a35tcsg324-2"

        if hasattr(build, "validate_build_configuration"):
            is_valid = build.validate_build_configuration(fpga_part)
            mock_validate.assert_called_with(fpga_part)

        # Test PCIe IP core selection
        if hasattr(build, "get_pcie_ip_configuration"):
            ip_config = build.get_pcie_ip_configuration(fpga_part)
            mock_select_ip.assert_called_with(fpga_part)

    def test_constants_integration(self):
        """Test integration with constants module."""
        # Test that build.py uses constants from the constants module
        if hasattr(build, "BOARD_PARTS"):
            # Should use constants from constants.py
            from constants import BOARD_PARTS as CONST_BOARD_PARTS

            # At minimum, should have some overlap or be identical
            build_boards = set(build.BOARD_PARTS.keys()) if build.BOARD_PARTS else set()
            const_boards = set(CONST_BOARD_PARTS.keys())

            # Should have significant overlap (allowing for gradual migration)
            overlap = len(build_boards.intersection(const_boards))
            total_unique = len(build_boards.union(const_boards))

            if total_unique > 0:
                overlap_ratio = overlap / total_unique
                assert (
                    overlap_ratio > 0.5
                ), "Insufficient overlap between build.py and constants.py board definitions"

    @patch("build.write_tcl_file_with_logging")
    def test_helper_function_integration(self, mock_write_helper):
        """Test integration with build helper functions."""
        mock_write_helper.return_value = True

        # Test that build.py uses helper functions for file operations
        if hasattr(build, "write_tcl_with_helpers"):
            content = "# Test TCL content"
            file_path = "test.tcl"
            tcl_files = []

            result = build.write_tcl_with_helpers(content, file_path, tcl_files, "test")

            mock_write_helper.assert_called_once_with(
                content, file_path, tcl_files, "test", None
            )

    def test_error_handling_with_refactored_components(self):
        """Test error handling when refactored components are unavailable."""
        # Test graceful fallback when new components can't be imported
        with patch("build.safe_import_with_fallback") as mock_import:
            mock_import.return_value = {
                "TemplateRenderer": None,
                "TCLBuilder": None,
                "ConfigSpaceManager": None,
            }

            # Build should still work with legacy methods
            if hasattr(build, "build_with_fallback"):
                # Should not raise exception
                try:
                    build.build_with_fallback()
                except Exception as e:
                    pytest.fail(f"Build failed to fallback gracefully: {e}")


class TestPerformanceComparison:
    """Test performance comparison between legacy and refactored systems."""

    def test_tcl_generation_performance(self, mock_donor_info):
        """Compare performance of legacy vs template-based TCL generation."""
        import time

        # Measure legacy performance
        start_time = time.time()
        for _ in range(10):  # Multiple iterations for better measurement
            legacy_content, legacy_file = build.build_tcl(
                mock_donor_info, "perf_test.tcl"
            )
        legacy_time = time.time() - start_time

        # Measure template-based performance if available
        if hasattr(build, "build_tcl_with_templates"):
            start_time = time.time()
            for _ in range(10):
                template_content, template_file = build.build_tcl_with_templates(
                    mock_donor_info, "perf_test.tcl"
                )
            template_time = time.time() - start_time

            # Template-based should not be significantly slower
            # Allow up to 2x slower for template overhead
            assert (
                template_time < legacy_time * 2
            ), f"Template generation too slow: {template_time}s vs {legacy_time}s"

    def test_memory_usage_comparison(self, mock_donor_info):
        """Compare memory usage of legacy vs refactored systems."""
        import gc
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Measure legacy memory usage
        gc.collect()
        initial_memory = process.memory_info().rss

        for _ in range(100):  # Generate multiple times
            legacy_content, legacy_file = build.build_tcl(
                mock_donor_info, "memory_test.tcl"
            )

        gc.collect()
        legacy_memory = process.memory_info().rss - initial_memory

        # Measure template-based memory usage if available
        if hasattr(build, "build_tcl_with_templates"):
            gc.collect()
            initial_memory = process.memory_info().rss

            for _ in range(100):
                template_content, template_file = build.build_tcl_with_templates(
                    mock_donor_info, "memory_test.tcl"
                )

            gc.collect()
            template_memory = process.memory_info().rss - initial_memory

            # Template-based should not use significantly more memory
            # Allow up to 50% more memory for template caching
            assert (
                template_memory < legacy_memory * 1.5
            ), f"Template generation uses too much memory: {template_memory} vs {legacy_memory}"


class TestMigrationCompatibility:
    """Test compatibility during migration from legacy to refactored system."""

    def test_gradual_migration_support(self):
        """Test that both legacy and refactored systems can coexist."""
        # Test that legacy functions still work
        assert hasattr(build, "build_tcl")
        assert hasattr(build, "build_sv")

        # Test that new functions are available (if implemented)
        new_functions = [
            "build_tcl_with_templates",
            "build_with_helpers",
            "validate_build_configuration",
        ]

        for func_name in new_functions:
            if hasattr(build, func_name):
                assert callable(getattr(build, func_name))

    def test_configuration_migration(self):
        """Test migration of configuration from legacy to constants."""
        # Test that legacy constants are still available
        legacy_constants = ["BOARD_INFO", "APERTURE"]

        for const_name in legacy_constants:
            if hasattr(build, const_name):
                legacy_const = getattr(build, const_name)
                assert isinstance(legacy_const, dict)
                assert len(legacy_const) > 0

    def test_api_consistency(self, mock_donor_info):
        """Test that API remains consistent during migration."""
        # Test that function signatures haven't changed
        import inspect

        # Check build_tcl signature
        sig = inspect.signature(build.build_tcl)
        params = list(sig.parameters.keys())

        # Should still accept donor_info and gen_tcl parameters
        assert "donor_info" in params or len(params) >= 1
        assert "gen_tcl" in params or len(params) >= 2

        # Test that return format is consistent
        result = build.build_tcl(mock_donor_info, "test.tcl")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)  # TCL content
        assert isinstance(result[1], str)  # TCL file path
