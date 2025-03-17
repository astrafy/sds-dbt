# dbt Product package
The product package focuses on creating models that define product dimensions and provide a full example of how to use test, singular test, generic tests and unit tests.

<details id="how_to_dbt_product">
  <summary><strong>How to execute dbt Product package </strong></summary>

The dbt Product package is independent from the others.

- Position your self with the terminal in the folder ``dbt Training project fulll/dbt/product`` and run ```dbt deps```
    - All at once
        - `dbt build --select tag:product` : it will run all the dbt model and all the dbt tests 
          - Per model: in the `dbt_ppoject.yml` structure (as shown below) it has been defined for each layer a tag so all the model with each layer can be triggered together (ref: https://docs.getdbt.com/reference/resource-configs/tags)
              ``` YAML 
                  models:
                      product:
                          +persist_docs:
                            relation: true
                            columns: true
                          +schema: demo_dbt
                          +tags: product
                          +incremental_strategy: "insert_overwrite"
                          +materialized: "incremental"
                          staging:
                            +tags: stg_product
                          intermediate:
                            +tags: int_product
                          marts:
                            +tags: mart_product
              ```    
              - `dbt run --select tag:stg_product` : it will run the staging models
              - `dbt run --select tag:int_product` : it will run the intermediate models
              - `dbt run --select tag:mart_product` : it will run the mart models
        
              The dbt run command will not execute test. In that case you will need to run dbt test command
        
              - Either `dbt test --select tag:product` or as mention before for granular tag.
</details>
<details>
  <summary><strong>dbt_project.yml </strong></summary>

You will find the reference to the profile that is used in the repo, the variable needed and some global information like

- `schema`: the schema for Google Cloud BigQuery project where dbt is going to write the table
- `tags`: the definition of tag used while running dbt `dbt build --select tag:product`
- `materialization`: the type of materialization used.
- `vars`: the list of variables that you are going to use in your dbt transformation logic with their default value.

⚠️ **Small reminder:** all those values are global. However, every time a model has configured one of the values, it will overwrite the one specified in the dbt_project.yml
</details>

## Data Layers

<details>
  <summary><strong>Sources</strong></summary>

This is where everything begins. In the **Sources** layer, you will find the landing zone tables that serve as the raw 
data inputs for your staging models.

</details>

<details>
  <summary><strong>Staging</strong></summary>

- Each package includes its own staging models to clean and normalize raw data.
- Staging models are materialized as **views**, ensuring light and performant transformations.

</details>

<details>
  <summary><strong>Intermediate</strong></summary>

The **Intermediate** layer builds pre-aggregations (e.g., `int__customer`) that support reporting and dashboards by 
providing specific metrics.

</details>

<details>
  <summary><strong>Marts</strong></summary>

- **Dimension Models**: Dimensional models (e.g., `dim_customer`, `dim_product`) provide enriched, analytical-ready data 
for each domain.
- **Fact Models**: Fact models (e.g., `fact_transactions`) join and reference the dimensional models to produce validated 
and enriched transactional data.

</details>

### Tests
<details>
dbt offers several types of testing to ensure data quality and accuracy within your data warehouse.  These tests help 
catch errors early in the development process, improving the reliability of your data transformations.

<details>
  <summary><strong>1. Source Tests</strong></summary>
These tests verify the quality of your source data before it's transformed by dbt models. They ensure that the data 
you're pulling into your warehouse is accurate and complete. They typically check for data type validation, null values,
and other data quality issues. <br>
   
*Example: A source test might check if a column in a source table is always a valid date format or if a required column 
contains any null values.*
   
```
version: 2
    sources:
    - name: my_source
        tables:
        - name: my_table
            schema: public
            tests:
            - name: unique_id
                config:
                unique_key: id
            - name: not_null_name
                config:
                not_null: name
            - name: valid_date
                config:
                accepted_values:
                    - type: date
                    column: date
   ```

This YAML defines three tests:
- `unique_id`: Ensures that the id column contains only unique values.
- `not_null_name`: Checks that the name column doesn't contain any NULL values.
- `valid_date`: Verifies that the date column contains valid date values
    
**Best Practices**: Define comprehensive source tests to catch data quality problems early in the pipeline.
</details>

<details>
  <summary><strong>2. Data Tests</strong></summary>
These tests are more general and can be used to verify various aspects of your data, including data quality, consistency, 
and relationships between different tables. Data tests are defined using dbt's testing macros and can be customized to 
perform a wide range of checks.  

*Example: A data test might check for referential integrity between two tables, ensure that a particular column's values 
fall within a specific range, or verify that aggregated values match expectations.* 

```SQL
    -- macros/data_tests.sql
    
    {% macro check_range(model, column_name, min_value, max_value) %}
    SELECT COUNT(*)
    FROM {{ model }}
    WHERE {{ column_name }} < {{ min_value }} OR {{ column_name }} > {{ max_value }}
    {% endmacro %}

    -- models/my_model.sql
    {{ config(materialized='table') }}

    SELECT * FROM {{ source('my_source', 'my_table') }}
    
    -- models/my_model_tests.yml
    version: 2
    models:
    - name: my_model
        tests:
        - test_name: check_age_range
            macro: dbt_utils.check_range
            args:
            - model: ref('my_model')
            - column_name: age
            - min_value: 0
            - max_value: 120
```

**Best Practices**: Use data tests to enforce business rules and data quality constraints that span multiple models or tables.
</details>

<details>
  <summary><strong>3. Schema Tests</strong></summary>

These tests verify the structure and schema of your models and tables. They ensure that the data types, column names, 
and other. They are defined in the `<model.yml>` file that you want to test. Can be at model layer or more granular a column layer.
Please refer `dim__product.yml`. <br>

*Example: A schema test might check if a column has the correct data type (e.g., INTEGER, VARCHAR) or if a required column exists.*

**Best Practices**: Use schema tests to maintain consistency and prevent schema drift in your data warehouse.

</details>

<details id="unit_test_consideration">
  <summary><strong>4. Unit Tests</strong></summary>

These tests focus on individual dbt models (SQL scripts that transform data). They verify that each model produces the expected output based on its input data. They are isolated and independent, making them easy to write, run, and debug.

*Example: A unit test might check if a calculated column in a model accurately reflects the expected values based on other columns in the same model.* 

**Best Practices**: Keep unit tests focused on individual models and their immediate outputs. Avoid testing complex interactions between multiple models at this level. Please refer the `test_dim_product` in the `dim_product.yml` where it is tested the logic of incremental. 
    <br>
    <br>To understand better how it works check this [considerations](#unit_test_consideration)
</details>
</details>
<details>
  <summary><strong>Unit test consideration </strong></summary>

The test has been created in order to test and check the incremental logic. 

In this specific use case we are defining a merge stategy which means that
dbt create a temporary table then generates and executes the **`MERGE` statement** to propagate changes into the target table. 
The `MERGE` operation includes two main actions:
1. **Update Existing Records**:
    - dbt **matches records in the target table** (`{{ this }}`) to records in the temporary table based on the `unique_key` (in this case, `product_id`).
    - If a match is found, dbt **updates the target table's existing records** with the most recent values from the temporary table.
2. **Insert New Records**:
    - If no matching record is found in the target table, dbt **inserts the record from the temporary table** into the target table.

Refer here for more explanation: https://docs.getdbt.com/docs/build/incremental-models


Considering now the following scenario and keeping in mind that the SQL model is as per follow

``` SQL

{{ config(
    materialized='incremental',
    unique_key='product_id',
    incremental_strategy='merge'
) }}

WITH base_product AS (
    -- STEP 1: Pull product data from `staging_product`
    SELECT
        product_id,
        product_name,
        product_category,
        product_price,
        is_available,
        ingested_date
    FROM {{ ref('int__product') }} -- Source staging table
)

select * from base_product as bp

{% if is_incremental() %}
-- STEP 4: Incremental logic – Only process new or updated rows
WHERE bp.ingested_date >= (SELECT MAX(ingested_date) FROM {{ this }})
{% endif %}

```

Which basically we are loading data from the intermediate model `int__product` and for product having the same `product_id` we take the record that has a greater ingest_date.

**Normally all the product ingested at in the same batch they have the same ingest_date**

Use case Unit test scenario

1. **SUCCES**
   ``` YAML
    unit_tests:
     - name: test_dim_product
       model: dim__product
       overrides:
         macros:
           # unit test this model in "full refresh" mode
           is_incremental: true 
       given:
         - input: ref('int__product')
           rows:
             - product_id: 1
               product_name: "Laptop"
               product_price: 1200.00
               ingested_date: 2025-03-05
         - input: this
           rows:
             - product_id: 1
               product_name: "Laptop"
               product_price: 1200.00
               ingested_date: 2025-03-05
       expect:
         rows: []
    ```
    Which means
    * *inputs*:
      * `this` the data we have at current time in the current model `dim__product` 
      * the intermediate layer `int__product` where we are sourcing the data from and are representing the loading data
    * *expect*: the expectation of the test.
    
    In this case we are expecting 0 rows. Why? For rome reason in the loading data we are loading something that we have already you can see it because we have the same `product_id=1` and the `ingest_date=2025-03-05` so basically there is not data to merge or to append to the table itself.
      
2. **FAILURE**
    Considering now the following
    ```YAML
    given:
      - input: ref('int__product')
        rows:
          - product_id: 1
            product_name: "Laptop"
            product_price: 1400.00
            ingested_date: 2025-03-05
      - input: this
        rows:
          - product_id: 1
            product_name: "Laptop"
            product_price: 1200.00
            ingested_date: 2025-03-04
    expect:
      rows:
        - product_id: 1
          product_name: "Laptop"
          product_price: 1200.00
          ingested_date: 2025-03-04
    ```
    In this case the model it is going to fail because we should insert the raw that is coming from the `input__prodcut` due to the fact the ingest_date is greater than what we have in the `this` model but in the expected rows we are still having the *product_price* and the *ingest_date* refering the old record

    The output would be like
    ```
        @@,product_id,product_name,product_price,ingested_date
        → ,1         ,Laptop      ,1200→1400    ,2025-03-04→2025-03-05
    ```


3. **FAILURE**
    ```YAML
    given:
      - input: ref('int__product')
        rows:
          - product_id: 1
            product_name: "Laptop"
            product_price: 1400.00
            ingested_date: 2025-03-05
      - input: this
        rows:
          - product_id: 1
            product_name: "Laptop"
            product_price: 1200.00
            ingested_date: 2025-03-04
    expect:
      rows:
        - product_id: 1
          product_name: "Laptop"
          product_price: 1200.00
          ingested_date: 2025-03-05
    ```
    The same exact example as before. Only to make you clear the logic :). In this case it will fail again because as explained above the *product_price* is wrong
4. **SUCCESS**
    The Success test is the following for the example.
    ```YAML
    given:
      - input: ref('int__product')
        rows:
          - product_id: 1
            product_name: "Laptop"
            product_price: 1400.00
            ingested_date: 2025-03-05
      - input: this
        rows:
          - product_id: 1
            product_name: "Laptop"
            product_price: 1200.00
            ingested_date: 2025-03-04
    expect:
      rows:
        - product_id: 1
          product_name: "Laptop"
          product_price: 1400.00
          ingested_date: 2025-03-05
    ```
</details>

## Exercises

- [Exercise 1](./exercises/exercise_1.md)
- [Exercise 2](./exercises/exercise_2.md)
- [Exercise 3](./exercises/exercise_3.md)