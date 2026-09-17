{{ config(materialized='table') }}

SELECT
    order_date,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_items,
    SUM(revenue) AS total_revenue,
    AVG(revenue) AS average_order_value
FROM {{ ref('fct_orders') }}
WHERE status = 'Completed'
GROUP BY order_date
ORDER BY order_date