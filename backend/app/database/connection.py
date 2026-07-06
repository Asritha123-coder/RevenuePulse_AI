"""
connection.py
-------------
Database connection helpers for the RevenuePulse AI platform.

Provides:
  - get_db()         : FastAPI / context-manager dependency that yields
                       a SQLAlchemy Session and closes it on exit.
  - test_connection(): Quick health-check that validates the DB is reachable.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import SessionLocal, engine
from ..utils.logger import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────
# Session dependency
# ──────────────────────────────────────────────

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context-manager that yields a database session and guarantees
    the session is closed (and rolled back on error).

    Usage (ETL scripts)::

        from backend.app.database.connection import get_db

        with get_db() as session:
            session.add(record)
            session.commit()

    Usage (FastAPI)::

        from fastapi import Depends
        from backend.app.database.connection import get_db

        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    session: Session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ──────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────

def test_connection() -> bool:
    """
    Validate that the database is reachable by executing a trivial query.

    Returns:
        True  if the connection succeeds.
        False if any error occurs.

    Logs the outcome at INFO / ERROR level.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connection successful: %s", engine.url)
        return True
    except Exception as exc:
        logger.error("Database connection FAILED: %s", exc)
        return False
