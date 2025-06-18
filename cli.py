"""Command-line interface with argparse sub-commands."""

import argparse
import sys
import textwrap
from typing import Dict, List, Optional

from config import BuildConfig
from utils.logging import get_logger

logger = get_logger(__name__)


def list_pci_devices() -> List[Dict[str, str]]:
    """List all PCIe devices with their details."""
    import re

    from vfio import check_linux_requirement

    from utils.shell import Shell

    check_linux_requirement("PCIe device enumeration")

    pattern = re.compile(
        r"(?P<bdf>[0-9a-fA-F:.]+) .*?\["
        r"(?P<class>[0-9a-fA-F]{4})\]: .*?\["
        r"(?P<ven>[0-9a-fA-F]{4}):(?P<dev>[0-9a-fA-F]{4})\]"
    )

    shell = Shell()
    devices = []
    for line in shell.run("lspci -Dnn").splitlines():
        match = pattern.match(line)
        if match:
            device_info = match.groupdict()
            device_info["pretty"] = line
            devices.append(device_info)

    return devices


def choose_device(devices: List[Dict[str, str]]) -> Dict[str, str]:
    """Interactive device selection from the list of PCIe devices."""
    print("\nSelect donor PCIe device:")
    for i, device in enumerate(devices):
        print(f" [{i}] {device['pretty']}")

    while True:
        try:
            selection = input("Enter number: ")
            index = int(selection)
            return devices[index]
        except (ValueError, IndexError):
            print("  Invalid selection — please try again.")


def choose_board() -> str:
    """Interactive board selection from supported boards."""
    # Import board config to get supported boards
    try:
        from src.board_config import get_board_info, list_supported_boards
    except ImportError:
        # Fallback to hardcoded list if import fails
        supported_boards = [
            "pcileech_75t484_x1",
            "35t",
            "75t",
            "100t",
            "pcileech_35t484_x1",
            "pcileech_35t325_x4",
            "pcileech_35t325_x1",
            "pcileech_100t484_x1",
            "pcileech_enigma_x1",
            "pcileech_squirrel",
            "pcileech_pciescreamer_xc7a35",
        ]
        get_board_info = None
    else:
        # Reorder to put CaptainDMA 75T first
        all_boards = list_supported_boards()
        if "pcileech_75t484_x1" in all_boards:
            all_boards.remove("pcileech_75t484_x1")
            supported_boards = ["pcileech_75t484_x1"] + all_boards
        else:
            supported_boards = all_boards

    print("\nSelect target FPGA board:")
    for i, board in enumerate(supported_boards):
        description = board
        if get_board_info:
            try:
                board_info = get_board_info(board)
                fpga_part = board_info.get("fpga_part", "")
                if fpga_part:
                    description = f"{board} ({fpga_part})"
            except:
                pass

        # Mark the default/recommended option
        if board == "pcileech_75t484_x1":
            description += " [RECOMMENDED - CaptainDMA 75T with USB-3]"

        print(f" [{i}] {description}")

    print(f"\nDefault: [0] CaptainDMA 75T (pcileech_75t484_x1)")
    while True:
        try:
            selection = input("Enter number (or press Enter for default): ").strip()
            if not selection:
                return supported_boards[0]  # Return default (CaptainDMA 75T)
            index = int(selection)
            return supported_boards[index]
        except (ValueError, IndexError):
            print("  Invalid selection — please try again.")


def choose_device_type() -> str:
    """Interactive device type selection."""
    device_types = [
        ("generic", "Generic device (default)"),
        ("network", "Network card optimizations"),
        ("storage", "Storage device optimizations"),
        ("graphics", "Graphics card optimizations"),
        ("audio", "Audio device optimizations"),
    ]

    print("\nSelect device type for optimizations:")
    for i, (device_type, description) in enumerate(device_types):
        print(f" [{i}] {description}")

    while True:
        try:
            selection = input("Enter number: ")
            index = int(selection)
            return device_types[index][0]
        except (ValueError, IndexError):
            print("  Invalid selection — please try again.")


def create_build_config_from_args(args: argparse.Namespace) -> BuildConfig:
    """Create BuildConfig from parsed arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        BuildConfig instance
    """
    # Get device information
    devices = list_pci_devices()
    if not devices:
        raise RuntimeError("No PCIe devices found")

    selected_device = choose_device(devices)
    bdf = selected_device["bdf"]
    vendor = selected_device["ven"]
    device = selected_device["dev"]

    # Get IOMMU information
    from vfio import get_current_driver, get_iommu_group

    iommu_group = get_iommu_group(bdf)
    original_driver = get_current_driver(bdf)

    return BuildConfig(
        bdf=bdf,
        vendor=vendor,
        device=device,
        board=args.board,
        device_type=args.device_type,
        advanced_sv=args.advanced_sv,
        enable_variance=args.enable_variance,
        donor_dump=args.donor_dump,
        auto_install_headers=args.auto_install_headers,
        disable_power_management=args.disable_power_management,
        disable_error_handling=args.disable_error_handling,
        disable_performance_counters=args.disable_performance_counters,
        flash=args.flash,
        behavior_profile_duration=args.behavior_profile_duration,
        tui=args.tui,
        interactive=getattr(args, "interactive", False),
        original_driver=original_driver,
        iommu_group=iommu_group,
        vfio_device=f"/dev/vfio/{iommu_group}",
    )


