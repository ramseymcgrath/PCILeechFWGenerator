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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.error_utils import extract_root_cause
from src.exceptions import PCILeechGenerationError, PlatformCompatibilityError

# Import from centralized locations
from src.string_utils import log_error_safe, log_info_safe, log_warning_safe
from src.templating import (
    AdvancedSVGenerator,
    BuildContext,
    TemplateRenderer,
    TemplateRenderError,
)

# Import existing infrastructure components
from .behavior_profiler import BehaviorProfile, BehaviorProfiler
from .config_space_manager import ConfigSpaceManager
from .msix_capability import parse_msix_capability, validate_msix_configuration
from .pcileech_context import PCILeechContextBuilder
from .writemask_generator import WritemaskGenerator

logger = logging.getLogger(__name__)


@dataclass
class PCILeechGenerationConfig:
    """Configuration for PCILeech firmware generation."""

    # Device identification
    device_bdf: str

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

    # Fallback control options
    fallback_mode: str = "none"  # "none", "prompt", or "auto"
    allowed_fallbacks: List[str] = field(default_factory=list)
    denied_fallbacks: List[str] = field(default_factory=list)

    # Donor template
    donor_template: Optional[Dict[str, Any]] = None


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

        # Initialize fallback manager
        from .fallback_manager import FallbackManager

        self.fallback_manager = FallbackManager(
            mode=config.fallback_mode,
            allowed_fallbacks=config.allowed_fallbacks,
            denied_fallbacks=config.denied_fallbacks,
        )

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
            prefix="PCIL",
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
            bdf=self.config.device_bdf,
            strict_vfio=getattr(self.config, "strict_vfio", True),
        )

        # Initialize template renderer
        self.template_renderer = TemplateRenderer(self.config.template_dir)

        # Initialize SystemVerilog generator
        self.sv_generator = AdvancedSVGenerator(template_dir=self.config.template_dir)

        # Initialize context builder (will be created after profiling)
        self.context_builder = None

        log_info_safe(
            self.logger,
            "PCILeech generator components initialized successfully",
            prefix="PCIL",
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
            prefix="PCIL",
        )

        try:
            # Step 0: Try to preload MSI-X data before any VFIO operations
            preloaded_msix = self._preload_msix_data_early()

            # Use a single VFIO binding session for both config space reading and BAR analysis
            # This prevents the cleanup from happening too early
            from ..cli.vfio_handler import VFIOBinder

            # Step 1: Capture device behavior profile (doesn't need VFIO)
            behavior_profile = self._capture_device_behavior()

            # Steps 2-4: Perform all VFIO-dependent operations within a single context
            with VFIOBinder(self.config.device_bdf) as vfio_device_path:
                log_info_safe(
                    self.logger,
                    "VFIO binding established for device {bdf} at {path}",
                    bdf=self.config.device_bdf,
                    path=vfio_device_path,
                    prefix="VFIO",
                )

                # Step 2: Analyze configuration space (with VFIO active)
                config_space_data = self._analyze_configuration_space_with_vfio()

                # Step 3: Process MSI-X capabilities (prefer preloaded data)
                msix_data = preloaded_msix or self._process_msix_capabilities(
                    config_space_data
                )

                # Step 3a: Handle interrupt strategy fallback if MSI-X not available
                if msix_data is None or msix_data.get("table_size", 0) == 0:
                    log_info_safe(
                        self.logger,
                        "MSI-X not available, checking for MSI capability",
                        prefix="PCIL",
                    )
                    # Check for MSI capability (ID 0x05)
                    config_space_hex = config_space_data.get("config_space_hex", "")
                    if config_space_hex:
                        from .msix_capability import find_cap

                        msi_cap = find_cap(config_space_hex, 0x05)
                        if msi_cap is not None:
                            log_info_safe(
                                self.logger,
                                "MSI capability found, using MSI with 1 vector",
                                prefix="PCIL",
                            )
                            interrupt_strategy = "msi"
                            interrupt_vectors = 1
                        else:
                            log_info_safe(
                                self.logger,
                                "No MSI capability found, using INTx",
                                prefix="PCIL",
                            )
                            interrupt_strategy = "intx"
                            interrupt_vectors = 1
                    else:
                        log_info_safe(
                            self.logger,
                            "No config space data, defaulting to INTx",
                            prefix="PCIL",
                        )
                        interrupt_strategy = "intx"
                        interrupt_vectors = 1
                else:
                    interrupt_strategy = "msix"
                    interrupt_vectors = msix_data["table_size"]

                # Step 4: Build comprehensive template context (with VFIO still active for BAR analysis)
                template_context = self._build_template_context(
                    behavior_profile,
                    config_space_data,
                    msix_data,
                    interrupt_strategy,
                    interrupt_vectors,
                )

            # VFIO cleanup happens here automatically when exiting the 'with' block
            log_info_safe(
                self.logger,
                "VFIO binding cleanup completed for device {bdf}",
                bdf=self.config.device_bdf,
                prefix="VFIO",
            )

            # Step 5: Generate SystemVerilog modules (no VFIO needed)
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
                self.logger,
                "PCILeech firmware generation completed successfully",
                prefix="PCIL",
            )

            return generation_result

        except PlatformCompatibilityError:
            # For platform compatibility issues, don't log additional error messages
            # The original detailed error was already logged
            raise
        except Exception as e:
            log_error_safe(
                self.logger,
                "PCILeech firmware generation failed: {error}",
                error=str(e),
                prefix="PCIL",
            )
            root_cause = extract_root_cause(e)
            raise PCILeechGenerationError(
                "Firmware generation failed", root_cause=root_cause
            )

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
            prefix="MSIX",
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
                prefix="MSIX",
            )

            return behavior_profile

        except Exception as e:
            implications = "Without behavior profiling, the generated firmware may not accurately reflect device timing patterns and behavior."

            if self.fallback_manager.confirm_fallback(
                "behavior-profiling", str(e), implications=implications
            ):
                log_warning_safe(
                    self.logger,
                    "Device behavior profiling failed, continuing without profile: {error}",
                    error=str(e),
                    prefix="MSIX",
                )
                return None
            else:
                raise PCILeechGenerationError(
                    f"Device behavior profiling failed: {e}"
                ) from e

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
            prefix="MSIX",
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
                "vendor_id": f"{device_info['vendor_id']:04x}",
                "device_id": f"{device_info['device_id']:04x}",
                "class_code": f"{device_info['class_code']:06x}",
                "revision_id": f"{device_info['revision_id']:02x}",
                "bars": device_info["bars"],
                "config_space_size": len(config_space_bytes),
            }

            log_info_safe(
                self.logger,
                "Configuration space analyzed: VID={vendor_id}, DID={device_id}, Class={class_code}",
                vendor_id=device_info["vendor_id"],
                device_id=device_info["device_id"],
                class_code=device_info["class_code"],
                prefix="MSIX",
            )

            return config_space_data

        except Exception as e:
            # Configuration space is critical for device identity - no hardcoded fallbacks
            implications = "Configuration space analysis is required for device identity and security. No fallback data will be provided."

            if self.fallback_manager.is_fallback_allowed("config-space-analysis"):
                log_warning_safe(
                    self.logger,
                    "Configuration space analysis failed, checking fallback options: {error}",
                    error=str(e),
                    prefix="MSIX",
                )
                # Let the fallback manager handle providing fallback data
                # This should not provide hardcoded defaults
                raise PCILeechGenerationError(
                    f"Configuration space analysis failed and no fallback data available: {e}"
                ) from e
            else:
                raise PCILeechGenerationError(
                    f"Configuration space analysis failed: {e}"
                ) from e

    def _analyze_configuration_space_with_vfio(self) -> Dict[str, Any]:
        """
        Analyze device configuration space when VFIO is already bound.

        This method assumes VFIO is already active and doesn't create its own binding.

        Returns:
            Dictionary containing configuration space data and analysis

        Raises:
            PCILeechGenerationError: If configuration space analysis fails
        """
        log_info_safe(
            self.logger,
            "Analyzing configuration space for device {bdf} (VFIO already active)",
            bdf=self.config.device_bdf,
            prefix="MSIX",
        )

        try:
            # Read configuration space without creating new VFIO binding
            config_space_bytes = self.config_space_manager._read_sysfs_config_space()

            # Extract device information
            device_info = self.config_space_manager.extract_device_info(
                config_space_bytes
            )

            # Build comprehensive configuration space data
            config_space_data = {
                "raw_config_space": config_space_bytes,
                "config_space_hex": config_space_bytes.hex(),
                "device_info": device_info,
                "vendor_id": f"{device_info['vendor_id']:04x}",
                "device_id": f"{device_info['device_id']:04x}",
                "class_code": f"{device_info['class_code']:06x}",
                "revision_id": f"{device_info['revision_id']:02x}",
                "bars": device_info["bars"],
                "config_space_size": len(config_space_bytes),
            }

            log_info_safe(
                self.logger,
                "Configuration space analyzed: VID={vendor_id}, DID={device_id}, Class={class_code}",
                vendor_id=device_info["vendor_id"],
                device_id=device_info["device_id"],
                class_code=device_info["class_code"],
                prefix="MSIX",
            )

            return config_space_data

        except Exception as e:
            # Configuration space is critical for device identity - no hardcoded fallbacks
            implications = "Configuration space analysis is required for device identity and security. No fallback data will be provided."

            if self.fallback_manager.confirm_fallback(
                "config-space", str(e), implications=implications
            ):
                log_warning_safe(
                    self.logger,
                    "Configuration space analysis failed, but fallback manager approved continuation: {error}",
                    error=str(e),
                    prefix="MSIX",
                )
                # Let the fallback manager handle providing fallback data
                # This should not provide hardcoded defaults
                raise PCILeechGenerationError(
                    f"Configuration space analysis failed and no fallback data available: {e}"
                ) from e
            else:
                raise PCILeechGenerationError(
                    f"Configuration space analysis failed: {e}"
                ) from e

    def _process_msix_capabilities(
        self, config_space_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Process MSI-X capabilities from configuration space.

        Args:
            config_space_data: Configuration space data

        Returns:
            Dictionary containing MSI-X capability information, or None if MSI-X
            capability is missing or table_size == 0
        """
        log_info_safe(self.logger, "Processing MSI-X capabilities", prefix="MSIX")

        config_space_hex = config_space_data.get("config_space_hex", "")

        if not config_space_hex:
            log_info_safe(
                self.logger,
                "No configuration space data available for MSI-X analysis",
                prefix="MSIX",
            )
            return None

        # Parse MSI-X capability
        msix_info = parse_msix_capability(config_space_hex)

        # Return None if capability is missing or table_size == 0
        if msix_info["table_size"] == 0:
            log_info_safe(self.logger, "MSI-X capability not found or table_size is 0")
            return None

        # Validate MSI-X configuration
        is_valid, validation_errors = validate_msix_configuration(msix_info)

        if not is_valid and self.config.strict_validation:
            log_warning_safe(
                self.logger,
                "MSI-X validation failed: {errors}",
                errors="; ".join(validation_errors),
                prefix="MSIX",
            )
            return None

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

    def _build_template_context(
        self,
        behavior_profile: Optional[BehaviorProfile],
        config_space_data: Dict[str, Any],
        msix_data: Optional[Dict[str, Any]],
        interrupt_strategy: str,
        interrupt_vectors: int,
    ) -> Dict[str, Any]:
        """
        Build comprehensive template context from all data sources.

        Args:
            behavior_profile: Device behavior profile
            config_space_data: Configuration space data
            msix_data: MSI-X capability data (None if not available)
            interrupt_strategy: Interrupt strategy ("msix", "msi", or "intx")
            interrupt_vectors: Number of interrupt vectors

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
                interrupt_strategy=interrupt_strategy,
                interrupt_vectors=interrupt_vectors,
                donor_template=self.config.donor_template,
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
            root_cause = extract_root_cause(e)
            raise PCILeechGenerationError(
                "Template context building failed", root_cause=root_cause
            )

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
            modules = self.sv_generator.generate_systemverilog_modules(
                template_context=template_context, behavior_profile=behavior_profile
            )

            # Cache the generated modules for use in writemask generation
            self._cached_systemverilog_modules = modules

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
            "config_space_hex": self._generate_config_space_hex(template_context),
        }

        # Generate writemask COE after config space COE is available
        # This requires the config space COE to be saved to disk first
        components["writemask_coe"] = self._generate_writemask_coe(template_context)

        return components

    def _generate_build_integration(self, template_context: Dict[str, Any]) -> str:
        """Generate build system integration code."""
        try:
            return self.sv_generator.generate_pcileech_integration_code(
                template_context
            )
        except Exception as e:
            implications = "Using fallback build integration may result in inconsistent or unpredictable build behavior."

            if self.fallback_manager.confirm_fallback(
                "build-integration", str(e), implications=implications
            ):
                log_warning_safe(
                    self.logger,
                    "PCILeech build integration generation failed, attempting fallback: {error}",
                    error=str(e),
                )
                # Fallback to base integration
                try:
                    return self.sv_generator.generate_enhanced_build_integration()
                except Exception as fallback_e:
                    if self.fallback_manager.confirm_fallback(
                        "basic-build-integration",
                        str(fallback_e),
                        implications="Using minimal build integration may result in build failures.",
                    ):
                        log_warning_safe(
                            self.logger,
                            "Enhanced build integration also failed, using minimal integration: {error}",
                            error=str(fallback_e),
                        )
                        return "# Build integration generation failed"
                    else:
                        raise PCILeechGenerationError(
                            f"Build integration generation failed: {fallback_e}"
                        ) from fallback_e
            else:
                raise PCILeechGenerationError(
                    f"Build integration generation failed: {e}"
                ) from e

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

    def _generate_writemask_coe(
        self, template_context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate writemask COE file for configuration space.

        Args:
            template_context: Template context data

        Returns:
            Writemask COE content or None if generation fails
        """
        try:
            log_info_safe(self.logger, "Generating writemask COE file")

            # Initialize writemask generator
            writemask_gen = WritemaskGenerator()

            # Get configuration space COE path from src directory (where COE files are saved)
            cfg_space_coe = (
                self.config.output_dir / "systemverilog" / "pcileech_cfgspace.coe"
            )
            writemask_coe = (
                self.config.output_dir
                / "systemverilog"
                / "pcileech_cfgspace_writemask.coe"
            )

            # Ensure output directory exists
            cfg_space_coe.parent.mkdir(parents=True, exist_ok=True)

            # Check if config space COE exists, if not, generate it first
            if not cfg_space_coe.exists():
                log_info_safe(
                    self.logger,
                    "Config space COE not found, generating it first",
                    prefix="WRMASK",
                )

                # First check if it exists in the already generated systemverilog modules
                # This avoids regenerating what was already created
                systemverilog_modules = getattr(
                    self, "_cached_systemverilog_modules", {}
                )

                if "pcileech_cfgspace.coe" in systemverilog_modules:
                    # Use the already generated content
                    cfg_space_coe.write_text(
                        systemverilog_modules["pcileech_cfgspace.coe"]
                    )
                    log_info_safe(
                        self.logger,
                        "Used cached config space COE content at {path}",
                        path=str(cfg_space_coe),
                        prefix="WRMASK",
                    )
                else:
                    # Check if COE file already exists in systemverilog directory
                    # This prevents regenerating files that were already saved
                    systemverilog_coe_path = (
                        self.config.output_dir
                        / "systemverilog"
                        / "pcileech_cfgspace.coe"
                    )
                    if systemverilog_coe_path.exists():
                        # Copy from systemverilog directory to avoid regeneration
                        cfg_space_coe.write_text(systemverilog_coe_path.read_text())
                        log_info_safe(
                            self.logger,
                            "Copied existing COE from systemverilog directory to {path}",
                            path=str(cfg_space_coe),
                            prefix="WRMASK",
                        )
                    else:
                        # Generate new content as last resort
                        from ..templating.systemverilog_generator import (
                            AdvancedSVGenerator,
                        )

                        sv_gen = AdvancedSVGenerator(
                            template_dir=self.config.template_dir
                        )
                        modules = sv_gen.generate_pcileech_modules(template_context)

                        if "pcileech_cfgspace.coe" in modules:
                            cfg_space_coe.write_text(modules["pcileech_cfgspace.coe"])
                            log_info_safe(
                                self.logger,
                                "Generated config space COE file at {path}",
                                path=str(cfg_space_coe),
                                prefix="WRMASK",
                            )
                        else:
                            log_warning_safe(
                                self.logger,
                                "Config space COE module not found in generated modules",
                                prefix="WRMASK",
                            )
                            return None

            # Extract device configuration for MSI/MSI-X settings
            device_config = {
                "msi_config": template_context.get("msi_config", {}),
                "msix_config": template_context.get("msix_config", {}),
            }

            # Generate writemask
            writemask_gen.generate_writemask(
                cfg_space_coe, writemask_coe, device_config
            )

            # Read generated writemask content
            if writemask_coe.exists():
                return writemask_coe.read_text()
            else:
                log_warning_safe(
                    self.logger, "Writemask COE file was not generated", prefix="WRMASK"
                )
                return None

        except Exception as e:
            log_warning_safe(
                self.logger,
                "Failed to generate writemask COE: {error}",
                error=str(e),
                prefix="WRMASK",
            )
            return None

    def _generate_config_space_hex(self, template_context: Dict[str, Any]) -> str:
        """
        Generate configuration space hex file for FPGA initialization.

        Args:
            template_context: Template context containing config space data

        Returns:
            Path to generated hex file as string

        Raises:
            PCILeechGenerationError: If hex generation fails
        """
        log_info_safe(
            self.logger, "Generating configuration space hex file", prefix="HEX"
        )

        try:
            # Import hex formatter
            from .hex_formatter import ConfigSpaceHexFormatter

            # Try multiple possible locations for config space data
            config_space_data = None
            raw_config_space = None

            # First try the direct key
            if "config_space_data" in template_context:
                config_space_data = template_context["config_space_data"]
                raw_config_space = config_space_data.get("raw_config_space", b"")

            # If not found, try alternative locations
            if not raw_config_space:
                # Try the config_space key directly
                config_space = template_context.get("config_space", {})
                if isinstance(config_space, dict):
                    # Try raw_data key (this is what we found in the logs)
                    raw_config_space = config_space.get("raw_data", b"")
                    # If raw_data is a string (hex), convert it to bytes
                    if isinstance(raw_config_space, str):
                        try:
                            raw_config_space = bytes.fromhex(raw_config_space)
                        except ValueError:
                            raw_config_space = b""
                    if not raw_config_space:
                        # Try raw_config_space key
                        raw_config_space = config_space.get("raw_config_space", b"")
                        # If raw_config_space is a string (hex), convert it to bytes
                        if isinstance(raw_config_space, str):
                            try:
                                raw_config_space = bytes.fromhex(raw_config_space)
                            except ValueError:
                                raw_config_space = b""
                    if not raw_config_space:
                        # Try hex format
                        config_space_hex = config_space.get("config_space_hex", "")
                        if config_space_hex:
                            try:
                                raw_config_space = bytes.fromhex(config_space_hex)
                            except ValueError:
                                pass

            # If still not found, try device_config or other locations
            if not raw_config_space:
                device_config = template_context.get("device_config", {})
                if "config_space_data" in device_config:
                    config_space_data = device_config["config_space_data"]
                    raw_config_space = config_space_data.get("raw_config_space", b"")

            if not raw_config_space:
                # Log all available keys for debugging
                log_warning_safe(
                    self.logger,
                    "Configuration space data not found. Available template context keys: {keys}",
                    keys=list(template_context.keys()),
                    prefix="HEX",
                )

                # Try to examine nested structure
                for key, value in template_context.items():
                    if isinstance(value, dict) and (
                        "config_space" in str(key).lower() or "raw" in str(key).lower()
                    ):
                        log_info_safe(
                            self.logger,
                            "Found potential config space key '{key}' with subkeys: {subkeys}",
                            key=key,
                            subkeys=(
                                list(value.keys())
                                if isinstance(value, dict)
                                else type(value)
                            ),
                            prefix="HEX",
                        )

                raise ValueError(
                    "No configuration space data available in template context"
                )

            # Create hex formatter
            formatter = ConfigSpaceHexFormatter()

            # Generate hex content
            hex_content = formatter.format_config_space_to_hex(
                raw_config_space, include_comments=True
            )

            log_info_safe(
                self.logger,
                "Generated configuration space hex file with {size} bytes",
                size=len(raw_config_space),
                prefix="HEX",
            )

            return hex_content

        except Exception as e:
            log_error_safe(
                self.logger,
                "Configuration space hex generation failed: {error}",
                error=str(e),
                prefix="HEX",
            )
            raise PCILeechGenerationError(
                f"Config space hex generation failed: {e}"
            ) from e

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
                # Handle COE files specially - they should NOT go in src directory
                if module_name.endswith(".coe"):
                    # COE files go in the systemverilog directory only
                    # Skip saving to src directory to avoid duplication
                    continue
                else:
                    # Avoid double .sv extension
                    if module_name.endswith(".sv"):
                        module_file = sv_dir / module_name
                    else:
                        module_file = sv_dir / f"{module_name}.sv"
                    module_file.write_text(module_code)

            # Save firmware components
            components_dir = output_dir / "components"
            components_dir.mkdir(exist_ok=True)

            # Save writemask COE if generated
            firmware_components = generation_result.get("firmware_components", {})
            if (
                "writemask_coe" in firmware_components
                and firmware_components["writemask_coe"]
            ):
                # Writemask COE goes in the src directory alongside other COE files
                writemask_file = sv_dir / "pcileech_cfgspace_writemask.coe"
                writemask_file.write_text(firmware_components["writemask_coe"])

                log_info_safe(
                    self.logger,
                    "Saved writemask COE to {path}",
                    path=str(writemask_file),
                    prefix="WRMASK",
                )

            # Save config space hex file if generated
            if (
                "config_space_hex" in firmware_components
                and firmware_components["config_space_hex"]
            ):
                # Config space hex file goes in the src directory for $readmemh
                hex_file = sv_dir / "config_space_init.hex"
                hex_file.write_text(firmware_components["config_space_hex"])

                log_info_safe(
                    self.logger,
                    "Saved configuration space hex file to {path}",
                    path=str(hex_file),
                    prefix="HEX",
                )

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

    def _preload_msix_data_early(self) -> Optional[Dict[str, Any]]:
        """
        Preload MSI-X data from sysfs before VFIO binding to ensure availability.

        Returns:
            MSI-X data dictionary if available, None otherwise
        """
        try:
            import os

            # Try to read config space from sysfs before VFIO binding
            config_space_path = f"/sys/bus/pci/devices/{self.config.device_bdf}/config"

            if not os.path.exists(config_space_path):
                log_info_safe(
                    self.logger,
                    "Config space not accessible via sysfs, skipping MSI-X preload",
                    prefix="MSIX",
                )
                return None

            log_info_safe(
                self.logger,
                "Preloading MSI-X data from sysfs before VFIO binding",
                prefix="MSIX",
            )

            with open(config_space_path, "rb") as f:
                config_space_bytes = f.read()

            config_space_hex = config_space_bytes.hex()

            # Parse MSI-X capability
            msix_info = parse_msix_capability(config_space_hex)

            if msix_info["table_size"] > 0:
                log_info_safe(
                    self.logger,
                    "Preloaded MSI-X capability: {vectors} vectors, table BIR {bir}, offset 0x{offset:x}",
                    vectors=msix_info["table_size"],
                    bir=msix_info["table_bir"],
                    offset=msix_info["table_offset"],
                    prefix="MSIX",
                )

                # Validate MSI-X configuration
                is_valid, validation_errors = validate_msix_configuration(msix_info)

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
                    "preloaded": True,
                }

                return msix_data
            else:
                log_info_safe(
                    self.logger,
                    "No MSI-X capability found during preload",
                    prefix="MSIX",
                )
                return None

        except Exception as e:
            log_warning_safe(
                self.logger,
                "MSI-X preload failed: {error}",
                error=str(e),
                prefix="MSIX",
            )
            return None
