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
                SELECT m.month, SUM(m.net_revenue) AS revenue, SUM(m.target_revenue) AS target
                FROM monthly_revenue_summary m
                WHERE m.month BETWEEN :start AND :end
                GROUP BY m.month ORDER BY m.month
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date}).fetchall(),
                                columns=["month", "revenue", "target"])
        else:
            q = text("""
                SELECT m.month, SUM(m.net_revenue) AS revenue, SUM(m.target_revenue) AS target
                FROM monthly_revenue_summary m
                JOIN regions r ON m.region_id = r.region_id
                WHERE m.month BETWEEN :start AND :end AND r.region_name = :region
                GROUP BY m.month ORDER BY m.month
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date, "region": region}).fetchall(),
                                columns=["month", "revenue", "target"])

@st.cache_data(ttl=300)
def load_region(start_date, end_date, region):
    with engine.connect() as conn:
        if region == "All":
            q = text("""
                SELECT r.region_name, ROUND(SUM(m.net_revenue),2) AS revenue
                FROM monthly_revenue_summary m
                JOIN regions r ON m.region_id = r.region_id
                WHERE m.month BETWEEN :start AND :end
                GROUP BY r.region_name ORDER BY revenue DESC
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date}).fetchall(),
                                columns=["region_name", "revenue"])
        else:
            q = text("""
                SELECT r.region_name, ROUND(SUM(m.net_revenue),2) AS revenue
                FROM monthly_revenue_summary m
                JOIN regions r ON m.region_id = r.region_id
                WHERE m.month BETWEEN :start AND :end AND r.region_name = :region
                GROUP BY r.region_name ORDER BY revenue DESC
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date, "region": region}).fetchall(),
                                columns=["region_name", "revenue"])

@st.cache_data(ttl=300)
def load_segment(start_date, end_date, region):
    with engine.connect() as conn:
        if region == "All":
            q = text("""
                SELECT cs.segment_name, ROUND(SUM(m.net_revenue),2) AS revenue
                FROM monthly_revenue_summary m
                JOIN customer_segments cs ON m.segment_id = cs.segment_id
                WHERE m.month BETWEEN :start AND :end
                GROUP BY cs.segment_name ORDER BY revenue DESC
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date}).fetchall(),
                                columns=["segment_name", "revenue"])
        else:
            q = text("""
                SELECT cs.segment_name, ROUND(SUM(m.net_revenue),2) AS revenue
                FROM monthly_revenue_summary m
                JOIN customer_segments cs ON m.segment_id = cs.segment_id
                JOIN regions r ON m.region_id = r.region_id
                WHERE m.month BETWEEN :start AND :end AND r.region_name = :region
                GROUP BY cs.segment_name ORDER BY revenue DESC
            """)
            return pd.DataFrame(conn.execute(q, {"start": start_date, "end": end_date, "region": region}).fetchall(),
                                columns=["segment_name", "revenue"])

@st.cache_data(ttl=300)
def load_products():
    return pd.read_sql("""
        SELECT p.product_name, ROUND(SUM(oi.line_total),2) AS revenue, SUM(oi.quantity) AS units
        FROM order_items oi JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_name ORDER BY revenue DESC LIMIT 15
    """, engine)

@st.cache_data(ttl=300)
def load_order_status():
    return pd.read_sql("SELECT status, COUNT(*) AS total_orders FROM orders GROUP BY status", engine)

@st.cache_data(ttl=300)
def load_payments():
    return pd.read_sql("""
        SELECT payment_method, ROUND(SUM(amount),2) AS total_amount
        FROM payments GROUP BY payment_method ORDER BY total_amount DESC
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

st.title("🧠 Executive Insights Center")

# =====================================================
# KPI ROW WITH DELTAS
# =====================================================

kpi_df = load_kpi()

if kpi_df.empty:
    st.error("No KPI snapshot found. Run build_summary_tables.py first.")
    st.stop()

k      = kpi_df.iloc[0]
k_prev = kpi_df.iloc[1] if len(kpi_df) > 1 else None

def delta(col):
    if k_prev is None:
        return None
    return round(float(k[col]) - float(k_prev[col]), 2)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Revenue",         f"${k['total_revenue']:,.0f}",   delta=f"${delta('total_revenue'):,.0f}" if delta('total_revenue') is not None else None)
c2.metric("Orders",          f"{int(k['total_orders']):,}",   delta=f"{delta('total_orders'):,.0f}" if delta('total_orders') is not None else None)
c3.metric("Customers",       f"{int(k['total_customers']):,}", delta=f"{delta('total_customers'):,.0f}" if delta('total_customers') is not None else None)
c4.metric("Avg Order Value", f"${k['avg_order_value']:,.0f}", delta=f"${delta('avg_order_value'):,.2f}" if delta('avg_order_value') is not None else None)
c5.metric("NPS",             f"{k['nps_score']}")

st.divider()

# =====================================================
# FILTERED CHARTS
# =====================================================

monthly  = load_monthly(start_date, end_date, selected_region)
region   = load_region(start_date, end_date, selected_region)
segment  = load_segment(start_date, end_date, selected_region)
products = load_products()
status   = load_order_status()
payments = load_payments()

fig = px.line(monthly, x="month", y=["revenue", "target"], markers=True, title="Revenue vs Target")
st.plotly_chart(fig, width='stretch')

left, right = st.columns(2)
with left:
    fig = px.bar(region, x="region_name", y="revenue", title="Revenue by Region")
    st.plotly_chart(fig, width='stretch')
with right:
    fig = px.pie(segment, names="segment_name", values="revenue", hole=0.55, title="Revenue by Segment")
    st.plotly_chart(fig, width='stretch')

st.subheader("🏆 Top Performing Products")
fig = px.bar(products, x="revenue", y="product_name", orientation="h")
st.plotly_chart(fig, width='stretch')

left, right = st.columns(2)
with left:
    fig = px.pie(status, names="status", values="total_orders", title="Order Status Distribution")
    st.plotly_chart(fig, width='stretch')
with right:
    fig = px.bar(payments, x="payment_method", y="total_amount", title="Payment Mix")
    st.plotly_chart(fig, width='stretch')

# =====================================================
# EXECUTIVE RECOMMENDATIONS
# =====================================================

st.subheader("🎯 Executive Recommendations")

if not region.empty and not segment.empty and not products.empty:
    top_region  = region.iloc[0]["region_name"]
    top_segment = segment.iloc[0]["segment_name"]
    top_product = products.iloc[0]["product_name"]

    st.success(f"Highest Revenue Region: {top_region}")
    st.info(f"Highest Revenue Segment: {top_segment}")
    st.warning(f"Best Selling Product: {top_product}")

    st.subheader("📋 Strategic Summary")
    st.markdown(f"""
- Focus expansion in **{top_region}**
- Increase marketing budget for **{top_segment}**
- Ensure inventory availability for **{top_product}**
- Monitor revenue trend against target line
- Track NPS and retention metrics monthly
""")
