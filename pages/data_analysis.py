"""
pages/data_analysis.py
------------------------
PAGE 2 - DATA ANALYSIS

Shows: Dataset Preview, Dataset Information, Missing Values, Summary Statistics,
Histograms, Boxplots, Scatterplots, Correlation Heatmap, Class Distribution,
Feature Relationships - all via interactive Plotly visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.preprocessing import (
    load_raw_dataset, get_missing_value_summary, get_summary_statistics,
    get_correlation_matrix, detect_outliers_iqr, clean_dataset, engineer_features,
)
from config import NUMERIC_COLUMNS, TARGET_COLUMN


@st.cache_data
def _load_cached_dataset():
    return load_raw_dataset()


def render():
    st.title("📊 Data Analysis")
    st.caption("Exploratory Data Analysis of the diabetes risk dataset")

    df = _load_cached_dataset()

    # --- Dataset Preview ---
    st.subheader("🔎 Dataset Preview")
    st.dataframe(df.head(20), use_container_width=True)

    # --- Dataset Information ---
    st.subheader("ℹ️ Dataset Information")
    info_col1, info_col2, info_col3 = st.columns(3)
    info_col1.metric("Total Rows", f"{len(df):,}")
    info_col2.metric("Total Columns", len(df.columns))
    info_col3.metric("Duplicate Rows", int(df.duplicated().sum()))

    with st.expander("Column Data Types"):
        dtype_df = pd.DataFrame({"Column": df.columns, "Data Type": df.dtypes.astype(str).values})
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    # --- Missing Values ---
    st.subheader("🕳️ Missing Values")
    missing_summary = get_missing_value_summary(df)
    if missing_summary.empty:
        st.success("No missing values detected in the raw dataset.")
    else:
        st.dataframe(missing_summary, use_container_width=True, hide_index=True)
        fig = px.bar(missing_summary, x="column", y="missing_percent",
                     title="Missing Value Percentage by Column", text="missing_percent")
        st.plotly_chart(fig, use_container_width=True)

    # --- Summary Statistics ---
    st.subheader("📐 Summary Statistics")
    st.dataframe(get_summary_statistics(df), use_container_width=True)

    # --- Outlier Detection ---
    st.subheader("🚨 Outlier Detection (IQR Method)")
    df_clean_preview = clean_dataset(df)
    outliers = detect_outliers_iqr(df)
    outlier_df = pd.DataFrame(outliers).T.reset_index().rename(columns={"index": "column"})
    st.dataframe(outlier_df, use_container_width=True, hide_index=True)

    st.divider()

    # --- Class Distribution ---
    st.subheader("⚖️ Class Distribution (Diabetes Outcome)")
    class_counts = df[TARGET_COLUMN].value_counts().rename({0: "Non-Diabetic", 1: "Diabetic"})
    fig_class = px.pie(
        names=class_counts.index, values=class_counts.values,
        title="Diabetic vs Non-Diabetic Distribution", hole=0.4,
        color=class_counts.index,
        color_discrete_map={"Non-Diabetic": "#2A9D8F", "Diabetic": "#E63946"},
    )
    st.plotly_chart(fig_class, use_container_width=True)

    st.divider()

    # --- Histograms ---
    st.subheader("📊 Histograms")
    hist_col = st.selectbox("Select a numeric feature for histogram", NUMERIC_COLUMNS, key="hist_select")
    fig_hist = px.histogram(df, x=hist_col, color=TARGET_COLUMN, marginal="box",
                             title=f"Distribution of {hist_col} by Diabetes Outcome",
                             barmode="overlay", opacity=0.7)
    st.plotly_chart(fig_hist, use_container_width=True)

    # --- Boxplots ---
    st.subheader("📦 Boxplots")
    box_col = st.selectbox("Select a numeric feature for boxplot", NUMERIC_COLUMNS, key="box_select")
    fig_box = px.box(df, x=TARGET_COLUMN, y=box_col, color=TARGET_COLUMN,
                      title=f"{box_col} by Diabetes Outcome",
                      labels={TARGET_COLUMN: "Diabetes (0=No, 1=Yes)"})
    st.plotly_chart(fig_box, use_container_width=True)

    # --- Scatterplots ---
    st.subheader("🔬 Scatterplots")
    sc_col1, sc_col2 = st.columns(2)
    with sc_col1:
        x_axis = st.selectbox("X-axis feature", NUMERIC_COLUMNS, index=0, key="scatter_x")
    with sc_col2:
        y_axis = st.selectbox("Y-axis feature", NUMERIC_COLUMNS, index=1, key="scatter_y")
    fig_scatter = px.scatter(df, x=x_axis, y=y_axis, color=TARGET_COLUMN,
                              title=f"{x_axis} vs {y_axis}", opacity=0.6,
                              labels={TARGET_COLUMN: "Diabetes"})
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    # --- Correlation Heatmap ---
    st.subheader("🌡️ Correlation Heatmap")
    df_engineered = engineer_features(df_clean_preview)
    corr_matrix = get_correlation_matrix(
        df_engineered[NUMERIC_COLUMNS + ["hypertension", "heart_disease", TARGET_COLUMN]]
    )
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.columns,
        colorscale="RdBu", zmid=0, text=corr_matrix.round(2).values, texttemplate="%{text}",
    ))
    fig_heatmap.update_layout(title="Feature Correlation Matrix", height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # --- Feature Relationships (gender / smoking vs outcome) ---
    st.subheader("🔗 Feature Relationships")
    rel_col1, rel_col2 = st.columns(2)
    with rel_col1:
        gender_rate = df.groupby("gender")[TARGET_COLUMN].mean().reset_index()
        fig_gender = px.bar(gender_rate, x="gender", y=TARGET_COLUMN,
                             title="Diabetes Rate by Gender", labels={TARGET_COLUMN: "Diabetes Rate"})
        st.plotly_chart(fig_gender, use_container_width=True)
    with rel_col2:
        smoke_rate = df.groupby("smoking_history")[TARGET_COLUMN].mean().reset_index()
        fig_smoke = px.bar(smoke_rate, x="smoking_history", y=TARGET_COLUMN,
                            title="Diabetes Rate by Smoking History", labels={TARGET_COLUMN: "Diabetes Rate"})
        st.plotly_chart(fig_smoke, use_container_width=True)
