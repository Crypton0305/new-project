"""
pages/clinical_support.py
----------------------------
PAGE 11 - CLINICAL DECISION SUPPORT

Displays: Prediction Insights, Risk Analysis, Clinical Suggestions,
Healthcare Guidance for use by Admins/Healthcare Providers.

Explicitly states the system assists professionals and does not replace
medical judgment.
"""

import streamlit as st
import pandas as pd

from utils.authentication import require_role
from database.db_manager import get_all_predictions, get_user_by_id, get_best_model
from config import ROLE_ADMIN, ROLE_PROVIDER


def _clinical_suggestion(risk_category: str) -> str:
    if risk_category == "High Risk":
        return (
            "Recommend prompt clinical evaluation: fasting glucose / OGTT confirmation, "
            "HbA1c retest, and assessment of comorbidities (hypertension, lipid profile). "
            "Consider referral to an endocrinologist if confirmed."
        )
    elif risk_category == "Moderate Risk":
        return (
            "Recommend structured lifestyle counseling and a follow-up screening within "
            "3-6 months. Monitor weight, blood pressure, and glycemic markers."
        )
    else:
        return (
            "No immediate clinical action indicated. Reinforce preventive lifestyle habits "
            "and continue routine periodic screening."
        )


def render():
    require_role(st.session_state, st, ROLE_ADMIN, ROLE_PROVIDER)

    st.title("🏥 Clinical Decision Support")
    st.caption("Aggregated prediction insights and clinical guidance to support — not replace — professional judgment.")

    st.error(
        "⚕️ **Important:** This module is a decision-support aid intended to assist healthcare "
        "professionals. It does **not** replace clinical judgment, diagnostic testing, or "
        "individualized patient care. All findings should be clinically verified."
    )

    predictions = get_all_predictions()
    if not predictions:
        st.info("No prediction records available yet.")
        return

    pred_df = pd.DataFrame(predictions)
    pred_df["predicted_at"] = pd.to_datetime(pred_df["predicted_at"])
    pred_df = pred_df.sort_values("predicted_at", ascending=False)

    st.subheader("📋 Prediction Insights")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Assessments", len(pred_df))
    col2.metric("High Risk Cases", int((pred_df["risk_category"] == "High Risk").sum()))
    col3.metric("Avg. Confidence", f"{pred_df['confidence_score'].mean() * 100:.1f}%")

    st.divider()

    st.subheader("🔍 Patient-Level Risk Analysis")
    selected_patient_id = st.selectbox(
        "Select a patient assessment to review",
        pred_df["prediction_id"].tolist(),
        format_func=lambda pid: f"Prediction #{pid}",
    )
    row = pred_df[pred_df["prediction_id"] == selected_patient_id].iloc[0]
    patient = get_user_by_id(row["user_id"])

    detail_col1, detail_col2 = st.columns(2)
    with detail_col1:
        st.markdown(f"**Patient:** {patient['full_name'] if patient else 'Unknown'}")
        st.markdown(f"**Assessment Date:** {row['predicted_at']}")
        st.markdown(f"**Predicted Probability:** {row['probability'] * 100:.1f}%")
    with detail_col2:
        st.markdown(f"**Risk Category:** {row['risk_category']}")
        st.markdown(f"**Confidence Score:** {row['confidence_score'] * 100:.1f}%")
        st.markdown(f"**Outcome:** {'Diabetic' if row['prediction_result'] == 1 else 'Non-Diabetic'}")

    st.subheader("💬 Clinical Suggestions")
    st.info(_clinical_suggestion(row["risk_category"]))

    st.divider()

    st.subheader("🏥 General Healthcare Guidance")
    st.markdown(
        """
        - Use this system's outputs as a **screening aid**, not a diagnostic tool.
        - Cross-reference predictions with laboratory-confirmed glucose/HbA1c testing.
        - Consider the patient's full clinical history, medications, and comorbidities,
          which are not captured by this model.
        - Document clinical reasoning independently when making care decisions.
        """
    )

    best_model = get_best_model()
    if best_model:
        st.caption(
            f"Current model in use: {best_model['model_name']} "
            f"(ROC AUC: {best_model['roc_auc']}, trained {best_model['trained_at'][:10]})"
        )

    st.divider()
    st.subheader("📊 All Recent Assessments")
    display_df = pred_df[["prediction_id", "user_id", "predicted_at", "risk_category", "probability", "confidence_score"]].head(50)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
