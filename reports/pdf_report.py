from pathlib import Path

import pandas as pd
from config.database import get_engine

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.styles import getSampleStyleSheet

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

EXPORT_FILE = "exports/executive_report.pdf"


# ==========================================
# GENERATE PDF REPORT
# ==========================================

def generate_pdf_report():

    doc = SimpleDocTemplate(EXPORT_FILE)

    styles = getSampleStyleSheet()

    elements = []

    # ======================================
    # TITLE
    # ======================================

    elements.append(
        Paragraph(
            "Nexus Intelligence Executive Report",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    # ======================================
    # KPI SECTION
    # ======================================

    kpi = pd.read_sql(
        """
        SELECT *
        FROM kpi_snapshots
        ORDER BY snapshot_date DESC
        LIMIT 1
        """,
        engine
    )

    if not kpi.empty:

        row = kpi.iloc[0]

        elements.append(
            Paragraph(
                "Executive KPI Summary",
                styles["Heading1"]
            )
        )

        elements.append(
            Paragraph(
                f"Total Revenue : ${row['total_revenue']:,.2f}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Total Orders : {row['total_orders']:,}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Total Customers : {row['total_customers']:,}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Average Order Value : ${row['avg_order_value']:,.2f}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Retention Rate : {row['retention_rate']}%",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"NPS Score : {row['nps_score']}",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 20))

    # ======================================
    # CUSTOMER HEALTH
    # ======================================

    health = pd.read_sql(
        """
        SELECT *
        FROM customer_health_metrics
        ORDER BY snapshot_date DESC
        LIMIT 1
        """,
        engine
    )

    if not health.empty:

        row = health.iloc[0]

        elements.append(
            Paragraph(
                "Customer Health Metrics",
                styles["Heading1"]
            )
        )

        elements.append(
            Paragraph(
                f"Retention Rate : {row['retention_rate']}%",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Repeat Purchase Rate : {row['repeat_purchase_rate']}%",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Satisfaction Score : {row['satisfaction_score']}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"NPS Score : {row['nps_score']}",
                styles["BodyText"]
            )
        )

    elements.append(PageBreak())

    # ======================================
    # INVENTORY HEALTH
    # ======================================

    inventory = pd.read_sql(
        """
        SELECT
            status,
            COUNT(*) total_products
        FROM inventory
        GROUP BY status
        """,
        engine
    )

    elements.append(
        Paragraph(
            "Inventory Health",
            styles["Heading1"]
        )
    )

    for _, row in inventory.iterrows():

        elements.append(
            Paragraph(
                f"{row['status']} : {row['total_products']} products",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 20))

    # ======================================
    # ALERTS
    # ======================================

    alerts = pd.read_sql(
        """
        SELECT
            alert_type,
            message
        FROM alerts
        ORDER BY created_at DESC
        LIMIT 10
        """,
        engine
    )

    elements.append(
        Paragraph(
            "Recent Alerts",
            styles["Heading1"]
        )
    )

    for _, row in alerts.iterrows():

        elements.append(
            Paragraph(
                f"[{row['alert_type'].upper()}] {row['message']}",
                styles["BodyText"]
            )
        )

    doc.build(elements)

    return EXPORT_FILE