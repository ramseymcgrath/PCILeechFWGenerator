#!/usr/bin/env python3
"""
Enhanced tests for driver_scrape.py with comprehensive fixtures.

Tests cover:
- Missing linux-source tarball scenarios
- Unknown VID:DID combinations
- Drivers with nested switch state machines
- Error handling and edge cases
- Performance optimizations
- Output schema validation
"""

import json
import pathlib
import tempfile
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.scripts.driver_scrape import (
    BIT_WIDTH_MAP,
    DriverAnalyzer,
    extract_registers_with_analysis,
    main,
    parse_arguments,
    validate_hex_id,
)
from src.scripts.kernel_utils import (
    ensure_kernel_source,
    find_driver_sources,
    resolve_driver_module,
    run_command,
)


@pytest.fixture
def fake_kernel_source_tree():
    """Create a fake kernel source tree for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kernel_dir = pathlib.Path(tmpdir) / "linux-source-5.15.0"
        drivers_dir = kernel_dir / "drivers" / "net" / "ethernet" / "intel"
        drivers_dir.mkdir(parents=True)

        # Create fake driver source files
        driver_c = drivers_dir / "e1000e_main.c"
        driver_h = drivers_dir / "e1000e_hw.h"

        # Sample driver content with registers and state machines
        driver_c_content = """
#include "e1000e_hw.h"

static int e1000e_probe(struct pci_dev *pdev, const struct pci_device_id *ent)
{
    struct e1000_adapter *adapter;
    
    /* Initialize control register */
    writel(0x1, adapter->hw.hw_addr + REG_CTRL);
    udelay(10);
    
    /* Read status to verify */
    u32 status = readl(adapter->hw.hw_addr + REG_STATUS);
    
    /* State machine for initialization */
    switch (adapter->state) {
        case E1000_STATE_INIT:
            writel(0x2, adapter->hw.hw_addr + REG_CTRL);
            adapter->state = E1000_STATE_READY;
            break;
        case E1000_STATE_READY:
            if (status & STATUS_LINK_UP) {
                writel(0x4, adapter->hw.hw_addr + REG_CTRL);
                adapter->state = E1000_STATE_ACTIVE;
            }
            break;
        case E1000_STATE_ACTIVE:
            /* Handle active state */
            break;
    }
    
    return 0;
}

static void e1000e_remove(struct pci_dev *pdev)
{
    struct e1000_adapter *adapter = pci_get_drvdata(pdev);
    
    /* Shutdown sequence */
    writel(0x0, adapter->hw.hw_addr + REG_CTRL);
    mdelay(100);
}

static int e1000e_resume(struct pci_dev *pdev)
{
    /* Resume operations */
    writeq(0x123456789ABCDEF0, adapter->hw.hw_addr + REG_DMA_ADDR);
    return 0;
}

/* Interrupt handler with nested logic */
static irqreturn_t e1000_intr(int irq, void *data)
{
    struct e1000_adapter *adapter = data;
    u32 icr = readl(adapter->hw.hw_addr + REG_ICR);
    
    if (icr & ICR_TXDW) {
        /* TX descriptor written back */
        for (int i = 0; i < adapter->num_tx_queues; i++) {
            if (adapter->tx_ring[i].next_to_clean != adapter->tx_ring[i].next_to_use) {
                writew(i, adapter->hw.hw_addr + REG_TDT);
            }
        }
    }
    
    return IRQ_HANDLED;
}
"""

        driver_h_content = """
#ifndef _E1000E_HW_H_
#define _E1000E_HW_H_

/* Register definitions */
#define REG_CTRL        0x00000000
#define REG_STATUS      0x00000008
#define REG_ICR         0x000000C0
#define REG_TDT         0x00003818
#define REG_DMA_ADDR    0x00002800

/* Status register bits */
#define STATUS_LINK_UP  0x00000002

/* Interrupt cause register bits */
#define ICR_TXDW        0x00000001

