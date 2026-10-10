
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import DBAPIError

from app.config import settings


REVENUE = "SUM(oi.quantity * oi.unit_price * (1 - oi.discount))"


def main():
    url = URL.create(
        "mysql+pymysql",
        username=settings.db_readonly_user,
        password=settings.db_readonly_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
    engine = create_engine(url, pool_pre_ping=True)

    queries = {
        "Row counts": """
            SELECT 'customers' AS table_name, COUNT(*) AS total FROM customers
            UNION ALL SELECT 'products', COUNT(*) FROM products
            UNION ALL SELECT 'orders', COUNT(*) FROM orders
            UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
        """,
        "Revenue by region": f"""
            SELECT o.region, ROUND({REVENUE}, 2) AS revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.status <> 'Cancelled'
            GROUP BY o.region
            ORDER BY revenue DESC
        """,
        "Top 5 products by revenue": f"""
            SELECT p.product_name, ROUND({REVENUE}, 2) AS revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.status <> 'Cancelled'
            GROUP BY p.product_id, p.product_name
            ORDER BY revenue DESC
            LIMIT 5
        """,
    }

    try:
        with engine.connect() as conn:
            for title, sql in queries.items():
                print(f"\n=== {title} ===")
                print(pd.read_sql(text(sql), conn).to_string(index=False))

        print("\n=== Read-only protection test ===")
        try:
            with engine.begin() as conn:
                conn.execute(text("DELETE FROM customers WHERE customer_id = -999"))
            print("FAIL: the read-only user could execute DELETE.")
        except DBAPIError:
            print("PASS: MySQL blocked the DELETE operation.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
