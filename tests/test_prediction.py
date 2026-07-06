"""
test_prediction.py
------------------
Unit and integration tests for the ML prediction/inference engine.
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path to enable imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.connection import test_connection
from app.ml.model_loader import get_cached_model
from app.ml.predict import predict_lead, predict_churn, predict_revenue, predict_health


class TestMLPrediction(unittest.TestCase):
    """Inference engine integration tests."""

    def setUp(self):
        self.db_online = test_connection()

    def test_predict_lead(self):
        """Ensure lead scoring outputs are structured properly."""
        if not self.db_online or not get_cached_model("lead_scoring"):
            self.skipTest("Database offline or models not trained yet. Skipping test_predict_lead.")
            
        record = {
            "company_size": "Enterprise",
            "industry": "Healthcare",
            "deal_value": 150000.00,
            "probability": 0.65,
            "customer_age_days": 450,
            "revenue_per_employee": 25000.00,
            "support_burden": 15.0,
            "web_sessions": 120.0,
            "login_count": 850.0
        }
        
        res = predict_lead(record)
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)
        self.assertIn("won_probability", res)
        self.assertIn("confidence_score", res)

    def test_predict_churn(self):
        """Ensure churn risk outputs are structured properly."""
        if not self.db_online or not get_cached_model("churn_model"):
            self.skipTest("Database offline or models not trained yet. Skipping test_predict_churn.")
            
        record = {
            "company_size": "Mid Market",
            "industry": "Finance",
            "login_count": 120.0,
            "api_calls": 4500.0,
            "storage_used_gb": 25.5,
            "feature_usage_score": 78.5,
            "total_tickets": 4.0,
            "open_tickets": 1.0,
            "avg_csat": 4.2,
            "monthly_spend": 1200.0,
            "customer_age_days": 320,
            "renewal_risk": 45.0
        }
        
        res = predict_churn(record)
        self.assertIsInstance(res, dict)
        self.assertIn("risk_category", res)
        self.assertIn("churn_probability", res)
        self.assertIn("confidence_score", res)

    def test_predict_revenue(self):
        """Ensure revenue forecasting timeline returns correct steps count."""
        if not self.db_online or not get_cached_model("revenue_forecast"):
            self.skipTest("Database offline or models not trained yet. Skipping test_predict_revenue.")
            
        mrr_lags = [28500.0, 28000.0, 27500.0]
        res = predict_revenue(mrr_lags)
        
        self.assertIsInstance(res, dict)
        self.assertIn("next_month", res)
        self.assertIn("next_quarter", res)
        self.assertIn("next_six_months", res)
        self.assertEqual(len(res["monthly_forecast_timeline"]), 6)

    def test_predict_health(self):
        """Ensure account health scoring outputs are structured properly."""
        if not self.db_online or not get_cached_model("account_health"):
            self.skipTest("Database offline or models not trained yet. Skipping test_predict_health.")
            
        record = {
            "company_size": "Small Business",
            "industry": "Retail",
            "monthly_spend": 450.00,
            "support_burden": 5.0,
            "usage_score": 62.4,
            "engagement_score": 58.9,
            "campaign_score": 72.0,
            "annual_contract_value": 5400.00,
            "api_calls": 850.0,
            "login_count": 35.0
        }
        
        res = predict_health(record)
        self.assertIsInstance(res, dict)
        self.assertIn("health_score", res)
        self.assertIn("health_category", res)


if __name__ == "__main__":
    unittest.main()
