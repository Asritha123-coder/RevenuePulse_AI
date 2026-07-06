"""
business_insights.py
--------------------
Rules-based business intelligence engine. Programmatically flags anomalies,
risk variables, growth drivers, and outputs executive recommendations.
"""

from typing import Dict, Any, List
import pandas as pd

from .revenue_analytics import get_top_industries
from .marketing_analytics import get_best_campaign
from .account_health import get_account_health_scores


def generate_business_insights(service) -> Dict[str, Any]:
    """
    Generate structured, rules-based business insights and recommendations
    for C-level executives.
    """
    insights = {}
    recommendations = []
    
    # ── 1. Highest Revenue Industry ─────────────────────────
    industries = get_top_industries(service)
    if industries:
        top_industry = industries[0]
        insights["top_revenue_industry"] = {
            "industry": top_industry["industry"],
            "arr": top_industry["arr"],
            "percentage_share": top_industry["share_pct"]
        }
    else:
        insights["top_revenue_industry"] = None
        
    # ── 2. Fastest Growing Region (last 90 days) ───────────
    query = """
    SELECT 
        COALESCE(country, 'Unknown') AS country,
        COUNT(account_id) AS new_accounts_count,
        SUM(annual_revenue) AS new_revenue
    FROM accounts
    WHERE customer_since >= NOW() - INTERVAL '90 days'
    GROUP BY country
    ORDER BY new_accounts_count DESC, new_revenue DESC
    LIMIT 1;
    """
    region_df = service.execute_to_df(query)
    if not region_df.empty:
        insights["fastest_growing_region"] = {
            "country": region_df.iloc[0]["country"],
            "new_accounts": int(region_df.iloc[0]["new_accounts_count"]),
            "new_revenue": float(region_df.iloc[0]["new_revenue"]) if pd.notnull(region_df.iloc[0]["new_revenue"]) else 0.0
        }
    else:
        insights["fastest_growing_region"] = None

    # ── 3. Campaign with Highest ROI ────────────────────────
    best_campaign = get_best_campaign(service)
    if best_campaign:
        insights["top_roi_campaign"] = {
            "name": best_campaign["campaign_name"],
            "type": best_campaign["campaign_type"],
            "roi": best_campaign["ROI"],
            "leads": best_campaign["leads_generated"]
        }
    else:
        insights["top_roi_campaign"] = None

    # ── 4. Accounts at Risk & Renewal Risks ──────────────────
    health_scores = get_account_health_scores(service)
    critical_accounts = []
    renewal_risks = []
    
    if health_scores:
        df_health = pd.DataFrame(health_scores)
        critical_df = df_health[df_health["health_category"] == "Critical"].sort_values(by="mrr", ascending=False)
        critical_accounts = critical_df.head(5)[["account_id", "company_name", "health_score", "mrr", "industry"]].to_dict(orient="records")
        
        # Renewal risk: renewal date in the next 90 days (or past due) and health score < 50
        df_health["renewal_date"] = pd.to_datetime(df_health["renewal_date"], errors="coerce")
        today = pd.to_datetime("today")
        
        risk_renew_df = df_health[
            (df_health["health_score"] < 50.0) & 
            (
                (df_health["renewal_date"] <= today + pd.Timedelta(days=90)) | 
                (df_health["renewal_date"] < today)
            )
        ].sort_values(by="mrr", ascending=False)
        
        renewal_risks = risk_renew_df.head(5)[["account_id", "company_name", "health_score", "mrr", "renewal_date"]].to_dict(orient="records")
        # Format dates for JSON serializer
        for r in renewal_risks:
            if pd.notnull(r["renewal_date"]):
                r["renewal_date"] = r["renewal_date"].strftime("%Y-%m-%d")
            else:
                r["renewal_date"] = None
                
    insights["accounts_at_risk_count"] = len(critical_accounts)
    insights["accounts_at_risk_list"] = critical_accounts
    insights["renewal_risks"] = renewal_risks

    # ── 5. Revenue Anomalies ────────────────────────────────
    # E.g. Accounts with active subscriptions but 0 product logins
    query_logins = """
    SELECT 
        a.account_id,
        a.company_name,
        s.monthly_revenue AS mrr
    FROM accounts a
    JOIN subscriptions s ON a.account_id = s.account_id
    WHERE s.status = 'Active' 
      AND a.account_id NOT IN (SELECT DISTINCT account_id FROM product_usage WHERE login_count > 0)
    ORDER BY mrr DESC
    LIMIT 5;
    """
    anomaly_df = service.execute_to_df(query_logins)
    insights["revenue_anomalies_zero_engagement"] = anomaly_df.to_dict(orient="records")

    # ── 6. Customer Engagement Trends ───────────────────────
    # Calculate login growth or feature adoption distribution
    query_engagement = """
    SELECT 
        adoption_segment,
        COUNT(*) AS count
    FROM (
        SELECT 
            CASE 
                WHEN feature_usage_score >= 80 THEN 'High Adoption (>80)'
                WHEN feature_usage_score >= 50 AND feature_usage_score < 80 THEN 'Medium Adoption (50-80)'
                ELSE 'Low Adoption (<50)'
            END AS adoption_segment
        FROM product_usage
    ) sub
    GROUP BY adoption_segment;
    """
    engagement_df = service.execute_to_df(query_engagement)
    insights["feature_adoption_segments"] = engagement_df.to_dict(orient="records")

    # ── 7. Executive Recommendations ─────────────────────────
    # Write programmatically triggered recommendations
    if insights["top_revenue_industry"]:
        ind = insights["top_revenue_industry"]["industry"]
        recommendations.append(
            f"Double down on sales pipelines inside the '{ind}' industry, "
            f"which represents the highest ARR revenue contributor."
        )
        
    if insights["top_roi_campaign"]:
        c_type = insights["top_roi_campaign"]["type"]
        recommendations.append(
            f"Increase Q3 marketing budget allocations toward '{c_type}' campaigns, "
            f"which currently generates the highest ROI across digital channels."
        )
        
    if critical_accounts:
        top_risk = critical_accounts[0]["company_name"]
        recommendations.append(
            f"Assign a Customer Success Manager immediately to '{top_risk}' "
            f"due to Critical Health Score drops (<40) on premium accounts."
        )
        
    if insights["revenue_anomalies_zero_engagement"]:
        count_zero = len(insights["revenue_anomalies_zero_engagement"])
        recommendations.append(
            f"Review onboarding processes: Found {count_zero} accounts paying active "
            f"monthly subscriptions with 0 product logins."
        )
        
    if renewal_risks:
        recommendations.append(
            f"Proactively trigger customer renewal interventions for {len(renewal_risks)} accounts "
            f"facing contract renewals in the next 90 days with health score indicators below 50."
        )
        
    insights["executive_recommendations"] = recommendations

    return {
        "status": "success",
        "insights": insights
    }
