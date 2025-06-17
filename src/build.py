#!/usr/bin/env python3
# USB-required commit 2025-06-16
"""
PCILeech FPGA Firmware Builder - Production System

This is a complete, production-level build system for generating PCILeech DMA firmware
for various FPGA boards using donor device configuration space information obtained via VFIO.

Features:
- VFIO-based configuration space extraction
- Advanced SystemVerilog generation
- Manufacturing variance simulation
- Device-specific optimizations
- Behavior profiling
- MSI-X capability handling
- Option ROM management
- Configuration space shadowing

Usage:
  python3 build.py --bdf 0000:03:00.0 --board pcileech_35t325_x4

Boards:
  pcileech_35t325_x4  → Artix-7 35T (PCIeSquirrel)
  pcileech_75t        → Kintex-7 75T (PCIeEnigmaX1)
  pcileech_100t       → Zynq UltraScale+ (XilinxZDMA)
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Production mode configuration - defaults to production with all advanced features
PRODUCTION_MODE = os.getenv("PCILEECH_PRODUCTION_MODE", "true").lower() == "true"
ALLOW_MOCK_DATA = os.getenv("PCILEECH_ALLOW_MOCK_DATA", "false").lower() == "true"

# Add the src directory to Python path for proper module resolution
import sys
from pathlib import Path

# Get the directory containing this script
script_dir = Path(__file__).parent.absolute()
# Add it to Python path if not already there
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Also add the parent directory (app) to Python path for container compatibility
parent_dir = script_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# For container compatibility, also try adding common container paths
container_paths = ["/app", "/app/src"]
for path in container_paths:
    if Path(path).exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Import project modules with new helper functions
try:
    from device_clone.behavior_profiler import BehaviorProfiler
    from build_helpers import safe_import_with_fallback, write_tcl_file_with_logging
    from device_clone.config_space_manager import ConfigSpaceManager
    from device_clone.constants import (
        BOARD_PARTS,
        LEGACY_TCL_FILES,
        PRODUCTION_DEFAULTS,
    )
    from file_management.donor_dump_manager import DonorDumpManager
    from file_management.file_manager import FileManager
    from scripts.driver_scrape import extract_registers_with_analysis, validate_hex_id
    from scripts.kernel_utils import (
        ensure_kernel_source,
        find_driver_sources,
        resolve_driver_module,
    )
    from string_utils import (
        build_device_info_string,
        build_file_size_string,
        generate_tcl_header_comment,
        log_debug_safe,
        log_error_safe,
        log_info_safe,
        log_warning_safe,
        safe_format,
    )
    from templating.tcl_builder import TCLBuilder
    from templating.template_renderer import TemplateRenderer
    from device_clone.variance_manager import VarianceManager
    from vivado_handling import find_vivado_installation, run_vivado_command

except ImportError as import_error:
    if PRODUCTION_MODE:
        # In production mode, we must not fall back to basic functionality
        print(f"PRODUCTION ERROR: Failed to import required modules: {import_error}")
        print("Production mode requires all modules to be available.")
        print(f"Python path: {sys.path}")
        print(f"Script directory: {script_dir}")

        # Clean up output folder if it exists
        output_dir = Path("output")
        if output_dir.exists():
            try:
                import shutil

                shutil.rmtree(output_dir)
                print(f"Cleaned up output directory: {output_dir}")
            except Exception as cleanup_error:
                print(f"Warning: Failed to clean up output directory: {cleanup_error}")

        # Exit with error code
        sys.exit(1)

    print(f"Error importing required modules: {import_error}")
    print("Falling back to basic functionality...")
    # Manual fallback imports since safe_import_with_fallback is not available
    try:
        from device_clone.config_space_manager import ConfigSpaceManager
    except ImportError:
        ConfigSpaceManager = None

    try:
        from file_management.file_manager import FileManager
    except ImportError:
        print("Warning: FileManager could not be imported")
        FileManager = None

        try:
            from device_clone.variance_manager import VarianceManager
        except ImportError:
            VarianceManager = None

        try:
            from file_management.donor_dump_manager import DonorDumpManager
        except ImportError:
            DonorDumpManager = None

        try:
            from vivado_handling import find_vivado_installation
        except ImportError:
            find_vivado_installation = None

        # Import string utilities for fallback
    try:
        from string_utils import (
            build_device_info_string,
            build_file_size_string,
            generate_tcl_header_comment,
            log_debug_safe,
            log_error_safe,
            log_info_safe,
            log_warning_safe,
            safe_format,
        )
    except ImportError:
        print("Warning: string_utils could not be imported")

        # Define minimal fallback functions with proper signatures
        def log_error_safe(logger, template, **kwargs):
            """Fallback error logging function."""
            try:
                message = template.format(**kwargs) if kwargs else template
                print(f"ERROR: {message}")
            except Exception:
                print(f"ERROR: {template}")

        def log_info_safe(logger, template, **kwargs):
            """Fallback info logging function."""
            try:
                message = template.format(**kwargs) if kwargs else template
                print(f"INFO: {message}")
            except Exception:
                print(f"INFO: {template}")

        def log_warning_safe(logger, template, **kwargs):
            """Fallback warning logging function."""
            try:
                message = template.format(**kwargs) if kwargs else template
                print(f"WARNING: {message}")
            except Exception:
                print(f"WARNING: {template}")

        def log_debug_safe(logger, template, **kwargs):
            """Fallback debug logging function."""
            try:
                message = template.format(**kwargs) if kwargs else template
                print(f"DEBUG: {message}")
            except Exception:
                print(f"DEBUG: {template}")

        def safe_format(template, **kwargs):
            """Fallback safe formatting function."""
            try:
                return template.format(**kwargs)
            except Exception:
                return template

        def build_device_info_string(device_info):
            """Fallback device info string builder."""
            if isinstance(device_info, dict):
                vid = device_info["vendor_id"]
                did = device_info["device_id"]
                return f"VID:{vid}, DID:{did}"
            return "Device info unavailable"

        def build_file_size_string(size_bytes):
            """Fallback file size string builder."""
            if isinstance(size_bytes, int):
                if size_bytes < 1024:
                    return f"{size_bytes} bytes"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.1f} KB"
                else:
                    return f"{size_bytes / (1024 * 1024):.1f} MB"
            return "Size unavailable"

        def generate_tcl_header_comment(title, **kwargs):
            """Fallback TCL header comment generator."""
            lines = ["#" + "=" * 78, f"# {title}"]
            for key, value in kwargs.items():
                if value is not None:
                    display_key = key.replace("_", " ").title()
                    lines.append(f"# {display_key}: {value}")
            lines.append("#" + "=" * 78)
            return "\n".join(lines)


# Try to import advanced modules (optional)
try:
    from templating.advanced_sv_generator import AdvancedSVGenerator
except ImportError:
    AdvancedSVGenerator = None

try:
    from file_management.option_rom_manager import OptionROMManager
except ImportError:
    OptionROMManager = None


# Set up logging
def setup_logging(output_dir: Optional[Path] = None):
    """Set up logging with appropriate handlers."""

    class ColoredFormatter(logging.Formatter):
        """A logging formatter that adds ANSI color codes to log messages."""

        # ANSI color codes
        COLORS = {"RED": "\033[91m", "YELLOW": "\033[93m", "RESET": "\033[0m"}

        def __init__(self, fmt=None, datefmt=None):
            super().__init__(fmt, datefmt)
            # Only use colors for TTY outputs
            self.use_colors = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

        def format(self, record):
            formatted = super().format(record)
            if self.use_colors:
                if record.levelno >= logging.ERROR:
                    return f"{self.COLORS['RED']}{formatted}{self.COLORS['RESET']}"
                elif record.levelno >= logging.WARNING:
                    return f"{self.COLORS['YELLOW']}{formatted}{self.COLORS['RESET']}"
            return formatted

    # Create formatters
    colored_formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
    plain_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Set up console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(colored_formatter)
    handlers = [console_handler]

    # Add file handler if output directory exists
    if output_dir and output_dir.exists():
        log_file = output_dir / "build.log"
        file_handler = logging.FileHandler(str(log_file), mode="a")
        file_handler.setFormatter(plain_formatter)
        handlers.append(file_handler)
    elif os.path.exists("/app/output"):
        # Container environment
        file_handler = logging.FileHandler("/app/output/build.log", mode="a")
        file_handler.setFormatter(plain_formatter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=logging.INFO,
        handlers=handlers,
        force=True,  # Override any existing configuration
    )


# Initialize basic logging (will be reconfigured in main)
class ColoredFormatter(logging.Formatter):
    """A logging formatter that adds ANSI color codes to log messages."""

    # ANSI color codes
    COLORS = {"RED": "\033[91m", "YELLOW": "\033[93m", "RESET": "\033[0m"}

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        # Only use colors for TTY outputs
        self.use_colors = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def format(self, record):
        formatted = super().format(record)
        if self.use_colors:
            if record.levelno >= logging.ERROR:
                return f"{self.COLORS['RED']}{formatted}{self.COLORS['RESET']}"
            elif record.levelno >= logging.WARNING:
                return f"{self.COLORS['YELLOW']}{formatted}{self.COLORS['RESET']}"
        return formatted


colored_formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(colored_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler],
)
logger = logging.getLogger(__name__)


class PCILeechFirmwareBuilder:
    """Main firmware builder class with PCILeech as primary build pattern."""

    def __init__(self, bdf: str, board: str, output_dir: Optional[Path] = None):
        self.bdf = bdf
        self.board = board

        # Set output directory based on environment
        if output_dir:
            self.output_dir = output_dir
        elif os.path.exists("/app/output"):
            self.output_dir = Path("/app/output")
        else:
            self.output_dir = Path("./output")

        self.output_dir.mkdir(exist_ok=True)

        # Reconfigure logging with proper output directory
        setup_logging(self.output_dir)

        # Initialize PCILeech generator as primary build component
        try:
            from device_clone.pcileech_generator import (
                PCILeechGenerator,
                PCILeechGenerationConfig,
            )

            # Create PCILeech configuration
            pcileech_config = PCILeechGenerationConfig(
                device_bdf=bdf,
                device_profile="generic",
                enable_behavior_profiling=True,
                enable_manufacturing_variance=True,
                enable_advanced_features=True,
                template_dir=None,
                output_dir=self.output_dir,
                strict_validation=PRODUCTION_MODE,
                fail_on_missing_data=PRODUCTION_MODE,
            )

            # Initialize PCILeech generator as primary component
            self.pcileech_generator = PCILeechGenerator(pcileech_config)
            self.use_pcileech_primary = True

            logger.info(
                f"Initialized PCILeech generator as primary build pattern for {bdf}"
            )

        except ImportError as e:
            logger.warning(
                f"PCILeech generator not available, falling back to legacy build: {e}"
            )
            self.pcileech_generator = None
            self.use_pcileech_primary = False

        # Initialize legacy components for backward compatibility
        self.config_manager = ConfigSpaceManager(bdf) if ConfigSpaceManager else None

        # Initialize file manager with better error handling
        if FileManager:
            self.file_manager = FileManager(self.output_dir)
        else:
            self.file_manager = None
            logger.warning(
                "FileManager not available - some functionality will be limited"
            )

        self.variance_manager = (
            VarianceManager(bdf, self.output_dir) if VarianceManager else None
        )
        self.donor_manager = DonorDumpManager() if DonorDumpManager else None
        self.option_rom_manager = OptionROMManager() if OptionROMManager else None

        # Initialize template-based TCL builder with PCILeech support
        self.tcl_builder = TCLBuilder(output_dir=self.output_dir)

        logger.info(
            f"Initialized PCILeech firmware builder for {bdf} on {board} (PCILeech primary: {self.use_pcileech_primary})"
        )

    def read_vfio_config_space(self) -> bytes:
        """Read PCI configuration space via VFIO."""
        if not self.config_manager:
            raise RuntimeError(
                "Configuration space manager not available - cannot read VFIO config space"
            )
        return self.config_manager.read_vfio_config_space()

    def extract_device_info(self, config_space: bytes) -> Dict[str, Any]:
        """Extract device information from configuration space."""
        if self.config_manager:
            device_info = self.config_manager.extract_device_info(config_space)
            # Add board information
            device_info["board"] = self.board
            return device_info
        else:
            logger.error("Configuration space manager not available")
            raise RuntimeError(
                "Cannot extract device info without configuration manager"
            )

    def generate_systemverilog_files(
        self,
        device_info: Dict[str, Any],
        advanced_sv: bool = False,
        device_type: Optional[str] = None,
        enable_variance: bool = False,
    ) -> List[str]:
        """Generate SystemVerilog files for the firmware."""
        generated_files = []

        try:
            # Initialize and use templated SystemVerilog generation
            logger.info("Generating templated SystemVerilog modules")
            # Generate core SystemVerilog modules using templates
            if TemplateRenderer:
                template_renderer = TemplateRenderer()
            else:
                logger.error("TemplateRenderer not available")
                return generated_files

            # Generate basic SystemVerilog modules from templates
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

            # Prepare template context from device_info
            template_context = {
                "device_info": device_info,
                "vendor_id": device_info.get("vendor_id", 0x1234),
                "device_id": device_info.get("device_id", 0x5678),
                "subsystem_vendor_id": device_info.get("subsystem_vendor_id", 0x1234),
                "subsystem_device_id": device_info.get("subsystem_device_id", 0x5678),
                "class_code": device_info.get("class_code", 0x020000),
                "revision_id": device_info.get("revision_id", 0x00),
                "capabilities": device_info.get("capabilities", []),
                "bars": device_info.get("bars", []),
                "registers": device_info.get("registers", []),
            }

            # Generate each SystemVerilog module from templates
            for module_template in basic_modules:
                try:
                    module_content = template_renderer.render_template(
                        f"systemverilog/{module_template}", template_context
                    )

                    # Write generated module to output directory
                    module_name = module_template.replace(".j2", "")
                    output_path = self.output_dir / "src" / module_name
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(output_path, "w") as f:
                        f.write(module_content)

                    generated_files.append(str(output_path))
                    logger.info(
                        f"Generated templated SystemVerilog module: {module_name}"
                    )

                except Exception as e:
                    logger.warning(f"Failed to generate {module_template}: {e}")

            # Generate advanced SystemVerilog modules if requested
            if advanced_sv:
                logger.info("Generating advanced SystemVerilog modules")
                try:
                    # Generate advanced controller using template renderer directly
                    advanced_content = template_renderer.render_template(
                        "systemverilog/advanced/advanced_controller.sv.j2",
                        template_context,
                    )

                    # Write advanced controller
                    advanced_path = self.output_dir / "src" / "advanced_controller.sv"
                    with open(advanced_path, "w") as f:
                        f.write(advanced_content)

                    generated_files.append(str(advanced_path))
                    logger.info("Generated advanced SystemVerilog controller")

                except Exception as e:
                    logger.warning(f"Failed to generate advanced SystemVerilog: {e}")

            # Generate manufacturing variance if enabled
            if (
                enable_variance
                and self.variance_manager
                and self.variance_manager.is_variance_available()
            ):
                logger.info("Applying manufacturing variance simulation")
                variance_files = self.variance_manager.apply_manufacturing_variance(
                    device_info
                )
                generated_files.extend(variance_files)

        except Exception as e:
            logger.error(f"Error generating SystemVerilog files: {e}")
            raise

        return generated_files

    def _generate_separate_tcl_files(
        self, device_info: Dict[str, Any], enable_custom_config: bool = True
    ) -> List[str]:
        """Generate TCL files using PCILeech's 2-script approach with custom configuration space support."""
        tcl_files = []

        if self.tcl_builder:
            # Use PCILeech 2-script approach
            logger.info(
                "Using PCILeech 2-script TCL generation with custom configuration space support"
            )

            # Extract device information for context - require all values
            if "vendor_id" not in device_info:
                raise ValueError(
                    "vendor_id is required in device_info for device cloning"
                )
            if "device_id" not in device_info:
                raise ValueError(
                    "device_id is required in device_info for device cloning"
                )
            if "revision_id" not in device_info:
                raise ValueError(
                    "revision_id is required in device_info for device cloning"
                )

            vendor_id = device_info["vendor_id"]
            device_id = device_info["device_id"]
            revision_id = device_info["revision_id"]

            # Convert hex strings to integers if needed
            if isinstance(vendor_id, str):
                vendor_id = (
                    int(vendor_id, 16)
                    if vendor_id.startswith("0x")
                    else int(vendor_id, 16)
                )
            if isinstance(device_id, str):
                device_id = (
                    int(device_id, 16)
                    if device_id.startswith("0x")
                    else int(device_id, 16)
                )
            if isinstance(revision_id, str):
                revision_id = (
                    int(revision_id, 16)
                    if revision_id.startswith("0x")
                    else int(revision_id, 16)
                )

            # Get PCILeech board configuration for file lists
            try:
                from device_clone.board_config import get_pcileech_board_config

                pcileech_config = get_pcileech_board_config(self.board)
                source_files = pcileech_config.get("src_files", [])
                ip_files = pcileech_config.get("ip_files", [])
                coefficient_files = pcileech_config.get("coefficient_files", [])
            except (ImportError, KeyError) as e:
                logger.warning(f"Could not get PCILeech board config: {e}")
                source_files = []
                ip_files = []
                coefficient_files = []

            # Generate custom configuration space files if enabled
            if enable_custom_config:
                logger.info(
                    "Generating custom configuration space and BAR controller files"
                )
                custom_files = self._generate_custom_config_files(device_info)
                source_files.extend(custom_files)

            # Generate PCILeech scripts using the new 2-script approach
            results = self.tcl_builder.build_pcileech_scripts_only(
                board=self.board,
                vendor_id=vendor_id,
                device_id=device_id,
                revision_id=revision_id,
                source_files=source_files,
                constraint_files=None,  # Will be auto-discovered
                source_file_list=source_files,
                ip_file_list=ip_files,
                coefficient_file_list=coefficient_files,
                enable_custom_config=enable_custom_config,
            )

            # Get list of generated files - extract from results dictionary keys
            tcl_files = list(results.keys())

            # Log results
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            logger.info(
                f"PCILeech TCL generation: {successful}/{total} files successful"
            )
            logger.info(f"Generated PCILeech scripts: {tcl_files}")
        return tcl_files

    def _generate_custom_config_files(self, device_info: Dict[str, Any]) -> List[str]:
        """Generate custom configuration space and BAR controller files."""
        generated_files = []

        try:
            # Generate pcileech_fifo.sv with custom configuration space enabled
            fifo_content = self._generate_pcileech_fifo_sv(device_info)
            fifo_path = self.output_dir / "src" / "pcileech_fifo.sv"
            fifo_path.parent.mkdir(parents=True, exist_ok=True)
            with open(fifo_path, "w") as f:
                f.write(fifo_content)
            generated_files.append(str(fifo_path))
            logger.info(
                "Generated pcileech_fifo.sv with custom configuration space enabled"
            )

            # Generate pcileech_cfgspace.coe file
            coe_content = self._generate_config_space_coe(device_info)
            coe_path = self.output_dir / "ip" / "pcileech_cfgspace.coe"
            coe_path.parent.mkdir(parents=True, exist_ok=True)
            with open(coe_path, "w") as f:
                f.write(coe_content)
            generated_files.append(str(coe_path))
            logger.info(
                "Generated pcileech_cfgspace.coe with device-specific configuration"
            )

            # Generate enhanced BAR controller with custom PIO regions
            bar_controller_content = self._generate_enhanced_bar_controller(device_info)
            bar_path = self.output_dir / "src" / "pcileech_tlps128_bar_controller.sv"
            bar_path.parent.mkdir(parents=True, exist_ok=True)
            with open(bar_path, "w") as f:
                f.write(bar_controller_content)
            generated_files.append(str(bar_path))
            logger.info(
                "Generated enhanced BAR controller with custom PIO memory regions"
            )

        except Exception as e:
            logger.error(f"Error generating custom configuration files: {e}")
            raise

        return generated_files

    def _generate_pcileech_fifo_sv(self, device_info: Dict[str, Any]) -> str:
        """Generate pcileech_fifo.sv with custom configuration space enabled."""
        from templating.template_renderer import TemplateRenderer

        renderer = TemplateRenderer()

        # Extract device information
        vendor_id = device_info.get("vendor_id", 0x10EE)
        device_id = device_info.get("device_id", 0x0666)

        # Convert to hex strings for template
        vendor_id_hex = (
            f"{vendor_id:04x}"
            if isinstance(vendor_id, int)
            else vendor_id.replace("0x", "")
        )
        device_id_hex = (
            f"{device_id:04x}"
            if isinstance(device_id, int)
            else device_id.replace("0x", "")
        )

        # Create template context
        context = {
            "vendor_id": f"0x{vendor_id_hex}",
            "device_id": f"0x{device_id_hex}",
            "vendor_id_hex": vendor_id_hex,
            "device_id_hex": device_id_hex,
            "enable_custom_config": True,  # Always enable custom config space
            "fifo_depth": 512,
            "data_width": 128,
            "fifo_type": "block_ram",  # Use block RAM for better performance
            "fpga_family": "artix7",
            "enable_clock_crossing": True,
            "enable_scatter_gather": True,
            "enable_interrupt": True,
            "enable_performance_counters": True,
            "enable_error_detection": True,
            "device_specific_config": {
                # PCILeech specific configuration bits
                "4": "1",  # Enable memory access
                "5": "1",  # Enable I/O access
                "6": "1",  # Enable bus master
                "7": "0",  # Disable special cycles
                "8": "1",  # Enable memory write and invalidate
                "9": "0",  # Disable VGA palette snoop
                "10": "0",  # Disable parity error response
                "11": "0",  # Disable address/data stepping
                "12": "0",  # Disable SERR
                "13": "1",  # Enable fast back-to-back
                "14": "0",  # Disable interrupt
            },
        }

        return renderer.render_template("systemverilog/pcileech_fifo.sv.j2", context)

    def _generate_config_space_coe(self, device_info: Dict[str, Any]) -> str:
        """Generate pcileech_cfgspace.coe file with device-specific configuration."""
        vendor_id = device_info.get("vendor_id", 0x10EE)
        device_id = device_info.get("device_id", 0x0666)
        revision_id = device_info.get("revision_id", 0x00)
        class_code = device_info.get("class_code", 0x020000)

        coe_content = f"""memory_initialization_radix=16;
memory_initialization_vector=
{device_id:04x}{vendor_id:04x},
0000{class_code:06x},
00000000,
00000000,
00000000,
00000000,
00000000,
00000000,
00000000,
00000000,
00000000,
00000000,
00000000,
00000000,
00000000,
00000000;
"""
        return coe_content

    def _generate_enhanced_bar_controller(self, device_info: Dict[str, Any]) -> str:
        """Generate enhanced BAR controller with custom PIO memory regions."""
        if TemplateRenderer:
            template_renderer = TemplateRenderer()

            # Enhanced template context with custom PIO support
            template_context = {
                "device_info": device_info,
                "vendor_id": device_info.get("vendor_id", 0x10EE),
                "device_id": device_info.get("device_id", 0x0666),
                "BAR_APERTURE_SIZE": 131072,  # 128KB
                "NUM_MSIX": 32,
                "MSIX_TABLE_BIR": 0,
                "MSIX_TABLE_OFFSET": 0x1000,
                "MSIX_PBA_BIR": 0,
                "MSIX_PBA_OFFSET": 0x2000,
                "CONFIG_SHDW_HI": "20'hFFFFE",
                "CUSTOM_WIN_BASE": "20'hFFFFC",
                "USE_BYTE_ENABLES": True,
                "ENABLE_CUSTOM_PIO": True,
                "CUSTOM_PIO_REGIONS": [
                    {"name": "device_control", "offset": 0x0000, "size": 0x100},
                    {"name": "status_regs", "offset": 0x0100, "size": 0x100},
                    {"name": "data_buffer", "offset": 0x0200, "size": 0x200},
                ],
            }

            try:
                return template_renderer.render_template(
                    "systemverilog/bar_controller.sv.j2", template_context
                )
            except Exception as e:
                logger.warning(f"Failed to use template renderer: {e}")
                # Fall back to basic implementation
                pass

        # Fallback implementation if template renderer fails
        return self._generate_basic_bar_controller(device_info)

    def _generate_basic_bar_controller(self, device_info: Dict[str, Any]) -> str:
        """Generate basic BAR controller using template."""
        if TemplateRenderer:
            template_renderer = TemplateRenderer()
            template_context = {
                "device_info": device_info,
            }

            try:
                return template_renderer.render_template(
                    "systemverilog/basic_bar_controller.sv.j2", template_context
                )
            except Exception as e:
                logger.warning(f"Failed to use basic template renderer: {e}")
                # Fall back to hardcoded implementation if template fails
                pass

    def run_behavior_profiling(
        self, device_info: Dict[str, Any], duration: int = 30
    ) -> Optional[str]:
        """Run behavior profiling if available."""
        if self.variance_manager and self.variance_manager.is_profiling_available():
            return self.variance_manager.run_behavior_profiling(device_info, duration)
        else:
            logger.warning("Behavior profiler not available")
            return None

    def generate_build_files(
        self, device_info: Dict[str, Any], enable_custom_config: bool = True
    ) -> List[str]:
        """Generate separate build files (TCL scripts, makefiles, etc.) with custom configuration space support."""
        build_files = []

        # Clean up any old unified TCL files first
        old_unified_files = [
            self.output_dir / legacy_file for legacy_file in LEGACY_TCL_FILES
        ]
        for old_file in old_unified_files:
            if old_file.exists():
                old_file.unlink()
                logger.info(f"Removed old unified file: {old_file.name}")

        # Generate separate TCL files using enhanced template system with custom config support
        tcl_files = self._generate_separate_tcl_files(device_info, enable_custom_config)
        build_files.extend(tcl_files)

        # Generate project file
        if self.file_manager:
            project_file = self.file_manager.generate_project_file(
                device_info, self.board
            )
            # Update features based on available components
            project_file["features"]["advanced_sv"] = AdvancedSVGenerator is not None
            project_file["features"]["manufacturing_variance"] = (
                self.variance_manager is not None
                and self.variance_manager.is_variance_available()
            )
            project_file["features"]["behavior_profiling"] = (
                self.variance_manager is not None
                and self.variance_manager.is_profiling_available()
            )

            proj_file = self.output_dir / "firmware_project.json"
            with open(proj_file, "w") as f:
                json.dump(project_file, f, indent=2)
            build_files.append(str(proj_file))

            # Generate file manifest for verification
            manifest = self.file_manager.generate_file_manifest(device_info, self.board)
            manifest_file = self.output_dir / "file_manifest.json"
            with open(manifest_file, "w") as f:
                json.dump(manifest, f, indent=2)
            build_files.append(str(manifest_file))
        else:
            logger.warning("File manager not available")

        logger.info(f"Generated {len(build_files)} build files")
        return build_files

    def build_firmware(
        self,
        advanced_sv: bool = False,
        device_type: Optional[str] = None,
        enable_variance: bool = False,
        behavior_profile_duration: int = 30,
        enable_ft601: bool = False,
        enable_custom_config: bool = True,
    ) -> Dict[str, Any]:
        """Main firmware build process with PCILeech as primary generation path."""
        logger.info("Starting PCILeech-first firmware build process")
        build_results = {
            "success": False,
            "files_generated": [],
            "errors": [],
            "build_time": 0,
            "custom_config_enabled": enable_custom_config,
            "pcileech_primary": self.use_pcileech_primary,
        }

        start_time = time.time()

        try:
            # Use PCILeech generator as primary build path
            if self.use_pcileech_primary and self.pcileech_generator:
                logger.info("Using PCILeech generator as primary build path")

                # Generate complete PCILeech firmware
                pcileech_result = self.pcileech_generator.generate_pcileech_firmware()

                # Extract generated files from PCILeech result
                if "systemverilog_modules" in pcileech_result:
                    sv_modules = pcileech_result["systemverilog_modules"]
                    for module_name, module_content in sv_modules.items():
                        output_path = self.output_dir / "src" / f"{module_name}.sv"
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        with open(output_path, "w") as f:
                            f.write(module_content)

                        build_results["files_generated"].append(str(output_path))
                        logger.info(
                            f"Generated PCILeech SystemVerilog module: {module_name}"
                        )

                # Generate PCILeech-specific TCL scripts
                if "firmware_components" in pcileech_result:
                    template_context = pcileech_result.get("template_context", {})
                    pcileech_tcl_files = self._generate_pcileech_tcl_scripts(
                        template_context
                    )
                    build_results["files_generated"].extend(pcileech_tcl_files)

                # Save PCILeech generation result
                self.pcileech_generator.save_generated_firmware(
                    pcileech_result, self.output_dir
                )

                # Extract device info from PCILeech result for compatibility
                device_info = pcileech_result.get("config_space_data", {}).get(
                    "device_info", {}
                )

            else:
                # Fallback to legacy build system for backward compatibility
                logger.info("Using legacy build system (PCILeech not available)")

                # Step 1: Read configuration space
                logger.info("Step 1: Reading device configuration space")
                config_space = self.read_vfio_config_space()

                # Step 2: Extract device information
                logger.info("Step 2: Extracting device information")
                device_info = self.extract_device_info(config_space)

                # Step 3: Generate SystemVerilog files
                logger.info("Step 3: Generating SystemVerilog files")
                sv_files = self.generate_systemverilog_files(
                    device_info, advanced_sv, device_type, enable_variance
                )
                build_results["files_generated"].extend(sv_files)

                # Step 4: Run behavior profiling if requested
                if behavior_profile_duration > 0:
                    logger.info("Step 4: Running behavior profiling")
                    profile_file = self.run_behavior_profiling(
                        device_info, behavior_profile_duration
                    )
                    if profile_file:
                        build_results["files_generated"].append(profile_file)

                # Step 5: Generate build files with custom configuration space support
                logger.info(
                    "Step 5: Generating build files with custom configuration space support"
                )
                build_files = self.generate_build_files(
                    device_info, enable_custom_config
                )
                build_results["files_generated"].extend(build_files)

            # Step 6: Save device info
            device_info_file = self.output_dir / "device_info.json"
            with open(device_info_file, "w") as f:
                json.dump(device_info, f, indent=2)
            build_results["files_generated"].append(str(device_info_file))

            # Step 7: Clean up intermediate files
            logger.info("Step 7: Cleaning up intermediate files")
            if self.file_manager:
                preserved_files = self.file_manager.cleanup_intermediate_files()
            else:
                preserved_files = []
                logger.warning("File manager not available for cleanup")

            # Step 8: Validate final outputs
            logger.info("Step 8: Validating final outputs")
            if self.file_manager:
                validation_results = self.file_manager.validate_final_outputs()
            else:
                validation_results = {
                    "validation_status": "error",
                    "build_mode": "unknown",
                }
                logger.warning("File manager not available for validation")

            build_results["success"] = True
            build_results["build_time"] = time.time() - start_time
            build_results["preserved_files"] = preserved_files
            build_results["validation"] = validation_results

            logger.info("Build completed successfully")
            logger.info(f"Build time: {build_results['build_time']:.2f} seconds")
            logger.info(f"Generated {len(build_results['files_generated'])} files")
            logger.info(f"Preserved {len(preserved_files)} final output files")

            # Print detailed validation information
            if self.file_manager:
                self.file_manager.print_final_output_info(validation_results)
            else:
                logger.warning("File manager not available for output info display")

        except Exception as e:
            error_msg = f"Build failed: {e}"
            logger.error(error_msg)
            build_results["errors"].append(error_msg)
            build_results["build_time"] = time.time() - start_time

        return build_results

    def _generate_pcileech_tcl_scripts(
        self, template_context: Dict[str, Any]
    ) -> List[str]:
        """Generate PCILeech-specific TCL scripts using the template context."""
        tcl_files = []

        try:
            # Generate PCILeech project setup script
            project_script_content = self.tcl_builder.build_pcileech_project_script(
                self._build_context_from_template_context(template_context)
            )
            project_script_path = self.output_dir / "vivado_generate_project.tcl"
            with open(project_script_path, "w") as f:
                f.write(project_script_content)
            tcl_files.append(str(project_script_path))
            logger.info("Generated PCILeech project setup script")

            # Generate PCILeech build script
            build_script_content = self.tcl_builder.build_pcileech_build_script(
                self._build_context_from_template_context(template_context)
            )
            build_script_path = self.output_dir / "vivado_build.tcl"
            with open(build_script_path, "w") as f:
                f.write(build_script_content)
            tcl_files.append(str(build_script_path))
            logger.info("Generated PCILeech build script")

        except Exception as e:
            logger.warning(f"Failed to generate PCILeech TCL scripts: {e}")
            # Fallback to legacy TCL generation
            try:
                device_info = template_context.get("device_info", {})
                legacy_tcl_files = self.generate_build_files(device_info)
                tcl_files.extend(legacy_tcl_files)
            except Exception as fallback_error:
                logger.error(f"Legacy TCL generation also failed: {fallback_error}")

        return tcl_files

    def _build_context_from_template_context(self, template_context: Dict[str, Any]):
        """Build TCL builder context from PCILeech template context."""
        from templating.tcl_builder import BuildContext

        device_info = template_context.get("device_info", {})

        return BuildContext(
            board_name=self.board,
            fpga_part=template_context.get("fpga_part", "xc7a35tcsg324-2"),
            fpga_family=template_context.get("fpga_family", "Artix-7"),
            pcie_ip_type=template_context.get("pcie_ip_type", "pcie7x"),
            max_lanes=template_context.get("max_lanes", 4),
            supports_msi=template_context.get("supports_msi", True),
            supports_msix=template_context.get("supports_msix", True),
            vendor_id=device_info.get("vendor_id"),
            device_id=device_info.get("device_id"),
            revision_id=device_info.get("revision_id"),
            class_code=device_info.get("class_code"),
            project_name="pcileech_firmware",
            project_dir="./vivado_project",
            output_dir=str(self.output_dir),
        )


