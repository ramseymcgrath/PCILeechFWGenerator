#!/usr/bin/env python3
"""
SystemVerilog Generator with Jinja2 Templates

This module provides advanced SystemVerilog code generation capabilities
using the centralized Jinja2 templating system for the PCILeech firmware generator.

Key Features:
- Uses the project's centralized TemplateRenderer for consistent template handling
- Strict error handling - template failures raise TemplateRenderError with detailed context
- Integration with the existing template system including custom filters and global functions
- Support for advanced features like power management, error handling, and performance monitoring
- Comprehensive input validation to prevent unsafe firmware generation

The generator properly delegates all template rendering to the TemplateRenderer class,
ensuring consistent behavior and proper error reporting throughout the system.
"""

import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.__version__ import __version__
from src.device_clone.device_config import DeviceClass, DeviceType
from src.device_clone.manufacturing_variance import VarianceModel
from src.string_utils import (generate_sv_header_comment, log_error_safe,
                              log_info_safe, log_warning_safe, safe_format)

from .advanced_sv_features import (AdvancedSVFeatureGenerator,
                                   ErrorHandlingConfig, PerformanceConfig)
from .advanced_sv_power import PowerManagementConfig
from .template_renderer import TemplateRenderer, TemplateRenderError


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
    """Main advanced SystemVerilog generator using the templating system."""

    def __init__(
        self,
        power_config: Optional[PowerManagementConfig] = None,
        error_config: Optional[ErrorHandlingConfig] = None,
        perf_config: Optional[PerformanceConfig] = None,
        device_config: Optional[DeviceSpecificLogic] = None,
        template_dir: Optional[Path] = None,
        use_pcileech_primary: bool = True,
    ):
        """
        Initialize the advanced SystemVerilog generator.

        Args:
            power_config: Power management configuration
            error_config: Error handling configuration
            perf_config: Performance monitoring configuration
            device_config: Device-specific logic configuration
            template_dir: Template directory path
            use_pcileech_primary: Whether to use PCILeech as primary generation path

        Raises:
            TemplateRenderError: If template renderer initialization fails
            ValueError: If invalid configuration is provided
        """
        # Set up logger first for error reporting
        self.logger = logging.getLogger(__name__)

        # Validate and set configurations with proper error handling
        try:
            self.power_config = power_config or PowerManagementConfig()
            self.error_config = error_config or ErrorHandlingConfig()
            self.perf_config = perf_config or PerformanceConfig()
            self.device_config = device_config or DeviceSpecificLogic()
            self.use_pcileech_primary = use_pcileech_primary

            # Validate device configuration has required attributes
            self._validate_device_config()

            # Initialize template renderer - this is our core templating system
            self.renderer = TemplateRenderer(template_dir)

        except Exception as e:
            error_msg = f"Failed to initialize AdvancedSVGenerator: {e}"
            log_error_safe(self.logger, error_msg)
            raise TemplateRenderError(error_msg) from e

        log_info_safe(
            self.logger,
            "AdvancedSVGenerator initialized with templating system, PCILeech primary: {primary}",
            primary=self.use_pcileech_primary,
        )

    def _validate_device_config(self) -> None:
        """
        Validate device configuration for safe firmware generation.

        Raises:
            ValueError: If device configuration is invalid or unsafe
        """
        if not self.device_config:
            raise ValueError(
                "Device configuration is required for safe firmware generation"
            )

        # Validate device type and class have proper enum values
        if not hasattr(self.device_config.device_type, "value"):
            raise ValueError(
                f"Invalid device_type: {self.device_config.device_type}. Must be a DeviceType enum."
            )

        if not hasattr(self.device_config.device_class, "value"):
            raise ValueError(
                f"Invalid device_class: {self.device_config.device_class}. Must be a DeviceClass enum."
            )

        # Validate critical size parameters
        if self.device_config.max_payload_size <= 0:
            raise ValueError(
                f"Invalid max_payload_size: {self.device_config.max_payload_size}. Must be positive."
            )

        if self.device_config.max_read_request_size <= 0:
            raise ValueError(
                f"Invalid max_read_request_size: {self.device_config.max_read_request_size}. Must be positive."
            )

        # Validate queue depths are reasonable
        if (
            self.device_config.tx_queue_depth <= 0
            or self.device_config.tx_queue_depth > 65536
        ):
            raise ValueError(
                f"Invalid tx_queue_depth: {self.device_config.tx_queue_depth}. Must be between 1 and 65536."
            )

        if (
            self.device_config.rx_queue_depth <= 0
            or self.device_config.rx_queue_depth > 65536
        ):
            raise ValueError(
                f"Invalid rx_queue_depth: {self.device_config.rx_queue_depth}. Must be between 1 and 65536."
            )

    @lru_cache(maxsize=32)
    def generate_device_specific_ports(self) -> str:
        """
        Generate device-specific port declarations using template.

        Returns:
            SystemVerilog port declarations as string

        Raises:
            TemplateRenderError: If template rendering fails

        Note:
            This method is cached to avoid regenerating identical port declarations.
        """
        # Create a hashable representation of device_config for caching
        device_config_key = (
            self.device_config.device_type.value,
            self.device_config.device_class.value,
            self.device_config.max_payload_size,
            self.device_config.max_read_request_size,
            self.device_config.msi_vectors,
            self.device_config.msix_vectors,
            self.device_config.enable_dma,
            self.device_config.enable_interrupt_coalescing,
            self.device_config.enable_virtualization,
            self.device_config.enable_sr_iov,
        )

        return self._generate_device_specific_ports_impl(device_config_key)

    def _generate_device_specific_ports_impl(self, device_config_key: tuple) -> str:
        """Implementation method for generating device-specific ports."""
        context = {
            "device_config": self.device_config,
        }

        try:
            return self.renderer.render_template(
                "systemverilog/components/device_specific_ports.sv.j2", context
            )
        except TemplateRenderError as e:
            log_error_safe(
                self.logger,
                "Failed to render device-specific ports template: {error}",
                error=e,
            )
            # Re-raise the exception to properly report the error
            raise

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
                module_content = self.renderer.render_template(
                    f"systemverilog/{module_template}", template_context
                )
                module_name = module_template.replace(".sv.j2", "")
                modules[module_name] = module_content

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

        # Validate required values before template generation
        self._validate_template_context()

        # Prepare template context - simplified for single use-case
        context = {
            "header": header,
            "device_config": self.device_config,
            "device_type": self.device_config.device_type.value,
            "device_class": self.device_config.device_class.value,
            "power_config": self.power_config,
            "error_config": self.error_config,
            "perf_config": self.perf_config,
            "registers": regs,
            "variance_model": variance_model,
            "device_specific_ports": device_specific_ports,
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
            ValueError: If required context data is missing or invalid
        """
        log_info_safe(self.logger, "Generating PCILeech SystemVerilog modules")

        # Strict validation of input parameters
        if not template_context:
            raise ValueError(
                "Template context is required for PCILeech module generation"
            )

        if not isinstance(template_context, dict):
            raise ValueError(
                f"Template context must be a dictionary, got {type(template_context)}"
            )

        modules = {}

        try:
            # Validate and extract device config with comprehensive error checking
            device_config = template_context.get("device_config")
            if not device_config:
                raise TemplateRenderError(
                    "device_config is missing from template context. "
                    "This is required for safe PCILeech firmware generation."
                )

            if not isinstance(device_config, dict):
                raise TemplateRenderError(
                    f"device_config must be a dictionary, got {type(device_config)}. "
                    "Cannot proceed with firmware generation."
                )

            # Validate critical device identification fields
            required_fields = ["vendor_id", "device_id"]
            missing_fields = []
            invalid_fields = []

            for field in required_fields:
                value = device_config.get(field)
                if not value:
                    missing_fields.append(field)
                elif not isinstance(value, str) or len(value) != 4:
                    invalid_fields.append(
                        f"{field}='{value}' (must be 4-character hex string)"
                    )

            if missing_fields or invalid_fields:
                error_details = []
                if missing_fields:
                    error_details.append(f"Missing fields: {', '.join(missing_fields)}")
                if invalid_fields:
                    error_details.append(f"Invalid fields: {', '.join(invalid_fields)}")

                error_msg = (
                    f"Critical device identification validation failed: {'; '.join(error_details)}. "
                    "Cannot generate safe firmware without proper device identification. "
                    "Vendor ID and Device ID must be 4-character hex strings (e.g., '10EC', '8168')."
                )
                log_error_safe(self.logger, error_msg)
                raise TemplateRenderError(error_msg)

            # Create enhanced context efficiently - avoid full copy for performance
            enhanced_context = self._create_context(template_context, device_config)

            # Generate header comment for SystemVerilog files
            header = generate_sv_header_comment(
                "PCILeech SystemVerilog Module",
                generator="PCILeechFWGenerator - SystemVerilog Generation",
                device_type="PCIe Device Controller",
                features="PCILeech integration, MSI-X support, BAR controller",
            )

            # Create device object for template compatibility
            device_info = {
                "vendor_id": device_config["vendor_id"],
                "device_id": device_config["device_id"],
                "subsys_vendor_id": device_config.get(
                    "subsystem_vendor_id", "0000"
                ),  # 0000 = no subsystem
                "subsys_device_id": device_config.get(
                    "subsystem_device_id", "0000"
                ),  # 0000 = no subsystem
                "class_code": device_config.get("class_code", "020000"),
                "revision_id": device_config.get("revision_id", "01"),
            }

            enhanced_context.update(
                {
                    "header": header,  # Add header for template
                    "device": device_info,
                    "config_space": {
                        "vendor_id": device_config["vendor_id"],
                        "device_id": device_config["device_id"],
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
                    "vendor_id": device_config["vendor_id"],
                    "device_id": device_config["device_id"],
                    "vendor_id_hex": device_config["vendor_id"],
                    "device_id_hex": device_config["device_id"],
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
            modules["top_level_wrapper"] = self.renderer.render_template(
                "systemverilog/top_level_wrapper.sv.j2", enhanced_context
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

        # Generate advanced controller - let template errors propagate
        advanced_modules["pcileech_advanced_controller"] = (
            self.generate_advanced_systemverilog(
                regs=registers, variance_model=variance_model
            )
        )

        return advanced_modules

    def _extract_pcileech_registers(self, behavior_profile: Any) -> List[Dict]:
        """
        Extract register definitions from behavior profile for PCILeech.

        Args:
            behavior_profile: Behavior profile containing register access data

        Returns:
            List of register definitions with validated data

        Raises:
            TemplateRenderError: If register extraction fails or produces invalid data
            ValueError: If behavior profile is invalid
        """
        if not behavior_profile:
            raise ValueError("Behavior profile is required for register extraction")

        if not hasattr(behavior_profile, "register_accesses"):
            raise TemplateRenderError(
                "Behavior profile missing 'register_accesses' attribute. "
                "Cannot generate SystemVerilog without register access information. "
                "Ensure the behavior profile was properly generated from actual device data."
            )

        register_accesses = behavior_profile.register_accesses
        if not register_accesses:
            raise TemplateRenderError(
                "No register accesses found in behavior profile. "
                "Cannot generate safe SystemVerilog without actual device register information. "
                "The behavior profile must contain real register access patterns from the target device."
            )

        registers = []
        register_map = {}
        invalid_accesses = []

        # Process register accesses with strict validation
        for i, access in enumerate(register_accesses):
            # Validate access object structure
            if not hasattr(access, "register"):
                invalid_accesses.append(f"Access {i}: missing 'register' attribute")
                continue

            reg_name = access.register
            if not reg_name or reg_name == "UNKNOWN":
                invalid_accesses.append(
                    f"Access {i}: invalid register name '{reg_name}'"
                )
                continue

            # Validate offset
            offset = getattr(access, "offset", None)
            if offset is None:
                invalid_accesses.append(
                    f"Access {i}: missing offset for register '{reg_name}'"
                )
                continue

            if not isinstance(offset, int) or offset < 0:
                invalid_accesses.append(
                    f"Access {i}: invalid offset {offset} for register '{reg_name}'"
                )
                continue

            # Initialize register entry if not seen before
            if reg_name not in register_map:
                register_map[reg_name] = {
                    "name": reg_name,
                    "offset": offset,
                    "size": 32,  # Standard PCIe register size
                    "access_count": 0,
                    "read_count": 0,
                    "write_count": 0,
                    "access_type": "rw",
                }

            # Count access types
            register_map[reg_name]["access_count"] += 1
            if hasattr(access, "operation"):
                operation = access.operation
                if operation == "read":
                    register_map[reg_name]["read_count"] += 1
                elif operation == "write":
                    register_map[reg_name]["write_count"] += 1
                else:
                    invalid_accesses.append(
                        f"Access {i}: unknown operation '{operation}' for register '{reg_name}'"
                    )

        # Report validation errors if any
        if invalid_accesses:
            error_msg = (
                f"Register access validation failed with {len(invalid_accesses)} errors:\n"
                + "\n".join(invalid_accesses[:10])  # Limit to first 10 errors
            )
            if len(invalid_accesses) > 10:
                error_msg += f"\n... and {len(invalid_accesses) - 10} more errors"
            log_error_safe(self.logger, error_msg)
            raise TemplateRenderError(error_msg)

        # Determine access types and validate register data
        for reg_name, reg_info in register_map.items():
            # Determine access type based on observed operations
            if reg_info["write_count"] == 0 and reg_info["read_count"] > 0:
                reg_info["access_type"] = "ro"
            elif reg_info["read_count"] == 0 and reg_info["write_count"] > 0:
                reg_info["access_type"] = "wo"
            elif reg_info["read_count"] > 0 and reg_info["write_count"] > 0:
                reg_info["access_type"] = "rw"
            else:
                # No valid operations recorded
                log_warning_safe(
                    self.logger,
                    f"Register '{reg_name}' has no valid read/write operations, defaulting to read-write",
                )
                reg_info["access_type"] = "rw"

            registers.append(reg_info)

        # Final validation
        if not registers:
            raise TemplateRenderError(
                "No valid registers extracted from behavior profile. "
                "Cannot generate safe SystemVerilog without actual device register information. "
                "Ensure the behavior profile contains valid register access patterns from real hardware."
            )

        log_info_safe(
            self.logger,
            f"Successfully extracted {len(registers)} registers from behavior profile",
        )

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
            else:
                raise TemplateRenderError(
                    "Failed to read actual MSI-X table data from hardware. "
                    "Cannot generate safe firmware without real MSI-X table values. "
                    "Ensure the device is properly accessible via VFIO."
                )
        except Exception as e:
            error_msg = (
                f"Failed to read actual MSI-X table from hardware: {e}. "
                "Cannot generate safe firmware without real MSI-X table values. "
                "Ensure the device is properly accessible via VFIO and try again."
            )
            log_error_safe(self.logger, error_msg)
            raise TemplateRenderError(error_msg) from e

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
                    "build_system_version": __version__,
                }
            )

            return self.renderer.render_template(
                "python/pcileech_build_integration.py.j2", build_context
            )

        except TemplateRenderError:
            # Re-raise the error to properly report template issues
            raise

    def _validate_template_context(self) -> None:
        """
        Validate that all required values are present before template generation.

        Raises:
            TemplateRenderError: If required values are missing or invalid
        """
        errors = []
        warnings = []

        # Validate device_config exists and has required attributes
        if not self.device_config:
            errors.append(
                "device_config is None or missing - this is required for safe firmware generation"
            )
        else:
            # Validate device_type
            if not hasattr(self.device_config, "device_type"):
                errors.append("device_config.device_type is missing")
            elif not hasattr(self.device_config.device_type, "value"):
                errors.append(
                    "device_config.device_type does not have a 'value' attribute - must be a DeviceType enum"
                )
            else:
                # Validate device_type value is reasonable
                device_type_value = self.device_config.device_type.value
                if (
                    not isinstance(device_type_value, str)
                    or not device_type_value.strip()
                ):
                    errors.append(
                        f"device_config.device_type.value is invalid: '{device_type_value}'"
                    )

            # Validate device_class
            if not hasattr(self.device_config, "device_class"):
                errors.append("device_config.device_class is missing")
            elif not hasattr(self.device_config.device_class, "value"):
                errors.append(
                    "device_config.device_class does not have a 'value' attribute - must be a DeviceClass enum"
                )
            else:
                # Validate device_class value is reasonable
                device_class_value = self.device_config.device_class.value
                if (
                    not isinstance(device_class_value, str)
                    or not device_class_value.strip()
                ):
                    errors.append(
                        f"device_config.device_class.value is invalid: '{device_class_value}'"
                    )

            # Validate critical numeric parameters
            numeric_params = [
                ("max_payload_size", 128, 4096),
                ("max_read_request_size", 128, 4096),
                ("tx_queue_depth", 1, 65536),
                ("rx_queue_depth", 1, 65536),
                ("command_queue_depth", 1, 4096),
            ]

            for param_name, min_val, max_val in numeric_params:
                if hasattr(self.device_config, param_name):
                    param_value = getattr(self.device_config, param_name)
                    if not isinstance(param_value, int):
                        errors.append(
                            f"device_config.{param_name} must be an integer, got {type(param_value)}"
                        )
                    elif param_value < min_val or param_value > max_val:
                        errors.append(
                            f"device_config.{param_name} = {param_value} is out of valid range [{min_val}, {max_val}]"
                        )
                else:
                    warnings.append(
                        f"device_config.{param_name} is missing, using default"
                    )

            # Validate frequency parameters
            frequency_params = [
                ("base_frequency_mhz", 1.0, 1000.0),
                ("memory_frequency_mhz", 1.0, 2000.0),
            ]

            for param_name, min_val, max_val in frequency_params:
                if hasattr(self.device_config, param_name):
                    param_value = getattr(self.device_config, param_name)
                    if not isinstance(param_value, (int, float)):
                        errors.append(
                            f"device_config.{param_name} must be a number, got {type(param_value)}"
                        )
                    elif param_value < min_val or param_value > max_val:
                        errors.append(
                            f"device_config.{param_name} = {param_value} MHz is out of valid range [{min_val}, {max_val}] MHz"
                        )

        # Validate power_config if present
        if self.power_config:
            if not hasattr(self.power_config, "enable_power_management"):
                warnings.append("power_config.enable_power_management is missing")

        # Validate error_config if present
        if self.error_config:
            if not hasattr(self.error_config, "enable_error_detection"):
                warnings.append("error_config.enable_error_detection is missing")

        # Validate perf_config if present
        if self.perf_config:
            if not hasattr(self.perf_config, "enable_performance_counters"):
                warnings.append("perf_config.enable_performance_counters is missing")

        # Log warnings
        for warning in warnings:
            log_warning_safe(
                self.logger, f"Template context validation warning: {warning}"
            )

        # If there are validation errors, raise an exception
        if errors:
            error_msg = (
                f"Template context validation failed with {len(errors)} critical errors:\n"
                + "\n".join(f"  - {error}" for error in errors)
                + "\n\nCannot proceed with firmware generation due to invalid configuration."
            )
            log_error_safe(self.logger, error_msg)
            raise TemplateRenderError(error_msg)

        log_info_safe(
            self.logger,
            f"Template context validation passed ({len(warnings)} warnings)",
        )

    def _create_context(
        self, template_context: Dict[str, Any], device_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create enhanced template context efficiently without full copying.

        Args:
            template_context: Original template context
            device_config: Validated device configuration

        Returns:
            Enhanced context dictionary with additional template variables
        """
        # Generate header comment for SystemVerilog files
        header = generate_sv_header_comment(
            "PCILeech SystemVerilog Module",
            generator="PCILeechFWGenerator - SystemVerilog Generation",
            device_type="PCIe Device Controller",
            features="PCILeech integration, MSI-X support, BAR controller",
        )

        # Create device object for template compatibility
        device_info = {
            "vendor_id": device_config["vendor_id"],
            "device_id": device_config["device_id"],
            "subsys_vendor_id": device_config.get("subsystem_vendor_id", "0000"),
            "subsys_device_id": device_config.get("subsystem_device_id", "0000"),
            "class_code": device_config.get("class_code", "020000"),
            "revision_id": device_config.get("revision_id", "01"),
        }

        # Build enhanced context incrementally for better performance
        enhanced_context = {
            # Copy only essential keys from original context
            "device_config": template_context["device_config"],
            "msix_config": template_context.get("msix_config", {}),
            "bar_config": template_context.get("bar_config", {}),
            "interrupt_config": template_context.get("interrupt_config", {}),
            "config_space_data": template_context.get("config_space_data", {}),
            "timing_config": template_context.get(
                "timing_config", {}
            ),  # Add timing_config
            # Add new template variables
            "header": header,
            "device": device_info,
            "config_space": {
                "vendor_id": device_config["vendor_id"],
                "device_id": device_config["device_id"],
                "class_code": device_config.get("class_code", "020000"),
                "revision_id": device_config.get("revision_id", "01"),
            },
            "enable_custom_config": True,
            "enable_scatter_gather": getattr(self.device_config, "enable_dma", True),
            "enable_interrupt": template_context.get("interrupt_config", {}).get(
                "vectors", 0
            )
            > 0,
            "enable_clock_crossing": True,
            "enable_performance_counters": getattr(
                self.perf_config, "enable_transaction_counters", True
            ),
            "enable_error_detection": getattr(self.error_config, "enable_ecc", True),
            "fifo_type": "block_ram",
            "fifo_depth": 512,
            "data_width": 128,
            "fpga_family": "artix7",
            "vendor_id": device_config["vendor_id"],
            "device_id": device_config["device_id"],
            "vendor_id_hex": device_config["vendor_id"],
            "device_id_hex": device_config["device_id"],
            "device_specific_config": {},
        }

        # Add enable_advanced_features to device_config section if it doesn't exist
        if "device_config" in enhanced_context and isinstance(
            enhanced_context["device_config"], dict
        ):
            enhanced_context["device_config"]["enable_advanced_features"] = getattr(
                self.error_config, "enable_ecc", True
            )

        return enhanced_context
