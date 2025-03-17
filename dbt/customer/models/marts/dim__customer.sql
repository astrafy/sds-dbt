
{{ config(
    materialized='table',
    partition_by={
      "field": "customer_signup_at",
      "data_type": "DATE",
      "granularity": "DAY"
      },
    schema= 'company_dm_customer',
    cluster_by = ['customer_name', 'customer_email'],
    tags=["mart_customer"]
) }}

SELECT 
    customer_id,
    customer_name,
    customer_email,
    customer_country_code,
    customer_signup_at,
FROM {{ ref('int__customer') }}