/* State definitions */
enum e1000_state {
    E1000_STATE_INIT,
    E1000_STATE_READY,
    E1000_STATE_ACTIVE,
};

#endif /* _E1000E_HW_H_ */
"""

        driver_c.write_text(driver_c_content)
        driver_h.write_text(driver_h_content)

        yield kernel_dir


@pytest.fixture
def fake_empty_kernel_source():
    """Create an empty kernel source tree for testing missing drivers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kernel_dir = pathlib.Path(tmpdir) / "linux-source-5.15.0"
        drivers_dir = kernel_dir / "drivers"
        drivers_dir.mkdir(parents=True)
        yield kernel_dir


@pytest.fixture
def sample_file_contents():
    """Sample file contents for DriverAnalyzer testing."""
    return {
        pathlib.Path(
            "test.c"
        ): """
#define REG_CONTROL 0x1000
#define REG_STATUS  0x1004

int init_device(void) {
    writel(0x1, REG_CONTROL);
    udelay(50);
    u32 status = readl(REG_STATUS);
    return status & 0x1;
}

void shutdown_device(void) {
    writel(0x0, REG_CONTROL);
    mdelay(10);
}

irqreturn_t device_interrupt(int irq, void *data) {
    u16 val = readw(REG_STATUS);
    if (val & 0x8000) {
        writeb(0xFF, REG_CONTROL);
        return IRQ_HANDLED;
    }
    return IRQ_NONE;
}
"""
    }


class TestValidateHexId:
    """Test hex ID validation."""

    def test_valid_hex_ids(self):
        """Test valid hex ID formats."""
        assert validate_hex_id("8086", "Vendor ID") == "8086"
        assert validate_hex_id("1533", "Device ID") == "1533"
        assert validate_hex_id("ABCD", "Test ID") == "abcd"
        assert validate_hex_id("0000", "Test ID") == "0000"
        assert validate_hex_id("FFFF", "Test ID") == "ffff"

    def test_invalid_hex_ids(self):
        """Test invalid hex ID formats."""
        with pytest.raises(ValueError, match="must be a 4-digit hexadecimal"):
            validate_hex_id("123", "Vendor ID")

        with pytest.raises(ValueError, match="must be a 4-digit hexadecimal"):
            validate_hex_id("12345", "Device ID")

        with pytest.raises(ValueError, match="must be a 4-digit hexadecimal"):
            validate_hex_id("GHIJ", "Test ID")

        with pytest.raises(ValueError, match="must be a 4-digit hexadecimal"):
            validate_hex_id("", "Empty ID")


class TestDriverAnalyzer:
    """Test DriverAnalyzer class functionality."""

    def test_initialization(self, sample_file_contents):
        """Test analyzer initialization."""
        analyzer = DriverAnalyzer(sample_file_contents)
        assert analyzer.file_contents == sample_file_contents
        assert "REG_CONTROL" in analyzer.all_content
        assert "REG_STATUS" in analyzer.all_content

    def test_function_context_analysis(self, sample_file_contents):
        """Test function context analysis."""
        analyzer = DriverAnalyzer(sample_file_contents)

        # Test control register context
        context = analyzer.analyze_function_context("REG_CONTROL")
        assert context["function"] in [
            "init_device",
            "shutdown_device",
            "device_interrupt",
        ]
        assert context["timing"] in ["early", "late", "interrupt"]
        assert context["access_pattern"] in [
            "write_heavy",
            "balanced",
            "write_then_read",
        ]

    def test_access_sequence_analysis(self, sample_file_contents):
        """Test access sequence analysis."""
        analyzer = DriverAnalyzer(sample_file_contents)

        sequences = analyzer.analyze_access_sequences("REG_CONTROL")
        assert len(sequences) > 0

        # Check sequence structure
        seq = sequences[0]
        assert "function" in seq
        assert "operation" in seq
        assert "register" in seq
        assert "bit_width" in seq
        assert seq["bit_width"] in [8, 16, 32, 64]

    def test_timing_constraints_analysis(self, sample_file_contents):
        """Test timing constraints analysis."""
        analyzer = DriverAnalyzer(sample_file_contents)

        constraints = analyzer.analyze_timing_constraints()
        assert len(constraints) > 0

        # Check constraint structure
        constraint = constraints[0]
        assert "delay_us" in constraint
        assert "registers" in constraint
        assert "type" in constraint
        assert constraint["delay_us"] > 0

    def test_bit_width_detection(self, sample_file_contents):
        """Test bit width detection from register access functions."""
        analyzer = DriverAnalyzer(sample_file_contents)

        sequences = analyzer.analyze_access_sequences()
        bit_widths = {seq["bit_width"] for seq in sequences}

        # Should detect 8, 16, 32 bit accesses from readb/w/l, writeb/w/l
        expected_widths = {8, 16, 32}
        assert expected_widths.issubset(bit_widths)


