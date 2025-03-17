# Exercise 3: Implementing Data Tests for Sales Data

## Objective
Enhance your project’s data quality by adding tests to ensure that critical fields are valid.

## Instructions
1. **Update the Schema File:**
   - Open (or create) a schema file named `sales_by_region.yml` in the `models` directory.
   - Add tests for key columns (e.g., `region` should be unique and not null, and `total_sales` should not be null).

2. **Example Schema File:**
   ```yaml
   version: 2

   models:
     - name: sales_by_region
       columns:
         - name: region
           tests:
             - not_null
             - unique
         - name: total_sales
           tests:
             - not_null