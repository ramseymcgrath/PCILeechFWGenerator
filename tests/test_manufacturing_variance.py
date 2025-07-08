#!/usr/bin/env python3
"""Unit tests for manufacturing variance simulation."""

import pytest
import json
from unittest.mock import Mock, patch

from src.device_clone.manufacturing_variance import (
    ManufacturingVarianceSimulator,
    VarianceModel,
    VarianceParameters,
    DeviceClass,
    VarianceType,
    clamp,
    setup_logging,
)


class TestHelperFunctions:
    """Test helper functions."""

    def test_clamp_within_bounds(self):
        """Test clamp function with value within bounds."""
        assert clamp(5.0, 0.0, 10.0) == 5.0

    def test_clamp_below_minimum(self):
        """Test clamp function with value below minimum."""
        assert clamp(-5.0, 0.0, 10.0) == 0.0

    def test_clamp_above_maximum(self):
        """Test clamp function with value above maximum."""
        assert clamp(15.0, 0.0, 10.0) == 10.0

    def test_clamp_edge_cases(self):
        """Test clamp function edge cases."""
        assert clamp(0.0, 0.0, 10.0) == 0.0
        assert clamp(10.0, 0.0, 10.0) == 10.0


class TestVarianceParameters:
    """Test VarianceParameters dataclass."""

    def test_variance_parameters_creation(self):
        """Test creating VarianceParameters with default values."""
        params = VarianceParameters(device_class=DeviceClass.CONSUMER)
        assert params.clock_jitter_percent_min == 2.0
        assert params.clock_jitter_percent_max == 5.0
        assert params.temp_min_c == 0.0
        assert params.temp_max_c == 85.0

    def test_variance_parameters_custom_values(self):
        """Test creating VarianceParameters with custom values."""
        params = VarianceParameters(
            device_class=DeviceClass.ENTERPRISE,
            clock_jitter_percent_min=1.0,
            clock_jitter_percent_max=3.0,
            temp_min_c=-10.0,
            temp_max_c=90.0,
        )
        assert params.device_class == DeviceClass.ENTERPRISE
        assert params.clock_jitter_percent_min == 1.0
        assert params.clock_jitter_percent_max == 3.0
        assert params.temp_min_c == -10.0
        assert params.temp_max_c == 90.0

    def test_variance_parameters_validation(self):
        """Test VarianceParameters validation in post_init."""
        # This should not raise an exception
        params = VarianceParameters(device_class=DeviceClass.CONSUMER)
        # Validation happens in __post_init__
        assert params.clock_jitter_percent_min <= params.clock_jitter_percent_max


