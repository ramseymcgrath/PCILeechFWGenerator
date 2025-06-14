"""
Pytest configuration and fixtures for refactored build system tests.

This module provides shared fixtures and configuration for testing
the refactored build system components.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_donor_info():
    """Mock donor device information for testing."""
    return {
        "vendor_id": "0x8086",
        "device_id": "0x1533",
        "subvendor_id": "0x8086",
        "subsystem_id": "0x0000",
        "revision_id": "0x03",
        "bar_size": "0x20000",
        "mpc": "0x02",
        "mpr": "0x02",
    }


@pytest.fixture
def mock_register_data():
    """Mock register data for testing."""
    return [
        {
            "offset": 0x400,
            "name": "reg_ctrl",
            "value": "0x12345678",
            "rw": "rw",
            "context": {
                "timing_constraints": [{"delay_us": 10, "context": "register_access"}],
                "access_pattern": "write_then_read",
                "sequences": [
                    {"function": "init", "position": 0, "operation": "write"},
                    {"function": "init", "position": 1, "operation": "read"},
                ],
            },
        },
        {
            "offset": 0x404,
            "name": "reg_status",
            "value": "0x87654321",
            "rw": "r",
            "context": {
                "timing_constraints": [{"delay_us": 5, "context": "status_read"}],
                "access_pattern": "read_only",
            },
        },
    ]


@pytest.fixture
def mock_behavior_profile():
    """Mock behavior profile data for testing."""
    return {
        "device_id": "0000:03:00.0",
        "capture_duration": 5.0,
        "total_accesses": 1500,
        "access_patterns": {
            "0x400": {
                "read_count": 750,
                "write_count": 750,
                "avg_interval_us": 100,
                "timing_variance": 0.15,
            },
            "0x404": {
                "read_count": 1500,
                "write_count": 0,
                "avg_interval_us": 50,
                "timing_variance": 0.05,
            },
        },
        "behavioral_signatures": {
            "timing_regularity": 0.85,
            "access_locality": 0.92,
            "burst_patterns": ["init_sequence", "status_polling"],
        },
    }


@pytest.fixture
def performance_test_data():
    """Performance test configuration data."""
    return {
        "small_device": {
            "register_count": 10,
            "expected_build_time_ms": 100,
            "expected_memory_mb": 10,
        },
        "medium_device": {
            "register_count": 100,
            "expected_build_time_ms": 500,
            "expected_memory_mb": 50,
        },
        "large_device": {
            "register_count": 1000,
            "expected_build_time_ms": 2000,
            "expected_memory_mb": 100,
        },
    }


@pytest.fixture
def sample_tcl_templates():
    """Sample TCL templates for testing."""
    return {
        "project_setup.j2": """
# Project Setup for {{ board }}
create_project {{ project_name | default('pcileech_firmware') }} ./vivado_project -part {{ fpga_part }} -force
set_property target_language Verilog [current_project]
set_property default_lib xil_defaultlib [current_project]

# Device configuration
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
""",
        "ip_config.j2": """
# IP Configuration for {{ pcie_ip_type }}
# Vendor: {{ vendor_id | hex(4) }} Device: {{ device_id | hex(4) }}
# Max lanes: {{ max_lanes }}
# MSI-X support: {{ supports_msix }}

{% if pcie_ip_type == "axi_pcie" %}
# AXI PCIe IP Configuration
create_ip -name axi_pcie -vendor xilinx.com -library ip -module_name axi_pcie_0
{% elif pcie_ip_type == "pcie_7x" %}
# PCIe 7-series IP Configuration  
create_ip -name pcie_7x -vendor xilinx.com -library ip -module_name pcie_7x_0
{% elif pcie_ip_type == "pcie_ultrascale" %}
# PCIe UltraScale IP Configuration
create_ip -name pcie_ultrascale -vendor xilinx.com -library ip -module_name pcie_ultrascale_0
{% endif %}
""",
        "sources.j2": """
# Source Files
{% for file in source_files %}
add_files {{ file | tcl_escape }}
{% endfor %}

{% if source_files %}
puts "Added {{ source_files | length }} source files"
{% else %}
puts "No source files specified"
{% endif %}
""",
        "constraints.j2": """
# Constraint Files
{% for file in constraint_files %}
add_files -fileset constrs_1 {{ file | tcl_escape }}
{% endfor %}

