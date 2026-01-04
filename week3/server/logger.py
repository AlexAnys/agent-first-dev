"""File-based logging for STDIO MCP servers.

CRITICAL: STDIO servers must NOT write to stdout as it's reserved for MCP protocol.
All logs go to file only.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "gmail_mcp",
    log_file: Optional[Path] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """Configure logger for STDIO server.

    Logs to both file and stderr. CRITICAL: Never use stdout as it's 
    reserved for MCP protocol communication.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    log_path = log_file or Path.home() / ".gmail_mcp" / "server.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler for persistent logs
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Stderr handler for real-time debugging (safe for STDIO servers)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(level)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    return logger


# Global logger instance
logger = setup_logger()
