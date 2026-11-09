"""DAG: ежедневная пересборка витрин бронирований (dbt run + dbt test + публикация метрик)."""

from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/dags/dbt/bookings_marts"

with DAG(
    dag_id="bookings_marts_daily",
    description="Пересборка витрин бронирований и проверка тестов dbt",
    schedule="0 6 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Moscow"),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": pendulum.duration(minutes=10)},
    tags=["dwh", "finance", "daily"],
) as dag:
    extract = BashOperator(
        task_id="extract_bookings",
        bash_command="airbyte sync --connection bookings_source",
        execution_timeout=pendulum.duration(minutes=40),
    )

    build_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=f"cd {DBT_DIR} && dbt run --select staging",
    )

    build_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=f"cd {DBT_DIR} && dbt run --select intermediate marts --full-refresh",
    )

    test_marts = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test --select marts",
        retries=0,
    )

    publish = BashOperator(
        task_id="publish_metrics",
        bash_command="python /opt/airflow/scripts/publish_bi_metrics.py --mart mart_channel_performance",
    )

    extract >> build_staging >> build_marts >> test_marts >> publish
