"""
generate_opportunities.py
--------------------------
Generates a realistic Sales Opportunities dataset for the RevenuePulse AI platform.

Pipeline stages: Prospecting → Qualified → Proposal → Negotiation → Won / Lost
Enterprise accounts receive larger deal values.
Probability increases with pipeline stage.
Won deals have an actual_close_date; Lost deals may have null.

Intentional data quality issues:
  - ~2%  negative deal_value
  - ~3%  duplicate opportunity rows
  - ~4%  future expected_close_date

Target: datasets/raw/opportunities.csv
Rows  : ~12,000
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
Faker.seed(20)
random.seed(20)

NUM_OPPORTUNITIES = 12_000

# Stage → (probability_range, weight)
STAGE_CONFIG = {
    "Prospecting": {"prob_range": (0.05, 0.20), "weight": 20},
    "Qualified":   {"prob_range": (0.20, 0.40), "weight": 25},
    "Proposal":    {"prob_range": (0.40, 0.60), "weight": 20},
    "Negotiation": {"prob_range": (0.60, 0.80), "weight": 15},
    "Won":         {"prob_range": (1.00, 1.00), "weight": 12},
    "Lost":        {"prob_range": (0.00, 0.00), "weight": 8},
}

STAGES       = list(STAGE_CONFIG.keys())
STAGE_WEIGHTS = [STAGE_CONFIG[s]["weight"] for s in STAGES]

SALES_REPS = [
    "Rahul Sharma", "Priya Singh", "John Miller", "Sneha Reddy",
    "Arjun Verma",  "David Wilson", "Sarah Johnson", "Meera Nair",
    "Carlos Rivera", "Aisha Patel",  "Tom Brady",    "Nina Chen",
]

# Deal value multipliers by company size
DEAL_VALUE_BY_SIZE = {
    "Startup":       (2_000,    25_000),
    "Small Business":(10_000,   80_000),
    "Mid Market":    (50_000,  300_000),
    "Enterprise":    (200_000, 2_000_000),
}


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def load_accounts(raw_dir: Path) -> pd.DataFrame:
    """Load accounts and return relevant columns with unique account_id."""
    path = raw_dir / "accounts.csv"
    if not path.exists():
        raise FileNotFoundError(f"accounts.csv not found at {path}.")
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset=["account_id"])
    # Normalise company_size: only keep known values
    known_sizes = list(DEAL_VALUE_BY_SIZE.keys())
    df = df[df["company_size"].isin(known_sizes)].copy()
    return df[["account_id", "company_size"]]


def deal_value_for_account(company_size: str) -> float:
    """Return a realistic deal value based on company size."""
    lo, hi = DEAL_VALUE_BY_SIZE.get(company_size, (5_000, 100_000))
    return round(random.uniform(lo, hi), 2)


def generate_opportunities(accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate opportunity records linked to accounts.

    Returns a DataFrame with NUM_OPPORTUNITIES rows (before duplication injection).
    """
    account_ids  = accounts_df["account_id"].tolist()
    size_map     = accounts_df.set_index("account_id")["company_size"].to_dict()
    today        = date.today()

    records = []

    for i in range(1, NUM_OPPORTUNITIES + 1):
        opp_id     = f"OPP{i:07d}"
        account_id = random.choice(account_ids)
        company_size = size_map[account_id]

        sales_rep  = random.choice(SALES_REPS)
        stage      = random.choices(STAGES, weights=STAGE_WEIGHTS, k=1)[0]

        # Probability
        lo, hi     = STAGE_CONFIG[stage]["prob_range"]
        probability = round(random.uniform(lo, hi), 2)

        deal_value = deal_value_for_account(company_size)

        # Dates
        expected_close = fake.date_between(start_date="-6m", end_date="+12m")

        if stage == "Won":
            # Actual close is in the past
            actual_close = fake.date_between(
                start_date="-18m", end_date=today
            )
            status = "Closed Won"
        elif stage == "Lost":
            # About half of Lost deals lack an actual close date
            if random.random() < 0.50:
                actual_close = None
            else:
                actual_close = fake.date_between(
                    start_date="-18m", end_date=today
                )
            status = "Closed Lost"
        else:
            actual_close = None
            status = "Open"

        records.append({
            "opportunity_id":     opp_id,
            "account_id":         account_id,
            "sales_rep":          sales_rep,
            "stage":              stage,
            "deal_value":         deal_value,
            "probability":        probability,
            "expected_close_date": expected_close,
            "actual_close_date":  actual_close,
            "status":             status,
        })

    return pd.DataFrame(records)


def inject_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inject intentional data quality problems.

      - ~2%  negative deal_value
      - ~3%  duplicate opportunity rows
      - ~4%  future expected_close_date (far future)
    """
    today = date.today()

    # ── 2% Negative deal value ────────────────
    neg_idx = df.sample(frac=0.02, random_state=21).index
    for idx in neg_idx:
        df.at[idx, "deal_value"] = round(-abs(df.at[idx, "deal_value"]), 2)

    # ── 3% Duplicate rows ─────────────────────
    duplicates = df.sample(frac=0.03, random_state=22)
    df = pd.concat([df, duplicates], ignore_index=True)

    # ── 4% Far-future expected_close_date ─────
    future_idx = df.sample(frac=0.04, random_state=23).index
    for idx in future_idx:
        far_future = today + timedelta(days=random.randint(365, 1460))
        df.at[idx, "expected_close_date"] = far_future

    return df


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Persist DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def print_summary(df: pd.DataFrame, output_path: Path) -> None:
    """Print a structured generation summary."""
    print("=" * 55)
    print("  Opportunities Dataset Generated Successfully")
    print("=" * 55)
    print(f"  Total Records  : {len(df):,}")
    print(f"  File Location  : {output_path}")
    print(f"  Columns        : {list(df.columns)}")
    print("=" * 55)


# ──────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────

def main():
    """Orchestrate opportunity data generation."""
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent
    raw_dir      = project_root / "datasets" / "raw"
    output_path  = raw_dir / "opportunities.csv"

    try:
        print("Loading accounts...")
        accounts_df = load_accounts(raw_dir)

        print(f"Generating {NUM_OPPORTUNITIES:,} opportunities...")
        df = generate_opportunities(accounts_df)

        print("Injecting data quality issues...")
        df = inject_quality_issues(df)

        print("Saving CSV...")
        save_csv(df, output_path)

        print_summary(df, output_path)

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error during opportunity generation: {e}")
        raise


if __name__ == "__main__":
    main()
