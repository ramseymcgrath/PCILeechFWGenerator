#!/usr/bin/env python3
"""
Storage Function Capabilities

This module provides dynamic storage function capabilities for PCIe device
generation. It analyzes build-time provided vendor/device IDs to generate
realistic storage controller capabilities without hardcoding.

The module integrates with the existing templating and logging infrastructure
to provide production-ready dynamic capability generation.
"""

import logging
from typing import Any, Dict, List, Optional, Set

from .base_function_analyzer import BaseFunctionAnalyzer, create_function_capabilities

try:
    from ..string_utils import (
        log_debug_safe,
        log_error_safe,
        log_info_safe,
        log_warning_safe,
        safe_format,
    )
except ImportError:
    import sys
    from pathlib import Path

    src_dir = Path(__file__).parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from ..string_utils import (
        log_debug_safe,
        log_error_safe,
        log_info_safe,
        log_warning_safe,
        safe_format,
    )

logger = logging.getLogger(__name__)


class StorageFunctionAnalyzer(BaseFunctionAnalyzer):
    """
    Dynamic storage function capability analyzer.

    Analyzes vendor/device IDs provided at build time to generate realistic
    storage function capabilities without hardcoding device-specific behavior.
    """

    # Storage-specific capability IDs
    AER_CAP_ID = 0x0001  # Advanced Error Reporting

    # PCI class codes for storage devices
    CLASS_CODES = {
        "scsi": 0x010000,  # Mass storage controller, SCSI
        "ide": 0x010100,  # Mass storage controller, IDE
        "floppy": 0x010200,  # Mass storage controller, Floppy
        "ipi": 0x010300,  # Mass storage controller, IPI bus
        "raid": 0x010400,  # Mass storage controller, RAID
        "ata": 0x010500,  # Mass storage controller, ATA
        "sata": 0x010601,  # Mass storage controller, Serial ATA (AHCI)
        "sas": 0x010700,  # Mass storage controller, Serial Attached SCSI
        "nvme": 0x010802,  # Mass storage controller, NVMe
        "other_storage": 0x018000,  # Mass storage controller, Other
    }

    def __init__(self, vendor_id: int, device_id: int):
        """
        Initialize analyzer with build-time provided vendor/device IDs.

        Args:
            vendor_id: PCI vendor ID from build process
            device_id: PCI device ID from build process
        """
        super().__init__(vendor_id, device_id, "storage")

    def _analyze_device_category(self) -> str:
        """
        Analyze device category based on vendor/device ID patterns.

        Returns:
            Device category string (scsi, nvme, sata, etc.)
        """
        # Pattern-based analysis without hardcoding specific device IDs
        device_lower = self.device_id & 0xFF00
        device_upper = (self.device_id >> 8) & 0xFF

        # Vendor-specific patterns
        if self.vendor_id == 0x8086:  # Intel
            if device_lower in [0x2800, 0x2900, 0x3A00]:  # SATA ranges
                return "sata"
            elif device_lower in [0x0900, 0x0A00]:  # NVMe ranges
                return "nvme"
        elif self.vendor_id == 0x144D:  # Samsung
            if device_lower in [0xA800, 0xA900]:  # NVMe ranges
                return "nvme"
        elif self.vendor_id == 0x1B4B:  # Marvell
            if device_lower in [0x9100, 0x9200]:  # SATA ranges
                return "sata"
        elif self.vendor_id == 0x1000:  # LSI/Broadcom
            if device_lower in [0x0050, 0x0060]:  # SAS ranges
                return "sas"
            elif device_lower in [0x0070]:  # RAID ranges
                return "raid"

        # Generic patterns based on device ID structure
        if device_upper >= 0xA0:  # High device IDs often NVMe
            return "nvme"
        elif device_upper >= 0x80:  # Mid-high often SATA
            return "sata"
        elif device_upper >= 0x50:  # Mid often SAS
            return "sas"

        return "sata"  # Default fallback

    def _analyze_capabilities(self) -> Set[int]:
        """
        Analyze which capabilities this device should support.

        Returns:
            Set of capability IDs that should be present
        """
        caps = set()

        # Always include basic storage capabilities
        caps.update([0x01, 0x05, 0x10, 0x11])  # PM, MSI, PCIe, MSI-X

        # Advanced capabilities based on device analysis
        if self._supports_aer():
            caps.add(self.AER_CAP_ID)

        return caps

    def _supports_aer(self) -> bool:
        """Check if device likely supports Advanced Error Reporting."""
        # High-end storage devices (NVMe, enterprise SATA/SAS) support AER
        if self._device_category in ["nvme", "sas"]:
            return True
        elif self._device_category in ["sata", "raid"] and self.device_id > 0x2000:
            return True
        return False

    def get_device_class_code(self) -> int:
        """Get appropriate PCI class code for this device."""
        return self.CLASS_CODES.get(self._device_category, self.CLASS_CODES["sata"])

    def _create_capability_by_id(self, cap_id: int) -> Optional[Dict[str, Any]]:
        """Create capability by ID, handling storage-specific capabilities."""
        # Try base class capabilities first
        capability = super()._create_capability_by_id(cap_id)
        if capability:
            return capability
            
        # Handle storage-specific capabilities
        if cap_id == self.AER_CAP_ID:
            return self._create_aer_capability()
        else:
            return None

    def _create_pm_capability(self, aux_current: int = 0) -> Dict[str, Any]:
        """Create Power Management capability for storage devices."""
        # RAID controllers may need aux power
        aux_current = 100 if self._device_category == "raid" else 0
        return super()._create_pm_capability(aux_current)

    def _create_msi_capability(
        self,
        multi_message_capable: Optional[int] = None,
        supports_per_vector_masking: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create MSI capability for storage devices."""
        if multi_message_capable is None:
            # Storage devices typically need more interrupts
            if self._device_category == "nvme":
                multi_message_capable = 5  # Up to 32 messages
            elif self._device_category in ["sas", "raid"]:
                multi_message_capable = 4  # Up to 16 messages
            else:
                multi_message_capable = 3  # Up to 8 messages
                
        return super()._create_msi_capability(multi_message_capable, supports_per_vector_masking)

    def _create_pcie_capability(
        self,
        max_payload_size: Optional[int] = None,
        supports_flr: bool = True,
    ) -> Dict[str, Any]:
        """Create PCIe Express capability for storage devices."""
        if max_payload_size is None:
            # Storage devices benefit from larger payloads
            if self._device_category == "nvme":
                max_payload_size = 512
            elif self._device_category in ["sas", "raid"]:
                max_payload_size = 256
            else:
                max_payload_size = 128
                
        return super()._create_pcie_capability(max_payload_size, supports_flr)

    def _calculate_default_queue_count(self) -> int:
        """Calculate appropriate queue count for storage devices."""
        base_queues = 2

        # Scale based on storage type
        if self._device_category == "nvme":
            base_queues = 64 if self.device_id > 0xA000 else 32
        elif self._device_category in ["sas", "raid"]:
            base_queues = 16 if self.device_id > 0x1500 else 8
        else:
            base_queues = 4

        # Add entropy-based variation for security
        entropy_factor = ((self.vendor_id ^ self.device_id) & 0xF) / 32.0
        variation = int(base_queues * entropy_factor * 0.5)
        if (self.device_id & 0x1) == 0:
            variation = -variation

        final_queues = max(1, base_queues + variation)
        return 1 << (final_queues - 1).bit_length()

    def _create_aer_capability(self) -> Dict[str, Any]:
        """Create Advanced Error Reporting capability."""
        return {
            "cap_id": self.AER_CAP_ID,
            "uncorrectable_error_mask": 0x00000000,
            "uncorrectable_error_severity": 0x00462030,
            "correctable_error_mask": 0x00002000,
            "advanced_error_capabilities": 0x00000020,
        }

    def generate_bar_configuration(self) -> List[Dict[str, Any]]:
        """Generate realistic BAR configuration for storage device."""
        bars = []

        # Base register space - size based on device type
        if self._device_category == "nvme":
            # NVMe controllers need larger register space
            base_size = 0x4000
            bars.append(
                {
                    "bar": 0,
                    "type": "memory",
                    "size": base_size,
                    "prefetchable": False,
                    "description": "NVMe registers",
                }
            )
        elif self._device_category in ["sas", "raid"]:
            # SAS/RAID controllers
            base_size = 0x8000
            bars.append(
                {
                    "bar": 0,
                    "type": "memory",
                    "size": base_size,
                    "prefetchable": False,
                    "description": "Controller registers",
                }
            )
            # Optional IO space for legacy compatibility
            bars.append(
                {
                    "bar": 1,
                    "type": "io",
                    "size": 0x100,
                    "prefetchable": False,
                    "description": "Legacy IO",
                }
            )
        else:
            # SATA/IDE controllers
            base_size = 0x2000
            bars.append(
                {
                    "bar": 0,
                    "type": "memory",
                    "size": base_size,
                    "prefetchable": False,
                    "description": "SATA registers",
                }
            )

        # MSI-X table space for devices that support it
        if 0x11 in self._capabilities:
            vector_count = self._calculate_default_queue_count()
            table_size = max(0x1000, (vector_count * 16 + 0xFFF) & ~0xFFF)
            
            bars.append(
                {
                    "bar": 2,
                    "type": "memory",
                    "size": table_size,
                    "prefetchable": False,
                    "description": "MSI-X table",
                }
            )

        return bars

    def generate_device_features(self) -> Dict[str, Any]:
        """Generate storage-specific device features."""
        features = {
            "category": self._device_category,
            "queue_count": self._calculate_default_queue_count(),
            "supports_ncq": True,
            "supports_trim": self._device_category in ["nvme", "sata"],
        }

        # Category-specific features
        if self._device_category == "nvme":
            features.update(
                {
                    "supports_namespace_management": self.device_id > 0xA000,
                    "max_namespaces": 256 if self.device_id > 0xA500 else 64,
                    "supports_nvme_mi": True,
                    "pci_gen": 4 if self.device_id > 0xA800 else 3,
                }
            )
        elif self._device_category in ["sas", "raid"]:
            features.update(
                {
                    "supports_raid_levels": [0, 1, 5, 6, 10],
                    "max_drives": 64 if self.device_id > 0x1500 else 16,
                    "supports_hot_swap": True,
                }
            )
        elif self._device_category == "sata":
            features.update(
                {
                    "max_ports": 8 if self.device_id > 0x2000 else 4,
                    "supports_port_multiplier": self.device_id > 0x1500,
                    "supports_fis_switching": True,
                }
            )

        # Advanced features for high-end devices
        if self._supports_aer():
            features["supports_aer"] = True

        return features


def create_storage_function_capabilities(
    vendor_id: int, device_id: int
) -> Dict[str, Any]:
    """
    Factory function to create storage function capabilities from build-time IDs.

    Args:
        vendor_id: PCI vendor ID from build process
        device_id: PCI device ID from build process

    Returns:
        Complete storage device configuration dictionary
    """
    return create_function_capabilities(
        StorageFunctionAnalyzer, vendor_id, device_id, "StorageFunctionAnalyzer"
    )
