"""
test_customer.py
----------------
Unit tests for the customer analytics module.
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
from app.analytics.customer_analytics import get_company_size_distribution, get_avg_customer_age


class TestCustomerAnalytics(unittest.TestCase):
    """Customer analytics calculations validation tests."""

    def setUp(self):
        self.service = AnalyticsService()
        self.db_online = test_connection()

    def test_company_size_distribution(self):
        """Ensure company sizes share distribution is computed properly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping customer size distribution test.")
            
        data = get_company_size_distribution(self.service)
        self.assertIsInstance(data, list)
        if data:
            row = data[0]
            self.assertIn("company_size", row)
            self.assertIn("percentage", row)

    def test_avg_customer_age(self):
        """Ensure average customer tenure is computed properly."""
        if not self.db_online:
            self.skipTest("Database is offline. Skipping customer age test.")
            
        data = get_avg_customer_age(self.service)
        self.assertIsInstance(data, list)
        if data:
            row = data[0]
            self.assertIn("company_size", row)
            self.assertIn("avg_age_days", row)


if __name__ == "__main__":
    unittest.main()
