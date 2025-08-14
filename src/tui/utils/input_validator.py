"""
Input validation utilities for PCILeech TUI application.

This module provides comprehensive validation for various user inputs,
including file paths, PCI BDF identifiers, and configuration values.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class InputValidator:
    """Provides comprehensive input validation for the PCILeech TUI application."""

    @staticmethod
    def validate_file_path(path: str) -> Tuple[bool, str]:
        """
        Validate file path input.

        Args:
            path: The file path to validate.

        Returns:
            A tuple containing (is_valid, error_message).
            If valid, error_message will be empty.
        """
        try:
            p = Path(path)
            if not p.exists():
                return False, f"File does not exist: {path}"
            if not p.is_file():
                return False, f"Path is not a file: {path}"
            return True, ""
        except Exception as e:
            return False, f"Invalid path: {e}"

    @staticmethod
    def validate_directory_path(path: str) -> Tuple[bool, str]:
        """
        Validate directory path input.

        Args:
            path: The directory path to validate.

        Returns:
            A tuple containing (is_valid, error_message).
            If valid, error_message will be empty.
        """
        try:
            p = Path(path)
            if not p.exists():
                return False, f"Directory does not exist: {path}"
            if not p.is_dir():
                return False, f"Path is not a directory: {path}"
            if not os.access(p, os.W_OK):
                return False, f"Directory is not writable: {path}"
            return True, ""
        except Exception as e:
            return False, f"Invalid directory path: {e}"

    @staticmethod
    def validate_bdf(bdf: str) -> Tuple[bool, str]:
        """
        Validate PCI BDF format.

        Args:
            bdf: The PCI BDF identifier to validate (format: XXXX:XX:XX.X).

        Returns:
            A tuple containing (is_valid, error_message).
            If valid, error_message will be empty.
        """
        import re

        pattern = r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9a-fA-F]$"
        if re.match(pattern, bdf):
            return True, ""
        return False, "Invalid BDF format (expected: XXXX:XX:XX.X)"

    @staticmethod
    def validate_non_empty(value: str, field_name: str = "Value") -> Tuple[bool, str]:
        """
        Validate that a string is not empty.

        Args:
            value: The string to validate.
            field_name: Name of the field being validated (for error message).

        Returns:
            A tuple containing (is_valid, error_message).
            If valid, error_message will be empty.
        """
        if not value or value.strip() == "":
            return False, f"{field_name} cannot be empty"
        return True, ""

    @staticmethod
    def validate_numeric(value: str, field_name: str = "Value") -> Tuple[bool, str]:
        """
        Validate that a string can be converted to a number.

        Args:
            value: The string to validate.
            field_name: Name of the field being validated (for error message).

        Returns:
            A tuple containing (is_valid, error_message).
            If valid, error_message will be empty.
        """
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, f"{field_name} must be a number"

    @staticmethod
    def validate_integer(value: str, field_name: str = "Value") -> Tuple[bool, str]:
        """
        Validate that a string can be converted to an integer.

        Args:
            value: The string to validate.
            field_name: Name of the field being validated (for error message).

        Returns:
            A tuple containing (is_valid, error_message).
            If valid, error_message will be empty.
        """
        try:
            int(value)
            return True, ""
        except ValueError:
            return False, f"{field_name} must be an integer"

    @staticmethod
    def validate_in_range(
        value: str, min_val: float, max_val: float, field_name: str = "Value"
    ) -> Tuple[bool, str]:
        """
        Validate that a numeric string is within a specified range.

        Args:
            value: The string to validate.
            min_val: Minimum allowed value.
            max_val: Maximum allowed value.
            field_name: Name of the field being validated (for error message).

        Returns:
            A tuple containing (is_valid, error_message).
            If valid, error_message will be empty.
        """
        is_valid, error = InputValidator.validate_numeric(value, field_name)
        if not is_valid:
            return is_valid, error

        num_val = float(value)
        if num_val < min_val or num_val > max_val:
            return False, f"{field_name} must be between {min_val} and {max_val}"
        return True, ""

    @staticmethod
    def validate_in_choices(
        value: str, choices: List[str], field_name: str = "Value"
    ) -> Tuple[bool, str]:
        """
        Validate that a string is one of the specified choices.

        Args:
            value: The string to validate.
            choices: List of valid choices.
            field_name: Name of the field being validated (for error message).

        Returns:
            A tuple containing (is_valid, error_message).
            If valid, error_message will be empty.
        """
        if value not in choices:
            return False, f"{field_name} must be one of: {', '.join(choices)}"
        return True, ""

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a configuration dictionary.

        Args:
            config: The configuration dictionary to validate.

        Returns:
            A tuple containing (is_valid, error_message).
            If valid, error_message will be empty.
        """
        required_fields = ["device_id", "board_type", "output_directory"]

        for field in required_fields:
            if field not in config or not config[field]:
                return False, f"Missing required field: {field}"

        # Validate output directory if provided
        if "output_directory" in config and config["output_directory"]:
            output_dir = config["output_directory"]
            is_valid, error = InputValidator.validate_directory_path(output_dir)
            if not is_valid:
                return is_valid, error

        return True, ""
