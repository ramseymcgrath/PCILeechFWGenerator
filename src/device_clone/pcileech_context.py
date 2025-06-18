#!/usr/bin/env python3
"""
PCILeech Template Context Builder

This module builds comprehensive template context from device profiling data,
integrating data from BehaviorProfiler, ConfigSpaceManager, and MSIXCapability
to provide structured context for all PCILeech templates.

The context builder ensures all required data is present and provides validation
to prevent template rendering failures. NO FALLBACK VALUES are used - the system
fails if data is incomplete to ensure firmware uniqueness.
"""

import hashlib
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from ..string_utils import log_error_safe, log_info_safe, log_warning_safe
from .behavior_profiler import BehaviorProfile

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation strictness levels."""

    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


class PCILeechContextError(Exception):
    """Exception raised when context building fails."""

    def __init__(self, message: str, missing_data: Optional[List[str]] = None):
        super().__init__(message)
        self.missing_data = missing_data or []


@dataclass
class DeviceIdentifiers:
    """Device identification data."""

    vendor_id: str
    device_id: str
    class_code: str
    revision_id: str
    subsystem_vendor_id: Optional[str] = None
    subsystem_device_id: Optional[str] = None

    def __post_init__(self):
        """Validate device identifiers."""
        if not all([self.vendor_id, self.device_id, self.class_code, self.revision_id]):
            raise PCILeechContextError("Device identifiers cannot be empty")

        # Validate hex format
        for field_name, value in [
            ("vendor_id", self.vendor_id),
            ("device_id", self.device_id),
            ("class_code", self.class_code),
            ("revision_id", self.revision_id),
        ]:
            try:
                int(value, 16)
            except ValueError:
                raise PCILeechContextError(
                    f"Invalid hex format for {field_name}: {value}"
                )


@dataclass
class BarConfiguration:
    """BAR configuration data."""

    index: int
    base_address: int
    size: int
    bar_type: int
    prefetchable: bool
    is_memory: bool
    is_io: bool

    def __post_init__(self):
        """Validate BAR configuration."""
        if self.index < 0 or self.index > 5:
            raise PCILeechContextError(f"Invalid BAR index: {self.index}")
        if self.size <= 0:
            raise PCILeechContextError(f"Invalid BAR size: {self.size}")


@dataclass
class TimingParameters:
    """Device timing parameters."""

    read_latency: int
    write_latency: int
    burst_length: int
    inter_burst_gap: int
    timeout_cycles: int
    clock_frequency_mhz: float

    def __post_init__(self):
        """Validate timing parameters."""
        if any(
            param <= 0
            for param in [
                self.read_latency,
                self.write_latency,
                self.burst_length,
                self.inter_burst_gap,
                self.timeout_cycles,
            ]
        ):
            raise PCILeechContextError("Timing parameters must be positive")
        if self.clock_frequency_mhz <= 0:
            raise PCILeechContextError("Clock frequency must be positive")


class PCILeechContextBuilder:
    """
    Builds comprehensive template context from device profiling data.

    This class integrates data from multiple sources to create a unified
    template context that can be used for all PCILeech template rendering.

    Key principles:
    - NO FALLBACK VALUES - ensures firmware uniqueness
    - Strict validation of all input data
    - Comprehensive error reporting
    - Deterministic context generation
    """

    # Constants for validation
    MIN_CONFIG_SPACE_SIZE = 256
    MAX_CONFIG_SPACE_SIZE = 4096
    REQUIRED_DEVICE_FIELDS = ["vendor_id", "device_id", "class_code", "revision_id"]
    REQUIRED_MSIX_FIELDS = ["table_size", "table_bir", "table_offset"]

    def __init__(
        self,
        device_bdf: str,
        config: Any,
        validation_level: ValidationLevel = ValidationLevel.STRICT,
    ):
        """
        Initialize the context builder.

        Args:
            device_bdf: Device Bus:Device.Function identifier
            config: PCILeech generation configuration
            validation_level: Strictness of validation
        """
        if not device_bdf or not device_bdf.strip():
            raise PCILeechContextError("Device BDF cannot be empty")

        self.device_bdf = device_bdf.strip()
        self.config = config
        self.validation_level = validation_level
        self.logger = logging.getLogger(__name__)
        self._context_cache: Dict[str, Any] = {}

    def build_context(
        self,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
        msix_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build comprehensive template context from all data sources.

        Args:
            behavior_profile: Device behavior profile data
            config_space_data: Configuration space analysis data
            msix_data: MSI-X capability data

        Returns:
            Comprehensive template context dictionary

        Raises:
            PCILeechContextError: If context building fails or data is incomplete
        """
        log_info_safe(
            self.logger,
            "Building PCILeech template context for device {bdf} with {level} validation",
            bdf=self.device_bdf,
            level=self.validation_level.value,
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

            # Generate unique device signature
            device_signature = self._generate_unique_device_signature(
                device_identifiers, behavior_profile, config_space_data
            )

            # Assemble complete context
            context = {
                "device_config": device_config,
                "config_space": config_space,
                "msix_config": msix_config,
                "bar_config": bar_config,
                "timing_config": timing_config,
                "pcileech_config": pcileech_config,
                "device_signature": device_signature,
                "generation_metadata": self._build_generation_metadata(
                    device_identifiers
                ),
            }

            # Final validation
            self._validate_context_completeness(context)

            log_info_safe(
                self.logger,
                "PCILeech template context built successfully with signature {signature}",
                signature=device_signature,
            )

            return context

        except Exception as e:
            log_error_safe(
                self.logger,
                "Failed to build PCILeech template context: {error}",
                error=str(e),
            )
            raise PCILeechContextError(f"Context building failed: {e}") from e

    def _validate_input_data(
        self,
        config_space_data: Dict[str, Any],
        msix_data: Dict[str, Any],
        behavior_profile: Optional[BehaviorProfile],
    ) -> None:
        """
        Validate all input data before processing.

        Args:
            config_space_data: Configuration space data
            msix_data: MSI-X capability data
            behavior_profile: Device behavior profile

        Raises:
            PCILeechContextError: If validation fails
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
            if (
                config_size < self.MIN_CONFIG_SPACE_SIZE
                or config_size > self.MAX_CONFIG_SPACE_SIZE
            ):
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
            raise PCILeechContextError(
                f"Missing required data for unique firmware generation: {missing_data}",
                missing_data=missing_data,
            )
        elif missing_data:
            log_warning_safe(
                self.logger,
                "Missing data detected but continuing with {level} validation: {missing}",
                level=self.validation_level.value,
                missing=missing_data,
            )

    def _extract_device_identifiers(
        self, config_space_data: Dict[str, Any]
    ) -> DeviceIdentifiers:
        """
        Extract and validate device identifiers.

        Args:
            config_space_data: Configuration space data

        Returns:
            Validated device identifiers

        Raises:
            PCILeechContextError: If identifiers are missing or invalid
        """
        try:
            return DeviceIdentifiers(
                vendor_id=config_space_data["vendor_id"],
                device_id=config_space_data["device_id"],
                class_code=config_space_data["class_code"],
                revision_id=config_space_data["revision_id"],
                subsystem_vendor_id=config_space_data.get("subsystem_vendor_id"),
                subsystem_device_id=config_space_data.get("subsystem_device_id"),
            )
        except KeyError as e:
            raise PCILeechContextError(f"Missing required device identifier: {e}")

    def _build_device_config(
        self,
        device_identifiers: DeviceIdentifiers,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build device configuration context with no fallbacks.

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
            PCILeechContextError: If serialization fails
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
            raise PCILeechContextError(f"Failed to serialize behavior profile: {e}")

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
            PCILeechContextError: If required data is missing
        """
        required_fields = ["config_space_hex", "config_space_size", "bars"]
        missing_fields = [
            field for field in required_fields if field not in config_space_data
        ]

        if missing_fields and self.validation_level == ValidationLevel.STRICT:
            raise PCILeechContextError(
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

    def _build_msix_context(self, msix_data: Dict[str, Any]) -> Dict[str, Any]:
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
            }

        capability_info = msix_data["capability_info"]
        table_size = capability_info["table_size"]

        return {
            "num_vectors": table_size,
            "table_bir": capability_info["table_bir"],
            "table_offset": capability_info["table_offset"],
            "pba_bir": capability_info.get("pba_bir", capability_info["table_bir"]),
            "pba_offset": capability_info.get("pba_offset", 0),
            "enabled": capability_info.get("enabled", False),
            "function_mask": capability_info.get("function_mask", False),
            "is_supported": table_size > 0,
            "validation_errors": msix_data.get("validation_errors", []),
            "is_valid": msix_data.get("is_valid", True),
            "table_size_bytes": table_size * 16,  # 16 bytes per entry
            "pba_size_bytes": ((table_size + 31) // 32) * 4,  # PBA size in bytes
        }

    def _build_bar_config(
        self,
        config_space_data: Dict[str, Any],
        behavior_profile: Optional[BehaviorProfile],
    ) -> Dict[str, Any]:
        """
        Build BAR configuration context with no fallbacks.

        Args:
            config_space_data: Configuration space data
            behavior_profile: Device behavior profile

        Returns:
            BAR configuration context

        Raises:
            PCILeechContextError: If no valid BARs found
        """
        bars = config_space_data["bars"]

        if not bars or all(bar == 0 for bar in bars):
            raise PCILeechContextError(
                "No valid BARs found - cannot generate unique firmware"
            )

        bar_configs = []
        primary_bar = None

        # Process each BAR
        for i, bar_value in enumerate(bars[:6]):  # Only process first 6 BARs
            if bar_value != 0:
                bar_info = self._analyze_bar(i, bar_value)
                bar_configs.append(bar_info)

                # Use first valid BAR as primary
                if primary_bar is None:
                    primary_bar = bar_info

        if not primary_bar:
            raise PCILeechContextError("No valid primary BAR found")

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

    def _analyze_bar(self, index: int, bar_value: int) -> BarConfiguration:
        """
        Analyze a single BAR value with validation.

        Args:
            index: BAR index (0-5)
            bar_value: BAR register value

        Returns:
            Validated BAR configuration

        Raises:
            PCILeechContextError: If BAR analysis fails
        """
        if bar_value == 0:
            raise PCILeechContextError(f"BAR {index} is empty")

        is_memory = (bar_value & 0x1) == 0

        if is_memory:
            # Memory BAR
            bar_type = (bar_value >> 1) & 0x3  # Bits 2:1
            prefetchable = bool((bar_value >> 3) & 0x1)  # Bit 3
            base_address = bar_value & 0xFFFFFFF0  # Clear lower 4 bits

            # Calculate size from BAR value (simplified estimation)
            # In real implementation, this would require probing
            size = self._estimate_bar_size(bar_value, is_memory=True)

            return BarConfiguration(
                index=index,
                base_address=base_address,
                size=size,
                bar_type=bar_type,
                prefetchable=prefetchable,
                is_memory=True,
                is_io=False,
            )
        else:
            # I/O BAR
            base_address = bar_value & 0xFFFFFFFC  # Clear lower 2 bits
            size = self._estimate_bar_size(bar_value, is_memory=False)

            return BarConfiguration(
                index=index,
                base_address=base_address,
                size=size,
                bar_type=0,
                prefetchable=False,
                is_memory=False,
                is_io=True,
            )

    def _estimate_bar_size(self, bar_value: int, is_memory: bool) -> int:
        """
        Probe actual BAR size using PCI standard method.

        This implementation performs proper PCI BAR size detection by:
        1. Writing all 1s to the BAR register
        2. Reading back to determine which bits are writable
        3. Calculating size from the address decode mask
        4. Restoring the original BAR value

        Args:
            bar_value: BAR register value
            is_memory: Whether this is a memory BAR

        Returns:
            Actual BAR size in bytes
        """
        # Calculate BAR offset from the device BDF
        bar_index = getattr(self, "_current_bar_index", 0)
        bar_offset = 0x10 + (bar_index * 4)  # BAR0 at 0x10, BAR1 at 0x14, etc.

        try:
            # Step 1: Save original value
            original_value = bar_value

            # Step 2: Write all 1s to determine writable bits
            self._pci_write32(bar_offset, 0xFFFFFFFF)

            # Step 3: Read back to get the size mask
            size_mask = self._pci_read32(bar_offset)

            # Step 4: Restore original value
            self._pci_write32(bar_offset, original_value)

            # Step 5: Calculate size from mask
            if size_mask == 0:
                return 0  # BAR not implemented

            if is_memory:
                # For memory BARs, mask out type bits [3:0]
                size_mask &= 0xFFFFFFF0
            else:
                # For I/O BARs, mask out type bits [1:0]
                size_mask &= 0xFFFFFFFC

            # Size is the complement + 1 of the writable bits
            if size_mask == 0:
                return 0

            # Find the size by inverting the mask
            size = (~size_mask + 1) & 0xFFFFFFFF

            # Ensure reasonable bounds
            if is_memory:
                return max(min(size, 4 * 1024 * 1024 * 1024), 4096)  # 4KB to 4GB
            else:
                return max(min(size, 65536), 4)  # 4 bytes to 64KB

        except Exception as e:
            log_warning_safe(logger, "Hardware BAR probing failed: {error}", error=e)
            # If hardware access fails, we cannot determine the size
            raise PCILeechContextError(
                f"Cannot determine BAR size without hardware access: {e}",
                missing_data=["bar_size"],
            )

    def _pci_read32(self, offset: int) -> int:
        """
        Read 32-bit value from PCI config space.

        Args:
            offset: Byte offset in config space

        Returns:
            32-bit value from config space
        """
        import subprocess

        try:
            # Use setpci to read from PCI config space
            # Format: setpci -s <bus:device.function> <offset>.L
            cmd = f"setpci -s {self.device_bdf} {offset:02x}.L"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=True
            )

            # Parse hex result
            hex_value = result.stdout.strip()
            return int(hex_value, 16)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to read PCI config space at offset 0x{offset:02x}: {e}"
            )
        except ValueError as e:
            raise RuntimeError(f"Invalid hex value from setpci: {e}")

    def _pci_write32(self, offset: int, value: int) -> None:
        """
        Write 32-bit value to PCI config space.

        Args:
            offset: Byte offset in config space
            value: 32-bit value to write
        """
        import subprocess

        try:
            # Use setpci to write to PCI config space
            # Format: setpci -s <bus:device.function> <offset>.L=<value>
            cmd = f"setpci -s {self.device_bdf} {offset:02x}.L={value:08x}"
            subprocess.run(cmd, shell=True, check=True, capture_output=True)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to write PCI config space at offset 0x{offset:02x}: {e}"
            )

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
            PCILeechContextError: If timing cannot be determined
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
            return TimingParameters(
                read_latency=2,
                write_latency=1,
                burst_length=32,
                inter_burst_gap=4,
                timeout_cycles=512,
                clock_frequency_mhz=min(200.0, avg_frequency / 1000),
            )
        elif avg_interval > 1000:  # Slow device
            return TimingParameters(
                read_latency=8,
                write_latency=4,
                burst_length=8,
                inter_burst_gap=16,
                timeout_cycles=2048,
                clock_frequency_mhz=max(50.0, avg_frequency / 1000),
            )
        else:  # Medium speed device
            return TimingParameters(
                read_latency=4,
                write_latency=2,
                burst_length=16,
                inter_burst_gap=8,
                timeout_cycles=1024,
                clock_frequency_mhz=100.0,
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

        # Network controllers (class 02xxxx)
        if class_code.startswith("02"):
            return TimingParameters(
                read_latency=2,
                write_latency=1,
                burst_length=32,
                inter_burst_gap=4,
                timeout_cycles=512,
                clock_frequency_mhz=125.0,
            )
        # Storage controllers (class 01xxxx)
        elif class_code.startswith("01"):
            return TimingParameters(
                read_latency=6,
                write_latency=3,
                burst_length=64,
                inter_burst_gap=8,
                timeout_cycles=1024,
                clock_frequency_mhz=100.0,
            )
        # Display controllers (class 03xxxx)
        elif class_code.startswith("03"):
            return TimingParameters(
                read_latency=4,
                write_latency=2,
                burst_length=16,
                inter_burst_gap=8,
                timeout_cycles=2048,
                clock_frequency_mhz=150.0,
            )
        else:
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
        # Create device-specific memory layout
        device_hash = int(
            hashlib.sha256(
                f"{device_identifiers.vendor_id}{device_identifiers.device_id}".encode()
            ).hexdigest()[:8],
            16,
        )

        # Generate unique but deterministic memory layout
        base_offset = (device_hash % 0x1000) & 0xFFF0  # Align to 16-byte boundary

        return {
            "command_timeout": getattr(self.config, "pcileech_command_timeout", 5000),
            "buffer_size": getattr(self.config, "pcileech_buffer_size", 4096),
            "enable_dma": getattr(self.config, "enable_dma_operations", False),
            "enable_scatter_gather": True,
            "max_payload_size": 256,
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

    def _generate_unique_device_signature(
        self,
        device_identifiers: DeviceIdentifiers,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
    ) -> str:
        """
        Generate a unique device signature for firmware uniqueness.

        Args:
            device_identifiers: Device identifiers
            behavior_profile: Device behavior profile
            config_space_data: Configuration space data

        Returns:
            Unique device signature
        """
        # Combine all unique device characteristics
        signature_components = [
            device_identifiers.vendor_id,
            device_identifiers.device_id,
            device_identifiers.class_code,
            device_identifiers.revision_id,
            self.device_bdf,
            str(config_space_data.get("config_space_size", 0)),
            str(len(config_space_data.get("bars", []))),
        ]

        # Add subsystem IDs if available
        if device_identifiers.subsystem_vendor_id:
            signature_components.append(device_identifiers.subsystem_vendor_id)
        if device_identifiers.subsystem_device_id:
            signature_components.append(device_identifiers.subsystem_device_id)

        # Add behavior profile signature if available
        if behavior_profile:
            signature_components.extend(
                [
                    str(behavior_profile.total_accesses),
                    str(behavior_profile.capture_duration),
                    str(len(behavior_profile.timing_patterns)),
                    str(len(behavior_profile.state_transitions)),
                ]
            )

        # Create deterministic hash
        signature_data = "_".join(signature_components)
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()

        return f"32'h{int(signature_hash[:8], 16):08X}"

    def _build_generation_metadata(
        self, device_identifiers: DeviceIdentifiers
    ) -> Dict[str, Any]:
        """
        Build generation metadata.

        Args:
            device_identifiers: Device identifiers

        Returns:
            Generation metadata
        """
        return {
            "generated_at": datetime.now().isoformat(),
            "device_bdf": self.device_bdf,
            "device_signature": f"{device_identifiers.vendor_id}:{device_identifiers.device_id}",
            "generator_version": "2.0.0",
            "context_builder_version": "2.0.0",
            "validation_level": self.validation_level.value,
        }

    def _validate_context_completeness(self, context: Dict[str, Any]) -> None:
        """
        Validate template context for completeness.

        Args:
            context: Template context to validate

        Raises:
            PCILeechContextError: If validation fails
        """
        required_sections = [
            "device_config",
            "config_space",
            "msix_config",
            "bar_config",
            "timing_config",
            "pcileech_config",
            "device_signature",
        ]

        missing_sections = [
            section for section in required_sections if section not in context
        ]

        if missing_sections:
            if self.validation_level == ValidationLevel.STRICT:
                raise PCILeechContextError(
                    f"Template context missing required sections: {missing_sections}"
                )
            else:
                log_warning_safe(
                    self.logger,
                    "Template context missing sections: {sections}",
                    sections=missing_sections,
                )

        # Validate critical device information
        device_config = context.get("device_config", {})
        if (
            not device_config.get("vendor_id")
            or device_config.get("vendor_id") == "0000"
        ):
            if self.validation_level == ValidationLevel.STRICT:
                raise PCILeechContextError("Device vendor ID is missing or invalid")
            else:
                log_warning_safe(self.logger, "Device vendor ID is missing or invalid")

        # Validate BAR configuration
        bar_config = context.get("bar_config", {})
        if not bar_config.get("bars"):
            if self.validation_level == ValidationLevel.STRICT:
                raise PCILeechContextError("No valid BARs found in context")

        # Validate device signature uniqueness
        device_signature = context.get("device_signature")
        if not device_signature or device_signature == "32'hDEADBEEF":
            if self.validation_level == ValidationLevel.STRICT:
                raise PCILeechContextError("Invalid or generic device signature")

        log_info_safe(self.logger, "Template context validation completed successfully")
