import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def get_forecast(engine):
    """
    Fit a LinearRegression on monthly revenue and project 12 months forward.

    Returns:
        actual   : DataFrame  (month, revenue)
        forecast : DataFrame  (month, forecast, lower_bound, upper_bound)
    """

    df = pd.read_sql("""
        SELECT month, SUM(net_revenue) AS revenue
        FROM monthly_revenue_summary
        GROUP BY month
        ORDER BY month
    """, engine)

    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df["month"]       = pd.to_datetime(df["month"])
    df["month_index"] = range(len(df))

    X = df[["month_index"]]
    y = df["revenue"]

    model = LinearRegression()
    model.fit(X, y)

    # ── Residual standard error for confidence band ───────────────────────────
    y_pred    = model.predict(X)
    residuals = y - y_pred
    std_err   = np.std(residuals)

    # ── Future 12 months ──────────────────────────────────────────────────────
    future = pd.DataFrame({
        "month_index": range(len(df), len(df) + 12)
    })

    future["forecast"]     = model.predict(future[["month_index"]])
    future["lower_bound"]  = future["forecast"] - (1.96 * std_err)
    future["upper_bound"]  = future["forecast"] + (1.96 * std_err)
    future["month"]        = pd.date_range(
        start=df["month"].max(),
        periods=13,
        freq="MS"
    )[1:]

    actual   = df[["month", "revenue"]]
    forecast = future[["month", "forecast", "lower_bound", "upper_bound"]]

    return actual, forecast
