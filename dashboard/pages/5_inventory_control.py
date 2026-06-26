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
def load_inventory_overview(warehouse):
    with engine.connect() as conn:
        if warehouse == "All":
            q = text("""
                SELECT COUNT(*) AS total_items,
                       SUM(CASE WHEN status='healthy'  THEN 1 ELSE 0 END) AS healthy_items,
                       SUM(CASE WHEN status='low'      THEN 1 ELSE 0 END) AS low_items,
                       SUM(CASE WHEN status='critical' THEN 1 ELSE 0 END) AS critical_items
                FROM inventory
            """)
            return pd.DataFrame(conn.execute(q).fetchall(),
                                columns=["total_items", "healthy_items", "low_items", "critical_items"])
        else:
            q = text("""
                SELECT COUNT(*) AS total_items,
                       SUM(CASE WHEN i.status='healthy'  THEN 1 ELSE 0 END) AS healthy_items,
                       SUM(CASE WHEN i.status='low'      THEN 1 ELSE 0 END) AS low_items,
                       SUM(CASE WHEN i.status='critical' THEN 1 ELSE 0 END) AS critical_items
                FROM inventory i JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                WHERE w.warehouse_name = :warehouse
            """)
            return pd.DataFrame(conn.execute(q, {"warehouse": warehouse}).fetchall(),
                                columns=["total_items", "healthy_items", "low_items", "critical_items"])

@st.cache_data(ttl=300)
def load_inventory_health(warehouse):
    with engine.connect() as conn:
        if warehouse == "All":
            q = text("SELECT status, COUNT(*) AS product_count FROM inventory GROUP BY status ORDER BY product_count DESC")
            return pd.DataFrame(conn.execute(q).fetchall(), columns=["status", "product_count"])
        else:
            q = text("""
                SELECT i.status, COUNT(*) AS product_count
                FROM inventory i JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                WHERE w.warehouse_name = :warehouse
                GROUP BY i.status ORDER BY product_count DESC
            """)
            return pd.DataFrame(conn.execute(q, {"warehouse": warehouse}).fetchall(), columns=["status", "product_count"])

@st.cache_data(ttl=300)
def load_warehouse_stock():
    return pd.read_sql("""
        SELECT w.warehouse_name, COUNT(*) AS products, SUM(i.quantity_on_hand) AS total_stock
        FROM inventory i JOIN warehouses w ON i.warehouse_id = w.warehouse_id
        GROUP BY w.warehouse_name ORDER BY total_stock DESC
    """, engine)

@st.cache_data(ttl=300)
def load_critical_stock(warehouse):
    with engine.connect() as conn:
        if warehouse == "All":
            q = text("""
                SELECT p.product_name, p.sku_code, w.warehouse_name, i.quantity_on_hand, i.reorder_level
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                WHERE i.status = 'critical' ORDER BY i.quantity_on_hand ASC LIMIT 25
            """)
            return pd.DataFrame(conn.execute(q).fetchall(),
                                columns=["product_name", "sku_code", "warehouse_name", "quantity_on_hand", "reorder_level"])
        else:
            q = text("""
                SELECT p.product_name, p.sku_code, w.warehouse_name, i.quantity_on_hand, i.reorder_level
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                WHERE i.status = 'critical' AND w.warehouse_name = :warehouse
                ORDER BY i.quantity_on_hand ASC LIMIT 25
            """)
            return pd.DataFrame(conn.execute(q, {"warehouse": warehouse}).fetchall(),
                                columns=["product_name", "sku_code", "warehouse_name", "quantity_on_hand", "reorder_level"])

@st.cache_data(ttl=300)
def load_low_stock(warehouse):
    with engine.connect() as conn:
        if warehouse == "All":
            q = text("""
                SELECT p.product_name, p.sku_code, w.warehouse_name, i.quantity_on_hand, i.reorder_level
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                WHERE i.status = 'low' ORDER BY i.quantity_on_hand ASC LIMIT 25
            """)
            return pd.DataFrame(conn.execute(q).fetchall(),
                                columns=["product_name", "sku_code", "warehouse_name", "quantity_on_hand", "reorder_level"])
        else:
            q = text("""
                SELECT p.product_name, p.sku_code, w.warehouse_name, i.quantity_on_hand, i.reorder_level
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                WHERE i.status = 'low' AND w.warehouse_name = :warehouse
                ORDER BY i.quantity_on_hand ASC LIMIT 25
            """)
            return pd.DataFrame(conn.execute(q, {"warehouse": warehouse}).fetchall(),
                                columns=["product_name", "sku_code", "warehouse_name", "quantity_on_hand", "reorder_level"])

@st.cache_data(ttl=300)
def load_warehouse_summary():
    return pd.read_sql("""
        SELECT w.warehouse_name, COUNT(*) AS products,
               SUM(i.quantity_on_hand) AS total_stock, ROUND(AVG(i.quantity_on_hand),2) AS avg_stock
        FROM inventory i JOIN warehouses w ON i.warehouse_id = w.warehouse_id
        GROUP BY w.warehouse_name ORDER BY total_stock DESC
    """, engine)

@st.cache_data(ttl=300)
def load_warehouses():
    return pd.read_sql("SELECT warehouse_name FROM warehouses ORDER BY warehouse_name", engine)

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("🔎 Filters")

warehouses_df      = load_warehouses()
warehouse_list     = ["All"] + warehouses_df["warehouse_name"].tolist()
selected_warehouse = st.sidebar.selectbox("Warehouse", warehouse_list)

# =====================================================
# PAGE TITLE
# =====================================================

st.title("📦 Inventory Control Tower")

# =====================================================
# KPI ROW
# =====================================================

try:
    overview = load_inventory_overview(selected_warehouse)
    kpi      = overview.iloc[0]
except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Inventory Records", f"{int(kpi['total_items']):,}")
col2.metric("Healthy",           f"{int(kpi['healthy_items']):,}")
col3.metric("Low Stock",         f"{int(kpi['low_items']):,}")
col4.metric("Critical",          f"{int(kpi['critical_items']):,}")

st.divider()

# =====================================================
# CHARTS
# =====================================================

left, right = st.columns(2)
with left:
    fig = px.pie(load_inventory_health(selected_warehouse), names="status", values="product_count",
                 hole=0.55, title="Inventory Health Distribution")
    st.plotly_chart(fig, width='stretch')
with right:
    fig = px.bar(load_warehouse_stock(), x="warehouse_name", y="total_stock", title="Warehouse Stock Distribution")
    st.plotly_chart(fig, width='stretch')

# =====================================================
# STOCK TABLES
# =====================================================

st.subheader("🚨 Critical Stock Alerts")
st.dataframe(load_critical_stock(selected_warehouse), width='stretch')

st.subheader("⚠️ Low Stock Products")
st.dataframe(load_low_stock(selected_warehouse), width='stretch')

st.subheader("🏭 Warehouse Inventory Summary")
st.dataframe(load_warehouse_summary(), width='stretch')

st.caption("Nexus Intelligence Platform • Inventory Control Tower")
