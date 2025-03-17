
{{ config(
    materialized='view'
) }}

SELECT
    id as product_id,
    name as product_name,
    category as product_category,
    CAST(price as NUMERIC) as product_price,
    CAST(in_stock AS BOOL) is_available,
    ingested_date
FROM {{ source('source_product', 'products') }}

