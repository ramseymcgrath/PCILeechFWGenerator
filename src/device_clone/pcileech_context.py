#!/usr/bin/env python3
"""
PCILeech Template Context Builder - Optimized Version

Builds comprehensive template context from device profiling data.
Integrates BehaviorProfiler, ConfigSpaceManager, and MSIXCapability data.

Key optimizations:
- Reduced code duplication through helper methods
- Simplified complex logic flows
- Improved type safety with streamlined hints
- Better performance through caching
- Consolidated similar functionality
"""

import ctypes
import fcntl
import hashlib
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

from src.cli.vfio_constants import (VFIO_DEVICE_GET_REGION_INFO,
                                    VFIO_REGION_INFO_FLAG_MMAP,
                                    VFIO_REGION_INFO_FLAG_READ,
                                    VFIO_REGION_INFO_FLAG_WRITE,
                                    VfioRegionInfo)
from src.device_clone.behavior_profiler import BehaviorProfile
from src.device_clone.config_space_manager import BarInfo
from src.device_clone.fallback_manager import FallbackManager
from src.device_clone.overlay_mapper import OverlayMapper
from src.error_utils import extract_root_cause
from src.exceptions import ContextError
from src.string_utils import (format_bar_summary_table, format_bar_table,
                              format_raw_bar_table, log_error_safe,
                              log_info_safe, log_warning_safe)
from src.utils.attribute_access import safe_get_attr

logger = logging.getLogger(__name__)


# Simplified TypedDicts
class ConfigSpaceData(TypedDict, total=False):
    """Configuration space data structure."""

    config_space_hex: str
    config_space_size: int
    bars: List[Any]
    device_info: Dict[str, Any]
    vendor_id: str
    device_id: str
    class_code: str
    revision_id: str
    subsystem_vendor_id: Optional[str]
    subsystem_device_id: Optional[str]


class MSIXCapabilityInfo(TypedDict):
    """MSI-X capability information."""

    table_size: int
    table_bir: int
    table_offset: int
    pba_bir: int
    pba_offset: int
    enabled: bool
    function_mask: bool


class TemplateContext(TypedDict, total=False):
    """Template context structure."""

    device_config: Dict[str, Any]
    config_space: Dict[str, Any]
    msix_config: Dict[str, Any]
    interrupt_config: Dict[str, Any]
    active_device_config: Dict[str, Any]
    bar_config: Dict[str, Any]
    timing_config: Dict[str, Any]
    pcileech_config: Dict[str, Any]
    device_signature: str
    generation_metadata: Dict[str, Any]
    vendor_id: str
    device_id: str


class ValidationLevel(Enum):
    """Validation strictness levels."""

    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


class PCIConstants:
    """PCIe-related constants."""

    MIN_CONFIG_SPACE_SIZE = 256
    MAX_CONFIG_SPACE_SIZE = 4096
    MIN_BAR_INDEX = 0
    MAX_BAR_INDEX = 5
    BAR_TYPE_MEMORY_32BIT = 0
    BAR_TYPE_MEMORY_64BIT = 1
    DEFAULT_BAR_SIZE = 4096
    DEFAULT_IO_BAR_SIZE = 256

    # Device class prefixes
    CLASS_NETWORK = "02"
    CLASS_STORAGE = "01"
    CLASS_DISPLAY = "03"
    CLASS_AUDIO = "040"

    # Power states
    POWER_STATE_D0 = "D0"
    POWER_STATE_D3 = "D3"


@dataclass(slots=True)
class DeviceIdentifiers:
    """Device identification data."""

    vendor_id: str
    device_id: str
    class_code: str
    revision_id: str
    subsystem_vendor_id: Optional[str] = None
    subsystem_device_id: Optional[str] = None

    def __post_init__(self):
        """Validate and normalize identifiers."""
        self._normalize_fields()

    def _normalize_fields(self):
        """Normalize hex fields to expected lengths."""
        specs = [
            ("vendor_id", 4),
            ("device_id", 4),
            ("class_code", 6),
            ("revision_id", 2),
        ]

        for field_name, length in specs:
            value = getattr(self, field_name)
            if not value:
                raise ContextError(f"Missing {field_name}")
            try:
                normalized = f"{int(value, 16):0{length}x}"
                setattr(self, field_name, normalized)
            except ValueError:
                raise ContextError(f"Invalid hex: {field_name}={value}")

        # Normalize optional fields
        if self.subsystem_vendor_id:
            self.subsystem_vendor_id = self._normalize_hex(self.subsystem_vendor_id, 4)
        if self.subsystem_device_id:
            self.subsystem_device_id = self._normalize_hex(self.subsystem_device_id, 4)

    @staticmethod
    def _normalize_hex(value: str, length: int) -> str:
        """Normalize a hex string."""
        return f"{int(value, 16):0{length}x}"

    @property
    def device_signature(self) -> str:
        """Generate device signature."""
        return f"{self.vendor_id}:{self.device_id}"

    @property
    def full_signature(self) -> str:
        """Generate full signature with subsystem IDs."""
        subsys_vendor = self.subsystem_vendor_id or self.vendor_id
        subsys_device = self.subsystem_device_id or self.device_id
        return f"{self.vendor_id}:{self.device_id}:{subsys_vendor}:{subsys_device}"

    def get_device_class_type(self) -> str:
        """Get human-readable device class."""
        class_map = {
            PCIConstants.CLASS_NETWORK: "Network Controller",
            PCIConstants.CLASS_STORAGE: "Storage Controller",
            PCIConstants.CLASS_DISPLAY: "Display Controller",
            PCIConstants.CLASS_AUDIO: "Audio Controller",
        }
        return class_map.get(self.class_code[:2], "Unknown Device")


