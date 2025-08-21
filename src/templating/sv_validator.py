"""Validation module for SystemVerilog generation."""

import logging
from typing import Any, Dict, List, Optional, Union

from src.device_clone.device_config import DeviceClass, DeviceType
from src.string_utils import log_error_safe, log_warning_safe

from .sv_constants import SV_CONSTANTS, SV_VALIDATION
from .template_renderer import TemplateRenderError


class SVValidator:
    """Handles validation for SystemVerilog generation."""

    def __init__(self, logger: logging.Logger):
        """Initialize the validator with a logger."""
        self.logger = logger
        self.constants = SV_CONSTANTS
        self.messages = SV_VALIDATION.ERROR_MESSAGES

    def validate_device_config(self, device_config: Any) -> None:
        """
        Validate device configuration for safe firmware generation.

        Args:
            device_config: Device configuration object

        Raises:
            ValueError: If device configuration is invalid
        """
        if not device_config:
            raise ValueError(self.messages["missing_device_config"])

        # Validate device type and class
        self._validate_device_enums(device_config)

        # Validate numeric parameters
        self._validate_numeric_params(device_config)

    def validate_template_context(self, context: Any) -> None:
        """
        Validate template context before processing.

        Args:
            context: Template context to validate

        Raises:
            ValueError: If context is invalid
            TemplateRenderError: If critical fields are missing
        """
        if not context:
            raise ValueError(
                self.messages["no_template_context"].format(
                    operation="template rendering"
                )
            )

        if not isinstance(context, dict):
            raise ValueError(
                self.messages["context_not_dict"].format(
                    type_name=type(context).__name__
                )
            )

        # Validate critical fields
        self._validate_critical_fields(context)

    def validate_device_identification(self, device_config: Dict[str, Any]) -> None:
        """
        Validate critical device identification fields.

        Args:
            device_config: Device configuration dictionary

        Raises:
            TemplateRenderError: If validation fails
        """
        required_fields = ["vendor_id", "device_id"]
        missing_fields = []
        invalid_fields = []

        for field in required_fields:
            value = device_config.get(field)
            if not value:
                missing_fields.append(field)
            elif not isinstance(value, str) or len(value) != 4:
                invalid_fields.append(
                    f"{field}='{value}' (must be 4-character hex string)"
                )

        if missing_fields or invalid_fields:
            error_details = []
            if missing_fields:
                error_details.append(f"Missing fields: {', '.join(missing_fields)}")
            if invalid_fields:
                error_details.append(f"Invalid fields: {', '.join(invalid_fields)}")

            error_msg = (
                f"Critical device identification validation failed: {'; '.join(error_details)}. "
                "Cannot generate safe firmware without proper device identification."
            )
            log_error_safe(self.logger, error_msg)
            raise TemplateRenderError(error_msg)

    def validate_numeric_range(
        self,
        param_name: str,
        value: Any,
        min_value: Union[int, float],
        max_value: Union[int, float],
    ) -> Optional[str]:
        """
        Validate a numeric parameter against a range.

        Args:
            param_name: Name of the parameter
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Returns:
            Error message if validation fails, None otherwise
        """
        if not isinstance(value, (int, float)):
            return f"{param_name} must be a number, got {type(value).__name__}"

        if value < min_value or value > max_value:
            return self.messages["invalid_numeric_param"].format(
                param=param_name, value=value, min=min_value, max=max_value
            )

        return None

    def _validate_device_enums(self, device_config: Any) -> None:
        """Validate device type and class enums."""
        if not hasattr(device_config.device_type, "value"):
            raise ValueError(
                self.messages["invalid_device_type"].format(
                    value=device_config.device_type
                )
            )

        if not hasattr(device_config.device_class, "value"):
            raise ValueError(
                self.messages["invalid_device_class"].format(
                    value=device_config.device_class
                )
            )

    def _validate_numeric_params(self, device_config: Any) -> None:
        """Validate numeric parameters of device configuration."""
        validations = [
            (
                "max_payload_size",
                device_config.max_payload_size,
                self.constants.MIN_PAYLOAD_SIZE,
                self.constants.MAX_PAYLOAD_SIZE,
            ),
            (
                "max_read_request_size",
                device_config.max_read_request_size,
                self.constants.MIN_READ_REQUEST_SIZE,
                self.constants.MAX_READ_REQUEST_SIZE,
            ),
            (
                "tx_queue_depth",
                device_config.tx_queue_depth,
                self.constants.MIN_QUEUE_DEPTH,
                self.constants.MAX_QUEUE_DEPTH,
            ),
            (
                "rx_queue_depth",
                device_config.rx_queue_depth,
                self.constants.MIN_QUEUE_DEPTH,
                self.constants.MAX_QUEUE_DEPTH,
            ),
        ]

        for param_name, value, min_val, max_val in validations:
            error = self.validate_numeric_range(param_name, value, min_val, max_val)
            if error:
                raise ValueError(error)

    def _validate_critical_fields(self, context: Dict[str, Any]) -> None:
        """Validate critical fields in template context."""
        # Check for device_config
        if "device_config" not in context:
            raise TemplateRenderError(self.messages["missing_critical_field"])

        device_config = context["device_config"]
        if not isinstance(device_config, dict):
            raise TemplateRenderError(
                self.messages["device_config_not_dict"].format(
                    type_name=type(device_config).__name__
                )
            )

        # Check for device_signature
        if "device_signature" not in context:
            raise TemplateRenderError(self.messages["missing_device_signature"])

        if not context["device_signature"]:
            raise TemplateRenderError(self.messages["empty_device_signature"])

    def validate_template_requirements(
        self, device_config: Any, power_config: Any, error_config: Any, perf_config: Any
    ) -> None:
        """
        Comprehensive validation of all template requirements.

        Args:
            device_config: Device configuration
            power_config: Power management configuration
            error_config: Error handling configuration
            perf_config: Performance configuration

        Raises:
            TemplateRenderError: If validation fails
        """
        errors = []
        warnings = []

        # Validate device config
        if not device_config:
            errors.append("device_config is None or missing")
        else:
            # Validate required attributes
            required_attrs = [
                "device_type",
                "device_class",
                "max_payload_size",
                "max_read_request_size",
                "tx_queue_depth",
                "rx_queue_depth",
            ]

            for attr in required_attrs:
                if not hasattr(device_config, attr):
                    errors.append(f"device_config.{attr} is missing")

        # Log warnings
        for warning in warnings:
            log_warning_safe(self.logger, f"Template validation warning: {warning}")

        # Raise error if any critical issues found
        if errors:
            error_msg = self.messages["validation_failed"].format(
                count=len(errors), errors="\n".join(f"  - {error}" for error in errors)
            )
            log_error_safe(self.logger, error_msg)
            raise TemplateRenderError(error_msg)
