"""
sales_analytics.py
------------------
Computes sales analytics including funnel transition rates, pipeline value,
reps performance, win rates, and won/lost distributions.
"""

from typing import Dict, Any, List
from .sql_queries import SQLQueries


def get_sales_funnel(service) -> List[Dict[str, Any]]:
    """Return stage funnel counts, total values, and averages."""
    df = service.execute_to_df(SQLQueries.SALES_FUNNEL_TRANSITION)
    return df.to_dict(orient="records")


def get_won_opportunities(service) -> List[Dict[str, Any]]:
    """Return won deals including account details and values."""
    query = """
    SELECT 
        o.opportunity_id,
        a.company_name,
        o.sales_rep,
        o.deal_value,
        o.actual_close_date
    FROM opportunities o
    JOIN accounts a ON o.account_id = a.account_id
    WHERE o.status = 'Closed Won'
    ORDER BY o.actual_close_date DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_lost_opportunities(service) -> List[Dict[str, Any]]:
    """Return lost deals including account details and values."""
    query = """
    SELECT 
        o.opportunity_id,
        a.company_name,
        o.sales_rep,
        o.deal_value,
        o.actual_close_date
    FROM opportunities o
    JOIN accounts a ON o.account_id = a.account_id
    WHERE o.status = 'Closed Lost'
    ORDER BY o.actual_close_date DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_average_deal_value(service) -> float:
    """Return the average deal value of won opportunities."""
    val = service.execute_scalar(SQLQueries.AVG_DEAL_SIZE)
    return float(val) if val else 0.0


def get_pipeline_value(service) -> float:
    """Return the total value of all currently open opportunities."""
    query = "SELECT SUM(deal_value) FROM opportunities WHERE status = 'Open';"
    val = service.execute_scalar(query)
    return float(val) if val else 0.0


def get_stage_distribution(service) -> List[Dict[str, Any]]:
    """Return opportunity counts and sums grouped by stages."""
    query = """
    SELECT 
        stage,
        COUNT(opportunity_id) AS count,
        SUM(deal_value) AS total_value
    FROM opportunities
    GROUP BY stage
    ORDER BY count DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_probability_analysis(service) -> List[Dict[str, Any]]:
    """Return probability ranges and value metrics by stage."""
    df = service.execute_to_df(SQLQueries.SALES_FUNNEL_TRANSITION)
    return df.to_dict(orient="records")


def get_sales_rep_performance(service) -> List[Dict[str, Any]]:
    """Return sales rep opportunity statistics and win rates."""
    df = service.execute_to_df(SQLQueries.SALES_REP_WIN_RATE)
    return df.to_dict(orient="records")


def get_top_sales_representatives(service, limit: int = 5) -> List[Dict[str, Any]]:
    """Return ranking list of sales reps based on won revenue."""
    df = service.execute_to_df(SQLQueries.TOP_SALES_REPS_LEADERBOARD)
    return df.head(limit).to_dict(orient="records")


def get_sales_summary_stats(service) -> Dict[str, Any]:
    """Retrieve full sales analytics summaries."""
    return {
        "funnel": get_sales_funnel(service),
        "total_pipeline_value": get_pipeline_value(service),
        "avg_deal_value": get_average_deal_value(service),
        "stage_distribution": get_stage_distribution(service),
        "won_vs_lost_monthly": service.execute_to_df(SQLQueries.WON_VS_LOST_BY_MONTH).to_dict(orient="records"),
        "rep_performance": get_sales_rep_performance(service),
        "top_reps_leaderboard": get_top_sales_representatives(service, 10)
    }
