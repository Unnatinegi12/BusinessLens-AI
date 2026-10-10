from sqlalchemy import text, create_engine
from sqlalchemy.engine import URL
from app.config import settings


def main():
    if not settings.db_admin_password or not settings.db_readonly_password:
        raise RuntimeError("Set both database passwords in .env first.")

    admin_url = URL.create(
        "mysql+pymysql",
        username=settings.db_admin_user,
        password=settings.db_admin_password,
        host=settings.db_host,
        port=settings.db_port,
        database="mysql",
    )
    admin_engine = create_engine(admin_url, pool_pre_ping=True)

    with admin_engine.begin() as conn:
        conn.execute(text(
            f"CREATE DATABASE IF NOT EXISTS `{settings.db_name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))

    db_url = admin_url.set(database=settings.db_name)
    db_engine = create_engine(db_url, pool_pre_ping=True)

    with db_engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INT PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL,
                region VARCHAR(50) NOT NULL,
                signup_date DATE NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INT PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                category VARCHAR(60) NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT PRIMARY KEY,
                customer_id INT NOT NULL,
                order_date DATE NOT NULL,
                status VARCHAR(30) NOT NULL,
                region VARCHAR(50) NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INT PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                discount DECIMAL(5,2) NOT NULL DEFAULT 0,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """))

    # Restrict the account to reading data from this database.
    user = settings.db_readonly_user
    if not user.replace("_", "").isalnum():
        raise ValueError("Read-only username must contain only letters, numbers, underscores.")

    # Escape the password as a MySQL string literal.
    import pymysql
    escaped_password = pymysql.converters.escape_string(
        settings.db_readonly_password
    ).replace("\\'", "\\\\'")

    with admin_engine.begin() as conn:
        conn.exec_driver_sql(
            f"CREATE USER IF NOT EXISTS '{user}'@'127.0.0.1' "
            f"IDENTIFIED BY '{escaped_password}'"
        )
        conn.exec_driver_sql(
            f"GRANT SELECT ON `{settings.db_name}`.* "
            f"TO '{user}'@'127.0.0.1'"
        )

    db_engine.dispose()
    admin_engine.dispose()
    print("Database and tables created. Read-only user configured.")


if __name__ == "__main__":
    main()