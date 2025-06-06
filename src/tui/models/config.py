"""
Build Configuration Data Model

Comprehensive build configuration for the TUI interface.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class BuildConfiguration:
    """Comprehensive build configuration"""

    board_type: str = "75t"
    device_type: str = "generic"
    advanced_sv: bool = True
    enable_variance: bool = True
    behavior_profiling: bool = False
    profile_duration: float = 30.0
    power_management: bool = True
    error_handling: bool = True
    performance_counters: bool = True
    flash_after_build: bool = False

    # Donor dump configuration
    donor_dump: bool = True  # Default to using donor dump
    auto_install_headers: bool = False
    donor_info_file: Optional[str] = None
    skip_board_check: bool = False
    local_build: bool = False

    # Profile metadata
    name: str = "Default Configuration"
    description: str = "Standard configuration for PCIe devices"
    created_at: Optional[str] = None
    last_used: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.board_type not in ["35t", "75t", "100t"]:
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
        """Convert to CLI arguments for existing generate.py"""
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
            "skip_donor_dump": not self.donor_dump,
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
        """Save configuration to JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: Path) -> "BuildConfiguration":
        """Load configuration from JSON file"""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def copy(self) -> "BuildConfiguration":
        """Create a copy of this configuration"""
        return BuildConfiguration.from_dict(self.to_dict())
