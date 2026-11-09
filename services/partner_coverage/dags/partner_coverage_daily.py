"""DAG: загрузка фидов поставщиков, пересборка Data Vault и gap-анализ."""

from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/dags/dbt/partner_coverage"

with DAG(
    dag_id="partner_coverage_daily",
    description="Data Vault по отелям и поставщикам, витрина покрытия направлений",
    schedule="0 8 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Moscow"),
    catchup=False,
    default_args={"retries": 2, "retry_delay": pendulum.duration(minutes=20)},
    tags=["dwh", "supply", "daily"],
) as dag:
    load_feeds = BashOperator(
        task_id="load_supplier_feeds",
        bash_command="python /opt/airflow/scripts/load_supplier_feeds.py --suppliers all",
    )

    build_vault = BashOperator(
        task_id="dbt_run_vault",
        bash_command=f"cd {DBT_DIR} && dbt run --select vault",
    )

    build_mart = BashOperator(
        task_id="dbt_run_mart_coverage",
        bash_command=f"cd {DBT_DIR} && dbt run --select marts",
    )

    dq = BashOperator(
        task_id="dbt_test_vault",
        bash_command=f"cd {DBT_DIR} && dbt test --select vault marts",
        retries=0,
    )

    gap_report = BashOperator(
        task_id="gap_report",
        bash_command="python /opt/airflow/scripts/gap_report.py --threshold 60",
    )

    load_feeds >> build_vault >> build_mart >> dq >> gap_report
