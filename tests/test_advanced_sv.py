#!/usr/bin/env python3
"""
Test suite for Advanced SystemVerilog Generation

Tests the modular advanced SystemVerilog generation components including
power management, error handling, performance counters, and main generator.
"""

import os
import tempfile

import pytest

from src.advanced_sv_error import ErrorHandlingConfig, ErrorHandlingGenerator, ErrorType
from src.advanced_sv_perf import (
    DeviceType,
    PerformanceCounterConfig,
    PerformanceCounterGenerator,
)

# Import the modules to test
from src.advanced_sv_power import (
    PowerManagementConfig,
    PowerManagementGenerator,
    PowerState,
)
from src.manufacturing_variance import DeviceClass, ManufacturingVarianceSimulator
from src.systemverilog_generator import AdvancedSVGenerator, DeviceSpecificLogic


class TestPowerManagementGenerator:
    """Test the power management SystemVerilog generator."""

    def test_power_management_config_defaults(self):
        """Test default power management configuration."""
        config = PowerManagementConfig()
        assert PowerState.D0 in config.supported_power_states
        assert PowerState.D1 in config.supported_power_states
        assert PowerState.D3_HOT in config.supported_power_states
        assert config.enable_clock_gating is True
        assert config.enable_aspm is True

    def test_power_management_generator_init(self):
        """Test power management generator initialization."""
        config = PowerManagementConfig(enable_clock_gating=False)
        generator = PowerManagementGenerator(config)
        assert generator.config.enable_clock_gating is False

    def test_power_declarations_generation(self):
        """Test power management declarations generation."""
        generator = PowerManagementGenerator()
        declarations = generator.generate_power_declarations()

        assert "Power Management Signals" in declarations
        assert "current_power_state" in declarations
        assert "current_link_state" in declarations
        assert "power_transition_timer" in declarations
        assert "gated_clk" in declarations  # Clock gating enabled by default

    def test_power_state_machine_generation(self):
        """Test power state machine generation."""
        generator = PowerManagementGenerator()
        state_machine = generator.generate_power_state_machine()

        assert "Power Management State Machine" in state_machine
        assert "PM_D0_ACTIVE" in state_machine
        assert "PM_D1_STANDBY" in state_machine
        assert "PM_D3_SUSPEND" in state_machine
        assert "always_ff @(posedge clk" in state_machine

    def test_link_state_machine_generation(self):
        """Test link state machine generation."""
        config = PowerManagementConfig(enable_aspm=True)
        generator = PowerManagementGenerator(config)
        link_machine = generator.generate_link_state_machine()

        assert "Link Power State Management" in link_machine
        assert "LINK_L0" in link_machine
        assert "LINK_L0S" in link_machine
        assert "LINK_L1" in link_machine

    def test_clock_gating_generation(self):
        """Test clock gating logic generation."""
        config = PowerManagementConfig(enable_clock_gating=True)
        generator = PowerManagementGenerator(config)
        clock_gating = generator.generate_clock_gating()

        assert "Clock Gating for Power Management" in clock_gating
        assert "clock_enable" in clock_gating
        assert "gated_clk" in clock_gating

    def test_disabled_features(self):
        """Test generation with disabled features."""
        config = PowerManagementConfig(
            supported_power_states=[], enable_clock_gating=False, enable_aspm=False
        )
        generator = PowerManagementGenerator(config)

        state_machine = generator.generate_power_state_machine()
        assert "Power management disabled" in state_machine

        link_machine = generator.generate_link_state_machine()
        assert "Link power management disabled" in link_machine

        clock_gating = generator.generate_clock_gating()
        assert "Clock gating disabled" in clock_gating


