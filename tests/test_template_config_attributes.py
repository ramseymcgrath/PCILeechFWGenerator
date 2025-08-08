#!/usr/bin/env python3
"""
Dynamic test to verify all config attributes used in templates exist.

This test scans all Jinja2 templates for config attribute references
and verifies they exist in the corresponding configuration classes.
"""

import re
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.templating.advanced_sv_features import (
    PerformanceConfig,
    ErrorHandlingConfig,
    PowerManagementConfig,
    AdvancedFeatureConfig,
)


def find_template_attribute_references(template_dir: Path) -> Dict[str, Set[str]]:
    """
    Scan templates for config attribute references.

    Returns a dict mapping config names to sets of referenced attributes.
    """
    config_refs = {
        "perf_config": set(),
        "error_config": set(),
        "error_handling": set(),  # Some templates use this name
        "power_config": set(),
        "power_management": set(),  # Some templates use this name
        "device_config": set(),
        "bar_config": set(),
        "msix_config": set(),
        "timing_config": set(),
        "pcileech_config": set(),
        "active_device_config": set(),
    }

    # Regex to find config attribute references
    # Matches: config_name.attribute or config_name.attr1.attr2
    pattern = re.compile(r"(\w+_config|\w+_handling|\w+_management)\.(\w+(?:\.\w+)*)")

    # Scan all .j2 files
    for template_file in template_dir.rglob("*.j2"):
        with open(template_file, "r") as f:
            content = f.read()

        # Find all matches
        for match in pattern.finditer(content):
            config_name = match.group(1)
            attribute_path = match.group(2)

            if config_name in config_refs:
                config_refs[config_name].add(attribute_path)

    return config_refs


def check_attributes_exist(config_obj, attributes: Set[str]) -> List[Tuple[str, bool]]:
    """
    Check if attributes exist in a config object.

    Returns list of (attribute_path, exists) tuples.
    """
    results = []

    for attr_path in sorted(attributes):
        # Skip false positives from include statements
        if attr_path.endswith(".j2") or attr_path.endswith(".sv"):
            continue

        parts = attr_path.split(".")
        obj = config_obj
        exists = True

        # Navigate through nested attributes
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                exists = False
                break

        results.append((attr_path, exists))

    return results


def test_performance_config_attributes():
    """Test that all PerformanceConfig attributes used in templates exist."""
    template_dir = Path(__file__).parent.parent / "src" / "templates"
    config_refs = find_template_attribute_references(template_dir)

    config = PerformanceConfig()
    perf_attrs = config_refs.get("perf_config", set())

    print("Testing PerformanceConfig attributes used in templates...")
    results = check_attributes_exist(config, perf_attrs)

    all_exist = True
    for attr, exists in results:
        if exists:
            print(f"  ✓ {attr}")
        else:
            print(f"  ✗ {attr} - MISSING!")
            all_exist = False

    if not perf_attrs:
        print("  (No attributes found in templates)")

    return all_exist


def test_error_handling_config_attributes():
    """Test that all ErrorHandlingConfig attributes used in templates exist."""
    template_dir = Path(__file__).parent.parent / "src" / "templates"
    config_refs = find_template_attribute_references(template_dir)

    config = ErrorHandlingConfig()
    # Combine both possible names
    error_attrs = config_refs.get("error_config", set()) | config_refs.get(
        "error_handling", set()
    )

    print("\nTesting ErrorHandlingConfig attributes used in templates...")
    results = check_attributes_exist(config, error_attrs)

    all_exist = True
    for attr, exists in results:
        if exists:
            print(f"  ✓ {attr}")
        else:
            print(f"  ✗ {attr} - MISSING!")
            all_exist = False

    if not error_attrs:
        print("  (No attributes found in templates)")

    return all_exist


def test_power_management_config_attributes():
    """Test that all PowerManagementConfig attributes used in templates exist."""
    template_dir = Path(__file__).parent.parent / "src" / "templates"
    config_refs = find_template_attribute_references(template_dir)

    config = PowerManagementConfig()
    # Combine both possible names
    power_attrs = config_refs.get("power_config", set()) | config_refs.get(
        "power_management", set()
    )

    print("\nTesting PowerManagementConfig attributes used in templates...")
    results = check_attributes_exist(config, power_attrs)

    all_exist = True
    for attr, exists in results:
        if exists:
            print(f"  ✓ {attr}")
        else:
            print(f"  ✗ {attr} - MISSING!")
            all_exist = False

    if not power_attrs:
        print("  (No attributes found in templates)")

    return all_exist


def test_all_known_attributes():
    """Test all known required attributes are present."""
    print("\nTesting all known required attributes...")

    # Test PerformanceConfig
    perf = PerformanceConfig()
    perf_attrs = [
        "enable_transaction_counters",
        "enable_bandwidth_monitoring",
        "enable_latency_tracking",
        "enable_latency_measurement",
        "enable_error_counting",
    ]

    print("  PerformanceConfig:")
    all_exist = True
    for attr in perf_attrs:
        if hasattr(perf, attr):
            print(f"    ✓ {attr}")
        else:
            print(f"    ✗ {attr} - MISSING!")
            all_exist = False

    # Test PowerManagementConfig nested attributes
    power = PowerManagementConfig()
    print("  PowerManagementConfig.transition_cycles:")
    if hasattr(power, "transition_cycles"):
        tc = power.transition_cycles
        for attr in ["d0_to_d1", "d1_to_d0", "d0_to_d3", "d3_to_d0"]:
            if hasattr(tc, attr):
                print(f"    ✓ {attr}")
            else:
                print(f"    ✗ {attr} - MISSING!")
                all_exist = False
    else:
        print("    ✗ transition_cycles - MISSING!")
        all_exist = False

    return all_exist


def main():
    """Run all tests."""
    print("=" * 70)
    print("Dynamic Template Configuration Attribute Test")
    print("=" * 70)

    results = []
    results.append(test_performance_config_attributes())
    results.append(test_error_handling_config_attributes())
    results.append(test_power_management_config_attributes())
    results.append(test_all_known_attributes())

    # Report on other config types found
    template_dir = Path(__file__).parent.parent / "src" / "templates"
    config_refs = find_template_attribute_references(template_dir)

    print("\n" + "-" * 70)
    print("Other config types found in templates (not tested):")
    for config_name, attrs in config_refs.items():
        if config_name not in [
            "perf_config",
            "error_config",
            "error_handling",
            "power_config",
            "power_management",
        ]:
            if attrs:
                print(f"  - {config_name}: {len(attrs)} attributes")

    print("\n" + "=" * 70)
    if all(results):
        print("✅ All tests passed! All template-referenced attributes exist.")
        return 0
    else:
        print("❌ Some tests failed! Missing attributes detected.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
