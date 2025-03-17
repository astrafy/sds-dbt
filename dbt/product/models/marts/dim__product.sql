
{{ config(
    materialized='incremental',
    unique_key='product_id',
    incremental_strategy='merge'
) }}

WITH base_product AS (
    -- STEP 1: Pull product data from `staging_product`
    SELECT
        product_id,
        product_name,
        product_category,
        product_price,
        is_available,
        ingested_date
    FROM {{ ref('int__product') }} -- Source staging table
)

select * from base_product as bp

{% if is_incremental() %}
-- STEP 4: Incremental logic – Only process new or updated rows
WHERE bp.ingested_date > (SELECT MAX(ingested_date) FROM {{ this }})
{% endif %}
QUALIFY ROW_NUMBER() OVER ( 
  PARTITION BY 
    product_id
        ORDER BY ingested_date ) = 1
