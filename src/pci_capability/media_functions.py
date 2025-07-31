#!/usr/bin/env python3
"""
Media Function Capabilities

This module provides dynamic media function capabilities for PCIe device
generation. It analyzes build-time provided vendor/device IDs to generate
realistic audio, video, and multimedia function capabilities without hardcoding.

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


class MediaFunctionAnalyzer(BaseFunctionAnalyzer):
    """
    Dynamic media function capability analyzer.

    Analyzes vendor/device IDs provided at build time to generate realistic
    media function capabilities without hardcoding device-specific behavior.
    """

    # Media-specific capability IDs
    VENDOR_CAP_ID = 0x09  # Vendor-specific capability

    # PCI class codes for media devices
    CLASS_CODES = {
        "audio": 0x040100,  # Multimedia controller, Audio device
        "video": 0x040000,  # Multimedia controller, Video
        "hdaudio": 0x040300,  # Multimedia controller, HD Audio
        "other_media": 0x040800,  # Multimedia controller, Other
    }

    def __init__(self, vendor_id: int, device_id: int):
        """
        Initialize analyzer with build-time provided vendor/device IDs.

        Args:
            vendor_id: PCI vendor ID from build process
            device_id: PCI device ID from build process
        """
        super().__init__(vendor_id, device_id, "media")

    def _analyze_device_category(self) -> str:
        """
        Analyze device category based on vendor/device ID patterns.

        Returns:
            Device category string (audio, video, hdaudio, other_media)
        """
        # Pattern-based analysis without hardcoding specific device IDs
        device_lower = self.device_id & 0xFF00
        device_upper = (self.device_id >> 8) & 0xFF

        # Vendor-specific patterns
        if self.vendor_id == 0x8086:  # Intel
            if device_lower in [0x2600, 0x2700, 0x2800]:  # HD Audio ranges
                return "hdaudio"
            elif device_lower in [0x5900, 0x5A00]:  # Video ranges
                return "video"
        elif self.vendor_id == 0x10DE:  # NVIDIA
            if device_lower in [0x0E00, 0x0F00]:  # Audio over HDMI
                return "hdaudio"
            elif device_lower in [0x1000, 0x1100]:  # Video capture
                return "video"
        elif self.vendor_id == 0x1002:  # AMD/ATI
            if device_lower in [0xAA00, 0xAB00]:  # Audio
                return "hdaudio"
        elif self.vendor_id == 0x13F6:  # C-Media
            return "audio"
        elif self.vendor_id == 0x1274:  # Creative Labs
            return "audio"

        # Generic patterns based on device ID structure
        if device_upper >= 0x80:  # Higher device IDs often HD Audio
            return "hdaudio"
        elif device_upper >= 0x50:  # Mid-range often video
            return "video"
        else:
            return "audio"  # Default to basic audio

    def _analyze_capabilities(self) -> Set[int]:
        """
        Analyze which capabilities this device should support.

        Returns:
            Set of capability IDs that should be present
        """
        caps = set()

        # Always include basic media capabilities
        caps.update([0x01, 0x05, 0x10])  # PM, MSI, PCIe

        # MSI-X for high-end devices
        if self._is_high_end_device():
            caps.add(0x11)  # MSI-X

        # Vendor-specific capabilities for certain devices
        if self._supports_vendor_capability():
            caps.add(self.VENDOR_CAP_ID)

        return caps

    def _is_high_end_device(self) -> bool:
        """Check if this is a high-end media device."""
        return (
            self._device_category in ["hdaudio", "video"]
            and self.device_id > 0x2000
        )

    def _supports_vendor_capability(self) -> bool:
        """Check if device supports vendor-specific capabilities."""
        # Vendor caps common in audio devices for DSP features
        return self._device_category in ["audio", "hdaudio"] and self.device_id > 0x1000

    def get_device_class_code(self) -> int:
        """Get appropriate PCI class code for this device."""
        return self.CLASS_CODES.get(self._device_category, self.CLASS_CODES["audio"])

    def _create_capability_by_id(self, cap_id: int) -> Optional[Dict[str, Any]]:
        """Create capability by ID, handling media-specific capabilities."""
        # Try base class capabilities first
        capability = super()._create_capability_by_id(cap_id)
        if capability:
            return capability
            
        # Handle media-specific capabilities
        if cap_id == self.VENDOR_CAP_ID:
            return self._create_vendor_capability()
        else:
            return None

    def _create_pm_capability(self, aux_current: int = 0) -> Dict[str, Any]:
        """Create Power Management capability for media devices."""
        # HD Audio may need aux power for always-on features
        aux_current = 50 if self._device_category == "hdaudio" else 0
        return super()._create_pm_capability(aux_current)

    def _create_msi_capability(
        self,
        multi_message_capable: Optional[int] = None,
        supports_per_vector_masking: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create MSI capability for media devices."""
        if multi_message_capable is None:
            # Most media devices need only single MSI
            multi_message_capable = 1 if not self._is_high_end_device() else 2
            
        return super()._create_msi_capability(multi_message_capable, supports_per_vector_masking)

    def _create_pcie_capability(
        self,
        max_payload_size: Optional[int] = None,
        supports_flr: bool = True,
    ) -> Dict[str, Any]:
        """Create PCIe Express capability for media devices."""
        if max_payload_size is None:
            # Conservative payload size for media devices
            max_payload_size = 128
            
        # HD Audio benefits from FLR
        supports_flr = self._device_category == "hdaudio"
        return super()._create_pcie_capability(max_payload_size, supports_flr)

    def _get_default_msix_bar_allocation(self) -> tuple[int, int]:
        """Get appropriate BAR allocation for MSI-X tables."""
        if self._device_category == "hdaudio":
            return (1, 1)  # HD Audio: Use BAR 1 for MSI-X
        else:
            return (0, 0)  # Other media: Use BAR 0

    def _calculate_default_queue_count(self) -> int:
        """Calculate appropriate queue count for media devices."""
        # Media devices typically need fewer queues
        if self._device_category == "hdaudio":
            base_queues = 8 if self.device_id > 0x2500 else 4
        elif self._device_category == "video":
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

    def _create_vendor_capability(self) -> Dict[str, Any]:
        """Create vendor-specific capability for media devices."""
        return {
            "cap_id": self.VENDOR_CAP_ID,
            "vendor_id": self.vendor_id,
            "length": 16,  # Basic vendor capability
            "vendor_data": f"MediaDSP_{self.device_id:04x}",
        }

    def generate_bar_configuration(self) -> List[Dict[str, Any]]:
        """Generate realistic BAR configuration for media device."""
        bars = []

        # Base register space - size based on device type
        if self._device_category == "hdaudio":
            # HD Audio needs larger register space
            base_size = 0x4000
            bars.append(
                {
                    "bar": 0,
                    "type": "memory",
                    "size": base_size,
                    "prefetchable": False,
                    "description": "HD Audio registers",
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
        elif self._device_category == "video":
            # Video devices need frame buffer space
            base_size = 0x10000
            bars.append(
                {
                    "bar": 0,
                    "type": "memory",
                    "size": base_size,
                    "prefetchable": True,
                    "description": "Video frame buffer",
                }
            )
            bars.append(
                {
                    "bar": 1,
                    "type": "memory",
                    "size": 0x2000,
                    "prefetchable": False,
                    "description": "Video registers",
                }
            )
        else:
            # Basic audio device
            base_size = 0x1000
            bars.append(
                {
                    "bar": 0,
                    "type": "memory",
                    "size": base_size,
                    "prefetchable": False,
                    "description": "Audio registers",
                }
            )

        return bars

    def generate_device_features(self) -> Dict[str, Any]:
        """Generate media-specific device features."""
        features = {
            "category": self._device_category,
            "queue_count": self._calculate_default_queue_count(),
        }

        # Category-specific features
        if self._device_category == "hdaudio":
            features.update(
                {
                    "codec_support": ["AC97", "HDA"],
                    "sample_rates": [44100, 48000, 96000, 192000],
                    "bit_depths": [16, 20, 24, 32],
                    "channels": 8 if self.device_id > 0x2500 else 2,
                    "supports_dsp": self._supports_vendor_capability(),
                }
            )
        elif self._device_category == "video":
            features.update(
                {
                    "max_resolution": "4K" if self.device_id > 0x2000 else "1080p",
                    "color_formats": ["RGB", "YUV420", "YUV422"],
                    "frame_rates": [30, 60] if self.device_id > 0x1500 else [30],
                    "supports_hardware_encoding": self.device_id > 0x2500,
                }
            )
        elif self._device_category == "audio":
            features.update(
                {
                    "codec_support": ["AC97"],
                    "sample_rates": [44100, 48000],
                    "bit_depths": [16],
                    "channels": 2,
                    "supports_midi": True,
                }
            )

        # High-end features
        if self._is_high_end_device():
            features["supports_advanced_features"] = True

        return features


def create_media_function_capabilities(
    vendor_id: int, device_id: int
) -> Dict[str, Any]:
    """
    Factory function to create media function capabilities from build-time IDs.

    Args:
        vendor_id: PCI vendor ID from build process
        device_id: PCI device ID from build process

    Returns:
        Complete media device configuration dictionary
    """
    return create_function_capabilities(
        MediaFunctionAnalyzer, vendor_id, device_id, "MediaFunctionAnalyzer"
    )
