#!/usr/bin/env python3
"""
Advanced SystemVerilog Generation Module

This module provides sophisticated SystemVerilog generation capabilities for PCIe device
firmware, including advanced timing models, power management, error handling, performance
counters, and device-specific logic generation using Jinja2 templates.

Advanced SystemVerilog Generation feature for the PCILeechFWGenerator project.
"""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

# Import device configuration system
from src.device_clone import DeviceConfiguration as NewDeviceConfiguration
from src.device_clone import (
    ManufacturingVarianceSimulator,
    VarianceModel,
    get_device_config,
)
from src.device_clone.manufacturing_variance import DeviceClass

# Import template renderer
from src.templating import TemplateRenderer, TemplateRenderError

# Import from centralized utils
from src.utils import generate_sv_header_comment


class PowerState(Enum):
    """PCIe power states."""

    D0 = "D0"  # Fully operational
    D1 = "D1"  # Intermediate power state
    D2 = "D2"  # Intermediate power state
    D3_HOT = "D3_HOT"  # Software power down
    D3_COLD = "D3_COLD"  # Hardware power down


class LinkState(Enum):
    """PCIe link power states."""

    L0 = "L0"  # Active state
    L0S = "L0s"  # Standby state
    L1 = "L1"  # Low power standby
    L2 = "L2"  # Auxiliary power
    L3 = "L3"  # Off state


class ErrorType(Enum):
    """PCIe error types."""

    CORRECTABLE = "correctable"
    UNCORRECTABLE_NON_FATAL = "uncorrectable_non_fatal"
    UNCORRECTABLE_FATAL = "uncorrectable_fatal"


class DeviceType(Enum):
    """Device-specific types for specialized logic."""

    GENERIC = "generic"
    NETWORK_CONTROLLER = "network"
    STORAGE_CONTROLLER = "storage"
    GRAPHICS_CONTROLLER = "graphics"
    AUDIO_CONTROLLER = "audio"


@dataclass
class PowerManagementConfig:
    """Configuration for power management features."""

    # Power state support
    supported_power_states: List[PowerState] = field(
        default_factory=lambda: [PowerState.D0, PowerState.D1, PowerState.D3_HOT]
    )
    supported_link_states: List[LinkState] = field(
        default_factory=lambda: [LinkState.L0, LinkState.L0S, LinkState.L1]
    )

    # Power transition timing (in clock cycles)
    d0_to_d1_cycles: int = 100
    d1_to_d0_cycles: int = 50
    d0_to_d3_cycles: int = 1000
    d3_to_d0_cycles: int = 10000

    # Link state transition timing
    l0_to_l0s_cycles: int = 10
    l0s_to_l0_cycles: int = 20
    l0_to_l1_cycles: int = 100
    l1_to_l0_cycles: int = 200

    # Power management features
    enable_clock_gating: bool = True
    enable_power_gating: bool = False
    enable_dynamic_voltage_scaling: bool = False


@dataclass
class PerformanceConfig:
    """Configuration for performance monitoring features."""

    # Counter configuration
    counter_width_bits: int = 32
    enable_bandwidth_monitoring: bool = True
    enable_latency_monitoring: bool = True
    enable_error_rate_monitoring: bool = True
    enable_transaction_counting: bool = True

    # Sampling configuration
    sample_period_cycles: int = 65536
    enable_overflow_interrupts: bool = True
    enable_threshold_alerts: bool = False


@dataclass
class ErrorHandlingConfig:
    """Configuration for error handling features."""

    # Error detection
    enable_correctable_error_detection: bool = True
    enable_uncorrectable_error_detection: bool = True
    enable_fatal_error_detection: bool = True

    # Error recovery
    enable_automatic_recovery: bool = True
    max_retry_count: int = 3
    error_recovery_cycles: int = 1000

    # Error reporting
    enable_error_logging: bool = True
    enable_error_interrupts: bool = True


@dataclass
class DeviceConfig:
    """Legacy configuration class - deprecated in favor of DeviceConfiguration."""

    device_type: DeviceType = DeviceType.GENERIC
    device_class: DeviceClass = DeviceClass.CONSUMER
    vendor_id: str = "0x1234"
    device_id: str = "0x5678"
    max_payload_size: int = 256
    msi_vectors: int = 1

    @classmethod
    def from_device_configuration(
        cls, config: NewDeviceConfiguration
    ) -> "DeviceConfig":
        """Create legacy DeviceConfig from new DeviceConfiguration."""
        return cls(
            device_type=DeviceType.GENERIC,  # Map from new enum
            device_class=DeviceClass.CONSUMER,  # Map from new enum
            vendor_id=config.identification.vendor_id_hex,
            device_id=config.identification.device_id_hex,
            max_payload_size=config.capabilities.max_payload_size,
            msi_vectors=config.capabilities.msi_vectors,
        )


