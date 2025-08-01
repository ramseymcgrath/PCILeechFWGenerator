#!/usr/bin/env python3
"""
Dynamic Function Capabilities

This module provides a unified interface for generating realistic PCIe device
capabilities based on build-time provided vendor/device IDs. It integrates
network and media function analyzers to provide comprehensive device generation.

The module integrates with the existing templating and logging infrastructure
to provide production-ready dynamic capability generation.
"""

import logging
from typing import Any, Dict, Optional

from .media_functions import create_media_function_capabilities
from .network_functions import create_network_function_capabilities
from .storage_functions import create_storage_function_capabilities
from .usb_functions import create_usb_function_capabilities

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


def analyze_device_function_type(
    vendor_id: int, device_id: int, class_code: Optional[int] = None
) -> str:
    """
    Analyze device function type based on vendor/device ID and optional class code.

    Args:
        vendor_id: PCI vendor ID from build process
        device_id: PCI device ID from build process
        class_code: Optional PCI class code for additional context

    Returns:
        Device function type string ('network', 'media', 'storage', 'usb', 'unknown')
    """
    # Use class code if provided for primary classification
    if class_code is not None:
        class_major = (class_code >> 16) & 0xFF
        class_minor = (class_code >> 8) & 0xFF
        if class_major == 0x02:  # Network controller
            return "network"
        elif class_major == 0x04:  # Multimedia controller
            return "media"
        elif class_major == 0x01:  # Mass storage controller
            return "storage"
        elif class_major == 0x0C:  # Serial bus controller
            if class_minor == 0x03:  # USB controller
                return "usb"
            elif class_minor == 0x80:  # Serial bus, other (often network)
                return "network"

    # Fallback to vendor/device ID pattern analysis
    device_upper = (device_id >> 8) & 0xFF
    device_lower = device_id & 0xFF

    # Vendor-specific patterns
    if vendor_id == 0x8086:  # Intel
        # Intel network ranges
        if device_upper in [0x15, 0x16, 0x17, 0x24, 0x25, 0x27, 0x51]:
            return "network"
        # Intel audio ranges
        elif device_upper in [0x0C, 0x0E, 0x0F, 0x1C, 0x1E, 0x1F, 0x22, 0x27, 0x29]:
            return "media"
        # Intel storage ranges
        elif device_upper in [0x02, 0x06, 0x0F, 0x28, 0x29, 0x31]:
            return "storage"
        # Intel USB ranges
        elif device_upper in [0x0F, 0x1E, 0x1F, 0x31, 0x34, 0x43, 0x51, 0x54]:
            return "usb"
    elif vendor_id == 0x10EC:  # Realtek
        if device_upper == 0x81:  # Realtek network
            return "network"
        elif device_upper == 0x52:  # Realtek NVMe
            return "storage"
        elif device_lower < 0x80:  # Realtek audio
            return "media"
    elif vendor_id == 0x14E4:  # Broadcom
        if device_upper in [0x16, 0x17]:  # Broadcom network
            return "network"
    elif vendor_id == 0x17CB:  # Qualcomm Atheros
        return "network"  # Primarily network devices
    elif vendor_id == 0x10DE:  # NVIDIA
        if device_upper >= 0x0A:  # NVIDIA USB/media
            return "media" if device_upper >= 0x40 else "usb"
        return "media"  # Primarily graphics/media
    elif vendor_id == 0x1002:  # AMD/ATI
        if device_upper >= 0x43:  # Modern AMD may have USB
            return "usb" if device_lower < 0x50 else "media"
        return "media"  # Primarily graphics/media
    elif vendor_id in [0x1412, 0xC003]:  # VIA, C-Media
        return "media"  # Audio vendors
    elif vendor_id == 0x1B4B:  # Marvell
        return "storage"  # Known for storage controllers
    elif vendor_id == 0x1000:  # LSI/Broadcom
        return "storage"  # RAID/SAS controllers
    elif vendor_id in [0x144D, 0x15B7, 0x1344]:  # Samsung, SanDisk, Micron
        return "storage"  # NVMe vendors
    elif vendor_id in [0x1033, 0x1912, 0x15E7]:  # NEC, Renesas, Etron
        return "usb"  # USB controller vendors
    elif vendor_id == 0x1106:  # VIA
        if device_upper >= 0x31:
            return "usb"
        return "storage"

    # Generic patterns
    if device_upper >= 0x80:  # Very high device IDs
        # Could be NVMe storage or advanced USB
        return "storage" if device_lower >= 0xA0 else "usb"
    elif device_upper >= 0x50:  # High device IDs
        return "storage"  # Often storage controllers
    elif device_upper >= 0x15:  # Mid-high device IDs often network
        return "network"
    elif device_lower < 0x50:  # Lower device IDs often media
        return "media"

    return "unknown"


