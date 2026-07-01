"""
train_models.py
-----------------
Trains and compares four classifiers on the diabetes dataset:
    1. Logistic Regression
    2. Decision Tree Classifier
    3. Support Vector Machine (SVM)
    4. Neural Network (Keras/TensorFlow)

Saves each trained model (and the shared preprocessing transformers) via
Joblib, records metadata in the Firestore Models collection, and automatically
flags the best-performing model based on ROC AUC.

Can be run standalone (`python train_models.py`) or imported and called
from the Streamlit "Model Training" page (with a progress callback).
"""

import os
import sys
import time
import joblib
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SAVED_MODELS_DIR, MODEL_NAMES
from utils.preprocessing import load_raw_dataset, full_preprocessing_pipeline
from models.evaluate_models import evaluate_classifier, select_best_model
from database.db_manager import initialize_database, save_model_metadata

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

# TensorFlow/Keras for the Neural Network model
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")  # suppress verbose TF logs
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


# ---------------------------------------------------------------------------
# INDIVIDUAL MODEL BUILDERS
# ---------------------------------------------------------------------------
def build_logistic_regression():
    return LogisticRegression(max_iter=1000, random_state=42)


def build_decision_tree():
    return DecisionTreeClassifier(max_depth=8, random_state=42)


def build_svm():
    return SVC(kernel="rbf", probability=True, random_state=42)


def build_neural_network(input_dim: int):
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(32, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(16, activation="relu"),
        layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


# ---------------------------------------------------------------------------
# MAIN TRAINING PIPELINE
# ---------------------------------------------------------------------------
def train_all_models(progress_callback=None, log_callback=None):
    """
    Trains all four models, evaluates them, saves artifacts to disk + DB,
    and returns a results dict suitable for display on the Model Training page.

    progress_callback(fraction: float) -> None   (0.0 to 1.0)
    log_callback(message: str) -> None
    """
    def log(msg):
        if log_callback:
            log_callback(msg)

    def progress(p):
        if progress_callback:
            progress_callback(p)

    initialize_database()

    log("Loading raw dataset...")
    df = load_raw_dataset()
    progress(0.05)

    log("Running full preprocessing pipeline (clean, engineer, encode, scale, split)...")
    X_train, X_test, y_train, y_test, transformers = full_preprocessing_pipeline(df)
    progress(0.15)

    # Save shared transformers (encoders + scaler) so prediction.py can reuse them
    transformers_path = os.path.join(SAVED_MODELS_DIR, "transformers.joblib")
    joblib.dump(transformers, transformers_path)
    log("Saved preprocessing transformers.")

    results = {}
    model_paths = {}

    steps = [
        ("Logistic Regression", build_logistic_regression),
        ("Decision Tree", build_decision_tree),
        ("SVM", build_svm),
    ]

    progress_per_step = 0.6 / (len(steps) + 1)
    current_progress = 0.15

    for name, builder in steps:
        log(f"Training {name}...")
        model = builder()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        metrics = evaluate_classifier(y_test, y_pred, y_proba)
        results[name] = metrics

        file_path = os.path.join(SAVED_MODELS_DIR, f"{name.replace(' ', '_').lower()}.joblib")
        joblib.dump(model, file_path)
        model_paths[name] = file_path

        log(f"{name} -> Accuracy: {metrics['accuracy']}, ROC AUC: {metrics['roc_auc']}")
        current_progress += progress_per_step
        progress(current_progress)

    # --- Neural Network (Keras) ---
    log("Training Neural Network (Keras)...")
    nn_model = build_neural_network(X_train.shape[1])
    nn_model.fit(
        X_train, y_train,
        epochs=25, batch_size=32, verbose=0,
        validation_split=0.1,
    )
    y_proba_nn = nn_model.predict(X_test, verbose=0).flatten()
    y_pred_nn = (y_proba_nn >= 0.5).astype(int)
    metrics_nn = evaluate_classifier(y_test, y_pred_nn, y_proba_nn)
    results["Neural Network"] = metrics_nn

    nn_path = os.path.join(SAVED_MODELS_DIR, "neural_network.keras")
    nn_model.save(nn_path)
    model_paths["Neural Network"] = nn_path

    log(f"Neural Network -> Accuracy: {metrics_nn['accuracy']}, ROC AUC: {metrics_nn['roc_auc']}")
    progress(0.9)

    # --- Best model selection ---
    best_name = select_best_model(results)
    log(f"Best model selected: {best_name} (highest ROC AUC)")

    for name, metrics in results.items():
        save_model_metadata(
            model_name=name,
            file_path=model_paths[name],
            metrics=metrics,
            is_best=(name == best_name),
        )

    # Persist a convenience pointer to the best model for prediction.py
    best_info = {"name": best_name, "path": model_paths[best_name]}
    joblib.dump(best_info, os.path.join(SAVED_MODELS_DIR, "best_model_info.joblib"))

    progress(1.0)
    log("Training complete.")

    return {
        "results": results,
        "best_model": best_name,
        "model_paths": model_paths,
        "transformers_path": transformers_path,
    }


if __name__ == "__main__":
    def cli_log(msg):
        print(f"[LOG] {msg}")

    def cli_progress(p):
        print(f"[PROGRESS] {int(p * 100)}%")

    output = train_all_models(progress_callback=cli_progress, log_callback=cli_log)
    print("\n=== FINAL RESULTS ===")
    for name, metrics in output["results"].items():
        print(name, {k: v for k, v in metrics.items() if k != "confusion_matrix"})
    print("\nBest model:", output["best_model"])
