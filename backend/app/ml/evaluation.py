"""
evaluation.py
-------------
Computes classification and regression metrics. Generates confusion matrices
and ROC curve plots if plotting packages are available.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)

from .utils import get_ml_logger

logger = get_ml_logger("evaluation")


def calculate_classification_metrics(y_true: pd.Series, y_pred: np.ndarray, y_prob: Optional[np.ndarray] = None) -> Dict[str, float]:
    """Compute classification metrics."""
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }
    
    if y_prob is not None:
        try:
            # For multi-class or binary
            if len(np.unique(y_true)) == 2:
                # Binary: take probability of positive class
                if len(y_prob.shape) > 1 and y_prob.shape[1] > 1:
                    y_prob_c = y_prob[:, 1]
                else:
                    y_prob_c = y_prob
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob_c))
            else:
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob, multi_class="ovr", average="weighted"))
        except Exception as e:
            logger.warning("Could not calculate ROC AUC score: %s", e)
            metrics["roc_auc"] = 0.0
            
    return metrics


def calculate_regression_metrics(y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute regression metrics (MAE, RMSE, MAPE, R2)."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    # Calculate Mean Absolute Percentage Error (MAPE)
    y_true_np = np.array(y_true)
    non_zero = y_true_np != 0
    if np.any(non_zero):
        mape = np.mean(np.abs((y_true_np[non_zero] - y_pred[non_zero]) / y_true_np[non_zero])) * 100.0
    else:
        mape = 0.0
        
    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "mape": float(mape),
        "r2": float(r2)
    }


def save_evaluation_plots(y_true: pd.Series, y_pred: np.ndarray, reports_dir: Path) -> None:
    """
    Save confusion matrix plot to reports_dir.
    Safely handles missing plotting packages.
    """
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt
        
        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        classes = np.unique(y_true)
        
        plt.figure(figsize=(6, 5))
        plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
        plt.title("Confusion Matrix")
        plt.colorbar()
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes, rotation=45)
        plt.yticks(tick_marks, classes)
        
        # Add labels
        thresh = cm.max() / 2.0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(
                    j, i, format(cm[i, j], "d"),
                    horizontalalignment="center",
                    color="white" if cm[i, j] > thresh else "black"
                )
                
        plt.tight_layout()
        plt.ylabel("True label")
        plt.xlabel("Predicted label")
        
        cm_path = reports_dir / "confusion_matrix.png"
        plt.savefig(cm_path, dpi=150)
        plt.close()
        logger.info("Saved confusion matrix image to %s", cm_path)
        
    except ImportError:
        logger.warning("matplotlib/seaborn not found. Skipping image plot outputs.")
    except Exception as e:
        logger.error("Failed to generate plots: %s", e)
