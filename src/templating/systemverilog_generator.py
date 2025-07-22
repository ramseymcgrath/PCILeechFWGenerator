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
    from ..device_clone.manufacturing_variance import (
        DeviceClass,
        ManufacturingVarianceSimulator,
        VarianceModel,
    )
    from .advanced_sv_error import ErrorHandlingConfig, ErrorHandlingGenerator
    from .advanced_sv_perf import (
        DeviceType,
        PerformanceCounterConfig,
        PerformanceCounterGenerator,
    )
    from .advanced_sv_power import PowerManagementConfig, PowerManagementGenerator
except ImportError:
    from ..device_clone.manufacturing_variance import (
        DeviceClass,
        ManufacturingVarianceSimulator,
        VarianceModel,
    )
    from .advanced_sv_error import ErrorHandlingConfig, ErrorHandlingGenerator
    from .advanced_sv_perf import (
        DeviceType,
        PerformanceCounterConfig,
        PerformanceCounterGenerator,
    )
    from .advanced_sv_power import PowerManagementConfig, PowerManagementGenerator


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
                "top_level_wrapper.sv.j2",  # Essential for Vivado top module
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
            # Add missing template variables for PCILeech modules
            enhanced_context = template_context.copy()

            # Extract device config for easier access
            device_config = template_context.get("device_config", {})

            # Generate header comment for SystemVerilog files
            try:
                from ..string_utils import generate_sv_header_comment

                header = generate_sv_header_comment(
                    "PCILeech SystemVerilog Module",
                    generator="PCILeechFWGenerator - SystemVerilog Generation",
                    device_type="PCIe Device Controller",
                    features="PCILeech integration, MSI-X support, BAR controller",
                )
            except ImportError:
                header = "// PCILeech SystemVerilog Module\n// Generated by PCILeechFWGenerator"

            # Create device object for template compatibility
            device_info = {
                "vendor_id": device_config.get("vendor_id", "0000"),
                "device_id": device_config.get("device_id", "0000"),
                "subsys_vendor_id": device_config.get("subsystem_vendor_id", "0000"),
                "subsys_device_id": device_config.get("subsystem_device_id", "0000"),
                "class_code": device_config.get("class_code", "020000"),
                "revision_id": device_config.get("revision_id", "01"),
            }

            enhanced_context.update(
                {
                    "header": header,  # Add header for template
                    "device": device_info,
                    "config_space": {
                        "vendor_id": device_config.get("vendor_id", "0000"),
                        "device_id": device_config.get("device_id", "0000"),
                        "class_code": device_config.get("class_code", "020000"),
                        "revision_id": device_config.get("revision_id", "01"),
                    },
                    "enable_custom_config": True,
                    "enable_scatter_gather": getattr(
                        self.device_config, "enable_dma", True
                    ),
                    "enable_interrupt": template_context.get(
                        "interrupt_config", {}
                    ).get("vectors", 0)
                    > 0,
                    "enable_clock_crossing": True,
                    "enable_performance_counters": getattr(
                        self.perf_config, "enable_transaction_counters", True
                    ),
                    "enable_error_detection": getattr(
                        self.error_config, "enable_ecc", True
                    ),
                    "fifo_type": "block_ram",
                    "fifo_depth": 512,
                    "data_width": 128,
                    "fpga_family": "artix7",
                    "vendor_id": device_config.get("vendor_id", "0000"),
                    "device_id": device_config.get("device_id", "0000"),
                    "vendor_id_hex": device_config.get("vendor_id", "0000"),
                    "device_id_hex": device_config.get("device_id", "0000"),
                    "device_specific_config": {},
                }
            )

            # Add enable_advanced_features to device_config section if it doesn't exist
            if "device_config" in enhanced_context and isinstance(
                enhanced_context["device_config"], dict
            ):
                enhanced_context["device_config"]["enable_advanced_features"] = getattr(
                    self.error_config, "enable_ecc", True
                )

            # Generate PCILeech TLP BAR controller
            modules["pcileech_tlps128_bar_controller"] = self.renderer.render_template(
                "systemverilog/pcileech_tlps128_bar_controller.sv.j2", enhanced_context
            )

            # Generate PCILeech FIFO controller
            modules["pcileech_fifo"] = self.renderer.render_template(
                "systemverilog/pcileech_fifo.sv.j2", enhanced_context
            )

            # Generate top-level wrapper (CRITICAL for Vivado top module)
            try:
                modules["top_level_wrapper"] = self.renderer.render_template(
                    "systemverilog/top_level_wrapper.sv.j2", enhanced_context
                )
            except TemplateRenderError:
                # Try alternative path
                try:
                    modules["top_level_wrapper"] = self.renderer.render_template(
                        "sv/top_level_wrapper.sv.j2", enhanced_context
                    )
                except TemplateRenderError as e:
                    log_warning_safe(
                        self.logger,
                        "Failed to generate top_level_wrapper from both paths: {error}",
                        error=str(e),
                    )
                    # Generate a basic top-level wrapper as fallback
                    modules["top_level_wrapper"] = self._generate_basic_top_wrapper(
                        enhanced_context
                    )

            # Generate configuration space COE file
            modules["pcileech_cfgspace.coe"] = self.renderer.render_template(
                "systemverilog/pcileech_cfgspace.coe.j2", enhanced_context
            )

            # Always generate MSI-X modules if MSI-X is supported
            msix_config = template_context.get("msix_config", {})
            if (
                msix_config.get("is_supported", False)
                or msix_config.get("num_vectors", 0) > 0
            ):
                log_info_safe(self.logger, "Generating MSI-X modules")

                # Create MSI-X specific template context
                msix_template_context = enhanced_context.copy()
                msix_template_context.update(msix_config)

                # Generate MSI-X capability registers
                modules["msix_capability_registers"] = self.renderer.render_template(
                    "systemverilog/msix_capability_registers.sv.j2",
                    msix_template_context,
                )

                # Generate MSI-X implementation
                modules["msix_implementation"] = self.renderer.render_template(
                    "systemverilog/msix_implementation.sv.j2", msix_template_context
                )

                # Generate MSI-X table
                modules["msix_table"] = self.renderer.render_template(
                    "systemverilog/msix_table.sv.j2", msix_template_context
                )

                # Generate MSI-X initialization files
                modules["msix_pba_init.hex"] = self._generate_msix_pba_init(
                    enhanced_context
                )
                modules["msix_table_init.hex"] = self._generate_msix_table_init(
                    enhanced_context
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

    def _generate_msix_pba_init(self, template_context: Dict[str, Any]) -> str:
        """
        Generate MSI-X PBA initialization file.

        Args:
            template_context: Template context data

        Returns:
            Hex file content for MSI-X PBA initialization
        """
        msix_config = template_context.get("msix_config", {})
        num_vectors = msix_config.get("num_vectors", 1)

        # Calculate PBA size in DWORDs
        pba_size = (num_vectors + 31) // 32

        # Generate PBA initialization data (all zeros initially)
        hex_lines = []
        for i in range(pba_size):
            hex_lines.append("00000000")

        return "\n".join(hex_lines) + "\n"

    def _generate_msix_table_init(self, template_context: Dict[str, Any]) -> str:
        """
        Generate MSI-X table initialization file.

        Args:
            template_context: Template context data

        Returns:
            Hex file content for MSI-X table initialization
        """
        msix_config = template_context.get("msix_config", {})
        num_vectors = msix_config.get("num_vectors", 1)

        # Try to read actual MSI-X table from hardware first
        try:
            actual_table_data = self._read_actual_msix_table(template_context)
            if actual_table_data:
                log_info_safe(
                    self.logger,
                    "Using actual MSI-X table data from hardware ({entries} entries)",
                    entries=len(actual_table_data) // 4,
                )
                return "\n".join(f"{value:08X}" for value in actual_table_data) + "\n"
        except Exception as e:
            log_warning_safe(
                self.logger,
                "Failed to read actual MSI-X table, using default values: {error}",
                error=str(e),
            )

        # Fallback to default initialization values
        log_info_safe(
            self.logger,
            "Generating default MSI-X table initialization for {vectors} vectors",
            vectors=num_vectors,
        )

        # Each MSI-X table entry is 4 DWORDs:
        # - DWORD 0: Message Address Low
        # - DWORD 1: Message Address High
        # - DWORD 2: Message Data
        # - DWORD 3: Vector Control (bit 0 = mask)

        hex_lines = []
        for vector in range(num_vectors):
            # Default values for each entry
            hex_lines.append("00000000")  # Message Address Low
            hex_lines.append("00000000")  # Message Address High
            hex_lines.append(f"{vector:08X}")  # Message Data (use vector number)
            hex_lines.append("00000001")  # Vector Control (masked initially)

        return "\n".join(hex_lines) + "\n"

    def _read_actual_msix_table(
        self, template_context: Dict[str, Any]
    ) -> Optional[List[int]]:
        """
        Read actual MSI-X table data from hardware via VFIO.

        Args:
            template_context: Template context data

        Returns:
            List of 32-bit values from MSI-X table, or None if failed
        """
        try:
            import mmap
            import os

            from ..cli.vfio_helpers import get_device_fd

            msix_config = template_context.get("msix_config", {})
            bar_config = template_context.get("bar_config", {})

            table_bir = msix_config.get("table_bir", 0)
            table_offset = msix_config.get("table_offset", 0)
            num_vectors = msix_config.get("num_vectors", 0)

            if num_vectors == 0:
                return None

            # Find the appropriate BAR
            bars = bar_config.get("bars", [])

            # Debug: Log all available BARs
            log_info_safe(
                self.logger,
                "Available BARs for MSI-X table lookup: {bars}",
                bars=[
                    {
                        "index": getattr(
                            bar,
                            "index",
                            getattr(bar, "get", lambda x: "unknown")("index"),
                        ),
                        "size": getattr(
                            bar,
                            "size",
                            getattr(bar, "get", lambda x: "unknown")("size"),
                        ),
                        "type": type(bar).__name__,
                    }
                    for bar in bars
                ],
            )
            log_info_safe(
                self.logger,
                "Looking for BAR {bir} for MSI-X table access",
                bir=table_bir,
            )

            target_bar = None
            # First try direct BIR match
            for bar in bars:
                bar_index = getattr(bar, "index", None)
                if bar_index is None and hasattr(bar, "get"):
                    bar_index = bar.get("index")

                if bar_index == table_bir:
                    target_bar = bar
                    log_info_safe(
                        self.logger,
                        "Found direct BAR match: BIR {bir} -> BAR {index}",
                        bir=table_bir,
                        index=bar_index,
                    )
                    break

            # If no direct match, try to find the BAR by analyzing the actual BAR layout
            if not target_bar and bars:
                # Try to find the actual physical BAR by examining configuration space
                # Look for a BAR that contains the MSI-X table offset
                log_info_safe(
                    self.logger,
                    "No direct BIR match found, analyzing BAR layout for MSI-X table",
                )

                # Get the original config space data to understand the real BAR mapping
                config_space_data = template_context.get("config_space_data", {})
                original_bars = config_space_data.get("device_info", {}).get("bars", [])

                # Also try the top-level bars if device_info.bars is empty
                if not original_bars:
                    original_bars = config_space_data.get("bars", [])

                log_info_safe(
                    self.logger,
                    "Original config space BARs: {bars}",
                    bars=[(i, str(bar)) for i, bar in enumerate(original_bars)],
                )

                # Find which original BAR corresponds to our target BIR
                target_original_bar = None
                if table_bir < len(original_bars):
                    target_original_bar = original_bars[table_bir]
                    log_info_safe(
                        self.logger,
                        "Target original BAR {bir}: {bar}",
                        bir=table_bir,
                        bar=str(target_original_bar),
                    )

                # Try to match by address if we have the original BAR info
                if target_original_bar:
                    target_address = None
                    if hasattr(target_original_bar, "address"):
                        target_address = target_original_bar.address
                    elif isinstance(target_original_bar, dict):
                        target_address = target_original_bar.get("address")

                    if target_address:
                        # Find VFIO BAR with matching address
                        for i, bar in enumerate(bars):
                            bar_address = getattr(bar, "base_address", None)
                            if bar_address == target_address:
                                target_bar = bar
                                log_info_safe(
                                    self.logger,
                                    "Matched BAR by address: physical BAR {bir} (0x{addr:x}) -> VFIO region {region}",
                                    bir=table_bir,
                                    addr=target_address,
                                    region=i,
                                )
                                break

                # If still no match, try to use the available memory BARs
                if not target_bar:
                    memory_bars = []
                    for i, bar in enumerate(bars):
                        is_memory = getattr(bar, "is_memory", False)
                        size = getattr(bar, "size", 0)
                        if is_memory and size > 0:
                            memory_bars.append((i, bar))

                    if memory_bars:
                        # Use the largest memory BAR as fallback
                        largest_bar = max(
                            memory_bars, key=lambda x: getattr(x[1], "size", 0)
                        )
                        target_bar = largest_bar[1]
                        log_warning_safe(
                            self.logger,
                            "Using largest memory BAR as fallback for MSI-X table: region {region}, size {size}",
                            region=largest_bar[0],
                            size=getattr(target_bar, "size", 0),
                        )

            if not target_bar:
                log_warning_safe(
                    self.logger,
                    "Could not find BAR {bir} for MSI-X table access",
                    bir=table_bir,
                )
                return None

            # Get VFIO device file descriptor
            device_fd, container_fd = get_device_fd(
                template_context["device_config"]["device_bdf"]
            )

            try:
                # Map the BAR region containing MSI-X table
                bar_size = getattr(target_bar, "size", None)
                if bar_size is None and hasattr(target_bar, "get"):
                    bar_size = target_bar.get("size", 4096)
                if bar_size is None:
                    bar_size = 4096  # Default fallback

                table_size_bytes = num_vectors * 16  # 16 bytes per entry

                if table_offset + table_size_bytes > bar_size:
                    log_warning_safe(
                        self.logger,
                        "MSI-X table extends beyond BAR boundary (offset=0x{offset:x}, size={size}, bar_size={bar_size})",
                        offset=table_offset,
                        size=table_size_bytes,
                        bar_size=bar_size,
                    )
                    return None

                # Memory map the BAR region
                # Use VFIO region index directly instead of calculating offset
                try:
                    with mmap.mmap(
                        device_fd, bar_size, mmap.MAP_SHARED, mmap.PROT_READ
                    ) as mm:

                        # Read MSI-X table entries
                        table_data = []
                        for i in range(num_vectors * 4):  # 4 DWORDs per entry
                            offset = table_offset + (i * 4)
                            if offset + 4 <= len(mm):
                                # Read 32-bit value in little-endian format
                                value = int.from_bytes(
                                    mm[offset : offset + 4], byteorder="little"
                                )
                                table_data.append(value)
                            else:
                                log_warning_safe(
                                    self.logger,
                                    "MSI-X table read beyond mapped region at offset 0x{offset:x}",
                                    offset=offset,
                                )
                                break

                        log_info_safe(
                            self.logger,
                            "Successfully read {count} DWORDs from actual MSI-X table",
                            count=len(table_data),
                        )

                        return table_data

                except OSError as e:
                    if e.errno == 22:  # EINVAL
                        log_warning_safe(
                            self.logger,
                            "mmap failed with EINVAL - BAR may not be mappable or accessible",
                        )
                    else:
                        log_warning_safe(
                            self.logger,
                            "mmap failed: [Errno {errno}] {error}",
                            errno=e.errno,
                            error=str(e),
                        )
                    return None

            finally:
                os.close(device_fd)
                os.close(container_fd)

        except Exception as e:
            log_warning_safe(
                self.logger,
                "Exception while reading actual MSI-X table: {error}",
                error=str(e),
            )
            return None

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
                    "build_system_version": "0.7.3",
                }
            )

            return self.renderer.render_template(
                "python/pcileech_build_integration.py.j2", build_context
            )

        except TemplateRenderError:
            # Fallback to base build integration
            return self.generate_enhanced_build_integration()

    def _generate_basic_top_wrapper(self, context: Dict[str, Any]) -> str:
        """Generate a basic top-level wrapper when template is not available."""
        device_config = context.get("device_config", {})
        vendor_id = device_config.get("vendor_id", "0000")
        device_id = device_config.get("device_id", "0000")

        header = context.get(
            "header",
            "// PCILeech Top-Level Wrapper\n// Generated by PCILeechFWGenerator",
        )

        return f"""// PCILeech Top-Level Wrapper
// Generated for device: {vendor_id}:{device_id}

module pcileech_top (
    // Clock and reset
    input  logic        clk,
    input  logic        reset_n,

    // PCIe interface (connect to PCIe hard IP)
    input  logic [127:0] pcie_rx_data,
    input  logic         pcie_rx_valid,
    output logic [127:0] pcie_tx_data,
    output logic         pcie_tx_valid,

    // Configuration space interface
    input  logic        cfg_ext_read_received,
    input  logic        cfg_ext_write_received,
    input  logic [9:0]  cfg_ext_register_number,
    input  logic [3:0]  cfg_ext_function_number,
    input  logic [31:0] cfg_ext_write_data,
    input  logic [3:0]  cfg_ext_write_byte_enable,
    output logic [31:0] cfg_ext_read_data,
    output logic        cfg_ext_read_data_valid,

    // MSI-X interrupt interface
    output logic        msix_interrupt,
    output logic [10:0] msix_vector,
    input  logic        msix_interrupt_ack,

    // Debug/status outputs
    output logic [31:0] debug_status,
    output logic        device_ready
);

    // Internal signals
    logic [31:0] bar_addr;
    logic [31:0] bar_wr_data;
    logic        bar_wr_en;
    logic        bar_rd_en;
    logic [31:0] bar_rd_data;
    logic [2:0]  bar_index;
    logic [3:0]  bar_wr_be;

    // Instantiate BAR controller
    pcileech_tlps128_bar_controller bar_controller (
        .clk(clk),
        .reset_n(reset_n),
        .bar_index(bar_index),
        .bar_addr(bar_addr),
        .bar_wr_data(bar_wr_data),
        .bar_wr_be(bar_wr_be),
        .bar_wr_en(bar_wr_en),
        .bar_rd_en(bar_rd_en),
        .bar_rd_data(bar_rd_data),
        .cfg_ext_read_received(cfg_ext_read_received),
        .cfg_ext_write_received(cfg_ext_write_received),
        .cfg_ext_register_number(cfg_ext_register_number),
        .cfg_ext_function_number(cfg_ext_function_number),
        .cfg_ext_write_data(cfg_ext_write_data),
        .cfg_ext_write_byte_enable(cfg_ext_write_byte_enable),
        .cfg_ext_read_data(cfg_ext_read_data),
        .cfg_ext_read_data_valid(cfg_ext_read_data_valid),
        .msix_interrupt(msix_interrupt),
        .msix_vector(msix_vector),
        .msix_interrupt_ack(msix_interrupt_ack)
    );

    // Basic assignments
    assign bar_index = 3'b000;
    assign bar_wr_be = 4'hF;
    assign device_ready = 1'b1;
    assign debug_status = 32'h{vendor_id}{device_id[:4]};

    // Simple TLP processing
    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            pcie_tx_data <= 128'h0;
            pcie_tx_valid <= 1'b0;
            bar_addr <= 32'h0;
            bar_wr_data <= 32'h0;
            bar_wr_en <= 1'b0;
            bar_rd_en <= 1'b0;
        end else begin
            // Basic echo for testing
            pcie_tx_data <= pcie_rx_data;
            pcie_tx_valid <= pcie_rx_valid;
        end
    end

endmodule
"""