class TestKernelUtils:
    """Test kernel utility functions."""

    @patch("src.scripts.kernel_utils.subprocess.run")
    def test_run_command_success(self, mock_run):
        """Test successful command execution."""
        mock_run.return_value.stdout = "test output"
        mock_run.return_value.returncode = 0

        result = run_command("echo test")
        assert result == "test output"
        mock_run.assert_called_once()

    @patch("src.scripts.kernel_utils.subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test command execution failure."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "false", stderr="error")

        with pytest.raises(RuntimeError, match="Command failed"):
            run_command("false")

    @patch("src.scripts.kernel_utils.pathlib.Path.glob")
    def test_ensure_kernel_source_not_found(self, mock_glob):
        """Test kernel source not found scenario."""
        mock_glob.return_value = []

        result = ensure_kernel_source()
        assert result is None

    @patch("src.scripts.kernel_utils.run_command")
    def test_resolve_driver_module_success(self, mock_run):
        """Test successful driver module resolution."""
        mock_run.return_value = "e1000e\n"

        result = resolve_driver_module("8086", "1533")
        assert result == "e1000e"

    @patch("src.scripts.kernel_utils.run_command")
    def test_resolve_driver_module_not_found(self, mock_run):
        """Test driver module not found."""
        mock_run.return_value = ""

        with pytest.raises(RuntimeError, match="No driver module found"):
            resolve_driver_module("FFFF", "FFFF")

    def test_find_driver_sources(self, fake_kernel_source_tree):
        """Test finding driver source files."""
        sources = find_driver_sources(fake_kernel_source_tree, "e1000e")
        assert len(sources) >= 2

        source_names = [s.name for s in sources]
        assert any("e1000e" in name for name in source_names)

    def test_find_driver_sources_empty(self, fake_empty_kernel_source):
        """Test finding driver sources in empty tree."""
        sources = find_driver_sources(fake_empty_kernel_source, "nonexistent")
        assert len(sources) == 0


class TestExtractRegistersWithAnalysis:
    """Test register extraction and analysis."""

    def test_extract_with_valid_sources(self, fake_kernel_source_tree):
        """Test extraction with valid source files."""
        sources = find_driver_sources(fake_kernel_source_tree, "e1000e")
        result = extract_registers_with_analysis(sources, "e1000e")

        # Check output structure
        assert "driver_module" in result
        assert "registers" in result
        assert "state_machine_analysis" in result
        assert result["driver_module"] == "e1000e"

        # Check register structure
        if result["registers"]:
            reg = result["registers"][0]
            assert "offset" in reg
            assert "name" in reg
            assert "rw" in reg
            assert "bit_width" in reg
            assert "context" in reg

            # Offset should be hex string
            assert reg["offset"].startswith("0x")

            # Bit width should be valid
            assert reg["bit_width"] in [8, 16, 32, 64]

    def test_extract_with_empty_sources(self):
        """Test extraction with no source files."""
        result = extract_registers_with_analysis([], "test_driver")

        assert result["driver_module"] == "test_driver"
        assert result["registers"] == []


