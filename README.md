# Olist E-Commerce Analytics Platform

End-to-end data analytics pipeline built on 99,441 Brazilian 
e-commerce orders across 2017–2018.

## Tech Stack
- MySQL — relational database + KPI queries
- Python (pandas, SQLAlchemy) — ingestion pipeline
- Streamlit + Plotly — interactive dashboard
- SMTP — automated email alerting

## Project Structure
- `ingest.py` — loads 7 CSVs into MySQL with column mapping
- `app.py` — 5-page Streamlit dashboard
- `alert.py` — automated late delivery alerting
- `sql/` — schema, data quality, and KPI queries
- `business_summary.md` — findings in plain English

## Key Findings
- Revenue grew 4x in 18 months (R$271K → R$1.1M)
- Northern states take 2.5x longer to deliver than São Paulo
- 14 weeks breached the 10% late delivery threshold
- Health & Beauty leads on both revenue and customer satisfaction


## How to Run
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Set up MySQL and run `sql/01_schema.sql`
4. Update credentials in `ingest.py` and run it
5. Launch dashboard: `python -m streamlit run app.py`
6. Schedule `alert.py` for daily monitoring

## Data Quality
- Zero duplicate order IDs
- Zero timestamp violations  
- 20 payment mismatches investigated and confirmed legitimate
