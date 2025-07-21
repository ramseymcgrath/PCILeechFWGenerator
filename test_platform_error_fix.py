#!/usr/bin/env python3
"""Test script to verify the improved platform error handling."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.exceptions import PlatformCompatibilityError
from src.device_clone.behavior_profiler import check_linux_requirement


def test_platform_error_handling():
    """Test that platform errors are handled correctly."""
    print("Testing platform compatibility error handling...")

    try:
        # This should raise a PlatformCompatibilityError on macOS
        check_linux_requirement("Device behavior monitoring")
        print("✗ Expected PlatformCompatibilityError but none was raised")
    except PlatformCompatibilityError as e:
        print(f"✓ PlatformCompatibilityError raised correctly: {e}")
        print(f"  Current platform: {e.current_platform}")
        print(f"  Required platform: {e.required_platform}")
    except Exception as e:
        print(f"✗ Unexpected exception type: {type(e).__name__}: {e}")


if __name__ == "__main__":
    test_platform_error_handling()
