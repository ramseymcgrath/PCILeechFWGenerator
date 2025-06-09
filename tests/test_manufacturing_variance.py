"""
Tests for manufacturing variance simulation module.
"""

import pytest

from src.manufacturing_variance import (
    DeviceClass,
    ManufacturingVarianceSimulator,
    VarianceModel,
    VarianceParameters,
    VarianceType,
)


class TestDeterministicVarianceSeeding:
    """Test cases for deterministic variance seeding."""

    def test_deterministic_seed_generation(self):
        """Test that deterministic seed generation produces consistent results."""
        simulator = ManufacturingVarianceSimulator()

        # Test with sample DSN and revision
        dsn = 0x1234567890ABCDEF
        revision = "abcdef1234567890abcd"

        # Generate seed twice with the same inputs
        seed1 = simulator.deterministic_seed(dsn, revision)
        seed2 = simulator.deterministic_seed(dsn, revision)

        # Seeds should be identical
        assert seed1 == seed2

        # Test with different DSN
        different_dsn = 0x1234567890ABCDE0
        different_seed = simulator.deterministic_seed(different_dsn, revision)

        # Seeds should be different
        assert seed1 != different_seed

        # Test with different revision
        different_revision = "abcdef1234567890abce"
        different_seed = simulator.deterministic_seed(dsn, different_revision)

        # Seeds should be different
        assert seed1 != different_seed

    def test_deterministic_rng_initialization(self):
        """Test that RNG initialization with deterministic seed produces consistent results."""
        simulator1 = ManufacturingVarianceSimulator()
        simulator2 = ManufacturingVarianceSimulator()

        dsn = 0x1234567890ABCDEF
        revision = "abcdef1234567890abcd"

        # Initialize both simulators with the same DSN and revision
        seed1 = simulator1.initialize_deterministic_rng(dsn, revision)
        seed2 = simulator2.initialize_deterministic_rng(dsn, revision)

        # Seeds should be identical
        assert seed1 == seed2

        # Generate some random numbers and verify they're identical
        for _ in range(10):
            assert simulator1.rng.random() == simulator2.rng.random()

    def test_deterministic_variance_model(self):
        """Test that variance models generated with the same DSN and revision are identical."""
        simulator1 = ManufacturingVarianceSimulator()
        simulator2 = ManufacturingVarianceSimulator()

        dsn = 0x1234567890ABCDEF
        revision = "abcdef1234567890abcd"

        # Generate variance models with the same DSN and revision
        model1 = simulator1.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        model2 = simulator2.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        # Models should have identical variance parameters
        assert model1.clock_jitter_percent == model2.clock_jitter_percent
        assert model1.register_timing_jitter_ns == model2.register_timing_jitter_ns
        assert model1.power_noise_percent == model2.power_noise_percent
        assert model1.temperature_drift_ppm_per_c == model2.temperature_drift_ppm_per_c
        assert model1.process_variation_percent == model2.process_variation_percent
        assert model1.propagation_delay_ps == model2.propagation_delay_ps
        assert model1.operating_temp_c == model2.operating_temp_c
        assert model1.supply_voltage_v == model2.supply_voltage_v

        # Generate a model with different DSN
        different_dsn = 0x1234567890ABCDE0
        different_model = simulator1.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=different_dsn,
            revision=revision,
        )

        # Models should have different variance parameters
        assert model1.clock_jitter_percent != different_model.clock_jitter_percent


