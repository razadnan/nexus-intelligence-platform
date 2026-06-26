import pandas as pd
import numpy as np


def get_rfm(engine):
    """
    Compute RFM (Recency, Frequency, Monetary) scores for every customer.
    Returns a DataFrame with columns:
        customer_id, customer_name, recency_days, frequency, monetary,
        r_score, f_score, m_score, rfm_score, segment
    """

    df = pd.read_sql("""
        SELECT
            o.customer_id,
            TRIM(CONCAT(c.first_name, ' ', c.last_name)) AS customer_name,
            MAX(o.order_date)                             AS last_order_date,
            COUNT(o.order_id)                             AS frequency,
            ROUND(SUM(o.net_amount), 2)                   AS monetary
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY o.customer_id, customer_name
    """, engine)

    if df.empty:
        return pd.DataFrame()

    # ── Recency ──────────────────────────────────────────────────────────────
    df["last_order_date"] = pd.to_datetime(df["last_order_date"])
    snapshot_date         = df["last_order_date"].max() + pd.Timedelta(days=1)
    df["recency_days"]    = (snapshot_date - df["last_order_date"]).dt.days

    # ── Score 1–5 (quintiles) ─────────────────────────────────────────────────
    # Recency:  lower days  = better = higher score
    # Frequency & Monetary: higher = better = higher score

    df["r_score"] = pd.qcut(df["recency_days"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    df["f_score"] = pd.qcut(df["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    df["m_score"] = pd.qcut(df["monetary"].rank(method="first"),  q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    df["rfm_score"] = df["r_score"] + df["f_score"] + df["m_score"]

    # ── Segment Labels ────────────────────────────────────────────────────────
    def assign_segment(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        score   = row["rfm_score"]

        if r >= 4 and f >= 4 and m >= 4:
            return "🏆 Champions"
        elif r >= 3 and f >= 3:
            return "💛 Loyal Customers"
        elif r >= 4 and f <= 2:
            return "🌱 Promising"
        elif r >= 3 and f <= 2 and m >= 3:
            return "🔍 Potential Loyalists"
        elif r <= 2 and f >= 3:
            return "⚠️ At Risk"
        elif r == 1 and f >= 4:
            return "😴 Hibernating"
        elif score <= 5:
            return "❌ Lost"
        else:
            return "🔄 Needs Attention"

    df["segment"] = df.apply(assign_segment, axis=1)

    return df[[
        "customer_id", "customer_name",
        "recency_days", "frequency", "monetary",
        "r_score", "f_score", "m_score", "rfm_score", "segment"
    ]].sort_values("rfm_score", ascending=False).reset_index(drop=True)