class SystemVerilogGenerator:
    """Generates advanced SystemVerilog modules using Jinja2 templates."""

    def __init__(
        self,
        device_config: DeviceConfig,
        power_config: PowerManagementConfig,
        perf_config: PerformanceConfig,
        error_config: ErrorHandlingConfig,
    ):
        self.device_config = device_config
        self.power_config = power_config
        self.perf_config = perf_config
        self.error_config = error_config
        self.renderer = TemplateRenderer()

    def generate_advanced_module(
        self, regs: List[Dict], variance_model: Optional[VarianceModel] = None
    ) -> str:
        """Generate advanced SystemVerilog module using templates."""
        # Build template context
        context = {
            "header": self._generate_header(),
            "device_config": self.device_config,
            "power_management": self._build_power_context(),
            "performance_counters": self._build_perf_context(),
            "error_handling": self._build_error_context(),
            "registers": regs,
            "variance_model": variance_model,
        }

        # Render main module template
        return self.renderer.render_template(
            "systemverilog/advanced/main_module.sv.j2", context
        )

    def _generate_header(self) -> str:
        """Generate SystemVerilog header comment."""
        return generate_sv_header_comment(
            f"Advanced {self.device_config.device_type.value.title()} Controller",
            device_type=self.device_config.device_type.value,
            device_class=self.device_config.device_class.value,
            vendor_id=self.device_config.vendor_id,
            device_id=self.device_config.device_id,
        )

    def _build_power_context(self) -> Dict:
        """Build power management context for templates."""
        return {
            "supported_states": [
                state.value for state in self.power_config.supported_power_states
            ],
            "transition_cycles": {
                "d0_to_d1": self.power_config.d0_to_d1_cycles,
                "d1_to_d0": self.power_config.d1_to_d0_cycles,
                "d0_to_d3": self.power_config.d0_to_d3_cycles,
                "d3_to_d0": self.power_config.d3_to_d0_cycles,
            },
            "enable_clock_gating": self.power_config.enable_clock_gating,
            "enable_power_gating": self.power_config.enable_power_gating,
        }

    def _build_perf_context(self) -> Dict:
        """Build performance monitoring context for templates."""
        return {
            "counter_width": self.perf_config.counter_width_bits,
            "enable_bandwidth": self.perf_config.enable_bandwidth_monitoring,
            "enable_latency": self.perf_config.enable_latency_monitoring,
            "enable_error_rate": self.perf_config.enable_error_rate_monitoring,
            "sample_period": self.perf_config.sample_period_cycles,
            "enable_overflow_interrupts": self.perf_config.enable_overflow_interrupts,
        }

    def _build_error_context(self) -> Dict:
        """Build error handling context for templates."""
        return {
            "correctable_errors": self.error_config.enable_correctable_error_detection,
            "uncorrectable_errors": self.error_config.enable_uncorrectable_error_detection,
            "fatal_errors": self.error_config.enable_fatal_error_detection,
            "automatic_recovery": self.error_config.enable_automatic_recovery,
            "max_retry_count": self.error_config.max_retry_count,
            "recovery_cycles": self.error_config.error_recovery_cycles,
            "enable_logging": self.error_config.enable_error_logging,
            "enable_interrupts": self.error_config.enable_error_interrupts,
        }

    def generate_clock_crossing_module(
        self, variance_model: Optional[VarianceModel] = None
    ) -> str:
        """Generate clock domain crossing module with variance compensation."""

        # Generate header comment using existing method
        header = generate_sv_header_comment(
            "Advanced Clock Domain Crossing Module",
            device_type=self.device_config.device_type.value,
            device_class=self.device_config.device_class.value,
        )

        # Build template context with required variables
        context = {
            "header": header,
            "module_name": "advanced_clock_crossing",
            "data_width": 32,
            "sync_stages": 2,
            "device_config": self.device_config,
            "variance_model": variance_model,
            "power_management": self._build_power_context(),
            "performance_counters": self._build_perf_context(),
            "error_handling": self._build_error_context(),
        }

        # Render template using the existing TemplateRenderer
        return self.renderer.render_template(
            "systemverilog/advanced/clock_crossing.sv.j2", context
        )


# Alias for backward compatibility
AdvancedSVGenerator = SystemVerilogGenerator
