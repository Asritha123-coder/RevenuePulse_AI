"""
generate_campaigns.py
---------------------
Generates a realistic Marketing Campaigns dataset for the RevenuePulse AI platform.

Campaign types: Email, LinkedIn, Google Ads, Events, Referral, Organic, Webinar
ROI is derived from conversions relative to spend.
Spend should NOT exceed budget — except for injected anomaly rows.

Intentional data quality issues:
  - ~3%  negative budget values
  - ~4%  future end dates beyond today
  - ~5%  missing ROI values

Target: datasets/raw/campaigns.csv
Rows  : 500
"""

import os
import random
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
from faker import Faker

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
fake = Faker()
Faker.seed(10)
random.seed(10)

NUM_CAMPAIGNS = 500

CAMPAIGN_TYPES = [
    "Email", "LinkedIn", "Google Ads",
    "Events", "Referral", "Organic", "Webinar",
]

# Budget ranges by campaign type (min, max) in USD
BUDGET_RANGES = {
    "Email":       (2_000,   15_000),
    "LinkedIn":    (5_000,   50_000),
    "Google Ads":  (10_000, 100_000),
    "Events":      (20_000, 200_000),
    "Referral":    (1_000,   10_000),
    "Organic":     (500,      5_000),
    "Webinar":     (3_000,   25_000),
}

# Typical conversion rates & leads per impression by type
PERFORMANCE_PROFILES = {
    "Email":       {"ctr": 0.025, "conv_rate": 0.12},
    "LinkedIn":    {"ctr": 0.008, "conv_rate": 0.08},
    "Google Ads":  {"ctr": 0.035, "conv_rate": 0.10},
    "Events":      {"ctr": 0.200, "conv_rate": 0.30},
    "Referral":    {"ctr": 0.100, "conv_rate": 0.25},
    "Organic":     {"ctr": 0.060, "conv_rate": 0.15},
    "Webinar":     {"ctr": 0.150, "conv_rate": 0.20},
}


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def random_date_between(start: date, end: date) -> date:
    """Return a random date between start and end (inclusive)."""
    delta = (end - start).days
    if delta <= 0:
        return start
    return start + timedelta(days=random.randint(0, delta))


def compute_roi(spend: float, conversions: int) -> float:
    """
    Compute ROI using a simple B2B SaaS revenue estimate.
    Assumes average deal value of $5,000 per conversion.

    ROI = ((Revenue - Spend) / Spend) * 100
    """
    avg_deal_value = random.uniform(3_000, 15_000)
    revenue = conversions * avg_deal_value
    if spend == 0:
        return 0.0
    return round(((revenue - spend) / spend) * 100, 2)


def generate_campaign_name(campaign_type: str, index: int) -> str:
    """Create a realistic campaign name."""
    themes = [
        "Q1", "Q2", "Q3", "Q4",
        "Summer", "Winter", "Spring", "Fall",
        "Launch", "Awareness", "Retargeting",
        "ABM", "Nurture", "Re-engagement",
    ]
    verbs = [
        "Boost", "Drive", "Scale", "Accelerate",
        "Maximize", "Grow", "Convert", "Engage",
    ]
    theme = random.choice(themes)
    verb = random.choice(verbs)
    year = random.randint(2023, 2026)
    return f"{theme} {campaign_type} {verb} {year} #{index}"


def generate_campaigns() -> pd.DataFrame:
    """
    Generate 500 campaign records with realistic performance metrics.

    Returns a clean DataFrame before quality-issue injection.
    """
    today = date.today()
    records = []

    for i in range(1, NUM_CAMPAIGNS + 1):
        campaign_id   = f"CMP{i:05d}"
        campaign_type = random.choice(CAMPAIGN_TYPES)
        campaign_name = generate_campaign_name(campaign_type, i)

        # Budget
        bmin, bmax = BUDGET_RANGES[campaign_type]
        budget = round(random.uniform(bmin, bmax), 2)

        # Spend: 60%–100% of budget (normal), leave anomaly injection for later
        spend_pct = random.uniform(0.60, 1.00)
        spend = round(budget * spend_pct, 2)

        # Dates
        start_date = random_date_between(date(2022, 1, 1), date(2025, 12, 31))
        duration   = random.randint(7, 90)          # campaign lasts 7–90 days
        end_date   = start_date + timedelta(days=duration)

        # Impressions → Clicks → Leads → Conversions
        profile      = PERFORMANCE_PROFILES[campaign_type]
        impressions  = random.randint(5_000, 500_000)
        clicks       = int(impressions * profile["ctr"] * random.uniform(0.7, 1.3))
        leads_gen    = int(clicks * random.uniform(0.10, 0.40))
        conversions  = int(leads_gen * profile["conv_rate"] * random.uniform(0.5, 1.5))
        conversions  = max(0, conversions)

        roi = compute_roi(spend, conversions)

        records.append({
            "campaign_id":      campaign_id,
            "campaign_name":    campaign_name,
            "campaign_type":    campaign_type,
            "budget":           budget,
            "spend":            spend,
            "impressions":      impressions,
            "clicks":           clicks,
            "leads_generated":  leads_gen,
            "conversions":      conversions,
            "ROI":              roi,
            "start_date":       start_date,
            "end_date":         end_date,
        })

    return pd.DataFrame(records)


def inject_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inject intentional data quality problems.

      - ~3%  negative budget (data entry error)
      - ~4%  future end_date beyond today (scheduling error)
      - ~5%  missing ROI (reporting gap)
      - ~2%  spend > budget (anomaly overspend)
    """
    today = date.today()

    # ── 3% Negative budget ────────────────────
    neg_budget_idx = df.sample(frac=0.03, random_state=11).index
    for idx in neg_budget_idx:
        df.at[idx, "budget"] = round(-abs(df.at[idx, "budget"]), 2)

    # ── 4% Future end_date ────────────────────
    future_idx = df.sample(frac=0.04, random_state=12).index
    for idx in future_idx:
        future_days = random.randint(180, 730)
        df.at[idx, "end_date"] = today + timedelta(days=future_days)

    # ── 5% Missing ROI ────────────────────────
    missing_roi_idx = df.sample(frac=0.05, random_state=13).index
    df.loc[missing_roi_idx, "ROI"] = None

    # ── 2% Spend exceeds budget ───────────────
    overspend_idx = df.sample(frac=0.02, random_state=14).index
    for idx in overspend_idx:
        budget_val = df.at[idx, "budget"]
        if pd.notnull(budget_val) and budget_val > 0:
            df.at[idx, "spend"] = round(budget_val * random.uniform(1.10, 1.50), 2)

    return df


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Persist the DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def print_summary(df: pd.DataFrame, output_path: Path) -> None:
    """Print a structured generation summary."""
    print("=" * 55)
    print("  Campaigns Dataset Generated Successfully")
    print("=" * 55)
    print(f"  Total Records  : {len(df):,}")
    print(f"  File Location  : {output_path}")
    print(f"  Columns        : {list(df.columns)}")
    print("=" * 55)


# ──────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────

def main():
    """Orchestrate campaign data generation."""
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent
    raw_dir      = project_root / "datasets" / "raw"
    output_path  = raw_dir / "campaigns.csv"

    try:
        print(f"Generating {NUM_CAMPAIGNS:,} campaigns...")
        df = generate_campaigns()

        print("Injecting data quality issues...")
        df = inject_quality_issues(df)

        print("Saving CSV...")
        save_csv(df, output_path)

        print_summary(df, output_path)

    except Exception as e:
        print(f"[ERROR] Unexpected error during campaign generation: {e}")
        raise


if __name__ == "__main__":
    main()
