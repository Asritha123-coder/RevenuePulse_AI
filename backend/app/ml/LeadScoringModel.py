"""
LeadScoringModel.py
-------------------
Trains and predicts Lead Scoring probabilities.
Determines whether an Opportunity (lead) is likely to convert to Closed Won (1) or Closed Lost (0).
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

logger = get_ml_logger("LeadScoring")


class LeadScoringModel:
    NUM_COLS = [
        "deal_value", 
        "probability", 
        "customer_age_days", 
        "revenue_per_employee", 
        "support_burden",
        "web_sessions",
        "login_count"
    ]
    
    CAT_COLS = [
        "company_size", 
        "industry"
    ]
    
    FEATURES = NUM_COLS + CAT_COLS
    TARGET = "is_won"

    @classmethod
    def prepare_training_data(cls, df_engineered: pd.DataFrame, df_opps: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sales opportunities targets with client account engineered features.
        """
        # Target: opportunities status where Closed Won -> 1, Closed Lost -> 0
        df_closed = df_opps[df_opps["status"].isin(["Closed Won", "Closed Lost"])].copy()
        df_closed["is_won"] = (df_closed["status"] == "Closed Won").astype(int)
        
        # Merge on account_id
        df_dataset = df_closed.merge(df_engineered, on="account_id", how="inner")
        
        # Clean numerical columns
        for col in cls.NUM_COLS:
            df_dataset[col] = pd.to_numeric(df_dataset[col], errors="coerce")
            
        return df_dataset[[cls.TARGET] + cls.FEATURES]

    @classmethod
    def train(cls, df_dataset: pd.DataFrame) -> Tuple[str, Dict[str, float]]:
        """
        Train multiple models (LR, RF, GB) on the dataset, compare them,
        and register the best performing classifier.
        """
        logger.info("Starting Lead Scoring training on %d rows...", len(df_dataset))
        
        # 1. Preprocess
        preprocessor = DataPreprocessor(cls.NUM_COLS, cls.CAT_COLS)
        X_train_raw, X_test_raw, y_train, y_test = create_train_test_split(df_dataset, cls.TARGET)
        
        # Fit preprocessor
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
            # Fetch probabilities
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
        
        # 3. Register best model pipeline
        pipeline = {
            "preprocessor": preprocessor,
            "model": best_model
        }
        
        params = best_model.get_params()
        # Clean params for JSON serialization (remove unhashable objects)
        serializable_params = {k: str(v) for k, v in params.items() if isinstance(v, (int, float, str, bool, type(None)))}
        serializable_params["algorithm"] = best_name
        
        version = ModelRegistry.register_model(
            model_name="lead_scoring",
            model_pipeline=pipeline,
            metrics=best_metrics,
            params=serializable_params,
            features=cls.FEATURES
        )
        
        return version, best_metrics
