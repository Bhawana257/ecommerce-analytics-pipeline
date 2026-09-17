import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

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

CARTS_API_URL = "https://dummyjson.com/carts?limit=0"
USERS_API_URL = "https://dummyjson.com/users?limit=0"

print("?? Fetching carts from DummyJSON API...")

carts_response = requests.get(CARTS_API_URL, timeout=30)
carts_response.raise_for_status()
carts = carts_response.json()["carts"]

print(f"?? Carts received: {len(carts)}")

print("?? Fetching users from DummyJSON API...")

users_response = requests.get(USERS_API_URL, timeout=30)
users_response.raise_for_status()
users = users_response.json()["users"]

print(f"?? Users received: {len(users)}")

user_regions = {}

for user in users:
    address = user.get("address", {})
    user_regions[user["id"]] = address.get("state", "Unknown")

rows = []

for cart in carts:
    customer_id = cart["userId"]
    region = user_regions.get(customer_id, "Unknown")

    for product in cart["products"]:
        rows.append(
            {
                "order_id": cart["id"],
                "customer_id": customer_id,
                "product_id": product["id"],
                "product": product["title"],
                "quantity": product["quantity"],
                "unit_price": product["price"],
                "revenue": product["discountedTotal"],
                "status": "Completed",
                "order_date": datetime.now().date() - timedelta(days=cart["id"] % 30),
                "region": region,
                "ingested_at": datetime.now(),
            }
        )

df = pd.DataFrame(rows)

print(f"?? Product rows created: {len(df)}")

with engine.begin() as conn:
    conn.execute(
        text(
            "ALTER TABLE raw_api_orders "
            "ADD COLUMN IF NOT EXISTS region TEXT"
        )
    )

    conn.execute(text("DELETE FROM raw_api_orders"))

df.to_sql(
    "raw_api_orders",
    engine,
    if_exists="append",
    index=False,
)

print("? API data loaded into PostgreSQL!")
print(f"Rows in raw_api_orders: {len(df)}")
print(f"Regions populated: {df['region'].nunique()}")
