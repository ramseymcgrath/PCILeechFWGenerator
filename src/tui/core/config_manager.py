"""
Configuration Manager

Manages build configuration profiles and persistence.
"""

import json
import os
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models.config import BuildConfiguration
from ..models.error import ErrorSeverity, TUIError


class ConfigManager:
    """Manages build configuration and profiles."""

    def __init__(self):
        self._current_config: Optional[BuildConfiguration] = None
        self.config_dir = Path.home() / ".pcileech" / "profiles"
        try:
            # Create directory with appropriate permissions if it doesn't exist
            self._ensure_config_directory()
        except Exception as e:
            # Log the error but continue - we'll handle file operations gracefully later
            print(f"Warning: Could not initialize config directory: {str(e)}")

    def get_current_config(self) -> BuildConfiguration:
        """Get current configuration, creating default if none exists."""
        if self._current_config is None:
            self._current_config = BuildConfiguration()
        return self._current_config

    def set_current_config(self, config: BuildConfiguration) -> None:
        """Set current configuration."""
        self._current_config = config
        # Update last used timestamp
        self._current_config.last_used = datetime.now().isoformat()

    def _ensure_config_directory(self) -> None:
        """
        Ensure the configuration directory exists with proper permissions.
        Creates the directory if it doesn't exist.
        """
        try:
            # Create directory with parents if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Set appropriate permissions (read/write for user only)
            # This helps prevent permission issues on multi-user systems
            if (
                os.name != "nt"
            ):  # Skip on Windows as it uses a different permission model
                os.chmod(
                    self.config_dir,
                    stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR,  # User: rwx
                )
        except PermissionError as e:
            raise PermissionError(
                f"Insufficient permissions to create or access config directory: {str(e)}"
            )
        except Exception as e:
            raise Exception(f"Failed to create config directory: {str(e)}")

    def save_profile(
        self, name: str, config: BuildConfiguration
    ) -> Tuple[bool, Optional[TUIError]]:
        """
        Save configuration profile to ~/.pcileech/profiles/.

        Returns:
            Tuple containing (success, error_if_any)
        """
        # Update metadata
        config.name = name
        config.created_at = config.created_at or datetime.now().isoformat()
        config.last_used = datetime.now().isoformat()

        try:
            # Ensure directory exists before saving
            self._ensure_config_directory()

            # Save to file
            profile_path = self.config_dir / f"{self._sanitize_filename(name)}.json"
            config.save_to_file(profile_path)
            return True, None
        except PermissionError as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Permission denied when saving profile '{name}'",
                details=str(e),
                suggested_actions=[
                    "Check file permissions in ~/.pcileech/profiles/",
                    "Ensure you have write access to your home directory",
                    "Try running the application with appropriate permissions",
                ],
            )
            return False, error
        except Exception as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Failed to save profile '{name}'",
                details=str(e),
                suggested_actions=[
                    "Check if your disk has sufficient space",
                    "Verify that the ~/.pcileech directory is accessible",
                ],
            )
            return False, error

    def load_profile(
        self, name: str
    ) -> Tuple[Optional[BuildConfiguration], Optional[TUIError]]:
        """
        Load configuration profile.

        Returns:
            Tuple containing (config_if_successful, error_if_any)
        """
        try:
            # Ensure directory exists
            self._ensure_config_directory()

            profile_path = self.config_dir / f"{self._sanitize_filename(name)}.json"
            if not profile_path.exists():
                error = TUIError(
                    severity=ErrorSeverity.WARNING,
                    category="config",
                    message=f"Profile '{name}' not found",
                    details=f"The configuration file does not exist at {profile_path}",
                    suggested_actions=[
                        "Check if the profile name is correct",
                        "Create a new profile with this name",
                    ],
                )
                return None, error

            config = BuildConfiguration.load_from_file(profile_path)

            # Update last used timestamp
            config.last_used = datetime.now().isoformat()
            success, error = self.save_profile(name, config)  # Save updated timestamp
            if not success and error:
                # If we couldn't save the updated timestamp, just log and continue
                print(
                    f"Warning: Could not update last_used timestamp for profile '{name}': {error.message}"
                )

            return config, None

        except PermissionError as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Permission denied when loading profile '{name}'",
                details=str(e),
                suggested_actions=[
                    "Check file permissions in ~/.pcileech/profiles/",
                    "Ensure you have read access to your home directory",
                ],
            )
            return None, error
        except json.JSONDecodeError as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Invalid JSON in profile '{name}'",
                details=f"Error at line {e.lineno}, column {e.colno}: {e.msg}",
                suggested_actions=[
                    "The profile file may be corrupted",
                    "Try deleting and recreating the profile",
                ],
            )
            return None, error
        except Exception as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Failed to load profile '{name}'",
                details=str(e),
                suggested_actions=[
                    "Check if the profile file exists and is accessible",
                    "Verify that the file contains valid JSON data",
                ],
            )
            return None, error

    def list_profiles(self) -> Tuple[List[Dict[str, str]], Optional[TUIError]]:
        """
        List available configuration profiles.

        Returns:
            Tuple containing (profiles_list, error_if_any)
        """
        try:
            # Ensure directory exists
            self._ensure_config_directory()

            profiles = []
            invalid_files = []

            for profile_file in self.config_dir.glob("*.json"):
                try:
                    with open(profile_file, "r") as f:
                        data = json.load(f)
                        profiles.append(
                            {
                                "name": data.get("name", profile_file.stem),
                                "description": data.get("description", ""),
                                "created_at": data.get("created_at", ""),
                                "last_used": data.get("last_used", ""),
                                "filename": profile_file.name,
                            }
                        )
                except (json.JSONDecodeError, KeyError):
                    # Track invalid files but don't stop processing
                    invalid_files.append(profile_file.name)
                except PermissionError:
                    # Track permission issues but don't stop processing
                    invalid_files.append(f"{profile_file.name} (permission denied)")
                except Exception:
                    # Track other issues but don't stop processing
                    invalid_files.append(f"{profile_file.name} (unknown error)")

            # Sort by last used (most recent first)
            profiles.sort(key=lambda x: x.get("last_used", ""), reverse=True)

            # If we found invalid files, return a warning
            if invalid_files:
                error = TUIError(
                    severity=ErrorSeverity.WARNING,
                    category="config",
                    message="Some profile files could not be loaded",
                    details=f"Skipped invalid files: {', '.join(invalid_files)}",
                    suggested_actions=[
                        "Check file permissions and format of the skipped files",
                        "Consider deleting corrupted profile files",
                    ],
                )
                return profiles, error

            return profiles, None

        except PermissionError as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message="Permission denied when listing profiles",
                details=str(e),
                suggested_actions=[
                    "Check permissions for ~/.pcileech/profiles/ directory",
                    "Ensure you have read access to your home directory",
                ],
            )
            return [], error
        except Exception as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message="Failed to list profiles",
                details=str(e),
                suggested_actions=[
                    "Check if the ~/.pcileech directory exists and is accessible"
                ],
            )
            return [], error

    def delete_profile(self, name: str) -> Tuple[bool, Optional[TUIError]]:
        """
        Delete a configuration profile.

        Returns:
            Tuple containing (success, error_if_any)
        """
        try:
            profile_path = self.config_dir / f"{self._sanitize_filename(name)}.json"
            if profile_path.exists():
                profile_path.unlink()
                return True, None
            return False, TUIError(
                severity=ErrorSeverity.WARNING,
                category="config",
                message=f"Profile '{name}' not found for deletion",
                details=f"The file {profile_path} does not exist",
                suggested_actions=["Check if the profile name is correct"],
            )
        except PermissionError as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Permission denied when deleting profile '{name}'",
                details=str(e),
                suggested_actions=[
                    "Check file permissions in ~/.pcileech/profiles/",
                    "Ensure you have write access to your home directory",
                ],
            )
            return False, error
        except Exception as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Failed to delete profile '{name}'",
                details=str(e),
                suggested_actions=[
                    "Check if the file is being used by another process",
                    "Verify that the ~/.pcileech directory is accessible",
                ],
            )
            return False, error

    def profile_exists(self, name: str) -> bool:
        """Check if a profile exists."""
        profile_path = self.config_dir / f"{self._sanitize_filename(name)}.json"
        return profile_path.exists()

    def create_default_profiles(self) -> Tuple[bool, Optional[TUIError]]:
        """
        Create default configuration profiles.

        Returns:
            Tuple containing (success, error_if_any)
        """
        try:
            # Ensure directory exists with proper permissions
            self._ensure_config_directory()

            default_profiles = [
                {
                    "name": "Network Device Standard",
                    "description": "Standard configuration for network devices",
                    "config": BuildConfiguration(
                        board_type="75t",
                        device_type="network",
                        advanced_sv=True,
                        enable_variance=True,
                        behavior_profiling=False,
                        profile_duration=30.0,
                        power_management=True,
                        error_handling=True,
                        performance_counters=True,
                        flash_after_build=False,
                    ),
                },
                {
                    "name": "Storage Device Optimized",
                    "description": "Optimized configuration for storage devices",
                    "config": BuildConfiguration(
                        board_type="100t",
                        device_type="storage",
                        advanced_sv=True,
                        enable_variance=True,
                        behavior_profiling=True,
                        profile_duration=45.0,
                        power_management=True,
                        error_handling=True,
                        performance_counters=True,
                        flash_after_build=False,
                    ),
                },
                {
                    "name": "Quick Development",
                    "description": "Fast configuration for development and testing",
                    "config": BuildConfiguration(
                        board_type="35t",
                        device_type="generic",
                        advanced_sv=False,
                        enable_variance=False,
                        behavior_profiling=False,
                        profile_duration=15.0,
                        power_management=False,
                        error_handling=False,
                        performance_counters=False,
                        flash_after_build=True,
                    ),
                },
                {
                    "name": "Full Featured",
                    "description": "All features enabled for comprehensive analysis",
                    "config": BuildConfiguration(
                        board_type="100t",
                        device_type="generic",
                        advanced_sv=True,
                        enable_variance=True,
                        behavior_profiling=True,
                        profile_duration=60.0,
                        power_management=True,
                        error_handling=True,
                        performance_counters=True,
                        flash_after_build=False,
                    ),
                },
            ]

            created_count = 0
            errors = []

            for profile_data in default_profiles:
                if not self.profile_exists(profile_data["name"]):
                    config = profile_data["config"]
                    config.name = profile_data["name"]
                    config.description = profile_data["description"]
                    success, error = self.save_profile(profile_data["name"], config)
                    if success:
                        created_count += 1
                    elif error:
                        errors.append(
                            f"Failed to create '{profile_data['name']}': {error.message}"
                        )
                    else:
                        errors.append(
                            f"Failed to create '{profile_data['name']}': Unknown error"
                        )

            if errors:
                error = TUIError(
                    severity=ErrorSeverity.WARNING,
                    category="config",
                    message=f"Created {created_count} of {len(default_profiles)} default profiles",
                    details="\n".join(errors),
                    suggested_actions=[
                        "Check permissions for ~/.pcileech/profiles/ directory",
                        "Ensure you have write access to your home directory",
                    ],
                )
                return created_count > 0, error

            return True, None

        except PermissionError as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message="Permission denied when creating default profiles",
                details=str(e),
                suggested_actions=[
                    "Check permissions for ~/.pcileech/profiles/ directory",
                    "Ensure you have write access to your home directory",
                    "Try running the application with appropriate permissions",
                ],
            )
            return False, error
        except Exception as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message="Failed to create default profiles",
                details=str(e),
                suggested_actions=[
                    "Check if your disk has sufficient space",
                    "Verify that the ~/.pcileech directory is accessible",
                ],
            )
            return False, error

    def export_profile(
        self, name: str, export_path: Path
    ) -> Tuple[bool, Optional[TUIError]]:
        """
        Export a profile to a specific path.

        Returns:
            Tuple containing (success, error_if_any)
        """
        try:
            config, error = self.load_profile(name)
            if error:
                return False, error

            if config:
                try:
                    config.save_to_file(export_path)
                    return True, None
                except PermissionError as e:
                    error = TUIError(
                        severity=ErrorSeverity.ERROR,
                        category="config",
                        message=f"Permission denied when exporting profile to {export_path}",
                        details=str(e),
                        suggested_actions=[
                            "Check if you have write permissions for the target directory",
                            "Try exporting to a different location",
                        ],
                    )
                    return False, error
                except Exception as e:
                    error = TUIError(
                        severity=ErrorSeverity.ERROR,
                        category="config",
                        message=f"Failed to export profile to {export_path}",
                        details=str(e),
                        suggested_actions=[
                            "Check if the target directory exists",
                            "Verify that you have sufficient disk space",
                        ],
                    )
                    return False, error
            return False, TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Cannot export profile '{name}' - profile not loaded",
                suggested_actions=["Check if the profile exists and is accessible"],
            )
        except Exception as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Unexpected error when exporting profile '{name}'",
                details=str(e),
            )
            return False, error

    def import_profile(
        self, import_path: Path, new_name: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[TUIError]]:
        """
        Import a profile from a file.

        Returns:
            Tuple containing (profile_name_if_successful, error_if_any)
        """
        try:
            if not import_path.exists():
                error = TUIError(
                    severity=ErrorSeverity.ERROR,
                    category="config",
                    message=f"Import file not found: {import_path}",
                    suggested_actions=[
                        "Check if the file path is correct",
                        "Verify that the file exists",
                    ],
                )
                return None, error

            try:
                config = BuildConfiguration.load_from_file(import_path)
            except json.JSONDecodeError as e:
                error = TUIError(
                    severity=ErrorSeverity.ERROR,
                    category="config",
                    message="Invalid JSON in import file",
                    details=f"Error at line {e.lineno}, column {e.colno}: {e.msg}",
                    suggested_actions=[
                        "Check if the file contains valid JSON data",
                        "Verify that the file is a valid configuration profile",
                    ],
                )
                return None, error
            except Exception as e:
                error = TUIError(
                    severity=ErrorSeverity.ERROR,
                    category="config",
                    message="Failed to parse import file",
                    details=str(e),
                    suggested_actions=[
                        "Check if the file is a valid configuration profile",
                        "Verify that the file is not corrupted",
                    ],
                )
                return None, error

            # Use provided name or extract from config
            profile_name = new_name or config.name or import_path.stem

            # Ensure unique name
            original_name = profile_name
            counter = 1
            while self.profile_exists(profile_name):
                profile_name = f"{original_name} ({counter})"
                counter += 1

            success, error = self.save_profile(profile_name, config)
            if not success:
                return None, error

            return profile_name, None

        except PermissionError as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Permission denied when importing profile from {import_path}",
                details=str(e),
                suggested_actions=[
                    "Check if you have read permissions for the source file",
                    "Ensure you have write access to ~/.pcileech/profiles/",
                ],
            )
            return None, error
        except Exception as e:
            error = TUIError(
                severity=ErrorSeverity.ERROR,
                category="config",
                message=f"Failed to import profile from {import_path}",
                details=str(e),
                suggested_actions=[
                    "Check if the file is accessible",
                    "Verify that the file is a valid configuration profile",
                ],
            )
            return None, error

    def get_profile_summary(self, name: str) -> Dict[str, str]:
        """
        Get a summary of a profile's configuration.
        Always returns a dictionary, with error information if loading fails.
        """
        try:
            config, error = self.load_profile(name)
            if error:
                return {"error": error.message, "details": error.details or ""}

            if config:
                return {
                    "name": config.name,
                    "description": config.description,
                    "board_type": config.board_type,
                    "device_type": config.device_type,
                    "features": config.feature_summary,
                    "advanced": "Yes" if config.is_advanced else "No",
                    "last_used": config.last_used or "Never",
                }
            return {"error": "Failed to load profile", "details": "Unknown error"}
        except Exception as e:
            return {"error": "Failed to load profile", "details": str(e)}

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize profile name for use as filename."""
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        sanitized = name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, "_")

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(" .")

        # Ensure it's not empty
        if not sanitized:
            sanitized = "unnamed_profile"

        return sanitized

    def validate_config(self, config: BuildConfiguration) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []

        try:
            # This will raise ValueError if invalid
            BuildConfiguration(**config.to_dict())
        except ValueError as e:
            issues.append(str(e))

        # Additional validation rules
        if config.behavior_profiling and config.profile_duration < 10:
            issues.append("Behavior profiling duration should be at least 10 seconds")

        if config.board_type == "35t" and config.is_advanced:
            issues.append("35t board may have limited resources for advanced features")

        return issues
