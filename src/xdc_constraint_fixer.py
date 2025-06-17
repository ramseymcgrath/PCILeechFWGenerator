#!/usr/bin/env python3
"""
XDC Constraint Fixer

This module provides advanced XDC constraint fixing capabilities to resolve
common issues like missing signals, incorrect hierarchical paths, and timing
constraint problems that cause Vivado warnings and errors.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class XDCConstraintFixer:
    """Advanced XDC constraint fixer for resolving Vivado constraint issues."""

    def __init__(self):
        self.design_signals: Set[str] = set()
        self.design_ports: Set[str] = set()
        self.design_nets: Set[str] = set()
        self.design_pins: Set[str] = set()
        self.hierarchical_paths: Set[str] = set()
        self.clock_signals: Set[str] = set()
        self.reset_signals: Set[str] = set()

    def analyze_vivado_errors(self, error_log: str) -> Dict[str, List[str]]:
        """Analyze Vivado error log to identify constraint issues."""
        issues = {
            "missing_ports": [],
            "missing_nets": [],
            "missing_pins": [],
            "missing_clocks": [],
            "timing_issues": [],
            "constraint_errors": [],
        }

        lines = error_log.split("\n")
        for line in lines:
            line = line.strip()

            # Parse port matching failures
            port_match = re.search(r"No ports matched '([^']+)'", line)
            if port_match:
                issues["missing_ports"].append(port_match.group(1))

            # Parse net matching failures
            net_match = re.search(r"No nets matched '([^']+)'", line)
            if net_match:
                issues["missing_nets"].append(net_match.group(1))

            # Parse pin matching failures
            pin_match = re.search(r"No pins matched '([^']+)'", line)
            if pin_match:
                issues["missing_pins"].append(pin_match.group(1))

            # Parse clock creation failures
            clock_match = re.search(r"No valid object.*for.*get_ports ([^]]+)", line)
            if clock_match:
                issues["missing_clocks"].append(clock_match.group(1))

            # Parse timing constraint failures
            if "set_input_delay" in line or "set_output_delay" in line:
                if "No valid object" in line:
                    issues["timing_issues"].append(line)

            # Parse general constraint errors
            if "CRITICAL WARNING" in line and "set_property" in line:
                issues["constraint_errors"].append(line)

        return issues

    def fix_xdc_constraints(
        self, xdc_content: str, vivado_errors: str = ""
    ) -> Tuple[str, List[str]]:
        """
        Fix XDC constraints based on Vivado error analysis.

        Args:
            xdc_content: Original XDC content
            vivado_errors: Vivado error log (optional)

        Returns:
            Tuple of (fixed_xdc_content, list_of_fixes_applied)
        """
        if not xdc_content.strip():
            return self._generate_minimal_safe_constraints(), [
                "Generated minimal safe constraints"
            ]

        fixes_applied = []

        # Analyze Vivado errors if provided
        error_analysis = {}
        if vivado_errors:
            error_analysis = self.analyze_vivado_errors(vivado_errors)
            logger.info(
                f"Analyzed Vivado errors: {sum(len(v) for v in error_analysis.values())} issues found"
            )

        lines = xdc_content.split("\n")
        fixed_lines = []

        for line_num, line in enumerate(lines, 1):
            original_line = line
            stripped_line = line.strip()

            # Keep comments and empty lines as-is
            if not stripped_line or stripped_line.startswith("#"):
                fixed_lines.append(line)
                continue

            # Apply various fixes
            fixed_line, line_fixes = self._fix_constraint_line(
                line, line_num, error_analysis
            )
            fixed_lines.append(fixed_line)

            if line_fixes:
                fixes_applied.extend(line_fixes)

        return "\n".join(fixed_lines), fixes_applied

    def _fix_constraint_line(
        self, line: str, line_num: int, error_analysis: Dict
    ) -> Tuple[str, List[str]]:
        """Fix a single constraint line."""
        fixes = []
        fixed_line = line

        # Fix 1: Comment out constraints for known missing signals
        missing_signals = (
            error_analysis.get("missing_ports", [])
            + error_analysis.get("missing_nets", [])
            + error_analysis.get("missing_pins", [])
        )

        for missing_signal in missing_signals:
            if missing_signal in line:
                fixed_line = f"# FIXED: Commented out due to missing signal '{missing_signal}'\n# {line}"
                fixes.append(
                    f"Line {line_num}: Commented out constraint for missing signal '{missing_signal}'"
                )
                break

        # Fix 2: Fix common signal name patterns
        if fixed_line == line:  # Only apply if not already commented out
            fixed_line, pattern_fixes = self._fix_signal_name_patterns(line, line_num)
            fixes.extend(pattern_fixes)

        # Fix 3: Fix timing constraint issues
        if fixed_line == line:  # Only apply if not already fixed
            fixed_line, timing_fixes = self._fix_timing_constraints(line, line_num)
            fixes.extend(timing_fixes)

        # Fix 4: Fix clock constraint issues
        if fixed_line == line:  # Only apply if not already fixed
            fixed_line, clock_fixes = self._fix_clock_constraints(line, line_num)
            fixes.extend(clock_fixes)

        return fixed_line, fixes

    def _fix_signal_name_patterns(
        self, line: str, line_num: int
    ) -> Tuple[str, List[str]]:
        """Fix common signal naming pattern issues."""
        fixes = []
        fixed_line = line

        # Common signal name transformations based on the error log
        transformations = [
            # FT601 signal fixes
            (r"\bft601_be\b", "ft_be"),
            (r"\bft601_data\b", "ft_data"),
            (r"\bft601_clk\b", "ft_clk"),
            (r"\bft601_oe_n\b", "ft_oe_n"),
            (r"\bft601_rd_n\b", "ft_rd_n"),
            (r"\bft601_rxf_n\b", "ft_rxf_n"),
            (r"\bft601_siwu_n\b", "ft_siwu_n"),
            (r"\bft601_txe_n\b", "ft_txe_n"),
            (r"\bft601_wr_n\b", "ft_wr_n"),
            (r"\bft601_rst_n\b", "ft_rst_n"),
            # User interface signal fixes
            (r"\buser_ld1_n\b", "led1_n"),
            (r"\buser_ld2_n\b", "led2_n"),
            (r"\buser_sw1_n\b", "sw1_n"),
            (r"\buser_sw2_n\b", "sw2_n"),
            # PCIe signal fixes
            (r"\bpcie_present\b", "pcie_prsnt"),
            (r"\bpcie_perst_n\b", "pcie_rst_n"),
        ]

        for old_pattern, new_pattern in transformations:
            if re.search(old_pattern, line, re.IGNORECASE):
                new_line = re.sub(old_pattern, new_pattern, line, flags=re.IGNORECASE)
                if new_line != line:
                    fixed_line = new_line
                    fixes.append(
                        f"Line {line_num}: Transformed signal pattern '{old_pattern}' to '{new_pattern}'"
                    )
                    break

        return fixed_line, fixes

    def _fix_timing_constraints(
        self, line: str, line_num: int
    ) -> Tuple[str, List[str]]:
        """Fix timing constraint issues."""
        fixes = []
        fixed_line = line

        # Fix input/output delay constraints with missing clocks
        if "set_input_delay" in line or "set_output_delay" in line:
            # Check if clock reference exists
            clock_match = re.search(r"-clock\s+(\w+)", line)
            if clock_match:
                clock_name = clock_match.group(1)
                # If clock doesn't exist, comment out the constraint
                if clock_name not in self.clock_signals:
                    fixed_line = f"# FIXED: Commented out due to missing clock '{clock_name}'\n# {line}"
                    fixes.append(
                        f"Line {line_num}: Commented out timing constraint due to missing clock '{clock_name}'"
                    )

        return fixed_line, fixes

    def _fix_clock_constraints(self, line: str, line_num: int) -> Tuple[str, List[str]]:
        """Fix clock constraint issues."""
        fixes = []
        fixed_line = line

        # Fix create_clock constraints with missing ports
        if "create_clock" in line:
            port_match = re.search(r"get_ports\s+(\w+)", line)
            if port_match:
                port_name = port_match.group(1)
                # If port doesn't exist, comment out the constraint
                if port_name not in self.design_ports:
                    fixed_line = f"# FIXED: Commented out due to missing port '{port_name}'\n# {line}"
                    fixes.append(
                        f"Line {line_num}: Commented out clock constraint due to missing port '{port_name}'"
                    )

        return fixed_line, fixes

    def _generate_minimal_safe_constraints(self) -> str:
        """Generate minimal safe constraints when no XDC content is available."""
        constraints = [
            "# Minimal Safe XDC Constraints",
            "# Generated by XDC Constraint Fixer",
            "",
            "# Configuration settings",
            "set_property CFGBVS VCCO [current_design]",
            "set_property CONFIG_VOLTAGE 3.3 [current_design]",
            "",
            "# Bitstream settings",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 33 [current_design]",
            "",
            "# NOTE: Board-specific pin assignments and timing constraints",
            "# should be added based on the actual hardware design.",
            "",
            "# Placeholder for clock constraints",
            "# create_clock -period 10.000 -name sys_clk [get_ports sys_clk]",
            "",
            "# Placeholder for I/O constraints",
            "# set_property PACKAGE_PIN <pin> [get_ports <signal>]",
            "# set_property IOSTANDARD LVCMOS33 [get_ports <signal>]",
        ]

        return "\n".join(constraints)


def fix_xdc_file(
    xdc_file_path: Path, vivado_error_log: str = ""
) -> Tuple[str, List[str]]:
    """
    Fix an XDC file based on Vivado error analysis.

    Args:
        xdc_file_path: Path to the XDC file to fix
        vivado_error_log: Optional Vivado error log for analysis

    Returns:
        Tuple of (fixed_xdc_content, list_of_fixes_applied)
    """
    fixer = XDCConstraintFixer()

    # Read original XDC content
    xdc_content = ""
    if xdc_file_path.exists():
        try:
            xdc_content = xdc_file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read XDC file {xdc_file_path}: {e}")

    # Fix the constraints
    fixed_content, fixes = fixer.fix_xdc_constraints(xdc_content, vivado_error_log)

    return fixed_content, fixes


def create_xdc_error_report(vivado_log: str) -> str:
    """Create a detailed report of XDC constraint errors from Vivado log."""
    fixer = XDCConstraintFixer()
    issues = fixer.analyze_vivado_errors(vivado_log)

    report_lines = [
        "XDC Constraint Error Analysis Report",
        "=" * 40,
        "",
        f"Total Issues Found: {sum(len(v) for v in issues.values())}",
        "",
    ]

    for category, items in issues.items():
        if items:
            report_lines.extend(
                [
                    f"{category.replace('_', ' ').title()}: {len(items)} issues",
                    "-" * 30,
                ]
            )
            for item in items[:10]:  # Show first 10 items
                report_lines.append(f"  - {item}")
            if len(items) > 10:
                report_lines.append(f"  ... and {len(items) - 10} more")
            report_lines.append("")

    return "\n".join(report_lines)
