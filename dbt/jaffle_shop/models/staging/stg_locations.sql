{{ config(
    materialized='view',
    schema= 'js_staging',
    alias = 'locations',
    tags=["stg_locations"]
    )
}}

with

source as (

    select * from {{ source('ecom', 'stores') }}

),

renamed as (

    select

        ----------  ids
        id as location_id,

        ---------- text
        name as location_name,

        ---------- numerics
        tax_rate,

        ---------- timestamps
        {{ dbt.date_trunc('day', 'opened_at') }} as opened_at

    from source

)

select * from renamed
