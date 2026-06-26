import pandas as pd


def get_cohort_matrix(engine):
    """
    Build a monthly cohort retention matrix.

    Returns:
        cohort_matrix : DataFrame  (cohort month × period index, values = retention %)
        cohort_sizes  : Series     (cohort month → number of customers in cohort)
    """

    # ── Raw order data ────────────────────────────────────────────────────────
    df = pd.read_sql("""
        SELECT
            customer_id,
            DATE_FORMAT(order_date, '%%Y-%%m-01') AS order_month
        FROM orders
    """, engine)

    if df.empty:
        return pd.DataFrame(), pd.Series(dtype=int)

    df["order_month"] = pd.to_datetime(df["order_month"])

    # ── Cohort month = first month the customer ever ordered ──────────────────
    df["cohort_month"] = df.groupby("customer_id")["order_month"].transform("min")

    # ── Period index = months since cohort month ──────────────────────────────
    df["period_index"] = (
        (df["order_month"].dt.year  - df["cohort_month"].dt.year)  * 12 +
        (df["order_month"].dt.month - df["cohort_month"].dt.month)
    )

    # ── Count unique customers per cohort × period ────────────────────────────
    cohort_data = (
        df.groupby(["cohort_month", "period_index"])["customer_id"]
          .nunique()
          .reset_index()
          .rename(columns={"customer_id": "customers"})
    )

    # ── Pivot into matrix ─────────────────────────────────────────────────────
    cohort_pivot = cohort_data.pivot_table(
        index="cohort_month",
        columns="period_index",
        values="customers"
    )

    # ── Cohort sizes (period 0 = acquisition month) ───────────────────────────
    cohort_sizes = cohort_pivot[0]

    # ── Retention % = customers in period N / cohort size ────────────────────
    cohort_matrix = cohort_pivot.divide(cohort_sizes, axis=0).round(4) * 100

    # ── Format index as readable month string ────────────────────────────────
    cohort_matrix.index = cohort_matrix.index.strftime("%Y-%m")

    # Keep only first 12 periods to keep the heatmap readable
    cohort_matrix = cohort_matrix.iloc[:, :12]

    return cohort_matrix, cohort_sizes
