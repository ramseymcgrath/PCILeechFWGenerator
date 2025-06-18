#!/usr/bin/env python3
"""
Board Configuration Module

Centralized board-to-FPGA mapping and configuration to eliminate
duplication across TCL generation methods.
"""

import logging
from typing import Any, Dict, Optional

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

# Board display information for user interface
BOARD_DISPLAY_INFO = {
    "pcileech_75t484_x1": {
        "display_name": "CaptainDMA 75T",
        "description": "[RECOMMENDED - CaptainDMA 75T with USB-3]",
        "is_recommended": True,
    },
    "35t": {
        "display_name": "35T Legacy Board",
        "description": "",
        "is_recommended": False,
    },
    "75t": {
        "display_name": "75T Legacy Board",
        "description": "",
        "is_recommended": False,
    },
    "100t": {
        "display_name": "100T Legacy Board",
        "description": "",
        "is_recommended": False,
    },
    "pcileech_35t484_x1": {
        "display_name": "CaptainDMA 35T x1",
        "description": "",
        "is_recommended": False,
    },
    "pcileech_35t325_x4": {
        "display_name": "CaptainDMA 35T x4",
        "description": "",
        "is_recommended": False,
    },
    "pcileech_35t325_x1": {
        "display_name": "CaptainDMA 35T x1 (325)",
        "description": "",
        "is_recommended": False,
    },
    "pcileech_100t484_x1": {
        "display_name": "CaptainDMA 100T",
        "description": "",
        "is_recommended": False,
    },
    "pcileech_enigma_x1": {
        "display_name": "CaptainDMA Enigma x1",
        "description": "",
        "is_recommended": False,
    },
    "pcileech_squirrel": {
        "display_name": "CaptainDMA Squirrel",
        "description": "",
        "is_recommended": False,
    },
    "pcileech_pciescreamer_xc7a35": {
        "display_name": "PCIeScreamer XC7A35",
        "description": "",
        "is_recommended": False,
    },
}

# PCILeech-specific board configurations
PCILEECH_BOARD_CONFIG = {
    "pcileech_35t325_x4": {
        "fpga_part": "xc7a35tcsg324-2",
        "fpga_family": "7series",
        "pcie_ip_type": "axi_pcie",
        "max_lanes": 4,
        "supports_msi": True,
        "supports_msix": False,
        "src_files": [
            "pcileech_top.sv",
            "bar_controller.sv",
            "cfg_shadow.sv",
            "msix_table.sv",
        ],
        "ip_files": ["pcie_axi_bridge.xci"],
        "coefficient_files": [],
    },
    "pcileech_75t484_x1": {
        "fpga_part": "xc7a75tfgg484-2",
        "fpga_family": "7series",
        "pcie_ip_type": "pcie_7x",
        "max_lanes": 1,
        "supports_msi": True,
        "supports_msix": True,
        "src_files": [
            "pcileech_top.sv",
            "bar_controller.sv",
            "cfg_shadow.sv",
            "msix_table.sv",
            "msix_capability_registers.sv",
            "msix_implementation.sv",
        ],
        "ip_files": ["pcie_7x_bridge.xci"],
        "coefficient_files": [],
    },
    "pcileech_100t484_x1": {
        "fpga_part": "xczu3eg-sbva484-1-e",
        "fpga_family": "ultrascale_plus",
        "pcie_ip_type": "pcie_ultrascale",
        "max_lanes": 1,
        "supports_msi": True,
        "supports_msix": True,
        "src_files": [
            "pcileech_top.sv",
            "bar_controller.sv",
            "cfg_shadow.sv",
            "msix_table.sv",
            "msix_capability_registers.sv",
            "msix_implementation.sv",
            "advanced_controller.sv",
        ],
        "ip_files": ["pcie_ultrascale_bridge.xci"],
        "coefficient_files": [],
    },
}


def get_fpga_part(board: str) -> str:
    """
    Get FPGA part number for a given board.

    Args:
        board: Board name

    Returns:
        FPGA part number string
    """
    fpga_part = BOARD_FPGA_MAPPING[board]
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


def get_pcileech_board_config(board: str) -> Dict[str, Any]:
    """
    Get PCILeech-specific board configuration.

    Args:
        board: Board name

    Returns:
        PCILeech board configuration dictionary

    Raises:
        KeyError: If board is not found in PCILeech configurations
    """
    if board not in PCILEECH_BOARD_CONFIG:
        raise KeyError(f"PCILeech board configuration not found for: {board}")

    return PCILEECH_BOARD_CONFIG[board]


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


def get_board_display_info(board: str) -> Dict[str, str]:
    """
    Get display information for a board.

    Args:
        board: Board name

    Returns:
        Dictionary with display information (display_name, description, is_recommended)
    """
    return BOARD_DISPLAY_INFO.get(
        board,
        {
            "display_name": board,
            "description": "",
            "is_recommended": False,
        },
    )


def list_boards_with_recommendations() -> list[tuple[str, Dict[str, str]]]:
    """
    Get list of boards with their display information, ordered by recommendation.

    Returns:
        List of tuples (board_name, display_info) with recommended boards first
    """
    boards = list_supported_boards()

    # Sort so recommended boards come first
    def sort_key(board):
        display_info = get_board_display_info(board)
        return (not display_info.get("is_recommended", False), board)

    sorted_boards = sorted(boards, key=sort_key)

    return [(board, get_board_display_info(board)) for board in sorted_boards]
