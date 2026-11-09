"""DAG: ежедневная сверка комиссий и открытие кейсов по расхождениям."""

from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

DBT_DIR = "/opt/airflow/dags/dbt/commission_recon"


def open_cases(**context) -> int:
    return context["ti"].xcom_push(key="open_cases", value=context["ti"].xcom_pull(task_ids="recon_report") or 0)


with DAG(
    dag_id="commission_recon_daily",
    description="Сверка начислений партнёров с биллингом и реестр расхождений",
    schedule="0 5 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Moscow"),
    catchup=False,
    default_args={"retries": 2, "retry_delay": pendulum.duration(minutes=15)},
    tags=["dwh", "finance", "daily"],
) as dag:
    extract_billing = BashOperator(
        task_id="extract_billing",
        bash_command="python /opt/airflow/scripts/extract_billing_api.py --all-partners",
    )

    build = BashOperator(
        task_id="dbt_run_reconciliation",
        bash_command=f"cd {DBT_DIR} && dbt run --select stg_payout_union marts",
    )

    verify = BashOperator(
        task_id="dbt_test_reconciliation",
        bash_command=f"cd {DBT_DIR} && dbt test --select mart_reconciliation",
        retries=0,
    )

    recon_report = BashOperator(
        task_id="recon_report",
        bash_command="python /opt/airflow/scripts/recon_report.py --mart mart_reconciliation",
        do_xcom_push=True,
    )

    notify = PythonOperator(task_id="open_cases", python_callable=open_cases)

    extract_billing >> build >> verify >> recon_report >> notify
