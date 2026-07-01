"""
config.py
---------
Global configuration and constants for the Intelligent Diabetes Risk Predictor.
Centralizing these values keeps the codebase modular and avoids magic numbers/strings
scattered across pages and utils.
"""

import os

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_PATH = os.path.join(DATA_DIR, "diabetes.csv")

DATABASE_DIR = os.path.join(BASE_DIR, "database")
# Path to the Firebase service account JSON key (download from Firebase Console:
# Project Settings -> Service Accounts -> Generate New Private Key)
FIREBASE_CREDENTIALS_PATH = os.path.join(DATABASE_DIR, "firebase-credentials.json")

MODELS_DIR = os.path.join(BASE_DIR, "models")
SAVED_MODELS_DIR = os.path.join(MODELS_DIR, "saved_models")

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
STYLES_PATH = os.path.join(ASSETS_DIR, "styles.css")

REPORTS_DIR = os.path.join(BASE_DIR, "documentation", "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# APP METADATA
# ---------------------------------------------------------------------------
APP_NAME = "Intelligent Diabetes Risk Predictor"
APP_ICON = "🩺"
APP_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# ROLES
# ---------------------------------------------------------------------------
ROLE_ADMIN = "Admin"
ROLE_PROVIDER = "Healthcare Provider"
ROLE_PATIENT = "Patient"
ALL_ROLES = [ROLE_ADMIN, ROLE_PROVIDER, ROLE_PATIENT]

# ---------------------------------------------------------------------------
# ML / DATA SETTINGS
# ---------------------------------------------------------------------------
TARGET_COLUMN = "diabetes"
TEST_SIZE = 0.30
RANDOM_STATE = 42

# Expected feature columns (based on the Kaggle diabetic prediction dataset schema)
FEATURE_COLUMNS = [
    "age",
    "gender",
    "bmi",
    "hypertension",
    "heart_disease",
    "smoking_history",
    "blood_glucose_level",
    "HbA1c_level",
]

CATEGORICAL_COLUMNS = ["gender", "smoking_history"]
NUMERIC_COLUMNS = ["age", "bmi", "blood_glucose_level", "HbA1c_level"]
BINARY_COLUMNS = ["hypertension", "heart_disease"]

MODEL_NAMES = [
    "Logistic Regression",
    "Decision Tree",
    "SVM",
    "Neural Network",
]

# ---------------------------------------------------------------------------
# RISK CATEGORY THRESHOLDS (based on predicted probability of diabetes)
# ---------------------------------------------------------------------------
RISK_LOW_MAX = 0.33
RISK_MODERATE_MAX = 0.66
# Anything above RISK_MODERATE_MAX is High Risk

RISK_LABELS = {
    "low": "Low Risk",
    "moderate": "Moderate Risk",
    "high": "High Risk",
}

# ---------------------------------------------------------------------------
# UI THEME
# ---------------------------------------------------------------------------
PRIMARY_COLOR = "#0E7C7B"     # teal - medical/clean
SECONDARY_COLOR = "#17A398"
ACCENT_COLOR = "#E63946"      # alert red for high risk
SUCCESS_COLOR = "#2A9D8F"
WARNING_COLOR = "#F4A261"
BACKGROUND_COLOR = "#F7FAFC"
