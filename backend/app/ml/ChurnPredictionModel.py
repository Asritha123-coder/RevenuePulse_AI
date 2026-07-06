"""
ChurnPredictionModel.py
----------------------
Trains and predicts Churn risks.
Determines whether an Account subscription is likely to cancel (1) or remain active (0).
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from .preprocessing import DataPreprocessor, create_train_test_split
from .evaluation import calculate_classification_metrics
from .model_registry import ModelRegistry
from .utils import get_ml_logger

logger = get_ml_logger("Churn")


class ChurnPredictionModel:
    NUM_COLS = [
        "login_count", 
        "api_calls", 
        "storage_used_gb", 
        "feature_usage_score", 
        "total_tickets",
        "open_tickets",
        "avg_csat",
        "monthly_spend",
        "customer_age_days",
        "renewal_risk"
    ]
    
    CAT_COLS = [
        "company_size",
        "industry"
    ]
    
    FEATURES = NUM_COLS + CAT_COLS
    TARGET = "is_churned"

    @classmethod
    def prepare_training_data(cls, df_engineered: pd.DataFrame, df_subs: pd.DataFrame) -> pd.DataFrame:
        """
        Merge subscription outcomes with engineered metrics.
        """
        # Target: subscription status where Cancelled -> 1, Active/Active plans -> 0
        df_target = df_subs.drop_duplicates(subset=["account_id"]).copy()
        df_target["is_churned"] = (df_target["status"] == "Cancelled").astype(int)
        
        # Merge on account_id
        df_dataset = df_target.merge(df_engineered, on="account_id", how="inner")
        
        for col in cls.NUM_COLS:
            df_dataset[col] = pd.to_numeric(df_dataset[col], errors="coerce")
            
        return df_dataset[[cls.TARGET] + cls.FEATURES]

    @classmethod
    def train(cls, df_dataset: pd.DataFrame) -> Tuple[str, Dict[str, float]]:
        """
        Train classification algorithms and register the best churn predictor.
        """
        logger.info("Starting Churn Prediction training on %d rows...", len(df_dataset))
        
        # 1. Preprocess
        preprocessor = DataPreprocessor(cls.NUM_COLS, cls.CAT_COLS)
        X_train_raw, X_test_raw, y_train, y_test = create_train_test_split(df_dataset, cls.TARGET)
        
        X_train = preprocessor.fit_transform(X_train_raw)
        X_test = preprocessor.transform(X_test_raw)
        
        # 2. Compare Classifiers
        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
            "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
        }
        
        best_name = None
        best_model = None
        best_f1 = -1.0
        best_metrics = {}
        
        for name, clf in models.items():
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            y_prob = clf.predict_proba(X_test)
            
            metrics = calculate_classification_metrics(y_test, y_pred, y_prob)
            f1 = metrics["f1"]
            logger.info("%s metrics: Accuracy=%.4f | F1=%.4f | ROC_AUC=%.4f", name, metrics["accuracy"], f1, metrics.get("roc_auc", 0.0))
            
            if f1 > best_f1:
                best_f1 = f1
                best_name = name
                best_model = clf
                best_metrics = metrics

        logger.info("Best model selected: %s with F1=%.4f", best_name, best_f1)
        
        # 3. Register model
        pipeline = {
            "preprocessor": preprocessor,
            "model": best_model
        }
        
        params = best_model.get_params()
        serializable_params = {k: str(v) for k, v in params.items() if isinstance(v, (int, float, str, bool, type(None)))}
        serializable_params["algorithm"] = best_name
        
        version = ModelRegistry.register_model(
            model_name="churn_model",
            model_pipeline=pipeline,
            metrics=best_metrics,
            params=serializable_params,
            features=cls.FEATURES
        )
        
        return version, best_metrics
