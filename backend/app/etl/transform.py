"""
transform.py
------------
Transform phase of the RevenuePulse AI ETL pipeline.
Cleans raw DataFrames and implements feature engineering:
  - Deduplication
  - Missing value handling
  - Whitespace trimming
  - Normalization of countries, phone numbers, and emails
  - Mixed date formats normalization
  - Removal/cleanup of invalid negative values
  - Feature engineering: Health Score, Revenue Tier, Company Category, Customer Age
"""

from datetime import date
from typing import Dict
import numpy as np
import pandas as pd

from ..utils.logger import get_logger
from ..utils.helpers import (
    parse_dates,
    normalize_country,
    clean_email,
    clean_phone,
    calculate_health_score,
)
from ..utils.constants import REVENUE_TIERS

logger = get_logger(__name__)

def trim_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim leading and trailing spaces from all string columns in the DataFrame."""
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def transform_accounts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform the accounts dataset.
    """
    logger.info("Transforming accounts dataset...")
    df = df.copy()
    
    # 1. Deduplicate by account_id (keep first)
    initial_len = len(df)
    df = df.drop_duplicates(subset=["account_id"], keep="first")
    logger.info("Accounts: Removed %d duplicate rows by ID", initial_len - len(df))
    
    # 2. Trim spaces
    df = trim_string_columns(df)
    
    # 3. Clean numeric fields
    df["employee_count"] = pd.to_numeric(df["employee_count"], errors="coerce")
    df.loc[df["employee_count"] < 0, "employee_count"] = 0
    
    df["annual_revenue"] = pd.to_numeric(df["annual_revenue"], errors="coerce")
    # Remove negative revenue by setting to None/NaN
    df.loc[df["annual_revenue"] < 0, "annual_revenue"] = np.nan
    
    # 4. Normalize Country Names
    df["country"] = df["country"].apply(normalize_country)
    
    # 5. Normalize Date Formats
    df["customer_since"] = parse_dates(df["customer_since"])
    df["last_activity"] = parse_dates(df["last_activity"])
    
    # Fill missing dates with sensible defaults or leave Null
    # Let's keep them as is (NaT) or drop them if critical.
    
    # 6. Feature Engineering: Company Category
    # Category = Company Size + Industry (e.g. "Enterprise Healthcare")
    df["company_category"] = df.apply(
        lambda r: f"{r['company_size']} {r['industry']}" if pd.notnull(r["company_size"]) and pd.notnull(r["industry"]) else "Standard",
        axis=1
    )
    
    # 7. Feature Engineering: Customer Age in Days
    today = pd.to_datetime(date.today())
    df["customer_age_days"] = (today - df["customer_since"]).dt.days
    df.loc[df["customer_age_days"] < 0, "customer_age_days"] = 0
    df["customer_age_days"] = df["customer_age_days"].fillna(0).astype(int)
    
    # 8. Feature Engineering: Revenue Tier
    def get_revenue_tier(rev):
        if pd.isna(rev) or rev < 0:
            return "Unknown"
        for tier, (low, high) in REVENUE_TIERS.items():
            if low <= rev < high:
                return tier
        return "Unknown"
        
    df["revenue_tier"] = df["annual_revenue"].apply(get_revenue_tier)
    
    logger.info("Accounts transformation complete. Resulting size: %d", len(df))
    return df


def transform_contacts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform the contacts dataset.
    """
    logger.info("Transforming contacts dataset...")
    df = df.copy()
    
    # 1. Deduplicate
    df = df.drop_duplicates(subset=["contact_id"], keep="first")
    
    # 2. Trim spaces
    df = trim_string_columns(df)
    
    # 3. Standardize Emails and Phone Numbers
    df["email"] = df["email"].apply(clean_email)
    df["phone"] = df["phone"].apply(clean_phone)
    
    # 4. Dates
    df["created_date"] = parse_dates(df["created_date"])
    
    logger.info("Contacts transformation complete. Size: %d", len(df))
    return df


def transform_campaigns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform the campaigns dataset.
    """
    logger.info("Transforming campaigns dataset...")
    df = df.copy()
    
    # 1. Deduplicate
    df = df.drop_duplicates(subset=["campaign_id"], keep="first")
    
    # 2. Trim spaces
    df = trim_string_columns(df)
    
    # 3. Remove negative budget or spend
    df["budget"] = pd.to_numeric(df["budget"], errors="coerce")
    df["spend"] = pd.to_numeric(df["spend"], errors="coerce")
    
    df.loc[df["budget"] < 0, "budget"] = np.nan
    df.loc[df["spend"] < 0, "spend"] = np.nan
    
    # 4. Clicks, impressions, conversions check
    df["impressions"] = pd.to_numeric(df["impressions"], errors="coerce").fillna(0).astype(int)
    df["clicks"] = pd.to_numeric(df["clicks"], errors="coerce").fillna(0).astype(int)
    df["leads_generated"] = pd.to_numeric(df["leads_generated"], errors="coerce").fillna(0).astype(int)
    df["conversions"] = pd.to_numeric(df["conversions"], errors="coerce").fillna(0).astype(int)
    
    df.loc[df["impressions"] < 0, "impressions"] = 0
    df.loc[df["clicks"] < 0, "clicks"] = 0
    df.loc[df["leads_generated"] < 0, "leads_generated"] = 0
    df.loc[df["conversions"] < 0, "conversions"] = 0
    
    # 5. ROI Recalculation (or clean negative/missing ROI)
    df["ROI"] = pd.to_numeric(df["ROI"], errors="coerce")
    
    # 6. Dates
    df["start_date"] = parse_dates(df["start_date"])
    df["end_date"] = parse_dates(df["end_date"])
    
    logger.info("Campaigns transformation complete. Size: %d", len(df))
    return df


