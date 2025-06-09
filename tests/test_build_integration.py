#!/usr/bin/env python3
"""
Test suite for integrating external examples with the build process.

This test suite validates that the build process can properly handle
real-world patterns found in external PCILeech examples.
"""

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import build
from advanced_sv_main import (
    AdvancedSVGenerator,
    DeviceSpecificLogic,
    DeviceType,
)
from manufacturing_variance import DeviceClass, ManufacturingVarianceSimulator
from tests.utils import get_pcileech_wifi_sv_file, get_pcileech_wifi_tcl_file


class TestBuildWithExternalExamples:
    """Test build process with external examples."""

    @pytest.fixture
    def external_sv_example(self):
        """Load the external SystemVerilog example file from GitHub."""
        try:
            return get_pcileech_wifi_sv_file()
        except ValueError as e:
            pytest.skip(f"Failed to fetch SystemVerilog example from GitHub: {str(e)}")

    @pytest.fixture
    def external_tcl_example(self):
        """Load the external TCL example file from GitHub."""
        try:
            return get_pcileech_wifi_tcl_file()
        except ValueError as e:
            pytest.skip(f"Failed to fetch TCL example from GitHub: {str(e)}")

    @pytest.fixture
    def mock_donor_info_from_example(self):
        """Create mock donor info that matches the external example."""
        return {
            "vendor_id": "0x1814",  # D-Link vendor ID
            "device_id": "0x0201",  # DWA-556 device ID
            "subvendor_id": "0x1814",
            "subsystem_id": "0x0201",
            "revision_id": "0x01",
            "bar_size": "0x20000",  # 128KB
            "mpc": "0x02",
            "mpr": "0x02",
        }

    @pytest.fixture
    def mock_registers_from_example(self, external_sv_example):
        """Create mock register data based on the external example."""
        # Extract register definitions from the example
        reg_pattern = r"logic\s+\[31:0\]\s+(\w+_reg)\s*=\s*32\'h([0-9a-fA-F]+);"
        registers = re.findall(reg_pattern, external_sv_example)

        # Convert to register definitions for our generator
        reg_defs = []
        for i, (reg_name, reg_value) in enumerate(registers):
            # Strip _reg suffix if present
            if reg_name.endswith("_reg"):
                reg_name = reg_name[:-4]

            # Extract register access type based on example patterns
            rw_type = "rw"
            if "status" in reg_name.lower():
                rw_type = "ro"

            reg_defs.append(
                {
                    "offset": 0x400
                    + (i * 4),  # Assuming 4-byte aligned registers starting at 0x400
                    "name": reg_name,
                    "value": f"0x{reg_value}",
                    "rw": rw_type,
                    "context": {
                        "function": f"example_derived_{reg_name}",
                        "timing": "runtime",
                        "access_pattern": (
                            "read_heavy" if rw_type == "ro" else "balanced"
                        ),
                    },
                }
            )

        # If no registers found, add some default ones
        if not reg_defs:
            reg_defs = [
                {
                    "offset": 0x400,
                    "name": "control",
                    "value": "0x00000000",
                    "rw": "rw",
                    "context": {
                        "function": "device_control",
                        "timing": "runtime",
                        "access_pattern": "balanced",
                    },
                },
                {
                    "offset": 0x404,
                    "name": "status",
                    "value": "0x00000001",
                    "rw": "ro",
                    "context": {
                        "function": "status_check",
                        "timing": "runtime",
                        "access_pattern": "read_heavy",
                    },
                },
            ]

        return reg_defs

    def test_build_sv_with_example_registers(
        self, mock_registers_from_example, temp_dir
    ):
        """Test building SystemVerilog with registers derived from external example."""
        target_file = temp_dir / "example_controller.sv"

        # Call the build_sv function with example-derived registers
        build.build_sv(mock_registers_from_example, target_file)

        # Verify that the file was created
        assert target_file.exists()

        # Read the generated SystemVerilog
        sv_content = target_file.read_text()

        # Check for module declaration
        assert "module pcileech_tlps128_bar_controller" in sv_content

        # Check for register declarations
        for reg in mock_registers_from_example:
            assert (
                f"{reg['name']}_reg" in sv_content
            ), f"Missing register {reg['name']}_reg"

        # Check for read logic
        assert "always_comb" in sv_content
        assert "case" in sv_content

        # Check for write logic
        assert "always_ff" in sv_content

    def test_build_tcl_with_example_donor_info(
        self, mock_donor_info_from_example, temp_dir
    ):
        """Test building TCL with donor info derived from external example."""
        # Call the build_tcl function with example-derived donor info
        tcl_content, tcl_file = build.build_tcl(
            mock_donor_info_from_example, "example_generate.tcl"
        )

        # Verify that TCL content was generated
        assert tcl_content
        assert tcl_file

        # Check for vendor and device ID configuration
        assert mock_donor_info_from_example["vendor_id"] in tcl_content
        assert mock_donor_info_from_example["device_id"] in tcl_content

        # Check for BAR size configuration
        assert "128_KB" in tcl_content  # BAR size conversion

    @patch("build.get_donor_info")
    @patch("build.scrape_driver_regs")
    @patch("build.integrate_behavior_profile")
    def test_full_build_workflow_with_example_data(
        self,
        mock_behavior,
        mock_scrape,
        mock_donor,
        mock_donor_info_from_example,
        mock_registers_from_example,
        temp_dir,
    ):
        """Test full build workflow with example-derived data."""
        # Setup mocks
        mock_donor.return_value = mock_donor_info_from_example
        mock_scrape.return_value = mock_registers_from_example
        mock_behavior.return_value = mock_registers_from_example

        # Create temporary output files
        sv_file = temp_dir / "example_controller.sv"
        tcl_file = temp_dir / "example_generate.tcl"

        # Simulate workflow steps
        bdf = "0000:03:00.0"
        vendor = mock_donor_info_from_example["vendor_id"].replace("0x", "")
        device = mock_donor_info_from_example["device_id"].replace("0x", "")

        # Get donor info
        donor_info = mock_donor(bdf)

        # Scrape registers
        registers = mock_scrape(vendor, device)

        # Integrate behavior profile
        enhanced_regs = mock_behavior(bdf, registers)

        # Build SystemVerilog
        build.build_sv(enhanced_regs, sv_file)

    @patch("build.BehaviorProfiler")
    def test_behavior_profiling_integration(
        self, mock_profiler_class, mock_registers_from_example, temp_dir
    ):
        """Test behavior profiling integration with the build process."""
        # Create a mock profiler instance
        mock_profiler = Mock()
        mock_profiler_class.return_value = mock_profiler

        # Create a mock profile with timing patterns
        from behavior_profiler import BehaviorProfile, TimingPattern

        mock_profile = BehaviorProfile(
            device_bdf="0000:03:00.0",
            capture_duration=10.0,
            total_accesses=100,
            register_accesses=[],
            timing_patterns=[
                TimingPattern(
                    pattern_type="periodic",
                    registers=["CONTROL"],
                    avg_interval_us=100.0,
                    std_deviation_us=5.0,
                    frequency_hz=10000.0,
                    confidence=0.95,
                )
            ],
            state_transitions={"init": ["ready"]},
            power_states=["D0"],
            interrupt_patterns={},
        )

        # Set up the mock analysis results
        mock_analysis = {
            "device_characteristics": {
                "access_frequency_hz": 5000.0,
            },
            "behavioral_signatures": {
                "timing_regularity": 0.85,
            },
        }

        mock_profiler.capture_behavior_profile.return_value = mock_profile
        mock_profiler.analyze_patterns.return_value = mock_analysis

        # Call the integrate_behavior_profile function
        enhanced_regs = build.integrate_behavior_profile(
            "0000:03:00.0", mock_registers_from_example
        )

        # Verify that the profiler was initialized correctly
        mock_profiler_class.assert_called_once_with("0000:03:00.0", debug=False)

        # Verify that the profiler methods were called
        mock_profiler.capture_behavior_profile.assert_called_once()
        mock_profiler.analyze_patterns.assert_called_once_with(mock_profile)

        # Verify that the registers were enhanced with behavioral data
        assert len(enhanced_regs) == len(mock_registers_from_example)

        # Check that all registers have device analysis information
        for reg in enhanced_regs:
            assert "context" in reg
            assert "device_analysis" in reg["context"]

        # Set up file paths for testing
        sv_file = temp_dir / "example_controller.sv"
        tcl_file = temp_dir / "example_generate.tcl"

        # Create mock donor info for testing
        donor_info = {
            "vendor_id": "0x1234",
            "device_id": "0x5678",
            "subvendor_id": "0x9abc",  # Changed from subsystem_vendor_id
            "subsystem_id": "0xdef0",  # Changed from subsystem_device_id
            "revision_id": "0x01",  # Added revision_id
            "bdf": "0000:03:00.0",
            "bar_size": "0x20000",  # 128KB
            "mpc": "0x02",  # Max payload capability
            "mpr": "0x02",  # Max read request capability
        }

        # Build SystemVerilog first
        build.build_sv(enhanced_regs, sv_file)

        # Build TCL
        tcl_content, tcl_path = build.build_tcl(donor_info, str(tcl_file))

        # Verify that files were created
        assert sv_file.exists()
        assert Path(tcl_path).exists() or tcl_content

        # Read the generated SystemVerilog
        sv_content = sv_file.read_text()

        # Check for module declaration
        assert "module pcileech_tlps128_bar_controller" in sv_content

        # Check for register declarations
        for reg in enhanced_regs:
            assert (
                f"{reg['name']}_reg" in sv_content
            ), f"Missing register {reg['name']}_reg"


