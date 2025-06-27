{%- macro generate_alias_name(custom_alias_name=none, node=none) -%}

    {% set is_elementary =     (node.fqn is defined and 'elementary' in node.fqn[0])  %}
    {% set is_project_evaluator = (node.fqn is defined and 'dbt_project_evaluator' in node.fqn) %}
    {% set is_seeds =       (node.resource_type is defined and node.resource_type == 'seed') %}

    {%- if target.name == 'sbx' and not env_var('NO_PREFIX', false) and not (is_elementary or is_project_evaluator or is_seeds) -%}
        {%- if custom_alias_name is none -%}
            {{ env_var('USER', 'default') | replace('-', '_') | replace('.', '_') }}_{{ node.name }}
        {%- else -%}
            {{ env_var('USER', 'default') | replace('-', '_') | replace('.', '_') }}_{{ custom_alias_name | trim }}
        {%- endif -%}

    {%- else -%}
        {%- if custom_alias_name is none -%}
            {{ node.name }}
        {%- else -%}
            {{ custom_alias_name | trim }}
        {%- endif -%}
    {%- endif -%}

{%- endmacro %}
