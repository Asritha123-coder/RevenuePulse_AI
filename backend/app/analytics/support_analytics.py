"""
support_analytics.py
---------------------
Computes support and ticketing analytics, queue loads, resolution rates, priorities,
categories, and CSAT customer satisfaction distributions.
"""

from typing import Dict, Any, List
from .sql_queries import SQLQueries


def get_open_tickets(service) -> List[Dict[str, Any]]:
    """Return all support tickets currently in open or in progress statuses."""
    query = """
    SELECT 
        t.ticket_id,
        a.company_name,
        t.priority,
        t.issue_category,
        t.status,
        t.created_date
    FROM support_tickets t
    JOIN accounts a ON t.account_id = a.account_id
    WHERE t.status IN ('Open', 'In Progress')
    ORDER BY t.created_date ASC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_resolved_tickets(service) -> List[Dict[str, Any]]:
    """Return resolved support tickets with resolution time and satisfaction score."""
    query = """
    SELECT 
        t.ticket_id,
        a.company_name,
        t.priority,
        t.issue_category,
        t.status,
        t.created_date,
        t.resolved_date,
        t.satisfaction_score
    FROM support_tickets t
    JOIN accounts a ON t.account_id = a.account_id
    WHERE t.status IN ('Resolved', 'Closed')
    ORDER BY t.resolved_date DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_resolution_time(service) -> List[Dict[str, Any]]:
    """Return average days required to resolve tickets grouped by category and priority."""
    df = service.execute_to_df(SQLQueries.RESOLUTION_VELOCITY_BY_CATEGORY)
    return df.to_dict(orient="records")


def get_tickets_by_category(service) -> List[Dict[str, Any]]:
    """Return tickets volumes and CSAT averages grouped by issue category."""
    df = service.execute_to_df(SQLQueries.SUPPORT_TICKETS_BY_CATEGORY)
    return df.to_dict(orient="records")


def get_tickets_by_priority(service) -> List[Dict[str, Any]]:
    """Return support ticket volumes and resolution split counts grouped by priority."""
    df = service.execute_to_df(SQLQueries.SUPPORT_TICKETS_BY_PRIORITY)
    return df.to_dict(orient="records")


def get_customer_satisfaction(service) -> List[Dict[str, Any]]:
    """Return client satisfaction (CSAT) rating percentages distributions."""
    df = service.execute_to_df(SQLQueries.CSAT_DISTRIBUTION)
    return df.to_dict(orient="records")


def get_support_load(service) -> List[Dict[str, Any]]:
    """Return historical ticket creation and resolution trends grouped by month."""
    df = service.execute_to_df(SQLQueries.SUPPORT_TICKET_LOAD_BY_MONTH)
    return df.to_dict(orient="records")


def get_support_summary_stats(service) -> Dict[str, Any]:
    """Retrieve full support analytics summaries."""
    # Count open vs resolved
    metrics = {"Open": 0, "Resolved": 0, "Total": 0}
    priority_stats = get_tickets_by_priority(service)
    for p in priority_stats:
        metrics["Open"] += p.get("open_count", 0)
        metrics["Resolved"] += p.get("resolved_count", 0)
        metrics["Total"] += p.get("count", 0)
        
    return {
        "overall_volume": metrics,
        "tickets_by_priority": priority_stats,
        "tickets_by_category": get_tickets_by_category(service),
        "resolution_time_analysis": get_resolution_time(service),
        "csat_distribution": get_customer_satisfaction(service),
        "monthly_load": get_support_load(service),
        "high_volume_accounts": service.execute_to_df(SQLQueries.HIGH_VOLUME_SUPPORT_ACCOUNTS).to_dict(orient="records")
    }
