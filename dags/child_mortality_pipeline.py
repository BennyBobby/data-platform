from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="child_mortality_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    bronze = BashOperator(
        task_id="ingest_bronze",
        bash_command="python /opt/airflow/scripts/ingestion/ingest_child_mortality.py",
    )

    silver = BashOperator(
        task_id="transform_silver",
        bash_command="python /opt/airflow/scripts/transformation/transform.py",
    )

    gold = BashOperator(
        task_id="dbt_gold",
        bash_command="cd /opt/airflow/dbt/child_mortality && dbt run --profiles-dir /opt/airflow/dbt --log-path /tmp/dbt_logs --target-path /tmp/dbt_target",
    )

    bronze >> silver >> gold
