import streamlit as st
from config.database import get_engine
from analytics.ai_insights import generate_ai_insights

st.set_page_config(
    page_title="Nexus Intelligence Platform",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Nexus Intelligence Platform")

st.markdown("""
### Enterprise Analytics Suite

Use the sidebar to navigate:

- 📊 Executive Dashboard
- 🧠 Executive Insights
- 📈 Sales Analytics
- 👥 Customer Intelligence
- 📦 Inventory Control
- 🔮 Forecasting
""")

st.divider()

# ==========================================
# AI INSIGHTS ON HOME PAGE
# ==========================================

st.subheader("🤖 AI Revenue Insights")

try:
    engine = get_engine()
    insights = generate_ai_insights(engine)
    for insight in insights:
        st.info(insight)
except Exception as e:
    st.warning(f"AI insights unavailable: {e}")