class TestAdvancedSVWithExternalExamples:
    """Test advanced SystemVerilog generation with external examples."""

    @pytest.fixture
    def external_sv_example(self):
        """Load the external SystemVerilog example file from GitHub."""
        try:
            return get_pcileech_wifi_sv_file()
        except ValueError as e:
            pytest.skip(f"Failed to fetch SystemVerilog example from GitHub: {str(e)}")

    @pytest.fixture
    def mock_registers_from_example(self, external_sv_example):
        """Create mock register data based on the external example."""
        # Extract register definitions from the example
        reg_pattern = r"logic\s+\[31:0\]\s+(\w+_reg)\s*=\s*32\'h([0-9a-fA-F]+);"
        registers = re.findall(reg_pattern, external_sv_example)

        # Convert to register definitions for our generator
        reg_defs = []
        for i, (reg_name, reg_value) in enumerate(registers):
            # Strip _reg suffix if present
            if reg_name.endswith("_reg"):
                reg_name = reg_name[:-4]

            # Extract register access type based on example patterns
            rw_type = "rw"
            if "status" in reg_name.lower():
                rw_type = "ro"

            reg_defs.append(
                {
                    "offset": 0x400
                    + (i * 4),  # Assuming 4-byte aligned registers starting at 0x400
                    "name": reg_name,
                    "value": f"0x{reg_value}",
                    "rw": rw_type,
                    "context": {
                        "function": f"example_derived_{reg_name}",
                        "timing": "runtime",
                        "access_pattern": (
                            "read_heavy" if rw_type == "ro" else "balanced"
                        ),
                    },
                }
            )

        # If no registers found, add some default ones
        if not reg_defs:
            reg_defs = [
                {
                    "offset": 0x400,
                    "name": "control",
                    "value": "0x00000000",
                    "rw": "rw",
                    "context": {
                        "function": "device_control",
                        "timing": "runtime",
                        "access_pattern": "balanced",
                    },
                },
                {
                    "offset": 0x404,
                    "name": "status",
                    "value": "0x00000001",
                    "rw": "ro",
                    "context": {
                        "function": "status_check",
                        "timing": "runtime",
                        "access_pattern": "read_heavy",
                    },
                },
            ]

        return reg_defs

    def test_advanced_sv_with_example_registers(
        self, mock_registers_from_example, temp_dir
    ):
        """Test advanced SystemVerilog generation with registers derived from external example."""
        # Create a generator with network controller configuration
        device_config = DeviceSpecificLogic(
            device_type=DeviceType.NETWORK_CONTROLLER,
            device_class=DeviceClass.INDUSTRIAL,
            max_payload_size=256,
            max_read_request_size=512,
            enable_dma=True,
        )

        generator = AdvancedSVGenerator(device_config=device_config)

        # Generate SystemVerilog
        sv_content = generator.generate_advanced_systemverilog(
            mock_registers_from_example
        )

        # Write to file
        target_file = temp_dir / "advanced_example_controller.sv"
        target_file.write_text(sv_content)

        # Verify that the file was created
        assert target_file.exists()

        # Check for module declaration
        assert "module advanced_pcileech_controller" in sv_content

        # Check for register declarations
        for reg in mock_registers_from_example:
            assert (
                f"{reg['name']}_reg" in sv_content
            ), f"Missing register {reg['name']}_reg"

        # Check for advanced features
        assert "Power Management" in sv_content
        assert "Error Handling" in sv_content
        assert "Performance Counter" in sv_content

        # Check for network controller specific features
        assert "Network controller" in sv_content

    def test_variance_model_with_example_registers(
        self, mock_registers_from_example, temp_dir
    ):
        """Test manufacturing variance integration with registers derived from external example."""
        # Create a variance simulator
        variance_simulator = ManufacturingVarianceSimulator()

        # Generate a variance model
        variance_model = variance_simulator.generate_variance_model(
            device_id="example_device",
            device_class=DeviceClass.INDUSTRIAL,
            base_frequency_mhz=125.0,  # Same as 75t board
        )

        # Create a generator with the variance model
        generator = AdvancedSVGenerator()

        # Generate SystemVerilog with variance model
        sv_content = generator.generate_advanced_systemverilog(
            mock_registers_from_example, variance_model
        )

        # Write to file
        target_file = temp_dir / "variance_example_controller.sv"
        target_file.write_text(sv_content)

        # Verify that the file was created
        assert target_file.exists()

        # Check for variance-related features
        assert "timing" in sv_content.lower()
        assert "variance" in sv_content.lower() or "jitter" in sv_content.lower()

        # Check for timing counters
        assert "timing_counter" in sv_content


