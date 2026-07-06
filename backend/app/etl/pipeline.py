"""
pipeline.py
-----------
Master ETL Pipeline for the RevenuePulse AI Platform.
Executes the full pipeline workflow:
  1. Extract raw CSVs from `datasets/raw/`
  2. Transform and feature-engineer dataframes
  3. Validate DataFrames and generate report
  4. Load cleaned datasets to PostgreSQL
  5. Generate statistics and metrics

Usage:
    python backend/app/etl/pipeline.py
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any

import pandas as pd

# Add backend directory to sys.path to enable imports
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.utils.logger import get_logger
from app.utils.file_utils import save_csv, ensure_dir
from app.database.connection import test_connection
from app.etl.extract import extract_all
from app.etl.transform import transform_all
from app.etl.validate import validate_all
from app.etl.load import load_all

logger = get_logger(__name__)


def run_pipeline() -> Dict[str, Any]:
    """
    Execute the entire ETL pipeline.
    
    Returns:
        Dict summarizing pipeline status, row counts, and statistics.
    """
    logger.info("=" * 60)
    logger.info("  RevenuePulse AI - Starting Master ETL Pipeline Execution")
    logger.info("=" * 60)
    
    pipeline_start = time.time()
    project_root = BACKEND_DIR.parent
    
    raw_dir = project_root / "datasets" / "raw"
    processed_dir = project_root / "datasets" / "processed"
    reports_dir = project_root / "reports"
    
    # Pre-checks
    logger.info("Verifying PostgreSQL database connection...")
    if not test_connection():
        logger.critical("Database connection test failed. Aborting pipeline.")
        raise ConnectionError("Database connection check failed.")
        
    # Ensure dirs exist
    ensure_dir(processed_dir)
    ensure_dir(reports_dir)
    
    status_summary = {
        "status": "FAILED",
        "extract_time_s": 0.0,
        "transform_time_s": 0.0,
        "validate_time_s": 0.0,
        "load_time_s": 0.0,
        "total_time_s": 0.0,
        "records_loaded": 0,
        "error_message": ""
    }
    
    try:
        # 1. EXTRACT
        t0 = time.time()
        raw_dfs = extract_all(raw_dir)
        status_summary["extract_time_s"] = round(time.time() - t0, 2)
        logger.info("Extract phase completed in %ss", status_summary["extract_time_s"])
        
        # 2. TRANSFORM
        t0 = time.time()
        transformed_dfs = transform_all(raw_dfs)
        status_summary["transform_time_s"] = round(time.time() - t0, 2)
        logger.info("Transform phase completed in %ss", status_summary["transform_time_s"])
        
        # Save processed CSVs locally (Standard best practice for data lineage and auditing)
        logger.info("Saving transformed datasets to %s...", processed_dir)
        for key, df in transformed_dfs.items():
            save_csv(df, processed_dir / f"{key}.csv")
            
        # 3. VALIDATE
        t0 = time.time()
        validation_report = validate_all(transformed_dfs, reports_dir)
        status_summary["validate_time_s"] = round(time.time() - t0, 2)
        logger.info("Validation phase completed in %ss", status_summary["validate_time_s"])
        
        # Count total issues
        issue_count = 0
        if not validation_report.empty and "issue_count" in validation_report.columns:
            issue_count = validation_report["issue_count"].sum()
        logger.info("Validation issues found: %d", issue_count)
        
        # 4. LOAD
        t0 = time.time()
        load_summary = load_all(transformed_dfs, reports_dir)
        status_summary["load_time_s"] = round(time.time() - t0, 2)
        logger.info("Load phase completed in %ss", status_summary["load_time_s"])
        
        # Sum records loaded
        records_loaded = load_summary["rows_loaded"].sum()
        status_summary["records_loaded"] = int(records_loaded)
        
        # Complete pipeline
        total_time = round(time.time() - pipeline_start, 2)
        status_summary["total_time_s"] = total_time
        status_summary["status"] = "SUCCESS"
        
        logger.info("=" * 60)
        logger.info("  RevenuePulse AI - Pipeline Executed Successfully!")
        logger.info("  Total Records Loaded : %d", records_loaded)
        logger.info("  Total Elapsed Time   : %ss", total_time)
        logger.info("=" * 60)
        
    except Exception as e:
        total_time = round(time.time() - pipeline_start, 2)
        status_summary["total_time_s"] = total_time
        status_summary["status"] = "FAILED"
        status_summary["error_message"] = str(e)
        logger.critical("Pipeline execution FAILED: %s", e, exc_info=True)
        
    # Save pipeline stats
    stats_df = pd.DataFrame([status_summary])
    save_csv(stats_df, reports_dir / "pipeline_statistics.csv")
    
    return status_summary


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as exc:
        print(f"\n[FATAL] ETL pipeline run aborted: {exc}")
        sys.exit(1)
