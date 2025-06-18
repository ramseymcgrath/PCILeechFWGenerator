"""Centralized logging setup with color support."""

import logging
import sys
from typing import Optional

try:
    from colorlog import ColoredFormatter

    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


def setup_logging(
    level: int = logging.INFO, log_file: Optional[str] = "generate.log"
) -> None:
    """Setup logging with color support using colorlog.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional log file path (default: generate.log)
    """
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handlers = []

    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)

    if HAS_COLORLOG and hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        # Use colorlog for colored output
        console_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    else:
        # Fallback to basic formatter
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )

    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    # File handler (no colors)
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a")
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,  # Override any existing configuration
    )

    # Log the setup
    logger = logging.getLogger(__name__)
    if HAS_COLORLOG:
        logger.debug("Logging setup complete with colorlog support")
    else:
        logger.warning("colorlog not available, using basic formatting")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Fallback ColoredFormatter for when colorlog is not available
class FallbackColoredFormatter(logging.Formatter):
    """A logging formatter that adds ANSI color codes to log messages."""

    # ANSI color codes
    COLORS = {
        "RED": "\033[91m",
        "YELLOW": "\033[93m",
        "GREEN": "\033[92m",
        "CYAN": "\033[96m",
        "RESET": "\033[0m",
    }

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        # Only use colors for TTY outputs
        self.use_colors = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def format(self, record):
        formatted = super().format(record)
        if self.use_colors:
            if record.levelno >= logging.ERROR:
                return f"{self.COLORS['RED']}{formatted}{self.COLORS['RESET']}"
            elif record.levelno >= logging.WARNING:
                return f"{self.COLORS['YELLOW']}{formatted}{self.COLORS['RESET']}"
            elif record.levelno >= logging.INFO:
                return f"{self.COLORS['GREEN']}{formatted}{self.COLORS['RESET']}"
            elif record.levelno >= logging.DEBUG:
                return f"{self.COLORS['CYAN']}{formatted}{self.COLORS['RESET']}"
        return formatted


# If colorlog is not available, monkey-patch it
if not HAS_COLORLOG:
    ColoredFormatter = FallbackColoredFormatter
