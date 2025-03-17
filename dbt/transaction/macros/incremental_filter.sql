
{% macro incremental_filter() %}
    
    {% set query %}
        SELECT COALESCE(MAX(ingested_date), DATE("2000-01-01T01:01:00")) 
        FROM {{ this }}
    {% endset %}

    {% set result = run_query(query) %}
    {% set max_partition_date = result.columns[0][0] %}

    -- Return the value of max_partition_date
    {{ return(max_partition_date) }}
    
{% endmacro %}
