"""
usage_analytics.py
------------------
Computes product usage analytics including active user ratios, login profiles,
API load metrics, storage utilization, feature adoption rates, and user list activity.
"""

from typing import Dict, Any, List
from .sql_queries import SQLQueries


def get_dau_mau_ratio(service) -> List[Dict[str, Any]]:
    """Return Daily Active User (DAU) and Monthly Active User (MAU) engagement percentages."""
    df = service.execute_to_df(SQLQueries.DAU_MAU_RATIO)
    return df.to_dict(orient="records")


def get_login_trends(service) -> List[Dict[str, Any]]:
    """Return logins activity timelines grouped by client size."""
    query = """
    SELECT 
        a.company_size,
        SUM(p.login_count) AS total_logins,
        ROUND(AVG(p.login_count), 2) AS avg_logins
    FROM product_usage p
    JOIN accounts a ON p.account_id = a.account_id
    GROUP BY a.company_size;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_api_usage(service) -> List[Dict[str, Any]]:
    """Return API volume usage segmentations grouped by company size."""
    df = service.execute_to_df(SQLQueries.API_STORAGE_USAGE_BY_SIZE)
    return df.to_dict(orient="records")


def get_storage_usage(service) -> List[Dict[str, Any]]:
    """Return storage space usage metrics grouped by company size."""
    df = service.execute_to_df(SQLQueries.API_STORAGE_USAGE_BY_SIZE)
    return df.to_dict(orient="records")


def get_feature_adoption(service) -> List[Dict[str, Any]]:
    """Return product feature adoption scores grouped by customer industry."""
    df = service.execute_to_df(SQLQueries.PRODUCT_ADOPTION_BY_INDUSTRY)
    return df.to_dict(orient="records")


def get_top_features(service) -> List[Dict[str, Any]]:
    """Return product feature score segments distributions."""
    df = service.execute_to_df(SQLQueries.ENGAGEMENT_WATERFALL)
    return df.to_dict(orient="records")


def get_active_accounts(service) -> List[Dict[str, Any]]:
    """Return accounts with login activity in the last 30 days."""
    query = """
    SELECT 
        a.account_id,
        a.company_name,
        a.company_size,
        p.login_count,
        p.last_login
    FROM product_usage p
    JOIN accounts a ON p.account_id = a.account_id
    WHERE p.login_count > 0 AND p.last_login >= NOW() - INTERVAL '30 days'
    ORDER BY p.login_count DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_inactive_accounts(service) -> List[Dict[str, Any]]:
    """Return high MRR accounts that have never logged in."""
    df = service.execute_to_df(SQLQueries.USAGE_ANOMALIES_ZERO_LOGIN)
    return df.to_dict(orient="records")


def get_usage_summary_stats(service) -> Dict[str, Any]:
    """Retrieve full product usage analytics summaries."""
    return {
        "dau_mau_ratio": get_dau_mau_ratio(service),
        "login_trends": get_login_trends(service),
        "api_usage_by_size": get_api_usage(service),
        "storage_usage_by_size": get_storage_usage(service),
        "feature_adoption_by_industry": get_feature_adoption(service),
        "adoption_segmentation": get_top_features(service),
        "active_accounts_sample": get_active_accounts(service)[:15],  # limit to top 15 sample
        "inactive_accounts_risk": get_inactive_accounts(service)
    }
