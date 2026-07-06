"""
database.py
-----------
SQLAlchemy engine, session factory, and declarative Base for
the RevenuePulse AI platform.

All database configuration is read from the DATABASE_URL environment
variable (loaded from backend/.env via python-dotenv).

Usage:
    from backend.app.database.database import engine, SessionLocal, Base

    # In an ETL script:
    with SessionLocal() as session:
        session.add(obj)
        session.commit()

    # In a FastAPI dependency:
    from backend.app.database.connection import get_db
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ── Load .env from backend/ ────────────────────────────────────────────────
_BACKEND_DIR = Path(__file__).resolve().parents[3]   # backend/
load_dotenv(_BACKEND_DIR / ".env")

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:admin123@localhost:5432/revenue_pulse",
)

# ── Engine ─────────────────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    # Connection pool settings suitable for an ETL workload
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,       # validate connections before use
    pool_recycle=1800,        # recycle connections every 30 min
    echo=False,               # set True for SQL debug output
    future=True,              # SQLAlchemy 2.0 style
)

# ── Session factory ─────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ── Declarative Base ────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """
    Shared declarative base for all SQLAlchemy ORM models.

    All model classes must inherit from this Base so that
    Base.metadata.create_all(engine) creates all tables together.
    """
    pass
