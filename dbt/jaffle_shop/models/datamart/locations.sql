{{ config(
    materialized='table',
    schema= 'js_datamart',
    alias = 'locations',
    tags=["mart_locations"]
) }}


with

locations as (

    select * from {{ ref('stg_locations') }}

)

select * from locations
