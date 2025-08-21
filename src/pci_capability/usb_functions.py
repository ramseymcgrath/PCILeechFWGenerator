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

from ..string_utils import (log_debug_safe, log_error_safe, log_info_safe,
                            log_warning_safe, safe_format)
from .base_function_analyzer import (BaseFunctionAnalyzer,
                                     create_function_capabilities)
from .constants import CLASS_CODES

logger = logging.getLogger(__name__)


class USBFunctionAnalyzer(BaseFunctionAnalyzer):
    """
    Dynamic USB function capability analyzer.

    Analyzes vendor/device IDs provided at build time to generate realistic
    USB function capabilities without hardcoding device-specific behavior.
    """

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
        device_lower = self.device_id & 0xFF00
        device_upper = (self.device_id >> 8) & 0xFF

        # Vendor-specific patterns
        if self.vendor_id == 0x8086:  # Intel
            if device_lower in [0x1E00, 0x1F00, 0x8C00, 0x9C00]:
                return "xhci"
            elif device_lower in [0x2600, 0x2700]:
                return "ehci"
            elif device_lower in [0x2400, 0x2500]:
                return "uhci"
        elif self.vendor_id == 0x1002:  # AMD
            if device_lower in [0x7800, 0x7900]:
                return "xhci"
            elif device_lower in [0x7600, 0x7700]:
                return "ehci"
        elif self.vendor_id == 0x1033:  # NEC
            if device_lower in [0x0100, 0x0200]:
                return "xhci"
        elif self.vendor_id == 0x1106:  # VIA
            if device_lower in [0x3000, 0x3100]:
                return "uhci"

        # Generic patterns
        if device_upper >= 0x90:
            return "usb4" if device_upper >= 0xA0 else "xhci"
        elif device_upper >= 0x80:
            return "xhci"
        elif device_upper >= 0x60:
            return "ehci"
        elif device_upper >= 0x30:
            return "uhci"
        else:
            return "ohci"

    def _analyze_capabilities(self) -> Set[int]:
        caps = set()
        caps.update([0x01, 0x05, 0x10])  # PM, MSI, PCIe
        if self._supports_msix():
            caps.add(0x11)  # MSI-X
        return caps

    def _supports_msix(self) -> bool:
        return self._device_category in ["xhci", "usb4"] and self.device_id > 0x1000

    def get_device_class_code(self) -> int:
        """Get appropriate PCI class code for this device."""
        return CLASS_CODES.get(self._device_category, CLASS_CODES["xhci"])

    def _create_pm_capability(self, aux_current: int = 0) -> Dict[str, Any]:
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
        if multi_message_capable is None:
            if self._device_category in ["xhci", "usb4"]:
                multi_message_capable = 4
            else:
                multi_message_capable = 2

        return super()._create_msi_capability(
            multi_message_capable, supports_per_vector_masking
        )

    def _create_pcie_capability(
        self,
        max_payload_size: Optional[int] = None,
        supports_flr: bool = True,
    ) -> Dict[str, Any]:
        if max_payload_size is None:
            max_payload_size = 256
        return super()._create_pcie_capability(max_payload_size, supports_flr)

    def _calculate_default_queue_count(self) -> int:
        if self._device_category == "usb4":
            base_queues = 16
        elif self._device_category == "xhci":
            base_queues = 8
        elif self._device_category == "ehci":
            base_queues = 4
        else:
            base_queues = 2

        entropy_factor = ((self.vendor_id ^ self.device_id) & 0x7) / 16.0
        variation = int(base_queues * entropy_factor * 0.5)
        if (self.device_id & 0x1) == 0:
            variation = -variation

        final_queues = max(1, base_queues + variation)
        return 1 << (final_queues - 1).bit_length()

    def generate_bar_configuration(self) -> List[Dict[str, Any]]:
        bars = []
        if self._device_category in ["xhci", "usb4"]:
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
        features = {
            "category": self._device_category,
            "queue_count": self._calculate_default_queue_count(),
        }

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

        features["supports_power_management"] = True
        if self._device_category in ["xhci", "usb4"]:
            features["supports_runtime_pm"] = True

        return features


def create_usb_function_capabilities(vendor_id: int, device_id: int) -> Dict[str, Any]:
    return create_function_capabilities(
        USBFunctionAnalyzer, vendor_id, device_id, "USBFunctionAnalyzer"
    )
