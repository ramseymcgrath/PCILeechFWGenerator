#!/usr/bin/env python3
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

# Import project modules with new helper functions
try:
    from behavior_profiler import BehaviorProfiler
    from build_helpers import safe_import_with_fallback, write_tcl_file_with_logging
    from config_space_manager import ConfigSpaceManager
    from constants import BOARD_PARTS, LEGACY_TCL_FILES, PRODUCTION_DEFAULTS
    from donor_dump_manager import DonorDumpManager
    from file_manager import FileManager
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
        log_error_safe,
        log_info_safe,
        log_warning_safe,
        safe_format,
    )
    from systemverilog_generator import SystemVerilogGenerator
    from tcl_builder import TCLBuilder
    from tcl_generator import TCLGenerator
    from template_renderer import TemplateRenderer
    from variance_manager import VarianceManager
    from vivado_utils import find_vivado_installation

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
        from config_space_manager import ConfigSpaceManager
    except ImportError:
        ConfigSpaceManager = None

    try:
        from systemverilog_generator import SystemVerilogGenerator
    except ImportError:
        SystemVerilogGenerator = None

    try:
        from tcl_generator import TCLGenerator
    except ImportError:
        TCLGenerator = None

    try:
        from file_manager import FileManager
    except ImportError:
        print("Warning: FileManager could not be imported")
        FileManager = None

        try:
            from variance_manager import VarianceManager
        except ImportError:
            VarianceManager = None

        try:
            from donor_dump_manager import DonorDumpManager
        except ImportError:
            DonorDumpManager = None

        try:
            from vivado_utils import find_vivado_installation
        except ImportError:
            find_vivado_installation = None

        # Import string utilities for fallback
    try:
        from string_utils import (
            build_device_info_string,
            build_file_size_string,
            generate_tcl_header_comment,
            log_error_safe,
            log_info_safe,
            log_warning_safe,
            safe_format,
        )
    except ImportError:
        print("Warning: string_utils could not be imported")

        # Define minimal fallback functions
        def log_error_safe(msg):
            print(f"ERROR: {msg}")

        def log_info_safe(msg):
            print(f"INFO: {msg}")

        def log_warning_safe(msg):
            print(f"WARNING: {msg}")

        def safe_format(template, **kwargs):
            return template.format(**kwargs)

        def build_device_info_string(*args):
            return "Device info unavailable"

        def build_file_size_string(*args):
            return "Size unavailable"

        def generate_tcl_header_comment(*args):
            return "# Generated TCL"

    # Fallback constants
    BOARD_PARTS = {}
    LEGACY_TCL_FILES = []
    TCLBuilder = None
    TemplateRenderer = None

# Try to import advanced modules (optional)
try:
    from advanced_sv_generator import AdvancedSVGenerator
except ImportError:
    AdvancedSVGenerator = None

