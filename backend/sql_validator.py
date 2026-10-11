
import re
from dataclasses import dataclass
from typing import Optional

import sqlglot
from sqlglot import exp
from sqlglot.errors import SqlglotError

ALLOWED_TABLES = {"customers", "products", "orders", "order_items"}
MAX_ROWS = 1000
MAX_SQL_LENGTH = 5000

BLOCKED_RAW = re.compile(
    r"/\*!|--|/\*|;|@@|"
    r"\b(sleep|benchmark|load_file|outfile|dumpfile|"
    r"get_lock|release_lock)\b",
    re.IGNORECASE,
)

BLOCKED_FUNCTIONS = {
    "SLEEP", "BENCHMARK", "LOAD_FILE", "GET_LOCK",
    "RELEASE_LOCK", "IS_FREE_LOCK", "IS_USED_LOCK",
    "DATABASE", "SCHEMA", "USER", "CURRENT_USER",
    "SESSION_USER", "SYSTEM_USER", "VERSION",
    "CONNECTION_ID",
}


@dataclass
class ValidationResult:
    is_valid: bool
    sql: Optional[str] = None
    error: Optional[str] = None


def reject(message: str) -> ValidationResult:
    return ValidationResult(False, error=message)


def validate_sql(sql: str) -> ValidationResult:
    if not sql or not sql.strip():
        return reject("The query is empty.")

    sql = sql.strip()

    if len(sql) > MAX_SQL_LENGTH:
        return reject("The query is too long.")

    if BLOCKED_RAW.search(sql):
        return reject("The query contains a blocked token.")

    try:
        statements = [
            statement
            for statement in sqlglot.parse(sql, read="mysql")
            if statement is not None
        ]
    except SqlglotError:
        return reject("The query is not valid MySQL SQL.")

    if len(statements) != 1:
        return reject("Exactly one SQL statement is allowed.")

    stmt = statements[0]

    if not isinstance(stmt, exp.Select):
        return reject("Only SELECT queries are allowed.")

    if stmt.args.get("locks"):
        return reject("Locking queries are not allowed.")

    forbidden_names = {
        "Insert", "Update", "Delete", "Drop", "Alter",
        "AlterTable", "Create", "Command", "Into",
        "Set", "Use", "Grant", "Revoke",
    }

    for node in stmt.walk():
        if type(node).__name__ in forbidden_names:
            return reject("The query contains a forbidden operation.")

        if isinstance(node, exp.Func):
            name = (
                node.name
                if isinstance(node, exp.Anonymous)
                else node.sql_name()
            )
            if name.upper() in BLOCKED_FUNCTIONS:
                return reject(f"The function {name.upper()} is not allowed.")

    cte_names = {
        cte.alias.lower()
        for cte in stmt.find_all(exp.CTE)
        if cte.alias
    }

    for table in stmt.find_all(exp.Table):
        if table.db or table.catalog:
            return reject("Schema-qualified tables are not allowed.")

        name = table.name.lower()
        if name not in ALLOWED_TABLES and name not in cte_names:
            return reject(f"Table '{table.name}' is not approved.")

    limit = stmt.args.get("limit")
    valid_limit = (
        limit is not None
        and isinstance(limit.expression, exp.Literal)
        and limit.expression.is_int
        and int(limit.expression.this) <= MAX_ROWS
    )

    if not valid_limit:
        stmt = stmt.limit(MAX_ROWS)

    return ValidationResult(
        is_valid=True,
        sql=stmt.sql(dialect="mysql"),
    )
