"""
TUI Utilities

Common utility functions for the TUI application.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.unified_context import get_package_version

from .models.device import PCIDevice


class DeviceFilter:
    """Device filtering utility class"""

    @staticmethod
    def filter_devices(
        devices: List[PCIDevice], filters: Dict[str, Any]
    ) -> List[PCIDevice]:
        """
        Apply filters to a list of devices

        Args:
            devices: List of PCIDevice objects to filter
            filters: Dictionary of filter criteria

        Returns:
            Filtered list of devices
        """
        filtered = devices.copy()

        # Text search filter
        search_text = filters.get("device_search", "").lower().strip()
        if search_text:
            filtered = [
                device
                for device in filtered
                if (
                    search_text in device.display_name.lower()
                    or search_text in device.bdf.lower()
                    or search_text in device.vendor_name.lower()
                    or search_text in device.device_name.lower()
                )
            ]

        # Device class filter
        class_filter = filters.get("class_filter", "all")
        if class_filter and class_filter != "all":
            filtered = [
                device
                for device in filtered
                if class_filter.lower() in device.device_class.lower()
            ]

        # Status filter
        status_filter = filters.get("status_filter", "all")
        if status_filter and status_filter != "all":
            if status_filter == "suitable":
                filtered = [d for d in filtered if d.is_suitable]
            elif status_filter == "bound":
                filtered = [d for d in filtered if d.has_driver]
            elif status_filter == "unbound":
                filtered = [d for d in filtered if not d.has_driver]
            elif status_filter == "vfio":
                filtered = [d for d in filtered if d.vfio_compatible]

        # Minimum score filter
        min_score = filters.get("min_score", 0.0)
        if min_score > 0:
            filtered = [
                device for device in filtered if device.suitability_score >= min_score
            ]

        return filtered

    @staticmethod
    def get_device_statistics(devices: List[PCIDevice]) -> Dict[str, Any]:
        """
        Get statistics about a list of devices

        Args:
            devices: List of PCIDevice objects

        Returns:
            Dictionary with device statistics
        """
        if not devices:
            return {
                "total": 0,
                "suitable": 0,
                "bound": 0,
                "unbound": 0,
                "vfio_compatible": 0,
                "avg_score": 0.0,
                "vendors": {},
                "classes": {},
            }

        suitable_count = sum(1 for d in devices if d.is_suitable)
        bound_count = sum(1 for d in devices if d.has_driver)
        unbound_count = len(devices) - bound_count
        vfio_count = sum(1 for d in devices if d.vfio_compatible)
        avg_score = sum(d.suitability_score for d in devices) / len(devices)

        # Count vendors
        vendors = {}
        for device in devices:
            vendor = device.vendor_name
            vendors[vendor] = vendors.get(vendor, 0) + 1

        # Count device classes
        classes = {}
        for device in devices:
            device_class = device.device_class
            classes[device_class] = classes.get(device_class, 0) + 1

        return {
            "total": len(devices),
            "suitable": suitable_count,
            "bound": bound_count,
            "unbound": unbound_count,
            "vfio_compatible": vfio_count,
            "avg_score": avg_score,
            "vendors": vendors,
            "classes": classes,
        }


class ExportManager:
    """Export utility class for various data formats"""

    @staticmethod
    def export_devices_json(
        devices: List[PCIDevice], output_path: Path, include_metadata: bool = True
    ) -> bool:
        """
        Export devices to JSON format

        Args:
            devices: List of devices to export
            output_path: Path to save the export file
            include_metadata: Whether to include export metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {"devices": [device.to_dict() for device in devices]}

            if include_metadata:
                data["metadata"] = {
                    "export_time": datetime.now().isoformat(),
                    "device_count": len(devices),
                    "exported_by": "PCILeech TUI",
                    "statistics": DeviceFilter.get_device_statistics(devices),
                }

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

            return True
        except Exception:
            return False

    @staticmethod
    def export_devices_csv(devices: List[PCIDevice], output_path: Path) -> bool:
        """
        Export devices to CSV format

        Args:
            devices: List of devices to export
            output_path: Path to save the export file

        Returns:
            True if successful, False otherwise
        """
        try:
            import csv

            with open(output_path, "w", newline="") as csvfile:
                fieldnames = [
                    "BDF",
                    "Vendor ID",
                    "Device ID",
                    "Vendor Name",
                    "Device Name",
                    "Class",
                    "Driver",
                    "IOMMU Group",
                    "Suitability Score",
                    "Is Suitable",
                    "VFIO Compatible",
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for device in devices:
                    writer.writerow(
                        {
                            "BDF": device.bdf,
                            "Vendor ID": device.vendor_id,
                            "Device ID": device.device_id,
                            "Vendor Name": device.vendor_name,
                            "Device Name": device.device_name,
                            "Class": device.device_class,
                            "Driver": device.driver or "None",
                            "IOMMU Group": device.iommu_group,
                            "Suitability Score": f"{device.suitability_score:.2f}",
                            "Is Suitable": "Yes" if device.is_suitable else "No",
                            "VFIO Compatible": (
                                "Yes" if device.vfio_compatible else "No"
                            ),
                        }
                    )

            return True
        except Exception:
            return False


class ValidationHelper:
    """Validation utilities for TUI inputs"""

    @staticmethod
    def validate_bdf(bdf: str) -> bool:
        """
        Validate PCI Bus:Device.Function format

        Args:
            bdf: BDF string to validate

        Returns:
            True if valid BDF format, False otherwise
        """
        pattern = r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9a-fA-F]$"
        return bool(re.match(pattern, bdf))

    @staticmethod
    def validate_score(score_str: str) -> Optional[float]:
        """
        Validate and parse a suitability score

        Args:
            score_str: Score string to validate

        Returns:
            Parsed float score if valid, None otherwise
        """
        try:
            score = float(score_str)
            if 0.0 <= score <= 1.0:
                return score
        except ValueError:
            pass
        return None

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename for cross-platform compatibility

        Args:
            filename: Filename to sanitize

        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        sanitized = filename
        for char in invalid_chars:
            sanitized = sanitized.replace(char, "_")

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(" .")

        # Ensure it's not empty
        if not sanitized:
            sanitized = "unnamed"

        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200]

        return sanitized


