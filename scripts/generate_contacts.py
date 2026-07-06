"""
generate_contacts.py
--------------------
Generates a realistic Contacts dataset for the RevenuePulse AI platform.

Each contact belongs to an account (via account_id).
Intentional data quality issues are injected for ETL pipeline testing:
  - 5%  duplicate contacts
  - 8%  missing email
  - 5%  invalid email format
  - 4%  missing phone

Target: datasets/raw/contacts.csv
Rows  : ~15,000
"""

import os
import random
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
fake = Faker()
Faker.seed(42)
random.seed(42)

NUM_CONTACTS = 15_000

DESIGNATIONS = [
    "CEO", "CTO", "CFO", "COO", "CMO",
    "VP of Sales", "VP of Marketing", "VP of Engineering",
    "Sales Manager", "Marketing Manager", "HR Manager",
    "Data Analyst", "Business Analyst", "Software Engineer",
    "Senior Software Engineer", "DevOps Engineer", "Product Manager",
    "Account Executive", "Customer Success Manager", "Operations Manager",
]

LEAD_SOURCES = [
    "Website", "LinkedIn", "Referral", "Cold Email",
    "Trade Show", "Webinar", "Google Ads", "Partner",
    "Inbound Call", "Content Marketing",
]

# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def load_accounts(raw_dir: Path) -> pd.DataFrame:
    """Load the accounts CSV and return a clean DataFrame with unique account_ids."""
    accounts_path = raw_dir / "accounts.csv"
    if not accounts_path.exists():
        raise FileNotFoundError(
            f"accounts.csv not found at {accounts_path}. "
            "Please run generate_accounts.py first."
        )
    df = pd.read_csv(accounts_path)
    # Drop duplicate account_ids to avoid row explosion during merge
    df = df.drop_duplicates(subset=["account_id"])
    return df[["account_id", "company_name"]]


def build_corporate_email(first: str, last: str, company: str) -> str:
    """Generate a realistic corporate email address from name + company."""
    domain = (
        company.lower()
        .replace(",", "")
        .replace(".", "")
        .replace(" ", "")
        .replace("'", "")
        .replace("&", "and")
        [:20]          # keep domain reasonably short
    )
    tlds = ["com", "io", "co", "net", "org"]
    tld = random.choice(tlds)
    patterns = [
        f"{first.lower()}.{last.lower()}@{domain}.{tld}",
        f"{first.lower()[0]}{last.lower()}@{domain}.{tld}",
        f"{first.lower()}_{last.lower()}@{domain}.{tld}",
    ]
    return random.choice(patterns)


def generate_contacts(accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate contact records distributed across all accounts.

    Returns a DataFrame with ~NUM_CONTACTS rows before duplication injection.
    """
    account_ids = accounts_df["account_id"].tolist()
    company_map = accounts_df.set_index("account_id")["company_name"].to_dict()

    records = []

    for i in range(1, NUM_CONTACTS + 1):
        contact_id = f"CON{i:07d}"

        account_id = random.choice(account_ids)
        company_name = company_map[account_id]

        first_name = fake.first_name()
        last_name = fake.last_name()

        email = build_corporate_email(first_name, last_name, company_name)

        # Phone: US-style 10-digit number
        phone = fake.numerify("###-###-####")

        designation = random.choice(DESIGNATIONS)

        # LinkedIn URL
        linkedin_url = (
            f"https://www.linkedin.com/in/"
            f"{first_name.lower()}-{last_name.lower()}-"
            f"{random.randint(100, 9999)}"
        )

        lead_source = random.choice(LEAD_SOURCES)

        # created_date between 5 years ago and today
        created_date = fake.date_between(start_date="-5y", end_date="today")

        records.append({
            "contact_id":    contact_id,
            "account_id":    account_id,
            "first_name":    first_name,
            "last_name":     last_name,
            "email":         email,
            "phone":         phone,
            "designation":   designation,
            "linkedin_url":  linkedin_url,
            "lead_source":   lead_source,
            "created_date":  created_date,
        })

    return pd.DataFrame(records)


def inject_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inject intentional data quality problems into the contacts DataFrame.

    Issues injected:
      - 5%  duplicate rows (exact copies)
      - 8%  missing email (NaN)
      - 5%  invalid email format (malformed strings)
      - 4%  missing phone (NaN)
    """
    # ── 5% Duplicate contacts ──────────────────
    duplicates = df.sample(frac=0.05, random_state=1)
    df = pd.concat([df, duplicates], ignore_index=True)

    # ── 8% Missing email ──────────────────────
    missing_email_idx = df.sample(frac=0.08, random_state=2).index
    df.loc[missing_email_idx, "email"] = None

    # ── 5% Invalid email format ───────────────
    invalid_email_idx = df.sample(frac=0.05, random_state=3).index
    invalid_patterns = [
        "notanemail",
        "missing@",
        "@nodomain.com",
        "double@@domain.com",
        "spaces in@email.com",
        "no-tld@domain",
        "plainstring",
    ]
    for idx in invalid_email_idx:
        if pd.isna(df.at[idx, "email"]):
            continue  # already null; skip to avoid overwriting
        df.at[idx, "email"] = random.choice(invalid_patterns)

    # ── 4% Missing phone ──────────────────────
    missing_phone_idx = df.sample(frac=0.04, random_state=4).index
    df.loc[missing_phone_idx, "phone"] = None

    return df


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Save the DataFrame to CSV at the given path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def print_summary(df: pd.DataFrame, output_path: Path) -> None:
    """Print a structured generation summary."""
    print("=" * 55)
    print("  Contacts Dataset Generated Successfully")
    print("=" * 55)
    print(f"  Total Records  : {len(df):,}")
    print(f"  File Location  : {output_path}")
    print(f"  Columns        : {list(df.columns)}")
    print("=" * 55)


# ──────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────

def main():
    """Orchestrate contact data generation."""
    # Resolve paths relative to this script's location
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    raw_dir = project_root / "datasets" / "raw"
    output_path = raw_dir / "contacts.csv"

    try:
        print("Loading accounts...")
        accounts_df = load_accounts(raw_dir)

        print(f"Generating {NUM_CONTACTS:,} contacts...")
        df = generate_contacts(accounts_df)

        print("Injecting data quality issues...")
        df = inject_quality_issues(df)

        print("Saving CSV...")
        save_csv(df, output_path)

        print_summary(df, output_path)

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error during contact generation: {e}")
        raise


if __name__ == "__main__":
    main()
