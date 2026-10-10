# BusinessLens AI

BusinessLens AI is a business analytics platform that transforms sales data into actionable insights through interactive dashboards and data visualization.

## Features

- Interactive sales analytics dashboard
- Revenue, order, customer, and average order value metrics
- Revenue analysis by region and product category
- Top-performing product analysis
- Region and category filters
- Downloadable sales data in CSV format
- MySQL database with synthetic business data
- Read-only database account for dashboard queries

## Tech Stack

- Python
- MySQL
- Pandas
- SQLAlchemy
- Streamlit
- Plotly

## Project Structure

```text
BusinessLens-AI/
├── app/
│   ├── config.py
│   └── dashboard.py
├── backend/
│   └── database.py
├── scripts/
│   ├── create_database.py
│   ├── seed_database.py
│   └── verify_database.py
├── tests/
├── knowledge_base/
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. Install Python and MySQL Server.
2. Create and activate a Python virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the local `.env` file using `.env.example` as a template.
5. Create the database and tables:

   ```bash
   python -m scripts.create_database
   ```

6. Generate sample data:

   ```bash
   python -m scripts.seed_database
   ```

7. Verify the database:

   ```bash
   python -m scripts.verify_database
   ```

8. Launch the dashboard:

   ```bash
   python -m streamlit run app/dashboard.py
   ```

## Revenue Definition

Revenue is calculated as:

`quantity × unit_price × (1 − discount)`

Cancelled orders are excluded from revenue calculations.

## Future Enhancements

- Natural-language business question answering
- AI-generated SQL with query validation
- Retrieval-augmented generation (RAG) for schema and business definitions

## Data

This project uses synthetic sample data for demonstration and educational purposes.