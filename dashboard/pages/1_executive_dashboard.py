import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from config.database import get_engine

engine = get_engine()

# =====================================================
# CACHED QUERY FUNCTIONS
# =====================================================

@st.cache_data(ttl=300)
def load_kpi_snapshots():
    return pd.read_sql("SELECT * FROM kpi_snapshots ORDER BY snapshot_date DESC LIMIT 2", engine)

@st.cache_data(ttl=300)
def load_monthly_revenue():
    return pd.read_sql("""
        SELECT month, SUM(net_revenue) AS revenue, SUM(target_revenue) AS target_revenue
        FROM monthly_revenue_summary GROUP BY month ORDER BY month
    """, engine)

@st.cache_data(ttl=300)
def load_region_revenue(start_date, end_date, region):
    with engine.connect() as conn:
        if region == "All":
            q = text("""
                SELECT r.region_name, SUM(m.net_revenue) AS revenue
                FROM monthly_revenue_summary m
                JOIN regions r ON m.region_id = r.region_id
                WHERE m.month BETWEEN :start AND :end
                GROUP BY r.region_name ORDER BY revenue DESC
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date}).fetchall(),
                                columns=["region_name", "revenue"])
        else:
            q = text("""
                SELECT r.region_name, SUM(m.net_revenue) AS revenue
                FROM monthly_revenue_summary m
                JOIN regions r ON m.region_id = r.region_id
                WHERE m.month BETWEEN :start AND :end AND r.region_name = :region
                GROUP BY r.region_name ORDER BY revenue DESC
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date, "region": region}).fetchall(),
                                columns=["region_name", "revenue"])

@st.cache_data(ttl=300)
def load_segment_revenue(start_date, end_date, region):
    with engine.connect() as conn:
        if region == "All":
            q = text("""
                SELECT cs.segment_name, SUM(m.net_revenue) AS revenue
                FROM monthly_revenue_summary m
                JOIN customer_segments cs ON m.segment_id = cs.segment_id
                WHERE m.month BETWEEN :start AND :end
                GROUP BY cs.segment_name ORDER BY revenue DESC
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date}).fetchall(),
                                columns=["segment_name", "revenue"])
        else:
            q = text("""
                SELECT cs.segment_name, SUM(m.net_revenue) AS revenue
                FROM monthly_revenue_summary m
                JOIN customer_segments cs ON m.segment_id = cs.segment_id
                JOIN regions r ON m.region_id = r.region_id
                WHERE m.month BETWEEN :start AND :end AND r.region_name = :region
                GROUP BY cs.segment_name ORDER BY revenue DESC
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date, "region": region}).fetchall(),
                                columns=["segment_name", "revenue"])

@st.cache_data(ttl=300)
def load_top_products():
    return pd.read_sql("""
        SELECT p.product_name, ROUND(SUM(oi.line_total),2) AS revenue, SUM(oi.quantity) AS units
        FROM order_items oi JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_id, p.product_name ORDER BY revenue DESC LIMIT 10
    """, engine)

@st.cache_data(ttl=300)
def load_alerts():
    return pd.read_sql("""
        SELECT alert_type, message, created_at FROM alerts ORDER BY created_at DESC LIMIT 10
    """, engine)

@st.cache_data(ttl=300)
def load_regions():
    return pd.read_sql("SELECT region_name FROM regions ORDER BY region_name", engine)

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("🔎 Filters")

monthly_all = load_monthly_revenue()
if not monthly_all.empty:
    min_date = pd.to_datetime(monthly_all["month"]).min().date()
    max_date = pd.to_datetime(monthly_all["month"]).max().date()
else:
    from datetime import date
    min_date = date(2023, 1, 1)
    max_date = date.today()

date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
start_date = str(date_range[0]) if len(date_range) > 0 else str(min_date)
end_date   = str(date_range[1]) if len(date_range) > 1 else str(max_date)

regions_df      = load_regions()
region_list     = ["All"] + regions_df["region_name"].tolist()
selected_region = st.sidebar.selectbox("Region", region_list)

# =====================================================
# PAGE TITLE
# =====================================================

st.title("📊 Nexus Executive Dashboard")

# =====================================================
# KPI ROW WITH DELTAS
# =====================================================

kpi_df = load_kpi_snapshots()

if kpi_df.empty:
    st.error("No KPI snapshot found. Run build_summary_tables.py first.")
    st.stop()

kpi      = kpi_df.iloc[0]
kpi_prev = kpi_df.iloc[1] if len(kpi_df) > 1 else None

def delta(col):
    if kpi_prev is None:
        return None
    return round(float(kpi[col]) - float(kpi_prev[col]), 2)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue",         f"${kpi['total_revenue']:,.0f}",      delta=f"${delta('total_revenue'):,.0f}" if delta('total_revenue') is not None else None)
c2.metric("Orders",          f"{int(kpi['total_orders']):,}",       delta=f"{delta('total_orders'):,.0f}" if delta('total_orders') is not None else None)
c3.metric("Customers",       f"{int(kpi['total_customers']):,}",    delta=f"{delta('total_customers'):,.0f}" if delta('total_customers') is not None else None)
c4.metric("Avg Order Value", f"${kpi['avg_order_value']:,.0f}",     delta=f"${delta('avg_order_value'):,.2f}" if delta('avg_order_value') is not None else None)

c5, c6, c7, c8 = st.columns(4)
c5.metric("Gross Margin %",   f"{kpi['gross_margin_pct']}%",  delta=f"{delta('gross_margin_pct')}%" if delta('gross_margin_pct') is not None else None)
c6.metric("Retention %",      f"{kpi['retention_rate']}%",    delta=f"{delta('retention_rate')}%" if delta('retention_rate') is not None else None)
c7.metric("Return Rate %",    f"{kpi['return_rate_pct']}%",   delta=f"{delta('return_rate_pct')}%" if delta('return_rate_pct') is not None else None, delta_color="inverse")
c8.metric("Inventory Fill %", f"{kpi['inventory_fill_pct']}%",delta=f"{delta('inventory_fill_pct')}%" if delta('inventory_fill_pct') is not None else None)

st.divider()

# =====================================================
# MONTHLY REVENUE
# =====================================================

left, right = st.columns(2)

with left:
    fig = px.line(monthly_all, x="month", y="revenue", markers=True, title="Revenue Trend")
    st.plotly_chart(fig, width='stretch')

with right:
    comparison = monthly_all.melt(id_vars=["month"], value_vars=["revenue", "target_revenue"], var_name="metric", value_name="value")
    fig = px.line(comparison, x="month", y="value", color="metric", markers=True, title="Revenue vs Target")
    st.plotly_chart(fig, width='stretch')

# =====================================================
# REGION & SEGMENT (FILTERED)
# =====================================================

region_revenue  = load_region_revenue(start_date, end_date, selected_region)
segment_revenue = load_segment_revenue(start_date, end_date, selected_region)

left, right = st.columns(2)

with left:
    fig = px.bar(region_revenue, x="region_name", y="revenue", title="Revenue by Region")
    st.plotly_chart(fig, width='stretch')

with right:
    fig = px.pie(segment_revenue, names="segment_name", values="revenue", hole=0.5, title="Revenue by Segment")
    st.plotly_chart(fig, width='stretch')

# =====================================================
# TOP PRODUCTS & ALERTS
# =====================================================

st.subheader("🏆 Top Products")
st.dataframe(load_top_products(), width='stretch')

st.subheader("🚨 Executive Alerts")
st.dataframe(load_alerts(), width='stretch')

st.caption("Nexus Intelligence Platform • Executive Dashboard")