class TestVarianceModel:
    """Test VarianceModel dataclass."""

    def test_variance_model_creation(self):
        """Test creating a VarianceModel."""
        model = VarianceModel(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            clock_jitter_percent=0.1,
            register_timing_jitter_ns=0.5,
            power_noise_percent=2.0,
            temperature_drift_ppm_per_c=50.0,
            process_variation_percent=5.0,
            propagation_delay_ps=100.0,
            operating_temp_c=25.0,
            supply_voltage_v=3.3,
        )
        assert model.device_id == "test_device"
        assert model.device_class == DeviceClass.CONSUMER
        assert model.base_frequency_mhz == 100.0

    def test_variance_model_timing_adjustments(self):
        """Test that timing adjustments are calculated in post_init."""
        model = VarianceModel(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            clock_jitter_percent=0.1,
            register_timing_jitter_ns=0.5,
            power_noise_percent=2.0,
            temperature_drift_ppm_per_c=50.0,
            process_variation_percent=5.0,
            propagation_delay_ps=100.0,
            operating_temp_c=25.0,
            supply_voltage_v=3.3,
        )
        # Check that timing adjustments were calculated
        assert hasattr(model, "effective_clock_period_ns")
        assert hasattr(model, "setup_time_adjustment_ns")
        assert hasattr(model, "hold_time_adjustment_ns")

    def test_variance_model_to_json(self):
        """Test serializing VarianceModel to JSON."""
        model = VarianceModel(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            clock_jitter_percent=0.1,
            register_timing_jitter_ns=0.5,
            power_noise_percent=2.0,
            temperature_drift_ppm_per_c=50.0,
            process_variation_percent=5.0,
            propagation_delay_ps=100.0,
            operating_temp_c=25.0,
            supply_voltage_v=3.3,
        )
        json_str = model.to_json()
        data = json.loads(json_str)
        assert data["device_id"] == "test_device"
        assert data["device_class"] == "CONSUMER"
        assert data["base_frequency_mhz"] == 100.0

    def test_variance_model_from_json(self):
        """Test deserializing VarianceModel from JSON."""
        json_data = {
            "device_id": "test_device",
            "device_class": "CONSUMER",
            "base_frequency_mhz": 100.0,
            "clock_jitter_percent": 0.1,
            "register_timing_jitter_ns": 0.5,
            "power_noise_percent": 2.0,
            "temperature_drift_ppm_per_c": 50.0,
            "process_variation_percent": 5.0,
            "propagation_delay_ps": 100.0,
            "operating_temp_c": 25.0,
            "supply_voltage_v": 3.3,
            "effective_clock_period_ns": 10.0,
            "setup_time_adjustment_ns": 0.1,
            "hold_time_adjustment_ns": 0.1,
        }
        json_str = json.dumps(json_data)
        model = VarianceModel.from_json(json_str)
        assert model.device_id == "test_device"
        assert model.device_class == DeviceClass.CONSUMER
        assert model.base_frequency_mhz == 100.0


