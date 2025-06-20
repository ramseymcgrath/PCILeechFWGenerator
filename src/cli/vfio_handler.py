#!/usr/bin/env python3
"""VFIO handler - strict, no-nonsense VFIO binding with context management."""

from __future__ import annotations

import ctypes
import fcntl
import io
import json
import logging
import os
import re
import struct
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Optional

# Import vfio_assist with fallback for missing module
try:
    import vfio_assist
except ImportError:
    # Create minimal stubs if vfio_assist is not available
    class _MockVfioAssist:
        class Diagnostics:
            def __init__(self, *args, **kwargs):
                pass

            def run(self):
                from dataclasses import dataclass, field

                @dataclass
                class _Result:
                    overall: str = "ok"
                    can_proceed: bool = True
                    checks: list = field(default_factory=list)

                return _Result()

    vfio_assist = _MockVfioAssist()

# Import proper VFIO constants with kernel-compatible ioctl generation
from .vfio_constants import (
    VFIO_DEVICE_GET_REGION_INFO,
    VFIO_GROUP_GET_DEVICE_FD,
    VFIO_GROUP_GET_STATUS,
    VFIO_REGION_INFO_FLAG_READ,
    VFIO_REGION_INFO_FLAG_WRITE,
    VFIO_REGION_INFO_FLAG_MMAP,
    vfio_region_info,
    vfio_group_status,
    VfioRegionInfo,  # legacy alias
    VfioGroupStatus,  # legacy alias
)
from .vfio_helpers import get_device_fd

# Import safe logging functions
try:
    from ..string_utils import (
        log_info_safe,
        log_error_safe,
        log_warning_safe,
        log_debug_safe,
    )
except ImportError:
    # Fallback implementations
    def log_info_safe(logger, template, **kwargs):
        logger.info(template.format(**kwargs))

    def log_error_safe(logger, template, **kwargs):
        logger.error(template.format(**kwargs))

    def log_warning_safe(logger, template, **kwargs):
        logger.warning(template.format(**kwargs))

    def log_debug_safe(logger, template, **kwargs):
        logger.debug(template.format(**kwargs))


# Configure global logger
logger = logging.getLogger(__name__)

# kernel struct vfio_region_info layout (32 bytes on all archs)
_FMT = "I I I I Q Q"  # argsz, flags, index, cap_off, size, offset
_STRUCT_SIZE = struct.calcsize(_FMT)


class VFIOBindError(Exception):
    """Raised when VFIO binding fails."""

    pass


