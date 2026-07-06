"""
test_revenue.py
---------------
Unit tests for the revenue analytics module.
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
from app.analytics.revenue_analytics import get_revenue_by_month, get_revenue_by_country


class TestRevenueAnalytics(unittest.TestCase):
    """Revenue calculations validation tests."""

    def setUp(self):
        self.service = AnalyticsService()
        self.db_online = test_connection()

    def test_revenue_by_month(self):
        """Ensure month-by-month revenue trends are computed properly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping revenue by month test.")
            
        data = get_revenue_by_month(self.service)
        self.assertIsInstance(data, list)
        if data:
            row = data[0]
            self.assertIn("month", row)
            self.assertIn("revenue", row)

    def test_revenue_by_country(self):
        """Ensure revenue aggregations by country are calculated properly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping revenue by country test.")
            
        data = get_revenue_by_country(self.service)
        self.assertIsInstance(data, list)
        if data:
            row = data[0]
            self.assertIn("country", row)
            self.assertIn("arr", row)


if __name__ == "__main__":
    unittest.main()
