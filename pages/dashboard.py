"""
pages/dashboard.py
---------------------
PAGE 8 - VISUALIZATION DASHBOARD

Advanced dashboard showing: Prediction Statistics, Risk Levels,
Model Performance, Health Trends, Interactive Charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from database.db_manager import get_all_predictions, get_all_models, get_predictions_for_user
from config import ROLE_ADMIN, ROLE_PROVIDER


def render():
    st.title("📉 Visualization Dashboard")
    st.caption("System-wide and personal analytics at a glance.")

    is_staff = st.session_state["role"] in (ROLE_ADMIN, ROLE_PROVIDER)

    if is_staff:
        predictions = get_all_predictions()
        scope_label = "All Patients (System-Wide)"
    else:
        predictions = get_predictions_for_user(st.session_state["user_id"])
        scope_label = "Your Personal History"

    st.subheader(f"📊 Prediction Statistics — {scope_label}")

    if not predictions:
        st.info("No prediction data available yet.")
    else:
        pred_df = pd.DataFrame(predictions)
        pred_df["predicted_at"] = pd.to_datetime(pred_df["predicted_at"])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Predictions", len(pred_df))
        col2.metric("Diabetic Predictions", int((pred_df["prediction_result"] == 1).sum()))
        col3.metric("Avg. Probability", f"{pred_df['probability'].mean() * 100:.1f}%")
        col4.metric("High Risk Cases", int((pred_df["risk_category"] == "High Risk").sum()))

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            risk_counts = pred_df["risk_category"].value_counts().reset_index()
            risk_counts.columns = ["Risk Category", "Count"]
            fig_risk = px.pie(
                risk_counts, names="Risk Category", values="Count", title="Risk Level Distribution",
                color="Risk Category",
                color_discrete_map={"Low Risk": "#2A9D8F", "Moderate Risk": "#F4A261", "High Risk": "#E63946"},
            )
            st.plotly_chart(fig_risk, use_container_width=True)

        with chart_col2:
            pred_df["date"] = pred_df["predicted_at"].dt.date
            daily_counts = pred_df.groupby("date").size().reset_index(name="count")
            fig_volume = px.bar(daily_counts, x="date", y="count", title="Prediction Volume Over Time")
            st.plotly_chart(fig_volume, use_container_width=True)

        st.subheader("📈 Health Trends")
        fig_health = px.line(
            pred_df.sort_values("predicted_at"), x="predicted_at", y="probability",
            color="risk_category" if is_staff else None,
            title="Predicted Probability Trend", markers=True,
        )
        st.plotly_chart(fig_health, use_container_width=True)

    st.divider()

    # --- Model Performance ---
    st.subheader("🤖 Model Performance")
    models = get_all_models()
    if not models:
        st.info("No trained models found yet. Visit **Model Training** to train models.")
    else:
        model_df = pd.DataFrame(models)
        latest_per_model = model_df.sort_values("trained_at").groupby("model_name").tail(1)

        fig_models = px.bar(
            latest_per_model, x="model_name", y=["accuracy", "precision_score", "recall_score", "f1_score", "roc_auc"],
            barmode="group", title="Latest Model Metrics Comparison",
        )
        st.plotly_chart(fig_models, use_container_width=True)

        best = latest_per_model[latest_per_model["is_best_model"] == 1]
        if not best.empty:
            st.success(f"🏆 Current best model: **{best.iloc[0]['model_name']}** (ROC AUC: {best.iloc[0]['roc_auc']})")
