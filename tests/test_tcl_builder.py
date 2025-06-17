"""
Comprehensive tests for src/tcl_builder.py - TCL builder class.

This module tests the TCL builder class including:
- Each TCL generation method (project_setup, ip_config, sources, etc.)
- Context preparation and template integration
- Fallback to legacy methods when templates unavailable
- build_all_tcl_scripts() orchestration method
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.tcl_builder import TCLBuilder


@pytest.fixture
def temp_template_dir():
    """Create a temporary directory with test templates."""
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)

        # Create TCL subdirectory
        tcl_dir = template_dir / "tcl"
        tcl_dir.mkdir()

        # Create test templates
        templates = {
            "project_setup.j2": """
# Project Setup for {{ board }}
create_project {{ project_name | default('pcileech_firmware') }} ./vivado_project -part {{ fpga_part }} -force
set_property target_language Verilog [current_project]
""",
            "ip_config.j2": """
# IP Configuration for {{ pcie_ip_type }}
# Vendor: {{ vendor_id_hex }} Device: {{ device_id_hex }}
# Max lanes: {{ max_lanes }}
""",
            "sources.j2": """
# Source Files
{% for file in source_files %}
add_files {{ file }}
{% endfor %}
""",
            "constraints.j2": """
# Constraint Files
{% for file in constraint_files %}
add_files -fileset constrs_1 {{ file }}
{% endfor %}
""",
            "synthesis.j2": """
# Synthesis
launch_runs synth_1 -strategy "{{ synthesis_strategy }}"
""",
            "implementation.j2": """
# Implementation
launch_runs impl_1 -strategy "{{ implementation_strategy }}"
""",
            "bitstream.j2": """
# Bitstream Generation
launch_runs impl_1 -to_step write_bitstream
""",
            "master_build.j2": """
# Master Build Script for {{ board }}
{% for script in tcl_script_files %}
source {{ script }}
{% endfor %}
""",
        }

        for filename, content in templates.items():
            (tcl_dir / filename).write_text(content)

        yield template_dir


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def tcl_builder(temp_template_dir, temp_output_dir):
    """Create a TCLBuilder instance with test directories."""
    return TCLBuilder(template_dir=temp_template_dir, output_dir=temp_output_dir)


@pytest.fixture
def mock_constants():
    """Mock constants for testing."""
    with (
        patch("tcl_builder.BOARD_PARTS") as mock_board_parts,
        patch("tcl_builder.DEFAULT_FPGA_PART") as mock_default_part,
        patch("tcl_builder.TCL_SCRIPT_FILES") as mock_script_files,
        patch("tcl_builder.MASTER_BUILD_SCRIPT") as mock_master_script,
        patch("tcl_builder.SYNTHESIS_STRATEGY") as mock_synth_strategy,
        patch("tcl_builder.IMPLEMENTATION_STRATEGY") as mock_impl_strategy,
    ):

        mock_board_parts.return_value = {
            "pcileech_35t325_x4": "xc7a35tcsg324-2",
            "pcileech_75t484_x1": "xc7a75tfgg484-2",
            "pcileech_100t484_x1": "xczu3eg-sbva484-1-e",
        }
        mock_default_part.return_value = "xc7a35tcsg324-2"
        mock_script_files.return_value = [
            "01_project_setup.tcl",
            "02_ip_config.tcl",
            "03_add_sources.tcl",
            "04_constraints.tcl",
            "05_synthesis.tcl",
            "06_implementation.tcl",
            "07_bitstream.tcl",
        ]
        mock_master_script.return_value = "build_all.tcl"
        mock_synth_strategy.return_value = "Vivado Synthesis Defaults"
        mock_impl_strategy.return_value = "Performance_Explore"

        yield {
            "board_parts": mock_board_parts,
            "default_part": mock_default_part,
            "script_files": mock_script_files,
            "master_script": mock_master_script,
            "synth_strategy": mock_synth_strategy,
            "impl_strategy": mock_impl_strategy,
        }


class TestTCLBuilderInitialization:
    """Test TCLBuilder initialization and setup."""

    def test_init_with_custom_directories(self, temp_template_dir, temp_output_dir):
        """Test initialization with custom template and output directories."""
        builder = TCLBuilder(template_dir=temp_template_dir, output_dir=temp_output_dir)

        assert builder.template_renderer.template_dir == temp_template_dir
        assert builder.output_dir == temp_output_dir
        assert builder.generated_files == []
        assert builder.fpga_strategy_selector is not None

    def test_init_with_default_directories(self):
        """Test initialization with default directories."""
        with patch("tcl_builder.TemplateRenderer") as mock_renderer:
            builder = TCLBuilder()

            mock_renderer.assert_called_once_with(None)
            assert builder.output_dir == Path(".")

    def test_init_creates_output_directory(self):
        """Test that initialization creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"

            builder = TCLBuilder(output_dir=output_dir)

            assert output_dir.exists()
            assert builder.output_dir == output_dir