class VFIOBinderImpl:
    """Context manager for VFIO device binding with strict error handling."""

    # BDF validation regex: 1-4 hex digits for domain
    BDF_PATTERN = re.compile(r"^[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}\.[0-7]$")

    def __init__(self, bdf: str) -> None:
        """Initialize VFIO binder for the specified BDF.

        Args:
            bdf: PCI Bus:Device.Function identifier

        Raises:
            ValueError: If BDF format is invalid
            PermissionError: If not running as root
        """
        if os.geteuid() != 0:
            raise PermissionError("VFIO operations require root privileges")

        if not self.BDF_PATTERN.match(bdf):
            raise ValueError(f"Invalid BDF format: {bdf}")

        self.bdf = bdf
        self.original_driver: Optional[str] = None
        self.group_id: Optional[str] = None
        self._bound = False

    def _get_current_driver(self) -> Optional[str]:
        """Get the current driver for the device."""
        driver_link = Path(f"/sys/bus/pci/devices/{self.bdf}/driver")
        if driver_link.exists():
            return driver_link.resolve().name
        return None

    def _get_iommu_group(self) -> str:
        """Get the IOMMU group for the device."""
        group_link = Path(f"/sys/bus/pci/devices/{self.bdf}/iommu_group")
        if not group_link.exists():
            raise VFIOBindError(f"No IOMMU group found for device {self.bdf}")
        return group_link.resolve().name

    def _write_sysfs(self, path: Path, value: str) -> None:
        """Write to sysfs file with root privilege check."""
        if os.geteuid() != 0:
            raise PermissionError("Root privileges required for sysfs write")
        try:
            path.write_text(value)
        except OSError as e:
            raise VFIOBindError(f"Failed to write '{value}' to {path}: {e}") from e

    def _bind_to_vfio(self) -> None:
        """Bind device to vfio-pci using driver_override workflow."""
        log_info_safe(
            logger,
            "[VFIO BIND] Starting VFIO binding process for device {bdf}",
            bdf=self.bdf,
        )

        # Check if already bound
        current_driver = self._get_current_driver()
        log_info_safe(
            logger,
            "[VFIO BIND] Current driver for {bdf}: {current_driver}",
            bdf=self.bdf,
            current_driver=current_driver or "none",
        )

        if current_driver == "vfio-pci":
            log_info_safe(
                logger,
                "[VFIO BIND] Device {bdf} already bound to vfio-pci",
                bdf=self.bdf,
            )
            # Verify the binding is actually working by checking IOMMU group
            self._verify_vfio_binding()
            return

        # Store original driver for cleanup
        self.original_driver = current_driver
        log_info_safe(
            logger,
            "[VFIO BIND] Stored original driver '{original_driver}' for restoration",
            original_driver=self.original_driver,
        )

        # If device has a current driver, unbind it first
        if current_driver:
            log_info_safe(
                logger,
                "[VFIO BIND] Unbinding device from current driver {current_driver}",
                current_driver=current_driver,
            )
            try:
                unbind_path = Path(f"/sys/bus/pci/drivers/{current_driver}/unbind")
                if unbind_path.exists():
                    self._write_sysfs(unbind_path, self.bdf)
                    log_debug_safe(
                        logger,
                        "[VFIO BIND] Successfully unbound from {current_driver}",
                        current_driver=current_driver,
                    )

                    # Wait for unbinding to complete
                    import time

                    time.sleep(0.2)
            except Exception as e:
                log_warning_safe(
                    logger,
                    "[VFIO BIND] Failed to unbind from {current_driver}: {error}",
                    current_driver=current_driver,
                    error=str(e),
                )

        # Use driver_override workflow exclusively
        device_path = Path(f"/sys/bus/pci/devices/{self.bdf}")
        driver_override_path = device_path / "driver_override"
        vfio_bind_path = Path("/sys/bus/pci/drivers/vfio-pci/bind")

        log_debug_safe(
            logger, "[VFIO BIND] Device path: {device_path}", device_path=device_path
        )
        log_debug_safe(
            logger,
            "[VFIO BIND] Driver override path: {driver_override_path}",
            driver_override_path=driver_override_path,
        )
        log_debug_safe(
            logger,
            "[VFIO BIND] VFIO bind path: {vfio_bind_path}",
            vfio_bind_path=vfio_bind_path,
        )

        # Set driver override
        log_info_safe(
            logger,
            "[VFIO BIND] Setting driver override to 'vfio-pci' for {bdf}",
            bdf=self.bdf,
        )
        self._write_sysfs(driver_override_path, "vfio-pci")
        log_debug_safe(logger, "[VFIO BIND] Successfully wrote driver override")

        # Bind to vfio-pci
        log_info_safe(
            logger, "[VFIO BIND] Binding {bdf} to vfio-pci driver", bdf=self.bdf
        )
        self._write_sysfs(vfio_bind_path, self.bdf)
        log_debug_safe(logger, "[VFIO BIND] Successfully wrote to vfio-pci bind file")

        # Wait for binding to complete
        import time

        time.sleep(0.5)

        # Verify binding
        new_driver = self._get_current_driver()
        log_info_safe(
            logger,
            "[VFIO BIND] Verifying binding - new driver: {new_driver}",
            new_driver=new_driver,
        )

        if new_driver != "vfio-pci":
            log_error_safe(
                logger,
                "[VFIO BIND] Binding verification failed - expected 'vfio-pci', got '{new_driver}'",
                new_driver=new_driver,
            )
            raise VFIOBindError(f"Failed to bind {self.bdf} to vfio-pci")

        # Additional verification that VFIO binding is functional
        self._verify_vfio_binding()

        self._bound = True
        log_info_safe(
            logger, "[VFIO BIND] Successfully bound {bdf} to vfio-pci", bdf=self.bdf
        )

    def _verify_vfio_binding(self) -> None:
        """Verify that VFIO binding is functional."""
        log_debug_safe(
            logger,
            "[VFIO BIND] Verifying VFIO binding functionality for {bdf}",
            bdf=self.bdf,
        )

        # Check IOMMU group exists and is accessible
        try:
            group_id = self._get_iommu_group()
            group_path = Path(f"/dev/vfio/{group_id}")

            if not group_path.exists():
                raise VFIOBindError(f"VFIO group device {group_path} does not exist")

            # Try to open the group device to verify it's accessible
            try:
                # Use os.open() for character devices instead of open() to avoid seekability issues
                test_fd = os.open(group_path, os.O_RDWR)
                os.close(test_fd)
                log_debug_safe(
                    logger,
                    "[VFIO BIND] Successfully opened VFIO group device {group_path}",
                    group_path=group_path,
                )
            except PermissionError:
                raise VFIOBindError(
                    f"Permission denied accessing VFIO group {group_path} - check permissions or run as root"
                )
            except (OSError, io.UnsupportedOperation) as e:
                raise VFIOBindError(f"Failed to access VFIO group {group_path}: {e}")

        except Exception as e:
            log_error_safe(
                logger,
                "[VFIO BIND] VFIO binding verification failed: {error}",
                error=str(e),
            )
            raise VFIOBindError(f"VFIO binding verification failed for {self.bdf}: {e}")

        log_debug_safe(
            logger,
            "[VFIO BIND] VFIO binding verification successful for {bdf}",
            bdf=self.bdf,
        )

    def _wait_for_group_node(self) -> Path:
        """Wait for VFIO group node with exponential backoff."""
        group_path = Path(f"/dev/vfio/{self.group_id}")

        # Exponential backoff: 0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4s (total ~12.7s)
        delay = 0.1
        total_time = 0.0
        max_time = 10.0

        while total_time < max_time:
            if group_path.exists():
                return group_path

            log_debug_safe(
                logger,
                "Waiting for {group_path} ({total_time:.1f}s elapsed)",
                group_path=group_path,
                total_time=total_time,
            )
            time.sleep(delay)
            total_time += delay
            delay = min(delay * 2, 3.2)  # Cap at 3.2s

        raise VFIOBindError(
            f"VFIO group node {group_path} did not appear within {max_time}s"
        )

    def _cleanup(self) -> None:
        """Clean up VFIO binding and restore original driver."""
        if not self._bound:
            return

        device_path = Path(f"/sys/bus/pci/devices/{self.bdf}")

        # Check if device still exists
        if not device_path.exists():
            log_debug_safe(
                logger, "Device {bdf} no longer exists, skipping cleanup", bdf=self.bdf
            )
            return

        try:
            # Only unbind if still bound to vfio-pci
            current_driver = self._get_current_driver()
            if current_driver == "vfio-pci":
                unbind_path = Path("/sys/bus/pci/drivers/vfio-pci/unbind")
                self._write_sysfs(unbind_path, self.bdf)
                log_debug_safe(logger, "Unbound {bdf} from vfio-pci", bdf=self.bdf)

                # Restore original driver if it existed
                if self.original_driver:
                    bind_path = Path(
                        f"/sys/bus/pci/drivers/{self.original_driver}/bind"
                    )
                    if bind_path.exists():
                        self._write_sysfs(bind_path, self.bdf)
                        log_debug_safe(
                            logger,
                            "Restored {bdf} to {original_driver}",
                            bdf=self.bdf,
                            original_driver=self.original_driver,
                        )

            # Clear driver override
            driver_override_path = device_path / "driver_override"
            if driver_override_path.exists():
                self._write_sysfs(driver_override_path, "")
                log_debug_safe(
                    logger, "Cleared driver_override for {bdf}", bdf=self.bdf
                )

        except Exception as e:
            # Only ignore errors if device node is gone
            if device_path.exists():
                log_warning_safe(
                    logger,
                    "Cleanup failed for {bdf}: {error}",
                    bdf=self.bdf,
                    error=str(e),
                )
            else:
                log_debug_safe(
                    logger, "Device {bdf} removed during cleanup", bdf=self.bdf
                )

    def _get_vfio_group(self) -> Optional[str]:
        """Get the VFIO group ID for this device."""
        return self.group_id

    def _open_vfio_device_fd(self) -> tuple[int, int]:
        """Open the device FD using the complete VFIO workflow.

        Returns:
            Tuple of (device_fd, container_fd). Both must be closed when done.
        """
        try:
            return get_device_fd(self.bdf)
        except OSError as e:
            if e.errno == 22:  # EINVAL
                log_error_safe(
                    logger,
                    "VFIO device FD opening failed with EINVAL for {bdf}",
                    bdf=self.bdf,
                )
                log_error_safe(logger, "This usually indicates:")
                log_error_safe(logger, "1. Device not properly bound to vfio-pci")
                log_error_safe(logger, "2. IOMMU group configuration issue")
                log_error_safe(logger, "3. Device already in use by another process")
                log_error_safe(logger, "4. Insufficient permissions")

                # Try to rebind the device
                log_info_safe(
                    logger,
                    "Attempting to rebind device {bdf} to vfio-pci",
                    bdf=self.bdf,
                )
                try:
                    self._bind_to_vfio()
                    # Wait a moment for the binding to take effect
                    import time

                    time.sleep(0.5)
                    return get_device_fd(self.bdf)
                except Exception as rebind_error:
                    log_error_safe(
                        logger, "Rebinding failed: {error}", error=str(rebind_error)
                    )
                    raise e
            else:
                raise e

    def _get_vfio_region_info(self, region_index: int) -> Optional[Dict[str, Any]]:
        """Get VFIO region information for the specified region index.

        Args:
            region_index: The region index to query

        Returns:
            Dictionary containing region information or None if failed
        """
        log_info_safe(
            logger,
            "[VFIO BAR] Getting region info for device {bdf}, region {region_index}",
            bdf=self.bdf,
            region_index=region_index,
        )

        try:
            log_debug_safe(
                logger, "[VFIO BAR] Opening VFIO device FD for {bdf}", bdf=self.bdf
            )
            dev_fd, cont_fd = self._open_vfio_device_fd()
            log_debug_safe(
                logger,
                "[VFIO BAR] Successfully opened device FD: {dev_fd}, container FD: {cont_fd}",
                dev_fd=dev_fd,
                cont_fd=cont_fd,
            )
        except OSError as e:
            log_error_safe(
                logger,
                "[VFIO BAR] Failed to open VFIO device FD for {bdf}: {error}",
                bdf=self.bdf,
                error=str(e),
            )
            return None

        try:
            log_debug_safe(
                logger,
                "[VFIO BAR] Preparing VFIO region info structure for region {region_index}",
                region_index=region_index,
            )
            info = vfio_region_info()
            info.argsz = ctypes.sizeof(vfio_region_info)
            info.index = region_index

            log_debug_safe(
                logger,
                "[VFIO BAR] Calling VFIO_DEVICE_GET_REGION_INFO ioctl for region {region_index}",
                region_index=region_index,
            )

            # mutate=True lets the kernel write back size/flags
            fcntl.ioctl(dev_fd, VFIO_DEVICE_GET_REGION_INFO, info, True)

            log_info_safe(
                logger,
                "[VFIO BAR] Successfully retrieved region {region_index} info:",
                region_index=region_index,
            )
            log_info_safe(logger, "[VFIO BAR]   Index: {index}", index=info.index)
            log_info_safe(logger, "[VFIO BAR]   Flags: 0x{flags:08x}", flags=info.flags)
            log_info_safe(
                logger,
                "[VFIO BAR]   Size: 0x{size:016x} ({size} bytes)",
                size=info.size,
            )

            # Decode flags for better understanding
            readable = bool(info.flags & VFIO_REGION_INFO_FLAG_READ)
            writable = bool(info.flags & VFIO_REGION_INFO_FLAG_WRITE)
            mappable = bool(info.flags & VFIO_REGION_INFO_FLAG_MMAP)

            log_info_safe(
                logger, "[VFIO BAR]   Readable: {readable}", readable=readable
            )
            log_info_safe(
                logger, "[VFIO BAR]   Writable: {writable}", writable=writable
            )
            log_info_safe(
                logger, "[VFIO BAR]   Mappable: {mappable}", mappable=mappable
            )

            if info.size == 0:
                log_warning_safe(
                    logger,
                    "[VFIO BAR] Region {region_index} has zero size - may be inactive",
                    region_index=region_index,
                )

            if not (readable or writable):
                log_warning_safe(
                    logger,
                    "[VFIO BAR] Region {region_index} is neither readable nor writable",
                    region_index=region_index,
                )

            region_info = {
                "index": info.index,
                "flags": info.flags,
                "size": info.size,
                "readable": readable,
                "writable": writable,
                "mappable": mappable,
            }

            log_debug_safe(
                logger,
                "[VFIO BAR] Returning region info: {region_info}",
                region_info=region_info,
            )
            return region_info

        except OSError as e:
            log_error_safe(
                logger,
                "[VFIO BAR] VFIO_DEVICE_GET_REGION_INFO ioctl failed for region {region_index}: {error}",
                region_index=region_index,
                error=str(e),
            )
            return None
        except Exception as e:
            log_error_safe(
                logger,
                "[VFIO BAR] Unexpected error getting region {region_index} info: {error}",
                region_index=region_index,
                error=str(e),
            )
            return None
        finally:
            log_debug_safe(
                logger,
                "[VFIO BAR] Closing device FD {dev_fd} and container FD {cont_fd}",
                dev_fd=dev_fd,
                cont_fd=cont_fd,
            )
            try:
                os.close(dev_fd)
            except OSError:
                pass  # Already closed
            try:
                os.close(cont_fd)
            except OSError:
                pass  # Already closed

    def rebind(self) -> None:
        """Manually rebind the device to vfio-pci."""
        if not self._bound:
            self._bind_to_vfio()

    def close(self) -> None:
        """Manually close and cleanup the binding."""
        self._cleanup()
        self._bound = False

    def __enter__(self) -> Path:
        """Enter context manager and return VFIO group device path."""
        # Get IOMMU group
        self.group_id = self._get_iommu_group()

        # Bind to VFIO
        self._bind_to_vfio()

        # Wait for group node and return it
        return self._wait_for_group_node()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and cleanup."""
        self._cleanup()


@contextmanager
def VFIOBinder(bdf: str) -> Generator[Path, None, None]:
    """Context manager that yields the VFIO group device path.

    Args:
        bdf: PCI Bus:Device.Function identifier

    Yields:
        Path to the VFIO group device node (/dev/vfio/<group>)

    Raises:
        ValueError: If BDF format is invalid
        PermissionError: If not running as root
        VFIOBindError: If binding fails
    """
    binder = VFIOBinderImpl(bdf)
    with binder as group_path:
        yield group_path


def run_diagnostics(bdf: Optional[str] = None) -> Dict[str, Any]:
    """Run VFIO diagnostics and return structured results.

    Args:
        bdf: Optional BDF to check specific device

    Returns:
        Dictionary containing diagnostic results
    """
    try:
        diagnostics = vfio_assist.Diagnostics(bdf)
        result = diagnostics.run()

        # Convert to dictionary for JSON serialization
        return {
            "overall": result.overall,
            "can_proceed": result.can_proceed,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status,
                    "message": check.message,
                    "details": getattr(check, "details", None),
                }
                for check in result.checks
            ],
        }
    except Exception as e:
        return {"overall": "error", "can_proceed": False, "checks": [], "error": str(e)}


def render_pretty(diagnostic_result: Dict[str, Any]) -> str:
    """Render diagnostic results with ANSI colors for display.

    Args:
        diagnostic_result: Result from run_diagnostics()

    Returns:
        Formatted string with ANSI color codes
    """
    try:
        # Use vfio_assist color functions if available
        from vfio_assist import colour, Fore

        output = []
        overall = diagnostic_result.get("overall", "unknown")

        # Header
        if overall == "ok":
            output.append(colour("✓ VFIO Diagnostics: PASSED", Fore.GREEN))
        elif overall == "warning":
            output.append(colour("⚠ VFIO Diagnostics: WARNINGS", Fore.YELLOW))
        else:
            output.append(colour("✗ VFIO Diagnostics: FAILED", Fore.RED))

        # Individual checks
        for check in diagnostic_result.get("checks", []):
            status = check.get("status", "unknown")
            name = check.get("name", "Unknown")
            message = check.get("message", "")

            if status == "ok":
                output.append(f"  ✓ {colour(name, Fore.GREEN)}: {message}")
            elif status == "warning":
                output.append(f"  ⚠ {colour(name, Fore.YELLOW)}: {message}")
            else:
                output.append(f"  ✗ {colour(name, Fore.RED)}: {message}")

        # Error if present
        if "error" in diagnostic_result:
            output.append(colour(f"Error: {diagnostic_result['error']}", Fore.RED))

        return "\n".join(output)

    except ImportError:
        # Fallback without colors
        return json.dumps(diagnostic_result, indent=2)


# Expose the context manager at module level for backward compatibility
__all__ = ["VFIOBinder", "VFIOBindError", "run_diagnostics", "render_pretty"]
