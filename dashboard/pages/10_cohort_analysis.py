import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
from config.database import get_engine
from analytics.cohort_analysis import get_cohort_matrix

engine = get_engine()

# =====================================================
# CACHED DATA
# =====================================================

@st.cache_data(ttl=300)
def load_cohort():
    return get_cohort_matrix(engine)

# =====================================================
# PAGE TITLE
# =====================================================

st.title("🔁 Cohort Retention Analysis")

st.markdown("""
Each row is a **cohort** — the group of customers who placed their first order in that month.
Each column is **months since acquisition (period index)**.
The value is the **percentage of that cohort who placed at least one order** in that period.

- **Period 0** is always 100% (the acquisition month itself)
- Higher retention in later periods = stronger customer loyalty
""")

st.divider()

# =====================================================
# LOAD DATA
# =====================================================

cohort_matrix, cohort_sizes = load_cohort()

if cohort_matrix.empty:
    st.warning("No order data available for cohort analysis.")
    st.stop()

# =====================================================
# COHORT SIZE KPIs
# =====================================================

avg_cohort_size = int(cohort_sizes.mean())
largest_cohort  = int(cohort_sizes.max())
total_cohorts   = len(cohort_sizes)

avg_month1_retention = cohort_matrix[1].mean() if 1 in cohort_matrix.columns else 0
avg_month3_retention = cohort_matrix[3].mean() if 3 in cohort_matrix.columns else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Cohorts",        f"{total_cohorts}")
c2.metric("Avg Cohort Size",      f"{avg_cohort_size:,}")
c3.metric("Largest Cohort",       f"{largest_cohort:,}")
c4.metric("Avg Month-1 Retention",f"{avg_month1_retention:.1f}%")
c5.metric("Avg Month-3 Retention",f"{avg_month3_retention:.1f}%")

st.divider()

# =====================================================
# COHORT HEATMAP
# =====================================================

st.subheader("📊 Retention Heatmap")

# Round for display
heatmap_data = cohort_matrix.round(1).fillna(0)

fig = px.imshow(
    heatmap_data,
    text_auto=True,
    color_continuous_scale="Blues",
    aspect="auto",
    title="Customer Retention by Cohort (%)",
    labels=dict(x="Months Since First Order", y="Cohort Month", color="Retention %")
)

fig.update_xaxes(side="top")
fig.update_layout(
    height=max(400, len(cohort_matrix) * 28),
    coloraxis_colorbar=dict(title="Retention %")
)

st.plotly_chart(fig, width='stretch')

# =====================================================
# RETENTION CURVE — Average across all cohorts
# =====================================================

st.subheader("📈 Average Retention Curve")

avg_retention = cohort_matrix.mean().reset_index()
avg_retention.columns = ["Period", "Avg Retention (%)"]
avg_retention = avg_retention[avg_retention["Period"] <= 11]

fig = px.line(
    avg_retention,
    x="Period",
    y="Avg Retention (%)",
    markers=True,
    title="Average Retention Across All Cohorts",
    labels={"Period": "Months Since First Order"}
)

fig.update_traces(line=dict(color="#1f77b4", width=2))
fig.add_hline(y=avg_retention["Avg Retention (%)"].mean(), line_dash="dash",
              line_color="orange", annotation_text="Overall Average")

st.plotly_chart(fig, width='stretch')

# =====================================================
# COHORT SIZE BAR
# =====================================================

st.subheader("👥 Cohort Sizes — Customers Acquired per Month")

cohort_size_df = cohort_sizes.reset_index()
cohort_size_df.columns = ["Cohort Month", "Customers"]
cohort_size_df["Cohort Month"] = cohort_size_df["Cohort Month"].astype(str)

fig = px.bar(
    cohort_size_df,
    x="Cohort Month",
    y="Customers",
    title="New Customers Acquired per Cohort Month"
)

st.plotly_chart(fig, width='stretch')

# =====================================================
# RAW COHORT TABLE
# =====================================================

st.subheader("📋 Full Cohort Retention Table (%)")
st.dataframe(heatmap_data, width='stretch')

st.caption("Nexus Intelligence Platform • Cohort Retention Analysis")
