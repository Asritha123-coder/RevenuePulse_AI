"""
test_extract.py
---------------
Unit tests for the ETL extraction module.
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path to enable imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.etl.extract import extract_all, extract_dataset


class TestExtract(unittest.TestCase):
    """Extraction phase validation tests."""
    
    def setUp(self):
        self.raw_dir = PROJECT_ROOT / "datasets" / "raw"

    def test_extract_dataset_not_found(self):
        """Ensure exception is raised if dataset name is unknown."""
        with self.assertRaises(ValueError):
            extract_dataset("unknown_dataset_name", self.raw_dir)

    def test_extract_invalid_path(self):
        """Ensure exception is raised when raw directory path does not exist."""
        invalid_dir = PROJECT_ROOT / "datasets" / "invalid_path"
        with self.assertRaises((FileNotFoundError, RuntimeError)):
            extract_dataset("accounts", invalid_dir)

    def test_extract_all_success(self):
        """Verify that all expected raw CSVs are loaded into pandas DataFrames."""
        if not self.raw_dir.exists():
            self.skipTest(f"Raw directory does not exist: {self.raw_dir}")
            
        try:
            dfs = extract_all(self.raw_dir)
            self.assertIn("accounts", dfs)
            self.assertIn("contacts", dfs)
            self.assertIn("campaigns", dfs)
            self.assertIn("opportunities", dfs)
            self.assertIn("subscriptions", dfs)
            self.assertIn("product_usage", dfs)
            self.assertIn("website_activity", dfs)
            self.assertIn("support_tickets", dfs)
            
            for key, df in dfs.items():
                self.assertIsNotNone(df)
                self.assertFalse(df.empty, f"Dataset {key} is empty")
        except Exception as e:
            self.fail(f"extract_all raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