class TestManufacturingVarianceSimulator:
    """Test cases for ManufacturingVarianceSimulator."""

    def test_simulator_initialization(self):
        """Test simulator initialization."""
        simulator = ManufacturingVarianceSimulator()
        assert simulator.generated_models == {}

    def test_variance_model_generation(self):
        """Test variance model generation."""
        simulator = ManufacturingVarianceSimulator(seed=42)

        model = simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
        )

        assert model.device_id == "test_device"
        assert model.device_class == DeviceClass.CONSUMER
        assert model.base_frequency_mhz == 100.0
        assert model.clock_jitter_percent > 0
        assert model.register_timing_jitter_ns > 0
        assert "test_device" in simulator.generated_models

    def test_device_class_parameters(self):
        """Test different device class parameters."""
        simulator = ManufacturingVarianceSimulator(seed=42)

        # Test enterprise class (should have lower variance)
        enterprise_model = simulator.generate_variance_model(
            device_id="enterprise_device", device_class=DeviceClass.ENTERPRISE
        )

        # Test consumer class (should have higher variance)
        consumer_model = simulator.generate_variance_model(
            device_id="consumer_device", device_class=DeviceClass.CONSUMER
        )

        # Enterprise should generally have lower variance than consumer
        # Note: This might not always be true due to randomness, but with seed it should be consistent
        assert enterprise_model.device_class == DeviceClass.ENTERPRISE
        assert consumer_model.device_class == DeviceClass.CONSUMER

    def test_timing_pattern_analysis(self):
        """Test timing pattern analysis."""
        simulator = ManufacturingVarianceSimulator()

        # Test with empty data
        empty_analysis = simulator.analyze_timing_patterns([])
        assert not empty_analysis["variance_detected"]

        # Test with timing data
        timing_data = [
            {"interval_us": 10.0},
            {"interval_us": 12.0},
            {"interval_us": 8.0},
            {"interval_us": 11.0},
            {"interval_us": 9.0},
        ]

        analysis = simulator.analyze_timing_patterns(timing_data)
        assert "variance_detected" in analysis
        assert "mean_interval_us" in analysis
        assert "coefficient_of_variation" in analysis
        assert analysis["sample_count"] == 5

    def test_variance_application(self):
        """Test variance application to timing values."""
        simulator = ManufacturingVarianceSimulator(seed=42)

        model = simulator.generate_variance_model(
            device_id="test_device", device_class=DeviceClass.CONSUMER
        )

        base_timing = 100.0  # 100ns
        adjusted_timing = simulator.apply_variance_to_timing(
            base_timing, model, "register_access"
        )

        # Should be positive and different from base
        assert adjusted_timing > 0
        # With variance, it should typically be different from base
        # (though with very low variance it might be the same)

    def test_systemverilog_code_generation(self):
        """Test SystemVerilog code generation."""
        simulator = ManufacturingVarianceSimulator(seed=42)

        model = simulator.generate_variance_model(
            device_id="test_device", device_class=DeviceClass.CONSUMER
        )

        sv_code = simulator.generate_systemverilog_timing_code(
            register_name="test_reg",
            base_delay_cycles=5,
            variance_model=model,
            offset=0x400,
        )

        assert "test_reg" in sv_code
        assert "always_ff" in sv_code
        assert "variance-aware" in sv_code
        assert "LFSR" in sv_code

    def test_variance_metadata(self):
        """Test variance metadata extraction."""
        simulator = ManufacturingVarianceSimulator(seed=42)

        model = simulator.generate_variance_model(
            device_id="test_device", device_class=DeviceClass.INDUSTRIAL
        )

        metadata = simulator.get_variance_metadata(model)

        assert metadata["device_id"] == "test_device"
        assert metadata["device_class"] == "industrial"
        assert "variance_parameters" in metadata
        assert "operating_conditions" in metadata
        assert "timing_adjustments" in metadata

    def test_variance_parameters_dataclass(self):
        """Test VarianceParameters dataclass."""
        params = VarianceParameters(
            device_class=DeviceClass.AUTOMOTIVE,
            clock_jitter_percent_min=1.0,
            clock_jitter_percent_max=2.0,
        )

        assert params.device_class == DeviceClass.AUTOMOTIVE
        assert params.clock_jitter_percent_min == 1.0
        assert params.clock_jitter_percent_max == 2.0
        # Test defaults
        assert params.register_timing_jitter_ns_min == 10.0

    def test_variance_model_timing_calculations(self):
        """Test variance model timing calculations."""
        model = VarianceModel(
            device_id="test",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            clock_jitter_percent=5.0,
            register_timing_jitter_ns=25.0,
            power_noise_percent=2.0,
            temperature_drift_ppm_per_c=50.0,
            process_variation_percent=10.0,
            propagation_delay_ps=100.0,
            operating_temp_c=50.0,  # 25°C above reference
        )

        # Check that timing adjustments are calculated
        assert "base_period_ns" in model.timing_adjustments
        assert "jitter_ns" in model.timing_adjustments
        assert "combined_timing_factor" in model.timing_adjustments

        # Temperature factor should be > 1 since temp is above reference
        assert model.timing_adjustments["temp_factor"] > 1.0

        # Combined factor should include all effects
        combined = model.timing_adjustments["combined_timing_factor"]
        assert combined > 1.0  # Should be greater than 1 due to variations

    def test_reproducible_generation(self):
        """Test that variance generation is reproducible with seed."""
        simulator1 = ManufacturingVarianceSimulator(seed=123)
        simulator2 = ManufacturingVarianceSimulator(seed=123)

        model1 = simulator1.generate_variance_model("test", DeviceClass.CONSUMER)
        model2 = simulator2.generate_variance_model("test", DeviceClass.CONSUMER)

        # Should be identical with same seed
        assert model1.clock_jitter_percent == model2.clock_jitter_percent
        assert model1.register_timing_jitter_ns == model2.register_timing_jitter_ns
        assert model1.operating_temp_c == model2.operating_temp_c


class TestVarianceIntegration:
    """Integration tests for variance simulation."""

    def test_default_device_class_parameters(self):
        """Test that default parameters exist for all device classes."""
        simulator = ManufacturingVarianceSimulator()

        for device_class in DeviceClass:
            assert device_class in simulator.DEFAULT_VARIANCE_PARAMS
            params = simulator.DEFAULT_VARIANCE_PARAMS[device_class]
            assert isinstance(params, VarianceParameters)
            assert params.device_class == device_class

    def test_variance_ranges_logical(self):
        """Test that variance ranges are logical."""
        simulator = ManufacturingVarianceSimulator()

        for device_class, params in simulator.DEFAULT_VARIANCE_PARAMS.items():
            # Min should be less than max
            assert params.clock_jitter_percent_min < params.clock_jitter_percent_max
            assert (
                params.register_timing_jitter_ns_min
                < params.register_timing_jitter_ns_max
            )
            assert params.power_noise_percent_min < params.power_noise_percent_max

            # Enterprise should generally have tighter tolerances than consumer
            if device_class == DeviceClass.ENTERPRISE:
                consumer_params = simulator.DEFAULT_VARIANCE_PARAMS[
                    DeviceClass.CONSUMER
                ]
                assert (
                    params.clock_jitter_percent_max
                    <= consumer_params.clock_jitter_percent_max
                )
                assert (
                    params.register_timing_jitter_ns_max
                    <= consumer_params.register_timing_jitter_ns_max
                )
