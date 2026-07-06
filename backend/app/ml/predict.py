"""
predict.py
----------
Exposes reusable inference methods for classifications and regressions,
providing prediction results, probabilities, and confidence scores.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from .model_loader import get_cached_model
from .AccountHealthModel import AccountHealthModel
from .RevenueForecastModel import RevenueForecastModel
from .utils import get_ml_logger

logger = get_ml_logger("predict")


def predict_lead(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict conversion probability and outcome for a sales lead (opportunity).
    
    Expected record schema:
      - company_size: str
      - industry: str
      - deal_value: float
      - probability: float
      - customer_age_days: int
      - revenue_per_employee: float
      - support_burden: float
      - web_sessions: float
      - login_count: float
    """
    pipeline = get_cached_model("lead_scoring")
    if not pipeline:
        raise RuntimeError("Lead Scoring model is not trained or registered yet.")
        
    preprocessor = pipeline["preprocessor"]
    model = pipeline["model"]
    
    # 1. Transform single record
    df_transformed = preprocessor.prepare_single_record(record)
    
    # 2. Run prediction
    pred = int(model.predict(df_transformed)[0])
    probs = model.predict_proba(df_transformed)[0]
    
    # Probability of Won class (1)
    won_prob = float(probs[1])
    
    # Confidence Score is the probability of the predicted class
    confidence = float(probs[pred])
    
    return {
        "status": "Won" if pred == 1 else "Lost",
        "won_probability": round(won_prob, 4),
        "confidence_score": round(confidence, 4)
    }


def predict_churn(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict churn risk probability and classification category for an account.
    
    Expected record schema:
      - company_size: str
      - industry: str
      - login_count: float
      - api_calls: float
      - storage_used_gb: float
      - feature_usage_score: float
      - total_tickets: float
      - open_tickets: float
      - avg_csat: float
      - monthly_spend: float
      - customer_age_days: int
      - renewal_risk: float
    """
    pipeline = get_cached_model("churn_model")
    if not pipeline:
        raise RuntimeError("Churn Prediction model is not trained or registered yet.")
        
    preprocessor = pipeline["preprocessor"]
    model = pipeline["model"]
    
    df_transformed = preprocessor.prepare_single_record(record)
    
    pred = int(model.predict(df_transformed)[0])
    probs = model.predict_proba(df_transformed)[0]
    
    churn_prob = float(probs[1])
    
    # Risk categorization
    if churn_prob >= 0.70:
        risk_category = "High Risk"
    elif churn_prob >= 0.35:
        risk_category = "Medium Risk"
    else:
        risk_category = "Low Risk"
        
    return {
        "risk_category": risk_category,
        "churn_probability": round(churn_prob, 4),
        "confidence_score": round(float(probs[pred]), 4)
    }


def predict_revenue(last_3_months_mrr: List[float]) -> Dict[str, Any]:
    """
    Forecast future MRR values for Next Month, Next Quarter, and Next Six Months.
    
    Args:
        last_3_months_mrr: List of last 3 months MRR, e.g. [current_mrr, last_mrr, prev_mrr]
    """
    pipeline = get_cached_model("revenue_forecast")
    if not pipeline:
        raise RuntimeError("Revenue Forecast model is not trained or registered yet.")
        
    if len(last_3_months_mrr) != 3:
        raise ValueError("Exactly 3 months of historical MRR values are required [t, t-1, t-2]")
        
    # Project 6 steps ahead using recursive forecast
    predictions = RevenueForecastModel.forecast_timeline(
        pipeline=pipeline,
        last_3_months_mrr=last_3_months_mrr,
        steps=6
    )
    
    # Round predictions
    predictions = [round(p, 2) for p in predictions]
    
    return {
        "next_month": predictions[0],
        "next_quarter": predictions[2],
        "next_six_months": predictions[5],
        "monthly_forecast_timeline": predictions
    }


def predict_health(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict health score and health category for an account.
    
    Expected record schema:
      - company_size: str
      - industry: str
      - monthly_spend: float
      - support_burden: float
      - usage_score: float
      - engagement_score: float
      - campaign_score: float
      - annual_contract_value: float
      - api_calls: float
      - login_count: float
    """
    pipeline = get_cached_model("account_health")
    if not pipeline:
        raise RuntimeError("Account Health model is not trained or registered yet.")
        
    preprocessor = pipeline["preprocessor"]
    model = pipeline["model"]
    
    df_transformed = preprocessor.prepare_single_record(record)
    
    # Predict continuous health score (clamp between 0 and 100)
    score = float(model.predict(df_transformed)[0])
    score = max(0.0, min(100.0, score))
    
    # Categorise
    category = AccountHealthModel.get_health_category(score)
    
    return {
        "health_score": round(score, 2),
        "health_category": category
    }
