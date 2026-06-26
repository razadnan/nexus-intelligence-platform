import random
import uuid
from faker import Faker
from config.database import get_engine, text

fake = Faker()
engine = get_engine()


def generate_products(num_products=100):
    print(f"Generating {num_products} products...")

    insert_query = text("""
    INSERT INTO products
    (product_id, product_name, sku_code, category_id, price, cost, created_at)
    VALUES
    (:product_id, :product_name, :sku_code, :category_id, :price, :cost, :created_at)
    """)

    with engine.begin() as conn:
        for _ in range(num_products):
            price = round(random.uniform(10.0, 500.0), 2)
            cost  = round(price * random.uniform(0.3, 0.7), 2)
            conn.execute(insert_query, {
                "product_id":   str(uuid.uuid4())[:8],
                "product_name": fake.catch_phrase()[:255],
                "sku_code":     "SKU-" + str(uuid.uuid4())[:8].upper(),
                "category_id":  random.randint(1, 5),
                "price":        price,
                "cost":         cost,
                "created_at":   fake.date_time_between(
                                    start_date="-2y",
                                    end_date="now"
                                )
            })

    print("Products generated.")


if __name__ == "__main__":
    generate_products()
