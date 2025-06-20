#!/usr/bin/env python3
"""VFIO module - re-exports the correct implementation from vfio_handler."""

# Re-export the correct, complete VFIO implementation
from .vfio_handler import VFIOBinder, VFIOBindError, run_diagnostics, render_pretty
from .vfio_helpers import get_device_fd

# Legacy compatibility functions - these are kept for backward compatibility
# but they now use the correct implementation internally

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_current_driver(bdf: str) -> Optional[str]:
    """Get the current driver for the device."""
    driver_link = Path(f"/sys/bus/pci/devices/{bdf}/driver")
    if driver_link.exists():
        return driver_link.resolve().name
    return None


def restore_driver(bdf: str, original: Optional[str]):
    """Restore device to original driver."""
    if original and get_current_driver(bdf) != original:
        try:
            bind_path = Path(f"/sys/bus/pci/drivers/{original}/bind")
            if bind_path.exists():
                bind_path.write_text(f"{bdf}\n")
                logger.debug("Restored %s to %s", bdf, original)
        except Exception as e:
            logger.warning("Failed to restore driver for %s: %s", bdf, e)


# Export the main symbols
__all__ = [
    "VFIOBinder",
    "VFIOBindError",
    "get_device_fd",
    "get_current_driver",
    "restore_driver",
    "run_diagnostics",
    "render_pretty",
]
