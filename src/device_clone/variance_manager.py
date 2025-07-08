#!/usr/bin/env python3
"""
Variance Management Module

Handles manufacturing variance simulation and behavior profiling for PCILeech firmware building.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..string_utils import log_info_safe
from .behavior_profiler import BehaviorProfiler
from .manufacturing_variance import (
    DeviceClass,
    ManufacturingVarianceSimulator,
    VarianceModel,
)

logger = logging.getLogger(__name__)


class VarianceManager:
    """Manages manufacturing variance simulation and behavior profiling."""

    def __init__(self, bdf: str, output_dir: Path, fallback_manager=None):
        self.bdf = bdf
        self.output_dir = output_dir
        self.variance_simulator = None
        self.behavior_profiler = None

        # Use provided fallback manager or create a default one
        if fallback_manager is None:
            try:
                from .fallback_manager import FallbackManager

                self.fallback_manager = FallbackManager(mode="none")
            except ImportError:
                self.fallback_manager = None
        else:
            self.fallback_manager = fallback_manager

    def apply_manufacturing_variance(self, device_info: Dict[str, Any]) -> List[str]:
        """Apply manufacturing variance simulation."""
        variance_files = []

        try:
            if not DeviceClass or not VarianceModel:
                error_msg = "Manufacturing variance modules not available"
                logger.warning(error_msg)

                # Check with fallback manager if available
                if (
                    self.fallback_manager
                    and not self.fallback_manager.confirm_fallback(
                        "variance-modules",
                        error_msg,
                        "Variance simulation enhances realism but isn't critical for functionality.",
                    )
                ):
                    logger.error("Manufacturing variance fallback denied by policy")

                return variance_files

            # Determine device class based on actual enum values
            class_code = int(device_info["class_code"], 16)
            if class_code == 0x0200:  # Ethernet
                device_class = DeviceClass.ENTERPRISE
            elif class_code == 0x0403:  # Audio
                device_class = DeviceClass.CONSUMER
            else:
                device_class = DeviceClass.CONSUMER

            # Create variance model
            variance_model = VarianceModel(
                device_id=device_info["device_id"],
                device_class=device_class,
                base_frequency_mhz=100.0,  # Default frequency
                clock_jitter_percent=2.5,
                register_timing_jitter_ns=25.0,
                power_noise_percent=2.0,
                temperature_drift_ppm_per_c=50.0,
                process_variation_percent=10.0,
                propagation_delay_ps=100.0,
            )

            # Save variance data
            variance_data = {
                "device_class": device_class.value,
                "variance_model": {
                    "device_id": variance_model.device_id,
                    "device_class": variance_model.device_class.value,
                    "base_frequency_mhz": variance_model.base_frequency_mhz,
                    "clock_jitter_percent": variance_model.clock_jitter_percent,
                    "register_timing_jitter_ns": variance_model.register_timing_jitter_ns,
                    "power_noise_percent": variance_model.power_noise_percent,
                    "temperature_drift_ppm_per_c": variance_model.temperature_drift_ppm_per_c,
                    "process_variation_percent": variance_model.process_variation_percent,
                    "propagation_delay_ps": variance_model.propagation_delay_ps,
                },
            }

            variance_file = self.output_dir / "manufacturing_variance.json"
            with open(variance_file, "w") as f:
                json.dump(variance_data, f, indent=2)
            variance_files.append(str(variance_file))

            log_info_safe(
                logger,
                "Applied manufacturing variance for {device_class}",
                device_class=device_class.value,
            )

        except Exception as e:
            error_msg = f"Error applying manufacturing variance: {e}"
            logger.error(error_msg)

            # Check with fallback manager if available
            if self.fallback_manager:
                self.fallback_manager.confirm_fallback(
                    "variance-simulation",
                    str(e),
                    "Without variance simulation, the generated firmware will use default timing values.",
                )

        return variance_files

    def run_behavior_profiling(
        self, device_info: Dict[str, Any], duration: int = 30
    ) -> Optional[str]:
        """Run behavior profiling if available."""
        if not BehaviorProfiler:
            error_msg = "Behavior profiler not available"
            logger.warning(error_msg)

            # Check with fallback manager if available
            if self.fallback_manager and not self.fallback_manager.confirm_fallback(
                "profiling-module",
                error_msg,
                "Behavior profiling enhances device emulation but isn't critical for functionality.",
            ):
                logger.error("Behavior profiling fallback denied by policy")

            return None

        try:
            logger.info(f"Starting behavior profiling for {duration} seconds")
            self.behavior_profiler = BehaviorProfiler(self.bdf)

            # Capture behavior profile
            profile_data = self.behavior_profiler.capture_behavior_profile(duration)

            # Convert to serializable format
            profile_dict = {
                "device_bdf": profile_data.device_bdf,
                "capture_duration": profile_data.capture_duration,
                "total_accesses": profile_data.total_accesses,
                "register_accesses": [
                    {
                        "timestamp": access.timestamp,
                        "register": access.register,
                        "offset": access.offset,
                        "operation": access.operation,
                        "value": access.value,
                        "duration_us": access.duration_us,
                    }
                    for access in profile_data.register_accesses
                ],
                "timing_patterns": [
                    {
                        "pattern_type": pattern.pattern_type,
                        "registers": pattern.registers,
                        "avg_interval_us": pattern.avg_interval_us,
                        "std_deviation_us": pattern.std_deviation_us,
                        "frequency_hz": pattern.frequency_hz,
                        "confidence": pattern.confidence,
                    }
                    for pattern in profile_data.timing_patterns
                ],
                "state_transitions": profile_data.state_transitions,
                "power_states": profile_data.power_states,
                "interrupt_patterns": profile_data.interrupt_patterns,
            }

            # Save profile data
            profile_file = self.output_dir / "behavior_profile.json"
            with open(profile_file, "w") as f:
                json.dump(profile_dict, f, indent=2)

            logger.info(f"Behavior profiling completed, saved to {profile_file}")
            return str(profile_file)

        except Exception as e:
            error_msg = f"Error during behavior profiling: {e}"
            logger.error(error_msg)

            # Check with fallback manager if available
            if self.fallback_manager and not self.fallback_manager.confirm_fallback(
                "behavior-profiling",
                str(e),
                "Without behavior profiling, the generated firmware may not accurately reflect device timing patterns.",
            ):
                logger.error("Behavior profiling fallback denied by policy")

            return None

    def is_variance_available(self) -> bool:
        """Check if manufacturing variance simulation is available."""
        return ManufacturingVarianceSimulator is not None

    def is_profiling_available(self) -> bool:
        """Check if behavior profiling is available."""
        return BehaviorProfiler is not None
