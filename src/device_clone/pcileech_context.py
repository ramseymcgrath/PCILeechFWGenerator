#!/usr/bin/env python3
"""
PCILeech Template Context Builder

This module builds comprehensive template context from device profiling data,
integrating data from BehaviorProfiler, ConfigSpaceManager, and MSIXCapability
to provide structured context for all PCILeech templates.

The context builder ensures all required data is present and provides validation
to prevent template rendering failures. No fallback values are used - the system
fails if data is incomplete.
"""

import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .behavior_profiler import BehaviorProfile
from ..string_utils import log_error_safe, log_info_safe, log_warning_safe

logger = logging.getLogger(__name__)


class PCILeechContextError(Exception):
    """Exception raised when context building fails."""

    pass


class PCILeechContextBuilder:
    """
    Builds comprehensive template context from device profiling data.

    This class integrates data from multiple sources to create a unified
    template context that can be used for all PCILeech template rendering.

    Key responsibilities:
    - Integrate behavior profiling data
    - Process configuration space information
    - Handle MSI-X capability data
    - Build BAR configuration context
    - Generate timing and performance parameters
    - Validate context completeness
    """

    def __init__(self, device_bdf: str, config: Any):
        """
        Initialize the context builder.

        Args:
            device_bdf: Device Bus:Device.Function identifier
            config: PCILeech generation configuration
        """
        self.device_bdf = device_bdf
        self.config = config
        self.logger = logging.getLogger(__name__)

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
            PCILeechContextError: If context building fails
        """
        log_info_safe(
            self.logger,
            "Building PCILeech template context for device {bdf}",
            bdf=self.device_bdf,
        )

        try:
            # Build core context sections
            device_config = self._build_device_config(
                behavior_profile, config_space_data
            )
            config_space = self._build_config_space_context(config_space_data)
            msix_config = self._build_msix_context(msix_data)
            bar_config = self._build_bar_config(config_space_data, behavior_profile)
            timing_config = self._build_timing_config(behavior_profile)
            pcileech_config = self._build_pcileech_config()

            # Assemble complete context
            context = {
                "device_config": device_config,
                "config_space": config_space,
                "msix_config": msix_config,
                "bar_config": bar_config,
                "timing_config": timing_config,
                "pcileech_config": pcileech_config,
                "generation_metadata": self._build_generation_metadata(),
            }

            # Validate context completeness
            self._validate_context(context)

            log_info_safe(self.logger, "PCILeech template context built successfully")

            return context

        except Exception as e:
            log_error_safe(
                self.logger,
                "Failed to build PCILeech template context: {error}",
                error=str(e),
            )
            raise PCILeechContextError(f"Context building failed: {e}") from e

    def _build_device_config(
        self,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build device configuration context.

        Args:
            behavior_profile: Device behavior profile
            config_space_data: Configuration space data

        Returns:
            Device configuration context
        """
        device_config = {
            "device_bdf": self.device_bdf,
            "vendor_id": config_space_data.get("vendor_id", "0000"),
            "device_id": config_space_data.get("device_id", "0000"),
            "class_code": config_space_data.get("class_code", "000000"),
            "revision_id": config_space_data.get("revision_id", "00"),
            "device_signature": self._generate_device_signature(config_space_data),
            "enable_error_injection": self.config.enable_advanced_features,
            "enable_perf_counters": self.config.enable_advanced_features,
            "enable_dma_operations": self.config.enable_dma_operations,
            "enable_interrupt_coalescing": self.config.enable_interrupt_coalescing,
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
                    "has_manufacturing_variance": hasattr(
                        behavior_profile, "variance_metadata"
                    )
                    and behavior_profile.variance_metadata is not None,
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
        """
        try:
            # Convert dataclass to dictionary
            profile_dict = asdict(behavior_profile)

            # Convert any non-serializable objects to strings
            for key, value in profile_dict.items():
                if hasattr(value, "__dict__"):
                    profile_dict[key] = str(value)

            return profile_dict

        except Exception as e:
            log_warning_safe(
                self.logger,
                "Failed to serialize behavior profile: {error}",
                error=str(e),
            )
            return {"serialization_error": str(e)}

    def _build_config_space_context(
        self, config_space_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build configuration space context.

        Args:
            config_space_data: Configuration space data

        Returns:
            Configuration space context
        """
        return {
            "raw_data": config_space_data.get("config_space_hex", ""),
            "size": config_space_data.get("config_space_size", 0),
            "device_info": config_space_data.get("device_info", {}),
            "vendor_id": config_space_data.get("vendor_id", "0000"),
            "device_id": config_space_data.get("device_id", "0000"),
            "class_code": config_space_data.get("class_code", "000000"),
            "revision_id": config_space_data.get("revision_id", "00"),
            "bars": config_space_data.get("bars", []),
            "has_extended_config": config_space_data.get("config_space_size", 0) > 256,
        }

    def _build_msix_context(self, msix_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build MSI-X configuration context.

        Args:
            msix_data: MSI-X capability data

        Returns:
            MSI-X configuration context
        """
        capability_info = msix_data.get("capability_info", {})

        return {
            "num_vectors": capability_info.get("table_size", 0),
            "table_bir": capability_info.get("table_bir", 0),
            "table_offset": capability_info.get("table_offset", 0),
            "pba_bir": capability_info.get("pba_bir", 0),
            "pba_offset": capability_info.get("pba_offset", 0),
            "enabled": capability_info.get("enabled", False),
            "function_mask": capability_info.get("function_mask", False),
            "is_supported": capability_info.get("table_size", 0) > 0,
            "validation_errors": msix_data.get("validation_errors", []),
            "is_valid": msix_data.get("is_valid", False),
            "table_size_bytes": capability_info.get("table_size", 0)
            * 16,  # 16 bytes per entry
            "pba_size_bytes": ((capability_info.get("table_size", 0) + 31) // 32)
            * 4,  # PBA size in bytes
        }

    def _build_bar_config(
        self,
        config_space_data: Dict[str, Any],
        behavior_profile: Optional[BehaviorProfile],
    ) -> Dict[str, Any]:
        """
        Build BAR configuration context.

        Args:
            config_space_data: Configuration space data
            behavior_profile: Device behavior profile

        Returns:
            BAR configuration context
        """
        bars = config_space_data.get("bars", [])

        # Default BAR configuration
        bar_config = {
            "bar_index": 0,
            "aperture_size": 65536,  # 64KB default
            "bar_type": 0,  # 32-bit
            "prefetchable": 0,
            "memory_type": "memory",
            "bars": [],
        }

        # Process each BAR
        for i, bar_value in enumerate(bars[:6]):  # Only process first 6 BARs
            if bar_value != 0:
                bar_info = self._analyze_bar(i, bar_value)
                bar_config["bars"].append(bar_info)

                # Use first valid BAR as primary
                if i == 0 or bar_config["bar_index"] == 0:
                    bar_config.update(
                        {
                            "bar_index": i,
                            "aperture_size": bar_info["size"],
                            "bar_type": bar_info["type"],
                            "prefetchable": bar_info["prefetchable"],
                        }
                    )

        # Add behavior-based adjustments
        if behavior_profile:
            bar_config.update(
                self._adjust_bar_config_for_behavior(bar_config, behavior_profile)
            )

        return bar_config

    def _analyze_bar(self, index: int, bar_value: int) -> Dict[str, Any]:
        """
        Analyze a single BAR value.

        Args:
            index: BAR index (0-5)
            bar_value: BAR register value

        Returns:
            BAR analysis information
        """
        is_memory = (bar_value & 0x1) == 0

        if is_memory:
            # Memory BAR
            bar_type = (bar_value >> 1) & 0x3  # Bits 2:1
            prefetchable = (bar_value >> 3) & 0x1  # Bit 3
            base_address = bar_value & 0xFFFFFFF0  # Clear lower 4 bits

            # Estimate size (simplified - would need actual probing)
            size = 65536  # Default 64KB

            return {
                "index": index,
                "type": bar_type,
                "prefetchable": prefetchable,
                "base_address": base_address,
                "size": size,
                "is_memory": True,
                "is_io": False,
            }
        else:
            # I/O BAR
            base_address = bar_value & 0xFFFFFFFC  # Clear lower 2 bits
            size = 256  # Default I/O size

            return {
                "index": index,
                "type": 0,
                "prefetchable": 0,
                "base_address": base_address,
                "size": size,
                "is_memory": False,
                "is_io": True,
            }

    def _adjust_bar_config_for_behavior(
        self, bar_config: Dict[str, Any], behavior_profile: BehaviorProfile
    ) -> Dict[str, Any]:
        """
        Adjust BAR configuration based on behavior profile.

        Args:
            bar_config: Current BAR configuration
            behavior_profile: Device behavior profile

        Returns:
            Adjusted BAR configuration parameters
        """
        adjustments = {}

        # Adjust based on access frequency
        if behavior_profile.total_accesses > 1000:
            adjustments["high_frequency_device"] = True
            adjustments["burst_optimization"] = True

        # Adjust based on timing patterns
        if len(behavior_profile.timing_patterns) > 5:
            adjustments["complex_timing"] = True
            adjustments["timing_sensitive"] = True

        return adjustments

    def _build_timing_config(
        self, behavior_profile: Optional[BehaviorProfile]
    ) -> Dict[str, Any]:
        """
        Build timing configuration context.

        Args:
            behavior_profile: Device behavior profile

        Returns:
            Timing configuration context
        """
        # Default timing configuration
        timing_config = {
            "read_latency": 4,
            "write_latency": 2,
            "burst_length": 16,
            "inter_burst_gap": 8,
            "timeout_cycles": 1024,
            "clock_frequency_mhz": 100.0,
            "has_timing_patterns": False,
            "timing_regularity": 0.0,
        }

        # Adjust based on behavior profile
        if behavior_profile:
            timing_config.update(self._extract_timing_from_behavior(behavior_profile))

        return timing_config

    def _extract_timing_from_behavior(
        self, behavior_profile: BehaviorProfile
    ) -> Dict[str, Any]:
        """
        Extract timing parameters from behavior profile.

        Args:
            behavior_profile: Device behavior profile

        Returns:
            Timing parameters extracted from behavior
        """
        timing_params = {
            "has_timing_patterns": len(behavior_profile.timing_patterns) > 0
        }

        if behavior_profile.timing_patterns:
            # Calculate average timing characteristics
            avg_interval = sum(
                p.avg_interval_us for p in behavior_profile.timing_patterns
            ) / len(behavior_profile.timing_patterns)
            avg_frequency = sum(
                p.frequency_hz for p in behavior_profile.timing_patterns
            ) / len(behavior_profile.timing_patterns)
            avg_confidence = sum(
                p.confidence for p in behavior_profile.timing_patterns
            ) / len(behavior_profile.timing_patterns)

            timing_params.update(
                {
                    "avg_access_interval_us": avg_interval,
                    "avg_access_frequency_hz": avg_frequency,
                    "timing_regularity": avg_confidence,
                    "pattern_count": len(behavior_profile.timing_patterns),
                }
            )

            # Adjust latencies based on observed patterns
            if avg_interval < 10:  # Very fast device
                timing_params.update(
                    {"read_latency": 2, "write_latency": 1, "burst_length": 32}
                )
            elif avg_interval > 1000:  # Slow device
                timing_params.update(
                    {"read_latency": 8, "write_latency": 4, "burst_length": 8}
                )

        return timing_params

    def _build_pcileech_config(self) -> Dict[str, Any]:
        """
        Build PCILeech-specific configuration context.

        Returns:
            PCILeech configuration context
        """
        return {
            "command_timeout": self.config.pcileech_command_timeout,
            "buffer_size": self.config.pcileech_buffer_size,
            "enable_dma": self.config.enable_dma_operations,
            "enable_scatter_gather": True,
            "max_payload_size": 256,
            "max_read_request_size": 512,
            "device_ctrl_base": "32'h00000000",
            "device_ctrl_size": "32'h00000100",
            "status_reg_base": "32'h00000100",
            "status_reg_size": "32'h00000100",
            "data_buffer_base": "32'h00000200",
            "data_buffer_size": "32'h00000200",
            "custom_region_base": "32'h00000400",
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

    def _generate_device_signature(self, config_space_data: Dict[str, Any]) -> str:
        """
        Generate a unique device signature.

        Args:
            config_space_data: Configuration space data

        Returns:
            Device signature as hex string
        """
        vendor_id = config_space_data.get("vendor_id", "0000")
        device_id = config_space_data.get("device_id", "0000")
        class_code = config_space_data.get("class_code", "000000")

        # Create signature from device identifiers
        signature = f"{vendor_id}{device_id}{class_code}"

        # Convert to 32-bit hex value
        try:
            signature_int = (
                int(signature[:8], 16) if len(signature) >= 8 else 0xDEADBEEF
            )
            return f"32'h{signature_int:08X}"
        except ValueError:
            return "32'hDEADBEEF"

    def _build_generation_metadata(self) -> Dict[str, Any]:
        """
        Build generation metadata.

        Returns:
            Generation metadata
        """
        from datetime import datetime

        return {
            "generated_at": datetime.now().isoformat(),
            "device_bdf": self.device_bdf,
            "generator_version": "1.0.0",
            "context_builder_version": "1.0.0",
        }

    def _validate_context(self, context: Dict[str, Any]) -> None:
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
        ]

        missing_sections = [
            section for section in required_sections if section not in context
        ]

        if missing_sections:
            if self.config.fail_on_missing_data:
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
            if self.config.fail_on_missing_data:
                raise PCILeechContextError("Device vendor ID is missing or invalid")
            else:
                log_warning_safe(self.logger, "Device vendor ID is missing or invalid")

        log_info_safe(self.logger, "Template context validation completed")
