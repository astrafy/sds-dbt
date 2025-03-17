{% macro generate_database_name(custom_database_name=none, node=none) -%}

    {# Environments helpers variables #}
    {% set is_dev =         ('dev' in target.name ) %}
    {% set is_uat =         ('uat' in target.name ) %}
    {% set is_prd =         ('prd' in target.name ) %}

    {% set is_export =     (node.config.export_as is not none)  %}
    {% if is_export and is_dev %}
      {{- 'internal-data-dm-dev-51ce' -}}
    {% elif is_export and is_uat %}
      {{- 'internal-data-dm-uat-de8a' -}}
    {% elif is_export and is_prd %}
      {{- 'internal-data-dm-prd-a412' -}}
    {%- else -%}
      {# Packages helpers variables #}
      {% set is_elementary =     ('elementary' in node.fqn[0])  %}
      {% set is_project_evaluator = ('dbt_project_evaluator' in node.fqn) %}
      {% set is_monitoring        = (is_elementary or is_project_evaluator or is_metrics) %}

      {# Data layers helpers variables #}
      {% set is_seeds =       (node.resource_type == 'seed') and not is_monitoring %}
      {% set is_test =        (node.resource_type == 'test') and not is_monitoring %}
      {% set is_analysis =    (node.resource_type == 'analysis') and not is_monitoring %}

      {% set is_layer_staging = ('staging' in node.fqn) and not is_monitoring and not is_test %}
      {% set is_layer_data_warehouse = (('data_warehouse' in node.fqn) or ('intermediate' in node.fqn)) and not is_monitoring and not is_test %}
      {% set is_layer_datamart = ('datamart' in node.fqn) and not is_monitoring and not is_test %}

      {% set is_on_end_hook = ('hooks' in node.fqn) %}

      {%- set error_unresolve_message -%}
          {{ node.resource_type | capitalize }} '{{ node.unique_id }}' unable to resolve database name.
      {%- endset -%}

      {%- if is_on_end_hook -%}
        {{- target.database | trim -}}

      {%- elif is_analysis -%}
        {{- target.database | trim -}}

      {# DEV (target: dev) #}
      {% elif is_dev %}
        {%- if   is_layer_staging -%}         {{- 'internal-data-stg-dev-27aa' -}}
        {%- elif is_layer_data_warehouse -%}  {{- 'internal-data-dw-dev-29ce'-}}
        {%- elif is_layer_datamart -%}        {{- 'internal-data-dm-dev-51ce' -}}
        {%- elif is_seeds -%}                 {{- 'internal-data-stg-dev-27aa' -}}
        {%- elif is_test -%}                  {{- 'internal-monitoring-dev-7e9d' -}}
        {%- elif is_project_evaluator -%}     {{- 'internal-monitoring-dev-7e9d' -}}
        {%- elif is_elementary -%}            {{- 'internal-monitoring-dev-7e9d' -}}
        {%- else -%}                          {{ exceptions.raise_compiler_error(error_unresolve_message) }}
        {%- endif -%}

      {# UAT (target: uat) #}
      {% elif is_uat %}
        {%- if   is_layer_staging -%}         {{- 'internal-data-stg-uat-b057' -}}
        {%- elif is_layer_data_warehouse -%}  {{- 'internal-data-dw-uat-c925'-}}
        {%- elif is_layer_datamart -%}        {{- 'internal-data-dm-uat-de8a' -}}
        {%- elif is_seeds -%}                 {{- 'internal-data-stg-uat-b057' -}}
        {%- elif is_test -%}                  {{- 'internal-monitoring-uat-ae85' -}}
        {%- elif is_project_evaluator -%}     {{- 'internal-monitoring-uat-ae85' -}}
        {%- elif is_elementary -%}            {{- 'internal-monitoring-uat-ae85' -}}
        {%- elif is_metrics -%}               {{- 'internal-data-dm-uat-de8a' -}}
        {%- else -%}                          {{ exceptions.raise_compiler_error(error_unresolve_message) }}
        {%- endif -%}


      {# PRD (target: prd) #}
      {% elif is_prd %}
        {%- if   is_layer_staging -%}       {{- 'internal-data-stg-prd-9970' -}}
        {%- elif is_layer_data_warehouse -%}  {{- 'internal-data-dw-prd-6502'-}}
        {%- elif is_layer_datamart -%}        {{- 'internal-data-dm-prd-a412' -}}
        {%- elif is_seeds -%}                 {{- 'internal-data-stg-prd-9970' -}}
        {%- elif is_test -%}                  {{- 'internal-monitoring-prd-afa4' -}}
        {%- elif is_project_evaluator -%}     {{- 'internal-monitoring-prd-afa4' -}}
        {%- elif is_elementary -%}            {{- 'internal-monitoring-prd-afa4' -}}
        {%- elif is_metrics -%}               {{- 'internal-data-dm-prd-a412' -}}
        {%- else -%}                          {{ exceptions.raise_compiler_error(error_unresolve_message) }}
        {%- endif -%}

      {%- else -%}
        {{ exceptions.raise_compiler_error(error_unresolve_message) }}
      {%- endif -%}
    {%- endif -%}
{%- endmacro %}