@dataclass(slots=True)
class BarConfiguration:
    """BAR configuration data."""

    index: int
    base_address: int
    size: int
    bar_type: int
    prefetchable: bool
    is_memory: bool
    is_io: bool
    is_64bit: bool = field(default=False)
    _size_encoding: Optional[int] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Validate BAR configuration."""
        if not PCIConstants.MIN_BAR_INDEX <= self.index <= PCIConstants.MAX_BAR_INDEX:
            raise ContextError(f"Invalid BAR index: {self.index}")
        if self.size < 0:
            raise ContextError(f"Invalid BAR size: {self.size}")

        if self.is_memory and self.bar_type == PCIConstants.BAR_TYPE_MEMORY_64BIT:
            self.is_64bit = True

    def get_size_encoding(self) -> int:
        """Get size encoding for this BAR."""
        if self._size_encoding is None:
            from src.device_clone.bar_size_converter import BarSizeConverter

            bar_type_str = "io" if self.is_io else "memory"
            self._size_encoding = BarSizeConverter.size_to_encoding(
                self.size, bar_type_str, self.is_64bit, self.prefetchable
            )
        return self._size_encoding

    @property
    def size_mb(self) -> float:
        """Get BAR size in MB."""
        return self.size / (1024 * 1024)

    @property
    def type_description(self) -> str:
        """Get BAR type description."""
        if self.is_io:
            return "I/O"
        return "64-bit Memory" if self.is_64bit else "32-bit Memory"


@dataclass(slots=True)
class TimingParameters:
    """Device timing parameters."""

    read_latency: int
    write_latency: int
    burst_length: int
    inter_burst_gap: int
    timeout_cycles: int
    clock_frequency_mhz: float
    timing_regularity: float

    def __post_init__(self):
        """Validate timing parameters."""
        for name, value in asdict(self).items():
            if value <= 0:
                raise ContextError(f"{name} must be positive: {value}")

        if not 0 < self.timing_regularity <= 1.0:
            raise ContextError(f"Invalid timing_regularity: {self.timing_regularity}")

    @property
    def total_latency(self) -> int:
        """Calculate total latency."""
        return self.read_latency + self.write_latency

    @property
    def effective_bandwidth_mbps(self) -> float:
        """Estimate bandwidth in MB/s."""
        cycles_per_burst = self.burst_length + self.inter_burst_gap
        bursts_per_second = (self.clock_frequency_mhz * 1e6) / cycles_per_burst
        bytes_per_burst = self.burst_length * 4  # 32-bit transfers
        return (bursts_per_second * bytes_per_burst) / 1e6

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result.update(
            {
                "total_latency": self.total_latency,
                "effective_bandwidth_mbps": self.effective_bandwidth_mbps,
            }
        )
        return result


class VFIODeviceManager:
    """Manages VFIO device operations."""

    def __init__(self, device_bdf: str, logger: logging.Logger):
        self.device_bdf = device_bdf
        self.logger = logger
        self._device_fd: Optional[int] = None
        self._container_fd: Optional[int] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self) -> Tuple[int, int]:
        """Open VFIO device and container FDs."""
        if self._device_fd is not None and self._container_fd is not None:
            return self._device_fd, self._container_fd

        from src.cli.vfio_helpers import get_device_fd

        try:
            self._device_fd, self._container_fd = get_device_fd(self.device_bdf)
            return self._device_fd, self._container_fd
        except Exception as e:
            log_error_safe(self.logger, f"Failed to open VFIO device: {e}")
            raise

    def close(self):
        """Close VFIO file descriptors."""
        for fd in [self._device_fd, self._container_fd]:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
        self._device_fd = None
        self._container_fd = None

    def get_region_info(self, index: int) -> Optional[Dict[str, Any]]:
        """Get VFIO region information."""
        if self._device_fd is None:
            self.open()

        info = VfioRegionInfo()
        info.argsz = ctypes.sizeof(VfioRegionInfo)
        info.index = index

        try:
            if self._device_fd is None:
                raise ContextError("Device FD not available")

            fcntl.ioctl(self._device_fd, VFIO_DEVICE_GET_REGION_INFO, info, True)

            return {
                "index": info.index,
                "flags": info.flags,
                "size": info.size,
                "readable": bool(info.flags & VFIO_REGION_INFO_FLAG_READ),
                "writable": bool(info.flags & VFIO_REGION_INFO_FLAG_WRITE),
                "mappable": bool(info.flags & VFIO_REGION_INFO_FLAG_MMAP),
            }
        except OSError as e:
            log_error_safe(self.logger, f"VFIO region info failed: {e}")
            return None


class PCILeechContextBuilder:
    """Builds template context from device profiling data - Optimized."""

    REQUIRED_DEVICE_FIELDS = ["vendor_id", "device_id", "class_code", "revision_id"]
    REQUIRED_MSIX_FIELDS = ["table_size", "table_bir", "table_offset"]

    def __init__(
        self,
        device_bdf: str,
        config: Any,
        validation_level: ValidationLevel = ValidationLevel.STRICT,
        fallback_manager: Optional[FallbackManager] = None,
    ):
        """Initialize context builder."""
        if not device_bdf or not device_bdf.strip():
            raise ContextError("Device BDF cannot be empty")

        self.device_bdf = device_bdf.strip()
        self.config = config
        self.validation_level = validation_level
        self.logger = logging.getLogger(__name__)
        self._context_cache: Dict[str, Any] = {}
        self._vfio_manager = VFIODeviceManager(self.device_bdf, self.logger)
        self.fallback_manager = fallback_manager or FallbackManager(
            mode="prompt", allowed_fallbacks=["bar-analysis"]
        )

    def build_context(
        self,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
        msix_data: Optional[Dict[str, Any]],
        interrupt_strategy: str = "intx",
        interrupt_vectors: int = 1,
        donor_template: Optional[Dict[str, Any]] = None,
    ) -> TemplateContext:
        """Build comprehensive template context."""
        log_info_safe(
            self.logger,
            f"Building context for {self.device_bdf} with {interrupt_strategy}",
        )

        # Validate input
        self._validate_input_data(config_space_data, msix_data, behavior_profile)

        try:
            # Extract device identifiers
            device_identifiers = self._extract_device_identifiers(config_space_data)

            # Build context sections
            context: TemplateContext = {
                "device_config": self._build_device_config(
                    device_identifiers, behavior_profile, config_space_data
                ),
                "config_space": self._build_config_space_context(config_space_data),
                "msix_config": self._build_msix_context(msix_data),
                "bar_config": self._build_bar_config(
                    config_space_data, behavior_profile
                ),
                "timing_config": self._build_timing_config(
                    behavior_profile, device_identifiers
                ).to_dict(),
                "pcileech_config": self._build_pcileech_config(device_identifiers),
                "interrupt_config": {
                    "strategy": interrupt_strategy,
                    "vectors": interrupt_vectors,
                    "msix_available": msix_data is not None,
                },
                "active_device_config": self._build_active_device_config(
                    device_identifiers, interrupt_strategy, interrupt_vectors
                ),
                "device_signature": self._generate_device_signature(
                    device_identifiers, behavior_profile, config_space_data
                ),
                "generation_metadata": self._build_generation_metadata(
                    device_identifiers
                ),
                "vendor_id": device_identifiers.vendor_id,
                "device_id": device_identifiers.device_id,
            }

            # Add overlay config
            overlay_config = self._build_overlay_config(config_space_data)
            for key, value in overlay_config.items():
                context[key] = value  # type: ignore

            # Add extended config pointers
            context["EXT_CFG_CAP_PTR"] = context.get("device_config", {}).get(  # type: ignore
                "ext_cfg_cap_ptr", 0x100
            )
            context["EXT_CFG_XP_CAP_PTR"] = context.get("device_config", {}).get(  # type: ignore
                "ext_cfg_xp_cap_ptr", 0x100
            )

            # Merge donor template if provided
            if donor_template:
                context = self._merge_donor_template(dict(context), donor_template)

            # Final validation
            self._validate_context_completeness(context)

            log_info_safe(
                self.logger,
                f"Context built successfully: {context.get('device_signature', 'unknown')}",
            )

            return context

        except Exception as e:
            root_cause = extract_root_cause(e)
            log_error_safe(self.logger, f"Context build failed: {root_cause}")
            raise ContextError("Context building failed", root_cause=root_cause)

    def _validate_input_data(
        self,
        config_space_data: Dict[str, Any],
        msix_data: Optional[Dict[str, Any]],
        behavior_profile: Optional[BehaviorProfile],
    ):
        """Validate input data."""
        missing = []

        # Check config space
        if not config_space_data:
            missing.append("config_space_data")
        else:
            for field in self.REQUIRED_DEVICE_FIELDS:
                if field not in config_space_data or not config_space_data[field]:
                    missing.append(f"config_space_data.{field}")

            # Check config space size
            size = config_space_data.get("config_space_size", 0)
            if size < PCIConstants.MIN_CONFIG_SPACE_SIZE:
                log_warning_safe(
                    self.logger,
                    f"Config space size {size} < {PCIConstants.MIN_CONFIG_SPACE_SIZE}",
                )
                if self.validation_level == ValidationLevel.STRICT and size == 0:
                    missing.append(f"config_space_size ({size})")

        # Check MSI-X if present
        if msix_data and msix_data.get("capability_info"):
            cap_info = msix_data["capability_info"]
            for field in self.REQUIRED_MSIX_FIELDS:
                if field not in cap_info:
                    missing.append(f"msix.{field}")

        # Check behavior profile
        if behavior_profile:
            if not getattr(behavior_profile, "total_accesses", 0) > 0:
                missing.append("behavior_profile.total_accesses")
            if not getattr(behavior_profile, "capture_duration", 0) > 0:
                missing.append("behavior_profile.capture_duration")

        if missing and self.validation_level == ValidationLevel.STRICT:
            raise ContextError(f"Missing required data: {missing}")

    def _extract_device_identifiers(
        self, config_space_data: Dict[str, Any]
    ) -> DeviceIdentifiers:
        """Extract device identifiers using ConfigSpaceManager if needed."""
        # If config_space_data doesn't have the required fields, use ConfigSpaceManager
        if not all(
            k in config_space_data
            for k in ["vendor_id", "device_id", "class_code", "revision_id"]
        ):
            from src.device_clone.config_space_manager import \
                ConfigSpaceManager

            manager = ConfigSpaceManager(self.device_bdf)
            # Read config space and extract device info
            config_space = manager.read_vfio_config_space()
            config_space_data = manager.extract_device_info(config_space)

        # ConfigSpaceManager already handles conversion and fallbacks
        # Just create DeviceIdentifiers from the extracted data
        return DeviceIdentifiers(
            vendor_id=str(config_space_data.get("vendor_id", "0000")),
            device_id=str(config_space_data.get("device_id", "0000")),
            class_code=str(config_space_data.get("class_code", "000000")),
            revision_id=str(config_space_data.get("revision_id", "00")),
            subsystem_vendor_id=str(
                config_space_data.get(
                    "subsystem_vendor_id", config_space_data.get("vendor_id", "0000")
                )
            ),
            subsystem_device_id=str(
                config_space_data.get(
                    "subsystem_device_id", config_space_data.get("device_id", "0000")
                )
            ),
        )

    def _build_device_config(
        self,
        identifiers: DeviceIdentifiers,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build device configuration."""
        config = {
            "device_bdf": self.device_bdf,
            **asdict(identifiers),
            "enable_perf_counters": getattr(
                self.config, "enable_advanced_features", False
            ),
            "enable_dma_operations": getattr(
                self.config, "enable_dma_operations", False
            ),
            "enable_interrupt_coalescing": getattr(
                self.config, "enable_interrupt_coalescing", False
            ),
        }

        # Add hex representations
        if identifiers.subsystem_vendor_id:
            config["subsystem_vendor_id_hex"] = (
                f"0x{int(identifiers.subsystem_vendor_id, 16):04X}"
            )
        if identifiers.subsystem_device_id:
            config["subsystem_device_id_hex"] = (
                f"0x{int(identifiers.subsystem_device_id, 16):04X}"
            )

        # Add extended config pointers
        if hasattr(self.config, "device_config"):
            caps = getattr(self.config.device_config, "capabilities", None)
            if caps:
                config["ext_cfg_cap_ptr"] = getattr(caps, "ext_cfg_cap_ptr", 0x100)
                config["ext_cfg_xp_cap_ptr"] = getattr(
                    caps, "ext_cfg_xp_cap_ptr", 0x100
                )

        # Add behavior profile
        if behavior_profile:
            config.update(
                {
                    "behavior_profile": self._serialize_behavior_profile(
                        behavior_profile
                    ),
                    "total_register_accesses": behavior_profile.total_accesses,
                    "capture_duration": behavior_profile.capture_duration,
                    "timing_patterns_count": len(behavior_profile.timing_patterns),
                    "state_transitions_count": len(behavior_profile.state_transitions),
                    "has_manufacturing_variance": bool(
                        getattr(behavior_profile, "variance_metadata", None)
                    ),
                }
            )

            if hasattr(behavior_profile, "pattern_analysis"):
                config["pattern_analysis"] = behavior_profile.pattern_analysis

        return config

    def _serialize_behavior_profile(self, profile: BehaviorProfile) -> Dict[str, Any]:
        """Serialize behavior profile."""
        try:
            profile_dict = asdict(profile)
            # Convert non-serializable objects
            for key, value in profile_dict.items():
                if hasattr(value, "__dict__"):
                    profile_dict[key] = f"{type(value).__name__}_{hash(str(value))}"
            return profile_dict
        except Exception as e:
            raise ContextError(f"Failed to serialize profile: {e}")

    def _build_config_space_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build config space context, using ConfigSpaceManager if needed."""
        # If data is incomplete, use ConfigSpaceManager to get it
        if not all(
            k in data for k in ["config_space_hex", "config_space_size", "bars"]
        ):
            from src.device_clone.config_space_manager import \
                ConfigSpaceManager

            manager = ConfigSpaceManager(self.device_bdf)
            config_space = manager.read_vfio_config_space()
            device_info = manager.extract_device_info(config_space)

            # Merge with provided data
            data = {**device_info, **data}

        return {
            "raw_data": data.get("config_space_hex", ""),
            "size": data.get("config_space_size", 256),
            "device_info": data.get("device_info", {}),
            "vendor_id": data.get("vendor_id", "0000"),
            "device_id": data.get("device_id", "0000"),
            "class_code": data.get("class_code", "000000"),
            "revision_id": data.get("revision_id", "00"),
            "bars": data.get("bars", []),
            "has_extended_config": data.get("config_space_size", 256) > 256,
        }

    def _build_msix_context(
        self, msix_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build MSI-X context."""
        if not msix_data or not msix_data.get("capability_info"):
            # Return disabled MSI-X config
            return {
                "num_vectors": 0,
                "table_bir": 0,
                "table_offset": 0,
                "pba_bir": 0,
                "pba_offset": 0,
                "enabled": False,
                "is_supported": False,
                "is_valid": False,
                "table_size": 0,
                "table_size_minus_one": 0,
                "NUM_MSIX": 0,
            }

        cap = msix_data["capability_info"]
        table_size = cap["table_size"]
        table_offset = cap["table_offset"]
        pba_offset = cap.get("pba_offset", table_offset + (table_size * 16))
        pba_size_dwords = (table_size + 31) // 32

        return {
            "num_vectors": table_size,
            "table_bir": cap["table_bir"],
            "table_offset": table_offset,
            "pba_bir": cap.get("pba_bir", cap["table_bir"]),
            "pba_offset": pba_offset,
            "enabled": cap.get("enabled", False),
            "function_mask": cap.get("function_mask", False),
            "is_supported": table_size > 0,
            "validation_errors": msix_data.get("validation_errors", []),
            "is_valid": msix_data.get("is_valid", True),
            "table_size_bytes": table_size * 16,
            "pba_size_bytes": pba_size_dwords * 4,
            "table_size": table_size,
            "table_size_minus_one": table_size - 1,
            "NUM_MSIX": table_size,
            "MSIX_TABLE_BIR": cap["table_bir"],
            "MSIX_TABLE_OFFSET": f"32'h{table_offset:08X}",
            "MSIX_PBA_BIR": cap.get("pba_bir", cap["table_bir"]),
            "MSIX_PBA_OFFSET": f"32'h{pba_offset:08X}",
        }

    def _build_bar_config(
        self,
        config_space_data: Dict[str, Any],
        behavior_profile: Optional[BehaviorProfile],
    ) -> Dict[str, Any]:
        """Build BAR configuration."""
        # Check power state
        self._check_and_fix_power_state()

        bars = config_space_data["bars"]
        bar_configs = []

        # Analyze all BARs
        for i, bar_data in enumerate(bars):
            try:
                bar_info = self._get_vfio_bar_info(i, bar_data)
                if bar_info:
                    bar_configs.append(bar_info)
            except Exception as e:
                log_warning_safe(self.logger, f"BAR {i} analysis failed: {e}")

        # Select primary BAR
        memory_bars = [b for b in bar_configs if b.is_memory and b.size > 0]
        if not memory_bars:
            raise ContextError("No valid MMIO BARs found")

        primary_bar = max(memory_bars, key=lambda b: b.size)

        log_info_safe(
            self.logger,
            f"Primary BAR: index={primary_bar.index}, size={primary_bar.size_mb:.2f}MB",
        )

        config = {
            "bar_index": primary_bar.index,
            "aperture_size": primary_bar.size,
            "bar_type": primary_bar.bar_type,
            "prefetchable": primary_bar.prefetchable,
            "memory_type": "memory" if primary_bar.is_memory else "io",
            "bars": bar_configs,
        }

        if behavior_profile:
            config.update(
                self._adjust_bar_config_for_behavior(config, behavior_profile)
            )

        return config

    def _get_vfio_bar_info(self, index: int, bar_data) -> Optional[BarConfiguration]:
        """Get BAR info via VFIO."""
        region_info = self._vfio_manager.get_region_info(index)
        if not region_info:
            return None

        size = region_info["size"]
        if size == 0:
            return None

        # Extract BAR properties
        if isinstance(bar_data, dict):
            is_memory = bar_data.get("type", "memory") == "memory"
            is_io = not is_memory
            base_address = bar_data.get("address", 0)
            prefetchable = bar_data.get("prefetchable", False)
            bar_type = 1 if bar_data.get("is_64bit", False) else 0
        elif isinstance(bar_data, BarInfo):
            is_memory = bar_data.bar_type == "memory"
            is_io = not is_memory
            base_address = bar_data.address
            prefetchable = bar_data.prefetchable
            bar_type = 1 if bar_data.is_64bit else 0
        elif hasattr(bar_data, "address"):
            is_memory = getattr(bar_data, "type", "memory") == "memory"
            is_io = not is_memory
            base_address = bar_data.address
            prefetchable = getattr(bar_data, "prefetchable", False)
            bar_type = 1 if getattr(bar_data, "is_64bit", False) else 0
        else:
            return None

        # Only return valid memory BARs
        if is_memory and size > 0:
            return BarConfiguration(
                index=index,
                base_address=base_address,
                size=size,
                bar_type=bar_type,
                prefetchable=prefetchable,
                is_memory=is_memory,
                is_io=is_io,
            )

        return None

    def _check_and_fix_power_state(self):
        """Check and fix device power state."""
        try:
            power_state_path = f"/sys/bus/pci/devices/{self.device_bdf}/power_state"
            if Path(power_state_path).exists():
                with open(power_state_path, "r") as f:
                    state = f.read().strip()
                    if state != PCIConstants.POWER_STATE_D0:
                        log_info_safe(self.logger, f"Waking device from {state}")
                        # Wake device by accessing config space
                        config_path = f"/sys/bus/pci/devices/{self.device_bdf}/config"
                        with open(config_path, "rb") as f:
                            f.read(4)  # Read vendor ID to wake device
        except Exception as e:
            log_warning_safe(self.logger, f"Power state check failed: {e}")

    def _adjust_bar_config_for_behavior(
        self, config: Dict[str, Any], profile: BehaviorProfile
    ) -> Dict[str, Any]:
        """Adjust BAR config based on behavior."""
        adjustments = {}

        if hasattr(profile, "access_patterns"):
            patterns = getattr(profile, "access_patterns", {})
            if patterns.get("burst_mode"):
                adjustments["burst_mode_enabled"] = True
                adjustments["burst_size"] = patterns.get("burst_size", 64)

        if hasattr(profile, "timing_patterns"):
            if len(profile.timing_patterns) > 0:
                adjustments["has_timing_patterns"] = True

        return adjustments

    def _build_timing_config(
        self,
        behavior_profile: Optional[BehaviorProfile],
        identifiers: DeviceIdentifiers,
    ) -> TimingParameters:
        """Build timing configuration using existing device config."""
        from src.device_clone.device_config import get_device_config

        # Try to get timing from behavior profile first
        if behavior_profile and hasattr(behavior_profile, "timing_patterns"):
            patterns = behavior_profile.timing_patterns
            if patterns and len(patterns) > 0:
                # Use the behavior profile's actual timing data
                # This is dynamic based on actual device behavior
                total_read = 0
                total_write = 0
                count = 0

                for p in patterns:
                    # Handle both object and dict patterns
                    if hasattr(p, "avg_interval_us"):
                        # Convert interval to latency estimate
                        total_read += max(1, int(p.avg_interval_us / 100))
                        total_write += max(1, int(p.avg_interval_us / 100))
                        count += 1
                    elif isinstance(p, dict) and "avg_interval_us" in p:
                        total_read += max(1, int(p["avg_interval_us"] / 100))
                        total_write += max(1, int(p["avg_interval_us"] / 100))
                        count += 1

                if count > 0:
                    avg_read = total_read / count
                    avg_write = total_write / count

                    # Get burst parameters from behavior if available
                    burst_length = 32  # Default
                    # TimingPattern doesn't have burst_length, use default

                    return TimingParameters(
                        read_latency=max(1, int(avg_read)),
                        write_latency=max(1, int(avg_write)),
                        burst_length=burst_length,
                        inter_burst_gap=max(1, burst_length // 4),
                        timeout_cycles=max(100, int(avg_read * 100)),
                        clock_frequency_mhz=100.0,  # This should come from config
                        timing_regularity=0.95,
                    )

        # Try to get device-specific config
        device_config = None
        try:
            # Build a profile name from the device identifiers
            profile_name = f"{identifiers.vendor_id}_{identifiers.device_id}"
            device_config = get_device_config(profile_name)
        except:
            pass

        if device_config and hasattr(device_config, "capabilities"):
            # Use the device-specific timing configuration from capabilities
            caps = device_config.capabilities
            return TimingParameters(
                read_latency=getattr(caps, "read_latency", 10),
                write_latency=getattr(caps, "write_latency", 10),
                burst_length=getattr(caps, "burst_length", 32),
                inter_burst_gap=getattr(caps, "inter_burst_gap", 8),
                timeout_cycles=getattr(caps, "timeout_cycles", 1000),
                clock_frequency_mhz=getattr(caps, "clock_frequency_mhz", 100.0),
                timing_regularity=getattr(caps, "timing_regularity", 0.95),
            )

        # Fallback to class-based defaults from fallback manager
        from src.device_clone.fallback_manager import FallbackManager

        fallback_mgr = FallbackManager()
        # Apply fallbacks for timing parameters
        timing_data = {
            "class_code": identifiers.class_code,
            "read_latency": None,
            "write_latency": None,
            "burst_length": None,
            "inter_burst_gap": None,
            "timeout_cycles": None,
            "clock_frequency_mhz": None,
            "timing_regularity": None,
        }
        timing_defaults = fallback_mgr.apply_fallbacks(timing_data)

        return TimingParameters(
            read_latency=timing_defaults.get("read_latency", 10),
            write_latency=timing_defaults.get("write_latency", 10),
            burst_length=timing_defaults.get("burst_length", 32),
            inter_burst_gap=timing_defaults.get("inter_burst_gap", 8),
            timeout_cycles=timing_defaults.get("timeout_cycles", 1000),
            clock_frequency_mhz=timing_defaults.get("clock_frequency_mhz", 100.0),
            timing_regularity=timing_defaults.get("timing_regularity", 0.95),
        )

    def _build_pcileech_config(self, identifiers: DeviceIdentifiers) -> Dict[str, Any]:
        """Build PCILeech-specific configuration using dynamic values."""
        # Get max payload size from config or use default
        max_payload_size = getattr(self.config, "max_payload_size", 256)
        max_read_request = getattr(self.config, "max_read_request", 512)

        # Try to get actual values from device capabilities
        if hasattr(self.config, "device_config") and self.config.device_config:
            caps = getattr(self.config.device_config, "capabilities", None)
            if caps:
                if hasattr(caps, "max_payload_size"):
                    max_payload_size = caps.max_payload_size
                if hasattr(caps, "max_read_request"):
                    max_read_request = caps.max_read_request

        # Get timing values from device capabilities if available
        completion_timeout = 50000  # Default 50ms
        replay_timer = 1000  # Default 1ms

        if hasattr(self.config, "device_config") and self.config.device_config:
            caps = getattr(self.config.device_config, "capabilities", None)
            if caps:
                # Use actual device capabilities
                if hasattr(caps, "completion_timeout"):
                    completion_timeout = caps.completion_timeout
                if hasattr(caps, "replay_timer"):
                    replay_timer = caps.replay_timer

        return {
            "device_signature": identifiers.device_signature,
            "full_signature": identifiers.full_signature,
            "enable_shadow_config": True,
            "enable_bar_emulation": True,
            "enable_dma": getattr(self.config, "enable_dma_operations", False),
            "enable_interrupts": True,
            "max_payload_size": max_payload_size,
            "max_read_request": max_read_request,
            "completion_timeout": completion_timeout,
            "replay_timer": replay_timer,
            "ack_nak_latency": 100,  # This is typically fixed at 100ns
        }

    def _build_active_device_config(
        self,
        identifiers: DeviceIdentifiers,
        interrupt_strategy: str,
        interrupt_vectors: int,
    ) -> Dict[str, Any]:
        """Build active device configuration."""
        return {
            "vendor_id": identifiers.vendor_id,
            "device_id": identifiers.device_id,
            "subsystem_vendor_id": identifiers.subsystem_vendor_id
            or identifiers.vendor_id,
            "subsystem_device_id": identifiers.subsystem_device_id
            or identifiers.device_id,
            "class_code": identifiers.class_code,
            "revision_id": identifiers.revision_id,
            "interrupt_mode": interrupt_strategy,
            "interrupt_vectors": interrupt_vectors,
            "device_class": identifiers.get_device_class_type(),
            "is_network": identifiers.class_code[:2] == PCIConstants.CLASS_NETWORK,
            "is_storage": identifiers.class_code[:2] == PCIConstants.CLASS_STORAGE,
            "is_display": identifiers.class_code[:2] == PCIConstants.CLASS_DISPLAY,
        }

    def _generate_device_signature(
        self,
        identifiers: DeviceIdentifiers,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
    ) -> str:
        """Generate unique device signature."""
        components = [
            identifiers.full_signature,
            config_space_data.get("config_space_size", 0),
        ]

        if behavior_profile:
            components.extend(
                [
                    behavior_profile.total_accesses,
                    behavior_profile.capture_duration,
                    len(behavior_profile.timing_patterns),
                ]
            )

        # Create hash of components
        signature_data = "|".join(str(c) for c in components)
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()[:16]

        return f"{identifiers.device_signature}_{signature_hash}"

    def _build_generation_metadata(
        self, identifiers: DeviceIdentifiers
    ) -> Dict[str, Any]:
        """Build generation metadata."""
        return {
            "timestamp": datetime.now().isoformat(),
            "generator_version": "2.0.0-optimized",
            "device_bdf": self.device_bdf,
            "device_class": identifiers.get_device_class_type(),
            "validation_level": self.validation_level.value,
            "vendor_name": self._get_vendor_name(identifiers.vendor_id),
            "device_name": self._get_device_name(
                identifiers.vendor_id, identifiers.device_id
            ),
        }

    def _get_vendor_name(self, vendor_id: str) -> str:
        """Get vendor name from ID using device info lookup."""
        from src.device_clone.device_info_lookup import lookup_device_info

        # Use the existing device info lookup to get vendor name dynamically
        device_info = lookup_device_info(self.device_bdf, {"vendor_id": vendor_id})

        # Try to get vendor name from device info or fallback
        vendor_name = device_info.get("vendor_name")
        if not vendor_name:
            # Use lspci or other system tools to get vendor name
            import subprocess

            try:
                result = subprocess.run(
                    ["lspci", "-mm", "-d", f"{vendor_id}:"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0 and result.stdout:
                    # Parse vendor name from lspci output
                    parts = result.stdout.strip().split('"')
                    if len(parts) > 3:
                        vendor_name = parts[3]
            except:
                pass

        return vendor_name or f"Vendor {vendor_id}"

    def _get_device_name(self, vendor_id: str, device_id: str) -> str:
        """Get device name from IDs using device info lookup."""
        from src.device_clone.device_info_lookup import lookup_device_info

        # Use the existing device info lookup to get device name dynamically
        device_info = lookup_device_info(
            self.device_bdf, {"vendor_id": vendor_id, "device_id": device_id}
        )

        # Try to get device name from device info
        device_name = device_info.get("device_name")
        if not device_name:
            # Use lspci to get device name
            import subprocess

            try:
                result = subprocess.run(
                    ["lspci", "-mm", "-d", f"{vendor_id}:{device_id}"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0 and result.stdout:
                    # Parse device name from lspci output
                    parts = result.stdout.strip().split('"')
                    if len(parts) > 5:
                        device_name = parts[5]
            except:
                pass

        return device_name or f"Device {device_id}"

    def _build_overlay_config(
        self, config_space_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build overlay configuration for shadow config space."""
        try:
            mapper = OverlayMapper()
            # Convert config_space_data to proper format for overlay mapper
            dword_map = config_space_data.get("dword_map", {})
            if not dword_map and "config_space_hex" in config_space_data:
                # Create dword_map from hex data if not present
                hex_data = config_space_data["config_space_hex"]
                if isinstance(hex_data, str):
                    hex_data = hex_data.replace(" ", "").replace("\n", "")
                    dword_map = {}
                    for i in range(
                        0, min(len(hex_data), 1024), 8
                    ):  # Process up to 256 dwords
                        if i + 8 <= len(hex_data):
                            dword = hex_data[i : i + 8]
                            dword_map[i // 8] = int(dword, 16)

            capabilities = config_space_data.get("capabilities", {})
            overlay_map = mapper.generate_overlay_map(dword_map, capabilities)
            return {
                "OVERLAY_MAP": overlay_map.get("overlay_map", {}),
                "OVERLAY_ENTRIES": overlay_map.get("overlay_entries", []),
            }
        except Exception as e:
            log_warning_safe(self.logger, f"Overlay generation failed: {e}")
            return {
                "OVERLAY_MAP": {},
                "OVERLAY_ENTRIES": [],
            }

    def _merge_donor_template(
        self, context: Dict[str, Any], donor: Dict[str, Any]
    ) -> TemplateContext:
        """Merge donor template with context."""
        # Deep merge, preferring context values
        merged = dict(donor)
        for key, value in context.items():
            if (
                key in merged
                and isinstance(value, dict)
                and isinstance(merged[key], dict)
            ):
                # Recursive merge for nested dicts
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        return merged  # type: ignore

    def _validate_context_completeness(self, context: TemplateContext):
        """Validate context has all required fields."""
        required_sections = [
            "device_config",
            "config_space",
            "bar_config",
            "interrupt_config",
        ]

        for section in required_sections:
            if section not in context or not context[section]:  # type: ignore
                raise ContextError(f"Missing required section: {section}")

        # Validate device signature
        if "device_signature" not in context or not context["device_signature"]:
            raise ContextError("Missing device signature")

        # Validate identifiers
        if "vendor_id" not in context or "device_id" not in context:
            raise ContextError("Missing device identifiers")
