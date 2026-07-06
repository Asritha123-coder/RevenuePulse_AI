"""
utils.py
--------
Utility helper module for the ML layer. Setup logging to logs/ml.log and
handles database reading to Pandas DataFrames.
"""

import os
import sys
import logging
import decimal
from logging.handlers import RotatingFileHandler
from pathlib import Path
import pandas as pd
from sqlalchemy import text

# Add backend directory to sys.path to enable imports
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.database import engine
from app.utils.file_utils import ensure_dir

PROJECT_ROOT = BACKEND_DIR.parent
LOGS_DIR = PROJECT_ROOT / "logs"
ensure_dir(LOGS_DIR)

# ── Set up specific logger for logs/ml.log ─────────────────────────────────────
ml_logger = logging.getLogger("ml")
ml_logger.setLevel(logging.INFO)
if ml_logger.hasHandlers():
    ml_logger.handlers.clear()

file_handler = RotatingFileHandler(
    LOGS_DIR / "ml.log",
    maxBytes=10*1024*1024,
    backupCount=3,
    encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
ml_logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
ml_logger.addHandler(console_handler)


def get_ml_logger(name: str) -> logging.Logger:
    """Return a logger child of the main ml logger."""
    return logging.getLogger(f"ml.{name}")


def _coerce_decimals(df: pd.DataFrame) -> pd.DataFrame:
    """
    PostgreSQL NUMERIC/DECIMAL columns are returned as decimal.Decimal objects.
    Cast any such columns to float64 so arithmetic works correctly with numpy/pandas.
    """
    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna()
            if len(sample) > 0 and isinstance(sample.iloc[0], decimal.Decimal):
                df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def read_table_to_df(table_name: str) -> pd.DataFrame:
    """
    Read an entire table from PostgreSQL and return a Pandas DataFrame.
    All NUMERIC/DECIMAL columns are automatically coerced to float64.
    """
    logger = get_ml_logger("utils")
    logger.info("Reading table %s from PostgreSQL...", table_name)
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name};"))
            if not result.returns_rows:
                return pd.DataFrame()
            cols = result.keys()
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=cols)
            df = _coerce_decimals(df)
            logger.info("Successfully loaded table %s | shape=%s", table_name, str(df.shape))
            return df
    except Exception as e:
        logger.error("Failed to read table %s: %s", table_name, e, exc_info=True)
        raise
