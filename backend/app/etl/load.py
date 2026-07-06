"""
load.py
-------
Load phase of the RevenuePulse AI ETL pipeline.
Loads cleaned DataFrames into the PostgreSQL database.
Handles transaction management, cascade clears, bulk inserts, and saves
`reports/etl_summary.csv`.
"""

import time
from pathlib import Path
from typing import Dict, List
import pandas as pd
from sqlalchemy import text

from ..database.database import engine
from ..utils.logger import get_logger
from ..utils.file_utils import save_csv

logger = get_logger(__name__)

# Forward loading order to respect foreign key constraints
LOAD_ORDER: List[str] = [
    "accounts",
    "contacts",
    "campaigns",
    "opportunities",
    "subscriptions",
    "product_usage",
    "website_activity",
    "support_tickets",
]


def clear_tables_in_transaction(conn) -> None:
    """Clear all database tables in reverse order of foreign key dependencies."""
    logger.info("Clearing existing tables in reverse order to avoid FK violations...")
    
    # We use TRUNCATE TABLE with CASCADE. Standard across PostgreSQL.
    for key in reversed(LOAD_ORDER):
        try:
            logger.info("Truncating table: %s", key)
            conn.execute(text(f"TRUNCATE TABLE {key} CASCADE;"))
        except Exception as e:
            logger.warning("Truncation check failed for %s: %s. Continuing anyway...", key, e)


def load_dataframe_to_db(df: pd.DataFrame, table_name: str, conn) -> int:
    """
    Load a single DataFrame into a PostgreSQL table using bulk inserting.
    
    Args:
        df: Cleaned pandas DataFrame.
        table_name: Database table name.
        conn: Active SQLAlchemy connection inside a transaction block.
        
    Returns:
        Number of rows successfully inserted.
    """
    logger.info("Bulk inserting %d rows into table: %s", len(df), table_name)
    
    # We must ensure dates and NaNs are properly converted. 
    # Pandas NaN values become NULL in PostgreSQL when calling to_sql.
    # Convert datetimes to string format or keep as datetime64[ns]
    df_load = df.copy()
    
    # Write to database using pandas to_sql with active connection
    df_load.to_sql(
        name=table_name,
        con=conn,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"  # Uses multi-row INSERT syntax for higher performance
    )
    
    return len(df_load)


def load_all(dfs: Dict[str, pd.DataFrame], reports_dir: Path) -> pd.DataFrame:
    """
    Load all transformed DataFrames into PostgreSQL inside a single transaction.
    
    Args:
        dfs: Dictionary of cleaned pandas DataFrames.
        reports_dir: Directory where ETL reports are saved.
        
    Returns:
        pd.DataFrame containing the ETL load execution summary.
    """
    logger.info("Initiating load phase to PostgreSQL database...")
    
    summary_rows = []
    success = True
    
    # Use engine.begin() which starts a transaction, commits on success, and rolls back on failure
    try:
        with engine.begin() as conn:
            # Clear existing tables first
            clear_tables_in_transaction(conn)
            
            for key in LOAD_ORDER:
                t0 = time.time()
                df = dfs[key]
                
                try:
                    rows_inserted = load_dataframe_to_db(df, key, conn)
                    elapsed = round(time.time() - t0, 2)
                    summary_rows.append({
                        "dataset": key,
                        "rows_loaded": rows_inserted,
                        "elapsed_seconds": elapsed,
                        "status": "SUCCESS",
                        "error_message": ""
                    })
                    logger.info("Loaded table %s: %d rows in %ss", key, rows_inserted, elapsed)
                except Exception as ex:
                    elapsed = round(time.time() - t0, 2)
                    logger.error("Failed to load table %s into database: %s", key, ex, exc_info=True)
                    summary_rows.append({
                        "dataset": key,
                        "rows_loaded": 0,
                        "elapsed_seconds": elapsed,
                        "status": "FAILED",
                        "error_message": str(ex)
                    })
                    success = False
                    raise ex  # Raise to trigger rollback of the entire transaction block
                    
    except Exception as e:
        logger.critical("Database transaction aborted! Rolling back all changes. Error: %s", e)
        success = False
        
    # Generate ETL summary report
    summary_df = pd.DataFrame(summary_rows)
    
    reports_dir.mkdir(parents=True, exist_ok=True)
    summary_path = reports_dir / "etl_summary.csv"
    save_csv(summary_df, summary_path)
    
    if not success:
        raise RuntimeError("Load phase failed. Database transaction was rolled back.")
        
    logger.info("Load phase completed successfully. ETL Summary saved to %s", summary_path)
    return summary_df
