import pandas as pd
from sklearn.linear_model import LinearRegression

def generate_ai_insights(engine):
    df = pd.read_sql("""
    SELECT
        month,
        SUM(net_revenue) revenue
    FROM monthly_revenue_summary
    GROUP BY month
    ORDER BY month
    """, engine)
    
    if len(df) < 2:
        return ["Not enough data to generate reliable AI insights."]
        
    df["month_index"] = range(len(df))
    X = df[["month_index"]]
    y = df["revenue"]
    
    model = LinearRegression()
    model.fit(X, y)
    
    slope = model.coef_[0]
    
    # Calculate percentage growth based on the average
    avg_revenue = df["revenue"].mean()
    growth_pct = (slope / avg_revenue) * 100 if avg_revenue else 0
    
    trend = "increasing" if slope > 0 else "decreasing"
    
    insights = [
        f"Based on recent data, revenue is trending **{trend}** with an average monthly change of **${abs(slope):,.2f}**.",
        f"This represents an approximate monthly growth trajectory of **{growth_pct:+.2f}%**."
    ]
    
    # If we have recent data vs previous data
    if len(df) >= 3:
        recent_avg = df["revenue"].iloc[-3:].mean()
        older_avg = df["revenue"].iloc[:-3].mean()
        if older_avg > 0:
            diff_pct = ((recent_avg - older_avg) / older_avg) * 100
            insights.append(f"Recent quarter average revenue (${recent_avg:,.2f}) is **{diff_pct:+.2f}%** compared to the older historical average.")
    
    return insights
