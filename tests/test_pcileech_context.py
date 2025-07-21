#!/usr/bin/env python3
"""
Comprehensive unit tests for PCILeech context builder module.

This test suite covers the critical PCILeechContextBuilder class which handles
core device cloning logic and VFIO device interaction. Tests include:
- Context builder initialization and configuration
- build_context() main context generation
- VFIO device file descriptor handling
- BAR memory mapping operations
- Configuration space reading
- Error handling and resource cleanup
- Integration with related components
"""

import ctypes
import fcntl
import hashlib
import os
import struct
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest

from src.cli.vfio_constants import (
    VFIO_DEVICE_GET_REGION_INFO,
    VFIO_GROUP_GET_DEVICE_FD,
    VFIO_REGION_INFO_FLAG_MMAP,
    VFIO_REGION_INFO_FLAG_READ,
    VFIO_REGION_INFO_FLAG_WRITE,
    VfioRegionInfo,
)
from src.device_clone.behavior_profiler import BehaviorProfile
from src.device_clone.config_space_manager import BarInfo
from src.device_clone.fallback_manager import FallbackManager
from src.device_clone.overlay_mapper import OverlayMapper
from src.device_clone.pcileech_context import (
    BarConfiguration,
    ContextError,
    DeviceIdentifiers,
    PCILeechContextBuilder,
    TimingParameters,
    ValidationLevel,
)


# Test fixtures for common data structures
@pytest.fixture
def mock_config():
    """Mock configuration object."""
    from src.device_clone.device_config import DeviceCapabilities

    config = Mock()
    config.enable_advanced_features = True
    config.enable_dma_operations = True
    config.enable_interrupt_coalescing = False
    config.pcileech_command_timeout = 5000
    config.pcileech_buffer_size = 4096
    config.device_config = Mock()

    # Create a mock that passes isinstance check
    capabilities_mock = Mock(spec=DeviceCapabilities)
    capabilities_mock.ext_cfg_cap_ptr = 0x100
    capabilities_mock.ext_cfg_xp_cap_ptr = 0x140
    capabilities_mock.max_payload_size = 256
    capabilities_mock.get_cfg_force_mps = Mock(return_value=1)
    capabilities_mock.check_tiny_pcie_issues = Mock(return_value=(False, ""))
    capabilities_mock.active_device = Mock(
        enabled=True,
        timer_period=100000,
        timer_enable=1,
        interrupt_mode="msix",
        interrupt_vector=0,
        priority=15,
        msi_vector_width=5,
        msi_64bit_addr=True,
        num_interrupt_sources=8,
        default_source_priority=8,
    )

    config.device_config.capabilities = capabilities_mock
    return config


@pytest.fixture
def device_identifiers():
    """Valid device identifiers fixture."""
    return DeviceIdentifiers(
        vendor_id="10ee",
        device_id="7024",
        class_code="020000",
        revision_id="01",
        subsystem_vendor_id="10ee",
        subsystem_device_id="0007",
    )


@pytest.fixture
def config_space_data():
    """Mock configuration space data."""
    return {
        "vendor_id": "10ee",
        "device_id": "7024",
        "class_code": "020000",
        "revision_id": "01",
        "subsystem_vendor_id": "10ee",
        "subsystem_device_id": "0007",
        "config_space_hex": "ee10247000000000" * 512,  # 4KB of mock data
        "config_space_size": 4096,
        "bars": [
            {
                "type": "memory",
                "address": 0xF7000000,
                "size": 65536,
                "prefetchable": False,
                "is_64bit": False,
            },
            {
                "type": "memory",
                "address": 0xF7100000,
                "size": 16384,
                "prefetchable": True,
                "is_64bit": True,
            },
            {
                "type": "io",
                "address": 0x3000,
                "size": 256,
                "prefetchable": False,
                "is_64bit": False,
            },
        ],
        "dword_map": {i: f"0x{i*4:08x}" for i in range(1024)},  # Mock dword map
        "capabilities": {
            "msi": {"offset": 0x50},
            "msix": {"offset": 0x70},
            "pcie": {"offset": 0x80},
        },
        "device_info": {"description": "Test Network Controller"},
    }


@pytest.fixture
def msix_data():
    """Mock MSI-X capability data."""
    return {
        "capability_info": {
            "table_size": 32,
            "table_bir": 0,
            "table_offset": 0x2000,
            "pba_bir": 0,
            "pba_offset": 0x3000,
            "enabled": True,
            "function_mask": False,
        },
        "validation_errors": [],
        "is_valid": True,
    }


