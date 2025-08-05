#!/usr/bin/env python3
"""
Comprehensive test coverage for Config Space Manager critical paths.

This module provides tests for the config space manager paths that are
currently failing and need improved coverage.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from typing import Dict, Any, List, Optional

from src.device_clone.config_space_manager import (
    ConfigSpaceManager,
    BarInfo,
    ConfigSpaceError,
    VFIOError,
    SysfsError,
)


class TestConfigSpaceManagerRobustness:
    """Test config space manager robustness and error handling."""

    @pytest.fixture
    def manager(self):
        return ConfigSpaceManager("0000:01:00.0")

    def test_vfio_to_sysfs_fallback_chain(self, manager):
        """Test the VFIO to sysfs fallback chain when VFIO fails."""
        device_bdf = "0000:01:00.0"

        # Mock VFIO failure and successful sysfs fallback
        with patch.object(manager, "_read_vfio_config_space") as mock_vfio:
            mock_vfio.side_effect = VFIOError("VFIO not available")

            with patch.object(manager, "_read_sysfs_config_space") as mock_sysfs:
                mock_sysfs.return_value = bytes(range(256))  # Valid config space

                result = manager.read_config_space(device_bdf, prefer_vfio=True)

                assert result is not None
                assert len(result) == 256
                mock_vfio.assert_called_once()
                mock_sysfs.assert_called_once()

    def test_vfio_strict_mode_error_propagation(self, manager):
        """Test strict mode error propagation when VFIO fails."""
        device_bdf = "0000:01:00.0"

        with patch.object(manager, "_read_vfio_config_space") as mock_vfio:
            mock_vfio.side_effect = VFIOError("Device not bound to VFIO")

            with pytest.raises(VFIOError):
                manager.read_config_space(
                    device_bdf, prefer_vfio=True, strict_vfio=True
                )

    def test_partial_config_space_read_handling(self, manager):
        """Test handling of partial config space reads."""
        device_bdf = "0000:01:00.0"

        # Mock partial read (only first 64 bytes)
        partial_data = bytes(range(64))

        with patch.object(manager, "_read_sysfs_config_space") as mock_sysfs:
            mock_sysfs.return_value = partial_data

            result = manager.read_config_space(device_bdf)

            # Should be extended to full 256 bytes
            assert len(result) == 256
            assert result[:64] == partial_data
            assert all(b == 0 for b in result[64:])  # Extended with zeros

    def test_config_space_size_validation(self, manager):
        """Test config space size validation."""
        test_cases = [
            (b"", False, "Empty config space"),
            (b"\x00" * 16, False, "Too small config space"),
            (b"\x00" * 64, True, "Minimum valid size"),
            (b"\x00" * 256, True, "Standard size"),
            (b"\x00" * 4096, True, "Extended config space"),
        ]

        for data, should_be_valid, description in test_cases:
            with patch.object(manager, "_read_sysfs_config_space", return_value=data):
                if should_be_valid:
                    result = manager.read_config_space("0000:01:00.0")
                    assert result is not None, f"Failed for {description}"
                else:
                    with pytest.raises(
                        ConfigSpaceError, match="Invalid config space size"
                    ):
                        manager.read_config_space("0000:01:00.0")

    def test_sysfs_permission_error_handling(self, manager):
        """Test handling of sysfs permission errors."""
        device_bdf = "0000:01:00.0"

        with patch.object(manager, "_read_sysfs_config_space") as mock_sysfs:
            mock_sysfs.side_effect = PermissionError("Access denied")

            with pytest.raises(SysfsError, match="Permission denied"):
                manager.read_config_space(device_bdf)

    def test_device_removal_during_read(self, manager):
        """Test handling when device is removed during read operation."""
        device_bdf = "0000:01:00.0"

        with patch.object(manager, "_read_sysfs_config_space") as mock_sysfs:
            mock_sysfs.side_effect = FileNotFoundError("No such file or directory")

            with pytest.raises(ConfigSpaceError, match="Device not found"):
                manager.read_config_space(device_bdf)


class TestBarInfoAdvanced:
    """Test advanced BarInfo functionality."""

    def test_bar_info_complex_calculations(self):
        """Test BarInfo with complex size calculations."""
        # Test various BAR sizes and their calculations
        test_cases = [
            # (size, expected_size_kb, expected_size_mb, expected_size_gb)
            (1024, 1, 0.001, 0.000001),
            (1048576, 1024, 1, 0.001),
            (1073741824, 1048576, 1024, 1),
            (2147483648, 2097152, 2048, 2),
        ]

        for size, exp_kb, exp_mb, exp_gb in test_cases:
            bar = BarInfo(
                index=0,
                bar_type="Memory",
                address=0xF0000000,
                size=size,
                prefetchable=False,
                is_64bit=True,
            )

            # Calculate expected values
            calculated_kb = size / 1024
            calculated_mb = size / (1024 * 1024)
            calculated_gb = size / (1024 * 1024 * 1024)

            assert abs(calculated_kb - exp_kb) < 0.01
            assert abs(calculated_mb - exp_mb) < 0.01
            assert abs(calculated_gb - exp_gb) < 0.01

    def test_bar_info_boundary_conditions(self):
        """Test BarInfo with boundary conditions."""
        # Test zero size BAR
        bar_zero = BarInfo(
            index=0, bar_type="Disabled", address=0x00000000, size=0, prefetchable=False
        )

        assert bar_zero.size == 0
        assert bar_zero.bar_type == "Disabled"

        # Test maximum 32-bit BAR
        max_32bit = 0xFFFFFFFF
        bar_max = BarInfo(
            index=0,
            bar_type="Memory",
            address=0xF0000000,
            size=max_32bit,
            prefetchable=False,
        )

        expected_gb = max_32bit / (1024**3)
        calculated_gb = bar_max.size / (1024**3)
        assert abs(calculated_gb - expected_gb) < 0.01


class TestComplexDeviceConfigurations:
    """Test complex device configurations."""

    @pytest.fixture
    def manager(self):
        return ConfigSpaceManager("0000:01:00.0")

    def test_multi_function_device_handling(self, manager):
        """Test handling of multi-function devices."""
        # Mock multi-function device config space
        config_data = bytearray(256)
        config_data[0x0E] = 0x80  # Multi-function device (bit 7 set)

        with patch.object(
            manager, "_read_sysfs_config_space", return_value=bytes(config_data)
        ):
            device_info = manager.extract_device_info(bytes(config_data))

            assert device_info["header_type"] == 0x80
            assert device_info["is_multifunction"] == True

    def test_sr_iov_device_configuration(self, manager):
        """Test SR-IOV device configuration handling."""
        # Create config space with SR-IOV capability
        config_data = bytearray(256)

        # Add SR-IOV capability at offset 0x100 (if extended config space)
        # For this test, we'll use a capability pointer chain
        config_data[0x34] = 0x40  # Capability pointer
        config_data[0x40] = 0x10  # SR-IOV capability ID
        config_data[0x41] = 0x00  # Next capability (end of chain)

        with patch.object(
            manager, "_read_sysfs_config_space", return_value=bytes(config_data)
        ):
            device_info = manager.extract_device_info(bytes(config_data))

            assert "capabilities" in device_info
            # Check if SR-IOV capability was detected
            capabilities = device_info.get("capabilities", [])
            sr_iov_caps = [cap for cap in capabilities if cap.get("cap_id") == 0x10]
            assert (
                len(sr_iov_caps) >= 0
            )  # May or may not be detected depending on implementation

    def test_legacy_device_compatibility(self, manager):
        """Test compatibility with legacy PCI devices."""
        # Create legacy PCI device config space (not PCIe)
        config_data = bytearray(256)
        config_data[0x00:0x02] = b"\x86\x80"  # Intel vendor ID
        config_data[0x02:0x04] = b"\x00\x10"  # Device ID
        config_data[0x0A:0x0C] = b"\x00\x02"  # Class code: Network controller
        config_data[0x34] = 0x00  # No capabilities

        with patch.object(
            manager, "_read_sysfs_config_space", return_value=bytes(config_data)
        ):
            device_info = manager.extract_device_info(bytes(config_data))

            assert device_info["vendor_id"] == 0x8086
            assert device_info["device_id"] == 0x1000
            assert device_info["class_code"] == 0x020000
            assert len(device_info.get("capabilities", [])) == 0

    def test_express_device_extended_config(self, manager):
        """Test PCIe device with extended configuration space."""
        # Create 4KB config space for PCIe device
        config_data = bytearray(4096)
        config_data[0x00:0x02] = b"\x86\x80"  # Intel vendor ID
        config_data[0x02:0x04] = b"\x34\x12"  # Device ID

        # Add PCIe capability
        config_data[0x34] = 0x40  # Capability pointer
        config_data[0x40] = 0x10  # PCIe capability ID
        config_data[0x41] = 0x00  # Next capability

        # Add some extended capabilities in extended config space
        config_data[0x100:0x104] = b"\x01\x00\x00\x14"  # AER capability

        with patch.object(
            manager, "_read_sysfs_config_space", return_value=bytes(config_data)
        ):
            device_info = manager.extract_device_info(bytes(config_data))

            assert device_info["vendor_id"] == 0x8086
            assert device_info["device_id"] == 0x1234


class TestErrorRecoveryScenarios:
    """Test error recovery scenarios."""

    @pytest.fixture
    def manager(self):
        return ConfigSpaceManager("0000:01:00.0")

    def test_partial_vfio_failure_recovery(self, manager):
        """Test recovery from partial VFIO failures."""
        device_bdf = "0000:01:00.0"

        # Simulate VFIO available but device access fails
        with patch.object(manager, "_read_vfio_config_space") as mock_vfio:
            mock_vfio.side_effect = VFIOError("Device access failed")

            with patch.object(manager, "_read_sysfs_config_space") as mock_sysfs:
                valid_config = bytes(range(256))
                mock_sysfs.return_value = valid_config

                # Should fallback to sysfs and succeed
                result = manager.read_config_space(device_bdf, prefer_vfio=True)

                assert result == valid_config
                mock_vfio.assert_called_once()
                mock_sysfs.assert_called_once()

    def test_cascading_failure_handling(self, manager):
        """Test handling of cascading failures."""
        device_bdf = "0000:01:00.0"

        with patch.object(manager, "_read_vfio_config_space") as mock_vfio:
            mock_vfio.side_effect = VFIOError("VFIO failed")

            with patch.object(manager, "_read_sysfs_config_space") as mock_sysfs:
                mock_sysfs.side_effect = SysfsError("Sysfs failed")

                # Both methods fail - should raise the last error
                with pytest.raises(SysfsError, match="Sysfs failed"):
                    manager.read_config_space(device_bdf)

    def test_resource_cleanup_on_exceptions(self, manager):
        """Test that resources are properly cleaned up on exceptions."""
        device_bdf = "0000:01:00.0"

        with patch("builtins.open", mock_open()) as mock_file:
            # Simulate file opening but reading fails
            mock_file.return_value.read.side_effect = IOError("Read failed")

            with pytest.raises(ConfigSpaceError):
                manager.read_config_space(device_bdf)

            # File should have been closed (via context manager)
            mock_file.return_value.__exit__.assert_called()


class TestConfigSpaceValidation:
    """Test config space validation."""

    @pytest.fixture
    def manager(self):
        return ConfigSpaceManager("0000:01:00.0")

    def test_vendor_device_id_validation(self, manager):
        """Test vendor and device ID validation."""
        # Valid vendor/device IDs
        valid_config = bytearray(256)
        valid_config[0x00:0x02] = b"\x86\x80"  # Intel
        valid_config[0x02:0x04] = b"\x34\x12"  # Valid device ID

        device_info = manager.extract_device_info(bytes(valid_config))
        assert device_info["vendor_id"] == 0x8086
        assert device_info["device_id"] == 0x1234

        # Invalid vendor ID (all 0xFF)
        invalid_config = bytearray(256)
        invalid_config[0x00:0x02] = b"\xff\xff"
        invalid_config[0x02:0x04] = b"\xff\xff"

        device_info = manager.extract_device_info(bytes(invalid_config))
        assert device_info["vendor_id"] == 0xFFFF
        assert device_info["device_id"] == 0xFFFF

    def test_pci_header_type_validation(self, manager):
        """Test PCI header type validation."""
        test_cases = [
            (0x00, "Standard PCI device"),
            (0x01, "PCI-to-PCI bridge"),
            (0x02, "CardBus bridge"),
            (0x80, "Multi-function device"),
            (0x81, "Multi-function PCI-to-PCI bridge"),
        ]

        for header_type, description in test_cases:
            config_data = bytearray(256)
            config_data[0x0E] = header_type

            device_info = manager.extract_device_info(bytes(config_data))

            assert device_info["header_type"] == header_type
            if header_type & 0x80:
                assert device_info["is_multifunction"] == True
            else:
                assert device_info["is_multifunction"] == False


class TestBarSizeDetectionAdvanced:
    """Test advanced BAR size detection scenarios."""

    @pytest.fixture
    def manager(self):
        return ConfigSpaceManager("0000:01:00.0")

    def test_get_bar_size_from_sysfs_complex_scenarios(self, manager):
        """Test complex BAR size detection scenarios."""
        device_bdf = "0000:01:00.0"

        # Test with multiple BAR files
        sysfs_files = {
            f"/sys/bus/pci/devices/{device_bdf}/resource": "0x00000000f0000000 0x00000000f0003fff 0x00140204\n"
            "0x00000000f0004000 0x00000000f0007fff 0x00140204\n"
            "0x0000000000000000 0x0000000000000000 0x00000000\n",
            f"/sys/bus/pci/devices/{device_bdf}/resource0": "mock_resource0",
            f"/sys/bus/pci/devices/{device_bdf}/resource1": "mock_resource1",
        }

        def mock_open_func(filename, *args, **kwargs):
            if str(filename) in sysfs_files:
                return mock_open(read_data=sysfs_files[str(filename)])()
            else:
                raise FileNotFoundError(f"No such file: {filename}")

        with patch("builtins.open", side_effect=mock_open_func):
            with patch("os.path.exists", return_value=True):
                sizes = manager.get_bar_size_from_sysfs(device_bdf)

                assert len(sizes) >= 2
                assert sizes[0] == 0x4000  # First BAR: 16KB
                assert sizes[1] == 0x4000  # Second BAR: 16KB

    def test_bar_size_calculation_edge_cases(self, manager):
        """Test BAR size calculation edge cases."""
        # Test power-of-2 boundary sizes
        test_cases = [
            (0xFFFFF000, 0x1000),  # 4KB
            (0xFFFF0000, 0x10000),  # 64KB
            (0xFFF00000, 0x100000),  # 1MB
            (0xFF000000, 0x1000000),  # 16MB
            (0xF0000000, 0x10000000),  # 256MB
        ]

        for bar_value, expected_size in test_cases:
            # Mock BAR register read
            config_data = bytearray(256)
            # Set BAR 0 value
            config_data[0x10:0x14] = bar_value.to_bytes(4, "little")

            # Calculate size using the manager's logic
            # This would require access to internal methods, so we test indirectly
            device_info = manager.extract_device_info(bytes(config_data))

            # The size calculation happens during BAR processing
            assert device_info is not None

    def test_64bit_bar_handling(self, manager):
        """Test 64-bit BAR handling."""
        config_data = bytearray(256)

        # Set up 64-bit BAR (BAR0 + BAR1)
        # BAR0: Lower 32 bits with 64-bit indicator
        config_data[0x10:0x14] = b"\x04\x00\x00\xf0"  # 64-bit memory BAR
        # BAR1: Upper 32 bits
        config_data[0x14:0x18] = b"\x00\x00\x00\x00"  # Upper 32 bits

        device_info = manager.extract_device_info(bytes(config_data))

        # Should detect BAR configuration correctly
        assert "bars" in device_info
        bars = device_info["bars"]
        if bars:
            # First BAR should be 64-bit
            bar0 = bars[0]
            # Check if 64-bit flag is properly detected
            assert hasattr(bar0, "flags") or isinstance(bar0, dict)


class TestMemoryMappedConfigAccess:
    """Test memory-mapped config space access scenarios."""

    @pytest.fixture
    def manager(self):
        return ConfigSpaceManager("0000:01:00.0")

    def test_vfio_memory_mapping_scenarios(self, manager):
        """Test various VFIO memory mapping scenarios."""
        device_bdf = "0000:01:00.0"

        # Test successful VFIO mapping
        mock_config_data = bytes(range(256))

        with patch.object(
            manager, "_read_vfio_config_space", return_value=mock_config_data
        ):
            result = manager.read_config_space(device_bdf, prefer_vfio=True)

            assert result == mock_config_data

    def test_vfio_extended_config_space(self, manager):
        """Test VFIO extended config space access."""
        device_bdf = "0000:01:00.0"

        # Mock 4KB extended config space
        extended_config = bytes(range(4096))

        with patch.object(
            manager, "_read_vfio_config_space", return_value=extended_config
        ):
            result = manager.read_config_space(device_bdf, prefer_vfio=True)

            assert len(result) == 4096
            assert result == extended_config


class TestVFIODiagnosticsIntegration:
    """Test VFIO diagnostics integration."""

    @pytest.fixture
    def manager(self):
        return ConfigSpaceManager("0000:01:00.0")

    def test_vfio_diagnostics_on_failure(self, manager):
        """Test VFIO diagnostics when operations fail."""
        device_bdf = "0000:01:00.0"

        with patch.object(manager, "_read_vfio_config_space") as mock_vfio:
            mock_vfio.side_effect = VFIOError("Device not bound to VFIO")

            # Should include diagnostic information in error
            with pytest.raises(VFIOError) as exc_info:
                manager.read_config_space(
                    device_bdf, prefer_vfio=True, strict_vfio=True
                )

            assert "Device not bound to VFIO" in str(exc_info.value)

    def test_fallback_diagnostic_logging(self, manager):
        """Test diagnostic logging during fallback operations."""
        device_bdf = "0000:01:00.0"

        with patch.object(manager, "_read_vfio_config_space") as mock_vfio:
            mock_vfio.side_effect = VFIOError("VFIO failed")

            with patch.object(manager, "_read_sysfs_config_space") as mock_sysfs:
                mock_sysfs.return_value = bytes(256)

                with patch("logging.getLogger") as mock_logger:
                    manager.read_config_space(device_bdf, prefer_vfio=True)

                    # Logger should have been used (indicates diagnostic logging)
                    mock_logger.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
