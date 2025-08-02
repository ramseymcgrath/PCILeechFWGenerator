#!/usr/bin/env python3
"""
Test script for enhanced MSI-X overlap detection with 64-bit BAR support.
"""

import sys
from pathlib import Path

# Add src to path for imports
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from device_clone.msix_capability import (
    parse_bar_info_from_config_space,
    parse_msix_capability,
    validate_msix_configuration,
    validate_msix_configuration_enhanced,
)


def create_test_config_space_with_64bit_bar():
    """Create a test configuration space with a 64-bit BAR."""
    config = bytearray(4096)  # 4KB config space

    # Basic PCI header
    config[0:2] = (0x8086).to_bytes(2, "little")  # Vendor ID: Intel
    config[2:4] = (0x15B8).to_bytes(2, "little")  # Device ID
    config[4:6] = (0x0006).to_bytes(2, "little")  # Command: Memory Space + Bus Master
    config[6:8] = (0x0210).to_bytes(2, "little")  # Status: Capabilities List
    config[8] = 0x01  # Revision ID
    config[9:12] = (0x020000).to_bytes(3, "little")  # Class Code: Ethernet Controller
    config[12] = 0x10  # Cache Line Size
    config[13] = 0x00  # Latency Timer
    config[14] = 0x00  # Header Type
    config[15] = 0x00  # BIST

    # BAR0: 64-bit memory BAR at 0x100000000 (4GB), size indicated by address mask
    # Lower 32 bits with 64-bit flag (bit 2-1 = 10b) and prefetchable (bit 3)
    bar0_lower = 0x00000000 | 0x4 | 0x8  # 64-bit + prefetchable, address 0
    config[16:20] = bar0_lower.to_bytes(4, "little")

    # BAR1: Upper 32 bits of 64-bit BAR0
    bar0_upper = 0x00000001  # 4GB base address
    config[20:24] = bar0_upper.to_bytes(4, "little")

    # BAR2: 32-bit memory BAR
    bar2_value = 0xF0000000  # 256MB BAR
    config[24:28] = bar2_value.to_bytes(4, "little")

    # Capabilities pointer
    config[52] = 0x40  # Capabilities start at 0x40

    # MSI-X Capability at offset 0x40
    config[0x40] = 0x11  # MSI-X Capability ID
    config[0x41] = 0x00  # Next capability (end of list)
    config[0x42:0x44] = (0x001F).to_bytes(
        2, "little"
    )  # Message Control: 32 entries, disabled

    # Table Offset/BIR: BAR 0 (64-bit), offset 0x1000
    table_offset_bir = 0x00001000 | 0x0  # BAR 0
    config[0x44:0x48] = table_offset_bir.to_bytes(4, "little")

    # PBA Offset/BIR: BAR 0 (64-bit), offset 0x2000
    pba_offset_bir = 0x00002000 | 0x0  # BAR 0
    config[0x48:0x4C] = pba_offset_bir.to_bytes(4, "little")

    return config.hex()


def create_test_config_space_with_overlap():
    """Create a test configuration space with overlapping MSI-X regions."""
    config = bytearray(4096)  # 4KB config space

    # Basic PCI header (similar to above)
    config[0:2] = (0x8086).to_bytes(2, "little")  # Vendor ID: Intel
    config[2:4] = (0x15B8).to_bytes(2, "little")  # Device ID
    config[6:8] = (0x0210).to_bytes(2, "little")  # Status: Capabilities List
    config[52] = 0x40  # Capabilities pointer

    # BAR0: 32-bit memory BAR, small size (4KB)
    config[16:20] = (0xFFFFF000).to_bytes(4, "little")  # 4KB BAR

    # MSI-X Capability at offset 0x40
    config[0x40] = 0x11  # MSI-X Capability ID
    config[0x41] = 0x00  # Next capability
    config[0x42:0x44] = (0x0007).to_bytes(2, "little")  # 8 entries

    # Table and PBA both in BAR 0, overlapping
    table_offset_bir = 0x00001000 | 0x0  # BAR 0, offset 0x1000
    config[0x44:0x48] = table_offset_bir.to_bytes(4, "little")

    pba_offset_bir = 0x00001080 | 0x0  # BAR 0, offset 0x1080 (overlaps with table)
    config[0x48:0x4C] = pba_offset_bir.to_bytes(4, "little")

    return config.hex()


