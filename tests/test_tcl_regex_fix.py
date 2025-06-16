"""
Test for TCL regex pattern fix in synthesis template.

This test ensures that the regex pattern used in the synthesis template
for parsing Vivado utilization reports is valid TCL syntax.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest


def test_tcl_regex_pattern_validity():
    """Test that the TCL regex pattern in synthesis template is valid."""

    # Create a test TCL script with the fixed regex pattern
    tcl_test_script = """#!/usr/bin/env tclsh

proc parse_synth_field {field txt} {
    regexp [format {%s\\s+\\|\\s+(\\d+)} [string map {[ \\\\[ ] \\\\]} $field]] $txt -> val
    return $val
}

# Test data similar to Vivado utilization report
set test_data {
| CLB LUTs                     |  1234 |     0 |  20800 |  5.93 |
| CLB Registers                |  5678 |     0 |  41600 | 13.65 |
| Block RAM Tile               |    12 |     0 |     50 | 24.00 |
| DSPs                         |     8 |     0 |     90 |  8.89 |
}

# Test the function
set lut_count [parse_synth_field "CLB LUTs" $test_data]
set reg_count [parse_synth_field "CLB Registers" $test_data]
set bram_count [parse_synth_field "Block RAM Tile" $test_data]
set dsp_count [parse_synth_field "DSPs" $test_data]

if {$lut_count == "1234" && $reg_count == "5678" && $bram_count == "12" && $dsp_count == "8"} {
    puts "SUCCESS"
    exit 0
} else {
    puts "FAILED"
    exit 1
}
"""

    # Write the test script to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".tcl", delete=False) as f:
        f.write(tcl_test_script)
        temp_file = f.name

    try:
        # Run the TCL script
        result = subprocess.run(
            ["tclsh", temp_file], capture_output=True, text=True, timeout=10
        )

        # Check that the script executed successfully
        assert result.returncode == 0, f"TCL script failed with error: {result.stderr}"
        assert "SUCCESS" in result.stdout, f"TCL regex test failed: {result.stdout}"

    finally:
        # Clean up the temporary file
        Path(temp_file).unlink(missing_ok=True)


def test_synthesis_template_contains_fixed_regex():
    """Test that the synthesis template contains the fixed regex pattern."""

    template_path = Path("src/templates/tcl/synthesis.j2")
    assert template_path.exists(), "Synthesis template not found"

    content = template_path.read_text()

    # Check that the old problematic pattern is not present
    assert (
        "\\\\Q$field\\\\E" not in content
    ), "Old problematic regex pattern still present"

    # Check that the new fixed pattern is present
    assert "format {%s\\s+\\|\\s+(\\d+)}" in content, "Fixed regex pattern not found"
    assert (
        "string map {[ \\\\[ ] \\\\]}" in content
    ), "String mapping for brackets not found"


if __name__ == "__main__":
    test_tcl_regex_pattern_validity()
    test_synthesis_template_contains_fixed_regex()
    print("All TCL regex tests passed!")
