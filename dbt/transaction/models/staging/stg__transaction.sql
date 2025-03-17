
{{ config(
    materialized='view'
) }}


{{transactions_fields("transactions_eu")}}
union all
{{transactions_fields("transactions_us")}}
union all
{{transactions_fields("transactions_uk")}}

