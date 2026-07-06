"""
pipeline.py
-----------
ML pipeline coordinator. Runs data extraction, feature engineering,
model training, evaluation, registry, and reports creation.

Usage:
    python backend/app/ml/pipeline.py
"""

import sys
import time
from pathlib import Path

# Add backend directory to sys.path to enable imports
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.utils import get_ml_logger
from app.database.connection import test_connection
from app.ml.train import run_training_pipeline

logger = get_ml_logger("pipeline")


def execute_ml_pipeline() -> dict:
    """
    Check connection and run the entire machine learning pipeline.
    """
    logger.info("*" * 60)
    logger.info("  RevenuePulse AI - Executing Master ML Pipeline")
    logger.info("*" * 60)
    
    t0 = time.time()
    
    # 1. Connection Health Check
    if not test_connection():
        logger.critical("Database offline! Aborting ML pipeline execution.")
        raise ConnectionError("Database connection check failed.")
        
    try:
        # 2. Execute Training, Evaluation and Registry
        stats = run_training_pipeline()
        
        elapsed = round(time.time() - t0, 2)
        logger.info("*" * 60)
        logger.info("  ML Pipeline Completed Successfully in %ss!", elapsed)
        logger.info("*" * 60)
        return {
            "status": "success",
            "elapsed_seconds": elapsed,
            "report": stats
        }
    except Exception as e:
        logger.critical("ML Pipeline execution failed: %s", e, exc_info=True)
        return {
            "status": "failed",
            "error_message": str(e)
        }


if __name__ == "__main__":
    try:
        execute_ml_pipeline()
    except Exception as exc:
        print(f"\n[FATAL ERROR] ML pipeline run aborted: {exc}")
        sys.exit(1)
