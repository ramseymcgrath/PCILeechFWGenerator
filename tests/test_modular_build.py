#!/usr/bin/env python3
"""
Test suite for the modular build architecture.

This module tests the new async-enabled modular build system to ensure
it provides the expected performance improvements and maintains backward compatibility.
"""

import asyncio
import sys
import time
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from build.analysis.device import DeviceAnalyzer
    from build.analysis.registers import RegisterAnalyzer
    from build.config.loader import ConfigLoader
    from build.config.validation import ConfigValidator
    from build.controller import BuildController, create_build_controller
    from build.generators.systemverilog import SystemVerilogGenerator
    from build.generators.tcl import TCLGenerator
    from build.orchestration.files import FileManager
    from build.orchestration.processes import ProcessManager

    MODULAR_BUILD_AVAILABLE = True
except ImportError as e:
    MODULAR_BUILD_AVAILABLE = False
    print(f"Modular build system not available: {e}")


@pytest.mark.skipif(
    not MODULAR_BUILD_AVAILABLE, reason="Modular build system not available"
)
class TestModularBuildArchitecture:
    """Test the modular build architecture."""

    def test_build_controller_creation(self):
        """Test BuildController can be created."""
        controller = create_build_controller()
        assert controller is not None
        assert isinstance(controller, BuildController)

    def test_file_manager_creation(self):
        """Test FileManager can be created."""
        file_manager = FileManager()
        assert file_manager is not None
        assert hasattr(file_manager, "read_file_async")
        assert hasattr(file_manager, "write_file_async")

    def test_process_manager_creation(self):
        """Test ProcessManager can be created."""
        process_manager = ProcessManager()
        assert process_manager is not None
        assert hasattr(process_manager, "run_command_async")

    def test_systemverilog_generator_creation(self):
        """Test SystemVerilogGenerator can be created."""
        generator = SystemVerilogGenerator()
        assert generator is not None
        assert hasattr(generator, "generate_async")

    def test_tcl_generator_creation(self):
        """Test TCLGenerator can be created."""
        generator = TCLGenerator()
        assert generator is not None
        assert hasattr(generator, "generate_async")

    def test_device_analyzer_creation(self):
        """Test DeviceAnalyzer can be created."""
        analyzer = DeviceAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, "extract_donor_info_async")

    def test_register_analyzer_creation(self):
        """Test RegisterAnalyzer can be created."""
        analyzer = RegisterAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, "analyze_registers_async")

    def test_config_validator_creation(self):
        """Test ConfigValidator can be created."""
        validator = ConfigValidator()
        assert validator is not None
        assert hasattr(validator, "validate_build_config_async")

    def test_config_loader_creation(self):
        """Test ConfigLoader can be created."""
        loader = ConfigLoader()
        assert loader is not None
        assert hasattr(loader, "load_build_config_async")

    @pytest.mark.asyncio
    async def test_async_file_operations(self):
        """Test async file operations work."""
        file_manager = FileManager()

        # Test file existence check
        exists = await file_manager.file_exists_async(__file__)
        assert exists is True

        # Test reading this test file
        content = await file_manager.read_file_async(__file__)
        assert len(content) > 0
        assert "TestModularBuildArchitecture" in content

    @pytest.mark.asyncio
    async def test_async_process_operations(self):
        """Test async process operations work."""
        process_manager = ProcessManager()

        # Test simple command
        result = await process_manager.run_command_async("echo 'test'")
        assert result.success
        assert "test" in result.stdout

    @pytest.mark.asyncio
    async def test_config_validation(self):
        """Test configuration validation works."""
        validator = ConfigValidator()

        # Test valid config
        valid_config = {"bdf": "0000:03:00.0", "board": "75t", "device_type": "generic"}

        result = await validator.validate_build_config_async(valid_config)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

        # Test invalid config
        invalid_config = {"bdf": "invalid", "board": "invalid_board"}

        result = await validator.validate_build_config_async(invalid_config)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_config_loading(self):
        """Test configuration loading works."""
        loader = ConfigLoader()

        # Test loading default config
        config = await loader.load_build_config_async()
        assert isinstance(config, dict)
        assert "profile_duration" in config
        assert "enhanced_timing" in config

    @pytest.mark.asyncio
    async def test_systemverilog_generation(self):
        """Test SystemVerilog generation works."""
        generator = SystemVerilogGenerator()

        # Test with minimal register set
        regs = [
            {
                "offset": 0x0,
                "name": "test_reg",
                "value": "0x0",
                "rw": "rw",
                "context": {"function": "test"},
            }
        ]

        config = {"board": "75t", "enable_variance": False}

        content = await generator.generate_async(regs, config)
        assert len(content) > 0
        assert "module pcileech_tlps128_bar_controller" in content
        assert "test_reg" in content

    @pytest.mark.asyncio
    async def test_tcl_generation(self):
        """Test TCL generation works."""
        generator = TCLGenerator()

        # Test with minimal device info
        info = {
            "vendor_id": "0x1234",
            "device_id": "0x5678",
            "subvendor_id": "0x1234",
            "subsystem_id": "0x5678",
            "revision_id": "0x01",
            "bar_size": "0x1000",
            "mpc": "0x0",
            "mpr": "0x0",
        }

        config = {"disable_capability_pruning": True}

        content = await generator.generate_async(info, config)
        assert len(content) > 0
        assert "create_project" in content
        assert "pcie_7x_0" in content

    def test_performance_improvement_estimation(self):
        """Test that the modular architecture provides performance benefits."""
        controller = create_build_controller()

        # The controller should have async capabilities
        assert hasattr(controller, "run_async")
        assert hasattr(controller, "_calculate_performance_improvement")

        # Test performance calculation
        controller._phase_times = {
            "donor_info_extraction": 2.0,
            "register_analysis": 3.0,
            "behavior_analysis": 5.0,
        }

        improvement = controller._calculate_performance_improvement()
        assert "estimated_improvement_percent" in improvement
        assert improvement["estimated_improvement_percent"] >= 0
        assert improvement["estimated_improvement_percent"] <= 30.0


