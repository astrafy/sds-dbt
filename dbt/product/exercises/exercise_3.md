# Exercise 3: Implementing Data Tests for Inventory Data

## Objective
Improve data quality by adding tests to validate critical fields in your inventory model.

## Instructions
1. **Update the Schema File:**
   - Open (or create) a schema file named `inventory_turnover.yml` in the `models` directory.
   - Define tests for important columns (e.g., `product_id` and `turnover_rate`).
   - **Example:**
     ```yaml
     version: 2

     models:
       - name: inventory_turnover
         columns:
           - name: product_id
             tests:
               - not_null
               - unique
           - name: turnover_rate
             tests:
               - not_null
     ```

2. **Run the Tests:**
   - Execute `dbt test --models inventory_turnover`.
   - Review the test results and adjust your model or source data as needed.

## Tips
- Look into dbt’s documentation on tests for additional test types you can implement.
