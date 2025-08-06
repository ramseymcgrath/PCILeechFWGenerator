#!/usr/bin/env python3
"""
PCILeech Template Context Builder

This module builds comprehensive template context from device profiling data,
integrating data from BehaviorProfiler, ConfigSpaceManager, and MSIXCapability
to provide structured context for all PCILeech templates.

The context builder ensures all required data is present and provides validation
to prevent template rendering failures. The system fails if data is incomplete to ensure firmware uniqueness.

Key improvements in this version:
- Enhanced type safety with comprehensive type hints
- Better error handling with context managers
- Performance optimizations through caching and lazy evaluation
- Reduced complexity through functional decomposition
- Improved testability with dependency injection
"""

import contextlib
import ctypes
import fcntl
import hashlib
import logging
import os
import struct
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from functools import lru_cache, cached_property
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple, Protocol, TypeVar, cast

from ..error_utils import extract_root_cause
from ..exceptions import ContextError
from ..string_utils import (
    format_bar_summary_table,
    format_bar_table,
    format_raw_bar_table,
    log_error_safe,
    log_info_safe,
    log_warning_safe,
)
from .behavior_profiler import BehaviorProfile
from .config_space_manager import BarInfo
from .fallback_manager import FallbackManager
from .overlay_mapper import OverlayMapper

logger = logging.getLogger(__name__)

# Import proper VFIO constants with kernel-compatible ioctl generation
from ..cli.vfio_constants import (
    VFIO_DEVICE_GET_REGION_INFO,
    VFIO_GROUP_GET_DEVICE_FD,
    VFIO_REGION_INFO_FLAG_MMAP,
    VFIO_REGION_INFO_FLAG_READ,
    VFIO_REGION_INFO_FLAG_WRITE,
    VfioRegionInfo,
)

# Type aliases for clarity
ConfigSpaceData = Dict[str, Any]
MSIXData = Dict[str, Any]
TemplateContext = Dict[str, Any]


class ValidationLevel(Enum):
    """Validation strictness levels."""

    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


# Alias for backward compatibility
PCILeechContextError = ContextError


# Constants moved to module level for better organization
class PCIConstants:
    """PCIe-related constants."""

    MIN_CONFIG_SPACE_SIZE = 256
    MAX_CONFIG_SPACE_SIZE = 4096
    MIN_BAR_INDEX = 0
    MAX_BAR_INDEX = 5

    # BAR type constants
    BAR_TYPE_MEMORY_32BIT = 0
    BAR_TYPE_MEMORY_64BIT = 1

    # Common BAR sizes
    DEFAULT_BAR_SIZE = 4096  # 4KB
    DEFAULT_IO_BAR_SIZE = 256

    # Device class prefixes
    CLASS_NETWORK = "02"
    CLASS_STORAGE = "01"
    CLASS_DISPLAY = "03"
    CLASS_AUDIO = "040"
    CLASS_MULTIMEDIA = "048"

    # Power states
    POWER_STATE_D0 = "D0"
    POWER_STATE_D3_COLD = "D3cold"
    POWER_STATE_D3_HOT = "D3hot"
    POWER_STATE_D3 = "D3"


@dataclass
class DeviceIdentifiers:
    """Device identification data with enhanced validation and utilities."""

    vendor_id: str
    device_id: str
    class_code: str
    revision_id: str
    subsystem_vendor_id: Optional[str] = None
    subsystem_device_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate device identifiers."""
        if not all([self.vendor_id, self.device_id, self.class_code, self.revision_id]):
            raise ContextError("Device identifiers cannot be empty")

        # Validate hex format and normalize
        self._validate_and_normalize_fields()

    def _validate_and_normalize_fields(self) -> None:
        """Validate hex format and normalize field values."""
        field_specs = [
            ("vendor_id", 4),
            ("device_id", 4),
            ("class_code", 6),
            ("revision_id", 2),
        ]

        for field_name, expected_length in field_specs:
            value = getattr(self, field_name)
            try:
                # Validate hex format
                int_value = int(value, 16)
                # Normalize to expected length with zero padding
                normalized = f"{int_value:0{expected_length}x}"
                setattr(self, field_name, normalized)
            except ValueError:
                raise ContextError(f"Invalid hex format for {field_name}: {value}")

        # Normalize optional fields if present
        if self.subsystem_vendor_id:
            self.subsystem_vendor_id = self._normalize_hex(self.subsystem_vendor_id, 4)
        if self.subsystem_device_id:
            self.subsystem_device_id = self._normalize_hex(self.subsystem_device_id, 4)

    @staticmethod
    def _normalize_hex(value: str, length: int) -> str:
        """Normalize a hex string to specified length."""
        try:
            int_value = int(value, 16)
            return f"{int_value:0{length}x}"
        except ValueError:
            return value

    @property
    def device_signature(self) -> str:
        """Generate a unique device signature."""
        return f"{self.vendor_id}:{self.device_id}"

    @property
    def full_signature(self) -> str:
        """Generate a full device signature including subsystem IDs."""
        subsys_vendor = self.subsystem_vendor_id or self.vendor_id
        subsys_device = self.subsystem_device_id or self.device_id
        return f"{self.vendor_id}:{self.device_id}:{subsys_vendor}:{subsys_device}"

    def get_device_class_type(self) -> str:
        """Get human-readable device class type."""
        class_prefix = self.class_code[:2]
        class_map = {
            PCIConstants.CLASS_NETWORK: "Network Controller",
            PCIConstants.CLASS_STORAGE: "Storage Controller",
            PCIConstants.CLASS_DISPLAY: "Display Controller",
            PCIConstants.CLASS_AUDIO: "Audio Controller",
        }
        return class_map.get(class_prefix, "Unknown Device")


@dataclass
class BarConfiguration:
    """BAR configuration data with enhanced validation and utilities."""

    index: int
    base_address: int
    size: int
    bar_type: int
    prefetchable: bool
    is_memory: bool
    is_io: bool
    is_64bit: bool = field(default=False)
    _size_encoding: Optional[int] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate BAR configuration."""
        if not PCIConstants.MIN_BAR_INDEX <= self.index <= PCIConstants.MAX_BAR_INDEX:
            raise ContextError(f"Invalid BAR index: {self.index}")
        if self.size < 0:
            raise ContextError(f"Invalid BAR size: {self.size}")

        # Set is_64bit based on bar_type
        if self.is_memory and self.bar_type == PCIConstants.BAR_TYPE_MEMORY_64BIT:
            self.is_64bit = True

    def get_size_encoding(self) -> int:
        """Get the size encoding for this BAR, computing it if necessary."""
        if self._size_encoding is None:
            from src.device_clone.bar_size_converter import BarSizeConverter

            bar_type_str = "io" if self.is_io else "memory"
            self._size_encoding = BarSizeConverter.size_to_encoding(
                self.size, bar_type_str, self.is_64bit, self.prefetchable
            )
        return self._size_encoding

    @property
    def size_encoding(self) -> int:
        """Property wrapper for backward compatibility."""
        return self.get_size_encoding()

    @property
    def size_mb(self) -> float:
        """Get BAR size in megabytes."""
        return self.size / (1024 * 1024)

    @property
    def type_description(self) -> str:
        """Get human-readable BAR type description."""
        if self.is_io:
            return "I/O"
        elif self.is_64bit:
            return "64-bit Memory"
        else:
            return "32-bit Memory"

    def __str__(self) -> str:
        """String representation for logging."""
        return (
            f"BAR{self.index}: {self.type_description} "
            f"@ 0x{self.base_address:08X}, size={self.size} bytes "
            f"({self.size_mb:.2f} MB), prefetchable={self.prefetchable}"
        )


