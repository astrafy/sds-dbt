{{ config(
    materialized='view',
    schema= 'js_staging',
    alias = 'products',
    tags=["stg_products"]
    )
}}

with

source as (

    select * from {{ source('ecom', 'products') }}

),

renamed as (

    select

        ----------  ids
        sku as product_id,

        ---------- text
        name as product_name,
        type as product_type,
        description as product_description,


        ---------- numerics
        {{ cents_to_dollars('price') }} as product_price,

        ---------- booleans
        ---------- booleans
        case
            when type = 'jaffle' then 1
            else 0
        end as is_food_item,

        case
            when type = 'beverage' then 1
            else 0
        end as is_drink_item

    from source

)

select * from renamed