def transform_opportunities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform the opportunities dataset.
    """
    logger.info("Transforming opportunities dataset...")
    df = df.copy()
    
    # 1. Deduplicate
    df = df.drop_duplicates(subset=["opportunity_id"], keep="first")
    
    # 2. Trim spaces
    df = trim_string_columns(df)
    
    # 3. Deal values - remove invalid negative deal values
    df["deal_value"] = pd.to_numeric(df["deal_value"], errors="coerce")
    df.loc[df["deal_value"] < 0, "deal_value"] = np.nan
    
    # 4. Probabilities between 0 and 1
    df["probability"] = pd.to_numeric(df["probability"], errors="coerce")
    df.loc[df["probability"] < 0, "probability"] = 0.0
    df.loc[df["probability"] > 1, "probability"] = 1.0
    
    # 5. Dates
    df["expected_close_date"] = parse_dates(df["expected_close_date"])
    df["actual_close_date"] = parse_dates(df["actual_close_date"])
    
    logger.info("Opportunities transformation complete. Size: %d", len(df))
    return df


def transform_subscriptions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform the subscriptions dataset.
    """
    logger.info("Transforming subscriptions dataset...")
    df = df.copy()
    
    # 1. Deduplicate
    df = df.drop_duplicates(subset=["subscription_id"], keep="first")
    
    # 2. Trim spaces
    df = trim_string_columns(df)
    
    # 3. Remove negative revenue
    df["monthly_revenue"] = pd.to_numeric(df["monthly_revenue"], errors="coerce")
    df["annual_contract_value"] = pd.to_numeric(df["annual_contract_value"], errors="coerce")
    
    df.loc[df["monthly_revenue"] < 0, "monthly_revenue"] = np.nan
    df.loc[df["annual_contract_value"] < 0, "annual_contract_value"] = np.nan
    
    # 4. Dates
    df["renewal_date"] = parse_dates(df["renewal_date"])
    
    logger.info("Subscriptions transformation complete. Size: %d", len(df))
    return df


def transform_website_activity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform the website activity dataset.
    """
    logger.info("Transforming website activity dataset...")
    df = df.copy()
    
    # 1. Deduplicate
    df = df.drop_duplicates(subset=["activity_id"], keep="first")
    
    # 2. Trim spaces
    df = trim_string_columns(df)
    
    # 3. Page views and sessions checks (no negatives)
    df["page_views"] = pd.to_numeric(df["page_views"], errors="coerce")
    df["sessions"] = pd.to_numeric(df["sessions"], errors="coerce")
    df["average_session_time"] = pd.to_numeric(df["average_session_time"], errors="coerce")
    df["downloads"] = pd.to_numeric(df["downloads"], errors="coerce").fillna(0).astype(int)
    df["webinar_attendance"] = pd.to_numeric(df["webinar_attendance"], errors="coerce").fillna(0).astype(int)
    
    df.loc[df["page_views"] < 0, "page_views"] = 0
    df.loc[df["sessions"] < 0, "sessions"] = 0
    df.loc[df["average_session_time"] < 0, "average_session_time"] = 0.0
    df.loc[df["downloads"] < 0, "downloads"] = 0
    df.loc[df["webinar_attendance"] < 0, "webinar_attendance"] = 0
    
    # 4. Dates
    df["last_visit"] = parse_dates(df["last_visit"])
    
    logger.info("Website activity transformation complete. Size: %d", len(df))
    return df


def transform_support_tickets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform the support tickets dataset.
    """
    logger.info("Transforming support tickets dataset...")
    df = df.copy()
    
    # 1. Deduplicate
    df = df.drop_duplicates(subset=["ticket_id"], keep="first")
    
    # 2. Trim spaces
    df = trim_string_columns(df)
    
    # 3. Priority, status, categories validation
    # Standardize checking is done by DB check constraints, but let's clean any NaN values
    
    # 4. Dates
    df["created_date"] = parse_dates(df["created_date"])
    df["resolved_date"] = parse_dates(df["resolved_date"])
    
    # 5. Satisfaction score
    df["satisfaction_score"] = pd.to_numeric(df["satisfaction_score"], errors="coerce")
    df.loc[(df["satisfaction_score"] < 1) | (df["satisfaction_score"] > 5), "satisfaction_score"] = np.nan
    
    logger.info("Support tickets transformation complete. Size: %d", len(df))
    return df


