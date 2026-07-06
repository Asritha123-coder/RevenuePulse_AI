"""
generate_product_usage.py
--------------------------
Generates a realistic Product Usage dataset for the RevenuePulse AI platform.

Enterprise companies exhibit higher usage: more active users, more API calls,
more storage, and more logins.

Intentional data quality issues:
  - ~3%  negative api_calls
  - ~2%  future last_login date
  - ~4%  missing storage_used

Target: datasets/raw/product_usage.csv
Rows  : 50,000
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
Faker.seed(40)
random.seed(40)

NUM_USAGE_RECORDS = 50_000

# Usage profile by company size
USAGE_PROFILES = {
    "Startup": {
        "login_count":        (10,   200),
        "active_users":       (1,    20),
        "api_calls":          (100,  5_000),
        "storage_used_gb":    (0.5,  20),
        "feature_score":      (10,   50),
    },
    "Small Business": {
        "login_count":        (100,  1_000),
        "active_users":       (10,   100),
        "api_calls":          (1_000, 50_000),
        "storage_used_gb":    (5,    100),
        "feature_score":      (30,   65),
    },
    "Mid Market": {
        "login_count":        (500,  5_000),
        "active_users":       (50,   500),
        "api_calls":          (10_000, 500_000),
        "storage_used_gb":    (50,   500),
        "feature_score":      (50,   80),
    },
    "Enterprise": {
        "login_count":        (2_000, 20_000),
        "active_users":       (200,  5_000),
        "api_calls":          (100_000, 5_000_000),
        "storage_used_gb":    (200,  5_000),
        "feature_score":      (65,   100),
    },
}

# Fallback profile if size is unknown
DEFAULT_PROFILE = USAGE_PROFILES["Mid Market"]


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


def sample_from_profile(profile: dict, field: str) -> float:
    """Return a random value within the given profile field range."""
    lo, hi = profile[field]
    if isinstance(lo, int) and isinstance(hi, int):
        return random.randint(lo, hi)
    return round(random.uniform(lo, hi), 2)


def generate_product_usage(accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate 50,000 product usage event records.

    Each record represents one usage snapshot for an account over a given period.

    Returns a DataFrame with NUM_USAGE_RECORDS rows (before quality injection).
    """
    today      = date.today()
    account_ids = accounts_df["account_id"].tolist()
    size_map    = accounts_df.set_index("account_id")["company_size"].to_dict()

    records = []

    for i in range(1, NUM_USAGE_RECORDS + 1):
        usage_id   = f"USG{i:08d}"
        account_id = random.choice(account_ids)
        size       = size_map.get(account_id, "Mid Market")
        profile    = USAGE_PROFILES.get(size, DEFAULT_PROFILE)

        login_count           = sample_from_profile(profile, "login_count")
        active_users          = sample_from_profile(profile, "active_users")
        api_calls             = sample_from_profile(profile, "api_calls")
        storage_used          = sample_from_profile(profile, "storage_used_gb")
        feature_usage_score   = round(
            random.uniform(*profile["feature_score"]), 1
        )

        # last_login: within the last 90 days
        days_ago  = random.randint(0, 90)
        last_login = today - timedelta(days=days_ago)

        records.append({
            "usage_id":            usage_id,
            "account_id":          account_id,
            "login_count":         login_count,
            "active_users":        active_users,
            "api_calls":           api_calls,
            "storage_used_gb":     storage_used,
            "feature_usage_score": feature_usage_score,
            "last_login":          last_login,
        })

    return pd.DataFrame(records)


def inject_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inject intentional data quality problems.

      - ~3%  negative api_calls
      - ~2%  future last_login (beyond today)
      - ~4%  missing storage_used_gb (NaN)
    """
    today = date.today()

    # ── 3% Negative api_calls ─────────────────
    neg_api_idx = df.sample(frac=0.03, random_state=41).index
    for idx in neg_api_idx:
        df.at[idx, "api_calls"] = -abs(df.at[idx, "api_calls"])

    # ── 2% Future last_login ──────────────────
    future_idx = df.sample(frac=0.02, random_state=42).index
    for idx in future_idx:
        df.at[idx, "last_login"] = today + timedelta(
            days=random.randint(1, 365)
        )

    # ── 4% Missing storage_used_gb ────────────
    missing_storage_idx = df.sample(frac=0.04, random_state=43).index
    df.loc[missing_storage_idx, "storage_used_gb"] = None

    return df


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Persist the DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def print_summary(df: pd.DataFrame, output_path: Path) -> None:
    """Print a structured generation summary."""
    print("=" * 55)
    print("  Product Usage Dataset Generated Successfully")
    print("=" * 55)
    print(f"  Total Records  : {len(df):,}")
    print(f"  File Location  : {output_path}")
    print(f"  Columns        : {list(df.columns)}")
    print("=" * 55)


# ──────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────

def main():
    """Orchestrate product usage data generation."""
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent
    raw_dir      = project_root / "datasets" / "raw"
    output_path  = raw_dir / "product_usage.csv"

    try:
        print("Loading accounts...")
        accounts_df = load_accounts(raw_dir)

        print(f"Generating {NUM_USAGE_RECORDS:,} product usage records...")
        df = generate_product_usage(accounts_df)

        print("Injecting data quality issues...")
        df = inject_quality_issues(df)

        print("Saving CSV...")
        save_csv(df, output_path)

        print_summary(df, output_path)

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error during product usage generation: {e}")
        raise


if __name__ == "__main__":
    main()
