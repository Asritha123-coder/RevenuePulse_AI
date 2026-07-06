"""
model_loader.py
--------------
Thread-safe model loading service. Caches loaded model objects in memory
for sub-millisecond API inference, with manual reload support.
"""

import threading
from typing import Dict, Any, Optional
from .model_registry import ModelRegistry
from .utils import get_ml_logger

logger = get_ml_logger("loader")

# In-memory model cache
_MODEL_CACHE: Dict[str, Any] = {}
_cache_lock = threading.Lock()


def get_cached_model(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a model from cache, loading it from disk if not present.
    """
    global _MODEL_CACHE
    
    with _cache_lock:
        if model_name in _MODEL_CACHE:
            return _MODEL_CACHE[model_name]
            
        # Try loading from registry
        logger.info("Cache miss for model: %s. Fetching from registry...", model_name)
        model_pipeline = ModelRegistry.load_active_model(model_name)
        
        if model_pipeline is not None:
            _MODEL_CACHE[model_name] = model_pipeline
            return model_pipeline
            
        return None


def reload_model(model_name: str) -> bool:
    """
    Evict model from cache and force reload from registry.
    Returns True if successfully reloaded.
    """
    global _MODEL_CACHE
    
    logger.info("Triggering reload for model: %s", model_name)
    with _cache_lock:
        if model_name in _MODEL_CACHE:
            del _MODEL_CACHE[model_name]
            
        # Attempt reloading
        model_pipeline = ModelRegistry.load_active_model(model_name)
        if model_pipeline is not None:
            _MODEL_CACHE[model_name] = model_pipeline
            logger.info("Successfully reloaded and cached model: %s", model_name)
            return True
            
        return False
