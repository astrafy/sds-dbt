# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
---
author:

- name: Andrea Bombino
- email: andrea@astrafy.io
- updated on: 08-03-2025

---
HERE YOU CAN SET THE DOCUMENTATION FOR USERS 
IN ORDER TO EXPLAIN THE DAG IS DOING
"""
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
# Local imports
from dags.utils.common_vars  import gke_bash
from dags.utils.generate_data_dbt_training import generate_and_load
from dags.utils.common_vars import ConfigVars

# Third-party imports
from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable, Param
from airflow.operators.python import (
    get_current_context,
)

from airflow.utils.task_group import TaskGroup
from airflow.utils.edgemodifier import Label
from dags.utils.common_vars import set_env_vars
from airflow.providers.google.cloud.operators.pubsub import PubSubPublishMessageOperator
import sys
import os
from datetime import timedelta

# Constants
MAIN_COURSE_PROJECT="prj-astrafy-main-courses"
PACKAGE_NAME = "product"
COMPANY_NAME = "fulll"
COMPANY_NAME = COMPANY_NAME.replace("_", "-").strip()
ENV = Variable.get("ENV", default_var="dev")
VERSION = "" #TODO TO BE REPLACED BASED ON YOUR TAG
# Global configurations
DP_TRAINING_VERSION = Variable.get(f"{PACKAGE_NAME.upper()}_{COMPANY_NAME.upper()}_VERSION")
SERVICE_ACCOUNT = "sa-dbt-fulll-dev@prj-astrafy-main-courses.iam.gserviceaccount.com"
IMAGE_DOCKER=f"europe-west1-docker.pkg.dev/{MAIN_COURSE_PROJECT}/dbt-training/{COMPANY_NAME}/{PACKAGE_NAME}:{DP_TRAINING_VERSION}"

# Set RunTime Vars
config_vars = ConfigVars()
config_vars.env_vars.extend(
    [
        set_env_vars(name="DATA_PRODUCT", value=PACKAGE_NAME),
        set_env_vars(name="ENV", value=ENV),
    ]
)



def construct_dbt_run_command(tag, ENV,mode):
    run_command = f"""
        dbt run --select tag:{tag} --target={ENV} --profiles-dir=/app {mode}; exit $?;
    """
    return run_command

def construct_dbt_test_command(tag, ENV):
    test_command = f"""
        dbt test --select tag:{tag} --target={ENV} --profiles-dir=/app; exit $?;
    """
    return test_command

with DAG(
    dag_id=f"dbt-training-{COMPANY_NAME}-{PACKAGE_NAME}-{ENV}-dag",
    schedule=None,
    description=f"{COMPANY_NAME} {PACKAGE_NAME} data product - {ENV}",
    max_active_tasks=10,
    catchup=False,
    is_paused_upon_creation=True,
    tags=["k8s", PACKAGE_NAME, COMPANY_NAME, ENV],
    max_active_runs=1,
    dagrun_timeout=timedelta(seconds=36000),
    default_view="grid",
    orientation="LR",
    sla_miss_callback=None,
    on_success_callback=None,
    on_failure_callback=None,
    params={
        "is_full_refresh": Param(False, type="boolean"),
    },
    start_date=datetime(2022, 10, 10, 1, 0),
    default_args={
        "owner": "andrea.bombino",
        "retries": 1,
        "retry_delay": timedelta(seconds=60),
    },
    doc_md=__doc__,
    render_template_as_native_obj=True,
) as dag:
    
    with TaskGroup(group_id="Ingestion") as Ingestion:
        @task()
        def data_ingestion(rows, bq_project,bq_dataset,data_product):
            """
            Ingest data for specific flow 50 rows
            """
            load_data_product = generate_and_load(rows, bq_project,bq_dataset,data_product)
            print(f"Function result: {load_data_product}")
            return load_data_product
        data_ingestion(50,"prj-data-fulll-lz-dev-1c8b","bqdts_company_lz","product")
    with TaskGroup(group_id="Transformations") as Transformations:
        dbt_run_stg_product = gke_bash(dag, 
                                        "dbt_run_stg_product", 
                                        IMAGE_DOCKER, 
                                        "{{ ti.xcom_pull(task_ids='get_dbt_mode_parameter', key='return_value')[0] }}", 
                                        config_vars.env_vars)
        dbt_run_int_product = gke_bash(dag, 
                                        "dbt_run_int_product", 
                                        IMAGE_DOCKER, 
                                        "{{ ti.xcom_pull(task_ids='get_dbt_mode_parameter', key='return_value')[1] }}", 
                                        config_vars.env_vars)
        dbt_run_mart_product = gke_bash(dag, 
                                        "dbt_run_mart_product", 
                                        IMAGE_DOCKER, 
                                        "{{ ti.xcom_pull(task_ids='get_dbt_mode_parameter', key='return_value')[2] }}", 
                                        config_vars.env_vars)
        dbt_run_test_product = gke_bash(dag, 
                                        "dbt_run_test_product", 
                                        IMAGE_DOCKER, 
                                        "{{ ti.xcom_pull(task_ids='get_dbt_mode_parameter', key='return_value')[3] }}", 
                                        config_vars.env_vars)
        (
            dbt_run_stg_product
            >> Label("Run Intermediate tables")
            >> dbt_run_int_product
            >> Label("Run Data Mart tables")
            >> dbt_run_mart_product
            >> Label("Run dbt test")
            >> dbt_run_test_product
        )
    
    with TaskGroup(group_id="Distribution") as Distribution:
        message = {"data": b"Product updated" }
    
        publish_message = PubSubPublishMessageOperator(
            task_id="publish_message",
            project_id=f"{MAIN_COURSE_PROJECT}",
            topic=f"topic-{COMPANY_NAME}-training",
            messages=[message],
        )
      
    @task()
    def get_dbt_mode_parameter(**kwargs):
        context = get_current_context()
        is_full_refresh = context["params"]["is_full_refresh"]
        print(f"is_full_refresh: {is_full_refresh}")
        print(f"type: {type(is_full_refresh)}")
        mode = "--full-refresh" if is_full_refresh else ""
        # Construct the run commands with mode variable
        run_stg = construct_dbt_run_command("stg_product", ENV,mode)
        run_int = construct_dbt_run_command("int_product", ENV,mode)
        run_dm = construct_dbt_run_command("mart_product", ENV,mode)
        run_test = construct_dbt_test_command("product",ENV)
        return run_stg,run_int,run_dm,run_test

    # Define task execution
    
    dbt_execution = get_dbt_mode_parameter()
    (
        Ingestion 
        >> Label("Data ingestion")
        >> dbt_execution
        >> Transformations
        >> Label("Notify the downstream application")
        >> Distribution
    )