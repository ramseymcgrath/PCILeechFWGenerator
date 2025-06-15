#!/usr/bin/env python3
"""
Constraint Writer Module

Generates XDC constraint files for PCILeech FPGA builds by enumerating
top-level ports and ensuring all ports have proper constraints.
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

from .repo_manager import RepoManager

logger = logging.getLogger(__name__)


class ConstraintWriter:
    """Generates XDC constraints for FPGA builds."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize constraint writer.
        
        Args:
            output_dir: Directory where XDC files will be written
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_top_level_ports(self, verilog_files: List[str]) -> Set[str]:
        """
        Extract top-level port names from SystemVerilog files.
        
        Args:
            verilog_files: List of SystemVerilog file paths
            
        Returns:
            Set of port names found in top-level modules
        """
        ports = set()
        
        for file_path in verilog_files:
            if not os.path.exists(file_path):
                logger.warning(f"Verilog file not found: {file_path}")
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Look for top-level module (pcileech_top)
                if 'module pcileech_top' in content:
                    ports.update(self._extract_ports_from_module(content))
                    
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        return ports
    
    def _extract_ports_from_module(self, content: str) -> Set[str]:
        """Extract port names from module definition."""
        ports = set()
        
        # Remove comments and multi-line comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Find module definition
        module_match = re.search(r'module\s+pcileech_top\s*\((.*?)\);', content, re.DOTALL)
        if not module_match:
            return ports
        
        port_section = module_match.group(1)
        
        # Extract individual port declarations
        # Handle input, output, inout declarations
        port_patterns = [
            r'(?:input|output|inout)\s+(?:wire\s+|reg\s+)?(?:\[\d+:\d+\]\s+)?(\w+)',
            r'(?:input|output|inout)\s+(?:\[\d+:\d+\]\s+)?(\w+)',
        ]
        
        for pattern in port_patterns:
            matches = re.findall(pattern, port_section)
            ports.update(matches)
        
        # Also look for port declarations in the module body
        body_match = re.search(r'module\s+pcileech_top\s*\(.*?\);(.*?)endmodule', content, re.DOTALL)
        if body_match:
            body = body_match.group(1)
            # Find input/output declarations in body
            body_patterns = [
                r'(?:input|output|inout)\s+(?:wire\s+|reg\s+)?(?:\[\d+:\d+\]\s+)?(\w+)\s*;',
                r'(?:input|output|inout)\s+(?:\[\d+:\d+\]\s+)?(\w+)\s*;',
            ]
            
            for pattern in body_patterns:
                matches = re.findall(pattern, body)
                ports.update(matches)
        
        return ports
    
    def _extract_constrained_ports(self, xdc_content: str) -> Set[str]:
        """
        Extract port names that are already constrained in XDC content.
        
        Args:
            xdc_content: XDC file content
            
        Returns:
            Set of port names that have constraints
        """
        constrained_ports = set()
        
        # Look for set_property commands that reference ports
        port_patterns = [
            r'set_property\s+\w+\s+\w+\s+\[get_ports\s+\{?(\w+)\}?\]',
            r'set_property\s+\w+\s+\w+\s+\[get_ports\s+(\w+)\]',
        ]
        
        for pattern in port_patterns:
            matches = re.findall(pattern, xdc_content, re.IGNORECASE)
            constrained_ports.update(matches)
        
        return constrained_ports
    
    def generate_xdc_constraints(self, board: str, verilog_files: List[str]) -> str:
        """
        Generate XDC constraints for the specified board.
        
        Args:
            board: Board name
            verilog_files: List of SystemVerilog files to analyze
            
        Returns:
            Path to generated XDC file
        """
        # Extract all top-level ports
        all_ports = self.extract_top_level_ports(verilog_files)
        logger.info(f"Found {len(all_ports)} top-level ports: {sorted(all_ports)}")
        
        # Get existing XDC constraints from PCILeech repo
        try:
            board_xdc_content = RepoManager.read_xdc_constraints(board)
            logger.info(f"Loaded XDC constraints for board: {board}")
        except Exception as e:
            logger.warning(f"Could not load XDC constraints for board {board}: {e}")
            board_xdc_content = ""
        
        # Extract ports that are already constrained
        constrained_ports = self._extract_constrained_ports(board_xdc_content)
        logger.info(f"Found {len(constrained_ports)} already constrained ports: {sorted(constrained_ports)}")
        
        # Find unconstrained ports
        unconstrained_ports = all_ports - constrained_ports
        logger.info(f"Found {len(unconstrained_ports)} unconstrained ports: {sorted(unconstrained_ports)}")
        
        # Generate complete XDC file
        xdc_lines = []
        
        # Add header
        xdc_lines.append(f"# XDC constraints for board: {board}")
        xdc_lines.append(f"# Generated by PCILeech FW Generator")
        xdc_lines.append("")
        
        # Add existing board-specific constraints
        if board_xdc_content:
            xdc_lines.append("# === Board-specific constraints from PCILeech repo ===")
            xdc_lines.append(board_xdc_content)
            xdc_lines.append("")
        
        # Add constraints for unconstrained ports
        if unconstrained_ports:
            xdc_lines.append("# === Additional constraints for unconstrained ports ===")
            xdc_lines.append("# These ports need proper pin assignments for your specific board")
            xdc_lines.append("")
            
            for port in sorted(unconstrained_ports):
                # Add IOSTANDARD constraint to prevent NSTD-1 errors
                xdc_lines.append(f"set_property IOSTANDARD LVCMOS33 [get_ports {{{port}}}]")
                # Add PULLUP false to prevent UCIO-1 errors for unused ports
                xdc_lines.append(f"set_property PULLUP false [get_ports {{{port}}}]")
                xdc_lines.append("")
        
        # Write XDC file
        xdc_filename = f"{board}.xdc"
        xdc_path = self.output_dir / xdc_filename
        
        with open(xdc_path, 'w') as f:
            f.write('\n'.join(xdc_lines))
        
        logger.info(f"Generated XDC constraints: {xdc_path}")
        return str(xdc_path)
    
    def generate_constraints_for_build(self, board: str, source_files: List[str]) -> str:
        """
        Generate constraints for a build, filtering for SystemVerilog files.
        
        Args:
            board: Board name
            source_files: List of all source files
            
        Returns:
            Path to generated XDC file
        """
        # Filter for SystemVerilog files
        verilog_files = [
            f for f in source_files 
            if f.endswith(('.sv', '.v', '.vh'))
        ]
        
        return self.generate_xdc_constraints(board, verilog_files)


def create_constraint_writer(output_dir: str = "output") -> ConstraintWriter:
    """
    Factory function to create a ConstraintWriter instance.
    
    Args:
        output_dir: Output directory for generated files
        
    Returns:
        ConstraintWriter instance
    """
    return ConstraintWriter(output_dir)