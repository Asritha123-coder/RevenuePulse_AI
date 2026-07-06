"""
test_training.py
----------------
Unit and integration tests for the ML model training module.
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path to enable imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.connection import test_connection
from app.ml.train import run_training_pipeline


class TestMLTraining(unittest.TestCase):
    """Model training pipeline integration tests."""

    def test_run_training_pipeline(self):
        """
        Execute the master training pipeline on database tables.
        Skipped if PostgreSQL is offline.
        """
        if not test_connection():
            self.skipTest("Database is offline. Skipping ML training pipeline integration test.")
            
        try:
            report = run_training_pipeline()
            self.assertIsInstance(report, dict)
            self.assertIn("models_trained", report)
            
            # Check model entry contains version metadata
            trained_models = report["models_trained"]
            self.assertIn("lead_scoring", trained_models)
            self.assertIn("churn_model", trained_models)
            self.assertIn("revenue_forecast", trained_models)
            self.assertIn("account_health", trained_models)
            
            for m_name, meta in trained_models.items():
                self.assertIn("version", meta)
                self.assertIn("metrics", meta)
        except Exception as e:
            self.fail(f"run_training_pipeline raised an unexpected exception: {e}")


if __name__ == "__main__":
    unittest.main()
