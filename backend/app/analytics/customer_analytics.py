"""
customer_analytics.py
---------------------
Computes advanced customer segmentations, cohort retention rates, customer lifetime value (CLV),
geographic distributions, and customer activity summaries.
"""

from typing import Dict, Any, List
from .sql_queries import SQLQueries


def get_customer_segmentation(service) -> List[Dict[str, Any]]:
    """Return count, employees, and revenue averages grouped by size and industry."""
    df = service.execute_to_df(SQLQueries.CUSTOMER_SEGMENTATION)
    return df.to_dict(orient="records")


def get_retention_rate(service) -> List[Dict[str, Any]]:
    """Return cohort retention rate percentages calculated month-over-month."""
    df = service.execute_to_df(SQLQueries.CUSTOMER_RETENTION_RATE)
    return df.to_dict(orient="records")


def get_customer_lifetime_value(service) -> List[Dict[str, Any]]:
    """Return accounts with their computed Customer Lifetime Value (CLV) based on customer duration and ARR."""
    df = service.execute_to_df(SQLQueries.CUSTOMER_LIFETIME_VALUE)
    return df.to_dict(orient="records")


def get_avg_customer_age(service) -> List[Dict[str, Any]]:
    """Return average days of tenure as a customer grouped by company size."""
    df = service.execute_to_df(SQLQueries.AVG_CUSTOMER_AGE)
    return df.to_dict(orient="records")


def get_new_customers(service) -> List[Dict[str, Any]]:
    """Return accounts acquired during the last 90 days."""
    query = """
    SELECT 
        account_id,
        company_name,
        company_size,
        industry,
        customer_since,
        annual_revenue
    FROM accounts
    WHERE customer_since >= NOW() - INTERVAL '90 days'
    ORDER BY customer_since DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_inactive_customers(service) -> List[Dict[str, Any]]:
    """Return accounts flagged inactive or without activity in 90 days."""
    df = service.execute_to_df(SQLQueries.INACTIVE_CUSTOMERS_LIST)
    return df.to_dict(orient="records")


def get_top_customers_by_usage(service, limit: int = 15) -> List[Dict[str, Any]]:
    """Return highest usage accounts sorted by API calls."""
    df = service.execute_to_df(SQLQueries.TOP_CUSTOMERS_BY_USAGE, {"limit": limit})
    return df.to_dict(orient="records")


def get_customer_geographic_distribution(service) -> List[Dict[str, Any]]:
    """Return nested rollout aggregation summaries crossing Country and State."""
    df = service.execute_to_df(SQLQueries.CUSTOMER_GEOGRAPHIC_DISTRIBUTION)
    return df.to_dict(orient="records")


def get_country_distribution(service) -> List[Dict[str, Any]]:
    """Return counts and revenue sums by country."""
    query = """
    SELECT 
        COALESCE(country, 'Unknown') AS country,
        COUNT(account_id) AS customer_count,
        SUM(annual_revenue) AS total_revenue
    FROM accounts
    GROUP BY country
    ORDER BY customer_count DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_industry_distribution(service) -> List[Dict[str, Any]]:
    """Return counts and revenue sums by industry."""
    query = """
    SELECT 
        COALESCE(industry, 'Unknown') AS industry,
        COUNT(account_id) AS customer_count,
        SUM(annual_revenue) AS total_revenue
    FROM accounts
    GROUP BY industry
    ORDER BY customer_count DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_company_size_distribution(service) -> List[Dict[str, Any]]:
    """Return counts and percentages split by company size category."""
    df = service.execute_to_df(SQLQueries.CUSTOMER_SIZE_SPLIT)
    return df.to_dict(orient="records")


def get_customer_summary_stats(service) -> Dict[str, Any]:
    """Retrieve full customer analytics summaries."""
    return {
        "segmentation": get_customer_segmentation(service),
        "retention_rate": get_retention_rate(service),
        "customer_lifetime_value": get_customer_lifetime_value(service)[:15],  # limit to top 15 for summary
        "avg_customer_age": get_avg_customer_age(service),
        "new_customers_last_90d": get_new_customers(service),
        "inactive_customers": get_inactive_customers(service),
        "top_customers_usage": get_top_customers_by_usage(service, 10),
        "geographic_distribution": get_customer_geographic_distribution(service),
        "country_distribution": get_country_distribution(service),
        "industry_distribution": get_industry_distribution(service),
        "company_size_distribution": get_company_size_distribution(service)
    }
