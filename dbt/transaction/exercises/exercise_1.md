# Exercise 1: Creating a New Model for Campaign Performance

## Objective
Develop a model to calculate key performance metrics for marketing campaigns such as total impressions, clicks, and click-through rate.

## Instructions
1. **Create a New Model File:**
   - In the `models` directory, create a file named `campaign_performance.sql`.

2. **Write Your SQL Query:**
   - Use the source table (e.g., `campaign_data`) to compute:
     - Total impressions
     - Total clicks
     - Click-through rate (CTR)
   - **Example:**
     ```sql
     
     SELECT
       campaign_id,
       SUM(impressions) AS total_impressions,
       SUM(clicks) AS total_clicks,
       CASE 
         WHEN SUM(impressions) > 0 THEN ROUND(SUM(clicks)::numeric / SUM(impressions), 2)
         ELSE 0 
       END AS click_through_rate
     FROM {{ ref('campaign_data') }}
     GROUP BY campaign_id
     
     ```

3. **Run and Validate:**
   - Run the model using `dbt run --models campaign_performance`.
   - Confirm that the output reflects the calculated metrics.