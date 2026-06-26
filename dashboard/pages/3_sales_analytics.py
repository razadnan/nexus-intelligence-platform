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
def load_kpi():
    return pd.read_sql("SELECT * FROM kpi_snapshots ORDER BY snapshot_date DESC LIMIT 2", engine)

@st.cache_data(ttl=300)
def load_monthly(start_date, end_date, region):
    with engine.connect() as conn:
        if region == "All":
            q = text("""
                SELECT m.month, SUM(m.net_revenue) AS revenue, SUM(m.target_revenue) AS target_revenue
                FROM monthly_revenue_summary m
                WHERE m.month BETWEEN :start AND :end
                GROUP BY m.month ORDER BY m.month
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date}).fetchall(),
                                columns=["month", "revenue", "target_revenue"])
        else:
            q = text("""
                SELECT m.month, SUM(m.net_revenue) AS revenue, SUM(m.target_revenue) AS target_revenue
                FROM monthly_revenue_summary m
                JOIN regions r ON m.region_id = r.region_id
                WHERE m.month BETWEEN :start AND :end AND r.region_name = :region
                GROUP BY m.month ORDER BY m.month
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date, "region": region}).fetchall(),
                                columns=["month", "revenue", "target_revenue"])

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
        SELECT p.product_name, ROUND(SUM(oi.line_total),2) AS revenue, SUM(oi.quantity) AS units_sold
        FROM order_items oi JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_id, p.product_name ORDER BY revenue DESC LIMIT 15
    """, engine)

@st.cache_data(ttl=300)
def load_order_status():
    return pd.read_sql("SELECT status, COUNT(*) AS total_orders FROM orders GROUP BY status ORDER BY total_orders DESC", engine)

@st.cache_data(ttl=300)
def load_payment_methods():
    return pd.read_sql("""
        SELECT payment_method, COUNT(*) AS payments, ROUND(SUM(amount),2) AS amount
        FROM payments GROUP BY payment_method ORDER BY amount DESC
    """, engine)

@st.cache_data(ttl=300)
def load_sales_activity():
    return pd.read_sql("""
        SELECT day_of_week, SUM(order_count) AS orders, ROUND(SUM(revenue),2) AS revenue
        FROM sales_activity_log GROUP BY day_of_week
        ORDER BY FIELD(day_of_week,'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
    """, engine)

@st.cache_data(ttl=300)
def load_regions():
    return pd.read_sql("SELECT region_name FROM regions ORDER BY region_name", engine)

@st.cache_data(ttl=300)
def load_date_bounds():
    return pd.read_sql("SELECT MIN(month) AS mn, MAX(month) AS mx FROM monthly_revenue_summary", engine)

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("🔎 Filters")

bounds   = load_date_bounds()
min_date = pd.to_datetime(bounds.iloc[0]["mn"]).date()
max_date = pd.to_datetime(bounds.iloc[0]["mx"]).date()

date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
start_date = str(date_range[0]) if len(date_range) > 0 else str(min_date)
end_date   = str(date_range[1]) if len(date_range) > 1 else str(max_date)

regions_df      = load_regions()
region_list     = ["All"] + regions_df["region_name"].tolist()
selected_region = st.sidebar.selectbox("Region", region_list)

# =====================================================
# PAGE TITLE
# =====================================================

st.title("📈 Sales Analytics Dashboard")

# =====================================================
# KPI ROW WITH DELTAS
# =====================================================

kpi_df = load_kpi()

if kpi_df.empty:
    st.error("No KPI data found.")
    st.stop()

kpi      = kpi_df.iloc[0]
kpi_prev = kpi_df.iloc[1] if len(kpi_df) > 1 else None

def delta(col):
    if kpi_prev is None:
        return None
    return round(float(kpi[col]) - float(kpi_prev[col]), 2)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Revenue",     f"${kpi['total_revenue']:,.0f}",    delta=f"${delta('total_revenue'):,.0f}" if delta('total_revenue') is not None else None)
c2.metric("Orders",      f"{int(kpi['total_orders']):,}",    delta=f"{delta('total_orders'):,.0f}" if delta('total_orders') is not None else None)
c3.metric("Customers",   f"{int(kpi['total_customers']):,}", delta=f"{delta('total_customers'):,.0f}" if delta('total_customers') is not None else None)
c4.metric("Avg Order",   f"${kpi['avg_order_value']:,.0f}",  delta=f"${delta('avg_order_value'):,.2f}" if delta('avg_order_value') is not None else None)
c5.metric("Return Rate", f"{kpi['return_rate_pct']}%",       delta=f"{delta('return_rate_pct')}%" if delta('return_rate_pct') is not None else None, delta_color="inverse")

st.divider()

# =====================================================
# FILTERED CHARTS
# =====================================================

monthly         = load_monthly(start_date, end_date, selected_region)
region_revenue  = load_region_revenue(start_date, end_date, selected_region)
segment_revenue = load_segment_revenue(start_date, end_date, selected_region)

left, right = st.columns(2)
with left:
    fig = px.line(monthly, x="month", y="revenue", markers=True, title="Monthly Revenue Trend")
    st.plotly_chart(fig, width='stretch')
with right:
    comparison = monthly.melt(id_vars=["month"], value_vars=["revenue", "target_revenue"], var_name="metric", value_name="value")
    fig = px.line(comparison, x="month", y="value", color="metric", markers=True, title="Revenue vs Target")
    st.plotly_chart(fig, width='stretch')

left, right = st.columns(2)
with left:
    fig = px.bar(region_revenue, x="region_name", y="revenue", title="Revenue by Region")
    st.plotly_chart(fig, width='stretch')
with right:
    fig = px.pie(segment_revenue, names="segment_name", values="revenue", hole=0.55, title="Revenue by Customer Segment")
    st.plotly_chart(fig, width='stretch')

# =====================================================
# TOP PRODUCTS
# =====================================================

top_products = load_top_products()
st.subheader("🏆 Top Revenue Products")
fig = px.bar(top_products, x="revenue", y="product_name", orientation="h")
st.plotly_chart(fig, width='stretch')

# =====================================================
# ORDER STATUS & PAYMENTS
# =====================================================

left, right = st.columns(2)
with left:
    fig = px.pie(load_order_status(), names="status", values="total_orders", title="Order Status Distribution")
    st.plotly_chart(fig, width='stretch')
with right:
    fig = px.bar(load_payment_methods(), x="payment_method", y="amount", title="Payment Method Revenue")
    st.plotly_chart(fig, width='stretch')

# =====================================================
# WEEKLY ACTIVITY & PRODUCT TABLE
# =====================================================

st.subheader("📅 Weekly Sales Activity")
fig = px.bar(load_sales_activity(), x="day_of_week", y="revenue")
st.plotly_chart(fig, width='stretch')

st.subheader("📦 Product Performance")
st.dataframe(top_products, width='stretch')

st.caption("Nexus Intelligence Platform • Sales Analytics")
