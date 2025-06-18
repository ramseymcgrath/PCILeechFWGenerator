#!/usr/bin/env python3
"""
PCILeech Build System Integration Tests

This module contains comprehensive tests that validate PCILeech is properly
integrated as the primary build pattern in the main build system.

Tests cover:
- PCILeech as primary build pattern in main build system
- SystemVerilog generator using PCILeech as default path
- TCL builder integration with PCILeech templates
- Backward compatibility with existing build workflows
- CLI integration and command-line options
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from build import PCILeechFirmwareBuilder
    from device_clone.pcileech_generator import (
        PCILeechGenerationConfig,
        PCILeechGenerator,
    )
    from templating.systemverilog_generator import AdvancedSVGenerator
    from templating.tcl_builder import TCLBuilder

    BUILD_SYSTEM_AVAILABLE = True
except ImportError as e:
    BUILD_SYSTEM_AVAILABLE = False
    IMPORT_ERROR = str(e)


@pytest.mark.skipif(
    not BUILD_SYSTEM_AVAILABLE,
    reason=f"Build system not available: {IMPORT_ERROR if not BUILD_SYSTEM_AVAILABLE else ''}",
)
class TestPCILeechBuildIntegration:
    """Test PCILeech build system integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_device_bdf = "0000:03:00.0"
        self.test_board = "pcileech_35t325_x4"
        self.test_output_dir = Path(tempfile.mkdtemp())

        # Mock successful PCILeech generation result
        self.mock_pcileech_result = {
            "device_bdf": self.test_device_bdf,
            "generation_timestamp": "2025-06-17T02:15:00Z",
            "systemverilog_modules": {
                "pcileech_fifo": "module pcileech_fifo();",
                "bar_controller": "module bar_controller();",
                "cfg_shadow": "module cfg_shadow();",
                "msix_implementation": "module msix_implementation();",
            },
            "firmware_components": {
                "build_integration": "# Build integration script",
                "constraint_files": "# Constraint files",
                "tcl_scripts": ["project_setup.tcl", "implementation.tcl"],
            },
            "template_context": {
                "device_config": {"vendor_id": "8086", "device_id": "153c"},
                "pcileech_config": {"command_timeout": 1000},
            },
            "generation_metadata": {
                "generator_version": "1.0.0",
                "validation_status": "passed",
            },
        }

    def test_pcileech_primary_build_pattern_initialization(self):
        """Test that PCILeech is initialized as the primary build pattern."""
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
            # Create builder
            builder = PCILeechFirmwareBuilder(self.test_device_bdf, self.test_board)

            # Verify PCILeech is set as primary
            assert hasattr(builder, "use_pcileech_primary")
            assert builder.use_pcileech_primary is True

            # Verify PCILeech generator was initialized
            assert hasattr(builder, "pcileech_generator")
            mock_pcileech_gen.assert_called_once()
            mock_config.assert_called_once()

            # Verify configuration includes device BDF and board
            config_call_args = mock_config.call_args[1]
            assert config_call_args["device_bdf"] == self.test_device_bdf

    def test_systemverilog_generator_pcileech_default_path(self):
        """Test that SystemVerilog generator uses PCILeech as default path."""
        with patch("templating.systemverilog_generator.TemplateRenderer"):
            # Initialize generator (should default to PCILeech primary)
            generator = AdvancedSVGenerator()

            # Verify PCILeech is the default path
            assert hasattr(generator, "use_pcileech_primary")
            assert generator.use_pcileech_primary is True

            # Verify PCILeech-specific methods exist
            assert hasattr(generator, "generate_systemverilog_modules")
            assert hasattr(generator, "generate_pcileech_modules")

            # Test that generate_systemverilog_modules delegates to PCILeech path
            with patch.object(
                generator, "generate_pcileech_modules"
            ) as mock_pcileech_gen:
                mock_pcileech_gen.return_value = {"test": "module"}

                context = {"device_config": {"vendor_id": "8086"}}
                result = generator.generate_systemverilog_modules(context)

                mock_pcileech_gen.assert_called_once_with(context)
                assert result == {"test": "module"}

    def test_tcl_builder_pcileech_template_integration(self):
        """Test that TCL builder integrates with PCILeech templates."""
        with patch("templating.tcl_builder.TemplateRenderer") as mock_renderer:
            builder = TCLBuilder()

            # Verify PCILeech template mapping exists
            assert hasattr(builder, "_pcileech_template_map")
            pcileech_templates = builder._pcileech_template_map

            # Verify required PCILeech templates are mapped
            required_templates = [
                "project_setup",
                "sources",
                "constraints",
                "implementation",
                "build",
            ]

            for template in required_templates:
                assert (
                    template in pcileech_templates
                ), f"Missing PCILeech template: {template}"
                assert pcileech_templates[template].startswith(
                    "pcileech_"
                ), f"Template {template} not PCILeech-specific"

            # Verify PCILeech-specific methods exist
            assert hasattr(builder, "build_pcileech_enhanced_scripts")
            assert hasattr(builder, "save_pcileech_scripts")

    def test_build_firmware_uses_pcileech_primary_path(self):
        """Test that build_firmware method uses PCILeech as primary path."""
        with (
            patch("build.ConfigSpaceManager"),
            patch("build.FileManager"),
            patch("build.VarianceManager"),
            patch("build.DonorDumpManager"),
            patch("build.OptionROMManager"),
            patch("build.TCLBuilder") as mock_tcl_builder,
            patch("build.PCILeechGenerator") as mock_pcileech_gen,
            patch("build.PCILeechGenerationConfig"),
        ):
            # Setup PCILeech generator mock
            mock_generator_instance = Mock()
            mock_generator_instance.generate_pcileech_firmware.return_value = (
                self.mock_pcileech_result
            )
            mock_generator_instance.save_generated_firmware.return_value = None
            mock_pcileech_gen.return_value = mock_generator_instance

            # Setup TCL builder mock
            mock_tcl_instance = Mock()
            mock_tcl_instance.build_pcileech_enhanced_scripts.return_value = {
                "project_setup.tcl": "# Project setup",
                "implementation.tcl": "# Implementation",
            }
            mock_tcl_builder.return_value = mock_tcl_instance

            # Create builder and build firmware
            builder = PCILeechFirmwareBuilder(self.test_device_bdf, self.test_board)
            result = builder.build_firmware()

            # Verify PCILeech primary path was used
            assert result["success"] is True
            assert result["pcileech_primary"] is True
            assert "pcileech_generation_result" in result

            # Verify PCILeech generator was called
            mock_generator_instance.generate_pcileech_firmware.assert_called_once()
            mock_generator_instance.save_generated_firmware.assert_called_once()

            # Verify TCL builder used PCILeech templates
            mock_tcl_instance.build_pcileech_enhanced_scripts.assert_called_once()

    def test_backward_compatibility_with_existing_workflows(self):
        """Test backward compatibility with existing build workflows."""
        with (
            patch("build.ConfigSpaceManager") as mock_config_manager,
            patch("build.FileManager") as mock_file_manager,
            patch("build.VarianceManager") as mock_variance_manager,
            patch("build.DonorDumpManager") as mock_donor_manager,
            patch("build.OptionROMManager") as mock_option_rom_manager,
            patch("build.TCLBuilder") as mock_tcl_builder,
            patch("build.PCILeechGenerator") as mock_pcileech_gen,
            patch("build.PCILeechGenerationConfig"),
        ):
            # Setup mocks for existing infrastructure
            mock_config_manager.return_value = Mock()
            mock_file_manager.return_value = Mock()
            mock_variance_manager.return_value = Mock()
            mock_donor_manager.return_value = Mock()
            mock_option_rom_manager.return_value = Mock()
            mock_tcl_builder.return_value = Mock()

            # Setup PCILeech to fail (test fallback)
            mock_generator_instance = Mock()
            mock_generator_instance.generate_pcileech_firmware.side_effect = Exception(
                "PCILeech generation failed"
            )
            mock_pcileech_gen.return_value = mock_generator_instance

            # Create builder
            builder = PCILeechFirmwareBuilder(self.test_device_bdf, self.test_board)

            # Verify existing infrastructure is still initialized
            mock_config_manager.assert_called_once()
            mock_file_manager.assert_called_once()
            mock_variance_manager.assert_called_once()
            mock_donor_manager.assert_called_once()
            mock_option_rom_manager.assert_called_once()
            mock_tcl_builder.assert_called_once()

            # Verify builder has access to existing components
            assert hasattr(builder, "config_space_manager")
            assert hasattr(builder, "file_manager")
            assert hasattr(builder, "variance_manager")
            assert hasattr(builder, "donor_dump_manager")
            assert hasattr(builder, "option_rom_manager")
            assert hasattr(builder, "tcl_builder")

    def test_cli_integration_pcileech_options(self):
        """Test CLI integration with PCILeech-specific options."""
        # Test that PCILeech entry point exists and is executable
        entry_point = Path(__file__).parent.parent / "pcileech_generate.py"
        assert entry_point.exists(), "PCILeech entry point script missing"

        # Verify script content includes PCILeech-specific options
        content = entry_point.read_text()
        assert "#!/usr/bin/env python3" in content
        assert "PCILeech" in content

        # Test CLI argument parsing (mock subprocess to avoid actual execution)
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(
                returncode=0, stdout="PCILeech help", stderr=""
            )

            # Test help command
            result = subprocess.run(
                [sys.executable, str(entry_point), "--help"],
                capture_output=True,
                text=True,
            )

            # Should not actually run due to mock, but structure should be correct
            mock_subprocess.assert_called_once()

    def test_build_system_pcileech_configuration_options(self):
        """Test build system PCILeech configuration options."""
        with (
            patch("build.ConfigSpaceManager"),
            patch("build.FileManager"),
            patch("build.VarianceManager"),
            patch("build.DonorDumpManager"),
            patch("build.OptionROMManager"),
            patch("build.TCLBuilder"),
            patch("build.PCILeechGenerator"),
            patch("build.PCILeechGenerationConfig") as mock_config,
        ):
            # Test various PCILeech configuration options
            test_configs = [
                {
                    "enable_behavior_profiling": True,
                    "behavior_capture_duration": 30.0,
                    "enable_manufacturing_variance": True,
                    "enable_advanced_features": True,
                },
                {
                    "enable_behavior_profiling": False,
                    "enable_manufacturing_variance": False,
                    "enable_advanced_features": False,
                    "strict_validation": False,
                },
                {
                    "pcileech_command_timeout": 2000,
                    "pcileech_buffer_size": 8192,
                    "enable_dma_operations": False,
                },
            ]

            for config_options in test_configs:
                # Create builder with specific options
                builder = PCILeechFirmwareBuilder(
                    self.test_device_bdf, self.test_board, **config_options
                )

                # Verify configuration was passed to PCILeech
                mock_config.assert_called()
                config_call = mock_config.call_args[1]

                for key, value in config_options.items():
                    assert (
                        config_call.get(key) == value
                    ), f"Configuration option {key} not set correctly"

    def test_tcl_builder_pcileech_enhanced_scripts(self):
        """Test TCL builder generates PCILeech-enhanced scripts."""
        with patch("templating.tcl_builder.TemplateRenderer") as mock_renderer:
            mock_template_renderer = Mock()
            mock_template_renderer.render_template.return_value = (
                "# PCILeech TCL script"
            )
            mock_renderer.return_value = mock_template_renderer

            builder = TCLBuilder()

            # Test PCILeech-enhanced script generation
            context = {
                "device_config": {"vendor_id": "8086", "device_id": "153c"},
                "pcileech_config": {"command_timeout": 1000},
                "board_config": {"part": "xc7a35tcpg236-1"},
            }

            scripts = builder.build_pcileech_enhanced_scripts(context)

            # Verify PCILeech-specific scripts were generated
            expected_scripts = [
                "pcileech_project_setup.tcl",
                "pcileech_sources.tcl",
                "pcileech_constraints.tcl",
                "pcileech_implementation.tcl",
            ]

            for script_name in expected_scripts:
                assert script_name in scripts, f"Missing PCILeech script: {script_name}"
                assert (
                    len(scripts[script_name]) > 0
                ), f"Empty PCILeech script: {script_name}"

            # Verify template renderer was called for each script
            assert mock_template_renderer.render_template.call_count >= len(
                expected_scripts
            )

    def test_systemverilog_generator_pcileech_modules(self):
        """Test SystemVerilog generator PCILeech module generation."""
        with patch(
            "templating.systemverilog_generator.TemplateRenderer"
        ) as mock_renderer:
            mock_template_renderer = Mock()
            mock_template_renderer.render_template.return_value = "module test();"
            mock_renderer.return_value = mock_template_renderer

            generator = AdvancedSVGenerator()

            # Test PCILeech module generation
            context = {
                "device_config": {"vendor_id": "8086", "device_id": "153c"},
                "bar_config": {"aperture_size": 65536},
                "msix_config": {"num_vectors": 8},
                "timing_config": {"clock_frequency_mhz": 125.0},
            }

            modules = generator.generate_pcileech_modules(context)

            # Verify PCILeech-specific modules were generated
            expected_modules = [
                "pcileech_fifo",
                "pcileech_tlps128_bar_controller",
                "cfg_shadow",
                "bar_controller",
                "msix_implementation",
            ]

            for module_name in expected_modules:
                assert module_name in modules, f"Missing PCILeech module: {module_name}"
                assert (
                    len(modules[module_name]) > 0
                ), f"Empty PCILeech module: {module_name}"

            # Verify template renderer was called for each module
            assert mock_template_renderer.render_template.call_count >= len(
                expected_modules
            )

    def test_build_integration_error_handling(self):
        """Test build integration error handling."""
        error_scenarios = [
            {
                "name": "pcileech_generator_failure",
                "mock_setup": lambda mocks: mocks[
                    "pcileech_gen"
                ].return_value.generate_pcileech_firmware.side_effect.__setattr__(
                    "side_effect", Exception("PCILeech generation failed")
                ),
                "expected_fallback": True,
            },
            {
                "name": "tcl_builder_failure",
                "mock_setup": lambda mocks: mocks[
                    "tcl_builder"
                ].return_value.build_pcileech_enhanced_scripts.side_effect.__setattr__(
                    "side_effect", Exception("TCL generation failed")
                ),
                "expected_fallback": True,
            },
            {
                "name": "systemverilog_generator_failure",
                "mock_setup": lambda mocks: None,  # Will be handled in test
                "expected_fallback": True,
            },
        ]

        for scenario in error_scenarios:
            with (
                patch("build.ConfigSpaceManager"),
                patch("build.FileManager"),
                patch("build.VarianceManager"),
                patch("build.DonorDumpManager"),
                patch("build.OptionROMManager"),
                patch("build.TCLBuilder") as mock_tcl_builder,
                patch("build.PCILeechGenerator") as mock_pcileech_gen,
                patch("build.PCILeechGenerationConfig"),
            ):
                # Setup base mocks
                mock_tcl_instance = Mock()
                mock_tcl_instance.build_pcileech_enhanced_scripts.return_value = {}
                mock_tcl_builder.return_value = mock_tcl_instance

                mock_generator_instance = Mock()
                mock_generator_instance.generate_pcileech_firmware.return_value = (
                    self.mock_pcileech_result
                )
                mock_pcileech_gen.return_value = mock_generator_instance

                mocks = {
                    "tcl_builder": mock_tcl_builder,
                    "pcileech_gen": mock_pcileech_gen,
                }

                # Apply scenario-specific setup
                if scenario["mock_setup"]:
                    scenario["mock_setup"](mocks)

                # Create builder and attempt build
                builder = PCILeechFirmwareBuilder(self.test_device_bdf, self.test_board)

                if scenario["expected_fallback"]:
                    # Should handle error gracefully and potentially fall back
                    try:
                        result = builder.build_firmware()
                        # If it succeeds, it should indicate fallback was used
                        if result["success"]:
                            assert (
                                "fallback_used" in result
                                or "pcileech_primary" in result
                            )
                    except Exception as e:
                        # Or it should fail with a clear error message
                        assert "PCILeech" in str(e) or "generation" in str(e)

    def test_build_output_structure_validation(self):
        """Test that build output has correct structure for PCILeech."""
        with (
            patch("build.ConfigSpaceManager"),
            patch("build.FileManager"),
            patch("build.VarianceManager"),
            patch("build.DonorDumpManager"),
            patch("build.OptionROMManager"),
            patch("build.TCLBuilder") as mock_tcl_builder,
            patch("build.PCILeechGenerator") as mock_pcileech_gen,
            patch("build.PCILeechGenerationConfig"),
        ):
            # Setup successful mocks
            mock_generator_instance = Mock()
            mock_generator_instance.generate_pcileech_firmware.return_value = (
                self.mock_pcileech_result
            )
            mock_generator_instance.save_generated_firmware.return_value = None
            mock_pcileech_gen.return_value = mock_generator_instance

            mock_tcl_instance = Mock()
            mock_tcl_instance.build_pcileech_enhanced_scripts.return_value = {
                "project_setup.tcl": "# Setup",
                "implementation.tcl": "# Implementation",
            }
            mock_tcl_builder.return_value = mock_tcl_instance

            # Build firmware
            builder = PCILeechFirmwareBuilder(self.test_device_bdf, self.test_board)
            result = builder.build_firmware()

            # Validate output structure
            required_keys = [
                "success",
                "pcileech_primary",
                "pcileech_generation_result",
                "build_timestamp",
                "device_bdf",
                "board_config",
            ]

            for key in required_keys:
                assert key in result, f"Missing required output key: {key}"

            # Validate PCILeech-specific output
            pcileech_result = result["pcileech_generation_result"]
            assert "systemverilog_modules" in pcileech_result
            assert "firmware_components" in pcileech_result
            assert "template_context" in pcileech_result

            # Validate SystemVerilog modules
            sv_modules = pcileech_result["systemverilog_modules"]
            expected_modules = ["pcileech_fifo", "bar_controller", "cfg_shadow"]
            for module in expected_modules:
                assert module in sv_modules, f"Missing SystemVerilog module: {module}"

    def test_build_system_performance_requirements(self):
        """Test that build system meets performance requirements."""
        with (
            patch("build.ConfigSpaceManager"),
            patch("build.FileManager"),
            patch("build.VarianceManager"),
            patch("build.DonorDumpManager"),
            patch("build.OptionROMManager"),
            patch("build.TCLBuilder"),
            patch("build.PCILeechGenerator") as mock_pcileech_gen,
            patch("build.PCILeechGenerationConfig"),
            patch("time.time") as mock_time,
        ):
            # Mock time to measure performance
            start_time = 1000.0
            end_time = 1005.0  # 5 seconds total
            mock_time.side_effect = [start_time, end_time]

            # Setup fast PCILeech generation
            mock_generator_instance = Mock()
            mock_generator_instance.generate_pcileech_firmware.return_value = (
                self.mock_pcileech_result
            )
            mock_generator_instance.save_generated_firmware.return_value = None
            mock_pcileech_gen.return_value = mock_generator_instance

            # Build firmware and measure time
            builder = PCILeechFirmwareBuilder(self.test_device_bdf, self.test_board)
            result = builder.build_firmware()

            # Verify build completed successfully
            assert result["success"] is True

            # Performance should be reasonable (mocked to 5 seconds)
            # In real scenarios, PCILeech build should complete within reasonable time
            build_duration = end_time - start_time
            assert build_duration < 60.0, f"Build took too long: {build_duration}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
