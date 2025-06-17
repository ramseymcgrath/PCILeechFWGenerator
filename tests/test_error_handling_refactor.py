#!/usr/bin/env python3
"""
Test for the refactored ErrorHandlingGenerator using TemplateRenderer.
"""

import pytest
from src.templating.advanced_sv_error import (
    ErrorHandlingGenerator,
    ErrorHandlingConfig,
    ErrorType,
)


class TestErrorHandlingRefactor:
    """Test the refactored ErrorHandlingGenerator class."""

    def test_error_handling_generator_initialization(self):
        """Test that the generator initializes correctly with TemplateRenderer."""
        generator = ErrorHandlingGenerator()
        assert generator.config is not None
        assert generator.renderer is not None

    def test_error_handling_with_custom_config(self):
        """Test error handling generation with custom configuration."""
        config = ErrorHandlingConfig(
            enable_ecc=True,
            enable_parity_check=True,
            enable_crc_check=True,
            enable_timeout_detection=True,
            enable_auto_retry=True,
            max_retry_count=5,
            enable_error_logging=True,
            enable_error_injection=True,
            timeout_cycles=2048576,
        )

        generator = ErrorHandlingGenerator(config)

        # Test individual components
        declarations = generator.generate_error_declarations()
        assert "error_status" in declarations
        assert "correctable_error_count" in declarations
        assert "calculated_crc" in declarations  # Should be present when CRC is enabled
        assert "error_log" in declarations  # Should be present when logging is enabled

        detection = generator.generate_error_detection()
        assert "timeout_counter" in detection
        assert "parity_error" in detection
        assert "crc_error" in detection
        assert "ecc_error" in detection

        state_machine = generator.generate_error_state_machine()
        assert "ERR_NORMAL" in state_machine
        assert "ERR_DETECTED" in state_machine
        assert "ERR_FATAL" in state_machine
        assert str(config.max_retry_count) in state_machine

        logging = generator.generate_error_logging()
        assert "Error Logging Logic" in logging
        assert "error_log_ptr" in logging

        counters = generator.generate_error_counters()
        assert "Error Counting Logic" in counters
        assert "correctable_error_count" in counters

        injection = generator.generate_error_injection()
        assert "Error Injection Logic" in injection
        assert "injection_lfsr" in injection

        outputs = generator.generate_error_outputs()
        assert "correctable_error" in outputs
        assert "uncorrectable_error" in outputs
        assert "error_code" in outputs

    def test_error_handling_with_minimal_config(self):
        """Test error handling generation with minimal configuration."""
        config = ErrorHandlingConfig(
            enable_ecc=False,
            enable_parity_check=False,
            enable_crc_check=False,
            enable_timeout_detection=False,
            enable_error_logging=False,
            enable_error_injection=False,
        )

        generator = ErrorHandlingGenerator(config)

        declarations = generator.generate_error_declarations()
        assert (
            "calculated_crc" not in declarations
        )  # Should not be present when CRC is disabled
        assert (
            "error_log" not in declarations
        )  # Should not be present when logging is disabled

        logging = generator.generate_error_logging()
        assert "Error logging disabled" in logging

        injection = generator.generate_error_injection()
        assert "Error injection disabled" in injection

    def test_complete_error_handling_generation(self):
        """Test complete error handling logic generation."""
        generator = ErrorHandlingGenerator()
        complete_logic = generator.generate_complete_error_handling()

        # Verify all components are included
        assert "Error Handling Signals" in complete_logic
        assert "Error Detection Logic" in complete_logic
        assert "Error Handling State Machine" in complete_logic
        assert "Error Counting Logic" in complete_logic
        assert "Error Output Assignments" in complete_logic

        # Verify SystemVerilog syntax
        assert "always_ff" in complete_logic
        assert "always_comb" in complete_logic
        assert "typedef enum" in complete_logic
        assert "assign" in complete_logic

    def test_backward_compatibility(self):
        """Test that the refactored generator maintains backward compatibility."""
        # Test with default configuration
        old_style_generator = ErrorHandlingGenerator()

        # All methods should still work
        declarations = old_style_generator.generate_error_declarations()
        detection = old_style_generator.generate_error_detection()
        state_machine = old_style_generator.generate_error_state_machine()
        logging = old_style_generator.generate_error_logging()
        counters = old_style_generator.generate_error_counters()
        injection = old_style_generator.generate_error_injection()
        outputs = old_style_generator.generate_error_outputs()
        complete = old_style_generator.generate_complete_error_handling()

        # All should return non-empty strings
        assert len(declarations) > 0
        assert len(detection) > 0
        assert len(state_machine) > 0
        assert len(logging) > 0
        assert len(counters) > 0
        assert len(injection) > 0
        assert len(outputs) > 0
        assert len(complete) > 0

    def test_error_types_enum_preserved(self):
        """Test that ErrorType enum is preserved."""
        assert ErrorType.CORRECTABLE.value == "correctable"
        assert ErrorType.UNCORRECTABLE_NON_FATAL.value == "uncorrectable_non_fatal"
        assert ErrorType.UNCORRECTABLE_FATAL.value == "uncorrectable_fatal"

    def test_config_class_preserved(self):
        """Test that ErrorHandlingConfig class is preserved."""
        config = ErrorHandlingConfig()

        # Test default values
        assert config.enable_ecc is True
        assert config.enable_parity_check is True
        assert config.enable_crc_check is True
        assert config.enable_timeout_detection is True
        assert config.enable_auto_retry is True
        assert config.max_retry_count == 3
        assert config.enable_error_logging is True
        assert config.enable_error_injection is False
        assert config.correctable_error_threshold == 100
        assert config.uncorrectable_error_threshold == 10
        assert config.error_recovery_cycles == 1000
        assert config.retry_delay_cycles == 100
        assert config.timeout_cycles == 1048576

        # Test supported error types
        assert ErrorType.CORRECTABLE in config.supported_error_types
        assert ErrorType.UNCORRECTABLE_NON_FATAL in config.supported_error_types


if __name__ == "__main__":
    pytest.main([__file__])