{% if constraint_files %}
puts "Added {{ constraint_files | length }} constraint files"
{% else %}
puts "No constraint files specified"
{% endif %}
""",
    }


@pytest.fixture
def sample_fpga_configurations():
    """Sample FPGA configuration data for testing."""
    return {
        "xc7a35tcsg324-2": {
            "family": "artix7",
            "size": "35t",
            "package": "csg324",
            "speed_grade": "-2",
            "pcie_ip_type": "axi_pcie",
            "max_lanes": 4,
            "supports_msi": True,
            "supports_msix": False,
        },
        "xc7a75tfgg484-2": {
            "family": "artix7",
            "size": "75t",
            "package": "fgg484",
            "speed_grade": "-2",
            "pcie_ip_type": "pcie_7x",
            "max_lanes": 8,
            "supports_msi": True,
            "supports_msix": True,
        },
        "xczu3eg-sbva484-1-e": {
            "family": "zynq_ultrascale",
            "size": "zu3eg",
            "package": "sbva484",
            "speed_grade": "-1",
            "pcie_ip_type": "pcie_ultrascale",
            "max_lanes": 16,
            "supports_msi": True,
            "supports_msix": True,
        },
    }


@pytest.fixture
def mock_template_context():
    """Mock template context for testing."""
    return {
        "board": "pcileech_35t325_x4",
        "fpga_part": "xc7a35tcsg324-2",
        "project_name": "pcileech_firmware",
        "pcie_ip_type": "axi_pcie",
        "fpga_family": "artix7",
        "max_lanes": 4,
        "supports_msi": True,
        "supports_msix": False,
        "vendor_id": 0x1234,
        "device_id": 0x5678,
        "revision_id": 0x01,
        "vendor_id_hex": "1234",
        "device_id_hex": "5678",
        "revision_id_hex": "01",
        "synthesis_strategy": "Vivado Synthesis Defaults",
        "implementation_strategy": "Performance_Explore",
        "source_files": ["src/pcileech_tlps128_bar_controller.sv"],
        "constraint_files": ["constraints/timing.xdc"],
    }


def generate_test_registers(count):
    """Generate test register data for performance testing."""
    registers = []

    for i in range(count):
        reg = {
            "offset": 0x400 + (i * 4),
            "name": f"test_reg_{i}",
            "value": f"0x{i:08x}",
            "rw": "rw" if i % 2 == 0 else "r",
            "context": {
                "timing_constraints": [
                    {"delay_us": 10 + (i % 50), "context": f"reg_{i}_access"}
                ],
                "access_pattern": "write_then_read" if i % 3 == 0 else "read_only",
                "sequences": (
                    [
                        {"function": f"func_{i}", "position": 0, "operation": "write"},
                        {"function": f"func_{i}", "position": 1, "operation": "read"},
                    ]
                    if i % 3 == 0
                    else []
                ),
            },
        }
        registers.append(reg)

    return registers


@pytest.fixture
def mock_jinja2_environment():
    """Mock Jinja2 environment for testing."""
    mock_env = Mock()
    mock_template = Mock()
    mock_template.render.return_value = "rendered template content"
    mock_env.get_template.return_value = mock_template
    mock_env.from_string.return_value = mock_template
    return mock_env


@pytest.fixture
def sample_board_configurations():
    """Sample board configuration data."""
    return {
        "pcileech_35t325_x4": {
            "fpga_part": "xc7a35tcsg324-2",
            "pcie_lanes": 4,
            "description": "PCILeech 35T x4 board",
            "constraints_file": "pcileech_35t_x4.xdc",
        },
        "pcileech_75t484_x1": {
            "fpga_part": "xc7a75tfgg484-2",
            "pcie_lanes": 1,
            "description": "PCILeech 75T x1 board",
            "constraints_file": "pcileech_75t_x1.xdc",
        },
        "pcileech_100t484_x1": {
            "fpga_part": "xczu3eg-sbva484-1-e",
            "pcie_lanes": 1,
            "description": "PCILeech 100T x1 board",
            "constraints_file": "pcileech_100t_x1.xdc",
        },
    }


@pytest.fixture
def mock_vivado_project_structure(temp_dir):
    """Create a mock Vivado project structure for testing."""
    project_dir = temp_dir / "vivado_project"
    project_dir.mkdir()

    # Create project file
    (project_dir / "pcileech_firmware.xpr").write_text(
        """
