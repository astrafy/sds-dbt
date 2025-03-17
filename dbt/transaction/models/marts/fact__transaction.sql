

{{ config(
    materialized='incremental', 
    unique_key='transaction_id',
    incremental_strategy='merge'
) }}

WITH base_transaction AS (
    -- STEP 1: Start with raw or staging transactional data
    SELECT
        transaction_id,
        customer_id,              -- FK to the `dim__customer` table
        product_id,               -- FK to the `dim__product` table
        transaction_date,
        transaction_amount,
        currency,                   -- Total revenue for this transaction
        CURRENT_TIMESTAMP AS last_updated -- Useful for incremental models
    FROM {{ ref('stg__transaction') }} -- Ensure `staging_transaction` is defined
),
currency_mapping AS (
    -- STEP 2: Use the currency seed to map currency_code to currency_text
    SELECT
        currency_code,
        currency_text
    FROM {{ ref('currencies') }}       -- Refers to the seed
),
enriched_transaction AS (
    -- STEP 2: Ensure foreign keys are valid using a JOIN or exclusion checks
    SELECT
        bt.transaction_id,
        bt.customer_id,
        bt.product_id,
        bt.transaction_date,
        bt.transaction_amount,
        bt.last_updated,
        cm.currency_text, 
    FROM base_transaction bt
    LEFT JOIN currency_mapping cm
    ON bt.currency = cm.currency_code
    LEFT JOIN {{ ref('dim__product') }} dp
      ON bt.product_id = dp.product_id
    LEFT JOIN {{ ref('dim__customer') }} dc
      ON bt.customer_id = dc.customer_id
    WHERE dp.product_id IS NOT NULL                -- Remove invalid product_ids
      AND dc.customer_id IS NOT NULL               -- Remove invalid customer_ids
)

-- STEP 3: Final output for the fact table
SELECT *
FROM enriched_transaction

{% if is_incremental() %}
-- Include only new or updated transaction in incremental runs
WHERE last_updated > (SELECT MAX(last_updated) FROM {{ this }})
{% endif %}
QUALIFY ROW_NUMBER() OVER ( 
  PARTITION BY 
    transaction_id
        ORDER BY last_updated ) = 1


