#!/usr/bin/env python3
"""
Templated SystemVerilog Generator

This module provides a templated approach to SystemVerilog generation,
integrating all the advanced SystemVerilog generation components
(power management, error handling, performance counters) into a cohesive
advanced PCIe device controller using Jinja2 templates.

Advanced SystemVerilog Generation feature for the PCILeechFWGenerator project.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import template renderer
try:
    from .template_renderer import TemplateRenderer, TemplateRenderError
except ImportError:
    from .template_renderer import TemplateRenderer, TemplateRenderError

# Import string utilities for safe formatting
try:
    from ..string_utils import (
        generate_sv_header_comment,
        log_error_safe,
        log_info_safe,
        log_warning_safe,
    )
except ImportError:
    from string_utils import (
        generate_sv_header_comment,
        log_error_safe,
        log_info_safe,
        log_warning_safe,
    )

# Import advanced components for integration
try:
    from .advanced_sv_error import ErrorHandlingConfig, ErrorHandlingGenerator
    from .advanced_sv_perf import (
        DeviceType,
        PerformanceCounterConfig,
        PerformanceCounterGenerator,
    )
    from .advanced_sv_power import PowerManagementConfig, PowerManagementGenerator
    from ..device_clone.manufacturing_variance import (
        DeviceClass,
        ManufacturingVarianceSimulator,
        VarianceModel,
    )
except ImportError:
    from .advanced_sv_error import ErrorHandlingConfig, ErrorHandlingGenerator
    from .advanced_sv_perf import (
        DeviceType,
        PerformanceCounterConfig,
        PerformanceCounterGenerator,
    )
    from .advanced_sv_power import PowerManagementConfig, PowerManagementGenerator
    from ..device_clone.manufacturing_variance import (
        DeviceClass,
        ManufacturingVarianceSimulator,
        VarianceModel,
    )


@dataclass
class DeviceSpecificLogic:
    """Configuration for device-specific logic generation."""

    device_type: DeviceType = DeviceType.GENERIC
    device_class: DeviceClass = DeviceClass.CONSUMER

    # Device capabilities
    max_payload_size: int = 256
    max_read_request_size: int = 512
    msi_vectors: int = 1
    msix_vectors: int = 0

    # Device-specific features
    enable_dma: bool = False
    enable_interrupt_coalescing: bool = False
    enable_virtualization: bool = False
    enable_sr_iov: bool = False

    # Queue management
    tx_queue_depth: int = 256
    rx_queue_depth: int = 256
    command_queue_depth: int = 64

    # Buffer sizes
    tx_buffer_size_kb: int = 64
    rx_buffer_size_kb: int = 64

    # Timing characteristics
    base_frequency_mhz: float = 100.0
    memory_frequency_mhz: float = 200.0


@dataclass
class PCILeechOutput:
    """Configuration for PCILeech-specific output management."""

    src_dir: str = "src"
    ip_dir: str = "ip"
    use_pcileech_structure: bool = True
    generate_explicit_file_lists: bool = True

    # File organization
    systemverilog_files: Optional[List[str]] = None
    ip_core_files: Optional[List[str]] = None
    coefficient_files: Optional[List[str]] = None
    constraint_files: Optional[List[str]] = None

    def __post_init__(self):
        """Initialize file lists if not provided."""
        if self.systemverilog_files is None:
            self.systemverilog_files = []
        if self.ip_core_files is None:
            self.ip_core_files = []
        if self.coefficient_files is None:
            self.coefficient_files = []
        if self.constraint_files is None:
            self.constraint_files = []


class AdvancedSVGenerator:
    """Main advanced SystemVerilog generator with PCILeech as primary generation path."""

    def __init__(
        self,
        power_config: Optional[PowerManagementConfig] = None,
        error_config: Optional[ErrorHandlingConfig] = None,
        perf_config: Optional[PerformanceCounterConfig] = None,
        device_config: Optional[DeviceSpecificLogic] = None,
        template_dir: Optional[Path] = None,
        use_pcileech_primary: bool = True,
    ):
        """Initialize the advanced SystemVerilog generator with PCILeech as primary path."""

        self.power_config = power_config or PowerManagementConfig()
        self.error_config = error_config or ErrorHandlingConfig()
        self.perf_config = perf_config or PerformanceCounterConfig()
        self.device_config = device_config or DeviceSpecificLogic()
        self.use_pcileech_primary = use_pcileech_primary

        # Initialize template renderer
        self.renderer = TemplateRenderer(template_dir)

        # Initialize component generators
        self.power_gen = PowerManagementGenerator(self.power_config)
        self.error_gen = ErrorHandlingGenerator(self.error_config)
        self.perf_gen = PerformanceCounterGenerator(
            self.perf_config, self.device_config.device_type
        )

        # Initialize variance simulator for realistic timing
        self.variance_simulator = ManufacturingVarianceSimulator()

        # Set up logger
        self.logger = logging.getLogger(__name__)

        log_info_safe(
            self.logger,
            "AdvancedSVGenerator initialized with PCILeech primary: {primary}",
            primary=self.use_pcileech_primary,
        )

    def generate_device_specific_ports(self) -> str:
        """Generate device-specific port declarations using template."""
        context = {
            "device_config": self.device_config,
        }

        try:
            return self.renderer.render_template(
                "systemverilog/components/device_specific_ports.sv.j2", context
            )
        except TemplateRenderError as e:
            self.logger.error(f"Failed to render device-specific ports: {e}")
            return "// Error generating device-specific ports"

    def generate_systemverilog_modules(
        self, template_context: Dict[str, Any], behavior_profile: Optional[Any] = None
    ) -> Dict[str, str]:
        """
        Primary SystemVerilog generation method with PCILeech as default path.

        Args:
            template_context: Template context from PCILeech or legacy sources
            behavior_profile: Optional behavior profile for advanced features

        Returns:
            Dictionary mapping module names to generated SystemVerilog code
        """
        if self.use_pcileech_primary:
            log_info_safe(
                self.logger, "Using PCILeech as primary SystemVerilog generation path"
            )
            return self.generate_pcileech_modules(template_context, behavior_profile)
        else:
            log_info_safe(self.logger, "Using legacy SystemVerilog generation path")
            return self._generate_legacy_modules(template_context, behavior_profile)

    def _generate_legacy_modules(
        self, template_context: Dict[str, Any], behavior_profile: Optional[Any] = None
    ) -> Dict[str, str]:
        """Generate SystemVerilog modules using legacy generation path."""
        modules = {}

        try:
            # Extract register definitions for legacy compatibility
            registers = template_context.get("registers", [])

            # Generate advanced SystemVerilog if behavior profile is available
            if behavior_profile:
                advanced_sv = self.generate_advanced_systemverilog(
                    regs=registers,
                    variance_model=getattr(behavior_profile, "variance_metadata", None),
                )
                modules["advanced_controller"] = advanced_sv

            # Generate basic modules using templates
            basic_modules = [
                "bar_controller.sv.j2",
                "cfg_shadow.sv.j2",
                "device_config.sv.j2",
                "msix_capability_registers.sv.j2",
                "msix_implementation.sv.j2",
                "msix_table.sv.j2",
                "option_rom_bar_window.sv.j2",
                "option_rom_spi_flash.sv.j2",
                "top_level_wrapper.sv.j2",
            ]

            for module_template in basic_modules:
                try:
                    module_content = self.renderer.render_template(
                        f"systemverilog/{module_template}", template_context
                    )
                    module_name = module_template.replace(".sv.j2", "")
                    modules[module_name] = module_content

                except Exception as e:
                    log_warning_safe(
                        self.logger,
                        "Failed to generate legacy module {module}: {error}",
                        module=module_template,
                        error=str(e),
                    )

            log_info_safe(
                self.logger,
                "Generated {count} legacy SystemVerilog modules",
                count=len(modules),
            )

        except Exception as e:
            log_error_safe(
                self.logger,
                "Legacy SystemVerilog generation failed: {error}",
                error=str(e),
            )

        return modules

    def generate_advanced_systemverilog(
        self, regs: List[Dict], variance_model: Optional[VarianceModel] = None
    ) -> str:
        """Generate comprehensive advanced SystemVerilog module using templates."""

        # Generate header comment
        header = generate_sv_header_comment(
            "Advanced PCIe Device Controller with Comprehensive Features",
            generator="AdvancedSVGenerator - Advanced SystemVerilog Generation Feature",
            device_type=self.device_config.device_type.value,
            device_class=self.device_config.device_class.value,
            features="Advanced power management (D0-D3, L0-L3 states), Comprehensive error handling and recovery, Hardware performance counters, Multiple clock domain support, Manufacturing variance integration",
        )

        # Generate device-specific ports
        device_specific_ports = self.generate_device_specific_ports()

        # Prepare template context
        context = {
            "header": header,
            "device_config": self.device_config,
            "power_config": self.power_config,
            "error_config": self.error_config,
            "perf_config": self.perf_config,
            "registers": regs,
            "variance_model": variance_model,
            "device_specific_ports": device_specific_ports,
            # Pass the config objects, not the generated strings
            "power_management": self.power_config if self.power_config else None,
            "error_handling": self.error_config if self.error_config else None,
            "performance_counters": self.perf_config if self.perf_config else None,
        }

        try:
            # Render main advanced controller template
            main_module = self.renderer.render_template(
                "systemverilog/advanced/advanced_controller.sv.j2", context
            )

            # Render clock crossing module
            clock_crossing_header = generate_sv_header_comment(
                "Advanced Clock Domain Crossing Module",
                generator="AdvancedSVGenerator - Clock Domain Crossing",
            )

            clock_crossing_context = {
                "header": clock_crossing_header,
            }

            clock_crossing_module = self.renderer.render_template(
                "systemverilog/advanced/clock_crossing.sv.j2", clock_crossing_context
            )

            # Combine modules
            return f"{main_module}\n\n{clock_crossing_module}"

        except TemplateRenderError as e:
            log_error_safe(
                self.logger,
                "Failed to render SystemVerilog template: {error}",
                error=e,
            )
            raise

    def generate_enhanced_build_integration(self) -> str:
        """Generate integration code for build.py enhancement using template."""

        context = {
            # No context variables needed for this template as it's static Python code
        }

        try:
            return self.renderer.render_template(
                "python/build_integration.py.j2", context
            )
        except TemplateRenderError as e:
            log_error_safe(
                self.logger,
                "Failed to render build integration template: {error}",
                error=e,
            )
            raise

    def generate_pcileech_modules(
        self, template_context: Dict[str, Any], behavior_profile: Optional[Any] = None
    ) -> Dict[str, str]:
        """
        Generate PCILeech-specific SystemVerilog modules with dynamic context.

        Args:
            template_context: Template context from PCILeechContextBuilder
            behavior_profile: Optional behavior profile for advanced features

        Returns:
            Dictionary mapping module names to generated SystemVerilog code

        Raises:
            TemplateRenderError: If template rendering fails
        """
        log_info_safe(self.logger, "Generating PCILeech SystemVerilog modules")

        modules = {}

        try:
            # Generate PCILeech TLP BAR controller
            modules["pcileech_tlps128_bar_controller"] = self.renderer.render_template(
                "systemverilog/pcileech_tlps128_bar_controller.sv.j2", template_context
            )

            # Generate PCILeech FIFO controller
            modules["pcileech_fifo"] = self.renderer.render_template(
                "systemverilog/pcileech_fifo.sv.j2", template_context
            )

            # Generate configuration space COE file
            modules["pcileech_cfgspace_coe"] = self.renderer.render_template(
                "systemverilog/pcileech_cfgspace.coe.j2", template_context
            )

            # Generate advanced modules if behavior profile is available
            if behavior_profile and template_context.get("device_config", {}).get(
                "enable_advanced_features"
            ):
                advanced_modules = self._generate_pcileech_advanced_modules(
                    template_context, behavior_profile
                )
                modules.update(advanced_modules)

            log_info_safe(
                self.logger,
                "Generated {count} PCILeech SystemVerilog modules",
                count=len(modules),
            )

            return modules

        except TemplateRenderError as e:
            log_error_safe(
                self.logger,
                "PCILeech SystemVerilog generation failed: {error}",
                error=str(e),
            )
            raise

    def _generate_pcileech_advanced_modules(
        self, template_context: Dict[str, Any], behavior_profile: Any
    ) -> Dict[str, str]:
        """Generate advanced PCILeech modules based on behavior profile."""
        advanced_modules = {}

        try:
            # Extract register definitions from behavior profile
            registers = self._extract_pcileech_registers(behavior_profile)

            # Get variance model if available
            variance_model = None
            if (
                hasattr(behavior_profile, "variance_metadata")
                and behavior_profile.variance_metadata
            ):
                variance_model = behavior_profile.variance_metadata

            # Generate advanced controller with PCILeech integration
            pcileech_context = template_context.copy()
            pcileech_context.update(
                {
                    "registers": registers,
                    "variance_model": variance_model,
                    "pcileech_integration": True,
                    "behavior_profile": behavior_profile,
                }
            )

            advanced_modules["pcileech_advanced_controller"] = (
                self.generate_advanced_systemverilog(
                    regs=registers, variance_model=variance_model
                )
            )

        except Exception as e:
            log_warning_safe(
                self.logger,
                "Advanced PCILeech module generation failed: {error}",
                error=str(e),
            )

        return advanced_modules

    def _extract_pcileech_registers(self, behavior_profile: Any) -> List[Dict]:
        """Extract register definitions from behavior profile for PCILeech."""
        registers = []

        if hasattr(behavior_profile, "register_accesses"):
            # Group register accesses by register name
            register_map = {}
            for access in behavior_profile.register_accesses:
                reg_name = access.register if hasattr(access, "register") else "UNKNOWN"
                if reg_name not in register_map:
                    register_map[reg_name] = {
                        "name": reg_name,
                        "offset": getattr(access, "offset", 0),
                        "size": 32,  # Default to 32-bit
                        "access_count": 0,
                        "read_count": 0,
                        "write_count": 0,
                        "access_type": "rw",
                    }

                register_map[reg_name]["access_count"] += 1
                if hasattr(access, "operation"):
                    if access.operation == "read":
                        register_map[reg_name]["read_count"] += 1
                    elif access.operation == "write":
                        register_map[reg_name]["write_count"] += 1

            # Convert to list and determine access types
            for reg_info in register_map.values():
                if reg_info["write_count"] == 0:
                    reg_info["access_type"] = "ro"
                elif reg_info["read_count"] == 0:
                    reg_info["access_type"] = "wo"
                else:
                    reg_info["access_type"] = "rw"

                registers.append(reg_info)

        # Add default PCILeech registers if none found
        if not registers:
            registers = [
                {
                    "name": "PCILEECH_CTRL",
                    "offset": 0x00,
                    "size": 32,
                    "access_type": "rw",
                },
                {
                    "name": "PCILEECH_STATUS",
                    "offset": 0x04,
                    "size": 32,
                    "access_type": "ro",
                },
                {
                    "name": "PCILEECH_ADDR_LO",
                    "offset": 0x08,
                    "size": 32,
                    "access_type": "rw",
                },
                {
                    "name": "PCILEECH_ADDR_HI",
                    "offset": 0x0C,
                    "size": 32,
                    "access_type": "rw",
                },
                {
                    "name": "PCILEECH_LENGTH",
                    "offset": 0x10,
                    "size": 32,
                    "access_type": "rw",
                },
                {
                    "name": "PCILEECH_DATA",
                    "offset": 0x14,
                    "size": 32,
                    "access_type": "rw",
                },
            ]

        return registers

    def generate_pcileech_integration_code(
        self, template_context: Dict[str, Any]
    ) -> str:
        """
        Generate PCILeech integration code for existing build system.

        Args:
            template_context: Template context data

        Returns:
            Python integration code for build system
        """
        try:
            # Enhance context with PCILeech-specific build parameters
            build_context = template_context.copy()
            build_context.update(
                {
                    "pcileech_modules": [
                        "pcileech_tlps128_bar_controller",
                        "pcileech_fifo",
                        "pcileech_cfgspace_coe",
                    ],
                    "integration_type": "pcileech",
                    "build_system_version": "2.0",
                }
            )

            return self.renderer.render_template(
                "python/pcileech_build_integration.py.j2", build_context
            )

        except TemplateRenderError:
            # Fallback to base build integration
            return self.generate_enhanced_build_integration()
