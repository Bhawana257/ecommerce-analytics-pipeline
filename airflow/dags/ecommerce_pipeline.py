from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="ecommerce_pipeline",
    start_date=datetime(2026, 9, 13),
    schedule="@daily",
    catchup=False,
) as dag:

    api_ingestion = BashOperator(
        task_id="api_ingestion",
        bash_command="cd /opt/project && python ingestion/api_ingestion.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/project/dbt_project && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/project/dbt_project && dbt test",
    )

    api_ingestion >> dbt_run >> dbt_test
