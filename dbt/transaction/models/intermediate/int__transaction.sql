
{{ config(
    materialized='incremental',
    incremental_strategy="insert_overwrite",
    partition_by={"field": "transaction_date", "data_type": "DATE"}
) }}


with source_transactions as (
    SELECT
    *
    FROM {{ ref('stg__transaction') }}
)

select * from source_transactions

{% if is_incremental() %}
    {% set max_partition_date = incremental_filter() %}
    WHERE ingested_date >= '{{ max_partition_date }}'
{% endif %}
QUALIFY ROW_NUMBER() OVER ( 
  PARTITION BY 
    transaction_id
        ORDER BY ingested_date ) = 1

