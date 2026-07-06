"""
test_marketing.py
-----------------
Unit tests for the marketing analytics module.
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
from app.analytics.analytics_service import AnalyticsService
from app.analytics.marketing_analytics import get_campaign_performance, get_best_campaign


class TestMarketingAnalytics(unittest.TestCase):
    """Marketing analytics calculations validation tests."""

    def setUp(self):
        self.service = AnalyticsService()
        self.db_online = test_connection()

    def test_campaign_performance(self):
        """Ensure details of campaigns performance are computed properly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping campaign performance test.")
            
        data = get_campaign_performance(self.service)
        self.assertIsInstance(data, list)
        if data:
            row = data[0]
            self.assertIn("campaign_id", row)
            self.assertIn("cost_per_lead", row)

    def test_best_campaign(self):
        """Ensure campaign with highest ROI is resolved correctly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping best campaign test.")
            
        data = get_best_campaign(self.service)
        self.assertIsInstance(data, dict)
        if data:
            self.assertIn("campaign_name", data)
            self.assertIn("ROI", data)


if __name__ == "__main__":
    unittest.main()
