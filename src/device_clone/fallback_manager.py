#!/usr/bin/env python3
"""
Fallback Manager - Centralized management of fallback policies

This module provides a centralized FallbackManager class that handles fallback policies
consistently across the codebase, implements user confirmation mechanisms, and tracks
and logs fallback events.
"""

import logging
import os
from typing import List, Optional, Set

from ..exceptions import PlatformCompatibilityError

# Production mode environment variable
PRODUCTION_MODE_ENV = "PCILEECH_PRODUCTION_MODE"


class FallbackManager:
    """
    Manages fallback policies and user confirmation across the codebase.

    This class centralizes all fallback decision-making, providing consistent
    policy enforcement, user confirmation mechanisms, and fallback event tracking.

    Attributes:
        mode (str): Fallback mode - "none" (fail-fast), "prompt" (ask user), or "auto" (allow)
        allowed_fallbacks (Set[str]): Set of explicitly allowed fallback types
        denied_fallbacks (Set[str]): Set of explicitly denied fallback types
        logger (logging.Logger): Logger for fallback events
        fallback_history (List[dict]): History of fallback events for tracking
    """

    def __init__(
        self,
        mode: str = "none",
        allowed_fallbacks: Optional[List[str]] = None,
        denied_fallbacks: Optional[List[str]] = None,
    ):
        """
        Initialize the fallback manager with the specified policies.

        Args:
            mode: Fallback mode - "none" (fail-fast), "prompt" (ask user), or "auto" (allow)
            allowed_fallbacks: List of fallback types that are explicitly allowed
            denied_fallbacks: List of fallback types that are explicitly denied
        """
        # Check if in production mode
        production_mode = os.environ.get(PRODUCTION_MODE_ENV, "false").lower() == "true"

        # In production mode, override settings to enforce fail-fast
        if production_mode:
            self.mode = "none"
            # Allow MSI-X and config-space fallbacks even in production mode
            self.allowed_fallbacks = {"msix", "config-space"}
            self.denied_fallbacks = {
                "build-integration",
                "module-import",
            }
        else:
            self.mode = mode
            self.allowed_fallbacks = set(allowed_fallbacks or [])
            self.denied_fallbacks = set(denied_fallbacks or [])

        self.logger = logging.getLogger("fallback_manager")
        self.fallback_history = []

        # Log initial configuration
        if production_mode:
            self.logger.info("Production mode enabled: All fallbacks disabled")
        else:
            self.logger.info(f"Fallback mode: {self.mode}")
            if self.allowed_fallbacks:
                self.logger.info(
                    f"Explicitly allowed fallbacks: {', '.join(self.allowed_fallbacks)}"
                )
            if self.denied_fallbacks:
                self.logger.info(
                    f"Explicitly denied fallbacks: {', '.join(self.denied_fallbacks)}"
                )

    def is_fallback_allowed(self, fallback_type: str) -> bool:
        """
        Check if a specific fallback is allowed based on configuration.

        Args:
            fallback_type: The type of fallback to check

        Returns:
            bool: True if the fallback is allowed, False otherwise
        """
        # Explicitly denied fallbacks are never allowed
        if fallback_type in self.denied_fallbacks:
            return False

        # In "none" mode, no fallbacks are allowed unless explicitly allowed
        if self.mode == "none" and fallback_type not in self.allowed_fallbacks:
            return False

        # In "auto" mode, all fallbacks are allowed unless explicitly denied
        if self.mode == "auto":
            return True

        # In "prompt" mode, explicitly allowed fallbacks don't need confirmation
        if fallback_type in self.allowed_fallbacks:
            return True

        # For "prompt" mode, we'll need to ask the user (handled in confirm_fallback)
        return self.mode == "prompt"

    def confirm_fallback(
        self, fallback_type: str, reason: str, implications: Optional[str] = None
    ) -> bool:
        """
        Get confirmation for using a fallback mechanism.

        Args:
            fallback_type: The type of fallback being considered
            reason: The reason for the fallback (usually an error message)
            implications: Optional description of the implications of using this fallback

        Returns:
            bool: True if the fallback is allowed, False otherwise
        """
        # First check if this fallback type is allowed at all
        if not self.is_fallback_allowed(fallback_type):
            self._log_fallback_event(fallback_type, reason, allowed=False)
            return False

        # For explicitly allowed fallbacks or auto mode, allow without confirmation
        if fallback_type in self.allowed_fallbacks or self.mode == "auto":
            self._log_fallback_event(fallback_type, reason, allowed=True)
            return True

        # For prompt mode, ask for confirmation
        if self.mode == "prompt":
            # Build the prompt message
            prompt = f"\n[WARNING] {fallback_type} failed: {reason}\n"
            if implications:
                prompt += f"Implications: {implications}\n"
            prompt += f"Allow fallback? [y/N]: "

            # Get user response
            response = input(prompt).lower()
            allowed = response in ("y", "yes")

            # Log the event
            self._log_fallback_event(fallback_type, reason, allowed=allowed)
            return allowed

        # Default to not allowing fallback
        return False

    def _log_fallback_event(
        self, fallback_type: str, reason: str, allowed: bool
    ) -> None:
        """
        Log a fallback event with appropriate level based on whether it was allowed.

        Args:
            fallback_type: The type of fallback
            reason: The reason for the fallback
            allowed: Whether the fallback was allowed
        """
        # Record in history
        self.fallback_history.append(
            {"type": fallback_type, "reason": reason, "allowed": allowed}
        )

        # Check if this is a platform compatibility issue to reduce redundant logging
        is_platform_error = (
            "requires Linux" in reason
            or "Current platform: Darwin" in reason
            or "only available on Linux" in reason
        )

        # Log with appropriate level
        if allowed:
            self.logger.warning(f"Using fallback for {fallback_type}: {reason}")
        else:
            if is_platform_error:
                # For platform compatibility issues, just log once at INFO level
                # since the detailed error was already logged by the platform check
                self.logger.info(
                    f"Fallback for {fallback_type} not allowed due to platform incompatibility"
                )
            else:
                self.logger.error(f"Fallback for {fallback_type} not allowed: {reason}")

    def get_fallback_history(self) -> List[dict]:
        """
        Get the history of fallback events.

        Returns:
            List of dictionaries containing fallback event details
        """
        return self.fallback_history
