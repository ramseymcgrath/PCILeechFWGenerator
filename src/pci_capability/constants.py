#!/usr/bin/env python3
"""
Shared PCI capability constants for PCILeechFWGenerator.

This module centralizes constants used by multiple capability analyzers so
they're not duplicated inside analyzer classes.
"""

# PCI class codes for USB devices
CLASS_CODES = {
    "uhci": 0x0C0300,  # Serial bus controller, USB (UHCI)
    "ohci": 0x0C0310,  # Serial bus controller, USB (OHCI)
    "ehci": 0x0C0320,  # Serial bus controller, USB2 (EHCI)
    "xhci": 0x0C0330,  # Serial bus controller, USB3 (xHCI)
    "usb4": 0x0C0340,  # Serial bus controller, USB4
    "other_usb": 0x0C0380,  # Serial bus controller, USB (Other)
}

# PCI Configuration Space Register Offsets
PCI_VENDOR_ID_OFFSET = 0x00
PCI_DEVICE_ID_OFFSET = 0x02
PCI_STATUS_REGISTER = 0x06
PCI_CAPABILITIES_POINTER = 0x34

# PCI Extended Configuration Space
PCI_EXT_CAP_START = 0x100
PCI_EXT_CONFIG_SPACE_END = 0x1000

# PCI Status Register Bits
PCI_STATUS_CAP_LIST = 0x10  # Capabilities List bit (bit 4)

# PCI Capability Header Offsets
PCI_CAP_ID_OFFSET = 0x00
PCI_CAP_NEXT_PTR_OFFSET = 0x01

# PCI Extended Capability Header Fields
PCI_EXT_CAP_ID_MASK = 0xFFFF
PCI_EXT_CAP_VERSION_MASK = 0xF
PCI_EXT_CAP_VERSION_SHIFT = 16
PCI_EXT_CAP_NEXT_PTR_MASK = 0xFFF
PCI_EXT_CAP_NEXT_PTR_SHIFT = 20

# PCI Extended Capability Alignment
PCI_EXT_CAP_ALIGNMENT = 0x3  # DWORD alignment mask

# Configuration Space Size Limits
PCI_CONFIG_SPACE_MIN_SIZE = 256  # Minimum 256 bytes
PCI_CONFIG_SPACE_MIN_HEX_CHARS = 512  # 256 bytes * 2 hex chars per byte

# Capability-Specific Offsets and Values

# Power Management Capability
PM_CAP_CAPABILITIES_OFFSET = 2  # PMC register offset from capability header
PM_CAP_D3HOT_SUPPORT = 0x0008  # D3hot support bit

# PCI Express Capability
PCIE_CAP_LINK_CONTROL_OFFSET = 0x10  # Link Control register offset
PCIE_CAP_DEVICE_CONTROL2_OFFSET = 0x28  # Device Control 2 register offset
PCIE_LINK_CONTROL_ASPM_MASK = 0x0003  # ASPM Control bits (0-1)
PCIE_DEVICE_CONTROL2_OBFF_LTR_MASK = 0x6400  # OBFF Enable (13-14) and LTR Enable (10)

# Access Control Services (ACS) Extended Capability
ACS_CONTROL_REGISTER_OFFSET = 6  # ACS Control Register offset from capability header

# Downstream Port Containment (DPC) Extended Capability
DPC_CONTROL_REGISTER_OFFSET = 6  # DPC Control Register offset from capability header

# Resizable BAR Extended Capability
RBAR_CAPABILITY_REGISTER_OFFSET = 8  # First BAR capability register offset
RBAR_SIZE_MASK_ABOVE_128MB = 0xF7FFFFFF  # Clear bits 27-31 (sizes above 128MB)

# Standard Capability Names Mapping
STANDARD_CAPABILITY_NAMES = {
    0x01: "Power Management",
    0x02: "AGP",
    0x03: "VPD",
    0x04: "Slot ID",
    0x05: "MSI",
    0x06: "CompactPCI Hot Swap",
    0x07: "PCI-X",
    0x08: "HyperTransport",
    0x09: "Vendor-Specific",
    0x0A: "Debug Port",
    0x0B: "CompactPCI CRC",
    0x0C: "PCI Hot Plug",
    0x0D: "PCI Bridge Subsystem VID",
    0x0E: "AGP 8x",
    0x0F: "Secure Device",
    0x10: "PCI Express",
    0x11: "MSI-X",
    0x12: "SATA Data Index Conf",
    0x13: "Advanced Features",
}

