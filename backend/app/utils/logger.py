"""
logger.py
---------
Centralised logging configuration for the RevenuePulse AI ETL pipeline.

Creates two handlers:
  1. RotatingFileHandler  → logs/etl.log      (all levels INFO+)
  2. RotatingFileHandler  → logs/errors.log   (ERROR+ only)
  3. StreamHandler        → console            (INFO+)

Usage:
    from backend.app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Pipeline started")
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ── Resolve log directory relative to project root ────────────────────────────
# This file lives at:  backend/app/utils/logger.py
# Project root is 3 levels up.
_UTILS_DIR   = Path(__file__).resolve().parent
_PROJECT_ROOT = _UTILS_DIR.parents[3]   # RevenuePulse/
_LOG_DIR     = _PROJECT_ROOT / "logs"

# Ensure the log directory exists
_LOG_DIR.mkdir(parents=True, exist_ok=True)

_ETL_LOG_PATH    = _LOG_DIR / "etl.log"
_ERROR_LOG_PATH  = _LOG_DIR / "errors.log"

# Max 10 MB per file, keep 5 backups
_MAX_BYTES   = 10 * 1024 * 1024
_BACKUP_COUNT = 5

_LOG_FORMAT  = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ── Module-level flag: configure only once ────────────────────────────────────
_configured = False


def _configure_root_logger() -> None:
    """Set up handlers on the root logger exactly once."""
    global _configured
    if _configured:
        return

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)       # capture everything; handlers filter

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # ── Handler 1: etl.log (INFO+) ────────────────────────────────────────
    etl_handler = RotatingFileHandler(
        _ETL_LOG_PATH,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    etl_handler.setLevel(logging.INFO)
    etl_handler.setFormatter(formatter)

    # ── Handler 2: errors.log (ERROR+) ────────────────────────────────────
    error_handler = RotatingFileHandler(
        _ERROR_LOG_PATH,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # ── Handler 3: console (INFO+) ────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root.addHandler(etl_handler)
    root.addHandler(error_handler)
    root.addHandler(console_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger with all handlers configured.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        logging.Logger instance ready for use.
    """
    _configure_root_logger()
    return logging.getLogger(name)
