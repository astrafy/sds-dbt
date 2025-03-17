# Exercise 2: Exploring dbt Sources – Defining a New Inventory Source

## Objective
Get hands-on with dbt sources by defining a new source for your inventory data and incorporating it into your models.

## Instructions
1. **Define a New Source:**
   - Locate or create a file named `sources.yml` (in the `models` or a dedicated `src` folder).
   - Add a source definition for your inventory data.
   - **Example:**
     ```yaml
     version: 2

     sources:
       - name: inventory_source
         tables:
           - name: inventory_data
             description: "Raw inventory data imported from the source system."
     ```

2. **Update a Model to Use the Source:**
   - Modify your `inventory_turnover.sql` model to reference the source:
     ```sql
     
     SELECT
       product_id,
       SUM(items_sold) AS total_items_sold,
       AVG(inventory_level) AS average_inventory,
       SUM(items_sold) / NULLIF(AVG(inventory_level), 0) AS turnover_rate
     FROM {{ source('inventory_source', 'inventory_data') }}
     GROUP BY product_id
     
     ```

3. **Generate and Explore Documentation:**
   - Run `dbt docs generate` and then `dbt docs serve`.
   - Verify that the new source and its metadata are displayed correctly in the documentation.
