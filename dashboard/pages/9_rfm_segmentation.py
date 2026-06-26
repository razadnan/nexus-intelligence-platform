import streamlit as st
import pandas as pd
import plotly.express as px
from config.database import get_engine
from analytics.rfm_segmentation import get_rfm

engine = get_engine()

# =====================================================
# CACHED DATA
# =====================================================

@st.cache_data(ttl=300)
def load_rfm():
    return get_rfm(engine)

# =====================================================
# PAGE TITLE
# =====================================================

st.title("🎯 RFM Customer Segmentation")

st.markdown("""
**RFM** scores every customer on three dimensions:
- **Recency** — how recently they ordered (higher = more recent)
- **Frequency** — how many orders they placed (higher = more orders)
- **Monetary** — how much they spent in total (higher = more spend)

Each dimension is scored 1–5. Combined score ranges from 3 (worst) to 15 (best).
""")

st.divider()

# =====================================================
# LOAD DATA
# =====================================================

df = load_rfm()

if df.empty:
    st.warning("No order data available for RFM analysis.")
    st.stop()

# =====================================================
# SEGMENT SUMMARY KPIs
# =====================================================

segment_summary = (
    df.groupby("segment")
      .agg(
          customers  = ("customer_id",  "count"),
          avg_spend  = ("monetary",     "mean"),
          avg_orders = ("frequency",    "mean"),
          avg_recency= ("recency_days", "mean")
      )
      .round(1)
      .reset_index()
      .sort_values("customers", ascending=False)
)

total_customers = len(df)
champions       = len(df[df["segment"] == "🏆 Champions"])
at_risk         = len(df[df["segment"] == "⚠️ At Risk"])
lost            = len(df[df["segment"] == "❌ Lost"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Customers",  f"{total_customers:,}")
c2.metric("🏆 Champions",     f"{champions:,}")
c3.metric("⚠️ At Risk",       f"{at_risk:,}")
c4.metric("❌ Lost",           f"{lost:,}")

st.divider()

# =====================================================
# SEGMENT DISTRIBUTION CHARTS
# =====================================================

left, right = st.columns(2)

with left:
    fig = px.pie(
        segment_summary,
        names="segment",
        values="customers",
        hole=0.5,
        title="Customer Distribution by Segment"
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, width='stretch')

with right:
    fig = px.bar(
        segment_summary.sort_values("avg_spend", ascending=True),
        x="avg_spend",
        y="segment",
        orientation="h",
        title="Average Spend by Segment ($)",
        color="avg_spend",
        color_continuous_scale="Blues"
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width='stretch')

# =====================================================
# SEGMENT DETAIL TABLE
# =====================================================

st.subheader("📊 Segment Summary")

segment_display = segment_summary.copy()
segment_display.columns = ["Segment", "Customers", "Avg Spend ($)", "Avg Orders", "Avg Recency (days)"]
st.dataframe(segment_display, width='stretch')

st.divider()

# =====================================================
# RFM SCATTER — Recency vs Monetary coloured by segment
# =====================================================

st.subheader("🔍 RFM Distribution — Recency vs Spend")

fig = px.scatter(
    df,
    x="recency_days",
    y="monetary",
    color="segment",
    size="frequency",
    hover_data=["customer_name", "rfm_score", "r_score", "f_score", "m_score"],
    title="Recency vs Monetary Value (bubble size = order frequency)",
    labels={"recency_days": "Recency (days since last order)", "monetary": "Total Spend ($)"}
)
st.plotly_chart(fig, width='stretch')

# =====================================================
# SIDEBAR FILTER — VIEW BY SEGMENT
# =====================================================

st.divider()
st.subheader("👤 Customer Detail by Segment")

segments      = ["All"] + sorted(df["segment"].unique().tolist())
sel_segment   = st.selectbox("Filter by Segment", segments)

filtered = df if sel_segment == "All" else df[df["segment"] == sel_segment]

display = filtered[[
    "customer_name", "recency_days", "frequency",
    "monetary", "r_score", "f_score", "m_score", "rfm_score", "segment"
]].copy()

display.columns = [
    "Customer", "Recency (days)", "Orders",
    "Total Spend ($)", "R Score", "F Score", "M Score", "RFM Score", "Segment"
]

st.dataframe(display, width='stretch')

st.caption("Nexus Intelligence Platform • RFM Customer Segmentation")