<?xml version="1.0" encoding="UTF-8"?>
<Project Version="7" Minor="44" Path="pcileech_firmware.xpr">
  <DefaultLaunch Dir="$PRUNDIR"/>
  <Configuration>
    <Option Name="Id" Val="test_project"/>
    <Option Name="Part" Val="xc7a35tcsg324-2"/>
    <Option Name="CompiledLibDir" Val="$PCACHEDIR/compile_simlib"/>
    <Option Name="CompiledLibDirXSim" Val=""/>
    <Option Name="CompiledLibDirModelSim" Val="$PCACHEDIR/compile_simlib/modelsim"/>
    <Option Name="CompiledLibDirQuesta" Val="$PCACHEDIR/compile_simlib/questa"/>
    <Option Name="CompiledLibDirIES" Val="$PCACHEDIR/compile_simlib/ies"/>
    <Option Name="CompiledLibDirXcelium" Val="$PCACHEDIR/compile_simlib/xcelium"/>
    <Option Name="CompiledLibDirVCS" Val="$PCACHEDIR/compile_simlib/vcs"/>
    <Option Name="CompiledLibDirRiviera" Val="$PCACHEDIR/compile_simlib/riviera"/>
    <Option Name="CompiledLibDirActivehdl" Val="$PCACHEDIR/compile_simlib/activehdl"/>
  </Configuration>
</Project>
"""
    )

    # Create sources directory
    sources_dir = project_dir / "sources_1" / "new"
    sources_dir.mkdir(parents=True)

    # Create constraints directory
    constrs_dir = project_dir / "constrs_1" / "new"
    constrs_dir.mkdir(parents=True)

    return project_dir


@pytest.fixture
def mock_build_environment():
    """Mock build environment with all necessary components."""
    return {
        "vivado_available": True,
        "jinja2_available": True,
        "template_dir": "src/templates",
        "output_dir": "output",
        "temp_dir": "/tmp/pcileech_build",
        "log_level": "INFO",
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line(
        "markers", "template: marks tests related to template rendering"
    )
    config.addinivalue_line("markers", "helpers: marks tests related to build helpers")
    config.addinivalue_line(
        "markers", "tcl_builder: marks tests related to TCL builder"
    )
    config.addinivalue_line("markers", "constants: marks tests related to constants")
    config.addinivalue_line("markers", "performance: marks performance tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "test_template_renderer" in item.nodeid:
            item.add_marker(pytest.mark.template)
        elif "test_build_helpers" in item.nodeid:
            item.add_marker(pytest.mark.helpers)
        elif "test_tcl_builder" in item.nodeid:
            item.add_marker(pytest.mark.tcl_builder)
        elif "test_constants" in item.nodeid:
            item.add_marker(pytest.mark.constants)

        # Add markers based on test names
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        elif "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        elif "large" in item.name.lower() or "memory" in item.name.lower():
            item.add_marker(pytest.mark.slow)


# Custom assertions for testing
def assert_tcl_content_valid(tcl_content):
    """Assert that TCL content is valid."""
    assert isinstance(tcl_content, str)
    assert len(tcl_content.strip()) > 0

    # Check for common TCL syntax
    tcl_keywords = ["set", "puts", "create_project", "add_files", "launch_runs"]
    has_tcl_keyword = any(keyword in tcl_content for keyword in tcl_keywords)
    assert has_tcl_keyword, "TCL content should contain at least one TCL keyword"


def assert_systemverilog_content_valid(sv_content):
    """Assert that SystemVerilog content is valid."""
    assert isinstance(sv_content, str)
    assert len(sv_content.strip()) > 0

    # Check for SystemVerilog syntax
    sv_keywords = ["module", "endmodule", "reg", "wire", "always", "case"]
    has_sv_keyword = any(keyword in sv_content for keyword in sv_keywords)
    assert (
        has_sv_keyword
    ), "SystemVerilog content should contain at least one SV keyword"


def assert_fpga_part_valid(fpga_part):
    """Assert that FPGA part string is valid."""
    assert isinstance(fpga_part, str)
    assert len(fpga_part) > 0

    # Check for valid Xilinx part format
    valid_prefixes = ["xc7a", "xc7k", "xc7v", "xczu", "xck", "xcvu"]
    assert any(fpga_part.lower().startswith(prefix) for prefix in valid_prefixes)
    assert "-" in fpga_part, "FPGA part should include speed grade"


# Export utility functions for use in tests
__all__ = [
    "generate_test_registers",
    "assert_tcl_content_valid",
    "assert_systemverilog_content_valid",
    "assert_fpga_part_valid",
]
