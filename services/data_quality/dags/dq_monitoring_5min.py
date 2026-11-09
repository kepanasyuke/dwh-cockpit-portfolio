"""DAG: мониторинг свежести витрин и DQ-тестов каждые пять минут."""

from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator

DBT_DIR = "/opt/airflow/dags/dbt/data_quality"


def route_by_status(**context) -> str:
    slo = context["ti"].xcom_pull(task_ids="freshness_report") or 100.0
    return "page_oncall" if slo < 97.0 else "log_ok"


with DAG(
    dag_id="dq_monitoring_5min",
    description="SLO витрин, свежесть и алерты по упавшим тестам",
    schedule="*/5 * * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Moscow"),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 0},
    tags=["monitoring", "dq"],
) as dag:
    refresh = BashOperator(
        task_id="dbt_run_freshness",
        bash_command=f"cd {DBT_DIR} && dbt run --select marts",
        retries=1,
    )

    freshness_report = BashOperator(
        task_id="freshness_report",
        bash_command="python /opt/airflow/scripts/slo_report.py --mart mart_freshness",
        do_xcom_push=True,
    )

    branch = BranchPythonOperator(task_id="slo_branch", python_callable=route_by_status)

    page_oncall = BashOperator(
        task_id="page_oncall",
        bash_command="python /opt/airflow/scripts/page_oncall.py --severity high",
    )

    log_ok = BashOperator(
        task_id="log_ok",
        bash_command="echo 'SLO в норме'",
    )

    refresh >> freshness_report >> branch >> [page_oncall, log_ok]
