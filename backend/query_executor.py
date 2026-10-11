
from decimal import Decimal
from functools import lru_cache

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.database import get_readonly_engine
from backend.sql_validator import validate_sql


class QueryExecutionError(Exception):
    pass


@lru_cache(maxsize=1)
def _get_engine():
    return get_readonly_engine()


def run_query(sql: str) -> pd.DataFrame:
    validation = validate_sql(sql)

    if not validation.is_valid:
        raise QueryExecutionError(
            f"Query rejected: {validation.error}"
        )

    try:
        with _get_engine().connect() as connection:
            connection.execute(
                text("SET SESSION MAX_EXECUTION_TIME = 10000")
            )
            df = pd.read_sql(text(validation.sql), connection)

    except SQLAlchemyError:
        raise QueryExecutionError(
            "Query execution failed. Check your database connection "
            "and SQL column names."
        ) from None

    for column in df.columns:
        if df[column].map(
            lambda value: isinstance(value, Decimal)
        ).any():
            df[column] = df[column].astype(float)

    return df
