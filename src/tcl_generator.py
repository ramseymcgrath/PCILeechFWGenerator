#!/usr/bin/env python3
"""
TCL Script Generation Module

Template-based TCL generator for PCILeech firmware building.
Replaces hardcoded string generation with Jinja2 templates.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from board_config import get_board_info, get_fpga_part, get_pcie_ip_type
from string_utils import generate_tcl_header_comment, log_info_safe, safe_format
from template_renderer import TemplateRenderer, TemplateRenderError

logger = logging.getLogger(__name__)


class TCLGenerator:
    """Generates TCL build scripts for PCILeech firmware using templates."""

    def __init__(self, board: str, output_dir: Path):
        """
        Initialize the TCL generator.

        Args:
            board: Target board name
            output_dir: Output directory for generated files
        """
        self.board = board
        self.output_dir = output_dir

        # Initialize template renderer
        self.template_renderer = TemplateRenderer()
        logger.info("Template-based TCL generator initialized")

        # Template mapping for each build stage
        self.template_mapping = {
            "project_setup": "tcl/project_setup.j2",
            "ip_config_pcie7x": "tcl/ip_config_pcie7x.j2",
            "ip_config": "tcl/ip_config.j2",
            "sources": "tcl/sources.j2",
            "constraints": "tcl/constraints.j2",
            "synthesis": "tcl/synthesis.j2",
            "implementation": "tcl/implementation.j2",
            "bitstream": "tcl/bitstream.j2",
            "master_build": "tcl/master_build.j2",
        }

    def _get_template_context(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build template context with all necessary variables.

        Args:
            device_info: Device configuration information

        Returns:
            Template context dictionary
        """
        # Get board configuration
        board_info = get_board_info(self.board)
        fpga_part = get_fpga_part(self.board)
        pcie_ip_type = get_pcie_ip_type(fpga_part)

        # Build comprehensive context with safe defaults
        context = {
            "device": {
                "vendor_id": device_info.get("vendor_id", "0x0000"),
                "device_id": device_info.get("device_id", "0x0000"),
                "class_code": device_info.get("class_code", "0x000000"),
                "revision_id": device_info.get("revision_id", "0x00"),
            },
            "board": {
                "name": self.board,
                "fpga_part": fpga_part,
                "fpga_family": board_info["fpga_family"],
                "pcie_ip_type": pcie_ip_type,
            },
            "project": {
                "name": "pcileech_firmware",
                "dir": "./vivado_project",
                "output_dir": ".",
            },
            "build": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "jobs": 8,
            },
            "header": generate_tcl_header_comment(
                "PCILeech Firmware Build Script",
                vendor_id=device_info["vendor_id"],
                device_id=device_info["device_id"],
                class_code=device_info["class_code"],
                board=self.board,
                fpga_part=fpga_part,
                generated=time.strftime("%Y-%m-%d %H:%M:%S"),
            ),
        }

        return context

    def _render_template_with_fallback(
        self, template_name: str, context: Dict[str, Any]
    ) -> str:
        """
        Render template with fallback to hardcoded generation if template fails.

        Args:
            template_name: Name of template to render
            context: Template context

        Returns:
            Rendered template content

        Raises:
            TemplateRenderError: If template rendering fails and no fallback available
        """
        try:
            if self.template_renderer.template_exists(template_name):
                content = self.template_renderer.render_template(template_name, context)
                logger.debug(f"Successfully rendered template: {template_name}")
                return content
            else:
                logger.warning(f"Template not found: {template_name}")
                raise TemplateRenderError(f"Template not found: {template_name}")

        except TemplateRenderError as e:
            logger.error(f"Template rendering failed for {template_name}: {e}")
            raise

    def generate_device_tcl_script(self, device_info: Dict[str, Any]) -> str:
        """Generate device-specific TCL script using templates."""
        context = self._get_template_context(device_info)

        # Generate comprehensive script by combining individual components
        # This approach ensures compatibility with existing tests that expect
        # create_project and set_property in the main script
        try:
            script_parts = []

            # Project setup
            script_parts.append(
                self._render_template_with_fallback("tcl/project_setup.j2", context)
            )

            # IP configuration based on FPGA type
            pcie_ip_type = context["board"]["pcie_ip_type"]
            if pcie_ip_type == "pcie_7x":
                script_parts.append(
                    self._render_template_with_fallback(
                        "tcl/ip_config_pcie7x.j2", context
                    )
                )
            else:
                script_parts.append(
                    self._render_template_with_fallback("tcl/ip_config.j2", context)
                )

            # Sources, constraints, synthesis, implementation, bitstream
            for stage in [
                "sources",
                "constraints",
                "synthesis",
                "implementation",
                "bitstream",
            ]:
                template_name = f"tcl/{stage}.j2"
                script_parts.append(
                    self._render_template_with_fallback(template_name, context)
                )

            return "\n\n".join(script_parts)

        except TemplateRenderError as e:
            logger.error(f"Failed to generate TCL script: {e}")
            raise

    def generate_separate_tcl_files(self, device_info: Dict[str, Any]) -> List[str]:
        """Generate separate TCL files for different build components."""
        context = self._get_template_context(device_info)
        tcl_files = []

        # Define the build stages and their corresponding files
        build_stages = [
            ("project_setup", "01_project_setup.tcl", "tcl/project_setup.j2"),
            ("ip_config", "02_ip_config.tcl", self._get_ip_config_template(context)),
            ("sources", "03_add_sources.tcl", "tcl/sources.j2"),
            ("constraints", "04_constraints.tcl", "tcl/constraints.j2"),
            ("synthesis", "05_synthesis.tcl", "tcl/synthesis.j2"),
            ("implementation", "06_implementation.tcl", "tcl/implementation.j2"),
            ("bitstream", "07_bitstream.tcl", "tcl/bitstream.j2"),
            ("master_build", "build_all.tcl", "tcl/master_build.j2"),
        ]

        for stage_name, filename, template_name in build_stages:
            try:
                content = self._render_template_with_fallback(template_name, context)
                file_path = self.output_dir / filename

                with open(file_path, "w") as f:
                    f.write(content)

                tcl_files.append(str(file_path))
                log_info_safe(
                    logger,
                    "Generated {stage} TCL: {filename}",
                    stage=stage_name,
                    filename=filename,
                )

            except TemplateRenderError as e:
                logger.error(f"Failed to generate {stage_name} TCL: {e}")
                raise

        return tcl_files

    def _get_ip_config_template(self, context: Dict[str, Any]) -> str:
        """Determine which IP config template to use based on FPGA type."""
        pcie_ip_type = context["board"]["pcie_ip_type"]

        if pcie_ip_type == "pcie_7x":
            return "tcl/ip_config_pcie7x.j2"
        else:
            return "tcl/ip_config.j2"

    def generate_project_setup_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate project setup TCL script."""
        context = self._get_template_context(device_info)
        return self._render_template_with_fallback("tcl/project_setup.j2", context)

    def generate_ip_config_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate IP core configuration TCL script."""
        context = self._get_template_context(device_info)
        template_name = self._get_ip_config_template(context)
        return self._render_template_with_fallback(template_name, context)

    def generate_sources_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate source file management TCL script."""
        context = self._get_template_context(device_info)
        return self._render_template_with_fallback("tcl/sources.j2", context)

    def generate_constraints_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate constraints TCL script."""
        context = self._get_template_context(device_info)
        return self._render_template_with_fallback("tcl/constraints.j2", context)

    def generate_synthesis_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate synthesis TCL script."""
        context = self._get_template_context(device_info)
        return self._render_template_with_fallback("tcl/synthesis.j2", context)

    def generate_implementation_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate implementation TCL script."""
        context = self._get_template_context(device_info)
        return self._render_template_with_fallback("tcl/implementation.j2", context)

    def generate_bitstream_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate bitstream generation TCL script."""
        context = self._get_template_context(device_info)
        return self._render_template_with_fallback("tcl/bitstream.j2", context)

    def generate_master_build_tcl(self, device_info: Dict[str, Any]) -> str:
        """Generate master build script that sources all other TCL files."""
        context = self._get_template_context(device_info)
        return self._render_template_with_fallback("tcl/master_build.j2", context)

    # Legacy method compatibility - these now use templates but maintain the same API
    def generate_axi_pcie_config(
        self, vendor_id: str, device_id: str, revision_id: str
    ) -> str:
        """Generate custom PCIe configuration for Artix-7 35T parts."""
        context = {
            "device": {
                "vendor_id": vendor_id,
                "device_id": device_id,
                "revision_id": revision_id,
            }
        }

        # Use template if available, otherwise fallback to hardcoded
        try:
            if self.template_renderer.template_exists("tcl/ip_config_axi_pcie.j2"):
                return self._render_template_with_fallback(
                    "tcl/ip_config_axi_pcie.j2", context
                )
        except TemplateRenderError:
            pass

        # Clean hex values (remove 0x prefix if present)
        clean_vendor_id = (
            vendor_id.replace("0x", "") if vendor_id.startswith("0x") else vendor_id
        )
        clean_device_id = (
            device_id.replace("0x", "") if device_id.startswith("0x") else device_id
        )
        clean_revision_id = (
            revision_id.replace("0x", "")
            if revision_id.startswith("0x")
            else revision_id
        )

        # Hardcoded fallback for AXI PCIe
        return f"""# Artix-7 35T PCIe Configuration
