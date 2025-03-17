# Exercise 2: Exploring dbt Macros – Create a Date Formatting Macro

## Objective
Learn how to create and use a simple macro by building one that formats date columns consistently across your models.

## Instructions
1. **Create a Macro File:**
   - In the `macros` directory, create a new file called `format_date.sql`.

2. **Define the Macro:**
   - Write a macro that takes a date column and returns it formatted as `YYYY-MM-DD`.
   - **Example Macro:**
     ```jinja
     
     {% macro format_date(date_column) %}
       to_char({{ date_column }}, 'YYYY-MM-DD')
     {% endmacro %}
     
     ```

3. **Use the Macro in a Model:**
   - Create or modify a model file (e.g., `formatted_sales_dates.sql` in the `models` directory).
   - Apply the macro to format a date column in your SELECT statement.
   - **Example:**
     ```sql
     
     SELECT
       id,
       {{ format_date('sale_date') }} AS formatted_sale_date,
       sale_amount
     FROM {{ ref('sales_data') }}
     
     ```

4. **Run and Validate:**
   - Execute `dbt run --models formatted_sales_dates` to see the macro in action.
   - Verify that the dates appear in the desired format in your warehouse.

## Tips
- Experiment with different date formats in your macro.
- Check your dbt logs to see the expanded SQL for debugging.