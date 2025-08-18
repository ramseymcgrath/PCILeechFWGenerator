#!/usr/bin/env python3
"""
Device Information Lookup Module

Provides resilient device information lookup using multiple data sources
including lspci, sysfs, and configuration space scraping.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional

from src.device_clone.config_space_manager import ConfigSpaceManager
from src.device_clone.device_config import DeviceConfiguration, DeviceIdentification
from src.device_clone.fallback_manager import get_global_fallback_manager
from src.string_utils import (
    log_debug_safe,
    log_error_safe,
    log_info_safe,
    log_warning_safe,
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
        # Start with provided partial info or empty dict
        device_info = partial_info.copy() if partial_info else {}

        # Only extract from config space if we don't already have basic info
        # This prevents infinite recursion when called from ConfigSpaceManager.extract_device_info
        if not all(
            key in device_info for key in ["vendor_id", "device_id", "class_code"]
        ):
            manager = ConfigSpaceManager(self.bdf)
            try:
                config_space = manager.read_vfio_config_space()
                # Use internal methods to avoid recursion
                extracted_info = manager._extract_basic_device_info(config_space)
                subsystem_vendor, subsystem_device = manager._extract_subsystem_info(
                    config_space
                )
                extracted_info["subsystem_vendor_id"] = subsystem_vendor
                extracted_info["subsystem_device_id"] = subsystem_device
                extracted_info["bars"] = manager._extract_bar_info(config_space)

                # Merge extracted info with existing info
                device_info.update(
                    {
                        k: v
                        for k, v in extracted_info.items()
                        if k not in device_info or device_info[k] is None
                    }
                )
            except Exception as e:
                log_warning_safe(
                    logger,
                    "Failed to extract device info for {bdf}: {error}",
                    bdf=self.bdf,
                    error=str(e),
                    prefix="LOOKUP",
                )

        # Diagnostic: log a sanitized snapshot of device_info before applying fallbacks
        try:

            def _is_sensitive(var_name: str) -> bool:
                # reuse FallbackManager's sensitivity rules if available, else conservative False
                try:
                    mgr = get_global_fallback_manager()
                    return mgr.is_sensitive_var(var_name)
                except Exception:
                    return False

            def _sanitize(ctx: Any, path: list) -> Any:
                if not isinstance(ctx, dict):
                    return ctx
                out: Dict[str, Any] = {}
                for k, v in ctx.items():
                    var_name = ".".join(path + [k]) if path else k
                    if _is_sensitive(var_name):
                        continue
                    if isinstance(v, dict):
                        out[k] = _sanitize(v, path + [k])
                    else:
                        try:
                            s = repr(v)
                        except Exception:
                            s = f"<{type(v).__name__}>"
                        if len(s) > 200:
                            s = s[:200] + "...<truncated>"
                        out[k] = s
                return out

            def _shape(ctx: Any) -> Any:
                if not isinstance(ctx, dict):
                    return type(ctx).__name__
                return {k: _shape(v) for k, v in ctx.items()}

            sanitized = _sanitize(device_info or {}, [])
            shape = _shape(sanitized)

            log_info_safe(
                logger,
                "Pre-fallback device_info (shape): {shape}",
                prefix="LOOKUP",
                shape=shape,
            )

            s = json.dumps(sanitized, indent=2, sort_keys=True)
            if len(s) > 4000:
                s = s[:4000] + "...<truncated>"

            log_info_safe(
                logger,
                "Pre-fallback device_info (sanitized): {snapshot}",
                prefix="LOOKUP",
                snapshot=s,
            )
        except Exception:
            log_warning_safe(
                logger,
                "Failed to emit pre-fallback diagnostic",
                prefix="LOOKUP",
            )

        # Apply fallbacks for missing fields using the shared/global FallbackManager
        fallback_mgr = get_global_fallback_manager()
        device_info = fallback_mgr.apply_fallbacks(device_info)

        # Optionally validate using DeviceIdentification
        try:
            # Convert values to integers in case they're strings
            def to_int(value):
                """Convert a value to int, accepting hex strings with or without 0x.

                Accept formats like '0x10ec', '10ec', or decimal '1234'.
                """
                if isinstance(value, str):
                    s = value.strip()
                    if s.startswith(("0x", "0X")):
                        return int(s, 16)
                    # Plain decimal
                    if re.match(r"^\d+$", s):
                        return int(s, 10)
                    # Hex digits without 0x prefix (e.g. '10ec')
                    if re.match(r"^[0-9A-Fa-f]+$", s):
                        return int(s, 16)
                    # Fallback to python auto-detect; if that fails try hex
                    try:
                        return int(s, 0)
                    except ValueError:
                        return int(s, 16)

                return int(value) if value else 0

            ident = DeviceIdentification(
                vendor_id=to_int(device_info.get("vendor_id", 0)),
                device_id=to_int(device_info.get("device_id", 0)),
                class_code=to_int(device_info.get("class_code", 0)),
                subsystem_vendor_id=to_int(device_info.get("subsystem_vendor_id", 0)),
                subsystem_device_id=to_int(device_info.get("subsystem_device_id", 0)),
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
