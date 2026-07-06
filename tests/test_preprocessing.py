"""
test_preprocessing.py
---------------------
Unit tests for the ML data preprocessing module.
"""

import sys
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

# Add backend directory to sys.path to enable imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.preprocessing import DataPreprocessor, create_train_test_split


class TestMLPreprocessing(unittest.TestCase):
    """Preprocessing pipeline validation tests."""

    def test_preprocessor_fitting_and_transformation(self):
        """Ensure scaler, one-hot encoder, and medians imputations fit and transform correctly."""
        df_train = pd.DataFrame([
            {"feature_num": 10.0, "feature_cat": "Alpha"},
            {"feature_num": 20.0, "feature_cat": "Beta"},
            {"feature_num": None, "feature_cat": "Alpha"},  # missing num
            {"feature_num": 30.0, "feature_cat": None}      # missing cat
        ])
        
        num_cols = ["feature_num"]
        cat_cols = ["feature_cat"]
        
        preprocessor = DataPreprocessor(num_cols, cat_cols)
        preprocessor.fit(df_train)
        
        # Check medians
        self.assertEqual(preprocessor.medians["feature_num"], 20.0)
        self.assertEqual(preprocessor.modes["feature_cat"], "Alpha")
        
        # Transform
        df_transformed = preprocessor.transform(df_train)
        self.assertFalse(df_transformed.empty)
        
        # Verify columns exist
        self.assertIn("feature_num", df_transformed.columns)
        self.assertIn("feature_cat_Alpha", df_transformed.columns)
        self.assertIn("feature_cat_Beta", df_transformed.columns)

    def test_single_record_preparation(self):
        """Ensure single record preprocessing formats input to model-ready shape."""
        df_train = pd.DataFrame([
            {"num": 100.0, "cat": "Yes"},
            {"num": 200.0, "cat": "No"}
        ])
        
        preprocessor = DataPreprocessor(["num"], ["cat"]).fit(df_train)
        
        record = {"num": 150.0, "cat": "Yes"}
        df_rec = preprocessor.prepare_single_record(record)
        
        self.assertEqual(len(df_rec), 1)
        self.assertIn("num", df_rec.columns)
        self.assertIn("cat_Yes", df_rec.columns)


if __name__ == "__main__":
    unittest.main()
