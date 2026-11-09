"""DAG: обновление каталога метрик и сбор обратной связи по ответам копайлота."""

from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/dags/dbt/nl_sql_copilot"

with DAG(
    dag_id="copilot_feedback_loop",
    description="Каталог метрик, проверка SQL-шаблонов и петля обратной связи",
    schedule="30 * * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Moscow"),
    catchup=False,
    default_args={"retries": 1},
    tags=["ai", "metadata", "hourly"],
) as dag:
    refresh_catalog = BashOperator(
        task_id="dbt_run_catalog",
        bash_command=f"cd {DBT_DIR} && dbt run --select marts",
    )

    validate_templates = BashOperator(
        task_id="validate_sql_templates",
        bash_command="python /opt/airflow/scripts/validate_sql_templates.py --catalog catalog_global_metrics",
        retries=0,
    )

    collect_feedback = BashOperator(
        task_id="collect_feedback",
        bash_command="python /opt/airflow/scripts/collect_copilot_feedback.py --window 24h",
    )

    retrain_router = BashOperator(
        task_id="retrain_router",
        bash_command="python /opt/airflow/scripts/retrain_router.py --min-samples 200",
    )

    refresh_catalog >> validate_templates >> collect_feedback >> retrain_router
