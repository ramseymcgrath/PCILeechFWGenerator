#!/usr/bin/env python3
"""
Device Information Lookup Module

Provides resilient device information lookup using multiple data sources
including lspci, sysfs, and configuration space scraping.
"""

import logging
from typing import Any, Dict, Optional
from pathlib import Path

from src.device_clone.config_space_manager import ConfigSpaceManager
from src.device_clone.fallback_manager import FallbackManager
from src.device_clone.device_config import DeviceConfiguration, DeviceIdentification
from src.string_utils import (
    log_info_safe,
    log_warning_safe,
    log_error_safe,
    log_debug_safe,
)

logger = logging.getLogger(__name__)


class DeviceInfoLookup:
    """
    DRY device information lookup using device clone subsystem.
    """

    def __init__(self, bdf: str):
        self.bdf = bdf
        self._cached_info: Optional[Dict[str, Any]] = None

    def get_complete_device_info(
        self, partial_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get complete device information using ConfigSpaceManager and FallbackManager.
        Args:
            partial_info: Partial device information to complete
        Returns:
            Complete device information dictionary
        """
        # Extract config space and device info using ConfigSpaceManager
        manager = ConfigSpaceManager(self.bdf)
        try:
            config_space = manager.read_vfio_config_space()
            device_info = manager.extract_device_info(config_space)
        except Exception as e:
            log_warning_safe(
                logger,
                "Failed to extract device info for {bdf}: {error}",
                bdf=self.bdf,
                error=str(e),
                prefix="LOOKUP",
            )
            device_info = partial_info.copy() if partial_info else {}

        # Merge with any provided partial info
        if partial_info:
            device_info.update({k: v for k, v in partial_info.items() if v is not None})

        # Apply fallbacks for missing fields using FallbackManager
        fallback_mgr = FallbackManager()
        device_info = fallback_mgr.apply_fallbacks(device_info)

        # Optionally validate using DeviceIdentification
        try:
            ident = DeviceIdentification(
                vendor_id=device_info.get("vendor_id", 0),
                device_id=device_info.get("device_id", 0),
                class_code=device_info.get("class_code", 0),
                subsystem_vendor_id=device_info.get("subsystem_vendor_id", 0),
                subsystem_device_id=device_info.get("subsystem_device_id", 0),
            )
            ident.validate()
        except Exception as e:
            log_error_safe(
                logger,
                "Device identification validation failed for {bdf}: {error}",
                bdf=self.bdf,
                error=str(e),
                prefix="VALIDATE",
            )

        self._cached_info = device_info
        return device_info


def lookup_device_info(
    bdf: str, partial_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to lookup device information using DRY subsystem.
    Args:
        bdf: Bus:Device.Function identifier
        partial_info: Partial device information to complete
    Returns:
        Complete device information dictionary
    """
    lookup = DeviceInfoLookup(bdf)
    return lookup.get_complete_device_info(partial_info)
