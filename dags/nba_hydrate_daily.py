from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator

default_args = {
    "owner": "neals-squad",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}
with DAG(
    dag_id="nba_hydrate_daily",
    default_args=default_args,
    schedule_interval="0 7 * * *",  # 07:00 UTC, daily
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:
    hydrate = SimpleHttpOperator(
        task_id="hydrate_games",
        http_conn_id="nba_api",  # define base URL in Airflow connections
        endpoint="games",
        method="GET",
        data={},  # none
        params={"date": "{{ ds }}"},
        log_response=True,
    )

