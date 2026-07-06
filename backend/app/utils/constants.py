"""
constants.py
-------------
Central store for all configuration constants used across the
RevenuePulse AI ETL pipeline.

Includes:
  - Country name normalization map
  - Industry and company-size reference lists
  - Revenue tier thresholds
  - Validation thresholds
  - Feature-engineering thresholds
"""

# ──────────────────────────────────────────────
# Country Normalization Mapping
# Maps every variant found in raw data → canonical name
# ──────────────────────────────────────────────
COUNTRY_NAME_MAP: dict[str, str] = {
    # United States variants
    "usa":            "United States",
    "u.s.a.":         "United States",
    "us":             "United States",
    "united states":  "United States",
    "america":        "United States",

    # United Kingdom variants
    "uk":             "United Kingdom",
    "u.k.":           "United Kingdom",
    "united kingdom": "United Kingdom",
    "great britain":  "United Kingdom",
    "britain":        "United Kingdom",

    # India variants
    "india":          "India",
    "ind":            "India",

    # Germany variants
    "germany":        "Germany",
    "deutschland":    "Germany",
    "ger":            "Germany",

    # Canada variants
    "canada":         "Canada",
    "can":            "Canada",

    # Singapore variants
    "singapore":      "Singapore",
    "sgp":            "Singapore",
    "sg":             "Singapore",

    # Australia variants
    "australia":      "Australia",
    "aus":            "Australia",

    # UAE variants
    "uae":            "UAE",
    "united arab emirates": "UAE",
    "u.a.e.":         "UAE",
}

# ──────────────────────────────────────────────
# Reference Lists
# ──────────────────────────────────────────────
KNOWN_INDUSTRIES: list[str] = [
    "Healthcare",
    "Finance",
    "Retail",
    "Education",
    "Manufacturing",
    "IT Services",
    "Telecommunications",
    "Energy",
    "Logistics",
    "E-Commerce",
]

KNOWN_COMPANY_SIZES: list[str] = [
    "Startup",
    "Small Business",
    "Mid Market",
    "Enterprise",
]

KNOWN_ACCOUNT_STATUSES: list[str] = ["Active", "Inactive"]

KNOWN_SUBSCRIPTION_PLANS: list[str] = [
    "Starter",
    "Growth",
    "Professional",
    "Enterprise",
]

KNOWN_OPPORTUNITY_STAGES: list[str] = [
    "Prospecting",
    "Qualified",
    "Proposal",
    "Negotiation",
    "Won",
    "Lost",
]

KNOWN_TICKET_PRIORITIES: list[str] = ["Low", "Medium", "High", "Critical"]

KNOWN_TICKET_CATEGORIES: list[str] = [
    "Billing",
    "Technical",
    "Bug",
    "Feature Request",
    "General Inquiry",
]

KNOWN_CAMPAIGN_TYPES: list[str] = [
    "Email",
    "LinkedIn",
    "Google Ads",
    "Events",
    "Referral",
    "Organic",
    "Webinar",
]

# ──────────────────────────────────────────────
# Revenue Tier Thresholds (annual_revenue in INR/USD)
# ──────────────────────────────────────────────
REVENUE_TIERS: dict[str, tuple[float, float]] = {
    "Tier 1 — Micro":       (0,           1_000_000),
    "Tier 2 — Small":       (1_000_000,   50_000_000),
    "Tier 3 — Mid":         (50_000_000,  500_000_000),
    "Tier 4 — Large":       (500_000_000, 5_000_000_000),
    "Tier 5 — Enterprise":  (5_000_000_000, float("inf")),
}

# ──────────────────────────────────────────────
# Validation Thresholds
# ──────────────────────────────────────────────
MAX_FUTURE_DAYS_ALLOWED: int = 0        # dates beyond today are invalid
MIN_DEAL_VALUE: float = 0.0             # deal_value must be >= 0
MIN_REVENUE: float = 0.0               # monthly_revenue must be >= 0
MIN_API_CALLS: int = 0                 # api_calls must be >= 0
MIN_PAGE_VIEWS: int = 0                # page_views must be >= 0
SATISFACTION_SCORE_MIN: int = 1
SATISFACTION_SCORE_MAX: int = 5
PROBABILITY_MIN: float = 0.0
PROBABILITY_MAX: float = 1.0

# ──────────────────────────────────────────────
# Feature Engineering — Health Score Weights
# ──────────────────────────────────────────────
HEALTH_SCORE_WEIGHTS: dict[str, float] = {
    "login_activity":       0.25,
    "feature_adoption":     0.25,
    "support_health":       0.20,
    "engagement":           0.15,
    "subscription_value":   0.15,
}

# Maximum normalisation reference values
HEALTH_SCORE_MAX_LOGINS: int   = 20_000
HEALTH_SCORE_MAX_FEATURE: float = 100.0
HEALTH_SCORE_MAX_SESSIONS: int = 2_000

# ──────────────────────────────────────────────
# ETL Pipeline Settings
# ──────────────────────────────────────────────
CHUNK_SIZE: int = 5_000          # rows per DB insert chunk
DATE_FORMAT_STANDARD: str = "%Y-%m-%d"

# ──────────────────────────────────────────────
# File / Path Names
# ──────────────────────────────────────────────
RAW_DIR_NAME:       str = "raw"
PROCESSED_DIR_NAME: str = "processed"
REPORTS_DIR_NAME:   str = "reports"
LOGS_DIR_NAME:      str = "logs"
