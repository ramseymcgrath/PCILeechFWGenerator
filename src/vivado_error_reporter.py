#!/usr/bin/env python3
"""
Vivado Error Reporter - Enhanced Error Detection and Reporting

This module provides comprehensive error detection, parsing, and reporting
for Vivado builds with colored console output and detailed error analysis.
"""

import logging
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class VivadoErrorType(Enum):
    """Types of Vivado errors."""
    SYNTAX_ERROR = "syntax"
    TIMING_ERROR = "timing"
    RESOURCE_ERROR = "resource"
    CONSTRAINT_ERROR = "constraint"
    IP_ERROR = "ip"
    SIMULATION_ERROR = "simulation"
    IMPLEMENTATION_ERROR = "implementation"
    BITSTREAM_ERROR = "bitstream"
    LICENSING_ERROR = "licensing"
    FILE_ERROR = "file"
    UNKNOWN_ERROR = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class VivadoError:
    """Structured representation of a Vivado error."""
    error_type: VivadoErrorType
    severity: ErrorSeverity
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    details: Optional[str] = None
    suggested_fix: Optional[str] = None
    raw_message: Optional[str] = None
    
    @property
    def location_str(self) -> str:
        """Get formatted location string."""
        if self.file_path:
            location = self.file_path
            if self.line_number:
                location += f":{self.line_number}"
                if self.column:
                    location += f":{self.column}"
            return location
        return "Unknown location"
    
    @property
    def severity_icon(self) -> str:
        """Get icon for severity level."""
        icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨",
        }
        return icons.get(self.severity, "❓")


class ColorFormatter:
    """ANSI color formatter for console output."""
    
    # ANSI color codes
    COLORS = {
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'MAGENTA': '\033[95m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
        'RESET': '\033[0m'
    }
    
    def __init__(self, use_colors: Optional[bool] = None):
        """Initialize color formatter."""
        if use_colors is None:
            # Auto-detect if terminal supports colors
            self.use_colors = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        else:
            self.use_colors = use_colors
    
    def colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if not self.use_colors:
            return text
        color_code = self.COLORS.get(color.upper(), '')
        reset_code = self.COLORS['RESET']
        return f"{color_code}{text}{reset_code}"
    
    def error(self, text: str) -> str:
        """Format error text."""
        return self.colorize(text, 'RED')
    
    def warning(self, text: str) -> str:
        """Format warning text."""
        return self.colorize(text, 'YELLOW')
    
    def info(self, text: str) -> str:
        """Format info text."""
        return self.colorize(text, 'BLUE')
    
    def success(self, text: str) -> str:
        """Format success text."""
        return self.colorize(text, 'GREEN')
    
    def bold(self, text: str) -> str:
        """Format bold text."""
        return self.colorize(text, 'BOLD')
    
    def underline(self, text: str) -> str:
        """Format underlined text."""
        return self.colorize(text, 'UNDERLINE')