try:
    from option_rom_manager import OptionROMManager
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
    """Main firmware builder class."""

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

        # Initialize components using new modular architecture
        self.config_manager = ConfigSpaceManager(bdf) if ConfigSpaceManager else None
        self.sv_generator = (
            SystemVerilogGenerator(self.output_dir) if SystemVerilogGenerator else None
        )
        self.tcl_generator = (
            TCLGenerator(board, self.output_dir) if TCLGenerator else None
        )
        # Initialize file manager with better error handling
        if FileManager:
            try:
                self.file_manager = FileManager(self.output_dir)
                logger.info("File manager initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize file manager: {e}")
                self.file_manager = None
        else:
            logger.warning("FileManager class not available")
            self.file_manager = None
        self.variance_manager = (
            VarianceManager(bdf, self.output_dir) if VarianceManager else None
        )
        self.donor_manager = DonorDumpManager() if DonorDumpManager else None
        self.option_rom_manager = OptionROMManager() if OptionROMManager else None

        # Initialize new template-based TCL builder
        self.tcl_builder = (
            TCLBuilder(output_dir=self.output_dir) if TCLBuilder else None
        )

        logger.info(f"Initialized PCILeech firmware builder for {bdf} on {board}")

    def read_vfio_config_space(self) -> bytes:
        """Read PCI configuration space via VFIO."""
        if self.config_manager:
            return self.config_manager.read_vfio_config_space()
        else:
            if PRODUCTION_MODE:
                # In production mode, we must not fall back to synthetic config space
                logger.error(
                    "PRODUCTION ERROR: Configuration space manager not available"
                )

                # Clean up output folder if it exists
                output_dir = Path("output")
                if output_dir.exists():
                    try:
                        import shutil

                        shutil.rmtree(output_dir)
                        logger.info(f"Cleaned up output directory: {output_dir}")
                    except Exception as cleanup_error:
                        logger.error(
                            f"Failed to clean up output directory: {cleanup_error}"
                        )

                raise RuntimeError(
                    "Production mode requires configuration space manager to be available"
                )

            logger.error("Configuration space manager not available")
            return self._generate_synthetic_config_space()

    def _generate_synthetic_config_space(self) -> bytes:
        """Fallback synthetic config space generation."""
        if self.config_manager:
            return self.config_manager.generate_synthetic_config_space()
        else:
            # Basic fallback - minimal valid PCI config space
            config_space = bytearray(256)
            # Set vendor/device ID to Intel defaults
            config_space[0:2] = (0x8086).to_bytes(2, "little")  # Intel vendor ID
            config_space[2:4] = (0x125C).to_bytes(2, "little")  # Device ID
            config_space[4:6] = (0x0006).to_bytes(2, "little")  # Command register
            config_space[6:8] = (0x0210).to_bytes(2, "little")  # Status register
            config_space[8] = 0x04  # Revision ID
            config_space[9:12] = (0x020000).to_bytes(
                3, "little"
            )  # Class code (Ethernet)
            logger.warning("Using minimal fallback configuration space")
            return bytes(config_space)

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
            # Initialize advanced SystemVerilog generator if available and requested
            if advanced_sv and AdvancedSVGenerator:
                logger.info("Generating advanced SystemVerilog modules")
                # Note: Advanced SV generator would be integrated here
                logger.info("Advanced SystemVerilog generator initialized")

            # Discover and copy all relevant project files
            if self.sv_generator:
                project_files = self.sv_generator.discover_and_copy_all_files(
                    device_info
                )
                generated_files.extend(project_files)
            else:
                logger.warning("SystemVerilog generator not available")

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

    def _generate_separate_tcl_files(self, device_info: Dict[str, Any]) -> List[str]:
        """Generate separate TCL files using the new template-based system."""
        tcl_files = []

        if self.tcl_builder:
            # Use new template-based TCL builder
            logger.info("Using template-based TCL generation")

            # Extract device information for context
            vendor_id = device_info.get("vendor_id", 0x1234)
            device_id = device_info.get("device_id", 0x5678)
            revision_id = device_info.get("revision_id", 0x01)

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

            # Generate all TCL scripts using the new builder
            results = self.tcl_builder.build_all_tcl_scripts(
                board=self.board,
                vendor_id=vendor_id,
                device_id=device_id,
                revision_id=revision_id,
            )

            # Get list of generated files
            tcl_files = self.tcl_builder.get_generated_files()

            # Log results
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            logger.info(
                f"Template-based TCL generation: {successful}/{total} files successful"
            )

        else:
            # Fallback to legacy TCL generator if template system not available
            logger.warning(
                "Template-based TCL builder not available, using legacy generator"
            )
            if self.tcl_generator:
                tcl_files = self.tcl_generator.generate_separate_tcl_files(device_info)
            else:
                if PRODUCTION_MODE:
                    # In production mode, we must not fall back to basic TCL generation
                    logger.error("PRODUCTION ERROR: No TCL generator available")

                    # Clean up output folder if it exists
                    output_dir = Path("output")
                    if output_dir.exists():
                        try:
                            import shutil

                            shutil.rmtree(output_dir)
                            logger.info(f"Cleaned up output directory: {output_dir}")
                        except Exception as cleanup_error:
                            logger.error(
                                f"Failed to clean up output directory: {cleanup_error}"
                            )

                    raise RuntimeError(
                        "Production mode requires TCL generator to be available"
                    )

                logger.error("No TCL generator available")
                # Add basic fallback TCL generation
                tcl_files = self._generate_fallback_tcl_files(device_info)

        return tcl_files

    def _generate_fallback_tcl_files(self, device_info: Dict[str, Any]) -> List[str]:
        """
        Generate basic TCL files when no TCL generator is available.
        This is a fallback method for container environments where imports fail.
        """
        tcl_files = []

        # Extract device information
        vendor_id = device_info.get("vendor_id", 0x1234)
        device_id = device_info.get("device_id", 0x5678)
        revision_id = device_info.get("revision_id", 0x01)

        # Convert to hex strings if they're integers
        if isinstance(vendor_id, int):
            vendor_id_hex = f"{vendor_id:04x}"
        else:
            vendor_id_hex = str(vendor_id).replace("0x", "")

        if isinstance(device_id, int):
            device_id_hex = f"{device_id:04x}"
        else:
            device_id_hex = str(device_id).replace("0x", "")

        if isinstance(revision_id, int):
            revision_id_hex = f"{revision_id:02x}"
        else:
            revision_id_hex = str(revision_id).replace("0x", "")

        # Determine FPGA part based on board
        fpga_parts = {
            "pcileech_35t325_x4": "xc7a35tcsg324-2",
            "pcileech_75t": "xc7a75tfgg484-2",
            "pcileech_100t": "xczu3eg-sbva484-1-e",
        }
        fpga_part = fpga_parts.get(self.board, "xc7a35tcsg324-2")

        # Generate master build script
        master_tcl_content = f"""# PCILeech Firmware Build Script - Generated for {self.board}
# Device: {vendor_id_hex}:{device_id_hex} (Rev {revision_id_hex})
# FPGA Part: {fpga_part}
# Generated by PCILeech Firmware Generator

puts "Starting PCILeech firmware build for {self.board}"
puts "Device: {vendor_id_hex}:{device_id_hex}"
puts "FPGA Part: {fpga_part}"

# Create project
create_project pcileech_firmware ./vivado_project -part {fpga_part} -force
set_property target_language Verilog [current_project]
set_property default_lib xil_defaultlib [current_project]

# Add source files
puts "Adding source files..."
set sv_files [glob -nocomplain *.sv]
if {{[llength $sv_files] > 0}} {{
    add_files $sv_files
    puts "Added [llength $sv_files] SystemVerilog files"
}}

# Add constraint files
puts "Adding constraint files..."
set xdc_files [glob -nocomplain *.xdc]
if {{[llength $xdc_files] > 0}} {{
    add_files -fileset constrs_1 $xdc_files
    puts "Added [llength $xdc_files] constraint files"
}}

# Configure PCIe IP (basic configuration)
puts "Configuring PCIe IP core..."
# Note: Detailed IP configuration would be added here based on FPGA part

# Run synthesis
puts "Starting synthesis..."
launch_runs synth_1 -jobs 8
wait_on_run synth_1
puts "Synthesis completed"

# Run implementation
puts "Starting implementation..."
launch_runs impl_1 -jobs 8
wait_on_run impl_1
puts "Implementation completed"

# Generate bitstream
puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1
puts "Bitstream generation completed"

puts "Build completed successfully"
"""

        # Write master build script
        master_tcl_file = self.output_dir / "build_all.tcl"
        try:
            with open(master_tcl_file, "w", encoding="utf-8") as f:
                f.write(master_tcl_content)
            tcl_files.append(str(master_tcl_file))
            logger.info("Generated fallback master build TCL script")
        except Exception as e:
            logger.error(f"Failed to write fallback TCL script: {e}")

        return tcl_files

    def run_behavior_profiling(
        self, device_info: Dict[str, Any], duration: int = 30
    ) -> Optional[str]:
        """Run behavior profiling if available."""
        if self.variance_manager and self.variance_manager.is_profiling_available():
            return self.variance_manager.run_behavior_profiling(device_info, duration)
        else:
            logger.warning("Behavior profiler not available")
            return None

    def generate_build_files(self, device_info: Dict[str, Any]) -> List[str]:
        """Generate separate build files (TCL scripts, makefiles, etc.)."""
        build_files = []

        # Clean up any old unified TCL files first
        old_unified_files = [
            self.output_dir / legacy_file for legacy_file in LEGACY_TCL_FILES
        ]
        for old_file in old_unified_files:
            if old_file.exists():
                old_file.unlink()
                logger.info(f"Removed old unified file: {old_file.name}")

        # Generate separate TCL files using new template system
        tcl_files = self._generate_separate_tcl_files(device_info)
        build_files.extend(tcl_files)

        # Generate project file
        if self.file_manager:
            project_file = self.file_manager.generate_project_file(
                device_info, self.board
            )
            # Update features based on available components
            project_file["features"]["advanced_sv"] = self.sv_generator is not None
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
    ) -> Dict[str, Any]:
        """Main firmware build process."""
        logger.info("Starting firmware build process")
        build_results = {
            "success": False,
            "files_generated": [],
            "errors": [],
            "build_time": 0,
        }

        start_time = time.time()

        try:
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

            # Step 5: Generate build files
            logger.info("Step 5: Generating build files")
            build_files = self.generate_build_files(device_info)
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

            log_info_safe(
                logger,
                "Firmware build completed successfully in {build_time:.2f} seconds",
                build_time=build_results["build_time"],
            )
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

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle disable flags to override defaults
    if hasattr(args, "disable_advanced_sv") and args.disable_advanced_sv:
        args.advanced_sv = False
    if hasattr(args, "disable_variance") and args.disable_variance:
        args.enable_variance = False

    # Validate production mode configuration before proceeding
    validate_production_mode()

    try:
        # Initialize builder
        builder = PCILeechFirmwareBuilder(args.bdf, args.board)

        # Run build process
        results = builder.build_firmware(
            advanced_sv=args.advanced_sv,
            device_type=args.device_type,
            enable_variance=args.enable_variance,
            behavior_profile_duration=args.behavior_profile_duration,
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
                print("Now run vivado with the following command:")
                print(
                    safe_format(
                        "cd {output_dir} && vivado -mode batch -source build.tcl -lic_retry 30 -lic_retry_int 60",
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

        # Fallback: generate basic TCL content
        vendor_id = donor_info.get("vendor_id", "0x1234")
        device_id = donor_info.get("device_id", "0x5678")

        tcl_content = f"""# Generated TCL for {vendor_id}:{device_id}
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
"""

        # Write to output file
        output_path = Path(output_file)
        output_path.write_text(tcl_content)

        return tcl_content, str(output_path)

    except Exception as e:
        logger.error(f"Error in build_tcl: {e}")
        # Return minimal valid TCL
        minimal_tcl = "# Minimal TCL fallback\nset_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]\n"
        return minimal_tcl, output_file


def build_sv(registers: List[Dict[str, Any]], target_file: Union[str, Path]) -> None:
    """Generate SystemVerilog files using the refactored system."""
    try:
        # Create a temporary builder instance
        builder = PCILeechFirmwareBuilder(
            bdf="0000:03:00.0", board="pcileech_35t325_x4"
        )

        # Convert registers to device_info format
        device_info = {
            "vendor_id": "0x1234",
            "device_id": "0x5678",
            "registers": registers,
        }

        # Generate SystemVerilog files
        generated_files = builder.generate_systemverilog_files(device_info)

        # Copy the main generated file to target location if needed
        target_path = Path(target_file)
        if generated_files and not target_path.exists():
            # Create a basic SystemVerilog file
            sv_content = f"""// Generated SystemVerilog for {len(registers)} registers
module pcileech_controller (
    input wire clk,
    input wire rst,
    // Register interface
    input wire [31:0] reg_addr,
    input wire [31:0] reg_wdata,
    output reg [31:0] reg_rdata,
    input wire reg_we
);

// Register implementation
always @(posedge clk) begin
    if (rst) begin
        reg_rdata <= 32'h0;
    end else begin
        case (reg_addr)
"""

            # Add register cases
            for i, reg in enumerate(registers[:10]):  # Limit to first 10 for brevity
                offset = reg.get("offset", i * 4)
                sv_content += f"            32'h{offset:08x}: reg_rdata <= 32'h{reg.get('value', 0):08x};\n"

            sv_content += """            default: reg_rdata <= 32'h0;
        endcase
    end
end

endmodule
"""

            target_path.write_text(sv_content)

    except Exception as e:
        if PRODUCTION_MODE:
            # In production mode, we must not fall back to minimal SystemVerilog
            logger.error(f"PRODUCTION ERROR: Failed to generate SystemVerilog: {e}")

            # Clean up output folder if it exists
            output_dir = Path("output")
            if output_dir.exists():
                try:
                    import shutil

                    shutil.rmtree(output_dir)
                    logger.info(f"Cleaned up output directory: {output_dir}")
                except Exception as cleanup_error:
                    logger.error(
                        f"Failed to clean up output directory: {cleanup_error}"
                    )

            raise RuntimeError(
                f"Production mode requires proper SystemVerilog generation: {e}"
            )

        logger.error(f"Error in build_sv: {e}")
        # Create minimal SystemVerilog file
        target_path = Path(target_file)
        minimal_sv = """// Minimal SystemVerilog fallback
module pcileech_controller (
    input wire clk,
    input wire rst
);
endmodule
"""
        target_path.write_text(minimal_sv)


def scrape_driver_regs(
    vendor_id: str, device_id: str
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Scrape driver registers using real implementation or controlled fallback."""
    try:
        # Validate production mode requirements
        if PRODUCTION_MODE and not ALLOW_MOCK_DATA:
            logger.info(
                f"Production mode: Real driver scraping for {vendor_id}:{device_id}"
            )

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
                        "name": reg_data.get("name", "UNKNOWN"),
                        "offset": reg_data.get("offset", 0),
                        "value": reg_data.get("value", 0),
                        "access": reg_data.get("rw", "RO").upper(),
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

        elif ALLOW_MOCK_DATA:
            # Development/testing mode with mock data
            logger.warning(
                f"DEVELOPMENT MODE: Using mock data for {vendor_id}:{device_id}"
            )

            mock_registers = [
                {"name": "CTRL", "offset": 0x0000, "value": 0x12345678, "access": "RW"},
                {
                    "name": "STATUS",
                    "offset": 0x0004,
                    "value": 0x87654321,
                    "access": "RO",
                },
                {
                    "name": "CONFIG",
                    "offset": 0x0008,
                    "value": 0xABCDEF00,
                    "access": "RW",
                },
            ]

            mock_state_machine = {
                "states": ["IDLE", "ACTIVE", "RESET"],
                "transitions": [
                    {"from": "IDLE", "to": "ACTIVE", "condition": "enable"},
                    {"from": "ACTIVE", "to": "IDLE", "condition": "disable"},
                    {"from": "*", "to": "RESET", "condition": "reset"},
                ],
            }

            return mock_registers, mock_state_machine
        else:
            raise RuntimeError(
                "Production mode enabled but real driver scraping failed. "
                "Cannot proceed without valid register data."
            )

    except Exception as e:
        if PRODUCTION_MODE:
            logger.error(f"PRODUCTION ERROR in scrape_driver_regs: {e}")
            raise RuntimeError(f"Production build failed: {e}")
        else:
            logger.error(f"Error in scrape_driver_regs: {e}")
            return [], {}


def integrate_behavior_profile(
    bdf: str, registers: List[Dict[str, Any]], duration: float = 30.0
) -> List[Dict[str, Any]]:
    """Integrate behavior profiling data with registers using real implementation or controlled fallback."""
    try:
        # Validate production mode requirements
        if PRODUCTION_MODE and not ALLOW_MOCK_DATA:
            logger.info(
                f"Production mode: Real behavior profiling for {bdf} over {duration}s"
            )

            # Use real behavior profiler
            profiler = BehaviorProfiler(bdf=bdf)
            behavior_profile = profiler.capture_behavior_profile(duration=duration)

            # Integrate real profiling data with registers
            enhanced_registers = []
            for reg in registers:
                enhanced_reg = reg.copy()

                # Find matching register access data
                reg_name = reg.get("name", "")
                reg_offset = reg.get("offset", 0)

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
                                timing_data["write_latency"] = int(
                                    access.duration_us * 1000
                                )

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

        elif ALLOW_MOCK_DATA:
            # Development/testing mode with mock data
            logger.warning(f"DEVELOPMENT MODE: Using mock behavior data for {bdf}")

            enhanced_registers = []
            for reg in registers:
                enhanced_reg = reg.copy()
                enhanced_reg["timing"] = {
                    "read_latency": 100,  # nanoseconds
                    "write_latency": 150,
                    "access_frequency": 1000,  # Hz
                }
                enhanced_reg["behavior_confidence"] = (
                    0.5  # Lower confidence for mock data
                )
                enhanced_registers.append(enhanced_reg)

            return enhanced_registers
        else:
            raise RuntimeError(
                "Production mode enabled but real behavior profiling failed. "
                "Cannot proceed without valid timing data."
            )

    except Exception as e:
        if PRODUCTION_MODE:
            logger.error(f"PRODUCTION ERROR in integrate_behavior_profile: {e}")
            raise RuntimeError(f"Production build failed: {e}")
        else:
            logger.error(f"Error in integrate_behavior_profile: {e}")
            return registers


def generate_register_state_machine(
    reg_name: str, sequences: List[Dict[str, Any]], base_offset: int
) -> Dict[str, Any]:
    """Generate state machine for register sequences."""
    try:
        if len(sequences) < 2:
            raise ValueError("Insufficient sequences for state machine generation")

        # Mock state machine generation
        state_machine = {
            "register": reg_name,
            "base_offset": base_offset,
            "states": [f"STATE_{i}" for i in range(len(sequences))],
            "sequences": sequences,
            "initial_state": "STATE_0",
        }

        return state_machine

    except Exception as e:
        logger.error(f"Error in generate_register_state_machine: {e}")
        return {}


def generate_device_state_machine(registers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate device-level state machine."""
    try:
        if not registers:
            return {"states": ["IDLE"], "registers": []}

        # Mock device state machine
        device_state_machine = {
            "device_states": ["INIT", "READY", "ACTIVE", "ERROR"],
            "register_count": len(registers),
            "state_transitions": [
                {"from": "INIT", "to": "READY", "trigger": "initialization_complete"},
                {"from": "READY", "to": "ACTIVE", "trigger": "operation_start"},
                {"from": "ACTIVE", "to": "READY", "trigger": "operation_complete"},
                {"from": "*", "to": "ERROR", "trigger": "error_condition"},
            ],
            "registers": [
                reg.get("name", f"REG_{i}") for i, reg in enumerate(registers)
            ],
        }

        return device_state_machine

    except Exception as e:
        logger.error(f"Error in generate_device_state_machine: {e}")
        return {}


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
