"""
ml.py
-----
FastAPI routing endpoints for Machine Learning operations:
  - POST /ml/train     : Trigger model training in the background.
  - POST /ml/retrain   : RETRAIN models in the background.
  - POST /ml/predict/* : Real-time model inference endpoints.
  - GET /ml/models     : List registered versions and metadata.
  - GET /ml/model-metrics : Retrieve metrics of active models.
"""

from typing import List, Dict, Any
from datetime import datetime
import threading
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field

from ..ml.utils import get_ml_logger
from ..ml.pipeline import execute_ml_pipeline
from ..ml.model_registry import ModelRegistry
from ..ml.model_loader import reload_model
from ..ml.predict import predict_lead, predict_churn, predict_revenue, predict_health

logger = get_ml_logger("api")
router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# ── Pydantic Request Models ──────────────────────────────────────────────────

class LeadPredictRequest(BaseModel):
    company_size: str = Field(..., examples=["Enterprise"])
    industry: str = Field(..., examples=["Healthcare"])
    deal_value: float = Field(..., ge=0, examples=[150000.00])
    probability: float = Field(..., ge=0, le=1, examples=[0.65])
    customer_age_days: int = Field(..., ge=0, examples=[450])
    revenue_per_employee: float = Field(..., ge=0, examples=[250000.00])
    support_burden: float = Field(..., ge=0, examples=[15.0])
    web_sessions: float = Field(..., ge=0, examples=[120.0])
    login_count: float = Field(..., ge=0, examples=[850.0])


class ChurnPredictRequest(BaseModel):
    company_size: str = Field(..., examples=["Mid Market"])
    industry: str = Field(..., examples=["Finance"])
    login_count: float = Field(..., ge=0, examples=[120.0])
    api_calls: float = Field(..., ge=0, examples=[4500.0])
    storage_used_gb: float = Field(..., ge=0, examples=[25.5])
    feature_usage_score: float = Field(..., ge=0, le=100, examples=[78.5])
    total_tickets: float = Field(..., ge=0, examples=[4.0])
    open_tickets: float = Field(..., ge=0, examples=[1.0])
    avg_csat: float = Field(..., ge=1, le=5, examples=[4.2])
    monthly_spend: float = Field(..., ge=0, examples=[1200.0])
    customer_age_days: int = Field(..., ge=0, examples=[320])
    renewal_risk: float = Field(..., ge=0, le=100, examples=[45.0])


class RevenuePredictRequest(BaseModel):
    last_3_months_mrr: List[float] = Field(..., min_items=3, max_items=3, examples=[[28500.0, 28000.0, 27500.0]])


class HealthPredictRequest(BaseModel):
    company_size: str = Field(..., examples=["Small Business"])
    industry: str = Field(..., examples=["Retail"])
    monthly_spend: float = Field(..., ge=0, examples=[450.00])
    support_burden: float = Field(..., ge=0, examples=[5.0])
    usage_score: float = Field(..., ge=0, le=100, examples=[62.4])
    engagement_score: float = Field(..., ge=0, le=100, examples=[58.9])
    campaign_score: float = Field(..., ge=0, le=100, examples=[72.0])
    annual_contract_value: float = Field(..., ge=0, examples=[5400.00])
    api_calls: float = Field(..., ge=0, examples=[850.0])
    login_count: float = Field(..., ge=0, examples=[35.0])

# ── Helper ───────────────────────────────────────────────────────────────────

def _run_training_bg() -> None:
    """Synchronous training task executed inside background thread."""
    logger.info("Background thread kicked off model training...")
    try:
        res = execute_ml_pipeline()
        if res["status"] == "success":
            logger.info("Background model training completed successfully. Evicting caches...")
            # Reload updated models in loader cache
            reload_model("lead_scoring")
            reload_model("churn_model")
            reload_model("revenue_forecast")
            reload_model("account_health")
        else:
            logger.error("Background model training task failed: %s", res.get("error_message"))
    except Exception as exc:
        logger.error("Background model training crashed: %s", exc)

# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/train", status_code=status.HTTP_202_ACCEPTED)
def train_endpoint(background_tasks: BackgroundTasks):
    """
    Trigger retraining pipeline on all models in the background.
    """
    logger.info("API: POST /ml/train called")
    background_tasks.add_task(_run_training_bg)
    return {
        "status": "success",
        "message": "Model training pipeline triggered in the background.",
        "started_at": datetime.utcnow().isoformat() + "Z"
    }


@router.post("/retrain", status_code=status.HTTP_202_ACCEPTED)
def retrain_endpoint(background_tasks: BackgroundTasks):
    """
    Trigger retraining pipeline in the background. Similar to /train.
    """
    logger.info("API: POST /ml/retrain called")
    background_tasks.add_task(_run_training_bg)
    return {
        "status": "success",
        "message": "Model retraining pipeline triggered in the background.",
        "started_at": datetime.utcnow().isoformat() + "Z"
    }


@router.post("/predict/lead")
def predict_lead_endpoint(req: LeadPredictRequest):
    """
    Predict won/lost outcome probabilities for a sales opportunity.
    """
    logger.info("API: POST /ml/predict/lead called")
    try:
        data = predict_lead(req.model_dump())
        return {
            "status": "success",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "data": data
        }
    except Exception as e:
        logger.error("API failed to score lead: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {e}"
        )


@router.post("/predict/churn")
def predict_churn_endpoint(req: ChurnPredictRequest):
    """
    Predict churn cancellation probabilities and risk category for an account.
    """
    logger.info("API: POST /ml/predict/churn called")
    try:
        data = predict_churn(req.model_dump())
        return {
            "status": "success",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "data": data
        }
    except Exception as e:
        logger.error("API failed to predict churn: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {e}"
        )


@router.post("/predict/revenue")
def predict_revenue_endpoint(req: RevenuePredictRequest):
    """
    Forecast future MRR values recursively using last 3 months metrics.
    """
    logger.info("API: POST /ml/predict/revenue called")
    try:
        data = predict_revenue(req.last_3_months_mrr)
        return {
            "status": "success",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "data": data
        }
    except Exception as e:
        logger.error("API failed to forecast revenue: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {e}"
        )


@router.post("/predict/health")
def predict_health_endpoint(req: HealthPredictRequest):
    """
    Predict continuous account health score and category bucket.
    """
    logger.info("API: POST /ml/predict/health called")
    try:
        data = predict_health(req.model_dump())
        return {
            "status": "success",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "data": data
        }
    except Exception as e:
        logger.error("API failed to predict health: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {e}"
        )


@router.get("/models")
def get_models_endpoint():
    """
    Retrieve list of all model versions and configurations inside the registry.
    """
    logger.info("API: GET /ml/models called")
    try:
        data = ModelRegistry.list_all_models()
        return {
            "status": "success",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "data": data
        }
    except Exception as e:
        logger.error("API failed to fetch models: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load registry: {e}"
        )


@router.get("/model-metrics")
def get_model_metrics_endpoint():
    """
    Fetch validation metrics details of currently active model versions.
    """
    logger.info("API: GET /ml/model-metrics called")
    try:
        registry = ModelRegistry.list_all_models()
        active_metrics = {}
        for m_name, meta in registry.get("models", {}).items():
            active_ver = meta.get("active_version")
            if active_ver:
                version_meta = next((v for v in meta["versions"] if v["version"] == active_ver), None)
                if version_meta:
                    active_metrics[m_name] = {
                        "active_version": active_ver,
                        "metrics": version_meta.get("metrics"),
                        "registered_at": version_meta.get("registered_at"),
                        "algorithm": version_meta.get("params", {}).get("algorithm", "Unknown")
                    }
        return {
            "status": "success",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "data": active_metrics
        }
    except Exception as e:
        logger.error("API failed to fetch model metrics: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load metrics: {e}"
        )
