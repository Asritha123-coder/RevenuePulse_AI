"""
analytics_service.py
--------------------
Central Analytics Service orchestrating SQL query execution, result caching,
CSV report generation, and logging. Exposes all metrics endpoints.
"""

import time
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import pandas as pd
from sqlalchemy import text

# Add backend directory to sys.path to enable imports
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.database import engine
from app.utils.file_utils import save_csv, ensure_dir

# Import sub-modules for service-level wrapping
from app.analytics import kpi_engine
from app.analytics import revenue_analytics
from app.analytics import customer_analytics
from app.analytics import sales_analytics
from app.analytics import marketing_analytics
from app.analytics import support_analytics
from app.analytics import usage_analytics
from app.analytics import account_health
from app.analytics import forecast
from app.analytics import business_insights

# ── Set up specific logger for logs/analytics.log ─────────────────────────────
PROJECT_ROOT = BACKEND_DIR.parent
LOGS_DIR = PROJECT_ROOT / "logs"
ensure_dir(LOGS_DIR)

analytics_logger = logging.getLogger("analytics")
analytics_logger.setLevel(logging.INFO)
# Clear old handlers to avoid duplicates
if analytics_logger.hasHandlers():
    analytics_logger.handlers.clear()

file_handler = RotatingFileHandler(
    LOGS_DIR / "analytics.log",
    maxBytes=5*1024*1024,
    backupCount=3,
    encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
analytics_logger.addHandler(file_handler)


class AnalyticsService:
    """Enterprise Analytics Service providing caching, SQL processing, and report creation."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.reports_dir = self.project_root / "reports"
        ensure_dir(self.reports_dir)

    def log_request(self, func_name: str, elapsed: float, status: str = "SUCCESS") -> None:
        """Log the analytics execution details to logs/analytics.log."""
        analytics_logger.info(
            "Service Call: %s | Duration: %.3fs | Status: %s",
            func_name, elapsed, status
        )

    # ── Database execution wrappers ──────────────────────────────────────────
    def execute_to_df(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute SQL query and return results as a Pandas DataFrame.
        """
        t0 = time.time()
        params_tuple = tuple(sorted(params.items())) if params else None
        
        try:
            df = self._execute_cached(query, params_tuple)
            # Log the hit or query time
            self.log_request(f"SQL Query ({hash(query)})", time.time() - t0)
            return df
        except Exception as e:
            self.log_request(f"SQL Query Failed ({hash(query)})", time.time() - t0, f"FAILED: {e}")
            raise

    def execute_scalar(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute SQL query and return a single scalar value.
        """
        df = self.execute_to_df(query, params)
        if df.empty:
            return None
        return df.iloc[0, 0]

    @lru_cache(maxsize=128)
    def _execute_cached(self, query: str, params_tuple: Optional[Tuple[Tuple[str, Any], ...]] = None) -> pd.DataFrame:
        """
        Internal cached execution wrapper. Uses lru_cache for query optimization.
        Params are parsed as hashable sorted tuples.
        """
        params = dict(params_tuple) if params_tuple else {}
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            # If no rows returned
            if not result.returns_rows:
                return pd.DataFrame()
            cols = result.keys()
            rows = result.fetchall()
            return pd.DataFrame(rows, columns=cols)

    def clear_cache(self) -> None:
        """Clear the query results cache. Call this after ETL runs."""
        self._execute_cached.cache_clear()
        analytics_logger.info("Analytics query cache cleared.")

    # ── KPI Engine API ───────────────────────────────────────────────────────
    def get_kpi_summary(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            res = kpi_engine.get_all_kpis(self)
            self.log_request("get_kpi_summary", time.time() - t0)
            return res
        except Exception as e:
            self.log_request("get_kpi_summary", time.time() - t0, f"FAILED: {e}")
            raise

    # ── Revenue Analytics API ────────────────────────────────────────────────
    def get_revenue_summary(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            res = revenue_analytics.get_revenue_summary_stats(self)
            self.log_request("get_revenue_summary", time.time() - t0)
            return res
        except Exception as e:
            self.log_request("get_revenue_summary", time.time() - t0, f"FAILED: {e}")
            raise

    # ── Customer Analytics API ───────────────────────────────────────────────
    def get_customer_summary(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            res = customer_analytics.get_customer_summary_stats(self)
            self.log_request("get_customer_summary", time.time() - t0)
            return res
        except Exception as e:
            self.log_request("get_customer_summary", time.time() - t0, f"FAILED: {e}")
            raise

    # ── Sales Analytics API ──────────────────────────────────────────────────
    def get_sales_summary(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            res = sales_analytics.get_sales_summary_stats(self)
            self.log_request("get_sales_summary", time.time() - t0)
            return res
        except Exception as e:
            self.log_request("get_sales_summary", time.time() - t0, f"FAILED: {e}")
            raise

    # ── Marketing Analytics API ──────────────────────────────────────────────
    def get_marketing_summary(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            res = marketing_analytics.get_marketing_summary_stats(self)
            self.log_request("get_marketing_summary", time.time() - t0)
            return res
        except Exception as e:
            self.log_request("get_marketing_summary", time.time() - t0, f"FAILED: {e}")
            raise

    # ── Support Analytics API ────────────────────────────────────────────────
    def get_support_summary(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            res = support_analytics.get_support_summary_stats(self)
            self.log_request("get_support_summary", time.time() - t0)
            return res
        except Exception as e:
            self.log_request("get_support_summary", time.time() - t0, f"FAILED: {e}")
            raise

    # ── Product Usage Analytics API ──────────────────────────────────────────
    def get_usage_summary(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            res = usage_analytics.get_usage_summary_stats(self)
            self.log_request("get_usage_summary", time.time() - t0)
            return res
        except Exception as e:
            self.log_request("get_usage_summary", time.time() - t0, f"FAILED: {e}")
            raise

    # ── Account Health API ───────────────────────────────────────────────────
    def get_account_health_summary(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            res = account_health.get_health_summary(self)
            self.log_request("get_account_health_summary", time.time() - t0)
            return res
        except Exception as e:
            self.log_request("get_account_health_summary", time.time() - t0, f"FAILED: {e}")
            raise

    # ── Forecast API ─────────────────────────────────────────────────────────
    def get_forecast(self, months: int = 6) -> Dict[str, Any]:
        t0 = time.time()
        try:
            res = forecast.get_forecast_summary(self, months)
            self.log_request("get_forecast", time.time() - t0)
            return res
        except Exception as e:
            self.log_request("get_forecast", time.time() - t0, f"FAILED: {e}")
            raise

    # ── Business Insights API ────────────────────────────────────────────────
    def get_business_insights(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            res = business_insights.generate_business_insights(self)
            self.log_request("get_business_insights", time.time() - t0)
            return res
        except Exception as e:
            self.log_request("get_business_insights", time.time() - t0, f"FAILED: {e}")
            raise

    # ── Automatic Reports Generation ─────────────────────────────────────────
    def generate_all_reports(self) -> None:
        """
        Generate summary CSV files inside reports/ directory.
        """
        analytics_logger.info("Automatic summary reports generation triggered...")
        t0 = time.time()
        
        try:
            # 1. Revenue summary
            rev = self.get_revenue_summary()
            df_rev = pd.DataFrame(rev["mrr_by_month"])
            save_csv(df_rev, self.reports_dir / "revenue_summary.csv")
            
            # 2. Customer summary
            cust = self.get_customer_summary()
            df_cust = pd.DataFrame(cust["company_size_distribution"])
            save_csv(df_cust, self.reports_dir / "customer_summary.csv")
            
            # 3. Marketing summary
            mktg = self.get_marketing_summary()
            df_mktg = pd.DataFrame(mktg["campaign_type_performance"])
            save_csv(df_mktg, self.reports_dir / "marketing_summary.csv")
            
            # 4. Sales summary
            sales = self.get_sales_summary()
            df_sales = pd.DataFrame(sales["funnel"])
            save_csv(df_sales, self.reports_dir / "sales_summary.csv")
            
            # 5. Usage summary
            use = self.get_usage_summary()
            df_use = pd.DataFrame(use["dau_mau_ratio"])
            save_csv(df_use, self.reports_dir / "usage_summary.csv")
            
            # 6. Support summary
            supp = self.get_support_summary()
            df_supp = pd.DataFrame(supp["tickets_by_priority"])
            save_csv(df_supp, self.reports_dir / "support_summary.csv")
            
            # 7. Executive Dashboard summary
            kpis = self.get_kpi_summary()
            df_exec = pd.DataFrame([kpis])
            save_csv(df_exec, self.reports_dir / "executive_dashboard_summary.csv")
            
            analytics_logger.info("All summary CSV reports generated successfully in %ss.", round(time.time() - t0, 2))
        except Exception as e:
            analytics_logger.error("Failed to generate summary CSV files: %s", e, exc_info=True)
            raise
