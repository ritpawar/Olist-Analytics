import pandas as pd
from sqlalchemy import create_engine

DB_USER     = "root"
DB_PASSWORD = "Password"
DB_HOST     = "localhost"
DB_NAME     = "olist"
DATA_FOLDER = r"C:\Users\Rutuja\Downloads\archive"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
print("Connected to MySQL successfully")

files = {
    "customers"  : "olist_customers_dataset.csv",
    "sellers"    : "olist_sellers_dataset.csv",
    "products"   : "olist_products_dataset.csv",
    "orders"     : "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments"   : "olist_order_payments_dataset.csv",
    "reviews"    : "olist_order_reviews_dataset.csv",
    "category_translation" : "product_category_name_translation.csv",
}

# Rename CSV columns to match our schema
column_renames = {
    "customers": {
        "customer_zip_code_prefix": "zip_code_prefix",
        "customer_city"           : "city",
        "customer_state"          : "state"
    },
    "sellers": {
        "seller_zip_code_prefix": "zip_code_prefix",
        "seller_city"           : "city",
        "seller_state"          : "state"
    },
    "products": {
        "product_category_name"            : "category_name",
        "product_name_lenght"              : "name_length",
        "product_description_lenght"       : "description_length",
        "product_photos_qty"               : "photos_qty",
        "product_weight_g"                 : "weight_g",
        "product_length_cm"                : "length_cm",
        "product_height_cm"                : "height_cm",
        "product_width_cm"                 : "width_cm"
    },
    "orders": {
        "order_purchase_timestamp"  : "purchase_timestamp",
        "order_approved_at"         : "approved_at",
        "order_delivered_carrier_date"  : "delivered_carrier_at",
        "order_delivered_customer_date" : "delivered_customer_at",
        "order_estimated_delivery_date" : "estimated_delivery"
    },
    "order_items": {
        "shipping_limit_date": "shipping_limit_date"
    },
    "payments": {
        "payment_sequential"   : "payment_sequential",
        "payment_type"         : "payment_type",
        "payment_installments" : "payment_installments",
        "payment_value"        : "payment_value"
    },
    "reviews": {
        "review_score"              : "score",
        "review_comment_title"      : "comment_title",
        "review_comment_message"    : "comment_message",
        "review_creation_date"      : "creation_date",
        "review_answer_timestamp"   : "answer_timestamp"
    },
    "category_translation": {
    "product_category_name"         : "category_name_portuguese",
    "product_category_name_english" : "category_name_english"
    }
}

for table, filename in files.items():
    filepath = f"{r"C:\Users\Rutuja\Downloads\archive"}\\{filename}"
    print(f"Loading {filename} → {table}...")
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()

    if table in column_renames:
        df = df.rename(columns=column_renames[table])

    df.to_sql(
        name      = table,
        con       = engine,
        if_exists = "append",
        index     = False
    )
    print(f"  Done — {len(df):,} rows loaded")

print("\nAll tables loaded successfully!")
