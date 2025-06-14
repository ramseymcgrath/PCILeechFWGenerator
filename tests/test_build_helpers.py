"""
Comprehensive tests for src/build_helpers.py - Helper functions for build system.

This module tests the helper functions including:
- safe_import_with_fallback() with both successful and failed imports
- select_pcie_ip_core() with different FPGA parts
- write_tcl_file_with_logging() functionality
- FPGA strategy selector functionality
"""

import logging
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from build_helpers import (
    batch_write_tcl_files,
    create_fpga_strategy_selector,
    safe_import_with_fallback,
    select_pcie_ip_core,
    validate_fpga_part,
    write_tcl_file_with_logging,
)


class TestSafeImportWithFallback:
    """Test the safe import with fallback functionality."""

    def test_successful_primary_import(self):
        """Test successful primary import without fallback."""
        with patch("builtins.__import__") as mock_import:
            # Mock successful import
            mock_module = Mock()
            mock_module.TestClass = "primary_class"
            mock_import.return_value = mock_module

            primary_imports = {"TestClass": "test_module.TestClass"}
            result = safe_import_with_fallback(primary_imports)

            assert result["TestClass"] == "primary_class"
            mock_import.assert_called_once()

    def test_fallback_import_success(self):
        """Test successful fallback import when primary fails."""
        with patch("builtins.__import__") as mock_import:
            # First call (primary) fails, second call (fallback) succeeds
            mock_fallback_module = Mock()
            mock_fallback_module.TestClass = "fallback_class"

            def import_side_effect(module_name, fromlist=None):
                if module_name == "test_module":
                    raise ImportError("Primary import failed")
                elif module_name == ".test_module":
                    return mock_fallback_module
                else:
                    raise ImportError("Unknown module")

            mock_import.side_effect = import_side_effect

            primary_imports = {"TestClass": "test_module.TestClass"}
            fallback_imports = {"TestClass": ".test_module.TestClass"}

            result = safe_import_with_fallback(primary_imports, fallback_imports)

            assert result["TestClass"] == "fallback_class"

    def test_both_imports_fail_with_fallback_value(self):
        """Test when both imports fail but fallback value is provided."""
        with patch("builtins.__import__") as mock_import:
            mock_import.side_effect = ImportError("All imports fail")

            primary_imports = {"TestClass": "test_module.TestClass"}
            fallback_imports = {"TestClass": ".test_module.TestClass"}
            fallback_values = {"TestClass": "default_value"}

            result = safe_import_with_fallback(
                primary_imports, fallback_imports, fallback_values
            )

            assert result["TestClass"] == "default_value"

    def test_both_imports_fail_no_fallback_value(self):
        """Test when both imports fail and no fallback value is provided."""
        with patch("builtins.__import__") as mock_import:
            mock_import.side_effect = ImportError("All imports fail")

            primary_imports = {"TestClass": "test_module.TestClass"}
            fallback_imports = {"TestClass": ".test_module.TestClass"}

            result = safe_import_with_fallback(primary_imports, fallback_imports)

            assert result["TestClass"] is None

    def test_simple_module_import(self):
        """Test importing a simple module (not a class from module)."""
        with patch("builtins.__import__") as mock_import:
            mock_module = Mock()
            mock_import.return_value = mock_module

            primary_imports = {"os": "os"}
            result = safe_import_with_fallback(primary_imports)

            assert result["os"] == mock_module

    def test_multiple_imports(self):
        """Test importing multiple modules/classes."""
        with patch("builtins.__import__") as mock_import:
            mock_module1 = Mock()
            mock_module1.Class1 = "class1"
            mock_module2 = Mock()
            mock_module2.Class2 = "class2"

            def import_side_effect(module_name, fromlist=None):
                if module_name == "module1":
                    return mock_module1
                elif module_name == "module2":
                    return mock_module2
                else:
                    raise ImportError("Unknown module")

            mock_import.side_effect = import_side_effect

            primary_imports = {"Class1": "module1.Class1", "Class2": "module2.Class2"}

            result = safe_import_with_fallback(primary_imports)

            assert result["Class1"] == "class1"
            assert result["Class2"] == "class2"

    def test_empty_imports(self):
        """Test with empty import dictionaries."""
        result = safe_import_with_fallback({})
        assert result == {}

    def test_none_fallback_parameters(self):
        """Test with None fallback parameters."""
        with patch("builtins.__import__") as mock_import:
            mock_import.side_effect = ImportError("Import failed")

            primary_imports = {"TestClass": "test_module.TestClass"}
            result = safe_import_with_fallback(primary_imports, None, None)

            assert result["TestClass"] is None