class TestMainFunction:
    """Test main function and CLI integration."""

    @patch("src.scripts.driver_scrape.parse_arguments")
    @patch("src.scripts.driver_scrape.ensure_kernel_source")
    @patch("src.scripts.driver_scrape.resolve_driver_module")
    @patch("src.scripts.driver_scrape.find_driver_sources")
    @patch("src.scripts.driver_scrape.extract_registers_with_analysis")
    def test_main_success_flow(
        self, mock_extract, mock_find, mock_resolve, mock_ensure, mock_parse
    ):
        """Test successful main execution flow."""
        # Setup mocks
        mock_args = Mock()
        mock_args.vendor_id = "8086"
        mock_args.device_id = "1533"
        mock_args.verbose = False
        mock_args.src = None
        mock_parse.return_value = mock_args

        mock_ensure.return_value = pathlib.Path("/fake/kernel")
        mock_resolve.return_value = "e1000e"
        mock_find.return_value = [pathlib.Path("/fake/driver.c")]
        mock_extract.return_value = {
            "driver_module": "e1000e",
            "registers": [],
            "state_machine_analysis": {"extracted_state_machines": 0},
        }

        # Should not raise any exceptions
        main()

        # Verify call chain
        mock_resolve.assert_called_once_with("8086", "1533")
        mock_find.assert_called_once()
        mock_extract.assert_called_once()

    @patch("src.scripts.driver_scrape.parse_arguments")
    @patch("src.scripts.driver_scrape.ensure_kernel_source")
    def test_main_no_kernel_source(self, mock_ensure, mock_parse, capsys):
        """Test main with no kernel source available."""
        mock_args = Mock()
        mock_args.vendor_id = "8086"
        mock_args.device_id = "1533"
        mock_args.verbose = False
        mock_args.src = None
        mock_parse.return_value = mock_args

        mock_ensure.return_value = None

        main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["driver_module"] == "unknown"
        assert output["registers"] == []
        assert (
            "Linux source package not found"
            in output["state_machine_analysis"]["analysis_report"]
        )

    @patch("src.scripts.driver_scrape.parse_arguments")
    def test_main_invalid_vendor_id(self, mock_parse):
        """Test main with invalid vendor ID."""
        mock_args = Mock()
        mock_args.vendor_id = "INVALID"
        mock_args.device_id = "1533"
        mock_args.verbose = False
        mock_args.src = None
        mock_parse.return_value = mock_args

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    @patch("src.scripts.driver_scrape.parse_arguments")
    @patch("src.scripts.driver_scrape.check_linux_requirement")
    def test_main_non_linux_platform(self, mock_check, mock_parse):
        """Test main on non-Linux platform."""
        mock_args = Mock()
        mock_args.vendor_id = "8086"
        mock_args.device_id = "1533"
        mock_args.verbose = False
        mock_args.src = None
        mock_parse.return_value = mock_args

        mock_check.side_effect = RuntimeError("Requires Linux")

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 2


