"""
etl.py
------
FastAPI API endpoints for managing the RevenuePulse AI ETL pipeline.
Defines:
  - POST /run-etl          : Kick off the ETL process in the background.
  - GET /pipeline-status   : Fetch current execution state and runtime metrics.
  - GET /validation-report : Return the latest data quality validation report.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import pandas as pd

from ..services.etl_service import trigger_pipeline, get_pipeline_status
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/etl", tags=["ETL Pipeline"])

# Resolve reports directory relative to backend app
REPORTS_DIR = Path(__file__).resolve().parents[3] / "reports"


@router.post("/run-etl", status_code=status.HTTP_202_ACCEPTED)
def run_etl_endpoint():
    """
    Trigger execution of the ETL pipeline in a background thread.
    
    Returns immediately with status 202 Accepted.
    """
    logger.info("API: POST /run-etl called")
    try:
        res = trigger_pipeline()
        return res
    except Exception as e:
        logger.error("API failed to trigger ETL pipeline: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start pipeline: {e}"
        )


@router.get("/pipeline-status")
def pipeline_status_endpoint():
    """
    Fetch the execution status of the pipeline, including execution times
    and records loaded metrics.
    """
    logger.info("API: GET /pipeline-status called")
    try:
        status_info = get_pipeline_status()
        return status_info
    except Exception as e:
        logger.error("API failed to fetch pipeline status: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pipeline status: {e}"
        )


@router.get("/validation-report")
def validation_report_endpoint():
    """
    Read the latest validation report CSV and return its records as a JSON list.
    """
    logger.info("API: GET /validation-report called")
    report_file = REPORTS_DIR / "validation_report.csv"
    
    if not report_file.exists():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "Validation report not found. Has the pipeline run at least once?",
                "status": "NOT_FOUND"
            }
        )
        
    try:
        df = pd.read_csv(report_file)
        # Convert NaN values to None for JSON compliance
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient="records")
        return {
            "report_file": str(report_file.name),
            "total_issues": len(records),
            "records": records
        }
    except Exception as e:
        logger.error("API failed to parse validation report: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read validation report: {e}"
        )
