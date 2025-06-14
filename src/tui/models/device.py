"""
PCIe Device Data Model

Enhanced PCIe device information for the TUI interface.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PCIDevice:
    """Enhanced PCIe device information."""

    bdf: str
    vendor_id: str
    device_id: str
    vendor_name: str
    device_name: str
    device_class: str
    subsystem_vendor: str
    subsystem_device: str
    driver: Optional[str]
    iommu_group: str
    power_state: str
    link_speed: str
    bars: List[Dict[str, Any]]
    suitability_score: float
    compatibility_issues: List[str]
    compatibility_factors: List[Dict[str, Any]] = field(default_factory=list)

    # Enhanced compatibility indicators
    is_valid: bool = True
    has_driver: bool = False
    is_detached: bool = False
    vfio_compatible: bool = False
    iommu_enabled: bool = False
    detailed_status: Dict[str, Any] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        """Human-readable device name for display."""
        return f"{self.vendor_name} {self.device_name}"

    @property
    def is_suitable(self) -> bool:
        """Check if device is suitable for firmware generation."""
        return self.suitability_score >= 0.7 and len(self.compatibility_issues) == 0

    @property
    def status_indicator(self) -> str:
        """Status indicator for UI display."""
        if not self.is_suitable:
            return "❌"
        elif self.driver:
            return "⚠️"
        else:
            return "✅"

    @property
    def validity_indicator(self) -> str:
        """Device validity indicator."""
        return "✅" if self.is_valid else "❌"

    @property
    def driver_indicator(self) -> str:
        """Driver status indicator."""
        if not self.has_driver:
            return "🔌"  # No driver
        elif self.is_detached:
            return "🔓"  # Detached
        else:
            return "🔒"  # Bound

    @property
    def vfio_indicator(self) -> str:
        """VFIO compatibility indicator."""
        return "🛡️" if self.vfio_compatible else "❌"

    @property
    def iommu_indicator(self) -> str:
        """IOMMU status indicator."""
        return "🔒" if self.iommu_enabled else "❌"

    @property
    def ready_indicator(self) -> str:
        """Overall readiness indicator."""
        if self.is_valid and self.vfio_compatible and self.iommu_enabled:
            return "⚡"
        elif self.is_suitable:
            return "⚠️"
        else:
            return "❌"

    @property
    def compact_status(self) -> str:
        """Compact multi-indicator status for table display."""
        indicators = []
        indicators.append(self.validity_indicator)
        indicators.append(self.driver_indicator)
        indicators.append(self.vfio_indicator)
        indicators.append(self.iommu_indicator)
        indicators.append(self.ready_indicator)
        return "".join(indicators)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "bd": self.bdf,
            "vendor_id": self.vendor_id,
            "device_id": self.device_id,
            "vendor_name": self.vendor_name,
            "device_name": self.device_name,
            "device_class": self.device_class,
            "subsystem_vendor": self.subsystem_vendor,
            "subsystem_device": self.subsystem_device,
            "driver": self.driver,
            "iommu_group": self.iommu_group,
            "power_state": self.power_state,
            "link_speed": self.link_speed,
            "bars": self.bars,
            "suitability_score": self.suitability_score,
            "compatibility_issues": self.compatibility_issues,
            "compatibility_factors": self.compatibility_factors,
            "is_valid": self.is_valid,
            "has_driver": self.has_driver,
            "is_detached": self.is_detached,
            "vfio_compatible": self.vfio_compatible,
            "iommu_enabled": self.iommu_enabled,
            "detailed_status": self.detailed_status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PCIDevice":
        """Create instance from dictionary."""
        return cls(**data)
