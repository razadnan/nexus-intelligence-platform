from config.database import get_engine, text
from faker import Faker
from datetime import datetime, timedelta
import random
import uuid

fake = Faker()

# ==========================================
# DATABASE
# ==========================================

engine = get_engine()

# ==========================================
# CONFIG
# ==========================================

TOTAL_ORDERS = 50000

ORDER_STATUSES = [
    "pending",
    "processing",
    "shipped",
    "delivered",
    "cancelled"
]

PAYMENT_METHODS = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Wallet"
]

RETURN_REASONS = [
    "Damaged Product",
    "Wrong Product",
    "Quality Issue",
    "Customer Dissatisfied",
    "Defective Item"
]

# ==========================================
# LOAD CUSTOMERS
# ==========================================

with engine.connect() as conn:

    customers = conn.execute(text("""
        SELECT customer_id, region_id
        FROM customers
    """)).fetchall()

    products = conn.execute(text("""
        SELECT product_id, price as unit_price
        FROM products
    """)).fetchall()

print(f"Customers Loaded : {len(customers)}")
print(f"Products Loaded  : {len(products)}")

# ==========================================
# GENERATE ORDERS
# ==========================================

order_insert = text("""
INSERT INTO orders
(
    customer_id,
    region_id,
    order_date,
    total_amount,
    discount_amount,
    net_amount,
    status,
    payment_method,
    created_at
)
VALUES
(
    :customer_id,
    :region_id,
    :order_date,
    :total_amount,
    :discount_amount,
    :net_amount,
    :status,
    :payment_method,
    :created_at
)
""")

item_insert = text("""
INSERT INTO order_items
(
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_pct,
    line_total
)
VALUES
(
    :order_id,
    :product_id,
    :quantity,
    :unit_price,
    :discount_pct,
    :line_total
)
""")

payment_insert = text("""
INSERT INTO payments
(
    order_id,
    payment_method,
    amount,
    status,
    transaction_id,
    paid_at
)
VALUES
(
    :order_id,
    :payment_method,
    :amount,
    :status,
    :transaction_id,
    :paid_at
)
""")

return_insert = text("""
INSERT INTO returns
(
    order_id,
    product_id,
    customer_id,
    return_reason,
    return_amount,
    status,
    created_at
)
VALUES
(
    :order_id,
    :product_id,
    :customer_id,
    :return_reason,
    :return_amount,
    :status,
    :created_at
)
""")

# ==========================================
# GENERATION LOOP
# ==========================================

with engine.begin() as conn:

    for i in range(TOTAL_ORDERS):

        customer_id, region_id = random.choice(customers)

        order_date = fake.date_time_between(
            start_date="-24M",
            end_date="now"
        )

        status = random.choices(
            ORDER_STATUSES,
            weights=[5, 10, 15, 65, 5]
        )[0]

        payment_method = random.choice(
            PAYMENT_METHODS
        )

        num_items = random.randint(1, 5)

        selected_products = random.sample(
            products,
            num_items
        )

        total_amount = 0

        order_lines = []

        for product_id, unit_price in selected_products:

            qty = random.randint(1, 5)

            discount_pct = random.choice(
                [0, 5, 10, 15]
            )

            line_total = round(
                qty * float(unit_price) * (1 - discount_pct / 100), 2
            )

            total_amount += line_total

            order_lines.append({
                "product_id": product_id,
                "quantity": qty,
                "unit_price": float(unit_price),
                "discount_pct": discount_pct,
                "line_total": line_total
            })

        discount_amount = round(
            total_amount * random.uniform(0, 0.15),
            2
        )

        net_amount = round(
            total_amount - discount_amount,
            2
        )

        result = conn.execute(
            order_insert,
            {
                "customer_id": customer_id,
                "region_id": region_id,
                "order_date": order_date,
                "total_amount": total_amount,
                "discount_amount": discount_amount,
                "net_amount": net_amount,
                "status": status,
                "payment_method": payment_method,
                "created_at": order_date
            }
        )

        order_id = result.lastrowid

        for line in order_lines:

            conn.execute(
                item_insert,
                {
                    "order_id": order_id,
                    **line
                }
            )

        payment_status = (
            "success"
            if status != "cancelled"
            else "failed"
        )

        conn.execute(
            payment_insert,
            {
                "order_id": order_id,
                "payment_method": payment_method,
                "amount": net_amount,
                "status": payment_status,
                "transaction_id": str(uuid.uuid4()),
                "paid_at": order_date
            }
        )

        if (
            status == "delivered"
            and random.random() < 0.03
        ):

            returned_product = random.choice(
                order_lines
            )

            conn.execute(
                return_insert,
                {
                    "order_id": order_id,
                    "product_id": returned_product["product_id"],
                    "customer_id": customer_id,
                    "return_reason": random.choice(
                        RETURN_REASONS
                    ),
                    "return_amount": returned_product["line_total"],
                    "status": "refunded",
                    "created_at": order_date + timedelta(days=7)
                }
            )

        if (i + 1) % 1000 == 0:
            print(
                f"{i+1:,} orders generated..."
            )

print("Order generation completed.")