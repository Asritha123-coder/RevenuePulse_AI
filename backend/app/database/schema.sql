-- =============================================================
-- schema.sql
-- RevenuePulse AI — Complete PostgreSQL Schema
-- =============================================================
-- Tables:
--   accounts, contacts, campaigns, opportunities,
--   subscriptions, product_usage, website_activity, support_tickets
--
-- Conventions:
--   - All PKs are TEXT (matching generated IDs like ACC000001)
--   - Dates stored as DATE
--   - Monetary values as NUMERIC(18,2)
--   - Percentages/scores as NUMERIC(5,2)
--   - Lookup columns use CHECK constraints
--   - Indexes on every FK column + high-cardinality filter columns
-- =============================================================

-- ── Extensions ────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- used by UUID defaults

-- =============================================================
-- 1. ACCOUNTS  (root / parent table — no FK dependencies)
-- =============================================================
CREATE TABLE IF NOT EXISTS accounts (
    account_id          TEXT            PRIMARY KEY,
    company_name        TEXT            NOT NULL,
    industry            TEXT,
    company_size        TEXT            CHECK (company_size IN (
                                            'Startup', 'Small Business',
                                            'Mid Market', 'Enterprise')),
    employee_count      INTEGER         CHECK (employee_count >= 0),
    annual_revenue      NUMERIC(18,2),
    country             TEXT,
    state               TEXT,
    city                TEXT,
    account_status      TEXT            DEFAULT 'Active'
                                        CHECK (account_status IN ('Active', 'Inactive')),
    account_owner       TEXT,
    customer_since      DATE,
    last_activity       DATE,
    -- Feature-engineered columns (populated by ETL)
    revenue_tier        TEXT,
    company_category    TEXT,
    customer_age_days   INTEGER,
    -- Audit
    created_at          TIMESTAMPTZ     DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_accounts_industry       ON accounts (industry);
CREATE INDEX IF NOT EXISTS idx_accounts_company_size   ON accounts (company_size);
CREATE INDEX IF NOT EXISTS idx_accounts_account_status ON accounts (account_status);
CREATE INDEX IF NOT EXISTS idx_accounts_country        ON accounts (country);
CREATE INDEX IF NOT EXISTS idx_accounts_account_owner  ON accounts (account_owner);


-- =============================================================
-- 2. CONTACTS
-- =============================================================
CREATE TABLE IF NOT EXISTS contacts (
    contact_id      TEXT        PRIMARY KEY,
    account_id      TEXT        NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    first_name      TEXT        NOT NULL,
    last_name       TEXT        NOT NULL,
    email           TEXT,
    phone           TEXT,
    designation     TEXT,
    linkedin_url    TEXT,
    lead_source     TEXT,
    created_date    DATE,
    -- Audit
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contacts_account_id  ON contacts (account_id);
CREATE INDEX IF NOT EXISTS idx_contacts_email       ON contacts (email);
CREATE INDEX IF NOT EXISTS idx_contacts_lead_source ON contacts (lead_source);


-- =============================================================
-- 3. CAMPAIGNS  (no FK to accounts — standalone marketing table)
-- =============================================================
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id         TEXT            PRIMARY KEY,
    campaign_name       TEXT            NOT NULL,
    campaign_type       TEXT            CHECK (campaign_type IN (
                                            'Email','LinkedIn','Google Ads',
                                            'Events','Referral','Organic','Webinar')),
    budget              NUMERIC(18,2),
    spend               NUMERIC(18,2),
    impressions         BIGINT          CHECK (impressions >= 0),
    clicks              BIGINT          CHECK (clicks >= 0),
    leads_generated     INTEGER         CHECK (leads_generated >= 0),
    conversions         INTEGER         CHECK (conversions >= 0),
    "ROI"               NUMERIC(10,2),
    start_date          DATE,
    end_date            DATE,
    -- Audit
    created_at          TIMESTAMPTZ     DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     DEFAULT NOW(),
    CONSTRAINT chk_campaign_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE INDEX IF NOT EXISTS idx_campaigns_campaign_type ON campaigns (campaign_type);
CREATE INDEX IF NOT EXISTS idx_campaigns_start_date    ON campaigns (start_date);


-- =============================================================
-- 4. OPPORTUNITIES
-- =============================================================
CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id          TEXT            PRIMARY KEY,
    account_id              TEXT            NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    sales_rep               TEXT,
    stage                   TEXT            CHECK (stage IN (
                                                'Prospecting','Qualified','Proposal',
                                                'Negotiation','Won','Lost')),
    deal_value              NUMERIC(18,2)   CHECK (deal_value >= 0),
    probability             NUMERIC(5,4)    CHECK (probability >= 0 AND probability <= 1),
    expected_close_date     DATE,
    actual_close_date       DATE,
    status                  TEXT            CHECK (status IN (
                                                'Open','Closed Won','Closed Lost')),
    -- Audit
    created_at              TIMESTAMPTZ     DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_opportunities_account_id ON opportunities (account_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_stage      ON opportunities (stage);
CREATE INDEX IF NOT EXISTS idx_opportunities_status     ON opportunities (status);
CREATE INDEX IF NOT EXISTS idx_opportunities_sales_rep  ON opportunities (sales_rep);
CREATE INDEX IF NOT EXISTS idx_opportunities_close_date ON opportunities (expected_close_date);


-- =============================================================
-- 5. SUBSCRIPTIONS
-- =============================================================
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id         TEXT            PRIMARY KEY,
    account_id              TEXT            NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    plan                    TEXT            CHECK (plan IN (
                                                'Starter','Growth','Professional','Enterprise')),
    monthly_revenue         NUMERIC(18,2)   CHECK (monthly_revenue >= 0),
    annual_contract_value   NUMERIC(18,2)   CHECK (annual_contract_value >= 0),
    renewal_date            DATE,
    status                  TEXT            CHECK (status IN (
                                                'Active','Cancelled','Paused','Trial')),
    -- Audit
    created_at              TIMESTAMPTZ     DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_account_id    ON subscriptions (account_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan          ON subscriptions (plan);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status        ON subscriptions (status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_renewal_date  ON subscriptions (renewal_date);


-- =============================================================
-- 6. PRODUCT_USAGE
-- =============================================================
CREATE TABLE IF NOT EXISTS product_usage (
    usage_id                TEXT            PRIMARY KEY,
    account_id              TEXT            NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    login_count             INTEGER         CHECK (login_count >= 0),
    active_users            INTEGER         CHECK (active_users >= 0),
    api_calls               BIGINT          CHECK (api_calls >= 0),
    storage_used_gb         NUMERIC(12,2)   CHECK (storage_used_gb >= 0),
    feature_usage_score     NUMERIC(5,2)    CHECK (feature_usage_score >= 0 AND feature_usage_score <= 100),
    last_login              DATE,
    -- Feature-engineered
    account_health_score    NUMERIC(5,2),
    -- Audit
    created_at              TIMESTAMPTZ     DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_product_usage_account_id  ON product_usage (account_id);
CREATE INDEX IF NOT EXISTS idx_product_usage_last_login  ON product_usage (last_login);


-- =============================================================
-- 7. WEBSITE_ACTIVITY
-- =============================================================
CREATE TABLE IF NOT EXISTS website_activity (
    activity_id             TEXT            PRIMARY KEY,
    account_id              TEXT            NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    page_views              INTEGER         CHECK (page_views >= 0),
    sessions                INTEGER         CHECK (sessions >= 0),
    average_session_time    NUMERIC(10,2)   CHECK (average_session_time >= 0),
    downloads               INTEGER         CHECK (downloads >= 0),
    webinar_attendance      INTEGER         CHECK (webinar_attendance >= 0),
    last_visit              DATE,
    -- Audit
    created_at              TIMESTAMPTZ     DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_website_activity_account_id ON website_activity (account_id);
CREATE INDEX IF NOT EXISTS idx_website_activity_last_visit  ON website_activity (last_visit);


-- =============================================================
-- 8. SUPPORT_TICKETS
-- =============================================================
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id               TEXT            PRIMARY KEY,
    account_id              TEXT            NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    priority                TEXT            CHECK (priority IN ('Low','Medium','High','Critical')),
    issue_category          TEXT            CHECK (issue_category IN (
                                                'Billing','Technical','Bug',
                                                'Feature Request','General Inquiry')),
    status                  TEXT            CHECK (status IN (
                                                'Open','In Progress','Resolved','Closed')),
    created_date            DATE,
    resolved_date           DATE,
    satisfaction_score      SMALLINT        CHECK (satisfaction_score >= 1 AND satisfaction_score <= 5),
    -- Audit
    created_at              TIMESTAMPTZ     DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     DEFAULT NOW(),
    CONSTRAINT chk_ticket_resolution
        CHECK (
            (status IN ('Open','In Progress') AND resolved_date IS NULL)
            OR (status IN ('Resolved','Closed'))
        )
);

CREATE INDEX IF NOT EXISTS idx_support_tickets_account_id     ON support_tickets (account_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_priority       ON support_tickets (priority);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status         ON support_tickets (status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_created_date   ON support_tickets (created_date);

-- =============================================================
-- End of schema
-- =============================================================
