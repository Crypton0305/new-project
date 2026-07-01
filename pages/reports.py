"""
pages/reports.py
-------------------
PAGE 9 - REPORT GENERATION

Generates PDF and CSV reports including: User Information, Prediction Results,
Risk Analysis, Model Metrics, Recommendations. Allows downloading.
"""

import streamlit as st
import os

from utils.report_generator import generate_pdf_report, generate_csv_report
from pages.recommendations import _get_recommendations
from database.db_manager import get_best_model, add_report, get_reports_for_user, get_user_by_id


def render():
    st.title("📄 Report Generation")
    st.caption("Generate a downloadable PDF or CSV report of your diabetes risk assessment.")

    if "last_prediction" not in st.session_state:
        st.info("Run a prediction on the **Diabetes Prediction** page first to generate a report.")
        return

    user = get_user_by_id(st.session_state["user_id"])
    prediction_result = st.session_state["last_prediction"]
    patient_input = st.session_state.get("last_patient_input", {})
    risk_category = prediction_result["risk_category"]

    recommendations = _get_recommendations(risk_category, patient_input)
    best_model = get_best_model()

    st.subheader("📝 Report Preview Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Prediction", "Diabetic" if prediction_result["prediction_result"] == 1 else "Non-Diabetic")
    col2.metric("Risk Category", risk_category)
    col3.metric("Confidence", f"{prediction_result['confidence_score'] * 100:.1f}%")

    st.divider()

    gen_col1, gen_col2 = st.columns(2)

    with gen_col1:
        st.markdown("### 📕 PDF Report")
        st.caption("Includes patient info, prediction, model metrics, and recommendations.")
        if st.button("Generate PDF Report", use_container_width=True):
            with st.spinner("Generating PDF..."):
                pdf_path = generate_pdf_report(
                    user, patient_input, prediction_result,
                    model_metrics=best_model, recommendations=recommendations,
                )
                add_report(user["user_id"], None, "PDF", pdf_path)
                st.session_state["last_pdf_report"] = pdf_path
            st.success("PDF report generated!")

        if "last_pdf_report" in st.session_state and os.path.exists(st.session_state["last_pdf_report"]):
            with open(st.session_state["last_pdf_report"], "rb") as f:
                st.download_button(
                    "⬇️ Download PDF Report", data=f.read(),
                    file_name=os.path.basename(st.session_state["last_pdf_report"]),
                    mime="application/pdf", use_container_width=True,
                )

    with gen_col2:
        st.markdown("### 📊 CSV Report")
        st.caption("Includes raw input fields and prediction values for record-keeping or import.")
        if st.button("Generate CSV Report", use_container_width=True):
            with st.spinner("Generating CSV..."):
                csv_path = generate_csv_report(user, patient_input, prediction_result)
                add_report(user["user_id"], None, "CSV", csv_path)
                st.session_state["last_csv_report"] = csv_path
            st.success("CSV report generated!")

        if "last_csv_report" in st.session_state and os.path.exists(st.session_state["last_csv_report"]):
            with open(st.session_state["last_csv_report"], "rb") as f:
                st.download_button(
                    "⬇️ Download CSV Report", data=f.read(),
                    file_name=os.path.basename(st.session_state["last_csv_report"]),
                    mime="text/csv", use_container_width=True,
                )

    st.divider()

    # --- Past reports ---
    st.subheader("🗂️ Your Past Reports")
    past_reports = get_reports_for_user(user["user_id"])
    if not past_reports:
        st.caption("No previous reports generated yet.")
    else:
        for report in past_reports:
            r_col1, r_col2, r_col3 = st.columns([3, 2, 2])
            r_col1.write(os.path.basename(report["file_path"]))
            r_col2.write(report["report_type"])
            r_col3.write(report["generated_at"][:19])
