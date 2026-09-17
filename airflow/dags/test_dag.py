from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def hello():
    print("Hello from E-Commerce Airflow Pipeline!")


with DAG(
    dag_id="ecommerce_test_dag",
    start_date=datetime(2026, 9, 13),
    schedule=None,
    catchup=False,
) as dag:

    task = PythonOperator(
        task_id="hello_task",
        python_callable=hello,
    )