#!/usr/bin/env python3
"""
Custom exceptions for the PCILeech firmware generator.

This module defines a hierarchy of custom exceptions to provide better
error handling and debugging capabilities throughout the application.
"""


class PCILeechError(Exception):
    """Base exception for all PCILeech firmware generator errors."""

    pass


class ConfigurationError(PCILeechError):
    """Raised when configuration is invalid or missing."""

    pass


class TemplateError(PCILeechError):
    """Base exception for template-related errors."""

    pass


class TemplateNotFoundError(TemplateError):
    """Raised when a required template file is not found."""

    pass


class TemplateRenderError(TemplateError):
    """Raised when template rendering fails."""

    pass


class DeviceConfigError(PCILeechError):
    """Raised when device configuration is invalid or unavailable."""

    pass


class TCLBuilderError(PCILeechError):
    """Base exception for TCL builder operations."""

    pass


class XDCConstraintError(PCILeechError):
    """Raised when XDC constraint operations fail."""

    pass


class RepositoryError(PCILeechError):
    """Raised when repository operations fail."""

    pass


class BuildError(PCILeechError):
    """Raised when build operations fail."""

    def __init__(self, message: str, root_cause: str | None = None):
        super().__init__(message)
        self.root_cause = root_cause

    def __str__(self):
        if self.root_cause and self.root_cause != str(super().__str__()):
            # Only show root cause if it's different from the main message
            return self.root_cause
        return super().__str__()


class ValidationError(PCILeechError):
    """Raised when validation fails."""

    pass


class ContextError(PCILeechError):
    """Exception raised when context building fails."""

    def __init__(self, message: str, root_cause: str | None = None):
        super().__init__(message)
        self.root_cause = root_cause

    def __str__(self):
        if self.root_cause and self.root_cause != str(super().__str__()):
            # Only show root cause if it's different from the main message
            return self.root_cause
        return super().__str__()


class PCILeechGenerationError(PCILeechError):
    """Exception raised when PCILeech generation fails."""

    def __init__(self, message: str, root_cause: str | None = None):
        super().__init__(message)
        self.root_cause = root_cause

    def __str__(self):
        if self.root_cause and self.root_cause != str(super().__str__()):
            # Only show root cause if it's different from the main message
            return self.root_cause
        return super().__str__()


class ModuleImportError(PCILeechError):
    """Raised when module imports fail."""

    pass


class PlatformCompatibilityError(PCILeechError):
    """Raised when a feature is not supported on the current platform."""

    def __init__(
        self,
        message: str,
        current_platform: str | None = None,
        required_platform: str | None = None,
    ):
        super().__init__(message)
        self.current_platform = current_platform
        self.required_platform = required_platform

    def __str__(self):
        base_msg = super().__str__()
        if self.current_platform and self.required_platform:
            return f"{base_msg} (Current: {self.current_platform}, Required: {self.required_platform})"
        return base_msg


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
]
