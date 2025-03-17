
{{ config(
    materialized='view',
    schema= 'company_stg_customer',
    tags=["stg_customer"]
    ) 
}}

SELECT
    id as customer_id,
    UPPER(name) as customer_name,
    LOWER(email) as customer_email,
    country as customer_country_code,
    signup_date as customer_signup_at,
    ingested_date
FROM  {{ source('source_customer', 'customers') }}
