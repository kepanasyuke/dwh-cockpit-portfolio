"""Прогноз спроса: сезонная модель (уровень × коэффициент дня недели) и бэктест на 14 дней."""

from __future__ import annotations

from _shared import envelope, seeding, warehouse

META = {
    "slug": "demand-forecast",
    "title": "Прогноз спроса",
    "subtitle": "Сезонная модель, бэктест MAPE и план загрузки",
    "engine": "SQLite · in-memory (прод: Greenplum + Airflow)",
    "updated_at": "2026-11-08 03:15 MSK",
}

SCHEMA = """
create table fact_bookings (day_index integer, day text, route text, weekday integer, bookings integer, capacity integer);
create table mart_demand_forecast (day text, route text, plan integer, fact integer, load numeric);
"""

ROUTES = ["Москва → Сочи", "Москва → Стамбул", "СПб → Калининград", "Москва → Тбилиси"]
HISTORY_DAYS = 42
TRAIN_DAYS = 28
BACKTEST_DAYS = 14
CAPACITY = 240


def connect() -> object:
    return warehouse.load(warehouse.build(SCHEMA, {"fact_bookings": history_rows()}), {"mart_demand_forecast": forecast_rows()})


def history_rows() -> list[tuple]:
    return [history_of(route, index) for route in ROUTES for index in range(HISTORY_DAYS)]


def history_of(route: str, index: int) -> tuple:
    return history_tuple(route, index, seeding.series(seeding.seed_of(f"{route}-day-{index}"), 2))


def history_tuple(route: str, index: int, dice: list[float]) -> tuple:
    return (index, seeding.day(index), route, index % 7, bookings_of(route, index, dice), capacity_of(route))


def bookings_of(route: str, index: int, dice: list[float]) -> int:
    return round(level_of(route) * weekday_factor(index % 7) * seeding.between(dice[0], 0.9, 1.1))


def level_of(route: str) -> float:
    return 60 + 70 * seeding.noise(seeding.seed_of(route + "-level"))


def capacity_of(route: str) -> int:
    return CAPACITY - 40 * seeding.whole(seeding.noise(seeding.seed_of(route + "-cap")), 0, 1)


def weekday_factor(weekday: int) -> float:
    return [0.86, 0.84, 0.9, 0.95, 1.12, 1.24, 1.09][weekday]


def weekday_factors(rows: list[tuple]) -> dict[int, float]:
    return {weekday: factor_of(rows, weekday) for weekday in range(7)}


def factor_of(rows: list[tuple], weekday: int) -> float:
    same = [row[4] for row in rows if row[3] == weekday]
    return sum(same) / len(same) / overall(rows) if same and overall(rows) else 1.0


def overall(rows: list[tuple]) -> float:
    return sum(row[4] for row in rows) / len(rows)


def train_rows(route: str) -> list[tuple]:
    return [row for row in history_rows() if row[2] == route and row[0] < TRAIN_DAYS]


def backtest_rows(route: str) -> list[tuple]:
    return [row for row in history_rows() if row[2] == route and row[0] >= TRAIN_DAYS]


def base_level(route: str) -> float:
    return sum(row[4] for row in train_rows(route)) / len(train_rows(route))


def plan_for(route: str, weekday: int) -> int:
    return max(1, round(base_level(route) * weekday_factors(train_rows(route)).get(weekday, 1.0)))


def forecast_rows() -> list[tuple]:
    return [forecast_of(route, row) for route in ROUTES for row in backtest_rows(route)]


def forecast_of(route: str, row: tuple) -> tuple:
    plan = plan_for(route, row[3])
    return (row[1], route, plan, row[4], round(100 * plan / row[5], 2))


SQL_SUMMARY = """
select sum(plan) as forecast,
       round(avg(abs(plan - fact) * 100.0 / fact), 2) as mape,
       round(max(load), 2) as peak,
       sum(abs(plan - fact)) as gap
from mart_demand_forecast
"""

SQL_DAILY = """
select day, sum(plan) as plan, sum(fact) as fact, round(avg(load), 2) as load
from mart_demand_forecast
group by day
order by day
"""

SQL_ROUTES = """
select day, route, plan, fact, round(load, 2) as load
from mart_demand_forecast
order by day, route
limit 8
"""


def summary(db: object) -> dict:
    return warehouse.query(db, SQL_SUMMARY)[0]


def daily(db: object) -> list[dict]:
    return warehouse.query(db, SQL_DAILY)


def route_rows(db: object) -> list[dict]:
    return warehouse.query(db, SQL_ROUTES)


def build_kpis(totals: dict) -> list[dict]:
    return [
        envelope.kpi("forecast", "Прогноз броней", totals["forecast"], "count", 3.4),
        envelope.kpi("mape", "MAPE, %", totals["mape"], "pct", -0.7),
        envelope.kpi("peak", "Пик загрузки, %", totals["peak"], "pct", 1.9),
        envelope.kpi("gap", "Отклонение факт/план", totals["gap"], "count", -1.2),
    ]


def dashboard(db: object) -> dict:
    return envelope.dashboard(
        META,
        kpis=build_kpis(summary(db)),
        charts=[envelope.chart("plan_vs_fact", "План и факт броней", "count", [(row["day"][-2:], row["plan"]) for row in daily(db)])],
        grid=envelope.table(COLUMNS, route_rows(db)),
        lineage=LINEAGE,
        notes=NOTES,
    )


def widget(db: object, payload: dict) -> dict:
    route = str(payload.get("route") or ROUTES[0])
    return {"route": route, "days": widget_days(route)}


def widget_days(route: str) -> list[dict]:
    return [
        {"day": f"Д{index + 1}", "weekday": index % 7, "plan": plan_for(route, index % 7), "capacity": capacity_of(route)}
        for index in range(7)
    ]


COLUMNS = [
    envelope.column("day", "Дата"),
    envelope.column("route", "Направление"),
    envelope.column("plan", "План, брони", "right", "count"),
    envelope.column("fact", "Факт, брони", "right", "count"),
    envelope.column("load", "Загрузка, %", "right", "pct"),
]

LINEAGE = envelope.pipeline(
    [
        ("stg_bookings_daily", "staging", HISTORY_DAYS * len(ROUTES), "ночью 02:00"),
        ("int_weekday_seasonality", "intermediate", 7, "ночью 02:30"),
        ("mart_demand_forecast", "mart", BACKTEST_DAYS * len(ROUTES), "ночью 03:00"),
    ]
)

NOTES = [
    "Модель без внешних зависимостей: уровень направления × сезонный коэффициент дня недели.",
    "Бэктест честный: коэффициенты считаются на первых 28 днях, проверка — на следующих 14.",
    "Загрузка считается как план / вместимость направления, пик выделяется красным на дашборде.",
]
