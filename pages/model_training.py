"""
pages/model_training.py
-------------------------
PAGE 3 - MODEL TRAINING

Features: Train Models Button, Training Progress, Training Logs,
Model Performance Table, Best Model Selection.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from models.train_models import train_all_models
from models.evaluate_models import metrics_to_dataframe
from database.db_manager import get_all_models
from utils.authentication import require_role
from config import ROLE_ADMIN, ROLE_PROVIDER


def render():
    require_role(st.session_state, st, ROLE_ADMIN, ROLE_PROVIDER)

    st.title("🤖 Model Training")
    st.caption("Train and compare Logistic Regression, Decision Tree, SVM, and a Neural Network")

    # --- Existing model history from DB ---
    existing_models = get_all_models()
    if existing_models and "training_results" not in st.session_state:
        st.info(f"📦 {len(existing_models)} previously trained model record(s) found in the database.")
        with st.expander("View Previous Training History"):
            hist_df = pd.DataFrame(existing_models)[
                ["model_name", "accuracy", "precision_score", "recall_score", "f1_score", "roc_auc", "is_best_model", "trained_at"]
            ]
            st.dataframe(hist_df, use_container_width=True, hide_index=True)

    st.divider()

    if st.button("🚀 Train All Models", type="primary", use_container_width=True):
        log_box = st.empty()
        progress_bar = st.progress(0.0)
        logs = []

        def log_callback(msg):
            logs.append(msg)
            log_box.code("\n".join(logs), language=None)

        def progress_callback(p):
            progress_bar.progress(min(p, 1.0))

        with st.spinner("Training in progress..."):
            output = train_all_models(progress_callback=progress_callback, log_callback=log_callback)

        st.session_state["training_results"] = output
        st.success(f"✅ Training complete! Best model: **{output['best_model']}**")

        # Reload prediction engine so the new best model is used immediately
        from utils import prediction as prediction_module
        prediction_module._engine_instance = None

    # --- Performance Table & Best Model ---
    if "training_results" in st.session_state:
        st.divider()
        st.subheader("📋 Model Performance Comparison")
        results = st.session_state["training_results"]["results"]
        best_model = st.session_state["training_results"]["best_model"]

        df_metrics = metrics_to_dataframe(results)
        st.dataframe(
            df_metrics.style.apply(
                lambda row: ["background-color: #d4edda" if row["Model"] == best_model else "" for _ in row],
                axis=1,
            ),
            use_container_width=True, hide_index=True,
        )

        st.success(f"🏆 **Best Performing Model: {best_model}** (selected by highest ROC AUC)")

        # Bar chart comparison
        melted = df_metrics.melt(id_vars="Model", var_name="Metric", value_name="Score")
        fig = px.bar(melted, x="Model", y="Score", color="Metric", barmode="group",
                     title="Model Metric Comparison")
        st.plotly_chart(fig, use_container_width=True)

        # Confusion matrices
        st.subheader("🧮 Confusion Matrices")
        cols = st.columns(len(results))
        for i, (name, metrics) in enumerate(results.items()):
            with cols[i]:
                cm = metrics["confusion_matrix"]
                fig_cm = px.imshow(
                    cm, text_auto=True, color_continuous_scale="Blues",
                    labels=dict(x="Predicted", y="Actual"),
                    x=["Non-Diabetic", "Diabetic"], y=["Non-Diabetic", "Diabetic"],
                )
                fig_cm.update_layout(title=name, height=300, margin=dict(t=40, b=10))
                st.plotly_chart(fig_cm, use_container_width=True)
    else:
        st.info("👆 Click **Train All Models** to begin training, or check previous results above if already trained.")
