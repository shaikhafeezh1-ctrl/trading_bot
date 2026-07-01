"""
Centralized logging configuration for the trading bot.

Logs go to both the console (INFO+) and a rotating log file (DEBUG+),
so every API request, response, and error is captured for audit /
debugging without flooding the terminal.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "trading_bot.log"


def setup_logging(level: int = logging.DEBUG) -> logging.Logger:
    """
    Configure and return the bot's root logger.

    - File handler: DEBUG and above, full detail, rotates at 2MB (keeps 5 backups)
    - Console handler: INFO and above, concise, for user-facing feedback
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(level)

    # Avoid duplicate handlers if setup_logging() is called more than once
    if logger.handlers:
        return logger

    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    console_formatter = logging.Formatter("%(levelname)-8s | %(message)s")

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()
