#!/usr/bin/env python3
"""
Helper functions for common patterns in the PCILeech firmware build system.

This module provides reusable helper functions to reduce code duplication
and improve maintainability in the build system.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Production mode configuration
PRODUCTION_MODE = os.getenv("PCILEECH_PRODUCTION_MODE", "true").lower() == "true"


def safe_import_with_fallback(
    primary_imports: Dict[str, str],
    fallback_imports: Optional[Dict[str, str]] = None,
    fallback_values: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Handle module importing with fallback logic to replace complex try/except blocks.

    This function consolidates the import pattern used throughout build.py where
    modules are imported with relative fallbacks and None defaults.

    Args:
        primary_imports: Dict mapping variable names to module paths for primary imports
        fallback_imports: Dict mapping variable names to relative module paths for fallback
        fallback_values: Dict mapping variable names to fallback values (default: None)

    Returns:
        Dict mapping variable names to imported modules or fallback values

    Example:
        >>> imports = safe_import_with_fallback(
        ...     primary_imports={
        ...         'ConfigSpaceManager': 'config_space_manager.ConfigSpaceManager',
        ...         'TCLGenerator': 'tcl_generator.TCLGenerator'
        ...     },
        ...     fallback_imports={
        ...         'ConfigSpaceManager': '.config_space_manager.ConfigSpaceManager',
        ...         'TCLGenerator': '.tcl_generator.TCLGenerator'
        ...     }
        ... )
    """
    if fallback_values is None:
        fallback_values = {}

    if fallback_imports is None:
        fallback_imports = {}

    imported_modules = {}

    for var_name, module_path in primary_imports.items():
        try:
            # Try primary import
            module_parts = module_path.split(".")
            if len(module_parts) == 1:
                # Simple module import
                module = __import__(module_parts[0])
                imported_modules[var_name] = module
            else:
                # Import from module
                module_name = ".".join(module_parts[:-1])
                class_name = module_parts[-1]
                module = __import__(module_name, fromlist=[class_name])
                imported_modules[var_name] = getattr(module, class_name)

        except ImportError as e:
            if PRODUCTION_MODE:
                # In production mode, we must not fall back - error out immediately
                logger.error(
                    f"PRODUCTION ERROR: Failed to import {var_name} from {module_path}: {e}"
                )
                raise RuntimeError(
                    f"Production mode requires all modules to be available. Failed to import {var_name}: {e}"
                )

            logger.debug(f"Primary import failed for {var_name}: {e}")

            # Try fallback import if available
            if var_name in fallback_imports:
                try:
                    fallback_path = fallback_imports[var_name]
                    module_parts = fallback_path.split(".")
                    if len(module_parts) == 1:
                        module = __import__(module_parts[0])
                        imported_modules[var_name] = module
                    else:
                        module_name = ".".join(module_parts[:-1])
                        class_name = module_parts[-1]
                        module = __import__(module_name, fromlist=[class_name])
                        imported_modules[var_name] = getattr(module, class_name)

                except ImportError as fallback_error:
                    logger.warning(
                        f"Fallback import failed for {var_name}: {fallback_error}"
                    )
                    imported_modules[var_name] = fallback_values.get(var_name, None)
            else:
                imported_modules[var_name] = fallback_values.get(var_name, None)

    return imported_modules


def select_pcie_ip_core(fpga_part: str) -> str:
    """
    Select appropriate PCIe IP core based on FPGA part.

    This function encapsulates the FPGA part selection logic that was
    previously embedded in the TCL generation code (lines 298-319).

    Args:
        fpga_part: FPGA part string (e.g., "xc7a35tcsg324-2")

    Returns:
        String indicating the PCIe IP core type to use

    Example:
        >>> select_pcie_ip_core("xc7a35tcsg324-2")
        'axi_pcie'
        >>> select_pcie_ip_core("xc7a75tfgg484-2")
        'pcie_7x'
        >>> select_pcie_ip_core("xczu3eg-sbva484-1-e")
        'pcie_ultrascale'
    """
    fpga_part_lower = fpga_part.lower()

    if "xc7a35t" in fpga_part_lower:
        # For Artix-7 35T, use AXI PCIe IP core which is available for smaller parts
        return "axi_pcie"
    elif "xc7a75t" in fpga_part_lower or "xc7k" in fpga_part_lower:
        # For Kintex-7 and larger Artix-7 parts, use pcie_7x IP core
        return "pcie_7x"
    elif "xczu" in fpga_part_lower:
        # For Zynq UltraScale+, use PCIe UltraScale IP core
        return "pcie_ultrascale"
    else:
        # Default fallback to pcie_7x for unknown parts
        logger.warning(
            f"Unknown FPGA part '{fpga_part}', defaulting to pcie_7x IP core"
        )
        return "pcie_7x"


def write_tcl_file_with_logging(
    content: str,
    file_path: Union[str, Path],
    tcl_files_list: List[str],
    description: str,
    logger_instance: Optional[logging.Logger] = None,
) -> bool:
    """
    Write TCL content to file with consistent logging and list management.

    This function handles the repetitive pattern of:
    1. Writing content to file
    2. Appending file path to tcl_files list
    3. Logging completion

    Args:
        content: TCL content to write
        file_path: Path where to write the file
        tcl_files_list: List to append the file path to
        description: Description for logging (e.g., "project setup TCL")
        logger_instance: Logger to use (defaults to module logger)

    Returns:
        True if successful, False otherwise

    Example:
        >>> tcl_files = []
        >>> success = write_tcl_file_with_logging(
        ...     "# TCL content here",
        ...     "output/project.tcl",
        ...     tcl_files,
        ...     "project setup TCL"
        ... )
        >>> print(tcl_files)
        ['output/project.tcl']
    """
    if logger_instance is None:
        logger_instance = logger

    try:
        file_path = Path(file_path)

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Append to file list
        tcl_files_list.append(str(file_path))

        # Log completion
        logger_instance.info(f"Generated {description}")

        return True

    except Exception as e:
        logger_instance.error(f"Failed to write {description} to {file_path}: {e}")
        return False


