# 🚀 Nexus Intelligence Platform

> Enterprise-grade Business Intelligence dashboard built with Python, MySQL, and Streamlit — featuring live KPI tracking, AI-powered revenue insights, multi-warehouse inventory control, and automated PDF/Excel reporting.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running the Dashboard](#running-the-dashboard)
- [Dashboard Pages](#dashboard-pages)
- [Generating Reports](#generating-reports)
- [Running Tests](#running-tests)
- [Architecture](#architecture)

---

## Overview

Nexus Intelligence Platform is a full-stack business intelligence tool that ingests transactional data (orders, customers, products, inventory) into a MySQL database, builds analytics summary tables, and surfaces insights through an 8-page interactive Streamlit dashboard.

**Key capabilities:**
- Live KPI metrics with delta indicators showing period-over-period change
- Sidebar filters for date range and region/warehouse on every page
- AI-generated revenue trend insights using scikit-learn LinearRegression
- Automated low-stock and revenue alerts
- 12-month revenue forecasting with actual vs projected chart
- One-click PDF and Excel executive report export
- 29-test pytest suite covering connection, data integrity, schema, and report generation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Database | MySQL 8+ |
| ORM / Queries | SQLAlchemy + PyMySQL |
| Data Processing | Pandas |
| Dashboard | Streamlit |
| Charts | Plotly Express |
| Machine Learning | scikit-learn |
| Fake Data | Faker |
| PDF Reports | ReportLab |
| Excel Reports | OpenPyXL |
| Testing | pytest |

---

## Project Structure

```
Nexus-Intelligence-Platform/
│
├── .env                          # Database credentials (never committed)
├── .gitignore
├── requirements.txt
├── setup.py                      # Editable install for module resolution
├── pytest.ini
│
├── config/
│   └── database.py               # get_engine() — single DB connection point
│
├── database/
│   ├── schema.sql                # All CREATE TABLE statements
│   └── master_data.sql           # Seed data: regions, segments, categories, warehouses
│
├── data_generation/
│   ├── generate_customers.py     # 500 fake customers
│   ├── generate_products.py      # 100 fake products with SKU codes
│   ├── generate_inventory.py     # Inventory records per product per warehouse
│   └── generate_orders.py        # 50,000 orders with line items and payments
│
├── analytics/
│   ├── build_summary_tables.py   # Builds all analytics tables from raw data
│   ├── kpi_queries.py            # SQL query constants
│   ├── ai_insights.py            # LinearRegression revenue trend insights
│   ├── alert_engine.py           # Low stock + revenue alert generation
│   └── forecasting.py            # 12-month revenue forecast engine
│
├── dashboard/
│   ├── app.py                    # Entry point — set_page_config lives here only
│   ├── queries.py                # Shared query functions
│   ├── charts.py                 # Shared chart helpers
│   └── pages/
│       ├── 1_executive_dashboard.py
│       ├── 2_executive_insights.py
│       ├── 3_sales_analytics.py
│       ├── 4_customer_intelligence.py
│       ├── 5_inventory_control.py
│       ├── 6_forecasting.py
│       ├── 7_excel_report.py
│       └── 8_pdf_report.py
│
├── reports/
│   ├── excel_report.py           # Generates exports/executive_report.xlsx
│   └── pdf_report.py             # Generates exports/executive_report.pdf
│
├── exports/                      # Auto-created — generated reports saved here
│
└── tests/
    ├── system_check.py           # File existence + report generation check
    └── test_nexus.py             # 29-test pytest suite
```

---

## Prerequisites

- Python 3.10+
- MySQL 8.0+ running locally
- MySQL command line client
- Git

---

## Setup

### 1. Clone and enter the project

```bash
git clone https://github.com/yourname/nexus-intelligence-platform.git
cd nexus-intelligence-platform
```

### 2. Create and activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=nexus_intelligence
```

> ⚠️ Never commit `.env` to version control. It is already listed in `.gitignore`.

### 5. Initialize the database

Open your MySQL command line client and run:

```sql
source /full/path/to/database/schema.sql
source /full/path/to/database/master_data.sql
```

### 6. Generate data

Run each script in this exact order — each depends on the previous:

```bash
python data_generation/generate_customers.py
python data_generation/generate_products.py
python data_generation/generate_inventory.py
python data_generation/generate_orders.py
```

> `generate_orders.py` generates 50,000 orders and will take 2–4 minutes.

### 7. Build analytics layer

```bash
python analytics/build_summary_tables.py
```

This populates `monthly_revenue_summary`, `kpi_snapshots`, `sales_activity_log`, `customer_health_metrics`, and `alerts`.

---

## Running the Dashboard

```bash
streamlit run dashboard/app.py
```

Opens at `http://localhost:8501`

---

## Dashboard Pages

| Page | Description |
|---|---|
| 🏠 Home | AI revenue insights powered by LinearRegression |
| 📊 Executive Dashboard | 8 KPI metrics with delta indicators, revenue trend, region/segment charts, top products, alerts |
| 🧠 Executive Insights | Strategic recommendations, payment mix, order status analysis |
| 📈 Sales Analytics | Monthly trend, revenue vs target, weekly activity heatmap, product performance |
| 👥 Customer Intelligence | Customer segmentation, top 20 customers by revenue, health metrics |
| 📦 Inventory Control | Per-warehouse stock health, critical/low stock alerts, reorder tracking |
| 🔮 Forecasting | Actual vs 12-month projected revenue chart |
| 📥 Excel Report | One-click download of multi-sheet Excel executive report |
| 📄 PDF Report | One-click download of formatted PDF executive report |

All pages with revenue data include a **date range picker** and **region filter** in the sidebar. The inventory page includes a **warehouse filter**.

---

## Generating Reports

Reports can be generated directly from the dashboard (pages 7 and 8), or from the command line:

```bash
python -c "from reports.excel_report import generate_excel_report; print(generate_excel_report())"
python -c "from reports.pdf_report import generate_pdf_report; print(generate_pdf_report())"
```

Output files are saved to the `exports/` directory.

---

## Running Tests

```bash
pytest
```

**29 tests across 7 categories:**

| Category | Tests |
|---|---|
| Database Connection | Engine connects successfully |
| Core Tables | customers, products, orders, order_items, inventory all populated |
| Seed Data | Correct counts for regions, segments, categories, warehouses |
| Analytics Tables | kpi_snapshots, monthly_revenue, alerts, customer_health populated |
| Query Columns | All tables have exact columns the dashboard expects |
| Data Integrity | No nulls, no negatives, no orphaned foreign keys, valid status values |
| Reports & Analytics | PDF/Excel files generate, AI insights returns strings, forecast returns DataFrames |

---

## Architecture

```
MySQL Database
      │
      ▼
data_generation/          — Faker-based scripts populate raw tables
      │
      ▼
analytics/                — build_summary_tables.py aggregates raw → analytics tables
      │
      ▼
dashboard/                — Streamlit reads analytics tables via cached SQLAlchemy queries
      │
      ▼
reports/                  — ReportLab + OpenPyXL export to exports/
```

**Design decisions:**
- All database credentials live exclusively in `.env` — no hardcoded strings anywhere
- `config/database.py` is the single source of `get_engine()` — imported by every file
- All dashboard queries use `@st.cache_data(ttl=300)` — pages load instantly after first visit
- Parameterized queries use SQLAlchemy `text()` + `engine.connect()` — safe from SQL injection
- `setup.py` + `pip install -e .` resolves all cross-package imports permanently

---

## License

MIT