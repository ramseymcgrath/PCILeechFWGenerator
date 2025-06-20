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

        logger.info(
            f"[CONFIG SPACE] Starting config space read for device {self.bdf}, strict_mode={strict}"
        )

        # Quick & dirty approach: use pure sysfs unless strict_vfio is enabled
        if strict:
            try:
                # Only attempt VFIO binding if strict mode is enabled
                from ..cli.vfio_handler import VFIOBinder

                logger.info(
                    f"[CONFIG SPACE] Binding device {self.bdf} to VFIO for configuration space access"
                )
                with VFIOBinder(self.bdf) as vfio_device_path:
                    logger.info(
                        f"[CONFIG SPACE] Successfully bound to VFIO device {vfio_device_path}"
                    )
                    logger.info(
                        f"[CONFIG SPACE] Reading configuration space via VFIO device {vfio_device_path}"
                    )

                    # TODO: Implement proper VFIO ioctl for config space access
                    # For now, we're using the sysfs method while device is bound to VFIO
                    config_space = self._read_sysfs_config_space()

                    logger.info(
                        f"[CONFIG SPACE] Successfully read {len(config_space)} bytes via VFIO"
                    )
                    logger.debug(
                        f"[CONFIG SPACE] First 64 bytes: {config_space[:64].hex()}"
                    )
                    return config_space

            except ImportError as e:
                error_msg = f"VFIO module not available: {e}"
                logger.error(f"[CONFIG SPACE] {error_msg}")
                raise RuntimeError(
                    f"VFIO config space reading failed: {error_msg}"
                ) from e

            except Exception as e:
                error_msg = f"VFIO config space reading failed: {e}"
                logger.error(f"[CONFIG SPACE] {error_msg}")

                # Run diagnostics to help user fix the issue
                try:
                    logger.info(
                        "[CONFIG SPACE] Running VFIO diagnostics to help troubleshoot..."
                    )
                    self.run_vfio_diagnostics()
                except Exception as diag_error:
                    logger.warning(
                        f"[CONFIG SPACE] Could not run VFIO diagnostics: {diag_error}"
                    )

                raise RuntimeError(f"VFIO config space reading failed: {e}") from e
        else:
            # In non-strict mode, just use sysfs directly
            try:
                logger.info(
                    f"[CONFIG SPACE] Reading configuration space for device {self.bdf} via sysfs (non-strict mode)"
                )
                config_space = self._read_sysfs_config_space()
                logger.info(
                    f"[CONFIG SPACE] Successfully read {len(config_space)} bytes via sysfs"
                )
                logger.debug(
                    f"[CONFIG SPACE] First 64 bytes: {config_space[:64].hex()}"
                )
                return config_space
            except Exception as e:
                logger.error(f"[CONFIG SPACE] Failed to read sysfs config space: {e}")
                # Do not automatically fallback to synthetic - let the caller handle this
                raise RuntimeError(
                    f"Failed to read configuration space via sysfs: {e}"
                ) from e

    # _read_vfio_config_space method removed as part of VFIO/sysfs strategy simplification

    def _read_sysfs_config_space(self) -> bytes:
        """Read configuration space from sysfs."""
        config_path = f"/sys/bus/pci/devices/{self.bdf}/config"
        logger.info(
            f"[CONFIG SPACE] Attempting to read config space from {config_path}"
        )

        if os.path.exists(config_path):
            logger.info(f"[CONFIG SPACE] Config space file exists: {config_path}")
            try:
                with open(config_path, "rb") as f:
                    # Read 4096 bytes (full extended configuration space) instead of just 256 bytes
                    # This ensures we capture MSI-X capabilities that may be in extended space
                    logger.debug(
                        "[CONFIG SPACE] Reading up to 4096 bytes for extended config space"
                    )
                    data = f.read(4096)
                    logger.info(
                        f"[CONFIG SPACE] Successfully read {len(data)} bytes from sysfs"
                    )

                    # Check if we got at least the minimum required size
                    if len(data) < 256:
                        logger.warning(
                            f"[CONFIG SPACE] Only read {len(data)} bytes from config space, minimum required is 256"
                        )

                        # Create a new buffer with at least 256 bytes
                        extended_data = bytearray(data)
                        # Extend to at least 256 bytes
                        if len(extended_data) < 256:
                            padding_bytes = 256 - len(extended_data)
                            logger.warning(
                                f"[CONFIG SPACE] Padding config space with {padding_bytes} zero bytes"
                            )
                            extended_data.extend(bytes(padding_bytes))

                        # Ensure revision_id is set (at offset 8)
                        if len(data) <= 8 or extended_data[8] == 0:
                            logger.warning(
                                "[CONFIG SPACE] Revision ID is missing or zero, setting default value 0x01"
                            )
                            extended_data[8] = 0x01

                        logger.info(
                            f"[CONFIG SPACE] Extended config space to {len(extended_data)} bytes"
                        )
                        return bytes(extended_data)

                    # Log basic header info for debugging
                    if len(data) >= 16:
                        vendor_id = int.from_bytes(data[0:2], "little")
                        device_id = int.from_bytes(data[2:4], "little")
                        logger.info(
                            f"[CONFIG SPACE] Read config space for device {vendor_id:04x}:{device_id:04x}"
                        )
                        logger.debug(
                            f"[CONFIG SPACE] Header bytes 0-15: {data[:16].hex()}"
                        )

                    return data
            except PermissionError:
                logger.warning(
                    "[CONFIG SPACE] Permission denied when reading config space, trying alternative method"
                )
                # Try using sudo to read the file
                try:
                    import subprocess

                    logger.info(
                        "[CONFIG SPACE] Attempting to read config space using sudo hexdump"
                    )
                    result = subprocess.run(
                        ["sudo", "hexdump", "-C", config_path],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    # Parse hexdump output to reconstruct binary data
                    hex_data = result.stdout
                    logger.debug(
                        f"[CONFIG SPACE] Hexdump output length: {len(hex_data)} characters"
                    )

                    # Create a buffer of at least 256 bytes
                    data = bytearray(256)
                    bytes_parsed = 0

                    # Parse hexdump output and fill the buffer
                    for line_num, line in enumerate(hex_data.splitlines()):
                        if "|" not in line:
                            continue
                        parts = line.split("|")[0].strip().split()
                        if not parts or not parts[0].endswith(":"):
                            continue

                        try:
                            offset = int(parts[0][:-1], 16)
                            hex_values = parts[1:17]  # Up to 16 hex values per line

                            for i, hex_val in enumerate(hex_values):
                                if offset + i < len(data):
                                    data[offset + i] = int(hex_val, 16)
                                    bytes_parsed += 1
                        except (ValueError, IndexError) as e:
                            logger.warning(
                                f"[CONFIG SPACE] Error parsing hexdump line {line_num}: {e}"
                            )
                            continue

                    logger.info(
                        f"[CONFIG SPACE] Parsed {bytes_parsed} bytes from hexdump output"
                    )

                    # Ensure revision_id is set
                    if data[8] == 0:
                        logger.warning(
                            "[CONFIG SPACE] Setting default revision ID 0x01"
                        )
                        data[8] = 0x01

                    # Log basic header info
                    vendor_id = int.from_bytes(data[0:2], "little")
                    device_id = int.from_bytes(data[2:4], "little")
                    logger.info(
                        f"[CONFIG SPACE] Parsed config space for device {vendor_id:04x}:{device_id:04x}"
                    )

                    return bytes(data)
                except Exception as e:
                    logger.error(f"[CONFIG SPACE] Alternative method failed: {e}")
                    raise
        else:
            logger.error(f"[CONFIG SPACE] Config space file not found: {config_path}")
            raise RuntimeError(f"Config space file not found: {config_path}")

    # _try_sysfs_config_or_synthetic method removed as part of VFIO/sysfs strategy simplification

    def generate_synthetic_config_space(self) -> bytes:
        """Generate production-quality synthetic PCI configuration space using device configuration."""
        # Create a new configuration space (4096 bytes for extended config space)
        config_space = bytearray(4096)

        # Require device configuration - no hardcoded defaults
        if not self.device_config:
            raise RuntimeError(
                "Cannot generate synthetic configuration space without device configuration. "
                "Device configuration is required to ensure proper device identity."
            )

        # Use device configuration - fail if not available
        try:
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
        except (AttributeError, TypeError) as e:
            raise RuntimeError(
                f"Device configuration is incomplete or invalid: {e}. "
                "Cannot generate synthetic configuration space without complete device data."
            ) from e

        # Write basic header fields
        config_space[0:2] = vendor_id.to_bytes(2, "little")
        config_space[2:4] = device_id.to_bytes(2, "little")
        config_space[4:6] = command_reg.to_bytes(2, "little")
        config_space[6:8] = status_reg.to_bytes(2, "little")
        config_space[8] = revision_id
        config_space[9:12] = class_code.to_bytes(3, "little")
        config_space[12] = cache_line_size
        config_space[13] = latency_timer
        config_space[14] = header_type
        config_space[15] = bist

        # Set BAR registers to 0 (not implemented in this synthetic config)
        for i in range(6):
            bar_offset = 16 + (i * 4)
            config_space[bar_offset : bar_offset + 4] = (0).to_bytes(4, "little")

        # Set subsystem vendor and device ID
        config_space[44:46] = subsys_vendor_id.to_bytes(2, "little")
        config_space[46:48] = subsys_device_id.to_bytes(2, "little")

        # Set capabilities pointer (first capability at offset 0x40)
        config_space[52] = 0x40

        # Add MSI-X capability at offset 0x40
        config_space[64] = 0x11  # Capability ID for MSI-X
        config_space[65] = 0x00  # Next capability pointer (none)
        config_space[66] = 0x00  # MSI-X control register (16-bit)
        config_space[67] = 0x80  # MSI-X enabled, function masked
        # Message Control: 32 table entries (5 bits, 0-based)
        table_size = 31  # 32 entries (0-based)
        config_space[66:68] = (table_size | (0 << 7)).to_bytes(2, "little")
        # Table Offset/BIR: BAR 0 (BIR = 0), offset 0x1000
        table_offset_bir = 0x00001000 | 0x0  # BAR 0 (BIR = 0)
        config_space[68:72] = table_offset_bir.to_bytes(4, "little")
        # PBA Offset/BIR: BAR 0 (BIR = 0), offset 0x2000
        pba_offset_bir = 0x00002000 | 0x0  # BAR 0 (BIR = 0)
        config_space[72:76] = pba_offset_bir.to_bytes(4, "little")

        # Add MSI capability at offset 0x50
        config_space[80] = 0x05  # Capability ID for MSI
        config_space[81] = 0x40  # Next capability pointer (points to MSI-X)
        config_space[82] = 0x00  # MSI control register (16-bit)
        config_space[83] = 0x00  # MSI disabled

        # Add PCIe capability at offset 0x60
        config_space[96] = 0x10  # Capability ID for PCIe
        config_space[97] = 0x50  # Next capability pointer (points to MSI)
        config_space[98] = 0x02  # PCIe capability version 2
        config_space[99] = 0x00  # Device/port type (endpoint)

        # Add MSI-X table structure at offset 0x100 (extended config space)
        # This is just a placeholder - the actual table would be in BAR memory
        for i in range(32):  # 32 MSI-X table entries
            entry_offset = 0x100 + (i * 16)
            # Message Address (lower 32 bits)
            config_space[entry_offset : entry_offset + 4] = (0).to_bytes(4, "little")
            # Message Address (upper 32 bits)
            config_space[entry_offset + 4 : entry_offset + 8] = (0).to_bytes(
                4, "little"
            )
            # Message Data
            config_space[entry_offset + 8 : entry_offset + 12] = (0).to_bytes(
                4, "little"
            )
            # Vector Control
            config_space[entry_offset + 12 : entry_offset + 16] = (1).to_bytes(
                4, "little"
            )  # Masked

        # Add MSI-X capability at offset 0x40
        config_space[64] = 0x11  # Capability ID for MSI-X
        config_space[65] = 0x50  # Next capability pointer (points to MSI)
        # Message Control: 32 table entries (5 bits, 0-based)
        table_size = 31  # 32 entries (0-based)
        config_space[66:68] = (table_size | (0 << 7)).to_bytes(2, "little")
        # Table Offset/BIR: BAR 0 (BIR = 0), offset 0x1000
        table_offset_bir = 0x00001000 | 0x0  # BAR 0 (BIR = 0)
        config_space[68:72] = table_offset_bir.to_bytes(4, "little")
        # PBA Offset/BIR: BAR 0 (BIR = 0), offset 0x2000
        pba_offset_bir = 0x00002000 | 0x0  # BAR 0 (BIR = 0)
        config_space[72:76] = pba_offset_bir.to_bytes(4, "little")

        log_info_safe(
            logger,
            "Generated synthetic configuration space: vendor={vendor:04x} device={device:04x}",
            vendor=vendor_id,
            device=device_id,
        )

        return bytes(config_space)

    def extract_device_info(self, config_space: bytes) -> Dict[str, Any]:
        """Extract device information from configuration space."""
        if len(config_space) < 16:
            raise ValueError(
                "Configuration space too short - need at least 16 bytes for basic header"
            )

        # Extract basic device information - no defaults, fail if data is insufficient
        vendor_id = int.from_bytes(config_space[0:2], "little")
        device_id = int.from_bytes(config_space[2:4], "little")
        command = int.from_bytes(config_space[4:6], "little")
        status = int.from_bytes(config_space[6:8], "little")

        if len(config_space) <= 8:
            raise ValueError(
                "Configuration space too short - missing revision_id at offset 8"
            )
        revision_id = config_space[8]

        if len(config_space) < 12:
            raise ValueError(
                "Configuration space too short - missing class_code at offset 9-11"
            )
        class_code = int.from_bytes(config_space[9:12], "little")

        if len(config_space) < 16:
            raise ValueError("Configuration space too short - missing header fields")
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

        # Extract BAR information with verbose logging
        bars = []
        logger.info(
            f"[BAR EXTRACTION] Starting BAR extraction from config space ({len(config_space)} bytes)"
        )

        if len(config_space) >= 40:  # Ensure we have enough bytes to read BARs
            logger.info(
                "[BAR EXTRACTION] Config space has sufficient length for BAR reading"
            )
            i = 0
            while i < 6:  # PCI has up to 6 BARs
                try:
                    bar_offset = 16 + (i * 4)  # BARs start at offset 0x10
                    logger.debug(
                        f"[BAR EXTRACTION] Processing BAR {i} at offset 0x{bar_offset:02x}"
                    )

                    if bar_offset + 4 <= len(config_space):
                        bar_value = int.from_bytes(
                            config_space[bar_offset : bar_offset + 4], "little"
                        )
                        logger.debug(
                            f"[BAR EXTRACTION] BAR {i} raw value: 0x{bar_value:08x}"
                        )

                        if bar_value != 0:  # Only include non-zero BARs
                            logger.info(
                                f"[BAR EXTRACTION] BAR {i} is active (non-zero): 0x{bar_value:08x}"
                            )

                            # Decode BAR type and properties
                            bar_type = "io" if (bar_value & 0x1) else "memory"
                            bar_prefetchable = (
                                bool(bar_value & 0x8) if bar_type == "memory" else False
                            )
                            bar_64bit = (
                                ((bar_value & 0x6) == 0x4)
                                if bar_type == "memory"
                                else False
                            )

                            logger.info(
                                f"[BAR EXTRACTION] BAR {i} properties: type={bar_type}, prefetchable={bar_prefetchable}, 64bit={bar_64bit}"
                            )

                            # Calculate base address
                            bar_addr = (
                                bar_value & ~0xF
                                if bar_type == "memory"
                                else bar_value & ~0x3
                            )
                            logger.debug(
                                f"[BAR EXTRACTION] BAR {i} base address (lower 32-bit): 0x{bar_addr:08x}"
                            )

                            # For 64-bit BARs, we need to read the next BAR as well
                            if bar_64bit and i < 5:  # Ensure we can read the next BAR
                                next_bar_offset = bar_offset + 4
                                logger.debug(
                                    f"[BAR EXTRACTION] Reading upper 32-bit for 64-bit BAR {i} at offset 0x{next_bar_offset:02x}"
                                )

                                if next_bar_offset + 4 <= len(config_space):
                                    next_bar_value = int.from_bytes(
                                        config_space[
                                            next_bar_offset : next_bar_offset + 4
                                        ],
                                        "little",
                                    )
                                    logger.debug(
                                        f"[BAR EXTRACTION] BAR {i} upper 32-bit value: 0x{next_bar_value:08x}"
                                    )
                                    bar_addr |= next_bar_value << 32
                                    logger.info(
                                        f"[BAR EXTRACTION] BAR {i} full 64-bit address: 0x{bar_addr:016x}"
                                    )
                                else:
                                    logger.warning(
                                        f"[BAR EXTRACTION] Cannot read upper 32-bit for BAR {i} - insufficient config space"
                                    )

                            bar_info = {
                                "index": i,
                                "type": bar_type,
                                "address": bar_addr,
                                "size": 0,  # Size would need to be determined by probing
                                "prefetchable": bar_prefetchable,
                                "is_64bit": bar_64bit,
                            }

                            bars.append(bar_info)
                            logger.info(f"[BAR EXTRACTION] Added BAR {i}: {bar_info}")

                            # Skip the next BAR if this was a 64-bit BAR
                            if bar_64bit:
                                logger.debug(
                                    f"[BAR EXTRACTION] Skipping BAR {i+1} (upper half of 64-bit BAR {i})"
                                )
                                i += 2  # Properly consume next BAR for 64-bit BAR
                            else:
                                i += 1
                        else:
                            logger.debug(
                                f"[BAR EXTRACTION] BAR {i} is empty (zero value), skipping"
                            )
                            i += 1  # Skip zero-valued BARs
                    else:
                        logger.warning(
                            f"[BAR EXTRACTION] Cannot read BAR {i} - insufficient config space length"
                        )
                        i += 1  # Skip if we can't read the full BAR
                except (IndexError, ValueError, KeyboardInterrupt) as e:
                    # Handle KeyboardInterrupt and other errors gracefully
                    if isinstance(e, KeyboardInterrupt):
                        logger.warning(
                            "[BAR EXTRACTION] BAR extraction interrupted by user"
                        )
                        raise  # Re-raise KeyboardInterrupt to allow proper cleanup
                    logger.warning(f"[BAR EXTRACTION] Error processing BAR {i}: {e}")
                    # Skip this BAR and continue with the next one
                    i += 1
        else:
            logger.warning(
                f"[BAR EXTRACTION] Config space too short ({len(config_space)} bytes) for BAR extraction - need at least 40 bytes"
            )

        logger.info(
            f"[BAR EXTRACTION] Completed BAR extraction: found {len(bars)} active BARs"
        )
        for bar in bars:
            logger.info(
                f"[BAR EXTRACTION] BAR {bar['index']}: {bar['type']} @ 0x{bar['address']:016x} ({'64-bit' if bar['is_64bit'] else '32-bit'}, {'prefetchable' if bar['prefetchable'] else 'non-prefetchable'})"
            )

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
            "bars": bars,
        }

        # Enhanced device info logging
        logger.info(f"[DEVICE INFO] Successfully extracted device information:")
        logger.info(f"[DEVICE INFO]   Vendor ID: 0x{vendor_id:04x}")
        logger.info(f"[DEVICE INFO]   Device ID: 0x{device_id:04x}")
        logger.info(f"[DEVICE INFO]   Class Code: 0x{class_code:06x}")
        logger.info(f"[DEVICE INFO]   Revision ID: 0x{revision_id:02x}")
        logger.info(f"[DEVICE INFO]   Command: 0x{command:04x}")
        logger.info(f"[DEVICE INFO]   Status: 0x{status:04x}")
        logger.info(f"[DEVICE INFO]   Header Type: 0x{header_type:02x}")
        logger.info(f"[DEVICE INFO]   Subsystem Vendor: 0x{subsys_vendor_id:04x}")
        logger.info(f"[DEVICE INFO]   Subsystem Device: 0x{subsys_device_id:04x}")
        logger.info(f"[DEVICE INFO]   Cache Line Size: {cache_line_size}")
        logger.info(f"[DEVICE INFO]   Latency Timer: {latency_timer}")
        logger.info(f"[DEVICE INFO]   BIST: 0x{bist:02x}")
        logger.info(f"[DEVICE INFO]   Total BARs found: {len(bars)}")

        # Log detailed BAR summary
        if bars:
            logger.info("[DEVICE INFO] BAR Summary:")
            for bar in bars:
                logger.info(
                    f"[DEVICE INFO]   BAR {bar['index']}: {bar['type']} @ 0x{bar['address']:016x} ({'64-bit' if bar['is_64bit'] else '32-bit'}, {'prefetchable' if bar['prefetchable'] else 'non-prefetchable'})"
                )
        else:
            logger.info("[DEVICE INFO] No active BARs found")

        log_info_safe(
            logger,
            "Extracted device info: vendor={vendor:04x} device={device:04x} class={class_code:06x}",
            vendor=vendor_id,
            device=device_id,
            class_code=class_code,
        )

        return device_info
