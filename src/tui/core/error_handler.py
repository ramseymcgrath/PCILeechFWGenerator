"""
Error Handler for PCILeech TUI

Provides centralized error handling for the PCILeech TUI application.
"""

import logging
import traceback
from typing import Any, Dict, Optional

# Configure logging
logger = logging.getLogger("pcileech.tui.error_handler")


class ErrorHandler:
    """
    Centralized error handling system for the PCILeech TUI application.

    This class provides a consistent way to handle errors throughout the application,
    including logging, user notifications, and critical error reporting.
    """

    def __init__(self, app):
        """
        Initialize the error handler with the app instance.

        Args:
            app: The main TUI application instance
        """
        self.app = app

    def handle_error(
        self, error: Exception, context: str, severity: str = "error"
    ) -> None:
        """
        Centralized error handling with context

        Args:
            error: The exception that occurred
            context: Description of where/when the error occurred
            severity: Error severity level ("error", "warning", "critical")
        """
        error_msg = f"{context}: {str(error)}"

        # Log error details
        logger.error(f"Error in {context}", exc_info=True)

        # Show user-friendly message
        user_msg = self._get_user_friendly_message(error, context)
        self.app.notify(user_msg, severity=severity)

        # Report critical errors
        if severity == "critical":
            self._report_critical_error(error, context)

    def handle_operation_error(
        self, operation: str, error: Exception, severity: str = "error"
    ) -> None:
        """
        Handle errors that occur during specific operations with a standard format.

        Args:
            operation: The operation that failed (e.g., "scanning devices", "starting build")
            error: The exception that occurred
            severity: Error severity level ("error", "warning", "critical")
        """
        context = f"Failed while {operation}"
        self.handle_error(error, context, severity)

    def _get_user_friendly_message(self, error: Exception, context: str) -> str:
        """
        Generate a user-friendly error message based on the exception type and context.

        Args:
            error: The exception that occurred
            context: Description of where/when the error occurred

        Returns:
            A user-friendly error message
        """
        error_type = type(error).__name__

        # Known error types with specific user-friendly messages
        error_messages = {
            "FileNotFoundError": f"A required file could not be found: {str(error)}",
            "PermissionError": f"Permission denied: {str(error)}. Try running with sudo.",
            "ConnectionError": f"Connection failed: {str(error)}. Check network settings.",
            "TimeoutError": f"Operation timed out: {str(error)}. Try again later.",
            "ValueError": f"Invalid value: {str(error)}",
            "NotImplementedError": f"This feature is not implemented yet: {str(error)}",
        }

        # Return custom message if available, otherwise use a generic one with the context
        return error_messages.get(error_type, f"{context}: {str(error)}")

    def _report_critical_error(self, error: Exception, context: str) -> None:
        """
        Report critical errors for later analysis or immediate attention.

        Args:
            error: The exception that occurred
            context: Description of where/when the error occurred
        """
        # Get traceback information
        tb_str = "".join(traceback.format_tb(error.__traceback__))

        # Log with full details
        logger.critical(
            f"CRITICAL ERROR in {context}: {str(error)}\n{tb_str}", exc_info=True
        )

        # In a production environment, this could:
        # 1. Send error reports to a monitoring service
        # 2. Write to a dedicated error log file
        # 3. Show a more prominent UI notification

        # For now, we'll just show an additional notification with recovery instructions
        self.app.notify(
            "A critical error occurred. Please save your work and restart the application.",
            severity="error",
        )
