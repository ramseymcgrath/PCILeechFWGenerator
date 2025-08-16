#!/usr/bin/env python3
"""
Fallback Manager for Template Variables

This module provides a centralized fallback management system for
template variables, ensuring that all templates have access to required variables
without needing to define defaults in the templates themselves.

"""

import copy
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
    Union,
)

from src.string_utils import log_error_safe, log_info_safe, log_warning_safe

# Type variable for return type of handler functions
T = TypeVar("T")

logger = logging.getLogger(__name__)


class FallbackMode(Enum):
    """Policy modes for fallback confirmation behavior."""

    NONE = "none"  # Never allow fallbacks
    AUTO = "auto"  # Always allow fallbacks
    PROMPT = "prompt"  # Permissive in non-interactive contexts


class VariableType(Enum):
    """Types of variables for categorization."""

    CRITICAL = "critical"  # Must come from hardware, no fallbacks
    SENSITIVE = "sensitive"  # Contains sensitive tokens
    STANDARD = "standard"  # Normal variables with fallbacks
    DEFAULT = "default"  # Built-in system defaults


@dataclass
class FallbackConfig:
    """Configuration for fallback behavior."""

    mode: FallbackMode = FallbackMode.PROMPT
    allowed_fallbacks: Set[str] = field(default_factory=set)
    config_path: Optional[Path] = None

    def __post_init__(self):
        """Validate and normalize configuration."""
        if isinstance(self.mode, str):
            self.mode = FallbackMode(self.mode)
        if self.config_path and isinstance(self.config_path, str):
            self.config_path = Path(self.config_path)


@dataclass
class VariableMetadata:
    """Metadata for a registered variable."""

    name: str
    value: Any
    var_type: VariableType = VariableType.STANDARD
    is_dynamic: bool = False
    handler: Optional[Callable[[], Any]] = None
    description: Optional[str] = None


class FallbackHandler(Protocol):
    """Protocol for fallback value handlers."""

    def __call__(self) -> Any: ...


