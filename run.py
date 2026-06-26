"""
run.py
──────
Single entry point for the Nexus Intelligence Platform.

Commands:
    python run.py dashboard       # Launch Streamlit dashboard
    python run.py seed            # Full database setup + data generation
    python run.py seed --skip-schema    # Skip schema, regenerate data only
    python run.py seed --analytics-only # Rebuild analytics tables only
    python run.py report          # Generate PDF + Excel reports
    python run.py test            # Run pytest suite
    python run.py check           # Run system_check.py
"""

import argparse
import subprocess
import sys


def run_dashboard():
    print("🚀 Launching Nexus Intelligence Platform dashboard...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py"])


def run_seed(skip_schema=False, analytics_only=False):
    args = [sys.executable, "database/seed.py"]
    if skip_schema:
        args.append("--skip-schema")
    if analytics_only:
        args.append("--analytics-only")
    subprocess.run(args)


def run_reports():
    print("📄 Generating PDF report...")
    subprocess.run([sys.executable, "-c",
        "from reports.pdf_report import generate_pdf_report; f=generate_pdf_report(); print(f'✅ PDF saved: {f}')"])

    print("📊 Generating Excel report...")
    subprocess.run([sys.executable, "-c",
        "from reports.excel_report import generate_excel_report; f=generate_excel_report(); print(f'✅ Excel saved: {f}')"])


def run_tests():
    print("🧪 Running pytest suite...")
    subprocess.run([sys.executable, "-m", "pytest"])


def run_check():
    print("🔍 Running system check...")
    subprocess.run([sys.executable, "tests/system_check.py"])


# =====================================================
# MAIN
# =====================================================

def main():
    parser = argparse.ArgumentParser(
        description="Nexus Intelligence Platform — Command Runner",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "command",
        choices=["dashboard", "seed", "report", "test", "check"],
        help=(
            "dashboard       Launch Streamlit dashboard\n"
            "seed            Full database setup + data generation\n"
            "report          Generate PDF + Excel reports\n"
            "test            Run 29-test pytest suite\n"
            "check           Run system file check\n"
        )
    )

    parser.add_argument("--skip-schema",    action="store_true", help="(seed only) Skip schema.sql and master_data.sql")
    parser.add_argument("--analytics-only", action="store_true", help="(seed only) Only rebuild analytics tables")

    args = parser.parse_args()

    if args.command == "dashboard":
        run_dashboard()

    elif args.command == "seed":
        run_seed(skip_schema=args.skip_schema, analytics_only=args.analytics_only)

    elif args.command == "report":
        run_reports()

    elif args.command == "test":
        run_tests()

    elif args.command == "check":
        run_check()


if __name__ == "__main__":
    main()