class TestContextPreparation:
    """Test context preparation for template rendering."""

    def test_prepare_base_context_with_known_board(self, tcl_builder):
        """Test context preparation with known board."""
        with patch("tcl_builder.BOARD_PARTS", {"test_board": "xc7a35tcsg324-2"}):
            context = tcl_builder.prepare_base_context(
                board="test_board", vendor_id=0x1234, device_id=0x5678, revision_id=0x01
            )

            assert context["board"] == "test_board"
            assert context["fpga_part"] == "xc7a35tcsg324-2"
            assert context["vendor_id"] == 0x1234
            assert context["device_id"] == 0x5678
            assert context["revision_id"] == 0x01
            assert context["vendor_id_hex"] == "1234"
            assert context["device_id_hex"] == "5678"
            assert context["revision_id_hex"] == "01"

    def test_prepare_base_context_with_explicit_fpga_part(self, tcl_builder):
        """Test context preparation with explicitly provided FPGA part."""
        context = tcl_builder.prepare_base_context(
            board="unknown_board", fpga_part="xc7a75tfgg484-2"
        )

        assert context["fpga_part"] == "xc7a75tfgg484-2"
        assert context["pcie_ip_type"] == "pcie_7x"  # Based on 75T part

    def test_prepare_base_context_with_default_values(self, tcl_builder):
        """Test context preparation with default values."""
        with patch("tcl_builder.DEFAULT_FPGA_PART", "xc7a35tcsg324-2"):
            context = tcl_builder.prepare_base_context(board="test_board")

            assert context["vendor_id"] == 0x1234  # Default
            assert context["device_id"] == 0x5678  # Default
            assert context["revision_id"] == 0x01  # Default

    def test_prepare_base_context_invalid_fpga_part(self, tcl_builder):
        """Test context preparation with invalid FPGA part falls back to default."""
        with (
            patch("tcl_builder.validate_fpga_part", return_value=False),
            patch("tcl_builder.DEFAULT_FPGA_PART", "xc7a35tcsg324-2"),
        ):

            context = tcl_builder.prepare_base_context(
                board="test_board", fpga_part="invalid_part"
            )

            assert context["fpga_part"] == "xc7a35tcsg324-2"  # Default fallback

    def test_prepare_base_context_fpga_strategy_integration(self, tcl_builder):
        """Test that context includes FPGA strategy configuration."""
        context = tcl_builder.prepare_base_context(
            board="test_board", fpga_part="xc7a35tcsg324-2"
        )

        # Should include strategy-based configuration
        assert "pcie_ip_type" in context
        assert "fpga_family" in context
        assert "max_lanes" in context
        assert "supports_msi" in context
        assert "supports_msix" in context


