"""
database/seed.py
────────────────
Single entry point to set up the entire Nexus Intelligence Platform
database from scratch.

Usage:
    python database/seed.py                  # full setup
    python database/seed.py --skip-schema    # skip schema/master_data (tables exist)
    python database/seed.py --analytics-only # only rebuild analytics tables
"""

import argparse
import sys
import os
from pathlib import Path

# ── Make sure project root is on the path ────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.logger import get_logger
from config.database import get_engine

logger = get_logger("seed")
engine = get_engine()

BASE_DIR = Path(__file__).resolve().parent.parent


# =====================================================
# HELPERS
# =====================================================

def run_sql_file(filepath: Path):
    """Execute a .sql file statement by statement."""
    logger.info(f"Running {filepath.name} ...")
    sql = filepath.read_text(encoding="utf-8")

    # Split on semicolons, skip empty statements
    statements = [s.strip() for s in sql.split(";") if s.strip()]

    with engine.begin() as conn:
        for statement in statements:
            try:
                conn.exec_driver_sql(statement)
            except Exception as e:
                # USE nexus_intelligence and IF NOT EXISTS are safe to skip
                if "1007" in str(e) or "1050" in str(e):
                    continue
                logger.warning(f"Skipped: {str(e)[:120]}")

    logger.info(f"{filepath.name} complete.")


def run_script(module_path: str, func_name: str, *args):
    """Dynamically import and call a data generation function."""
    import importlib
    module = importlib.import_module(module_path)
    func   = getattr(module, func_name)
    func(*args)


# =====================================================
# STEPS
# =====================================================

def step_schema():
    logger.info("=" * 50)
    logger.info("STEP 1 — Database Schema")
    logger.info("=" * 50)
    run_sql_file(BASE_DIR / "database" / "schema.sql")


def step_master_data():
    logger.info("=" * 50)
    logger.info("STEP 2 — Master / Seed Data")
    logger.info("=" * 50)
    run_sql_file(BASE_DIR / "database" / "master_data.sql")


def step_generate_customers():
    logger.info("=" * 50)
    logger.info("STEP 3 — Generate Customers")
    logger.info("=" * 50)
    run_script("data_generation.generate_customers", "generate_customers")


def step_generate_products():
    logger.info("=" * 50)
    logger.info("STEP 4 — Generate Products")
    logger.info("=" * 50)
    run_script("data_generation.generate_products", "generate_products")


def step_generate_inventory():
    logger.info("=" * 50)
    logger.info("STEP 5 — Generate Inventory")
    logger.info("=" * 50)
    run_script("data_generation.generate_inventory", "generate_inventory")


def step_generate_orders():
    logger.info("=" * 50)
    logger.info("STEP 6 — Generate Orders (50,000 — takes a few minutes)")
    logger.info("=" * 50)
    run_script("data_generation.generate_orders", "generate_orders")


def step_build_analytics():
    logger.info("=" * 50)
    logger.info("STEP 7 — Build Analytics Layer")
    logger.info("=" * 50)
    import analytics.build_summary_tables  # noqa: F401 — runs on import


# =====================================================
# MAIN
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="Nexus Intelligence Platform — Database Setup")
    parser.add_argument("--skip-schema",    action="store_true", help="Skip schema.sql and master_data.sql")
    parser.add_argument("--analytics-only", action="store_true", help="Only rebuild analytics tables")
    args = parser.parse_args()

    logger.info("🚀 Nexus Intelligence Platform — Full Setup Starting")

    if args.analytics_only:
        step_build_analytics()
        logger.info("✅ Analytics layer rebuilt successfully.")
        return

    if not args.skip_schema:
        step_schema()
        step_master_data()

    step_generate_customers()
    step_generate_products()
    step_generate_inventory()
    step_generate_orders()
    step_build_analytics()

    logger.info("=" * 50)
    logger.info("✅ Full setup complete. Run: streamlit run dashboard/app.py")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
