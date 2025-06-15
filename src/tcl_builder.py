#!/usr/bin/env python3
"""
High-level TCL builder interface for PCILeech firmware generation.

This module provides a clean, object-oriented interface for building TCL scripts
using the template system, integrating with constants and build helpers.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Try relative imports first, then absolute imports for test compatibility
try:
    from .template_renderer import TemplateRenderer, TemplateRenderError
except ImportError:
    from template_renderer import TemplateRenderer, TemplateRenderError

try:
    from .device_config import DeviceConfigManager, get_device_config
except ImportError:
    try:
        from device_config import DeviceConfigManager, get_device_config
    except ImportError:
        # Fallback if device config is not available
        def get_device_config(profile_name="generic"):
            return None

        class DeviceConfigManager:
            pass


try:
    from .build_helpers import (
        batch_write_tcl_files,
        create_fpga_strategy_selector,
        select_pcie_ip_core,
        validate_fpga_part,
        write_tcl_file_with_logging,
    )
except ImportError:
    from build_helpers import (
        batch_write_tcl_files,
        create_fpga_strategy_selector,
        select_pcie_ip_core,
        validate_fpga_part,
        write_tcl_file_with_logging,
    )

try:
    from .constants import (
        BOARD_PARTS,
        DEFAULT_FPGA_PART,
        FPGA_FAMILIES,
        IMPLEMENTATION_STRATEGY,
        MASTER_BUILD_SCRIPT,
        SYNTHESIS_STRATEGY,
        TCL_SCRIPT_FILES,
    )
except ImportError:
    try:
        from constants import (
            BOARD_PARTS,
            DEFAULT_FPGA_PART,
            FPGA_FAMILIES,
            IMPLEMENTATION_STRATEGY,
            MASTER_BUILD_SCRIPT,
            SYNTHESIS_STRATEGY,
            TCL_SCRIPT_FILES,
        )
    except ImportError:
        # Fallback constants if import fails
        BOARD_PARTS = {}
        DEFAULT_FPGA_PART = "xc7a35tcsg324-2"
        TCL_SCRIPT_FILES = [
            "01_project_setup.tcl",
            "02_ip_config.tcl",
            "03_add_sources.tcl",
            "04_constraints.tcl",
            "05_synthesis.tcl",
            "06_implementation.tcl",
            "07_bitstream.tcl",
        ]
        MASTER_BUILD_SCRIPT = "build_all.tcl"
        SYNTHESIS_STRATEGY = "Vivado Synthesis Defaults"
        IMPLEMENTATION_STRATEGY = "Performance_Explore"
        FPGA_FAMILIES = {}

logger = logging.getLogger(__name__)


class TCLBuilder:
    """
    High-level interface for building TCL scripts using templates.

    This class wraps the template renderer and provides methods for each type
    of TCL script, handling context preparation and template rendering.
    """

    def __init__(
        self,
        template_dir: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        device_profile: str = "generic",
    ):
        """
        Initialize the TCL builder.

        Args:
            template_dir: Directory containing template files (defaults to src/templates)
            output_dir: Directory for output files (defaults to current directory)
            device_profile: Device configuration profile to use
        """
        self.template_renderer = TemplateRenderer(template_dir)
        self.output_dir = Path(output_dir) if output_dir else Path(".")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize strategy selector for FPGA-specific configurations
        self.fpga_strategy_selector = create_fpga_strategy_selector()

        # Load device configuration
        self.device_config = get_device_config(device_profile)

        # Track generated files
        self.generated_files: List[str] = []

        logger.debug(f"TCL builder initialized with output dir: {self.output_dir}")

    def prepare_base_context(
        self,
        board: str,
        fpga_part: Optional[str] = None,
        vendor_id: Optional[int] = None,
        device_id: Optional[int] = None,
        revision_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Prepare base context variables used across all TCL templates.

        Args:
            board: Board name (e.g., "pcileech_35t325_x4")
            fpga_part: FPGA part string (auto-detected from board if not provided)
            vendor_id: PCI vendor ID
            device_id: PCI device ID
            revision_id: PCI revision ID

        Returns:
            Dictionary containing base context variables
        """
        # Determine FPGA part
        if fpga_part is None:
            fpga_part = BOARD_PARTS.get(board, DEFAULT_FPGA_PART)

        # Validate FPGA part
        if not validate_fpga_part(fpga_part):
            logger.warning(f"Invalid FPGA part '{fpga_part}', using default")
            fpga_part = DEFAULT_FPGA_PART

        # Get FPGA-specific configuration
        fpga_config = self.fpga_strategy_selector(fpga_part)

        # Get device configuration values with fallbacks
        if self.device_config:
            config_vendor_id = self.device_config.identification.vendor_id
            config_device_id = self.device_config.identification.device_id
            config_revision_id = self.device_config.registers.revision_id
            config_class_code = self.device_config.identification.class_code
        else:
            # Fallback to hardcoded defaults if no device config
            config_vendor_id = 0x1234
            config_device_id = 0x5678
            config_revision_id = 0x01
            config_class_code = 0x040300

        # Prepare base context
        context = {
            "board": board,
            "fpga_part": fpga_part,
            "pcie_ip_type": fpga_config["pcie_ip_type"],
            "fpga_family": fpga_config["family"],
            "max_lanes": fpga_config["max_lanes"],
            "supports_msi": fpga_config["supports_msi"],
            "supports_msix": fpga_config["supports_msix"],
            "synthesis_strategy": SYNTHESIS_STRATEGY,
            "implementation_strategy": IMPLEMENTATION_STRATEGY,
            "vendor_id": vendor_id or config_vendor_id,
            "device_id": device_id or config_device_id,
            "revision_id": revision_id or config_revision_id,
            "class_code": config_class_code,
            "project_name": "pcileech_firmware",
            "project_dir": "./vivado_project",
            "output_dir": ".",
            "header_comment": f"# PCILeech Firmware Build - {board}",
        }

        # Add hex-formatted IDs for convenience
        context.update(
            {
                "vendor_id_hex": f"{context['vendor_id']:04x}",
                "device_id_hex": f"{context['device_id']:04x}",
                "revision_id_hex": f"{context['revision_id']:02x}",
            }
        )

        return context

    def build_project_setup_tcl(self, context: Dict[str, Any]) -> str:
        """
        Build project setup TCL script.

        Args:
            context: Template context variables

        Returns:
            Rendered TCL content
        """
        try:
            return self.template_renderer.render_template(
                "tcl/project_setup.j2", context
            )
        except TemplateRenderError:
            logger.warning("Template not found, using fallback project setup")
            return self._fallback_project_setup(context)

    def build_ip_config_tcl(self, context: Dict[str, Any]) -> str:
        """
        Build IP configuration TCL script.

        Args:
            context: Template context variables

        Returns:
            Rendered TCL content
        """
        try:
            return self.template_renderer.render_template("tcl/ip_config.j2", context)
        except TemplateRenderError:
            logger.warning("Template not found, using fallback IP config")
            return self._fallback_ip_config(context)

    def build_sources_tcl(
        self, context: Dict[str, Any], source_files: Optional[List[str]] = None
    ) -> str:
        """
        Build sources management TCL script.

        Args:
            context: Template context variables
            source_files: List of source files to include

        Returns:
            Rendered TCL content
        """
        # Add source files to context
        context = context.copy()
        context["source_files"] = source_files or []

        try:
            return self.template_renderer.render_template("tcl/sources.j2", context)
        except TemplateRenderError:
            logger.warning("Template not found, using fallback sources")
            return self._fallback_sources(context)

    def build_constraints_tcl(
        self, context: Dict[str, Any], constraint_files: Optional[List[str]] = None
    ) -> str:
        """
        Build constraints TCL script.

        Args:
            context: Template context variables
            constraint_files: List of constraint files to include

        Returns:
            Rendered TCL content
        """
        # Add constraint files to context
        context = context.copy()
        context["constraint_files"] = constraint_files or []

        # Try to load board-specific XDC content from PCILeech repository
        board_xdc_content = None
        if context.get("board") and context["board"].get("name"):
            board_name = context["board"]["name"]
            try:
                try:
                    from .repo_manager import RepoManager
                except ImportError:
                    # Fallback for when running as script (not package)
                    from repo_manager import RepoManager
                board_xdc_content = RepoManager.read_xdc_constraints(board_name)
                logger.info(f"Loaded XDC constraints for board: {board_name}")
            except Exception as e:
                logger.warning(
                    f"Could not load XDC constraints for board {board_name}: {e}"
                )
                board_xdc_content = None

        context["board_xdc_content"] = board_xdc_content

        try:
            return self.template_renderer.render_template("tcl/constraints.j2", context)
        except TemplateRenderError:
            logger.warning("Template not found, using fallback constraints")
            return self._fallback_constraints(context)

    def build_synthesis_tcl(self, context: Dict[str, Any]) -> str:
        """
        Build synthesis TCL script.

        Args:
            context: Template context variables

        Returns:
            Rendered TCL content
        """
        try:
            return self.template_renderer.render_template("tcl/synthesis.j2", context)
        except TemplateRenderError:
            logger.warning("Template not found, using fallback synthesis")
            return self._fallback_synthesis(context)

    def build_implementation_tcl(self, context: Dict[str, Any]) -> str:
        """
        Build implementation TCL script.

        Args:
            context: Template context variables

        Returns:
            Rendered TCL content
        """
        try:
            return self.template_renderer.render_template(
                "tcl/implementation.j2", context
            )
        except TemplateRenderError:
            logger.warning("Template not found, using fallback implementation")
            return self._fallback_implementation(context)

    def build_bitstream_tcl(self, context: Dict[str, Any]) -> str:
        """
        Build bitstream generation TCL script.

        Args:
            context: Template context variables

        Returns:
            Rendered TCL content
        """
        try:
            return self.template_renderer.render_template("tcl/bitstream.j2", context)
        except TemplateRenderError:
            logger.warning("Template not found, using fallback bitstream")
            return self._fallback_bitstream(context)

    def build_master_tcl(self, context: Dict[str, Any]) -> str:
        """
        Build master build TCL script that sources all other scripts.

        Args:
            context: Template context variables

        Returns:
            Rendered TCL content
        """
        # Add script files to context
        context = context.copy()
        context["tcl_script_files"] = TCL_SCRIPT_FILES

        try:
            return self.template_renderer.render_template(
                "tcl/master_build.j2", context
            )
        except TemplateRenderError:
            logger.warning("Template not found, using fallback master build")
            return self._fallback_master_build(context)

    def build_all_tcl_scripts(
        self,
        board: str,
        fpga_part: Optional[str] = None,
        vendor_id: Optional[int] = None,
        device_id: Optional[int] = None,
        revision_id: Optional[int] = None,
        source_files: Optional[List[str]] = None,
        constraint_files: Optional[List[str]] = None,
    ) -> Dict[str, bool]:
        """
        Build all TCL scripts and write them to the output directory.

        Args:
            board: Board name
            fpga_part: FPGA part string (auto-detected if not provided)
            vendor_id: PCI vendor ID
            device_id: PCI device ID
            revision_id: PCI revision ID
            source_files: List of source files
            constraint_files: List of constraint files

        Returns:
            Dictionary mapping script names to success status
        """
        # Prepare base context
        context = self.prepare_base_context(
            board, fpga_part, vendor_id, device_id, revision_id
        )

        # Build all TCL scripts
        tcl_contents = {
            TCL_SCRIPT_FILES[0]: self.build_project_setup_tcl(context),
            TCL_SCRIPT_FILES[1]: self.build_ip_config_tcl(context),
            TCL_SCRIPT_FILES[2]: self.build_sources_tcl(context, source_files),
            TCL_SCRIPT_FILES[3]: self.build_constraints_tcl(context, constraint_files),
            TCL_SCRIPT_FILES[4]: self.build_synthesis_tcl(context),
            TCL_SCRIPT_FILES[5]: self.build_implementation_tcl(context),
            TCL_SCRIPT_FILES[6]: self.build_bitstream_tcl(context),
            MASTER_BUILD_SCRIPT: self.build_master_tcl(context),
        }

        # Write all files in batch
        results = batch_write_tcl_files(
            tcl_contents, self.output_dir, self.generated_files, logger
        )

        return results

    # Fallback methods for when templates are not available
    def _fallback_project_setup(self, context: Dict[str, Any]) -> str:
        """Fallback project setup TCL when template is not available."""
        return f"""# Project Setup TCL - Generated for {context['board']}
create_project pcileech_firmware ./vivado_project -part {context['fpga_part']} -force
set_property target_language Verilog [current_project]
set_property default_lib xil_defaultlib [current_project]
"""

    def _fallback_ip_config(self, context: Dict[str, Any]) -> str:
        """Fallback IP config TCL when template is not available."""
        pcie_ip = select_pcie_ip_core(context["fpga_part"])
        return f"""# IP Configuration TCL - Generated for {context['board']}
# PCIe IP Core: {pcie_ip}
# Device: {context['vendor_id_hex']}:{context['device_id_hex']}
puts "Creating PCIe IP core..."
"""

    def _fallback_sources(self, context: Dict[str, Any]) -> str:
        """Fallback sources TCL when template is not available."""
        return f"""# Sources TCL - Generated for {context['board']}
puts "Adding source files..."
set sv_files [glob -nocomplain *.sv]
if {{[llength $sv_files] > 0}} {{
    add_files $sv_files
    puts "Added [llength $sv_files] SystemVerilog files"
}}
"""

    def _fallback_constraints(self, context: Dict[str, Any]) -> str:
        """Fallback constraints TCL when template is not available."""
        return f"""# Constraints TCL - Generated for {context['board']}
puts "Adding constraint files..."
set xdc_files [glob -nocomplain *.xdc]
if {{[llength $xdc_files] > 0}} {{
    add_files -fileset constrs_1 $xdc_files
    puts "Added [llength $xdc_files] constraint files"
}}
"""

    def _fallback_synthesis(self, context: Dict[str, Any]) -> str:
        """Fallback synthesis TCL when template is not available."""
        return f"""# Synthesis TCL - Generated for {context['board']}
puts "Starting synthesis..."
launch_runs synth_1 -jobs 8
wait_on_run synth_1
puts "Synthesis completed"
"""

    def _fallback_implementation(self, context: Dict[str, Any]) -> str:
        """Fallback implementation TCL when template is not available."""
        return f"""# Implementation TCL - Generated for {context['board']}
puts "Starting implementation..."
launch_runs impl_1 -jobs 8
wait_on_run impl_1
puts "Implementation completed"
"""

    def _fallback_bitstream(self, context: Dict[str, Any]) -> str:
        """Fallback bitstream TCL when template is not available."""
        return f"""# Bitstream TCL - Generated for {context['board']}
puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1
puts "Bitstream generation completed"
"""

    def _fallback_master_build(self, context: Dict[str, Any]) -> str:
        """Fallback master build TCL when template is not available."""
        script_sources = "\n".join(f"source {script}" for script in TCL_SCRIPT_FILES)
        return f"""# Master Build TCL - Generated for {context['board']}
puts "Starting PCILeech firmware build for {context['board']}"
puts "FPGA Part: {context['fpga_part']}"
puts "Device: {context['vendor_id_hex']}:{context['device_id_hex']}"

{script_sources}

puts "Build completed successfully"
"""

    def get_generated_files(self) -> List[str]:
        """Get list of generated TCL files."""
        return self.generated_files.copy()

    def clean_generated_files(self) -> None:
        """Remove all generated TCL files."""
        for file_path in self.generated_files:
            try:
                Path(file_path).unlink(missing_ok=True)
                logger.debug(f"Removed {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove {file_path}: {e}")

        self.generated_files.clear()
        logger.info("Cleaned up generated TCL files")


# Convenience function for quick TCL generation
def generate_tcl_scripts(
    board: str,
    output_dir: Union[str, Path] = ".",
    fpga_part: Optional[str] = None,
    vendor_id: Optional[int] = None,
    device_id: Optional[int] = None,
    revision_id: Optional[int] = None,
    source_files: Optional[List[str]] = None,
    constraint_files: Optional[List[str]] = None,
) -> Dict[str, bool]:
    """
    Convenience function to generate all TCL scripts for a board.

    Args:
        board: Board name
        output_dir: Output directory for TCL files
        fpga_part: FPGA part string (auto-detected if not provided)
        vendor_id: PCI vendor ID
        device_id: PCI device ID
        revision_id: PCI revision ID
        source_files: List of source files
        constraint_files: List of constraint files

    Returns:
        Dictionary mapping script names to success status
    """
    builder = TCLBuilder(output_dir=output_dir)
    return builder.build_all_tcl_scripts(
        board,
        fpga_part,
        vendor_id,
        device_id,
        revision_id,
        source_files,
        constraint_files,
    )
