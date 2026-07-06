"""
file_utils.py
-------------
Filesystem helper utilities for the RevenuePulse AI ETL pipeline.

Functions:
  - ensure_dir(path)        : Create directory (parents) if not exists
  - read_csv(path, **kw)    : Safe CSV reader with logging
  - save_csv(df, path, **kw): Safe CSV writer with logging
"""

from pathlib import Path
from typing import Optional

import pandas as pd

from .logger import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────
# Directory helpers
# ──────────────────────────────────────────────

def ensure_dir(path: Path) -> Path:
    """
    Create *path* and all missing parent directories if they do not exist.

    Args:
        path: The directory path to create.

    Returns:
        The resolved Path object.
    """
    resolved = Path(path).resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    logger.debug("Directory ensured: %s", resolved)
    return resolved


# ──────────────────────────────────────────────
# CSV helpers
# ──────────────────────────────────────────────

def read_csv(
    path: Path,
    dtype: Optional[dict] = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Read a CSV file into a pandas DataFrame with error handling.

    Args:
        path:  Absolute or relative path to the CSV file.
        dtype: Optional column dtype mapping passed to pd.read_csv.
        **kwargs: Additional keyword arguments forwarded to pd.read_csv.

    Returns:
        DataFrame with the CSV contents.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError:        If the file is empty.
    """
    resolved = Path(path).resolve()

    if not resolved.exists():
        raise FileNotFoundError(f"CSV not found: {resolved}")

    if resolved.stat().st_size == 0:
        raise ValueError(f"CSV file is empty: {resolved}")

    logger.info("Reading CSV: %s", resolved)

    df = pd.read_csv(resolved, dtype=dtype, low_memory=False, **kwargs)

    logger.info(
        "Loaded %s | rows=%d | cols=%d",
        resolved.name, len(df), len(df.columns),
    )
    return df


def save_csv(
    df: pd.DataFrame,
    path: Path,
    index: bool = False,
    **kwargs,
) -> Path:
    """
    Save a DataFrame to a CSV file, creating parent directories if needed.

    Args:
        df:     DataFrame to save.
        path:   Target file path.
        index:  Whether to write the row index (default False).
        **kwargs: Additional keyword arguments forwarded to df.to_csv.

    Returns:
        The resolved Path where the file was saved.
    """
    resolved = Path(path).resolve()
    ensure_dir(resolved.parent)

    df.to_csv(resolved, index=index, **kwargs)

    logger.info(
        "Saved CSV: %s | rows=%d | cols=%d",
        resolved.name, len(df), len(df.columns),
    )
    return resolved