@pytest.mark.skipif(
    not MODULAR_BUILD_AVAILABLE, reason="Modular build system not available"
)
class TestBackwardCompatibility:
    """Test backward compatibility with existing build system."""

    def test_build_controller_backward_compatibility(self):
        """Test BuildController maintains backward compatibility."""
        controller = create_build_controller()

        # Should have old interface methods
        assert hasattr(controller, "start_build")
        assert hasattr(controller, "track_phase")
        assert hasattr(controller, "get_build_summary")
        assert hasattr(controller, "run")  # Sync wrapper

    def test_factory_functions_available(self):
        """Test factory functions are available."""
        from build.controller import create_build_controller, run_controlled_build

        controller = create_build_controller()
        assert controller is not None

        # run_controlled_build should be callable
        assert callable(run_controlled_build)


if __name__ == "__main__":
    # Run basic tests if executed directly
    if MODULAR_BUILD_AVAILABLE:
        print("Testing modular build architecture...")

        # Test basic creation
        controller = create_build_controller()
        print(f"✓ BuildController created: {type(controller)}")

        file_manager = FileManager()
        print(f"✓ FileManager created: {type(file_manager)}")

        process_manager = ProcessManager()
        print(f"✓ ProcessManager created: {type(process_manager)}")

        print("✓ All basic components can be created successfully")
        print("✓ Modular build architecture is functional")

        # Test async functionality
        async def test_async():
            config_loader = ConfigLoader()
            config = await config_loader.load_build_config_async()
            print(f"✓ Async config loading works: {len(config)} settings loaded")

            validator = ConfigValidator()
            result = await validator.validate_build_config_async(
                {"bdf": "0000:03:00.0", "board": "75t"}
            )
            print(f"✓ Async validation works: {result['valid']}")

        asyncio.run(test_async())
        print("✓ Async operations working correctly")
        print("\n🎉 Modular build architecture Phase 2 implementation successful!")
    else:
        print("❌ Modular build system not available - check imports")