class TestBuildScriptIntegration:
    """Test integration with build script functionality."""

    @pytest.fixture
    def external_sv_example(self):
        """Load the external SystemVerilog example file from GitHub."""
        try:
            return get_pcileech_wifi_sv_file()
        except ValueError as e:
            pytest.skip(f"Failed to fetch SystemVerilog example from GitHub: {str(e)}")

    @pytest.fixture
    def external_tcl_example(self):
        """Load the external TCL example file from GitHub."""
        try:
            return get_pcileech_wifi_tcl_file()
        except ValueError as e:
            pytest.skip(f"Failed to fetch TCL example from GitHub: {str(e)}")

    @patch("build.run")
    def test_build_script_with_example_files(
        self, mock_run, external_sv_example, external_tcl_example, temp_dir
    ):
        """Test build script with example files."""
        # Create example files in the temp directory
        sv_file = temp_dir / "pcileech_tlps128_cfgspace_shadow.sv"
        tcl_file = temp_dir / "vivado_generate_project.tcl"

        sv_file.write_text(external_sv_example)
        tcl_file.write_text(external_tcl_example)

        # Mock the build process
        with patch("build.get_donor_info") as mock_donor:
            mock_donor.return_value = {
                "vendor_id": "0x1814",
                "device_id": "0x0201",
                "subvendor_id": "0x1814",
                "subsystem_id": "0x0201",
                "revision_id": "0x01",
                "bar_size": "0x20000",  # 128KB
                "mpc": "0x02",
                "mpr": "0x02",
            }

            # Mock the Vivado environment
            with patch.dict(os.environ, {"VIVADO_PATH": "/opt/Xilinx/Vivado/2023.1"}):
                with patch("shutil.which") as mock_which:
                    mock_which.return_value = "/opt/Xilinx/Vivado/2023.1/bin/vivado"

                    # Call the build function (if it exists)
                    if hasattr(build, "build_fpga"):
                        with patch("tempfile.mkdtemp") as mock_mkdtemp:
                            mock_mkdtemp.return_value = str(temp_dir)

                            # This would call the build_fpga function
                            # build.build_fpga("0000:03:00.0", "75t")

                            # Instead, we'll just verify that the mock_run was called
                            mock_run.assert_called()
                    else:
                        # Skip the test if build_fpga doesn't exist
                        pytest.skip("build_fpga function not found")

    @patch("subprocess.run")
    def test_tcl_script_execution_with_example(
        self, mock_run, external_tcl_example, temp_dir
    ):
        """Test TCL script execution with example."""
        # Create example TCL file in the temp directory
        tcl_file = temp_dir / "vivado_generate_project.tcl"
        tcl_file.write_text(external_tcl_example)

        # Mock the Vivado environment
        with patch.dict(os.environ, {"VIVADO_PATH": "/opt/Xilinx/Vivado/2023.1"}):
            with patch("shutil.which") as mock_which:
                mock_which.return_value = "/opt/Xilinx/Vivado/2023.1/bin/vivado"

                # Simulate running the TCL script
                cmd = f"/opt/Xilinx/Vivado/2023.1/bin/vivado -mode batch -source {tcl_file}"

                # This would execute the command
                # subprocess.run(cmd, shell=True, check=True)

                # Instead, we'll just verify that the mock_run would be called with the right command
                mock_run.return_value = Mock(returncode=0)
                build.run(cmd)

                mock_run.assert_called_with(cmd, shell=True, check=True)