class TestTCLGenerationMethods:
    """Test individual TCL generation methods."""

    def test_build_project_setup_tcl_with_template(self, tcl_builder):
        """Test project setup TCL generation with template."""
        context = {"board": "test_board", "fpga_part": "xc7a35tcsg324-2"}

        result = tcl_builder.build_project_setup_tcl(context)

        assert "test_board" in result
        assert "xc7a35tcsg324-2" in result
        assert "create_project" in result

    def test_build_project_setup_tcl_fallback(self, tcl_builder):
        """Test project setup TCL generation with fallback when template missing."""
        # Mock template renderer to raise error
        tcl_builder.template_renderer.render_template = Mock(
            side_effect=Exception("Template not found")
        )

        context = {"board": "test_board", "fpga_part": "xc7a35tcsg324-2"}

        result = tcl_builder.build_project_setup_tcl(context)

        # Should use fallback method
        assert "test_board" in result
        assert "xc7a35tcsg324-2" in result
        assert "create_project" in result

    def test_build_ip_config_tcl_with_template(self, tcl_builder):
        """Test IP config TCL generation with template."""
        context = {
            "pcie_ip_type": "axi_pcie",
            "vendor_id_hex": "1234",
            "device_id_hex": "5678",
            "max_lanes": 4,
        }

        result = tcl_builder.build_ip_config_tcl(context)

        assert "axi_pcie" in result
        assert "1234" in result
        assert "5678" in result
        assert "4" in result

    def test_build_sources_tcl_with_files(self, tcl_builder):
        """Test sources TCL generation with source files."""
        context = {"board": "test_board"}
        source_files = ["src/file1.sv", "src/file2.sv"]

        result = tcl_builder.build_sources_tcl(context, source_files)

        assert "src/file1.sv" in result
        assert "src/file2.sv" in result
        assert "add_files" in result

    def test_build_sources_tcl_no_files(self, tcl_builder):
        """Test sources TCL generation with no source files."""
        context = {"board": "test_board"}

        result = tcl_builder.build_sources_tcl(context, [])

        # Should handle empty file list gracefully
        assert isinstance(result, str)

    def test_build_constraints_tcl_with_files(self, tcl_builder):
        """Test constraints TCL generation with constraint files."""
        context = {"board": "test_board"}
        constraint_files = ["constraints/timing.xdc", "constraints/pins.xdc"]

        result = tcl_builder.build_constraints_tcl(context, constraint_files)

        assert "constraints/timing.xdc" in result
        assert "constraints/pins.xdc" in result
        assert "add_files -fileset constrs_1" in result

    def test_build_synthesis_tcl(self, tcl_builder):
        """Test synthesis TCL generation."""
        context = {"synthesis_strategy": "Vivado Synthesis Defaults"}

        result = tcl_builder.build_synthesis_tcl(context)

        assert "Vivado Synthesis Defaults" in result
        assert "launch_runs synth_1" in result

    def test_build_implementation_tcl(self, tcl_builder):
        """Test implementation TCL generation."""
        context = {"implementation_strategy": "Performance_Explore"}

        result = tcl_builder.build_implementation_tcl(context)

        assert "Performance_Explore" in result
        assert "launch_runs impl_1" in result

    def test_build_bitstream_tcl(self, tcl_builder):
        """Test bitstream TCL generation."""
        context = {"board": "test_board"}

        result = tcl_builder.build_bitstream_tcl(context)

        assert "write_bitstream" in result
        assert "launch_runs" in result

    def test_build_master_tcl(self, tcl_builder):
        """Test master build TCL generation."""
        with patch("tcl_builder.TCL_SCRIPT_FILES", ["script1.tcl", "script2.tcl"]):
            context = {"board": "test_board"}

            result = tcl_builder.build_master_tcl(context)

            assert "test_board" in result
            assert "script1.tcl" in result
            assert "script2.tcl" in result
            assert "source" in result


