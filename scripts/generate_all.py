"""
generate_all.py
----------------
Master orchestration script for the RevenuePulse AI synthetic data pipeline.

Execution order:
  1. Contacts         (requires accounts.csv)
  2. Campaigns        (standalone)
  3. Opportunities    (requires accounts.csv)
  4. Subscriptions    (requires accounts.csv)
  5. Product Usage    (requires accounts.csv)
  6. Website Activity (requires accounts.csv)
  7. Support Tickets  (requires accounts.csv)

Accounts dataset (accounts.csv) must already exist in datasets/raw/.
Run generate_accounts.py first if it does not.

Usage:
    python generate_all.py
"""

import sys
import time
from pathlib import Path

# ──────────────────────────────────────────────
# Ensure the scripts directory is on the path
# so that sibling modules can be imported.
# ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# Import individual generator modules
import generate_contacts
import generate_campaigns
import generate_opportunities
import generate_subscriptions
import generate_product_usage
import generate_website_activity
import generate_support_tickets


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────

def run_step(step_name: str, main_fn) -> float:
    """
    Execute a single generation step, measure elapsed time,
    and surface any errors without halting subsequent steps.

    Args:
        step_name : Human-readable name for the step.
        main_fn   : The main() callable from the generator module.

    Returns:
        Elapsed seconds, or -1 on failure.
    """
    print(f"\n{'-' * 55}")
    print(f"  >> Starting: {step_name}")
    print(f"{'-' * 55}")
    t0 = time.time()
    try:
        main_fn()
        elapsed = round(time.time() - t0, 2)
        print(f"  [OK] Completed in {elapsed}s")
        return elapsed
    except Exception as exc:
        elapsed = round(time.time() - t0, 2)
        print(f"  [FAIL] FAILED after {elapsed}s -- {exc}")
        return -1.0


# ──────────────────────────────────────────────
# Pipeline Definition
# ──────────────────────────────────────────────

PIPELINE = [
    ("Contacts",         generate_contacts.main),
    ("Campaigns",        generate_campaigns.main),
    ("Opportunities",    generate_opportunities.main),
    ("Subscriptions",    generate_subscriptions.main),
    ("Product Usage",    generate_product_usage.main),
    ("Website Activity", generate_website_activity.main),
    ("Support Tickets",  generate_support_tickets.main),
]


# ──────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────

def main():
    """
    Run the full RevenuePulse synthetic data generation pipeline.

    Pre-condition: datasets/raw/accounts.csv must already exist.
    """
    project_root     = SCRIPT_DIR.parent
    accounts_csv     = project_root / "datasets" / "raw" / "accounts.csv"

    print("=" * 55)
    print("  RevenuePulse AI — Data Generation Pipeline")
    print("=" * 55)

    # Guard: accounts.csv must exist
    if not accounts_csv.exists():
        print(
            f"\n[ERROR] accounts.csv not found at:\n  {accounts_csv}\n"
            "Please run generate_accounts.py first.\n"
        )
        sys.exit(1)

    print(f"\n  accounts.csv found at:\n  {accounts_csv}\n")

    pipeline_start = time.time()
    results        = {}

    for step_name, main_fn in PIPELINE:
        elapsed = run_step(step_name, main_fn)
        results[step_name] = elapsed

    total_elapsed = round(time.time() - pipeline_start, 2)

    # ── Final Summary ─────────────────────────
    print(f"\n{'=' * 55}")
    print("  All Datasets Generated Successfully!")
    print(f"{'=' * 55}")
    print(f"  {'Dataset':<22}  {'Status':<10}  {'Time (s)'}")
    print(f"  {'-'*22}  {'-'*10}  {'-'*8}")
    for name, elapsed in results.items():
        status = "[OK]   " if elapsed >= 0 else "[FAIL] "
        time_str = f"{elapsed}s" if elapsed >= 0 else "n/a"
        print(f"  {name:<22}  {status:<10}  {time_str}")
    print(f"{'-' * 55}")
    print(f"  Total Pipeline Time : {total_elapsed}s")
    print(f"  Output Directory    : {project_root / 'datasets' / 'raw'}")
    print(f"{'=' * 55}\n")

    failed = [n for n, e in results.items() if e < 0]
    if failed:
        print(f"[WARNING] {len(failed)} step(s) failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
