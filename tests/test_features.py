"""
test_features.py
----------------
Unit tests for the ML feature engineering module.
"""

import sys
import unittest
from pathlib import Path
import pandas as pd

# Add backend directory to sys.path to enable imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.feature_engineering import engineer_features


class TestMLFeatures(unittest.TestCase):
    """Feature engineering validation tests."""

    def test_feature_engineering_aggregations(self):
        """Ensure relational tables are correctly grouped and engineered into feature metrics."""
        df_accounts = pd.DataFrame([
            {"account_id": "ACC1", "company_name": "Co A", "employee_count": 10, "annual_revenue": 100000.0, "company_size": "Startup", "industry": "Healthcare", "customer_since": "2024-01-01"}
        ])
        df_subs = pd.DataFrame([
            {"account_id": "ACC1", "monthly_revenue": 1000.0, "annual_contract_value": 12000.0, "renewal_date": "2026-12-31", "status": "Active"}
        ])
        df_opps = pd.DataFrame([
            {"account_id": "ACC1", "opportunity_id": "OPP1", "status": "Closed Won", "deal_value": 5000.0}
        ])
        df_usage = pd.DataFrame([
            {"account_id": "ACC1", "login_count": 50, "active_users": 5, "api_calls": 5000, "storage_used_gb": 10.5, "feature_usage_score": 85.0}
        ])
        df_web = pd.DataFrame([
            {"account_id": "ACC1", "sessions": 10, "page_views": 50, "average_session_time": 180.0}
        ])
        df_tickets = pd.DataFrame([
            {"account_id": "ACC1", "ticket_id": "TKT1", "status": "Open", "satisfaction_score": None}
        ])

        df_feat = engineer_features(df_accounts, df_subs, df_opps, df_usage, df_web, df_tickets)
        
        self.assertFalse(df_feat.empty)
        self.assertEqual(df_feat.iloc[0]["account_id"], "ACC1")
        
        # Verify custom engineered features
        self.assertIn("revenue_per_employee", df_feat.columns)
        self.assertIn("monthly_spend", df_feat.columns)
        self.assertIn("customer_value_score", df_feat.columns)
        self.assertIn("deal_success_rate", df_feat.columns)
        self.assertIn("usage_score", df_feat.columns)
        self.assertIn("support_burden", df_feat.columns)
        self.assertIn("renewal_risk", df_feat.columns)
        
        # Check calculation accuracy
        self.assertEqual(df_feat.iloc[0]["revenue_per_employee"], 10000.0)
        self.assertEqual(df_feat.iloc[0]["monthly_spend"], 1000.0)
        self.assertEqual(df_feat.iloc[0]["deal_success_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
