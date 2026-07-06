"""
revenue_analytics.py
---------------------
Computes advanced revenue analytics, segmentation, trends, waterfalls, and heatmaps.
"""

from typing import Dict, Any, List
from .sql_queries import SQLQueries


def get_revenue_by_month(service) -> List[Dict[str, Any]]:
    """Return historical revenue trends grouped by month."""
    df = service.execute_to_df(SQLQueries.REVENUE_BY_MONTH)
    return df.to_dict(orient="records")


def get_revenue_by_country(service) -> List[Dict[str, Any]]:
    """Return recurring revenue segmentations by country."""
    df = service.execute_to_df(SQLQueries.REVENUE_BY_COUNTRY)
    return df.to_dict(orient="records")


def get_revenue_by_industry(service) -> List[Dict[str, Any]]:
    """Return recurring revenue segmentations by customer industry."""
    df = service.execute_to_df(SQLQueries.REVENUE_BY_INDUSTRY)
    return df.to_dict(orient="records")


def get_revenue_by_company_size(service) -> List[Dict[str, Any]]:
    """Return recurring revenue segmentations by customer company size."""
    df = service.execute_to_df(SQLQueries.REVENUE_BY_COMPANY_SIZE)
    return df.to_dict(orient="records")


def get_revenue_trend(service) -> List[Dict[str, Any]]:
    """Return recurring revenue trend over time with growth percentage."""
    df = service.execute_to_df(SQLQueries.REVENUE_GROWTH_HISTORICAL)
    return df.to_dict(orient="records")


def get_top_revenue_accounts(service, limit: int = 10) -> List[Dict[str, Any]]:
    """Return top active accounts ordered by ARR contributions."""
    df = service.execute_to_df(SQLQueries.TOP_REVENUE_ACCOUNTS, {"limit": limit})
    return df.to_dict(orient="records")


def get_lowest_revenue_accounts(service, limit: int = 10) -> List[Dict[str, Any]]:
    """Return lowest revenue active accounts ordered by ARR contributions."""
    df = service.execute_to_df(SQLQueries.LOWEST_REVENUE_ACCOUNTS, {"limit": limit})
    return df.to_dict(orient="records")


def get_subscription_revenue_breakdown(service) -> List[Dict[str, Any]]:
    """Return active subscription count and ARR grouped by subscription tier plan."""
    query = """
    SELECT 
        plan,
        COUNT(subscription_id) AS active_subscriptions,
        SUM(monthly_revenue) AS monthly_recurring_revenue,
        SUM(annual_contract_value) AS arr
    FROM subscriptions
    WHERE status = 'Active'
    GROUP BY plan
    ORDER BY arr DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_revenue_distribution(service) -> List[Dict[str, Any]]:
    """Return counts and ARR distributions grouped into size categories."""
    df = service.execute_to_df(SQLQueries.REVENUE_DISTRIBUTION_BUCKETS)
    return df.to_dict(orient="records")


def get_revenue_waterfall(service) -> List[Dict[str, Any]]:
    """Return revenue expansion waterfall metrics by client acquisition cohort."""
    df = service.execute_to_df(SQLQueries.REVENUE_WATERFALL)
    return df.to_dict(orient="records")


def get_top_industries(service) -> List[Dict[str, Any]]:
    """Return the breakdown of the most valuable industries by revenue percentage share."""
    df = service.execute_to_df(SQLQueries.TOP_INDUSTRIES_REVENUE_SHARE)
    return df.to_dict(orient="records")


def get_revenue_heatmap_data(service) -> List[Dict[str, Any]]:
    """Return composite heat-grid coordinates crossing Country and Industry by ARR."""
    df = service.execute_to_df(SQLQueries.REVENUE_HEATMAP)
    return df.to_dict(orient="records")


def get_revenue_growth_rate(service) -> float:
    """Calculate the latest month-over-month MRR growth rate percentage."""
    df = service.execute_to_df(SQLQueries.REVENUE_GROWTH_HISTORICAL)
    if df.empty or len(df) < 2:
        return 0.0
    val = df.iloc[-1]["growth_pct"]
    return float(val) if val else 0.0


def get_revenue_summary_stats(service) -> Dict[str, Any]:
    """Retrieve full revenue segment summaries."""
    return {
        "mrr_by_month": get_revenue_by_month(service),
        "revenue_by_country": get_revenue_by_country(service),
        "revenue_by_industry": get_revenue_by_industry(service),
        "revenue_by_company_size": get_revenue_by_company_size(service),
        "top_accounts": get_top_revenue_accounts(service, 10),
        "lowest_accounts": get_lowest_revenue_accounts(service, 10),
        "subscription_breakdown": get_subscription_revenue_breakdown(service),
        "distribution_buckets": get_revenue_distribution(service),
        "waterfall": get_revenue_waterfall(service),
        "top_industries": get_top_industries(service),
        "heatmap": get_revenue_heatmap_data(service)
    }
