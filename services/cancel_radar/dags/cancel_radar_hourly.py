"""DAG: почасовой скоринг риска отмен и пересборка витрины."""

from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

DBT_DIR = "/opt/airflow/dags/dbt/cancel_radar"


def alert_high_risk(**context) -> None:
    at_risk = context["ti"].xcom_pull(task_ids="risk_report") or 0
    if at_risk > 500:
        raise ValueError(f"Слишком много броней в риске: {at_risk}")


with DAG(
    dag_id="cancel_radar_hourly",
    description="Скоринг отмен, витрина рисков и алерт по объёму",
    schedule="15 * * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Moscow"),
    catchup=False,
    default_args={"retries": 1, "retry_delay": pendulum.duration(minutes=5)},
    tags=["dwh", "risk", "hourly"],
) as dag:
    build_features = BashOperator(
        task_id="dbt_run_staging",
        bash_command=f"cd {DBT_DIR} && dbt run --select staging",
    )

    score = BashOperator(
        task_id="dbt_run_mart_cancel_risk",
        bash_command=f"cd {DBT_DIR} && dbt run --select marts",
    )

    test_risk = BashOperator(
        task_id="dbt_test_risk",
        bash_command=f"cd {DBT_DIR} && dbt test --select mart_cancel_risk",
        retries=0,
    )

    risk_report = BashOperator(
        task_id="risk_report",
        bash_command="python /opt/airflow/scripts/risk_report.py --mart mart_cancel_risk --threshold 0.35",
    )

    guard = PythonOperator(task_id="alert_high_risk", python_callable=alert_high_risk)

    build_features >> score >> test_risk >> risk_report >> guard
