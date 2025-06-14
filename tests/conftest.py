"""
Pytest configuration and shared fixtures for PCILeech firmware generator tests.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_pci_device():
    """Mock PCIe device data for testing."""
    return {
        "bd": "0000:03:00.0",
        "ven": "8086",
        "dev": "1533",
        "class": "0200",
        "pretty": "0000:03:00.0 Ethernet controller [0200]: Intel Corporation I210 Gigabit Network Connection [8086:1533] (rev 03)",
    }


@pytest.fixture
def mock_donor_info():
    """Mock donor device information."""
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
    return [{"offset": 0x400,
             "name": "reg_ctrl",
             "value": "0x0",
             "rw": "rw",
             "context": {"function": "init_device",
                         "dependencies": ["reg_status"],
                         "timing": "early",
                         "access_pattern": "write_then_read",
                         "timing_constraints": [{"delay_us": 10,
                                                 "context": "register_access"}],
                         "sequences": [{"function": "init_device",
                                        "position": 0,
                                        "total_ops": 3,
                                        "operation": "write",
                                        }],
                         },
             },
            {"offset": 0x404,
             "name": "reg_status",
             "value": "0x1",
             "rw": "ro",
             "context": {"function": "check_status",
                         "dependencies": [],
                         "timing": "runtime",
                         "access_pattern": "read_heavy",
                         },
             },
            ]


@pytest.fixture
def mock_behavior_profile():
    """Mock behavior profile data."""
    from src.behavior_profiler import BehaviorProfile, RegisterAccess, TimingPattern

    return BehaviorProfile(
        device_bdf="0000:03:00.0",
        capture_duration=10.0,
        total_accesses=100,
        register_accesses=[
            RegisterAccess(
                timestamp=1234567890.0,
                register="reg_ctrl",
                offset=0x400,
                operation="write",
                value=0x1,
                duration_us=5.0,
            )
        ],
        timing_patterns=[
            TimingPattern(
                pattern_type="periodic",
                registers=["reg_ctrl"],
                avg_interval_us=100.0,
                std_deviation_us=5.0,
                frequency_hz=10000.0,
                confidence=0.95,
            )
        ],
        state_transitions={"init": ["ready", "error"]},
        power_states=["D0", "D3"],
        interrupt_patterns={"msi": {"count": 10, "avg_interval_ms": 50}},
    )


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls."""
    with (
        patch("subprocess.run") as mock_run,
        patch("subprocess.check_output") as mock_output,
    ):
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_output.return_value = ""
        yield mock_run, mock_output


@pytest.fixture
def mock_file_system():
    """Mock file system operations."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("pathlib.Path.exists") as mock_path_exists,
        patch("pathlib.Path.read_text") as mock_read_text,
        patch("pathlib.Path.write_text") as mock_write_text,
    ):
        mock_exists.return_value = True
        mock_path_exists.return_value = True
        mock_read_text.return_value = ""
        yield mock_exists, mock_path_exists, mock_read_text, mock_write_text


@pytest.fixture
def mock_kernel_module():
    """Mock kernel module operations."""
    with patch("subprocess.run") as mock_run:
        # Mock successful module compilation and loading
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        yield mock_run


@pytest.fixture
def mock_usb_devices():
    """Mock USB device listing."""
    return [
        ("1d50:6130", "LambdaConcept Screamer"),
        ("0403:6010", "FTDI FT2232C/D/H Dual UART/FIFO IC"),
        ("04b4:8613", "Cypress CY7C68013 EZ-USB FX2 USB 2.0 Development Kit"),
    ]


@pytest.fixture
def sample_systemverilog():
    """Sample SystemVerilog content for testing."""
    return """
module pcileech_tlps128_bar_controller
(
 input logic clk, reset_n,
 input logic [31:0] bar_addr, bar_wr_data,
 input logic bar_wr_en, bar_rd_en,
 output logic [31:0] bar_rd_data,
 output logic msi_request,  input logic msi_ack,
 input logic cfg_interrupt_msi_enable,
 output logic cfg_interrupt, input logic cfg_interrupt_ready
);

    logic [31:0] reg_ctrl_reg = 32'h00000000;
    logic [31:0] reg_status_reg = 32'h00000001;

    always_comb begin
        unique case(bar_addr)
            32'h00000400: bar_rd_data = reg_ctrl_reg;
            32'h00000404: bar_rd_data = reg_status_reg;
            default: bar_rd_data = 32'h0;
        endcase
    end

endmodule
"""


@pytest.fixture
def mock_vivado_environment():
    """Mock Vivado environment for FPGA builds."""
    with patch.dict(os.environ, {"VIVADO_PATH": "/opt/Xilinx/Vivado/2023.1"}):
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/opt/Xilinx/Vivado/2023.1/bin/vivado"
            yield


@pytest.fixture
def mock_vfio_environment():
    """Mock VFIO environment for device binding."""
    with patch("os.path.exists") as mock_exists:

        def exists_side_effect(path):
            if "vfio" in path:
                return True
            if "sys/bus/pci" in path:
                return True
            return False

        mock_exists.side_effect = exists_side_effect
        yield mock_exists


@pytest.fixture
def performance_test_data():
    """Performance test data for benchmarking."""
    return {
        "small_device": {
            "register_count": 10,
            "expected_build_time_ms": 1000,
            "expected_memory_mb": 50,
        },
        "medium_device": {
            "register_count": 100,
            "expected_build_time_ms": 5000,
            "expected_memory_mb": 100,
        },
        "large_device": {
            "register_count": 1000,
            "expected_build_time_ms": 30000,
            "expected_memory_mb": 200,
        },
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables and state before each test."""
    # Store original environment
    original_env = os.environ.copy()

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_container_runtime():
    """Mock container runtime (Podman) operations."""
    with patch("shutil.which") as mock_which, patch("subprocess.run") as mock_run:
        mock_which.return_value = "/usr/bin/podman"
        mock_run.return_value = Mock(
            returncode=0, stdout="Build successful", stderr="")
        yield mock_run


# Test data generators
def generate_test_registers(count: int) -> List[Dict[str, Any]]:
    """Generate test register data."""
    registers = []
    for i in range(count):
        registers.append(
            {
                "offset": 0x400 + (i * 4),
                "name": f"reg_{i:03d}",
                "value": f"0x{i:08x}",
                "rw": "rw" if i % 2 == 0 else "ro",
                "context": {
                    "function": f"function_{i}",
                    "dependencies": [f"reg_{j:03d}" for j in range(max(0, i - 2), i)],
                    "timing": ["early", "runtime", "late"][i % 3],
                    "access_pattern": ["read_heavy", "write_heavy", "balanced"][i % 3],
                },
            }
        )
    return registers


def generate_test_pci_devices(count: int) -> List[Dict[str, str]]:
    """Generate test PCIe device data."""
    devices = []
    for i in range(count):
        devices.append(
            {
                "bd": f"0000:0{
                    i:01x}:00.0", "ven": f"80{
                    i:02x}", "dev": f"15{
                    i:02x}", "class": "0200", "pretty": f"0000:0{
                        i:01x}:00.0 Test Device {i} [0200]: Test Vendor [80{
                            i:02x}:15{
                                i:02x}]", })
    return devices