class KeyboardShortcuts:
    """Keyboard shortcut utilities and help"""

    SHORTCUTS = {
        "Navigation": {
            "Ctrl+Q": "Quit application",
            "Ctrl+R / F5": "Refresh device list",
            "Tab": "Navigate between widgets",
            "Enter": "Activate selected item",
            "Escape": "Close dialog/cancel",
        },
        "Device Management": {
            "Ctrl+F": "Search/Filter devices",
            "Ctrl+D": "Show device details",
            "Ctrl+E": "Export device list",
            "Up/Down": "Navigate device list",
        },
        "Configuration": {
            "Ctrl+C": "Open configuration dialog",
            "Ctrl+P": "Manage profiles",
            "Ctrl+S": "Start build (when device selected)",
            "Ctrl+B": "Backup configuration",
        },
        "Information": {
            "Ctrl+L": "View build logs",
            "Ctrl+H / F1": "Show help",
            "Ctrl+I": "Show system information",
        },
    }

    @classmethod
    def get_help_text(cls) -> str:
        """
        Get formatted help text for all keyboard shortcuts

        Returns:
            Formatted help text string
        """
        help_lines = ["PCILeech Firmware Generator - Keyboard Shortcuts\n"]

        for category, shortcuts in cls.SHORTCUTS.items():
            help_lines.append(f"{category}:")
            for key, description in shortcuts.items():
                help_lines.append(f"  {key:12} - {description}")
            help_lines.append("")

        help_lines.extend(
            [
                "Mouse Controls:",
                "  Click        - Select items",
                "  Double-click - Open details/configure",
                "  Right-click  - Context menu (where available)",
                "",
                "Visual Indicators:",
                "  ✅ Green    - Suitable/Ready devices",
                "  ⚠️ Yellow   - Devices with warnings",
                "  ❌ Red      - Incompatible devices",
                "  🔒 Lock     - Driver bound devices",
                "  🔓 Unlock   - Detached devices",
                "  🔌 Plug     - No driver devices",
                "",
                "Tips:",
                "- Use the quick search bar to filter devices in real-time",
                "- Multiple indicator symbols show device status at a glance",
                "- Press Ctrl+F for advanced filtering options",
                "- Build progress and logs are available during builds",
            ]
        )

        return "\n".join(help_lines)


class ConfigurationTemplates:
    """Pre-defined configuration templates"""

    TEMPLATES = {
        "development": {
            "name": "Development",
            "description": "Fast development configuration",
            "advanced_sv": False,
            "enable_variance": False,
            "behavior_profiling": False,
            "power_management": False,
            "error_handling": True,
            "performance_counters": False,
            "flash_after_build": True,
        },
        "production": {
            "name": "Production",
            "description": "Full-featured production configuration",
            "advanced_sv": True,
            "enable_variance": True,
            "behavior_profiling": True,
            "power_management": True,
            "error_handling": True,
            "performance_counters": True,
            "flash_after_build": False,
        },
        "testing": {
            "name": "Testing",
            "description": "Configuration optimized for testing",
            "advanced_sv": True,
            "enable_variance": False,
            "behavior_profiling": True,
            "power_management": False,
            "error_handling": True,
            "performance_counters": True,
            "flash_after_build": False,
        },
        "minimal": {
            "name": "Minimal",
            "description": "Minimal configuration for basic functionality",
            "advanced_sv": False,
            "enable_variance": False,
            "behavior_profiling": False,
            "power_management": False,
            "error_handling": False,
            "performance_counters": False,
            "flash_after_build": True,
        },
    }

    @classmethod
    def get_template(cls, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a configuration template by name

        Args:
            template_name: Name of the template

        Returns:
            Template configuration dict or None if not found
        """
        return cls.TEMPLATES.get(template_name)

    @classmethod
    def list_templates(cls) -> List[str]:
        """
        Get list of available template names

        Returns:
            List of template names
        """
        return list(cls.TEMPLATES.keys())


class SystemInfo:
    """System information utilities"""

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Get comprehensive system information

        Returns:
            Dictionary with system information
        """
        import platform

        info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
            },
            "pcileech": {
                "tui_version": get_package_version(),  # Use centralized version
                "features": [
                    "Device scanning",
                    "Configuration management",
                    "Build orchestration",
                    "Profile management",
                    "Export/Import",
                    "Keyboard shortcuts",
                ],
            },
        }

        # Try to get additional system info if available
        try:
            import psutil

            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            info["resources"] = {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
            }
        except ImportError:
            info["resources"] = {
                "note": "Install psutil for detailed resource information"
            }

        return info
