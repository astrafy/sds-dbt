# Exercise 1: Creating a New Model for Sales Aggregation

## Objective
Create a new model that aggregates sales data by region. You will summarize metrics such as total sales, average sales, and transaction counts.

## Instructions
1. **Create a New Model File:**
   - Navigate to the `models` directory.
   - Create a new file named `sales_by_region.sql`.

2. **Develop Your SQL Query:**
   - Use an existing source table (e.g., `sales_data`) to group sales by region.
   - Calculate aggregated metrics such as:
     - `SUM(sale_amount)` as total sales
     - `AVG(sale_amount)` as average sales
     - `COUNT(transaction_id)` as the number of transactions
   - **Example:**
     ```sql
     
     SELECT
       region,
       SUM(sale_amount) AS total_sales,
       AVG(sale_amount) AS average_sales,
       COUNT(transaction_id) AS transaction_count
     FROM {{ ref('sales_data') }}
     GROUP BY region
     
     ```

3. **Run and Validate:**
   - Run the model using `dbt run --models sales_by_region`.
   - Check the resulting table or view in your data warehouse to ensure accuracy.

## Tips
- Use existing models as a reference for naming conventions and SQL style.
- Remember to use the `{{ ref() }}` function to reference other models.