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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "bdf": self.bdf,
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
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PCIDevice":
        """Create instance from dictionary."""
        return cls(**data)