# This part uses custom SystemVerilog modules instead of Xilinx IP cores
# Device configuration: {vendor_id}:{device_id} (Rev: {revision_id})

# Set device-specific parameters for custom PCIe implementation
set DEVICE_ID 0x{clean_device_id}
set VENDOR_ID 0x{clean_vendor_id}
set REVISION_ID 0x{clean_revision_id}
set SUBSYSTEM_VENDOR_ID 0x{clean_vendor_id}
set SUBSYSTEM_ID 0x0000

puts "Using custom PCIe implementation for Artix-7 35T"
puts "Device ID: $DEVICE_ID"
puts "Vendor ID: $VENDOR_ID"
puts "Revision ID: $REVISION_ID"

# No IP cores required - PCIe functionality implemented in custom SystemVerilog modules"""

    def generate_pcie_7x_config(
        self, vendor_id: str, device_id: str, revision_id: str
    ) -> str:
        """Generate PCIe 7-series IP configuration."""
        context = {
            "device": {
                "vendor_id": vendor_id,
                "device_id": device_id,
                "revision_id": revision_id,
            }
        }

        try:
            return self._render_template_with_fallback(
                "tcl/ip_config_pcie7x.j2", context
            )
        except TemplateRenderError:
            # Hardcoded fallback
            return f"""# Create PCIe 7-series IP core
create_ip -name pcie_7x -vendor xilinx.com -library ip -module_name pcie_7x_0

# Configure PCIe IP core with device-specific settings
set_property -dict [list \\
    CONFIG.Bar0_Scale {{Kilobytes}} \\
    CONFIG.Bar0_Size {{128_KB}} \\
    CONFIG.Device_ID {{0x{device_id}}} \\
    CONFIG.Vendor_ID {{0x{vendor_id}}} \\
    CONFIG.Subsystem_Vendor_ID {{0x{vendor_id}}} \\
    CONFIG.Subsystem_ID {{0x0000}} \\
    CONFIG.Revision_ID {{0x{revision_id}}} \\
    CONFIG.Link_Speed {{2.5_GT/s}} \\
    CONFIG.Max_Link_Width {{X1}} \\
    CONFIG.Maximum_Link_Width {{X1}} \\
    CONFIG.Enable_Slot_Clock_Configuration {{false}} \\
    CONFIG.Legacy_Interrupt {{NONE}} \\
    CONFIG.MSI_Enabled {{false}} \\
    CONFIG.MSI_64b_Address_Capable {{false}} \\
    CONFIG.MSIX_Enabled {{true}} \\
] [get_ips pcie_7x_0]"""

    def generate_pcie_ultrascale_config(
        self, vendor_id: str, device_id: str, revision_id: str
    ) -> str:
        """Generate PCIe UltraScale IP configuration."""
        context = {
            "device": {
                "vendor_id": vendor_id,
                "device_id": device_id,
                "revision_id": revision_id,
            }
        }

        try:
            if self.template_renderer.template_exists("tcl/ip_config_ultrascale.j2"):
                return self._render_template_with_fallback(
                    "tcl/ip_config_ultrascale.j2", context
                )
        except TemplateRenderError:
            pass

        # Hardcoded fallback
        return f"""# Create PCIe UltraScale IP core
create_ip -name pcie4_uscale_plus -vendor xilinx.com -library ip -module_name pcie4_uscale_plus_0

# Configure PCIe UltraScale IP core with device-specific settings
set_property -dict [list \\
    CONFIG.PL_LINK_CAP_MAX_LINK_SPEED {{2.5_GT/s}} \\
    CONFIG.PL_LINK_CAP_MAX_LINK_WIDTH {{X1}} \\
    CONFIG.AXISTEN_IF_EXT_512_RQ_STRADDLE {{false}} \\
    CONFIG.PF0_DEVICE_ID {{0x{device_id}}} \\
    CONFIG.PF0_VENDOR_ID {{0x{vendor_id}}} \\
    CONFIG.PF0_SUBSYSTEM_VENDOR_ID {{0x{vendor_id}}} \\
    CONFIG.PF0_SUBSYSTEM_ID {{0x0000}} \\
    CONFIG.PF0_REVISION_ID {{0x{revision_id}}} \\
    CONFIG.PF0_CLASS_CODE {{0x040300}} \\
    CONFIG.PF0_BAR0_SCALE {{Kilobytes}} \\
    CONFIG.PF0_BAR0_SIZE {{128}} \\
    CONFIG.PF0_MSI_ENABLED {{false}} \\
    CONFIG.PF0_MSIX_ENABLED {{true}} \\
] [get_ips pcie4_uscale_plus_0]"""
