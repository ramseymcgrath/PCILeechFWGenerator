"""
Base Plugin Interface

Defines the base interface for plugins in the PCILeech TUI application.
"""

import abc
from typing import Any, Dict, List, Optional, Protocol, Type, Union


class DeviceAnalyzer(Protocol):
    """Protocol defining a device analyzer component."""

    def analyze_device(self, device_id: str, config_space: bytes) -> Dict[str, Any]:
        """
        Analyze a device and return a dictionary of analysis results.

        Args:
            device_id: Device identifier
            config_space: Device configuration space data

        Returns:
            Dictionary containing analysis results
        """
        ...

    def get_name(self) -> str:
        """Get the name of the analyzer."""
        ...

    def get_description(self) -> str:
        """Get a description of the analyzer."""
        ...


class BuildHook(Protocol):
    """Protocol defining a build hook component."""

    def pre_build(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute before the build process starts.

        Args:
            config: Build configuration

        Returns:
            Modified build configuration
        """
        ...

    def post_build(self, build_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute after the build process completes.

        Args:
            build_result: Build results

        Returns:
            Modified build results
        """
        ...


class ConfigValidator(Protocol):
    """Protocol defining a configuration validator component."""

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate a configuration and return a list of validation issues.

        Args:
            config: Configuration to validate

        Returns:
            List of validation issues (empty if valid)
        """
        ...


class PCILeechPlugin(abc.ABC):
    """
    Base class for PCILeech TUI plugins.

    All plugins must inherit from this class and implement its required methods.
    """

    @abc.abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the plugin.

        Returns:
            Plugin name
        """
        pass

    @abc.abstractmethod
    def get_version(self) -> str:
        """
        Get the version of the plugin.

        Returns:
            Plugin version
        """
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        """
        Get a description of the plugin.

        Returns:
            Plugin description
        """
        pass

    def get_device_analyzer(self) -> Optional[DeviceAnalyzer]:
        """
        Get a device analyzer component if the plugin provides one.

        Returns:
            DeviceAnalyzer or None if not provided
        """
        return None

    def get_build_hook(self) -> Optional[BuildHook]:
        """
        Get a build hook component if the plugin provides one.

        Returns:
            BuildHook or None if not provided
        """
        return None

    def get_config_validator(self) -> Optional[ConfigValidator]:
        """
        Get a configuration validator component if the plugin provides one.

        Returns:
            ConfigValidator or None if not provided
        """
        return None

    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with application context.

        Args:
            app_context: Application context dictionary

        Returns:
            Boolean indicating initialization success
        """
        return True

    def shutdown(self) -> None:
        """Clean up resources when the plugin is being unloaded."""
        pass


class SimplePlugin(PCILeechPlugin):
    """
    A simplified base class for creating plugins with minimal boilerplate.

    Inherit from this class and override only the specific methods needed
    for your plugin functionality.
    """

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        device_analyzer: Optional[DeviceAnalyzer] = None,
        build_hook: Optional[BuildHook] = None,
        config_validator: Optional[ConfigValidator] = None,
    ):
        """
        Initialize a simple plugin with provided components.

        Args:
            name: Plugin name
            version: Plugin version
            description: Plugin description
            device_analyzer: Optional device analyzer component
            build_hook: Optional build hook component
            config_validator: Optional configuration validator component
        """
        self._name = name
        self._version = version
        self._description = description
        self._device_analyzer = device_analyzer
        self._build_hook = build_hook
        self._config_validator = config_validator

    def get_name(self) -> str:
        """Get the plugin name."""
        return self._name

    def get_version(self) -> str:
        """Get the plugin version."""
        return self._version

    def get_description(self) -> str:
        """Get the plugin description."""
        return self._description

    def get_device_analyzer(self) -> Optional[DeviceAnalyzer]:
        """Get the device analyzer component if provided."""
        return self._device_analyzer

    def get_build_hook(self) -> Optional[BuildHook]:
        """Get the build hook component if provided."""
        return self._build_hook

    def get_config_validator(self) -> Optional[ConfigValidator]:
        """Get the configuration validator component if provided."""
        return self._config_validator
