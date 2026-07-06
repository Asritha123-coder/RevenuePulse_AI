"""
test_usage.py
-------------
Unit tests for the product usage analytics module.
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
from app.analytics.usage_analytics import get_dau_mau_ratio, get_login_trends


class TestUsageAnalytics(unittest.TestCase):
    """Usage analytics calculations validation tests."""

    def setUp(self):
        self.service = AnalyticsService()
        self.db_online = test_connection()

    def test_dau_mau_ratio(self):
        """Ensure active ratio is computed properly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping DAU/MAU ratio test.")
            
        data = get_dau_mau_ratio(self.service)
        self.assertIsInstance(data, list)
        if data:
            row = data[0]
            self.assertIn("company_size", row)
            self.assertIn("engagement_ratio_pct", row)

    def test_login_trends(self):
        """Ensure logins distribution is computed properly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping login trends test.")
            
        data = get_login_trends(self.service)
        self.assertIsInstance(data, list)
        if data:
            row = data[0]
            self.assertIn("company_size", row)
            self.assertIn("total_logins", row)


if __name__ == "__main__":
    unittest.main()
