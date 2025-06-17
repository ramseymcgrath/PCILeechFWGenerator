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

    pass


class ValidationError(PCILeechError):
    """Raised when validation fails."""

    pass


class ImportError(PCILeechError):
    """Raised when module imports fail."""

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
    "ImportError",
]
