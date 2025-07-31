#!/usr/bin/env python3
"""
Test script for MSI-X and BAR validation functionality.

This script demonstrates how to use the validation functions to detect
and fix common MSI-X/BAR configuration issues.
"""

import sys
from pathlib import Path

# Add the src directory to path for imports
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from pci_capability.msix_bar_validator import (
    validate_msix_bar_configuration,
    auto_fix_msix_configuration,
    print_validation_report,
)


def test_valid_configuration():
    """Test a valid MSI-X/BAR configuration."""
    print("=" * 80)
    print("TEST 1: Valid Configuration")
    print("=" * 80)

    bars = [
        {"bar": 0, "type": "memory", "size": 0x10000, "prefetchable": False},
        {"bar": 1, "type": "memory", "size": 0x8000, "prefetchable": False},
    ]

    capabilities = [
        {
            "cap_id": 0x11,  # MSI-X
            "table_size": 7,  # 8 vectors (encoded as N-1)
            "table_bar": 1,
            "table_offset": 0x1000,  # 4KB aligned
            "pba_bar": 1,
            "pba_offset": 0x2000,  # No overlap, 4KB aligned
        }
    ]

    device_info = {"vendor_id": 0x8086, "device_id": 0x1572}

    is_valid, errors, warnings = validate_msix_bar_configuration(
        bars, capabilities, device_info
    )

    print_validation_report(is_valid, errors, warnings, device_info)
    return is_valid


def test_overlapping_structures():
    """Test MSI-X table and PBA overlap in same BAR."""
    print("\n" + "=" * 80)
    print("TEST 2: Overlapping MSI-X Structures")
    print("=" * 80)

    bars = [
        {"bar": 0, "type": "memory", "size": 0x10000, "prefetchable": False},
        {"bar": 1, "type": "memory", "size": 0x4000, "prefetchable": False},
    ]

    capabilities = [
        {
            "cap_id": 0x11,  # MSI-X
            "table_size": 31,  # 32 vectors (encoded as N-1)
            "table_bar": 1,
            "table_offset": 0x1000,
            "pba_bar": 1,
            "pba_offset": 0x1200,  # Overlaps with table (32*16 = 512 bytes)
        }
    ]

    device_info = {"vendor_id": 0x10DE, "device_id": 0x1B80}

    is_valid, errors, warnings = validate_msix_bar_configuration(
        bars, capabilities, device_info
    )

    print_validation_report(is_valid, errors, warnings, device_info)

    if not is_valid:
        print("\n🔧 Attempting auto-fix...")
        fixed_bars, fixed_caps, fix_messages = auto_fix_msix_configuration(
            bars, capabilities
        )

        print("Fix actions taken:")
        for msg in fix_messages:
            print(f"  ✅ {msg}")

        # Re-validate
        is_valid_after, errors_after, warnings_after = validate_msix_bar_configuration(
            fixed_bars, fixed_caps, device_info
        )

        print("\nValidation after auto-fix:")
        print_validation_report(
            is_valid_after, errors_after, warnings_after, device_info
        )

        return is_valid_after

    return is_valid


def test_insufficient_bar_size():
    """Test MSI-X structures that don't fit in their BAR."""
    print("\n" + "=" * 80)
    print("TEST 3: Insufficient BAR Size")
    print("=" * 80)

    bars = [
        {
            "bar": 0,
            "type": "memory",
            "size": 0x2000,
            "prefetchable": False,
        },  # Too small
    ]

    capabilities = [
        {
            "cap_id": 0x11,  # MSI-X
            "table_size": 63,  # 64 vectors (encoded as N-1)
            "table_bar": 0,
            "table_offset": 0x1000,  # 64*16 = 1024 bytes needed
            "pba_bar": 0,
            "pba_offset": 0x1800,  # ((64+31)//32)*4 = 12 bytes needed
        }
    ]

    device_info = {"vendor_id": 0x15B3, "device_id": 0x1017}

    is_valid, errors, warnings = validate_msix_bar_configuration(
        bars, capabilities, device_info
    )

    print_validation_report(is_valid, errors, warnings, device_info)

    if not is_valid:
        print("\n🔧 Attempting auto-fix...")
        fixed_bars, fixed_caps, fix_messages = auto_fix_msix_configuration(
            bars, capabilities
        )

        print("Fix actions taken:")
        for msg in fix_messages:
            print(f"  ✅ {msg}")

        print(f"\nOriginal BAR 0 size: 0x{bars[0]['size']:x}")
        print(f"Fixed BAR 0 size:    0x{fixed_bars[0]['size']:x}")

        # Re-validate
        is_valid_after, errors_after, warnings_after = validate_msix_bar_configuration(
            fixed_bars, fixed_caps, device_info
        )

        print("\nValidation after auto-fix:")
        print_validation_report(
            is_valid_after, errors_after, warnings_after, device_info
        )

        return is_valid_after

    return is_valid


