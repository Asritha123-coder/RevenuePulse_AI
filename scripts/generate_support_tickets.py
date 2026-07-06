"""
generate_support_tickets.py
-----------------------------
Generates a realistic Support Tickets dataset for the RevenuePulse AI platform.

Enterprise companies generate more tickets.
Resolved tickets must have a resolved_date; Open tickets must not.

Issue Categories : Billing | Technical | Bug | Feature Request | General Inquiry
Priorities       : Low | Medium | High | Critical

Intentional data quality issues:
  - ~3%  future created_date
  - ~4%  duplicate ticket rows
  - ~5%  missing satisfaction_score

Target: datasets/raw/support_tickets.csv
Rows  : ~20,000
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
Faker.seed(60)
random.seed(60)

NUM_TICKETS = 20_000

PRIORITIES  = ["Low", "Medium", "High", "Critical"]
STATUSES    = ["Open", "In Progress", "Resolved", "Closed"]
CATEGORIES  = [
    "Billing", "Technical", "Bug",
    "Feature Request", "General Inquiry",
]

# Ticket volume weights by company size
TICKET_WEIGHTS_BY_SIZE = {
    "Startup":       10,
    "Small Business": 20,
    "Mid Market":    30,
    "Enterprise":    40,   # Enterprise generates more tickets
}

# Resolution time ranges (days) by priority
RESOLUTION_DAYS = {
    "Critical": (0, 1),
    "High":     (1, 3),
    "Medium":   (3, 7),
    "Low":      (7, 30),
}

# Satisfaction score: 1–5 (only for Resolved/Closed)
SAT_SCORE_RANGE = (1, 5)


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


def build_weighted_account_pool(accounts_df: pd.DataFrame) -> list:
    """
    Build a pool of account_ids weighted by company size so that
    Enterprise accounts submit more tickets proportionally.
    """
    pool = []
    for _, row in accounts_df.iterrows():
        weight = TICKET_WEIGHTS_BY_SIZE.get(row["company_size"], 20)
        pool.extend([row["account_id"]] * weight)
    return pool


def generate_support_tickets(accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate 20,000 support ticket records.

    Business Rules:
      - Resolved/Closed tickets always have a resolved_date.
      - Open/In Progress tickets have resolved_date = NULL.
      - Satisfaction score only set for Resolved/Closed tickets.

    Returns a DataFrame before quality injection.
    """
    today        = date.today()
    account_pool = build_weighted_account_pool(accounts_df)

    records = []

    for i in range(1, NUM_TICKETS + 1):
        ticket_id   = f"TKT{i:07d}"
        account_id  = random.choice(account_pool)
        priority    = random.choices(
            PRIORITIES,
            weights=[30, 40, 20, 10],   # mostly Low/Medium
            k=1
        )[0]
        category    = random.choice(CATEGORIES)
        status      = random.choices(
            STATUSES,
            weights=[25, 20, 35, 20],
            k=1
        )[0]

        # created_date: within the past 2 years
        created_date = fake.date_between(start_date="-2y", end_date="today")

        # resolved_date logic
        if status in ("Resolved", "Closed"):
            res_lo, res_hi = RESOLUTION_DAYS[priority]
            res_days       = random.randint(res_lo, res_hi)
            resolved_date  = created_date + timedelta(days=res_days)
            # Clamp to today if resolution date is in the future
            if resolved_date > today:
                resolved_date = today
            # Satisfaction score for resolved/closed
            satisfaction_score = random.randint(*SAT_SCORE_RANGE)
        else:
            resolved_date      = None
            satisfaction_score = None

        records.append({
            "ticket_id":          ticket_id,
            "account_id":         account_id,
            "priority":           priority,
            "issue_category":     category,
            "status":             status,
            "created_date":       created_date,
            "resolved_date":      resolved_date,
            "satisfaction_score": satisfaction_score,
        })

    return pd.DataFrame(records)


def inject_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inject intentional data quality problems.

      - ~3%  future created_date (data entry error)
      - ~4%  duplicate ticket rows
      - ~5%  missing satisfaction_score (even on Resolved)
    """
    today = date.today()

    # ── 3% Future created_date ────────────────
    future_idx = df.sample(frac=0.03, random_state=61).index
    for idx in future_idx:
        df.at[idx, "created_date"] = today + timedelta(
            days=random.randint(1, 365)
        )

    # ── 4% Duplicate ticket rows ──────────────
    duplicates = df.sample(frac=0.04, random_state=62)
    df = pd.concat([df, duplicates], ignore_index=True)

    # ── 5% Missing satisfaction_score (including Resolved) ──
    missing_sat_idx = df.sample(frac=0.05, random_state=63).index
    df.loc[missing_sat_idx, "satisfaction_score"] = None

    return df


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Persist the DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def print_summary(df: pd.DataFrame, output_path: Path) -> None:
    """Print a structured generation summary."""
    print("=" * 55)
    print("  Support Tickets Dataset Generated Successfully")
    print("=" * 55)
    print(f"  Total Records  : {len(df):,}")
    print(f"  File Location  : {output_path}")
    print(f"  Columns        : {list(df.columns)}")
    print("=" * 55)


# ──────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────

def main():
    """Orchestrate support ticket data generation."""
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent
    raw_dir      = project_root / "datasets" / "raw"
    output_path  = raw_dir / "support_tickets.csv"

    try:
        print("Loading accounts...")
        accounts_df = load_accounts(raw_dir)

        print(f"Generating {NUM_TICKETS:,} support tickets...")
        df = generate_support_tickets(accounts_df)

        print("Injecting data quality issues...")
        df = inject_quality_issues(df)

        print("Saving CSV...")
        save_csv(df, output_path)

        print_summary(df, output_path)

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error during support ticket generation: {e}")
        raise


if __name__ == "__main__":
    main()
