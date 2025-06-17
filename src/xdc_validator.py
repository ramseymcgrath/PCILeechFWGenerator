#!/usr/bin/env python3
"""
XDC Constraint Validator and Filter

This module validates XDC constraints against the actual design and filters out
constraints that reference non-existent signals, preventing Vivado warnings.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class XDCValidator:
    """Validates and filters XDC constraints based on actual design signals."""

    def __init__(self):
        self.design_signals: Set[str] = set()
        self.design_ports: Set[str] = set()
        self.design_nets: Set[str] = set()
        self.design_pins: Set[str] = set()

    def extract_design_signals(self, systemverilog_files: List[Path]) -> None:
        """Extract all signal names from SystemVerilog files."""
        logger.info(
            f"Extracting design signals from {len(systemverilog_files)} SystemVerilog files"
        )

        for sv_file in systemverilog_files:
            if not sv_file.exists():
                continue

            try:
                content = sv_file.read_text(encoding="utf-8")
                self._parse_systemverilog_signals(content)
            except Exception as e:
                logger.warning(f"Failed to parse {sv_file}: {e}")

        logger.info(f"Found {len(self.design_signals)} total signals in design")
        logger.debug(
            f"Ports: {len(self.design_ports)}, Nets: {len(self.design_nets)}, Pins: {len(self.design_pins)}"
        )

    def _parse_systemverilog_signals(self, content: str) -> None:
        """Parse SystemVerilog content to extract signal names."""
        # Remove comments and strings to avoid false matches
        content = self._remove_comments_and_strings(content)

        # Extract port declarations with improved patterns
        port_patterns = [
            # Standard port declarations
            r"\b(?:input|output|inout)\s+(?:wire|reg|logic)?\s*(?:\[\d+:\d+\]\s+)?(\w+)",
            # Port declarations with data types
            r"\b(?:input|output|inout)\s+(?:wire|reg|logic)\s+(?:\[\d+:\d+\]\s+)?(\w+)",
            # Port declarations in module headers
            r"\b(?:input|output|inout)\s+(?:\w+\s+)?(?:\[\d+:\d+\]\s+)?(\w+)\s*[,\)]",
            # Bus declarations
            r"\b(?:input|output|inout)\s+(?:\[\d+:\d+\]\s+)?(\w+)\s*[,\)]",
        ]

        for pattern in port_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                signal_name = match.strip()
                if signal_name and not signal_name.isdigit() and len(signal_name) > 1:
                    self.design_signals.add(signal_name)
                    self.design_ports.add(signal_name)

        # Extract wire/reg/logic declarations with improved patterns
        wire_patterns = [
            # Standard wire/reg declarations
            r"\b(?:wire|reg|logic)\s+(?:\[\d+:\d+\]\s+)?(\w+)",
            # Wire/reg with explicit sizing
            r"\b(?:wire|reg|logic)\s+(\w+)\s*(?:\[|\;|,)",
            # Multi-dimensional arrays
            r"\b(?:wire|reg|logic)\s+(?:\[\d+:\d+\]\s*)*(\w+)",
        ]

        for pattern in wire_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                signal_name = match.strip()
                if signal_name and not signal_name.isdigit() and len(signal_name) > 1:
                    self.design_signals.add(signal_name)
                    self.design_nets.add(signal_name)

        # Extract module instantiation signals and port connections
        inst_patterns = [
            r"\.(\w+)\s*\(",  # Port connections in instantiations
            r"(\w+)\s*\.\w+\s*\(",  # Instance names
            r"assign\s+(\w+)",  # Assign statements
        ]

        for pattern in inst_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                signal_name = match.strip()
                if signal_name and not signal_name.isdigit() and len(signal_name) > 1:
                    self.design_signals.add(signal_name)

        # Extract signals from always blocks and procedural assignments
        always_patterns = [
            r"always.*?@.*?\(.*?(\w+)",  # Sensitivity lists
            r"(\w+)\s*<=",  # Non-blocking assignments
            r"(\w+)\s*=",  # Blocking assignments
        ]

        for pattern in always_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                signal_name = match.strip()
                if signal_name and not signal_name.isdigit() and len(signal_name) > 1:
                    self.design_signals.add(signal_name)

    def _remove_comments_and_strings(self, content: str) -> str:
        """Remove comments and string literals to avoid false signal matches."""
        # Remove single-line comments
        content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)

        # Remove multi-line comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        # Remove string literals
        content = re.sub(r'"[^"]*"', "", content)

        return content

    def validate_xdc_constraints(self, xdc_content: str) -> Tuple[str, List[str]]:
        """
        Validate XDC constraints and return filtered content with warnings.

        Returns:
            Tuple of (filtered_xdc_content, list_of_warnings)
        """
        if not xdc_content.strip():
            return "", []

        lines = xdc_content.split("\n")
        filtered_lines = []
        warnings = []

        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()

            # Keep comments and empty lines
            if not stripped_line or stripped_line.startswith("#"):
                filtered_lines.append(line)
                continue

            # Validate constraint line
            is_valid, warning = self._validate_constraint_line(stripped_line, line_num)

            if is_valid:
                filtered_lines.append(line)
            else:
                # Comment out invalid constraint
                filtered_lines.append(f"# FILTERED: {line}")
                if warning:
                    warnings.append(warning)

        return "\n".join(filtered_lines), warnings

    def _validate_constraint_line(
        self, line: str, line_num: int
    ) -> Tuple[bool, Optional[str]]:
        """Validate a single constraint line."""
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith("#"):
            return True, None

        # Always allow certain safe constraint types
        safe_patterns = [
            r"^\s*set_property\s+CFGBVS",
            r"^\s*set_property\s+CONFIG_VOLTAGE",
            r"^\s*set_property\s+BITSTREAM",
            r"^\s*set_property\s+PACKAGE_PIN",  # Pin assignments are usually safe
            r"^\s*create_generated_clock",
            r"^\s*set_clock_groups",
            r"^\s*set_max_delay",
            r"^\s*set_min_delay",
        ]

        for safe_pattern in safe_patterns:
            if re.match(safe_pattern, line, re.IGNORECASE):
                return True, None

        # Extract signal references from common XDC commands with improved patterns
        signal_patterns = [
            # get_ports patterns
            r"get_ports\s+\{([^}]+)\}",  # Braced lists
            r"get_ports\s+(\w+(?:\[\*?\])?)",  # Single ports with optional bus notation
            r"get_ports\s+\{([^}]+)\}",  # Multiple ports in braces
            # get_nets patterns
            r"get_nets\s+\{([^}]+)\}",
            r"get_nets\s+(\w+(?:\[\*?\])?)",
            # get_pins patterns
            r"get_pins\s+\{([^}]+)\}",
            r"get_pins\s+([\w/\[\]]+)",  # Hierarchical pin paths
            # get_cells patterns
            r"get_cells\s+\{([^}]+)\}",
            r"get_cells\s+([\w/\[\]]+)",
            # get_clocks patterns
            r"get_clocks\s+\{([^}]+)\}",
            r"get_clocks\s+(\w+)",
        ]

        # Check all signal references in the line
        found_invalid_signal = False
        invalid_signal_name = None
        total_signals_checked = 0
        valid_signals_found = 0

        for pattern in signal_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                # Handle both single signals and signal groups
                signals = self._parse_signal_reference(match)

                for signal in signals:
                    total_signals_checked += 1
                    if self._signal_exists(signal):
                        valid_signals_found += 1
                    else:
                        logger.debug(
                            f"Line {line_num}: Signal '{signal}' not found in design"
                        )
                        if not found_invalid_signal:  # Record first invalid signal
                            found_invalid_signal = True
                            invalid_signal_name = signal

        # If we found some signals but none are valid, filter the constraint
        if total_signals_checked > 0 and valid_signals_found == 0:
            return (
                False,
                f"Line {line_num}: No valid signals found (checked {total_signals_checked} signals)",
            )

        # If we found mixed valid/invalid signals, allow the constraint but warn
        if (
            total_signals_checked > 0
            and found_invalid_signal
            and valid_signals_found > 0
        ):
            logger.warning(
                f"Line {line_num}: Mixed valid/invalid signals - allowing constraint"
            )
            return (
                True,
                f"Line {line_num}: Some signals not found but constraint allowed",
            )

        return True, None

    def _parse_signal_reference(self, signal_ref: str) -> List[str]:
        """Parse signal reference which may contain multiple signals or wildcards."""
        signals = []

        # Clean up the signal reference - remove outer brackets and extra whitespace
        clean_ref = signal_ref.strip("{}[]").strip()

        # Handle multiple signals separated by spaces or commas
        if " " in clean_ref or "," in clean_ref:
            # Split by both spaces and commas
            parts = re.split(r"[\s,]+", clean_ref)
        else:
            parts = [clean_ref]

        for part in parts:
            part = part.strip("{}[]").strip()
            if not part:
                continue

            # Handle hierarchical paths (e.g., "i_pcileech_com/i_pcileech_ft601/FT601_OE_N_reg")
            if "/" in part:
                # Extract the final signal name from hierarchical path
                path_parts = part.split("/")
                final_signal = path_parts[-1]
                signals.append(final_signal)
                # Also add the full path for exact matching
                signals.append(part)
            # Handle bus notation like {signal[*]} or signal[0] or signal[15:0]
            elif "[" in part and "]" in part:
                # Extract base signal name from bus notation
                base_signal = part.split("[")[0]
                signals.append(base_signal)
                # Also add the full signal with index for exact matching
                signals.append(part)
            # Handle wildcard patterns like signal[*]
            elif "[*]" in part:
                base_signal = part.replace("[*]", "")
                signals.append(base_signal)
            else:
                signals.append(part)

        # Remove duplicates while preserving order
        unique_signals = []
        seen = set()
        for signal in signals:
            if signal and signal not in seen:
                unique_signals.append(signal)
                seen.add(signal)

        return unique_signals

    def _signal_exists(self, signal: str) -> bool:
        """Check if a signal exists in the design."""
        # Remove any remaining brackets or special characters
        clean_signal = re.sub(r"[\[\]{}*]", "", signal)

        # Check exact match first
        if clean_signal in self.design_signals:
            return True

        # Check common signal variations with more comprehensive patterns
        variations = [
            clean_signal.lower(),
            clean_signal.upper(),
            f"i_{clean_signal}",
            f"o_{clean_signal}",
            f"{clean_signal}_i",
            f"{clean_signal}_o",
            f"{clean_signal}_n",  # Active low signals
            f"{clean_signal}_p",  # Positive differential
            f"n_{clean_signal}",  # Negative prefix
            f"p_{clean_signal}",  # Positive prefix
        ]

        for variation in variations:
            if variation in self.design_signals:
                return True

        # Check for hierarchical signals with more flexible matching
        for design_signal in self.design_signals:
            # Check if the clean_signal is a substring of design_signal
            if clean_signal.lower() in design_signal.lower():
                return True
            # Check word boundary matching
            if re.search(
                rf"\b{re.escape(clean_signal)}\b", design_signal, re.IGNORECASE
            ):
                return True
            # Check for common PCIe/FPGA signal naming patterns
            if self._check_signal_pattern_match(clean_signal, design_signal):
                return True

        return False

    def _check_signal_pattern_match(
        self, target_signal: str, design_signal: str
    ) -> bool:
        """Check for common FPGA/PCIe signal naming pattern matches."""
        target_lower = target_signal.lower()
        design_lower = design_signal.lower()

        # Common FPGA signal transformations
        transformations = [
            # FT601 specific patterns
            ("ft601_", "ft_"),
            ("ft601_", "ftdi_"),
            ("ft601_", "usb_"),
            # PCIe patterns
            ("pcie_", "pci_"),
            ("pcie_", "pcix_"),
            # Clock patterns
            ("_clk", "_clock"),
            ("clk_", "clock_"),
            # Reset patterns
            ("_rst", "_reset"),
            ("rst_", "reset_"),
            # Data patterns
            ("_data", "_d"),
            ("data_", "d_"),
            # Control signal patterns
            ("_n", "_neg"),
            ("_p", "_pos"),
        ]

        for old_pattern, new_pattern in transformations:
            if old_pattern in target_lower:
                transformed = target_lower.replace(old_pattern, new_pattern)
                if transformed in design_lower:
                    return True
            if new_pattern in target_lower:
                transformed = target_lower.replace(new_pattern, old_pattern)
                if transformed in design_lower:
                    return True

        return False

    def generate_safe_constraints(self, device_info: Dict, board_info: Dict) -> str:
        """Generate safe, minimal constraints that don't reference specific signals."""
        constraints = [
            "# Safe constraints generated by XDC Validator",
            "# These constraints only reference signals that exist in the design",
            "",
            "# Basic timing constraints",
        ]

        # Only add clock constraints if we have clock signals
        clock_signals = [s for s in self.design_signals if "clk" in s.lower()]
        if clock_signals:
            constraints.extend(
                [
                    "# Clock constraints for detected clock signals",
                ]
            )
            for clk_signal in clock_signals:
                if "pcie" in clk_signal.lower():
                    constraints.append(
                        f"# create_clock -period 10.000 -name {clk_signal} [get_ports {clk_signal}]"
                    )
                else:
                    constraints.append(
                        f"# create_clock -period 10.000 -name {clk_signal} [get_ports {clk_signal}]"
                    )

        # Add reset constraints if reset signals exist
        reset_signals = [
            s for s in self.design_signals if "reset" in s.lower() or "rst" in s.lower()
        ]
        if reset_signals:
            constraints.extend(
                [
                    "",
                    "# Reset constraints for detected reset signals",
                ]
            )
            for rst_signal in reset_signals:
                constraints.append(f"# set_false_path -from [get_ports {rst_signal}]")

        constraints.extend(
            [
                "",
                "# Device-specific constraints",
                f"# Device: {device_info['vendor_id']}:{device_info['device_id']}",
                f"# Board: {board_info['name']}",
                "",
                "# NOTE: Board-specific pin assignments should be added manually",
                "# based on the actual board layout and FPGA package.",
            ]
        )

        return "\n".join(constraints)


