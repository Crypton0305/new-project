"""
evaluate_models.py
-------------------
Computes standard classification metrics for trained models:
Accuracy, Precision, Recall, F1 Score, ROC AUC, Confusion Matrix.
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve,
)


def evaluate_classifier(y_true, y_pred, y_proba) -> dict:
    """
    Returns a dict of standard metrics for a binary classifier.
    y_proba should be the probability of the positive class (diabetes=1).
    """
    metrics = {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_true, y_proba), 4),
    }
    cm = confusion_matrix(y_true, y_pred)
    metrics["confusion_matrix"] = cm.tolist()
    return metrics


def get_roc_curve_data(y_true, y_proba):
    """Returns FPR, TPR arrays for plotting an ROC curve."""
    fpr, tpr, thresholds = roc_curve(y_true, y_proba)
    return fpr, tpr, thresholds


def select_best_model(results: dict) -> str:
    """
    Picks the best model by ROC AUC (most robust single metric for
    imbalanced healthcare classification), tie-broken by F1 score.
    `results` is a dict of {model_name: metrics_dict}.
    """
    best_name = max(
        results.keys(),
        key=lambda name: (results[name]["roc_auc"], results[name]["f1"]),
    )
    return best_name


def metrics_to_dataframe(results: dict):
    """Converts the {model_name: metrics} dict into a tidy comparison DataFrame."""
    import pandas as pd
    rows = []
    for name, m in results.items():
        rows.append({
            "Model": name,
            "Accuracy": m["accuracy"],
            "Precision": m["precision"],
            "Recall": m["recall"],
            "F1 Score": m["f1"],
            "ROC AUC": m["roc_auc"],
        })
    return pd.DataFrame(rows).sort_values("ROC AUC", ascending=False).reset_index(drop=True)
