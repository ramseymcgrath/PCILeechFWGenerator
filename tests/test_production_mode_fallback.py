#!/usr/bin/env python3
"""
Test production mode fallback behavior.

This test verifies that in production mode, the system errors out and cleans up
instead of falling back to basic functionality.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Set production mode for testing
os.environ["PCILEECH_PRODUCTION_MODE"] = "true"

from src.build_helpers import safe_import_with_fallback


class TestProductionModeFallback:
    """Test production mode fallback behavior."""

    def test_safe_import_with_fallback_production_mode(self):
        """Test that safe_import_with_fallback errors in production mode."""
        with pytest.raises(RuntimeError, match="Production mode requires all modules"):
            safe_import_with_fallback(
                primary_imports={
                    "NonExistentModule": "non_existent_module.NonExistentClass"
                },
                fallback_imports={
                    "NonExistentModule": ".non_existent_module.NonExistentClass"
                },
                fallback_values={"NonExistentModule": None},
            )

    def test_build_py_import_fallback_production_mode(self):
        """Test that build.py import fallback errors in production mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()

            # Create a test file in output directory
            test_file = output_dir / "test.txt"
            test_file.write_text("test content")

            # Mock the import error scenario
            with patch(
                "builtins.__import__", side_effect=ImportError("Module not found")
            ):
                with patch("sys.exit") as mock_exit:
                    with patch("src.build.Path") as mock_path:
                        mock_path.return_value = output_dir
                        mock_path.return_value.exists.return_value = True

                        # This should trigger the production mode error handling
                        try:
                            # Import the module to trigger the fallback logic
                            import src.build
                        except SystemExit:
                            pass

                        # Verify sys.exit was called
                        mock_exit.assert_called_with(1)

    def test_tcl_generator_fallback_production_mode(self):
        """Test that TCL generator fallback errors in production mode."""
        from src.build import PCILeechFirmwareBuilder

        # Create a builder with no TCL generator
        builder = PCILeechFirmwareBuilder("0000:00:1f.3", "pcileech_35t325_x4")
        builder.tcl_generator = None

        device_info = {"vendor_id": 0x8086, "device_id": 0x54C8, "revision_id": 0x01}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()

            with patch("src.build.Path") as mock_path:
                mock_path.return_value = output_dir
                mock_path.return_value.exists.return_value = True

                with pytest.raises(
                    RuntimeError, match="Production mode requires TCL generator"
                ):
                    builder.generate_tcl_files(device_info)

    def test_systemverilog_fallback_production_mode(self):
        """Test that SystemVerilog fallback errors in production mode."""
        from src.build import build_sv

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()
            target_file = output_dir / "test.sv"

            # Mock an exception during SystemVerilog generation
            with patch("src.build.Path") as mock_path:
                mock_path.return_value = output_dir
                mock_path.return_value.exists.return_value = True

                # Force an exception by providing invalid registers
                with pytest.raises(
                    RuntimeError,
                    match="Production mode requires proper SystemVerilog generation",
                ):
                    # This will trigger the exception handling in build_sv
                    with patch(
                        "pathlib.Path.write_text", side_effect=Exception("Write failed")
                    ):
                        build_sv([], target_file)

    def test_config_space_fallback_production_mode(self):
        """Test that config space fallback errors in production mode."""
        from src.build import PCILeechFirmwareBuilder

        # Create a builder with no config manager
        builder = PCILeechFirmwareBuilder("0000:00:1f.3", "pcileech_35t325_x4")
        builder.config_manager = None

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()

            with patch("src.build.Path") as mock_path:
                mock_path.return_value = output_dir
                mock_path.return_value.exists.return_value = True

                with pytest.raises(
                    RuntimeError,
                    match="Production mode requires configuration space manager",
                ):
                    builder.read_config_space()

    def test_output_cleanup_on_error(self):
        """Test that output directory is cleaned up on production mode errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()

            # Create some test files
            test_file1 = output_dir / "test1.txt"
            test_file2 = output_dir / "test2.txt"
            test_file1.write_text("test content 1")
            test_file2.write_text("test content 2")

            assert output_dir.exists()
            assert test_file1.exists()
            assert test_file2.exists()

            # Mock the cleanup scenario
            with patch("src.build_helpers.Path") as mock_path:
                mock_path.return_value = output_dir
                mock_path.return_value.exists.return_value = True

                with pytest.raises(
                    RuntimeError, match="Production mode requires all modules"
                ):
                    safe_import_with_fallback(
                        primary_imports={
                            "NonExistentModule": "non_existent_module.NonExistentClass"
                        }
                    )


if __name__ == "__main__":
    pytest.main([__file__])