def create_dynamic_device_capabilities(
    vendor_id: int,
    device_id: int,
    class_code: Optional[int] = None,
    function_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create dynamic device capabilities based on build-time provided IDs.

    This is the main entry point for generating realistic PCIe device capabilities
    during the build process. It analyzes the provided vendor/device IDs and
    generates appropriate capabilities without hardcoding.

    Args:
        vendor_id: PCI vendor ID from build process
        device_id: PCI device ID from build process
        class_code: Optional PCI class code for classification hints
        function_hint: Optional function type hint ('network', 'media', 'storage', 'usb', 'auto')

    Returns:
        Complete device configuration dictionary with capabilities, BARs, and features
    """
    try:
        # Determine function type
        if function_hint and function_hint in ["network", "media", "storage", "usb"]:
            function_type = function_hint
            log_debug_safe(
                logger,
                safe_format(
                    "Using provided function hint: {hint} for device {vendor_id:04x}:{device_id:04x}",
                    hint=function_hint,
                    vendor_id=vendor_id,
                    device_id=device_id,
                ),
            )
        else:
            function_type = analyze_device_function_type(
                vendor_id, device_id, class_code
            )
            log_debug_safe(
                logger,
                safe_format(
                    "Analyzed device {vendor_id:04x}:{device_id:04x} as function type: {function_type}",
                    vendor_id=vendor_id,
                    device_id=device_id,
                    function_type=function_type,
                ),
            )

        # Generate capabilities based on function type
        if function_type == "network":
            config = create_network_function_capabilities(vendor_id, device_id)
        elif function_type == "media":
            config = create_media_function_capabilities(vendor_id, device_id)
        elif function_type == "storage":
            config = create_storage_function_capabilities(vendor_id, device_id)
        elif function_type == "usb":
            config = create_usb_function_capabilities(vendor_id, device_id)
        else:
            # Create basic generic device config for unknown types
            config = _create_generic_device_capabilities(
                vendor_id, device_id, class_code
            )
            log_warning_safe(
                logger,
                safe_format(
                    "Unknown function type for device {vendor_id:04x}:{device_id:04x}, using generic capabilities",
                    vendor_id=vendor_id,
                    device_id=device_id,
                ),
            )

        # Add metadata
        config.update(
            {
                "analysis_metadata": {
                    "detected_function_type": function_type,
                    "class_code_provided": class_code is not None,
                    "function_hint_provided": function_hint is not None,
                }
            }
        )

        log_info_safe(
            logger,
            safe_format(
                "Successfully generated dynamic capabilities for {vendor_id:04x}:{device_id:04x} as {function_type}",
                vendor_id=vendor_id,
                device_id=device_id,
                function_type=function_type,
            ),
        )

        return config

    except Exception as e:
        log_error_safe(
            logger,
            safe_format(
                "Failed to generate dynamic capabilities for {vendor_id:04x}:{device_id:04x}: {error}",
                vendor_id=vendor_id,
                device_id=device_id,
                error=str(e),
            ),
        )
        raise


def _create_generic_device_capabilities(
    vendor_id: int, device_id: int, class_code: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create generic device capabilities for unknown device types.

    Args:
        vendor_id: PCI vendor ID
        device_id: PCI device ID
        class_code: Optional PCI class code

    Returns:
        Basic device configuration dictionary
    """
    # Determine basic class code if not provided
    if class_code is None:
        class_code = 0x000000  # Unclassified

    # Basic capabilities all devices should have
    capabilities = [
        {"cap_id": 0x01, "version": 3, "d3_support": True},  # Power Management
        {"cap_id": 0x05, "multi_message_capable": 1, "supports_64bit": True},  # MSI
        {"cap_id": 0x10, "version": 2, "device_type": 0},  # PCIe Express
    ]

    # Basic BAR configuration
    bars = [{"bar": 0, "type": "memory", "size": 0x1000, "prefetchable": False}]

    # Basic features
    features = {
        "category": "generic",
        "power_management": True,
        "interrupt_model": "MSI",
    }

    return {
        "vendor_id": vendor_id,
        "device_id": device_id,
        "class_code": class_code,
        "capabilities": capabilities,
        "bars": bars,
        "features": features,
        "generated_by": "GenericDeviceAnalyzer",
    }


# Convenience functions for direct integration into build process
def get_network_capabilities(vendor_id: int, device_id: int) -> Dict[str, Any]:
    """Direct network capability generation for build process."""
    return create_network_function_capabilities(vendor_id, device_id)


def get_media_capabilities(vendor_id: int, device_id: int) -> Dict[str, Any]:
    """Direct media capability generation for build process."""
    return create_media_function_capabilities(vendor_id, device_id)


def get_storage_capabilities(vendor_id: int, device_id: int) -> Dict[str, Any]:
    """Direct storage capability generation for build process."""
    return create_storage_function_capabilities(vendor_id, device_id)


def get_usb_capabilities(vendor_id: int, device_id: int) -> Dict[str, Any]:
    """Direct USB capability generation for build process."""
    return create_usb_function_capabilities(vendor_id, device_id)


def get_auto_capabilities(
    vendor_id: int, device_id: int, class_code: Optional[int] = None
) -> Dict[str, Any]:
    """Auto-detect and generate appropriate capabilities for build process."""
    return create_dynamic_device_capabilities(vendor_id, device_id, class_code, "auto")