class VivadoErrorParser:
    """Parser for Vivado log files and error messages."""
    
    # Regex patterns for different types of Vivado errors
    ERROR_PATTERNS = {
        VivadoErrorType.SYNTAX_ERROR: [
            r"ERROR: \[Synth 8-(\d+)\] (.*?) \[(.*?):(\d+)\]",
            r"ERROR: \[HDL 9-(\d+)\] (.*?) \[(.*?):(\d+)\]",
            r"ERROR: \[Vivado 12-(\d+)\] (.*?) \[(.*?):(\d+)\]",
            r"ERROR: \[Coretcl 2-(\d+)\] (.*?) \[(.*?):(\d+)\]",
        ],
        VivadoErrorType.TIMING_ERROR: [
            r"ERROR: \[Timing 38-(\d+)\] (.*)",
            r"ERROR: \[Route 35-(\d+)\] (.*)",
            r"CRITICAL WARNING: \[Timing 38-(\d+)\] (.*)",
            r"ERROR: \[Vivado 12-4739\] (.*)",  # Timing not met
        ],
        VivadoErrorType.RESOURCE_ERROR: [
            r"ERROR: \[Place 30-(\d+)\] (.*)",
            r"ERROR: \[Opt 31-(\d+)\] (.*)",
            r"ERROR: \[Synth 8-6859\] (.*)",  # Resource over-utilization
            r"ERROR: \[Place 30-640\] (.*)",  # Placement failed
        ],
        VivadoErrorType.CONSTRAINT_ERROR: [
            r"ERROR: \[Vivado 12-(\d+)\] (.*constraint.*)",
            r"ERROR: \[Common 17-(\d+)\] (.*constraint.*)",
            r"WARNING: \[Vivado 12-(\d+)\] (.*constraint.*)",
            r"ERROR: \[Designutils 20-(\d+)\] (.*)",
        ],
        VivadoErrorType.IP_ERROR: [
            r"ERROR: \[IP_Flow 19-(\d+)\] (.*)",
            r"ERROR: \[Vivado 12-(\d+)\] (.*IP.*)",
            r"ERROR: \[BD 5-(\d+)\] (.*)",
            r"ERROR: \[Coretcl 2-(\d+)\] (.*IP.*)",
        ],
        VivadoErrorType.IMPLEMENTATION_ERROR: [
            r"ERROR: \[Route 35-(\d+)\] (.*)",
            r"ERROR: \[Place 30-(\d+)\] (.*)",
            r"ERROR: \[PhysOpt 32-(\d+)\] (.*)",
            r"ERROR: \[Opt 31-(\d+)\] (.*)",
        ],
        VivadoErrorType.BITSTREAM_ERROR: [
            r"ERROR: \[Bitstream 2-(\d+)\] (.*)",
            r"ERROR: \[Vivado 12-(\d+)\] (.*bitstream.*)",
            r"ERROR: \[DRC 23-(\d+)\] (.*)",
        ],
        VivadoErrorType.LICENSING_ERROR: [
            r"ERROR: \[Common 17-349\] (.*license.*)",
            r"ERROR: \[Vivado 12-(\d+)\] (.*license.*)",
            r"WARNING: \[Common 17-(\d+)\] (.*license.*)",
        ],
        VivadoErrorType.FILE_ERROR: [
            r"ERROR: \[Common 17-(\d+)\] (.*file.*)",
            r"ERROR: \[Vivado 12-(\d+)\] (.*file.*not found.*)",
            r"ERROR: \[Coretcl 2-(\d+)\] (.*file.*)",
        ],
    }
    
    # Warning patterns
    WARNING_PATTERNS = [
        r"WARNING: \[(\w+) (\d+-\d+)\] (.*)",
        r"CRITICAL WARNING: \[(\w+) (\d+-\d+)\] (.*)",
        r"INFO: \[(\w+) (\d+-\d+)\] (.*)",
    ]
    
    # Common error fixes
    ERROR_FIXES = {
        "Synth 8-6859": "Reduce resource usage or use a larger FPGA part",
        "Timing 38-282": "Add timing constraints or optimize critical paths",
        "Place 30-640": "Reduce logic utilization or use placement constraints",
        "Route 35-39": "Reduce routing congestion or use different placement",
        "Vivado 12-4739": "Timing constraints not met - review clock constraints",
        "Common 17-349": "Check Vivado license availability",
        "HDL 9-806": "Fix SystemVerilog/Verilog syntax errors",
        "Coretcl 2-1": "Check TCL script syntax",
    }
    
    def __init__(self):
        """Initialize the error parser."""
        self.errors: List[VivadoError] = []
        self.warnings: List[VivadoError] = []
        
    def parse_log_file(self, log_file: Union[str, Path]) -> Tuple[List[VivadoError], List[VivadoError]]:
        """Parse a Vivado log file for errors and warnings."""
        log_path = Path(log_file)
        if not log_path.exists():
            return [], []
        
        self.errors.clear()
        self.warnings.clear()
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                self._parse_content(content)
        except Exception as e:
            logging.error(f"Failed to parse log file {log_path}: {e}")
        
        return self.errors, self.warnings
    
    def parse_output(self, output: str) -> Tuple[List[VivadoError], List[VivadoError]]:
        """Parse Vivado output text for errors and warnings."""
        self.errors.clear()
        self.warnings.clear()
        self._parse_content(output)
        return self.errors, self.warnings
    
    def _parse_content(self, content: str) -> None:
        """Parse content for errors and warnings."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Check for errors
            error = self._parse_error_line(line, line_num)
            if error:
                if error.severity == ErrorSeverity.ERROR or error.severity == ErrorSeverity.CRITICAL:
                    self.errors.append(error)
                else:
                    self.warnings.append(error)
    
    def _parse_error_line(self, line: str, line_num: int) -> Optional[VivadoError]:
        """Parse a single line for error patterns."""
        # Check error patterns
        for error_type, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return self._create_error_from_match(match, error_type, line, line_num)
        
        # Check warning patterns
        for pattern in self.WARNING_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return self._create_warning_from_match(match, line, line_num)
        
        return None
    
    def _create_error_from_match(self, match, error_type: VivadoErrorType, line: str, line_num: int) -> VivadoError:
        """Create VivadoError from regex match."""
        groups = match.groups()
        
        # Determine severity
        severity = ErrorSeverity.ERROR
        if "CRITICAL WARNING" in line:
            severity = ErrorSeverity.CRITICAL
        elif "WARNING" in line:
            severity = ErrorSeverity.WARNING
        
        # Extract message and location
        message = groups[1] if len(groups) > 1 else groups[0]
        file_path = groups[2] if len(groups) > 2 else None
        line_number = int(groups[3]) if len(groups) > 3 and groups[3].isdigit() else None
        
        # Get suggested fix
        error_code = groups[0] if groups else ""
        suggested_fix = self.ERROR_FIXES.get(f"{error_type.value.title()} {error_code}", None)
        
        return VivadoError(
            error_type=error_type,
            severity=severity,
            message=message.strip(),
            file_path=file_path,
            line_number=line_number,
            suggested_fix=suggested_fix,
            raw_message=line
        )
    
    def _create_warning_from_match(self, match, line: str, line_num: int) -> VivadoError:
        """Create VivadoError from warning match."""
        groups = match.groups()
        
        severity = ErrorSeverity.WARNING
        if "CRITICAL WARNING" in line:
            severity = ErrorSeverity.CRITICAL
        elif "INFO" in line:
            severity = ErrorSeverity.INFO
        
        message = groups[2] if len(groups) > 2 else line
        
        return VivadoError(
            error_type=VivadoErrorType.UNKNOWN_ERROR,
            severity=severity,
            message=message.strip(),
            raw_message=line
        )


class VivadoErrorReporter:
    """Main error reporter class for Vivado builds."""
    
    def __init__(self, use_colors: Optional[bool] = None, output_file: Optional[Path] = None):
        """Initialize the error reporter."""
        self.formatter = ColorFormatter(use_colors)
        self.parser = VivadoErrorParser()
        self.output_file = output_file
        self.logger = logging.getLogger(__name__)
        
    def monitor_vivado_process(self, process: subprocess.Popen, log_file: Optional[Path] = None) -> Tuple[int, List[VivadoError], List[VivadoError]]:
        """Monitor a running Vivado process and report errors in real-time."""
        errors = []
        warnings = []
        
        try:
            # Read output line by line
            if process.stdout:
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        line = output.strip()
                        print(line)  # Echo the output
                        
                        # Parse for errors
                        line_errors, line_warnings = self.parser.parse_output(line)
                        errors.extend(line_errors)
                        warnings.extend(line_warnings)
                        
                        # Highlight errors in real-time
                        for error in line_errors:
                            self._print_error_highlight(error)
            
            # Get return code
            return_code = process.poll()
            if return_code is None:
                return_code = 0
            
            # Parse log file if provided
            if log_file and log_file.exists():
                log_errors, log_warnings = self.parser.parse_log_file(log_file)
                errors.extend(log_errors)
                warnings.extend(log_warnings)
            
            return return_code, errors, warnings
            
        except Exception as e:
            self.logger.error(f"Error monitoring Vivado process: {e}")
            return -1, errors, warnings
    
    def generate_error_report(self, errors: List[VivadoError], warnings: List[VivadoError], 
                            build_stage: str = "Build", output_file: Optional[Path] = None) -> str:
        """Generate a comprehensive error report."""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append(f"VIVADO {build_stage.upper()} ERROR REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary
        total_errors = len(errors)
        total_warnings = len(warnings)
        
        if total_errors == 0 and total_warnings == 0:
            report_lines.append(self.formatter.success("✅ No errors or warnings found!"))
            report_lines.append("")
        else:
            report_lines.append("SUMMARY:")
            if total_errors > 0:
                report_lines.append(f"  {self.formatter.error('❌ Errors:')} {total_errors}")
            if total_warnings > 0:
                report_lines.append(f"  {self.formatter.warning('⚠️  Warnings:')} {total_warnings}")
            report_lines.append("")
        
        # Error details
        if errors:
            report_lines.append(self.formatter.bold("ERRORS:"))
            report_lines.append("-" * 40)
            for i, error in enumerate(errors, 1):
                report_lines.extend(self._format_error_detail(error, i))
                report_lines.append("")
        
        # Warning details
        if warnings:
            report_lines.append(self.formatter.bold("WARNINGS:"))
            report_lines.append("-" * 40)
            for i, warning in enumerate(warnings, 1):
                report_lines.extend(self._format_error_detail(warning, i))
                report_lines.append("")
        
        # Error type summary
        if errors or warnings:
            report_lines.extend(self._generate_error_type_summary(errors, warnings))
        
        # Recommendations
        if errors:
            report_lines.extend(self._generate_recommendations(errors))
        
        report_lines.append("=" * 80)
        
        report_content = "\n".join(report_lines)
        
        # Write to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    # Write plain text version (no ANSI codes)
                    plain_content = self._strip_ansi_codes(report_content)
                    f.write(plain_content)
                self.logger.info(f"Error report written to: {output_file}")
            except Exception as e:
                self.logger.error(f"Failed to write error report: {e}")
        
        return report_content
    
    def _print_error_highlight(self, error: VivadoError) -> None:
        """Print highlighted error in real-time."""
        if error.severity == ErrorSeverity.ERROR or error.severity == ErrorSeverity.CRITICAL:
            print(self.formatter.error(f"\n🚨 {error.severity.value.upper()}: {error.message}"))
            if error.location_str != "Unknown location":
                print(self.formatter.error(f"   Location: {error.location_str}"))
            if error.suggested_fix:
                print(self.formatter.info(f"   Suggestion: {error.suggested_fix}"))
            print()
    
    def _format_error_detail(self, error: VivadoError, index: int) -> List[str]:
        """Format detailed error information."""
        lines = []
        
        # Error header
        severity_color = 'RED' if error.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL] else 'YELLOW'
        header = f"{index}. {error.severity_icon} {error.severity.value.upper()}: {error.message}"
        lines.append(self.formatter.colorize(header, severity_color))
        
        # Location
        if error.location_str != "Unknown location":
            lines.append(f"   📍 Location: {error.location_str}")
        
        # Error type
        lines.append(f"   🏷️  Type: {error.error_type.value.replace('_', ' ').title()}")
        
        # Suggested fix
        if error.suggested_fix:
            lines.append(f"   💡 Suggestion: {self.formatter.colorize(error.suggested_fix, 'CYAN')}")
        
        # Raw message (if different from parsed message)
        if error.raw_message and error.raw_message.strip() != error.message:
            lines.append(f"   📝 Raw: {error.raw_message}")
        
        return lines
    
    def _generate_error_type_summary(self, errors: List[VivadoError], warnings: List[VivadoError]) -> List[str]:
        """Generate summary by error type."""
        lines = []
        lines.append(self.formatter.bold("ERROR TYPE BREAKDOWN:"))
        lines.append("-" * 40)
        
        # Count by type
        type_counts = {}
        for error in errors + warnings:
            error_type = error.error_type
            if error_type not in type_counts:
                type_counts[error_type] = {'errors': 0, 'warnings': 0}
            
            if error.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
                type_counts[error_type]['errors'] += 1
            else:
                type_counts[error_type]['warnings'] += 1
        
        for error_type, counts in sorted(type_counts.items(), key=lambda x: x[0].value):
            type_name = error_type.value.replace('_', ' ').title()
            error_count = counts['errors']
            warning_count = counts['warnings']
            
            line = f"  {type_name}:"
            if error_count > 0:
                line += f" {self.formatter.error(f'{error_count} errors')}"
            if warning_count > 0:
                if error_count > 0:
                    line += ","
                line += f" {self.formatter.warning(f'{warning_count} warnings')}"
            
            lines.append(line)
        
        lines.append("")
        return lines
    
    def _generate_recommendations(self, errors: List[VivadoError]) -> List[str]:
        """Generate recommendations based on error types."""
        lines = []
        lines.append(self.formatter.bold("RECOMMENDATIONS:"))
        lines.append("-" * 40)
        
        # Collect unique error types
        error_types = set(error.error_type for error in errors)
        
        recommendations = {
            VivadoErrorType.SYNTAX_ERROR: [
                "Review SystemVerilog/Verilog syntax in source files",
                "Check for missing semicolons, parentheses, or keywords",
                "Verify module declarations and port lists"
            ],
            VivadoErrorType.TIMING_ERROR: [
                "Add or refine timing constraints (XDC file)",
                "Review critical path delays",
                "Consider pipeline optimization or clock domain crossing"
            ],
            VivadoErrorType.RESOURCE_ERROR: [
                "Reduce logic utilization or use a larger FPGA",
                "Optimize resource usage with synthesis directives",
                "Consider using block RAM instead of distributed RAM"
            ],
            VivadoErrorType.CONSTRAINT_ERROR: [
                "Review XDC constraint file syntax",
                "Verify pin assignments match board layout",
                "Check clock constraint definitions"
            ],
            VivadoErrorType.IP_ERROR: [
                "Regenerate IP cores with current Vivado version",
                "Check IP core configuration parameters",
                "Verify IP core licensing"
            ],
            VivadoErrorType.LICENSING_ERROR: [
                "Check Vivado license server connectivity",
                "Verify license features are available",
                "Contact system administrator for license issues"
            ]
        }
        
        for error_type in error_types:
            if error_type in recommendations:
                type_name = error_type.value.replace('_', ' ').title()
                lines.append(f"For {self.formatter.bold(type_name)} issues:")
                for rec in recommendations[error_type]:
                    lines.append(f"  • {rec}")
                lines.append("")
        
        return lines
    
    def _strip_ansi_codes(self, text: str) -> str:
        """Remove ANSI color codes from text."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def print_summary(self, errors: List[VivadoError], warnings: List[VivadoError]) -> None:
        """Print a quick summary to console."""
        total_errors = len(errors)
        total_warnings = len(warnings)
        
        print("\n" + "=" * 60)
        print(self.formatter.bold("VIVADO BUILD SUMMARY"))
        print("=" * 60)
        
        if total_errors == 0 and total_warnings == 0:
            print(self.formatter.success("✅ Build completed successfully!"))
        else:
            if total_errors > 0:
                print(self.formatter.error(f"❌ {total_errors} error(s) found"))
            if total_warnings > 0:
                print(self.formatter.warning(f"⚠️  {total_warnings} warning(s) found"))
            
            if total_errors > 0:
                print(self.formatter.error("\n🚨 Build FAILED due to errors"))
            else:
                print(self.formatter.warning("\n⚠️  Build completed with warnings"))
        
        print("=" * 60)


