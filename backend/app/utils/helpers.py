"""
helpers.py
----------
Reusable pure-function helpers for the RevenuePulse AI ETL pipeline.

Functions:
  - parse_dates()            : Coerce mixed date strings to datetime
  - normalize_country()      : Canonical country name from raw variant
  - clean_email()            : Validate / nullify bad email addresses
  - clean_phone()            : Strip non-digit chars, validate length
  - calculate_health_score() : Composite 0-100 score from usage metrics
"""

import re
from datetime import date
from typing import Optional

import pandas as pd

from .constants import (
    COUNTRY_NAME_MAP,
    HEALTH_SCORE_WEIGHTS,
    HEALTH_SCORE_MAX_LOGINS,
    HEALTH_SCORE_MAX_FEATURE,
    HEALTH_SCORE_MAX_SESSIONS,
)

# ──────────────────────────────────────────────
# Email validation regex (RFC-compliant enough for B2B data)
# ──────────────────────────────────────────────
_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

# ──────────────────────────────────────────────
# Phone: strip to digits, valid if 10–15 digits (E.164 without +)
# ──────────────────────────────────────────────
_PHONE_DIGIT_RE = re.compile(r"\D")       # non-digit chars


# ──────────────────────────────────────────────
# Date parsing
# ──────────────────────────────────────────────

def parse_dates(series: pd.Series) -> pd.Series:
    """
    Coerce a mixed-format date Series to datetime64[ns].

    Handles formats like:
      '2024-01-15', '15/01/2024', '01-15-2024', 'Jan 15 2024'

    Values that cannot be parsed are set to NaT.

    Args:
        series: Raw pandas Series of date strings / dates.

    Returns:
        pd.Series of dtype datetime64[ns].
    """
    return pd.to_datetime(series, errors="coerce", dayfirst=False)


# ──────────────────────────────────────────────
# Country normalisation
# ──────────────────────────────────────────────

def normalize_country(raw: Optional[str]) -> Optional[str]:
    """
    Map a raw country string to its canonical form using COUNTRY_NAME_MAP.

    Lookup is case-insensitive and strips surrounding whitespace.
    Unknown values are returned as-is (so they can be flagged later).

    Args:
        raw: Raw country string (e.g. "USA", "U.S.A.", "usa").

    Returns:
        Canonical country name, or the original value if not found.
    """
    if pd.isna(raw) or not isinstance(raw, str):
        return raw
    key = raw.strip().lower()
    return COUNTRY_NAME_MAP.get(key, raw.strip())


def normalize_country_series(series: pd.Series) -> pd.Series:
    """Apply normalize_country element-wise to a Series."""
    return series.apply(normalize_country)


# ──────────────────────────────────────────────
# Email cleaning
# ──────────────────────────────────────────────

def clean_email(raw: Optional[str]) -> Optional[str]:
    """
    Return the email as-is if it passes basic RFC validation,
    otherwise return None.

    Args:
        raw: Raw email string.

    Returns:
        Cleaned email string or None.
    """
    if pd.isna(raw) or not isinstance(raw, str):
        return None
    stripped = raw.strip().lower()
    if _EMAIL_RE.match(stripped):
        return stripped
    return None


def clean_email_series(series: pd.Series) -> pd.Series:
    """Apply clean_email element-wise to a Series."""
    return series.apply(clean_email)


# ──────────────────────────────────────────────
# Phone cleaning
# ──────────────────────────────────────────────

def clean_phone(raw: Optional[str]) -> Optional[str]:
    """
    Strip all non-digit characters and return the number if it has
    10–15 digits (international E.164 range without the '+').
    Otherwise return None.

    Args:
        raw: Raw phone string (e.g. "###-###-####", "+1 (800) 555-1234").

    Returns:
        Digit-only string (10–15 chars) or None.
    """
    if pd.isna(raw) or not isinstance(raw, str):
        return None
    digits = _PHONE_DIGIT_RE.sub("", raw.strip())
    if 10 <= len(digits) <= 15:
        return digits
    return None


def clean_phone_series(series: pd.Series) -> pd.Series:
    """Apply clean_phone element-wise to a Series."""
    return series.apply(clean_phone)


# ──────────────────────────────────────────────
# Health Score
# ──────────────────────────────────────────────

def calculate_health_score(
    login_count: float,
    feature_usage_score: float,
    sessions: float,
    open_tickets: int,
    monthly_revenue: float,
    max_revenue: float,
) -> float:
    """
    Compute a composite Account Health Score on a 0–100 scale.

    The score combines five dimensions:
      1. Login Activity      (25%) — normalized by max expected logins
      2. Feature Adoption    (25%) — feature_usage_score / 100
      3. Support Health      (20%) — penalised for open tickets
      4. Web Engagement      (15%) — sessions normalized
      5. Subscription Value  (15%) — monthly_revenue / max_revenue

    Args:
        login_count:         Monthly login count.
        feature_usage_score: 0–100 feature adoption score.
        sessions:            Monthly website sessions.
        open_tickets:        Count of currently open support tickets.
        monthly_revenue:     Account's monthly subscription revenue.
        max_revenue:         Maximum revenue in the cohort (for normalisation).

    Returns:
        Float health score in [0, 100].
    """
    # ── 1. Login activity (0–1) ───────────────
    login_score = min(login_count / max(HEALTH_SCORE_MAX_LOGINS, 1), 1.0)

    # ── 2. Feature adoption (0–1) ─────────────
    feature_score = min(
        feature_usage_score / max(HEALTH_SCORE_MAX_FEATURE, 1), 1.0
    )

    # ── 3. Support health (0–1) ──────────────
    # 0 open tickets → 1.0; each open ticket subtracts 0.1 (floor 0)
    support_score = max(0.0, 1.0 - open_tickets * 0.10)

    # ── 4. Web engagement (0–1) ───────────────
    engagement_score = min(
        sessions / max(HEALTH_SCORE_MAX_SESSIONS, 1), 1.0
    )

    # ── 5. Subscription value (0–1) ───────────
    revenue_score = (
        min(monthly_revenue / max(max_revenue, 1), 1.0)
        if max_revenue > 0
        else 0.0
    )

    # Weighted composite
    raw_score = (
        login_score     * HEALTH_SCORE_WEIGHTS["login_activity"]
        + feature_score * HEALTH_SCORE_WEIGHTS["feature_adoption"]
        + support_score * HEALTH_SCORE_WEIGHTS["support_health"]
        + engagement_score * HEALTH_SCORE_WEIGHTS["engagement"]
        + revenue_score * HEALTH_SCORE_WEIGHTS["subscription_value"]
    )

    return round(raw_score * 100, 2)
