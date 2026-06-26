from sqlalchemy import create_engine
import pandas as pd

engine = create_engine(
    "mysql+pymysql://root:raza@localhost/nexus_intelligence"
)

tables = [

    "customers",
    "products",
    "warehouses",
    "inventory",
    "orders",
    "order_items",
    "payments",
    "returns",

    "monthly_revenue_summary",
    "sales_activity_log",
    "alerts",
    "kpi_snapshots",
    "customer_health_metrics"

]

print("\nDATABASE VALIDATION\n")

all_passed = True

for table in tables:

    try:

        df = pd.read_sql(
            f"SELECT COUNT(*) AS total FROM {table}",
            engine
        )

        count = int(df.iloc[0]["total"])

        print(
            f"[PASS] {table:<30} {count:,} rows"
        )

    except Exception as e:

        all_passed = False

        print(
            f"[FAIL] {table}"
        )

        print(e)

print("\n----------------------------------")

if all_passed:

    print("ALL TESTS PASSED")

else:

    print("SOME TESTS FAILED")