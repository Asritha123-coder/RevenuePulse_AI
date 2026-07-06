"""
model_registry.py
-----------------
Model registry for the ML layer. Automatically handles model serialization (saving),
deserialization (loading), version control, and metadata tracking.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import joblib

from .utils import get_ml_logger

logger = get_ml_logger("registry")

# Resolving paths
BACKEND_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = BACKEND_DIR / "models"
REGISTRY_JSON = MODELS_DIR / "model_registry.json"


class ModelRegistry:
    """Manages serialization, loading, and version metrics of models."""

    @staticmethod
    def _ensure_models_dir() -> None:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        if not REGISTRY_JSON.exists():
            with open(REGISTRY_JSON, "w") as f:
                json.dump({"models": {}}, f, indent=4)

    @classmethod
    def register_model(
        cls, 
        model_name: str, 
        model_pipeline: Any, 
        metrics: Dict[str, float], 
        params: Dict[str, Any],
        features: list
    ) -> str:
        """
        Save a model pipeline and update registry metadata.
        
        Args:
            model_name: Base identifier (e.g., 'lead_scoring')
            model_pipeline: Dictionary {"preprocessor": p, "model": m}
            metrics: Map of performance metrics (Accuracy, F1, RMSE etc.)
            params: Dict of model hyper-parameters
            features: List of feature columns used
            
        Returns:
            Registered version string.
        """
        cls._ensure_models_dir()
        
        # Read current registry
        with open(REGISTRY_JSON, "r") as f:
            registry = json.load(f)
            
        # Get next version number
        model_entry = registry["models"].get(model_name, {"versions": [], "active_version": None})
        versions = model_entry["versions"]
        next_ver = len(versions) + 1
        version_str = f"v{next_ver}"
        
        # Paths
        model_filename = f"{model_name}_{version_str}.pkl"
        model_path = MODELS_DIR / model_filename
        
        # Save model pipeline using joblib
        logger.info("Registering model %s version %s to %s", model_name, version_str, model_path)
        joblib.dump(model_pipeline, model_path)
        
        # Update metadata entry
        meta = {
            "version": version_str,
            "filename": model_filename,
            "registered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": metrics,
            "params": params,
            "features": features
        }
        
        versions.append(meta)
        model_entry["active_version"] = version_str
        registry["models"][model_name] = model_entry
        
        # Save registry json
        with open(REGISTRY_JSON, "w") as f:
            json.dump(registry, f, indent=4)
            
        logger.info("Model %s %s registered successfully.", model_name, version_str)
        return version_str

    @classmethod
    def load_active_model(cls, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Load the current active version of a model from the registry.
        
        Returns:
            Dictionary {"preprocessor": p, "model": m} or None.
        """
        cls._ensure_models_dir()
        
        with open(REGISTRY_JSON, "r") as f:
            registry = json.load(f)
            
        model_entry = registry["models"].get(model_name)
        if not model_entry or not model_entry.get("active_version"):
            logger.warning("No active version found in registry for model: %s", model_name)
            return None
            
        active_ver = model_entry["active_version"]
        version_meta = next((v for v in model_entry["versions"] if v["version"] == active_ver), None)
        
        if not version_meta:
            logger.error("Active version %s metadata is missing in registry for %s", active_ver, model_name)
            return None
            
        model_path = MODELS_DIR / version_meta["filename"]
        if not model_path.exists():
            logger.error("Model file %s not found on disk.", model_path)
            return None
            
        logger.info("Loading active model %s version %s from %s", model_name, active_ver, model_path)
        return joblib.load(model_path)

    @classmethod
    def get_model_metadata(cls, model_name: str) -> Optional[Dict[str, Any]]:
        """Fetch registry metadata for a model."""
        cls._ensure_models_dir()
        with open(REGISTRY_JSON, "r") as f:
            registry = json.load(f)
        return registry["models"].get(model_name)

    @classmethod
    def list_all_models(cls) -> Dict[str, Any]:
        """Fetch all models currently registered."""
        cls._ensure_models_dir()
        with open(REGISTRY_JSON, "r") as f:
            return json.load(f)
