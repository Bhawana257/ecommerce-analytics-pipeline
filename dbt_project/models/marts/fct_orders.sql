{{ config(materialized='table') }}

SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    product,
    quantity,
    unit_price,
    revenue,
    status,
    region,
    ingested_at
FROM {{ ref('stg_orders') }}
