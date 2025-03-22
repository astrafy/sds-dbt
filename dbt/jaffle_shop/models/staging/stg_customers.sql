
{{ config(
    materialized='table',
    schema= 'js_staging',
    alias = 'customer',
    tags=["stg_customer"]
    )
}}

with

source as (

    select * from {{ source('ecom', 'customers') }}

),

renamed as (

    select
        ----------  ids
        id as customer_id,
        ---------- text
        name as customer_name,
        bigfunctions.eu.faker("ascii_email", null) as customer_email,
        bigfunctions.eu.faker("country_code", null) as customer_country_code,
        CAST(bigfunctions.eu.faker("date", null) AS DATE) as customer_signup_at

    from source

)

select * from renamed
