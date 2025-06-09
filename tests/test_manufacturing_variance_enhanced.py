#!/usr/bin/env python3
"""
Enhanced test suite for manufacturing variance simulation module.

This test suite focuses on:
1. Testing deterministic variance seeding with different DSN and revision combinations
2. Verifying reproducibility across multiple runs
3. Testing boundary conditions for seed generation
4. Testing integration with SystemVerilog code generation
"""

import hashlib
import struct
import unittest
from unittest.mock import MagicMock, patch

from src.manufacturing_variance import (
    DeviceClass,
    ManufacturingVarianceSimulator,
    VarianceModel,
    VarianceParameters,
    VarianceType,
)


class TestDeterministicVarianceSeedingEnhanced(unittest.TestCase):
    """Enhanced test cases for deterministic variance seeding."""

    def test_seed_with_different_dsn_revision_combinations(self):
        """Test deterministic seeding with various DSN and revision combinations."""
        simulator = ManufacturingVarianceSimulator()

        # Test cases with different DSN and revision combinations
        test_cases = [
            # DSN, Revision
            (
                0x0000000000000000,
                "0000000000000000000000000000000000000000",
            ),  # All zeros
            (
                0xFFFFFFFFFFFFFFFF,
                "ffffffffffffffffffffffffffffffffffffffff",
            ),  # All ones
            (
                0x1234567890ABCDEF,
                "abcdef1234567890abcdef1234567890abcdef12",
            ),  # Mixed values
            (
                0x0000000000000001,
                "0000000000000000000000000000000000000001",
            ),  # Minimal values
            (
                0xFFFFFFFFFFFFFFFE,
                "fffffffffffffffffffffffffffffffffffffffe",
            ),  # Near-maximum values
        ]

        # Generate seeds for each test case
        seeds = {}
        for dsn, revision in test_cases:
            seed = simulator.deterministic_seed(dsn, revision)
            seeds[(dsn, revision)] = seed

            # Verify seed is reproducible
            seed2 = simulator.deterministic_seed(dsn, revision)
            self.assertEqual(
                seed, seed2, f"Seed not reproducible for DSN={dsn}, revision={revision}"
            )

        # Verify all seeds are different
        unique_seeds = set(seeds.values())
        self.assertEqual(len(unique_seeds), len(test_cases), "Not all seeds are unique")

    def test_seed_algorithm_correctness(self):
        """Test that the seed algorithm matches the specified requirements."""
        simulator = ManufacturingVarianceSimulator()

        # Test case
        dsn = 0x1234567890ABCDEF
        revision = "abcdef1234567890abcd"

        # Generate seed using the simulator
        seed = simulator.deterministic_seed(dsn, revision)

        # Manually implement the algorithm to verify correctness
        # Pack the DSN as a 64-bit integer and the first 20 chars of revision as bytes
        blob = struct.pack("<Q", dsn) + bytes.fromhex(revision[:20])
        # Generate a SHA-256 hash and convert to integer (little-endian)
        expected_seed = int.from_bytes(hashlib.sha256(blob).digest(), "little")

        # Verify the seed matches the expected value
        self.assertEqual(
            seed, expected_seed, "Seed algorithm does not match specification"
        )

    def test_reproducibility_across_multiple_runs(self):
        """Test that variance models are reproducible across multiple simulator instances."""
        # Create multiple simulator instances
        simulator1 = ManufacturingVarianceSimulator()
        simulator2 = ManufacturingVarianceSimulator()
        simulator3 = ManufacturingVarianceSimulator()

        # Test parameters
        dsn = 0x1234567890ABCDEF
        revision = "abcdef1234567890abcd"
        device_id = "test_device"

        # Generate variance models with the same DSN and revision
        model1 = simulator1.generate_variance_model(
            device_id=device_id,
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        model2 = simulator2.generate_variance_model(
            device_id=device_id,
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        model3 = simulator3.generate_variance_model(
            device_id=device_id,
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
            dsn=dsn,
            revision=revision,
        )

        # Verify all models have identical variance parameters
        self.assertEqual(model1.clock_jitter_percent, model2.clock_jitter_percent)
        self.assertEqual(model1.clock_jitter_percent, model3.clock_jitter_percent)

        self.assertEqual(
            model1.register_timing_jitter_ns, model2.register_timing_jitter_ns
        )
        self.assertEqual(
            model1.register_timing_jitter_ns, model3.register_timing_jitter_ns
        )

        self.assertEqual(model1.power_noise_percent, model2.power_noise_percent)
        self.assertEqual(model1.power_noise_percent, model3.power_noise_percent)

        self.assertEqual(
            model1.temperature_drift_ppm_per_c, model2.temperature_drift_ppm_per_c
        )
        self.assertEqual(
            model1.temperature_drift_ppm_per_c, model3.temperature_drift_ppm_per_c
        )

        self.assertEqual(
            model1.process_variation_percent, model2.process_variation_percent
        )
        self.assertEqual(
            model1.process_variation_percent, model3.process_variation_percent
        )

        self.assertEqual(model1.propagation_delay_ps, model2.propagation_delay_ps)
        self.assertEqual(model1.propagation_delay_ps, model3.propagation_delay_ps)

        self.assertEqual(model1.operating_temp_c, model2.operating_temp_c)
        self.assertEqual(model1.operating_temp_c, model3.operating_temp_c)

        self.assertEqual(model1.supply_voltage_v, model2.supply_voltage_v)
        self.assertEqual(model1.supply_voltage_v, model3.supply_voltage_v)

    def test_boundary_conditions_for_seed_generation(self):
        """Test boundary conditions for seed generation."""
        simulator = ManufacturingVarianceSimulator()

        # Test with minimum DSN value
        min_dsn = 0x0000000000000000
        min_revision = "0000000000000000000000000000000000000000"
        min_seed = simulator.deterministic_seed(min_dsn, min_revision)
        self.assertIsInstance(min_seed, int)
        self.assertGreaterEqual(min_seed, 0)

        # Test with maximum DSN value
        max_dsn = 0xFFFFFFFFFFFFFFFF
        max_revision = "ffffffffffffffffffffffffffffffffffffffff"
        max_seed = simulator.deterministic_seed(max_dsn, max_revision)
        self.assertIsInstance(max_seed, int)
        self.assertGreaterEqual(max_seed, 0)

        # Test with empty revision (should use first 20 chars, which is empty)
        empty_revision = ""
        empty_seed = simulator.deterministic_seed(0x1234567890ABCDEF, empty_revision)
        self.assertIsInstance(empty_seed, int)
        self.assertGreaterEqual(empty_seed, 0)

        # Test with very long revision (should only use first 20 chars)
        long_revision = "a" * 100
        long_seed = simulator.deterministic_seed(0x1234567890ABCDEF, long_revision)

        # Should be the same as using just the first 20 chars
        short_revision = "a" * 20
        short_seed = simulator.deterministic_seed(0x1234567890ABCDEF, short_revision)

        self.assertEqual(long_seed, short_seed)

    def test_deterministic_rng_sequence(self):
        """Test that the RNG sequence is deterministic after initialization."""
        # Create two simulator instances
        simulator1 = ManufacturingVarianceSimulator()
        simulator2 = ManufacturingVarianceSimulator()

        # Initialize with the same seed
        dsn = 0x1234567890ABCDEF
        revision = "abcdef1234567890abcd"

        simulator1.initialize_deterministic_rng(dsn, revision)
        simulator2.initialize_deterministic_rng(dsn, revision)

        # Generate a sequence of random numbers from each simulator
        sequence1 = [simulator1.rng.random() for _ in range(100)]
        sequence2 = [simulator2.rng.random() for _ in range(100)]

        # Verify the sequences are identical
        for i, (val1, val2) in enumerate(zip(sequence1, sequence2)):
            self.assertEqual(val1, val2, f"Random sequences diverged at position {i}")

    def test_deterministic_timing_adjustments(self):
        """Test that timing adjustments are deterministic with the same seed."""
        # Create two simulator instances
        simulator1 = ManufacturingVarianceSimulator()
        simulator2 = ManufacturingVarianceSimulator()

        # Initialize with the same seed
        dsn = 0x1234567890ABCDEF
        revision = "abcdef1234567890abcd"

        # Generate variance models
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

        # Apply variance to timing values
        base_timing = 100.0  # 100ns

        # Generate a sequence of adjusted timings
        timings1 = [
            simulator1.apply_variance_to_timing(base_timing, model1, "register_access")
            for _ in range(20)
        ]
        timings2 = [
            simulator2.apply_variance_to_timing(base_timing, model2, "register_access")
            for _ in range(20)
        ]

        # Verify the sequences are identical
        for i, (val1, val2) in enumerate(zip(timings1, timings2)):
            self.assertEqual(val1, val2, f"Timing sequences diverged at position {i}")

    def test_systemverilog_code_determinism(self):
        """Test that generated SystemVerilog code is deterministic with the same seed."""
        # Create two simulator instances
        simulator1 = ManufacturingVarianceSimulator()
        simulator2 = ManufacturingVarianceSimulator()

        # Initialize with the same seed
        dsn = 0x1234567890ABCDEF
        revision = "abcdef1234567890abcd"

        # Generate variance models
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

        # Generate SystemVerilog code
        sv_code1 = simulator1.generate_systemverilog_timing_code(
            register_name="test_reg",
            base_delay_cycles=5,
            variance_model=model1,
            offset=0x400,
        )

        sv_code2 = simulator2.generate_systemverilog_timing_code(
            register_name="test_reg",
            base_delay_cycles=5,
            variance_model=model2,
            offset=0x400,
        )

        # Verify the generated code is identical
        self.assertEqual(sv_code1, sv_code2)

        # Generate code for different registers with the same models
        sv_code1_reg1 = simulator1.generate_systemverilog_timing_code(
            register_name="reg1",
            base_delay_cycles=5,
            variance_model=model1,
            offset=0x400,
        )

        sv_code2_reg1 = simulator2.generate_systemverilog_timing_code(
            register_name="reg1",
            base_delay_cycles=5,
            variance_model=model2,
            offset=0x400,
        )

        sv_code1_reg2 = simulator1.generate_systemverilog_timing_code(
            register_name="reg2",
            base_delay_cycles=5,
            variance_model=model1,
            offset=0x404,
        )

        sv_code2_reg2 = simulator2.generate_systemverilog_timing_code(
            register_name="reg2",
            base_delay_cycles=5,
            variance_model=model2,
            offset=0x404,
        )

        # Verify the generated code is identical for each register
        self.assertEqual(sv_code1_reg1, sv_code2_reg1)
        self.assertEqual(sv_code1_reg2, sv_code2_reg2)

        # But different between registers (due to different offsets)
        self.assertNotEqual(sv_code1_reg1, sv_code1_reg2)


class TestManufacturingVarianceIntegration(unittest.TestCase):
    """Integration tests for manufacturing variance simulation."""

    def test_device_class_variance_ranges(self):
        """Test that different device classes have appropriate variance ranges."""
        simulator = ManufacturingVarianceSimulator(seed=42)

        # Generate models for different device classes
        consumer_model = simulator.generate_variance_model(
            device_id="consumer_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
        )

        enterprise_model = simulator.generate_variance_model(
            device_id="enterprise_device",
            device_class=DeviceClass.ENTERPRISE,
            base_frequency_mhz=100.0,
        )

        industrial_model = simulator.generate_variance_model(
            device_id="industrial_device",
            device_class=DeviceClass.INDUSTRIAL,
            base_frequency_mhz=100.0,
        )

        automotive_model = simulator.generate_variance_model(
            device_id="automotive_device",
            device_class=DeviceClass.AUTOMOTIVE,
            base_frequency_mhz=100.0,
        )

        # Verify that enterprise has lower variance than consumer
        self.assertLess(
            enterprise_model.clock_jitter_percent, consumer_model.clock_jitter_percent
        )

        self.assertLess(
            enterprise_model.register_timing_jitter_ns,
            consumer_model.register_timing_jitter_ns,
        )

        # Verify that automotive has lower variance than enterprise
        # Note: Due to random number generation, this might not always be true
        # So we'll check the parameter ranges instead
        auto_params = simulator.DEFAULT_VARIANCE_PARAMS[DeviceClass.AUTOMOTIVE]
        enterprise_params = simulator.DEFAULT_VARIANCE_PARAMS[DeviceClass.ENTERPRISE]

        self.assertLess(
            auto_params.process_variation_percent_max,
            enterprise_params.process_variation_percent_max,
        )

        # Verify that industrial has wider temperature range than consumer
        industrial_params = simulator.DEFAULT_VARIANCE_PARAMS[DeviceClass.INDUSTRIAL]
        consumer_params = simulator.DEFAULT_VARIANCE_PARAMS[DeviceClass.CONSUMER]

        self.assertLess(industrial_params.temp_min_c, consumer_params.temp_min_c)

        self.assertGreater(industrial_params.temp_max_c, consumer_params.temp_max_c)

    def test_deterministic_variance_with_different_device_classes(self):
        """Test that deterministic variance works with different device classes."""
        # Create two simulator instances
        simulator1 = ManufacturingVarianceSimulator()
        simulator2 = ManufacturingVarianceSimulator()

        # Initialize with the same seed
        dsn = 0x1234567890ABCDEF
        revision = "abcdef1234567890abcd"

        # Test with all device classes
        for device_class in DeviceClass:
            # Generate variance models
            model1 = simulator1.generate_variance_model(
                device_id=f"test_{device_class.value}",
                device_class=device_class,
                base_frequency_mhz=100.0,
                dsn=dsn,
                revision=revision,
            )

            model2 = simulator2.generate_variance_model(
                device_id=f"test_{device_class.value}",
                device_class=device_class,
                base_frequency_mhz=100.0,
                dsn=dsn,
                revision=revision,
            )

            # Verify models are identical
            self.assertEqual(model1.clock_jitter_percent, model2.clock_jitter_percent)
            self.assertEqual(
                model1.register_timing_jitter_ns, model2.register_timing_jitter_ns
            )
            self.assertEqual(model1.power_noise_percent, model2.power_noise_percent)
            self.assertEqual(
                model1.temperature_drift_ppm_per_c, model2.temperature_drift_ppm_per_c
            )
            self.assertEqual(
                model1.process_variation_percent, model2.process_variation_percent
            )
            self.assertEqual(model1.propagation_delay_ps, model2.propagation_delay_ps)
            self.assertEqual(model1.operating_temp_c, model2.operating_temp_c)
            self.assertEqual(model1.supply_voltage_v, model2.supply_voltage_v)


if __name__ == "__main__":
    unittest.main()
