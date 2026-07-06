"""
seed_database.py
----------------
Reads processed CSV datasets from `datasets/processed/` and seeds the PostgreSQL database.
Ensure the tables have been created using `create_tables.py` and the ETL pipeline
has run to produce processed CSVs.

Usage:
    python backend/app/database/seed_database.py
"""

import sys
import time
from pathlib import Path

import pandas as pd
from sqlalchemy import text

# Add backend directory to sys.path to enable imports
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.database import engine
from app.database.connection import test_connection
from app.utils.logger import get_logger
from app.utils.file_utils import read_csv
from app.etl.load import LOAD_ORDER, clear_tables_in_transaction, load_dataframe_to_db

logger = get_logger(__name__)

def seed_db() -> None:
    """Read processed CSVs and seed the PostgreSQL database."""
    print("Testing connection to database...")
    if not test_connection():
        print("[ERROR] Database connection failed. Seeding aborted.")
        sys.exit(1)
        
    project_root = BACKEND_DIR.parent
    processed_dir = project_root / "datasets" / "processed"
    
    print(f"Reading processed CSVs from: {processed_dir}")
    if not processed_dir.exists() or not any(processed_dir.iterdir()):
        print(
            f"[ERROR] Processed datasets directory is empty or does not exist: {processed_dir}\n"
            "Please run the ETL pipeline first using: python backend/app/etl/pipeline.py"
        )
        sys.exit(1)
        
    # Check if all files in LOAD_ORDER exist
    missing_files = []
    for key in LOAD_ORDER:
        file_path = processed_dir / f"{key}.csv"
        if not file_path.exists():
            missing_files.append(file_path.name)
            
    if missing_files:
        print(f"[ERROR] Some processed CSV files are missing: {', '.join(missing_files)}")
        print("Please rerun the ETL pipeline to generate all processed files.")
        sys.exit(1)
        
    print("Beginning database seeding transaction...")
    t_start = time.time()
    
    try:
        with engine.begin() as conn:
            # Clear existing data first to avoid duplicate primary key collisions
            clear_tables_in_transaction(conn)
            
            for key in LOAD_ORDER:
                csv_path = processed_dir / f"{key}.csv"
                print(f"Loading processed dataset: {csv_path.name}")
                df = read_csv(csv_path)
                
                rows_inserted = load_dataframe_to_db(df, key, conn)
                print(f"  Successfully loaded {rows_inserted} rows into {key}")
                
        elapsed = round(time.time() - t_start, 2)
        print(f"\n[SUCCESS] Database seeded successfully in {elapsed}s.")
        
    except Exception as e:
        print(f"\n[FATAL ERROR] Seeding failed. Database transaction was rolled back: {e}")
        sys.exit(1)


if __name__ == "__main__":
    seed_db()
