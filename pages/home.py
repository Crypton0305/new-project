"""
pages/home.py
--------------
PAGE 1 - HOME DASHBOARD

Shows: Welcome Screen, Project Overview, Diabetes Statistics, Risk Information,
Navigation Menu (handled by sidebar), Key Features.
"""

import streamlit as st


def render():
    st.title("🏠 Home Dashboard")
    st.markdown(f"### Welcome, {st.session_state.get('full_name', 'User')} 👋")

    st.markdown(
        """
        The **Intelligent Diabetes Risk Predictor** is an AI-powered clinical decision
        support system that helps patients and healthcare providers assess diabetes risk
        using machine learning, and turns that assessment into clear, actionable guidance.
        """
    )

    st.divider()

    # --- Key global diabetes statistics (well-known public health figures) ---
    st.subheader("🌍 Diabetes at a Glance")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Adults with Diabetes Worldwide", "~537M", help="Approximate global estimate")
    col2.metric("Undiagnosed Cases", "~240M", help="Many cases go undetected for years")
    col3.metric("Type 2 Diabetes Share", "~90%", help="Of all diabetes cases globally")
    col4.metric("Preventable Cases", "Significant %", help="Through lifestyle intervention")

    st.caption("Figures are approximate global public-health estimates intended for educational context.")

    st.divider()

    # --- Risk information ---
    st.subheader("⚠️ Why Early Risk Detection Matters")
    risk_col1, risk_col2 = st.columns(2)
    with risk_col1:
        st.markdown(
            """
            **Common Risk Factors**
            - High Body Mass Index (BMI)
            - Hypertension (high blood pressure)
            - Heart disease history
            - Smoking history
            - Elevated blood glucose levels
            - Elevated HbA1c levels
            - Advancing age
            """
        )
    with risk_col2:
        st.markdown(
            """
            **Benefits of Early Detection**
            - Enables lifestyle intervention before disease onset
            - Reduces risk of long-term complications
            - Supports informed conversations with healthcare providers
            - Allows continuous tracking of risk trends over time
            """
        )

    st.divider()

    # --- Key features ---
    st.subheader("✨ Key Features of This System")
    feat_cols = st.columns(3)
    features = [
        ("🤖", "ML-Powered Prediction", "Compares 4 trained models and automatically uses the best performer."),
        ("📊", "Interactive Data Analysis", "Explore the underlying dataset with rich Plotly visualizations."),
        ("🔍", "Explainable AI", "Understand which factors are driving your risk score."),
        ("💡", "Personalized Recommendations", "Diet, exercise, and lifestyle guidance tailored to your result."),
        ("📈", "Longitudinal Tracking", "Track how your risk changes over time, visit to visit."),
        ("📄", "Downloadable Reports", "Generate professional PDF/CSV reports of your assessment."),
    ]
    for i, (icon, title, desc) in enumerate(features):
        with feat_cols[i % 3]:
            st.markdown(f"**{icon} {title}**")
            st.caption(desc)

    st.divider()
    st.info(
        "👉 Use the sidebar to navigate to **Diabetes Prediction** to run your first risk assessment, "
        "or explore **Data Analysis** to understand the dataset behind the models."
    )

    st.warning(
        "⚕️ **Medical Disclaimer:** This tool is a decision-support aid for educational and "
        "screening purposes. It does not replace professional medical diagnosis or advice."
    )
