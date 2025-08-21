#!/usr/bin/env python3
"""
SystemVerilog Generator with Jinja2 Templates

This module provides advanced SystemVerilog code generation capabilities
using the centralized Jinja2 templating system for the PCILeech firmware generator.

This is the improved modular version that replaces the original monolithic implementation.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.__version__ import __version__
from src.device_clone.device_config import DeviceClass, DeviceType
from src.device_clone.manufacturing_variance import VarianceModel
from src.error_utils import format_user_friendly_error
from src.string_utils import generate_sv_header_comment, log_error_safe, log_info_safe

from ..utils.unified_context import (
    DEFAULT_TIMING_CONFIG,
    MSIX_DEFAULT,
    PCILEECH_DEFAULT,
    TemplateObject,
    normalize_config_to_dict,
)
from .advanced_sv_features import (
    AdvancedSVFeatureGenerator,
    ErrorHandlingConfig,
    PerformanceConfig,
)
from .advanced_sv_power import PowerManagementConfig
from .template_renderer import TemplateRenderer, TemplateRenderError
from .sv_constants import SVConstants, SVTemplates, SVValidation
from .sv_context_builder import SVContextBuilder
from .sv_device_config import DeviceSpecificLogic
from .sv_module_generator import SVModuleGenerator
from .sv_validator import SVValidator


class SystemVerilogGenerator:
    """
    Main SystemVerilog generator with improved modular architecture.

    This class coordinates the generation of SystemVerilog modules using
    a modular design with clear separation of concerns.
    """

    def __init__(
        self,
        power_config: Optional[PowerManagementConfig] = None,
        error_config: Optional[ErrorHandlingConfig] = None,
        perf_config: Optional[PerformanceConfig] = None,
        device_config: Optional[DeviceSpecificLogic] = None,
        template_dir: Optional[Path] = None,
        use_pcileech_primary: bool = True,
    ):
        """Initialize the SystemVerilog generator with improved architecture."""
        self.logger = logging.getLogger(__name__)

        # Initialize configurations with defaults
        self.power_config = power_config or PowerManagementConfig()
        self.error_config = error_config or ErrorHandlingConfig()
        self.perf_config = perf_config or PerformanceConfig()
        self.device_config = device_config or DeviceSpecificLogic()
        self.use_pcileech_primary = use_pcileech_primary

        # Initialize components
        self.validator = SVValidator(self.logger)
        self.context_builder = SVContextBuilder(self.logger)
        self.renderer = TemplateRenderer(template_dir)
        self.module_generator = SVModuleGenerator(self.renderer, self.logger)

        # Validate device configuration
        self.validator.validate_device_config(self.device_config)

        log_info_safe(
            self.logger,
            "SystemVerilogGenerator initialized successfully",
            use_pcileech=self.use_pcileech_primary,
        )

    def generate_modules(
        self, template_context: Dict[str, Any], behavior_profile: Optional[Any] = None
    ) -> Dict[str, str]:
        """
        Generate SystemVerilog modules with improved error handling and performance.

        Args:
            template_context: Template context data
            behavior_profile: Optional behavior profile for advanced features

        Returns:
            Dictionary mapping module names to generated code

        Raises:
            TemplateRenderError: If generation fails
        """
        try:
            # Validate input context
            self.validator.validate_template_context(template_context)

            # Build enhanced context efficiently
            enhanced_context = self.context_builder.build_enhanced_context(
                template_context,
                self.power_config,
                self.error_config,
                self.perf_config,
                self.device_config,
            )

            # Generate modules based on configuration
            if self.use_pcileech_primary:
                return self.module_generator.generate_pcileech_modules(
                    enhanced_context, behavior_profile
                )
            else:
                return self.module_generator.generate_legacy_modules(
                    enhanced_context, behavior_profile
                )

        except Exception as e:
            error_msg = format_user_friendly_error(e, "SystemVerilog generation")
            log_error_safe(self.logger, error_msg)
            raise TemplateRenderError(error_msg) from e

    # Backward compatibility methods
    def generate_systemverilog_modules(
        self, template_context: Dict[str, Any], behavior_profile: Optional[Any] = None
    ) -> Dict[str, str]:
        """Legacy method name for backward compatibility."""
        return self.generate_modules(template_context, behavior_profile)

    def generate_pcileech_modules(
        self, template_context: Dict[str, Any], behavior_profile: Optional[Any] = None
    ) -> Dict[str, str]:
        """Direct access to PCILeech module generation for backward compatibility."""
        return self.module_generator.generate_pcileech_modules(
            template_context, behavior_profile
        )

    def generate_device_specific_ports(self, context_hash: str = "") -> str:
        """Generate device-specific ports for backward compatibility."""
        return self.module_generator.generate_device_specific_ports(
            self.device_config.device_type.value,
            self.device_config.device_class.value,
            context_hash,
        )

    def clear_cache(self) -> None:
        """Clear the LRU cache for device-specific ports generation."""
        self.module_generator.generate_device_specific_ports.cache_clear()
        log_info_safe(self.logger, "Cleared SystemVerilog generator cache")


# Backward compatibility alias
AdvancedSVGenerator = SystemVerilogGenerator


# Re-export commonly used items for backward compatibility
__all__ = [
    "SystemVerilogGenerator",
    "AdvancedSVGenerator",
    "DeviceSpecificLogic",
    "PowerManagementConfig",
    "ErrorHandlingConfig",
    "PerformanceConfig",
    "TemplateRenderError",
]