@pytest.fixture
def behavior_profile():
    """Mock behavior profile."""
    from src.device_clone.behavior_profiler import (
        BehaviorProfile,
        RegisterAccess,
        TimingPattern,
    )

    return BehaviorProfile(
        device_bdf="0000:03:00.0",
        capture_duration=60.0,
        total_accesses=1500,
        register_accesses=[
            RegisterAccess(
                timestamp=0.1,
                register="BAR0",
                offset=0x100,
                operation="read",
                value=0x12345678,
                duration_us=10.0,
            ),
            RegisterAccess(
                timestamp=0.2,
                register="BAR0",
                offset=0x200,
                operation="write",
                value=0xABCDEF00,
                duration_us=15.0,
            ),
        ],
        timing_patterns=[
            TimingPattern(
                pattern_type="periodic",
                registers=["BAR0"],
                avg_interval_us=50.0,
                std_deviation_us=5.0,
                frequency_hz=20000.0,
                confidence=0.95,
            ),
            TimingPattern(
                pattern_type="burst",
                registers=["BAR1"],
                avg_interval_us=100.0,
                std_deviation_us=10.0,
                frequency_hz=10000.0,
                confidence=0.90,
            ),
        ],
        state_transitions={
            "idle": ["active"],
            "active": ["idle", "busy"],
            "busy": ["active"],
        },
        power_states=["D0", "D3hot"],
        interrupt_patterns={"msi": {"frequency": 1000, "burst": False}},
        variance_metadata={"variance": 0.05},
        pattern_analysis={"burst_detected": True},
    )


@pytest.fixture
def vfio_region_info():
    """Mock VFIO region info structure."""
    info = Mock()
    info.argsz = 32
    info.index = 0
    info.flags = (
        VFIO_REGION_INFO_FLAG_READ
        | VFIO_REGION_INFO_FLAG_WRITE
        | VFIO_REGION_INFO_FLAG_MMAP
    )
    info.size = 65536
    return info


