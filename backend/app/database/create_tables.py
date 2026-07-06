"""
create_tables.py
----------------
Automatically creates all tables in the PostgreSQL database based on SQLAlchemy models.

Usage:
    python backend/app/database/create_tables.py
"""

import sys
from pathlib import Path

# Add backend directory to sys.path to enable imports
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.database import Base, engine
from app.database.connection import test_connection

# Import all models to ensure they are registered on Base.metadata
from app.models import (
    Account,
    Contact,
    Campaign,
    Opportunity,
    Subscription,
    ProductUsage,
    WebsiteActivity,
    SupportTicket,
)

def create_all_tables() -> None:
    """Create all tables in the PostgreSQL database."""
    print("Testing connection to database...")
    if not test_connection():
        print("[ERROR] Database connection failed. Tables could not be created.")
        sys.exit(1)

    print("Creating all tables defined in SQLAlchemy models...")
    try:
        Base.metadata.create_all(bind=engine)
        print("All tables and indexes created successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_all_tables()
