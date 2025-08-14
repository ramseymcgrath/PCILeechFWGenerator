"""
Configuration models for the PCILeech TUI application.

This module defines data classes for representing build configurations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BuildConfiguration:
    """Configuration for a PCILeech firmware build."""

    name: str = "Default Configuration"
    description: str = "Standard configuration for PCIe devices"
    device_id: Optional[str] = None
    device_type: str = "default"
    board_type: str = "default"
    output_directory: Optional[str] = None

    # Build options
    optimization_level: str = "balanced"
    debug_mode: bool = False
    enable_logging: bool = True
    enable_performance_counters: bool = False
    enable_error_counters: bool = True

    # Feature toggles
    advanced_sv: bool = True
    enable_variance: bool = True
    behavior_profiling: bool = False
    disable_ftrace: bool = False
    power_management: bool = True
    error_handling: bool = True
    performance_counters: bool = True
    flash_after_build: bool = False

    # Donor configuration
    donor_dump: bool = True
    auto_install_headers: bool = False
    local_build: bool = False
    skip_board_check: bool = False
    donor_info_file: Optional[str] = None
    profile_duration: float = 30.0

    # Advanced options
    custom_parameters: Dict[str, Any] = field(default_factory=dict)
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    compatibility_overrides: List[str] = field(default_factory=list)

    @property
    def is_advanced(self) -> bool:
        """Check if advanced features are enabled."""
        return self.advanced_sv

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary for serialization."""
        from dataclasses import asdict

        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BuildConfiguration":
        """Create a configuration from a dictionary."""
        # Filter out any keys that are not valid parameters
        valid_keys = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


@dataclass
class BuildProgress:
    """Progress information for a PCILeech firmware build."""

    build_id: str
    status: str  # "pending", "running", "completed", "failed", "cancelled"
    progress: float  # 0.0 to 100.0
    current_step: Optional[str] = None
    message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    logs: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if the build is complete."""
        return self.status in ("completed", "failed", "cancelled")

    @property
    def is_successful(self) -> bool:
        """Check if the build was successful."""
        return self.status == "completed" and not self.errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert progress information to a dictionary for serialization."""
        from dataclasses import asdict

        return asdict(self)
