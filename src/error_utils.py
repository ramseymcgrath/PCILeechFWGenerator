#!/usr/bin/env python3
"""
Error handling utilities for cleaner exception management.

This module provides utilities to extract root causes from exception chains
and format error messages in a more user-friendly way.
"""

import logging
from typing import Optional


def extract_root_cause(exception: Exception) -> str:
    """
    Extract the root cause from an exception chain.

    Args:
        exception: The exception to extract the root cause from

    Returns:
        The root cause message as a string
    """
    root_cause = str(exception)
    current = exception

    # Walk the exception chain to find the root cause
    while hasattr(current, "__cause__") and current.__cause__:
        current = current.__cause__
        root_cause = str(current)

    return root_cause


def log_error_with_root_cause(
    logger: logging.Logger,
    message: str,
    exception: Exception,
    show_full_traceback: bool = False,
) -> None:
    """
    Log an error with the root cause extracted from the exception chain.

    Args:
        logger: The logger to use
        message: The base error message
        exception: The exception that occurred
        show_full_traceback: Whether to show the full traceback (default: False)
    """
    root_cause = extract_root_cause(exception)
    logger.error("%s: %s", message, root_cause)

    if show_full_traceback or logger.isEnabledFor(logging.DEBUG):
        logger.debug("Full traceback:", exc_info=True)


def format_concise_error(message: str, exception: Exception) -> str:
    """
    Format a concise error message with root cause.

    Args:
        message: The base error message
        exception: The exception that occurred

    Returns:
        A formatted error message with root cause
    """
    root_cause = extract_root_cause(exception)
    return f"{message}: {root_cause}"
