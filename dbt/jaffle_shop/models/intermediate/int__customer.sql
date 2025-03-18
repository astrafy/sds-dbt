
{{ config(
    materialized='incremental',
    unique_key='customer_surrogate_key',
    incremental_strategy='merge',
    partition_by={
      "field": "customer_signup_at",
      "data_type": "DATE",
      "granularity": "DAY"
      },
    schema= 'company_int_customer',
    cluster_by = ['customer_surrogate_key'],
    tags=["int_customer"]
) }}

-- Merge changes from staging customer to ensure the latest data is maintained
SELECT
    customer_id,
    customer_name,
    customer_email,
    customer_country_code,
    customer_signup_at,
    {{ dbt_utils.generate_surrogate_key([
        'customer_id',
        'customer_email',
    ]) }}                               AS customer_surrogate_key
FROM {{ ref('stg__customer') }}
{% if is_incremental() %}
-- Only process records modified since the last run during incremental runs
WHERE customer_signup_at > (SELECT MAX(customer_signup_at) FROM {{ this }})
{% endif %}
QUALIFY ROW_NUMBER() OVER ( 
  PARTITION BY 
    customer_surrogate_key
        ORDER BY customer_signup_at ) = 1

