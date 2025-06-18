#!/usr/bin/env python3
"""
Comprehensive test to verify that the build validation fix works correctly.

This test validates that the updated validation logic in src/file_manager.py
properly detects both legacy and PCILeech TCL files.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from constants import PCILEECH_BUILD_SCRIPT, PCILEECH_PROJECT_SCRIPT

from src.file_management.file_manager import FileManager


class TestBuildValidationFix:
    """Test suite for build validation fix functionality."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def file_manager(self, temp_output_dir):
        """Create a FileManager instance with temporary output directory."""
        return FileManager(output_dir=temp_output_dir)

    def create_test_tcl_file(self, file_path: Path, content_type: str = "basic"):
        """
        Create a test TCL file with appropriate content.

        Args:
            file_path: Path where to create the file
            content_type: Type of content to include ("basic", "full", "minimal")
        """
        if content_type == "full":
            content = """# Full TCL build script with all required components
# This is a comprehensive PCILeech firmware build script
# Generated for testing the build validation fix

set project_name "pcileech_firmware"
set device "xc7a35tcsg324-2"
set board_part ""

# Create project
create_project $project_name . -part $device -force

# Device configuration - this is required for validation
CONFIG.Device_ID {0x1533}
CONFIG.Vendor_ID {0x8086}
CONFIG.Subsystem_ID {0x0000}
CONFIG.Subsystem_Vendor_ID {0x8086}
CONFIG.Revision_ID {0x03}
CONFIG.Class_Code {0x020000}

# Add source files
add_files -norecurse {
    pcileech_top.sv
    device_config.sv
    bar_controller.sv
    cfg_shadow.sv
}

# Add constraint files
add_files -fileset constrs_1 -norecurse {
    pcileech_constraints.xdc
}

# Set top module
set_property top pcileech_top [current_fileset]

# Synthesis configuration
set_property strategy "Vivado Synthesis Defaults" [get_runs synth_1]
launch_runs synth_1 -jobs 8
wait_on_run synth_1

# Implementation configuration
set_property strategy "Performance_Explore" [get_runs impl_1]
launch_runs impl_1 -jobs 8
wait_on_run impl_1

# Bitstream generation
open_run impl_1
write_bitstream -force firmware.bit

# Generate hex file for flash programming
write_cfgmem -format hex -interface spix4 -size 16 -loadbit "up 0x0 firmware.bit" firmware.hex

# Generate reports
report_timing_summary -file timing_summary.rpt
report_utilization -file utilization.rpt
report_power -file power.rpt

puts "Build completed successfully"
"""
        elif content_type == "minimal":
            content = """# Minimal TCL script
set project_name "test"
"""
        else:  # basic
            content = """# Basic TCL build script
set project_name "pcileech_firmware"
CONFIG.Device_ID {0x1533}
launch_runs synth_1
launch_runs impl_1
write_cfgmem -format hex -interface spix4 -size 16 firmware.hex
"""

        file_path.write_text(content)

    def test_legacy_build_firmware_tcl_validation(self, file_manager, temp_output_dir):
        """Test validation succeeds when build_firmware.tcl exists."""
        # Create legacy build_firmware.tcl file
        tcl_file = temp_output_dir / "build_firmware.tcl"
        self.create_test_tcl_file(tcl_file, "full")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        # The validation should succeed since we have device config and hex generation
        assert result["validation_status"] == "success_tcl_ready"
        assert result["tcl_file_info"] is not None
        assert result["tcl_file_info"]["filename"] == "build_firmware.tcl"
        assert result["tcl_file_info"]["has_device_config"] is True
        assert result["tcl_file_info"]["has_synthesis"] is True
        assert result["tcl_file_info"]["has_implementation"] is True
        assert result["tcl_file_info"]["has_hex_generation"] is True
        assert result["build_mode"] == "tcl_only"

    def test_legacy_build_all_tcl_validation(self, file_manager, temp_output_dir):
        """Test validation succeeds when build_all.tcl exists."""
        # Create legacy build_all.tcl file
        tcl_file = temp_output_dir / "build_all.tcl"
        self.create_test_tcl_file(tcl_file, "full")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        assert result["validation_status"] == "success_tcl_ready"
        assert result["tcl_file_info"] is not None
        assert result["tcl_file_info"]["filename"] == "build_all.tcl"
        assert result["tcl_file_info"]["has_device_config"] is True
        assert result["build_mode"] == "tcl_only"

    def test_pcileech_vivado_build_tcl_validation(self, file_manager, temp_output_dir):
        """Test validation succeeds when vivado_build.tcl exists."""
        # Create PCILeech vivado_build.tcl file
        tcl_file = temp_output_dir / PCILEECH_BUILD_SCRIPT
        self.create_test_tcl_file(tcl_file, "full")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        assert result["validation_status"] == "success_tcl_ready"
        assert result["tcl_file_info"] is not None
        assert result["tcl_file_info"]["filename"] == PCILEECH_BUILD_SCRIPT
        assert result["tcl_file_info"]["has_device_config"] is True
        assert result["build_mode"] == "tcl_only"

    def test_pcileech_vivado_generate_project_tcl_validation(
        self, file_manager, temp_output_dir
    ):
        """Test validation succeeds when vivado_generate_project.tcl exists."""
        # Create PCILeech vivado_generate_project.tcl file
        tcl_file = temp_output_dir / PCILEECH_PROJECT_SCRIPT
        self.create_test_tcl_file(tcl_file, "full")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        assert result["validation_status"] == "success_tcl_ready"
        assert result["tcl_file_info"] is not None
        assert result["tcl_file_info"]["filename"] == PCILEECH_PROJECT_SCRIPT
        assert result["tcl_file_info"]["has_device_config"] is True
        assert result["build_mode"] == "tcl_only"

    def test_mixed_legacy_and_pcileech_files(self, file_manager, temp_output_dir):
        """Test validation works when both legacy and PCILeech files exist."""
        # Create both legacy and PCILeech files
        legacy_file = temp_output_dir / "build_firmware.tcl"
        pcileech_file = temp_output_dir / PCILEECH_BUILD_SCRIPT

        self.create_test_tcl_file(legacy_file, "full")
        self.create_test_tcl_file(pcileech_file, "full")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results - should pick up the first one found (legacy has priority)
        assert result["validation_status"] == "success_tcl_ready"
        assert result["tcl_file_info"] is not None
        assert result["tcl_file_info"]["filename"] == "build_firmware.tcl"
        assert result["build_mode"] == "tcl_only"

    def test_both_pcileech_files_exist(self, file_manager, temp_output_dir):
        """Test validation when both PCILeech files exist."""
        # Create both PCILeech files
        build_file = temp_output_dir / PCILEECH_BUILD_SCRIPT
        project_file = temp_output_dir / PCILEECH_PROJECT_SCRIPT

        self.create_test_tcl_file(build_file, "full")
        self.create_test_tcl_file(project_file, "basic")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results - should pick up the build script first
        assert result["validation_status"] == "success_tcl_ready"
        assert result["tcl_file_info"] is not None
        assert result["tcl_file_info"]["filename"] == PCILEECH_BUILD_SCRIPT
        assert result["build_mode"] == "tcl_only"

    def test_no_tcl_files_validation_fails(self, file_manager, temp_output_dir):
        """Test validation fails when no TCL files exist."""
        # Don't create any TCL files

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        assert result["validation_status"] == "failed_no_tcl"
        assert result["tcl_file_info"] is None
        # Note: build_mode is set to "tcl_only" by default, even when no TCL files exist
        assert result["build_mode"] == "tcl_only"

    def test_partial_pcileech_files_only_build_script(
        self, file_manager, temp_output_dir
    ):
        """Test behavior when only PCILeech build script exists."""
        # Create only the build script
        tcl_file = temp_output_dir / PCILEECH_BUILD_SCRIPT
        self.create_test_tcl_file(tcl_file, "full")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        assert result["validation_status"] == "success_tcl_ready"
        assert result["tcl_file_info"] is not None
        assert result["tcl_file_info"]["filename"] == PCILEECH_BUILD_SCRIPT

    def test_partial_pcileech_files_only_project_script(
        self, file_manager, temp_output_dir
    ):
        """Test behavior when only PCILeech project script exists."""
        # Create only the project script
        tcl_file = temp_output_dir / PCILEECH_PROJECT_SCRIPT
        self.create_test_tcl_file(tcl_file, "full")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        assert result["validation_status"] == "success_tcl_ready"
        assert result["tcl_file_info"] is not None
        assert result["tcl_file_info"]["filename"] == PCILEECH_PROJECT_SCRIPT

    def test_minimal_tcl_content_validation(self, file_manager, temp_output_dir):
        """Test validation with minimal TCL content."""
        # Create TCL file with minimal content
        tcl_file = temp_output_dir / "build_firmware.tcl"
        self.create_test_tcl_file(tcl_file, "minimal")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results - should warn about missing hex (takes priority over incomplete)
        assert result["validation_status"] == "warning_missing_hex"
        assert result["tcl_file_info"] is not None
        assert result["tcl_file_info"]["has_device_config"] is False

    def test_tcl_without_hex_generation(self, file_manager, temp_output_dir):
        """Test validation when TCL file lacks hex generation commands."""
        # Create TCL file without hex generation
        tcl_file = temp_output_dir / "build_firmware.tcl"
        content = """
# TCL script without hex generation
set project_name "pcileech_firmware"
CONFIG.Device_ID {0x1533}
launch_runs synth_1
launch_runs impl_1
"""
        tcl_file.write_text(content)

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        assert result["validation_status"] == "warning_missing_hex"
        assert result["tcl_file_info"] is not None
        assert result["tcl_file_info"]["has_hex_generation"] is False

    def test_full_vivado_build_with_bitstream(self, file_manager, temp_output_dir):
        """Test validation with full Vivado build (bitstream present)."""
        # Create TCL file and bitstream
        tcl_file = temp_output_dir / "build_firmware.tcl"
        bitstream_file = temp_output_dir / "firmware.bit"

        self.create_test_tcl_file(tcl_file, "full")

        # Create a realistic bitstream file (> 1MB)
        bitstream_content = b"0" * (2 * 1024 * 1024)  # 2MB of data
        bitstream_file.write_bytes(bitstream_content)

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        assert result["validation_status"] == "success_full_build"
        assert result["build_mode"] == "full_vivado"
        assert result["bitstream_info"] is not None
        assert result["bitstream_info"]["size_mb"] == 2.0
        assert result["bitstream_info"]["filename"] == "firmware.bit"

    def test_small_bitstream_warning(self, file_manager, temp_output_dir):
        """Test validation warns about small bitstream files."""
        # Create TCL file and small bitstream
        tcl_file = temp_output_dir / "build_firmware.tcl"
        bitstream_file = temp_output_dir / "firmware.bit"

        self.create_test_tcl_file(tcl_file, "full")

        # Create a small bitstream file (< 1MB)
        bitstream_content = b"0" * (500 * 1024)  # 500KB
        bitstream_file.write_bytes(bitstream_content)

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        assert result["validation_status"] == "warning_small_bitstream"
        assert result["build_mode"] == "full_vivado"
        assert result["bitstream_info"] is not None

    def test_backward_compatibility_maintained(self, file_manager, temp_output_dir):
        """Test that backward compatibility with legacy files is maintained."""
        # Test all legacy file names
        legacy_files = ["build_firmware.tcl", "build_all.tcl"]

        for legacy_file in legacy_files:
            # Clean up any existing files
            for file in temp_output_dir.glob("*.tcl"):
                file.unlink()

            # Create the legacy file
            tcl_file = temp_output_dir / legacy_file
            self.create_test_tcl_file(tcl_file, "full")

            # Run validation
            result = file_manager.validate_final_outputs()

            # Verify validation results
            assert result["validation_status"] == "success_tcl_ready"
            assert result["tcl_file_info"]["filename"] == legacy_file
            assert result["build_mode"] == "tcl_only"

    def test_pcileech_files_detection(self, file_manager, temp_output_dir):
        """Test that PCILeech files are properly detected."""
        pcileech_files = [PCILEECH_BUILD_SCRIPT, PCILEECH_PROJECT_SCRIPT]

        for pcileech_file in pcileech_files:
            # Clean up any existing files
            for file in temp_output_dir.glob("*.tcl"):
                file.unlink()

            # Create the PCILeech file
            tcl_file = temp_output_dir / pcileech_file
            self.create_test_tcl_file(tcl_file, "full")

            # Run validation
            result = file_manager.validate_final_outputs()

            # Verify validation results
            assert result["validation_status"] == "success_tcl_ready"
            assert result["tcl_file_info"]["filename"] == pcileech_file
            assert result["build_mode"] == "tcl_only"

    def test_file_priority_order(self, file_manager, temp_output_dir):
        """Test that files are detected in the correct priority order."""
        # Create all possible TCL files
        files_to_create = [
            "build_firmware.tcl",
            "build_all.tcl",
            PCILEECH_BUILD_SCRIPT,
            PCILEECH_PROJECT_SCRIPT,
        ]

        for file_name in files_to_create:
            tcl_file = temp_output_dir / file_name
            self.create_test_tcl_file(tcl_file, "full")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Should pick up build_firmware.tcl first (highest priority)
        assert result["validation_status"] == "success_tcl_ready"
        assert result["tcl_file_info"]["filename"] == "build_firmware.tcl"

    def test_validation_with_additional_files(self, file_manager, temp_output_dir):
        """Test validation works correctly with additional output files present."""
        # Create TCL file
        tcl_file = temp_output_dir / "build_firmware.tcl"
        self.create_test_tcl_file(tcl_file, "full")

        # Create additional files that might be present
        (temp_output_dir / "firmware.mcs").write_text("MCS flash file content")
        (temp_output_dir / "debug.ltx").write_text("Debug probe file")
        (temp_output_dir / "timing.rpt").write_text("Timing report")
        (temp_output_dir / "utilization.rpt").write_text("Utilization report")

        # Run validation
        result = file_manager.validate_final_outputs()

        # Verify validation results
        assert result["validation_status"] == "success_tcl_ready"
        assert result["flash_file_info"] is not None
        assert result["debug_file_info"] is not None
        assert len(result["reports_info"]) == 2
        assert result["flash_file_info"]["filename"] == "firmware.mcs"
        assert result["debug_file_info"]["filename"] == "debug.ltx"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
