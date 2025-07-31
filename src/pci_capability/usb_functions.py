#!/usr/bin/env python3
"""
USB Function Capabilities

This module provides dynamic USB function capabilities for PCIe device
generation. It analyzes build-time provided vendor/device IDs to generate
realistic USB controller capabilities without hardcoding.

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


class USBFunctionAnalyzer(BaseFunctionAnalyzer):
    """
    Dynamic USB function capability analyzer.

    Analyzes vendor/device IDs provided at build time to generate realistic
    USB function capabilities without hardcoding device-specific behavior.
    """

    # PCI class codes for USB devices
    CLASS_CODES = {
        "uhci": 0x0C0300,  # Serial bus controller, USB (UHCI)
        "ohci": 0x0C0310,  # Serial bus controller, USB (OHCI)
        "ehci": 0x0C0320,  # Serial bus controller, USB2 (EHCI)
        "xhci": 0x0C0330,  # Serial bus controller, USB3 (xHCI)
        "usb4": 0x0C0340,  # Serial bus controller, USB4
        "other_usb": 0x0C0380,  # Serial bus controller, USB (Other)
    }

    def __init__(self, vendor_id: int, device_id: int):
        """
        Initialize analyzer with build-time provided vendor/device IDs.

        Args:
            vendor_id: PCI vendor ID from build process
            device_id: PCI device ID from build process
        """
        super().__init__(vendor_id, device_id, "usb")

    def _analyze_device_category(self) -> str:
        """
        Analyze device category based on vendor/device ID patterns.

        Returns:
            Device category string (uhci, ohci, ehci, xhci, usb4, other_usb)
        """
        # Pattern-based analysis without hardcoding specific device IDs
        device_lower = self.device_id & 0xFF00
        device_upper = (self.device_id >> 8) & 0xFF

        # Vendor-specific patterns
        if self.vendor_id == 0x8086:  # Intel
            if device_lower in [0x1E00, 0x1F00, 0x8C00, 0x9C00]:  # xHCI ranges
                return "xhci"
            elif device_lower in [0x2600, 0x2700]:  # EHCI ranges
                return "ehci"
            elif device_lower in [0x2400, 0x2500]:  # UHCI ranges
                return "uhci"
        elif self.vendor_id == 0x1002:  # AMD
            if device_lower in [0x7800, 0x7900]:  # xHCI ranges
                return "xhci"
            elif device_lower in [0x7600, 0x7700]:  # EHCI ranges
                return "ehci"
        elif self.vendor_id == 0x1033:  # NEC
            if device_lower in [0x0100, 0x0200]:  # xHCI ranges
                return "xhci"
        elif self.vendor_id == 0x1106:  # VIA
            if device_lower in [0x3000, 0x3100]:  # UHCI/OHCI ranges
                return "uhci"

        # Generic patterns based on device ID structure
        if device_upper >= 0x90:  # Very high device IDs often USB4/xHCI
            return "usb4" if device_upper >= 0xA0 else "xhci"
        elif device_upper >= 0x80:  # High device IDs often xHCI
            return "xhci"
        elif device_upper >= 0x60:  # Mid-high often EHCI
            return "ehci"
        elif device_upper >= 0x30:  # Mid often UHCI
            return "uhci"
        else:
            return "ohci"  # Low device IDs often OHCI

    def _analyze_capabilities(self) -> Set[int]:
        """
        Analyze which capabilities this device should support.

        Returns:
            Set of capability IDs that should be present
        """
        caps = set()

        # Always include basic USB capabilities
        caps.update([0x01, 0x05, 0x10])  # PM, MSI, PCIe

        # MSI-X for modern controllers
        if self._supports_msix():
            caps.add(0x11)  # MSI-X

        return caps

    def _supports_msix(self) -> bool:
        """Check if USB controller supports MSI-X."""
        # Modern xHCI and USB4 controllers support MSI-X
        return self._device_category in ["xhci", "usb4"] and self.device_id > 0x1000

    def get_device_class_code(self) -> int:
        """Get appropriate PCI class code for this device."""
        return self.CLASS_CODES.get(self._device_category, self.CLASS_CODES["xhci"])

    def _create_pm_capability(self, aux_current: int = 0) -> Dict[str, Any]:
        """Create Power Management capability for USB devices."""
        # Modern controllers may need more aux power
        if self._device_category in ["xhci", "usb4"]:
            aux_current = 200
        else:
            aux_current = 100
        return super()._create_pm_capability(aux_current)

    def _create_msi_capability(
        self,
        multi_message_capable: Optional[int] = None,
        supports_per_vector_masking: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create MSI capability for USB devices."""
        if multi_message_capable is None:
            # USB controllers typically need multiple interrupts
            if self._device_category in ["xhci", "usb4"]:
                multi_message_capable = 4  # Up to 16 messages
            else:
                multi_message_capable = 2  # Up to 4 messages
                
        return super()._create_msi_capability(multi_message_capable, supports_per_vector_masking)

    def _create_pcie_capability(
        self,
        max_payload_size: Optional[int] = None,
        supports_flr: bool = True,
    ) -> Dict[str, Any]:
        """Create PCIe Express capability for USB devices."""
        if max_payload_size is None:
            # USB controllers don't need large payloads
            max_payload_size = 256
            
        return super()._create_pcie_capability(max_payload_size, supports_flr)

    def _calculate_default_queue_count(self) -> int:
        """Calculate appropriate queue count for USB devices."""
        # USB controllers need queues for each port and endpoint
        if self._device_category == "usb4":
            base_queues = 16
        elif self._device_category == "xhci":
            base_queues = 8
        elif self._device_category == "ehci":
            base_queues = 4
        else:
            base_queues = 2

        # Add entropy-based variation for security
        entropy_factor = ((self.vendor_id ^ self.device_id) & 0x7) / 16.0
        variation = int(base_queues * entropy_factor * 0.5)
        if (self.device_id & 0x1) == 0:
            variation = -variation

        final_queues = max(1, base_queues + variation)
        return 1 << (final_queues - 1).bit_length()

    def generate_bar_configuration(self) -> List[Dict[str, Any]]:
        """Generate realistic BAR configuration for USB device."""
        bars = []

        # Base register space - size based on controller type
        if self._device_category in ["xhci", "usb4"]:
            # xHCI/USB4 controllers need larger register space
            base_size = 0x10000
            bars.append(
                {
                    "bar": 0,
                    "type": "memory",
                    "size": base_size,
                    "prefetchable": False,
                    "description": "xHCI registers",
                }
            )
            
            # MSI-X table space if supported
            if 0x11 in self._capabilities:
                bars.append(
                    {
                        "bar": 1,
                        "type": "memory",
                        "size": 0x1000,
                        "prefetchable": False,
                        "description": "MSI-X table",
                    }
                )
        elif self._device_category == "ehci":
            # EHCI controllers
            base_size = 0x1000
            bars.append(
                {
                    "bar": 0,
                    "type": "memory",
                    "size": base_size,
                    "prefetchable": False,
                    "description": "EHCI registers",
                }
            )
        else:
            # UHCI/OHCI controllers (legacy)
            bars.append(
                {
                    "bar": 0,
                    "type": "io",
                    "size": 0x20,
                    "prefetchable": False,
                    "description": "USB IO ports",
                }
            )

        return bars

    def generate_device_features(self) -> Dict[str, Any]:
        """Generate USB-specific device features."""
        features = {
            "category": self._device_category,
            "queue_count": self._calculate_default_queue_count(),
        }

        # Category-specific features
        if self._device_category == "usb4":
            features.update(
                {
                    "usb_version": "4.0",
                    "max_speed": "40Gbps",
                    "port_count": 2,
                    "supports_thunderbolt": True,
                    "supports_display_port": True,
                    "supports_pcie_tunneling": True,
                }
            )
        elif self._device_category == "xhci":
            features.update(
                {
                    "usb_version": "3.1" if self.device_id > 0x8000 else "3.0",
                    "max_speed": "10Gbps" if self.device_id > 0x8000 else "5Gbps",
                    "port_count": 8 if self.device_id > 0x1500 else 4,
                    "supports_streams": True,
                    "supports_lpm": True,
                }
            )
        elif self._device_category == "ehci":
            features.update(
                {
                    "usb_version": "2.0",
                    "max_speed": "480Mbps",
                    "port_count": 8 if self.device_id > 0x2600 else 4,
                    "supports_tt": True,
                }
            )
        elif self._device_category == "uhci":
            features.update(
                {
                    "usb_version": "1.1",
                    "max_speed": "12Mbps",
                    "port_count": 2,
                    "supports_legacy": True,
                }
            )
        elif self._device_category == "ohci":
            features.update(
                {
                    "usb_version": "1.1",
                    "max_speed": "12Mbps",
                    "port_count": 4,
                    "supports_isochronous": True,
                }
            )

        # Power management features
        features["supports_power_management"] = True
        if self._device_category in ["xhci", "usb4"]:
            features["supports_runtime_pm"] = True

        return features


def create_usb_function_capabilities(vendor_id: int, device_id: int) -> Dict[str, Any]:
    """
    Factory function to create USB function capabilities from build-time IDs.

    Args:
        vendor_id: PCI vendor ID from build process
        device_id: PCI device ID from build process

    Returns:
        Complete USB device configuration dictionary
    """
    return create_function_capabilities(
        USBFunctionAnalyzer, vendor_id, device_id, "USBFunctionAnalyzer"
    )
