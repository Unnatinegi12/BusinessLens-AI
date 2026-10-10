
import random
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from app.config import settings


def main():
    rng = random.Random(42)
    today = date(2026, 10, 10)
    regions = ["North", "South", "East", "West", "Central"]
    categories = ["Electronics", "Clothing", "Home", "Sports", "Books"]
    statuses = ["Delivered", "Delivered", "Shipped", "Processing", "Cancelled"]

    customers = pd.DataFrame([
        {
            "customer_id": i,
            "customer_name": f"Customer {i}",
            "email": f"customer{i}@example.com",
            "region": rng.choice(regions),
            "signup_date": today - timedelta(days=rng.randint(30, 1000)),
        }
        for i in range(1, 201)
    ])

    products = pd.DataFrame([
        {
            "product_id": i,
            "product_name": f"{categories[(i - 1) % 5]} Product {i}",
            "category": categories[(i - 1) % 5],
            "unit_price": round(rng.uniform(10, 500), 2),
        }
        for i in range(1, 41)
    ])

    orders = []
    order_items = []
    item_id = 1

    for order_id in range(1, 2001):
        customer_id = rng.randint(1, 200)
        region = customers.loc[
            customers["customer_id"] == customer_id, "region"
        ].iloc[0]

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": today - timedelta(days=rng.randint(0, 730)),
            "status": rng.choice(statuses),
            "region": region,
        })

        for _ in range(rng.randint(1, 4)):
            product = products.iloc[rng.randrange(len(products))]
            order_items.append({
                "order_item_id": item_id,
                "order_id": order_id,
                "product_id": int(product["product_id"]),
                "quantity": rng.randint(1, 5),
                "unit_price": float(product["unit_price"]),
                "discount": rng.choice([0, 0, 0, 0.05, 0.10, 0.15]),
            })
            item_id += 1

    url = URL.create(
        "mysql+pymysql",
        username=settings.db_admin_user,
        password=settings.db_admin_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
    engine = create_engine(url, pool_pre_ping=True)

    with engine.begin() as conn:
        conn.exec_driver_sql("DELETE FROM order_items")
        conn.exec_driver_sql("DELETE FROM orders")
        conn.exec_driver_sql("DELETE FROM products")
        conn.exec_driver_sql("DELETE FROM customers")

        customers.to_sql("customers", conn, if_exists="append", index=False)
        products.to_sql("products", conn, if_exists="append", index=False)
        pd.DataFrame(orders).to_sql(
            "orders", conn, if_exists="append", index=False
        )
        pd.DataFrame(order_items).to_sql(
            "order_items", conn, if_exists="append", index=False
        )

    engine.dispose()
    print(
        f"Seeded {len(customers)} customers, {len(products)} products, "
        f"{len(orders)} orders, and {len(order_items)} order items."
    )


if __name__ == "__main__":
    main()