class FallbackManager:
    """
    Manages fallback values for template variables.

    This class provides a centralized way to register, retrieve, and apply
    fallback values for template variables, ensuring consistent handling
    across all templates.

    Attributes:
        SENSITIVE_TOKENS: Tokens that indicate sensitive variables
        DEFAULT_FALLBACKS: System-wide default fallback values
    """

    # Class-level constants
    SENSITIVE_TOKENS: Final[Tuple[str, ...]] = (
        "vendor_id",
        "device_id",
        "revision_id",
        "class_code",
        "bars",
        "subsys",
    )

    DEFAULT_FALLBACKS: Final[Dict[str, Any]] = {
        "board.name": "",
        "board.fpga_part": "",
        "board.fpga_family": "7series",
        "board.pcie_ip_type": "pcie7x",
        "sys_clk_freq_mhz": 100,
        "generated_xdc_path": "",
        "board_xdc_content": "",
        "max_lanes": 1,
        "supports_msi": True,
        "supports_msix": False,
    }

    # Regex patterns for template variable detection
    JINJA_VAR_PATTERN: Final[re.Pattern] = re.compile(
        r"{{\s*([a-zA-Z0-9_.]+)|{%\s*if\s+([a-zA-Z0-9_.]+)"
    )

    def __init__(
        self,
        config_path: Optional[Union[str, FallbackConfig]] = None,
        mode: str = "prompt",
        allowed_fallbacks: Optional[List[str]] = None,
    ):
        """
        Initialize the fallback manager.

        Args:
            config_path: Path to YAML config file OR FallbackConfig object for new API
            mode: Policy mode controlling fallback confirmation behavior
            allowed_fallbacks: Optional whitelist of fallback keys
        """
        # Support both old and new initialization styles
        if isinstance(config_path, FallbackConfig):
            # New API: first arg is FallbackConfig
            self.config = config_path
        else:
            # Legacy API: individual parameters
            self.config = FallbackConfig(
                mode=FallbackMode(mode) if isinstance(mode, str) else mode,
                allowed_fallbacks=set(allowed_fallbacks or []),
                config_path=Path(config_path) if config_path else None,
            )

        # Expose legacy attributes for backward compatibility
        self.mode = self.config.mode.value
        self.allowed_fallbacks = self.config.allowed_fallbacks

        # Internal storage
        self._variables: Dict[str, VariableMetadata] = {}
        self._critical_vars: Set[str] = set()
        self._default_registered_keys: Set[str] = set()

        # Legacy compatibility: expose _fallbacks as a property-like dict
        self._fallbacks: Dict[str, Any] = {}
        self._default_handlers: Dict[str, Callable[[], Any]] = {}

        # Performance cache
        self._path_cache: Dict[str, List[str]] = {}

        # Initialize defaults
        self._register_default_fallbacks()

        # Load external config if provided
        if self.config.config_path:
            self.load_from_config(str(self.config.config_path))

    def confirm_fallback(
        self, key: str, reason: str, details: Optional[str] = None
    ) -> bool:
        """
        Policy decision helper for fallback permission.

        Args:
            key: Identifier for the fallback being requested
            reason: Short explanation why the fallback would be used
            details: Optional longer description

        Returns:
            True if the fallback is permitted, False otherwise
        """
        # Check whitelist first
        if self.config.allowed_fallbacks and key not in self.config.allowed_fallbacks:
            log_warning_safe(
                logger, "Fallback {key} not in whitelist", prefix="FALLBACK", key=key
            )
            return False

        # Apply mode-based policy
        if self.config.mode == FallbackMode.NONE:
            log_warning_safe(
                logger,
                "Fallback denied by policy (mode=none) for {key}: {reason}",
                prefix="FALLBACK",
                key=key,
                reason=reason,
            )
            return False

        if self.config.mode == FallbackMode.AUTO:
            log_info_safe(
                logger,
                "Fallback auto-approved for {key}",
                prefix="FALLBACK",
                key=key,
            )
            return True

        # PROMPT mode - allow in non-interactive contexts
        log_info_safe(
            logger,
            "Fallback permitted (mode=prompt) for {key}: {reason}",
            prefix="FALLBACK",
            key=key,
            reason=reason,
        )
        return True

    def _register_default_fallbacks(self) -> None:
        """Register default fallbacks for common variables."""
        for key, value in self.DEFAULT_FALLBACKS.items():
            metadata = VariableMetadata(
                name=key,
                value=value,
                var_type=VariableType.DEFAULT,
                description=f"Default fallback for {key}",
            )
            self._variables[key] = metadata
            self._default_registered_keys.add(key)

            log_info_safe(
                logger,
                "Registered default fallback for {var_name}",
                prefix="FALLBACK",
                var_name=key,
            )

        self._register_default_critical_variables()

    def _register_default_critical_variables(self) -> None:
        """Register default critical variables that should never have fallbacks."""
        critical_vars = []

        # Build critical variable list from sensitive tokens
        for token in self.SENSITIVE_TOKENS:
            if token == "bars":
                critical_vars.extend(["bars", "device.bars"])
            else:
                critical_vars.append(f"device.{token}")

        # Additional critical variables
        critical_vars.extend(
            [
                "device.subsys_vendor_id",
                "device.subsys_device_id",
            ]
        )

        self.mark_as_critical(critical_vars)

    def _split_path(self, path: str) -> List[str]:
        """
        Split a dot-notation path into parts with caching.

        Args:
            path: Dot-notation path like "device.config.id"

        Returns:
            List of path components
        """
        if path not in self._path_cache:
            self._path_cache[path] = path.split(".")
        return self._path_cache[path]

    def _navigate_nested_dict(
        self,
        context: Dict[str, Any],
        path_parts: List[str],
        create_missing: bool = False,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], bool]:
        """
        Navigate to a nested dictionary path.

        Args:
            context: The dictionary to navigate
            path_parts: List of parts in the path
            create_missing: Whether to create missing intermediate dicts

        Returns:
            Tuple of (parent_dict, final_key, success)
        """
        if not path_parts:
            return context, "", True

        current = context

        # Navigate to parent of final key
        for part in path_parts[:-1]:
            if part not in current:
                if create_missing:
                    current[part] = {}
                else:
                    return None, None, False
            elif not isinstance(current[part], dict):
                return None, None, False
            current = current[part]

        return current, path_parts[-1], True

    def register_fallback(
        self, var_name: str, value: Any, description: Optional[str] = None
    ) -> bool:
        """
        Register a fallback value for a variable.

        Args:
            var_name: The variable name (can use dot notation)
            value: The fallback value
            description: Optional description of the variable

        Returns:
            True if registered successfully, False otherwise
        """
        if not self._validate_variable_name(var_name):
            return False

        if var_name in self._critical_vars:
            log_warning_safe(
                logger,
                "Cannot register fallback for critical variable: {var_name}",
                prefix="FALLBACK",
                var_name=var_name,
            )
            return False

        metadata = VariableMetadata(
            name=var_name,
            value=value,
            var_type=self._determine_variable_type(var_name),
            description=description,
        )
        self._variables[var_name] = metadata

        log_info_safe(
            logger,
            "Registered fallback for {var_name} = {value}",
            prefix="FALLBACK",
            var_name=var_name,
            value=value,
        )
        return True

    def register_handler(
        self, var_name: str, handler: FallbackHandler, description: Optional[str] = None
    ) -> bool:
        """
        Register a dynamic handler for a variable.

        Args:
            var_name: The variable name (can use dot notation)
            handler: A callable that returns the fallback value
            description: Optional description

        Returns:
            True if registered successfully, False otherwise
        """
        if not self._validate_variable_name(var_name):
            return False

        if var_name in self._critical_vars:
            log_warning_safe(
                logger,
                "Cannot register handler for critical variable: {var_name}",
                prefix="FALLBACK",
                var_name=var_name,
            )
            return False

        if not callable(handler):
            log_error_safe(
                logger,
                "Handler for {var_name} is not callable",
                prefix="FALLBACK",
                var_name=var_name,
            )
            return False

        metadata = VariableMetadata(
            name=var_name,
            value=None,
            var_type=self._determine_variable_type(var_name),
            is_dynamic=True,
            handler=handler,
            description=description,
        )
        self._variables[var_name] = metadata

        log_info_safe(
            logger,
            "Registered dynamic handler for {var_name}",
            prefix="FALLBACK",
            var_name=var_name,
        )
        return True

    def mark_as_critical(self, var_names: List[str]) -> None:
        """
        Mark variables as critical, preventing fallbacks.

        Args:
            var_names: List of variable names to mark as critical
        """
        for var_name in var_names:
            if not self._validate_variable_name(var_name):
                continue

            self._critical_vars.add(var_name)

            # Remove any existing registrations
            if var_name in self._variables:
                del self._variables[var_name]
            # Legacy compatibility: also remove from old dicts
            if var_name in self._fallbacks:
                del self._fallbacks[var_name]
            if var_name in self._default_handlers:
                del self._default_handlers[var_name]
            # Legacy compatibility
            if var_name in self._fallbacks:
                del self._fallbacks[var_name]
            if var_name in self._default_handlers:
                del self._default_handlers[var_name]

        log_info_safe(
            logger,
            "Marked {count} variables as critical (no fallbacks)",
            prefix="FALLBACK",
            count=len(var_names),
        )

    def get_fallback(self, var_name: str) -> Any:
        """
        Get the fallback value for a variable.

        Args:
            var_name: The variable name

        Returns:
            The fallback value or None if not found

        Raises:
            ValueError: If the variable is critical
            RuntimeError: If a dynamic handler fails
        """
        if var_name in self._critical_vars:
            raise ValueError(f"Cannot get fallback for critical variable: {var_name}")

        if var_name not in self._variables:
            return None

        metadata = self._variables[var_name]

        if metadata.is_dynamic and metadata.handler:
            try:
                return metadata.handler()
            except Exception as e:
                log_error_safe(
                    logger,
                    "Handler for {var_name} raised an exception: {error}",
                    prefix="FALLBACK",
                    var_name=var_name,
                    error=str(e),
                )
                raise RuntimeError(f"Handler failed for {var_name}") from e

        return metadata.value

    def apply_fallbacks(
        self, template_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply all registered fallbacks to a template context.

        Args:
            template_context: The original template context

        Returns:
            Updated template context with fallbacks applied
        """
        # Deep copy to avoid modifying original
        context = copy.deepcopy(template_context) if template_context else {}

        # Apply all registered variables
        for var_name, metadata in self._variables.items():
            if var_name in self._critical_vars:
                continue

            self._apply_single_fallback(context, metadata)

        return context

    def _apply_single_fallback(
        self, context: Dict[str, Any], metadata: VariableMetadata
    ) -> bool:
        """
        Apply a single fallback value to the context.

        Args:
            context: The template context to update
            metadata: Variable metadata

        Returns:
            True if the fallback was applied, False otherwise
        """
        var_name = metadata.name

        # Get the value (from handler or static)
        if metadata.is_dynamic and metadata.handler:
            try:
                value = metadata.handler()
            except Exception as e:
                log_warning_safe(
                    logger,
                    "Handler for {var_name} failed: {error}",
                    prefix="FALLBACK",
                    var_name=var_name,
                    error=str(e),
                )
                return False
        else:
            value = metadata.value

        # Apply to context
        if "." in var_name:
            parts = self._split_path(var_name)
            parent, key, success = self._navigate_nested_dict(
                context, parts, create_missing=True
            )

            if success and parent is not None and key:
                if key not in parent:
                    parent[key] = value
                    self._log_fallback_applied(var_name, metadata.is_dynamic)
                    return True
        else:
            if var_name not in context:
                context[var_name] = value
                self._log_fallback_applied(var_name, metadata.is_dynamic)
                return True

        return False

    def _log_fallback_applied(self, var_name: str, is_dynamic: bool) -> None:
        """Log that a fallback was applied."""
        if is_dynamic:
            log_info_safe(
                logger,
                "Applied dynamic fallback for {var_name}",
                prefix="FALLBACK",
                var_name=var_name,
            )
        else:
            log_info_safe(
                logger,
                "Applied fallback for {var_name}",
                prefix="FALLBACK",
                var_name=var_name,
            )

    def validate_critical_variables(
        self, template_context: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all critical variables are present.

        Args:
            template_context: The template context to validate

        Returns:
            Tuple of (is_valid, missing_variables)
        """
        missing = []

        for var_name in self._critical_vars:
            exists, _ = self._check_var_exists(template_context, var_name)
            if not exists:
                missing.append(var_name)

        if missing:
            log_error_safe(
                logger,
                "Missing critical variables: {missing}",
                prefix="FALLBACK",
                missing=", ".join(missing),
            )
            return False, missing

        return True, []

    def _check_var_exists(
        self, template_context: Dict[str, Any], var_name: str
    ) -> Tuple[bool, Any]:
        """
        Check if a variable exists and has a non-empty value.

        Args:
            template_context: The template context to check
            var_name: The variable name (can use dot notation)

        Returns:
            Tuple of (exists, value)
        """
        if "." in var_name:
            parts = self._split_path(var_name)
            parent, key, success = self._navigate_nested_dict(
                template_context, parts, create_missing=False
            )

            if not success or parent is None or key not in parent:
                return False, None

            value = parent[key]
        else:
            if var_name not in template_context:
                return False, None
            value = template_context[var_name]

        # Check for empty containers
        if value is None:
            return False, None
        if isinstance(value, (list, dict, str)) and len(value) == 0:
            return False, None

        return True, value

    def get_exposable_fallbacks(self) -> Dict[str, Any]:
        """
        Get fallbacks that are safe to expose to users.

        Returns:
            Dictionary of variable names and values that are safe to expose
        """
        exposable = {}

        for var_name, metadata in self._variables.items():
            # Skip critical and sensitive variables
            if var_name in self._critical_vars:
                continue
            if self.is_sensitive_var(var_name):
                continue

            # Skip dynamic handlers (can't serialize)
            if metadata.is_dynamic:
                continue

            # Present defaults as blanks for user input
            if var_name in self._default_registered_keys:
                exposable[var_name] = ""
            else:
                exposable[var_name] = metadata.value

        return exposable

    def is_sensitive_var(self, name: str) -> bool:
        """
        Check if a variable name contains sensitive tokens.

        Args:
            name: The variable name to check

        Returns:
            True if the name contains a sensitive token
        """
        if not isinstance(name, str):
            return False

        name_lower = name.lower()
        return any(token in name_lower for token in self.SENSITIVE_TOKENS)

    def _determine_variable_type(self, var_name: str) -> VariableType:
        """
        Determine the type of a variable based on its name.

        Args:
            var_name: The variable name

        Returns:
            The determined variable type
        """
        if var_name in self._critical_vars:
            return VariableType.CRITICAL
        if self.is_sensitive_var(var_name):
            return VariableType.SENSITIVE
        if var_name in self._default_registered_keys:
            return VariableType.DEFAULT
        return VariableType.STANDARD

    def _validate_variable_name(self, var_name: str) -> bool:
        """
        Validate that a variable name is properly formatted.

        Args:
            var_name: The variable name to validate

        Returns:
            True if valid, False otherwise
        """
        if not var_name or not isinstance(var_name, str):
            log_error_safe(
                logger,
                "Invalid variable name: must be non-empty string",
                prefix="FALLBACK",
            )
            return False

        # Check for valid characters
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*$", var_name):
            log_error_safe(
                logger,
                "Invalid variable name format: {var_name}",
                prefix="FALLBACK",
                var_name=var_name,
            )
            return False

        return True

    def load_from_config(self, config_path: str) -> bool:
        """
        Load fallback configurations from a YAML file.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            True if configuration was loaded successfully
        """
        try:
            import yaml

            config_file = Path(config_path)
            if not config_file.exists():
                log_error_safe(
                    logger,
                    "Configuration file not found: {path}",
                    prefix="FALLBACK",
                    path=config_path,
                )
                return False

            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            if not config:
                log_warning_safe(
                    logger,
                    "Empty fallback configuration in {path}",
                    prefix="FALLBACK",
                    path=config_path,
                )
                return False

            # Process critical variables first
            if "critical_variables" in config:
                self.mark_as_critical(config["critical_variables"])
                log_info_safe(
                    logger,
                    "Loaded {count} critical variables from {path}",
                    prefix="FALLBACK",
                    count=len(config["critical_variables"]),
                    path=config_path,
                )

            # Then register fallbacks
            if "fallbacks" in config:
                for var_name, value in config["fallbacks"].items():
                    self.register_fallback(var_name, value)

                log_info_safe(
                    logger,
                    "Loaded {count} fallbacks from {path}",
                    prefix="FALLBACK",
                    count=len(config["fallbacks"]),
                    path=config_path,
                )

            return True

        except yaml.YAMLError as e:
            log_error_safe(
                logger,
                "YAML parsing error in {path}: {error}",
                prefix="FALLBACK",
                path=config_path,
                error=str(e),
            )
            return False
        except Exception as e:
            log_error_safe(
                logger,
                "Error loading fallback configuration: {error}",
                prefix="FALLBACK",
                error=str(e),
            )
            return False

    def scan_template_variables(
        self, template_dir: str, pattern: str = "*.j2"
    ) -> Set[str]:
        """
        Scan templates to discover used variables.

        Args:
            template_dir: Directory containing template files
            pattern: Glob pattern for matching template files

        Returns:
            Set of discovered variable names
        """
        discovered_vars = set()
        template_path = Path(template_dir)

        if not template_path.exists():
            log_error_safe(
                logger,
                "Template directory not found: {dir}",
                prefix="FALLBACK",
                dir=template_dir,
            )
            return discovered_vars

        # Find all template files
        template_files = list(template_path.rglob(pattern))

        log_info_safe(
            logger,
            "Scanning {count} template files in {dir}",
            prefix="FALLBACK",
            count=len(template_files),
            dir=template_dir,
        )

        for file_path in template_files:
            try:
                content = file_path.read_text()

                # Extract variable names
                for match in self.JINJA_VAR_PATTERN.finditer(content):
                    var_name = match.group(1) or match.group(2)
                    if var_name:
                        discovered_vars.add(var_name)

            except Exception as e:
                log_warning_safe(
                    logger,
                    "Error scanning template {path}: {error}",
                    prefix="FALLBACK",
                    path=file_path,
                    error=str(e),
                )

        return discovered_vars

    def validate_templates_for_critical_vars(
        self, template_dir: str, pattern: str = "*.j2"
    ) -> bool:
        """
        Validate templates don't use critical variables directly.

        This method maintains backward compatibility by returning just a bool.
        Use validate_templates_with_details() for the full tuple return.

        Args:
            template_dir: Directory containing template files
            pattern: Glob pattern for matching template files

        Returns:
            True if no critical variables are found in templates, False otherwise
        """
        is_valid, _ = self.validate_templates_with_details(template_dir, pattern)
        return is_valid

    def validate_templates_with_details(
        self, template_dir: str, pattern: str = "*.j2"
    ) -> Tuple[bool, Set[str]]:
        """
        Validate templates don't use critical variables directly with details.

        Args:
            template_dir: Directory containing template files
            pattern: Glob pattern for matching template files

        Returns:
            Tuple of (is_valid, critical_vars_found)
        """
        all_template_vars = self.scan_template_variables(template_dir, pattern)
        critical_vars_in_templates = set()

        for var in all_template_vars:
            # Check direct critical variable usage
            if var in self._critical_vars:
                critical_vars_in_templates.add(var)
                continue

            # Check if any parent path is critical
            if "." in var:
                parts = self._split_path(var)
                for i in range(1, len(parts)):
                    parent_path = ".".join(parts[: i + 1])
                    if parent_path in self._critical_vars:
                        critical_vars_in_templates.add(var)
                        break

        if critical_vars_in_templates:
            log_error_safe(
                logger,
                "Critical variables found in templates: {vars}",
                prefix="FALLBACK",
                vars=", ".join(sorted(critical_vars_in_templates)),
            )
            return False, critical_vars_in_templates

        log_info_safe(
            logger,
            "No critical variables found in templates - validation passed",
            prefix="FALLBACK",
        )
        return True, set()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about registered fallbacks.

        Returns:
            Dictionary with statistics about the fallback manager
        """
        stats = {
            "total_variables": len(self._variables),
            "critical_variables": len(self._critical_vars),
            "default_variables": len(self._default_registered_keys),
            "dynamic_handlers": sum(
                1 for v in self._variables.values() if v.is_dynamic
            ),
            "by_type": {},
        }

        # Count by type
        for var_type in VariableType:
            count = sum(1 for v in self._variables.values() if v.var_type == var_type)
            stats["by_type"][var_type.value] = count

        return stats

    def export_config(self, output_path: str) -> bool:
        """
        Export current configuration to a YAML file.

        Args:
            output_path: Path to write the configuration

        Returns:
            True if exported successfully
        """
        try:
            import yaml

            config = {
                "critical_variables": sorted(self._critical_vars),
                "fallbacks": {},
            }

            # Export non-dynamic, non-critical variables
            for var_name, metadata in self._variables.items():
                if var_name in self._critical_vars:
                    continue
                if metadata.is_dynamic:
                    continue
                if self.is_sensitive_var(var_name):
                    continue

                config["fallbacks"][var_name] = metadata.value

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=True)

            log_info_safe(
                logger,
                "Exported configuration to {path}",
                prefix="FALLBACK",
                path=output_path,
            )
            return True

        except Exception as e:
            log_error_safe(
                logger,
                "Failed to export configuration: {error}",
                prefix="FALLBACK",
                error=str(e),
            )
            return False

    def clear(self) -> None:
        """Clear all registered fallbacks and reset to defaults."""
        self._variables.clear()
        self._critical_vars.clear()
        self._default_registered_keys.clear()
        self._path_cache.clear()

        # Legacy compatibility
        self._fallbacks.clear()
        self._default_handlers.clear()

        # Re-register defaults
        self._register_default_fallbacks()

        log_info_safe(
            logger, "Cleared all fallbacks and reset to defaults", prefix="FALLBACK"
        )
