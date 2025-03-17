
{% macro transactions_fields(source_table) %}
    SELECT
    
    id as transaction_id,
    customer_id,
    product_id,
    currency,
    CAST(amount AS NUMERIC) as transaction_amount,
    transaction_date,
    ingested_date

    from   {{ source("source_transaction", source_table) }}
{%- endmacro %}
