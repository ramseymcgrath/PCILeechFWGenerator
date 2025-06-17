#!/usr/bin/env python3
"""
Configuration Space Management Module

Handles PCI configuration space reading via VFIO and synthetic configuration
space generation for PCILeech firmware building.
"""

import logging
import os
from typing import Any, Dict

try:
    from ..string_utils import log_info_safe, log_warning_safe
except ImportError:
    # Fallback for when string_utils is not available
    def log_info_safe(logger, template, **kwargs):
        logger.info(template.format(**kwargs))

    def log_warning_safe(logger, template, **kwargs):
        logger.warning(template.format(**kwargs))


# Import device configuration system
try:
    from .device_config import DeviceConfiguration, get_device_config
except ImportError:
    try:
        from .device_config import DeviceConfiguration, get_device_config
    except ImportError:
        # Fallback if device config is not available
        def get_device_config(profile_name="generic"):
            return None

        class DeviceConfiguration:
            pass


logger = logging.getLogger(__name__)


class ConfigSpaceManager:
    """Manages PCI configuration space operations."""

    def __init__(self, bdf: str, device_profile: str = "generic"):
        self.bdf = bdf
        self.device_config = get_device_config(device_profile)

    def read_vfio_config_space(self) -> bytes:
        """Read PCI configuration space via VFIO."""
        try:
            # Find IOMMU group for the device
            iommu_group_path = f"/sys/bus/pci/devices/{self.bdf}/iommu_group"
            if not os.path.exists(iommu_group_path):
                raise RuntimeError(f"IOMMU group not found for device {self.bdf}")

            iommu_group = os.path.basename(os.readlink(iommu_group_path))
            vfio_device = f"/dev/vfio/{iommu_group}"

            if not os.path.exists(vfio_device):
                raise RuntimeError(f"VFIO device {vfio_device} not found")

            logger.info(
                f"Reading configuration space for device {self.bdf} via VFIO group {iommu_group}"
            )

            # Read actual configuration space from sysfs as fallback
            config_path = f"/sys/bus/pci/devices/{self.bdf}/config"
            if os.path.exists(config_path):
                with open(config_path, "rb") as f:
                    config_space = f.read(256)  # Read first 256 bytes
                log_info_safe(
                    logger,
                    "Successfully read {bytes} bytes of configuration space",
                    bytes=len(config_space),
                )
                return config_space
            else:
                # Generate synthetic configuration space if real one not available
                logger.warning(
                    "Real config space not available, generating synthetic data"
                )
                return self.generate_synthetic_config_space()

        except Exception as e:
            logger.error(f"Failed to read VFIO config space: {e}")
            logger.info("Generating synthetic configuration space as fallback")
            return self.generate_synthetic_config_space()

    def generate_synthetic_config_space(self) -> bytes:
        """Generate production-quality synthetic PCI configuration space using device configuration."""
        config_space = bytearray(4096)  # Extended config space (4KB)

        # Use device configuration if available, otherwise fall back to defaults
        if self.device_config:
            vendor_id = self.device_config.identification.vendor_id
            device_id = self.device_config.identification.device_id
            class_code = self.device_config.identification.class_code
            subsys_vendor_id = self.device_config.identification.subsystem_vendor_id
            subsys_device_id = self.device_config.identification.subsystem_device_id
            command_reg = self.device_config.registers.command
            status_reg = self.device_config.registers.status
            revision_id = self.device_config.registers.revision_id
            cache_line_size = self.device_config.registers.cache_line_size
            latency_timer = self.device_config.registers.latency_timer
            header_type = self.device_config.registers.header_type
            bist = self.device_config.registers.bist

            log_info_safe(
                logger,
                "Using device configuration profile: {profile}",
                profile=self.device_config.name,
            )
        else:
            # Fallback to hardcoded defaults
            vendor_id = 0x8086
            device_id = 0x15B8
            class_code = 0x020000
            subsys_vendor_id = 0x8086
            subsys_device_id = 0x0000
            command_reg = 0x0006
            status_reg = 0x0210
            revision_id = 0x01
            cache_line_size = 0x10
            latency_timer = 0x00
            header_type = 0x00
            bist = 0x00

            log_warning_safe(
                logger, "No device configuration available, using fallback defaults"
            )

        # Standard PCI Configuration Header (0x00-0x3F)
        # Vendor ID and Device ID
        config_space[0:2] = vendor_id.to_bytes(2, "little")
        config_space[2:4] = device_id.to_bytes(2, "little")

        # Command Register - configurable based on device type
        config_space[4:6] = command_reg.to_bytes(2, "little")

        # Status Register - configurable based on device capabilities
        # Ensure capabilities list bit (bit 4) is set
        status_reg_with_caps = status_reg | 0x0010  # Set capabilities list bit
        config_space[6:8] = status_reg_with_caps.to_bytes(2, "little")

        # Revision ID and Class Code
        config_space[8] = revision_id  # Revision ID from device config
        config_space[9] = class_code & 0xFF  # Programming Interface
        config_space[10:12] = ((class_code >> 8) & 0xFFFF).to_bytes(2, "little")

        # Cache Line Size, Latency Timer, Header Type, BIST - use device config
        config_space[12] = cache_line_size
        config_space[13] = latency_timer
        config_space[14] = header_type
        config_space[15] = bist

        # Base Address Registers (BARs) - use default configuration for now
        # TODO: Make BARs configurable through device configuration
        default_bar_configs = [
            0xF0000000,
            0x00000000,
            0x0000E001,
            0x00000000,
            0x00000000,
            0x00000000,
        ]
        for i, bar_val in enumerate(default_bar_configs):
            offset = 16 + (i * 4)
            config_space[offset : offset + 4] = bar_val.to_bytes(4, "little")

        # Cardbus CIS Pointer (unused)
        config_space[40:44] = (0x00000000).to_bytes(4, "little")

        # Subsystem Vendor ID and Subsystem ID
        config_space[44:46] = subsys_vendor_id.to_bytes(2, "little")
        config_space[46:48] = subsys_device_id.to_bytes(2, "little")
        # Expansion ROM Base Address (unused)
        config_space[48:52] = (0x00000000).to_bytes(4, "little")

        # Capabilities Pointer - point to first capability at 0x40
        config_space[52] = 0x40  # First capability at 0x40

        # Reserved
        config_space[53:60] = b"\x00" * 7

        # Interrupt Line, Interrupt Pin, Min Grant, Max Latency
        config_space[60] = 0x0B  # Interrupt line (IRQ 11)
        config_space[61] = 0x01  # Interrupt pin A
        config_space[62] = 0x00  # Min grant
        config_space[63] = 0x00  # Max latency

        # Build capability chain starting at 0x40
        cap_offset = 0x40

        # Power Management Capability (always present)
        config_space[cap_offset] = 0x01  # PM Capability ID
        config_space[cap_offset + 1] = 0x50  # Next capability pointer
        config_space[cap_offset + 2 : cap_offset + 4] = (0x0003).to_bytes(
            2, "little"
        )  # PM Capabilities
        config_space[cap_offset + 4 : cap_offset + 6] = (0x0000).to_bytes(
            2, "little"
        )  # PM Control/Status
        cap_offset = 0x50

        # MSI-X Capability
        config_space[cap_offset] = 0x11  # MSI-X Capability ID
        config_space[cap_offset + 1] = 0x60  # Next capability pointer
        # MSI-X Control: Table size = 7 (8 entries), Function Mask = 0, MSI-X Enable = 0
        # Bits 10:0 = Table Size - 1 = 7 (for 8 entries)
        config_space[cap_offset + 2 : cap_offset + 4] = (0x0007).to_bytes(
            2, "little"
        )  # MSI-X Control with 8 table entries
        config_space[cap_offset + 4 : cap_offset + 8] = (0x00000000).to_bytes(
            4, "little"
        )  # Table Offset/BIR (BAR 0, offset 0)
        config_space[cap_offset + 8 : cap_offset + 12] = (0x00002000).to_bytes(
            4, "little"
        )  # PBA Offset/BIR (BAR 0, offset 0x2000)
        cap_offset = 0x60

        # PCIe Capability (for modern devices)
        config_space[cap_offset] = 0x10  # PCIe Capability ID
        config_space[cap_offset + 1] = 0x00  # Next capability pointer (end of chain)
        config_space[cap_offset + 2 : cap_offset + 4] = (0x0002).to_bytes(
            2, "little"
        )  # PCIe Capabilities
        config_space[cap_offset + 4 : cap_offset + 8] = (0x00000000).to_bytes(
            4, "little"
        )  # Device Capabilities
        config_space[cap_offset + 8 : cap_offset + 10] = (0x0000).to_bytes(
            2, "little"
        )  # Device Control
        config_space[cap_offset + 10 : cap_offset + 12] = (0x0000).to_bytes(
            2, "little"
        )  # Device Status

        log_info_safe(
            logger,
            "Generated synthetic config space with vendor_id=0x{vendor_id:04X}, device_id=0x{device_id:04X}",
            vendor_id=vendor_id,
            device_id=device_id,
        )

        # Return standard 256-byte config space
        return bytes(config_space[:256])

    def extract_device_info(self, config_space: bytes) -> Dict[str, Any]:
        """Extract device information from configuration space."""
        if len(config_space) < 64:
            raise ValueError("Configuration space too short")

        vendor_id = int.from_bytes(config_space[0:2], "little")
        device_id = int.from_bytes(config_space[2:4], "little")
        class_code = int.from_bytes(config_space[10:12], "little")
        revision_id = config_space[8]

        # Extract BARs
        bars = []
        for i in range(6):
            bar_offset = 16 + (i * 4)
            if bar_offset + 4 <= len(config_space):
                bar_value = int.from_bytes(
                    config_space[bar_offset : bar_offset + 4], "little"
                )
                bars.append(bar_value)

        device_info = {
            "vendor_id": f"{vendor_id:04x}",
            "device_id": f"{device_id:04x}",
            "class_code": f"{class_code:04x}",
            "revision_id": f"{revision_id:02x}",
            "bdf": self.bdf,
            "bars": bars,
            "config_space_hex": config_space.hex(),
            "config_space_size": len(config_space),
        }

        log_info_safe(
            logger,
            "Extracted device info: VID={vendor_id}, DID={device_id}",
            vendor_id=device_info["vendor_id"],
            device_id=device_info["device_id"],
        )
        return device_info
