import random
import uuid
from faker import Faker
from config.database import get_engine, text

fake = Faker()
engine = get_engine()


def generate_customers(num_customers=500):
    print(f"Generating {num_customers} customers...")

    insert_query = text("""
    INSERT INTO customers
    (customer_id, first_name, last_name, email, phone, segment_id, region_id, created_at)
    VALUES
    (:customer_id, :first_name, :last_name, :email, :phone, :segment_id, :region_id, :created_at)
    """)

    with engine.begin() as conn:
        for _ in range(num_customers):
            conn.execute(insert_query, {
                "customer_id":  str(uuid.uuid4())[:8],
                "first_name":   fake.first_name(),
                "last_name":    fake.last_name(),
                "email":        fake.email(),
                "phone":        fake.phone_number()[:20],
                "segment_id":   random.randint(1, 5),
                "region_id":    random.randint(1, 5),
                "created_at":   fake.date_time_between(
                                    start_date="-2y",
                                    end_date="now"
                                )
            })

    print("Customers generated.")


if __name__ == "__main__":
    generate_customers()
