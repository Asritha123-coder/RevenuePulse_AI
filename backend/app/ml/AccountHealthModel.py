"""
AccountHealthModel.py
--------------------
Trains and predicts continuous Account Health scores.
Classifies outcomes into Healthy, Medium Risk, or Critical categories.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from .preprocessing import DataPreprocessor, create_train_test_split
from .evaluation import calculate_regression_metrics
from .model_registry import ModelRegistry
from .utils import get_ml_logger

logger = get_ml_logger("AccountHealth")


class AccountHealthModel:
    NUM_COLS = [
        "monthly_spend", 
        "support_burden", 
        "usage_score", 
        "engagement_score", 
        "campaign_score", 
        "annual_contract_value", 
        "api_calls", 
        "login_count"
    ]
    
    CAT_COLS = [
        "company_size",
        "industry"
    ]
    
    FEATURES = NUM_COLS + CAT_COLS
    TARGET = "account_health_score"

    @classmethod
    def prepare_training_data(cls, df_engineered: pd.DataFrame, df_usage: pd.DataFrame) -> pd.DataFrame:
        """
        Merge account engineered metrics with the target health score from product usage.
        """
        # Fetch target score
        df_target = df_usage.drop_duplicates(subset=["account_id"])[["account_id", "account_health_score"]].copy()
        df_target = df_target.dropna(subset=["account_health_score"])
        
        # Merge on account_id
        df_dataset = df_target.merge(df_engineered, on="account_id", how="inner")
        
        for col in cls.NUM_COLS:
            df_dataset[col] = pd.to_numeric(df_dataset[col], errors="coerce")
            
        return df_dataset[[cls.TARGET] + cls.FEATURES]

    @classmethod
    def train(cls, df_dataset: pd.DataFrame) -> Tuple[str, Dict[str, float]]:
        """
        Train regression models to predict the health score, select best, and register.
        """
        logger.info("Starting Account Health regression training on %d rows...", len(df_dataset))
        
        # 1. Preprocess
        preprocessor = DataPreprocessor(cls.NUM_COLS, cls.CAT_COLS)
        X_train_raw, X_test_raw, y_train, y_test = create_train_test_split(df_dataset, cls.TARGET)
        
        X_train = preprocessor.fit_transform(X_train_raw)
        X_test = preprocessor.transform(X_test_raw)
        
        # 2. Compare Regressors
        models = {
            "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42),
            "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
        }
        
        best_name = None
        best_model = None
        best_r2 = -float("inf")
        best_metrics = {}
        
        for name, reg in models.items():
            reg.fit(X_train, y_train)
            y_pred = reg.predict(X_test)
            
            metrics = calculate_regression_metrics(y_test, y_pred)
            r2 = metrics["r2"]
            logger.info("%s metrics: RMSE=%.2f | MAE=%.2f | R2=%.4f", name, metrics["rmse"], metrics["mae"], r2)
            
            if r2 > best_r2:
                best_r2 = r2
                best_name = name
                best_model = reg
                best_metrics = metrics

        logger.info("Best model selected: %s with R2=%.4f", best_name, best_r2)
        
        # 3. Register model
        pipeline = {
            "preprocessor": preprocessor,
            "model": best_model
        }
        
        params = best_model.get_params()
        serializable_params = {k: str(v) for k, v in params.items() if isinstance(v, (int, float, str, bool, type(None)))}
        serializable_params["algorithm"] = best_name
        
        version = ModelRegistry.register_model(
            model_name="account_health",
            model_pipeline=pipeline,
            metrics=best_metrics,
            params=serializable_params,
            features=cls.FEATURES
        )
        
        return version, best_metrics

    @staticmethod
    def get_health_category(score: float) -> str:
        """Map numerical score to classification bucket."""
        if score >= 70.0:
            return "Healthy"
        elif score >= 40.0:
            return "Medium Risk"
        else:
            return "Critical"