def test_misaligned_offsets():
    """Test misaligned MSI-X table and PBA offsets."""
    print("\n" + "=" * 80)
    print("TEST 4: Misaligned Offsets")
    print("=" * 80)

    bars = [
        {"bar": 0, "type": "memory", "size": 0x10000, "prefetchable": False},
    ]

    capabilities = [
        {
            "cap_id": 0x11,  # MSI-X
            "table_size": 15,  # 16 vectors (encoded as N-1)
            "table_bar": 0,
            "table_offset": 0x1003,  # Not 8-byte aligned
            "pba_bar": 0,
            "pba_offset": 0x2005,  # Not 8-byte aligned
        }
    ]

    device_info = {"vendor_id": 0x1414, "device_id": 0x0007}

    is_valid, errors, warnings = validate_msix_bar_configuration(
        bars, capabilities, device_info
    )

    print_validation_report(is_valid, errors, warnings, device_info)

    if not is_valid:
        print("\n🔧 Attempting auto-fix...")
        fixed_bars, fixed_caps, fix_messages = auto_fix_msix_configuration(
            bars, capabilities
        )

        print("Fix actions taken:")
        for msg in fix_messages:
            print(f"  ✅ {msg}")

        print(f"\nOriginal table offset: 0x{capabilities[0]['table_offset']:x}")
        print(f"Fixed table offset:    0x{fixed_caps[0]['table_offset']:x}")
        print(f"Original PBA offset:   0x{capabilities[0]['pba_offset']:x}")
        print(f"Fixed PBA offset:      0x{fixed_caps[0]['pba_offset']:x}")

        # Re-validate
        is_valid_after, errors_after, warnings_after = validate_msix_bar_configuration(
            fixed_bars, fixed_caps, device_info
        )

        print("\nValidation after auto-fix:")
        print_validation_report(
            is_valid_after, errors_after, warnings_after, device_info
        )

        return is_valid_after

    return is_valid


def test_reserved_region_conflict():
    """Test MSI-X structures conflicting with reserved regions."""
    print("\n" + "=" * 80)
    print("TEST 5: Reserved Region Conflicts")
    print("=" * 80)

    bars = [
        {"bar": 0, "type": "memory", "size": 0x20000, "prefetchable": False},
    ]

    capabilities = [
        {
            "cap_id": 0x11,  # MSI-X
            "table_size": 7,  # 8 vectors (encoded as N-1)
            "table_bar": 0,
            "table_offset": 0x0800,  # Conflicts with device control region
            "pba_bar": 0,
            "pba_offset": 0x5000,  # Conflicts with custom PIO region
        }
    ]

    device_info = {"vendor_id": 0x1B21, "device_id": 0x0612}

    is_valid, errors, warnings = validate_msix_bar_configuration(
        bars, capabilities, device_info
    )

    print_validation_report(is_valid, errors, warnings, device_info)

    if not is_valid:
        print("\n🔧 Attempting auto-fix...")
        fixed_bars, fixed_caps, fix_messages = auto_fix_msix_configuration(
            bars, capabilities
        )

        print("Fix actions taken:")
        for msg in fix_messages:
            print(f"  ✅ {msg}")

        print(f"\nOriginal table offset: 0x{capabilities[0]['table_offset']:x}")
        print(f"Fixed table offset:    0x{fixed_caps[0]['table_offset']:x}")
        print(f"Original PBA offset:   0x{capabilities[0]['pba_offset']:x}")
        print(f"Fixed PBA offset:      0x{fixed_caps[0]['pba_offset']:x}")

        # Re-validate
        is_valid_after, errors_after, warnings_after = validate_msix_bar_configuration(
            fixed_bars, fixed_caps, device_info
        )

        print("\nValidation after auto-fix:")
        print_validation_report(
            is_valid_after, errors_after, warnings_after, device_info
        )

        return is_valid_after

    return is_valid


def run_all_tests():
    """Run all validation tests."""
    print("🧪 MSI-X/BAR Configuration Validation Test Suite")
    print("=" * 80)

    results = []

    try:
        results.append(("Valid Configuration", test_valid_configuration()))
        results.append(("Overlapping Structures", test_overlapping_structures()))
        results.append(("Insufficient BAR Size", test_insufficient_bar_size()))
        results.append(("Misaligned Offsets", test_misaligned_offsets()))
        results.append(("Reserved Region Conflicts", test_reserved_region_conflict()))

        print("\n" + "=" * 80)
        print("🏁 TEST SUMMARY")
        print("=" * 80)

        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<30} {status}")
            if result:
                passed += 1

        print(f"\nOverall: {passed}/{len(results)} tests passed")

        if passed == len(results):
            print("🎉 All tests passed! MSI-X/BAR validation is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the validation logic.")

    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