def validate_production_mode() -> None:
    """Validate production mode configuration and prevent mock data usage."""
    if PRODUCTION_MODE and ALLOW_MOCK_DATA:
        raise RuntimeError(
            "CRITICAL: Production mode is enabled but mock data is allowed. "
            "Set PCILEECH_ALLOW_MOCK_DATA=false for production builds."
        )

    if PRODUCTION_MODE:
        logger.info("Production mode enabled - mock implementations disabled")
    else:
        logger.warning("Development mode - mock implementations may be used")


def _execute_vivado_build(preserved_files: List[str]) -> bool:
    """
    Execute Vivado build using the generated TCL scripts.

    Args:
        preserved_files: List of preserved files from the build

    Returns:
        True if Vivado build succeeded, False otherwise
    """
    try:
        from vivado_handling import (
            find_vivado_installation,
            run_vivado_with_error_reporting,
        )
        from pathlib import Path

        # Find Vivado installation
        vivado_info = find_vivado_installation()
        if not vivado_info:
            print("[✗] Vivado installation not found")
            print("    Please ensure Vivado is installed and in PATH")
            return False

        print(f"[*] Found Vivado: {vivado_info['version']} at {vivado_info['path']}")

        # Look for TCL build script in preserved files
        build_script = None
        output_dir = Path("output")

        # Check for PCILeech build script first
        pcileech_build_script = output_dir / "vivado_build.tcl"
        if pcileech_build_script.exists():
            build_script = pcileech_build_script
        else:
            # Look for any TCL build script
            for file_path in preserved_files:
                if file_path.endswith(".tcl") and (
                    "build" in file_path.lower() or "impl" in file_path.lower()
                ):
                    build_script = Path(file_path)
                    break

        if not build_script or not build_script.exists():
            print("[✗] No Vivado build script found")
            print("    Expected: vivado_build.tcl or similar build script")
            return False

        print(f"[*] Using build script: {build_script}")

        # Run Vivado with error reporting
        try:
            return_code, report = run_vivado_with_error_reporting(
                build_script, output_dir, vivado_info["executable"]
            )

            if return_code == 0:
                print("[✓] Vivado synthesis and implementation completed successfully")

                # Check for generated bitstream
                bitstream_files = list(output_dir.glob("*.bit"))
                if bitstream_files:
                    print(f"[✓] Generated bitstream: {bitstream_files[0]}")
                else:
                    print("[!] Warning: No bitstream file found")

                return True
            else:
                print(f"[✗] Vivado build failed with return code: {return_code}")
                if report:
                    print(f"[!] Error report saved to: {report}")
                return False

        except Exception as vivado_error:
            print(f"[✗] Vivado execution failed: {vivado_error}")
            return False

    except ImportError as e:
        print(f"[✗] Failed to import Vivado handling modules: {e}")
        print("    Please ensure vivado_handling module is available")
        return False
    except Exception as e:
        print(f"[✗] Unexpected error during Vivado execution: {e}")
        return False


