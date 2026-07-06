"""
forecast.py
-----------
Performs simple, rule-based revenue forecasting, including moving averages,
growth rate projections, and monthly timeline extrapolations.
"""

from typing import Dict, Any, List
import pandas as pd
from .revenue_analytics import get_revenue_by_month


def calculate_moving_average_forecast(service, forecast_months: int = 6) -> List[Dict[str, Any]]:
    """
    Project MRR for future months using a 3-month simple moving average (SMA).
    """
    history = get_revenue_by_month(service)
    if not history:
        return []
        
    df = pd.DataFrame(history)
    # Ensure sorted by month
    df = df.sort_values(by="month").reset_index(drop=True)
    
    # Exclude any current month that might be partial or future
    # Project based on the last 3 rows of actuals
    forecast_results = []
    
    # Start projection date based on last month in history
    last_month_str = df.iloc[-1]["month"]
    last_mrr = float(df.iloc[-1]["revenue"])
    
    # Calculate simple moving average of last 3 months
    if len(df) >= 3:
        sma_mrr = float(df.tail(3)["revenue"].mean())
    else:
        sma_mrr = last_mrr
        
    current_year = int(last_month_str.split("-")[0])
    current_month = int(last_month_str.split("-")[1])
    
    for i in range(1, forecast_months + 1):
        # Increment month
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
            
        proj_month = f"{current_year:04d}-{current_month:02d}"
        forecast_results.append({
            "month": proj_month,
            "projected_revenue": round(sma_mrr, 2),
            "type": "Moving Average (3-Month SMA)"
        })
        
    return forecast_results


def calculate_growth_projection_forecast(service, forecast_months: int = 6) -> List[Dict[str, Any]]:
    """
    Project MRR by applying the average historical growth rate to the latest MRR.
    """
    # Fetch historical MoM growth
    query = """
    WITH MonthlyRev AS (
        SELECT 
            TO_CHAR(renewal_date - INTERVAL '1 month', 'YYYY-MM') AS month,
            SUM(monthly_revenue) AS mrr
        FROM subscriptions
        WHERE status = 'Active'
        GROUP BY month
    )
    SELECT 
        month,
        mrr,
        ROUND(((mrr - LAG(mrr, 1) OVER (ORDER BY month)) / NULLIF(LAG(mrr, 1) OVER (ORDER BY month), 0)) * 100, 2) AS growth_pct
    FROM MonthlyRev
    ORDER BY month;
    """
    df = service.execute_to_df(query)
    if df.empty or len(df) < 2:
        return []
        
    # Get last record
    last_row = df.iloc[-1]
    last_month_str = last_row["month"]
    last_mrr = float(last_row["mrr"])
    
    # Average MoM growth rate (exclude first row as growth_pct is NaN)
    avg_growth = float(df["growth_pct"].dropna().mean()) / 100.0
    # Guard against extreme negative or positive rates
    avg_growth = max(-0.10, min(avg_growth, 0.15))
    
    forecast_results = []
    current_year = int(last_month_str.split("-")[0])
    current_month = int(last_month_str.split("-")[1])
    
    current_mrr = last_mrr
    for i in range(1, forecast_months + 1):
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
            
        proj_month = f"{current_year:04d}-{current_month:02d}"
        current_mrr = current_mrr * (1.0 + avg_growth)
        
        forecast_results.append({
            "month": proj_month,
            "projected_revenue": round(current_mrr, 2),
            "projected_growth_rate_pct": round(avg_growth * 100.0, 2),
            "type": "Growth Extrapolation"
        })
        
    return forecast_results


def get_forecast_summary(service, months: int = 6) -> Dict[str, Any]:
    """
    Combine moving average and growth rate projections.
    """
    ma_proj = calculate_moving_average_forecast(service, months)
    gr_proj = calculate_growth_projection_forecast(service, months)
    
    # Combine history + forecasts for dashboard charts
    history = get_revenue_by_month(service)
    
    chart_data = []
    for h in history:
        chart_data.append({
            "month": h["month"],
            "revenue": h["revenue"],
            "category": "Historical"
        })
        
    for p in gr_proj:
        chart_data.append({
            "month": p["month"],
            "revenue": p["projected_revenue"],
            "category": "Forecasted"
        })
        
    return {
        "moving_average_projection": ma_proj,
        "growth_extrapolation_projection": gr_proj,
        "combined_timeline_chart": chart_data,
        "forecast_horizon_months": months
    }
