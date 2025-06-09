#!/usr/bin/env python3
"""
Test suite for configuration space shadow integration with the build process.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.build import build_tcl, get_donor_info
from src.donor_dump_manager import DonorDumpManager


class TestConfigSpaceIntegration(unittest.TestCase):
    """Test cases for configuration space shadow integration with the build process."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.donor_info_path = os.path.join(self.temp_dir.name, "donor_info.json")
        self.config_hex_path = os.path.join(self.temp_dir.name, "config_space_init.hex")

        # Sample configuration space data (simplified for testing)
        self.sample_config_space = "".join(["0123456789abcdef"] * 256)  # 4096 bytes

        # Sample device info
        self.sample_device_info = {
            "vendor_id": "0x8086",
            "device_id": "0x1533",
            "subvendor_id": "0x8086",
            "subsystem_id": "0x0000",
            "revision_id": "0x03",
            "class_code": "0x020000",
            "bar_size": "0x20000",
            "mpc": "0x2",
            "mpr": "0x2",
            "extended_config": self.sample_config_space,
        }

        # Save sample device info to file
        with open(self.donor_info_path, "w") as f:
            json.dump(self.sample_device_info, f)

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    @patch("src.build.DonorDumpManager")
    def test_get_donor_info_with_config_space(self, mock_manager_class):
        """Test that get_donor_info properly handles configuration space extraction."""
        # Setup mock
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.setup_module.return_value = self.sample_device_info

        # Call get_donor_info
        info = get_donor_info(
            bdf="0000:03:00.0",
            use_donor_dump=True,
            donor_info_path=self.donor_info_path,
            device_type="generic",
        )

        # Verify the result
        self.assertEqual(info["vendor_id"], "0x8086")
        self.assertEqual(info["device_id"], "0x1533")
        self.assertTrue("extended_config" in info)

        # Verify setup_module was called with extract_full_config=True
        mock_manager.setup_module.assert_called_once()
        call_args = mock_manager.setup_module.call_args[1]
        self.assertTrue(call_args.get("extract_full_config", False))

    def test_build_tcl_includes_config_space_hex(self):
        """Test that build_tcl includes the config_space_init.hex file."""
        # Call build_tcl
        tcl_content, tcl_path = build_tcl(
            self.sample_device_info, "vivado_generate_project_75t.tcl"
        )

        # Verify the TCL content includes config_space_init.hex
        self.assertIn("config_space_init.hex", tcl_content)

        # Clean up
        if os.path.exists(tcl_path):
            os.unlink(tcl_path)

    @patch("src.build.vivado_run")
    @patch("src.build.build_tcl")
    @patch("src.build.get_donor_info")
    def test_build_process_integration(
        self, mock_get_donor_info, mock_build_tcl, mock_vivado_run
    ):
        """Test the integration of configuration space shadow with the build process."""
        # Setup mocks
        mock_get_donor_info.return_value = self.sample_device_info
        mock_build_tcl.return_value = ("tcl_content", "tcl_path")

        # Create a mock for the build function
        with patch("src.build.build_sv") as mock_build_sv:
            from src.build import main

            # Mock command line arguments
            with patch(
                "sys.argv", ["build.py", "--bdf", "0000:03:00.0", "--board", "75t"]
            ):
                with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
                    # Configure mock arguments
                    mock_args = MagicMock()
                    mock_args.bdf = "0000:03:00.0"
                    mock_args.board = "75t"
                    mock_args.enable_behavior_profiling = False
                    mock_args.advanced_sv = False
                    mock_args.enhanced_timing = True
                    mock_args.save_analysis = None
                    mock_args.verbose = False
                    mock_parse_args.return_value = mock_args

                    # Run the main function
                    with patch("builtins.print"):  # Suppress print output
                        try:
                            main()
                        except SystemExit:
                            pass  # Ignore SystemExit

        # Verify that get_donor_info was called
        mock_get_donor_info.assert_called_once()

        # Verify that build_tcl was called with the sample device info
        mock_build_tcl.assert_called_once()
        self.assertEqual(mock_build_tcl.call_args[0][0], self.sample_device_info)

        # Verify that vivado_run was called
        mock_vivado_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
