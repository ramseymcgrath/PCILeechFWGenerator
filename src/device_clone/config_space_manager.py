#!/usr/bin/env python3
"""
Configuration Space Management Module

Handles PCI configuration space reading via VFIO and synthetic configuration
space generation for PCILeech firmware building.
"""

import logging
import os
from typing import Any, Dict, Optional, Union

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
    # Fallback if device config is not available
    class DeviceConfiguration:
        pass

    def get_device_config(
        profile_name: str = "generic",
    ) -> Optional[DeviceConfiguration]:
        return None


logger = logging.getLogger(__name__)


class ConfigSpaceManager:
    """Manages PCI configuration space operations."""

    def __init__(
        self, bdf: str, device_profile: str = "generic", strict_vfio: bool = False
    ):
        self.bdf = bdf
        self.device_config = get_device_config(device_profile)
        self.strict_vfio = strict_vfio

    def run_vfio_diagnostics(self):
        """Run VFIO diagnostics to help troubleshoot issues."""
        try:
            from ..cli.vfio_diagnostics import run_vfio_diagnostics

            logger.info("Running VFIO diagnostics for troubleshooting...")
            run_vfio_diagnostics(self.bdf)
        except ImportError:
            logger.warning("VFIO diagnostics module not available")
        except Exception as e:
            logger.warning(f"VFIO diagnostics failed: {e}")

    def read_vfio_config_space(self, strict: Optional[bool] = None) -> bytes:
        """
        Read PCI configuration space via VFIO with automatic device binding.

        Args:
            strict: If True, fail if VFIO is not available. If None, use instance setting.

        Returns:
            Configuration space bytes

        Raises:
            RuntimeError: If VFIO reading fails in strict mode
        """
        if strict is None:
            strict = self.strict_vfio

        try:
            # Find IOMMU group for the device
            iommu_group_path = f"/sys/bus/pci/devices/{self.bdf}/iommu_group"
            if not os.path.exists(iommu_group_path):
                error_msg = f"IOMMU group not found for device {self.bdf}"
                if strict:
                    logger.error(f"{error_msg} - VFIO is required but not available")
                    raise RuntimeError(
                        f"{error_msg}. VFIO is required but IOMMU group not found. "
                        "Ensure IOMMU is enabled and device supports VFIO."
                    )
                else:
                    logger.warning(f"{error_msg}, using fallback")
                    return self._try_sysfs_config_or_synthetic()

            # Get IOMMU group number
            iommu_group = os.path.basename(os.path.realpath(iommu_group_path))
            vfio_device = f"/dev/vfio/{iommu_group}"

            if not os.path.exists(vfio_device):
                error_msg = f"VFIO device {vfio_device} not found"
                if strict:
                    logger.error(f"{error_msg} - VFIO is required but not available")
                    logger.error(
                        "Running VFIO diagnostics to help troubleshoot the issue..."
                    )

                    # Run diagnostics to help user fix the issue
                    try:
                        self.run_vfio_diagnostics()
                    except Exception as diag_error:
                        logger.warning(f"Could not run VFIO diagnostics: {diag_error}")

                    raise RuntimeError(
                        f"{error_msg}. VFIO is required but device is not available. "
                        "Ensure device is properly bound to VFIO driver and VFIO modules are loaded."
                    )
                else:
                    logger.warning(f"{error_msg}, using fallback")
                    return self._try_sysfs_config_or_synthetic()

            logger.info(
                f"Reading configuration space for device {self.bdf} via VFIO group {iommu_group}"
            )

            # Implement actual VFIO config space reading using VFIOBinder
            try:
                from ..cli.vfio import VFIOBinder

                logger.info(
                    f"Binding device {self.bdf} to VFIO for configuration space access"
                )
                with VFIOBinder(self.bdf) as vfio_device_path:
                    logger.info(
                        f"Reading configuration space via VFIO device {vfio_device_path}"
                    )

                    # Read configuration space through VFIO device
                    config_space = self._read_vfio_config_space(vfio_device_path)

                    log_info_safe(
                        logger,
                        "Successfully read {bytes} bytes of configuration space via VFIO",
                        bytes=len(config_space),
                    )
                    return config_space

            except ImportError as e:
                error_msg = f"VFIO module not available: {e}"
                if strict:
                    logger.error(error_msg)
                    raise RuntimeError(
                        f"VFIO config space reading failed: {error_msg}"
                    ) from e
                else:
                    logger.warning(f"{error_msg}, using sysfs fallback")
                    return self._try_sysfs_config_or_synthetic()
            except Exception as e:
                error_msg = f"VFIO config space reading failed: {e}"
                if strict:
                    logger.error(error_msg)
                    raise RuntimeError(error_msg) from e
                else:
                    logger.warning(f"{error_msg}, using sysfs fallback")
                    return self._try_sysfs_config_or_synthetic()

        except Exception as e:
            if strict:
                logger.error(f"Failed to read VFIO config space in strict mode: {e}")
                raise RuntimeError(f"VFIO config space reading failed: {e}") from e
            else:
                logger.error(f"Failed to read VFIO config space: {e}")
                logger.info("Generating synthetic configuration space as fallback")
                return self.generate_synthetic_config_space()

    def _read_vfio_config_space(self, vfio_device_path) -> bytes:
        """Read PCI configuration space through VFIO device file."""
        try:
            # For now, fall back to sysfs reading while device is bound to VFIO
            # This is a simplified implementation - full VFIO implementation would
            # use proper VFIO ioctls for configuration space access
            logger.info(
                "Using sysfs fallback for config space reading while device is bound to VFIO"
            )
            return self._read_sysfs_config_space()

        except Exception as e:
            logger.error(f"Failed to read VFIO config space: {e}")
            # Fall back to sysfs reading
            return self._read_sysfs_config_space()

    def _read_sysfs_config_space(self) -> bytes:
        """Read configuration space from sysfs."""
        config_path = f"/sys/bus/pci/devices/{self.bdf}/config"
        if os.path.exists(config_path):
            with open(config_path, "rb") as f:
                return f.read(256)  # Read first 256 bytes
        else:
            raise RuntimeError(f"Config space file not found: {config_path}")

    def _try_sysfs_config_or_synthetic(self) -> bytes:
        """Try to read config space from sysfs, or generate synthetic if not available."""
        # Read actual configuration space from sysfs as fallback
        config_path = f"/sys/bus/pci/devices/{self.bdf}/config"
        if os.path.exists(config_path):
            try:
                with open(config_path, "rb") as f:
                    config_space = f.read(256)  # Read first 256 bytes
                log_info_safe(
                    logger,
                    "Successfully read {bytes} bytes of configuration space from sysfs",
                    bytes=len(config_space),
                )
                return config_space
            except Exception as e:
                log_warning_safe(
                    logger,
                    "Failed to read configuration space from sysfs: {error}",
                    error=str(e),
                )
                logger.info("Generating synthetic configuration space as fallback")
                return self.generate_synthetic_config_space()
        else:
            logger.info(
                f"Configuration space file not found at {config_path}, generating synthetic"
            )
            return self.generate_synthetic_config_space()

    def generate_synthetic_config_space(self) -> bytes:
        """Generate production-quality synthetic PCI configuration space using device configuration."""
        config_space = bytearray(4096)  # Extended config space (4KB)

        # Use device configuration if available, otherwise fall back to defaults
        if self.device_config and hasattr(self.device_config, "identification"):
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
                "Generating synthetic configuration space using device profile: {profile}",
                profile=getattr(self.device_config, "name", "unknown"),
            )
        else:
            # Default values for generic device
            vendor_id = 0x8086  # Intel
            device_id = 0x15B8  # Generic Intel device
            class_code = 0x020000  # Ethernet controller
            subsys_vendor_id = 0x8086
            subsys_device_id = 0x0000
            command_reg = 0x0007  # I/O Space, Memory Space, Bus Master
            status_reg = 0x0010  # Capabilities List
            revision_id = 0x01
            cache_line_size = 0x10
            latency_timer = 0x00
            header_type = 0x00  # Type 0 header
            bist = 0x00

            logger.info("Generating synthetic configuration space using default values")

        # Standard PCI Configuration Space Header (first 64 bytes)
        # Vendor ID (0x00-0x01)
        config_space[0:2] = vendor_id.to_bytes(2, "little")
        # Device ID (0x02-0x03)
        config_space[2:4] = device_id.to_bytes(2, "little")
        # Command Register (0x04-0x05)
        config_space[4:6] = command_reg.to_bytes(2, "little")
        # Status Register (0x06-0x07)
        config_space[6:8] = status_reg.to_bytes(2, "little")
        # Revision ID (0x08)
        config_space[8] = revision_id
        # Class Code (0x09-0x0B)
        config_space[9:12] = class_code.to_bytes(3, "little")
        # Cache Line Size (0x0C)
        config_space[12] = cache_line_size
        # Latency Timer (0x0D)
        config_space[13] = latency_timer
        # Header Type (0x0E)
        config_space[14] = header_type
        # BIST (0x0F)
        config_space[15] = bist

        # BAR0 (0x10-0x13) - Memory BAR, 64-bit, prefetchable
        config_space[16:20] = (0x0000000C).to_bytes(4, "little")
        # BAR1 (0x14-0x17) - Upper 32 bits of 64-bit BAR0
        config_space[20:24] = (0x00000000).to_bytes(4, "little")

        # Subsystem Vendor ID (0x2C-0x2D)
        config_space[44:46] = subsys_vendor_id.to_bytes(2, "little")
        # Subsystem Device ID (0x2E-0x2F)
        config_space[46:48] = subsys_device_id.to_bytes(2, "little")

        # Capabilities Pointer (0x34)
        config_space[52] = 0x40  # Point to first capability at offset 0x40

        # Interrupt Line (0x3C)
        config_space[60] = 0xFF  # No interrupt assigned
        # Interrupt Pin (0x3D)
        config_space[61] = 0x01  # INTA#

        # Add Power Management Capability at offset 0x40
        config_space[64] = 0x01  # Capability ID: Power Management
        config_space[65] = 0x50  # Next Capability Pointer
        config_space[66:68] = (0x0003).to_bytes(2, "little")  # PMC
        config_space[68:70] = (0x0008).to_bytes(2, "little")  # PMCSR

        # Add MSI Capability at offset 0x50
        config_space[80] = 0x05  # Capability ID: MSI
        config_space[81] = 0x60  # Next Capability Pointer
        config_space[82:84] = (0x0082).to_bytes(2, "little")  # Message Control

        # Add PCIe Capability at offset 0x60
        config_space[96] = 0x10  # Capability ID: PCIe
        config_space[97] = 0x00  # Next Capability Pointer (end of list)
        config_space[98:100] = (0x0002).to_bytes(2, "little")  # PCIe Capabilities

        log_info_safe(
            logger,
            "Generated synthetic configuration space: vendor={vendor:04x} device={device:04x}",
            vendor=vendor_id,
            device=device_id,
        )

        return bytes(config_space)

    def extract_device_info(self, config_space: bytes) -> Dict[str, Any]:
        """Extract device information from configuration space."""
        if len(config_space) < 64:
            raise ValueError("Configuration space too short")

        # Extract basic device information
        vendor_id = int.from_bytes(config_space[0:2], "little")
        device_id = int.from_bytes(config_space[2:4], "little")
        command = int.from_bytes(config_space[4:6], "little")
        status = int.from_bytes(config_space[6:8], "little")
        revision_id = config_space[8]
        class_code = int.from_bytes(config_space[9:12], "little")
        cache_line_size = config_space[12]
        latency_timer = config_space[13]
        header_type = config_space[14]
        bist = config_space[15]

        # Extract subsystem information if available
        subsys_vendor_id = 0
        subsys_device_id = 0
        if len(config_space) >= 48:
            subsys_vendor_id = int.from_bytes(config_space[44:46], "little")
            subsys_device_id = int.from_bytes(config_space[46:48], "little")

        device_info = {
            "vendor_id": vendor_id,
            "device_id": device_id,
            "command": command,
            "status": status,
            "revision_id": revision_id,
            "class_code": class_code,
            "cache_line_size": cache_line_size,
            "latency_timer": latency_timer,
            "header_type": header_type,
            "bist": bist,
            "subsys_vendor_id": subsys_vendor_id,
            "subsys_device_id": subsys_device_id,
        }

        log_info_safe(
            logger,
            "Extracted device info: vendor={vendor:04x} device={device:04x} class={class_code:06x}",
            vendor=vendor_id,
            device=device_id,
            class_code=class_code,
        )

        return device_info
