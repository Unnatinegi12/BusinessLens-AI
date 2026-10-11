
import pytest

from backend.sql_validator import validate_sql


def test_select_query_is_accepted():
    result = validate_sql("SELECT * FROM customers")
    assert result.is_valid
    assert "LIMIT 1000" in result.sql.upper()


def test_small_limit_is_preserved():
    result = validate_sql("SELECT * FROM customers LIMIT 5")
    assert result.is_valid
    assert "LIMIT 5" in result.sql.upper()


@pytest.mark.parametrize("sql", [
    "DELETE FROM customers",
    "DROP TABLE customers",
    "UPDATE customers SET city = 'X'",
    "INSERT INTO customers VALUES (1, 'A', 'B', 'C')",
    "SELECT * FROM mysql.user",
    "SELECT * FROM information_schema.tables",
    "SELECT SLEEP(10) FROM customers",
    "SELECT * FROM customers FOR UPDATE",
    "SELECT * FROM customers; SELECT * FROM orders",
])


def test_unsafe_queries_are_rejected(sql):
    assert not validate_sql(sql).is_valid


def test_unknown_table_is_rejected():
    result = validate_sql("SELECT * FROM secret_table")
    assert not result.is_valid


def test_empty_query_is_rejected():
    assert not validate_sql("").is_valid
