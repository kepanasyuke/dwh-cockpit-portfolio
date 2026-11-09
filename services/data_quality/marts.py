"""Качество данных: SLO пайплайнов, свежесть витрин и прогон dbt-тестов."""

from __future__ import annotations

from _shared import envelope, seeding, warehouse

META = {
    "slug": "data-quality",
    "title": "Качество данных",
    "subtitle": "SLO пайплайнов, свежесть витрин и DQ-правила",
    "engine": "SQLite · in-memory (прод: PostgreSQL + Airflow metadata)",
    "updated_at": "2026-11-08 07:05 MSK",
}

SCHEMA = """
create table monitor_pipeline_runs (
    model text, layer text, hour integer, lag_hours numeric, rows integer, status text
);
create table monitor_dq_checks (
    model text, rule text, status text, failed_rows integer, lag_hours numeric
);
"""

MODELS = [
    ("stg_bookings", "staging"),
    ("stg_quotes", "staging"),
    ("stg_payouts", "staging"),
    ("int_booking_revenue", "intermediate"),
    ("int_cancel_features", "intermediate"),
    ("int_supplier_terms", "intermediate"),
    ("mart_channel_performance", "mart"),
    ("mart_cancel_risk", "mart"),
    ("mart_elasticity", "mart"),
    ("mart_coverage", "mart"),
    ("mart_reconciliation", "mart"),
    ("mart_demand_forecast", "mart"),
]

RULES = ["not_null(booking_id)", "unique(booking_id)", "accepted_range(amount)", "freshness_max_2h", "relationships(city_id)"]


def connect() -> object:
    return warehouse.build(SCHEMA, {"monitor_pipeline_runs": run_rows(), "monitor_dq_checks": check_rows()})


def run_rows() -> list[tuple]:
    return [run_of(model, layer, hour) for model, layer in MODELS for hour in (0, 4, 8, 12, 16, 20)]


def run_of(model: str, layer: str, hour: int) -> tuple:
    return run_tuple(model, layer, hour, seeding.series(seeding.seed_of(f"{model}-{hour}"), 3))


def run_tuple(model: str, layer: str, hour: int, dice: list[float]) -> tuple:
    lag = round(seeding.between(dice[0], 0.1, 3.4) * (1.8 if layer == "mart" else 1.0), 2)
    return (model, layer, hour, lag, seeding.whole(dice[1], 120, 98000), status_of(lag, dice[2]))


def status_of(lag: float, dice: float) -> str:
    return "fail" if lag > 5.5 or dice > 0.95 else "warn" if lag > 3.0 or dice > 0.85 else "ok"


def check_rows() -> list[tuple]:
    return [check_of(model, rule) for model, _ in MODELS for rule in RULES[: 2 + len(model) % 3]]


def check_of(model: str, rule: str) -> tuple:
    return check_tuple(model, rule, seeding.series(seeding.seed_of(f"{model}-{rule}"), 3))


def check_tuple(model: str, rule: str, dice: list[float]) -> tuple:
    return (model, rule, "ok" if failed_rows(dice) == 0 else "fail", failed_rows(dice), round(seeding.between(dice[2], 0.1, 4.2), 2))


def failed_rows(dice: list[float]) -> int:
    return seeding.whole(dice[0], 0, 40) if dice[1] > 0.72 else 0


SQL_SUMMARY = """
select 100.0 * sum(case when status = 'ok' then 1 else 0 end) / count(*) as slo,
       (select count(*) from monitor_dq_checks where status <> 'ok') as failed,
       round(avg(lag_hours), 2) as lag,
       sum(case when status = 'fail' then 1 else 0 end) as incidents
from monitor_pipeline_runs
"""

SQL_MODELS = """
select model, layer, round(max(lag_hours), 2) as lag, max(rows) as rows, max(status) as status
from monitor_pipeline_runs
group by model, layer
order by lag desc
"""

SQL_LAG_BY_HOUR = """
select hour, round(avg(lag_hours), 2) as lag
from monitor_pipeline_runs
group by hour
order by hour
"""

SQL_CHECKS = """
select model, rule, status, failed_rows, round(lag_hours, 2) as lag_hours
from monitor_dq_checks
order by failed_rows desc, model
limit 30
"""


def summary(db: object) -> dict:
    return warehouse.query(db, SQL_SUMMARY)[0]


def models(db: object) -> list[dict]:
    return warehouse.query(db, SQL_MODELS)


def checks(db: object) -> list[dict]:
    return warehouse.query(db, SQL_CHECKS)


def lag_by_hour(db: object) -> list[dict]:
    return warehouse.query(db, SQL_LAG_BY_HOUR)


def build_kpis(totals: dict) -> list[dict]:
    return [
        envelope.kpi("slo", "SLO соблюдён, %", totals["slo"], "pct", 0.8),
        envelope.kpi("failed", "Упавших тестов", totals["failed"], "count", -3.0),
        envelope.kpi("lag", "Среднее отставание, ч", totals["lag"], "hours", -0.4),
        envelope.kpi("incidents", "Инцидентов за сутки", totals["incidents"], "count", 2.0),
    ]


def dashboard(db: object) -> dict:
    return envelope.dashboard(
        META,
        kpis=build_kpis(summary(db)),
        charts=[envelope.chart("lag_by_hour", "Отставание по часам", "hours", [(f"{row['hour']:02d}", row["lag"]) for row in lag_by_hour(db)])],
        grid=envelope.table(COLUMNS, models(db)),
        lineage=LINEAGE,
        notes=NOTES,
        extra={"checks": checks(db)},
    )


def widget(db: object, payload: dict) -> dict:
    return {"checks": checks(db), "slo": summary(db)["slo"]}


COLUMNS = [
    envelope.column("model", "Модель"),
    envelope.column("layer", "Слой"),
    envelope.column("lag", "Лаг, ч", "right", "hours"),
    envelope.column("rows", "Строк", "right", "count"),
    envelope.column("status", "Статус", "right", "text"),
]

LINEAGE = envelope.pipeline(
    [
        ("monitor_pipeline_runs", "staging", len(MODELS) * 6, "каждые 5 минут"),
        ("monitor_dq_checks", "staging", len(MODELS) * 2, "после каждого dbt run"),
        ("mart_freshness", "mart", len(MODELS), "каждые 5 минут"),
    ]
)

NOTES = [
    "SLO считается по фактическим запускам: доля прогонов, закончившихся вовремя и без ошибок.",
    "Тесты dbt попадают в витрину как отдельный источник: not_null, unique, accepted_range, freshness.",
    "Падение SLO ниже 97% поднимает инцидент в дежурную очередь — это и есть контракт с бизнесом.",
]
