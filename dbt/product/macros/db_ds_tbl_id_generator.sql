{% macro generate_alias_name(custom_alias_name=none, node=none) -%}
    {{ common.generate_alias_name(custom_alias_name, node) }}
{%- endmacro %}
