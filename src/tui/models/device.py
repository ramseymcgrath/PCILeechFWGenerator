"""
Device models for the PCILeech TUI application.

This module defines data classes for representing PCI devices in the application.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PCIDevice:
    """Enhanced PCIe device information."""

    bdf: str  # Bus/Device/Function identifier (e.g., "0000:00:00.0")
    vendor_id: str
    device_id: str
    vendor_name: str
    device_name: str
    device_class: str
    subsystem_vendor: Optional[str] = None
    subsystem_device: Optional[str] = None
    driver: Optional[str] = None
    iommu_group: Optional[int] = None
    power_state: Optional[str] = None
    link_speed: Optional[str] = None
    bars: Dict[str, Dict[str, str]] = field(default_factory=dict)
    suitability_score: int = 0
    compatibility_issues: List[str] = field(default_factory=list)
    compatibility_factors: List[str] = field(default_factory=list)
    detailed_status: Dict[str, str] = field(default_factory=dict)
    is_valid: bool = True
    has_driver: bool = False
    is_detached: bool = False
    vfio_compatible: bool = False
    iommu_enabled: bool = False
    compatibility_factors: List[str] = field(default_factory=list)
    detailed_status: Dict[str, str] = field(default_factory=dict)
    is_valid: bool = True
    has_driver: bool = False
    is_detached: bool = False
    vfio_compatible: bool = False
    iommu_enabled: bool = False

    @property
    def display_name(self) -> str:
        """Return a user-friendly display name for the device."""
        return f"{self.vendor_name} {self.device_name} ({self.bdf})"

    @property
    def is_supported(self) -> bool:
        """Check if the device is supported for firmware generation."""
        return self.compatibility_issues == []

    @property
    def is_suitable(self) -> bool:
        """Check if the device is suitable for firmware generation."""
        return (
            self.is_valid
            and self.vfio_compatible
            and len(self.compatibility_issues) == 0
        )

    @property
    def id(self) -> str:
        """Return the BDF as the device ID for backward compatibility."""
        return self.bdf

    @property
    def name(self) -> str:
        """Return the device name for backward compatibility."""
        return self.device_name

    @property
    def class_id(self) -> str:
        """Return the class ID for backward compatibility."""
        return self.device_class[:4]

    @property
    def class_name(self) -> str:
        """Return a human-readable class name based on the class ID."""
        class_names = {
            "0100": "SCSI Storage Controller",
            "0101": "IDE Controller",
            "0102": "Floppy Controller",
            "0103": "IPI Controller",
            "0104": "RAID Controller",
            "0105": "ATA Controller",
            "0106": "SATA Controller",
            "0107": "SAS Controller",
            "0180": "Other Storage Controller",
            "0200": "Ethernet Controller",
            "0280": "Other Network Controller",
            "0300": "VGA Compatible Controller",
            "0301": "XGA Controller",
            "0302": "3D Controller",
            "0380": "Other Display Controller",
            "0400": "Multimedia Video Controller",
            "0401": "Multimedia Audio Controller",
            "0402": "Computer Telephony Device",
            "0403": "Audio Device",
            "0480": "Other Multimedia Controller",
        }

        class_id = self.class_id
        return class_names.get(class_id, f"Unknown Device Class ({class_id})")

    def to_dict(self) -> Dict[str, Any]:
        """Convert device information to a dictionary for serialization."""
        from dataclasses import asdict
        import copy

        # Create a deep copy to avoid modifying the original
        device_dict = asdict(self)

        # Add any computed properties that should be included
        device_dict["is_suitable"] = self.is_suitable
        device_dict["is_supported"] = self.is_supported
        device_dict["class_name"] = self.class_name
        device_dict["display_name"] = self.display_name

        return device_dict