class TestSelectPcieIpCore:
    """Test PCIe IP core selection based on FPGA part."""

    def test_artix7_35t_selection(self):
        """Test PCIe IP core selection for Artix-7 35T parts."""
        test_parts = [
            "xc7a35tcsg324-2",
            "XC7A35TCSG324-2",  # Test case insensitivity
            "xc7a35tfgg484-1",
        ]

        for part in test_parts:
            result = select_pcie_ip_core(part)
            assert result == "axi_pcie"

    def test_artix7_75t_selection(self):
        """Test PCIe IP core selection for Artix-7 75T parts."""
        test_parts = ["xc7a75tfgg484-2", "XC7A75TFGG484-2", "xc7a75tcsg324-1"]

        for part in test_parts:
            result = select_pcie_ip_core(part)
            assert result == "pcie_7x"

    def test_kintex7_selection(self):
        """Test PCIe IP core selection for Kintex-7 parts."""
        test_parts = ["xc7k325tffg900-2", "XC7K325TFFG900-2", "xc7k160tfbg484-1"]

        for part in test_parts:
            result = select_pcie_ip_core(part)
            assert result == "pcie_7x"

    def test_zynq_ultrascale_selection(self):
        """Test PCIe IP core selection for Zynq UltraScale+ parts."""
        test_parts = [
            "xczu3eg-sbva484-1-e",
            "XCZU3EG-SBVA484-1-E",
            "xczu7ev-ffvc1156-2-e",
        ]

        for part in test_parts:
            result = select_pcie_ip_core(part)
            assert result == "pcie_ultrascale"

    def test_unknown_part_default(self):
        """Test PCIe IP core selection for unknown FPGA parts."""
        test_parts = [
            "unknown_part",
            "xc6vlx240t",  # Virtex-6 (older generation)
            "xcvu9p-flga2104-2-i",  # UltraScale+ (not Zynq)
        ]

        with patch("build_helpers.logger") as mock_logger:
            for part in test_parts:
                result = select_pcie_ip_core(part)
                assert result == "pcie_7x"
                mock_logger.warning.assert_called()


