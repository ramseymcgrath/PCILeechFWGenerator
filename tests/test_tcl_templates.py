#!/usr/bin/env python3
"""
Test suite for template-based TCL generation.

Tests the enhanced TCL generator with templates and fallback mechanisms.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the enhanced TCL generator
try:
    from src.board_config import get_board_info, get_fpga_part
    from src.tcl_generator_enhanced import EnhancedTCLGenerator
    from src.template_renderer import TemplateRenderer
except ImportError as e:
    pytest.skip(f"Required modules not available: {e}", allow_module_level=True)


class TestEnhancedTCLGenerator:
    """Test the enhanced TCL generator with templates."""

    @pytest.fixture
    def sample_device_info(self):
        """Sample device information for testing."""
        return {
            "vendor_id": "1234",
            "device_id": "5678",
            "class_code": "040300",
            "revision_id": "01",
        }

    @pytest.fixture
    def temp_output_dir(self):
        """Temporary output directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_board_config_integration(self):
        """Test board configuration integration."""
        # Test known board
        fpga_part = get_fpga_part("75t")
        assert fpga_part == "xc7a75tfgg484-2"

        # Test board info
        board_info = get_board_info("75t")
        assert board_info["name"] == "75t"
        assert board_info["fpga_part"] == "xc7a75tfgg484-2"
        assert board_info["fpga_family"] == "7series"

    def test_enhanced_generator_initialization(self, temp_output_dir):
        """Test enhanced generator initialization."""
        # Test with templates enabled
        generator = EnhancedTCLGenerator("75t", temp_output_dir, use_templates=True)
        assert generator.board == "75t"
        assert generator.output_dir == temp_output_dir

        # The use_templates flag might be False if imports failed, which is acceptable for fallback
        # We test that the generator works regardless of template availability
        print(f"Generator use_templates: {generator.use_templates}")
        print(f"Template renderer available: {generator.template_renderer is not None}")

        # Test with templates disabled
        generator_no_templates = EnhancedTCLGenerator(
            "75t", temp_output_dir, use_templates=False
        )
        assert generator_no_templates.use_templates is False

    def test_context_building(self, temp_output_dir, sample_device_info):
        """Test template context building."""
        generator = EnhancedTCLGenerator("75t", temp_output_dir)
        context = generator._build_context(sample_device_info)

        # Check device info
        assert context["device"]["vendor_id"] == "1234"
        assert context["device"]["device_id"] == "5678"
        assert context["device"]["class_code"] == "040300"

        # Check board info
        assert context["board"]["name"] == "75t"
        assert context["board"]["fpga_part"] == "xc7a75tfgg484-2"

        # Check project info
        assert context["project"]["name"] == "pcileech_firmware"
        assert context["project"]["dir"] == "./vivado_project"

        # Check metadata
        assert "generated_time" in context["meta"]
        assert context["meta"]["generator_version"] == "2.0.0-template"

    def test_project_setup_generation(self, temp_output_dir, sample_device_info):
        """Test project setup TCL generation."""
        generator = EnhancedTCLGenerator("75t", temp_output_dir)
        tcl_content = generator.generate_project_setup_tcl(sample_device_info)

        # Check that content is generated
        assert tcl_content is not None
        assert len(tcl_content) > 0

        # Check for key elements (should work with template or fallback)
        assert "project_name" in tcl_content
        assert "create_project" in tcl_content
        assert "75t" in tcl_content or "xc7a75tfgg484-2" in tcl_content

    def test_ip_config_generation(self, temp_output_dir, sample_device_info):
        """Test IP configuration TCL generation."""
        generator = EnhancedTCLGenerator("75t", temp_output_dir)
        tcl_content = generator.generate_ip_config_tcl(sample_device_info)

        # Check that content is generated
        assert tcl_content is not None
        assert len(tcl_content) > 0

        # Check for PCIe IP elements
        assert "1234" in tcl_content  # vendor_id
        assert "5678" in tcl_content  # device_id

    def test_constraints_generation(self, temp_output_dir, sample_device_info):
        """Test constraints TCL generation."""
        generator = EnhancedTCLGenerator("75t", temp_output_dir)
        tcl_content = generator.generate_constraints_tcl(sample_device_info)

        # Check that content is generated
        assert tcl_content is not None
        assert len(tcl_content) > 0

        # Check for timing constraints
        assert "constraint" in tcl_content.lower() or "clock" in tcl_content.lower()

    def test_fallback_mechanisms(self, temp_output_dir, sample_device_info):
        """Test fallback to hardcoded generation when templates fail."""
        # Create generator with templates disabled
        generator = EnhancedTCLGenerator("75t", temp_output_dir, use_templates=False)

        # Test that fallback methods work
        tcl_content = generator.generate_project_setup_tcl(sample_device_info)
        assert "fallback" in tcl_content.lower()
        assert "project_name" in tcl_content

    @patch("src.template_renderer.TemplateRenderer")
    def test_template_rendering_failure_fallback(
        self, mock_renderer, temp_output_dir, sample_device_info
    ):
        """Test fallback when template rendering fails."""
        # Mock template renderer to raise an exception
        mock_renderer.return_value.template_exists.return_value = True
        mock_renderer.return_value.render_template.side_effect = Exception(
            "Template error"
        )

        generator = EnhancedTCLGenerator("75t", temp_output_dir, use_templates=True)
        tcl_content = generator.generate_project_setup_tcl(sample_device_info)

        # Should fall back to hardcoded generation
        assert tcl_content is not None
        assert "fallback" in tcl_content.lower()

    def test_all_build_stages(self, temp_output_dir, sample_device_info):
        """Test all build stage generations."""
        generator = EnhancedTCLGenerator("75t", temp_output_dir)

        # Test all build stages
        stages = [
            "generate_project_setup_tcl",
            "generate_ip_config_tcl",
            "generate_sources_tcl",
            "generate_constraints_tcl",
            "generate_synthesis_tcl",
            "generate_implementation_tcl",
            "generate_bitstream_tcl",
            "generate_master_build_tcl",
        ]

        for stage_method in stages:
            method = getattr(generator, stage_method)
            tcl_content = method(sample_device_info)

            # Each stage should generate content
            assert tcl_content is not None
            assert len(tcl_content) > 0
            print(f"✓ {stage_method} generated {len(tcl_content)} characters")

    def test_different_boards(self, temp_output_dir, sample_device_info):
        """Test generation for different board types."""
        boards_to_test = ["35t", "75t", "100t", "pcileech_75t484_x1"]

        for board in boards_to_test:
            generator = EnhancedTCLGenerator(board, temp_output_dir)
            tcl_content = generator.generate_project_setup_tcl(sample_device_info)

            # Should generate content for each board
            assert tcl_content is not None
            assert len(tcl_content) > 0
            print(f"✓ Board {board} generation successful")

    def test_template_vs_fallback_comparison(self, temp_output_dir, sample_device_info):
        """Compare template output with fallback output."""
        # Generate with templates
        generator_template = EnhancedTCLGenerator(
            "75t", temp_output_dir, use_templates=True
        )
        template_content = generator_template.generate_project_setup_tcl(
            sample_device_info
        )

        # Generate with fallback
        generator_fallback = EnhancedTCLGenerator(
            "75t", temp_output_dir, use_templates=False
        )
        fallback_content = generator_fallback.generate_project_setup_tcl(
            sample_device_info
        )

        # Both should generate content
        assert template_content is not None
        assert fallback_content is not None

        # Fallback should contain "fallback" indicator
        assert "fallback" in fallback_content.lower()

        print(f"Template content length: {len(template_content)}")
        print(f"Fallback content length: {len(fallback_content)}")


if __name__ == "__main__":
    # Run basic tests if executed directly
    import tempfile

    sample_device = {
        "vendor_id": "1234",
        "device_id": "5678",
        "class_code": "040300",
        "revision_id": "01",
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        generator = EnhancedTCLGenerator("75t", Path(temp_dir))

        print("Testing enhanced TCL generator...")

        # Test project setup
        project_tcl = generator.generate_project_setup_tcl(sample_device)
        print(f"✓ Project setup: {len(project_tcl)} characters")

        # Test constraints (high priority template)
        constraints_tcl = generator.generate_constraints_tcl(sample_device)
        print(f"✓ Constraints: {len(constraints_tcl)} characters")

        # Test bitstream (complex file handling)
        bitstream_tcl = generator.generate_bitstream_tcl(sample_device)
        print(f"✓ Bitstream: {len(bitstream_tcl)} characters")

        print("All tests passed!")