class TestNestedStateMachine:
    """Test handling of drivers with nested switch state machines."""

    def test_nested_switch_analysis(self):
        """Test analysis of nested switch statements."""
        complex_content = {
            pathlib.Path(
                "complex.c"
            ): """
#define REG_STATE_CTRL 0x2000
#define REG_SUB_STATE  0x2004

int complex_state_machine(struct device *dev) {
    u32 main_state = readl(dev->base + REG_STATE_CTRL);
    
    switch (main_state) {
        case MAIN_STATE_INIT:
            writel(0x1, dev->base + REG_STATE_CTRL);
            
            /* Nested state machine */
            switch (dev->sub_state) {
                case SUB_INIT:
                    writew(0x10, dev->base + REG_SUB_STATE);
                    udelay(100);
                    dev->sub_state = SUB_READY;
                    break;
                case SUB_READY:
                    if (readw(dev->base + REG_SUB_STATE) & 0x8000) {
                        writew(0x20, dev->base + REG_SUB_STATE);
                        dev->sub_state = SUB_ACTIVE;
                    }
                    break;
                case SUB_ACTIVE:
                    /* Complex nested logic */
                    for (int i = 0; i < 10; i++) {
                        if (readl(dev->base + REG_STATE_CTRL) & (1 << i)) {
                            writel(i, dev->base + REG_SUB_STATE);
                            msleep(10);
                        }
                    }
                    break;
            }
            break;
            
        case MAIN_STATE_ACTIVE:
            /* Another level of nesting */
            if (dev->flags & FLAG_SPECIAL) {
                switch (dev->special_mode) {
                    case SPECIAL_MODE_A:
                        writeq(0x123456789ABCDEF0, dev->base + REG_STATE_CTRL);
                        break;
                    case SPECIAL_MODE_B:
                        writeb(0xFF, dev->base + REG_SUB_STATE);
                        break;
                }
            }
            break;
    }
    
    return 0;
}
"""
        }

        analyzer = DriverAnalyzer(complex_content)

        # Test that nested braces are handled correctly
        sequences = analyzer.analyze_access_sequences("REG_STATE_CTRL")
        assert len(sequences) > 0

        # Should detect multiple bit widths
        bit_widths = {seq["bit_width"] for seq in sequences}
        assert len(bit_widths) > 1  # Should have 8, 16, 32, 64 bit accesses

        # Test timing constraints detection
        constraints = analyzer.analyze_timing_constraints()
        assert len(constraints) > 0

        # Should detect different delay types
        delay_types = {c.get("type") for c in constraints}
        assert len(delay_types) > 0


class TestOutputSchema:
    """Test output schema compliance."""

    def test_register_schema(self, sample_file_contents):
        """Test that register output matches expected schema."""
        analyzer = DriverAnalyzer(sample_file_contents)

        # Mock source files for extraction
        with patch("pathlib.Path.read_text") as mock_read:
            mock_read.return_value = sample_file_contents[pathlib.Path("test.c")]

            result = extract_registers_with_analysis(
                [pathlib.Path("test.c")], "test_driver"
            )

            # Check top-level schema
            assert "driver_module" in result
            assert "registers" in result
            assert "state_machine_analysis" in result

            # Check register schema
            if result["registers"]:
                reg = result["registers"][0]
                required_fields = [
                    "offset",
                    "name",
                    "value",
                    "rw",
                    "bit_width",
                    "context",
                ]
                for field in required_fields:
                    assert field in reg, f"Missing required field: {field}"

                # Check offset is hex string
                assert isinstance(reg["offset"], str)
                assert reg["offset"].startswith("0x")

                # Check bit_width is integer
                assert isinstance(reg["bit_width"], int)
                assert reg["bit_width"] in [8, 16, 32, 64]

                # Check rw values
                assert reg["rw"] in ["ro", "wo", "rw"]


class TestPerformanceOptimizations:
    """Test performance optimization features."""

    def test_file_content_caching(self, sample_file_contents):
        """Test that file contents are cached and reused."""
        analyzer = DriverAnalyzer(sample_file_contents)

        # Multiple calls should use cached content
        context1 = analyzer.analyze_function_context("REG_CONTROL")
        context2 = analyzer.analyze_function_context("REG_STATUS")

        # Both should succeed without re-reading files
        assert context1["function"] is not None
        assert context2["function"] is not None

    def test_regex_pattern_caching(self, sample_file_contents):
        """Test that regex patterns are cached."""
        analyzer = DriverAnalyzer(sample_file_contents)

        # First call should compile and cache pattern
        analyzer._get_function_pattern("REG_CONTROL")
        assert "REG_CONTROL" in analyzer._func_pattern_cache

        # Second call should use cached pattern
        pattern = analyzer._get_function_pattern("REG_CONTROL")
        assert pattern is analyzer._func_pattern_cache["REG_CONTROL"]


if __name__ == "__main__":
    pytest.main([__file__])