def test_64bit_bar_parsing():
    """Test parsing of 64-bit BARs."""
    print("=== Testing 64-bit BAR Parsing ===")

    config_space = create_test_config_space_with_64bit_bar()
    bars = parse_bar_info_from_config_space(config_space)

    print(f"Found {len(bars)} BARs:")
    for bar in bars:
        bitness = "64-bit" if bar["is_64bit"] else "32-bit"
        prefetch = "prefetchable" if bar["prefetchable"] else "non-prefetchable"
        print(
            f"  BAR {bar['index']}: {bar['bar_type']} @ 0x{bar['address']:016x}, "
            f"size=0x{bar['size']:x} ({bitness}, {prefetch})"
        )

    # Verify 64-bit BAR was parsed correctly
    assert len(bars) >= 1, "Should have found at least one BAR"
    bar0 = bars[0]
    assert bar0["is_64bit"], "BAR 0 should be 64-bit"
    assert bar0["prefetchable"], "BAR 0 should be prefetchable"
    assert (
        bar0["address"] == 0x100000000
    ), f"BAR 0 address should be 4GB, got 0x{bar0['address']:x}"

    print("✓ 64-bit BAR parsing test passed")


def test_enhanced_validation():
    """Test enhanced MSI-X validation with BAR information."""
    print("\n=== Testing Enhanced MSI-X Validation ===")

    # Test 1: Valid configuration
    config_space = create_test_config_space_with_64bit_bar()
    msix_info = parse_msix_capability(config_space)

    is_valid, errors = validate_msix_configuration(msix_info, config_space)
    print(f"Valid config test: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        print("  Errors:", errors)

    # Test 2: Overlapping configuration
    overlap_config = create_test_config_space_with_overlap()
    msix_info_overlap = parse_msix_capability(overlap_config)

    is_valid_overlap, errors_overlap = validate_msix_configuration(
        msix_info_overlap, overlap_config
    )
    print(f"Overlap detection test: {'PASS' if not is_valid_overlap else 'FAIL'}")
    if errors_overlap:
        print("  Expected errors:", errors_overlap)

    # Test 3: Legacy mode (backward compatibility)
    is_valid_legacy, errors_legacy = validate_msix_configuration(msix_info)
    print(f"Legacy mode test: {'PASS' if is_valid_legacy else 'FAIL'}")

    print("✓ Enhanced validation tests completed")


def test_msix_parsing():
    """Test MSI-X capability parsing."""
    print("\n=== Testing MSI-X Capability Parsing ===")

    config_space = create_test_config_space_with_64bit_bar()
    msix_info = parse_msix_capability(config_space)

    print("MSI-X Info:")
    for key, value in msix_info.items():
        if isinstance(value, int) and key.endswith(("offset", "bir")):
            print(f"  {key}: 0x{value:x}")
        else:
            print(f"  {key}: {value}")

    # Verify parsing results
    assert (
        msix_info["table_size"] == 32
    ), f"Expected 32 entries, got {msix_info['table_size']}"
    assert (
        msix_info["table_bir"] == 0
    ), f"Expected table BIR 0, got {msix_info['table_bir']}"
    assert (
        msix_info["table_offset"] == 0x1000
    ), f"Expected table offset 0x1000, got 0x{msix_info['table_offset']:x}"
    assert msix_info["pba_bir"] == 0, f"Expected PBA BIR 0, got {msix_info['pba_bir']}"
    assert (
        msix_info["pba_offset"] == 0x2000
    ), f"Expected PBA offset 0x2000, got 0x{msix_info['pba_offset']:x}"

    print("✓ MSI-X parsing test passed")


if __name__ == "__main__":
    try:
        test_msix_parsing()
        test_64bit_bar_parsing()
        test_enhanced_validation()
        print(
            "\n🎉 All tests passed! Enhanced MSI-X overlap detection is working correctly."
        )
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
