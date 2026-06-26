from sqlalchemy import text

# ==========================================
# EXECUTIVE KPI SNAPSHOT
# ==========================================

KPI_QUERY = text("""
SELECT
    total_revenue,
    total_orders,
    total_customers,
    avg_order_value,
    gross_margin_pct,
    return_rate_pct,
    retention_rate,
    inventory_fill_pct,
    nps_score
FROM kpi_snapshots
ORDER BY snapshot_date DESC
LIMIT 1
""")

# ==========================================
# MONTHLY REVENUE TREND
# ==========================================

MONTHLY_REVENUE_QUERY = text("""
SELECT
    month,
    SUM(net_revenue) AS net_revenue,
    SUM(gross_revenue) AS gross_revenue,
    SUM(target_revenue) AS target_revenue
FROM monthly_revenue_summary
GROUP BY month
ORDER BY month
""")

# ==========================================
# REVENUE BY REGION
# ==========================================

REGION_REVENUE_QUERY = text("""
SELECT
    r.region_name,
    SUM(m.net_revenue) AS revenue
FROM monthly_revenue_summary m
JOIN regions r
    ON m.region_id = r.region_id
GROUP BY r.region_name
ORDER BY revenue DESC
""")

# ==========================================
# REVENUE BY SEGMENT
# ==========================================

SEGMENT_REVENUE_QUERY = text("""
SELECT
    cs.segment_name,
    SUM(m.net_revenue) AS revenue
FROM monthly_revenue_summary m
JOIN customer_segments cs
    ON m.segment_id = cs.segment_id
GROUP BY cs.segment_name
ORDER BY revenue DESC
""")

# ==========================================
# TOP PRODUCTS
# ==========================================

TOP_PRODUCTS_QUERY = text("""
SELECT
    p.product_name,
    pc.category_name,
    SUM(oi.quantity) AS total_units,
    ROUND(SUM(oi.line_total), 2) AS revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN product_categories pc
    ON p.category_id = pc.category_id
GROUP BY p.product_name, pc.category_name
ORDER BY revenue DESC
LIMIT 5
""")

# ==========================================
# ORDER STATUS DISTRIBUTION
# ==========================================

ORDER_STATUS_QUERY = text("""
SELECT
    status,
    COUNT(*) AS total_orders
FROM orders
GROUP BY status
ORDER BY total_orders DESC
""")

# ==========================================
# PAYMENT METHOD MIX
# ==========================================

PAYMENT_METHOD_QUERY = text("""
SELECT
    payment_method,
    COUNT(*) AS total_payments,
    ROUND(SUM(amount), 2) AS total_amount
FROM payments
GROUP BY payment_method
ORDER BY total_amount DESC
""")

# ==========================================
# SALES ACTIVITY HEATMAP
# ==========================================

SALES_ACTIVITY_QUERY = text("""
SELECT
    day_of_week,
    hour_slot,
    SUM(order_count) AS order_count,
    ROUND(SUM(revenue), 2) AS revenue
FROM sales_activity_log
GROUP BY day_of_week, hour_slot
ORDER BY
    FIELD(day_of_week,
        'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'
    ),
    hour_slot
""")

# ==========================================
# INVENTORY HEALTH SUMMARY
# ==========================================

INVENTORY_HEALTH_QUERY = text("""
SELECT
    status,
    COUNT(*) AS product_count
FROM inventory
GROUP BY status
ORDER BY product_count DESC
""")

# ==========================================
# INVENTORY HEALTH TOTALS
# ==========================================

INVENTORY_OVERVIEW_QUERY = text("""
SELECT
    COUNT(*) AS total_items,
    SUM(CASE WHEN status = 'healthy' THEN 1 ELSE 0 END) AS healthy_items,
    SUM(CASE WHEN status = 'low' THEN 1 ELSE 0 END) AS low_items,
    SUM(CASE WHEN status = 'critical' THEN 1 ELSE 0 END) AS critical_items
FROM inventory
""")

# ==========================================
# LOW STOCK ALERTS
# ==========================================

LOW_STOCK_QUERY = text("""
SELECT
    p.product_name,
    CONCAT('SKU-', p.product_id) AS sku,
    i.quantity_on_hand AS stock,
    i.reorder_level
FROM inventory i
JOIN products p
    ON i.product_id = p.product_id
WHERE i.status IN ('low', 'critical')
ORDER BY i.quantity_on_hand ASC
LIMIT 5
""")

# ==========================================
# ALERTS
# ==========================================

ALERTS_QUERY = text("""
SELECT
    alert_type,
    message,
    created_at
FROM alerts
ORDER BY created_at DESC
LIMIT 5
""")