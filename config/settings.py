from pathlib import Path

# =====================================================
# APPLICATION
# =====================================================

APP_NAME    = "Nexus Intelligence Platform"
VERSION     = "1.0.0"
DESCRIPTION = "Enterprise Business Intelligence Dashboard"

# =====================================================
# PATHS
# =====================================================

BASE_DIR    = Path(__file__).resolve().parent.parent
EXPORT_DIR  = BASE_DIR / "exports"
LOG_DIR     = BASE_DIR / "logs"

# Auto-create directories if they don't exist
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# REPORT FILE NAMES
# =====================================================

PDF_REPORT_NAME   = "executive_report.pdf"
EXCEL_REPORT_NAME = "executive_report.xlsx"

PDF_REPORT_PATH   = EXPORT_DIR / PDF_REPORT_NAME
EXCEL_REPORT_PATH = EXPORT_DIR / EXCEL_REPORT_NAME

# =====================================================
# DASHBOARD
# =====================================================

DEFAULT_CHART_HEIGHT  = 400
DEFAULT_ROW_LIMIT     = 100
CACHE_TTL_SECONDS     = 300        # 5 minutes
FORECAST_MONTHS_AHEAD = 12
CONFIDENCE_INTERVAL   = 0.95       # 95% CI on forecasting

# =====================================================
# DATA GENERATION
# =====================================================

NUM_CUSTOMERS = 500
NUM_PRODUCTS  = 100
NUM_ORDERS    = 50_000

# =====================================================
# ALERT THRESHOLDS
# =====================================================

LOW_STOCK_THRESHOLD      = 20      # units
CRITICAL_STOCK_THRESHOLD = 10      # units
REVENUE_TARGET_MULTIPLIER = 1.10   # target = actual * 1.10

# =====================================================
# RFM
# =====================================================

RFM_SEGMENTS = {
    "🏆 Champions":           "High R, High F, High M — your best customers",
    "💛 Loyal Customers":     "Order regularly, solid spend",
    "🌱 Promising":           "Recent but infrequent — nurture them",
    "🔍 Potential Loyalists": "Decent spend, not yet frequent",
    "⚠️ At Risk":             "Used to buy often but haven't recently",
    "😴 Hibernating":         "High frequency in the past, now inactive",
    "❌ Lost":                "Low scores across all dimensions",
    "🔄 Needs Attention":     "Mixed signals — watch closely",
}