class TestWriteTclFileWithLogging:
    """Test TCL file writing with logging functionality."""

    def test_successful_file_write(self):
        """Test successful TCL file writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.tcl"
            tcl_files_list = []
            content = '# Test TCL content\nputs "Hello World"'

            result = write_tcl_file_with_logging(
                content, file_path, tcl_files_list, "test TCL"
            )

            assert result is True
            assert file_path.exists()
            assert file_path.read_text() == content
            assert str(file_path) in tcl_files_list

    def test_create_parent_directories(self):
        """Test that parent directories are created if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "subdir" / "nested" / "test.tcl"
            tcl_files_list = []
            content = "# Test content"

            result = write_tcl_file_with_logging(
                content, file_path, tcl_files_list, "test TCL"
            )

            assert result is True
            assert file_path.exists()
            assert file_path.parent.exists()

    def test_custom_logger(self):
        """Test using custom logger instance."""
        custom_logger = Mock()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.tcl"
            tcl_files_list = []
            content = "# Test content"

            result = write_tcl_file_with_logging(
                content, file_path, tcl_files_list, "test TCL", custom_logger
            )

            assert result is True
            custom_logger.info.assert_called_once_with("Generated test TCL")

    def test_file_write_error(self):
        """Test handling of file write errors."""
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")

            tcl_files_list = []

            with patch("build_helpers.logger") as mock_logger:
                result = write_tcl_file_with_logging(
                    "content", "/invalid/path/test.tcl", tcl_files_list, "test TCL"
                )

                assert result is False
                assert len(tcl_files_list) == 0
                mock_logger.error.assert_called_once()

    def test_string_path_input(self):
        """Test with string path input instead of Path object."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = str(Path(temp_dir) / "test.tcl")
            tcl_files_list = []
            content = "# Test content"

            result = write_tcl_file_with_logging(
                content, file_path, tcl_files_list, "test TCL"
            )

            assert result is True
            assert Path(file_path).exists()
            assert file_path in tcl_files_list


class TestFpgaStrategySelector:
    """Test FPGA strategy selector functionality."""

    def test_artix7_35t_strategy(self):
        """Test strategy for Artix-7 35T parts."""
        selector = create_fpga_strategy_selector()
        config = selector("xc7a35tcsg324-2")

        assert config["pcie_ip_type"] == "axi_pcie"
        assert config["family"] == "artix7"
        assert config["size"] == "small"
        assert config["max_lanes"] == 4
        assert config["supports_msi"] is True
        assert config["supports_msix"] is False
        assert "clock_constraints" in config

    def test_artix7_75t_strategy(self):
        """Test strategy for Artix-7 75T parts."""
        selector = create_fpga_strategy_selector()
        config = selector("xc7a75tfgg484-2")

        assert config["pcie_ip_type"] == "pcie_7x"
        assert config["family"] == "artix7"
        assert config["size"] == "medium"
        assert config["max_lanes"] == 8
        assert config["supports_msi"] is True
        assert config["supports_msix"] is True

    def test_kintex7_strategy(self):
        """Test strategy for Kintex-7 parts."""
        selector = create_fpga_strategy_selector()
        config = selector("xc7k325tffg900-2")

        assert config["pcie_ip_type"] == "pcie_7x"
        assert config["family"] == "kintex7"
        assert config["size"] == "medium"
        assert config["max_lanes"] == 8
        assert config["supports_msi"] is True
        assert config["supports_msix"] is True

    def test_zynq_ultrascale_strategy(self):
        """Test strategy for Zynq UltraScale+ parts."""
        selector = create_fpga_strategy_selector()
        config = selector("xczu3eg-sbva484-1-e")

        assert config["pcie_ip_type"] == "pcie_ultrascale"
        assert config["family"] == "zynq_ultrascale"
        assert config["size"] == "large"
        assert config["max_lanes"] == 16
        assert config["supports_msi"] is True
        assert config["supports_msix"] is True

    def test_default_strategy(self):
        """Test default strategy for unknown parts."""
        selector = create_fpga_strategy_selector()

        with patch("build_helpers.logger") as mock_logger:
            config = selector("unknown_part")

            assert config["pcie_ip_type"] == "pcie_7x"
            assert config["family"] == "unknown"
            assert config["size"] == "medium"
            assert config["max_lanes"] == 4
            assert config["supports_msi"] is True
            assert config["supports_msix"] is False
            mock_logger.warning.assert_called_once()

    def test_case_insensitive_matching(self):
        """Test that FPGA part matching is case insensitive."""
        selector = create_fpga_strategy_selector()

        # Test with uppercase
        config_upper = selector("XC7A35TCSG324-2")
        config_lower = selector("xc7a35tcsg324-2")

        assert config_upper == config_lower
        assert config_upper["pcie_ip_type"] == "axi_pcie"


class TestBatchWriteTclFiles:
    """Test batch TCL file writing functionality."""

    def test_successful_batch_write(self):
        """Test successful batch writing of multiple TCL files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tcl_contents = {
                "project.tcl": "# Project setup",
                "synthesis.tcl": "# Synthesis config",
                "implementation.tcl": "# Implementation config",
            }
            tcl_files_list = []

            results = batch_write_tcl_files(tcl_contents, temp_dir, tcl_files_list)

            # Check all files were written successfully
            assert all(results.values())
            assert len(results) == 3

            # Check files exist and have correct content
            for filename, content in tcl_contents.items():
                file_path = Path(temp_dir) / filename
                assert file_path.exists()
                assert file_path.read_text() == content
                assert str(file_path) in tcl_files_list

    def test_partial_failure_batch_write(self):
        """Test batch writing with some failures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tcl_contents = {
                "good_file.tcl": "# Good content",
                "bad_file.tcl": "# Bad content",
            }
            tcl_files_list = []

            # Mock write_tcl_file_with_logging to fail for one file
            with patch("build_helpers.write_tcl_file_with_logging") as mock_write:

                def write_side_effect(content, path, files_list, desc, logger):
                    if "bad_file" in str(path):
                        return False
                    else:
                        # Actually write the good file
                        Path(path).write_text(content)
                        files_list.append(str(path))
                        return True

                mock_write.side_effect = write_side_effect

                results = batch_write_tcl_files(tcl_contents, temp_dir, tcl_files_list)

                assert results["good_file.tcl"] is True
                assert results["bad_file.tcl"] is False

    def test_custom_logger_batch_write(self):
        """Test batch writing with custom logger."""
        custom_logger = Mock()

        with tempfile.TemporaryDirectory() as temp_dir:
            tcl_contents = {"test.tcl": "# Test content"}
            tcl_files_list = []

            results = batch_write_tcl_files(
                tcl_contents, temp_dir, tcl_files_list, custom_logger
            )

            assert results["test.tcl"] is True
            # Should log summary
            custom_logger.info.assert_called()

    def test_empty_contents_batch_write(self):
        """Test batch writing with empty contents dictionary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tcl_files_list = []

            results = batch_write_tcl_files({}, temp_dir, tcl_files_list)

            assert results == {}
            assert len(tcl_files_list) == 0