class TestPCILeechContextBuilder:
    """Test suite for PCILeechContextBuilder class."""

    def test_initialization_valid(self, mock_config):
        """Test valid initialization of context builder."""
        builder = PCILeechContextBuilder(
            device_bdf="0000:03:00.0",
            config=mock_config,
            validation_level=ValidationLevel.STRICT,
        )

        assert builder.device_bdf == "0000:03:00.0"
        assert builder.config == mock_config
        assert builder.validation_level == ValidationLevel.STRICT
        assert isinstance(builder.fallback_manager, FallbackManager)

    def test_initialization_empty_bdf(self, mock_config):
        """Test initialization with empty BDF raises error."""
        with pytest.raises(ContextError, match="Device BDF cannot be empty"):
            PCILeechContextBuilder(device_bdf="", config=mock_config)

    def test_initialization_with_fallback_manager(self, mock_config):
        """Test initialization with custom fallback manager."""
        fallback_manager = FallbackManager(mode="auto", allowed_fallbacks=["all"])
        builder = PCILeechContextBuilder(
            device_bdf="0000:03:00.0",
            config=mock_config,
            fallback_manager=fallback_manager,
        )

        assert builder.fallback_manager == fallback_manager

    @patch("src.device_clone.pcileech_context.OverlayMapper")
    def test_build_context_success(
        self,
        mock_overlay_mapper,
        mock_config,
        device_identifiers,
        config_space_data,
        msix_data,
        behavior_profile,
    ):
        """Test successful context building with all data available."""
        # Setup overlay mapper mock
        mock_overlay_instance = Mock()
        mock_overlay_instance.generate_overlay_map.return_value = {
            "OVERLAY_MAP": [(0, 0xFFFFFFFF), (1, 0x0000FFFF)],
            "OVERLAY_ENTRIES": 2,
        }
        mock_overlay_mapper.return_value = mock_overlay_instance

        builder = PCILeechContextBuilder(
            device_bdf="0000:03:00.0",
            config=mock_config,
            validation_level=ValidationLevel.STRICT,
        )

        # Mock internal methods
        builder._extract_device_identifiers = Mock(return_value=device_identifiers)
        builder._build_device_config = Mock(
            return_value={
                "vendor_id": "10ee",
                "device_id": "7024",
                "class_code": "020000",
                "revision_id": "01",
                "subsystem_vendor_id": "10ee",
                "subsystem_device_id": "0007",
            }
        )
        builder._build_config_space_context = Mock(
            return_value={"config_space": "test"}
        )
        builder._build_msix_context = Mock(return_value={"msix": "test"})
        builder._build_bar_config = Mock(
            return_value={"bars": [{"type": "memory", "size": 1024}]}
        )
        builder._build_timing_config = Mock(
            return_value=TimingParameters(
                read_latency=4,
                write_latency=2,
                burst_length=16,
                inter_burst_gap=8,
                timeout_cycles=1024,
                clock_frequency_mhz=100.0,
                timing_regularity=0.9,
            )
        )
        builder._build_pcileech_config = Mock(return_value={"pcileech": "test"})
        builder._build_active_device_config = Mock(return_value={"active": "test"})
        builder._generate_unique_device_signature = Mock(return_value="32'h12345678")
        builder._build_generation_metadata = Mock(return_value={"metadata": "test"})

        context = builder.build_context(
            behavior_profile=behavior_profile,
            config_space_data=config_space_data,
            msix_data=msix_data,
            interrupt_strategy="msix",
            interrupt_vectors=32,
        )

        # Verify context structure
        assert "device_config" in context
        assert "config_space" in context
        assert "msix_config" in context
        assert "bar_config" in context
        assert "timing_config" in context
        assert "pcileech_config" in context
        assert "device_signature" in context
        assert "generation_metadata" in context
        assert "interrupt_config" in context
        assert "active_device_config" in context
        assert "EXT_CFG_CAP_PTR" in context
        assert "EXT_CFG_XP_CAP_PTR" in context
        assert "OVERLAY_MAP" in context
        assert "OVERLAY_ENTRIES" in context

        # Verify interrupt config
        assert context["interrupt_config"]["strategy"] == "msix"
        assert context["interrupt_config"]["vectors"] == 32
        assert context["interrupt_config"]["msix_available"] is True

    def test_build_context_missing_required_data(self, mock_config):
        """Test context building fails with missing required data."""
        builder = PCILeechContextBuilder(
            device_bdf="0000:03:00.0",
            config=mock_config,
            validation_level=ValidationLevel.STRICT,
        )

        # Missing vendor_id in config_space_data
        invalid_config_space = {
            "device_id": "7024",
            "class_code": "020000",
            "revision_id": "01",
        }

        with pytest.raises(ContextError, match="Missing required data"):
            builder.build_context(
                behavior_profile=None,
                config_space_data=invalid_config_space,
                msix_data=None,
            )

    def test_validate_input_data_strict(self, mock_config, config_space_data):
        """Test strict validation of input data."""
        builder = PCILeechContextBuilder(
            device_bdf="0000:03:00.0",
            config=mock_config,
            validation_level=ValidationLevel.STRICT,
        )

        # Remove required field
        del config_space_data["vendor_id"]

        with pytest.raises(ContextError, match="Missing required data"):
            builder._validate_input_data(config_space_data, None, None)

    def test_validate_input_data_permissive(self, mock_config, config_space_data):
        """Test permissive validation allows missing data with warnings."""
        builder = PCILeechContextBuilder(
            device_bdf="0000:03:00.0",
            config=mock_config,
            validation_level=ValidationLevel.PERMISSIVE,
        )

        # Remove required field
        del config_space_data["vendor_id"]

        # Should not raise, just log warnings
        builder._validate_input_data(config_space_data, None, None)

    def test_extract_device_identifiers_success(self, mock_config, config_space_data):
        """Test successful extraction of device identifiers."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        identifiers = builder._extract_device_identifiers(config_space_data)

        assert identifiers.vendor_id == "10ee"
        assert identifiers.device_id == "7024"
        assert identifiers.class_code == "020000"
        assert identifiers.revision_id == "01"
        assert identifiers.subsystem_vendor_id == "10ee"
        assert identifiers.subsystem_device_id == "0007"

    def test_extract_device_identifiers_missing_subsystem(self, mock_config):
        """Test extraction with missing subsystem IDs falls back to main IDs."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        config_data = {
            "vendor_id": "10ee",
            "device_id": "7024",
            "class_code": "020000",
            "revision_id": "01",
            "subsystem_vendor_id": None,
            "subsystem_device_id": 0,
        }

        identifiers = builder._extract_device_identifiers(config_data)

        # Should fall back to main IDs
        assert identifiers.subsystem_vendor_id == "10ee"
        assert identifiers.subsystem_device_id == "7024"

    def test_build_device_config(
        self, mock_config, device_identifiers, behavior_profile
    ):
        """Test device configuration building."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        config = builder._build_device_config(device_identifiers, behavior_profile, {})

        assert config["device_bdf"] == "0000:03:00.0"
        assert config["vendor_id"] == "10ee"
        assert config["device_id"] == "7024"
        assert config["enable_error_injection"] is True
        assert config["enable_perf_counters"] is True
        assert config["enable_dma_operations"] is True
        assert config["behavior_profile"] is not None
        assert config["total_register_accesses"] == 1500
        assert config["has_manufacturing_variance"] is True

    def test_build_config_space_context(self, mock_config, config_space_data):
        """Test configuration space context building."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        context = builder._build_config_space_context(config_space_data)

        assert context["raw_data"] == config_space_data["config_space_hex"]
        assert context["size"] == 4096
        assert context["vendor_id"] == "10ee"
        assert context["device_id"] == "7024"
        assert context["has_extended_config"] is True
        assert len(context["bars"]) == 3

    def test_build_msix_context_enabled(self, mock_config, msix_data):
        """Test MSI-X context building with MSI-X enabled."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        context = builder._build_msix_context(msix_data)

        assert context["num_vectors"] == 32
        assert context["table_bir"] == 0
        assert context["table_offset"] == 0x2000
        assert context["enabled"] is True
        assert context["is_supported"] is True
        assert context["table_size_bytes"] == 512  # 32 * 16
        assert context["NUM_MSIX"] == 32

    def test_build_msix_context_disabled(self, mock_config):
        """Test MSI-X context building with MSI-X not available."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        context = builder._build_msix_context(None)

        assert context["num_vectors"] == 0
        assert context["enabled"] is False
        assert context["is_supported"] is False
        assert context["table_size"] == 0

    @patch(
        "src.device_clone.pcileech_context.PCILeechContextBuilder._get_vfio_bar_info"
    )
    def test_build_bar_config_success(
        self, mock_get_vfio_bar_info, mock_config, config_space_data, behavior_profile
    ):
        """Test successful BAR configuration building."""
        # Mock VFIO BAR info responses
        bar0_config = BarConfiguration(
            index=0,
            base_address=0xF7000000,
            size=65536,
            bar_type=0,
            prefetchable=False,
            is_memory=True,
            is_io=False,
        )
        bar1_config = BarConfiguration(
            index=1,
            base_address=0xF7100000,
            size=16384,
            bar_type=1,
            prefetchable=True,
            is_memory=True,
            is_io=False,
        )

        mock_get_vfio_bar_info.side_effect = [bar0_config, bar1_config, None]

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        bar_config = builder._build_bar_config(config_space_data, behavior_profile)

        assert bar_config["bar_index"] == 0  # Largest BAR selected
        assert bar_config["aperture_size"] == 65536
        assert bar_config["memory_type"] == "memory"
        assert len(bar_config["bars"]) == 2

    @patch(
        "src.device_clone.pcileech_context.PCILeechContextBuilder._get_vfio_bar_info"
    )
    def test_build_bar_config_no_valid_bars(
        self, mock_get_vfio_bar_info, mock_config, config_space_data
    ):
        """Test BAR configuration fails when no valid BARs found."""
        # All BARs return None (invalid)
        mock_get_vfio_bar_info.return_value = None

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        with pytest.raises(ContextError, match="No valid MMIO BARs found"):
            builder._build_bar_config(config_space_data, None)

    @patch("os.close")
    @patch("fcntl.ioctl")
    @patch(
        "src.device_clone.pcileech_context.PCILeechContextBuilder._open_vfio_device_fd"
    )
    def test_get_vfio_region_info_success(
        self, mock_open_fd, mock_ioctl, mock_close, mock_config, vfio_region_info
    ):
        """Test successful VFIO region info retrieval."""
        mock_open_fd.return_value = (10, 11)  # device_fd, container_fd

        # Mock ioctl to populate the structure
        def ioctl_side_effect(fd, cmd, data, mutate):
            if cmd == VFIO_DEVICE_GET_REGION_INFO:
                data.size = 65536
                data.flags = vfio_region_info.flags
            return 0

        mock_ioctl.side_effect = ioctl_side_effect

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        info = builder._get_vfio_region_info(0)

        assert info is not None
        assert info["size"] == 65536
        assert info["readable"] is True
        assert info["writable"] is True
        assert info["mappable"] is True

        # Verify cleanup
        assert mock_close.call_count == 2

    @patch(
        "src.device_clone.pcileech_context.PCILeechContextBuilder._open_vfio_device_fd"
    )
    def test_get_vfio_region_info_open_failure(self, mock_open_fd, mock_config):
        """Test VFIO region info handles device open failure."""
        mock_open_fd.side_effect = OSError(22, "Invalid argument")

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        info = builder._get_vfio_region_info(0)

        assert info is None

    @patch("os.close")
    @patch("fcntl.ioctl")
    @patch(
        "src.device_clone.pcileech_context.PCILeechContextBuilder._open_vfio_device_fd"
    )
    def test_get_vfio_region_info_ioctl_failure(
        self, mock_open_fd, mock_ioctl, mock_close, mock_config
    ):
        """Test VFIO region info handles ioctl failure."""
        mock_open_fd.return_value = (10, 11)
        mock_ioctl.side_effect = OSError(22, "Invalid argument")

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        info = builder._get_vfio_region_info(0)

        assert info is None
        # Verify cleanup still happens
        assert mock_close.call_count == 2

    @patch("src.cli.vfio_helpers.get_device_fd")
    def test_open_vfio_device_fd_success(self, mock_get_device_fd, mock_config):
        """Test successful VFIO device FD opening."""
        mock_get_device_fd.return_value = (10, 11)

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        device_fd, container_fd = builder._open_vfio_device_fd()

        assert device_fd == 10
        assert container_fd == 11
        mock_get_device_fd.assert_called_once_with("0000:03:00.0")

    @patch("src.cli.vfio_helpers.get_device_fd")
    def test_open_vfio_device_fd_failure(self, mock_get_device_fd, mock_config):
        """Test VFIO device FD open failure propagates."""
        mock_get_device_fd.side_effect = Exception("VFIO not available")

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        with pytest.raises(Exception, match="VFIO not available"):
            builder._open_vfio_device_fd()

    @patch("os.listdir")
    @patch("os.readlink")
    @patch("os.path.exists")
    def test_get_vfio_group_sysfs_success(
        self, mock_exists, mock_readlink, mock_listdir, mock_config
    ):
        """Test VFIO group resolution via sysfs."""
        mock_exists.return_value = True
        mock_readlink.return_value = "../../../kernel/iommu_groups/7"

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        group = builder._get_vfio_group()

        assert group == "7"

    @patch("os.listdir")
    @patch("os.path.exists")
    def test_get_vfio_group_fallback(self, mock_exists, mock_listdir, mock_config):
        """Test VFIO group fallback to /dev/vfio enumeration."""
        mock_exists.return_value = False
        mock_listdir.return_value = ["vfio", "5", "10", "char"]

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        group = builder._get_vfio_group()

        assert group == "5"  # First numeric entry

    @patch("os.listdir")
    @patch("os.path.exists")
    def test_get_vfio_group_last_resort(self, mock_exists, mock_listdir, mock_config):
        """Test VFIO group falls back to '0' as last resort."""
        mock_exists.return_value = False
        mock_listdir.side_effect = FileNotFoundError()

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        group = builder._get_vfio_group()

        assert group == "0"

    def test_build_timing_config_from_behavior(
        self, mock_config, device_identifiers, behavior_profile
    ):
        """Test timing configuration from behavior profile."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        timing = builder._build_timing_config(behavior_profile, device_identifiers)

        assert isinstance(timing, TimingParameters)
        assert timing.read_latency == 4  # Medium speed device
        assert timing.write_latency == 2
        assert timing.clock_frequency_mhz == 100.0

    def test_build_timing_config_from_device(self, mock_config, device_identifiers):
        """Test timing configuration from device characteristics."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        timing = builder._build_timing_config(None, device_identifiers)

        assert isinstance(timing, TimingParameters)
        # Network controller timings
        assert timing.read_latency == 2
        assert timing.write_latency == 1
        assert timing.clock_frequency_mhz == 125.0

    def test_generate_unique_device_signature(
        self, mock_config, device_identifiers, config_space_data, behavior_profile
    ):
        """Test unique device signature generation."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        signature = builder._generate_unique_device_signature(
            device_identifiers, behavior_profile, config_space_data
        )

        assert signature.startswith("32'h")
        assert len(signature) == 12  # 32'h + 8 hex chars

    def test_validate_context_completeness_success(self, mock_config):
        """Test successful context validation."""
        builder = PCILeechContextBuilder(
            device_bdf="0000:03:00.0",
            config=mock_config,
            validation_level=ValidationLevel.STRICT,
        )

        valid_context = {
            "device_config": {"vendor_id": "10ee", "bdf": "0000:03:00.0"},
            "config_space": {},
            "msix_config": {},
            "bar_config": {"bars": [Mock()]},
            "timing_config": {},
            "pcileech_config": {},
            "device_signature": "32'h12345678",
            "generation_metadata": {},
            "interrupt_config": {},
            "active_device_config": {},
        }

        # Should not raise
        builder._validate_context_completeness(valid_context)

    def test_validate_context_completeness_missing_section(self, mock_config):
        """Test context validation with missing section."""
        builder = PCILeechContextBuilder(
            device_bdf="0000:03:00.0",
            config=mock_config,
            validation_level=ValidationLevel.STRICT,
        )

        invalid_context = {
            "device_config": {"vendor_id": "10ee"},
            "config_space": {},
            # Missing other required sections
        }

        with pytest.raises(ContextError, match="missing required sections"):
            builder._validate_context_completeness(invalid_context)

    def test_validate_context_completeness_invalid_vendor(self, mock_config):
        """Test context validation with invalid vendor ID."""
        builder = PCILeechContextBuilder(
            device_bdf="0000:03:00.0",
            config=mock_config,
            validation_level=ValidationLevel.STRICT,
        )

        invalid_context = {
            "device_config": {"vendor_id": "0000"},  # Invalid
            "config_space": {},
            "msix_config": {},
            "bar_config": {"bars": []},
            "timing_config": {},
            "pcileech_config": {},
            "device_signature": "32'h12345678",
            "generation_metadata": {},
        }

        with pytest.raises(ContextError, match="vendor ID is missing or invalid"):
            builder._validate_context_completeness(invalid_context)

    def test_serialize_behavior_profile(self, mock_config, behavior_profile):
        """Test behavior profile serialization."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        # Use the behavior_profile fixture which is a proper Mock
        serialized = builder._serialize_behavior_profile(behavior_profile)

        # Check that serialization works and returns a dictionary
        assert isinstance(serialized, dict)
        # The mock should have these attributes from the fixture
        assert "total_accesses" in str(serialized)
        assert "capture_duration" in str(serialized)

    def test_adjust_bar_config_for_behavior(self, mock_config, behavior_profile):
        """Test BAR configuration adjustment based on behavior."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        bar_config = {"bar_index": 0, "aperture_size": 65536}
        adjustments = builder._adjust_bar_config_for_behavior(
            bar_config, behavior_profile
        )

        assert adjustments["high_frequency_device"] is True
        assert adjustments["access_frequency_class"] == "high"
        assert adjustments["timing_complexity"] == "low"  # Only 2 patterns
        assert "behavior_signature" in adjustments

    def test_estimate_bar_size_from_device_context(self, mock_config):
        """Test BAR size estimation based on device context."""
        mock_config.device_class = "network"
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        # Test network device estimation
        size = builder._estimate_bar_size_from_device_context(0, {"type": "memory"})
        assert size == 65536  # 64KB for network devices

        # Test display device with prefetchable BAR
        mock_config.device_class = "display"
        size = builder._estimate_bar_size_from_device_context(1, {"prefetchable": True})
        assert size == 268435456  # 256MB for framebuffer

    def test_build_pcileech_config(self, mock_config, device_identifiers):
        """Test PCILeech-specific configuration building."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        config = builder._build_pcileech_config(device_identifiers)

        assert config["command_timeout"] == 5000
        assert config["buffer_size"] == 4096
        assert config["enable_dma"] is True
        assert config["max_payload_size"] == 256
        assert config["cfg_force_mps"] == 1
        assert "device_ctrl_base" in config
        assert "supported_commands" in config
        assert len(config["supported_commands"]) > 0

    def test_build_active_device_config_with_capabilities(
        self, mock_config, device_identifiers
    ):
        """Test active device configuration with device capabilities."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        config = builder._build_active_device_config(device_identifiers, "msix", 32)

        assert config["enabled"] is True
        assert config["timer_period"] == 100000
        assert config["interrupt_mode"] == "msix"
        assert config["num_msix"] == 32
        assert config["device_id"] == "16'h7024"
        assert config["vendor_id"] == "16'h10EE"

    def test_build_active_device_config_without_capabilities(
        self, mock_config, device_identifiers
    ):
        """Test active device configuration with defaults."""
        mock_config.device_config = None
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        config = builder._build_active_device_config(device_identifiers, "intx", 1)

        assert config["enabled"] is False  # Default
        assert config["timer_period"] == 100000
        assert config["interrupt_mode"] == "intx"
        assert config["num_msix"] == 0

    @patch("src.device_clone.pcileech_context.OverlayMapper")
    def test_build_overlay_config_success(
        self, mock_overlay_mapper, mock_config, config_space_data
    ):
        """Test overlay configuration building."""
        mock_mapper = Mock()
        mock_mapper.generate_overlay_map.return_value = {
            "OVERLAY_MAP": [(0, 0xFFFFFFFF), (4, 0x0000FFFF)],
            "OVERLAY_ENTRIES": 2,
        }
        mock_overlay_mapper.return_value = mock_mapper

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        overlay_config = builder._build_overlay_config(config_space_data)

        assert overlay_config["OVERLAY_ENTRIES"] == 2
        assert len(overlay_config["OVERLAY_MAP"]) == 2
        assert overlay_config["OVERLAY_MAP"][0] == (0, 0xFFFFFFFF)

    def test_build_overlay_config_no_dword_map(self, mock_config):
        """Test overlay configuration with missing dword map."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        config_data = {"capabilities": {}}  # No dword_map
        overlay_config = builder._build_overlay_config(config_data)

        assert overlay_config["OVERLAY_ENTRIES"] == 0
        assert overlay_config["OVERLAY_MAP"] == []

    @patch(
        "src.device_clone.pcileech_context.PCILeechContextBuilder._get_vfio_region_info"
    )
    @patch(
        "src.device_clone.pcileech_context.PCILeechContextBuilder._open_vfio_device_fd"
    )
    def test_get_vfio_bar_info_memory_bar(
        self, mock_open_fd, mock_get_region_info, mock_config
    ):
        """Test VFIO BAR info retrieval for memory BAR."""
        mock_get_region_info.return_value = {
            "size": 65536,
            "flags": VFIO_REGION_INFO_FLAG_READ
            | VFIO_REGION_INFO_FLAG_WRITE
            | VFIO_REGION_INFO_FLAG_MMAP,
            "readable": True,
            "writable": True,
            "mappable": True,
        }

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        bar_data = {
            "type": "memory",
            "address": 0xF7000000,
            "prefetchable": False,
            "is_64bit": False,
        }
        bar_info = builder._get_vfio_bar_info(0, bar_data)

        assert bar_info is not None
        assert bar_info.index == 0
        assert bar_info.size == 65536
        assert bar_info.is_memory is True
        assert bar_info.is_io is False

    def test_get_vfio_bar_info_io_bar(self, mock_config):
        """Test VFIO BAR info skips I/O BARs."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        # Mock I/O BAR data
        bar_data = {"type": "io", "address": 0x3000, "size": 256}

        # Patch _get_vfio_region_info to return valid info
        with patch.object(builder, "_get_vfio_region_info") as mock_region_info:
            mock_region_info.return_value = {"size": 256, "flags": 0}

            bar_info = builder._get_vfio_bar_info(0, bar_data)

            # I/O BARs should be skipped
            assert bar_info is None

    @patch(
        "src.device_clone.pcileech_context.PCILeechContextBuilder._get_vfio_region_info"
    )
    def test_get_vfio_bar_info_zero_size(self, mock_get_region_info, mock_config):
        """Test VFIO BAR info skips zero-sized BARs."""
        mock_get_region_info.return_value = {"size": 0, "flags": 0}

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        bar_data = {"type": "memory", "address": 0xF7000000}
        bar_info = builder._get_vfio_bar_info(0, bar_data)

        assert bar_info is None

    @patch(
        "src.device_clone.pcileech_context.PCILeechContextBuilder._get_vfio_region_info"
    )
    def test_get_vfio_bar_info_vfio_failure(self, mock_get_region_info, mock_config):
        """Test VFIO BAR info handles VFIO access failure."""
        mock_get_region_info.side_effect = Exception("VFIO error")

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        bar_data = {"type": "memory", "address": 0xF7000000}

        with pytest.raises(ContextError, match="VFIO access failed"):
            builder._get_vfio_bar_info(0, bar_data)

    def test_generate_behavior_signature(self, mock_config, behavior_profile):
        """Test behavior signature generation."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        signature = builder._generate_behavior_signature(behavior_profile)

        assert isinstance(signature, str)
        assert len(signature) == 16  # SHA256 truncated to 16 chars

    def test_extract_timing_from_behavior_fast_device(self, mock_config):
        """Test timing extraction for fast device."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        # Create behavior profile with very fast timing
        fast_profile = Mock(spec=BehaviorProfile)
        fast_profile.timing_patterns = [
            Mock(avg_interval_us=5, frequency_hz=200000),
            Mock(avg_interval_us=8, frequency_hz=125000),
        ]

        timing = builder._extract_timing_from_behavior(fast_profile)

        assert timing.read_latency == 2
        assert timing.write_latency == 1
        assert timing.burst_length == 32
        assert timing.clock_frequency_mhz <= 200.0

    def test_extract_timing_from_behavior_slow_device(self, mock_config):
        """Test timing extraction for slow device."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        # Create behavior profile with slow timing
        slow_profile = Mock(spec=BehaviorProfile)
        slow_profile.timing_patterns = [
            Mock(avg_interval_us=2000, frequency_hz=500),
            Mock(avg_interval_us=1500, frequency_hz=667),
        ]

        timing = builder._extract_timing_from_behavior(slow_profile)

        assert timing.read_latency == 8
        assert timing.write_latency == 4
        assert timing.burst_length == 8
        assert timing.clock_frequency_mhz >= 50.0

    def test_generate_timing_from_device_network(self, mock_config):
        """Test timing generation for network device."""
        network_identifiers = DeviceIdentifiers(
            vendor_id="8086",
            device_id="1521",
            class_code="020000",  # Network controller
            revision_id="01",
        )

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        timing = builder._generate_timing_from_device(network_identifiers)

        assert timing.read_latency == 2
        assert timing.clock_frequency_mhz == 125.0

    def test_generate_timing_from_device_storage(self, mock_config):
        """Test timing generation for storage device."""
        storage_identifiers = DeviceIdentifiers(
            vendor_id="144d",
            device_id="a808",
            class_code="010802",  # NVMe storage
            revision_id="00",
        )

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        timing = builder._generate_timing_from_device(storage_identifiers)

        assert timing.read_latency == 6
        assert timing.burst_length == 64
        assert timing.clock_frequency_mhz == 100.0

    def test_generate_timing_from_device_generic(self, mock_config):
        """Test timing generation for generic device."""
        generic_identifiers = DeviceIdentifiers(
            vendor_id="1234",
            device_id="5678",
            class_code="ff0000",  # Unassigned class
            revision_id="00",
        )

        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        timing = builder._generate_timing_from_device(generic_identifiers)

        # Should use deterministic hash-based values
        assert 2 <= timing.read_latency <= 8
        assert 75.0 <= timing.clock_frequency_mhz <= 200.0

    def test_build_generation_metadata(self, mock_config, device_identifiers):
        """Test generation metadata building."""
        builder = PCILeechContextBuilder(
            device_bdf="0000:03:00.0",
            config=mock_config,
            validation_level=ValidationLevel.MODERATE,
        )

        metadata = builder._build_generation_metadata(device_identifiers)

        assert metadata["device_bdf"] == "0000:03:00.0"
        assert metadata["device_signature"] == "10ee:7024"
        assert metadata["validation_level"] == "moderate"
        assert "generated_at" in metadata
        assert "generator_version" in metadata

    def test_context_error_handling(self, mock_config):
        """Test proper error handling and context cleanup."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        # Mock a method to raise an exception
        builder._extract_device_identifiers = Mock(side_effect=KeyError("vendor_id"))

        with pytest.raises(ContextError) as exc_info:
            builder.build_context(
                behavior_profile=None, config_space_data={}, msix_data=None
            )

        # The error comes from _validate_input_data which checks for required fields
        assert "Missing required data for unique firmware generation" in str(
            exc_info.value
        )

    def test_msix_alignment_warning(self, mock_config):
        """Test MSI-X table alignment warning generation."""
        builder = PCILeechContextBuilder(device_bdf="0000:03:00.0", config=mock_config)

        # Unaligned table offset
        msix_data = {
            "capability_info": {
                "table_size": 16,
                "table_bir": 0,
                "table_offset": 0x2004,  # Not 8-byte aligned
                "pba_bir": 0,
                "pba_offset": 0x3000,
            }
        }

        context = builder._build_msix_context(msix_data)

        assert "WARNING" in context["alignment_warning"]
        assert "not 8-byte aligned" in context["alignment_warning"]

    def test_bar_size_encoding_validation(self, mock_config):
        """Test BAR size encoding validation."""
        with patch(
            "src.device_clone.bar_size_converter.BarSizeConverter"
        ) as mock_converter:
            mock_converter.validate_bar_size.return_value = True
            mock_converter.format_size.return_value = "64 KB"

            builder = PCILeechContextBuilder(
                device_bdf="0000:03:00.0", config=mock_config
            )

            # Create a BAR configuration with size encoding
            bar_config = BarConfiguration(
                index=0,
                base_address=0xF7000000,
                size=65536,
                bar_type=0,
                prefetchable=False,
                is_memory=True,
                is_io=False,
            )

            # Mock get_size_encoding
            with patch.object(bar_config, "get_size_encoding", return_value=0xFFFF0000):
                encoding = bar_config.get_size_encoding()
                assert encoding == 0xFFFF0000

    def test_device_identifiers_validation(self):
        """Test DeviceIdentifiers validation."""
        # Valid identifiers
        valid = DeviceIdentifiers(
            vendor_id="10ee", device_id="7024", class_code="020000", revision_id="01"
        )
        assert valid.vendor_id == "10ee"

        # Invalid hex format
        with pytest.raises(ContextError, match="Invalid hex format"):
            DeviceIdentifiers(
                vendor_id="XXXX",
                device_id="7024",
                class_code="020000",
                revision_id="01",
            )

        # Empty required field
        with pytest.raises(ContextError, match="cannot be empty"):
            DeviceIdentifiers(
                vendor_id="", device_id="7024", class_code="020000", revision_id="01"
            )

    def test_bar_configuration_validation(self):
        """Test BarConfiguration validation."""
        # Valid configuration
        valid = BarConfiguration(
            index=0,
            base_address=0xF7000000,
            size=65536,
            bar_type=0,
            prefetchable=False,
            is_memory=True,
            is_io=False,
        )
        assert valid.index == 0

        # Invalid index
        with pytest.raises(ContextError, match="Invalid BAR index"):
            BarConfiguration(
                index=6,  # Max is 5
                base_address=0xF7000000,
                size=65536,
                bar_type=0,
                prefetchable=False,
                is_memory=True,
                is_io=False,
            )

        # Invalid size
        with pytest.raises(ContextError, match="Invalid BAR size"):
            BarConfiguration(
                index=0,
                base_address=0xF7000000,
                size=-1,
                bar_type=0,
                prefetchable=False,
                is_memory=True,
                is_io=False,
            )

    def test_timing_parameters_validation(self):
        """Test TimingParameters validation."""
        # Valid parameters
        valid = TimingParameters(
            read_latency=4,
            write_latency=2,
            burst_length=16,
            inter_burst_gap=8,
            timeout_cycles=1024,
            clock_frequency_mhz=100.0,
            timing_regularity=0.9,
        )
        assert valid.read_latency == 4

        # Invalid parameters
        with pytest.raises(ContextError, match="must be positive"):
            TimingParameters(
                read_latency=0,  # Must be > 0
                write_latency=2,
                burst_length=16,
                inter_burst_gap=8,
                timeout_cycles=1024,
                clock_frequency_mhz=100.0,
                timing_regularity=0.9,
            )

    def test_full_integration_scenario(
        self, mock_config, config_space_data, msix_data, behavior_profile
    ):
        """Test full integration scenario with all components."""
        with patch("src.device_clone.pcileech_context.OverlayMapper") as mock_overlay:
            mock_overlay.return_value.generate_overlay_map.return_value = {
                "OVERLAY_MAP": [(0, 0xFFFFFFFF)],
                "OVERLAY_ENTRIES": 1,
            }

            builder = PCILeechContextBuilder(
                device_bdf="0000:03:00.0",
                config=mock_config,
                validation_level=ValidationLevel.STRICT,
            )

            # Mock VFIO operations
            with patch.object(builder, "_get_vfio_bar_info") as mock_bar_info:
                mock_bar_info.side_effect = [
                    BarConfiguration(
                        index=0,
                        base_address=0xF7000000,
                        size=65536,
                        bar_type=0,
                        prefetchable=False,
                        is_memory=True,
                        is_io=False,
                    ),
                    None,
                    None,  # Other BARs
                ]

                context = builder.build_context(
                    behavior_profile=behavior_profile,
                    config_space_data=config_space_data,
                    msix_data=msix_data,
                    interrupt_strategy="msix",
                    interrupt_vectors=32,
                )

                # Verify complete context
                assert context["device_config"]["vendor_id"] == "10ee"
                assert context["config_space"]["size"] == 4096
                assert context["msix_config"]["num_vectors"] == 32
                assert context["bar_config"]["aperture_size"] == 65536
                assert isinstance(context["timing_config"], TimingParameters)
                assert context["interrupt_config"]["strategy"] == "msix"
                assert context["OVERLAY_ENTRIES"] == 1
