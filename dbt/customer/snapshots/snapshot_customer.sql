
{% snapshot snapshot_customer %}
{{ config(
  target_schema=target.schema~"_snapshot",
  unique_key='customer_surrogate_key',
  strategy='check',
  check_cols=[
'customer_signup_at'],
  
) }}

SELECT * FROM {{ ref('int__customer') }}
{% endsnapshot %}
