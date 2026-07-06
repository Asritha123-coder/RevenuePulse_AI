"""
generate_website_activity.py
-----------------------------
Generates a realistic Website Activity dataset for the RevenuePulse AI platform.

Higher-engagement accounts (Enterprise / Mid Market) show more page views,
sessions, downloads, and webinar attendance.

Intentional data quality issues:
  - ~3%  negative page_views
  - ~2%  future last_visit date

Target: datasets/raw/website_activity.csv
Rows  : 40,000
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
Faker.seed(50)
random.seed(50)

NUM_ACTIVITY_RECORDS = 40_000

# Engagement profile by company size
ENGAGEMENT_PROFILES = {
    "Startup": {
        "page_views":           (5,   200),
        "sessions":             (1,   30),
        "avg_session_time_sec": (30,  300),
        "downloads":            (0,   5),
        "webinar_attendance":   (0,   2),
    },
    "Small Business": {
        "page_views":           (50,  800),
        "sessions":             (10,  100),
        "avg_session_time_sec": (60,  600),
        "downloads":            (1,   15),
        "webinar_attendance":   (0,   5),
    },
    "Mid Market": {
        "page_views":           (200, 3_000),
        "sessions":             (50,  400),
        "avg_session_time_sec": (120, 900),
        "downloads":            (5,   40),
        "webinar_attendance":   (2,   15),
    },
    "Enterprise": {
        "page_views":           (1_000, 20_000),
        "sessions":             (200,   2_000),
        "avg_session_time_sec": (300,   1_800),
        "downloads":            (20,    200),
        "webinar_attendance":   (10,    100),
    },
}

DEFAULT_PROFILE = ENGAGEMENT_PROFILES["Mid Market"]


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


def sample_from_range(lo: int, hi: int) -> int:
    """Return a random integer in [lo, hi]."""
    return random.randint(lo, hi)


def generate_website_activity(accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate 40,000 website activity records linked to accounts.

    Each record represents one activity session snapshot for an account.

    Returns a DataFrame before quality injection.
    """
    today       = date.today()
    account_ids = accounts_df["account_id"].tolist()
    size_map    = accounts_df.set_index("account_id")["company_size"].to_dict()

    records = []

    for i in range(1, NUM_ACTIVITY_RECORDS + 1):
        activity_id = f"ACT{i:08d}"
        account_id  = random.choice(account_ids)
        size        = size_map.get(account_id, "Mid Market")
        profile     = ENGAGEMENT_PROFILES.get(size, DEFAULT_PROFILE)

        page_views           = sample_from_range(*profile["page_views"])
        sessions             = sample_from_range(*profile["sessions"])
        avg_session_time     = round(
            random.uniform(*profile["avg_session_time_sec"]), 1
        )
        downloads            = sample_from_range(*profile["downloads"])
        webinar_attendance   = sample_from_range(*profile["webinar_attendance"])

        # last_visit: within the past 60 days
        days_ago   = random.randint(0, 60)
        last_visit = today - timedelta(days=days_ago)

        records.append({
            "activity_id":          activity_id,
            "account_id":           account_id,
            "page_views":           page_views,
            "sessions":             sessions,
            "average_session_time": avg_session_time,
            "downloads":            downloads,
            "webinar_attendance":   webinar_attendance,
            "last_visit":           last_visit,
        })

    return pd.DataFrame(records)


def inject_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inject intentional data quality problems.

      - ~3%  negative page_views
      - ~2%  future last_visit date (beyond today)
    """
    today = date.today()

    # ── 3% Negative page_views ────────────────
    neg_pv_idx = df.sample(frac=0.03, random_state=51).index
    for idx in neg_pv_idx:
        df.at[idx, "page_views"] = -abs(df.at[idx, "page_views"])

    # ── 2% Future last_visit ──────────────────
    future_idx = df.sample(frac=0.02, random_state=52).index
    for idx in future_idx:
        df.at[idx, "last_visit"] = today + timedelta(
            days=random.randint(1, 180)
        )

    return df


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Persist the DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def print_summary(df: pd.DataFrame, output_path: Path) -> None:
    """Print a structured generation summary."""
    print("=" * 55)
    print("  Website Activity Dataset Generated Successfully")
    print("=" * 55)
    print(f"  Total Records  : {len(df):,}")
    print(f"  File Location  : {output_path}")
    print(f"  Columns        : {list(df.columns)}")
    print("=" * 55)


# ──────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────

def main():
    """Orchestrate website activity data generation."""
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent
    raw_dir      = project_root / "datasets" / "raw"
    output_path  = raw_dir / "website_activity.csv"

    try:
        print("Loading accounts...")
        accounts_df = load_accounts(raw_dir)

        print(f"Generating {NUM_ACTIVITY_RECORDS:,} website activity records...")
        df = generate_website_activity(accounts_df)

        print("Injecting data quality issues...")
        df = inject_quality_issues(df)

        print("Saving CSV...")
        save_csv(df, output_path)

        print_summary(df, output_path)

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error during website activity generation: {e}")
        raise


if __name__ == "__main__":
    main()
