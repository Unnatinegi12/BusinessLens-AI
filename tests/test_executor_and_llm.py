
import pytest

from backend import query_executor
from backend.nl_to_sql import (
    LLMNotConfiguredError,
    SQLGenerationError,
    _clean_sql,
    generate_sql,
)
from backend.query_executor import QueryExecutionError


def test_invalid_sql_never_connects_to_database(monkeypatch):
    def should_not_run():
        raise AssertionError("Database must not be accessed")

    monkeypatch.setattr(query_executor, "_get_engine", should_not_run)

    with pytest.raises(QueryExecutionError):
        query_executor.run_query("DROP TABLE customers")


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(LLMNotConfiguredError):
        generate_sql("What is the total revenue?")


def test_empty_question():
    with pytest.raises(SQLGenerationError):
        generate_sql("")


def test_question_too_long():
    with pytest.raises(SQLGenerationError):
        generate_sql("x" * 501)


def test_markdown_fences_removed():
    assert _clean_sql("```sql\nSELECT 1\n```") == "SELECT 1"
