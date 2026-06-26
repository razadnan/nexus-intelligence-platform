import random
from datetime import datetime
from config.database import get_engine, text

engine = get_engine()


def generate_inventory():
    with engine.connect() as conn:
        products   = conn.execute(text("SELECT product_id FROM products")).fetchall()
        warehouses = conn.execute(text("SELECT warehouse_id FROM warehouses")).fetchall()

    inventory_rows = []

    for product in products:
        for warehouse in warehouses:

            quantity_on_hand = random.randint(20, 1000)
            reorder_level    = random.randint(20, 150)
            reorder_qty      = random.randint(50, 300)

            if quantity_on_hand <= reorder_level * 0.5:
                status = "critical"
            elif quantity_on_hand <= reorder_level:
                status = "low"
            else:
                status = "healthy"

            inventory_rows.append({
                "product_id":      product[0],
                "warehouse_id":    warehouse[0],
                "quantity_on_hand": quantity_on_hand,
                "reorder_level":   reorder_level,
                "reorder_qty":     reorder_qty,
                "last_updated":    datetime.now(),
                "status":          status
            })

    insert_query = text("""
        INSERT INTO inventory
        (product_id, warehouse_id, quantity_on_hand, reorder_level, reorder_qty, last_updated, status)
        VALUES
        (:product_id, :warehouse_id, :quantity_on_hand, :reorder_level, :reorder_qty, :last_updated, :status)
    """)

    with engine.begin() as conn:
        conn.execute(insert_query, inventory_rows)

    print(f"Inserted {len(inventory_rows)} inventory records successfully.")


if __name__ == "__main__":
    generate_inventory()