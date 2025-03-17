# dbt All Package 

This dbt "all" project is exclusively used to run the "dbt docs" command and to expose global docuemtnation with lineage
about the three dbt projects.

It is importing all the dbt projects/packages:
1. dbt_customer
2. dbt_product
3. dbt_transaction

> **Side Note:** Since dbt transaction is importing already dbt_customer and dbt_product we could have imported only that one but for integrity we are importing all of them.

<details>
<summary><strong>dbt docs </strong></summary>
dbt docs is a built-in feature of dbt (Data Build Tool) that automatically generates documentation for your dbt project. 

Key Features of dbt Docs:
* **Model and Column Documentation**
* **Data Lineage**
* **Tests Documentation**
* **Sources Documentation**

**How to Use dbt docs**

Here is how dbt docs works in practice, from setup to generating and serving the documentation:

1. Add Documentation:
    * In your SQL model directly (not best practice due to readability of your code).
    ``` SQL
        {{ docs(
            description="This model processes raw sales data to provide daily sales totals",
            columns={
                "order_id": "Unique identifier for each order",
                "customer_id": "Customer identifier",
                "sales_amount": "Total sales for the order"
            }
        ) }}
    ```
    * In the YML of your model
    ``` YAML
      version: 2
        models:
          - name: dim__product
            description: "Dimension table for product details, enriched with currency text"
    ```
2. Run `dbt docs generate`: This command will analyze your dbt project, pull all the metadata (model names, descriptions, tests, column information, etc.), and generate the HTML documentation files. By default, this will place the generated documentation in the target folder.

3. Run `dbt docs serve` to start a local web server (usually at http://localhost:8000) where you can view the generated docs. The web page will include:
    * A searchable list of your models.
    * Detailed descriptions of each model and column.
    * A lineage graph showing the relationships between models.

</details>

### Interesting fact

Since this package is importing all other dbt projects, we could actually run all th different dbt projects from here
- [Run dbt_customer](../customer/README.md#how_to_dbt_customer)
- [Run dbt_product](../product/README.md#how_to_dbt_product)
- [Run dbt_transaction](../transaction/README.md#how_to_dbt_transaction)

Give it a try!
