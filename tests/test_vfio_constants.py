#!/usr/bin/env python3
"""Unit tests for the VFIO constants module.

This test suite ensures that all VFIO constants are properly defined,
have correct values, and that the module can be imported without errors.
"""

import ctypes

import pytest

from src.cli.vfio_constants import (VFIO_CHECK_EXTENSION,
                                    VFIO_DEVICE_GET_REGION_INFO,
                                    VFIO_DEVICE_NAME_MAX_LENGTH,
                                    VFIO_GET_API_VERSION,
                                    VFIO_GROUP_FLAGS_CONTAINER_SET,
                                    VFIO_GROUP_FLAGS_VIABLE,
                                    VFIO_GROUP_GET_DEVICE_FD,
                                    VFIO_GROUP_GET_STATUS,
                                    VFIO_GROUP_SET_CONTAINER,
                                    VFIO_REGION_INFO_FLAG_MMAP,
                                    VFIO_REGION_INFO_FLAG_READ,
                                    VFIO_REGION_INFO_FLAG_WRITE,
                                    VFIO_SET_IOMMU, VFIO_TYPE,
                                    VFIO_TYPE1_IOMMU, VfioGroupStatus,
                                    VfioRegionInfo, vfio_group_status,
                                    vfio_region_info)


class TestVFIOConstants:
    """Test suite for VFIO constants."""

    def test_vfio_device_name_max_length_defined(self):
        """Test that VFIO_DEVICE_NAME_MAX_LENGTH is defined and has a reasonable value."""
        assert VFIO_DEVICE_NAME_MAX_LENGTH is not None
        assert isinstance(VFIO_DEVICE_NAME_MAX_LENGTH, int)
        assert VFIO_DEVICE_NAME_MAX_LENGTH > 0
        assert VFIO_DEVICE_NAME_MAX_LENGTH <= 512  # Reasonable upper bound

    def test_vfio_type_constant(self):
        """Test that VFIO_TYPE is properly defined."""
        assert VFIO_TYPE == ord(";")
        assert isinstance(VFIO_TYPE, int)

    def test_vfio_iommu_constants(self):
        """Test VFIO IOMMU related constants."""
        assert VFIO_TYPE1_IOMMU == 1
        assert isinstance(VFIO_TYPE1_IOMMU, int)

    def test_vfio_region_flags(self):
        """Test VFIO region info flags."""
        assert VFIO_REGION_INFO_FLAG_READ == (1 << 0)
        assert VFIO_REGION_INFO_FLAG_WRITE == (1 << 1)
        assert VFIO_REGION_INFO_FLAG_MMAP == (1 << 2)

    def test_vfio_group_flags(self):
        """Test VFIO group flags."""
        assert VFIO_GROUP_FLAGS_VIABLE == (1 << 0)
        assert VFIO_GROUP_FLAGS_CONTAINER_SET == (1 << 1)

    def test_ioctl_constants_are_integers(self):
        """Test that all IOCTL constants are integers."""
        ioctl_constants = [
            VFIO_GET_API_VERSION,
            VFIO_CHECK_EXTENSION,
            VFIO_SET_IOMMU,
            VFIO_GROUP_GET_STATUS,
            VFIO_GROUP_SET_CONTAINER,
            VFIO_GROUP_GET_DEVICE_FD,
            VFIO_DEVICE_GET_REGION_INFO,
        ]

        for const in ioctl_constants:
            assert isinstance(const, int)
            assert const > 0

    def test_vfio_structures_defined(self):
        """Test that VFIO structures are properly defined."""
        # Test vfio_group_status
        assert hasattr(vfio_group_status, "_fields_")
        assert len(vfio_group_status._fields_) == 2

        status = vfio_group_status()
        assert hasattr(status, "argsz")
        assert hasattr(status, "flags")

        # Test vfio_region_info
        assert hasattr(vfio_region_info, "_fields_")
        assert len(vfio_region_info._fields_) == 6

        region = vfio_region_info()
        assert hasattr(region, "argsz")
        assert hasattr(region, "flags")
        assert hasattr(region, "index")
        assert hasattr(region, "cap_offset")
        assert hasattr(region, "size")
        assert hasattr(region, "offset")

    def test_legacy_aliases(self):
        """Test that legacy aliases are properly defined."""
        assert VfioGroupStatus is vfio_group_status
        assert VfioRegionInfo is vfio_region_info

    def test_structure_sizes(self):
        """Test that structures have expected sizes."""
        # vfio_group_status should have 2 uint32 fields = 8 bytes
        status = vfio_group_status()
        assert ctypes.sizeof(status) == 8

        # vfio_region_info should have 4 uint32 + 2 uint64 fields = 32 bytes
        region = vfio_region_info()
        assert ctypes.sizeof(region) == 32

    def test_ioctl_encoding(self):
        """Test that IOCTL values are encoded correctly."""
        # VFIO_GET_API_VERSION should be _IO(VFIO_TYPE, 0)
        # This is a basic sanity check that the encoding produces non-zero values
        assert VFIO_GET_API_VERSION != 0

        # Check that different IOCTLs have different values
        ioctl_values = {
            VFIO_GET_API_VERSION,
            VFIO_CHECK_EXTENSION,
            VFIO_SET_IOMMU,
            VFIO_GROUP_GET_STATUS,
            VFIO_GROUP_SET_CONTAINER,
            VFIO_GROUP_GET_DEVICE_FD,
            VFIO_DEVICE_GET_REGION_INFO,
        }
        assert len(ioctl_values) == 7  # All values should be unique

    def test_module_imports_without_errors(self):
        """Test that the module can be imported without any errors."""
        # This test passes if we get here without import errors
        import src.cli.vfio_constants

        assert src.cli.vfio_constants is not None

    def test_all_exports(self):
        """Test that __all__ exports are properly defined."""
        from src.cli import vfio_constants

        # Check that __all__ is defined
        assert hasattr(vfio_constants, "__all__")
        assert isinstance(vfio_constants.__all__, list)

        # Check that all exported names exist
        for name in vfio_constants.__all__:
            assert hasattr(
                vfio_constants, name
            ), f"Exported name '{name}' not found in module"

        # Check that VFIO_DEVICE_NAME_MAX_LENGTH is in exports
        assert "VFIO_DEVICE_NAME_MAX_LENGTH" in vfio_constants.__all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
