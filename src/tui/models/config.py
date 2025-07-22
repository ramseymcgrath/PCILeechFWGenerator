"""
Build Configuration Data Model

Comprehensive build configuration for the TUI interface.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

# Import production defaults
try:
    from ...constants import PRODUCTION_DEFAULTS
except ImportError:
    # Fallback defaults if constants not available
    PRODUCTION_DEFAULTS = {
        "ADVANCED_SV": True,
        "MANUFACTURING_VARIANCE": True,
        "BEHAVIOR_PROFILING": True,
        "POWER_MANAGEMENT": True,
        "ERROR_HANDLING": True,
        "PERFORMANCE_COUNTERS": True,
        "DEFAULT_DEVICE_TYPE": "network",
    }


@dataclass
class BuildConfiguration:
    """Comprehensive build configuration with production defaults"""

    board_type: str = "pcileech_35t325_x1"
    device_type: str = PRODUCTION_DEFAULTS["DEFAULT_DEVICE_TYPE"]
    advanced_sv: bool = PRODUCTION_DEFAULTS["ADVANCED_SV"]
    enable_variance: bool = PRODUCTION_DEFAULTS["MANUFACTURING_VARIANCE"]
    behavior_profiling: bool = PRODUCTION_DEFAULTS["BEHAVIOR_PROFILING"]
    profile_duration: float = 30.0
    disable_ftrace: bool = False
    power_management: bool = PRODUCTION_DEFAULTS["POWER_MANAGEMENT"]
    error_handling: bool = PRODUCTION_DEFAULTS["ERROR_HANDLING"]
    performance_counters: bool = PRODUCTION_DEFAULTS["PERFORMANCE_COUNTERS"]
    flash_after_build: bool = False

    # Donor dump configuration
    donor_dump: bool = True  # Default to donor dump enabled
    auto_install_headers: bool = False
    donor_info_file: Optional[str] = None
    skip_board_check: bool = False
    local_build: bool = False  # Default to standard builds with donor dump

    # Profile metadata
    name: str = "Production Configuration"
    description: str = (
        "Production-ready configuration with all advanced features enabled"
    )
    created_at: Optional[str] = None
    last_used: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization"""
        valid_board_types = [
            # CaptainDMA boards
            "pcileech_75t484_x1",
            "pcileech_35t484_x1",
            "pcileech_35t325_x4",
            "pcileech_35t325_x1",
            "pcileech_100t484_x1",
            # Other boards
            "pcileech_enigma_x1",
            "pcileech_squirrel",
            "pcileech_pciescreamer_xc7a35",
        ]
        if self.board_type not in valid_board_types:
            raise ValueError(f"Invalid board type: {self.board_type}")

        if self.device_type not in [
            "network",
            "storage",
            "graphics",
            "audio",
            "generic",
        ]:
            raise ValueError(f"Invalid device type: {self.device_type}")

        if self.profile_duration <= 0:
            raise ValueError("Profile duration must be positive")

    @property
    def is_advanced(self) -> bool:
        """Check if advanced features are enabled"""
        return (
            self.advanced_sv
            or self.enable_variance
            or self.behavior_profiling
            or self.device_type != "generic"
        )

    @property
    def feature_summary(self) -> str:
        """Get a summary of enabled features"""
        features = []
        if self.advanced_sv:
            features.append("Advanced SystemVerilog")
        if self.enable_variance:
            features.append("Manufacturing Variance")
        if self.behavior_profiling:
            features.append("Behavior Profiling")
        if self.device_type != "generic":
            features.append(f"{self.device_type.title()} Optimizations")
        if self.donor_dump:
            features.append("Donor Device Analysis")
        if self.local_build:
            features.append("Local Build")
            if self.donor_info_file:
                features.append("Custom Donor Info")
            if self.skip_board_check:
                features.append("Skip Board Check")

        return ", ".join(features) if features else "Basic Configuration"

    def to_cli_args(self) -> Dict[str, Any]:
        """Convert to CLI arguments for unified pcileech.py entrypoint"""
        args = {
            "board": self.board_type,
            "flash": self.flash_after_build,
            "advanced_sv": self.advanced_sv,
            "device_type": self.device_type,
            "enable_variance": self.enable_variance,
            "disable_power_management": not self.power_management,
            "disable_error_handling": not self.error_handling,
            "disable_performance_counters": not self.performance_counters,
            "enable_behavior_profiling": self.behavior_profiling,
            "behavior_profile_duration": int(self.profile_duration),
            "use_donor_dump": self.donor_dump,  # Use the new parameter name
            "auto_install_headers": self.auto_install_headers,
        }

        # Add local build options if enabled
        if self.local_build:
            if self.donor_info_file:
                args["donor_info_file"] = self.donor_info_file
            if self.skip_board_check:
                args["skip_board_check"] = True

        return args

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "board_type": self.board_type,
            "device_type": self.device_type,
            "advanced_sv": self.advanced_sv,
            "enable_variance": self.enable_variance,
            "behavior_profiling": self.behavior_profiling,
            "profile_duration": self.profile_duration,
            "power_management": self.power_management,
            "error_handling": self.error_handling,
            "performance_counters": self.performance_counters,
            "flash_after_build": self.flash_after_build,
            "donor_dump": self.donor_dump,
            "auto_install_headers": self.auto_install_headers,
            "donor_info_file": self.donor_info_file,
            "skip_board_check": self.skip_board_check,
            "local_build": self.local_build,
            "created_at": self.created_at,
            "last_used": self.last_used,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BuildConfiguration":
        """Create instance from dictionary"""
        return cls(**data)

    def save_to_file(self, filepath: Path) -> None:
        """
        Save configuration to JSON file

        Args:
            filepath: Path to save the configuration file

        Raises:
            PermissionError: If the file cannot be written due to permission issues
            OSError: If there's an error creating the directory or writing the file
            Exception: For any other unexpected errors
        """
        try:
            # Create parent directory if it doesn't exist
            if not filepath.parent.exists():
                filepath.parent.mkdir(parents=True, exist_ok=True)

                # Set appropriate permissions on Unix-like systems
                if os.name != "nt":  # Skip on Windows
                    os.chmod(
                        filepath.parent, 0o700  # User: rwx, Group: ---, Other: ---
                    )

            # Write the file
            with open(filepath, "w") as f:
                json.dump(self.to_dict(), f, indent=2)

            # Set appropriate permissions on Unix-like systems
            if os.name != "nt":  # Skip on Windows
                os.chmod(filepath, 0o600)  # User: rw-, Group: ---, Other: ---
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied when saving to {filepath}: {str(e)}"
            )
        except OSError as e:
            raise OSError(
                f"Failed to create directory or write file {filepath}: {str(e)}"
            )
        except Exception as e:
            raise Exception(
                f"Unexpected error when saving configuration to {filepath}: {str(e)}"
            )

    @classmethod
    def load_from_file(cls, filepath: Path) -> "BuildConfiguration":
        """
        Load configuration from JSON file

        Args:
            filepath: Path to the configuration file

        Returns:
            BuildConfiguration: The loaded configuration

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read due to permission issues
            json.JSONDecodeError: If the file contains invalid JSON
            ValueError: If the configuration data is invalid
            Exception: For any other unexpected errors
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied when reading {filepath}: {str(e)}"
            )
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in configuration file {filepath}: {e.msg}",
                e.doc,
                e.pos,
            )
        except ValueError as e:
            raise ValueError(f"Invalid configuration data in {filepath}: {str(e)}")
        except Exception as e:
            raise Exception(
                f"Unexpected error when loading configuration from {filepath}: {str(e)}"
            )

    def copy(self) -> "BuildConfiguration":
        """Create a copy of this configuration"""
        return BuildConfiguration.from_dict(self.to_dict())
