#!/usr/bin/env python3
"""
PCILeech Firmware Generator - Main Package

This package provides the core functionality for generating PCILeech firmware
with a simplified import structure to reduce complexity.
"""

# Version information
from .__version__ import __version__

# Core exceptions
from .exceptions import (
    PCILeechError,
    PCILeechGenerationError,
    TemplateError,
    ConfigurationError,
    BuildError,
    ValidationError,
)

# Utility functions from specific utility modules
from .string_utils import (
    # String utilities
    safe_format,
    log_info_safe,
    log_error_safe,
    log_warning_safe,
    generate_sv_header_comment,
)

# Import utilities
from .import_utils import safe_import

# Device cloning functionality - flattened imports
from .device_clone import (
    # Board configuration
    get_board_info,
    validate_board,
    # Device configuration
    DeviceConfiguration,
    DeviceConfigManager,
    # Config space management
    ConfigSpaceManager,
    # Behavior profiling
    BehaviorProfiler,
    BehaviorProfile,
    # PCILeech generator
    PCILeechGenerator,
    PCILeechGenerationConfig,
)

# PCI capability handling - now at top level
from .pci_capability import (
    ConfigSpace,
    CapabilityWalker,
    CapabilityProcessor,
    PCICapabilityID,
    PCIExtCapabilityID,
)

# Templating functionality
from .templating import (
    TemplateRenderer,
    AdvancedSVGenerator,
    TCLBuilder,
)

# CLI functionality
from .cli import (
    VFIOBinder,
    BuildConfig,
    run_build,
    flash_firmware,
)

# File management
from .file_management import (
    FileManager,
    DonorDumpManager,
    OptionROMManager,
    RepoManager,
)

# Vivado handling
from .vivado_handling import (
    VivadoErrorReporter,
)

__all__ = [
    # Version
    "__version__",
    # Exceptions
    "PCILeechError",
    "PCILeechGenerationError",
    "BuildError",
    "ValidationError",
    "TemplateError",
    "ConfigurationError",
    # Utilities
    "safe_format",
    "log_info_safe",
    "log_error_safe",
    "log_warning_safe",
    "generate_sv_header_comment",
    "safe_import",
    # Device cloning
    "get_board_info",
    "validate_board",
    "DeviceConfiguration",
    "DeviceConfigManager",
    "ConfigSpaceManager",
    "BehaviorProfiler",
    "BehaviorProfile",
    "PCILeechGenerator",
    "PCILeechGenerationConfig",
    # PCI capabilities
    "ConfigSpace",
    "CapabilityWalker",
    "CapabilityProcessor",
    "PCICapabilityID",
    "PCIExtCapabilityID",
    # Templating
    "TemplateRenderer",
    "AdvancedSVGenerator",
    "TCLBuilder",
    # CLI
    "VFIOBinder",
    "BuildConfig",
    "run_build",
    "flash_firmware",
    # File management
    "FileManager",
    "DonorDumpManager",
    "OptionROMManager",
    "RepoManager",
    # Vivado
    "VivadoErrorReporter",
]