def main():
    """Main entry point for the build system."""
    parser = argparse.ArgumentParser(
        description="PCILeech FPGA Firmware Builder - Production System"
    )
    parser.add_argument(
        "--bdf", required=True, help="Bus:Device.Function (e.g., 0000:03:00.0)"
    )
    parser.add_argument("--board", required=True, help="Target board")
    parser.add_argument(
        "--advanced-sv",
        action="store_true",
        default=PRODUCTION_DEFAULTS["ADVANCED_SV"],
        help="Enable advanced SystemVerilog generation (default: enabled in production mode)",
    )
    parser.add_argument(
        "--disable-advanced-sv",
        action="store_true",
        help="Disable advanced SystemVerilog generation",
    )
    parser.add_argument(
        "--device-type",
        default=PRODUCTION_DEFAULTS["DEFAULT_DEVICE_TYPE"],
        help=f"Device type for optimizations (network, audio, storage, etc.) (default: {PRODUCTION_DEFAULTS['DEFAULT_DEVICE_TYPE']})",
    )
    parser.add_argument(
        "--enable-variance",
        action="store_true",
        default=PRODUCTION_DEFAULTS["MANUFACTURING_VARIANCE"],
        help="Enable manufacturing variance simulation (default: enabled in production mode)",
    )
    parser.add_argument(
        "--disable-variance",
        action="store_true",
        help="Disable manufacturing variance simulation",
    )
    parser.add_argument(
        "--behavior-profile-duration",
        type=int,
        default=30,
        help="Duration for behavior profiling in seconds (0 to disable)",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--enable-ft601",
        action="store_true",
        help="Enable FT601 USB-3 capture functionality",
    )
    parser.add_argument(
        "--enable-custom-config",
        action="store_true",
        default=True,
        help="Enable custom configuration space and BAR PIO memory regions (default: enabled)",
    )
    parser.add_argument(
        "--disable-custom-config",
        action="store_true",
        help="Disable custom configuration space functionality",
    )
    parser.add_argument(
        "--run-vivado",
        action="store_true",
        help="Automatically run Vivado synthesis and implementation after generating TCL scripts",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle disable flags to override defaults
    if hasattr(args, "disable_advanced_sv") and args.disable_advanced_sv:
        args.advanced_sv = False
    if hasattr(args, "disable_variance") and args.disable_variance:
        args.enable_variance = False
    if hasattr(args, "disable_custom_config") and args.disable_custom_config:
        args.enable_custom_config = False

    # Validate production mode configuration before proceeding
    validate_production_mode()

    try:
        # Initialize builder
        builder = PCILeechFirmwareBuilder(args.bdf, args.board)

        # Run enhanced build process with custom configuration space support
        results = builder.build_firmware(
            advanced_sv=args.advanced_sv,
            device_type=args.device_type,
            enable_variance=args.enable_variance,
            behavior_profile_duration=args.behavior_profile_duration,
            enable_ft601=args.enable_ft601,
            enable_custom_config=args.enable_custom_config,
        )

        # Print results
        if results["success"]:
            print(
                safe_format(
                    "[✓] Build completed successfully in {build_time:.2f} seconds",
                    build_time=results["build_time"],
                )
            )

            # Show preserved files (final outputs)
            if "preserved_files" in results and results["preserved_files"]:
                print(f"[✓] Final output files ({len(results['preserved_files'])}):")
                for file_path in results["preserved_files"]:
                    print(f"    - {file_path}")

            # Validation results are already printed by
            # _print_final_output_info
            if "preserved_files" in results:
                # Check if we should run Vivado automatically
                if hasattr(args, "run_vivado") and args.run_vivado:
                    print("[*] Running Vivado synthesis and implementation...")
                    vivado_success = _execute_vivado_build(results["preserved_files"])
                    if vivado_success:
                        print("[✓] Vivado build completed successfully")
                        return 0
                    else:
                        print("[✗] Vivado build failed")
                        return 1
                else:
                    print("Now run vivado with the following command:")
                    print(
                        safe_format(
                            "cd output/ && vivado -mode batch -source build.tcl -lic_retry 30 -lic_retry_int 60",
                        )
                    )
                    print("Or do whatever you want with the tcl pz")

            return 0
        else:
            print(
                safe_format(
                    "[✗] Build failed after {build_time:.2f} seconds",
                    build_time=results["build_time"],
                )
            )
            for error in results["errors"]:
                print(f"    Error: {error}")
            return 1

    except KeyboardInterrupt:
        print("\n[!] Build interrupted by user")
        return 130
    except Exception as e:
        print(f"[✗] Fatal error: {e}")
        logger.exception("Fatal error during build")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# =============================================================================
# BACKWARD COMPATIBILITY API
# =============================================================================
# These functions provide backward compatibility with the test suite
# by bridging the class-based implementation with the expected functional API

import subprocess
import tempfile
from typing import Tuple, Union

# Constants expected by tests
BOARD_INFO = {
    "35t": {"root": "xc7a35tcsg324-2"},
    "75t": {"root": "xc7k70tfbg676-2"},
    "100t": {"root": "xczu7ev-ffvc1156-2-e"},
    "pcileech_75t484_x1": {"root": "xc7k70tfbg484-2"},
    "pcileech_35t484_x1": {"root": "xc7a35tfgg484-2"},
    "pcileech_35t325_x4": {"root": "xc7a35tcsg324-2"},
    "pcileech_35t325_x1": {"root": "xc7a35tcsg324-2"},
    "pcileech_100t484_x1": {"root": "xczu7ev-ffvc1156-2-e"},
    "pcileech_enigma_x1": {"root": "xc7k70tfbg676-2"},
    "pcileech_squirrel": {"root": "xc7a35tcsg324-2"},
    "pcileech_pciescreamer_xc7a35": {"root": "xc7a35tcsg324-2"},
}

APERTURE = {1024: "1_KB", 65536: "64_KB", 16777216: "16_MB"}

# Byte count to code mapping for TCL generation
_BYTE_CODE_MAPPING = {128: 0, 256: 1, 512: 2, 1024: 3, 2048: 4, 4096: 5}


def code_from_bytes(byte_count: int) -> int:
    """Convert byte count to code for TCL generation."""
    if byte_count not in _BYTE_CODE_MAPPING:
        raise KeyError(f"Unsupported byte count: {byte_count}")
    return _BYTE_CODE_MAPPING[byte_count]


def build_tcl(donor_info: Dict[str, Any], output_file: str) -> Tuple[str, str]:
    """Generate TCL content using the refactored system."""
    try:
        # Create a temporary builder instance
        builder = PCILeechFirmwareBuilder(
            bdf="0000:03:00.0", board="pcileech_35t325_x4"
        )

        # Generate TCL files using the new system
        tcl_files = builder._generate_separate_tcl_files(donor_info)

        # For backward compatibility, return the first generated file content
        if tcl_files:
            tcl_file_path = Path(tcl_files[0])
            if tcl_file_path.exists():
                content = tcl_file_path.read_text()
                return content, str(tcl_file_path)

        # If no TCL files were generated, raise an error
        raise RuntimeError("No TCL files were generated")

    except Exception as e:
        raise RuntimeError(f"Failed to generate TCL content: {e}") from e


def scrape_driver_regs(
    vendor_id: str, device_id: str
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Scrape driver registers using real implementation only."""
    logger.info(f"Real driver scraping for {vendor_id}:{device_id}")

    # Validate hex IDs
    validated_vendor = validate_hex_id(vendor_id, "Vendor ID")
    validated_device = validate_hex_id(device_id, "Device ID")

    # Resolve driver module
    driver_name = resolve_driver_module(validated_vendor, validated_device)
    if not driver_name:
        raise RuntimeError(f"No driver found for {vendor_id}:{device_id}")

    # Ensure kernel source is available
    kernel_source_dir = ensure_kernel_source()
    if not kernel_source_dir:
        raise RuntimeError("Kernel source not available for driver analysis")

    # Find driver sources
    source_files = find_driver_sources(kernel_source_dir, driver_name)
    if not source_files:
        raise RuntimeError(f"No source files found for driver {driver_name}")

    # Extract registers with analysis
    analysis_result = extract_registers_with_analysis(source_files, driver_name)

    # Convert to expected format
    registers = []
    for reg_data in analysis_result.get("registers", []):
        registers.append(
            {
                "name": reg_data["name"],
                "offset": reg_data["offset"],
                "value": reg_data["value"],
                "access": reg_data["rw"].upper(),
            }
        )

    # Extract state machine information
    state_machine = {
        "states": ["IDLE", "ACTIVE", "RESET"],  # Default states
        "transitions": [],
    }

    # Add state machine data if available
    if "state_machines" in analysis_result:
        sm_data = analysis_result["state_machines"]
        if sm_data:
            state_machine.update(sm_data[0])  # Use first state machine

    logger.info(
        f"Successfully scraped {len(registers)} registers from driver {driver_name}"
    )
    return registers, state_machine


def integrate_behavior_profile(
    bdf: str, registers: List[Dict[str, Any]], duration: float = 30.0
) -> List[Dict[str, Any]]:
    """Integrate behavior profiling data with registers using real implementation only."""
    logger.info(f"Real behavior profiling for {bdf} over {duration}s")

    # Use real behavior profiler
    profiler = BehaviorProfiler(bdf=bdf)
    behavior_profile = profiler.capture_behavior_profile(duration=duration)

    # Integrate real profiling data with registers
    enhanced_registers = []
    for reg in registers:
        enhanced_reg = reg.copy()

        # Find matching register access data
        reg_name = reg["name"]
        reg_offset = reg["offset"]

        # Extract timing data from behavior profile
        timing_data = {
            "read_latency": 100,  # Default fallback
            "write_latency": 150,
            "access_frequency": 1000,
        }

        # Look for register-specific timing in captured accesses
        for access in behavior_profile.register_accesses:
            if access.register == reg_name or access.offset == reg_offset:
                if access.duration_us:
                    if access.operation == "read":
                        timing_data["read_latency"] = int(
                            access.duration_us * 1000
                        )  # Convert to ns
                    elif access.operation == "write":
                        timing_data["write_latency"] = int(access.duration_us * 1000)

        # Calculate access frequency from timing patterns
        for pattern in behavior_profile.timing_patterns:
            if reg_name in pattern.registers:
                timing_data["access_frequency"] = int(pattern.frequency_hz)
                break

        enhanced_reg["timing"] = timing_data
        enhanced_reg["behavior_confidence"] = getattr(
            behavior_profile, "confidence", 0.8
        )
        enhanced_registers.append(enhanced_reg)

    logger.info(
        f"Successfully integrated behavior profile with {len(enhanced_registers)} registers"
    )
    return enhanced_registers


def run(command: str) -> None:
    """Run a shell command."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        logger.info(f"Command executed successfully: {command}")
        logger.info(f"Command executed successfully: {command}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        raise


def create_secure_tempfile(suffix: str = "", prefix: str = "pcileech_") -> str:
    """Create a secure temporary file."""
    try:
        with tempfile.NamedTemporaryFile(
            suffix=suffix, prefix=prefix, delete=False
        ) as tmp:
            return tmp.name
    except Exception as e:
        logger.error(f"Error creating secure tempfile: {e}")
        raise


# Additional compatibility functions can be added here as needed

if __name__ == "__main__":
    main()
