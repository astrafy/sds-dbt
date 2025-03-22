{{ config(
    materialized='view',
    schema= 'js_staging',
    alias = 'order_items',
    tags=["stg_order_items"]
    )
}}

with

source as (

    select * from {{ source('ecom', 'items') }}

),

renamed as (

    select

        ----------  ids
        GENERATE_UUID() as order_item_id,
        GENERATE_UUID() as order_id,
        sku as product_id

    from source

)

select * from renamed
