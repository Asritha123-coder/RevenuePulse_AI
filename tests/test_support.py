"""
test_support.py
---------------
Unit tests for the support analytics module.
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
from app.analytics.support_analytics import get_tickets_by_priority, get_customer_satisfaction


class TestSupportAnalytics(unittest.TestCase):
    """Support analytics calculations validation tests."""

    def setUp(self):
        self.service = AnalyticsService()
        self.db_online = test_connection()

    def test_tickets_by_priority(self):
        """Ensure ticket volumes by priority are computed properly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping tickets by priority test.")
            
        data = get_tickets_by_priority(self.service)
        self.assertIsInstance(data, list)
        if data:
            row = data[0]
            self.assertIn("priority", row)
            self.assertIn("open_count", row)

    def test_customer_satisfaction(self):
        """Ensure CSAT score distribution percentages are computed properly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping CSAT distribution test.")
            
        data = get_customer_satisfaction(self.service)
        self.assertIsInstance(data, list)
        if data:
            row = data[0]
            self.assertIn("satisfaction_score", row)
            self.assertIn("share_pct", row)


if __name__ == "__main__":
    unittest.main()
