# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
---
author:

- name: Andrea Bombino
- email: andrea@astrafy.io
- updated on: 14-03-2025

---
## **READ CAREFULLY** 
## 1. Data Marketing Team DAG works: 
The DAG is Pulling data using the PubSubPullSensor in order to check whenenever a message has been pushed from the Central Data team.
When a message is pulled the Downstream pipeline from the Data Marketing team will start doing their analysis and their data processing.
**IMPORTNAT**: there is a self triggered because the PubSubPullSensor will not continuesly sensing but as soon as it sense the first message
the DAG will be in a succesfull mode and this is not what we want.
"""


from datetime import datetime, timedelta
import base64

from airflow import DAG
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.providers.google.cloud.sensors.pubsub import PubSubPullSensor
from airflow.operators.empty import EmptyOperator
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.edgemodifier import Label

#CONSTANT
MAIN_COURSE_PROJECT="prj-astrafy-main-courses"

COMPANY_NAME = "fulll"
COMPANY_NAME = COMPANY_NAME.replace("_", "-").strip()

ENV = Variable.get("ENV", default_var="dev")

# UTILITY FUNCTIONS
def downstream_dipsatch_message(**kwargs):
    ti = kwargs['ti']
    topic_xcom = ti.xcom_pull(task_ids='Pulling.pull_messages',key='return_value')
    topic_message = topic_xcom[0]['message']['data']
    decoded_message = base64.b64decode(topic_message).decode()
    print(decoded_message)
    if "customer" in decoded_message.lower():
        return "Acknowledge.customer_ack_task"
    if "product" in decoded_message.lower():
        return "Acknowledge.product_ack_task"
    if "transaction" in decoded_message.lower():
        return "Acknowledge.transaction_ack_task"
    else:
        return "Acknowledge.skip"


def acknowledge_data_product(data_product: str):
    """
    This function acknowledges the receipt of a data product.

    Args:
        data_product (str): The name of the data product.
    """
    print(f"Received and acknowledged data product: {data_product}")
    
with DAG(
    dag_id=f"pull-{COMPANY_NAME}-{ENV}-dag",
    start_date=datetime(2024, 8, 22),
    schedule=None,
    tags=[COMPANY_NAME, ENV],
    max_active_runs=1,
    concurrency=1,
    default_args={
        "owner": "andrea.bombino",
        "retries": 1,
        "retry_delay": timedelta(seconds=60),
    },
    doc_md=__doc__,
) as dag:
    with TaskGroup(group_id="Pulling") as Pulling:
        pull_messages = PubSubPullSensor(
            task_id="pull_messages",
            ack_messages=True,
            project_id=f"{MAIN_COURSE_PROJECT}",
            subscription=f"sub-{COMPANY_NAME}-training",
        )
    with TaskGroup(group_id="Dispatching") as Dispatching:
        message_selector = BranchPythonOperator(
            task_id='message_selector', 
            python_callable=downstream_dipsatch_message,
            provide_context=True
        )
    with TaskGroup(group_id="Acknowledge") as Acknowledge:
        customer_ack_task = PythonOperator(
            task_id='customer_ack_task',
            python_callable=acknowledge_data_product,
            op_kwargs={"data_product": "customer"},
        )
        product_ack_task = PythonOperator(
            task_id='product_ack_task',
            python_callable=acknowledge_data_product,
            op_kwargs={"data_product": "product"},
        )
        transaction_ack_task = PythonOperator(
            task_id='transaction_ack_task',
            python_callable=acknowledge_data_product,
            op_kwargs={"data_product": "transaction"},
        )
        skip = EmptyOperator(
            task_id='skip'
        )
    with TaskGroup(group_id="Sensing") as Sensing:
        self_trigger_task = TriggerDagRunOperator(
            task_id='self_trigger_task',
            trigger_dag_id=dag.dag_id,
            trigger_rule=TriggerRule.ALL_DONE,
        )
    
    
    
    Pulling >> Label("Data pulling")  >> Dispatching >> Label("Data Dispatch") >> Acknowledge >> Label("Sense new data") >> Sensing
