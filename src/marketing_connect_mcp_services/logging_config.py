"""
Logging Configuration
=====================

Centralized logging setup for the application.

USAGE:
------
    # At application startup (e.g., in cli.py):
    from marketing_connect_mcp_services.logging_config import setup_logging
    setup_logging()

    # In any module:
    import logging
    logger = logging.getLogger(__name__)
    logger.info("This is a log message")

LOG LEVELS:
-----------
    DEBUG    - Detailed information for debugging
    INFO     - Confirmation that things are working
    WARNING  - Something unexpected happened, but the app still works
    ERROR    - A more serious problem
    CRITICAL - A very serious error, the app may not continue

CONFIGURATION:
--------------
    Set via environment variables:
    - MCP_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL
    - MCP_DEBUG=true (sets log level to DEBUG automatically)
"""

import logging
import sys
from datetime import UTC, datetime
from typing import Any

from marketing_connect_mcp_services.config import settings


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors for different log levels.

    Colors only applied when outputting to a terminal (TTY).
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, fmt: str | None = None, use_colors: bool = True):
        super().__init__(fmt)
        self.use_colors = use_colors and sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        # Add timestamp in ISO format
        record.timestamp = datetime.now(UTC).isoformat()

        # Apply color if enabled
        if self.use_colors:
            color = self.COLORS.get(record.levelname, "")
            record.levelname = f"{color}{record.levelname}{self.RESET}"

        return super().format(record)


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Useful for log aggregation systems (ELK, Splunk, CloudWatch, etc.).
    """

    def format(self, record: logging.LogRecord) -> str:
        import json

        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any extra fields
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data)


def get_log_level() -> int:
    """
    Determine the logging level from settings.

    If debug mode is enabled, always use DEBUG.
    Otherwise, use the configured log level.
    """
    if settings.debug:
        return logging.DEBUG

    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    return level_map.get(settings.log_level.upper(), logging.INFO)


def setup_logging(
    use_json: bool = False,
    use_colors: bool = True,
) -> None:
    """
    Configure logging for the entire application.

    This should be called once at application startup, before any
    logging calls are made.

    Args:
        use_json: If True, output logs in JSON format (for log aggregation)
        use_colors: If True, colorize log output (only works in terminals)

    Example:
        # In cli.py or __main__.py:
        from marketing_connect_mcp_services.logging_config import setup_logging
        setup_logging()
    """
    log_level = get_log_level()

    # Create root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers (in case of reconfiguration)
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)

    # Choose formatter based on configuration
    formatter: logging.Formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        # Human-readable format with timestamp, level, logger name, and message
        log_format = "%(timestamp)s | %(levelname)-8s | %(name)s | %(message)s"
        formatter = ColoredFormatter(log_format, use_colors=use_colors)

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set levels for third-party libraries to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging configured: level={settings.log_level}, debug={settings.debug}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Convenience function for consistent logger naming.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for adding extra context to log messages.

    Usage:
        with LogContext(request_id="abc123", user_id="user1"):
            logger.info("Processing request")  # Will include request_id and user_id
    """

    def __init__(self, **kwargs: Any):
        self.extra = kwargs
        self._old_factory: Any = None

    def __enter__(self) -> "LogContext":
        self._old_factory = logging.getLogRecordFactory()

        extra = self.extra
        old_factory = self._old_factory

        def factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
            record: logging.LogRecord = old_factory(*args, **kwargs)
            record.extra_data = extra
            return record

        logging.setLogRecordFactory(factory)
        return self

    def __exit__(self, *args: Any) -> None:
        logging.setLogRecordFactory(self._old_factory)
