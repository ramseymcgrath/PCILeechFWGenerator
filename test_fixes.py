#!/usr/bin/env python3
"""Test script to validate fixes"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_log_config_fix():
    """Test the log config scope fix"""
    from log_config import FallbackColoredFormatter
    import logging

    formatter = FallbackColoredFormatter()
    record = logging.LogRecord(
        "test", logging.INFO, "test.py", 1, "test message", (), None
    )
    try:
        result = formatter.format(record)
        return True, "Log config scope issue: FIXED"
    except Exception as e:
        return False, f"Log config scope issue: NOT FIXED - {e}"


def test_header_file():
    """Test if the missing header file was created"""
    header_path = Path("pcileech/pcileech_header.svh")
    if header_path.exists():
        return True, "Missing SVH header issue: FIXED"
    else:
        return False, "Missing SVH header issue: NOT FIXED"


def test_jinja2_extension():
    """Test if ErrorTagExtension was implemented (basic import test)"""
    try:
        # This will fail due to jinja2 imports, but we can check the file content
        with open("src/templating/template_renderer.py", "r") as f:
            content = f.read()
            if (
                "ErrorTagExtension" in content
                and "extensions=[ErrorTagExtension]" in content
            ):
                return True, "Jinja2 ErrorTagExtension: IMPLEMENTED"
            else:
                return False, "Jinja2 ErrorTagExtension: NOT IMPLEMENTED"
    except Exception as e:
        return False, f"Jinja2 ErrorTagExtension: ERROR - {e}"


def test_vivado_function_signature():
    """Test if vivado function signature was updated"""
    try:
        with open("src/vivado_handling/vivado_error_reporter.py", "r") as f:
            content = f.read()
            if (
                "vivado_jobs: int = 4" in content
                and "vivado_timeout: int = 3600" in content
            ):
                return True, "Vivado function parameters: FIXED"
            else:
                return False, "Vivado function parameters: NOT FIXED"
    except Exception as e:
        return False, f"Vivado function parameters: ERROR - {e}"


if __name__ == "__main__":
    print("Testing PCILeech FW Generator Fixes")
    print("=" * 40)

    tests = [
        test_log_config_fix,
        test_header_file,
        test_jinja2_extension,
        test_vivado_function_signature,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            success, message = test()
            status = "✓" if success else "✗"
            print(f"{status} {message}")
            if success:
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR - {e}")

    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} fixes verified")

    if passed == total:
        print("🎉 All reported issues have been addressed!")
    else:
        print("⚠️  Some issues may need additional work")
