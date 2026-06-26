from pathlib import Path

import pandas as pd
from config.database import get_engine

# ==========================================
# DATABASE
# ==========================================

engine = get_engine()

# ==========================================
# EXPORT LOCATION
# ==========================================

Path("exports").mkdir(
    parents=True,
    exist_ok=True
)

EXPORT_FILE = "exports/executive_report.xlsx"


# ==========================================
# GENERATE EXCEL REPORT
# ==========================================

def generate_excel_report():

    with pd.ExcelWriter(
        EXPORT_FILE,
        engine="openpyxl"
    ) as writer:

        # Executive KPIs
        pd.read_sql(
            """
            SELECT
                snapshot_date,
                total_revenue,
                total_orders,
                total_customers,
                avg_order_value,
                gross_margin_pct,
                return_rate_pct,
                retention_rate,
                inventory_fill_pct,
                nps_score
            FROM kpi_snapshots
            ORDER BY snapshot_date DESC
            LIMIT 1
            """,
            engine
        ).to_excel(
            writer,
            sheet_name="Executive_KPIs",
            index=False
        )

        # Revenue Trend
        pd.read_sql(
            """
            SELECT
                month,
                SUM(net_revenue) revenue,
                SUM(target_revenue) target_revenue
            FROM monthly_revenue_summary
            GROUP BY month
            ORDER BY month
            """,
            engine
        ).to_excel(
            writer,
            sheet_name="Revenue_Trend",
            index=False
        )

        # Revenue by Region
        pd.read_sql(
            """
            SELECT
                r.region_name,
                ROUND(SUM(m.net_revenue),2) revenue
            FROM monthly_revenue_summary m
            JOIN regions r
                ON m.region_id = r.region_id
            GROUP BY r.region_name
            ORDER BY revenue DESC
            """,
            engine
        ).to_excel(
            writer,
            sheet_name="Revenue_By_Region",
            index=False
        )

        # Customer Health
        pd.read_sql(
            """
            SELECT *
            FROM customer_health_metrics
            ORDER BY snapshot_date DESC
            LIMIT 1
            """,
            engine
        ).to_excel(
            writer,
            sheet_name="Customer_Health",
            index=False
        )

        # Inventory Health
        pd.read_sql(
            """
            SELECT
                status,
                COUNT(*) product_count
            FROM inventory
            GROUP BY status
            """,
            engine
        ).to_excel(
            writer,
            sheet_name="Inventory_Health",
            index=False
        )

        # Alerts
        pd.read_sql(
            """
            SELECT
                alert_type,
                message,
                created_at
            FROM alerts
            ORDER BY created_at DESC
            """,
            engine
        ).to_excel(
            writer,
            sheet_name="Alerts",
            index=False
        )

    return EXPORT_FILE
