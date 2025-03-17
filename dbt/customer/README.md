# dbt Customer Package

The **dbt Customer Package** focuses on creating models that define customer dimensions and provide enriched insights 
into customer behavior. It is used for tracking customers, their attributes, and metadata to better understand customer 
segments and behavior.

<details id="how_to_dbt_customer">
  <summary><strong>How to run the dbt Customer data product </strong></summary>

The dbt Customer Package operates independently from the other packages.

From your terminal, navigate to the ``dbt Training project fulll/dbt/customer`` directory and execute the following commands:

<details>
  <summary><strong>Run All Models at Once</strong></summary>

Execute:
    dbt deps
    
    dbt build --select tag:customer
     
    dbt snapshot --select snapshot_customer
    
</details>

<details>
  <summary><strong>Run Models by Tag</strong></summary>

  Each SQL model includes a tag in its configuration, enabling you to run groups of models:
  - To run staging models:
    ```bash
    dbt run --select tag:stg_customer
    ```
  - To run intermediate models:
    ```bash
    dbt run --select tag:int_customer
    ```
  - To run mart models:
    ```bash
    dbt run --select tag:mart_customer
    ```
</details>
&nbsp;

**Note:** The `dbt run` command does not execute tests. To run tests, use:

&nbsp;

  ```bash
  dbt test --select tag:customer
  ```
</details>

<details>
  <summary><strong>dbt_project.yml</strong></summary>

This file references the profile used in the repository, defines necessary variables, and includes some global configurations such as:

- `schema`: The schema in the Google Cloud BigQuery project where dbt writes the tables.
- `tags`: The tags used when running dbt commands (e.g., `dbt build --select tag:customer`).
- `materialization`: The type of materialization applied to models.
- `vars`: The list of variables used in your dbt transformation logic along with their default values.

⚠️ **Reminder:** These values are global. However, if a model configures any of these settings individually, it will 
override the corresponding value specified in `dbt_project.yml`.
</details>

## Data Layers

<details>
  <summary><strong>Sources</strong></summary>

This is where everything begins. In the **Sources** layer, you will find the landing zone tables that serve as the 
raw data inputs for your staging models.

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

<details>
  <summary><strong>Snapshot</strong></summary>

Official dbt documentation for snapshots: [dbt Snapshots](https://docs.getdbt.com/docs/build/snapshots)

Snapshots accomplish two main goals:

<details>
  <summary><strong>1. Track Changes to Source Data:</strong></summary>

  - Detect changes by comparing the latest version of the data to its previous version stored in the snapshot table.
  - For example, if a column value (such as `customer_status`) changes from `'active'` to `'churned'`, the snapshot logs the new version along with a timestamp.
</details>

<details>
  <summary><strong>2. Maintain Historical Context:</strong></summary>

   - Preserve records that existed in the source at a specific point in time, even if those records have been deleted or modified upstream.
</details>

Snapshots work by maintaining two key pieces of information for each record:
- **valid_from**: The timestamp when this version of the record became effective.
- **valid_to**: The timestamp when this version was superseded (or `NULL` if it’s the current version).

In particular, the `snapshot__customer.sql` file is built as follows:

The `config` block defines the **behavior of the snapshot**:
<details>
  <summary><strong>target_database and target_schema</strong></summary>

  - Snapshots are stored in the `analytics.snapshots` schema in your data warehouse, ensuring that your production tables remain unaffected.
</details>
<details>
  <summary><strong>unique_key</strong></summary>

  - The primary key (`customer_id`) uniquely identifies each record. dbt uses this key to determine if a record already exists in the snapshot table.
</details>
<details>
  <summary><strong>strategy</strong></summary>

- Uses the `check` strategy to detect changes:
    - Compares the current state of a source row to its historical record.
    - Tracks changes for specified columns (see `check_cols`).
</details>
<details>
  <summary><strong>check_cols</strong></summary>

- Specifies which columns to monitor for changes (e.g., `status`, `email`, and `region`).
- If any of these columns are updated in the source table, a new version of the record is created.
</details>
</details>

## Exercises

- [Exercise 1](./exercises/exercise_1.md)
- [Exercise 2](./exercises/exercise_2.md)
- [Exercise 3](./exercises/exercise_3.md)