"""Эластичность цен: спрос как функция цены, оценка log-log МНК и рекомендации по тарифу."""

from __future__ import annotations

import math

from _shared import envelope, seeding, warehouse

META = {
    "slug": "price-elasticity",
    "title": "Эластичность цен",
    "subtitle": "Log-log МНК по котировкам и симулятор тарифа",
    "engine": "SQLite · in-memory (прод: ClickHouse)",
    "updated_at": "2026-11-08 04:40 MSK",
}

SCHEMA = """
create table fact_quotes (
    quote_id integer primary key,
    route text,
    price numeric,
    demand integer,
    season_index numeric,
    week integer
);
create table mart_elasticity (
    route text primary key,
    price numeric,
    demand integer,
    elasticity numeric,
    r2 numeric,
    recommend numeric
);
"""

ROUTES = [
    "Москва → Сочи",
    "Москва → Стамбул",
    "СПб → Калининград",
    "Москва → Тбилиси",
    "Казань → Сочи",
    "Москва → Владивосток",
]
QUOTES_PER_ROUTE = 30


def connect() -> object:
    return warehouse.load(warehouse.build(SCHEMA, {"fact_quotes": quote_rows()}), {"mart_elasticity": mart_rows()})


def quote_rows() -> list[tuple]:
    return [quote_of(route, index) for route in ROUTES for index in range(QUOTES_PER_ROUTE)]


def quote_of(route: str, index: int) -> tuple:
    return quote_tuple(route, index, seeding.series(seeding.seed_of(f"{route}-{index}"), 4))


def quote_tuple(route: str, index: int, dice: list[float]) -> tuple:
    return (
        index + seeding.seed_of(route) % 100000,
        route,
        price_of(route, dice),
        demand_of(route, dice),
        round(seeding.between(dice[2], 0.8, 1.3), 3),
        seeding.whole(dice[3], 1, 8),
    )


def base_price(route: str) -> float:
    return seeding.between(seeding.noise(seeding.seed_of(route)), 8500, 46000)


def price_of(route: str, dice: list[float]) -> float:
    return round(base_price(route) * seeding.between(dice[0], 0.82, 1.35), 2)


def demand_of(route: str, dice: list[float]) -> int:
    return max(1, int(180 * (price_of(route, dice) / base_price(route)) ** true_elasticity(route) * seeding.between(dice[1], 0.9, 1.1)))


def true_elasticity(route: str) -> float:
    return round(-1.1 - 1.3 * seeding.noise(seeding.seed_of(route + "-el")), 3)


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def covariance(xs: list[float], ys: list[float]) -> float:
    return mean([(x - mean(xs)) * (y - mean(ys)) for x, y in zip(xs, ys)])


def variance(xs: list[float]) -> float:
    return mean([(x - mean(xs)) ** 2 for x in xs])


def slope(xs: list[float], ys: list[float]) -> float:
    return covariance(xs, ys) / variance(xs) if variance(xs) else 0.0


def intercept(xs: list[float], ys: list[float]) -> float:
    return mean(ys) - slope(xs, ys) * mean(xs)


def residues(xs: list[float], ys: list[float]) -> float:
    return mean([(y - intercept(xs, ys) - slope(xs, ys) * x) ** 2 for x, y in zip(xs, ys)])


def r2(xs: list[float], ys: list[float]) -> float:
    return 1 - residues(xs, ys) / variance(ys) if variance(ys) else 0.0


def quotes_of(route: str) -> list[tuple]:
    return [row for row in quote_rows() if row[1] == route]


def mean_price(quotes: list[tuple]) -> float:
    return round(mean([row[2] for row in quotes]), 2)


def log_prices(quotes: list[tuple]) -> list[float]:
    return [math.log(row[2]) for row in quotes]


def log_demands(quotes: list[tuple]) -> list[float]:
    return [math.log(row[3]) for row in quotes]


def elasticity_of(quotes: list[tuple]) -> float:
    return round(slope(log_prices(quotes), log_demands(quotes)), 3)


def r2_of(quotes: list[tuple]) -> float:
    return round(r2(log_prices(quotes), log_demands(quotes)), 3)


def rate_for(elasticity: float) -> float:
    return 0.06 if elasticity < -1 else -0.04 if elasticity > -0.6 else 0.02


