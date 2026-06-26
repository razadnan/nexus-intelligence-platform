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
def load_customer_count():
    return pd.read_sql("SELECT COUNT(*) AS total_customers FROM customers", engine)

@st.cache_data(ttl=300)
def load_active_customers():
    return pd.read_sql("SELECT COUNT(DISTINCT customer_id) AS active_customers FROM orders", engine)

@st.cache_data(ttl=300)
def load_health():
    return pd.read_sql("SELECT * FROM customer_health_metrics ORDER BY snapshot_date DESC LIMIT 1", engine)

@st.cache_data(ttl=300)
def load_region_customers(region):
    with engine.connect() as conn:
        if region == "All":
            q = text("""
                SELECT r.region_name, COUNT(*) AS customer_count
                FROM customers c JOIN regions r ON c.region_id = r.region_id
                GROUP BY r.region_name ORDER BY customer_count DESC
            """)
            return pd.DataFrame(conn.execute(q).fetchall(), columns=["region_name", "customer_count"])
        else:
            q = text("""
                SELECT r.region_name, COUNT(*) AS customer_count
                FROM customers c JOIN regions r ON c.region_id = r.region_id
                WHERE r.region_name = :region
                GROUP BY r.region_name ORDER BY customer_count DESC
            """)
            return pd.DataFrame(conn.execute(q, {"region": region}).fetchall(), columns=["region_name", "customer_count"])

@st.cache_data(ttl=300)
def load_segment_customers(region):
    with engine.connect() as conn:
        if region == "All":
            q = text("""
                SELECT cs.segment_name, COUNT(*) AS customer_count
                FROM customers c JOIN customer_segments cs ON c.segment_id = cs.segment_id
                GROUP BY cs.segment_name ORDER BY customer_count DESC
            """)
            return pd.DataFrame(conn.execute(q).fetchall(), columns=["segment_name", "customer_count"])
        else:
            q = text("""
                SELECT cs.segment_name, COUNT(*) AS customer_count
                FROM customers c
                JOIN customer_segments cs ON c.segment_id = cs.segment_id
                JOIN regions r ON c.region_id = r.region_id
                WHERE r.region_name = :region
                GROUP BY cs.segment_name ORDER BY customer_count DESC
            """)
            return pd.DataFrame(conn.execute(q, {"region": region}).fetchall(), columns=["segment_name", "customer_count"])

@st.cache_data(ttl=300)
def load_top_customers(region):
    with engine.connect() as conn:
        if region == "All":
            q = text("""
                SELECT TRIM(CONCAT(c.first_name,' ',c.last_name)) AS customer_name,
                       ROUND(SUM(o.net_amount),2) AS revenue, COUNT(o.order_id) AS orders
                FROM orders o JOIN customers c ON o.customer_id = c.customer_id
                GROUP BY c.customer_id, customer_name ORDER BY revenue DESC LIMIT 20
            """)
            return pd.DataFrame(conn.execute(q).fetchall(), columns=["customer_name", "revenue", "orders"])
        else:
            q = text("""
                SELECT TRIM(CONCAT(c.first_name,' ',c.last_name)) AS customer_name,
                       ROUND(SUM(o.net_amount),2) AS revenue, COUNT(o.order_id) AS orders
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN regions r ON c.region_id = r.region_id
                WHERE r.region_name = :region
                GROUP BY c.customer_id, customer_name ORDER BY revenue DESC LIMIT 20
            """)
            return pd.DataFrame(conn.execute(q, {"region": region}).fetchall(), columns=["customer_name", "revenue", "orders"])

@st.cache_data(ttl=300)
def load_regions():
    return pd.read_sql("SELECT region_name FROM regions ORDER BY region_name", engine)

def get_metric(df, col, default="N/A"):
    if df is None or df.empty or col not in df.columns:
        return default
    val = df.at[0, col]
    return default if pd.isna(val) else val

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("🔎 Filters")

regions_df      = load_regions()
region_list     = ["All"] + regions_df["region_name"].tolist()
selected_region = st.sidebar.selectbox("Region", region_list)

# =====================================================
# PAGE TITLE
# =====================================================

st.title("👥 Customer Intelligence")

# =====================================================
# KPI ROW
# =====================================================

customer_count   = load_customer_count()
active_customers = load_active_customers()
health           = load_health()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Customers",   f"{customer_count.iloc[0]['total_customers']:,}" if not customer_count.empty else "0")
c2.metric("Active Customers",  f"{active_customers.iloc[0]['active_customers']:,}" if not active_customers.empty else "0")
c3.metric("Retention %",       f"{get_metric(health, 'retention_rate')}")
c4.metric("Repeat Purchase %", f"{get_metric(health, 'repeat_purchase_rate')}")
c5.metric("NPS",               f"{get_metric(health, 'nps_score')}")

st.divider()

# =====================================================
# FILTERED CHARTS
# =====================================================

region_df  = load_region_customers(selected_region)
segment_df = load_segment_customers(selected_region)

left, right = st.columns(2)
with left:
    if not region_df.empty:
        fig = px.bar(region_df, x="region_name", y="customer_count", title="Customers by Region")
        st.plotly_chart(fig, width='stretch')
with right:
    if not segment_df.empty:
        fig = px.pie(segment_df, names="segment_name", values="customer_count", hole=0.5, title="Customer Segments")
        st.plotly_chart(fig, width='stretch')

# =====================================================
# TOP 20 CUSTOMERS
# =====================================================

st.subheader("🏆 Top 20 Customers")
st.dataframe(load_top_customers(selected_region), width='stretch')

# =====================================================
# CUSTOMER HEALTH METRICS
# =====================================================

st.subheader("📊 Customer Health Metrics")

health_display = pd.DataFrame({
    "Metric": ["NPS Score", "Retention Rate", "Repeat Purchase Rate", "Satisfaction Score", "Support CSAT", "Lifetime Value Index"],
    "Value":  [
        get_metric(health, "nps_score"),
        get_metric(health, "retention_rate"),
        get_metric(health, "repeat_purchase_rate"),
        get_metric(health, "satisfaction_score"),
        get_metric(health, "support_csat"),
        get_metric(health, "lifetime_value_index")
    ]
})

st.dataframe(health_display, width='stretch')
