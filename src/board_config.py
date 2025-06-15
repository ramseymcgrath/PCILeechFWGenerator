#!/usr/bin/env python3
"""
Board Configuration Module

Centralized board-to-FPGA mapping and configuration to eliminate
duplication across TCL generation methods.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Centralized board-to-FPGA part mapping
BOARD_FPGA_MAPPING = {
    # Original boards
    "35t": "xc7a35tcsg324-2",
    "75t": "xc7a75tfgg484-2",
    "100t": "xczu3eg-sbva484-1-e",
    # CaptainDMA boards
    "pcileech_75t484_x1": "xc7a75tfgg484-2",
    "pcileech_35t484_x1": "xc7a35tfgg484-2",
    "pcileech_35t325_x4": "xc7a35tcsg324-2",
    "pcileech_35t325_x1": "xc7a35tcsg324-2",
    "pcileech_100t484_x1": "xczu3eg-sbva484-1-e",
    # Other boards
    "pcileech_enigma_x1": "xc7a75tfgg484-2",
    "pcileech_squirrel": "xc7a35tcsg324-2",
    "pcileech_pciescreamer_xc7a35": "xc7a35tcsg324-2",
}

# FPGA family detection patterns
FPGA_FAMILY_PATTERNS = {
    "7series": ["xc7a", "xc7k", "xc7v", "xc7z"],
    "ultrascale": ["xcku", "xcvu", "xczu"],
    "ultrascale_plus": ["xcku", "xcvu", "xczu"],  # UltraScale+ uses same prefixes
}


def get_fpga_part(board: str) -> str:
    """
    Get FPGA part number for a given board.

    Args:
        board: Board name

    Returns:
        FPGA part number string
    """
    fpga_part = BOARD_FPGA_MAPPING.get(board, "xc7a35tcsg324-2")
    logger.debug(f"Board {board} mapped to FPGA part {fpga_part}")
    return fpga_part


def get_fpga_family(fpga_part: str) -> str:
    """
    Determine FPGA family from part number.

    Args:
        fpga_part: FPGA part number

    Returns:
        FPGA family string
    """
    fpga_part_lower = fpga_part.lower()

    for family, patterns in FPGA_FAMILY_PATTERNS.items():
        for pattern in patterns:
            if fpga_part_lower.startswith(pattern):
                return family

    # Default to 7-series for unknown parts
    return "7series"


def get_pcie_ip_type(fpga_part: str) -> str:
    """
    Determine appropriate PCIe IP core type based on FPGA part.

    Args:
        fpga_part: FPGA part number

    Returns:
        PCIe IP type string
    """
    if "xc7a35t" in fpga_part:
        return "axi_pcie"
    elif "xczu" in fpga_part:
        return "pcie_ultrascale"
    else:
        return "pcie_7x"


def get_board_info(board: str) -> Dict[str, str]:
    """
    Get comprehensive board information.

    Args:
        board: Board name

    Returns:
        Dictionary with board configuration
    """
    fpga_part = get_fpga_part(board)
    fpga_family = get_fpga_family(fpga_part)
    pcie_ip_type = get_pcie_ip_type(fpga_part)

    return {
        "name": board,
        "fpga_part": fpga_part,
        "fpga_family": fpga_family,
        "pcie_ip_type": pcie_ip_type,
    }


def validate_board(board: str) -> bool:
    """
    Validate if board is supported.

    Args:
        board: Board name

    Returns:
        True if board is supported
    """
    return board in BOARD_FPGA_MAPPING


def list_supported_boards() -> list[str]:
    """
    Get list of all supported boards.

    Returns:
        List of supported board names
    """
    return list(BOARD_FPGA_MAPPING.keys())
