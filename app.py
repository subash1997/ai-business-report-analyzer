import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.analyzer import analyze_dataframe
from utils.insights import generate_insights, generate_narrative
from utils.report import generate_excel_report

st.set_page_config(page_title="AI BI Analyzer", layout="wide")

st.title("📊 AI Business Intelligence Analyzer")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    if df.empty:
        st.error("Uploaded file is empty")
        st.stop()

    analysis = analyze_dataframe(df)

    # =========================
    # 🎯 SIDEBAR FILTERS (NEW)
    # =========================
    st.sidebar.header("🔍 Filters")

    filtered_df = df.copy()

    # Date filter
    date_col = analysis.get("date_col")
    if date_col:
        filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors="coerce")

        min_date = filtered_df[date_col].min()
        max_date = filtered_df[date_col].max()

        date_range = st.sidebar.date_input(
            "Select Date Range",
            [min_date, max_date]
        )

        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df[date_col] >= pd.to_datetime(date_range[0])) &
                (filtered_df[date_col] <= pd.to_datetime(date_range[1]))
            ]

    # Category filter
    cat_cols = analysis.get("categorical_cols")
    if cat_cols:
        col = cat_cols[0]

        selected = st.sidebar.multiselect(
            f"Select {col}",
            options=filtered_df[col].dropna().unique()
        )

        if selected:
            filtered_df = filtered_df[filtered_df[col].isin(selected)]

    # =========================
    # 🔁 USE FILTERED DATA
    # =========================
    df = filtered_df

    insights = generate_insights(df, analysis)
    narrative = generate_narrative(insights)

    # =========================
    # KPIs
    # =========================
    st.subheader("📊 Business KPIs")

    rev_col = analysis.get("revenue_col")

    total_revenue = df[rev_col].sum() if rev_col else 0
    total_orders = len(df)
    avg_order = total_revenue / total_orders if total_orders else 0

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Revenue", round(total_revenue, 2))
    c2.metric("Total Orders", total_orders)
    c3.metric("Avg Order Value", round(avg_order, 2))

    # =========================
    # NARRATIVE
    # =========================
    st.subheader("🧠 AI Executive Narrative")
    st.info(narrative)

    # =========================
    # ALERTS
    # =========================
    st.subheader("🚨 Alerts")
    for a in insights["alerts"]:
        st.warning(a)

    # =========================
    # RECOMMENDATIONS
    # =========================
    st.subheader("⚡ Recommendations")
    for r in insights["recommendations"]:
        st.success(r)

    # =========================
    # PROFILE
    # =========================
    st.subheader("🔬 Column Diagnostics")
    st.dataframe(analysis["profile"], use_container_width=True)

    # =========================
    # BUSINESS CHARTS
    # =========================
    st.subheader("📈 Business Intelligence")

    # Revenue Trend
    if rev_col and date_col:
        trend = df.groupby(date_col)[rev_col].sum()

        st.write("📈 Revenue Trend")
        st.line_chart(trend)

    # Category
    if rev_col and cat_cols:
        col = cat_cols[0]
        top = df.groupby(col)[rev_col].sum().sort_values(ascending=False).head(10)

        st.write(f"🏆 Top {col}")
        st.bar_chart(top)

    # Distribution
    if rev_col:
        st.write("📊 Revenue Distribution")

        fig, ax = plt.subplots()
        df[rev_col].hist(ax=ax, bins=25)
        st.pyplot(fig)

    # =========================
    # ANOMALY DETECTION
    # =========================
    st.subheader("🚨 Anomaly Detection")

    if rev_col:
        mean = df[rev_col].mean()
        std = df[rev_col].std()

        upper = mean + 2 * std
        lower = mean - 2 * std

        anomalies = df[(df[rev_col] > upper) | (df[rev_col] < lower)]

        if not anomalies.empty:
            st.error(f"{len(anomalies)} anomalies detected")
            st.dataframe(anomalies.head(10))
        else:
            st.success("No anomalies detected")

    # =========================
    # DOWNLOAD
    # =========================
    st.subheader("📥 Download Report")

    file = generate_excel_report(df, analysis, insights)

    with open(file, "rb") as f:
        st.download_button(
            "Download Excel Report",
            f,
            file_name=file
        )