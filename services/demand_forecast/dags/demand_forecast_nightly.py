"""DAG: ночной прогноз спроса и проверка MAPE перед публикацией плана."""

from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import ShortCircuitOperator

DBT_DIR = "/opt/airflow/dags/dbt/demand_forecast"
MAX_MAPE = 15.0


def mape_ok(**context) -> bool:
    mape = context["ti"].xcom_pull(task_ids="backtest") or MAX_MAPE
    return mape <= MAX_MAPE


with DAG(
    dag_id="demand_forecast_nightly",
    description="Прогноз спроса, бэктест MAPE и публикация плана загрузки",
    schedule="0 3 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Moscow"),
    catchup=False,
    default_args={"retries": 2, "retry_delay": pendulum.duration(minutes=15)},
    tags=["dwh", "planning", "nightly"],
) as dag:
    build_forecast = BashOperator(
        task_id="dbt_run_forecast",
        bash_command=f"cd {DBT_DIR} && dbt run --select stg_bookings_daily marts",
    )

    backtest = BashOperator(
        task_id="backtest",
        bash_command="python /opt/airflow/scripts/backtest_mape.py --mart mart_demand_forecast",
        do_xcom_push=True,
    )

    gate = ShortCircuitOperator(task_id="mape_gate", python_callable=mape_ok)

    publish = BashOperator(
        task_id="publish_plan",
        bash_command="python /opt/airflow/scripts/publish_load_plan.py --mart mart_demand_forecast --horizon 14",
    )

    build_forecast >> backtest >> gate >> publish
