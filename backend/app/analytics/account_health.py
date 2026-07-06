"""
account_health.py
------------------
Evaluates account health categories (Healthy, Medium Risk, Critical)
based on subscription status, support tickets, and feature utilization.
"""

from typing import Dict, Any, List
import pandas as pd


def get_account_health_scores(service) -> List[Dict[str, Any]]:
    """
    Fetch and categorise health scores for all accounts.
    """
    query = """
    WITH OpenTickets AS (
        SELECT account_id, COUNT(*) AS open_tickets_count
        FROM support_tickets
        WHERE status IN ('Open', 'In Progress')
        GROUP BY account_id
    ),
    LatestUsage AS (
        SELECT DISTINCT ON (account_id)
            account_id,
            account_health_score,
            login_count,
            feature_usage_score
        FROM product_usage
        ORDER BY account_id, last_login DESC
    ),
    ActiveSub AS (
        SELECT account_id, plan, monthly_revenue, renewal_date, status AS sub_status
        FROM subscriptions
    )
    SELECT 
        a.account_id,
        a.company_name,
        a.company_size,
        a.industry,
        COALESCE(u.account_health_score, 50.0) AS health_score,
        COALESCE(u.login_count, 0) AS login_count,
        COALESCE(u.feature_usage_score, 0.0) AS feature_score,
        COALESCE(t.open_tickets_count, 0) AS open_tickets,
        COALESCE(s.plan, 'None') AS plan,
        COALESCE(s.monthly_revenue, 0.0) AS mrr,
        s.sub_status,
        s.renewal_date,
        CASE 
            WHEN COALESCE(u.account_health_score, 50.0) >= 70.0 THEN 'Healthy'
            WHEN COALESCE(u.account_health_score, 50.0) >= 40.0 THEN 'Medium Risk'
            ELSE 'Critical'
        END AS health_category
    FROM accounts a
    LEFT JOIN LatestUsage u ON a.account_id = u.account_id
    LEFT JOIN OpenTickets t ON a.account_id = t.account_id
    LEFT JOIN ActiveSub s ON a.account_id = s.account_id;
    """
    df = service.execute_to_df(query)
    return df.to_dict(orient="records")


def get_health_summary(service) -> Dict[str, Any]:
    """
    Return counts and percentages of accounts in each health tier (Healthy, Medium Risk, Critical).
    """
    data = get_account_health_scores(service)
    if not data:
        return {
            "counts": {"Healthy": 0, "Medium Risk": 0, "Critical": 0},
            "percentages": {"Healthy": 0.0, "Medium Risk": 0.0, "Critical": 0.0},
            "critical_risk_sample": []
        }
        
    df = pd.DataFrame(data)
    
    # Calculate counts
    counts = df["health_category"].value_counts().to_dict()
    total = len(df)
    
    # Ensure all keys are represented
    for cat in ["Healthy", "Medium Risk", "Critical"]:
        if cat not in counts:
            counts[cat] = 0
            
    # Calculate percentages
    pcts = {cat: round((cnt / total) * 100.0, 2) for cat, cnt in counts.items()}
    
    # Extract top critical risk accounts (lowest health score first, sorted by ARR / MRR value)
    critical_df = df[df["health_category"] == "Critical"].sort_values(by=["health_score", "mrr"], ascending=[True, False])
    critical_sample = critical_df.head(15).to_dict(orient="records")
    
    # Industry and company size breakdowns of critical accounts
    critical_industry = critical_df["industry"].value_counts().head(5).to_dict() if not critical_df.empty else {}
    critical_size = critical_df["company_size"].value_counts().to_dict() if not critical_df.empty else {}
    
    return {
        "counts": counts,
        "percentages": pcts,
        "critical_risk_sample": critical_sample,
        "risk_breakdown_by_industry": critical_industry,
        "risk_breakdown_by_size": critical_size,
        "total_accounts_evaluated": total
    }
