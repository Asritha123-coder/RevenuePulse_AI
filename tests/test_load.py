"""
test_load.py
-------------
Unit tests for the ETL database loading module.
Gracefully skips tests if the PostgreSQL database is not reachable.
"""

import sys
import unittest
from pathlib import Path
import pandas as pd
from sqlalchemy import text

# Add backend directory to sys.path to enable imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.database import engine
from app.database.connection import test_connection
from app.etl.load import load_dataframe_to_db


class TestLoad(unittest.TestCase):
    """Database loading integration tests."""

    def test_database_reachability(self):
        """Ensure connection check operates correctly and returns a boolean value."""
        try:
            status = test_connection()
            self.assertIn(status, [True, False])
        except Exception as e:
            self.fail(f"test_connection raised an unexpected exception: {e}")

    def test_load_dataframe_transaction(self):
        """
        Verify database insert behavior inside a rollback transaction.
        Skipped if PostgreSQL is offline.
        """
        if not test_connection():
            self.skipTest("PostgreSQL database is offline. Skipping database insert test.")
            
        # Create a tiny mock dataframe matching accounts schema
        df_mock = pd.DataFrame([{
            "account_id": "ACC_TEST_999",
            "company_name": "Test Integration LLC",
            "industry": "IT Services",
            "company_size": "Startup",
            "employee_count": 5,
            "annual_revenue": 100000.0,
            "country": "United States",
            "state": "California",
            "city": "San Francisco",
            "account_status": "Active",
            "account_owner": "John Miller",
            "customer_since": "2025-01-01",
            "last_activity": "2025-02-01",
            "revenue_tier": "Tier 1 — Micro",
            "company_category": "Startup IT Services",
            "customer_age_days": 100
        }])
        
        # Open transaction block and test insert, then roll back
        try:
            with engine.begin() as conn:
                # Truncate clean first (only inside transaction) if exists or insert directly
                # We use append
                rows_inserted = load_dataframe_to_db(df_mock, "accounts", conn)
                self.assertEqual(rows_inserted, 1)
                
                # Retrieve record to verify it got loaded
                res = conn.execute(text("SELECT company_name FROM accounts WHERE account_id = 'ACC_TEST_999';"))
                val = res.scalar()
                self.assertEqual(val, "Test Integration LLC")
                
                # Force rollback by raising an exception or just rely on transaction end.
                # Actually, raising an exception in the end forces SQLAlchemy to ROLLBACK.
                # This leaves the database in its original clean state!
                raise RuntimeError("Force rollback to clean database state after test.")
        except RuntimeError as re:
            # Check if this is our forced rollback
            self.assertIn("Force rollback", str(re))
        except Exception as e:
            self.fail(f"Insert test failed with database exception: {e}")


if __name__ == "__main__":
    unittest.main()