@dataclass
class TimingParameters:
    """Device timing parameters with validation and utilities."""

    read_latency: int
    write_latency: int
    burst_length: int
    inter_burst_gap: int
    timeout_cycles: int
    clock_frequency_mhz: float
    timing_regularity: float

    def __post_init__(self) -> None:
        """Validate timing parameters."""
        numeric_params = {
            "read_latency": self.read_latency,
            "write_latency": self.write_latency,
            "burst_length": self.burst_length,
            "inter_burst_gap": self.inter_burst_gap,
            "timeout_cycles": self.timeout_cycles,
            "timing_regularity": self.timing_regularity,
            "clock_frequency_mhz": self.clock_frequency_mhz,
        }

        for param_name, value in numeric_params.items():
            if value <= 0:
                raise ContextError(f"{param_name} must be positive, got {value}")

        if not 0 < self.timing_regularity <= 1.0:
            raise ContextError(
                f"timing_regularity must be between 0 and 1, got {self.timing_regularity}"
            )

    @property
    def total_latency(self) -> int:
        """Calculate total read/write latency."""
        return self.read_latency + self.write_latency

    @property
    def effective_bandwidth_mbps(self) -> float:
        """Estimate effective bandwidth in MB/s."""
        # Simplified calculation based on burst parameters
        cycles_per_burst = self.burst_length + self.inter_burst_gap
        bursts_per_second = (self.clock_frequency_mhz * 1e6) / cycles_per_burst
        bytes_per_burst = self.burst_length * 4  # Assuming 32-bit transfers
        return (bursts_per_second * bytes_per_burst) / 1e6

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with additional computed values."""
        base_dict = asdict(self)
        base_dict.update(
            {
                "total_latency": self.total_latency,
                "effective_bandwidth_mbps": self.effective_bandwidth_mbps,
            }
        )
        return base_dict


class VFIODeviceManager:
    """Manages VFIO device operations with proper resource management."""

    def __init__(self, device_bdf: str, logger: logging.Logger):
        """Initialize VFIO device manager."""
        self.device_bdf = device_bdf
        self.logger = logger
        self._device_fd: Optional[int] = None
        self._container_fd: Optional[int] = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()

    def open(self) -> Tuple[int, int]:
        """Open VFIO device and container file descriptors."""
        if self._device_fd is not None and self._container_fd is not None:
            return self._device_fd, self._container_fd

        from ..cli.vfio_helpers import get_device_fd

        log_info_safe(
            self.logger,
            "Opening VFIO device FD for device {bdf}",
            bdf=self.device_bdf,
            prefix="VFIO",
        )

        try:
            self._device_fd, self._container_fd = get_device_fd(self.device_bdf)
            log_info_safe(
                self.logger,
                "Successfully opened VFIO device FD {fd} and container FD {cont_fd}",
                fd=self._device_fd,
                cont_fd=self._container_fd,
                prefix="VFIO",
            )
            return self._device_fd, self._container_fd
        except Exception as e:
            log_error_safe(
                self.logger,
                "Failed to open VFIO device FD: {error}",
                error=str(e),
                prefix="VFIO",
            )
            raise

    def close(self) -> None:
        """Close VFIO file descriptors."""
        if self._device_fd is not None:
            try:
                os.close(self._device_fd)
                self._device_fd = None
            except OSError:
                pass

        if self._container_fd is not None:
            try:
                os.close(self._container_fd)
                self._container_fd = None
            except OSError:
                pass

    def get_region_info(self, index: int) -> Optional[Dict[str, Any]]:
        """Get VFIO region information."""
        if self._device_fd is None:
            self.open()

        info = VfioRegionInfo()
        info.argsz = ctypes.sizeof(VfioRegionInfo)
        info.index = index

        try:
            # Ensure device_fd is not None after open()
            assert self._device_fd is not None
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
            log_error_safe(
                self.logger,
                "VFIO region info ioctl failed for index {index}: {error}",
                index=index,
                error=str(e),
                prefix="VFIO",
            )
            return None


class PCILeechContextBuilder:
    """
    Builds comprehensive template context from device profiling data.

    This class integrates data from multiple sources to create a unified
    template context that can be used for all PCILeech template rendering.

    Key principles:
    - Strict validation of all input data
    - Comprehensive error reporting
    - Deterministic context generation
    - Resource management with context managers
    - Performance optimization through caching
    """

    # Required fields for validation
    REQUIRED_DEVICE_FIELDS = ["vendor_id", "device_id", "class_code", "revision_id"]
    REQUIRED_MSIX_FIELDS = ["table_size", "table_bir", "table_offset"]

    def __init__(
        self,
        device_bdf: str,
        config: Any,
        validation_level: ValidationLevel = ValidationLevel.STRICT,
        fallback_manager: Optional[FallbackManager] = None,
    ):
        """
        Initialize the context builder.

        Args:
            device_bdf: Device Bus:Device.Function identifier
            config: PCILeech generation configuration
            validation_level: Strictness of validation
            fallback_manager: Optional fallback manager for controlling fallback behavior
        """
        if not device_bdf or not device_bdf.strip():
            raise ContextError("Device BDF cannot be empty")

        self.device_bdf = device_bdf.strip()
        self.config = config
        self.validation_level = validation_level
        self.logger = logging.getLogger(__name__)
        self._context_cache: Dict[str, Any] = {}
        self._vfio_manager = VFIODeviceManager(self.device_bdf, self.logger)

        # Initialize fallback manager with default settings if not provided
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
    ) -> Dict[str, Any]:
        """
        Build comprehensive template context from all data sources.

        Args:
            behavior_profile: Device behavior profile data
            config_space_data: Configuration space analysis data
            msix_data: MSI-X capability data (None if not available)
            interrupt_strategy: Interrupt strategy ("msix", "msi", or "intx")
            interrupt_vectors: Number of interrupt vectors

        Returns:
            Comprehensive template context dictionary

        Raises:
            ContextError: If context building fails or data is incomplete
        """
        log_info_safe(
            self.logger,
            "Building PCILeech template context for device {bdf} with {strategy} interrupts ({vectors} vectors)",
            bdf=self.device_bdf,
            strategy=interrupt_strategy,
            vectors=interrupt_vectors,
        )

        # Pre-validate all input data
        self._validate_input_data(config_space_data, msix_data, behavior_profile)

        try:
            # Extract device identifiers first (required for all other operations)
            device_identifiers = self._extract_device_identifiers(config_space_data)

            # Build context sections with strict validation
            device_config = self._build_device_config(
                device_identifiers, behavior_profile, config_space_data
            )
            config_space = self._build_config_space_context(config_space_data)
            msix_config = self._build_msix_context(msix_data)
            bar_config = self._build_bar_config(config_space_data, behavior_profile)
            timing_config = self._build_timing_config(
                behavior_profile, device_identifiers
            )
            pcileech_config = self._build_pcileech_config(device_identifiers)

            # Generate overlay mapping for configuration space shadow
            overlay_config = self._build_overlay_config(config_space_data)

            # Generate unique device signature
            device_signature = self._generate_unique_device_signature(
                device_identifiers, behavior_profile, config_space_data
            )

            # Build interrupt configuration
            interrupt_config = {
                "strategy": interrupt_strategy,
                "vectors": interrupt_vectors,
                "msix_available": msix_data is not None,
            }

            # Build active device configuration
            active_device_config = self._build_active_device_config(
                device_identifiers, interrupt_strategy, interrupt_vectors
            )

            # Assemble complete context
            context = {
                "device_config": device_config,
                "config_space": config_space,
                "msix_config": msix_config,
                "interrupt_config": interrupt_config,
                "active_device_config": active_device_config,
                "bar_config": bar_config,
                "timing_config": timing_config,
                "pcileech_config": pcileech_config,
                "device_signature": device_signature,
                "generation_metadata": self._build_generation_metadata(
                    device_identifiers
                ),
                # Add extended configuration pointers at top level for easy template access
                "EXT_CFG_CAP_PTR": device_config.get("ext_cfg_cap_ptr", 0x100),
                "EXT_CFG_XP_CAP_PTR": device_config.get("ext_cfg_xp_cap_ptr", 0x100),
                # Add overlay mapping for configuration space shadow
                **overlay_config,  # This adds OVERLAY_MAP and OVERLAY_ENTRIES
            }

            # Merge donor template if provided
            if donor_template:
                context = self._merge_donor_template(context, donor_template)

            # Final validation
            self._validate_context_completeness(context)

            log_info_safe(
                self.logger,
                "PCILeech template context built successfully with signature {signature}",
                signature=device_signature,
            )

            return context

        except Exception as e:
            root_cause = extract_root_cause(e)
            log_error_safe(
                self.logger,
                "Failed to build PCILeech template context: {error}",
                error=root_cause,
            )
            raise ContextError("Context building failed", root_cause=root_cause)

    def _validate_input_data(
        self,
        config_space_data: Dict[str, Any],
        msix_data: Optional[Dict[str, Any]],
        behavior_profile: Optional[BehaviorProfile],
    ) -> None:
        """
        Validate all input data before processing.

        Args:
            config_space_data: Configuration space data
            msix_data: MSI-X capability data (None if not available)
            behavior_profile: Device behavior profile

        Raises:
            ContextError: If validation fails
        """
        missing_data = []

        # Validate config space data
        if not config_space_data:
            missing_data.append("config_space_data")
        else:
            for field in self.REQUIRED_DEVICE_FIELDS:
                if field not in config_space_data or not config_space_data[field]:
                    missing_data.append(f"config_space_data.{field}")

            # Validate config space size
            config_size = config_space_data.get("config_space_size", 0)
            if config_size < PCIConstants.MIN_CONFIG_SPACE_SIZE:
                # Log warning but don't fail - many devices only expose 64 bytes via sysfs
                log_warning_safe(
                    self.logger,
                    "Config space size ({size}) is less than ideal minimum ({min_size}), "
                    "but proceeding as this is common for sysfs-based reads",
                    size=config_size,
                    min_size=PCIConstants.MIN_CONFIG_SPACE_SIZE,
                    prefix="CONF",
                )
                # Only fail in strict mode if we have absolutely no config space data
                if self.validation_level == ValidationLevel.STRICT and config_size == 0:
                    missing_data.append(
                        f"config_space_data.config_space_size (got {config_size})"
                    )
            elif config_size > PCIConstants.MAX_CONFIG_SPACE_SIZE:
                missing_data.append(
                    f"config_space_data.config_space_size (got {config_size})"
                )

        # Validate MSI-X data if present
        if msix_data and msix_data.get("capability_info"):
            capability_info = msix_data["capability_info"]
            for field in self.REQUIRED_MSIX_FIELDS:
                if field not in capability_info:
                    missing_data.append(f"msix_data.capability_info.{field}")

        # Validate behavior profile if present
        if behavior_profile:
            if (
                not hasattr(behavior_profile, "total_accesses")
                or behavior_profile.total_accesses <= 0
            ):
                missing_data.append("behavior_profile.total_accesses")
            if (
                not hasattr(behavior_profile, "capture_duration")
                or behavior_profile.capture_duration <= 0
            ):
                missing_data.append("behavior_profile.capture_duration")

        if missing_data and self.validation_level == ValidationLevel.STRICT:
            raise ContextError(
                f"Missing required data for unique firmware generation: {missing_data}"
            )
        elif missing_data:
            log_warning_safe(
                self.logger,
                "Missing data detected but continuing with {level} validation: {missing}",
                level=self.validation_level.value,
                missing=missing_data,
                prefix="VLDN",
            )

    def _extract_device_identifiers(
        self, config_space_data: Dict[str, Any]
    ) -> DeviceIdentifiers:
        """
        Extract and validate device identifiers with enhanced subsystem ID handling.

        Args:
            config_space_data: Configuration space data

        Returns:
            Validated device identifiers

        Raises:
            ContextError: If identifiers are missing or invalid
        """
        try:
            # Extract main identifiers
            vendor_id = config_space_data["vendor_id"]
            device_id = config_space_data["device_id"]
            class_code = config_space_data["class_code"]
            revision_id = config_space_data["revision_id"]

            # Extract subsystem identifiers with enhanced fallback logic
            subsystem_vendor_id = config_space_data.get("subsystem_vendor_id")
            subsystem_device_id = config_space_data.get("subsystem_device_id")

            # Log raw extraction for debugging
            log_info_safe(
                self.logger,
                "Raw identifier extraction - Main: vendor={vendor}, device={device}, Subsystem: vendor={subsys_vendor}, device={subsys_device}",
                vendor=vendor_id,
                device=device_id,
                subsys_vendor=subsystem_vendor_id,
                subsys_device=subsystem_device_id,
                prefix="IDENT",
            )

            # Convert to hex strings for consistency
            if isinstance(vendor_id, int):
                vendor_id = f"{vendor_id:04x}"
            if isinstance(device_id, int):
                device_id = f"{device_id:04x}"
            if isinstance(class_code, int):
                class_code = f"{class_code:06x}"
            if isinstance(revision_id, int):
                revision_id = f"{revision_id:02x}"

            # Enhanced subsystem ID handling
            if subsystem_vendor_id is None or subsystem_vendor_id == 0:
                log_warning_safe(
                    self.logger,
                    "Subsystem vendor ID is None or 0, using main vendor ID {vendor}",
                    vendor=vendor_id,
                    prefix="IDENT",
                )
                subsystem_vendor_id = vendor_id
            elif isinstance(subsystem_vendor_id, int):
                subsystem_vendor_id = f"{subsystem_vendor_id:04x}"

            if subsystem_device_id is None or subsystem_device_id == 0:
                log_warning_safe(
                    self.logger,
                    "Subsystem device ID is None or 0, using main device ID {device}",
                    device=device_id,
                    prefix="IDENT",
                )
                subsystem_device_id = device_id
            elif isinstance(subsystem_device_id, int):
                subsystem_device_id = f"{subsystem_device_id:04x}"

            # Final validation
            if not subsystem_vendor_id or subsystem_vendor_id == "0000":
                subsystem_vendor_id = vendor_id
                log_info_safe(
                    self.logger,
                    "Final fallback: subsystem vendor ID -> {vendor}",
                    vendor=vendor_id,
                    prefix="IDENT",
                )

            if not subsystem_device_id or subsystem_device_id == "0000":
                subsystem_device_id = device_id
                log_info_safe(
                    self.logger,
                    "Final fallback: subsystem device ID -> {device}",
                    device=device_id,
                    prefix="IDENT",
                )

            # Log final extraction result
            log_info_safe(
                self.logger,
                "Final device identifiers - Main: {vendor}:{device}, Subsystem: {subsys_vendor}:{subsys_device}",
                vendor=vendor_id,
                device=device_id,
                subsys_vendor=subsystem_vendor_id,
                subsys_device=subsystem_device_id,
                prefix="IDENT",
            )

            return DeviceIdentifiers(
                vendor_id=vendor_id,
                device_id=device_id,
                class_code=class_code,
                revision_id=revision_id,
                subsystem_vendor_id=subsystem_vendor_id,
                subsystem_device_id=subsystem_device_id,
            )
        except KeyError as e:
            raise ContextError(f"Missing required device identifier: {e}")

    def _build_device_config(
        self,
        device_identifiers: DeviceIdentifiers,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build device configuration context.

        Args:
            device_identifiers: Validated device identifiers
            behavior_profile: Device behavior profile
            config_space_data: Configuration space data

        Returns:
            Device configuration context
        """
        device_config = {
            "device_bdf": self.device_bdf,
            **asdict(device_identifiers),
            "enable_error_injection": getattr(
                self.config, "enable_advanced_features", False
            ),
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

        # Ensure subsystem IDs are available as hex strings for templates
        if device_identifiers.subsystem_vendor_id:
            device_config["subsystem_vendor_id_hex"] = (
                f"0x{int(device_identifiers.subsystem_vendor_id, 16):04X}"
            )
        if device_identifiers.subsystem_device_id:
            device_config["subsystem_device_id_hex"] = (
                f"0x{int(device_identifiers.subsystem_device_id, 16):04X}"
            )

        # Add extended configuration space pointers if available
        if hasattr(self.config, "device_config") and self.config.device_config:
            device_capabilities = getattr(
                self.config.device_config, "capabilities", None
            )
            if device_capabilities:
                device_config["ext_cfg_cap_ptr"] = getattr(
                    device_capabilities, "ext_cfg_cap_ptr", 0x100
                )
                device_config["ext_cfg_xp_cap_ptr"] = getattr(
                    device_capabilities, "ext_cfg_xp_cap_ptr", 0x100
                )

        # Add behavior profile data if available
        if behavior_profile:
            device_config.update(
                {
                    "behavior_profile": self._serialize_behavior_profile(
                        behavior_profile
                    ),
                    "total_register_accesses": behavior_profile.total_accesses,
                    "capture_duration": behavior_profile.capture_duration,
                    "timing_patterns_count": len(behavior_profile.timing_patterns),
                    "state_transitions_count": len(behavior_profile.state_transitions),
                    "has_manufacturing_variance": (
                        hasattr(behavior_profile, "variance_metadata")
                        and behavior_profile.variance_metadata is not None
                    ),
                }
            )

            # Add pattern analysis if available
            if hasattr(behavior_profile, "pattern_analysis"):
                device_config["pattern_analysis"] = behavior_profile.pattern_analysis

        return device_config

    def _serialize_behavior_profile(
        self, behavior_profile: BehaviorProfile
    ) -> Dict[str, Any]:
        """
        Serialize behavior profile for template context.

        Args:
            behavior_profile: Behavior profile to serialize

        Returns:
            Serialized behavior profile data

        Raises:
            ContextError: If serialization fails
        """
        try:
            # Convert dataclass to dictionary
            profile_dict = asdict(behavior_profile)

            # Convert any non-serializable objects to deterministic strings
            for key, value in profile_dict.items():
                if hasattr(value, "__dict__"):
                    # Create deterministic string representation
                    profile_dict[key] = f"{type(value).__name__}_{hash(str(value))}"

            return profile_dict

        except Exception as e:
            raise ContextError(f"Failed to serialize behavior profile: {e}")

    def _build_config_space_context(
        self, config_space_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build configuration space context with validation.

        Args:
            config_space_data: Configuration space data

        Returns:
            Configuration space context

        Raises:
            ContextError: If required data is missing
        """
        required_fields = ["config_space_hex", "config_space_size", "bars"]
        missing_fields = [
            field for field in required_fields if field not in config_space_data
        ]

        if missing_fields and self.validation_level == ValidationLevel.STRICT:
            raise ContextError(
                f"Missing required config space fields: {missing_fields}"
            )

        return {
            "raw_data": config_space_data["config_space_hex"],
            "size": config_space_data["config_space_size"],
            "device_info": config_space_data.get("device_info", {}),
            "vendor_id": config_space_data["vendor_id"],
            "device_id": config_space_data["device_id"],
            "class_code": config_space_data["class_code"],
            "revision_id": config_space_data["revision_id"],
            "bars": config_space_data["bars"],
            "has_extended_config": config_space_data["config_space_size"] > 256,
        }

    def _build_msix_context(
        self, msix_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build MSI-X configuration context.

        Args:
            msix_data: MSI-X capability data

        Returns:
            MSI-X configuration context
        """
        if not msix_data or not msix_data.get("capability_info"):
            # MSI-X not supported - return disabled configuration
            return {
                "num_vectors": 0,
                "table_bir": 0,
                "table_offset": 0,
                "pba_bir": 0,
                "pba_offset": 0,
                "enabled": False,
                "function_mask": False,
                "is_supported": False,
                "validation_errors": [],
                "is_valid": False,
                "table_size_bytes": 0,
                "pba_size_bytes": 0,
                # Template variables
                "table_size": 0,
                "table_size_minus_one": 0,
                "table_offset_bir": 0,
                "pba_offset_bir": 0,
                "enabled_val": 0,
                "function_mask_val": 0,
                "pba_size": 0,
                "pba_size_minus_one": 0,
                "alignment_warning": "",
            }

        capability_info = msix_data["capability_info"]
        table_size = capability_info["table_size"]
        table_offset = capability_info["table_offset"]
        pba_offset = capability_info.get("pba_offset", table_offset + (table_size * 16))

        # Calculate PBA size in DWORDs
        pba_size_dwords = (table_size + 31) // 32

        # Check alignment and generate warning if needed
        alignment_warning = ""
        if table_offset % 8 != 0:
            alignment_warning = f"// WARNING: MSI-X table offset 0x{table_offset:x} is not 8-byte aligned"

        return {
            "num_vectors": table_size,
            "table_bir": capability_info["table_bir"],
            "table_offset": table_offset,
            "pba_bir": capability_info.get("pba_bir", capability_info["table_bir"]),
            "pba_offset": pba_offset,
            "enabled": capability_info.get("enabled", False),
            "function_mask": capability_info.get("function_mask", False),
            "is_supported": table_size > 0,
            "validation_errors": msix_data.get("validation_errors", []),
            "is_valid": msix_data.get("is_valid", True),
            "table_size_bytes": table_size * 16,  # 16 bytes per entry
            "pba_size_bytes": pba_size_dwords * 4,  # PBA size in bytes
            # Template variables for MSI-X templates
            "table_size": table_size,
            "table_size_minus_one": table_size - 1,
            "table_offset_bir": (table_offset & 0xFFFFFFF8)
            | (capability_info["table_bir"] & 0x7),
            "pba_offset_bir": (pba_offset & 0xFFFFFFF8)
            | (capability_info.get("pba_bir", capability_info["table_bir"]) & 0x7),
            "enabled_val": 1 if capability_info.get("enabled", False) else 0,
            "function_mask_val": (
                1 if capability_info.get("function_mask", False) else 0
            ),
            "pba_size": pba_size_dwords,
            "pba_size_minus_one": max(0, pba_size_dwords - 1),
            "alignment_warning": alignment_warning,
            # SystemVerilog template constants
            "NUM_MSIX": table_size,
            "MSIX_TABLE_BIR": capability_info["table_bir"],
            "MSIX_TABLE_OFFSET": f"32'h{table_offset:08X}",
            "MSIX_PBA_BIR": capability_info.get(
                "pba_bir", capability_info["table_bir"]
            ),
            "MSIX_PBA_OFFSET": f"32'h{pba_offset:08X}",
            # Template control flags
            "RESET_CLEAR": True,
            "USE_BYTE_ENABLES": True,
            "WRITE_PBA_ALLOWED": False,
            "INIT_TABLE": True,
            "INIT_PBA": True,
        }

    def _build_bar_config(
        self,
        config_space_data: Dict[str, Any],
        behavior_profile: Optional[BehaviorProfile],
    ) -> Dict[str, Any]:
        """
        Build BAR configuration context using VFIO region info.

        Fetches each BAR's true size via VFIO_DEVICE_GET_REGION_INFO,
        considers any MMIO BAR with size > 0 a valid candidate,
        chooses the largest such BAR as primary, and raises ContextError
        only if all BARs are size 0 or I/O-port.

        This method now includes power state checking and device wake functionality
        to handle devices that report BAR size 0 when in D3 power state.

        Args:
            config_space_data: Configuration space data
            behavior_profile: Device behavior profile

        Returns:
            BAR configuration context

        Raises:
            ContextError: If no valid MMIO BARs found
        """
        # Check and fix device power state before analyzing BARs
        self._check_and_fix_power_state()

        bars = config_space_data["bars"]
        bar_configs = []
        primary_bar = None

        # Log raw BAR data from config space using table format
        log_info_safe(
            self.logger,
            "Analyzing BARs for device {bdf} with {count} BARs",
            bdf=self.device_bdf,
            count=len(bars),
            prefix="BARA",
        )

        # Display raw BAR data in table format
        raw_bar_table = format_raw_bar_table(bars, self.device_bdf)
        log_info_safe(self.logger, "Raw BAR Configuration:")
        for line in raw_bar_table.split("\n"):
            log_info_safe(self.logger, line)

        # First pass: Collect all BAR information
        for i in range(len(bars)):
            try:
                bar_data = bars[i]
                bar_info = self._get_vfio_bar_info(i, bar_data)

                if bar_info is not None:
                    bar_configs.append(bar_info)
                    log_info_safe(
                        self.logger,
                        "BAR {index} VFIO info: {info}",
                        index=bar_info.index,
                        info=asdict(bar_info),
                        prefix="BARA",
                    )
                else:
                    # Log why this BAR was skipped
                    if isinstance(bar_data, dict):
                        bar_type = bar_data.get("type", "unknown")
                        size = bar_data.get("size", 0)
                        if bar_type == "memory" and size == 0:
                            log_info_safe(
                                self.logger,
                                "BAR {num}: Skipped (memory BAR with size 0)",
                                num=i,
                                prefix="BARA",
                            )
                        elif bar_type == "io":
                            log_info_safe(
                                self.logger,
                                "BAR {num}: Skipped (I/O BAR - not suitable for MMIO)",
                                num=i,
                                prefix="BARA",
                            )
                        else:
                            log_info_safe(
                                self.logger,
                                "BAR {num}: Skipped (type={type}, size={size})",
                                num=i,
                                type=bar_type,
                                size=size,
                                prefix="BARA",
                            )
                    else:
                        log_info_safe(
                            self.logger,
                            "BAR {num}: Skipped (invalid or not implemented)",
                            num=i,
                            prefix="BARA",
                        )

            except Exception as e:
                log_warning_safe(
                    self.logger,
                    "Failed to analyze BAR {index}: {error}",
                    index=i,
                    error=str(e),
                    prefix="BARA",
                )
                continue

        # Always display BAR information for debugging, even if no valid BARs found
        log_info_safe(self.logger, "=== BAR Configuration Summary ===", prefix="BARA")
        if not bar_configs:
            log_info_safe(
                self.logger,
                "No valid MMIO BARs found - all BARs are either size 0 or I/O-port",
                prefix="BARA",
            )
        else:
            # Display detailed BAR table
            detailed_table = format_bar_table(bar_configs, primary_bar)
            log_info_safe(self.logger, "Detailed BAR Configuration:", prefix="BARA")
            for line in detailed_table.split("\n"):
                log_info_safe(self.logger, line)

            # Display compact summary table
            summary_table = format_bar_summary_table(bar_configs, primary_bar)
            log_info_safe(self.logger, "\nBAR Summary:", prefix="BARA")
            for line in summary_table.split("\n"):
                log_info_safe(self.logger, line)

            # Log primary BAR selection details
            if primary_bar:
                log_info_safe(
                    self.logger,
                    "\nPrimary BAR selected: index={index}, size={size} bytes ({mb:.2f} MB), type={type}",
                    index=primary_bar.index,
                    size=primary_bar.size,
                    mb=primary_bar.size / (1024 * 1024),
                    type="memory" if primary_bar.is_memory else "io",
                    prefix="BARA",
                )

        log_info_safe(self.logger, "=" * 70)

        # Second pass: Select the primary BAR from candidates
        memory_bars = [bar for bar in bar_configs if bar.is_memory and bar.size > 0]

        if memory_bars:
            # Choose the largest memory BAR as primary
            primary_bar = max(memory_bars, key=lambda bar: bar.size)
            log_info_safe(
                self.logger,
                "Primary BAR selected: index={index}, size={size} bytes ({mb:.2f} MB), type={type}",
                index=primary_bar.index,
                size=primary_bar.size,
                mb=primary_bar.size / (1024 * 1024),
                type="memory" if primary_bar.is_memory else "io",
                prefix="BARA",
            )
        # Raise error only if all BARs are size 0 or I/O-port
        if primary_bar is None:
            raise ContextError(
                "No valid MMIO BARs found - all BARs are either size 0 or I/O-port"
            )

        bar_config = {
            "bar_index": primary_bar.index,
            "aperture_size": primary_bar.size,
            "bar_type": primary_bar.bar_type,
            "prefetchable": primary_bar.prefetchable,
            "memory_type": "memory" if primary_bar.is_memory else "io",
            "bars": bar_configs,
        }

        # Add behavior-based adjustments
        if behavior_profile:
            bar_config.update(
                self._adjust_bar_config_for_behavior(bar_config, behavior_profile)
            )

        return bar_config

    def _get_vfio_bar_info(self, index: int, bar_data) -> Optional[BarConfiguration]:
        """
        Get BAR information using VFIO region info.

        Args:
            index: BAR index (0-5)
            bar_data: BAR data from config space

        Returns:
            BAR configuration or None if BAR is not valid

        Raises:
            ContextError: If VFIO access fails
        """
        try:
            log_info_safe(
                self.logger,
                "Analyzing BAR {index} with data: {data}",
                index=index,
                data=bar_data,
                prefix="BARA",
            )
            # Try to get VFIO region info for accurate size
            region_info = self._get_vfio_region_info(index)
            if region_info:
                log_info_safe(
                    self.logger,
                    "VFIO region info for BAR {index}: {info}",
                    index=index,
                    info=region_info,
                    prefix="BARA",
                )
                size = region_info["size"]
                flags = region_info["flags"]

                # Determine BAR properties from config space data
                if isinstance(bar_data, dict):
                    log_info_safe(
                        self.logger,
                        "BAR {index} data: {data}",
                        index=index,
                        data=bar_data,
                        prefix="BARA",
                    )
                    bar_type_str = bar_data.get("type", "memory")
                    is_memory = bar_type_str == "memory"
                    is_io = bar_type_str == "io"
                    base_address = bar_data.get("address", 0)
                    prefetchable = bar_data.get("prefetchable", False)
                    bar_type = 1 if bar_data.get("is_64bit", False) else 0
                elif isinstance(bar_data, BarInfo):
                    # 新增支持 BarInfo 类型
                    log_info_safe(
                        self.logger,
                        "BAR {index} data (BarInfo): {data}",
                        index=index,
                        data=str(bar_data),
                        prefix="BARA",
                    )
                    is_memory = bar_data.bar_type == "memory"
                    is_io = bar_data.bar_type == "io"
                    base_address = bar_data.address
                    prefetchable = bar_data.prefetchable
                    bar_type = 1 if bar_data.is_64bit else 0

                elif isinstance(bar_data, int):
                    log_info_safe(
                        self.logger,
                        "BAR {index} data (int raw): {data}",
                        index=index,
                        data=bar_data,
                        prefix="BARA",
                    )
                    bar_value = bar_data
                    if bar_value == 0:
                        return None

                    is_memory = (bar_value & 0x1) == 0
                    is_io = not is_memory

                    if is_memory:
                        bar_type = (bar_value >> 1) & 0x3
                        prefetchable = bool((bar_value >> 3) & 0x1)
                        base_address = bar_value & 0xFFFFFFF0
                    else:
                        bar_type = 0
                        prefetchable = False
                        base_address = bar_value & 0xFFFFFFFC

                elif hasattr(bar_data, "address") and hasattr(bar_data, "type"):
                    # Support BarInfo object
                    log_info_safe(
                        self.logger,
                        "BAR {index} data (BarInfo): {data}",
                        index=index,
                        data=str(bar_data),
                        prefix="BARA",
                    )
                    is_memory = bar_data.type == "memory"
                    is_io = not is_memory
                    base_address = bar_data.address
                    prefetchable = getattr(bar_data, "prefetchable", False)
                    bar_type = 1 if getattr(bar_data, "is_64bit", False) else 0

                else:
                    raise TypeError(f"Unknown BAR data type: {type(bar_data)}")

                # Log detailed BAR analysis results
                log_info_safe(
                    self.logger,
                    "BAR {index} analysis complete - type: {type}, memory: {is_memory}, I/O: {is_io}, "
                    "size: {size}, address: 0x{address:x}, prefetchable: {prefetchable}",
                    index=index,
                    type="memory" if is_memory else "io",
                    is_memory=is_memory,
                    is_io=is_io,
                    size=size,
                    address=base_address,
                    prefetchable=prefetchable,
                    prefix="BARA",
                )

                # Only return valid memory BARs with size > 0 (I/O BARs are not suitable for MMIO)
                if is_memory and size > 0:
                    log_info_safe(
                        self.logger,
                        "BAR {index} is valid - creating BarConfiguration",
                        index=index,
                        prefix="BARA",
                    )
                    bar_config = BarConfiguration(
                        index=index,
                        base_address=base_address,
                        size=size,
                        bar_type=bar_type,
                        prefetchable=prefetchable,
                        is_memory=is_memory,
                        is_io=is_io,
                    )

                    # Compute and validate size encoding
                    if size > 0:
                        from src.device_clone.bar_size_converter import BarSizeConverter

                        try:
                            bar_type_str = "io" if is_io else "memory"
                            if BarSizeConverter.validate_bar_size(size, bar_type_str):
                                size_encoding = bar_config.get_size_encoding()
                                log_info_safe(
                                    self.logger,
                                    "BAR {index} size encoding: 0x{encoding:08X} for size {size} ({size_str})",
                                    index=index,
                                    encoding=size_encoding,
                                    size=size,
                                    size_str=BarSizeConverter.format_size(size),
                                    prefix="BARA",
                                )
                            else:
                                log_warning_safe(
                                    self.logger,
                                    "BAR {index} has invalid size {size} for {type} BAR",
                                    index=index,
                                    size=size,
                                    type=bar_type_str,
                                    prefix="BARA",
                                )
                        except Exception as e:
                            log_warning_safe(
                                self.logger,
                                "Failed to compute size encoding for BAR {index}: {error}",
                                index=index,
                                error=str(e),
                                prefix="BARA",
                            )

                    return bar_config
                else:
                    if is_memory and size == 0:
                        log_info_safe(
                            self.logger,
                            "BAR {index}: Skipped (memory BAR with zero size)",
                            index=index,
                            prefix="BARA",
                        )
                    elif is_io:
                        log_info_safe(
                            self.logger,
                            "BAR {index}: Skipped (I/O BAR - not suitable for MMIO)",
                            index=index,
                            prefix="BARA",
                        )

        except Exception as e:
            log_error_safe(
                self.logger,
                "VFIO region info failed for BAR {index}: {error}",
                index=index,
                error=str(e),
                prefix="BARA",
            )
            # NO FALLBACKS - fail fast when VFIO access fails
            raise ContextError(
                f"VFIO access failed for BAR {index}: {str(e)}. "
                f"Ensure device {self.device_bdf} is properly bound to vfio-pci and IOMMU is configured correctly."
            )

        # Explicitly return None if no valid BAR is found
        return None

    def _open_vfio_device_fd(self) -> tuple[int, int]:
        """Open the device FD using the complete VFIO workflow.

        Returns:
            Tuple of (device_fd, container_fd). Both must be closed when done.
        """
        from ..cli.vfio_helpers import get_device_fd

        log_info_safe(
            self.logger,
            "Opening VFIO device FD for device {bdf}",
            bdf=self.device_bdf,
            prefix="BARA",
        )

        try:
            device_fd, container_fd = get_device_fd(self.device_bdf)
            log_info_safe(
                self.logger,
                "Successfully opened VFIO device FD {fd} and container FD {cont_fd} for device {bdf}",
                fd=device_fd,
                cont_fd=container_fd,
                bdf=self.device_bdf,
                prefix="BARA",
            )
            return device_fd, container_fd
        except Exception as e:
            log_error_safe(
                self.logger,
                "Failed to open VFIO device FD for device {bdf}: {error}",
                bdf=self.device_bdf,
                error=str(e),
                prefix="BARA",
            )
            raise

    def _check_and_fix_power_state(self) -> None:
        """Check device power state and wake from D3 if needed."""
        try:
            power_state_file = f"/sys/bus/pci/devices/{self.device_bdf}/power_state"
            if os.path.exists(power_state_file):
                with open(power_state_file, "r") as f:
                    power_state = f.read().strip()

                log_info_safe(
                    self.logger,
                    "Device power state: {state}",
                    state=power_state,
                    prefix="PWR",
                )

                if power_state in ["D3cold", "D3hot", "D3"]:
                    log_warning_safe(
                        self.logger,
                        "Device is in power saving state {state}, attempting to wake...",
                        state=power_state,
                        prefix="PWR",
                    )

                    # Try to wake the device
                    power_control = (
                        f"/sys/bus/pci/devices/{self.device_bdf}/power/control"
                    )
                    if os.path.exists(power_control):
                        try:
                            # Set runtime PM to 'on'
                            subprocess.run(
                                ["sh", "-c", f"echo on > {power_control}"],
                                check=True,
                                capture_output=True,
                                text=True,
                            )

                            # Also try using setpci to set D0 state
                            result = subprocess.run(
                                ["setpci", "-s", self.device_bdf, "CAP_PM+4.b=0"],
                                capture_output=True,
                                text=True,
                            )
                            if result.returncode != 0:
                                log_warning_safe(
                                    self.logger,
                                    "setpci command failed: {error}",
                                    error=result.stderr,
                                    prefix="PWR",
                                )

                            # Give device time to wake
                            time.sleep(0.5)

                            # Check new power state
                            with open(power_state_file, "r") as f:
                                new_state = f.read().strip()

                            log_info_safe(
                                self.logger,
                                "Device power state after wake attempt: {old} -> {new}",
                                old=power_state,
                                new=new_state,
                                prefix="PWR",
                            )
                        except Exception as e:
                            log_warning_safe(
                                self.logger,
                                "Failed to wake device: {error}",
                                error=str(e),
                                prefix="PWR",
                            )
        except Exception as e:
            log_warning_safe(
                self.logger,
                "Failed to check power state: {error}",
                error=str(e),
                prefix="PWR",
            )

    def _get_vfio_region_info(self, index: int) -> Optional[Dict[str, Any]]:
        # First log sysfs BAR info for comparison
        try:
            resource_file = f"/sys/bus/pci/devices/{self.device_bdf}/resource{index}"
            if os.path.exists(resource_file):
                with open(resource_file, "r") as f:
                    line = f.read().strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 3:
                            start = int(parts[0], 16)
                            end = int(parts[1], 16)
                            sysfs_size = end - start + 1 if end >= start else 0
                            log_info_safe(
                                self.logger,
                                "BAR {index} sysfs shows size: {size} bytes (start: 0x{start:x}, end: 0x{end:x})",
                                index=index,
                                size=sysfs_size,
                                start=start,
                                end=end,
                                prefix="BARA",
                            )
        except Exception:
            pass

        log_info_safe(
            self.logger,
            "Attempting to get VFIO region info for BAR {index} on device {bdf}",
            index=index,
            bdf=self.device_bdf,
            prefix="BARA",
        )

        try:
            fd, cont_fd = self._open_vfio_device_fd()
            log_info_safe(
                self.logger,
                "Successfully opened VFIO device FD {fd} and container FD {cont_fd} for region info query",
                fd=fd,
                cont_fd=cont_fd,
                prefix="BARA",
            )
        except OSError as e:
            error_code = getattr(e, "errno", "unknown")
            if error_code == 22:  # EINVAL
                log_warning_safe(
                    self.logger,
                    "Failed to open VFIO device FD for region info: [Errno 22] Invalid argument - device may not be properly bound to vfio-pci or IOMMU issue",
                    prefix="BARA",
                )
            else:
                log_warning_safe(
                    self.logger,
                    "Failed to open VFIO device FD for region info: [Errno {errno}] {error}",
                    errno=error_code,
                    error=str(e),
                    prefix="BARA",
                )
            return None
        except Exception as e:
            log_warning_safe(
                self.logger,
                "Unexpected error opening VFIO device FD for region info: {error}",
                error=str(e),
                prefix="BARA",
            )
            return None

        try:
            info = VfioRegionInfo()
            info.argsz = ctypes.sizeof(VfioRegionInfo)
            info.index = index

            log_info_safe(
                self.logger,
                "Querying VFIO region info for index {index} with struct size {size}",
                index=index,
                size=info.argsz,
                prefix="BARA",
            )

            # mutate=True lets the kernel write back size/flags
            fcntl.ioctl(fd, VFIO_DEVICE_GET_REGION_INFO, info, True)

            log_info_safe(
                self.logger,
                "VFIO region info successful - index: {index}, size: {size}, flags: 0x{flags:x}",
                index=info.index,
                size=info.size,
                flags=info.flags,
                prefix="BARA",
            )

            result = {
                "index": info.index,
                "flags": info.flags,
                "size": info.size,
                "readable": bool(info.flags & VFIO_REGION_INFO_FLAG_READ),
                "writable": bool(info.flags & VFIO_REGION_INFO_FLAG_WRITE),
                "mappable": bool(info.flags & VFIO_REGION_INFO_FLAG_MMAP),
            }

            log_info_safe(
                self.logger,
                "VFIO region {index} properties - readable: {readable}, writable: {writable}, mappable: {mappable}",
                index=index,
                readable=result["readable"],
                writable=result["writable"],
                mappable=result["mappable"],
                prefix="BARA",
            )

            return result

        except OSError as e:
            log_error_safe(
                self.logger,
                "VFIO region info ioctl failed for index {index}: [Errno {errno}] {error}",
                index=index,
                errno=getattr(e, "errno", "unknown"),
                error=str(e),
                prefix="BARA",
            )
            return None
        finally:
            log_info_safe(
                self.logger,
                "Closing VFIO device FD {fd} and container FD {cont_fd}",
                fd=fd,
                cont_fd=cont_fd,
                prefix="BARA",
            )
            try:
                os.close(fd)
            except OSError:
                pass  # Already closed
            try:
                os.close(cont_fd)
            except OSError:
                pass  # Already closed

    @lru_cache(maxsize=1)
    def _get_vfio_group(self) -> str:
        """
        Return the IOMMU group number for the device.

        This method is cached since the IOMMU group doesn't change during runtime.
        """
        # Try sysfs first
        group = self._get_iommu_group_from_sysfs()
        if group:
            return group

        # Try container fallback
        group = self._get_iommu_group_from_container()
        if group:
            return group

        # Last resort
        log_warning_safe(
            self.logger,
            "All IOMMU group resolution methods failed, using fallback group '0'",
            prefix="IOMMU",
        )
        return "0"

    def _get_iommu_group_from_sysfs(self) -> Optional[str]:
        """Try to get IOMMU group from sysfs."""
        try:
            # Parse BDF components
            bdf_parts = self._parse_bdf()
            if not bdf_parts:
                return None

            dom, bus, dev, fn = bdf_parts
            iommu_path = Path(
                f"/sys/bus/pci/devices/{dom}:{bus}:{dev}.{fn}/iommu_group"
            )

            if iommu_path.exists():
                group_link = iommu_path.readlink()
                group_number = group_link.name
                log_info_safe(
                    self.logger,
                    "Successfully resolved IOMMU group via sysfs: {group}",
                    group=group_number,
                    prefix="IOMMU",
                )
                return group_number

        except Exception as e:
            log_warning_safe(
                self.logger,
                "Exception during sysfs IOMMU group resolution: {error}",
                error=str(e),
                prefix="IOMMU",
            )
        return None

    def _get_iommu_group_from_container(self) -> Optional[str]:
        """Try to get IOMMU group from container environment."""
        try:
            vfio_path = Path("/dev/vfio")
            if not vfio_path.exists():
                return None

            numeric_groups = [
                entry.name for entry in vfio_path.iterdir() if entry.name.isdigit()
            ]

            if numeric_groups:
                selected_group = numeric_groups[0]
                log_info_safe(
                    self.logger,
                    "Selected VFIO group from container enumeration: {group}",
                    group=selected_group,
                    prefix="IOMMU",
                )
                return selected_group

        except Exception as e:
            log_warning_safe(
                self.logger,
                "Exception during /dev/vfio enumeration: {error}",
                error=str(e),
                prefix="IOMMU",
            )
        return None

    def _parse_bdf(self) -> Optional[Tuple[str, str, str, str]]:
        """Parse BDF string into components."""
        try:
            # Handle both formats: "0000:00:00.0" and "00:00.0"
            if self.device_bdf.count(":") == 2:
                dom, bus_devfunc = self.device_bdf.split(":", 1)
            else:
                dom = "0000"
                bus_devfunc = self.device_bdf

            bus, dev_func = bus_devfunc.split(":")
            dev, fn = dev_func.split(".")

            return dom, bus, dev, fn
        except ValueError:
            log_error_safe(
                self.logger,
                "Invalid BDF format: {bdf}",
                bdf=self.device_bdf,
                prefix="BDF",
            )
            return None

    def _analyze_bar_fallback(self, index: int, bar_data) -> Optional[BarConfiguration]:
        """
        Fallback BAR analysis when VFIO is not available.

        This method provides intelligent size estimation based on device class,
        BAR type, and common patterns when hardware probing is not possible.

        Args:
            index: BAR index
            bar_data: BAR data

        Returns:
            BAR configuration or None
        """
        log_warning_safe(
            self.logger,
            "Falling back to intelligent BAR analysis for index {index} with data: {data}",
            index=index,
            data=bar_data,
            prefix="BARA",
        )

        # Handle both dict and int formats
        if isinstance(bar_data, dict):
            bar_type_str = bar_data.get("type", "memory")
            is_memory = bar_type_str == "memory"
            is_io = bar_type_str == "io"
            base_address = bar_data.get("address", 0)
            prefetchable = bar_data.get("prefetchable", False)
            size = bar_data.get("size", 0)

            # If size is available from config space, use it
            if size > 0:
                bar_type = 1 if bar_data.get("is_64bit", False) else 0
                log_info_safe(
                    self.logger,
                    "Fallback BAR {index}: Using config space size - type={type}, address=0x{address:08X}, size={size}, prefetchable={prefetchable}",
                    index=index,
                    type=bar_type_str,
                    address=base_address,
                    size=size,
                    prefetchable=prefetchable,
                    prefix="BARA",
                )

                return BarConfiguration(
                    index=index,
                    base_address=base_address,
                    size=size,
                    bar_type=bar_type,
                    prefetchable=prefetchable,
                    is_memory=is_memory,
                    is_io=is_io,
                )

            # If no size available but we have a valid address, estimate based on device type
            if base_address > 0 and is_memory:
                estimated_size = self._estimate_bar_size_from_device_context(
                    index, bar_data
                )
                bar_type = 1 if bar_data.get("is_64bit", False) else 0

                log_warning_safe(
                    self.logger,
                    "Fallback BAR {index}: Estimating size - type={type}, address=0x{address:08X}, estimated_size={size}, prefetchable={prefetchable}",
                    index=index,
                    type=bar_type_str,
                    address=base_address,
                    size=estimated_size,
                    prefetchable=prefetchable,
                    prefix="BARA",
                )

                return BarConfiguration(
                    index=index,
                    base_address=base_address,
                    size=estimated_size,
                    bar_type=bar_type,
                    prefetchable=prefetchable,
                    is_memory=is_memory,
                    is_io=is_io,
                )

            # Skip BARs with no address and no size
            return None

        else:
            # Handle integer BAR values
            bar_value = bar_data
            if bar_value == 0:
                return None

            is_memory = (bar_value & 0x1) == 0
            is_io = not is_memory

            if is_memory:
                bar_type = (bar_value >> 1) & 0x3
                prefetchable = bool((bar_value >> 3) & 0x1)
                base_address = bar_value & 0xFFFFFFF0
                # Estimate size based on device context and BAR properties
                size = self._estimate_bar_size_from_device_context(
                    index,
                    {
                        "type": "memory",
                        "address": base_address,
                        "prefetchable": prefetchable,
                    },
                )
            else:
                bar_type = 0
                prefetchable = False
                base_address = bar_value & 0xFFFFFFFC
                # I/O BARs are typically smaller
                size = 256  # Default I/O size

            log_warning_safe(
                self.logger,
                "Fallback BAR {index}: Estimated from raw value - type={type}, address=0x{address:08X}, size={size}, prefetchable={prefetchable}",
                index=index,
                type="memory" if is_memory else "io",
                address=base_address,
                size=size,
                prefetchable=prefetchable,
                prefix="BARA",
            )

            return BarConfiguration(
                index=index,
                base_address=base_address,
                size=size,
                bar_type=bar_type,
                prefetchable=prefetchable,
                is_memory=is_memory,
                is_io=is_io,
            )

    def _estimate_bar_size_from_device_context(
        self, bar_index: int, bar_data: dict
    ) -> int:
        """
        Estimate BAR size based on device class, BAR properties, and common patterns.

        Args:
            bar_index: BAR index (0-5)
            bar_data: BAR data dictionary

        Returns:
            Estimated BAR size in bytes
        """
        # Default sizes based on common device patterns
        base_size = 4096  # 4KB minimum

        # Check if we have device class information for better estimation
        if hasattr(self, "config") and hasattr(self.config, "device_class"):
            device_class = getattr(self.config, "device_class", "")

            # Network controllers typically have larger register spaces
            if "network" in device_class.lower() or "ethernet" in device_class.lower():
                base_size = 64 * 1024  # 64KB
            # Audio controllers typically have moderate register spaces
            elif (
                "audio" in device_class.lower() or "multimedia" in device_class.lower()
            ):
                base_size = 16 * 1024  # 16KB
            # Graphics cards typically have very large BARs
            elif "display" in device_class.lower() or "vga" in device_class.lower():
                if bar_data.get("prefetchable", False):
                    base_size = 256 * 1024 * 1024  # 256MB for framebuffer
                else:
                    base_size = 16 * 1024  # 16KB for registers
            # Storage controllers typically have moderate register spaces
            elif "storage" in device_class.lower() or "sata" in device_class.lower():
                base_size = 8 * 1024  # 8KB

        # Adjust based on BAR index (BAR0 is typically the main register space)
        if bar_index == 0:
            # BAR0 is usually the primary register space
            pass  # Use base_size as-is
        elif bar_index == 1 and bar_data.get("prefetchable", False):
            # BAR1 prefetchable might be a larger memory space
            base_size = max(base_size, 64 * 1024)
        else:
            # Other BARs are typically smaller
            base_size = min(base_size, 16 * 1024)

        log_info_safe(
            self.logger,
            "Estimated BAR {index} size: {size} bytes ({kb}KB) based on device context",
            index=bar_index,
            size=base_size,
            kb=base_size // 1024,
            prefix="BARA",
        )

        return base_size

    def _adjust_bar_config_for_behavior(
        self, bar_config: Dict[str, Any], behavior_profile: BehaviorProfile
    ) -> Dict[str, Any]:
        """
        Adjust BAR configuration based on behavior profile.

        Args:
            bar_config: Current BAR configuration
            behavior_profile: Device behavior profile

        Returns:
            Behavior-based adjustments
        """
        log_info_safe(
            self.logger,
            "Adjusting BAR configuration for device {bdf} based on behavior profile",
            bdf=self.device_bdf,
            prefix="BARA",
        )
        adjustments = {}

        # Adjust based on access frequency
        if behavior_profile.total_accesses > 1000:
            adjustments["high_frequency_device"] = True
            adjustments["burst_optimization"] = True
            adjustments["access_frequency_class"] = "high"
        elif behavior_profile.total_accesses > 100:
            adjustments["access_frequency_class"] = "medium"
        else:
            adjustments["access_frequency_class"] = "low"

        # Adjust based on timing patterns
        pattern_count = len(behavior_profile.timing_patterns)
        if pattern_count > 10:
            adjustments["timing_complexity"] = "high"
            adjustments["timing_sensitive"] = True
        elif pattern_count > 5:
            adjustments["timing_complexity"] = "medium"
        else:
            adjustments["timing_complexity"] = "low"

        # Add unique behavior signature
        adjustments["behavior_signature"] = self._generate_behavior_signature(
            behavior_profile
        )

        return adjustments

    def _generate_behavior_signature(self, behavior_profile: BehaviorProfile) -> str:
        """
        Generate unique signature from behavior profile.

        Args:
            behavior_profile: Device behavior profile

        Returns:
            Unique behavior signature
        """
        signature_data = f"{behavior_profile.total_accesses}_{behavior_profile.capture_duration}_{len(behavior_profile.timing_patterns)}_{len(behavior_profile.state_transitions)}"
        return hashlib.sha256(signature_data.encode()).hexdigest()[:16]

    def _build_timing_config(
        self,
        behavior_profile: Optional[BehaviorProfile],
        device_identifiers: DeviceIdentifiers,
    ) -> TimingParameters:
        """
        Build timing configuration from behavior profile or device characteristics.

        Args:
            behavior_profile: Device behavior profile
            device_identifiers: Device identifiers

        Returns:
            Validated timing parameters

        Raises:
            ContextError: If timing cannot be determined
        """
        if behavior_profile and behavior_profile.timing_patterns:
            # Extract timing from behavior profile
            return self._extract_timing_from_behavior(behavior_profile)
        else:
            # Generate timing based on device characteristics
            return self._generate_timing_from_device(device_identifiers)

    def _extract_timing_from_behavior(
        self, behavior_profile: BehaviorProfile
    ) -> TimingParameters:
        """
        Extract timing parameters from behavior profile.

        Args:
            behavior_profile: Device behavior profile

        Returns:
            Timing parameters extracted from behavior
        """
        patterns = behavior_profile.timing_patterns

        # Calculate timing characteristics from patterns
        avg_interval = sum(p.avg_interval_us for p in patterns) / len(patterns)
        avg_frequency = sum(p.frequency_hz for p in patterns) / len(patterns)

        # Derive timing parameters from observed behavior
        if avg_interval < 10:  # Very fast device
            log_info_safe(
                self.logger,
                "Detected very fast device {bdf} with avg_interval: {avg_interval}",
                bdf=self.device_bdf,
                avg_interval=avg_interval,
                prefix="BARA",
            )
            return TimingParameters(
                read_latency=2,
                write_latency=1,
                burst_length=32,
                inter_burst_gap=4,
                timeout_cycles=512,
                clock_frequency_mhz=min(200.0, avg_frequency / 1000),
                timing_regularity=0.92,
            )
        elif avg_interval > 1000:  # Slow device
            log_info_safe(
                self.logger,
                "Detected slow device {bdf} with avg_interval: {avg_interval}",
                bdf=self.device_bdf,
                avg_interval=avg_interval,
                prefix="BARA",
            )
            return TimingParameters(
                read_latency=8,
                write_latency=4,
                burst_length=8,
                inter_burst_gap=16,
                timeout_cycles=2048,
                clock_frequency_mhz=max(50.0, avg_frequency / 1000),
                timing_regularity=0.85,
            )
        else:  # Medium speed device
            log_info_safe(
                self.logger,
                "Detected medium speed device {bdf} with avg_interval: {avg_interval}",
                bdf=self.device_bdf,
                avg_interval=avg_interval,
                prefix="BARA",
            )
            return TimingParameters(
                read_latency=4,
                write_latency=2,
                burst_length=16,
                inter_burst_gap=8,
                timeout_cycles=1024,
                clock_frequency_mhz=100.0,
                timing_regularity=0.90,
            )

    def _generate_timing_from_device(
        self, device_identifiers: DeviceIdentifiers
    ) -> TimingParameters:
        """
        Generate timing parameters based on device characteristics.

        Args:
            device_identifiers: Device identifiers

        Returns:
            Device-specific timing parameters
        """
        # Use device class to determine timing characteristics
        class_code = device_identifiers.class_code
        log_info_safe(
            self.logger,
            "Generating timing parameters for device {bdf} with class code {class_code}",
            bdf=self.device_bdf,
            class_code=class_code,
            prefix="BARA",
        )
        # Network controllers (class 02xxxx)
        if class_code.startswith("02"):
            log_info_safe(
                self.logger,
                "Detected network controller for device {bdf}",
                bdf=self.device_bdf,
                prefix="BARA",
            )
            return TimingParameters(
                read_latency=2,
                write_latency=1,
                burst_length=32,
                inter_burst_gap=4,
                timeout_cycles=512,
                clock_frequency_mhz=125.0,
                timing_regularity=0.92,
            )
        # Storage controllers (class 01xxxx)
        elif class_code.startswith("01"):
            log_info_safe(
                self.logger,
                "Detected storage controller for device {bdf}",
                bdf=self.device_bdf,
                prefix="BARA",
            )
            return TimingParameters(
                read_latency=6,
                write_latency=3,
                burst_length=64,
                inter_burst_gap=8,
                timeout_cycles=1024,
                clock_frequency_mhz=100.0,
                timing_regularity=0.92,
            )
        # Display controllers (class 03xxxx)
        elif class_code.startswith("03"):
            log_info_safe(
                self.logger,
                "Detected display controller for device {bdf}",
                bdf=self.device_bdf,
                prefix="BARA",
            )
            return TimingParameters(
                read_latency=4,
                write_latency=2,
                burst_length=16,
                inter_burst_gap=8,
                timeout_cycles=2048,
                clock_frequency_mhz=150.0,
                timing_regularity=0.92,
            )
        else:
            log_info_safe(
                self.logger,
                "Falling back to generic timing parameters for device {bdf}",
                bdf=self.device_bdf,
                prefix="BARA",
            )
            # Use device ID hash to create deterministic but unique timing
            device_hash = int(
                hashlib.sha256(
                    f"{device_identifiers.vendor_id}{device_identifiers.device_id}".encode()
                ).hexdigest()[:8],
                16,
            )

            return TimingParameters(
                read_latency=2 + (device_hash % 6),
                write_latency=1 + (device_hash % 4),
                burst_length=8 + (device_hash % 56),  # 8-64
                inter_burst_gap=4 + (device_hash % 12),  # 4-16
                timeout_cycles=512 + (device_hash % 1536),  # 512-2048
                clock_frequency_mhz=75.0 + (device_hash % 125),  # 75-200 MHz
                timing_regularity=0.85 + (device_hash % 15) / 100.0,
            )

    def _build_pcileech_config(
        self, device_identifiers: DeviceIdentifiers
    ) -> Dict[str, Any]:
        """
        Build PCILeech-specific configuration context.

        Args:
            device_identifiers: Device identifiers for customization

        Returns:
            PCILeech configuration context
        """
        log_info_safe(
            self.logger,
            "Building PCILeech configuration for device {bdf}",
            bdf=self.device_bdf,
            prefix="CONF",
        )
        # Create device-specific memory layout
        device_hash = int(
            hashlib.sha256(
                f"{device_identifiers.vendor_id}{device_identifiers.device_id}".encode()
            ).hexdigest()[:8],
            16,
        )

        # Generate unique but deterministic memory layout
        base_offset = (device_hash % 0x1000) & 0xFFF0  # Align to 16-byte boundary
        log_info_safe(
            self.logger,
            "Using base offset 0x{offset:04X} for device {bdf}",
            offset=base_offset,
            bdf=self.device_bdf,
            prefix="CONF",
        )

        # Get payload size configuration from device config if available
        max_payload_size = 256  # Default
        cfg_force_mps = 1  # Default encoding for 256 bytes

        # Try to get from device configuration
        if hasattr(self.config, "device_config") and hasattr(
            self.config.device_config, "capabilities"
        ):
            try:
                from .device_config import DeviceCapabilities

                capabilities = self.config.device_config.capabilities
                if isinstance(capabilities, DeviceCapabilities):
                    max_payload_size = capabilities.max_payload_size
                    cfg_force_mps = capabilities.get_cfg_force_mps()

                    # Check for tiny PCIe algo issues
                    has_issues, warning = capabilities.check_tiny_pcie_issues()
                    if has_issues:
                        log_warning_safe(
                            self.logger,
                            "Payload size warning for device {bdf}: {warning}",
                            bdf=self.device_bdf,
                            warning=warning,
                            prefix="CONF",
                        )
            except Exception as e:
                log_warning_safe(
                    self.logger,
                    "Failed to get payload size config for device {bdf}: {error}",
                    bdf=self.device_bdf,
                    error=str(e),
                    prefix="CONF",
                )

        log_info_safe(
            self.logger,
            "Using max_payload_size={mps} bytes, cfg_force_mps={cfg_mps} for device {bdf}",
            mps=max_payload_size,
            cfg_mps=cfg_force_mps,
            bdf=self.device_bdf,
            prefix="CONF",
        )

        return {
            "command_timeout": getattr(self.config, "pcileech_command_timeout", 5000),
            "buffer_size": getattr(self.config, "pcileech_buffer_size", 4096),
            "enable_dma": getattr(self.config, "enable_dma_operations", False),
            "enable_scatter_gather": True,
            "max_payload_size": max_payload_size,
            "cfg_force_mps": cfg_force_mps,
            "max_read_request_size": 512,
            "device_ctrl_base": f"32'h{base_offset:08X}",
            "device_ctrl_size": "32'h00000100",
            "status_reg_base": f"32'h{(base_offset + 0x100):08X}",
            "status_reg_size": "32'h00000100",
            "data_buffer_base": f"32'h{(base_offset + 0x200):08X}",
            "data_buffer_size": "32'h00000200",
            "custom_region_base": f"32'h{(base_offset + 0x400):08X}",
            "custom_region_size": "32'h00000C00",
            "supported_commands": [
                "PCILEECH_CMD_READ",
                "PCILEECH_CMD_WRITE",
                "PCILEECH_CMD_PROBE",
                "PCILEECH_CMD_WRITE_SCATTER",
                "PCILEECH_CMD_READ_SCATTER",
                "PCILEECH_CMD_EXEC",
                "PCILEECH_CMD_STATUS",
            ],
        }

    def _build_active_device_config(
        self,
        device_identifiers: DeviceIdentifiers,
        interrupt_strategy: str,
        interrupt_vectors: int,
    ) -> Dict[str, Any]:
        """
        Build active device interrupt configuration.

        Args:
            device_identifiers: Device identifiers
            interrupt_strategy: Interrupt strategy ("msix", "msi", or "intx")
            interrupt_vectors: Number of interrupt vectors

        Returns:
            Active device configuration for templates
        """
        log_info_safe(
            self.logger,
            "Building active device configuration for {bdf} with {strategy} interrupts",
            bdf=self.device_bdf,
            strategy=interrupt_strategy,
            prefix="ACTDEV",
        )

        # Get active device config from device capabilities if available
        active_config = None
        if hasattr(self.config, "device_config") and hasattr(
            self.config.device_config, "capabilities"
        ):
            try:
                from .device_config import DeviceCapabilities

                capabilities = self.config.device_config.capabilities
                if isinstance(capabilities, DeviceCapabilities):
                    active_config = capabilities.active_device
                    log_info_safe(
                        self.logger,
                        "Using active device config from device capabilities",
                        prefix="ACTDEV",
                    )
            except Exception as e:
                log_warning_safe(
                    self.logger,
                    "Failed to get active device config: {error}",
                    error=str(e),
                    prefix="ACTDEV",
                )

        # Build configuration with defaults if not available
        if active_config:
            # Use configuration from device config
            config = {
                "enabled": active_config.enabled,
                "timer_period": active_config.timer_period,
                "timer_enable": active_config.timer_enable,
                "interrupt_mode": active_config.interrupt_mode,
                "interrupt_vector": active_config.interrupt_vector,
                "priority": active_config.priority,
                "msi_vector_width": active_config.msi_vector_width,
                "msi_64bit_addr": 1 if active_config.msi_64bit_addr else 0,
                "num_sources": active_config.num_interrupt_sources,
                "default_priority": active_config.default_source_priority,
            }
        else:
            # Use defaults
            config = {
                "enabled": False,
                "timer_period": 100000,
                "timer_enable": 1,
                "interrupt_mode": interrupt_strategy,
                "interrupt_vector": 0,
                "priority": 15,
                "msi_vector_width": 5,
                "msi_64bit_addr": 0,
                "num_sources": 8,
                "default_priority": 8,
            }

        # Add template-specific values
        config.update(
            {
                # MSI-X specific parameters
                "num_msix": interrupt_vectors if interrupt_strategy == "msix" else 0,
                "msix_table_bir": 0,  # Will be updated from msix_data if available
                "msix_table_offset": 0,
                "msix_pba_bir": 0,
                "msix_pba_offset": 0,
                # Device identification for interrupt generation
                "device_id": f"16'h{int(device_identifiers.device_id, 16):04X}",
                "vendor_id": f"16'h{int(device_identifiers.vendor_id, 16):04X}",
                "completer_id": f"16'h0000",  # Bus/Dev/Func - will be set by PCIe core
            }
        )

        log_info_safe(
            self.logger,
            "Active device config: enabled={enabled}, mode={mode}, timer={timer}",
            enabled=config["enabled"],
            mode=config["interrupt_mode"],
            timer=config["timer_period"],
            prefix="ACTDEV",
        )

        return config

    def _build_overlay_config(
        self, config_space_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build overlay RAM configuration for configuration space shadow.

        This method automatically detects which registers need overlay entries
        based on PCIe specifications and generates the OVERLAY_MAP.

        Args:
            config_space_data: Configuration space analysis data

        Returns:
            Dictionary with OVERLAY_MAP and OVERLAY_ENTRIES
        """
        log_info_safe(
            self.logger,
            "Building overlay RAM configuration for device {bdf}",
            bdf=self.device_bdf,
            prefix="OVERLAY",
        )

        try:
            # Initialize overlay mapper
            overlay_mapper = OverlayMapper()

            # Get configuration space dword map and capabilities
            dword_map = config_space_data.get("dword_map", {})
            capabilities = config_space_data.get("capabilities", {})

            if not dword_map:
                log_warning_safe(
                    self.logger,
                    "No configuration space dword map available for overlay generation",
                    prefix="OVERLAY",
                )
                # Return empty overlay map
                return {
                    "OVERLAY_MAP": [],
                    "OVERLAY_ENTRIES": 0,
                }

            # Generate overlay mapping
            overlay_config = overlay_mapper.generate_overlay_map(
                dword_map, capabilities
            )

            log_info_safe(
                self.logger,
                "Generated overlay mapping with {entries} entries for device {bdf}",
                entries=overlay_config["OVERLAY_ENTRIES"],
                bdf=self.device_bdf,
                prefix="OVERLAY",
            )

            # Log details of overlay entries for debugging
            if self.logger.isEnabledFor(logging.DEBUG):
                for reg_num, mask in overlay_config["OVERLAY_MAP"]:
                    self.logger.debug(
                        f"[OVERLAY] Overlay entry: Register 0x{reg_num * 4:03X} with mask 0x{mask:08X}"
                    )

            return overlay_config

        except Exception as e:
            log_error_safe(
                self.logger,
                "Failed to generate overlay configuration: {error}",
                error=str(e),
                prefix="OVERLAY",
            )
            # Return empty overlay map on error
            return {
                "OVERLAY_MAP": [],
                "OVERLAY_ENTRIES": 0,
            }

    def _generate_unique_device_signature(
        self,
        device_identifiers: DeviceIdentifiers,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: ConfigSpaceData,
    ) -> str:
        """
        Generate a unique device signature for firmware uniqueness.

        Args:
            device_identifiers: Device identifiers
            behavior_profile: Device behavior profile
            config_space_data: Configuration space data

        Returns:
            Unique device signature in Verilog format
        """
        # Create cache key
        cache_key = (
            device_identifiers.full_signature,
            self.device_bdf,
            self._create_config_space_key(config_space_data),
            self._create_behavior_key(behavior_profile) if behavior_profile else None,
        )

        # Check if we've already computed this signature
        if hasattr(self, "_signature_cache"):
            if cache_key in self._signature_cache:
                return self._signature_cache[cache_key]
        else:
            self._signature_cache = {}

        # Build signature components
        hasher = hashlib.sha256()

        # Add device identifiers
        hasher.update(device_identifiers.full_signature.encode())
        hasher.update(self.device_bdf.encode())

        # Add config space characteristics
        hasher.update(self._create_config_space_key(config_space_data).encode())

        # Add behavior profile if available
        if behavior_profile:
            behavior_data = (
                f"{behavior_profile.total_accesses}"
                f"{behavior_profile.capture_duration}"
                f"{len(behavior_profile.timing_patterns)}"
                f"{len(behavior_profile.state_transitions)}"
            )
            hasher.update(behavior_data.encode())

        # Generate final hash
        signature_hash = hasher.hexdigest()

        log_info_safe(
            self.logger,
            "Generated device signature: {hash}",
            hash=signature_hash[:8],
            prefix="SIG",
        )

        result = f"32'h{int(signature_hash[:8], 16):08X}"

        # Cache the result
        self._signature_cache[cache_key] = result

        return result

    def _create_behavior_key(self, behavior_profile: BehaviorProfile) -> str:
        """Create a hashable key from behavior profile."""
        return (
            f"{behavior_profile.total_accesses}_"
            f"{behavior_profile.capture_duration}_"
            f"{len(behavior_profile.timing_patterns)}_"
            f"{len(behavior_profile.state_transitions)}"
        )

    def _create_config_space_key(self, config_space_data: ConfigSpaceData) -> str:
        """Create a hashable key from config space data."""
        # Extract key components
        config_size = config_space_data.get("config_space_size", 0)
        bar_count = len(config_space_data.get("bars", []))

        # Hash the config space hex data
        config_hex = config_space_data.get("config_space_hex", "")
        if config_hex:
            # Normalize to 4KB for consistent hashing
            normalized_hex = config_hex[:8192].ljust(8192, "0")
            config_hash = hashlib.md5(normalized_hex.encode()).hexdigest()
        else:
            config_hash = "empty"

        return f"{config_size}_{bar_count}_{config_hash}"

    def _build_generation_metadata(
        self, device_identifiers: DeviceIdentifiers
    ) -> Dict[str, Any]:
        """
        Build generation metadata with enhanced information.

        Args:
            device_identifiers: Device identifiers

        Returns:
            Generation metadata
        """
        return {
            "generated_at": datetime.now().isoformat(),
            "device_bdf": self.device_bdf,
            "device_signature": device_identifiers.device_signature,
            "device_class": device_identifiers.get_device_class_type(),
            "generator_version": "2.0.0",
            "context_builder_version": "2.0.0",
            "validation_level": self.validation_level.value,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
        }

    def _merge_donor_template(
        self, context: Dict[str, Any], donor_template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge donor template values with discovered context values.

        Template values override discovered values when there's a conflict.
        Null values in the template are ignored.

        Args:
            context: The discovered context
            donor_template: The donor template to merge

        Returns:
            Merged context dictionary
        """
        log_info_safe(
            self.logger,
            "Merging donor template with discovered values",
            prefix="PCIL",
        )

        # Import the merge function from donor_info_template
        from .donor_info_template import DonorInfoTemplateGenerator

        # Create a temporary generator instance to use its merge method
        generator = DonorInfoTemplateGenerator()

        # Use the existing merge_template_with_discovered method
        merged_context = generator.merge_template_with_discovered(
            template=donor_template, discovered=context
        )

        log_info_safe(
            self.logger,
            "Successfully merged donor template with discovered values",
            prefix="PCIL",
        )

        return merged_context

    def _validate_context_completeness(self, context: TemplateContext) -> None:
        """
        Validate template context for completeness with structured validation.

        Args:
            context: Template context to validate

        Raises:
            ContextError: If validation fails in strict mode
        """
        validation_errors = []
        validation_warnings = []

        # Define validation rules
        validations = [
            self._validate_required_sections,
            self._validate_device_config,
            self._validate_bar_config,
            self._validate_device_signature,
            self._validate_timing_config,
            self._validate_interrupt_config,
        ]

        # Run all validations
        for validator in validations:
            errors, warnings = validator(context)
            validation_errors.extend(errors)
            validation_warnings.extend(warnings)

        # Log warnings
        for warning in validation_warnings:
            log_warning_safe(self.logger, warning, prefix="VLDN")

        # Handle errors based on validation level
        if validation_errors:
            if self.validation_level == ValidationLevel.STRICT:
                raise ContextError(
                    f"Context validation failed with {len(validation_errors)} errors: "
                    + "; ".join(validation_errors)
                )
            else:
                for error in validation_errors:
                    log_warning_safe(
                        self.logger,
                        f"Validation error (non-strict mode): {error}",
                        prefix="VLDN",
                    )

        if not validation_errors and not validation_warnings:
            log_info_safe(
                self.logger,
                "Template context validation completed successfully",
                prefix="VLDN",
            )

    def _validate_required_sections(
        self, context: TemplateContext
    ) -> Tuple[List[str], List[str]]:
        """Validate required sections are present."""
        errors = []
        warnings = []

        required_sections = [
            "device_config",
            "config_space",
            "msix_config",
            "bar_config",
            "timing_config",
            "pcileech_config",
            "device_signature",
            "generation_metadata",
        ]

        missing_sections = [
            section for section in required_sections if section not in context
        ]

        if missing_sections:
            errors.append(f"Missing required sections: {missing_sections}")

        return errors, warnings

    def _validate_device_config(
        self, context: TemplateContext
    ) -> Tuple[List[str], List[str]]:
        """Validate device configuration."""
        errors = []
        warnings = []

        device_config = context.get("device_config", {})

        if (
            not device_config.get("vendor_id")
            or device_config.get("vendor_id") == "0000"
        ):
            errors.append("Device vendor ID is missing or invalid")

        if (
            not device_config.get("device_id")
            or device_config.get("device_id") == "0000"
        ):
            errors.append("Device ID is missing or invalid")

        return errors, warnings

    def _validate_bar_config(
        self, context: TemplateContext
    ) -> Tuple[List[str], List[str]]:
        """Validate BAR configuration."""
        errors = []
        warnings = []

        bar_config = context.get("bar_config", {})
        bars = bar_config.get("bars")

        if bars is None:
            errors.append("BARs section is missing in context")
        elif isinstance(bars, list) and len(bars) == 0:
            warnings.append("BARs list is empty - device may not have any BARs")

        return errors, warnings

    def _validate_device_signature(
        self, context: TemplateContext
    ) -> Tuple[List[str], List[str]]:
        """Validate device signature."""
        errors = []
        warnings = []

        device_signature = context.get("device_signature")

        if not device_signature:
            errors.append("Device signature is missing")
        elif device_signature == "32'hDEADBEEF":
            errors.append("Device signature is using default/invalid value")

        return errors, warnings

    def _validate_timing_config(
        self, context: TemplateContext
    ) -> Tuple[List[str], List[str]]:
        """Validate timing configuration."""
        errors = []
        warnings = []

        timing_config = context.get("timing_config", {})

        if isinstance(timing_config, dict):
            # Validate timing parameters are reasonable
            clock_freq = timing_config.get("clock_frequency_mhz", 0)
            if clock_freq <= 0:
                errors.append("Invalid clock frequency")
            elif clock_freq > 1000:
                warnings.append(f"Unusually high clock frequency: {clock_freq} MHz")

        return errors, warnings

    def _validate_interrupt_config(
        self, context: TemplateContext
    ) -> Tuple[List[str], List[str]]:
        """Validate interrupt configuration."""
        errors = []
        warnings = []

        interrupt_config = context.get("interrupt_config", {})
        strategy = interrupt_config.get("strategy")

        if strategy not in ["intx", "msi", "msix"]:
            errors.append(f"Invalid interrupt strategy: {strategy}")

        if strategy == "msix" and not interrupt_config.get("msix_available"):
            warnings.append("MSI-X strategy selected but MSI-X not available")

        return errors, warnings
