import os

print("=" * 60)
print("NEXUS INTELLIGENCE PLATFORM")
print("SYSTEM VERIFICATION")
print("=" * 60)

# ==========================================
# REPORTS
# ==========================================

try:
    from reports.excel_report import generate_excel_report
    file = generate_excel_report()
    print("✅ Excel Report Generated")
    print(file)
except Exception as e:
    print("❌ Excel Report Failed")
    print(e)

print("-" * 60)

try:
    from reports.pdf_report import generate_pdf_report
    file = generate_pdf_report()
    print("✅ PDF Report Generated")
    print(file)
except Exception as e:
    print("❌ PDF Report Failed")
    print(e)

print("-" * 60)

# ==========================================
# DASHBOARD FILES
# ==========================================

dashboard_files = [
    "dashboard/app.py",
    "dashboard/pages/1_executive_dashboard.py",
    "dashboard/pages/2_executive_insights.py",
    "dashboard/pages/3_sales_analytics.py",
    "dashboard/pages/4_customer_intelligence.py",
    "dashboard/pages/5_inventory_control.py",
    "dashboard/pages/6_forecasting.py",
    "dashboard/excel_reports.py",
    "dashboard/pdf_reports.py",
]

for file in dashboard_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ Missing -> {file}")

print("-" * 60)

# ==========================================
# ANALYTICS FILES
# ==========================================

analytics_files = [
    "analytics/ai_insights.py",
    "analytics/alert_engine.py",
    "analytics/forecasting.py",
    "analytics/kpi_queries.py",
    "analytics/build_summary_tables.py",
]

for file in analytics_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ Missing -> {file}")

print("-" * 60)

# ==========================================
# CONFIG FILES
# ==========================================

config_files = [
    "config/database.py",
    ".env",
    "requirements.txt",
    "database/schema.sql",
    "database/master_data.sql",
]

for file in config_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ Missing -> {file}")

print("-" * 60)

# ==========================================
# EXPORTS
# ==========================================

if os.path.exists("exports/executive_report.xlsx"):
    print("✅ Excel Export Exists")
else:
    print("❌ Excel Export Missing")

if os.path.exists("exports/executive_report.pdf"):
    print("✅ PDF Export Exists")
else:
    print("❌ PDF Export Missing")

print("-" * 60)
print("Verification Completed")
