"""
pages/admin.py
-----------------
PAGE 13 - ADMIN PANEL

Admin Features: Upload Dataset, Manage Users, View Statistics, Train Models,
Update Models, Monitor System Performance, Manage Reports, View Feedback.
"""

import os
import streamlit as st
import pandas as pd

from utils.authentication import require_role
from config import ROLE_ADMIN, DATASET_PATH, DATA_DIR
from database.db_manager import (
    get_all_users, set_user_active_status, delete_user, get_all_predictions,
    get_all_models, get_all_feedback, get_all_reports,
)


def render():
    require_role(st.session_state, st, ROLE_ADMIN)

    st.title("⚙️ Admin Panel")
    st.caption("System administration: dataset, users, models, and monitoring.")

    tabs = st.tabs([
        "📁 Upload Dataset", "👥 Manage Users", "📊 View Statistics",
        "🤖 Train / Update Models", "🖥️ System Performance",
        "📄 Manage Reports", "💬 View Feedback",
    ])

    # --- Upload Dataset ---
    with tabs[0]:
        st.subheader("📁 Upload Dataset")
        st.caption(f"Current dataset: `{DATASET_PATH}`")
        uploaded_file = st.file_uploader("Upload a replacement diabetes.csv dataset", type=["csv"])
        if uploaded_file is not None:
            preview_df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded dataset:")
            st.dataframe(preview_df.head(10), use_container_width=True)
            if st.button("✅ Confirm and Replace Dataset", type="primary"):
                uploaded_file.seek(0)
                with open(DATASET_PATH, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Dataset replaced successfully. Visit 'Train / Update Models' to retrain.")
                st.cache_data.clear()

    # --- Manage Users ---
    with tabs[1]:
        st.subheader("👥 Manage Users")
        users = get_all_users()
        if not users:
            st.info("No users found.")
        else:
            users_df = pd.DataFrame(users)
            st.dataframe(users_df, use_container_width=True, hide_index=True)

            st.markdown("#### Update User Status")
            target_user_id = st.selectbox(
                "Select user", users_df["user_id"].tolist(),
                format_func=lambda uid: f"#{uid} - {users_df[users_df['user_id']==uid]['username'].values[0]}",
            )
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("🚫 Deactivate User", use_container_width=True):
                    if target_user_id == st.session_state["user_id"]:
                        st.error("You cannot deactivate your own account.")
                    else:
                        set_user_active_status(target_user_id, False)
                        st.success(f"User #{target_user_id} deactivated.")
                        st.rerun()
            with action_col2:
                if st.button("✅ Activate User", use_container_width=True):
                    set_user_active_status(target_user_id, True)
                    st.success(f"User #{target_user_id} activated.")
                    st.rerun()

            with st.expander("⚠️ Danger Zone: Delete User"):
                if st.button("🗑️ Permanently Delete Selected User"):
                    if target_user_id == st.session_state["user_id"]:
                        st.error("You cannot delete your own account.")
                    else:
                        delete_user(target_user_id)
                        st.success(f"User #{target_user_id} deleted.")
                        st.rerun()

    # --- View Statistics ---
    with tabs[2]:
        st.subheader("📊 System Statistics")
        users = get_all_users()
        predictions = get_all_predictions()
        models = get_all_models()
        feedback = get_all_feedback()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Users", len(users))
        c2.metric("Total Predictions", len(predictions))
        c3.metric("Trained Models", len(models))
        c4.metric("Feedback Entries", len(feedback))

        if users:
            role_counts = pd.DataFrame(users)["role"].value_counts()
            st.bar_chart(role_counts)

    # --- Train / Update Models ---
    with tabs[3]:
        st.subheader("🤖 Train / Update Models")
        st.info("Use the dedicated **Model Training** page (sidebar) for the full training workflow with progress, logs, and metrics.")
        models = get_all_models()
        if models:
            st.dataframe(pd.DataFrame(models), use_container_width=True, hide_index=True)
        if st.button("Go to Model Training Page"):
            st.info("Please select '🤖 Model Training' from the sidebar.")

    # --- System Performance Monitoring ---
    with tabs[4]:
        st.subheader("🖥️ Monitor System Performance")
        st.caption("Database backend: Firebase Firestore (cloud-hosted, no local file size to report)")

        perf_col1, perf_col2, perf_col3 = st.columns(3)
        perf_col1.metric("Total Users", len(get_all_users()))
        perf_col2.metric("Total Predictions Logged", len(get_all_predictions()))
        perf_col3.metric("Models Stored", len(get_all_models()))

        if models := get_all_models():
            best = [m for m in models if m.get("is_best_model")]
            if best:
                st.success(f"Active best model: **{best[0]['model_name']}** (ROC AUC: {best[0]['roc_auc']})")

    # --- Manage Reports ---
    with tabs[5]:
        st.subheader("📄 Manage Reports")
        reports = get_all_reports()
        if not reports:
            st.caption("No reports generated yet.")
        else:
            reports_df = pd.DataFrame(reports)[["report_id", "full_name", "report_type", "file_path", "generated_at"]]
            st.dataframe(reports_df, use_container_width=True, hide_index=True)

    # --- View Feedback ---
    with tabs[6]:
        st.subheader("💬 View Feedback")
        feedback = get_all_feedback()
        if not feedback:
            st.caption("No feedback submitted yet.")
        else:
            fb_df = pd.DataFrame(feedback)[["submitted_at", "full_name", "role", "feedback_type", "rating", "message"]]
            st.dataframe(fb_df, use_container_width=True, hide_index=True)
