{{ config(
    materialized='table',
    schema= 'js_datamart',
    alias = 'supplies',
    tags=["mart_supplies"]
) }}

with

supplies as (

    select * from {{ ref('stg_supplies') }}

)

select * from supplies