class TestErrorHandlingGenerator:
    """Test the error handling SystemVerilog generator."""

    def test_error_handling_config_defaults(self):
        """Test default error handling configuration."""
        config = ErrorHandlingConfig()
        assert ErrorType.CORRECTABLE in config.supported_error_types
        assert ErrorType.UNCORRECTABLE_NON_FATAL in config.supported_error_types
        assert config.enable_ecc is True
        assert config.enable_parity_check is True
        assert config.max_retry_count == 3

    def test_error_declarations_generation(self):
        """Test error handling declarations generation."""
        generator = ErrorHandlingGenerator()
        declarations = generator.generate_error_declarations()

        assert "Error Handling Signals" in declarations
        assert "error_status" in declarations
        assert "correctable_error_count" in declarations
        assert "retry_count" in declarations
        assert "timeout_counter" in declarations

    def test_error_detection_generation(self):
        """Test error detection logic generation."""
        generator = ErrorHandlingGenerator()
        detection = generator.generate_error_detection()

        assert "Error Detection Logic" in detection
        assert "Timeout detection" in detection
        assert "Parity error detection" in detection
        assert "CRC error detection" in detection

    def test_error_state_machine_generation(self):
        """Test error state machine generation."""
        generator = ErrorHandlingGenerator()
        state_machine = generator.generate_error_state_machine()

        assert "Error Handling State Machine" in state_machine
        assert "ERR_NORMAL" in state_machine
        assert "ERR_DETECTED" in state_machine
        assert "ERR_RECOVERING" in state_machine
        assert "ERR_FATAL" in state_machine

    def test_error_logging_generation(self):
        """Test error logging generation."""
        config = ErrorHandlingConfig(enable_error_logging=True)
        generator = ErrorHandlingGenerator(config)
        logging = generator.generate_error_logging()

        assert "Error Logging Logic" in logging
        assert "error_log" in logging
        assert "error_log_ptr" in logging

    def test_error_injection_generation(self):
        """Test error injection generation."""
        config = ErrorHandlingConfig(enable_error_injection=True)
        generator = ErrorHandlingGenerator(config)
        injection = generator.generate_error_injection()

        assert "Error Injection Logic" in injection
        assert "injection_lfsr" in injection
        assert "inject_parity_error" in injection


class TestPerformanceCounterGenerator:
    """Test the performance counter SystemVerilog generator."""

    def test_perf_counter_config_defaults(self):
        """Test default performance counter configuration."""
        config = PerformanceCounterConfig()
        assert config.enable_transaction_counters is True
        assert config.enable_bandwidth_monitoring is True
        assert config.counter_width_bits == 32
        assert "rx_packets" in config.network_counters

    def test_perf_declarations_generation(self):
        """Test performance counter declarations generation."""
        generator = PerformanceCounterGenerator()
        declarations = generator.generate_perf_declarations()

        assert "Performance Counter Signals" in declarations
        assert "transaction_counter" in declarations
        assert "bandwidth_counter" in declarations
        assert "latency_accumulator" in declarations
        assert "performance_grade" in declarations

    def test_transaction_counters_generation(self):
        """Test transaction counter generation."""
        config = PerformanceCounterConfig(enable_transaction_counters=True)
        generator = PerformanceCounterGenerator(config)
        counters = generator.generate_transaction_counters()

        assert "Transaction Counting Logic" in counters
        assert "transaction_counter" in counters
        assert "bar_wr_en || bar_rd_en" in counters

    def test_bandwidth_monitoring_generation(self):
        """Test bandwidth monitoring generation."""
        config = PerformanceCounterConfig(enable_bandwidth_monitoring=True)
        generator = PerformanceCounterGenerator(config)
        bandwidth = generator.generate_bandwidth_monitoring()

        assert "Bandwidth Monitoring Logic" in bandwidth
        assert "bandwidth_counter" in bandwidth
        assert "perf_window_counter" in bandwidth

    def test_device_specific_counters(self):
        """Test device-specific counter generation."""
        # Test network controller
        config = PerformanceCounterConfig(enable_device_specific_counters=True)
        generator = PerformanceCounterGenerator(config, DeviceType.NETWORK_CONTROLLER)
        network_counters = generator.generate_device_specific_counters()

        assert "Network Controller Performance Counters" in network_counters
        assert "rx_packets" in network_counters
        assert "tx_packets" in network_counters

        # Test storage controller
        generator = PerformanceCounterGenerator(config, DeviceType.STORAGE_CONTROLLER)
        storage_counters = generator.generate_device_specific_counters()

        assert "Storage Controller Performance Counters" in storage_counters
        assert "read_ops" in storage_counters
        assert "write_ops" in storage_counters

    def test_performance_grading_generation(self):
        """Test performance grading generation."""
        generator = PerformanceCounterGenerator()
        grading = generator.generate_performance_grading()

        assert "Performance Grading Logic" in grading
        assert "performance_grade" in grading
        assert "high_latency_detected" in grading


