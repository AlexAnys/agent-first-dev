"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path


def setup_logging() -> None:
    """Configure logging for the application.

    Sets up both console and file logging with appropriate formats and levels.
    Creates a logs directory if it doesn't exist.
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
        ],
    )

    # Set specific log levels for third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: Name of the logger (typically __name__ from the calling module).

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
