# Exercises

## Day 1
<details>
  <summary><strong> Morning session</strong></summary>

### Objectives
- Learn to interact with dbt with basic commands and flags
- Build your first models and undestand relationships between models and sources


### Exercises instructions
- dbt commands 
  - dbt --version
  - dbt deps 
  - dbt debug
  - dbt compile, dbt run, dbt build, dbt test 
  - dbt ls
  - dbt clean
  - dbt flags:
    - select
    - target
    - warn-error
    - quiet


- dbt Models 
  - Create new staging, intermediate and datamart models 
  - Tag those models and run it by tag 
  - Run only upstream and dowsntream model from the intermediate model created 
  - Build a simple dashboard in Looker Studio


- dbt Sources 
  - create a new source for the source table "tweet" and reference that source model in a staging file
  
</details>

<details>
  <summary><strong>Afternoon session</strong></summary>

### Objectives
- Apply data test and unit testing to various models
- Use external package to test your model
- Learn how to change the configuration of dbt models
- Generation of dbt docs and learn how to navigate through it
- Build macro to simulate for loop in SQL and use external macros built  by the community

### Exercises instructions
- dbt tests 
  - Generic data test to the columns of the model
  - Source test
  - Add custom sql test to one model 
  - Add a test with dbt_expectations 
  - Add a unit test

- dbt docs 
  - Create doc block and use it in different models 
  - create project-wide documentation 
  - generate dbt docs and serve it locally

- Config / properties 
  - check query-comment macro and see details in jobs from BigQuery UI
  - explore profiles.yml an dchange number of threads to 1 and then do a dbt run 
  - add dbt var and use it in a model 
  - add env variable and use it in a source file 
  - apply configuration at dbt-project.yml level 
  - apply configuration at model level via config block 
  - apply configuration at model level via property file

- Macros 
  - build a macro to do a for loop 
  - build a macro to execute a query and use the query result into another macro 
  - use dbt-utils in one of the models

</details>

## Day 2
<details>
  <summary><strong>Morning session</strong></summary>

### Objectives
- Build incremental models with different strategies and use of full-refresh flag
- Understand how dbt packages work and start using a few famous ones
- Learn to b emore productive lby leveraging AI to generate code

### Exercises instructions

- Incremental models
  - Create an incremental model and run it to initialize it. Insert then new data and run the model again to
  showcase only new data has been added
  
- Package 
  - dbt-checkpoints with thee following checks and run those checks via pre-commit 
    - check-column-desc-are-same 
    - check-model-has-properties-file 
  - use elementary check the html results on your localhost 
  - use dbt project evaluator

- Generators: 
  - dbt_codegen to generate yml files for the models 
  - Show how AI like chatgpt cna generate yml files for your models
  - Show how chatgpt can create dbt models for you


</details>

<details>
  <summary><strong>Afternoon session</strong></summary>

### Objectives
- Learn GitOps workflow to trigger CI pipeline
- DataOps introduction with a simple CI pipeline that compiles dbt code and pushes a Docker image
- Data Mesh demo with multiple dbt projects within the same repository

### Exercises instructions

- Gitops workflow
  - Perform various commits and then a git tag "rc-x.x.x" to trigger a dev deployment pipeline
- Dataops
	- check model with SQLFluff
	- dbt-checkpoint

</details>


