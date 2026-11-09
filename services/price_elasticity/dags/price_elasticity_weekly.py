"""DAG: еженедельный пересчёт эластичности и публикация рекомендованных тарифов."""

from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/dags/dbt/price_elasticity"

with DAG(
    dag_id="price_elasticity_weekly",
    description="Пересчёт эластичности спроса и рекомендаций по цене",
    schedule="0 4 * * 1",
    start_date=pendulum.datetime(2026, 1, 5, tz="Europe/Moscow"),
    catchup=False,
    default_args={"retries": 1},
    tags=["dwh", "pricing", "weekly"],
) as dag:
    refresh_quotes = BashOperator(
        task_id="refresh_quotes",
        bash_command="python /opt/airflow/scripts/load_quotes.py --window 30d",
    )

    fit_models = BashOperator(
        task_id="dbt_run_mart_elasticity",
        bash_command=f"cd {DBT_DIR} && dbt run --select marts",
    )

    verify = BashOperator(
        task_id="dbt_test_elasticity",
        bash_command=f"cd {DBT_DIR} && dbt test --select mart_elasticity",
        retries=0,
    )

    publish = BashOperator(
        task_id="publish_prices",
        bash_command="python /opt/airflow/scripts/publish_price_recommendations.py --mart mart_elasticity",
    )

    refresh_quotes >> fit_models >> verify >> publish
