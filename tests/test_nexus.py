import pytest
import pandas as pd
from pathlib import Path
from config.database import get_engine

engine = get_engine()

# =====================================================
# FIXTURES
# =====================================================

@pytest.fixture(scope="session")
def db():
    return get_engine()


# =====================================================
# DATABASE CONNECTION
# =====================================================

class TestDatabaseConnection:

    def test_engine_connects(self, db):
        with db.connect() as conn:
            result = conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            assert result.fetchone()[0] == 1


# =====================================================
# CORE TABLES HAVE DATA
# =====================================================

class TestCoreTablesHaveData:

    def test_customers_not_empty(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM customers", db)
        assert df.iloc[0]["n"] > 0, "customers table is empty"

    def test_products_not_empty(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM products", db)
        assert df.iloc[0]["n"] > 0, "products table is empty"

    def test_orders_not_empty(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM orders", db)
        assert df.iloc[0]["n"] > 0, "orders table is empty"

    def test_order_items_not_empty(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM order_items", db)
        assert df.iloc[0]["n"] > 0, "order_items table is empty"

    def test_inventory_not_empty(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM inventory", db)
        assert df.iloc[0]["n"] > 0, "inventory table is empty"


# =====================================================
# REFERENCE TABLES HAVE SEED DATA
# =====================================================

class TestSeedData:

    def test_regions_seeded(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM regions", db)
        assert df.iloc[0]["n"] == 5, "expected 5 regions"

    def test_customer_segments_seeded(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM customer_segments", db)
        assert df.iloc[0]["n"] == 5, "expected 5 customer segments"

    def test_product_categories_seeded(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM product_categories", db)
        assert df.iloc[0]["n"] == 5, "expected 5 product categories"

    def test_warehouses_seeded(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM warehouses", db)
        assert df.iloc[0]["n"] == 3, "expected 3 warehouses"


# =====================================================
# ANALYTICS TABLES HAVE DATA
# =====================================================

class TestAnalyticsTables:

    def test_kpi_snapshots_not_empty(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM kpi_snapshots", db)
        assert df.iloc[0]["n"] > 0, "kpi_snapshots is empty — run build_summary_tables.py"

    def test_monthly_revenue_not_empty(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM monthly_revenue_summary", db)
        assert df.iloc[0]["n"] > 0, "monthly_revenue_summary is empty — run build_summary_tables.py"

    def test_alerts_not_empty(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM alerts", db)
        assert df.iloc[0]["n"] > 0, "alerts table is empty — run build_summary_tables.py"

    def test_customer_health_not_empty(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM customer_health_metrics", db)
        assert df.iloc[0]["n"] > 0, "customer_health_metrics is empty — run build_summary_tables.py"


# =====================================================
# QUERY RETURN CORRECT COLUMNS
# =====================================================

class TestQueryColumns:

    def test_kpi_snapshot_columns(self, db):
        df = pd.read_sql("SELECT * FROM kpi_snapshots LIMIT 1", db)
        expected = {"total_revenue", "total_orders", "total_customers",
                    "avg_order_value", "gross_margin_pct", "return_rate_pct",
                    "nps_score", "retention_rate", "inventory_fill_pct"}
        assert expected.issubset(set(df.columns)), f"Missing columns: {expected - set(df.columns)}"

    def test_monthly_revenue_columns(self, db):
        df = pd.read_sql("SELECT * FROM monthly_revenue_summary LIMIT 1", db)
        expected = {"month", "region_id", "segment_id", "net_revenue", "target_revenue"}
        assert expected.issubset(set(df.columns)), f"Missing columns: {expected - set(df.columns)}"

    def test_products_has_sku_code(self, db):
        df = pd.read_sql("SELECT * FROM products LIMIT 1", db)
        assert "sku_code" in df.columns, "products table missing sku_code column"

    def test_customers_has_name_columns(self, db):
        df = pd.read_sql("SELECT * FROM customers LIMIT 1", db)
        assert "first_name" in df.columns, "customers table missing first_name"
        assert "last_name" in df.columns, "customers table missing last_name"

    def test_inventory_has_status(self, db):
        df = pd.read_sql("SELECT * FROM inventory LIMIT 1", db)
        assert "status" in df.columns, "inventory table missing status column"


# =====================================================
# DATA INTEGRITY
# =====================================================

class TestDataIntegrity:

    def test_no_null_order_amounts(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM orders WHERE net_amount IS NULL", db)
        assert df.iloc[0]["n"] == 0, "orders table has NULL net_amount values"

    def test_no_negative_order_amounts(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM orders WHERE net_amount < 0", db)
        assert df.iloc[0]["n"] == 0, "orders table has negative net_amount values"

    def test_no_null_product_names(self, db):
        df = pd.read_sql("SELECT COUNT(*) AS n FROM products WHERE product_name IS NULL", db)
        assert df.iloc[0]["n"] == 0, "products table has NULL product_name values"

    def test_all_orders_have_valid_customer(self, db):
        df = pd.read_sql("""
            SELECT COUNT(*) AS n FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """, db)
        assert df.iloc[0]["n"] == 0, "orders exist with no matching customer"

    def test_all_order_items_have_valid_order(self, db):
        df = pd.read_sql("""
            SELECT COUNT(*) AS n FROM order_items oi
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL
        """, db)
        assert df.iloc[0]["n"] == 0, "order_items exist with no matching order"

    def test_inventory_status_values_valid(self, db):
        df = pd.read_sql("""
            SELECT COUNT(*) AS n FROM inventory
            WHERE status NOT IN ('healthy', 'low', 'critical')
        """, db)
        assert df.iloc[0]["n"] == 0, "inventory has invalid status values"


# =====================================================
# REPORTS GENERATE FILES
# =====================================================

class TestReports:

    def test_excel_report_generates(self):
        from reports.excel_report import generate_excel_report
        path = generate_excel_report()
        assert Path(path).exists(), f"Excel report not found at {path}"
        assert Path(path).stat().st_size > 0, "Excel report is empty"

    def test_pdf_report_generates(self):
        from reports.pdf_report import generate_pdf_report
        path = generate_pdf_report()
        assert Path(path).exists(), f"PDF report not found at {path}"
        assert Path(path).stat().st_size > 0, "PDF report is empty"


# =====================================================
# ANALYTICS MODULES
# =====================================================

class TestAnalyticsModules:

    def test_ai_insights_returns_list(self, db):
        from analytics.ai_insights import generate_ai_insights
        insights = generate_ai_insights(db)
        assert isinstance(insights, list), "generate_ai_insights should return a list"
        assert len(insights) > 0, "generate_ai_insights returned empty list"
        assert all(isinstance(i, str) for i in insights), "all insights should be strings"

    def test_forecasting_returns_dataframes(self, db):
        from analytics.forecasting import get_forecast
        actual, forecast = get_forecast(db)
        assert isinstance(actual, pd.DataFrame), "actual should be a DataFrame"
        assert isinstance(forecast, pd.DataFrame), "forecast should be a DataFrame"
        assert not actual.empty, "actual DataFrame is empty"
        assert not forecast.empty, "forecast DataFrame is empty"
        assert "month" in forecast.columns, "forecast missing month column"
        assert "forecast" in forecast.columns, "forecast missing forecast column"