"""
train.py
--------
Master orchestrator to train all 4 machine learning models.
Saves metrics reports and outputs feature importance scores to reports/ml/.
"""

from typing import Dict, Any
import sys
import os
import json
import time
from pathlib import Path
import pandas as pd
import numpy as np

# Add backend directory to sys.path to enable imports
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.utils import get_ml_logger, read_table_to_df
from app.ml.feature_engineering import engineer_features
from app.ml.model_registry import ModelRegistry
from app.ml.evaluation import save_evaluation_plots

# Models
from app.ml.LeadScoringModel import LeadScoringModel
from app.ml.ChurnPredictionModel import ChurnPredictionModel
from app.ml.RevenueForecastModel import RevenueForecastModel
from app.ml.AccountHealthModel import AccountHealthModel

logger = get_ml_logger("train")

REPORTS_ML_DIR = BACKEND_DIR.parent / "reports" / "ml"
REPORTS_ML_DIR.mkdir(parents=True, exist_ok=True)


def calculate_feature_importance(model, features: list) -> pd.DataFrame:
    """Extract feature importance from fitted ensemble classifiers/regressors."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        # For one-hot encoded variables the feature list expands, so we clamp or align
        # If preprocessor added columns, the length of importances matches self.encoded_cat_cols + num_cols
        # For simplicity, if lengths match features:
        if len(importances) == len(features):
            df_imp = pd.DataFrame({
                "feature": features,
                "importance_pct": np.round(importances * 100.0, 2)
            }).sort_values(by="importance_pct", ascending=False)
            return df_imp
    return pd.DataFrame()


def run_training_pipeline() -> Dict[str, Any]:
    """
    Run the full model training pipeline.
    
    Returns:
        Dict summarizing execution outcomes.
    """
    logger.info("=" * 60)
    logger.info("  Starting RevenuePulse AI Machine Learning Training Pipeline")
    logger.info("=" * 60)
    
    t_start = time.time()
    
    # ── 1. Extract Data from Database ──────────────────────────────────────
    try:
        df_accounts = read_table_to_df("accounts")
        df_contacts = read_table_to_df("contacts")
        df_campaigns = read_table_to_df("campaigns")
        df_opportunities = read_table_to_df("opportunities")
        df_subscriptions = read_table_to_df("subscriptions")
        df_product_usage = read_table_to_df("product_usage")
        df_website_activity = read_table_to_df("website_activity")
        df_support_tickets = read_table_to_df("support_tickets")
    except Exception as e:
        logger.critical("Data extraction failed. Training pipeline aborted: %s", e)
        raise RuntimeError("Data extraction failed.") from e

    # ── 2. Feature Engineering ─────────────────────────────────────────────
    logger.info("Engineering analytical features...")
    df_engineered = engineer_features(
        df_accounts=df_accounts,
        df_subs=df_subscriptions,
        df_opps=df_opportunities,
        df_usage=df_product_usage,
        df_web=df_website_activity,
        df_tickets=df_support_tickets
    )
    
    report_meta = {
        "training_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models_trained": {}
    }
    
    metrics_summary = []
    importance_dfs = []

    # ── 3. Train Model 1: Lead Scoring ─────────────────────────────────────
    try:
        df_ls = LeadScoringModel.prepare_training_data(df_engineered, df_opportunities)
        version, metrics = LeadScoringModel.train(df_ls)
        report_meta["models_trained"]["lead_scoring"] = {"version": version, "metrics": metrics}
        
        # Log performance
        metrics_summary.append({"model": "lead_scoring", "version": version, **metrics})
        
        # Save validation plot using test data
        pipeline = ModelRegistry.load_active_model("lead_scoring")
        preprocessor = pipeline["preprocessor"]
        model = pipeline["model"]
        X_test_scaled = preprocessor.transform(df_ls[LeadScoringModel.FEATURES])
        y_pred = model.predict(X_test_scaled)
        save_evaluation_plots(df_ls[LeadScoringModel.TARGET], y_pred, REPORTS_ML_DIR)
        
        # Feature Importance
        df_imp = calculate_feature_importance(model, preprocessor.num_cols + preprocessor.encoded_cat_cols)
        if not df_imp.empty:
            df_imp["model"] = "lead_scoring"
            importance_dfs.append(df_imp)
            
    except Exception as e:
        logger.error("Failed training Lead Scoring: %s", e, exc_info=True)

    # ── 4. Train Model 2: Churn Prediction ─────────────────────────────────
    try:
        df_churn = ChurnPredictionModel.prepare_training_data(df_engineered, df_subscriptions)
        version, metrics = ChurnPredictionModel.train(df_churn)
        report_meta["models_trained"]["churn_model"] = {"version": version, "metrics": metrics}
        metrics_summary.append({"model": "churn_model", "version": version, **metrics})
        
        # Save plots
        pipeline = ModelRegistry.load_active_model("churn_model")
        preprocessor = pipeline["preprocessor"]
        model = pipeline["model"]
        X_test_scaled = preprocessor.transform(df_churn[ChurnPredictionModel.FEATURES])
        y_pred = model.predict(X_test_scaled)
        save_evaluation_plots(df_churn[ChurnPredictionModel.TARGET], y_pred, REPORTS_ML_DIR)
        
        df_imp = calculate_feature_importance(model, preprocessor.num_cols + preprocessor.encoded_cat_cols)
        if not df_imp.empty:
            df_imp["model"] = "churn_model"
            importance_dfs.append(df_imp)
            
    except Exception as e:
        logger.error("Failed training Churn Prediction: %s", e, exc_info=True)

    # ── 5. Train Model 3: Revenue Forecast ─────────────────────────────────
    try:
        df_forecast = RevenueForecastModel.prepare_training_data(df_subscriptions)
        version, metrics = RevenueForecastModel.train(df_forecast)
        report_meta["models_trained"]["revenue_forecast"] = {"version": version, "metrics": metrics}
        metrics_summary.append({"model": "revenue_forecast", "version": version, **metrics})
        
        pipeline = ModelRegistry.load_active_model("revenue_forecast")
        df_imp = calculate_feature_importance(pipeline["model"], pipeline["preprocessor"].num_cols)
        if not df_imp.empty:
            df_imp["model"] = "revenue_forecast"
            importance_dfs.append(df_imp)
            
    except Exception as e:
        logger.error("Failed training Revenue Forecast: %s", e, exc_info=True)

    # ── 6. Train Model 4: Account Health ───────────────────────────────────
    try:
        df_health = AccountHealthModel.prepare_training_data(df_engineered, df_product_usage)
        version, metrics = AccountHealthModel.train(df_health)
        report_meta["models_trained"]["account_health"] = {"version": version, "metrics": metrics}
        metrics_summary.append({"model": "account_health", "version": version, **metrics})
        
        pipeline = ModelRegistry.load_active_model("account_health")
        preprocessor = pipeline["preprocessor"]
        df_imp = calculate_feature_importance(pipeline["model"], preprocessor.num_cols + preprocessor.encoded_cat_cols)
        if not df_imp.empty:
            df_imp["model"] = "account_health"
            importance_dfs.append(df_imp)
            
    except Exception as e:
        logger.error("Failed training Account Health: %s", e, exc_info=True)

    # ── 7. Save MLOps CSV Summaries ───────────────────────────────────────
    elapsed = round(time.time() - t_start, 2)
    report_meta["training_elapsed_seconds"] = elapsed
    logger.info("Saving training reports...")
    
    # Save training_report.json
    with open(REPORTS_ML_DIR / "training_report.json", "w") as f:
        json.dump(report_meta, f, indent=4)
        
    # Save model_metrics.csv
    df_metrics = pd.DataFrame(metrics_summary)
    df_metrics.to_csv(REPORTS_ML_DIR / "model_metrics.csv", index=False)
    
    # Save feature_importance.csv
    if importance_dfs:
        df_all_imp = pd.concat(importance_dfs, ignore_index=True)
        df_all_imp.to_csv(REPORTS_ML_DIR / "feature_importance.csv", index=False)
        
    logger.info("=" * 60)
    logger.info("  ML training pipeline completed in %ss", elapsed)
    logger.info("=" * 60)
    
    return report_meta


if __name__ == "__main__":
    try:
        run_training_pipeline()
    except Exception as exc:
        print(f"\n[FATAL ERROR] Model training failed: {exc}")
        sys.exit(1)
