"""
test_validate.py
-----------------
Unit tests for the ETL data validation module.
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

from app.etl.validate import ValidationEngine


class TestValidate(unittest.TestCase):
    """Validation engine tests."""

    def test_validation_engine_duplicates(self):
        """Ensure duplicate primary keys are identified and logged as Critical."""
        df_accounts = pd.DataFrame([
            {"account_id": "ACC001", "company_name": "Company A", "company_size": "Startup"},
            {"account_id": "ACC001", "company_name": "Company A Dup", "company_size": "Startup"}  # Duplicate
        ])
        
        dfs = {"accounts": df_accounts}
        engine = ValidationEngine(dfs)
        engine.validate_duplicates("accounts", "account_id")
        
        report_df = pd.DataFrame(engine.report_rows)
        self.assertFalse(report_df.empty)
        
        # Check that we found duplicate IDs
        dup_row = report_df[report_df["check_type"] == "Duplicate IDs"]
        self.assertEqual(len(dup_row), 1)
        self.assertEqual(dup_row.iloc[0]["issue_count"], 1)
        self.assertEqual(dup_row.iloc[0]["severity"], "CRITICAL")

    def test_validation_engine_missing_values(self):
        """Ensure missing values are identified and flagged."""
        df_accounts = pd.DataFrame([
            {"account_id": "ACC001", "company_name": None, "company_size": "Enterprise"},
            {"account_id": "ACC002", "company_name": "Company B", "company_size": None}
        ])
        
        dfs = {"accounts": df_accounts}
        engine = ValidationEngine(dfs)
        engine.validate_missing("accounts")
        
        report_df = pd.DataFrame(engine.report_rows)
        self.assertFalse(report_df.empty)
        
        # Verify missing company_name issues are recorded
        name_issues = report_df[report_df["column"] == "company_name"]
        self.assertEqual(len(name_issues), 1)
        self.assertEqual(name_issues.iloc[0]["issue_count"], 1)

    def test_validation_engine_invalid_email(self):
        """Ensure malformed email formats are flagged by validation checks."""
        df_contacts = pd.DataFrame([
            {"contact_id": "CON01", "email": "valid@corp.com"},
            {"contact_id": "CON02", "email": "invalid_email_no_at"},
            {"contact_id": "CON03", "email": None}  # Nulls should be skipped in email format validation
        ])
        
        dfs = {"contacts": df_contacts}
        engine = ValidationEngine(dfs)
        engine.validate_emails("contacts", "email")
        
        report_df = pd.DataFrame(engine.report_rows)
        self.assertFalse(report_df.empty)
        self.assertEqual(report_df.iloc[0]["issue_count"], 1)
        self.assertEqual(report_df.iloc[0]["check_type"], "Invalid Email")


if __name__ == "__main__":
    unittest.main()