def setup_build_parser(subparsers) -> argparse.ArgumentParser:
    """Setup the build sub-command parser."""
    build_parser = subparsers.add_parser(
        "build",
        help="Build firmware for specified device and board",
        description="Build PCILeech firmware from donor PCIe device",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              # CaptainDMA 75T with advanced features
              generate.py build --board pcileech_75t484_x1 --device-type network --advanced-sv
              
              # Legacy board with basic configuration
              generate.py build --board 35t --device-type generic
              
              # Manufacturing variance simulation
              generate.py build --enable-variance --behavior-profile-duration 60
        """
        ),
    )

    # Board selection
    build_parser.add_argument(
        "--board",
        choices=[
            "35t",
            "75t",
            "100t",
            "pcileech_75t484_x1",
            "pcileech_35t484_x1",
            "pcileech_35t325_x4",
            "pcileech_35t325_x1",
            "pcileech_100t484_x1",
            "pcileech_enigma_x1",
            "pcileech_squirrel",
            "pcileech_pciescreamer_xc7a35",
        ],
        default="pcileech_75t484_x1",
        help="Target FPGA board type (default: pcileech_75t484_x1)",
    )

    # Device type
    build_parser.add_argument(
        "--device-type",
        choices=["network", "storage", "graphics", "audio", "generic"],
        default="generic",
        help="Device type for specialized optimizations (default: generic)",
    )

    # Advanced features
    build_parser.add_argument(
        "--advanced-sv",
        action="store_true",
        help="Enable advanced SystemVerilog generation with enhanced features",
    )

    build_parser.add_argument(
        "--enable-variance",
        action="store_true",
        help="Enable manufacturing variance simulation for realistic timing",
    )

    build_parser.add_argument(
        "--donor-dump",
        action="store_true",
        help="Extract donor device parameters using kernel module before generation",
    )

    build_parser.add_argument(
        "--auto-install-headers",
        action="store_true",
        help="Automatically install kernel headers if missing (for donor dump)",
    )

    # Feature control
    build_parser.add_argument(
        "--disable-power-management",
        action="store_true",
        help="Disable power management features in advanced generation",
    )

    build_parser.add_argument(
        "--disable-error-handling",
        action="store_true",
        help="Disable error handling features in advanced generation",
    )

    build_parser.add_argument(
        "--disable-performance-counters",
        action="store_true",
        help="Disable performance counter features in advanced generation",
    )

    # Timing
    build_parser.add_argument(
        "--behavior-profile-duration",
        type=int,
        default=45,
        help="Duration for behavior profiling in seconds (default: 45)",
    )

    # TUI mode
    build_parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch TUI (Text User Interface) mode",
    )

    # Flash after build
    build_parser.add_argument(
        "--flash",
        action="store_true",
        help="Flash firmware after successful build",
    )

    return build_parser


def setup_flash_parser(subparsers) -> argparse.ArgumentParser:
    """Setup the flash sub-command parser."""
    flash_parser = subparsers.add_parser(
        "flash",
        help="Flash firmware binary to FPGA board",
        description="Flash firmware binary to FPGA board using usbloader",
    )

    flash_parser.add_argument(
        "firmware_path", help="Path to firmware binary file (e.g., output/firmware.bin)"
    )

    return flash_parser


def setup_tui_parser(subparsers) -> argparse.ArgumentParser:
    """Setup the TUI sub-command parser."""
    tui_parser = subparsers.add_parser(
        "tui",
        help="Launch Text User Interface",
        description="Launch interactive TUI for firmware generation",
    )

    return tui_parser


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with sub-commands."""
    parser = argparse.ArgumentParser(
        description="PCILeech Firmware Generator - Podman-based build system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Sub-commands:
              build    Build firmware for specified device and board
              flash    Flash firmware binary to FPGA board  
              tui      Launch Text User Interface
              
            Examples:
              # Build with CaptainDMA 75T and advanced features
              generate.py build --board pcileech_75t484_x1 --device-type network --advanced-sv
              
              # Flash existing firmware
              generate.py flash output/firmware.bin
              
              # Launch TUI
              generate.py tui
        """
        ),
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing commands",
    )

    # Create sub-parsers
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", metavar="COMMAND"
    )

    # Setup sub-command parsers
    setup_build_parser(subparsers)
    setup_flash_parser(subparsers)
    setup_tui_parser(subparsers)

    return parser


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Optional list of arguments (for testing)

    Returns:
        Parsed arguments namespace
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # If no sub-command specified, default to build with interactive board selection
    if not parsed_args.command:
        # Set default values for build command
        parsed_args.command = "build"
        parsed_args.board = choose_board()
        parsed_args.device_type = "generic"
        parsed_args.advanced_sv = True
        parsed_args.enable_variance = True
        parsed_args.donor_dump = True
        parsed_args.auto_install_headers = True
        parsed_args.disable_power_management = False
        parsed_args.disable_error_handling = False
        parsed_args.disable_performance_counters = False
        parsed_args.behavior_profile_duration = 45
        parsed_args.tui = False
        parsed_args.flash = True

    return parsed_args
