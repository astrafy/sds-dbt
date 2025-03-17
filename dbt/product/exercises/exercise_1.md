# Exercise 1: Creating a New Model for Inventory Turnover

## Objective
Build a model that calculates inventory turnover, helping you analyze how quickly products move through inventory.

## Instructions
1. **Create a New Model File:**
   - In the `models` directory, create a file named `inventory_turnover.sql`.

2. **Develop Your SQL Query:**
   - Use a source table (e.g., `inventory_data`) to calculate:
     - Total items sold
     - Average inventory levels
     - Turnover rate (e.g., total items sold divided by average inventory)
   - **Example:**
     ```sql
     
     SELECT
       product_id,
       SUM(items_sold) AS total_items_sold,
       AVG(inventory_level) AS average_inventory,
       SUM(items_sold) / NULLIF(AVG(inventory_level), 0) AS turnover_rate
     FROM {{ ref('inventory_data') }}
     GROUP BY product_id
     
     ```

3. **Run and Validate:**
   - Run the model with `dbt run --models inventory_turnover`.
   - Confirm that the output in your data warehouse reflects the intended calculations.