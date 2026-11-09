"""Радар отмен: скоринг риска отмены брони и витрина потерь выручки."""

from __future__ import annotations

import math

from _shared import envelope, seeding, warehouse

META = {
    "slug": "cancel-radar",
    "title": "Радар отмен",
    "subtitle": "Логистическая регрессия поверх витрины броней",
    "engine": "SQLite · in-memory (прод: ClickHouse + Airflow)",
    "updated_at": "2026-11-08 05:00 MSK",
}

SCHEMA = """
create table fact_bookings (
    booking_id integer primary key,
    city text,
    hotel text,
    channel text,
    lead_time_days integer,
    nights integer,
    amount numeric,
    deposit numeric,
    is_refundable integer,
    past_cancels integer,
    cancelled integer
);
create table mart_cancel_risk (
    booking_id integer,
    city text,
    hotel text,
    channel text,
    lead_time_days integer,
    amount numeric,
    risk numeric,
    expected_loss numeric,
    cancelled integer
);
"""

ROWS = 480

WEIGHTS = {
    "bias": -4.3,
    "lead": 0.011,
    "nights": 0.045,
    "amount": 0.0000045,
    "channel_web": 0.32,
    "channel_partner": -0.28,
    "refundable": 0.62,
    "past_cancels": 0.55,
}


def connect() -> object:
    return warehouse.load(warehouse.build(SCHEMA, {"fact_bookings": booking_rows()}), {"mart_cancel_risk": risk_rows()})


def booking_rows() -> list[tuple]:
    return [booking_of(index) for index in range(ROWS)]


def booking_of(index: int) -> tuple:
    return complete(index, seeding.series(seeding.seed_of(f"cancel-{index}"), 7))


def complete(index: int, dice: list[float]) -> tuple:
    return (
        index + 1,
        city_of(dice),
        hotel_of(index, dice),
        channel_of(dice),
        lead_of(dice),
        nights_of(dice),
        amount_of(dice),
        deposit_of(dice),
        refundable_of(dice),
        past_of(dice),
        cancelled_of(index, dice),
    )


def city_of(dice: list[float]) -> str:
    return str(seeding.pick([city[0] for city in seeding.CITIES], dice[0]))


def hotel_of(index: int, dice: list[float]) -> str:
    return seeding.hotel_name(index, city_of(dice))


def channel_of(dice: list[float]) -> str:
    return str(seeding.pick(seeding.CHANNELS, dice[1]))


def lead_of(dice: list[float]) -> int:
    return seeding.whole(dice[2], 1, 120)


def nights_of(dice: list[float]) -> int:
    return seeding.whole(dice[3], 1, 12)


def amount_of(dice: list[float]) -> float:
    return round(seeding.between(dice[4], 3800, 120000), 2)


def deposit_of(dice: list[float]) -> float:
    return round(amount_of(dice) * seeding.between(dice[5], 0, 0.3), 2)


def refundable_of(dice: list[float]) -> int:
    return int(dice[6] > 0.45)


def past_of(dice: list[float]) -> int:
    return seeding.whole(dice[5], 0, 3)


def cancelled_of(index: int, dice: list[float]) -> int:
    return int(seeding.noise(seeding.seed_of(f"label-{index}")) < risk_of(features_from(dice)))


def features_from(dice: list[float]) -> dict:
    return {
        "lead_time_days": lead_of(dice),
        "nights": nights_of(dice),
        "amount": amount_of(dice),
        "channel": channel_of(dice),
        "is_refundable": refundable_of(dice),
        "past_cancels": past_of(dice),
    }


def logit(features: dict) -> float:
    return (
        WEIGHTS["bias"]
        + WEIGHTS["lead"] * features["lead_time_days"]
        + WEIGHTS["nights"] * features["nights"]
        + WEIGHTS["amount"] * features["amount"]
        + WEIGHTS["channel_web"] * (features["channel"] == "web")
        + WEIGHTS["channel_partner"] * (features["channel"] == "partner")
        + WEIGHTS["refundable"] * features["is_refundable"]
        + WEIGHTS["past_cancels"] * features["past_cancels"]
    )


def risk_of(features: dict) -> float:
    return 1 / (1 + math.exp(-max(-30.0, min(30.0, logit(features)))))


def risk_rows() -> list[tuple]:
    return [
        (row[0], row[1], row[2], row[3], row[4], row[6], risk_of(features_of(row)), round(risk_of(features_of(row)) * row[6], 2), row[10])
        for row in booking_rows()
    ]


def features_of(row: tuple) -> dict:
    return {"lead_time_days": row[4], "nights": row[5], "amount": row[6], "channel": row[3], "is_refundable": row[8], "past_cancels": row[9]}