def transform_product_usage_and_calculate_health(
    usage_df: pd.DataFrame,
    website_df: pd.DataFrame,
    tickets_df: pd.DataFrame,
    subs_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Clean and transform the product usage dataset, and calculate the account health score
    using associated information from other datasets.
    """
    logger.info("Transforming product usage and calculating Account Health Scores...")
    usage_df = usage_df.copy()
    
    # 1. Deduplicate
    usage_df = usage_df.drop_duplicates(subset=["usage_id"], keep="first")
    
    # 2. Trim spaces
    usage_df = trim_string_columns(usage_df)
    
    # 3. Clean numeric usage fields (no negatives)
    usage_df["login_count"] = pd.to_numeric(usage_df["login_count"], errors="coerce").fillna(0).astype(int)
    usage_df["active_users"] = pd.to_numeric(usage_df["active_users"], errors="coerce").fillna(0).astype(int)
    usage_df["api_calls"] = pd.to_numeric(usage_df["api_calls"], errors="coerce")
    usage_df.loc[usage_df["api_calls"] < 0, "api_calls"] = 0
    usage_df["api_calls"] = usage_df["api_calls"].fillna(0).astype(int)
    
    usage_df["storage_used_gb"] = pd.to_numeric(usage_df["storage_used_gb"], errors="coerce")
    usage_df.loc[usage_df["storage_used_gb"] < 0, "storage_used_gb"] = 0.0
    
    usage_df["feature_usage_score"] = pd.to_numeric(usage_df["feature_usage_score"], errors="coerce").fillna(0.0)
    usage_df.loc[usage_df["feature_usage_score"] < 0, "feature_usage_score"] = 0.0
    usage_df.loc[usage_df["feature_usage_score"] > 100, "feature_usage_score"] = 100.0
    
    usage_df["last_login"] = parse_dates(usage_df["last_login"])
    
    # ── Calculate Account Health Score components ──
    # Aggregate website sessions per account
    web_sessions = website_df.groupby("account_id")["sessions"].sum().to_dict()
    
    # Aggregate open tickets per account
    open_tickets = tickets_df[tickets_df["status"].isin(["Open", "In Progress"])].groupby("account_id")["ticket_id"].count().to_dict()
    
    # Get monthly revenue per account
    monthly_rev = subs_df.set_index("account_id")["monthly_revenue"].to_dict()
    max_rev = subs_df["monthly_revenue"].max()
    if pd.isna(max_rev) or max_rev <= 0:
        max_rev = 1.0
        
    def row_health_score(row):
        acc_id = row["account_id"]
        
        l_count = row["login_count"]
        feat_score = row["feature_usage_score"]
        
        sess = web_sessions.get(acc_id, 0)
        tickets = open_tickets.get(acc_id, 0)
        rev = monthly_rev.get(acc_id, 0.0)
        if pd.isna(rev) or rev < 0:
            rev = 0.0
            
        return calculate_health_score(
            login_count=l_count,
            feature_usage_score=feat_score,
            sessions=sess,
            open_tickets=tickets,
            monthly_revenue=rev,
            max_revenue=max_rev
        )
        
    usage_df["account_health_score"] = usage_df.apply(row_health_score, axis=1)
    
    logger.info("Product usage transformation complete. Size: %d", len(usage_df))
    return usage_df


def transform_all(raw_dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Run full transformation workflows on all extracted DataFrames.
    """
    logger.info("Beginning global data transformation...")
    
    transformed_dfs = {}
    
    transformed_dfs["accounts"] = transform_accounts(raw_dfs["accounts"])
    transformed_dfs["contacts"] = transform_contacts(raw_dfs["contacts"])
    transformed_dfs["campaigns"] = transform_campaigns(raw_dfs["campaigns"])
    transformed_dfs["opportunities"] = transform_opportunities(raw_dfs["opportunities"])
    transformed_dfs["subscriptions"] = transform_subscriptions(raw_dfs["subscriptions"])
    transformed_dfs["website_activity"] = transform_website_activity(raw_dfs["website_activity"])
    transformed_dfs["support_tickets"] = transform_support_tickets(raw_dfs["support_tickets"])
    
    # Product usage calculation requires columns/data from website activity, tickets, and subscriptions
    transformed_dfs["product_usage"] = transform_product_usage_and_calculate_health(
        raw_dfs["product_usage"],
        transformed_dfs["website_activity"],
        transformed_dfs["support_tickets"],
        transformed_dfs["subscriptions"]
    )
    
    logger.info("Global transformation phase completed successfully.")
    return transformed_dfs
