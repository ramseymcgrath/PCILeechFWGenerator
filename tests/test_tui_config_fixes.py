"""
Test TUI Configuration Fixes

Tests to verify that configuration changes are properly applied and
that the donor dump functionality is accessible.
"""

from tui.models.config import BuildConfiguration
from tui.core.config_manager import ConfigManager
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestConfigurationFixes:
    """Test configuration fixes in the TUI"""

    def test_default_configuration_has_donor_dump_enabled(self):
        """Test that default configuration has donor dump enabled"""
        config = BuildConfiguration()

        assert config.donor_dump is True
        assert config.local_build is False
        assert config.name == "Default Configuration"

    def test_config_manager_persistence(self):
        """Test that config manager properly persists configurations"""
        config_manager = ConfigManager()

        # Create a test configuration
        test_config = BuildConfiguration(
            board_type="100t",
            device_type="network",
            donor_dump=True,
            local_build=False,
            name="Test Config",
        )

        # Set current config
        config_manager.set_current_config(test_config)

        # Get current config
        retrieved_config = config_manager.get_current_config()

        assert retrieved_config.board_type == "100t"
        assert retrieved_config.device_type == "network"
        assert retrieved_config.donor_dump is True
        assert retrieved_config.local_build is False
        assert retrieved_config.name == "Test Config"

    def test_configuration_to_cli_args_with_donor_dump(self):
        """Test that configuration properly converts to CLI args with donor dump"""
        config = BuildConfiguration(
            board_type="75t",
            device_type="network",
            donor_dump=True,
            local_build=False,
            advanced_sv=True,
            enable_variance=True,
        )

        cli_args = config.to_cli_args()

        assert cli_args["board"] == "75t"
        assert cli_args["device_type"] == "network"
        assert cli_args["use_donor_dump"] is True
        assert cli_args["advanced_sv"] is True
        assert cli_args["enable_variance"] is True

    def test_configuration_to_cli_args_without_donor_dump(self):
        """Test that configuration properly converts to CLI args without donor dump"""
        config = BuildConfiguration(
            board_type="35t",
            device_type="generic",
            donor_dump=False,
            local_build=True,
            advanced_sv=False,
            enable_variance=False,
        )

        cli_args = config.to_cli_args()

        assert cli_args["board"] == "35t"
        assert cli_args["device_type"] == "generic"
        assert cli_args["use_donor_dump"] is False
        assert cli_args["advanced_sv"] is False
        assert cli_args["enable_variance"] is False

    def test_configuration_feature_summary_with_donor_dump(self):
        """Test that feature summary includes donor dump when enabled"""
        config = BuildConfiguration(
            donor_dump=True,
            local_build=False,
            advanced_sv=True,
            enable_variance=True)

        summary = config.feature_summary

        assert "Donor Device Analysis" in summary
        assert "Advanced SystemVerilog" in summary
        assert "Manufacturing Variance" in summary

    def test_configuration_feature_summary_without_donor_dump(self):
        """Test that feature summary includes local build when donor dump disabled"""
        config = BuildConfiguration(
            donor_dump=False,
            local_build=True,
            advanced_sv=False,
            enable_variance=False)

        summary = config.feature_summary

        assert "Local Build" in summary
        assert "Donor Device Analysis" not in summary

    def test_configuration_copy_preserves_donor_dump_settings(self):
        """Test that copying configuration preserves donor dump settings"""
        original_config = BuildConfiguration(
            donor_dump=True,
            local_build=False,
            auto_install_headers=True,
            donor_info_file="/path/to/donor.json",
        )

        copied_config = original_config.copy()

        assert copied_config.donor_dump == original_config.donor_dump
        assert copied_config.local_build == original_config.local_build
        assert (copied_config.auto_install_headers ==
                original_config.auto_install_headers)
        assert copied_config.donor_info_file == original_config.donor_info_file

    def test_configuration_validation_with_valid_settings(self):
        """Test that configuration validation passes with valid settings"""
        # This should not raise any exceptions
        config = BuildConfiguration(
            board_type="75t",
            device_type="network",
            donor_dump=True,
            profile_duration=30.0,
        )

        assert config.board_type == "75t"
        assert config.device_type == "network"
        assert config.donor_dump is True
        assert config.profile_duration == 30.0

    def test_configuration_validation_with_invalid_board_type(self):
        """Test that configuration validation fails with invalid board type"""
        with pytest.raises(ValueError, match="Invalid board type"):
            BuildConfiguration(board_type="invalid_board")

    def test_configuration_validation_with_invalid_device_type(self):
        """Test that configuration validation fails with invalid device type"""
        with pytest.raises(ValueError, match="Invalid device type"):
            BuildConfiguration(device_type="invalid_device")

    def test_configuration_validation_with_invalid_profile_duration(self):
        """Test that configuration validation fails with invalid profile duration"""
        with pytest.raises(ValueError, match="Profile duration must be positive"):
            BuildConfiguration(profile_duration=-1.0)


class TestTUIConfigurationIntegration:
    """Test TUI configuration integration"""

    @patch("src.tui.main.PCILeechTUI")
    def test_tui_configuration_update_calls_config_manager(self, mock_tui):
        """Test that TUI configuration updates call config manager"""
        # This test would verify that when configuration is updated in the TUI,
        # it properly calls config_manager.set_current_config()

        # Create mock instances
        mock_app = Mock()
        mock_config_manager = Mock()
        mock_app.config_manager = mock_config_manager

        # Create test configuration
        test_config = BuildConfiguration(donor_dump=True, local_build=False)

        # Simulate configuration update
        mock_app.config_manager.set_current_config(test_config)

        # Verify that set_current_config was called
        mock_config_manager.set_current_config.assert_called_once_with(
            test_config)

    def test_donor_dump_toggle_functionality(self):
        """Test donor dump toggle functionality"""
        # Test enabling donor dump
        config = BuildConfiguration(donor_dump=False, local_build=True)

        # Simulate enabling donor dump
        config.donor_dump = True
        config.local_build = False

        assert config.donor_dump is True
        assert config.local_build is False

        # Test disabling donor dump
        config.donor_dump = False
        config.local_build = True

        assert config.donor_dump is False
        assert config.local_build is True


if __name__ == "__main__":
    pytest.main([__file__])