class TestAdvancedSVGenerator:
    """Test the main advanced SystemVerilog generator."""

    def test_advanced_sv_generator_init(self):
        """Test advanced SystemVerilog generator initialization."""
        generator = AdvancedSVGenerator()
        assert generator.power_gen is not None
        assert generator.error_gen is not None
        assert generator.perf_gen is not None
        assert generator.variance_simulator is not None

    def test_module_header_generation(self):
        """Test module header generation."""
        device_config = DeviceSpecificLogic(device_type=DeviceType.NETWORK_CONTROLLER)
        generator = AdvancedSVGenerator(device_config=device_config)
        header = generator.generate_module_header()

        assert "advanced_pcileech_controller" in header
        assert "DEVICE_TYPE" in header
        assert "network" in header
        assert "input logic clk" in header
        assert "output logic correctable_error" in header

    def test_device_specific_ports(self):
        """Test device-specific port generation."""
        # Test network controller ports
        device_config = DeviceSpecificLogic(device_type=DeviceType.NETWORK_CONTROLLER)
        generator = AdvancedSVGenerator(device_config=device_config)
        ports = generator._generate_device_specific_ports()

        assert "Network controller ports" in ports
        assert "link_up" in ports
        assert "link_speed" in ports

        # Test storage controller ports
        device_config = DeviceSpecificLogic(device_type=DeviceType.STORAGE_CONTROLLER)
        generator = AdvancedSVGenerator(device_config=device_config)
        ports = generator._generate_device_specific_ports()

        assert "Storage controller ports" in ports
        assert "storage_ready" in ports
        assert "queue_depth" in ports

    def test_register_logic_generation(self):
        """Test register logic generation."""
        generator = AdvancedSVGenerator()

        # Sample register data
        regs = [
            {"name": "test_reg", "offset": "0x100", "value": "0x12345678", "rw": "rw"},
            {
                "name": "status_reg",
                "offset": "0x104",
                "value": "0x00000000",
                "rw": "ro",
            },
        ]

        register_logic = generator.generate_register_logic(regs, None)

        assert "Advanced Register Access Logic" in register_logic
        assert "test_reg_reg" in register_logic
        assert "status_reg_reg" in register_logic
        assert "register_access_timer" in register_logic

    def test_register_logic_with_variance(self):
        """Test register logic generation with variance model."""
        generator = AdvancedSVGenerator()

        # Create a variance model
        variance_simulator = ManufacturingVarianceSimulator()
        variance_model = variance_simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.CONSUMER,
            base_frequency_mhz=100.0,
        )

        regs = [
            {"name": "test_reg", "offset": "0x100", "value": "0x12345678", "rw": "rw"}
        ]

        register_logic = generator.generate_register_logic(regs, variance_model)

        assert "test_reg_reg" in register_logic
        assert "timing_counter" in register_logic
        assert "access_pending" in register_logic

    def test_read_logic_generation(self):
        """Test read logic generation."""
        generator = AdvancedSVGenerator()

        regs = [
            {"name": "test_reg", "offset": "0x100", "value": "0x12345678", "rw": "rw"},
            {
                "name": "status_reg",
                "offset": "0x104",
                "value": "0x00000000",
                "rw": "ro",
            },
        ]

        read_logic = generator.generate_read_logic(regs)

        assert "Main read logic with advanced features" in read_logic
        assert "32'h00000100: bar_rd_data = test_reg_reg" in read_logic
        assert "32'h00000104: bar_rd_data = status_reg_reg" in read_logic
        assert "Power management registers" in read_logic
        assert "Performance counter registers" in read_logic

    def test_interrupt_logic_generation(self):
        """Test interrupt logic generation."""
        generator = AdvancedSVGenerator()
        interrupt_logic = generator.generate_interrupt_logic()

        assert "Advanced Interrupt Handling" in interrupt_logic
        assert "interrupt_pending" in interrupt_logic
        assert "interrupt_vector" in interrupt_logic
        assert "interrupt_priority" in interrupt_logic
        assert "msi_request" in interrupt_logic

    def test_complete_systemverilog_generation(self):
        """Test complete SystemVerilog module generation."""
        generator = AdvancedSVGenerator()

        regs = [
            {
                "name": "control_reg",
                "offset": "0x100",
                "value": "0x00000000",
                "rw": "rw",
            },
            {
                "name": "status_reg",
                "offset": "0x104",
                "value": "0x00000001",
                "rw": "ro",
            },
        ]

        sv_content = generator.generate_advanced_systemverilog(regs)

        # Check for major sections
        assert "advanced_pcileech_controller" in sv_content
        assert "Power Management Signals" in sv_content
        assert "Error Handling Signals" in sv_content
        assert "Performance Counter Signals" in sv_content
        assert "Advanced Register Access Logic" in sv_content
        assert "endmodule" in sv_content
        assert "advanced_clock_crossing" in sv_content

    def test_systemverilog_with_all_features(self):
        """Test SystemVerilog generation with all features enabled."""
        from src.advanced_sv_error import ErrorHandlingConfig
        from src.advanced_sv_perf import PerformanceCounterConfig
        from src.advanced_sv_power import PowerManagementConfig

        power_config = PowerManagementConfig(
            enable_clock_gating=True, enable_aspm=True, enable_power_domains=True
        )

        error_config = ErrorHandlingConfig(
            enable_ecc=True,
            enable_parity_check=True,
            enable_crc_check=True,
            enable_error_logging=True,
            enable_error_injection=True,
        )

        perf_config = PerformanceCounterConfig(
            enable_transaction_counters=True,
            enable_bandwidth_monitoring=True,
            enable_latency_measurement=True,
            enable_error_rate_tracking=True,
            enable_device_specific_counters=True,
        )

        device_config = DeviceSpecificLogic(
            device_type=DeviceType.NETWORK_CONTROLLER,
            device_class=DeviceClass.ENTERPRISE,
        )

        generator = AdvancedSVGenerator(
            power_config, error_config, perf_config, device_config
        )

        regs = [
            {
                "name": "tx_control",
                "offset": "0x1000",
                "value": "0x00000000",
                "rw": "rw",
            },
            {
                "name": "rx_status",
                "offset": "0x2000",
                "value": "0x00000001",
                "rw": "ro",
            },
        ]

        sv_content = generator.generate_advanced_systemverilog(regs)

        # Verify all features are present
        assert "Clock Gating for Power Management" in sv_content
        assert "Error Injection Logic" in sv_content
        assert "Network Controller Performance Counters" in sv_content
        assert "tx_control_reg" in sv_content
        assert "rx_status_reg" in sv_content

    def test_generate_enhanced_build_integration(self):
        """Test generation of build.py integration code."""
        generator = AdvancedSVGenerator()
        integration_code = generator.generate_enhanced_build_integration()

        # Check for key components in the integration code
        assert "def build_advanced_sv" in integration_code
        assert "from .systemverilog_generator import" in integration_code
        assert "AdvancedSVGenerator" in integration_code
        assert "PowerManagementConfig" in integration_code
        assert "ErrorHandlingConfig" in integration_code
        assert "PerformanceCounterConfig" in integration_code
        assert "DeviceSpecificLogic" in integration_code
        assert "DeviceType" in integration_code
        assert "variance_model = None" in integration_code
        assert "if enable_variance:" in integration_code
        assert "generator = AdvancedSVGenerator" in integration_code
        assert (
            "sv_content = generator.generate_advanced_systemverilog" in integration_code
        )
        assert "write_text" in integration_code
        assert "shutil.copyfile" in integration_code

    def test_register_logic_with_special_names(self):
        """Test register logic generation with special register names."""
        generator = AdvancedSVGenerator()

        # Test with special register names
        regs = [
            {
                "name": "pcileech_tlps128_cfgspace_shadow_status",
                "offset": "0x100",
                "value": "0x00000000",
                "rw": "rw",
            },
            {
                "name": "register-with-dashes",
                "offset": "0x104",
                "value": "0x00000001",
                "rw": "ro",
            },
            {
                "name": "register_with_underscores",
                "offset": "0x108",
                "value": "0x00000002",
                "rw": "rw",
            },
            {
                "name": "UPPERCASE_REGISTER",
                "offset": "0x10C",
                "value": "0x00000003",
                "rw": "ro",
            },
        ]

        register_logic = generator.generate_register_logic(regs, None)

        # Check for special case handling of
        # pcileech_tlps128_cfgspace_shadow_status
        assert "pcileech_tlps128_cfgspace_shadow_status_reg = 32'h1" in register_logic

        # Check for other register names
        assert "register-with-dashes_reg" in register_logic
        assert "register_with_underscores_reg" in register_logic
        assert "UPPERCASE_REGISTER_reg" in register_logic

    def test_clock_domain_logic_with_variance(self):
        """Test clock domain logic generation with variance model."""
        generator = AdvancedSVGenerator()

        # Create a variance model
        variance_simulator = ManufacturingVarianceSimulator()
        variance_model = variance_simulator.generate_variance_model(
            device_id="test_device",
            device_class=DeviceClass.INDUSTRIAL,
            base_frequency_mhz=125.0,
        )

        clock_logic = generator.generate_clock_domain_logic(variance_model)

        # Check for clock domain management
        assert "Clock Domain Management" in clock_logic
        assert "clk_monitor_counter" in clock_logic
        assert "mem_clk_monitor_counter" in clock_logic
        assert "aux_clk_monitor_counter" in clock_logic
        assert "clock_domain_status" in clock_logic

    def test_device_type_class_combinations(self):
        """Test different combinations of device types and classes."""
        # Test all device types with ENTERPRISE class
        for device_type in DeviceType:
            device_config = DeviceSpecificLogic(
                device_type=device_type, device_class=DeviceClass.ENTERPRISE
            )
            generator = AdvancedSVGenerator(device_config=device_config)
            header = generator.generate_module_header()

            assert f'DEVICE_TYPE = "{device_type.value}"' in header
            assert 'DEVICE_CLASS = "enterprise"' in header

            # Check device-specific ports
            ports = generator._generate_device_specific_ports()
            if device_type == DeviceType.NETWORK_CONTROLLER:
                assert "Network controller ports" in ports
            elif device_type == DeviceType.STORAGE_CONTROLLER:
                assert "Storage controller ports" in ports
            elif device_type == DeviceType.GRAPHICS_CONTROLLER:
                assert "Graphics controller ports" in ports
            else:
                assert "Generic device ports" in ports

    def test_register_logic_with_invalid_values(self):
        """Test register logic generation with invalid register values."""
        generator = AdvancedSVGenerator()

        # Test with invalid register values
        regs = [
            {"name": "invalid_hex", "offset": "0x100", "value": "invalid", "rw": "rw"},
        ]

        # This should handle the errors gracefully or raise appropriate
        # exceptions
        with pytest.raises(ValueError):
            generator.generate_register_logic(regs, None)


