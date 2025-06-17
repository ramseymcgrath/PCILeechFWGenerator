#!/usr/bin/env python3
"""
SystemVerilog Template Test Runner
Validates that Jinja2 templates can generate valid SystemVerilog modules
"""

import os
import sys
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def render_template(template_path, output_path, **kwargs):
    """Render a Jinja2 template with given parameters"""
    template_dir = template_path.parent
    template_name = template_path.name

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)

    rendered = template.render(**kwargs)

    with open(output_path, "w") as f:
        f.write(rendered)

    return output_path


def test_bar_controller():
    """Test BAR controller template"""
    print("Testing BAR controller template...")

    template_path = Path(
        "../src/templating/templates/systemverilog/bar_controller.sv.j2"
    )
    output_path = Path("generated_bar_controller.sv")

    params = {
        "BAR_APERTURE_SIZE": 131072,
        "NUM_MSIX": 4,
        "MSIX_TABLE_BIR": 0,
        "MSIX_TABLE_OFFSET": 0x1000,
        "MSIX_PBA_BIR": 0,
        "MSIX_PBA_OFFSET": 0x2000,
        "CONFIG_SHDW_HI": "20'hFFFFF",
        "CUSTOM_WIN_BASE": "20'hFFFFE",
        "USE_BYTE_ENABLES": True,
    }

    try:
        render_template(template_path, output_path, **params)
        print(f"✓ BAR controller template rendered successfully to {output_path}")
        return True
    except Exception as e:
        print(f"✗ BAR controller template failed: {e}")
        return False


def test_cfg_shadow():
    """Test configuration space shadow template"""
    print("Testing configuration space shadow template...")

    template_path = Path("../src/templating/templates/systemverilog/cfg_shadow.sv.j2")
    output_path = Path("generated_cfg_shadow.sv")

    params = {
        "CONFIG_SPACE_SIZE": 4096,
        "OVERLAY_ENTRIES": 32,
        "OVERLAY_MAP": [
            (0x001, 0x0000FFFF),  # Command register
            (0x002, 0x0000FFFF),  # Status register
            (0x004, 0x000000FF),  # Cache Line Size
            (0x01C, 0xC000FFFF),  # MSI-X capability
        ],
        "DUAL_PORT": False,
    }

    try:
        render_template(template_path, output_path, **params)
        print(f"✓ Config space shadow template rendered successfully to {output_path}")
        return True
    except Exception as e:
        print(f"✗ Config space shadow template failed: {e}")
        return False


def test_msix_table():
    """Test MSI-X table template"""
    print("Testing MSI-X table template...")

    template_path = Path("../src/templating/templates/systemverilog/msix_table.sv.j2")
    output_path = Path("generated_msix_table.sv")

    params = {
        "NUM_MSIX": 8,
        "MSIX_TABLE_BIR": 0,
        "MSIX_TABLE_OFFSET": 0x1000,
        "MSIX_PBA_BIR": 0,
        "MSIX_PBA_OFFSET": 0x2000,
        "INIT_TABLE": [],
        "INIT_PBA": [],
        "RESET_CLEAR": True,
        "WRITE_PBA_ALLOWED": True,
        "USE_BYTE_ENABLES": True,
    }

    try:
        render_template(template_path, output_path, **params)
        print(f"✓ MSI-X table template rendered successfully to {output_path}")
        return True
    except Exception as e:
        print(f"✗ MSI-X table template failed: {e}")
        return False


def test_option_rom_bar():
    """Test Option ROM BAR window template"""
    print("Testing Option ROM BAR window template...")

    template_path = Path(
        "../src/templating/templates/systemverilog/option_rom_bar_window.sv.j2"
    )
    output_path = Path("generated_option_rom_bar.sv")

    params = {
        "ROM_SIZE": 65536,
        "ROM_BAR_INDEX": 5,
        "ROM_HEX_FILE": "rom_init.hex",
        "INIT_ROM": [],
        "ALLOW_ROM_WRITES": True,
        "ENABLE_SIGNATURE_CHECK": True,
    }

    try:
        render_template(template_path, output_path, **params)
        print(f"✓ Option ROM BAR template rendered successfully to {output_path}")
        return True
    except Exception as e:
        print(f"✗ Option ROM BAR template failed: {e}")
        return False


def test_option_rom_spi():
    """Test Option ROM SPI flash template"""
    print("Testing Option ROM SPI flash template...")

    template_path = Path(
        "../src/templating/templates/systemverilog/option_rom_spi_flash.sv.j2"
    )
    output_path = Path("generated_option_rom_spi.sv")

    params = {
        "ROM_SIZE": 65536,
        "FLASH_ADDR_OFFSET": 0,
        "CACHE_SIZE": 16,
        "USE_QSPI": True,
        "ENABLE_CACHE": True,
        "INIT_CACHE_VALID": False,
        "RESET_CLEAR": True,
        "SIGNATURE_CHECK": True,
        "QSPI_ONLY_CMD": "EB",
        "SPI_FAST_CMD": "0B",
    }

    try:
        render_template(template_path, output_path, **params)
        print(f"✓ Option ROM SPI template rendered successfully to {output_path}")
        return True
    except Exception as e:
        print(f"✗ Option ROM SPI template failed: {e}")
        return False


def main():
    """Run all template tests"""
    print("SystemVerilog Template Test Runner")
    print("=" * 40)

    # Change to tests directory
    os.chdir(Path(__file__).parent)

    tests = [
        test_bar_controller,
        test_cfg_shadow,
        test_msix_table,
        test_option_rom_bar,
        test_option_rom_spi,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("All template tests passed! ✓")
        return 0
    else:
        print("Some template tests failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
