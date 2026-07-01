"""
pages/tracking.py
--------------------
PAGE 7 - LONGITUDINAL TRACKING

Stores and displays prediction history: Historical Records, Trend Analysis,
Health Progress Graphs, Risk Changes Over Time.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from database.db_manager import get_predictions_for_user, get_health_records_for_user


def render():
    st.title("📈 Longitudinal Tracking")
    st.caption("Track how your diabetes risk and health metrics have changed over time.")

    user_id = st.session_state["user_id"]
    predictions = get_predictions_for_user(user_id)
    health_records = get_health_records_for_user(user_id)

    if not predictions:
        st.info("No prediction history yet. Visit the **Diabetes Prediction** page to create your first assessment.")
        return

    pred_df = pd.DataFrame(predictions)
    pred_df["predicted_at"] = pd.to_datetime(pred_df["predicted_at"])
    pred_df = pred_df.sort_values("predicted_at")

    # --- Historical Records ---
    st.subheader("📋 Historical Records")
    display_df = pred_df[["predicted_at", "prediction_result", "probability", "confidence_score", "risk_category"]].copy()
    display_df["prediction_result"] = display_df["prediction_result"].map({0: "Non-Diabetic", 1: "Diabetic"})
    display_df.columns = ["Date", "Result", "Probability", "Confidence", "Risk Category"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()

    # --- Trend Analysis / Risk Changes Over Time ---
    st.subheader("📉 Risk Trend Over Time")
    fig_trend = px.line(
        pred_df, x="predicted_at", y="probability", markers=True,
        title="Predicted Diabetes Probability Over Time",
        labels={"predicted_at": "Date", "probability": "Predicted Probability"},
    )
    fig_trend.add_hline(y=0.33, line_dash="dash", line_color="green", annotation_text="Low/Moderate boundary")
    fig_trend.add_hline(y=0.66, line_dash="dash", line_color="red", annotation_text="Moderate/High boundary")
    st.plotly_chart(fig_trend, use_container_width=True)

    # --- Risk category changes ---
    st.subheader("🚦 Risk Category Changes")
    fig_cat = px.scatter(
        pred_df, x="predicted_at", y="risk_category",
        color="risk_category", title="Risk Category by Assessment Date",
        category_orders={"risk_category": ["Low Risk", "Moderate Risk", "High Risk"]},
        color_discrete_map={"Low Risk": "#2A9D8F", "Moderate Risk": "#F4A261", "High Risk": "#E63946"},
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    st.divider()

    # --- Health Progress Graphs (from HealthRecords) ---
    if health_records:
        st.subheader("🩺 Health Metric Progress")
        hr_df = pd.DataFrame(health_records)
        hr_df["recorded_at"] = pd.to_datetime(hr_df["recorded_at"])
        hr_df = hr_df.sort_values("recorded_at")

        metric_choice = st.selectbox(
            "Select a metric to track",
            ["bmi", "blood_glucose_level", "hba1c_level"],
            format_func=lambda x: {"bmi": "BMI", "blood_glucose_level": "Blood Glucose Level", "hba1c_level": "HbA1c Level"}[x],
        )
        fig_metric = px.line(
            hr_df, x="recorded_at", y=metric_choice, markers=True,
            title=f"{metric_choice.replace('_', ' ').title()} Over Time",
        )
        st.plotly_chart(fig_metric, use_container_width=True)

    # --- Summary ---
    st.divider()
    latest = pred_df.iloc[-1]
    first = pred_df.iloc[0]
    delta = latest["probability"] - first["probability"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Assessments", len(pred_df))
    col2.metric("Latest Risk Category", latest["risk_category"])
    col3.metric("Change Since First Assessment", f"{delta * 100:+.1f}%")
