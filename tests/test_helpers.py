#!/usr/bin/env python3
"""
Test helper functions for PCILeech FW Generator tests.
"""

import os
from pathlib import Path

import pytest


def has_vfio_device():
    """
    Check if there are any VFIO devices available on the system.

    Returns:
        bool: True if VFIO devices are available, False otherwise
    """
    # Check if running in CI environment
    if os.environ.get("CI"):
        return False

    # Check for VFIO devices in /dev
    vfio_path = Path("/dev/vfio")
    if not vfio_path.exists():
        return False

    # Check for at least one VFIO group
    vfio_groups = list(vfio_path.glob("[0-9]*"))
    return len(vfio_groups) > 0


def requires_hardware(reason="Requires VFIO hardware access"):
    """
    Decorator to skip tests that require hardware access.

    Args:
        reason: Reason for skipping the test

    Returns:
        pytest.mark.skipif decorator
    """
    return pytest.mark.skipif(not has_vfio_device(), reason=reason)


def requires_root(reason="Requires root privileges"):
    """
    Decorator to skip tests that require root privileges.

    Args:
        reason: Reason for skipping the test

    Returns:
        pytest.mark.skipif decorator
    """
    return pytest.mark.skipif(os.geteuid() != 0, reason=reason)
