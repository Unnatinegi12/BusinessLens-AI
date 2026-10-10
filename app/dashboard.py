
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from app.config import settings


st.set_page_config(
    page_title="BusinessLens AI",
    page_icon="📊",
    layout="wide",
)

st.title("📊 BusinessLens AI")
st.caption("Business performance analytics dashboard")

# Connect using the read-only database account.
url = URL.create(
    "mysql+pymysql",
    username=settings.db_readonly_user,
    password=settings.db_readonly_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)
engine = create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=60)
def load_data():
    query = """
        SELECT
            o.order_id,
            o.order_date,
            o.status,
            o.region,
            c.customer_name,
            p.product_name,
            p.category,
            oi.quantity,
            oi.unit_price,
            oi.discount,
            oi.quantity * oi.unit_price * (1 - oi.discount) AS revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.status <> 'Cancelled'
    """
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


try:
    df = load_data()

    if df.empty:
        st.warning("No sales data found. Check that the database is seeded.")
        st.stop()

    st.sidebar.header("Filters")

    regions = sorted(df["region"].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect(
        "Region", regions, default=regions
    )

    categories = sorted(df["category"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "Product category", categories, default=categories
    )

    filtered = df[
        df["region"].isin(selected_regions)
        & df["category"].isin(selected_categories)
    ].copy()

    total_revenue = filtered["revenue"].sum()
    total_orders = filtered["order_id"].nunique()
    total_customers = filtered["customer_name"].nunique()
    average_order_value = (
        total_revenue / total_orders if total_orders else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    col2.metric("Orders", f"{total_orders:,}")
    col3.metric("Customers", f"{total_customers:,}")
    col4.metric("Average Order Value", f"₹{average_order_value:,.2f}")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Revenue over time")
        daily = (
            filtered.groupby("order_date", as_index=False)["revenue"]
            .sum()
            .sort_values("order_date")
        )
        fig = px.line(
            daily,
            x="order_date",
            y="revenue",
            markers=True,
            title="Daily revenue",
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Revenue by region")
        region_data = (
            filtered.groupby("region", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
        )
        fig = px.bar(
            region_data,
            x="region",
            y="revenue",
            color="region",
            title="Regional performance",
        )
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.subheader("Revenue by category")
        category_data = (
            filtered.groupby("category", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
        )
        fig = px.pie(
            category_data,
            names="category",
            values="revenue",
            hole=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Top 10 products")
        product_data = (
            filtered.groupby("product_name", as_index=False)["revenue"]
            .sum()
            .nlargest(10, "revenue")
            .sort_values("revenue")
        )
        fig = px.bar(
            product_data,
            x="revenue",
            y="product_name",
            orientation="h",
            title="Top products by revenue",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sales data")
    st.dataframe(
        filtered.sort_values("order_date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download filtered data as CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="businesslens_sales.csv",
        mime="text/csv",
    )

except Exception as exc:
    st.error(f"Could not load dashboard data: {exc}")
    st.info(
        "Check your .env credentials and confirm the database "
        "was seeded and the read-only user has SELECT permissions."
    )
finally:
    engine.dispose()