class TestFallbackMethods:
    """Test fallback methods when templates are not available."""

    def test_fallback_project_setup(self, tcl_builder):
        """Test fallback project setup method."""
        context = {"board": "test_board", "fpga_part": "xc7a35tcsg324-2"}

        result = tcl_builder._fallback_project_setup(context)

        assert "test_board" in result
        assert "xc7a35tcsg324-2" in result
        assert "create_project" in result
        assert "set_property" in result

    def test_fallback_ip_config(self, tcl_builder):
        """Test fallback IP config method."""
        context = {
            "board": "test_board",
            "fpga_part": "xc7a35tcsg324-2",
            "vendor_id_hex": "1234",
            "device_id_hex": "5678",
        }

        result = tcl_builder._fallback_ip_config(context)

        assert "test_board" in result
        assert "1234" in result
        assert "5678" in result
        assert "PCIe IP" in result

    def test_fallback_sources(self, tcl_builder):
        """Test fallback sources method."""
        context = {"board": "test_board"}

        result = tcl_builder._fallback_sources(context)

        assert "test_board" in result
        assert "add_files" in result
        assert "*.sv" in result

    def test_fallback_constraints(self, tcl_builder):
        """Test fallback constraints method."""
        context = {"board": "test_board"}

        result = tcl_builder._fallback_constraints(context)

        assert "test_board" in result
        assert "add_files -fileset constrs_1" in result
        assert "*.xdc" in result

    def test_fallback_synthesis(self, tcl_builder):
        """Test fallback synthesis method."""
        context = {"board": "test_board"}

        result = tcl_builder._fallback_synthesis(context)

        assert "test_board" in result
        assert "launch_runs synth_1" in result
        assert "wait_on_run" in result

    def test_fallback_implementation(self, tcl_builder):
        """Test fallback implementation method."""
        context = {"board": "test_board"}

        result = tcl_builder._fallback_implementation(context)

        assert "test_board" in result
        assert "launch_runs impl_1" in result
        assert "wait_on_run" in result

    def test_fallback_bitstream(self, tcl_builder):
        """Test fallback bitstream method."""
        context = {"board": "test_board"}

        result = tcl_builder._fallback_bitstream(context)

        assert "test_board" in result
        assert "write_bitstream" in result
        assert "launch_runs" in result

    def test_fallback_master_build(self, tcl_builder):
        """Test fallback master build method."""
        with patch("tcl_builder.TCL_SCRIPT_FILES", ["script1.tcl", "script2.tcl"]):
            context = {
                "board": "test_board",
                "fpga_part": "xc7a35tcsg324-2",
                "vendor_id_hex": "1234",
                "device_id_hex": "5678",
            }

            result = tcl_builder._fallback_master_build(context)

            assert "test_board" in result
            assert "xc7a35tcsg324-2" in result
            assert "1234:5678" in result
            assert "source script1.tcl" in result
            assert "source script2.tcl" in result


class TestBuildAllTclScripts:
    """Test the orchestration method that builds all TCL scripts."""

    def test_build_all_tcl_scripts_success(self, tcl_builder):
        """Test successful generation of all TCL scripts."""
        with (
            patch("tcl_builder.TCL_SCRIPT_FILES", ["project.tcl", "ip.tcl"]),
            patch("tcl_builder.MASTER_BUILD_SCRIPT", "build_all.tcl"),
            patch("tcl_builder.batch_write_tcl_files") as mock_batch_write,
        ):

            mock_batch_write.return_value = {
                "project.tcl": True,
                "ip.tcl": True,
                "build_all.tcl": True,
            }

            results = tcl_builder.build_all_tcl_scripts(
                board="test_board",
                fpga_part="xc7a35tcsg324-2",
                vendor_id=0x1234,
                device_id=0x5678,
            )

            assert all(results.values())
            mock_batch_write.assert_called_once()

    def test_build_all_tcl_scripts_with_source_files(self, tcl_builder):
        """Test building all TCL scripts with source and constraint files."""
        source_files = ["src/file1.sv", "src/file2.sv"]
        constraint_files = ["constraints/timing.xdc"]

        with patch("tcl_builder.batch_write_tcl_files") as mock_batch_write:
            mock_batch_write.return_value = {"script.tcl": True}

            results = tcl_builder.build_all_tcl_scripts(
                board="test_board",
                source_files=source_files,
                constraint_files=constraint_files,
            )

            # Verify that batch_write_tcl_files was called with content
            mock_batch_write.assert_called_once()
            call_args = mock_batch_write.call_args[0]
            tcl_contents = call_args[0]

            # Check that source files are included in the content
            assert any("src/file1.sv" in content for content in tcl_contents.values())

    def test_build_all_tcl_scripts_auto_detect_fpga_part(self, tcl_builder):
        """Test building scripts with auto-detected FPGA part."""
        with (
            patch("tcl_builder.BOARD_PARTS", {"test_board": "xc7a75tfgg484-2"}),
            patch("tcl_builder.batch_write_tcl_files") as mock_batch_write,
        ):

            mock_batch_write.return_value = {"script.tcl": True}

            results = tcl_builder.build_all_tcl_scripts(board="test_board")

            # Should auto-detect FPGA part from board mapping
            mock_batch_write.assert_called_once()

    def test_build_all_tcl_scripts_partial_failure(self, tcl_builder):
        """Test handling of partial failures in script generation."""
        with patch("tcl_builder.batch_write_tcl_files") as mock_batch_write:
            mock_batch_write.return_value = {
                "project.tcl": True,
                "ip.tcl": False,  # Failure
                "build_all.tcl": True,
            }

            results = tcl_builder.build_all_tcl_scripts(board="test_board")

            assert results["project.tcl"] is True
            assert results["ip.tcl"] is False
            assert results["build_all.tcl"] is True