class TestValidateFpgaPart:
    """Test FPGA part validation functionality."""

    def test_validate_known_parts(self):
        """Test validation with known FPGA parts."""
        known_parts = {"xc7a35tcsg324-2", "xc7a75tfgg484-2", "xczu3eg-sbva484-1-e"}

        for part in known_parts:
            assert validate_fpga_part(part, known_parts) is True

    def test_validate_unknown_but_valid_format(self):
        """Test validation of unknown parts with valid format."""
        valid_parts = [
            "xc7a100tcsg324-2",  # Valid Artix-7 format
            "xc7k160tfbg484-1",  # Valid Kintex-7 format
            "xczu7ev-ffvc1156-2-e",  # Valid Zynq UltraScale+ format
        ]

        for part in valid_parts:
            assert validate_fpga_part(part) is True

    def test_validate_invalid_parts(self):
        """Test validation of invalid FPGA parts."""
        invalid_parts = [
            "",  # Empty string
            "invalid_part",  # No valid prefix
            "xc6vlx240t",  # Older generation (not in valid prefixes)
            "altera_part",  # Different vendor
        ]

        for part in invalid_parts:
            assert validate_fpga_part(part) is False

    def test_validate_with_constants_import_error(self):
        """Test validation when constants import fails."""
        with patch("build_helpers.BOARD_PARTS", side_effect=ImportError):
            # Should fall back to basic validation
            assert validate_fpga_part("xc7a35tcsg324-2") is True
            assert validate_fpga_part("invalid_part") is False

    def test_validate_case_insensitive(self):
        """Test that validation is case insensitive."""
        part_lower = "xc7a35tcsg324-2"
        part_upper = "XC7A35TCSG324-2"

        assert validate_fpga_part(part_lower) is True
        assert validate_fpga_part(part_upper) is True

    def test_validate_none_input(self):
        """Test validation with None input."""
        assert validate_fpga_part(None) is False


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple helper functions."""

    def test_complete_fpga_configuration_workflow(self):
        """Test complete workflow from FPGA part to configuration."""
        fpga_part = "xc7a35tcsg324-2"

        # Validate the part
        assert validate_fpga_part(fpga_part) is True

        # Select PCIe IP core
        pcie_ip = select_pcie_ip_core(fpga_part)
        assert pcie_ip == "axi_pcie"

        # Get strategy configuration
        selector = create_fpga_strategy_selector()
        config = selector(fpga_part)

        assert config["pcie_ip_type"] == pcie_ip
        assert config["family"] == "artix7"
        assert config["supports_msix"] is False  # Limited resources

    def test_batch_tcl_generation_with_strategy(self):
        """Test generating TCL files using FPGA strategy."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fpga_part = "xc7a75tfgg484-2"
            selector = create_fpga_strategy_selector()
            config = selector(fpga_part)

            # Generate TCL content based on strategy
            tcl_contents = {
                "ip_config.tcl": f"# PCIe IP: {config['pcie_ip_type']}\n# Max lanes: {config['max_lanes']}",
                "constraints.tcl": f"# Constraints for {config['family']}\n# Clock file: {config['clock_constraints']}",
            }

            tcl_files_list = []
            results = batch_write_tcl_files(tcl_contents, temp_dir, tcl_files_list)

            assert all(results.values())
            assert len(tcl_files_list) == 2

            # Verify content
            ip_file = Path(temp_dir) / "ip_config.tcl"
            assert "pcie_7x" in ip_file.read_text()
            assert "8" in ip_file.read_text()  # max_lanes

    def test_error_handling_integration(self):
        """Test error handling across multiple helper functions."""
        # Test with invalid FPGA part
        invalid_part = "invalid_fpga_part"

        # Validation should fail
        assert validate_fpga_part(invalid_part) is False

        # PCIe selection should use default with warning
        with patch("build_helpers.logger") as mock_logger:
            pcie_ip = select_pcie_ip_core(invalid_part)
            assert pcie_ip == "pcie_7x"  # Default
            mock_logger.warning.assert_called()

        # Strategy selector should use default
        selector = create_fpga_strategy_selector()
        with patch("build_helpers.logger") as mock_logger:
            config = selector(invalid_part)
            assert config["family"] == "unknown"
            mock_logger.warning.assert_called()


class TestLoggingBehavior:
    """Test logging behavior of helper functions."""

    def test_write_tcl_file_logging_levels(self):
        """Test different logging levels in write_tcl_file_with_logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.tcl"
            tcl_files_list = []

            # Test with different logger levels
            for level in [logging.DEBUG, logging.INFO, logging.WARNING]:
                logger = logging.getLogger(f"test_logger_{level}")
                logger.setLevel(level)

                result = write_tcl_file_with_logging(
                    "# Test content", file_path, tcl_files_list, "test TCL", logger
                )

                assert result is True

    def test_batch_write_logging_summary(self):
        """Test that batch write logs summary correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tcl_contents = {
                "file1.tcl": "content1",
                "file2.tcl": "content2",
                "file3.tcl": "content3",
            }
            tcl_files_list = []

            with patch("build_helpers.logger") as mock_logger:
                results = batch_write_tcl_files(tcl_contents, temp_dir, tcl_files_list)

                # Should log summary with success count
                summary_calls = [
                    call
                    for call in mock_logger.info.call_args_list
                    if "Batch TCL write completed" in str(call)
                ]
                assert len(summary_calls) == 1
                assert "3/3 files successful" in str(summary_calls[0])
