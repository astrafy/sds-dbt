# Exercise 2: Exploring dbt Exposures – Documenting Marketing Models

## Objective
Learn how to use dbt exposures to document how your models are consumed downstream (for example, by dashboards or reports).

## Instructions
1. **Define an Exposure:**
   - Create or update an `exposures.yml` file in the project root or within the `models` folder.
   - Add an exposure entry for the `campaign_performance` model.
   - **Example:**
     ```yaml
     version: 2

     exposures:
       - name: marketing_dashboard
         type: dashboard
         url: "http://your-dashboard-url"
         description: "Dashboard showcasing campaign performance metrics."
         owners:
           - name: "Marketing Team"
         depends_on:
           - ref: campaign_performance
     ```

2. **Generate Documentation:**
   - Run `dbt docs generate` and then `dbt docs serve`.
   - Verify that the exposure information appears and is linked to your model.

3. **Experiment Further:**
   - Consider adding additional details or multiple exposures if your model is used in different contexts.
