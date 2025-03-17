# Exercise 3: Implementing Data Tests for Marketing Data

## Objective
Ensure the integrity of your marketing insights by adding tests that validate key columns in the `campaign_performance` model.

## Instructions
1. **Update the Schema File:**
   - Open (or create) a schema file named `campaign_performance.yml` in the `models` directory.
   - Add tests for critical columns such as `campaign_id` and `click_through_rate`.
   - **Example:**
     ```yaml
     version: 2

     models:
       - name: campaign_performance
         columns:
           - name: campaign_id
             tests:
               - not_null
               - unique
           - name: click_through_rate
             tests:
               - not_null
     ```

2. **Run the Tests:**
   - Execute `dbt test --models campaign_performance`.
   - Analyze the test results and adjust your model if necessary.

## Tips
- Use this opportunity to explore additional test types (e.g., relationships or accepted values) as needed.