def recommend_price(quotes: list[tuple]) -> float:
    return round(mean_price(quotes) * (1 + rate_for(elasticity_of(quotes))), 2)


def mart_rows() -> list[tuple]:
    return [mart_row(route) for route in ROUTES]


def mart_row(route: str) -> tuple:
    return (route, mean_price(quotes_of(route)), sum(row[3] for row in quotes_of(route)), elasticity_of(quotes_of(route)), r2_of(quotes_of(route)), recommend_price(quotes_of(route)))


SQL_SUMMARY = """
select avg(elasticity) as elasticity,
       sum(recommend - price) as margin_uplift,
       count(*) as routes,
       avg(r2) as confidence
from mart_elasticity
"""

SQL_ROUTES = """
select route, price, demand, elasticity, recommend
from mart_elasticity
order by route
"""

SQL_FIRST = """
select elasticity from mart_elasticity order by route limit 1
"""

CURVE = [("-10%", -10.0), ("-5%", -5.0), ("0%", 0.0), ("+5%", 5.0), ("+10%", 10.0), ("+15%", 15.0)]


def summary(db: object) -> dict:
    return warehouse.query(db, SQL_SUMMARY)[0]


def route_rows(db: object) -> list[dict]:
    return warehouse.query(db, SQL_ROUTES)


def demand_curve(db: object) -> list[tuple[str, float]]:
    elasticity = warehouse.query(db, SQL_FIRST)[0]["elasticity"]
    return [(label, round(100 * (1 + delta / 100) ** elasticity, 2)) for label, delta in CURVE]


def build_kpis(summary_row: dict) -> list[dict]:
    return [
        envelope.kpi("elasticity", "Средняя эластичность", summary_row["elasticity"], "ratio", -0.1),
        envelope.kpi("margin_uplift", "Прирост маржи, ₽", summary_row["margin_uplift"], "rub", 6.2),
        envelope.kpi("routes", "Направлений", summary_row["routes"], "count", 0.0),
        envelope.kpi("confidence", "Средний R²", summary_row["confidence"], "score", 0.4),
    ]


def dashboard(db: object) -> dict:
    return envelope.dashboard(
        META,
        kpis=build_kpis(summary(db)),
        charts=[envelope.chart("demand_curve", "Спрос при изменении цены", "pct", demand_curve(db))],
        grid=envelope.table(COLUMNS, route_rows(db)),
        lineage=LINEAGE,
        notes=NOTES,
    )


def simulate(price: float, delta: float, elasticity: float) -> dict:
    return {
        "new_price": round(price * (1 + delta), 2),
        "demand_factor": round((1 + delta) ** elasticity, 4),
        "revenue_factor": round((1 + delta) ** (1 + elasticity), 4),
        "verdict": verdict_of((1 + delta) ** (1 + elasticity)),
    }


def verdict_of(revenue_factor: float) -> str:
    return "поднять цену" if revenue_factor > 1.01 else "снизить цену" if revenue_factor < 0.99 else "оставить как есть"


def widget(db: object, payload: dict) -> dict:
    return simulate(
        float(payload.get("price") or 12500),
        float(payload.get("delta_pct") or 5) / 100,
        float(payload.get("elasticity") or -1.4),
    )


COLUMNS = [
    envelope.column("route", "Направление"),
    envelope.column("price", "Цена, ₽", "right", "rub"),
    envelope.column("demand", "Спрос, шт", "right", "count"),
    envelope.column("elasticity", "Эластичность", "right", "ratio"),
    envelope.column("recommend", "Рекомендация, ₽", "right", "rub"),
]

LINEAGE = envelope.pipeline(
    [
        ("stg_quotes", "staging", QUOTES_PER_ROUTE * len(ROUTES), "каждые 15 минут"),
        ("int_price_demand_pairs", "intermediate", QUOTES_PER_ROUTE * len(ROUTES), "ежедневно"),
        ("mart_elasticity", "mart", len(ROUTES), "еженедельно"),
    ]
)

NOTES = [
    "Эластичность оценивается МНК в log-log координатах: наклон регрессии и есть коэффициент эластичности.",
    "R² считается на тех же данных, что и наклон, поэтому низкий R² сразу подсвечивает ненадёжное направление.",
    "Симулятор повторяет формулу витрины: выручка меняется как (1+δ)^(1+ε).",
]
