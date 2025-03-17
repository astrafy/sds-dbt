

{{ config(materialized='table') }}

SELECT
    t.transaction_id,
    t.customer_id,
    c.customer_name,
    t.transaction_amount,
    t.transaction_date,
    
FROM {{ ref('int__transaction') }} t
LEFT JOIN {{ ref('int__customer') }} c
    ON t.customer_id = c.customer_id