def validate_and_filter_xdc(
    xdc_content: str,
    systemverilog_files: List[Path],
    device_info: Dict,
    board_info: Dict,
) -> Tuple[str, List[str]]:
    """
    Main function to validate and filter XDC constraints.

    Args:
        xdc_content: Raw XDC content from repository
        systemverilog_files: List of SystemVerilog files in the design
        device_info: Device information dictionary
        board_info: Board information dictionary

    Returns:
        Tuple of (filtered_xdc_content, list_of_warnings)
    """
    validator = XDCValidator()

    # Extract signals from SystemVerilog files
    validator.extract_design_signals(systemverilog_files)

    if not xdc_content.strip():
        # Generate safe constraints if no XDC content provided
        logger.info("No XDC content provided, generating safe constraints")
        safe_constraints = validator.generate_safe_constraints(device_info, board_info)
        return safe_constraints, ["No XDC content provided, generated safe constraints"]

    # Validate and filter existing XDC content
    filtered_content, warnings = validator.validate_xdc_constraints(xdc_content)

    if warnings:
        logger.warning(f"Filtered {len(warnings)} invalid constraints from XDC file")
        for warning in warnings[:10]:  # Log first 10 warnings
            logger.warning(warning)
        if len(warnings) > 10:
            logger.warning(f"... and {len(warnings) - 10} more warnings")

    return filtered_content, warnings