class TestUtilityMethods:
    """Test utility methods of TCLBuilder."""

    def test_get_generated_files(self, tcl_builder):
        """Test getting list of generated files."""
        # Simulate some generated files
        tcl_builder.generated_files = ["file1.tcl", "file2.tcl"]

        files = tcl_builder.get_generated_files()

        assert files == ["file1.tcl", "file2.tcl"]
        # Should return a copy, not the original list
        assert files is not tcl_builder.generated_files

    def test_clean_generated_files(self, tcl_builder, temp_output_dir):
        """Test cleaning up generated files."""
        # Create some test files
        test_files = [temp_output_dir / "test1.tcl", temp_output_dir / "test2.tcl"]

        for file_path in test_files:
            file_path.write_text("# Test content")
            tcl_builder.generated_files.append(str(file_path))

        # Verify files exist
        assert all(f.exists() for f in test_files)

        # Clean up
        tcl_builder.clean_generated_files()

        # Verify files are removed and list is cleared
        assert not any(f.exists() for f in test_files)
        assert tcl_builder.generated_files == []

    def test_clean_generated_files_missing_files(self, tcl_builder):
        """Test cleaning up when some files are already missing."""
        # Add non-existent files to the list
        tcl_builder.generated_files = [
            "/non/existent/file1.tcl",
            "/non/existent/file2.tcl",
        ]

        # Should handle missing files gracefully
        tcl_builder.clean_generated_files()

        assert tcl_builder.generated_files == []

    def test_clean_generated_files_permission_error(self, tcl_builder):
        """Test cleaning up when file removal fails."""
        tcl_builder.generated_files = ["/protected/file.tcl"]

        with patch(
            "pathlib.Path.unlink", side_effect=PermissionError("Permission denied")
        ):
            # Should handle errors gracefully and still clear the list
            tcl_builder.clean_generated_files()

            assert tcl_builder.generated_files == []


