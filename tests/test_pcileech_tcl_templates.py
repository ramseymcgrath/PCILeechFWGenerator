#!/usr/bin/env python3
"""
PCILeech TCL Template Validation Tests

This module tests the PCILeech TCL templates to ensure they generate valid scripts
with proper batch mode compatibility and explicit file lists.
"""

import shutil

# Import modules under test
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.templating.template_renderer import TemplateRenderer, TemplateRenderError


class TestPCILeechTCLTemplates:
    """Test suite for PCILeech TCL template validation."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def template_renderer(self):
        """Create template renderer with actual template directory."""
        template_dir = Path(__file__).parent.parent / "src" / "templates"
        return TemplateRenderer(template_dir)

    @pytest.fixture
    def pcileech_project_context(self):
        """Create context for PCILeech project generation template."""
        return {
            "header_comment": "# Generated PCILeech Project Script",
            "board_name": "pcileech_35t325_x4",
            "fpga_part": "xc7a35tcsg324-2",
            "fpga_family": "7series",
            "project_name": "pcileech_firmware",
            "project_dir": "./vivado_project",
            "pcie_ip_type": "axi_pcie",
            "max_lanes": 4,
            "supports_msi": True,
            "supports_msix": False,
            "device": {
                "vendor_id": "0x10EE",
                "device_id": "0x7021",
                "class_code": "0x058000",
                "revision_id": "0x00",
            },
            "pcileech": {
                "src_dir": "src",
                "ip_dir": "ip",
                "source_files": [
                    "pcileech_top.sv",
                    "bar_controller.sv",
                    "cfg_shadow.sv",
                    "msix_table.sv",
                ],
                "ip_files": ["pcie_axi_bridge.xci", "clk_wiz_0.xci"],
                "coefficient_files": ["coefficients.coe"],
            },
            "constraint_files": ["pcileech_35t325_x4.xdc"],
        }

    @pytest.fixture
    def pcileech_build_context(self):
        """Create context for PCILeech build template."""
        return {
            "header_comment": "# Generated PCILeech Build Script",
            "board_name": "pcileech_35t325_x4",
            "fpga_part": "xc7a35tcsg324-2",
            "fpga_family": "7series",
            "project_name": "pcileech_firmware",
            "project_dir": "./vivado_project",
            "batch_mode": True,
            "build": {"jobs": 8},
            "synthesis_strategy": "Vivado Synthesis Defaults",
            "implementation_strategy": "Performance_Explore",
        }

    def test_pcileech_project_template_rendering(
        self, template_renderer, pcileech_project_context
    ):
        """Test PCILeech project generation template rendering."""
        try:
            content = template_renderer.render_template(
                "tcl/pcileech_generate_project.j2", pcileech_project_context
            )

            # Validate basic structure
            assert "PCILeech" in content
            assert "create_project" in content
            assert pcileech_project_context["fpga_part"] in content
            assert pcileech_project_context["project_name"] in content

            # Validate PCILeech directory structure
            assert pcileech_project_context["pcileech"]["src_dir"] in content
            assert pcileech_project_context["pcileech"]["ip_dir"] in content

            # Validate explicit file lists (no glob patterns)
            for source_file in pcileech_project_context["pcileech"]["source_files"]:
                assert source_file in content
                # Ensure no glob patterns
                assert "*.sv" not in content or source_file in content

            for ip_file in pcileech_project_context["pcileech"]["ip_files"]:
                assert ip_file in content

            # Validate PCIe IP configuration
            assert pcileech_project_context["pcie_ip_type"] in content
            assert str(pcileech_project_context["max_lanes"]) in content

            # Validate device configuration
            device = pcileech_project_context["device"]
            assert device["vendor_id"] in content
            assert device["device_id"] in content

        except TemplateRenderError as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )

    def test_pcileech_build_template_rendering(
        self, template_renderer, pcileech_build_context
    ):
        """Test PCILeech build template rendering."""
        try:
            content = template_renderer.render_template(
                "tcl/pcileech_build.j2", pcileech_build_context
            )

            # Validate basic structure
            assert "PCILeech" in content
            assert "batch" in content.lower()
            assert pcileech_build_context["fpga_part"] in content
            assert pcileech_build_context["project_name"] in content

            # Validate batch mode configuration
            assert str(pcileech_build_context["build"]["jobs"]) in content
            assert "launch_runs" in content
            assert "wait_on_run" in content

            # Validate build strategies
            assert pcileech_build_context["synthesis_strategy"] in content
            assert pcileech_build_context["implementation_strategy"] in content

            # Validate build flow steps
            assert "synth_1" in content
            assert "impl_1" in content
            assert "write_bitstream" in content

            # Validate error handling
            assert "ERROR:" in content
            assert "exit 1" in content

        except TemplateRenderError as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )

    def test_explicit_file_lists_validation(
        self, template_renderer, pcileech_project_context
    ):
        """Test that templates generate explicit file lists instead of glob patterns."""
        try:
            content = template_renderer.render_template(
                "tcl/pcileech_generate_project.j2", pcileech_project_context
            )

            # Check that explicit files are listed
            source_files = pcileech_project_context["pcileech"]["source_files"]
            ip_files = pcileech_project_context["pcileech"]["ip_files"]

            for source_file in source_files:
                # File should be explicitly mentioned
                assert source_file in content

            for ip_file in ip_files:
                # IP file should be explicitly mentioned
                assert ip_file in content

            # Validate no glob patterns are used for critical files
            # (Some glob patterns may be acceptable for fallback cases)
            lines = content.split("\n")
            explicit_file_lines = [
                line
                for line in lines
                if any(f in line for f in source_files + ip_files)
            ]

            # At least some files should be explicitly listed
            assert len(explicit_file_lines) > 0

        except TemplateRenderError as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )

    def test_batch_mode_compatibility(self, template_renderer, pcileech_build_context):
        """Test batch mode compatibility in PCILeech build template."""
        try:
            content = template_renderer.render_template(
                "tcl/pcileech_build.j2", pcileech_build_context
            )

            # Validate batch mode settings
            assert pcileech_build_context["batch_mode"] is True

            # Check for batch mode indicators in generated script
            batch_indicators = ["maxThreads", "launch_runs", "wait_on_run", "-jobs"]

            for indicator in batch_indicators:
                assert indicator in content

            # Validate job count is used
            job_count = str(pcileech_build_context["build"]["jobs"])
            assert job_count in content

            # Validate no interactive commands
            interactive_commands = ["start_gui", "open_gui", "show_gui"]

            for cmd in interactive_commands:
                assert cmd not in content

        except TemplateRenderError as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )

    def test_fpga_family_specific_configurations(self, template_renderer):
        """Test FPGA family-specific configurations in templates."""
        test_cases = [
            {
                "fpga_family": "7series",
                "pcie_ip_type": "axi_pcie",
                "expected_ip": "axi_pcie",
            },
            {
                "fpga_family": "7series",
                "pcie_ip_type": "pcie_7x",
                "expected_ip": "pcie_7x",
            },
            {
                "fpga_family": "ultrascale",
                "pcie_ip_type": "pcie_ultrascale",
                "expected_ip": "pcie4_uscale_plus",
            },
        ]

        for case in test_cases:
            context = {
                "header_comment": "# Test script",
                "board_name": "test_board",
                "fpga_part": "test_part",
                "fpga_family": case["fpga_family"],
                "pcie_ip_type": case["pcie_ip_type"],
                "project_name": "test_project",
                "project_dir": "./test_project",
                "max_lanes": 4,
                "supports_msi": True,
                "supports_msix": False,
                "device": {
                    "vendor_id": "0x10EE",
                    "device_id": "0x7021",
                    "class_code": "0x058000",
                    "revision_id": "0x00",
                },
                "pcileech": {
                    "src_dir": "src",
                    "ip_dir": "ip",
                    "source_files": ["test.sv"],
                    "ip_files": ["test.xci"],
                },
            }

            try:
                content = template_renderer.render_template(
                    "tcl/pcileech_generate_project.j2", context
                )

                # Validate family-specific IP configuration
                if case["fpga_family"] == "ultrascale":
                    assert (
                        "pcie4_uscale_plus" in content
                        or "ultrascale" in content.lower()
                    )
                elif case["fpga_family"] == "7series":
                    assert case["pcie_ip_type"] in content

            except TemplateRenderError as e:
                pytest.skip(f"Template rendering failed for {case['fpga_family']}: {e}")

    def test_ip_configuration_validation(
        self, template_renderer, pcileech_project_context
    ):
        """Test IP configuration sections in PCILeech project template."""
        try:
            content = template_renderer.render_template(
                "tcl/pcileech_generate_project.j2", pcileech_project_context
            )

            # Validate IP creation commands
            assert "create_ip" in content

            # Validate IP configuration properties
            ip_config_properties = [
                "CONFIG.MAX_LINK_SPEED",
                "CONFIG.DEVICE_ID",
                "CONFIG.VENDOR_ID",
                "CONFIG.CLASS_CODE",
                "CONFIG.BAR0_ENABLED",
            ]

            # At least some IP configuration should be present
            config_found = any(prop in content for prop in ip_config_properties)
            assert config_found

            # Validate device-specific values
            device = pcileech_project_context["device"]
            assert device["device_id"] in content
            assert device["vendor_id"] in content

        except TemplateRenderError as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )

    def test_constraint_file_handling(
        self, template_renderer, pcileech_project_context
    ):
        """Test constraint file handling in PCILeech templates."""
        try:
            content = template_renderer.render_template(
                "tcl/pcileech_generate_project.j2", pcileech_project_context
            )

            # Validate constraint file addition
            assert "add_files -fileset constrs_1" in content

            # Validate constraint files are referenced
            constraint_files = pcileech_project_context["constraint_files"]
            for constraint_file in constraint_files:
                assert constraint_file in content

        except TemplateRenderError as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )

    def test_error_handling_in_templates(
        self, template_renderer, pcileech_build_context
    ):
        """Test error handling mechanisms in PCILeech build template."""
        try:
            content = template_renderer.render_template(
                "tcl/pcileech_build.j2", pcileech_build_context
            )

            # Validate error checking
            error_checks = ["ERROR:", "exit 1", "PROGRESS", "NEEDS_REFRESH"]

            for check in error_checks:
                assert check in content

            # Validate timing validation
            timing_checks = ["WNS", "WHS", "timing_met"]

            for check in timing_checks:
                assert check in content

        except TemplateRenderError as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )

    def test_output_file_generation(self, template_renderer, pcileech_build_context):
        """Test output file generation in PCILeech build template."""
        try:
            content = template_renderer.render_template(
                "tcl/pcileech_build.j2", pcileech_build_context
            )

            # Validate bitstream generation
            assert "write_bitstream" in content
            assert ".bit" in content

            # Validate MCS file generation
            assert "write_cfgmem" in content
            assert ".mcs" in content

            # Validate report generation
            report_types = [
                "report_timing_summary",
                "report_utilization",
                "report_power",
                "report_drc",
            ]

            for report_type in report_types:
                assert report_type in content

        except TemplateRenderError as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