class TestManufacturingVarianceSimulator:
    """Test ManufacturingVarianceSimulator class."""

    @pytest.fixture
    def simulator(self):
        """Create a simulator instance for testing."""
        return ManufacturingVarianceSimulator(seed=42)

    def test_simulator_initialization_with_seed(self):
        """Test simulator initialization with specific seed."""
        sim = ManufacturingVarianceSimulator(seed=42)
        # The seed is stored internally in the rng
        assert sim.rng is not None

    def test_simulator_initialization_with_string_seed(self):
        """Test simulator initialization with string seed."""
        sim = ManufacturingVarianceSimulator(seed="test_seed")
        # String seed should be hashed internally
        assert sim.rng is not None

    def test_deterministic_seed_generation(self, simulator):
        """Test deterministic seed generation from DSN and revision."""
        seed1 = simulator.deterministic_seed(dsn=12345, revision="v1.0")
        seed2 = simulator.deterministic_seed(dsn=12345, revision="v1.0")
        seed3 = simulator.deterministic_seed(dsn=12346, revision="v1.0")

        assert seed1 == seed2  # Same inputs should produce same seed
        assert seed1 != seed3  # Different DSN should produce different seed

    def test_generate_variance_model_basic(self, simulator):
        """Test basic variance model generation."""
        model = simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
        )

        assert model.device_id == "test_device"
        assert model.device_class == DeviceClass.CONSUMER
        assert model.base_frequency_mhz == 100.0

        # Check that variance values are within expected ranges
        params = simulator.default_variance_params[DeviceClass.CONSUMER]
        assert (
            params.clock_jitter_percent_min
            <= model.clock_jitter_percent
            <= params.clock_jitter_percent_max
        )
        assert params.temp_min_c <= model.operating_temp_c <= params.temp_max_c

    def test_generate_variance_model_with_custom_params(self, simulator):
        """Test variance model generation with custom parameters."""
        custom_params = VarianceParameters(
            device_class=DeviceClass.CONSUMER,
            clock_jitter_percent_min=1.0,
            clock_jitter_percent_max=2.0,
            temp_min_c=10.0,
            temp_max_c=50.0,
        )

        model = simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            custom_params=custom_params,
        )

        # Check that custom parameters were used
        assert 1.0 <= model.clock_jitter_percent <= 2.0
        assert 10.0 <= model.operating_temp_c <= 50.0

    def test_generate_variance_model_deterministic(self, simulator):
        """Test deterministic variance model generation."""
        model1 = simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=12345,
            revision="v1.0",
        )

        # Reset simulator with same seed
        simulator2 = ManufacturingVarianceSimulator(seed=42)
        model2 = simulator2.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=12345,
            revision="v1.0",
        )

        # Models should be identical when using same DSN and revision
        assert model1.clock_jitter_percent == model2.clock_jitter_percent
        assert model1.operating_temp_c == model2.operating_temp_c

    def test_generate_variance_model_invalid_frequency(self, simulator):
        """Test variance model generation with invalid frequency."""
        with pytest.raises(ValueError, match="base_frequency_mhz must be positive"):
            simulator.generate_variance_model(
                device_id="test_device",
                device_class=DeviceClass.CONSUMER,
                base_frequency_mhz=-100.0,
            )

    def test_analyze_timing_patterns(self, simulator):
        """Test timing pattern analysis."""
        # Create mock timing data
        from collections import namedtuple

        TimingDatum = namedtuple("TimingDatum", ["timestamp", "duration", "register"])

        timing_data = [
            TimingDatum(timestamp=0.0, duration=0.001, register=0x10),
            TimingDatum(timestamp=0.1, duration=0.0012, register=0x10),
            TimingDatum(timestamp=0.2, duration=0.0011, register=0x10),
            TimingDatum(timestamp=0.3, duration=0.0009, register=0x20),
            TimingDatum(timestamp=0.4, duration=0.0008, register=0x20),
        ]

        analysis = simulator.analyze_timing_patterns(timing_data)

        assert "register_patterns" in analysis
        assert 0x10 in analysis["register_patterns"]
        assert 0x20 in analysis["register_patterns"]
        assert "overall_stats" in analysis

    def test_apply_variance_to_timing(self, simulator):
        """Test applying variance to timing value."""
        model = simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
        )

        base_timing_ns = 10.0
        varied_timing = simulator.apply_variance_to_timing(
            base_timing_ns=base_timing_ns,
            variance_model=model,
            timing_type=VarianceType.REGISTER_TIMING,
        )

        # Varied timing should be different from base (with very high probability)
        # but within reasonable bounds
        assert 0.5 * base_timing_ns <= varied_timing <= 2.0 * base_timing_ns

    def test_generate_systemverilog_timing_code(self, simulator):
        """Test SystemVerilog timing code generation."""
        model = simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
        )

        sv_code = simulator.generate_systemverilog_timing_code(
            variance_model=model,
            module_name="test_module",
        )

        assert "module test_module" in sv_code
        assert "parameter" in sv_code
        assert "CLOCK_PERIOD" in sv_code

    def test_get_variance_metadata(self, simulator):
        """Test variance metadata generation."""
        model = simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
        )

        metadata = simulator.get_variance_metadata(model)

        assert "device_id" in metadata
        assert "device_class" in metadata
        assert "variance_summary" in metadata
        assert "timing_parameters" in metadata
        assert "environmental_conditions" in metadata


class TestDeviceClass:
    """Test DeviceClass enum."""

    def test_device_class_values(self):
        """Test DeviceClass enum values."""
        assert DeviceClass.CONSUMER.value == "consumer"
        assert DeviceClass.ENTERPRISE.value == "enterprise"
        assert DeviceClass.INDUSTRIAL.value == "industrial"
        assert DeviceClass.AUTOMOTIVE.value == "automotive"
        # MILITARY class doesn't exist in the actual enum


class TestVarianceType:
    """Test VarianceType enum."""

    def test_variance_type_values(self):
        """Test VarianceType enum values."""
        assert VarianceType.CLOCK_JITTER.value == "clock_jitter"
        assert VarianceType.REGISTER_TIMING.value == "register_timing"
        assert VarianceType.POWER_NOISE.value == "power_noise"
        assert VarianceType.TEMPERATURE_DRIFT.value == "temperature_drift"
        assert VarianceType.PROCESS_VARIATION.value == "process_variation"
        assert VarianceType.PROPAGATION_DELAY.value == "propagation_delay"
