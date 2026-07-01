"""
prediction.py
--------------
Loads the best-performing trained model + shared transformers and runs
inference for a single patient's input (from the Streamlit prediction form).

Also handles risk-category bucketing and a simple confidence score.
"""

import os
import sys
import joblib
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SAVED_MODELS_DIR, RISK_LOW_MAX, RISK_MODERATE_MAX, RISK_LABELS
from utils.preprocessing import preprocess_single_input


class PredictionEngine:
    """Wraps the best model + transformers for repeated single-patient predictions."""

    def __init__(self):
        self.transformers = None
        self.model = None
        self.model_name = None
        self.model_type = None  # "sklearn" or "keras"
        self._load_artifacts()

    def _load_artifacts(self):
        transformers_path = os.path.join(SAVED_MODELS_DIR, "transformers.joblib")
        best_info_path = os.path.join(SAVED_MODELS_DIR, "best_model_info.joblib")

        if not os.path.exists(transformers_path) or not os.path.exists(best_info_path):
            raise FileNotFoundError(
                "Trained model artifacts not found. Please run model training first "
                "(Admin Panel -> Train Models, or python models/train_models.py)."
            )

        self.transformers = joblib.load(transformers_path)
        best_info = joblib.load(best_info_path)
        self.model_name = best_info["name"]
        model_path = best_info["path"]

        if model_path.endswith(".keras"):
            from tensorflow import keras
            self.model = keras.models.load_model(model_path)
            self.model_type = "keras"
        else:
            self.model = joblib.load(model_path)
            self.model_type = "sklearn"

    def reload(self):
        """Call after retraining models so the engine picks up the new best model."""
        self._load_artifacts()

    def predict(self, patient_input: dict) -> dict:
        """
        patient_input keys (matching FEATURE_COLUMNS):
            age, gender, bmi, hypertension, heart_disease,
            smoking_history, blood_glucose_level, HbA1c_level
        Returns dict with prediction_result, probability, confidence_score, risk_category.
        """
        X = preprocess_single_input(patient_input, self.transformers)

        if self.model_type == "keras":
            probability = float(self.model.predict(X.values, verbose=0).flatten()[0])
        else:
            probability = float(self.model.predict_proba(X)[:, 1][0])

        prediction_result = int(probability >= 0.5)
        confidence_score = round(abs(probability - 0.5) * 2, 4)  # 0 (uncertain) -> 1 (very confident)
        risk_category = self._get_risk_category(probability)

        return {
            "model_used": self.model_name,
            "prediction_result": prediction_result,
            "probability": round(probability, 4),
            "confidence_score": confidence_score,
            "risk_category": risk_category,
        }

    @staticmethod
    def _get_risk_category(probability: float) -> str:
        if probability <= RISK_LOW_MAX:
            return RISK_LABELS["low"]
        elif probability <= RISK_MODERATE_MAX:
            return RISK_LABELS["moderate"]
        else:
            return RISK_LABELS["high"]


# ---------------------------------------------------------------------------
# Module-level singleton accessor (Streamlit-friendly: cache in session_state)
# ---------------------------------------------------------------------------
_engine_instance = None


def get_prediction_engine() -> PredictionEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = PredictionEngine()
    return _engine_instance