SQL_TOTALS = """
select 100.0 * sum(cancelled) / count(*) as cancel_rate,
       sum(case when cancelled = 1 then amount else 0 end) as lost_gmv,
       sum(case when risk > 0.35 then 1 else 0 end) as at_risk,
       count(*) as bookings
from mart_cancel_risk
"""

SQL_BY_LEAD = """
select case
           when lead_time_days <= 7 then '0-7'
           when lead_time_days <= 14 then '8-14'
           when lead_time_days <= 30 then '15-30'
           when lead_time_days <= 60 then '31-60'
           when lead_time_days <= 90 then '61-90'
           else '90+'
       end as bucket,
       round(100.0 * sum(cancelled) / count(*), 2) as cancel_rate
from mart_cancel_risk
group by bucket
order by min(lead_time_days)
"""

SQL_TOP_RISK = """
select booking_id, hotel, lead_time_days, amount, round(risk * 100, 1) as risk
from mart_cancel_risk
order by risk desc
limit 6
"""


def totals(db: object) -> dict:
    return warehouse.query(db, SQL_TOTALS)[0]


def by_lead(db: object) -> list[dict]:
    return warehouse.query(db, SQL_BY_LEAD)


def top_risk(db: object) -> list[dict]:
    return warehouse.query(db, SQL_TOP_RISK)


def auc(rows: list[dict]) -> float:
    return auc_value(positive_ranks(rows), len(rows))


def positive_ranks(rows: list[dict]) -> list[int]:
    ordered = sorted(rows, key=lambda row: row["risk"])
    return [index + 1 for index, row in enumerate(ordered) if row["cancelled"]]


def auc_value(positives: list[int], total: int) -> float:
    pairs = len(positives) * (total - len(positives))
    return 0.5 if not pairs else round((sum(positives) - len(positives) * (len(positives) + 1) / 2) / pairs, 4)


def dashboard(db: object) -> dict:
    return envelope.dashboard(
        META,
        kpis=build_kpis(totals(db), auc(warehouse.query(db, "select risk, cancelled from mart_cancel_risk"))),
        charts=[envelope.chart("cancel_by_lead", "Доля отмен по сроку бронирования", "pct", [(row["bucket"], row["cancel_rate"]) for row in by_lead(db)])],
        grid=envelope.table(COLUMNS, top_risk(db)),
        lineage=LINEAGE,
        notes=NOTES,
    )


def build_kpis(totals_row: dict, auc_value: float) -> list[dict]:
    return [
        envelope.kpi("cancel_rate", "Доля отмен, %", totals_row["cancel_rate"], "pct", -0.6),
        envelope.kpi("lost_gmv", "Потеря GMV, ₽", totals_row["lost_gmv"], "rub", -2.4),
        envelope.kpi("at_risk", "Брони в риске", totals_row["at_risk"], "count", 1.1),
        envelope.kpi("auc", "ROC AUC модели", auc_value, "score", 0.8),
    ]


def widget(db: object, payload: dict) -> dict:
    return score_payload(features_of_payload(payload))


def features_of_payload(payload: dict) -> dict:
    return {
        "lead_time_days": float(payload.get("lead_time_days") or 35),
        "nights": 3.0,
        "amount": float(payload.get("amount") or 42000),
        "channel": str(payload.get("channel") or "web"),
        "is_refundable": 1,
        "past_cancels": 0,
    }


def score_payload(features: dict) -> dict:
    risk = risk_of(features)
    return {"risk": round(risk, 4), "expected_loss": round(risk * features["amount"], 2), "action": action_of(risk)}


def action_of(risk: float) -> str:
    return "предоплата 30%" if risk > 0.55 else "предоплата 10%" if risk > 0.35 else "без предоплаты"


COLUMNS = [
    envelope.column("booking_id", "Бронь"),
    envelope.column("hotel", "Отель"),
    envelope.column("lead_time_days", "Дней до заезда", "right", "count"),
    envelope.column("amount", "Сумма, ₽", "right", "rub"),
    envelope.column("risk", "Риск, %", "right", "pct"),
]

LINEAGE = envelope.pipeline(
    [
        ("stg_bookings_events", "staging", ROWS, "каждый час"),
        ("int_booking_features", "intermediate", ROWS, "каждый час"),
        ("mart_cancel_risk", "mart", ROWS, "каждые 30 минут"),
    ]
)

NOTES = [
    "Скор — логистическая регрессия с фиксированными весами: интерпретируемо и воспроизводимо в dbt-тестах.",
    "ROC AUC считается по витрине, а не по офлайн-выборке, поэтому метрика всегда соответствует проду.",
    "Порог 0.35 используется как триггер предоплаты: риск выше — бронь уходит в отдельную очередь.",
]