def create_enhanced_vivado_runner(use_colors: bool = True, log_file: Optional[Path] = None) -> VivadoErrorReporter:
    """Create a Vivado error reporter instance."""
    return VivadoErrorReporter(use_colors=use_colors, output_file=log_file)


# Example usage functions
def run_vivado_with_error_reporting(tcl_script: Path, output_dir: Path, 
                                  vivado_executable: Optional[str] = None) -> Tuple[int, str]:
    """Run Vivado with enhanced error reporting."""
    from .vivado_utils import get_vivado_executable
    
    if not vivado_executable:
        vivado_executable = get_vivado_executable()
        if not vivado_executable:
            raise FileNotFoundError("Vivado executable not found")
    
    # Setup error reporter
    log_file = output_dir / "vivado_build.log"
    reporter = VivadoErrorReporter(use_colors=True, output_file=output_dir / "error_report.txt")
    
    # Run Vivado
    cmd = [vivado_executable, "-mode", "batch", "-source", str(tcl_script), "-log", str(log_file)]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=output_dir
        )
        
        # Monitor process with error reporting
        return_code, errors, warnings = reporter.monitor_vivado_process(process, log_file)
        
        # Generate comprehensive report
        report = reporter.generate_error_report(errors, warnings, "Build", output_dir / "error_report.txt")
        
        # Print summary
        reporter.print_summary(errors, warnings)
        
        return return_code, report
        
    except Exception as e:
        error_msg = f"Failed to run Vivado: {e}"
        logging.error(error_msg)
        return -1, error_msg


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Vivado Error Reporter")
    parser.add_argument("log_file", help="Vivado log file to analyze")
    parser.add_argument("--no-colors", action="store_true", help="Disable colored output")
    parser.add_argument("--output", "-o", help="Output report file")
    
    args = parser.parse_args()
    
    reporter = VivadoErrorReporter(use_colors=not args.no_colors)
    errors, warnings = reporter.parser.parse_log_file(args.log_file)
    
    report = reporter.generate_error_report(
        errors, warnings, "Analysis", 
        Path(args.output) if args.output else None
    )
    
    print(report)
    reporter.print_summary(errors, warnings)