class TestConvenienceFunction:
    """Test the convenience function for quick TCL generation."""

    def test_generate_tcl_scripts_success(self, temp_output_dir):
        """Test successful TCL generation using convenience function."""
        with patch("tcl_builder.TCLBuilder") as mock_builder_class:
            mock_builder = Mock()
            mock_builder.build_all_tcl_scripts.return_value = {"script.tcl": True}
            mock_builder_class.return_value = mock_builder

            results = generate_tcl_scripts(
                board="test_board",
                output_dir=temp_output_dir,
                fpga_part="xc7a35tcsg324-2",
            )

            assert results == {"script.tcl": True}
            mock_builder_class.assert_called_once_with(output_dir=temp_output_dir)
            mock_builder.build_all_tcl_scripts.assert_called_once()

    def test_generate_tcl_scripts_with_all_parameters(self):
        """Test convenience function with all parameters."""
        with patch("tcl_builder.TCLBuilder") as mock_builder_class:
            mock_builder = Mock()
            mock_builder.build_all_tcl_scripts.return_value = {}
            mock_builder_class.return_value = mock_builder

            results = generate_tcl_scripts(
                board="test_board",
                output_dir="./output",
                fpga_part="xc7a75tfgg484-2",
                vendor_id=0x1234,
                device_id=0x5678,
                revision_id=0x01,
                source_files=["src/file1.sv"],
                constraint_files=["constraints/timing.xdc"],
            )

            # Verify all parameters were passed through
            mock_builder.build_all_tcl_scripts.assert_called_once_with(
                "test_board",
                "xc7a75tfgg484-2",
                0x1234,
                0x5678,
                0x01,
                ["src/file1.sv"],
                ["constraints/timing.xdc"],
            )


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_template_renderer_initialization_error(self):
        """Test handling of template renderer initialization errors."""
        with patch(
            "tcl_builder.TemplateRenderer", side_effect=Exception("Init failed")
        ):
            with pytest.raises(Exception):
                TCLBuilder()

    def test_fpga_strategy_selector_error(self, temp_template_dir, temp_output_dir):
        """Test handling of FPGA strategy selector errors."""
        with patch(
            "tcl_builder.create_fpga_strategy_selector",
            side_effect=Exception("Strategy error"),
        ):
            with pytest.raises(Exception):
                TCLBuilder(template_dir=temp_template_dir, output_dir=temp_output_dir)

    def test_template_rendering_error_fallback(self, tcl_builder):
        """Test that template rendering errors trigger fallback methods."""
        # Mock template renderer to always fail
        tcl_builder.template_renderer.render_template = Mock(
            side_effect=Exception("Template error")
        )

        context = {"board": "test_board", "fpga_part": "xc7a35tcsg324-2"}

        # All methods should fall back gracefully
        result = tcl_builder.build_project_setup_tcl(context)
        assert isinstance(result, str)
        assert "test_board" in result

    def test_batch_write_error_handling(self, tcl_builder):
        """Test error handling in batch write operations."""
        with patch("tcl_builder.batch_write_tcl_files") as mock_batch_write:
            mock_batch_write.side_effect = Exception("Write error")

            with pytest.raises(Exception):
                tcl_builder.build_all_tcl_scripts(board="test_board")


class TestIntegrationScenarios:
    """Test integration scenarios and real-world usage patterns."""

    def test_complete_build_workflow(self, tcl_builder, temp_output_dir):
        """Test complete build workflow from start to finish."""
        # Prepare context
        context = tcl_builder.prepare_base_context(
            board="pcileech_35t325_x4",
            fpga_part="xc7a35tcsg324-2",
            vendor_id=0x1234,
            device_id=0x5678,
        )

        # Generate individual scripts
        project_tcl = tcl_builder.build_project_setup_tcl(context)
        ip_tcl = tcl_builder.build_ip_config_tcl(context)
        sources_tcl = tcl_builder.build_sources_tcl(context, ["src/test.sv"])

        # Verify content
        assert "pcileech_35t325_x4" in project_tcl
        assert "xc7a35tcsg324-2" in project_tcl
        assert "axi_pcie" in ip_tcl  # Should use AXI PCIe for 35T
        assert "src/test.sv" in sources_tcl

    def test_different_fpga_families(self, tcl_builder):
        """Test TCL generation for different FPGA families."""
        test_cases = [
            ("xc7a35tcsg324-2", "axi_pcie"),  # Artix-7 35T
            ("xc7a75tfgg484-2", "pcie_7x"),  # Artix-7 75T
            ("xczu3eg-sbva484-1-e", "pcie_ultrascale"),  # Zynq UltraScale+
        ]

        for fpga_part, expected_ip in test_cases:
            context = tcl_builder.prepare_base_context(
                board="test_board", fpga_part=fpga_part
            )

            ip_tcl = tcl_builder.build_ip_config_tcl(context)
            assert expected_ip in ip_tcl or expected_ip in context["pcie_ip_type"]

    def test_template_vs_fallback_consistency(self, tcl_builder):
        """Test that template and fallback methods produce consistent results."""
        context = {
            "board": "test_board",
            "fpga_part": "xc7a35tcsg324-2",
            "vendor_id_hex": "1234",
            "device_id_hex": "5678",
        }

        # Get template result
        template_result = tcl_builder.build_project_setup_tcl(context)

        # Get fallback result
        fallback_result = tcl_builder._fallback_project_setup(context)

        # Both should contain essential elements
        for result in [template_result, fallback_result]:
            assert "test_board" in result
            assert "xc7a35tcsg324-2" in result
            assert "create_project" in result
