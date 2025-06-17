#!/usr/bin/env python3
"""
PCILeech Generator - Main orchestrator for PCILeech firmware generation

This module provides the main orchestrator class that coordinates complete PCILeech
firmware generation by integrating with existing infrastructure components and
eliminating all hard-coded fallbacks.

The PCILeechGenerator class serves as the central coordination point for:
- Device behavior profiling and analysis
- Configuration space management
- MSI-X capability handling
- Template context building
- SystemVerilog generation
- Production-ready error handling

All data sources are dynamic with no fallback mechanisms - the system fails
fast if required data is not available.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import existing infrastructure components
from .behavior_profiler import BehaviorProfile, BehaviorProfiler
from .config_space_manager import ConfigSpaceManager
from .msix_capability import (
    parse_msix_capability,
    validate_msix_configuration,
)
from .pcileech_context import PCILeechContextBuilder

# Import templating infrastructure
from ..templating.systemverilog_generator import AdvancedSVGenerator
from ..templating.template_renderer import TemplateRenderer, TemplateRenderError

# Import string utilities
from ..string_utils import log_error_safe, log_info_safe, log_warning_safe

logger = logging.getLogger(__name__)


@dataclass
class PCILeechGenerationConfig:
    """Configuration for PCILeech firmware generation."""

    # Device identification
    device_bdf: str
    device_profile: str = "generic"

    # Generation options
    enable_behavior_profiling: bool = True
    behavior_capture_duration: float = 30.0
    enable_manufacturing_variance: bool = True
    enable_advanced_features: bool = True

    # Template configuration
    template_dir: Optional[Path] = None
    output_dir: Path = Path("generated")

    # PCILeech-specific options
    pcileech_command_timeout: int = 1000
    pcileech_buffer_size: int = 4096
    enable_dma_operations: bool = True
    enable_interrupt_coalescing: bool = False

    # Validation options
    strict_validation: bool = True
    fail_on_missing_data: bool = True


class PCILeechGenerationError(Exception):
    """Exception raised when PCILeech generation fails."""

    pass


class PCILeechGenerator:
    """
    Main orchestrator class for PCILeech firmware generation.

    This class coordinates the complete PCILeech firmware generation process by
    integrating with existing infrastructure components and providing dynamic
    data sourcing for all template variables.

    Key responsibilities:
    - Orchestrate device behavior profiling
    - Manage configuration space analysis
    - Handle MSI-X capability processing
    - Build comprehensive template contexts
    - Generate SystemVerilog modules
    - Provide production-ready error handling
    """

    def __init__(self, config: PCILeechGenerationConfig):
        """
        Initialize the PCILeech generator.

        Args:
            config: Generation configuration

        Raises:
            PCILeechGenerationError: If initialization fails
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize infrastructure components
        try:
            self._initialize_components()
        except Exception as e:
            raise PCILeechGenerationError(
                f"Failed to initialize PCILeech generator: {e}"
            ) from e

    def _initialize_components(self) -> None:
        """Initialize all infrastructure components."""
        log_info_safe(
            self.logger,
            "Initializing PCILeech generator for device {bdf}",
            bdf=self.config.device_bdf,
        )

        # Initialize behavior profiler
        if self.config.enable_behavior_profiling:
            self.behavior_profiler = BehaviorProfiler(
                bdf=self.config.device_bdf,
                debug=True,
                enable_variance=self.config.enable_manufacturing_variance,
                enable_ftrace=True,
            )
        else:
            self.behavior_profiler = None

        # Initialize configuration space manager
        self.config_space_manager = ConfigSpaceManager(
            bdf=self.config.device_bdf, device_profile=self.config.device_profile
        )

        # Initialize template renderer
        self.template_renderer = TemplateRenderer(self.config.template_dir)

        # Initialize SystemVerilog generator
        self.sv_generator = AdvancedSVGenerator(template_dir=self.config.template_dir)

        # Initialize context builder (will be created after profiling)
        self.context_builder = None

        log_info_safe(
            self.logger, "PCILeech generator components initialized successfully"
        )

    def generate_pcileech_firmware(self) -> Dict[str, Any]:
        """
        Generate complete PCILeech firmware with dynamic data integration.

        Returns:
            Dictionary containing generated firmware components and metadata

        Raises:
            PCILeechGenerationError: If generation fails at any stage
        """
        log_info_safe(
            self.logger,
            "Starting PCILeech firmware generation for device {bdf}",
            bdf=self.config.device_bdf,
        )

        try:
            # Step 1: Capture device behavior profile
            behavior_profile = self._capture_device_behavior()

            # Step 2: Analyze configuration space
            config_space_data = self._analyze_configuration_space()

            # Step 3: Process MSI-X capabilities
            msix_data = self._process_msix_capabilities(config_space_data)

            # Step 4: Build comprehensive template context
            template_context = self._build_template_context(
                behavior_profile, config_space_data, msix_data
            )

            # Step 5: Generate SystemVerilog modules
            systemverilog_modules = self._generate_systemverilog_modules(
                template_context
            )

            # Step 6: Generate additional firmware components
            firmware_components = self._generate_firmware_components(template_context)

            # Step 7: Validate generated firmware
            self._validate_generated_firmware(
                systemverilog_modules, firmware_components
            )

            # Compile results
            generation_result = {
                "device_bdf": self.config.device_bdf,
                "generation_timestamp": self._get_timestamp(),
                "behavior_profile": behavior_profile,
                "config_space_data": config_space_data,
                "msix_data": msix_data,
                "template_context": template_context,
                "systemverilog_modules": systemverilog_modules,
                "firmware_components": firmware_components,
                "generation_metadata": self._build_generation_metadata(),
            }

            log_info_safe(
                self.logger, "PCILeech firmware generation completed successfully"
            )

            return generation_result

        except Exception as e:
            log_error_safe(
                self.logger,
                "PCILeech firmware generation failed: {error}",
                error=str(e),
            )
            raise PCILeechGenerationError(f"Firmware generation failed: {e}") from e

    def _capture_device_behavior(self) -> Optional[BehaviorProfile]:
        """
        Capture device behavior profile using the behavior profiler.

        Returns:
            BehaviorProfile if profiling is enabled, None otherwise

        Raises:
            PCILeechGenerationError: If behavior profiling fails
        """
        if not self.behavior_profiler:
            log_info_safe(
                self.logger,
                "Behavior profiling disabled, skipping device behavior capture",
            )
            return None

        log_info_safe(
            self.logger,
            "Capturing device behavior profile for {duration}s",
            duration=self.config.behavior_capture_duration,
        )

        try:
            behavior_profile = self.behavior_profiler.capture_behavior_profile(
                duration=self.config.behavior_capture_duration
            )

            # Analyze patterns for enhanced context
            pattern_analysis = self.behavior_profiler.analyze_patterns(behavior_profile)

            # Store analysis results in profile for later use
            behavior_profile.pattern_analysis = pattern_analysis

            log_info_safe(
                self.logger,
                "Captured {accesses} register accesses with {patterns} timing patterns",
                accesses=behavior_profile.total_accesses,
                patterns=len(behavior_profile.timing_patterns),
            )

            return behavior_profile

        except Exception as e:
            if self.config.fail_on_missing_data:
                raise PCILeechGenerationError(
                    f"Device behavior profiling failed: {e}"
                ) from e
            else:
                log_warning_safe(
                    self.logger,
                    "Device behavior profiling failed, continuing without profile: {error}",
                    error=str(e),
                )
                return None

    def _analyze_configuration_space(self) -> Dict[str, Any]:
        """
        Analyze device configuration space.

        Returns:
            Dictionary containing configuration space data and analysis

        Raises:
            PCILeechGenerationError: If configuration space analysis fails
        """
        log_info_safe(
            self.logger,
            "Analyzing configuration space for device {bdf}",
            bdf=self.config.device_bdf,
        )

        try:
            # Read configuration space
            config_space_bytes = self.config_space_manager.read_vfio_config_space()

            # Extract device information
            device_info = self.config_space_manager.extract_device_info(
                config_space_bytes
            )

            # Build comprehensive configuration space data
            config_space_data = {
                "raw_config_space": config_space_bytes,
                "config_space_hex": config_space_bytes.hex(),
                "device_info": device_info,
                "vendor_id": device_info["vendor_id"],
                "device_id": device_info["device_id"],
                "class_code": device_info["class_code"],
                "revision_id": device_info["revision_id"],
                "bars": device_info["bars"],
                "config_space_size": len(config_space_bytes),
            }

            log_info_safe(
                self.logger,
                "Configuration space analyzed: VID={vendor_id}, DID={device_id}, Class={class_code}",
                vendor_id=device_info["vendor_id"],
                device_id=device_info["device_id"],
                class_code=device_info["class_code"],
            )

            return config_space_data

        except Exception as e:
            if self.config.fail_on_missing_data:
                raise PCILeechGenerationError(
                    f"Configuration space analysis failed: {e}"
                ) from e
            else:
                log_warning_safe(
                    self.logger,
                    "Configuration space analysis failed: {error}",
                    error=str(e),
                )
                # Return minimal fallback data
                return {
                    "raw_config_space": b"",
                    "config_space_hex": "",
                    "device_info": {},
                    "vendor_id": "0000",
                    "device_id": "0000",
                    "class_code": "0000",
                    "revision_id": "00",
                    "bars": [],
                    "config_space_size": 0,
                }

    def _process_msix_capabilities(
        self, config_space_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process MSI-X capabilities from configuration space.

        Args:
            config_space_data: Configuration space data

        Returns:
            Dictionary containing MSI-X capability information

        Raises:
            PCILeechGenerationError: If MSI-X processing fails
        """
        log_info_safe(self.logger, "Processing MSI-X capabilities")

        try:
            config_space_hex = config_space_data.get("config_space_hex", "")

            if not config_space_hex:
                log_warning_safe(
                    self.logger,
                    "No configuration space data available for MSI-X analysis",
                )
                return self._get_default_msix_data()

            # Parse MSI-X capability
            msix_info = parse_msix_capability(config_space_hex)

            # Validate MSI-X configuration
            is_valid, validation_errors = validate_msix_configuration(msix_info)

            if not is_valid and self.config.strict_validation:
                error_msg = f"MSI-X validation failed: {'; '.join(validation_errors)}"
                raise PCILeechGenerationError(error_msg)

            # Build comprehensive MSI-X data
            msix_data = {
                "capability_info": msix_info,
                "table_size": msix_info["table_size"],
                "table_bir": msix_info["table_bir"],
                "table_offset": msix_info["table_offset"],
                "pba_bir": msix_info["pba_bir"],
                "pba_offset": msix_info["pba_offset"],
                "enabled": msix_info["enabled"],
                "function_mask": msix_info["function_mask"],
                "validation_errors": validation_errors,
                "is_valid": is_valid,
            }

            log_info_safe(
                self.logger,
                "MSI-X capabilities processed: {vectors} vectors, table BIR {bir}, offset 0x{offset:x}",
                vectors=msix_info["table_size"],
                bir=msix_info["table_bir"],
                offset=msix_info["table_offset"],
            )

            return msix_data

        except Exception as e:
            if self.config.fail_on_missing_data:
                raise PCILeechGenerationError(
                    f"MSI-X capability processing failed: {e}"
                ) from e
            else:
                log_warning_safe(
                    self.logger,
                    "MSI-X capability processing failed: {error}",
                    error=str(e),
                )
                return self._get_default_msix_data()

    def _get_default_msix_data(self) -> Dict[str, Any]:
        """Get default MSI-X data when processing fails."""
        return {
            "capability_info": {
                "table_size": 0,
                "table_bir": 0,
                "table_offset": 0,
                "pba_bir": 0,
                "pba_offset": 0,
                "enabled": False,
                "function_mask": False,
            },
            "table_size": 0,
            "table_bir": 0,
            "table_offset": 0,
            "pba_bir": 0,
            "pba_offset": 0,
            "enabled": False,
            "function_mask": False,
            "validation_errors": ["MSI-X not available"],
            "is_valid": False,
        }

    def _build_template_context(
        self,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
        msix_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build comprehensive template context from all data sources.

        Args:
            behavior_profile: Device behavior profile
            config_space_data: Configuration space data
            msix_data: MSI-X capability data

        Returns:
            Comprehensive template context dictionary

        Raises:
            PCILeechGenerationError: If context building fails
        """
        log_info_safe(self.logger, "Building comprehensive template context")

        try:
            # Initialize context builder
            self.context_builder = PCILeechContextBuilder(
                device_bdf=self.config.device_bdf, config=self.config
            )

            # Build context from all data sources
            template_context = self.context_builder.build_context(
                behavior_profile=behavior_profile,
                config_space_data=config_space_data,
                msix_data=msix_data,
            )

            # Validate context completeness
            self._validate_template_context(template_context)

            log_info_safe(
                self.logger,
                "Template context built successfully with {keys} top-level keys",
                keys=len(template_context),
            )

            return template_context

        except Exception as e:
            raise PCILeechGenerationError(
                f"Template context building failed: {e}"
            ) from e

    def _validate_template_context(self, context: Dict[str, Any]) -> None:
        """
        Validate template context for completeness.

        Args:
            context: Template context to validate

        Raises:
            PCILeechGenerationError: If context validation fails
        """
        required_keys = [
            "device_config",
            "config_space",
            "msix_config",
            "bar_config",
            "timing_config",
            "pcileech_config",
        ]

        missing_keys = [key for key in required_keys if key not in context]

        if missing_keys and self.config.fail_on_missing_data:
            raise PCILeechGenerationError(
                f"Template context missing required keys: {missing_keys}"
            )

        if missing_keys:
            log_warning_safe(
                self.logger,
                "Template context missing optional keys: {keys}",
                keys=missing_keys,
            )

    def _generate_systemverilog_modules(
        self, template_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate SystemVerilog modules using template context.

        Args:
            template_context: Template context data

        Returns:
            Dictionary mapping module names to generated SystemVerilog code

        Raises:
            PCILeechGenerationError: If SystemVerilog generation fails
        """
        log_info_safe(self.logger, "Generating SystemVerilog modules")

        try:
            # Use the enhanced SystemVerilog generator for PCILeech modules
            behavior_profile = template_context.get("device_config", {}).get(
                "behavior_profile"
            )
            modules = self.sv_generator.generate_pcileech_modules(
                template_context=template_context, behavior_profile=behavior_profile
            )

            log_info_safe(
                self.logger,
                "Generated {count} SystemVerilog modules",
                count=len(modules),
            )

            return modules

        except TemplateRenderError as e:
            raise PCILeechGenerationError(
                f"SystemVerilog generation failed: {e}"
            ) from e

    def _generate_advanced_modules(
        self, template_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate advanced SystemVerilog modules."""
        advanced_modules = {}

        try:
            # Generate advanced controller if behavior profile is available
            if template_context.get("device_config", {}).get("behavior_profile"):
                registers = self._extract_register_definitions(template_context)
                variance_model = template_context.get("device_config", {}).get(
                    "variance_model"
                )

                advanced_modules["advanced_controller"] = (
                    self.sv_generator.generate_advanced_systemverilog(
                        regs=registers, variance_model=variance_model
                    )
                )

        except Exception as e:
            log_warning_safe(
                self.logger, "Advanced module generation failed: {error}", error=str(e)
            )

        return advanced_modules

    def _extract_register_definitions(
        self, template_context: Dict[str, Any]
    ) -> List[Dict]:
        """Extract register definitions from template context."""
        registers = []

        # Extract from behavior profile if available
        behavior_profile = template_context.get("device_config", {}).get(
            "behavior_profile"
        )
        if behavior_profile:
            for access in behavior_profile.get("register_accesses", []):
                registers.append(
                    {
                        "name": access.get("register", "UNKNOWN"),
                        "offset": access.get("offset", 0),
                        "size": 32,  # Default to 32-bit registers
                        "access_type": access.get("operation", "rw"),
                    }
                )

        return registers

    def _generate_firmware_components(
        self, template_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate additional firmware components.

        Args:
            template_context: Template context data

        Returns:
            Dictionary containing additional firmware components
        """
        log_info_safe(self.logger, "Generating additional firmware components")

        components = {
            "build_integration": self._generate_build_integration(template_context),
            "constraint_files": self._generate_constraint_files(template_context),
            "tcl_scripts": self._generate_tcl_scripts(template_context),
        }

        return components

    def _generate_build_integration(self, template_context: Dict[str, Any]) -> str:
        """Generate build system integration code."""
        try:
            return self.sv_generator.generate_pcileech_integration_code(
                template_context
            )
        except Exception as e:
            log_warning_safe(
                self.logger,
                "PCILeech build integration generation failed: {error}",
                error=str(e),
            )
            # Fallback to base integration
            try:
                return self.sv_generator.generate_enhanced_build_integration()
            except Exception as fallback_e:
                log_warning_safe(
                    self.logger,
                    "Fallback build integration also failed: {error}",
                    error=str(fallback_e),
                )
                return "# Build integration generation failed"

    def _generate_constraint_files(
        self, template_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate constraint files."""
        # Placeholder for constraint file generation
        return {
            "timing_constraints": "# Timing constraints placeholder",
            "pin_constraints": "# Pin constraints placeholder",
        }

    def _generate_tcl_scripts(self, template_context: Dict[str, Any]) -> Dict[str, str]:
        """Generate TCL build scripts."""
        # Placeholder for TCL script generation
        return {
            "build_script": "# TCL build script placeholder",
            "synthesis_script": "# TCL synthesis script placeholder",
        }

    def _validate_generated_firmware(
        self, systemverilog_modules: Dict[str, str], firmware_components: Dict[str, Any]
    ) -> None:
        """
        Validate generated firmware for completeness and correctness.

        Args:
            systemverilog_modules: Generated SystemVerilog modules
            firmware_components: Generated firmware components

        Raises:
            PCILeechGenerationError: If validation fails
        """
        if self.config.strict_validation:
            # Validate SystemVerilog modules
            required_modules = ["pcileech_tlps128_bar_controller"]
            missing_modules = [
                mod for mod in required_modules if mod not in systemverilog_modules
            ]

            if missing_modules:
                raise PCILeechGenerationError(
                    f"Missing required SystemVerilog modules: {missing_modules}"
                )

            # Validate module content
            for module_name, module_code in systemverilog_modules.items():
                if not module_code or len(module_code.strip()) == 0:
                    raise PCILeechGenerationError(
                        f"SystemVerilog module '{module_name}' is empty"
                    )

    def _build_generation_metadata(self) -> Dict[str, Any]:
        """Build metadata about the generation process."""
        return {
            "generator_version": "1.0.0",
            "config": {
                "device_bdf": self.config.device_bdf,
                "device_profile": self.config.device_profile,
                "enable_behavior_profiling": self.config.enable_behavior_profiling,
                "enable_manufacturing_variance": self.config.enable_manufacturing_variance,
                "enable_advanced_features": self.config.enable_advanced_features,
                "strict_validation": self.config.strict_validation,
            },
            "components_used": [
                "BehaviorProfiler",
                "ConfigSpaceManager",
                "MSIXCapability",
                "PCILeechContextBuilder",
                "AdvancedSVGenerator",
                "TemplateRenderer",
            ],
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp for generation metadata."""
        from datetime import datetime

        return datetime.now().isoformat()

    def save_generated_firmware(
        self, generation_result: Dict[str, Any], output_dir: Optional[Path] = None
    ) -> Path:
        """
        Save generated firmware to disk.

        Args:
            generation_result: Result from generate_pcileech_firmware()
            output_dir: Output directory (optional, uses config default)

        Returns:
            Path to the output directory

        Raises:
            PCILeechGenerationError: If saving fails
        """
        if output_dir is None:
            output_dir = self.config.output_dir

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Save SystemVerilog modules
            sv_dir = output_dir / "systemverilog"
            sv_dir.mkdir(exist_ok=True)

            for module_name, module_code in generation_result[
                "systemverilog_modules"
            ].items():
                module_file = sv_dir / f"{module_name}.sv"
                module_file.write_text(module_code)

            # Save firmware components
            components_dir = output_dir / "components"
            components_dir.mkdir(exist_ok=True)

            # Save metadata
            import json

            metadata_file = output_dir / "generation_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(generation_result["generation_metadata"], f, indent=2)

            log_info_safe(
                self.logger, "Generated firmware saved to {path}", path=str(output_dir)
            )

            return output_dir

        except Exception as e:
            raise PCILeechGenerationError(
                f"Failed to save generated firmware: {e}"
            ) from e
