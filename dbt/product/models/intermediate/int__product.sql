
{{ config(
    materialized='incremental',
    unique_key='product_id',
    incremental_strategy='merge'
) }}

SELECT 
    product_id,
    product_name,
    product_category,
    product_price,
    is_available,
    ingested_date
FROM {{ ref('stg__product') }}

{% if is_incremental() %}
-- STEP 4: Incremental logic – Only process new or updated rows
WHERE ingested_date > (SELECT MAX(ingested_date) FROM {{ this }})
{% endif %}
QUALIFY ROW_NUMBER() OVER ( 
  PARTITION BY 
    product_id
        ORDER BY ingested_date ) = 1
