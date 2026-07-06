"""
analytics.py
------------
FastAPI API router exposing REST endpoints for the Business Analytics Layer.
Ensures responses are encapsulated in a standard envelope structure.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..analytics.analytics_service import AnalyticsService
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["Business Analytics"])
service = AnalyticsService()


def make_response(data: dict) -> dict:
    """Helper to envelope endpoints responses in standard JSON format."""
    return {
        "status": "success",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "data": data
    }


@router.get("/kpis")
def get_kpis_endpoint():
    """Fetch high-level business KPI metrics (MRR, ARR, growth, conversions, health)."""
    try:
        data = service.get_kpi_summary()
        return make_response(data)
    except Exception as e:
        logger.error("API failed on /analytics/kpis: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch KPIs: {e}"
        )


@router.get("/dashboard")
def get_dashboard_endpoint():
    """Fetch aggregated executive dashboard summary statistics."""
    try:
        data = service.get_kpi_summary()
        return make_response(data)
    except Exception as e:
        logger.error("API failed on /analytics/dashboard: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard: {e}"
        )


@router.get("/revenue")
def get_revenue_endpoint():
    """Fetch recurring revenue analytics, waterfall, heatmap, and segments."""
    try:
        data = service.get_revenue_summary()
        return make_response(data)
    except Exception as e:
        logger.error("API failed on /analytics/revenue: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch revenue analytics: {e}"
        )


@router.get("/customers")
def get_customers_endpoint():
    """Fetch customer tenure, cohort retention, and geographic segmentations."""
    try:
        data = service.get_customer_summary()
        return make_response(data)
    except Exception as e:
        logger.error("API failed on /analytics/customers: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch customer analytics: {e}"
        )


@router.get("/sales")
def get_sales_endpoint():
    """Fetch sales funnel transition counts, pipeline values, and reps leaderboard."""
    try:
        data = service.get_sales_summary()
        return make_response(data)
    except Exception as e:
        logger.error("API failed on /analytics/sales: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sales analytics: {e}"
        )


@router.get("/marketing")
def get_marketing_endpoint():
    """Fetch marketing spend, campaign performance, cost metrics, CPC, and conversion rates."""
    try:
        data = service.get_marketing_summary()
        return make_response(data)
    except Exception as e:
        logger.error("API failed on /analytics/marketing: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch marketing analytics: {e}"
        )


@router.get("/support")
def get_support_endpoint():
    """Fetch ticketing priorities/categories volumes, CSAT distribution, and resolution velocity."""
    try:
        data = service.get_support_summary()
        return make_response(data)
    except Exception as e:
        logger.error("API failed on /analytics/support: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch support analytics: {e}"
        )


@router.get("/usage")
def get_usage_endpoint():
    """Fetch active/inactive accounts, login timelines, and API usage stats."""
    try:
        data = service.get_usage_summary()
        return make_response(data)
    except Exception as e:
        logger.error("API failed on /analytics/usage: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch usage analytics: {e}"
        )


@router.get("/account-health")
def get_account_health_endpoint():
    """Fetch account health tier splits (Healthy, Medium Risk, Critical) and risk accounts."""
    try:
        data = service.get_account_health_summary()
        return make_response(data)
    except Exception as e:
        logger.error("API failed on /analytics/account-health: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch health analytics: {e}"
        )


@router.get("/forecast")
def get_forecast_endpoint(months: int = Query(6, ge=1, le=24)):
    """Fetch MRR moving average projections and historical growth rates forecasts."""
    try:
        data = service.get_forecast(months)
        return make_response(data)
    except Exception as e:
        logger.error("API failed on /analytics/forecast: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate forecasts: {e}"
        )


@router.get("/business-insights")
def get_business_insights_endpoint():
    """Fetch automated rules-based business executive insights and recommendations."""
    try:
        res = service.get_business_insights()
        return make_response(res["insights"])
    except Exception as e:
        logger.error("API failed on /analytics/business-insights: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {e}"
        )


@router.post("/clear-cache", status_code=status.HTTP_200_OK)
def clear_cache_endpoint():
    """Trigger manual eviction of cached query results."""
    try:
        service.clear_cache()
        return {"status": "success", "message": "Query cache cleared successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {e}"
        )


@router.post("/generate-reports", status_code=status.HTTP_201_CREATED)
def generate_reports_endpoint():
    """Manually trigger generation of all analytics summary CSV reports."""
    try:
        service.generate_all_reports()
        return {"status": "success", "message": "All summary reports written to reports/ directory."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate reports: {e}"
        )
