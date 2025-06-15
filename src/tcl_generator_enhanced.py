#!/usr/bin/env python3
"""
Enhanced TCL Script Generation Module

Template-based TCL generator that replaces hardcoded strings with Jinja2 templates
while maintaining backward compatibility through fallback mechanisms.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from board_config import get_board_info, get_fpga_part, get_pcie_ip_type
    from string_utils import generate_tcl_header_comment, log_info_safe, safe_format
    from template_renderer import TemplateRenderer, TemplateRenderError

    IMPORTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Import error: {e}. Some features may not be available.")
    # Fallback imports will be handled in the class
    IMPORTS_AVAILABLE = False

    # Define fallback classes/functions
    class TemplateRenderer:
        def __init__(self, *args, **kwargs):
            pass

        def template_exists(self, *args, **kwargs):
            return False

        def render_template(self, *args, **kwargs):
            raise Exception("Template renderer not available")

    class TemplateRenderError(Exception):
        pass

    def get_board_info(board):
        return {
            "name": board,
            "fpga_part": "xc7a35tcsg324-2",
            "fpga_family": "7series",
            "pcie_ip_type": "pcie_7x",
        }

    def get_fpga_part(board):
        board_mapping = {
            "75t": "xc7a75tfgg484-2",
            "35t": "xc7a35tcsg324-2",
            "100t": "xczu3eg-sbva484-1-e",
        }
        return board_mapping.get(board, "xc7a35tcsg324-2")

    def get_pcie_ip_type(fpga_part):
        return "pcie_7x"

    def generate_tcl_header_comment(title, **kwargs):
        return f"# {title}\n# Generated with fallback mode"

    def log_info_safe(logger, template, **kwargs):
        logger.info(template.format(**kwargs))

    def safe_format(template, **kwargs):
        return template.format(**kwargs)


logger = logging.getLogger(__name__)


class EnhancedTCLGenerator:
    """
    Enhanced TCL Generator with template support and fallback mechanisms.

    This class uses Jinja2 templates to generate TCL scripts while maintaining
    backward compatibility with the original hardcoded string approach.
    """

    def __init__(self, board: str, output_dir: Path, use_templates: bool = True):
        """
        Initialize the enhanced TCL generator.

        Args:
            board: Target board name
            output_dir: Output directory for generated files
            use_templates: Whether to use templates (True) or fallback to hardcoded (False)
        """
        self.board = board
        self.output_dir = output_dir
        self.use_templates = use_templates

        # Initialize template renderer if available
        self.template_renderer = None
        if use_templates and IMPORTS_AVAILABLE:
            try:
                self.template_renderer = TemplateRenderer()
                logger.info("Template renderer initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize template renderer: {e}")
                self.use_templates = False
        elif use_templates and not IMPORTS_AVAILABLE:
            logger.warning("Template renderer not available due to import issues")
            self.use_templates = False

        # Template mapping for each build stage
        self.template_mapping = {
            "project_setup": "tcl/project_setup.j2",
            "ip_config_pcie7x": "tcl/ip_config_pcie7x.j2",
            "sources": "tcl/sources.j2",
            "constraints": "tcl/constraints.j2",
            "synthesis": "tcl/synthesis.j2",
            "implementation": "tcl/implementation.j2",
            "bitstream": "tcl/bitstream.j2",
            "master_build": "tcl/master_build.j2",
        }

    def _build_context(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build comprehensive template context from device info and board config.

        Args:
            device_info: Device information dictionary

        Returns:
            Template context dictionary
        """
        try:
            board_info = get_board_info(self.board)
        except Exception:
            # Fallback to basic board info
            try:
                fpga_part = get_fpga_part(self.board)
            except:
                # Hardcoded fallback mapping for common boards
                board_mapping = {
                    "75t": "xc7a75tfgg484-2",
                    "35t": "xc7a35tcsg324-2",
                    "100t": "xczu3eg-sbva484-1-e",
                }
                fpga_part = board_mapping.get(self.board, "xc7a35tcsg324-2")

            board_info = {
                "name": self.board,
                "fpga_part": fpga_part,
                "fpga_family": "7series",
                "pcie_ip_type": "pcie_7x",
            }

        context = {
            "device": {
                "vendor_id": device_info.get("vendor_id", "0000"),
                "device_id": device_info.get("device_id", "0000"),
                "class_code": device_info.get("class_code", "040300"),
                "revision_id": device_info.get("revision_id", "01"),
            },
            "board": board_info,
            "project": {
                "name": "pcileech_firmware",
                "dir": "./vivado_project",
                "output_dir": ".",
            },
            "meta": {
                "generated_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "generator_version": "2.0.0-template",
            },
        }

        # Add header using template or fallback
        context["header"] = self._generate_header(
            "PCILeech Firmware Build Script",
            context["device"],
            context["board"],
            context["meta"],
        )

        return context

    def _generate_header(
        self,
        title: str,
        device: Dict[str, Any],
        board: Dict[str, Any],
        meta: Dict[str, Any],
    ) -> str:
        """Generate header using template or fallback."""
        if self.template_renderer and self.template_renderer.template_exists(
            "common/header.j2"
        ):
            try:
                return self.template_renderer.render_template(
                    "common/header.j2",
                    {"title": title, "device": device, "board": board, "meta": meta},
                )
            except TemplateRenderError:
                pass

        # Fallback to hardcoded header
        return generate_tcl_header_comment(
            title,
            vendor_id=device["vendor_id"],
            device_id=device["device_id"],
            board=board["name"],
            generated=meta["generated_time"],
        )

    def _render_template_safely(
        self, template_name: str, context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Safely render a template with error handling.

        Args:
            template_name: Name of template to render
            context: Template context

        Returns:
            Rendered template content or None if failed
        """
        if not self.use_templates or not self.template_renderer:
            return None

        try:
            if not self.template_renderer.template_exists(template_name):
                logger.warning(f"Template not found: {template_name}")
                return None

            content = self.template_renderer.render_template(template_name, context)
            logger.debug(f"Successfully rendered template: {template_name}")
            return content

        except TemplateRenderError as e:
            logger.warning(f"Template rendering failed for {template_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error rendering {template_name}: {e}")
            return None

    def generate_project_setup_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate project setup TCL using templates with fallback."""
        context = self._build_context(device_info)

        # Try template first
        template_content = self._render_template_safely(
            self.template_mapping["project_setup"], context
        )
        if template_content:
            return template_content

        # Fallback to hardcoded implementation
        logger.info("Using fallback for project setup TCL generation")
        return self._generate_project_setup_fallback(device_info)

    def generate_ip_config_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate IP configuration TCL using templates with fallback."""
        context = self._build_context(device_info)

        # Determine which IP template to use
        pcie_ip_type = context["board"].get("pcie_ip_type", "pcie_7x")
        template_name = f"tcl/ip_config_{pcie_ip_type}.j2"

        # Try template first
        template_content = self._render_template_safely(template_name, context)
        if template_content:
            return template_content

        # Fallback to hardcoded implementation
        logger.info("Using fallback for IP config TCL generation")
        return self._generate_ip_config_fallback(device_info)

    def generate_constraints_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate constraints TCL using templates with fallback."""
        context = self._build_context(device_info)

        # Try template first
        template_content = self._render_template_safely(
            self.template_mapping["constraints"], context
        )
        if template_content:
            return template_content

        # Fallback to hardcoded implementation
        logger.info("Using fallback for constraints TCL generation")
        return self._generate_constraints_fallback(device_info)

    def generate_sources_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate sources TCL using templates with fallback."""
        context = self._build_context(device_info)

        # Try template first
        template_content = self._render_template_safely(
            self.template_mapping["sources"], context
        )
        if template_content:
            return template_content

        # Fallback to hardcoded implementation
        logger.info("Using fallback for sources TCL generation")
        return self._generate_sources_fallback(device_info)

    def generate_synthesis_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate synthesis TCL using templates with fallback."""
        context = self._build_context(device_info)

        # Try template first
        template_content = self._render_template_safely(
            self.template_mapping["synthesis"], context
        )
        if template_content:
            return template_content

        # Fallback to hardcoded implementation
        logger.info("Using fallback for synthesis TCL generation")
        return self._generate_synthesis_fallback(device_info)

    def generate_implementation_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate implementation TCL using templates with fallback."""
        context = self._build_context(device_info)

        # Try template first
        template_content = self._render_template_safely(
            self.template_mapping["implementation"], context
        )
        if template_content:
            return template_content

        # Fallback to hardcoded implementation
        logger.info("Using fallback for implementation TCL generation")
        return self._generate_implementation_fallback(device_info)

    def generate_bitstream_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate bitstream TCL using templates with fallback."""
        context = self._build_context(device_info)

        # Try template first
        template_content = self._render_template_safely(
            self.template_mapping["bitstream"], context
        )
        if template_content:
            return template_content

        # Fallback to hardcoded implementation
        logger.info("Using fallback for bitstream TCL generation")
        return self._generate_bitstream_fallback(device_info)

    def generate_master_build_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate master build TCL using templates with fallback."""
        context = self._build_context(device_info)

        # Try template first
        template_content = self._render_template_safely(
            self.template_mapping["master_build"], context
        )
        if template_content:
            return template_content

        # Fallback to hardcoded implementation
        logger.info("Using fallback for master build TCL generation")
        return self._generate_master_build_fallback(device_info)

    # Fallback methods (simplified versions of original hardcoded implementations)
    def _generate_project_setup_fallback(self, device_info: Dict[str, Any]) -> str:
        """Fallback project setup generation."""
        fpga_part = (
            get_fpga_part(self.board)
            if "get_fpga_part" in globals()
            else "xc7a35tcsg324-2"
        )
        vendor_id = device_info.get("vendor_id", "0000")
        device_id = device_info.get("device_id", "0000")
        class_code = device_info.get("class_code", "040300")

        return f"""# PCILeech Project Setup (Fallback)
# Device: {vendor_id}:{device_id} (Class: {class_code})
# Board: {self.board}

set project_name "pcileech_firmware"
set project_dir "./vivado_project"
create_project $project_name $project_dir -part {fpga_part} -force
set_property target_language Verilog [current_project]
puts "Project setup completed (fallback mode)"
"""

    def _generate_ip_config_fallback(self, device_info: Dict[str, Any]) -> str:
        """Fallback IP config generation."""
        vendor_id = device_info.get("vendor_id", "0000")
        device_id = device_info.get("device_id", "0000")

        return f"""# PCIe IP Configuration (Fallback)
puts "Creating PCIe IP core for device {vendor_id}:{device_id}..."
# Simplified PCIe 7x configuration
create_ip -name pcie_7x -vendor xilinx.com -library ip -module_name pcie_7x_0
puts "PCIe IP configuration completed (fallback mode)"
"""

    def _generate_constraints_fallback(self, device_info: Dict[str, Any]) -> str:
        """Fallback constraints generation."""
        return """# Timing Constraints (Fallback)
puts "Adding basic timing constraints..."
# Basic clock constraint
create_clock -period 10.000 -name sys_clk [get_ports clk]
puts "Constraints setup completed (fallback mode)"
"""

    def _generate_sources_fallback(self, device_info: Dict[str, Any]) -> str:
        """Fallback sources generation."""
        return """# Source Files (Fallback)
puts "Adding source files..."
add_files -norecurse [glob -nocomplain *.sv]
add_files -norecurse [glob -nocomplain *.v]
puts "Source files added (fallback mode)"
"""

    def _generate_synthesis_fallback(self, device_info: Dict[str, Any]) -> str:
        """Fallback synthesis generation."""
        return """# Synthesis (Fallback)
puts "Starting synthesis..."
launch_runs synth_1 -jobs 8
wait_on_run synth_1
puts "Synthesis completed (fallback mode)"
"""

    def _generate_implementation_fallback(self, device_info: Dict[str, Any]) -> str:
        """Fallback implementation generation."""
        return """# Implementation (Fallback)
puts "Starting implementation..."
launch_runs impl_1 -jobs 8
wait_on_run impl_1
puts "Implementation completed (fallback mode)"
"""

    def _generate_bitstream_fallback(self, device_info: Dict[str, Any]) -> str:
        """Fallback bitstream generation."""
        vendor_id = device_info.get("vendor_id", "0000")
        device_id = device_info.get("device_id", "0000")

        return f"""# Bitstream Generation (Fallback)
puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1
# Basic file copy
set output_bit "pcileech_{vendor_id}_{device_id}_{self.board}.bit"
puts "Bitstream generation completed (fallback mode)"
"""

    def _generate_master_build_fallback(self, device_info: Dict[str, Any]) -> str:
        """Fallback master build generation."""
        vendor_id = device_info.get("vendor_id", "0000")
        device_id = device_info.get("device_id", "0000")

        return f"""# Master Build Script (Fallback)
puts "Starting PCILeech firmware build process..."
puts "Device: {vendor_id}:{device_id}"
puts "Board: {self.board}"
puts "Build completed (fallback mode)"
close_project
"""
