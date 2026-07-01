"""
pages/risk_analysis.py
-------------------------
PAGE 5 - RISK FACTOR ANALYSIS

Shows: Feature Importance, SHAP Analysis, Key Risk Factors, Explainable AI
Results, with understandable plain-language explanations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.prediction import get_prediction_engine
from utils.preprocessing import load_raw_dataset, full_preprocessing_pipeline
from config import FEATURE_COLUMNS


FRIENDLY_NAMES = {
    "age": "Age",
    "gender": "Gender",
    "bmi": "Body Mass Index (BMI)",
    "hypertension": "Hypertension",
    "heart_disease": "Heart Disease",
    "smoking_history": "Smoking History",
    "blood_glucose_level": "Blood Glucose Level",
    "HbA1c_level": "HbA1c Level",
}


def render():
    st.title("🔍 Risk Factor Analysis")
    st.caption("Explainable AI: understand which factors most influence diabetes risk predictions.")

    try:
        engine = get_prediction_engine()
    except FileNotFoundError as e:
        st.error(str(e))
        return

    st.info(f"Explaining predictions from: **{engine.model_name}**")

    # --- Global Feature Importance ---
    st.subheader("📊 Global Feature Importance")

    importance_df = None
    try:
        if engine.model_type == "sklearn" and hasattr(engine.model, "coef_"):
            importances = np.abs(engine.model.coef_[0])
            importance_df = pd.DataFrame({"Feature": FEATURE_COLUMNS, "Importance": importances})
        elif engine.model_type == "sklearn" and hasattr(engine.model, "feature_importances_"):
            importances = engine.model.feature_importances_
            importance_df = pd.DataFrame({"Feature": FEATURE_COLUMNS, "Importance": importances})
    except Exception:
        importance_df = None

    if importance_df is not None:
        importance_df["Feature"] = importance_df["Feature"].map(lambda f: FRIENDLY_NAMES.get(f, f))
        importance_df = importance_df.sort_values("Importance", ascending=True)
        fig = px.bar(importance_df, x="Importance", y="Feature", orientation="h",
                     title="Which Factors Drive the Model's Predictions?", color="Importance",
                     color_continuous_scale="Tealrose")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(
            "The current best model (e.g. SVM with RBF kernel, or Neural Network) does not expose "
            "linear coefficients directly. Use the SHAP analysis below for model-agnostic explanations."
        )

    st.divider()

    # --- SHAP Analysis ---
    st.subheader("🧠 SHAP Analysis (SHapley Additive exPlanations)")
    st.caption("SHAP values show how much each factor pushed a specific prediction higher or lower risk.")

    if "last_patient_input" in st.session_state:
        if st.button("Run SHAP Explanation for Last Prediction"):
            with st.spinner("Computing SHAP values..."):
                try:
                    import shap
                    df = load_raw_dataset()
                    X_train, X_test, y_train, y_test, transformers = full_preprocessing_pipeline(df)

                    from utils.preprocessing import preprocess_single_input
                    patient_X = preprocess_single_input(st.session_state["last_patient_input"], transformers)

                    if engine.model_type == "sklearn":
                        background = X_train.sample(min(100, len(X_train)), random_state=42)
                        if hasattr(engine.model, "predict_proba"):
                            explainer = shap.KernelExplainer(
                                lambda x: engine.model.predict_proba(pd.DataFrame(x, columns=FEATURE_COLUMNS))[:, 1],
                                background,
                            )
                        else:
                            explainer = shap.KernelExplainer(engine.model.predict, background)
                        shap_values = explainer.shap_values(patient_X, nsamples=100)
                    else:
                        background = X_train.sample(min(50, len(X_train)), random_state=42).values
                        explainer = shap.KernelExplainer(
                            lambda x: engine.model.predict(x, verbose=0).flatten(), background
                        )
                        shap_values = explainer.shap_values(patient_X.values, nsamples=50)

                    shap_arr = np.array(shap_values).flatten()
                    shap_df = pd.DataFrame({
                        "Feature": [FRIENDLY_NAMES.get(c, c) for c in FEATURE_COLUMNS],
                        "SHAP Value": shap_arr,
                    }).sort_values("SHAP Value")

                    fig_shap = px.bar(
                        shap_df, x="SHAP Value", y="Feature", orientation="h",
                        title="SHAP Contribution to This Patient's Risk Prediction",
                        color="SHAP Value", color_continuous_scale="RdBu_r",
                    )
                    st.plotly_chart(fig_shap, use_container_width=True)

                    st.markdown("**Plain-language interpretation:**")
                    top_positive = shap_df.sort_values("SHAP Value", ascending=False).iloc[0]
                    top_negative = shap_df.sort_values("SHAP Value", ascending=True).iloc[0]
                    st.markdown(
                        f"- 🔺 **{top_positive['Feature']}** contributed the most toward **increasing** this "
                        f"patient's predicted risk.\n"
                        f"- 🔻 **{top_negative['Feature']}** contributed the most toward **decreasing** "
                        f"this patient's predicted risk."
                    )
                except Exception as e:
                    st.warning(f"SHAP computation could not complete: {e}")
    else:
        st.info("Run a prediction on the **Diabetes Prediction** page first, then return here for a SHAP explanation of that specific result.")

    st.divider()

    # --- Key Risk Factors (clinical, static reference) ---
    st.subheader("🩺 Key Clinical Risk Factors for Diabetes")
    st.markdown(
        """
        - **Elevated HbA1c Level** — reflects average blood sugar over ~3 months; the strongest lab indicator.
        - **High Blood Glucose Level** — directly measures current blood sugar concentration.
        - **High BMI** — excess body fat is strongly linked to insulin resistance.
        - **Hypertension** — frequently co-occurs with metabolic syndrome and diabetes.
        - **Heart Disease** — shares many underlying risk pathways with diabetes.
        - **Age** — risk generally increases with age, especially after 45.
        - **Smoking History** — smoking is associated with insulin resistance.
        """
    )
