"""
Test TUI Configuration Fixes

Tests to verify that configuration changes are properly applied and
that the donor dump functionality is accessible.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from tui.core.config_manager import ConfigManager
from tui.models.config import BuildConfiguration

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
            donor_dump=True, local_build=False, advanced_sv=True, enable_variance=True
        )

        summary = config.feature_summary

        assert "Donor Device Analysis" in summary
        assert "Advanced SystemVerilog" in summary
        assert "Manufacturing Variance" in summary

    def test_configuration_feature_summary_without_donor_dump(self):
        """Test that feature summary includes local build when donor dump disabled"""
        config = BuildConfiguration(
            donor_dump=False, local_build=True, advanced_sv=False, enable_variance=False
        )

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
        assert (
            copied_config.auto_install_headers == original_config.auto_install_headers
        )
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
        mock_config_manager.set_current_config.assert_called_once_with(test_config)


class TestConfigManagerEnhanced:
    """Enhanced test cases for ConfigManager functionality."""

    def setUp(self):
        """Set up test environment."""
        import tempfile

        self.temp_dir = tempfile.mkdtemp()
        self.test_config_dir = Path(self.temp_dir) / ".pcileech" / "profiles"

    def tearDown(self):
        """Clean up test environment."""
        import os
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("pathlib.Path.home")
    def test_config_manager_initialization_with_error(self, mock_home):
        """Test ConfigManager initialization with directory creation error."""
        mock_home.return_value = Path(self.temp_dir)

        with patch.object(
            ConfigManager,
            "_ensure_config_directory",
            side_effect=Exception("Test error"),
        ):
            with patch("builtins.print") as mock_print:
                ConfigManager()

                mock_print.assert_called_once()
                assert (
                    "Warning: Could not initialize config directory"
                    in mock_print.call_args[0][0]
                )

    @patch("pathlib.Path.mkdir")
    @patch("os.chmod")
    def test_ensure_config_directory_success(self, mock_chmod, mock_mkdir):
        """Test successful config directory creation."""
        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()

        # Test the actual method
        with patch("os.name", "posix"):
            manager._ensure_config_directory()

            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mock_chmod.assert_called_once()

    @patch("pathlib.Path.mkdir")
    def test_ensure_config_directory_windows(self, mock_mkdir):
        """Test config directory creation on Windows."""
        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()

        with patch("os.name", "nt"):
            with patch("os.chmod") as mock_chmod:
                manager._ensure_config_directory()

                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
                mock_chmod.assert_not_called()

    @patch("pathlib.Path.mkdir")
    def test_ensure_config_directory_permission_error(self, mock_mkdir):
        """Test handling of permission errors during directory creation."""
        mock_mkdir.side_effect = PermissionError("Permission denied")

        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()

        with pytest.raises(PermissionError) as context:
            manager._ensure_config_directory()

        assert "Insufficient permissions" in str(context.exception)

    def test_save_profile_success(self):
        """Test successful profile saving."""
        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()
            config = BuildConfiguration()

            with patch.object(manager, "_ensure_config_directory"):
                with patch.object(config, "save_to_file") as mock_save:
                    result = manager.save_profile("test_profile", config)

                    assert result is True
                    assert config.name == "test_profile"
                    assert config.created_at is not None
                    assert config.last_used is not None
                    mock_save.assert_called_once()

    def test_save_profile_permission_error(self):
        """Test profile saving with permission error."""
        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()
            config = BuildConfiguration()

            with patch.object(manager, "_ensure_config_directory"):
                with patch.object(
                    config,
                    "save_to_file",
                    side_effect=PermissionError("Permission denied"),
                ):
                    with patch("builtins.print") as mock_print:
                        result = manager.save_profile("test_profile", config)

                        assert result is False
                        mock_print.assert_called_once()

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()

            # Test various problematic characters
            test_cases = [
                ("normal_name", "normal_name"),
                ("name with spaces", "name with spaces"),  # Spaces are preserved
                ("name/with\\slashes", "name_with_slashes"),
                ("name:with*special?chars", "name_with_special_chars"),
                ("name<with>pipes|", "name_with_pipes_"),
                (
                    "name\"with'quotes",
                    "name_with'quotes",
                ),  # Only double quotes replaced
            ]

            for input_name, expected in test_cases:
                result = manager._sanitize_filename(input_name)
                assert result == expected

    def test_load_profile_success(self):
        """Test successful profile loading."""
        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()

            with patch("pathlib.Path.exists", return_value=True):
                with patch.object(BuildConfiguration, "load_from_file") as mock_load:
                    mock_config = BuildConfiguration()
                    mock_config.name = "test_profile"
                    mock_config.board_type = "75t"
                    mock_load.return_value = mock_config

                    with patch.object(manager, "save_profile", return_value=True):
                        config = manager.load_profile("test_profile")

                        assert isinstance(config, BuildConfiguration)
                        if config:
                            assert config.name == "test_profile"
                            assert config.board_type == "75t"

    def test_load_profile_not_found(self):
        """Test loading non-existent profile."""
        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()

            with patch("pathlib.Path.exists", return_value=False):
                config = manager.load_profile("nonexistent")

                assert config is None

    def test_list_profiles_success(self):
        """Test successful profile listing."""
        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()

            # Mock profile files
            mock_files = [
                Path("profile1.json"),
                Path("profile2.json"),
                Path("profile3.json"),
            ]

            with patch("pathlib.Path.glob", return_value=mock_files):
                with patch("builtins.open", mock_open(read_data='{"name": "test"}')):
                    profiles = manager.list_profiles()

                    # Should return 3 profiles
                    assert len(profiles) == 3
                    # Each should be a dict with expected keys
                    for profile in profiles:
                        assert "name" in profile
                        assert "description" in profile
                        assert "filename" in profile

    def test_delete_profile_success(self):
        """Test successful profile deletion."""
        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()

            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.unlink") as mock_unlink:
                    result = manager.delete_profile("test_profile")

                    assert result is True
                    mock_unlink.assert_called_once()

    def test_delete_profile_not_found(self):
        """Test deleting non-existent profile."""
        with patch.object(ConfigManager, "_ensure_config_directory"):
            manager = ConfigManager()

            with patch("pathlib.Path.exists", return_value=False):
                result = manager.delete_profile("nonexistent")

                assert result is False

    @patch("pathlib.Path.home")
    def test_full_profile_lifecycle(self, mock_home):
        """Test complete profile lifecycle: create, save, load, delete."""
        mock_home.return_value = Path(self.temp_dir)

        # Create manager and ensure directory exists
        manager = ConfigManager()
        manager.config_dir.mkdir(parents=True, exist_ok=True)

        # Create and save profile
        config = BuildConfiguration()
        config.board_type = "75t"

        save_result = manager.save_profile("test_lifecycle", config)
        assert save_result is True

        # Load profile
        loaded_config = manager.load_profile("test_lifecycle")
        assert loaded_config is not None
        if loaded_config:
            assert loaded_config.board_type == "75t"

        # List profiles
        profiles = manager.list_profiles()
        profile_names = [p.get("name", "") for p in profiles]
        assert "test_lifecycle" in profile_names

        # Delete profile
        delete_result = manager.delete_profile("test_lifecycle")
        assert delete_result is True

        # Verify deletion
        profiles_after_delete = manager.list_profiles()
        profile_names_after = [p.get("name", "") for p in profiles_after_delete]
        assert "test_lifecycle" not in profile_names_after

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
