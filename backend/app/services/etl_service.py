"""
etl_service.py
--------------
Service layer wrapping the ETL execution pipeline and exposing status monitoring.
"""

import threading
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd

from ..utils.logger import get_logger
from ..etl.pipeline import run_pipeline, BACKEND_DIR

logger = get_logger(__name__)

# Global state to keep track of current pipeline status in memory
_PIPELINE_STATUS: Dict[str, Any] = {
    "is_running": False,
    "last_status": "NOT_RUN",  # SUCCESS, FAILED, RUNNING
    "last_run_stats": None,
    "error": None
}

_status_lock = threading.Lock()


def get_pipeline_status() -> Dict[str, Any]:
    """
    Retrieve the current status of the pipeline.
    If not running, attempts to read history from pipeline_statistics.csv.
    """
    with _status_lock:
        if _PIPELINE_STATUS["is_running"]:
            return {
                "status": "RUNNING",
                "details": "Pipeline is currently running in the background."
            }
            
        # Check if we have run stats in memory
        if _PIPELINE_STATUS["last_run_stats"] is not None:
            return {
                "status": _PIPELINE_STATUS["last_status"],
                "statistics": _PIPELINE_STATUS["last_run_stats"],
                "error": _PIPELINE_STATUS["error"]
            }
            
        # Check file system reports/pipeline_statistics.csv
        stats_path = BACKEND_DIR.parent / "reports" / "pipeline_statistics.csv"
        if stats_path.exists():
            try:
                df = pd.read_csv(stats_path)
                if not df.empty:
                    stats = df.iloc[0].to_dict()
                    # Clean up pandas types for JSON serializability
                    for key, val in stats.items():
                        if pd.isna(val):
                            stats[key] = None
                        elif isinstance(val, (int, float)):
                            pass
                        else:
                            stats[key] = str(val)
                            
                    _PIPELINE_STATUS["last_status"] = stats.get("status", "SUCCESS")
                    _PIPELINE_STATUS["last_run_stats"] = stats
                    return {
                        "status": _PIPELINE_STATUS["last_status"],
                        "statistics": stats,
                        "error": stats.get("error_message")
                    }
            except Exception as e:
                logger.error("Failed to read pipeline statistics from file: %s", e)
                
        return {
            "status": "NOT_RUN",
            "details": "No pipeline statistics found. The pipeline has not run yet."
        }


def _execute_pipeline_bg() -> None:
    """Helper method to run the pipeline synchronously in a background thread."""
    global _PIPELINE_STATUS
    
    with _status_lock:
        if _PIPELINE_STATUS["is_running"]:
            return
        _PIPELINE_STATUS["is_running"] = True
        _PIPELINE_STATUS["last_status"] = "RUNNING"
        _PIPELINE_STATUS["error"] = None
        
    logger.info("Pipeline thread started successfully.")
    
    try:
        stats = run_pipeline()
        with _status_lock:
            _PIPELINE_STATUS["is_running"] = False
            _PIPELINE_STATUS["last_status"] = stats["status"]
            _PIPELINE_STATUS["last_run_stats"] = stats
            _PIPELINE_STATUS["error"] = stats.get("error_message")
    except Exception as e:
        with _status_lock:
            _PIPELINE_STATUS["is_running"] = False
            _PIPELINE_STATUS["last_status"] = "FAILED"
            _PIPELINE_STATUS["error"] = str(e)
        logger.error("ETL pipeline background thread crashed: %s", e)


def trigger_pipeline() -> Dict[str, Any]:
    """
    Trigger the ETL pipeline to run asynchronously in a background thread.
    
    Returns:
        Dict confirming that the pipeline has been kicked off.
    """
    with _status_lock:
        if _PIPELINE_STATUS["is_running"]:
            return {
                "message": "ETL pipeline is already running.",
                "status": "RUNNING"
            }
            
    thread = threading.Thread(target=_execute_pipeline_bg, name="ETLPipelineThread")
    thread.daemon = True  # Thread will exit when main process exits
    thread.start()
    
    return {
        "message": "ETL pipeline execution triggered successfully in the background.",
        "status": "RUNNING"
    }
