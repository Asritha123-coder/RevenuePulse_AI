"""
sql_queries.py
--------------
Central repository for advanced PostgreSQL queries used by the RevenuePulse AI analytics layer.
Contains over 50 optimized SQL queries utilizing Common Table Expressions (CTEs), Window Functions,
aggregations, having, rollups, rank, lag/lead, and complex joins.
"""

class SQLQueries:
    # =========================================================================
    # 1. KPI ENGINE QUERIES (1-10)
    # =========================================================================
    
    TOTAL_MRR = """
    SELECT COALESCE(SUM(monthly_revenue), 0) AS total_mrr
    FROM subscriptions
    WHERE status = 'Active';
    """
    
    TOTAL_ARR = """
    SELECT COALESCE(SUM(annual_contract_value), 0) AS total_arr
    FROM subscriptions
    WHERE status = 'Active';
    """

    REVENUE_BY_MONTH = """
    SELECT 
        TO_CHAR(renewal_date - INTERVAL '1 month', 'YYYY-MM') AS month,
        SUM(monthly_revenue) AS revenue
    FROM subscriptions
    WHERE status = 'Active'
    GROUP BY month
    ORDER BY month;
    """

    AVG_DEAL_SIZE = """
    SELECT COALESCE(AVG(deal_value), 0) AS avg_deal_size
    FROM opportunities
    WHERE stage = 'Won';
    """

    CUSTOMER_STATUS_COUNTS = """
    SELECT 
        account_status,
        COUNT(account_id) AS count
    FROM accounts
    GROUP BY account_status;
    """

    NEW_CUSTOMERS_COUNT = """
    SELECT COUNT(account_id) AS count
    FROM accounts
    WHERE customer_since >= NOW() - INTERVAL '30 days';
    """

    TOTAL_CAMPAIGNS = """
    SELECT COUNT(campaign_id) AS total_campaigns
    FROM campaigns;
    """

    CAMPAIGN_ROI_KPI = """
    SELECT 
        COALESCE(AVG("ROI"), 0) AS avg_roi
    FROM campaigns
    WHERE "ROI" IS NOT NULL;
    """

    LEAD_CONVERSION_RATE = """
    SELECT 
        CASE 
            WHEN SUM(impressions) = 0 THEN 0.0
            ELSE ROUND((SUM(conversions)::NUMERIC / SUM(impressions)::NUMERIC) * 100, 2)
        END AS lead_conversion_rate
    FROM campaigns;
    """

    SUPPORT_TICKETS_KPI = """
    SELECT 
        status,
        COUNT(ticket_id) AS count
    FROM support_tickets
    GROUP BY status;
    """

    AVG_TICKET_RESOLUTION_TIME = """
    SELECT 
        COALESCE(AVG(resolved_date - created_date), 0) AS avg_resolution_days
    FROM support_tickets
    WHERE resolved_date IS NOT NULL AND status IN ('Resolved', 'Closed');
    """

    AVG_CSAT = """
    SELECT 
        COALESCE(AVG(satisfaction_score), 0) AS avg_csat
    FROM support_tickets
    WHERE satisfaction_score IS NOT NULL;
    """

    # =========================================================================
    # 2. REVENUE ANALYTICS QUERIES (11-20)
    # =========================================================================

    REVENUE_BY_COUNTRY = """
    SELECT 
        COALESCE(a.country, 'Unknown') AS country,
        SUM(s.monthly_revenue) AS monthly_revenue,
        SUM(s.annual_contract_value) AS arr
    FROM subscriptions s
    JOIN accounts a ON s.account_id = a.account_id
    WHERE s.status = 'Active'
    GROUP BY a.country
    ORDER BY arr DESC;
    """

    REVENUE_BY_INDUSTRY = """
    SELECT 
        COALESCE(a.industry, 'Unknown') AS industry,
        SUM(s.monthly_revenue) AS monthly_revenue,
        SUM(s.annual_contract_value) AS arr
    FROM subscriptions s
    JOIN accounts a ON s.account_id = a.account_id
    WHERE s.status = 'Active'
    GROUP BY a.industry
    ORDER BY arr DESC;
    """

    REVENUE_BY_COMPANY_SIZE = """
    SELECT 
        COALESCE(a.company_size, 'Unknown') AS company_size,
        SUM(s.monthly_revenue) AS monthly_revenue,
        SUM(s.annual_contract_value) AS arr
    FROM subscriptions s
    JOIN accounts a ON s.account_id = a.account_id
    WHERE s.status = 'Active'
    GROUP BY a.company_size
    ORDER BY arr DESC;
    """

    TOP_REVENUE_ACCOUNTS = """
    SELECT 
        a.account_id,
        a.company_name,
        s.plan,
        s.annual_contract_value AS arr
    FROM subscriptions s
    JOIN accounts a ON s.account_id = a.account_id
    WHERE s.status = 'Active'
    ORDER BY arr DESC
    LIMIT :limit;
    """

    LOWEST_REVENUE_ACCOUNTS = """
    SELECT 
        a.account_id,
        a.company_name,
        s.plan,
        s.annual_contract_value AS arr
    FROM subscriptions s
    JOIN accounts a ON s.account_id = a.account_id
    WHERE s.status = 'Active'
    ORDER BY arr ASC
    LIMIT :limit;
    """

    REVENUE_GROWTH_HISTORICAL = """
    WITH MonthlyRev AS (
        SELECT 
            TO_CHAR(renewal_date - INTERVAL '1 month', 'YYYY-MM') AS month,
            SUM(monthly_revenue) AS mrr
        FROM subscriptions
        WHERE status = 'Active'
        GROUP BY month
    )
    SELECT 
        month,
        mrr,
        LAG(mrr, 1) OVER (ORDER BY month) AS prev_mrr,
        ROUND(((mrr - LAG(mrr, 1) OVER (ORDER BY month)) / NULLIF(LAG(mrr, 1) OVER (ORDER BY month), 0)) * 100, 2) AS growth_pct
    FROM MonthlyRev
    ORDER BY month;
    """

    REVENUE_WATERFALL = """
    WITH Cohort AS (
        SELECT 
            TO_CHAR(customer_since, 'YYYY-MM') AS cohort_month,
            SUM(annual_revenue) AS cohort_revenue
        FROM accounts
        GROUP BY cohort_month
    )
    SELECT 
        cohort_month,
        cohort_revenue,
        SUM(cohort_revenue) OVER (ORDER BY cohort_month) AS cumulative_revenue
    FROM Cohort
    ORDER BY cohort_month;
    """

    TOP_INDUSTRIES_REVENUE_SHARE = """
    WITH TotalRev AS (
        SELECT SUM(annual_contract_value) AS grand_total FROM subscriptions WHERE status = 'Active'
    )
    SELECT 
        COALESCE(a.industry, 'Unknown') AS industry,
        SUM(s.annual_contract_value) AS arr,
        ROUND((SUM(s.annual_contract_value) / (SELECT grand_total FROM TotalRev)) * 100, 2) AS share_pct
    FROM subscriptions s
    JOIN accounts a ON s.account_id = a.account_id
    WHERE s.status = 'Active'
    GROUP BY a.industry
    ORDER BY arr DESC;
    """

    REVENUE_HEATMAP = """
    SELECT 
        COALESCE(a.country, 'Unknown') AS country,
        COALESCE(a.industry, 'Unknown') AS industry,
        SUM(s.annual_contract_value) AS arr
    FROM subscriptions s
    JOIN accounts a ON s.account_id = a.account_id
    WHERE s.status = 'Active'
    GROUP BY a.country, a.industry
    ORDER BY arr DESC;
    """

    REVENUE_DISTRIBUTION_BUCKETS = """
    SELECT 
        CASE 
            WHEN annual_contract_value < 5000 THEN 'Under $5k'
            WHEN annual_contract_value >= 5000 AND annual_contract_value < 20000 THEN '$5k - $20k'
            WHEN annual_contract_value >= 20000 AND annual_contract_value < 50000 THEN '$20k - $50k'
            ELSE 'Over $50k'
        END AS revenue_bucket,
        COUNT(*) AS account_count,
        SUM(annual_contract_value) AS total_arr
    FROM subscriptions
    WHERE status = 'Active'
    GROUP BY revenue_bucket
    ORDER BY total_arr DESC;
    """

    # =========================================================================
    # 3. CUSTOMER ANALYTICS QUERIES (21-30)
    # =========================================================================

    CUSTOMER_SEGMENTATION = """
    SELECT 
        company_size,
        industry,
        COUNT(account_id) AS customer_count,
        ROUND(AVG(employee_count), 0) AS avg_employee_count,
        ROUND(AVG(annual_revenue), 2) AS avg_annual_revenue
    FROM accounts
    GROUP BY company_size, industry
    ORDER BY customer_count DESC;
    """

    CUSTOMER_RETENTION_RATE = """
    WITH MonthlySub AS (
        SELECT 
            TO_CHAR(renewal_date - INTERVAL '1 month', 'YYYY-MM') AS month,
            account_id,
            status
        FROM subscriptions
    ),
    Churners AS (
        SELECT month, COUNT(DISTINCT account_id) AS churned_count
        FROM MonthlySub
        WHERE status = 'Cancelled'
        GROUP BY month
    ),
    Actives AS (
        SELECT month, COUNT(DISTINCT account_id) AS active_count
        FROM MonthlySub
        WHERE status = 'Active'
        GROUP BY month
    )
    SELECT 
        a.month,
        a.active_count,
        COALESCE(c.churned_count, 0) AS churned_count,
        ROUND((1.0 - (COALESCE(c.churned_count, 0)::NUMERIC / NULLIF(a.active_count + COALESCE(c.churned_count, 0), 0)::NUMERIC)) * 100, 2) AS retention_rate_pct
    FROM Actives a
    LEFT JOIN Churners c ON a.month = c.month
    ORDER BY a.month;
    """

    CUSTOMER_LIFETIME_VALUE = """
    SELECT 
        a.account_id,
        a.company_name,
        a.company_size,
        COALESCE(s.annual_contract_value, 0) AS arr,
        EXTRACT(EPOCH FROM (NOW() - a.customer_since))/86400 AS customer_days,
        ROUND((COALESCE(s.monthly_revenue, 0) * (EXTRACT(EPOCH FROM (NOW() - a.customer_since))/2592000))::NUMERIC, 2) AS calculated_clv
    FROM accounts a
    LEFT JOIN subscriptions s ON a.account_id = s.account_id
    ORDER BY calculated_clv DESC;
    """

    AVG_CUSTOMER_AGE = """
    SELECT 
        company_size,
        ROUND(AVG(EXTRACT(EPOCH FROM (NOW() - customer_since))/86400)) AS avg_age_days
    FROM accounts
    GROUP BY company_size;
    """

    INACTIVE_CUSTOMERS_LIST = """
    SELECT 
        account_id,
        company_name,
        last_activity,
        EXTRACT(EPOCH FROM (NOW() - last_activity))/86400 AS days_since_activity
    FROM accounts
    WHERE account_status = 'Inactive' OR last_activity < NOW() - INTERVAL '90 days'
    ORDER BY last_activity ASC;
    """

    TOP_CUSTOMERS_BY_USAGE = """
    SELECT 
        a.account_id,
        a.company_name,
        SUM(p.login_count) AS total_logins,
        SUM(p.api_calls) AS total_api_calls
    FROM accounts a
    JOIN product_usage p ON a.account_id = p.account_id
    GROUP BY a.account_id, a.company_name
    ORDER BY total_api_calls DESC
    LIMIT :limit;
    """

    CUSTOMER_GEOGRAPHIC_DISTRIBUTION = """
    SELECT 
        country,
        state,
        COUNT(account_id) AS customer_count,
        SUM(annual_revenue) AS total_revenue
    FROM accounts
    GROUP BY ROLLUP(country, state)
    ORDER BY country, customer_count DESC;
    """

    CUSTOMER_ACQUISITION_COHORTS = """
    SELECT 
        TO_CHAR(customer_since, 'YYYY-MM') AS cohort_month,
        COUNT(account_id) AS acquisition_count,
        SUM(annual_revenue) AS initial_revenue
    FROM accounts
    GROUP BY cohort_month
    ORDER BY cohort_month;
    """

    CONTACTS_BY_ACCOUNT_RANK = """
    SELECT 
        a.company_name,
        COUNT(c.contact_id) AS contact_count,
        DENSE_RANK() OVER (ORDER BY COUNT(c.contact_id) DESC) AS rank
    FROM accounts a
    LEFT JOIN contacts c ON a.account_id = c.account_id
    GROUP BY a.account_id, a.company_name
    ORDER BY contact_count DESC;
    """

    CUSTOMER_SIZE_SPLIT = """
    SELECT 
        company_size,
        COUNT(*) AS count,
        ROUND((COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM accounts)::NUMERIC) * 100, 2) AS percentage
    FROM accounts
    GROUP BY company_size;
    """

    # =========================================================================
    # 4. SALES ANALYTICS QUERIES (31-38)
    # =========================================================================

    SALES_FUNNEL_TRANSITION = """
    SELECT 
        stage,
        COUNT(opportunity_id) AS deal_count,
        SUM(deal_value) AS total_value,
        ROUND(AVG(probability) * 100, 2) AS avg_probability
    FROM opportunities
    GROUP BY stage
    ORDER BY 
        CASE stage
            WHEN 'Prospecting' THEN 1
            WHEN 'Qualified' THEN 2
            WHEN 'Proposal' THEN 3
            WHEN 'Negotiation' THEN 4
            WHEN 'Won' THEN 5
            WHEN 'Lost' THEN 6
            ELSE 7
        END;
    """

    OPPORTUNITY_STATUS_KPI = """
    SELECT 
        status,
        COUNT(*) AS count,
        SUM(deal_value) AS total_value
    FROM opportunities
    GROUP BY status;
    """

    PIPELINE_VALUE_BY_REP = """
    SELECT 
        sales_rep,
        COUNT(opportunity_id) AS total_opportunities,
        SUM(CASE WHEN status = 'Open' THEN deal_value ELSE 0 END) AS open_pipeline_value,
        SUM(CASE WHEN status = 'Closed Won' THEN deal_value ELSE 0 END) AS won_value
    FROM opportunities
    GROUP BY sales_rep
    ORDER BY open_pipeline_value DESC;
    """

    AVG_SALES_CYCLE_DURATION = """
    SELECT 
        stage,
        ROUND(AVG(actual_close_date - expected_close_date), 1) AS avg_days_deviation
    FROM opportunities
    WHERE actual_close_date IS NOT NULL
    GROUP BY stage;
    """

    SALES_REP_WIN_RATE = """
    WITH RepStats AS (
        SELECT 
            sales_rep,
            COUNT(CASE WHEN status = 'Closed Won' THEN 1 END) AS won_count,
            COUNT(CASE WHEN status IN ('Closed Won', 'Closed Lost') THEN 1 END) AS closed_count
        FROM opportunities
        GROUP BY sales_rep
    )
    SELECT 
        sales_rep,
        won_count,
        closed_count,
        ROUND((won_count::NUMERIC / NULLIF(closed_count, 0)::NUMERIC) * 100, 2) AS win_rate_pct
    FROM RepStats
    ORDER BY win_rate_pct DESC;
    """

    PIPELINE_VELOCITY = """
    SELECT 
        a.company_size,
        COUNT(o.opportunity_id) AS deal_count,
        SUM(o.deal_value) AS pipeline_value,
        AVG(o.deal_value) AS avg_deal_value
    FROM opportunities o
    JOIN accounts a ON o.account_id = a.account_id
    WHERE o.status = 'Open'
    GROUP BY a.company_size
    ORDER BY pipeline_value DESC;
    """

    WON_VS_LOST_BY_MONTH = """
    SELECT 
        TO_CHAR(actual_close_date, 'YYYY-MM') AS close_month,
        SUM(CASE WHEN status = 'Closed Won' THEN deal_value ELSE 0 END) AS won_value,
        SUM(CASE WHEN status = 'Closed Lost' THEN deal_value ELSE 0 END) AS lost_value
    FROM opportunities
    WHERE actual_close_date IS NOT NULL
    GROUP BY close_month
    ORDER BY close_month;
    """

    TOP_SALES_REPS_LEADERBOARD = """
    SELECT 
        sales_rep,
        COUNT(CASE WHEN status = 'Closed Won' THEN 1 END) AS deals_won,
        SUM(CASE WHEN status = 'Closed Won' THEN deal_value ELSE 0 END) AS revenue_won,
        ROW_NUMBER() OVER (ORDER BY SUM(CASE WHEN status = 'Closed Won' THEN deal_value ELSE 0 END) DESC) AS rank
    FROM opportunities
    GROUP BY sales_rep
    ORDER BY revenue_won DESC;
    """

    # =========================================================================
    # 5. MARKETING ANALYTICS QUERIES (39-44)
    # =========================================================================

    CAMPAIGN_PERFORMANCE_DETAIL = """
    SELECT 
        campaign_id,
        campaign_name,
        campaign_type,
        budget,
        spend,
        impressions,
        clicks,
        leads_generated,
        conversions,
        "ROI",
        ROUND((clicks::NUMERIC / NULLIF(impressions, 0)::NUMERIC) * 100, 2) AS ctr_pct,
        ROUND((spend::NUMERIC / NULLIF(leads_generated, 0)::NUMERIC), 2) AS cost_per_lead,
        ROUND((conversions::NUMERIC / NULLIF(clicks, 0)::NUMERIC) * 100, 2) AS conversion_rate_pct
    FROM campaigns
    ORDER BY "ROI" DESC;
    """

    CAMPAIGN_PERFORMANCE_BY_TYPE = """
    SELECT 
        campaign_type,
        COUNT(campaign_id) AS campaign_count,
        SUM(budget) AS total_budget,
        SUM(spend) AS total_spend,
        SUM(leads_generated) AS total_leads,
        SUM(conversions) AS total_conversions,
        ROUND(AVG("ROI"), 2) AS avg_roi
    FROM campaigns
    GROUP BY campaign_type
    ORDER BY avg_roi DESC;
    """

    LEAD_SOURCE_CONTRIBUTION = """
    SELECT 
        lead_source,
        COUNT(contact_id) AS leads_count,
        ROUND((COUNT(contact_id)::NUMERIC / (SELECT COUNT(*) FROM contacts)::NUMERIC) * 100, 2) AS share_pct
    FROM contacts
    GROUP BY lead_source
    ORDER BY leads_count DESC;
    """

    BEST_WORST_ROI_CAMPAIGN = """
    (SELECT 'BEST' AS category, campaign_name, campaign_type, "ROI" FROM campaigns WHERE "ROI" IS NOT NULL ORDER BY "ROI" DESC LIMIT 1)
    UNION ALL
    (SELECT 'WORST' AS category, campaign_name, campaign_type, "ROI" FROM campaigns WHERE "ROI" IS NOT NULL ORDER BY "ROI" ASC LIMIT 1);
    """

    CAMPAIGN_COST_BENEFIT = """
    SELECT 
        campaign_name,
        spend,
        conversions,
        CASE WHEN conversions = 0 THEN 0.0 ELSE ROUND(spend / conversions, 2) END AS cost_per_conversion
    FROM campaigns
    ORDER BY spend DESC
    LIMIT 20;
    """

    MARKETING_FUNNEL_AGGREGATE = """
    SELECT 
        campaign_type,
        SUM(impressions) AS total_impressions,
        SUM(clicks) AS total_clicks,
        SUM(leads_generated) AS total_leads,
        SUM(conversions) AS total_conversions
    FROM campaigns
    GROUP BY campaign_type;
    """

    # =========================================================================
    # 6. SUPPORT ANALYTICS QUERIES (45-50)
    # =========================================================================

    SUPPORT_TICKETS_BY_PRIORITY = """
    SELECT 
        priority,
        COUNT(ticket_id) AS count,
        SUM(CASE WHEN status IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS open_count,
        SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_count
    FROM support_tickets
    GROUP BY priority
    ORDER BY 
        CASE priority
            WHEN 'Critical' THEN 1
            WHEN 'High' THEN 2
            WHEN 'Medium' THEN 3
            WHEN 'Low' THEN 4
            ELSE 5
        END;
    """

    SUPPORT_TICKETS_BY_CATEGORY = """
    SELECT 
        issue_category,
        COUNT(ticket_id) AS ticket_count,
        ROUND(AVG(satisfaction_score), 2) AS avg_csat
    FROM support_tickets
    GROUP BY issue_category
    ORDER BY ticket_count DESC;
    """

    RESOLUTION_VELOCITY_BY_CATEGORY = """
    SELECT 
        issue_category,
        priority,
        ROUND(AVG(resolved_date - created_date), 1) AS avg_days_to_resolve
    FROM support_tickets
    WHERE resolved_date IS NOT NULL
    GROUP BY issue_category, priority
    ORDER BY issue_category, avg_days_to_resolve;
    """

    CSAT_DISTRIBUTION = """
    SELECT 
        satisfaction_score,
        COUNT(ticket_id) AS ticket_count,
        ROUND((COUNT(ticket_id)::NUMERIC / (SELECT COUNT(*) FROM support_tickets WHERE satisfaction_score IS NOT NULL)::NUMERIC) * 100, 2) AS share_pct
    FROM support_tickets
    WHERE satisfaction_score IS NOT NULL
    GROUP BY satisfaction_score
    ORDER BY satisfaction_score DESC;
    """

    SUPPORT_TICKET_LOAD_BY_MONTH = """
    SELECT 
        TO_CHAR(created_date, 'YYYY-MM') AS month,
        COUNT(ticket_id) AS created_count,
        SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_count
    FROM support_tickets
    GROUP BY month
    ORDER BY month;
    """

    HIGH_VOLUME_SUPPORT_ACCOUNTS = """
    SELECT 
        a.account_id,
        a.company_name,
        a.company_size,
        COUNT(t.ticket_id) AS ticket_count
    FROM accounts a
    JOIN support_tickets t ON a.account_id = t.account_id
    GROUP BY a.account_id, a.company_name, a.company_size
    ORDER BY ticket_count DESC
    LIMIT 20;
    """

    # =========================================================================
    # 7. PRODUCT USAGE ANALYTICS QUERIES (51-55)
    # =========================================================================

    DAU_MAU_RATIO = """
    WITH MonthlyLogins AS (
        SELECT 
            account_id,
            SUM(login_count) AS total_logins,
            COUNT(DISTINCT last_login) AS active_days
        FROM product_usage
        GROUP BY account_id
    )
    SELECT 
        a.company_size,
        ROUND(AVG(m.active_days), 2) AS avg_active_days_monthly,
        ROUND((AVG(m.active_days) / 30.0) * 100, 2) AS engagement_ratio_pct
    FROM MonthlyLogins m
    JOIN accounts a ON m.account_id = a.account_id
    GROUP BY a.company_size;
    """

    API_STORAGE_USAGE_BY_SIZE = """
    SELECT 
        a.company_size,
        SUM(p.api_calls) AS total_api_calls,
        ROUND(AVG(p.api_calls), 0) AS avg_api_calls,
        ROUND(SUM(p.storage_used_gb), 2) AS total_storage_gb,
        ROUND(AVG(p.storage_used_gb), 2) AS avg_storage_gb,
        ROUND(AVG(p.feature_usage_score), 2) AS avg_feature_score
    FROM product_usage p
    JOIN accounts a ON p.account_id = a.account_id
    GROUP BY a.company_size
    ORDER BY total_api_calls DESC;
    """

    PRODUCT_ADOPTION_BY_INDUSTRY = """
    SELECT 
        a.industry,
        COUNT(DISTINCT a.account_id) AS accounts_count,
        ROUND(AVG(p.feature_usage_score), 2) AS avg_feature_score,
        ROUND(AVG(p.login_count), 2) AS avg_login_count
    FROM product_usage p
    JOIN accounts a ON p.account_id = a.account_id
    GROUP BY a.industry
    ORDER BY avg_feature_score DESC;
    """

    USAGE_ANOMALIES_ZERO_LOGIN = """
    SELECT 
        a.account_id,
        a.company_name,
        a.company_size,
        COALESCE(s.plan, 'No Active Plan') AS plan,
        COALESCE(s.monthly_revenue, 0) AS mrr
    FROM accounts a
    LEFT JOIN subscriptions s ON a.account_id = s.account_id AND s.status = 'Active'
    WHERE a.account_id NOT IN (SELECT DISTINCT account_id FROM product_usage WHERE login_count > 0)
    ORDER BY mrr DESC;
    """

    ENGAGEMENT_WATERFALL = """
    SELECT 
        CASE 
            WHEN feature_usage_score >= 80 THEN 'High Adoption (>80)'
            WHEN feature_usage_score >= 50 AND feature_usage_score < 80 THEN 'Medium Adoption (50-80)'
            ELSE 'Low Adoption (<50)'
        END AS adoption_segment,
        COUNT(*) AS account_count,
        ROUND(AVG(api_calls), 0) AS avg_api_calls
    FROM product_usage
    GROUP BY adoption_segment
    ORDER BY account_count DESC;
    """
