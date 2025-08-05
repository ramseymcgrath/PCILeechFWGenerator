#!/usr/bin/env python3
"""Test script to verify the advanced_controller template renders without errors."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from templating.systemverilog_generator import SystemVerilogGenerator
from device_clone.device_config import DeviceConfig, DeviceType, DeviceClass
from templating.advanced_sv_perf import PerformanceConfig
from templating.advanced_sv_power import PowerManagementConfig
from templating.advanced_sv_error import ErrorHandlingConfig


def test_advanced_controller_rendering():
    """Test that advanced_controller template renders without undefined variable errors."""

    # Create a basic device config
    device_config = DeviceConfig(
        device_type=DeviceType.NETWORK,
        device_class=DeviceClass.NETWORK_CONTROLLER,
        vendor_id=0x10EE,
        device_id=0x0001,
        subsystem_vendor_id=0x10EE,
        subsystem_id=0x0001,
        max_payload_size=256,
        msi_vectors=4,
    )

    # Create performance config with enable_error_rate_tracking
    perf_config = PerformanceConfig(
        enable_transaction_counters=True,
        enable_bandwidth_monitoring=True,
        enable_latency_measurement=True,
        enable_error_rate_tracking=True,
        enable_device_specific_counters=True,
    )

    # Create other configs
    power_config = PowerManagementConfig()
    error_config = ErrorHandlingConfig()

    # Create the generator
    generator = SystemVerilogGenerator(
        device_config=device_config,
        power_config=power_config,
        error_config=error_config,
        perf_config=perf_config,
    )

    try:
        # Generate advanced SystemVerilog - this should not raise an error
        result = generator.generate_advanced_systemverilog()

        # Check that the result contains expected content
        assert "advanced_pcileech_controller" in result
        assert "Error Rate Tracking Logic" in result or "error_rate" in result

        print("✅ SUCCESS: Advanced controller template rendered without errors!")
        print(f"Generated module size: {len(result)} characters")

        # Check for the specific error tracking content
        if "enable_error_rate_tracking" in result:
            print("✅ Found enable_error_rate_tracking in generated output")

        return True

    except Exception as e:
        print(f"❌ ERROR: Failed to render template: {e}")
        if "'enable_error_rate_tracking' is undefined" in str(e):
            print("❌ The original error still exists - fix did not work")
        else:
            print(f"❌ Different error occurred: {type(e).__name__}")
        return False


if __name__ == "__main__":
    success = test_advanced_controller_rendering()
    sys.exit(0 if success else 1)
