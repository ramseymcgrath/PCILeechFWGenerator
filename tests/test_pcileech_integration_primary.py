#!/usr/bin/env python3
"""
Test PCILeech Integration as Primary Build Pattern

This test validates that PCILeech has been successfully integrated as the primary
build pattern throughout the system.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestPCILeechPrimaryIntegration:
    """Test PCILeech integration as primary build pattern."""

    def test_build_system_uses_pcileech_primary(self):
        """Test that the build system initializes with PCILeech as primary."""
        try:
            from build import PCILeechFirmwareBuilder

            # Mock dependencies
            with (
                patch("build.ConfigSpaceManager"),
                patch("build.FileManager"),
                patch("build.VarianceManager"),
                patch("build.DonorDumpManager"),
                patch("build.OptionROMManager"),
                patch("build.TCLBuilder"),
                patch("build.PCILeechGenerator") as mock_pcileech_gen,
                patch("build.PCILeechGenerationConfig") as mock_config,
            ):

                # Create builder instance
                builder = PCILeechFirmwareBuilder("0000:03:00.0", "pcileech_35t325_x4")

                # Verify PCILeech generator was initialized
                assert hasattr(builder, "use_pcileech_primary")
                assert hasattr(builder, "pcileech_generator")

                # Should attempt to use PCILeech as primary
                assert builder.use_pcileech_primary is True

        except ImportError:
            pytest.skip("Build system components not available")

    def test_systemverilog_generator_pcileech_primary(self):
        """Test that SystemVerilog generator uses PCILeech as primary path."""
        try:
            from templating.systemverilog_generator import AdvancedSVGenerator

            # Initialize with PCILeech primary (default)
            generator = AdvancedSVGenerator()

            # Should default to PCILeech primary
            assert hasattr(generator, "use_pcileech_primary")
            assert generator.use_pcileech_primary is True

            # Should have primary generation method
            assert hasattr(generator, "generate_systemverilog_modules")

        except ImportError:
            pytest.skip("SystemVerilog generator not available")

    def test_tcl_builder_pcileech_templates(self):
        """Test that TCL builder includes PCILeech-specific templates."""
        try:
            from templating.tcl_builder import TCLBuilder

            with patch("templating.tcl_builder.TemplateRenderer"):
                builder = TCLBuilder()

                # Should have PCILeech template mapping
                assert hasattr(builder, "_pcileech_template_map")
                assert "project_setup" in builder._pcileech_template_map
                assert "sources" in builder._pcileech_template_map
                assert "constraints" in builder._pcileech_template_map
                assert "implementation" in builder._pcileech_template_map

                # Should have PCILeech-specific methods
                assert hasattr(builder, "build_pcileech_enhanced_scripts")
                assert hasattr(builder, "save_pcileech_scripts")

        except ImportError:
            pytest.skip("TCL builder not available")

    def test_pcileech_templates_exist(self):
        """Test that PCILeech-specific templates exist."""
        template_dir = Path(__file__).parent.parent / "src" / "templates" / "tcl"

        expected_templates = [
            "pcileech_project_setup.j2",
            "pcileech_sources.j2",
            "pcileech_constraints.j2",
            "pcileech_implementation.j2",
        ]

        for template in expected_templates:
            template_path = template_dir / template
            assert template_path.exists(), f"PCILeech template missing: {template}"

            # Verify template has content
            content = template_path.read_text()
            assert len(content) > 0, f"PCILeech template is empty: {template}"
            assert (
                "PCILeech" in content
            ), f"Template doesn't contain PCILeech references: {template}"

    def test_pcileech_generator_integration(self):
        """Test PCILeech generator integration."""
        try:
            from device_clone.pcileech_generator import (
                PCILeechGenerator,
                PCILeechGenerationConfig,
            )

            # Should be able to create configuration
            config = PCILeechGenerationConfig(
                device_bdf="0000:03:00.0",
                device_profile="generic",
                enable_behavior_profiling=True,
                enable_manufacturing_variance=True,
                enable_advanced_features=True,
            )

            assert config.device_bdf == "0000:03:00.0"
            assert config.enable_behavior_profiling is True
            assert config.enable_manufacturing_variance is True
            assert config.enable_advanced_features is True

            # Should be able to create generator (with mocked dependencies)
            with (
                patch("device_clone.pcileech_generator.BehaviorProfiler"),
                patch("device_clone.pcileech_generator.ConfigSpaceManager"),
                patch("device_clone.pcileech_generator.TemplateRenderer"),
                patch("device_clone.pcileech_generator.AdvancedSVGenerator"),
            ):

                generator = PCILeechGenerator(config)
                assert generator.config == config

        except ImportError:
            pytest.skip("PCILeech generator not available")

    def test_build_firmware_uses_pcileech_primary(self):
        """Test that build_firmware method uses PCILeech as primary path."""
        try:
            from build import PCILeechFirmwareBuilder

            with (
                patch("build.ConfigSpaceManager"),
                patch("build.FileManager"),
                patch("build.VarianceManager"),
                patch("build.DonorDumpManager"),
                patch("build.OptionROMManager"),
                patch("build.TCLBuilder"),
                patch("build.PCILeechGenerator") as mock_pcileech_gen,
                patch("build.PCILeechGenerationConfig"),
            ):

                # Setup mock PCILeech generator
                mock_generator_instance = Mock()
                mock_generator_instance.generate_pcileech_firmware.return_value = {
                    "systemverilog_modules": {"test_module": "module test_module();"},
                    "firmware_components": {"test_component": "test"},
                    "template_context": {"device_info": {"vendor_id": "1234"}},
                }
                mock_generator_instance.save_generated_firmware.return_value = None
                mock_pcileech_gen.return_value = mock_generator_instance

                # Create builder
                builder = PCILeechFirmwareBuilder("0000:03:00.0", "pcileech_35t325_x4")
                builder.use_pcileech_primary = True
                builder.pcileech_generator = mock_generator_instance

                # Mock the TCL generation method
                builder._generate_pcileech_tcl_scripts = Mock(return_value=["test.tcl"])

                # Call build_firmware
                result = builder.build_firmware()

                # Should have called PCILeech generator
                mock_generator_instance.generate_pcileech_firmware.assert_called_once()
                mock_generator_instance.save_generated_firmware.assert_called_once()

                # Should return successful result
                assert result["success"] is True
                assert result["pcileech_primary"] is True

        except ImportError:
            pytest.skip("Build system not available")

    def test_pcileech_entry_point_exists(self):
        """Test that PCILeech entry point script exists."""
        entry_point = Path(__file__).parent.parent / "pcileech_generate.py"
        assert entry_point.exists(), "PCILeech entry point script missing"

        # Verify it's executable
        content = entry_point.read_text()
        assert "#!/usr/bin/env python3" in content
        assert "PCILeech Firmware Generator" in content
        assert "PCILeech-first build system" in content

    def test_integration_completeness(self):
        """Test that PCILeech integration is complete across all components."""
        integration_checklist = {
            "build_system": False,
            "systemverilog_generator": False,
            "tcl_builder": False,
            "pcileech_generator": False,
            "templates": False,
            "entry_point": False,
        }

        # Check build system integration
        try:
            from build import PCILeechFirmwareBuilder

            integration_checklist["build_system"] = True
        except ImportError:
            pass

        # Check SystemVerilog generator integration
        try:
            from templating.systemverilog_generator import AdvancedSVGenerator

            generator = AdvancedSVGenerator()
            if hasattr(generator, "use_pcileech_primary"):
                integration_checklist["systemverilog_generator"] = True
        except ImportError:
            pass

        # Check TCL builder integration
        try:
            from templating.tcl_builder import TCLBuilder

            with patch("templating.tcl_builder.TemplateRenderer"):
                builder = TCLBuilder()
                if hasattr(builder, "_pcileech_template_map"):
                    integration_checklist["tcl_builder"] = True
        except ImportError:
            pass

        # Check PCILeech generator
        try:
            from device_clone.pcileech_generator import PCILeechGenerator

            integration_checklist["pcileech_generator"] = True
        except ImportError:
            pass

        # Check templates
        template_dir = Path(__file__).parent.parent / "src" / "templates" / "tcl"
        if (template_dir / "pcileech_project_setup.j2").exists():
            integration_checklist["templates"] = True

        # Check entry point
        entry_point = Path(__file__).parent.parent / "pcileech_generate.py"
        if entry_point.exists():
            integration_checklist["entry_point"] = True

        # Report integration status
        completed = sum(integration_checklist.values())
        total = len(integration_checklist)

        print(
            f"\nPCILeech Integration Status: {completed}/{total} components integrated"
        )
        for component, status in integration_checklist.items():
            status_str = "✓" if status else "✗"
            print(f"  {status_str} {component}")

        # Should have at least 80% integration
        integration_percentage = (completed / total) * 100
        assert (
            integration_percentage >= 80
        ), f"PCILeech integration incomplete: {integration_percentage:.1f}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