# Extended Capability Names Mapping
EXTENDED_CAPABILITY_NAMES = {
    0x0001: "Advanced Error Reporting",
    0x0002: "Virtual Channel",
    0x0003: "Device Serial Number",
    0x0004: "Power Budgeting",
    0x0005: "Root Complex Link Declaration",
    0x0006: "Root Complex Internal Link Control",
    0x0007: "Root Complex Event Collector Endpoint Association",
    0x0008: "Multi-Function Virtual Channel",
    0x0009: "Virtual Channel (MFVC)",
    0x000A: "Root Complex Register Block",
    0x000B: "Vendor-Specific Extended",
    0x000C: "Config Access Correlation",
    0x000D: "Access Control Services",
    0x000E: "Alternative Routing-ID Interpretation",
    0x000F: "Address Translation Services",
    0x0010: "Single Root I/O Virtualization",
    0x0011: "Multi-Root I/O Virtualization",
    0x0012: "Multicast",
    0x0013: "Page Request",
    0x0014: "Reserved for AMD",
    0x0015: "Resizable BAR",
    0x0016: "Dynamic Power Allocation",
    0x0017: "TPH Requester",
    0x0018: "Latency Tolerance Reporting",
    0x0019: "Secondary PCI Express",
    0x001A: "Protocol Multiplexing",
    0x001B: "Process Address Space ID",
    0x001C: "LN Requester",
    0x001D: "Downstream Port Containment",
    0x001E: "L1 PM Substates",
    0x001F: "Precision Time Measurement",
    0x0020: "PCI Express over M-PHY",
    0x0021: "FRS Queueing",
    0x0022: "Readiness Time Reporting",
    0x0023: "Designated Vendor-Specific",
    0x0024: "VF Resizable BAR",
    0x0025: "Data Link Feature",
    0x0026: "Physical Layer 16.0 GT/s",
    0x0027: "Lane Margining at Receiver",
    0x0028: "Hierarchy ID",
    0x0029: "Native PCIe Enclosure Management",
}

# Capabilities with 2-byte headers (instead of standard 1-byte)
TWO_BYTE_HEADER_CAPABILITIES = {0x07, 0x04}  # PCI-X and Slot ID

# Capability Size Constants
# Standard capability size estimates in bytes
STD_CAP_SIZE_POWER_MANAGEMENT = 8
STD_CAP_SIZE_MSI = 24
STD_CAP_SIZE_MSI_X = 12
STD_CAP_SIZE_PCI_EXPRESS = 60
STD_CAP_SIZE_DEFAULT = 16

# Extended capability size estimates in bytes
EXT_CAP_SIZE_ADVANCED_ERROR_REPORTING = 48
EXT_CAP_SIZE_ACCESS_CONTROL_SERVICES = 8
EXT_CAP_SIZE_DOWNSTREAM_PORT_CONTAINMENT = 16
EXT_CAP_SIZE_RESIZABLE_BAR = 16
EXT_CAP_SIZE_DEFAULT = 32

## MSI-X Constants
MSIX_CAPABILITY_SIZE = 12  # MSI-X capability structure is 12 bytes
MSIX_MESSAGE_CONTROL_OFFSET = 2
MSIX_TABLE_OFFSET_BIR_OFFSET = 4
MSIX_PBA_OFFSET_BIR_OFFSET = 8

# MSI-X Message Control register bit definitions
MSIX_TABLE_SIZE_MASK = 0x07FF  # Bits 0-10
MSIX_FUNCTION_MASK_BIT = 0x4000  # Bit 14
MSIX_ENABLE_BIT = 0x8000  # Bit 15

# MSI-X Table/PBA offset register bit definitions
MSIX_BIR_MASK = 0x7  # Bits 0-2
MSIX_OFFSET_MASK = 0xFFFFFFF8  # Bits 3-31

# MSI-X constraints
MSIX_MIN_TABLE_SIZE = 1
MSIX_MAX_TABLE_SIZE = 2048
MSIX_MAX_BIR = 5
MSIX_OFFSET_ALIGNMENT = 8
MSIX_LARGE_TABLE_THRESHOLD = 64
