"""
generate_subscriptions.py
--------------------------
Generates a realistic Subscriptions dataset for the RevenuePulse AI platform.

Plans   : Starter | Growth | Professional | Enterprise
Revenue : Monthly revenue depends on plan tier.
Enterprise accounts are biased toward the Enterprise plan.

Intentional data quality issues:
  - ~3%  missing monthly_revenue
  - ~2%  negative monthly_revenue
  - ~4%  expired renewal_date (in the past)

Target: datasets/raw/subscriptions.csv
Rows  : 3,000
"""

import random
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
from faker import Faker

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
fake = Faker()
Faker.seed(30)
random.seed(30)

NUM_SUBSCRIPTIONS = 3_000

# Monthly revenue ranges (USD) per plan
PLAN_REVENUE = {
    "Starter":      (99,   499),
    "Growth":       (500,  1_999),
    "Professional": (2_000, 7_499),
    "Enterprise":   (7_500, 50_000),
}

# ACV multiplier: annual = monthly * 12, with slight discount on annual
ACV_DISCOUNT_RANGE = (0.85, 1.00)   # 0–15% annual discount

SUBSCRIPTION_STATUSES = ["Active", "Cancelled", "Paused", "Trial"]

# Plan weights by company size
PLAN_WEIGHTS_BY_SIZE = {
    "Startup":       [45, 35, 15, 5],    # mostly Starter/Growth
    "Small Business":[20, 40, 30, 10],
    "Mid Market":    [5,  20, 50, 25],
    "Enterprise":    [1,  4,  15, 80],   # mostly Enterprise
}

PLANS = ["Starter", "Growth", "Professional", "Enterprise"]


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def load_accounts(raw_dir: Path) -> pd.DataFrame:
    """Load accounts with unique account_id and company_size."""
    path = raw_dir / "accounts.csv"
    if not path.exists():
        raise FileNotFoundError(f"accounts.csv not found at {path}.")
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset=["account_id"])
    return df[["account_id", "company_size"]]


def pick_plan(company_size: str) -> str:
    """Select a subscription plan weighted by company size."""
    weights = PLAN_WEIGHTS_BY_SIZE.get(company_size, [25, 25, 25, 25])
    return random.choices(PLANS, weights=weights, k=1)[0]


def generate_subscriptions(accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate subscription records linked to accounts.

    Business Rules:
      - One subscription per unique account (sampled up to NUM_SUBSCRIPTIONS).
      - Enterprise accounts are biased toward Enterprise plan.
      - Annual contract value = monthly_revenue * 12 * discount.
      - Active subscriptions renew in the future; Cancelled ones may be in the past.

    Returns a DataFrame with NUM_SUBSCRIPTIONS rows (before quality injection).
    """
    today = date.today()

    # Ensure we don't request more subscriptions than accounts
    all_accounts = accounts_df.to_dict("records")
    sample_size  = min(NUM_SUBSCRIPTIONS, len(all_accounts))
    sampled      = random.sample(all_accounts, sample_size)

    records = []

    for i, acc in enumerate(sampled, start=1):
        sub_id       = f"SUB{i:06d}"
        account_id   = acc["account_id"]
        company_size = acc.get("company_size", "Mid Market")

        plan = pick_plan(company_size)
        rev_lo, rev_hi = PLAN_REVENUE[plan]
        monthly_revenue = round(random.uniform(rev_lo, rev_hi), 2)

        # Annual contract value with possible discount
        discount = random.uniform(*ACV_DISCOUNT_RANGE)
        annual_contract_value = round(monthly_revenue * 12 * discount, 2)

        # Status: mostly Active
        status = random.choices(
            SUBSCRIPTION_STATUSES,
            weights=[70, 10, 10, 10],
            k=1
        )[0]

        # Renewal date
        if status == "Active":
            renewal_date = today + timedelta(days=random.randint(1, 365))
        elif status == "Trial":
            renewal_date = today + timedelta(days=random.randint(1, 30))
        else:
            # Cancelled / Paused — renewal was in the past or near future
            renewal_date = today - timedelta(days=random.randint(0, 180))

        records.append({
            "subscription_id":       sub_id,
            "account_id":            account_id,
            "plan":                  plan,
            "monthly_revenue":       monthly_revenue,
            "annual_contract_value": annual_contract_value,
            "renewal_date":          renewal_date,
            "status":                status,
        })

    return pd.DataFrame(records)


def inject_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inject intentional data quality problems.

      - ~3%  missing monthly_revenue (NaN)
      - ~2%  negative monthly_revenue
      - ~4%  expired renewal_date (in the past, for Active subscriptions)
    """
    today = date.today()

    # ── 3% Missing monthly_revenue ────────────
    missing_rev_idx = df.sample(frac=0.03, random_state=31).index
    df.loc[missing_rev_idx, "monthly_revenue"] = None

    # ── 2% Negative monthly_revenue ───────────
    neg_rev_idx = df.sample(frac=0.02, random_state=32).index
    for idx in neg_rev_idx:
        val = df.at[idx, "monthly_revenue"]
        if pd.notnull(val):
            df.at[idx, "monthly_revenue"] = -abs(val)

    # ── 4% Expired renewal_date (Active subs that should have renewed) ──
    active_mask = df["status"] == "Active"
    active_sample = df[active_mask].sample(frac=0.04, random_state=33).index
    for idx in active_sample:
        df.at[idx, "renewal_date"] = today - timedelta(
            days=random.randint(30, 365)
        )

    return df


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Persist the DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def print_summary(df: pd.DataFrame, output_path: Path) -> None:
    """Print a structured generation summary."""
    print("=" * 55)
    print("  Subscriptions Dataset Generated Successfully")
    print("=" * 55)
    print(f"  Total Records  : {len(df):,}")
    print(f"  File Location  : {output_path}")
    print(f"  Columns        : {list(df.columns)}")
    print("=" * 55)


# ──────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────

def main():
    """Orchestrate subscription data generation."""
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent
    raw_dir      = project_root / "datasets" / "raw"
    output_path  = raw_dir / "subscriptions.csv"

    try:
        print("Loading accounts...")
        accounts_df = load_accounts(raw_dir)

        print(f"Generating {NUM_SUBSCRIPTIONS:,} subscriptions...")
        df = generate_subscriptions(accounts_df)

        print("Injecting data quality issues...")
        df = inject_quality_issues(df)

        print("Saving CSV...")
        save_csv(df, output_path)

        print_summary(df, output_path)

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error during subscription generation: {e}")
        raise


if __name__ == "__main__":
    main()
