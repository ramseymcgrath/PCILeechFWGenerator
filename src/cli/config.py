"""Configuration dataclass for PCILeech firmware generation."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BuildConfig:
    """Strongly-typed configuration for firmware build process."""
    
    # Device configuration
    bdf: str
    vendor: str
    device: str
    board: str = "pcileech_75t484_x1"
    device_type: str = "generic"
    
    # Advanced features
    advanced_sv: bool = True
    enable_variance: bool = True
    donor_dump: bool = True
    auto_install_headers: bool = True
    
    # Feature toggles
    disable_power_management: bool = False
    disable_error_handling: bool = False
    disable_performance_counters: bool = False
    
    # USB/Flash configuration
    enable_ft601: bool = True
    disable_ft601: bool = False
    flash: bool = True
    
    # Timing configuration
    behavior_profile_duration: int = 45
    
    # Mode configuration
    tui: bool = False
    interactive: bool = False
    
    # Runtime state
    original_driver: Optional[str] = None
    iommu_group: Optional[str] = None
    vfio_device: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        # Force FT601 for CaptainDMA 75T board
        if self.board == "pcileech_75t484_x1":
            if self.disable_ft601:
                raise ValueError("FT601 USB-3 capture cannot be disabled for pcileech_75t484_x1 board")
            self.enable_ft601 = True
            self.disable_ft601 = False
        
        # Validate BDF format
        import re
        bdf_pattern = re.compile(r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]$")
        if not bdf_pattern.match(self.bdf):
            raise ValueError(f"Invalid BDF format: {self.bdf}. Expected format: DDDD:BB:DD.F")
        
        # Validate vendor and device IDs
        if not re.match(r"^[0-9a-fA-F]{4}$", self.vendor):
            raise ValueError(f"Invalid vendor ID format: {self.vendor}. Expected 4-digit hex.")
        if not re.match(r"^[0-9a-fA-F]{4}$", self.device):
            raise ValueError(f"Invalid device ID format: {self.device}. Expected 4-digit hex.")