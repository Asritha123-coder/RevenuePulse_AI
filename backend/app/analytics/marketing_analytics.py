"""
marketing_analytics.py
----------------------
Computes marketing and campaign statistics including spend, CPC, Cost-per-Lead (CPL),
CTR, conversion rates, and ROI analysis.
"""

from typing import Dict, Any, List
from .sql_queries import SQLQueries


def get_campaign_performance(service) -> List[Dict[str, Any]]:
    """Return comprehensive campaign metric details."""
    df = service.execute_to_df(SQLQueries.CAMPAIGN_PERFORMANCE_DETAIL)
    # Clean NaN values for JSON output compliance
    df = df.where(df.notnull(), None)
    return df.to_dict(orient="records")


def get_campaign_roi(service) -> List[Dict[str, Any]]:
    """Return campaign ROI performance summaries grouped by campaign type."""
    df = service.execute_to_df(SQLQueries.CAMPAIGN_PERFORMANCE_BY_TYPE)
    return df.to_dict(orient="records")


def get_cost_per_lead(service) -> List[Dict[str, Any]]:
    """Return CPL analysis for campaigns with positive lead count."""
    query = """
    SELECT 
        campaign_name,
        campaign_type,
        spend,
        leads_generated,
        ROUND((spend / NULLIF(leads_generated, 0))::NUMERIC, 2) AS cost_per_lead
    FROM campaigns
    WHERE spend > 0 AND leads_generated > 0
    ORDER BY cost_per_lead ASC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_ctr(service) -> List[Dict[str, Any]]:
    """Return Click-Through-Rate (CTR) analytics per campaign type."""
    query = """
    SELECT 
        campaign_type,
        SUM(impressions) AS impressions,
        SUM(clicks) AS clicks,
        ROUND((SUM(clicks)::NUMERIC / NULLIF(SUM(impressions), 0)::NUMERIC) * 100, 2) AS ctr_pct
    FROM campaigns
    GROUP BY campaign_type
    ORDER BY ctr_pct DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_cpc(service) -> List[Dict[str, Any]]:
    """Return Cost-Per-Click (CPC) metrics per campaign type."""
    query = """
    SELECT 
        campaign_type,
        SUM(spend) AS total_spend,
        SUM(clicks) AS total_clicks,
        ROUND((SUM(spend) / NULLIF(SUM(clicks), 0))::NUMERIC, 2) AS cpc
    FROM campaigns
    GROUP BY campaign_type
    ORDER BY cpc ASC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_conversion_rate(service) -> List[Dict[str, Any]]:
    """Return campaign conversion rates grouped by campaign type."""
    query = """
    SELECT 
        campaign_type,
        SUM(clicks) AS total_clicks,
        SUM(conversions) AS total_conversions,
        ROUND((SUM(conversions)::NUMERIC / NULLIF(SUM(clicks), 0)::NUMERIC) * 100, 2) AS conversion_rate_pct
    FROM campaigns
    GROUP BY campaign_type
    ORDER BY conversion_rate_pct DESC;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_best_campaign(service) -> Dict[str, Any]:
    """Return the campaign with the highest ROI."""
    df = service.execute_to_df(SQLQueries.CAMPAIGN_PERFORMANCE_DETAIL)
    if df.empty:
        return {}
    best = df.iloc[0].to_dict()
    # Clean float NaNs
    for k, v in best.items():
        if isinstance(v, float) and (v != v):  # NaN check
            best[k] = None
    return best


def get_worst_campaign(service) -> Dict[str, Any]:
    """Return the campaign with the lowest ROI."""
    df = service.execute_to_df(SQLQueries.CAMPAIGN_PERFORMANCE_DETAIL)
    if df.empty:
        return {}
    # Find last row which has not null ROI
    df_valid = df[df["ROI"].notna()]
    if df_valid.empty:
        return {}
    worst = df_valid.iloc[-1].to_dict()
    for k, v in worst.items():
        if isinstance(v, float) and (v != v):
            worst[k] = None
    return worst


def get_lead_source_analysis(service) -> List[Dict[str, Any]]:
    """Return contact attribution shares split by lead source."""
    df = service.execute_to_df(SQLQueries.LEAD_SOURCE_CONTRIBUTION)
    return df.to_dict(orient="records")


def get_marketing_spend(service) -> Dict[str, Any]:
    """Return total marketing budgets, actual spend, and utilization rates."""
    query = """
    SELECT 
        SUM(budget) AS total_budget,
        SUM(spend) AS total_spend,
        ROUND((SUM(spend) / NULLIF(SUM(budget), 0)) * 100, 2) AS spend_utilization_pct
    FROM campaigns;
    """
    df = service.execute_to_df(query)
    if df.empty:
        return {"total_budget": 0.0, "total_spend": 0.0, "spend_utilization_pct": 0.0}
    return df.iloc[0].to_dict()


def get_marketing_summary_stats(service) -> Dict[str, Any]:
    """Retrieve full marketing analytics summaries."""
    return {
        "campaign_performance": get_campaign_performance(service)[:15],  # limit to top 15 for summary
        "campaign_type_performance": get_campaign_roi(service),
        "ctr_by_type": get_ctr(service),
        "cpc_by_type": get_cpc(service),
        "conversion_rate_by_type": get_conversion_rate(service),
        "best_campaign": get_best_campaign(service),
        "worst_campaign": get_worst_campaign(service),
        "lead_source_analysis": get_lead_source_analysis(service),
        "spend_summary": get_marketing_spend(service)
    }
