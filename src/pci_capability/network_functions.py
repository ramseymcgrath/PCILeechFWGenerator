#!/usr/bin/env python3
"""
Network Function Capabilities

This module provides dynamic network function capabilities for PCIe device
generation. It analyzes build-time provided vendor/device IDs to generate
realistic network and media function capabilities without hardcoding.

The module integrates with the existing templating and logging infrastructure to
provide production-ready dynamic capability generation.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from .base_function_analyzer import (BaseFunctionAnalyzer,
                                     create_function_capabilities)

try:
    from ..string_utils import (log_debug_safe, log_error_safe, log_info_safe,
                                log_warning_safe, safe_format)
except ImportError:
    import sys
    from pathlib import Path

    src_dir = Path(__file__).parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from ..string_utils import (log_debug_safe, log_error_safe, log_info_safe,
                                log_warning_safe, safe_format)

logger = logging.getLogger(__name__)


class NetworkFunctionAnalyzer(BaseFunctionAnalyzer):
    """
    Dynamic network function capability analyzer.

    Analyzes vendor/device IDs provided at build time to generate realistic
    network function capabilities without hardcoding device-specific behavior.
    """

    # Network-specific capability IDs
    SRIOV_CAP_ID = 0x0010  # SR-IOV
    ACS_CAP_ID = 0x000D  # Access Control Services
    LTR_CAP_ID = 0x0018  # Latency Tolerance Reporting
    PTM_CAP_ID = 0x001F  # Precision Time Measurement
    ARI_CAP_ID = 0x000E  # Alternative Routing-ID Interpretation

    # PCI class codes for network devices
    CLASS_CODES = {
        "ethernet": 0x020000,
        "wifi": 0x028000,
        "bluetooth": 0x0D1100,
        "cellular": 0x028000,
    }

    def __init__(self, vendor_id: int, device_id: int):
        """
        Initialize analyzer with build-time provided vendor/device IDs.

        Args:
            vendor_id: PCI vendor ID from build process
            device_id: PCI device ID from build process
        """
        super().__init__(vendor_id, device_id, "network")

    def _analyze_device_category(self) -> str:
        """
        Analyze device category based on vendor/device ID patterns.

        Returns:
            Device category string (ethernet, wifi, bluetooth, cellular, unknown)
        """
        # Pattern-based analysis without hardcoding specific device IDs
        device_lower = self.device_id & 0xFF00
        device_upper = (self.device_id >> 8) & 0xFF

        # Vendor-specific patterns
        if self.vendor_id == 0x8086:  # Intel
            # Intel network device ID patterns
            if device_lower in [0x1500, 0x1600, 0x1700]:  # Ethernet ranges
                return "ethernet"
            elif device_lower in [0x2400, 0x2500, 0x2700, 0x5100]:  # WiFi ranges
                return "wifi"
        elif self.vendor_id == 0x10EC:  # Realtek
            if device_lower in [0x8100, 0x8200]:  # Ethernet ranges
                return "ethernet"
        elif self.vendor_id == 0x14E4:  # Broadcom
            if device_lower in [0x1600, 0x1700]:  # Ethernet ranges
                return "ethernet"
        elif self.vendor_id == 0x17CB:  # Qualcomm Atheros
            if device_lower in [0x1100]:  # WiFi ranges
                return "wifi"

        # Generic patterns based on device ID structure
        if device_upper >= 0x80:  # Higher device IDs often indicate advanced features
            return "ethernet"
        elif device_upper >= 0x20:
            return "wifi"

        return "ethernet"  # Default fallback

    def _analyze_capabilities(self) -> Set[int]:
        """
        Analyze which capabilities this device should support.

        Returns:
            Set of capability IDs that should be present
        """
        caps = set()

        # Always include basic network capabilities
        caps.update([0x01, 0x05, 0x10, 0x11])  # PM, MSI, PCIe, MSI-X

        # Advanced capabilities based on device analysis
        if self._supports_sriov():
            caps.add(self.SRIOV_CAP_ID)
            # Add ACS/ARI with device-specific variation for security
            if (self.device_id & 0x3) != 0:  # 75% chance based on device ID bits
                caps.add(self.ACS_CAP_ID)
            if (self.vendor_id & 0x1) == 0:  # 50% chance based on vendor ID bit
                caps.add(self.ARI_CAP_ID)

        if self._supports_ltr():
            caps.add(self.LTR_CAP_ID)

        if self._supports_ptm():
            caps.add(self.PTM_CAP_ID)

        return caps

    def _supports_sriov(self) -> bool:
        """Check if device likely supports SR-IOV based on patterns."""
        # High-end devices (higher device IDs) more likely to support SR-IOV
        if self.device_id > 0x1500 and self._device_category == "ethernet":
            # Check for enterprise/datacenter patterns
            if self.vendor_id == 0x8086 and (self.device_id & 0x0F00) >= 0x0500:
                return True
            elif self.vendor_id == 0x14E4 and (self.device_id & 0x00F0) >= 0x0080:
                return True
        return False

    def _supports_ltr(self) -> bool:
        """Check if device likely supports LTR."""
        # Most modern network devices support LTR
        return self.device_id > 0x1000

    def _supports_ptm(self) -> bool:
        """Check if device likely supports PTM."""
        # PTM mainly for high-speed Ethernet
        return (
            self._device_category == "ethernet"
            and self.device_id > 0x1500
            and self._supports_sriov()
        )

    def get_device_class_code(self) -> int:
        """Get appropriate PCI class code for this device."""
        return self.CLASS_CODES.get(self._device_category, self.CLASS_CODES["ethernet"])

    def _create_capability_by_id(self, cap_id: int) -> Optional[Dict[str, Any]]:
        """Override base class to handle network-specific capabilities and parameters."""
        # Handle network-specific capabilities
        if cap_id == self.SRIOV_CAP_ID:
            return self._create_sriov_capability()
        elif cap_id == self.ACS_CAP_ID:
            return self._create_acs_capability()
        elif cap_id == self.LTR_CAP_ID:
            return self._create_ltr_capability()
        elif cap_id == self.PTM_CAP_ID:
            return self._create_ptm_capability()
        elif cap_id == self.ARI_CAP_ID:
            return self._create_ari_capability()

        # Use base class for common capabilities with network-specific parameters
        if cap_id == self.PM_CAP_ID:
            return self._create_pm_capability(
                aux_current=0
            )  # Network devices don't need aux power
        elif cap_id == self.MSI_CAP_ID:
            queue_count = self._calculate_network_queue_count()
            return self._create_msi_capability(
                multi_message_capable=min(5, queue_count.bit_length()),
                supports_per_vector_masking=self.device_id > 0x1000,
            )
        elif cap_id == self.PCIE_CAP_ID:
            max_payload = 512 if self.device_id > 0x1500 else 256
            return self._create_pcie_capability(
                max_payload_size=max_payload, supports_flr=True
            )
        elif cap_id == self.MSIX_CAP_ID:
            table_bar, pba_bar = self._get_network_msix_bars()
            return self._create_msix_capability(
                table_size=self._calculate_network_queue_count(),
                table_bar=table_bar,
                pba_bar=pba_bar,
            )

        return None

    def _get_network_msix_bars(self) -> Tuple[int, int]:
        """Get network-specific MSI-X BAR allocation with entropy for uniqueness."""
        # Network devices typically use BAR 1 for MSI-X
        # Add device-specific variation for security against firmware fingerprinting
        if (self.device_id & 0x0F) >= 8:  # Use low nibble for variation
            return (0, 0)  # Some devices use BAR 0
        else:
            return (1, 1)  # Most use BAR 1

    def _get_default_msix_bar_allocation(self) -> Tuple[int, int]:
        """Override base class for network-specific MSI-X allocation."""
        return self._get_network_msix_bars()

    def _calculate_network_queue_count(self) -> int:
        """Calculate network-specific queue count with entropy."""
        base_queues = 4

        # Scale based on device ID (higher = more capable)
        if self.device_id > 0x2000:
            base_queues = 64
        elif self.device_id > 0x1500:
            base_queues = 32
        elif self.device_id > 0x1000:
            base_queues = 16

        # Adjust for device category
        if self._device_category == "wifi":
            base_queues = min(base_queues, 16)  # WiFi typically has fewer queues
        elif self._device_category == "ethernet" and self._supports_sriov():
            base_queues = max(base_queues, 32)  # SR-IOV devices need more queues

        # Add entropy-based variation for security (±25% based on ID bits)
        entropy_factor = ((self.vendor_id ^ self.device_id) & 0xF) / 32.0  # 0 to ~0.47
        variation = int(base_queues * entropy_factor * 0.5)  # ±25% max
        if (self.device_id & 0x1) == 0:
            variation = -variation

        final_queues = max(1, base_queues + variation)
        # Ensure power of 2 for realistic hardware
        return 1 << (final_queues - 1).bit_length()

    def _calculate_default_queue_count(self) -> int:
        """Override base class to use network-specific calculation."""
        return self._calculate_network_queue_count()

    def generate_bar_configuration(self) -> List[Dict[str, Any]]:
        """Generate realistic BAR configuration for network device."""
        bars = []

        # Base register space - size based on device complexity with entropy
        base_size = 0x10000 if self.device_id < 0x1500 else 0x20000
        # Add device-specific size variation for security
        size_variation = (self.device_id & 0xF) * 0x1000  # 0-60KB variation
        base_size += size_variation

        bars.append(
            {
                "bar": 0,
                "type": "memory",
                "size": base_size,
                "prefetchable": False,
                "description": "Device registers",
            }
        )

        # MSI-X table space with dynamic sizing
        if 0x11 in self._capabilities:
            # Vary MSI-X table BAR size based on vector count and device entropy
            vector_count = self._calculate_network_queue_count()
            table_size = max(
                0x1000, (vector_count * 16 + 0xFFF) & ~0xFFF
            )  # Round up to 4KB
            # Add entropy-based padding for uniqueness
            size_padding = ((self.vendor_id ^ self.device_id) & 0x7) * 0x1000
            table_size += size_padding

            bars.append(
                {
                    "bar": 1,
                    "type": "memory",
                    "size": table_size,
                    "prefetchable": False,
                    "description": "MSI-X table",
                }
            )

        # Flash/EEPROM space for Ethernet
        if self._device_category == "ethernet":
            bars.append(
                {
                    "bar": 2,
                    "type": "memory",
                    "size": 0x4000,
                    "prefetchable": False,
                    "description": "Flash/EEPROM",
                }
            )

        # Additional register space for WiFi
        elif self._device_category == "wifi":
            bars.append(
                {
                    "bar": 2,
                    "type": "memory",
                    "size": 0x100000,
                    "prefetchable": False,
                    "description": "WiFi registers",
                }
            )

        return bars

    def generate_device_features(self) -> Dict[str, Any]:
        """Generate network-specific device features."""
        features = {
            "category": self._device_category,
            "queue_count": self._calculate_network_queue_count(),
            "supports_rss": True,
            "supports_tso": True,
            "supports_checksum_offload": True,
            "supports_vlan": True,
        }

        # Category-specific features
        if self._device_category == "ethernet":
            features.update(
                {
                    "supports_jumbo_frames": self.device_id > 0x1200,
                    "supports_flow_control": True,
                    "max_link_speed": self._estimate_link_speed(),
                }
            )
        elif self._device_category == "wifi":
            features.update(
                {
                    "supports_mimo": True,
                    "max_spatial_streams": self._estimate_spatial_streams(),
                    "supported_bands": self._estimate_wifi_bands(),
                }
            )

        # Advanced features for high-end devices
        if self._supports_sriov():
            features["supports_sriov"] = True
            features["max_vfs"] = self._calculate_max_vfs()

        return features

    def _create_sriov_capability(self) -> Dict[str, Any]:
        """Create SR-IOV capability."""
        max_vfs = self._calculate_max_vfs()
        return {
            "cap_id": self.SRIOV_CAP_ID,
            "initial_vfs": max_vfs,
            "total_vfs": max_vfs,
            "num_vf_bars": 6,
            "vf_device_id": self.device_id
            + 1,  # VF typically has incremented device ID
            "supported_page_sizes": 0x553,  # Common page sizes
            "system_page_size": 0x1,
        }

    def _create_acs_capability(self) -> Dict[str, Any]:
        """Create Access Control Services capability."""
        return {
            "cap_id": self.ACS_CAP_ID,
            "source_validation": True,
            "translation_blocking": True,
            "p2p_request_redirect": True,
            "p2p_completion_redirect": True,
            "upstream_forwarding": True,
        }

    def _create_ltr_capability(self) -> Dict[str, Any]:
        """Create Latency Tolerance Reporting capability."""
        # Calculate realistic latency values based on device type
        base_latency = 0x1003 if self._device_category == "wifi" else 0x1001
        return {
            "cap_id": self.LTR_CAP_ID,
            "max_snoop_latency": base_latency,
            "max_no_snoop_latency": base_latency,
        }

    def _create_ptm_capability(self) -> Dict[str, Any]:
        """Create Precision Time Measurement capability."""
        return {
            "cap_id": self.PTM_CAP_ID,
            "ptm_requester_capable": True,
            "ptm_responder_capable": True,
            "ptm_root_capable": False,
            "local_clock_granularity": 0xFF,  # 255ns
        }

    def _create_ari_capability(self) -> Dict[str, Any]:
        """Create Alternative Routing-ID Interpretation capability."""
        return {
            "cap_id": self.ARI_CAP_ID,
            "mfvc_function_groups_capability": False,
            "acs_function_groups_capability": False,
            "next_function_number": 0,
        }

    def _calculate_max_vfs(self) -> int:
        """Calculate maximum VFs for SR-IOV devices."""
        if not self._supports_sriov():
            return 0

        # Base VF count on device capability with entropy
        base_vfs = 8
        if self.device_id > 0x1700:
            base_vfs = 64
        elif self.device_id > 0x1500:
            base_vfs = 32

        # Add device-specific variation for uniqueness
        variation = (self.device_id & 0x7) - 4  # -4 to +3 variation
        return max(1, base_vfs + variation)

    def _estimate_link_speed(self) -> str:
        """Estimate link speed for Ethernet devices."""
        if self.device_id > 0x1700:
            return "25Gbps"
        elif self.device_id > 0x1500:
            return "10Gbps"
        elif self.device_id > 0x1200:
            return "1Gbps"
        else:
            return "100Mbps"

    def _estimate_spatial_streams(self) -> int:
        """Estimate spatial streams for WiFi devices."""
        if self.device_id > 0x2700:
            return 8
        elif self.device_id > 0x2400:
            return 4
        else:
            return 2

    def _estimate_wifi_bands(self) -> List[str]:
        """Estimate supported WiFi bands."""
        bands = ["2.4GHz"]

        if self.device_id > 0x2000:
            bands.append("5GHz")
        if self.device_id > 0x2500:
            bands.append("6GHz")

        return bands


def create_network_function_capabilities(
    vendor_id: int, device_id: int
) -> Dict[str, Any]:
    """
    Factory function to create network function capabilities from build-time IDs.

    Args:
        vendor_id: PCI vendor ID from build process
        device_id: PCI device ID from build process

    Returns:
        Complete network device configuration dictionary
    """
    return create_function_capabilities(
        NetworkFunctionAnalyzer, vendor_id, device_id, "NetworkFunctionAnalyzer"
    )
