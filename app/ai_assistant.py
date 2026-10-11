
import streamlit as st

from backend.nl_to_sql import (
    LLMNotConfiguredError,
    SQLGenerationError,
    generate_sql,
)
from backend.query_executor import QueryExecutionError, run_query
from backend.sql_validator import validate_sql


def render_ai_assistant():
    st.divider()
    st.header("AI Business Query Assistant")
    st.caption("Ask a business question, review the generated SQL, then run it.")

    question = st.text_input(
        "Your business question",
        placeholder="e.g. What is the total revenue?",
        key="business_question",
    )

    if st.button("Generate SQL"):
        st.session_state.pop("generated_sql", None)
        st.session_state.pop("query_results", None)

        try:
            with st.spinner("Generating SQL..."):
                sql = generate_sql(question)
                validation = validate_sql(sql)

            if validation.is_valid:
                st.session_state["generated_sql"] = validation.sql
            else:
                st.error(f"SQL rejected: {validation.error}")

        except (LLMNotConfiguredError, SQLGenerationError) as exc:
            st.error(str(exc))

    sql = st.session_state.get("generated_sql")

    if sql:
        st.subheader("Review generated SQL")
        st.code(sql, language="sql")

        if st.button("Run Query"):
            try:
                with st.spinner("Running query..."):
                    st.session_state["query_results"] = run_query(sql)
            except QueryExecutionError as exc:
                st.error(str(exc))

    results = st.session_state.get("query_results")

    if results is not None:
        st.subheader("Query Results")
        st.dataframe(results, width="stretch")

        st.download_button(
            "Download CSV",
            data=results.to_csv(index=False).encode("utf-8"),
            file_name="business_query_results.csv",
            mime="text/csv",
        )
