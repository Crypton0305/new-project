"""
generate_dataset.py
--------------------
Generates a realistic synthetic dataset matching the schema of the Kaggle
"Diabetic Prediction" dataset (akhilalexander/diabeticprediction):

    age, gender, bmi, hypertension, heart_disease, smoking_history,
    blood_glucose_level, HbA1c_level, diabetes

This is used because direct internet download of the Kaggle dataset is not
available in this environment. The generation logic uses medically plausible
relationships (higher BMI/glucose/HbA1c/age increase diabetes probability)
so that downstream ML training produces meaningful, non-trivial results.

Run once: python generate_dataset.py
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

N = 8000

genders = np.random.choice(["Male", "Female", "Other"], size=N, p=[0.48, 0.50, 0.02])
ages = np.clip(np.random.normal(45, 20, N), 1, 90).round(1)

smoking_categories = ["never", "No Info", "former", "current", "not current", "ever"]
smoking_history = np.random.choice(
    smoking_categories, size=N, p=[0.35, 0.32, 0.10, 0.10, 0.08, 0.05]
)

bmi = np.clip(np.random.normal(27, 6, N), 12, 60).round(2)
hypertension = np.random.binomial(1, 0.15, N)
heart_disease = np.random.binomial(1, 0.08, N)

blood_glucose_level = np.clip(np.random.normal(135, 45, N), 70, 300).round(1)
hba1c_level = np.clip(np.random.normal(5.7, 1.0, N), 3.5, 9.5).round(2)

# Build a risk score from medically plausible weighted factors, then convert
# to probability via logistic function and sample the binary outcome.
risk_score = (
    0.035 * (ages - 45)
    + 0.10 * (bmi - 27)
    + 1.8 * hypertension
    + 1.6 * heart_disease
    + 0.045 * (blood_glucose_level - 135)
    + 1.3 * (hba1c_level - 5.7)
    + np.where(np.isin(smoking_history, ["current", "former"]), 0.4, 0.0)
)

probability = 1 / (1 + np.exp(-(risk_score - 1.5) * 0.6))
diabetes = np.random.binomial(1, probability)

df = pd.DataFrame({
    "gender": genders,
    "age": ages,
    "hypertension": hypertension,
    "heart_disease": heart_disease,
    "smoking_history": smoking_history,
    "bmi": bmi,
    "HbA1c_level": hba1c_level,
    "blood_glucose_level": blood_glucose_level,
    "diabetes": diabetes,
})

# Inject a small percentage of missing values to make data-cleaning steps meaningful
for col in ["bmi", "HbA1c_level", "blood_glucose_level"]:
    mask = np.random.rand(N) < 0.02
    df.loc[mask, col] = np.nan

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diabetes.csv")
df.to_csv(out_path, index=False)
print(f"Generated {len(df)} rows -> {out_path}")
print(df["diabetes"].value_counts(normalize=True))
