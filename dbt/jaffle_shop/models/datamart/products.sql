{{ config(
    materialized='table',
    schema= 'js_datamart',
    alias = 'products',
    tags=["mart_products"]
) }}

with

products as (

    select * from {{ ref('stg_products') }}

)

select * from products
