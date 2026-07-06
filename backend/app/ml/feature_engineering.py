"""
feature_engineering.py
----------------------
Feature engineering engine for the ML layer. Computes corporate metrics:
  - Support Burden, Renewal Risk, Engagement Score, Revenue per Employee,
    Deal Success Rate, Customer Value Score, and Monthly Spend.
"""

from datetime import date
import pandas as pd
import numpy as np


def engineer_features(
    df_accounts: pd.DataFrame,
    df_subs: pd.DataFrame,
    df_opps: pd.DataFrame,
    df_usage: pd.DataFrame,
    df_web: pd.DataFrame,
    df_tickets: pd.DataFrame
) -> pd.DataFrame:
    """
    Aggragate relational tables and engineer corporate features.
    
    Returns:
        DataFrame indexed by account_id containing all features.
    """
    today = pd.to_datetime(date.today())

    # Ensure accounts are unique
    df_feat = df_accounts.drop_duplicates(subset=["account_id"]).set_index("account_id").copy()

    # 1. Customer Age in Days
    df_feat["customer_since"] = pd.to_datetime(df_feat["customer_since"], errors="coerce")
    df_feat["customer_age_days"] = (today - df_feat["customer_since"]).dt.days.fillna(365).astype(int)
    df_feat.loc[df_feat["customer_age_days"] < 0, "customer_age_days"] = 0

    # 2. Revenue Per Employee
    df_feat["employee_count"] = pd.to_numeric(df_feat["employee_count"], errors="coerce").fillna(1)
    df_feat["annual_revenue"] = pd.to_numeric(df_feat["annual_revenue"], errors="coerce").fillna(0.0)
    df_feat["revenue_per_employee"] = df_feat["annual_revenue"] / df_feat["employee_count"].replace(0, 1)

    # 3. Monthly Spend & ACV (from Subscriptions)
    df_subs_clean = df_subs.drop_duplicates(subset=["account_id"]).set_index("account_id")
    df_feat["monthly_spend"] = df_subs_clean["monthly_revenue"].reindex(df_feat.index).fillna(0.0)
    df_feat["annual_contract_value"] = df_subs_clean["annual_contract_value"].reindex(df_feat.index).fillna(0.0)
    
    # 4. Customer Value Score
    # Formula: ACV * (Age in days / 365)
    df_feat["customer_value_score"] = df_feat["annual_contract_value"] * (df_feat["customer_age_days"] / 365.0)

    # 5. Deal Success Rate (from Opportunities)
    # count Won / Closed (Won + Lost)
    df_opps_closed = df_opps[df_opps["status"].isin(["Closed Won", "Closed Lost"])].copy()
    opps_grouped = df_opps_closed.groupby("account_id")
    won_count = df_opps_closed[df_opps_closed["status"] == "Closed Won"].groupby("account_id")["opportunity_id"].count()
    total_closed = opps_grouped["opportunity_id"].count()
    
    success_rate = (won_count / total_closed).reindex(df_feat.index).fillna(0.0)
    df_feat["deal_success_rate"] = success_rate

    # 6. Usage Score & Engagement Score (from Product Usage & Web Activity)
    df_usage_agg = df_usage.groupby("account_id").agg({
        "login_count": "sum",
        "active_users": "max",
        "api_calls": "sum",
        "storage_used_gb": "sum",
        "feature_usage_score": "mean"
    }).reindex(df_feat.index).fillna(0.0)

    df_web_agg = df_web.groupby("account_id").agg({
        "sessions": "sum",
        "page_views": "sum",
        "average_session_time": "mean"
    }).reindex(df_feat.index).fillna(0.0)

    # Combine usage features
    df_feat["login_count"] = df_usage_agg["login_count"]
    df_feat["api_calls"] = df_usage_agg["api_calls"]
    df_feat["storage_used_gb"] = df_usage_agg["storage_used_gb"]
    df_feat["feature_usage_score"] = df_usage_agg["feature_usage_score"]
    df_feat["web_sessions"] = df_web_agg["sessions"]

    # Usage Score: normalized index combining API Calls + Logins + Storage
    max_api = max(1.0, df_feat["api_calls"].max())
    max_logins = max(1.0, df_feat["login_count"].max())
    df_feat["usage_score"] = ((df_feat["api_calls"] / max_api) * 50.0) + ((df_feat["login_count"] / max_logins) * 50.0)

    # Engagement Score: combine Feature Usage + Web sessions
    max_sessions = max(1.0, df_feat["web_sessions"].max())
    df_feat["engagement_score"] = (df_feat["feature_usage_score"] * 0.6) + ((df_feat["web_sessions"] / max_sessions) * 40.0)

    # 7. Support Burden (from Support Tickets)
    # formula: count tickets * 5 + count open tickets * 10 - average CSAT * 2
    tickets_grouped = df_tickets.groupby("account_id")
    total_tickets = tickets_grouped["ticket_id"].count()
    open_tickets = df_tickets[df_tickets["status"].isin(["Open", "In Progress"])].groupby("account_id")["ticket_id"].count()
    avg_csat = df_tickets[df_tickets["satisfaction_score"].notnull()].groupby("account_id")["satisfaction_score"].mean()

    df_feat["total_tickets"] = total_tickets.reindex(df_feat.index).fillna(0.0)
    df_feat["open_tickets"] = open_tickets.reindex(df_feat.index).fillna(0.0)
    df_feat["avg_csat"] = avg_csat.reindex(df_feat.index).fillna(3.0)  # assume neutral CSAT if none

    df_feat["support_burden"] = (df_feat["total_tickets"] * 5.0) + (df_feat["open_tickets"] * 10.0) - (df_feat["avg_csat"] * 2.0)
    df_feat.loc[df_feat["support_burden"] < 0, "support_burden"] = 0.0

    # 8. Renewal Risk
    # Based on expired renewal date (past due) or high support burden combined with low logins
    df_subs_clean["renewal_date"] = pd.to_datetime(df_subs_clean["renewal_date"], errors="coerce")
    days_to_renew = (df_subs_clean["renewal_date"] - today).dt.days.reindex(df_feat.index).fillna(365)
    
    # Calculate renewal risk (0 to 100)
    # If expired (days_to_renew < 0), risk is high. If low usage (logins < 10) and high tickets, risk is higher.
    renewal_risk = np.zeros(len(df_feat))
    for idx, (acc_id, row) in enumerate(df_feat.iterrows()):
        r_days = days_to_renew.loc[acc_id]
        risk = 30.0  # base risk
        if r_days < 0:
            risk += 40.0  # expired renewal date adds risk
        elif r_days < 30:
            risk += 20.0  # upcoming renewal
            
        if row["login_count"] < 100:
            risk += 20.0  # low adoption
            
        if row["support_burden"] > 50:
            risk += 10.0  # high friction
            
        renewal_risk[idx] = min(100.0, risk)
        
    df_feat["renewal_risk"] = renewal_risk

    # 9. Campaign Score (campaign conversions relative to budget)
    # We can default to a generic index
    df_feat["campaign_score"] = np.random.uniform(20.0, 80.0, size=len(df_feat))

    # Reset index to return account_id as column
    return df_feat.reset_index()
