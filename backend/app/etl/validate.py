"""
validate.py
-----------
Validation engine for the RevenuePulse AI ETL pipeline.
Identifies remaining data quality issues and integrity violations in DataFrames:
  - Duplicate IDs
  - Duplicate Records
  - Missing Values
  - Invalid Email
  - Invalid Phone
  - Negative Revenue
  - Future Dates
  - Invalid Foreign Keys
  - Invalid Data Types
Saves reports inside `reports/validation_report.csv`.
"""

import re
from datetime import date
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

from ..utils.logger import get_logger
from ..utils.file_utils import save_csv

logger = get_logger(__name__)

# Basic RFC email pattern
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


class ValidationEngine:
    """Reusable validation engine to run checks on B2B SaaS datasets."""
    
    def __init__(self, dfs: Dict[str, pd.DataFrame]):
        self.dfs = dfs
        self.report_rows: List[Dict[str, Any]] = []
        self.today = pd.to_datetime(date.today())

    def log_issue(self, dataset: str, check_type: str, column: str, issue_count: int, severity: str, details: str = "") -> None:
        """Helper to append an issue to the final report list."""
        if issue_count > 0:
            self.report_rows.append({
                "dataset": dataset,
                "check_type": check_type,
                "column": column,
                "issue_count": issue_count,
                "severity": severity,
                "details": details
            })
            logger.warning(
                "Validation [%s] on %s.%s: Found %d issues (%s) - %s",
                check_type, dataset, column, issue_count, severity, details
            )

    def validate_duplicates(self, key: str, pk: str) -> None:
        """Validate duplicate IDs and duplicate records."""
        df = self.dfs[key]
        if df.empty:
            return
            
        # Duplicate primary keys
        dup_pk_count = df.duplicated(subset=[pk]).sum()
        self.log_issue(key, "Duplicate IDs", pk, dup_pk_count, "CRITICAL", f"Duplicate primary keys found in {pk}")
        
        # Duplicate full rows
        dup_rows_count = df.duplicated().sum()
        self.log_issue(key, "Duplicate Records", "ALL_COLUMNS", dup_rows_count, "WARNING", "Exact duplicate rows found")

    def validate_missing(self, key: str) -> None:
        """Validate missing values across all columns."""
        df = self.dfs[key]
        if df.empty:
            return
            
        null_counts = df.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                # Check if it's a critical column (like primary keys or foreign keys)
                severity = "CRITICAL" if col in [f"{key}_id", "account_id"] else "INFO"
                self.log_issue(key, "Missing Values", col, count, severity, "Null or missing value")

    def validate_emails(self, key: str, email_col: str) -> None:
        """Validate email format."""
        df = self.dfs[key]
        if df.empty or email_col not in df.columns:
            return
            
        emails = df[email_col].dropna().astype(str)
        invalid_mask = emails.apply(lambda x: not bool(EMAIL_RE.match(x)))
        invalid_count = invalid_mask.sum()
        self.log_issue(key, "Invalid Email", email_col, invalid_count, "ERROR", "Email addresses do not match RFC standard")

    def validate_phones(self, key: str, phone_col: str) -> None:
        """Validate phone format (length between 10 and 15 digits)."""
        df = self.dfs[key]
        if df.empty or phone_col not in df.columns:
            return
            
        phones = df[phone_col].dropna().astype(str)
        # Strip common formatting chars to evaluate length
        cleaned = phones.apply(lambda x: re.sub(r"\D", "", x))
        invalid_mask = cleaned.apply(lambda x: not (10 <= len(x) <= 15))
        invalid_count = invalid_mask.sum()
        self.log_issue(key, "Invalid Phone", phone_col, invalid_count, "ERROR", "Phone number length is not 10-15 digits")

    def validate_negative_columns(self, key: str, cols: List[str]) -> None:
        """Validate columns that should never be negative."""
        df = self.dfs[key]
        if df.empty:
            return
            
        for col in cols:
            if col in df.columns:
                nums = pd.to_numeric(df[col], errors="coerce").dropna()
                neg_count = (nums < 0).sum()
                self.log_issue(key, "Negative Values", col, neg_count, "ERROR", "Value is negative but must be non-negative")

    def validate_future_dates(self, key: str, date_cols: List[str]) -> None:
        """Validate that dates are not in the future."""
        df = self.dfs[key]
        if df.empty:
            return
            
        for col in date_cols:
            if col in df.columns:
                dates = pd.to_datetime(df[col], errors="coerce").dropna()
                future_count = (dates > self.today).sum()
                self.log_issue(key, "Future Dates", col, future_count, "ERROR", f"Date is in the future (after today: {date.today()})")

    def validate_foreign_keys(self, child_key: str, parent_key: str = "accounts", fk_col: str = "account_id") -> None:
        """Validate referential integrity between child and parent datasets."""
        child_df = self.dfs[child_key]
        parent_df = self.dfs[parent_key]
        if child_df.empty or parent_df.empty or fk_col not in child_df.columns:
            return
            
        # Get unique valid parent keys
        parent_pks = set(parent_df["account_id"].dropna().unique())
        
        # Check kids whose keys aren't in the parent set
        child_fks = child_df[fk_col].dropna()
        invalid_mask = child_fks.apply(lambda x: x not in parent_pks)
        invalid_count = invalid_mask.sum()
        self.log_issue(child_key, "Invalid Foreign Keys", fk_col, invalid_count, "CRITICAL", f"account_id does not exist in {parent_key} table")

    def validate_datatypes(self, key: str, schema: Dict[str, str]) -> None:
        """Validate datatypes of columns."""
        df = self.dfs[key]
        if df.empty:
            return
            
        for col, expected_type in schema.items():
            if col not in df.columns:
                continue
                
            actual_type = str(df[col].dtype)
            # Trivial check for type mismatches
            if expected_type == "numeric":
                # Check if it cannot be converted to numeric
                converted = pd.to_numeric(df[col], errors="coerce")
                failed_count = (df[col].notna() & converted.isna()).sum()
                self.log_issue(key, "Invalid Data Type", col, failed_count, "ERROR", f"Expected numeric, but values cannot be parsed")
            elif expected_type == "date":
                # Check if it cannot be converted to datetime
                converted = pd.to_datetime(df[col], errors="coerce")
                failed_count = (df[col].notna() & converted.isna()).sum()
                self.log_issue(key, "Invalid Data Type", col, failed_count, "ERROR", f"Expected date, but values cannot be parsed")

    def run_all(self, reports_dir: Path) -> pd.DataFrame:
        """Run validation rules for all datasets and generate a report."""
        logger.info("Starting validation rules for all datasets...")
        
        # 1. Accounts
        self.validate_duplicates("accounts", "account_id")
        self.validate_missing("accounts")
        self.validate_negative_columns("accounts", ["annual_revenue", "employee_count"])
        self.validate_future_dates("accounts", ["customer_since", "last_activity"])
        self.validate_datatypes("accounts", {"annual_revenue": "numeric", "employee_count": "numeric", "customer_since": "date", "last_activity": "date"})

        # 2. Contacts
        self.validate_duplicates("contacts", "contact_id")
        self.validate_missing("contacts")
        self.validate_emails("contacts", "email")
        self.validate_phones("contacts", "phone")
        self.validate_future_dates("contacts", ["created_date"])
        self.validate_foreign_keys("contacts")
        self.validate_datatypes("contacts", {"created_date": "date"})

        # 3. Campaigns
        self.validate_duplicates("campaigns", "campaign_id")
        self.validate_missing("campaigns")
        self.validate_negative_columns("campaigns", ["budget", "spend", "impressions", "clicks", "leads_generated", "conversions"])
        self.validate_future_dates("campaigns", ["start_date", "end_date"])
        self.validate_datatypes("campaigns", {"budget": "numeric", "spend": "numeric", "ROI": "numeric", "start_date": "date", "end_date": "date"})

        # 4. Opportunities
        self.validate_duplicates("opportunities", "opportunity_id")
        self.validate_missing("opportunities")
        self.validate_negative_columns("opportunities", ["deal_value", "probability"])
        self.validate_future_dates("opportunities", ["expected_close_date", "actual_close_date"])
        self.validate_foreign_keys("opportunities")
        self.validate_datatypes("opportunities", {"deal_value": "numeric", "probability": "numeric", "expected_close_date": "date", "actual_close_date": "date"})

        # 5. Subscriptions
        self.validate_duplicates("subscriptions", "subscription_id")
        self.validate_missing("subscriptions")
        self.validate_negative_columns("subscriptions", ["monthly_revenue", "annual_contract_value"])
        self.validate_future_dates("subscriptions", ["renewal_date"])
        self.validate_foreign_keys("subscriptions")
        self.validate_datatypes("subscriptions", {"monthly_revenue": "numeric", "annual_contract_value": "numeric", "renewal_date": "date"})

        # 6. Product Usage
        self.validate_duplicates("product_usage", "usage_id")
        self.validate_missing("product_usage")
        self.validate_negative_columns("product_usage", ["login_count", "active_users", "api_calls", "storage_used_gb", "feature_usage_score"])
        self.validate_future_dates("product_usage", ["last_login"])
        self.validate_foreign_keys("product_usage")
        self.validate_datatypes("product_usage", {"login_count": "numeric", "active_users": "numeric", "api_calls": "numeric", "storage_used_gb": "numeric", "feature_usage_score": "numeric", "last_login": "date"})

        # 7. Website Activity
        self.validate_duplicates("website_activity", "activity_id")
        self.validate_missing("website_activity")
        self.validate_negative_columns("website_activity", ["page_views", "sessions", "average_session_time", "downloads", "webinar_attendance"])
        self.validate_future_dates("website_activity", ["last_visit"])
        self.validate_foreign_keys("website_activity")
        self.validate_datatypes("website_activity", {"page_views": "numeric", "sessions": "numeric", "average_session_time": "numeric", "downloads": "numeric", "webinar_attendance": "numeric", "last_visit": "date"})

        # 8. Support Tickets
        self.validate_duplicates("support_tickets", "ticket_id")
        self.validate_missing("support_tickets")
        self.validate_negative_columns("support_tickets", ["satisfaction_score"])
        self.validate_future_dates("support_tickets", ["created_date", "resolved_date"])
        self.validate_foreign_keys("support_tickets")
        self.validate_datatypes("support_tickets", {"satisfaction_score": "numeric", "created_date": "date", "resolved_date": "date"})

        # Create Validation Report DataFrame
        if not self.report_rows:
            report_df = pd.DataFrame(columns=["dataset", "check_type", "column", "issue_count", "severity", "details"])
            logger.info("No validation issues found. Datasets are clean.")
        else:
            report_df = pd.DataFrame(self.report_rows)
            
        # Ensure target folder exists and save report
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / "validation_report.csv"
        save_csv(report_df, report_path)
        
        logger.info("Validation completed. Report saved to %s", report_path)
        return report_df


def validate_all(dfs: Dict[str, pd.DataFrame], reports_dir: Path) -> pd.DataFrame:
    """Helper to run the ValidationEngine on all DataFrames."""
    engine = ValidationEngine(dfs)
    return engine.run_all(reports_dir)
