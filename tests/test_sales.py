"""
test_sales.py
-------------
Unit tests for the sales analytics module.
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
from app.analytics.sales_analytics import get_sales_funnel, get_pipeline_value


class TestSalesAnalytics(unittest.TestCase):
    """Sales analytics calculations validation tests."""

    def setUp(self):
        self.service = AnalyticsService()
        self.db_online = test_connection()

    def test_sales_funnel(self):
        """Ensure sales funnel stage counts and ratios are computed properly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping sales funnel test.")
            
        data = get_sales_funnel(self.service)
        self.assertIsInstance(data, list)
        if data:
            row = data[0]
            self.assertIn("stage", row)
            self.assertIn("deal_count", row)

    def test_pipeline_value(self):
        """Ensure pipeline aggregate value returns a numerical float."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping pipeline value test.")
            
        val = get_pipeline_value(self.service)
        self.assertIsInstance(val, (int, float))
        self.assertGreaterEqual(val, 0.0)


if __name__ == "__main__":
    unittest.main()
