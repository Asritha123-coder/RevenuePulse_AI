"""
test_transform.py
-----------------
Unit tests for the ETL transformation and cleaning module.
"""

import sys
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

# Add backend directory to sys.path to enable imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.utils.helpers import normalize_country, clean_email, clean_phone, calculate_health_score
from app.etl.transform import transform_accounts, transform_contacts


class TestTransform(unittest.TestCase):
    """Transformation rules validation tests."""

    def test_country_normalization(self):
        """Ensure country names are mapped to canonical standards."""
        self.assertEqual(normalize_country("usa"), "United States")
        self.assertEqual(normalize_country("U.S.A. "), "United States")
        self.assertEqual(normalize_country("uk"), "United Kingdom")
        self.assertEqual(normalize_country("india"), "India")
        self.assertEqual(normalize_country("Germany"), "Germany")
        self.assertEqual(normalize_country("unknown"), "unknown")

    def test_email_cleaning(self):
        """Ensure emails are validated and malformed ones returned as None."""
        self.assertEqual(clean_email("TEST@domain.com "), "test@domain.com")
        self.assertIsNone(clean_email("missing_at_sign.com"))
        self.assertIsNone(clean_email("@missing_mailbox.com"))
        self.assertIsNone(clean_email("spaces in@email.com"))

    def test_phone_cleaning(self):
        """Ensure phone numbers are cleaned of non-digits and evaluated by length."""
        self.assertEqual(clean_phone("+1 (800) 555-0199"), "18005550199")
        self.assertEqual(clean_phone("123-456-7890"), "1234567890")
        self.assertIsNone(clean_phone("12345"))  # too short
        self.assertIsNone(clean_phone("1234567890123456"))  # too long

    def test_health_score_calculation(self):
        """Verify health score calculations return values between 0 and 100."""
        score = calculate_health_score(
            login_count=1000,
            feature_usage_score=80.0,
            sessions=200,
            open_tickets=0,
            monthly_revenue=5000.0,
            max_revenue=10000.0
        )
        self.assertTrue(0.0 <= score <= 100.0)
        
        # High tickets should decrease score
        score_low_tickets = calculate_health_score(1000, 80.0, 200, 0, 5000.0, 10000.0)
        score_high_tickets = calculate_health_score(1000, 80.0, 200, 10, 5000.0, 10000.0)
        self.assertGreater(score_low_tickets, score_high_tickets)

    def test_transform_accounts_negatives(self):
        """Verify negative values in annual_revenue are set to NaN during transformation."""
        df_accounts = pd.DataFrame([{
            "account_id": "ACC000001",
            "company_name": "Test Company",
            "industry": "Healthcare",
            "company_size": "Enterprise",
            "employee_count": 120,
            "annual_revenue": -5000000.0,  # Negative
            "country": "USA",
            "state": "California",
            "city": "Austin",
            "account_status": "Active",
            "account_owner": "Arjun Verma",
            "customer_since": "2024-01-15",
            "last_activity": "2025-06-20"
        }])
        
        transformed = transform_accounts(df_accounts)
        # Revenue should be NaN because it was negative
        self.assertTrue(pd.isna(transformed.iloc[0]["annual_revenue"]))
        
        # Categories should be correctly engineered
        self.assertEqual(transformed.iloc[0]["company_category"], "Enterprise Healthcare")
        self.assertEqual(transformed.iloc[0]["country"], "United States")


if __name__ == "__main__":
    unittest.main()