def create_fpga_strategy_selector() -> Callable[[str], Dict[str, Any]]:
    """
    Create a strategy selector function for FPGA-specific configurations.

    This implements a strategy pattern for selecting FPGA-specific settings
    based on the FPGA part, making it easy to extend with new FPGA families.

    Returns:
        Function that takes fpga_part and returns configuration dict

    Example:
        >>> selector = create_fpga_strategy_selector()
        >>> config = selector("xc7a35tcsg324-2")
        >>> print(config['pcie_ip_type'])
        'axi_pcie'
    """

    def artix7_35t_strategy(fpga_part: str) -> Dict[str, Any]:
        """Strategy for Artix-7 35T parts."""
        return {
            "pcie_ip_type": "axi_pcie",
            "family": "artix7",
            "size": "small",
            "max_lanes": 4,
            "supports_msi": True,
            "supports_msix": False,  # Limited resources
            "clock_constraints": "artix7_35t.xdc",
        }

    def artix7_75t_strategy(fpga_part: str) -> Dict[str, Any]:
        """Strategy for Artix-7 75T and Kintex-7 parts."""
        return {
            "pcie_ip_type": "pcie_7x",
            "family": "artix7" if "xc7a" in fpga_part else "kintex7",
            "size": "medium",
            "max_lanes": 8,
            "supports_msi": True,
            "supports_msix": True,
            "clock_constraints": (
                "artix7_75t.xdc" if "xc7a" in fpga_part else "kintex7.xdc"
            ),
        }

    def zynq_ultrascale_strategy(fpga_part: str) -> Dict[str, Any]:
        """Strategy for Zynq UltraScale+ parts."""
        return {
            "pcie_ip_type": "pcie_ultrascale",
            "family": "zynq_ultrascale",
            "size": "large",
            "max_lanes": 16,
            "supports_msi": True,
            "supports_msix": True,
            "clock_constraints": "zynq_ultrascale.xdc",
        }

    def default_strategy(fpga_part: str) -> Dict[str, Any]:
        """Default strategy for unknown parts."""
        logger.warning(f"Unknown FPGA part '{fpga_part}', using default strategy")
        return {
            "pcie_ip_type": "pcie_7x",
            "family": "unknown",
            "size": "medium",
            "max_lanes": 4,
            "supports_msi": True,
            "supports_msix": False,
            "clock_constraints": "default.xdc",
        }

    # Strategy mapping
    strategies = {
        "xc7a35t": artix7_35t_strategy,
        "xc7a75t": artix7_75t_strategy,
        "xc7k": artix7_75t_strategy,  # Kintex-7 uses same strategy as 75T
        "xczu": zynq_ultrascale_strategy,
    }

    def select_strategy(fpga_part: str) -> Dict[str, Any]:
        """Select and execute the appropriate strategy for the given FPGA part."""
        fpga_part_lower = fpga_part.lower()

        # Find matching strategy
        for pattern, strategy_func in strategies.items():
            if pattern in fpga_part_lower:
                return strategy_func(fpga_part)

        # No match found, use default
        return default_strategy(fpga_part)

    return select_strategy


def batch_write_tcl_files(
    tcl_contents: Dict[str, str],
    output_dir: Union[str, Path],
    tcl_files_list: List[str],
    logger_instance: Optional[logging.Logger] = None,
) -> Dict[str, bool]:
    """
    Write multiple TCL files in batch with consistent error handling.

    Args:
        tcl_contents: Dict mapping filename to content
        output_dir: Directory to write files to
        tcl_files_list: List to append successful file paths to
        logger_instance: Logger to use (defaults to module logger)

    Returns:
        Dict mapping filename to success status

    Example:
        >>> contents = {
        ...     "project.tcl": "# Project setup",
        ...     "synthesis.tcl": "# Synthesis config"
        ... }
        >>> results = batch_write_tcl_files(contents, "output", [])
    """
    if logger_instance is None:
        logger_instance = logger

    output_dir = Path(output_dir)
    results = {}

    for filename, content in tcl_contents.items():
        file_path = output_dir / filename
        description = f"{filename.replace('.tcl', '')} TCL"

        success = write_tcl_file_with_logging(
            content, file_path, tcl_files_list, description, logger_instance
        )
        results[filename] = success

    # Log summary
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    logger_instance.info(
        f"Batch TCL write completed: {successful}/{total} files successful"
    )

    return results


def validate_fpga_part(fpga_part: str, known_parts: Optional[set] = None) -> bool:
    """
    Validate FPGA part string against known parts.

    Args:
        fpga_part: FPGA part string to validate
        known_parts: Optional set of known parts (defaults to constants.BOARD_PARTS values)

    Returns:
        True if valid, False otherwise
    """
    if known_parts is None:
        # Import here to avoid circular imports
        try:
            from constants import BOARD_PARTS

            known_parts = set(BOARD_PARTS.values())
        except ImportError:
            # Fallback to basic validation
            known_parts = set()

    if not fpga_part:
        return False

    # If we have known parts, check against them
    if known_parts and fpga_part in known_parts:
        return True

    # Basic format validation for Xilinx parts
    fpga_part_lower = fpga_part.lower()
    valid_prefixes = ["xc7a", "xc7k", "xc7v", "xczu", "xck", "xcvu"]

    return any(fpga_part_lower.startswith(prefix) for prefix in valid_prefixes)
