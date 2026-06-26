from sqlalchemy import text

def generate_alerts(conn):
    conn.execute(text("DELETE FROM alerts"))

    low_stock_rows = conn.execute(text("""
        SELECT 
            p.product_name,
            p.sku_code,
            w.warehouse_name,
            i.quantity_on_hand,
            i.reorder_level
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        JOIN warehouses w ON i.warehouse_id = w.warehouse_id
        WHERE i.quantity_on_hand <= i.reorder_level
    """)).fetchall()

    for row in low_stock_rows:
        msg = (
            f"Low stock alert: {row.product_name} ({row.sku_code}) "
            f"in {row.warehouse_name} has only {row.quantity_on_hand} units left "
            f"(reorder level: {row.reorder_level})."
        )
        conn.execute(text("""
            INSERT INTO alerts (alert_type, message, is_read, created_at)
            VALUES (:alert_type, :message, 0, NOW())
        """), {
            "alert_type": "warn",
            "message": msg
        })

    revenue_row = conn.execute(text("""
        SELECT COALESCE(SUM(net_amount), 0) AS monthly_revenue
        FROM orders
        WHERE YEAR(order_date) = YEAR(CURDATE())
          AND MONTH(order_date) = MONTH(CURDATE())
    """)).fetchone()

    monthly_revenue = revenue_row.monthly_revenue or 0
    revenue_target = 500000

    if monthly_revenue < revenue_target:
        shortfall_pct = round((1 - monthly_revenue / revenue_target) * 100, 2)
        msg = (
            f"Revenue alert: Current month revenue is ₹{monthly_revenue:,.2f}, "
            f"which is {shortfall_pct}% below the target of ₹{revenue_target:,.2f}."
        )
        conn.execute(text("""
            INSERT INTO alerts (alert_type, message, is_read, created_at)
            VALUES (:alert_type, :message, 0, NOW())
        """), {
            "alert_type": "warn",
            "message": msg
        })