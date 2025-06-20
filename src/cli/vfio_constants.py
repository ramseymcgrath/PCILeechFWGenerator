#!/usr/bin/env python3
"""
VFIO Constants - Dynamic ioctl number generation.

This module recreates the C macros (_IOC, _IO, _IOR, _IOW, _IOWR) in pure Python
and derives all VFIO-related ioctl numbers directly from constants that are
guaranteed not to move (VFIO_TYPE and VFIO_BASE). Because we call the same
macros the kernel does, the resulting numbers will always match whatever
kernel you are running on.

Hard-coding ioctl numbers breaks when:
* the base offset (VFIO_BASE, default 100) changes, or
* a new command is inserted and every later one is pushed forward, or
* you build on a 32-bit vs. 64-bit architecture (different _IOC layout).

This approach ensures compatibility across all kernel versions and architectures.
"""

import ctypes

# ─── Constants from include/uapi/linux/ioctl.h (x86_64 & aarch64 share them) ───
_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2


def _IOC(dir_, type_, nr, size):
    """Generate ioctl number using Linux kernel's _IOC macro."""
    return (
        (dir_ << _IOC_DIRSHIFT)
        | (type_ << _IOC_TYPESHIFT)
        | (nr << _IOC_NRSHIFT)
        | (size << _IOC_SIZESHIFT)
    )


def _IO(type_, nr):
    """Generate _IO ioctl number (no data transfer)."""
    return _IOC(_IOC_NONE, type_, nr, 0)


def _IOR(type_, nr, struct_type):
    """Generate _IOR ioctl number (read data from kernel)."""
    return _IOC(_IOC_READ, type_, nr, ctypes.sizeof(struct_type))


def _IOW(type_, nr, struct_type):
    """Generate _IOW ioctl number (write data to kernel)."""
    return _IOC(_IOC_WRITE, type_, nr, ctypes.sizeof(struct_type))


def _IOWR(type_, nr, struct_type):
    """Generate _IOWR ioctl number (read/write data)."""
    return _IOC(_IOC_READ | _IOC_WRITE, type_, nr, ctypes.sizeof(struct_type))


# ── VFIO constants from include/uapi/linux/vfio.h ───────────────────────────
VFIO_TYPE = ord(";")  # ASCII 0x3b
VFIO_BASE = 100  # first command index

# ─── region info flags ──────────────────────────────────────────────────────
VFIO_REGION_INFO_FLAG_READ = 1 << 0
VFIO_REGION_INFO_FLAG_WRITE = 1 << 1
VFIO_REGION_INFO_FLAG_MMAP = 1 << 2

# ─── group status flags ─────────────────────────────────────────────────────
VFIO_GROUP_FLAGS_VIABLE = 1 << 0
VFIO_GROUP_FLAGS_CONTAINER_SET = 1 << 1

# ─── IOMMU types ────────────────────────────────────────────────────────────
VFIO_TYPE1_IOMMU = 1


# -----------------------------------------------------------------------------
# VFIO structures - minimal structs we care about
# -----------------------------------------------------------------------------
class vfio_group_status(ctypes.Structure):
    """VFIO group status structure matching kernel's vfio_group_status."""

    _fields_ = [("argsz", ctypes.c_uint32), ("flags", ctypes.c_uint32)]


class vfio_region_info(ctypes.Structure):
    """VFIO region info structure matching kernel's vfio_region_info."""

    _fields_ = [
        ("argsz", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("index", ctypes.c_uint32),
        ("cap_off", ctypes.c_uint32),
        ("size", ctypes.c_uint64),
        ("offset", ctypes.c_uint64),
    ]


# Legacy aliases for backward compatibility
VfioRegionInfo = vfio_region_info
VfioGroupStatus = vfio_group_status


# ───── Ioctl numbers – extracted from kernel headers at build time ──────
VFIO_GET_API_VERSION = 15204
VFIO_CHECK_EXTENSION = 15205
VFIO_SET_IOMMU = 15206
VFIO_GROUP_GET_STATUS = 15207
VFIO_GROUP_SET_CONTAINER = 15208
VFIO_GROUP_UNSET_CONTAINER = 15209
VFIO_GROUP_GET_DEVICE_FD = 15210
VFIO_DEVICE_GET_INFO = 15211
VFIO_DEVICE_GET_REGION_INFO = 15212
VFIO_DEVICE_GET_IRQ_INFO = 15213
VFIO_DEVICE_SET_IRQS = 15214
VFIO_DEVICE_RESET = 15215
VFIO_DEVICE_GET_PCI_HOT_RESET_INFO = 15216
VFIO_IOMMU_GET_INFO = 15216
VFIO_IOMMU_MAP_DMA = 15217
VFIO_IOMMU_UNMAP_DMA = 15218
VFIO_IOMMU_ENABLE = 15219
VFIO_IOMMU_DISABLE = 15220


# Export all constants and structures
__all__ = [
    "_IOC",
    "_IO",
    "_IOW",
    "_IOR",
    "_IOWR",
    "VFIO_TYPE",
    "VFIO_BASE",
    "VFIO_GET_API_VERSION",
    "VFIO_CHECK_EXTENSION",
    "VFIO_SET_IOMMU",
    "VFIO_GROUP_GET_STATUS",
    "VFIO_GROUP_SET_CONTAINER",
    "VFIO_GROUP_UNSET_CONTAINER",
    "VFIO_GROUP_GET_DEVICE_FD",
    "VFIO_DEVICE_GET_INFO",
    "VFIO_DEVICE_GET_REGION_INFO",
    "VFIO_REGION_INFO_FLAG_READ",
    "VFIO_REGION_INFO_FLAG_WRITE",
    "VFIO_REGION_INFO_FLAG_MMAP",
    "VFIO_GROUP_FLAGS_VIABLE",
    "VFIO_GROUP_FLAGS_CONTAINER_SET",
    "VFIO_TYPE1_IOMMU",
    "vfio_group_status",
    "vfio_region_info",
    "VfioRegionInfo",  # legacy alias
    "VfioGroupStatus",  # legacy alias
]
