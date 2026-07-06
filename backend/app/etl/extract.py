"""
extract.py
----------
Extract phase of the RevenuePulse AI ETL pipeline.
Reads raw CSV files from `datasets/raw/` and returns pandas DataFrames.
"""

from pathlib import Path
from typing import Dict
import pandas as pd

from ..utils.logger import get_logger
from ..utils.file_utils import read_csv

logger = get_logger(__name__)

# CSV files expected in datasets/raw/
CSV_FILES = {
    "accounts": "accounts.csv",
    "contacts": "contacts.csv",
    "campaigns": "campaigns.csv",
    "opportunities": "opportunities.csv",
    "subscriptions": "subscriptions.csv",
    "product_usage": "product_usage.csv",
    "website_activity": "website_activity.csv",
    "support_tickets": "support_tickets.csv",
}

def extract_dataset(dataset_name: str, raw_dir: Path) -> pd.DataFrame:
    """
    Extract a single CSV file by name and return a pandas DataFrame.
    
    Args:
        dataset_name: Key of the CSV file in CSV_FILES.
        raw_dir: Path to the raw datasets directory.
        
    Returns:
        pd.DataFrame containing the raw data.
    """
    if dataset_name not in CSV_FILES:
        raise ValueError(f"Unknown dataset name: {dataset_name}")
        
    file_name = CSV_FILES[dataset_name]
    file_path = raw_dir / file_name
    
    try:
        logger.info("Extracting %s from %s", dataset_name, file_path)
        df = read_csv(file_path)
        return df
    except Exception as e:
        logger.error("Failed to extract %s: %s", dataset_name, str(e), exc_info=True)
        raise RuntimeError(f"Extraction failed for {dataset_name}: {e}") from e


def extract_all(raw_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Extract all raw datasets from the raw directory.
    
    Args:
        raw_dir: Path to the raw datasets directory.
        
    Returns:
        Dict mapping dataset keys to pandas DataFrames.
    """
    logger.info("Starting extraction of all datasets from %s", raw_dir)
    extracted_dfs = {}
    
    for key in CSV_FILES:
        try:
            df = extract_dataset(key, raw_dir)
            extracted_dfs[key] = df
        except Exception as e:
            logger.error("Global extraction halted due to failure in %s", key)
            raise e
            
    logger.info("Extraction phase completed successfully. All datasets loaded.")
    return extracted_dfs
