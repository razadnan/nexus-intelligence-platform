import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config.database import get_engine
from analytics.forecasting import get_forecast

engine = get_engine()

# =====================================================
# CACHED FORECAST
# =====================================================

@st.cache_data(ttl=300)
def load_forecast():
    return get_forecast(engine)

# =====================================================
# PAGE TITLE
# =====================================================

st.title("🔮 Revenue Forecasting")

# =====================================================
# FORECAST CHART WITH CONFIDENCE INTERVALS
# =====================================================

actual, forecast = load_forecast()

if actual.empty:
    st.warning("No data available for forecasting. Run build_summary_tables.py first.")
    st.stop()

fig = go.Figure()

# Actual revenue line
fig.add_trace(go.Scatter(
    x=actual["month"],
    y=actual["revenue"],
    mode="lines+markers",
    name="Actual Revenue",
    line=dict(color="#1f77b4", width=2),
    marker=dict(size=5)
))

# Confidence interval shading (upper → lower filled)
fig.add_trace(go.Scatter(
    x=pd.concat([forecast["month"], forecast["month"][::-1]]),
    y=pd.concat([forecast["upper_bound"], forecast["lower_bound"][::-1]]),
    fill="toself",
    fillcolor="rgba(255, 165, 0, 0.15)",
    line=dict(color="rgba(255,255,255,0)"),
    hoverinfo="skip",
    name="95% Confidence Interval",
    showlegend=True
))

# Forecast line
fig.add_trace(go.Scatter(
    x=forecast["month"],
    y=forecast["forecast"],
    mode="lines+markers",
    name="Forecast",
    line=dict(color="orange", width=2, dash="dash"),
    marker=dict(size=5)
))

fig.update_layout(
    title="Revenue Forecast — Actual vs Projected (with 95% Confidence Interval)",
    xaxis_title="Month",
    yaxis_title="Revenue ($)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)

st.plotly_chart(fig, width='stretch')

# =====================================================
# FORECAST TABLE
# =====================================================

st.subheader("📅 Next 12 Month Forecast")

forecast_display = forecast.copy()
forecast_display["month"]       = forecast_display["month"].dt.strftime("%B %Y")
forecast_display["forecast"]    = forecast_display["forecast"].round(2)
forecast_display["lower_bound"] = forecast_display["lower_bound"].round(2)
forecast_display["upper_bound"] = forecast_display["upper_bound"].round(2)
forecast_display.columns        = ["Month", "Forecast ($)", "Lower Bound ($)", "Upper Bound ($)"]

st.dataframe(forecast_display, width='stretch')

# =====================================================
# SUMMARY METRICS
# =====================================================

st.divider()

total_forecast  = forecast["forecast"].sum()
avg_monthly     = forecast["forecast"].mean()
growth_rate     = ((forecast["forecast"].iloc[-1] - actual["revenue"].iloc[-1]) / actual["revenue"].iloc[-1]) * 100

c1, c2, c3 = st.columns(3)
c1.metric("12-Month Forecast Total", f"${total_forecast:,.0f}")
c2.metric("Avg Monthly Forecast",    f"${avg_monthly:,.0f}")
c3.metric("Projected Growth",        f"{growth_rate:.1f}%")

st.caption("Nexus Intelligence Platform • Revenue Forecasting")
