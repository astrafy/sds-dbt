{% macro generate_schema_name(custom_schema_name=none, node=none) -%}

    {# Environments helper variables #}
    {% set is_dev =         modules.re.match('sbx|dev', target.name) %}
    {% set is_uat =         ('uat' in target.name ) %}
    {% set is_prd =         ('prd' in target.name ) %}

    {% if is_dev %}
        {% set suffix =     "dev" %}
    {% elif is_uat %}
        {% set suffix =     "uat" %}
    {% elif is_prd %}
        {% set suffix =     "prd" %}
    {%- endif -%}

    {% set is_export =     (node.config.export_as is not none)  %}
    {% if is_export %}
        {{- 'bqdts_' ~ node.config.schema_name -}}
    {%- else -%}
        {# Packages helpers variables #}

        {% set is_elementary =     ('elementary' in node.fqn[0])  %}
        {% set is_project_evaluator = ('dbt_project_evaluator' in node.fqn) %}
        {% if is_elementary %} {% set package = "_elementary" %}
        {% elif is_project_evaluator %} {% set package = "_project_evaluator" %}
        {%- endif -%}

        {%- set error_message_schema_provided -%}
            {{ node.resource_type | capitalize }} '{{ node.unique_id }}' has a schema configured. This is not allowed.
        {%- endset -%}

        {%- set error_message_no_rules -%}
            {{ node.resource_type | capitalize }} '{{ node.unique_id }}' has no rules defined for its schema.
        {%- endset -%}

        {%- if custom_schema_name is not none -%}
            {# handling test #}
            {%- if node.resource_type == 'test' and node.tags[0] == 'elementary' -%}  {{- 'bqdts_' ~ node.tags[1] ~ '_tests' -}}
            {%- elif node.resource_type == 'test' -%} {{- 'bqdts_' ~ node.tags[0] ~ '_tests' -}}
            {%- else -%}
                {{ exceptions.raise_compiler_error(error_message) }}
            {%- endif -%}

        {# Handling schema for dbt packages #}
        {%- elif custom_schema_name is none and node.path.split('/')[0] == 'dbt_logs' -%}
            {{- 'bqdts_dbt_logs' -}}
        {%- elif node.resource_type == 'seed' and not is_project_evaluator -%}
            {{- 'bqdts_mapping' -}}
        {%- elif custom_schema_name is none and (is_elementary or is_project_evaluator) -%}
            {{- 'bqdts_' ~ node.tags[0] ~ package -}}

        {%- elif custom_schema_name is none -%}
            {{- 'bqdts_' ~ node.tags[0] -}}
        {%- endif -%}
    {%- endif -%}

{%- endmacro %}