class TestIntegration:
    """Integration tests for the advanced SystemVerilog generation system."""

    def test_file_generation(self):
        """Test that SystemVerilog files can be generated and written."""
        generator = AdvancedSVGenerator()

        regs = [
            {"name": "test_reg", "offset": "0x100", "value": "0x12345678", "rw": "rw"}
        ]

        sv_content = generator.generate_advanced_systemverilog(regs)

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sv", delete=False) as f:
            f.write(sv_content)
            temp_path = f.name

        try:
            # Verify file was written and contains expected content
            with open(temp_path, "r") as f:
                content = f.read()

            assert "module advanced_pcileech_controller" in content
            assert "endmodule" in content
            assert len(content) > 1000  # Should be substantial content

        finally:
            # Clean up
            os.unlink(temp_path)

    def test_variance_integration(self):
        """Test integration with manufacturing variance simulation."""
        generator = AdvancedSVGenerator()

        # Create variance model
        variance_simulator = ManufacturingVarianceSimulator()
        variance_model = variance_simulator.generate_variance_model(
            device_id="integration_test",
            device_class=DeviceClass.INDUSTRIAL,
            base_frequency_mhz=125.0,
        )

        regs = [
            {"name": "test_reg", "offset": "0x100", "value": "0x12345678", "rw": "rw"}
        ]

        sv_content = generator.generate_advanced_systemverilog(regs, variance_model)

        # Should contain variance-aware timing logic
        assert "timing_counter" in sv_content
        assert "access_pending" in sv_content


