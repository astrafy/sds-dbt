# dbt Transaction package
The transaction package focuses on creating models that define transaction dimensions and provide enriched insights into 
transactions behavior. It’s used for tracking and build reports on top of it, aggregating data with product and customer.
<details id="how_to_dbt_product">
  <summary><strong>How to execute dbt Transaction package </strong></summary>


The dbt Transaction is depending from customer and product so be sure to run the dbt models respective before

- Position your self with the terminal in the folder ``dbt Training project fulll/dbt/transaction`` and run ``` dbt deps ```
- This specific model is using seeds so you need to create them ``` dbt seed ```
    - All at once
        - `dbt build --select tag:transaction` : it will run all the dbt model and all the dbt tests 
    - Per model: in the `dbt_pproject.yml` structure (as shown below) it has been defined for each layer a tag so all 
  the model with each layer can be triggered together (ref: https://docs.getdbt.com/reference/resource-configs/tags)
        ``` YAML 
            models:
                transaction:
                    +persist_docs:
                    relation: true
                    columns: true
                    +schema: demo_dbt
                    +tags: transaction
                    +incremental_strategy: "insert_overwrite"
                    +materialized: "incremental"
                    staging:
                    +tags: stg_transaction
                    intermediate:
                    +tags: int_transaction
                    marts:
                    +tags: mart_transaction

        ```    
        - `dbt run --select tag:stg_transaction` : it will allow to run the staging model
        - `dbt run --select tag:int_transaction` : it will allow to run the intermediate model
        - `dbt run --select tag:mart_transaction` : it will allow to run the mart model
        
        The dbt run command will not execute test. In that case you will need to run dbt test command
        
        - Either `dbt test --select tag:transaction` or as mention before for granular tag.
</details>
<details>
  <summary><strong>dbt_project.yml </strong></summary>
You will find the reference to the profile that is used in the repo, the variable needed and some global information like

- `schema`: the schema for Google Cloud BigQuery project where dbt is going to write the table
- `tags`: the definition of tag used while running dbt `dbt build --select tag:customer`
- `materialization`: the type of materialization used.
- `vars`: the list of variables that you are going to use in your dbt transformation logic with their default value.

⚠️ **Small reminder:** all those values are global. However, every time a model has configured one of the values, it 
will overwrite the one specified in the dbt_project.yml

</details>

## Data Layers

<details>
  <summary><strong>Sources</strong></summary>

This is where everything begins. Here, you will find the sources that are needed in your models, what we call the landing 
zone tables that we are referring to in our staging.

In this particular use case we have 3 different source tables
1. **transactions_eu**: containing only the transaction coming from Europe
2. **transactions_us**: containing only the transaction coming from US
3. **transactions_uk**: containing only the transaction coming from UK

</details>

<details>
  <summary><strong>Staging</strong></summary>

- Each package has its own staging models to clean and normalize raw data.
- Stage models are materialized as **views**, ensuring light and performant transformations.

<aside>⚠️ There is a peculiarity here if you check in the code `stg__transaction.sql` </aside>

``` SQL

{{transactions_fields("transactions_eu")}}
union all
{{transactions_fields("transactions_us")}}
union all
{{transactions_fields("transactions_uk")}}

```
In the model we are doing an union between all the tables coming from all the different region calling a macro `transactions_fields`
</details>

<details>
  <summary><strong>Macros</strong></summary>
Macros are like function the programming language that allow you to extract a logic that can be reused in different part of your model. 

For example, as mentione above, in the `stg__transaction` we have the following macro that is doing the same transformation independently from the region since the schema of the table is the same.

``` SQL

{% macro transactions_fields(source_table) %}
    SELECT
    
    id as transaction_id,
    customer_id,
    product_id,
    currency,
    CAST(amount AS NUMERIC) as transaction_amount,
    transaction_date,
    ingested_date

    from   {{ source("source_transaction", source_table) }}
{%- endmacro %}

```
In addition in the folder there is a macro called `incremental_filter` that is used to incapsulate the logic of incremental since it could be a repeatable code it is better to put in a macro. It will return the max partition date. It can be used in the code as per follow:

``` SQL

    {% if is_incremental() %}
        {% set max_partition_date = incremental_filter() %}
        WHERE column_date >= '{{ max_partition_date }}' --change the column_date with the name of the column of your model
    {% endif %}

```

</details>

<details>
  <summary><strong>Model Ephemeral</strong></summary>
Instead of calling a macro we could use as well an ephemeral model, what is an ephemeral model? it is a model that you 
can reference in other SQL model without being materialized. It will perform a CTE. 
Please refer here for more documentation https://docs.getdbt.com/docs/build/materializations#ephemeral

In that case what we would have is under the folder *`staging/base/transaction_fields.sql`* that will look like

```SQL

{{ config(
    materialized='ephemeral'
) }}

    SELECT
        id as transaction_id,
        customer_id,
        product_id,
        currency,
        CAST(amount AS NUMERIC) as transaction_amount,
        transaction_date,
        ingested_date
    from   {{ source("source_transaction", "transactions_eu") }}
    
    UNION ALL
    
    SELECT
        id as transaction_id,
        customer_id,
        product_id,
        currency,
        CAST(amount AS NUMERIC) as transaction_amount,
        transaction_date,
        ingested_date
    from   {{ source("source_transaction", "transactions_us") }}
    
    UNION ALL
    
    SELECT
        id as transaction_id,
        customer_id,
        product_id,
        currency,
        CAST(amount AS NUMERIC) as transaction_amount,
        transaction_date,
        ingested_date
    from   {{ source("source_transaction", "transactions_uk") }}


```

At this point the staging `stg__transaction.sql` looks like


```SQL


{{ config(
    materialized='view'
) }}

select * from {{ref("transaction_fields")}}


```
</details>

<details>
  <summary><strong>Intermediate</strong></summary>

Build pre-aggregations (e.g., `int__customer`) for specific metrics to support reporting and dashboards.

</details>

<details>
  <summary><strong>Marts</strong></summary>

- Dimension: The dimensional models (e.g., dim_customer, dim_product) provide enriched, analytical-ready data for each domain.
- Fact: The fact model (fact_transactions) joins and references the dimensional models for validated and enriched transactional data.

</details>

<details>
  <summary><strong>Seed</strong></summary>

Seed are used to represent mapping, static table that are not changing often (or even better never) with a small amount of data that are used to do look up/enrich your model in CSV format: https://docs.getdbt.com/docs/build/seeds

In Transaction use case we are using a seed for currency under `seeds/currencies.csv` to enrich the currency information with the description of the currency in the `fact__transaction.sql`.

</details>

## Tests

<details>
  <summary><strong>Unit test</strong></summary>
The test has been created in order to test and check the incremental logic. 
In this specific use case we are defining a merge stategy which means (in few words).

The behavior depends heavily on how your dbt model and the underlying data warehouse are partitioned.  To give you a precise explanation, I need information on:

1. Partitioning Key: What column(s) are used as the partitioning key in your target table?  This is crucial because the `insert_overwrite` operation will affect partitions based on this key.
2. Partitioning Scheme: How is your data warehouse partitioned?  (e.g., range partitioning, list partitioning, hash partitioning).  Different schemes will lead to different behaviors during the overwrite.
3. dbt Model Code:  Seeing the actual dbt model code (the SQL) will help me understand how the data is loaded and transformed before the `insert_overwrite` operation.  This will show how the partitioning key is handled within the model's logic.
4. Incremental Strategy Implementation: How is the incremental logic implemented within your dbt model?  This will clarify how the temporary table is created and how the overwrite happens.  Is it using a WHERE clause to filter data based on the partition key?

General Concepts: Assuming your target table is partitioned by a column like date, an `insert_overwrite` strategy would likely work as follows:
* Temporary Table Creation:  The incremental model creates a temporary table containing only the data for the new partition (or partitions) being updated.  This is usually achieved by filtering the source data based on the date column.
* Partition-Specific Overwrite: Instead of overwriting the entire target table, the `insert_overwrite` operation would only affect the specific partition(s) containing the data in the temporary table.  The other partitions would remain untouched.  This is a more efficient approach than overwriting the entire table.
* Underlying Data Warehouse Behavior: The exact mechanism for the partition-specific overwrite depends on your data warehouse's capabilities.  Some warehouses might allow direct replacement of individual partitions, while others might require more complex operations involving dropping and recreating partitions.

Considering now the following scenario and keeping in mind that the SQL model `int__transaction.sql` is as per follow
``` SQL

{{ config(
    materialized='incremental',
    incremental_strategy="insert_overwrite",
    partition_by={"field": "transaction_date", "data_type": "DATE"}
) }}


with source_transactions as (
    SELECT
    *
    FROM {{ ref('stg__transaction') }}
)

select * from source_transactions

{% if is_incremental() %}
    {% set max_partition_date = incremental_filter() %}
    WHERE ingested_date >= '{{ max_partition_date }}'
{% endif %}


```
Which means taht the the model `int__transaction.sql` is partitioned by ***transaction_date***. We are considering the ***ingested_date*** to get the incremental delta from the staging.
So basically all the time that we are reloading data we overwrite all the transaction for a specific date because it means that updates has been done.

## Example of dbt `insert_overwrite` Strategy

In this example, we use dbt's `insert_overwrite` strategy to refresh data for a specific partition (`transaction_date`) while leaving the rest of the table intact.

### Scenario

We have an existing `transactions` table, which is partitioned by `transaction_date`, and we want to update only the records for `transaction_date >= '2025-03-03'`. Here’s how it works:

### Initial Table Data (`stg__transaction`):

| transaction_id | customer_id | product_id | currency | transaction_amount | transaction_date | ingested_date |
|----------------|-------------|------------|----------|--------------------|------------------|---------------|
| 1001           | 2001        | 3001       | USD      | 150.00             | 2025-03-01       | 2025-03-02    |
| 1002           | 2002        | 3002       | EUR      | 130.00             | 2025-03-02       | 2025-03-03    |
| 1003           | 2003        | 3003       | USD      | 180.00             | 2025-03-05       | 2025-03-06    |

### New Data for Insert Overwrite (`stg__transaction`):

| transaction_id | customer_id | product_id | currency | transaction_amount | transaction_date | ingested_date |
|----------------|-------------|------------|----------|--------------------|------------------|---------------|
| 1003           | 2003        | 3003       | USD      | 180.00             | 2025-03-05       | 2025-03-06    |
| 1004           | 2004        | 3004       | EUR      | 200.00             | 2025-03-06       | 2025-03-07    |

### Model Example (`int__transaction.sql`):

``` SQL

{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by={'field': 'transaction_date', 'data_type': 'date'}
) }}

WITH source_transactions AS (
    SELECT * 
    FROM {{ ref('stg__transaction') }}  -- Source table with new records
)

SELECT *
FROM source_transactions

{% if is_incremental() %}
    WHERE transaction_date >= '2025-03-03'  -- Filter to only include recent records
{% endif %} 


```

### After `insert_overwrite` Strategy:

- **Delete** data for `transaction_date >= '2025-03-03'`.
- **Insert** new data where `transaction_date >= '2025-03-03'`.

### Final Table Data after `insert_overwrite`:

| transaction_id | customer_id | product_id | currency | transaction_amount | transaction_date | ingested_date |
|----------------|-------------|------------|----------|--------------------|------------------|---------------|
| 1001           | 2001        | 3001       | USD      | 150.00             | 2025-03-01       | 2025-03-02    |
| 1002           | 2002        | 3002       | EUR      | 130.00             | 2025-03-02       | 2025-03-03    |
| 1003           | 2003        | 3003       | USD      | 180.00             | 2025-03-05       | 2025-03-06    |
| 1004           | 2004        | 3004       | EUR      | 200.00             | 2025-03-06       | 2025-03-07    |

</details>


## Exercises

- [Exercise 1](./exercises/exercise_1.md)
- [Exercise 2](./exercises/exercise_2.md)
- [Exercise 3](./exercises/exercise_3.md)