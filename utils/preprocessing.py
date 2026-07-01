"""
preprocessing.py
-----------------
Data cleaning, feature engineering, encoding, scaling, validation, outlier
detection and EDA helper functions for the Diabetes Risk Predictor.

All functions are pure (no Streamlit calls) so they can be unit-tested and
reused by both the model-training pipeline and the live prediction pipeline.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DATASET_PATH, TARGET_COLUMN, TEST_SIZE, RANDOM_STATE,
    CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, BINARY_COLUMNS, FEATURE_COLUMNS,
)


# ---------------------------------------------------------------------------
# LOADING
# ---------------------------------------------------------------------------
def load_raw_dataset(path: str = DATASET_PATH) -> pd.DataFrame:
    """Loads the raw CSV dataset into a DataFrame."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at {path}. Run data/generate_dataset.py or place diabetes.csv there."
        )
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# DATA VALIDATION
# ---------------------------------------------------------------------------
def validate_dataset(df: pd.DataFrame) -> dict:
    """Validates that required columns exist and reports basic data-health info."""
    missing_cols = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    report = {
        "missing_columns": missing_cols,
        "is_valid": len(missing_cols) == 0,
        "row_count": len(df),
        "duplicate_rows": int(df.duplicated().sum()),
    }
    return report


# ---------------------------------------------------------------------------
# MISSING VALUE HANDLING
# ---------------------------------------------------------------------------
def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Imputes missing numeric values with median, categorical with mode."""
    df = df.copy()
    for col in NUMERIC_COLUMNS:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].mode()[0])
    return df


def get_missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a tidy summary table of missing values per column."""
    summary = df.isnull().sum().reset_index()
    summary.columns = ["column", "missing_count"]
    summary["missing_percent"] = (summary["missing_count"] / len(df) * 100).round(2)
    return summary[summary["missing_count"] > 0].sort_values("missing_count", ascending=False)


# ---------------------------------------------------------------------------
# OUTLIER DETECTION
# ---------------------------------------------------------------------------
def detect_outliers_iqr(df: pd.DataFrame, columns=None) -> dict:
    """Detects outliers per numeric column using the IQR method. Returns counts and bounds."""
    columns = columns or NUMERIC_COLUMNS
    results = {}
    for col in columns:
        if col not in df.columns:
            continue
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outlier_count = int(((df[col] < lower) | (df[col] > upper)).sum())
        results[col] = {"lower_bound": round(lower, 2), "upper_bound": round(upper, 2), "outlier_count": outlier_count}
    return results


def cap_outliers(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    """Caps (winsorizes) outliers to the IQR bounds rather than dropping rows."""
    df = df.copy()
    columns = columns or NUMERIC_COLUMNS
    for col in columns:
        if col not in df.columns:
            continue
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        df[col] = df[col].clip(lower, upper)
    return df


# ---------------------------------------------------------------------------
# CLEANING PIPELINE
# ---------------------------------------------------------------------------
def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Full cleaning pipeline: dedupe, missing values, outlier capping."""
    df = df.copy()
    df = df.drop_duplicates()
    df = handle_missing_values(df)
    df = cap_outliers(df)
    return df


# ---------------------------------------------------------------------------
# FEATURE ENGINEERING
# ---------------------------------------------------------------------------
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adds derived features that help model performance and clinical interpretability."""
    df = df.copy()

    def bmi_category(bmi):
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    if "bmi" in df.columns:
        df["bmi_category"] = df["bmi"].apply(bmi_category)

    def age_group(age):
        if age < 18:
            return "Child"
        elif age < 40:
            return "Young Adult"
        elif age < 60:
            return "Middle Age"
        else:
            return "Senior"

    if "age" in df.columns:
        df["age_group"] = df["age"].apply(age_group)

    if "HbA1c_level" in df.columns:
        df["hba1c_high"] = (df["HbA1c_level"] >= 6.5).astype(int)

    if "blood_glucose_level" in df.columns:
        df["glucose_high"] = (df["blood_glucose_level"] >= 140).astype(int)

    return df


# ---------------------------------------------------------------------------
# ENCODING
# ---------------------------------------------------------------------------
def encode_features(df: pd.DataFrame, fit_encoders: dict = None):
    """
    Label-encodes categorical columns. If `fit_encoders` is provided (dict of
    column -> fitted LabelEncoder), reuses them for consistent inference-time
    encoding; otherwise fits new encoders and returns them.
    """
    df = df.copy()
    encoders = fit_encoders or {}

    for col in CATEGORICAL_COLUMNS:
        if col not in df.columns:
            continue
        if col in encoders:
            le = encoders[col]
            # Handle unseen categories gracefully at inference time
            df[col] = df[col].apply(lambda x: x if x in le.classes_ else le.classes_[0])
            df[col] = le.transform(df[col])
        else:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le

    return df, encoders


# ---------------------------------------------------------------------------
# SCALING / NORMALIZATION
# ---------------------------------------------------------------------------
def scale_features(df: pd.DataFrame, columns=None, fit_scaler: StandardScaler = None):
    """
    Standardizes numeric columns (zero mean, unit variance). If `fit_scaler`
    is provided, reuses it (inference time); otherwise fits a new one.
    """
    df = df.copy()
    columns = columns or NUMERIC_COLUMNS
    columns = [c for c in columns if c in df.columns]

    if fit_scaler is not None:
        scaler = fit_scaler
        df[columns] = scaler.transform(df[columns])
    else:
        scaler = StandardScaler()
        df[columns] = scaler.fit_transform(df[columns])

    return df, scaler


# ---------------------------------------------------------------------------
# FULL PREPROCESSING PIPELINE (used by training)
# ---------------------------------------------------------------------------
def full_preprocessing_pipeline(df: pd.DataFrame):
    """
    Runs the entire pipeline: clean -> feature engineer -> encode -> scale ->
    train/test split. Returns processed splits plus fitted transformers so the
    exact same transformations can be applied to new patient data at inference.
    """
    df = clean_dataset(df)
    df = engineer_features(df)

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    X_encoded, encoders = encode_features(X)
    X_scaled, scaler = scale_features(X_encoded, columns=NUMERIC_COLUMNS)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    transformers = {"encoders": encoders, "scaler": scaler}
    return X_train, X_test, y_train, y_test, transformers


def preprocess_single_input(input_dict: dict, transformers: dict) -> pd.DataFrame:
    """
    Transforms a single patient's raw form input (dict) into a model-ready
    DataFrame row, using the SAME fitted encoders/scaler from training.
    """
    df = pd.DataFrame([input_dict])[FEATURE_COLUMNS]
    df_encoded, _ = encode_features(df, fit_encoders=transformers["encoders"])
    df_scaled, _ = scale_features(df_encoded, columns=NUMERIC_COLUMNS, fit_scaler=transformers["scaler"])
    return df_scaled


# ---------------------------------------------------------------------------
# EDA HELPERS
# ---------------------------------------------------------------------------
def get_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    return df.describe(include="all").transpose()


def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=[np.number])
    return numeric_df.corr()


def get_class_distribution(df: pd.DataFrame) -> pd.Series:
    return df[TARGET_COLUMN].value_counts()
