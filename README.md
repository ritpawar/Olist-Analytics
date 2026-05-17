# Olist E-Commerce Analytics

End-to-end data analytics pipeline built on 99,441 Brazilian e-commerce orders.

## Tools Used
- MySQL — database and KPI queries
- Python — data ingestion and automation
- Streamlit + Plotly — interactive dashboard
- SMTP — automated email alerting

## Project Structure
olist-analytics/
├── sql/
│   ├── 01_schema.sql        # Database schema
│   ├── 02_data_quality.sql  # Data validation queries
│   └── 03_kpis.sql          # Business KPI queries
├── ingest.py                # Loads CSVs into MySQL
├── app.py                   # Streamlit dashboard
├── alert.py                 # Automated email alerting
├── requirements.txt         # Python dependencies
└── business_summary.md      # Findings in plain English

## Key Findings
- Revenue grew 4x in 18 months — R$271K to R$1.1M
- Northern states take 2.5x longer to deliver than São Paulo
- 14 weeks breached the 10% late delivery threshold
- Health & Beauty leads on both revenue and customer satisfaction

## How to Run

**1. Install dependencies**
pip install -r requirements.txt

**2. Set up the database**
- Create a MySQL database called `olist`
- Run `sql/01_schema.sql` in MySQL Workbench

**3. Load the data**
- Download the Olist dataset from Kaggle
- Update credentials in `ingest.py`
- Run `python ingest.py`

**4. Launch the dashboard**
python -m streamlit run app.py

**5. Run the alert script**
python alert.py


## Data Quality
- Zero duplicate order IDs
- Zero timestamp violations
- 20 payment mismatches confirmed as legitimate split-payment transactions

## Dataset
[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
