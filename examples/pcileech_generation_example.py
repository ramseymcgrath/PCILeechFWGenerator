#!/usr/bin/env python3
"""
PCILeech Firmware Generation Example

This example demonstrates the complete PCILeech firmware generation process
using the dynamic data integration layer and main orchestrator class.

The example shows how to:
1. Configure PCILeech generation parameters
2. Generate complete firmware with behavior profiling
3. Save generated artifacts to disk
4. Integrate with build system

Usage:
    python examples/pcileech_generation_example.py --device 0000:03:00.0
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from device_clone.pcileech_generator import (PCILeechGenerationConfig,
                                             PCILeechGenerationError,
                                             PCILeechGenerator)


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("pcileech_generation.log"),
        ],
    )


def create_generation_config(
    device_bdf: str,
    output_dir: str = "generated_firmware",
    enable_profiling: bool = True,
    enable_advanced: bool = True,
) -> PCILeechGenerationConfig:
    """
    Create PCILeech generation configuration.

    Args:
        device_bdf: Device Bus:Device.Function identifier
        output_dir: Output directory for generated files
        enable_profiling: Enable device behavior profiling
        enable_advanced: Enable advanced features

    Returns:
        PCILeech generation configuration
    """
    return PCILeechGenerationConfig(
        device_bdf=device_bdf,
        device_profile="generic",
        enable_behavior_profiling=enable_profiling,
        behavior_capture_duration=30.0,
        enable_manufacturing_variance=True,
        enable_advanced_features=enable_advanced,
        template_dir=None,  # Use default template directory
        output_dir=Path(output_dir),
        pcileech_command_timeout=1000,
        pcileech_buffer_size=4096,
        enable_dma_operations=True,
        enable_interrupt_coalescing=False,
        strict_validation=True,
        fail_on_missing_data=False,  # Allow graceful degradation for demo
    )


def generate_pcileech_firmware(config: PCILeechGenerationConfig) -> None:
    """
    Generate complete PCILeech firmware.

    Args:
        config: PCILeech generation configuration
    """
    logger = logging.getLogger(__name__)

    try:
        # Initialize PCILeech generator
        logger.info(f"Initializing PCILeech generator for device {config.device_bdf}")
        generator = PCILeechGenerator(config)

        # Generate complete firmware
        logger.info("Starting PCILeech firmware generation...")
        generation_result = generator.generate_pcileech_firmware()

        # Display generation summary
        display_generation_summary(generation_result)

        # Save generated firmware to disk
        logger.info("Saving generated firmware...")
        output_path = generator.save_generated_firmware(generation_result)

        logger.info(f"PCILeech firmware generation completed successfully!")
        logger.info(f"Generated files saved to: {output_path}")

        # Display file structure
        display_generated_files(output_path)

    except PCILeechGenerationError as e:
        logger.error(f"PCILeech generation failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during generation: {e}")
        sys.exit(1)


def display_generation_summary(result: dict) -> None:
    """Display summary of generation results."""
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("PCILeech Firmware Generation Summary")
    logger.info("=" * 60)

    # Device information
    device_config = result.get("device_config", {})
    logger.info(f"Device BDF: {result.get('device_bdf', 'Unknown')}")
    logger.info(f"Vendor ID: {device_config.get('vendor_id', 'Unknown')}")
    logger.info(f"Device ID: {device_config.get('device_id', 'Unknown')}")
    logger.info(f"Class Code: {device_config.get('class_code', 'Unknown')}")

    # Behavior profile information
    behavior_profile = result.get("behavior_profile")
    if behavior_profile:
        logger.info(f"Behavior Profile:")
        logger.info(f"  - Total Accesses: {behavior_profile.total_accesses}")
        logger.info(f"  - Capture Duration: {behavior_profile.capture_duration:.1f}s")
        logger.info(f"  - Timing Patterns: {len(behavior_profile.timing_patterns)}")
        logger.info(f"  - State Transitions: {len(behavior_profile.state_transitions)}")
    else:
        logger.info("Behavior Profile: Not captured")

    # MSI-X information
    msix_data = result.get("msix_data", {})
    if msix_data.get("is_supported"):
        logger.info(f"MSI-X Configuration:")
        logger.info(f"  - Vectors: {msix_data.get('table_size', 0)}")
        logger.info(f"  - Table BIR: {msix_data.get('table_bir', 0)}")
        logger.info(f"  - Table Offset: 0x{msix_data.get('table_offset', 0):x}")
    else:
        logger.info("MSI-X: Not supported")

    # Generated modules
    systemverilog_modules = result.get("systemverilog_modules", {})
    logger.info(f"Generated SystemVerilog Modules: {len(systemverilog_modules)}")
    for module_name in systemverilog_modules.keys():
        logger.info(f"  - {module_name}")

    # Template context summary
    template_context = result.get("template_context", {})
    logger.info(f"Template Context Sections: {len(template_context)}")
    for section_name in template_context.keys():
        logger.info(f"  - {section_name}")

    logger.info("=" * 60)


def display_generated_files(output_path: Path) -> None:
    """Display structure of generated files."""
    logger = logging.getLogger(__name__)

    logger.info("Generated File Structure:")
    logger.info("-" * 40)

    def print_tree(path: Path, prefix: str = ""):
        """Recursively print directory tree."""
        if path.is_file():
            size = path.stat().st_size
            logger.info(f"{prefix}├── {path.name} ({size} bytes)")
        elif path.is_dir():
            logger.info(f"{prefix}├── {path.name}/")
            children = sorted(path.iterdir())
            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                child_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(child, child_prefix)

    print_tree(output_path)
    logger.info("-" * 40)


def validate_device_bdf(bdf: str) -> bool:
    """
    Validate device BDF format.

    Args:
        bdf: Device Bus:Device.Function identifier

    Returns:
        True if valid, False otherwise
    """
    import re

    pattern = r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]$"
    return bool(re.match(pattern, bdf))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PCILeech Firmware Generation Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate firmware for a specific device
  python pcileech_generation_example.py --device 0000:03:00.0
  
  # Generate with custom output directory
  python pcileech_generation_example.py --device 0000:03:00.0 --output my_firmware
  
  # Generate without behavior profiling (faster)
  python pcileech_generation_example.py --device 0000:03:00.0 --no-profiling
  
  # Generate with debug logging
  python pcileech_generation_example.py --device 0000:03:00.0 --debug
        """,
    )

    parser.add_argument(
        "--device",
        "-d",
        required=True,
        help="Device BDF (Bus:Device.Function) e.g., 0000:03:00.0",
    )

    parser.add_argument(
        "--output",
        "-o",
        default="generated_firmware",
        help="Output directory for generated files (default: generated_firmware)",
    )

    parser.add_argument(
        "--no-profiling",
        action="store_true",
        help="Disable device behavior profiling (faster generation)",
    )

    parser.add_argument(
        "--no-advanced",
        action="store_true",
        help="Disable advanced features generation",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    # Validate device BDF
    if not validate_device_bdf(args.device):
        logger.error(f"Invalid device BDF format: {args.device}")
        logger.error("Expected format: XXXX:XX:XX.X (e.g., 0000:03:00.0)")
        sys.exit(1)

    # Create generation configuration
    config = create_generation_config(
        device_bdf=args.device,
        output_dir=args.output,
        enable_profiling=not args.no_profiling,
        enable_advanced=not args.no_advanced,
    )

    logger.info("PCILeech Firmware Generation Example")
    logger.info(f"Device: {args.device}")
    logger.info(f"Output: {args.output}")
    logger.info(
        f"Behavior Profiling: {'Enabled' if config.enable_behavior_profiling else 'Disabled'}"
    )
    logger.info(
        f"Advanced Features: {'Enabled' if config.enable_advanced_features else 'Disabled'}"
    )

    # Generate PCILeech firmware
    generate_pcileech_firmware(config)


if __name__ == "__main__":
    main()