class TestDeviceSpecificLogic:
    """Test the DeviceSpecificLogic configuration class."""

    def test_device_specific_logic_defaults(self):
        """Test default values for DeviceSpecificLogic."""
        config = DeviceSpecificLogic()
        assert config.device_type == DeviceType.GENERIC
        assert config.device_class == DeviceClass.CONSUMER
        assert config.max_payload_size == 256
        assert config.max_read_request_size == 512
        assert config.msi_vectors == 1
        assert config.msix_vectors == 0
        assert config.enable_dma is False
        assert config.tx_queue_depth == 256
        assert config.rx_queue_depth == 256
        assert config.base_frequency_mhz == 100.0

    def test_device_specific_logic_custom_values(self):
        """Test custom values for DeviceSpecificLogic."""
        config = DeviceSpecificLogic(
            device_type=DeviceType.NETWORK_CONTROLLER,
            device_class=DeviceClass.ENTERPRISE,
            max_payload_size=512,
            max_read_request_size=1024,
            msi_vectors=4,
            msix_vectors=16,
            enable_dma=True,
            enable_interrupt_coalescing=True,
            tx_queue_depth=512,
            rx_queue_depth=512,
            base_frequency_mhz=250.0,
        )
        assert config.device_type == DeviceType.NETWORK_CONTROLLER
        assert config.device_class == DeviceClass.ENTERPRISE
        assert config.max_payload_size == 512
        assert config.max_read_request_size == 1024
        assert config.msi_vectors == 4
        assert config.msix_vectors == 16
        assert config.enable_dma is True
        assert config.enable_interrupt_coalescing is True
        assert config.tx_queue_depth == 512
        assert config.rx_queue_depth == 512
        assert config.base_frequency_mhz == 250.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
