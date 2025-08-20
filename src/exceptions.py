#!/usr/bin/env python3
"""
Custom exceptions for the PCILeech firmware generator.

This module defines a hierarchy of custom exceptions to provide better
error handling and debugging capabilities throughout the application.
"""

from typing import Optional


class PCILeechError(Exception):
    """Base exception for all PCILeech firmware generator errors."""

    pass


class ConfigurationError(PCILeechError):
    """Raised when configuration is invalid or missing."""

    pass


class TemplateError(PCILeechError):
    """Base exception for template-related errors."""

    def __init__(self, message: Optional[str] = None, root_cause: Optional[str] = None):
        super().__init__(message if message else "Template error occurred")
        self.root_cause = root_cause

    def __str__(self):
        base_msg = super().__str__()
        if self.root_cause and self.root_cause != base_msg:
            return f"{base_msg} | Root cause: {self.root_cause}"
        return base_msg


class TemplateNotFoundError(TemplateError):
    """Raised when a required template file is not found."""

    def __init__(self, message: Optional[str] = None, root_cause: Optional[str] = None):
        super().__init__(message or "Template file not found", root_cause)

    def __str__(self):
        return super().__str__()


class TemplateRenderError(TemplateError):
    """Raised when template rendering fails."""

    def __init__(self, message: Optional[str] = None, root_cause: Optional[str] = None):
        super().__init__(message or "Template rendering failed", root_cause)

    def __str__(self):
        return super().__str__()


class DeviceConfigError(PCILeechError):
    """Raised when device configuration is invalid or unavailable."""

    def __init__(self, message: Optional[str] = None, root_cause: Optional[str] = None):
        super().__init__(message or "Device configuration error", root_cause)
        self.root_cause = root_cause

    def __str__(self):
        base_msg = super().__str__()
        if self.root_cause and self.root_cause != base_msg:
            return f"{base_msg} | Root cause: {self.root_cause}"
        return base_msg


class TCLBuilderError(PCILeechError):
    """Base exception for TCL builder operations."""

    def __init__(self, message: Optional[str] = None, root_cause: Optional[str] = None):
        super().__init__(message or "TCL builder error", root_cause)
        self.root_cause = root_cause

    def __str__(self):
        base_msg = super().__str__()
        if self.root_cause and self.root_cause != base_msg:
            return f"{base_msg} | Root cause: {self.root_cause}"
        return base_msg


class XDCConstraintError(PCILeechError):
    """Raised when XDC constraint operations fail."""

    def __init__(self, message: Optional[str] = None, root_cause: Optional[str] = None):
        super().__init__(message or "XDC constraint error", root_cause)
        self.root_cause = root_cause

    def __str__(self):
        base_msg = super().__str__()
        if self.root_cause and self.root_cause != base_msg:
            return f"{base_msg} | Root cause: {self.root_cause}"
        return base_msg


class RepositoryError(PCILeechError):
    """Raised when repository operations fail."""

    def __init__(self, message: Optional[str] = None, root_cause: Optional[str] = None):
        super().__init__(message or "Repository error", root_cause)
        self.root_cause = root_cause

    def __str__(self):
        base_msg = super().__str__()
        if self.root_cause and self.root_cause != base_msg:
            return f"{base_msg} | Root cause: {self.root_cause}"
        return base_msg


class BuildError(PCILeechError):
    """Raised when build operations fail."""

    def __init__(self, message: str, root_cause: Optional[str] = None):
        super().__init__(message)
        self.root_cause = root_cause

    def __str__(self):
        if self.root_cause and self.root_cause != str(super().__str__()):
            # Only show root cause if it's different from the main message
            return self.root_cause
        return super().__str__()


class ValidationError(PCILeechError):
    """Raised when validation fails."""

    def __init__(self, message: Optional[str] = None, root_cause: Optional[str] = None):
        super().__init__(message or "Validation error", root_cause)
        self.root_cause = root_cause

    def __str__(self):
        base_msg = super().__str__()
        if self.root_cause and self.root_cause != base_msg:
            return f"{base_msg} | Root cause: {self.root_cause}"
        return base_msg


class ContextError(PCILeechError):
    """Exception raised when context building fails."""

    def __init__(self, message: str, root_cause: Optional[str] = None):
        super().__init__(message)
        self.root_cause = root_cause

    def __str__(self):
        if self.root_cause and self.root_cause != str(super().__str__()):
            # Only show root cause if it's different from the main message
            return self.root_cause
        return super().__str__()


class PCILeechGenerationError(PCILeechError):
    """Exception raised when PCILeech generation fails."""

    def __init__(self, message: str, root_cause: Optional[str] = None):
        super().__init__(message)
        self.root_cause = root_cause

    def __str__(self):
        if self.root_cause and self.root_cause != str(super().__str__()):
            # Only show root cause if it's different from the main message
            return self.root_cause
        return super().__str__()


class ModuleImportError(PCILeechError):
    """Raised when module imports fail."""

    def __init__(self, message: Optional[str] = None, root_cause: Optional[str] = None):
        super().__init__(message or "Module import error", root_cause)
        self.root_cause = root_cause

    def __str__(self):
        base_msg = super().__str__()
        if self.root_cause and self.root_cause != base_msg:
            return f"{base_msg} | Root cause: {self.root_cause}"
        return base_msg


class PlatformCompatibilityError(PCILeechError):
    """Raised when a feature is not supported on the current platform."""

    def __init__(
        self,
        message: str,
        current_platform: Optional[str] = None,
        required_platform: Optional[str] = None,
    ):
        super().__init__(message)
        self.current_platform = current_platform
        self.required_platform = required_platform

    def __str__(self):
        base_msg = super().__str__()
        if self.current_platform and self.required_platform:
            return f"{base_msg} (Current: {self.current_platform}, Required: {self.required_platform})"
        return base_msg


class VFIOBindError(Exception):
    """Raised when VFIO binding fails."""

    pass


class VFIODeviceNotFoundError(VFIOBindError):
    """Raised when a VFIO device is not found."""

    pass


class VFIOPermissionError(VFIOBindError):
    """Raised when VFIO operations lack required permissions."""

    pass


class VFIOGroupError(VFIOBindError):
    """Raised when VFIO group operations fail."""

    pass


# Export all exception classes
__all__ = [
    "PCILeechError",
    "ConfigurationError",
    "TemplateError",
    "TemplateNotFoundError",
    "TemplateRenderError",
    "DeviceConfigError",
    "TCLBuilderError",
    "XDCConstraintError",
    "RepositoryError",
    "BuildError",
    "ValidationError",
    "ContextError",
    "PCILeechGenerationError",
    "ModuleImportError",
    "PlatformCompatibilityError",
    "VFIOBindError",
    "VFIODeviceNotFoundError",
    "VFIOPermissionError",
    "VFIOGroupError",
]
