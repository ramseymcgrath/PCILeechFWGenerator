#!/usr/bin/env python3
"""
Test script to verify the SystemVerilog generator works correctly with all configurations.
"""

from src.templating.systemverilog_generator import (
    AdvancedSVGenerator,
    DeviceSpecificLogic,
)
from src.templating.advanced_sv_perf import PerformanceCounterConfig, DeviceType
from src.templating.advanced_sv_error import ErrorHandlingConfig
from src.templating.advanced_sv_power import PowerManagementConfig


def test_with_all_features():
    print("Testing SystemVerilog generation with all features enabled...")
    # Create configuration with all features enabled
    perf_config = PerformanceCounterConfig(
        enable_transaction_counters=True,
        enable_bandwidth_monitoring=True,
        enable_latency_measurement=True,
        enable_error_rate_tracking=True,
        enable_device_specific_counters=True,
    )

    error_config = ErrorHandlingConfig(enable_ecc=True, enable_error_injection=True)

    power_config = PowerManagementConfig(
        enable_pme=True, clk_hz=125_000_000  # 125 MHz clock
    )

    # Test with different device types
    for device_type in [
        DeviceType.GENERIC,
        DeviceType.NETWORK_CONTROLLER,
        DeviceType.STORAGE_CONTROLLER,
        DeviceType.GRAPHICS_CONTROLLER,
        DeviceType.AUDIO_CONTROLLER,
    ]:
        print(f"\nTesting with device type: {device_type.value}")
        device_config = DeviceSpecificLogic(device_type=device_type)

        # Initialize the generator
        gen = AdvancedSVGenerator(
            perf_config=perf_config,
            error_config=error_config,
            power_config=power_config,
            device_config=device_config,
        )

        # Generate SystemVerilog
        try:
            sv_code = gen.generate_advanced_systemverilog(regs=[])
            print(f"✓ Successfully generated SystemVerilog for {device_type.value}")
            # Print first 100 characters to verify content
            print(f"Preview: {sv_code[:100]}...")
        except Exception as e:
            print(f"✗ Failed to generate SystemVerilog for {device_type.value}: {e}")

    print("\nAll device type tests completed.")


def test_with_error_rate_tracking_variations():
    print("\nTesting specific error_rate_tracking configurations...")

    # Test with error_rate_tracking explicitly enabled
    perf_config = PerformanceCounterConfig(enable_error_rate_tracking=True)
    gen = AdvancedSVGenerator(
        perf_config=perf_config,
        device_config=DeviceSpecificLogic(device_type=DeviceType.GENERIC),
    )

    try:
        sv_code = gen.generate_advanced_systemverilog(regs=[])
        print(
            "✓ Successfully generated SystemVerilog with enable_error_rate_tracking=True"
        )
    except Exception as e:
        print(f"✗ Failed with enable_error_rate_tracking=True: {e}")

    # Test with error_rate_tracking explicitly disabled
    perf_config = PerformanceCounterConfig(enable_error_rate_tracking=False)
    gen = AdvancedSVGenerator(
        perf_config=perf_config,
        device_config=DeviceSpecificLogic(device_type=DeviceType.GENERIC),
    )

    try:
        sv_code = gen.generate_advanced_systemverilog(regs=[])
        print(
            "✓ Successfully generated SystemVerilog with enable_error_rate_tracking=False"
        )
    except Exception as e:
        print(f"✗ Failed with enable_error_rate_tracking=False: {e}")

    print("Error rate tracking tests completed.")


if __name__ == "__main__":
    print("Starting SystemVerilog generator tests...\n")
    test_with_all_features()
    test_with_error_rate_tracking_variations()
    print("\nAll tests completed!")
