import streamlit as st
import pandas as pd
from sqlalchemy import text
from config.database import get_engine

engine = get_engine()

# =====================================================
# AVAILABLE TABLES
# =====================================================

TABLES = {
    "Orders":                   "orders",
    "Order Items":              "order_items",
    "Customers":                "customers",
    "Products":                 "products",
    "Inventory":                "inventory",
    "Payments":                 "payments",
    "Returns":                  "returns",
    "Warehouses":               "warehouses",
    "Regions":                  "regions",
    "Customer Segments":        "customer_segments",
    "Product Categories":       "product_categories",
    "Monthly Revenue Summary":  "monthly_revenue_summary",
    "KPI Snapshots":            "kpi_snapshots",
    "Sales Activity Log":       "sales_activity_log",
    "Customer Health Metrics":  "customer_health_metrics",
    "Alerts":                   "alerts",
}

# =====================================================
# PAGE TITLE
# =====================================================

st.title("🔎 Data Explorer")

st.markdown("Browse any table in the database, filter by search term, and download as CSV.")

st.divider()

# =====================================================
# CONTROLS
# =====================================================

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    selected_label = st.selectbox("Select Table", list(TABLES.keys()))

with col2:
    search_term = st.text_input("Search (filters all text columns)", placeholder="e.g. Mumbai, completed, SKU-...")

with col3:
    row_limit = st.selectbox("Row Limit", [100, 250, 500, 1000, 5000], index=0)

table_name = TABLES[selected_label]

# =====================================================
# LOAD TABLE
# =====================================================

@st.cache_data(ttl=60)
def load_table(table, limit):
    return pd.read_sql(f"SELECT * FROM {table} LIMIT {limit}", engine)

@st.cache_data(ttl=60)
def get_row_count(table):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        return result.fetchone()[0]

try:
    df          = load_table(table_name, row_limit)
    total_rows  = get_row_count(table_name)
except Exception as e:
    st.error(f"Could not load table `{table_name}`: {e}")
    st.stop()

# =====================================================
# APPLY SEARCH FILTER
# =====================================================

if search_term:
    str_cols = df.select_dtypes(include="object").columns
    if len(str_cols) > 0:
        mask = df[str_cols].apply(
            lambda col: col.astype(str).str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        df = df[mask]

# =====================================================
# TABLE INFO ROW
# =====================================================

info1, info2, info3 = st.columns(3)
info1.metric("Total Rows in Table", f"{total_rows:,}")
info2.metric("Showing",             f"{len(df):,}")
info3.metric("Columns",             f"{len(df.columns)}")

st.divider()

# =====================================================
# DATAFRAME DISPLAY
# =====================================================

st.dataframe(df, width='stretch', height=500)

# =====================================================
# DOWNLOAD BUTTON
# =====================================================

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label=f"⬇️ Download {selected_label} as CSV",
    data=csv,
    file_name=f"{table_name}.csv",
    mime="text/csv"
)

st.caption("Nexus Intelligence Platform • Data Explorer")
