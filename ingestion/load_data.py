import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")


DB_HOST = os.getenv("DB_HOST", "host.docker.internal")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "dbt_ecommerce")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# --------------------------------------------------
# 2. Database connection
# --------------------------------------------------

engine = create_engine(
    "postgresql+psycopg2://",
    connect_args={
        "host": DB_HOST,
        "port": DB_PORT,
        "database": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
    },
)


# --------------------------------------------------
# 3. Read CSV
# --------------------------------------------------

csv_path = PROJECT_DIR / "data" / "orders.csv"

df = pd.read_csv(csv_path)

print("📄 CSV loaded")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# --------------------------------------------------
# 4. Clean data
# --------------------------------------------------

df.columns = df.columns.str.strip().str.lower()

df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="coerce"
)

df["quantity"] = pd.to_numeric(
    df["quantity"],
    errors="coerce"
)

df["unit_price"] = pd.to_numeric(
    df["unit_price"],
    errors="coerce"
)

df["revenue"] = df["quantity"] * df["unit_price"]

df = df.dropna(
    subset=[
        "order_id",
        "order_date",
        "customer_id",
        "quantity",
        "unit_price"
    ]
)

df = df.drop_duplicates(
    subset=["order_id"],
    keep="last"
)

print("🧹 Clean rows:", len(df))


# --------------------------------------------------
# 5. Check PostgreSQL table
# --------------------------------------------------

inspector = inspect(engine)

table_exists = inspector.has_table(
    "raw_orders",
    schema="public"
)


# --------------------------------------------------
# 6. First load
# --------------------------------------------------

if not table_exists:

    df.to_sql(
        "raw_orders",
        engine,
        schema="public",
        if_exists="replace",
        index=False
    )

    print("🆕 raw_orders table created")


# --------------------------------------------------
# 7. Incremental load
# --------------------------------------------------

else:

    staging_table = "raw_orders_staging"

    # Load incoming data into staging table
    df.to_sql(
        staging_table,
        engine,
        schema="public",
        if_exists="replace",
        index=False
    )

    with engine.begin() as connection:

        # Remove existing versions of incoming orders
        connection.execute(
            text("""
                DELETE FROM public.raw_orders
                WHERE order_id IN (
                    SELECT order_id
                    FROM public.raw_orders_staging
                );
            """)
        )

        # Insert latest versions
        connection.execute(
            text("""
                INSERT INTO public.raw_orders (
                    order_id,
                    order_date,
                    customer_id,
                    product,
                    category,
                    quantity,
                    unit_price,
                    region,
                    status,
                    revenue
                )
                SELECT
                    order_id,
                    order_date,
                    customer_id,
                    product,
                    category,
                    quantity,
                    unit_price,
                    region,
                    status,
                    revenue
                FROM public.raw_orders_staging;
            """)
        )

        # Remove staging table
        connection.execute(
            text("""
                DROP TABLE public.raw_orders_staging;
            """)
        )

    print("🔄 raw_orders updated successfully")


# --------------------------------------------------
# 8. Verify data
# --------------------------------------------------

with engine.connect() as connection:

    result = connection.execute(
        text("""
            SELECT COUNT(*)
            FROM public.raw_orders;
        """)
    )

    row_count = result.scalar_one()

    print("✅ Data loaded into PostgreSQL!")
    print("Rows in raw_orders:", row_count)