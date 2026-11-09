"""Сверка комиссий: федеративный запрос Trino по двум источникам и реестр расхождений."""

from __future__ import annotations

from _shared import envelope, seeding, warehouse

META = {
    "slug": "commission-recon",
    "title": "Сверка комиссий",
    "subtitle": "Trino-федерация: начисления против биллинга партнёров",
    "engine": "SQLite · in-memory (прод: Trino, catalogs payout + billing)",
    "updated_at": "2026-11-08 08:20 MSK",
}

SCHEMA = """
create table fact_payouts (partner text, day integer, accrued numeric);
create table fact_billing (partner text, day integer, billed numeric);
create table mart_reconciliation (partner text primary key, accrued numeric, billed numeric, diff numeric, status text);
"""

PARTNERS = seeding.SUPPLIERS + ["Trevolution", "HRS Group"]
DAYS = 6

MART_LOAD = """
insert into mart_reconciliation
with payouts as (
    select partner, sum(accrued) as accrued from fact_payouts group by partner
),
billing as (
    select partner, sum(billed) as billed from fact_billing group by partner
),
merged as (
    select partner, accrued, 0 as billed from payouts
    union all
    select partner, 0 as accrued, billed from billing
)
select partner,
       round(sum(accrued), 2) as accrued,
       round(sum(billed), 2) as billed,
       round(sum(accrued) - sum(billed), 2) as diff,
       case
           when abs(sum(accrued) - sum(billed)) < 1 then 'matched'
           when abs(sum(accrued) - sum(billed)) < 900 then 'minor'
           else 'open'
       end as status
from merged
group by partner
"""


def connect() -> object:
    return materialise(warehouse.build(SCHEMA, {"fact_payouts": payout_rows(), "fact_billing": billing_rows()}))


def materialise(db: object) -> object:
    warehouse.script(db, MART_LOAD)
    return db


def payout_rows() -> list[tuple]:
    return [(partner, day_index, accrued_of(partner, day_index)) for partner in PARTNERS for day_index in range(DAYS)]


def billing_rows() -> list[tuple]:
    return [(partner, day_index, billed_of(partner, day_index)) for partner in PARTNERS for day_index in range(DAYS)]


def accrued_of(partner: str, day_index: int) -> float:
    return round(seeding.between(seeding.noise(seeding.seed_of(f"pay-{partner}-{day_index}")), 48000, 920000), 2)


def billed_of(partner: str, day_index: int) -> float:
    drift = 1 + (seeding.noise(seeding.seed_of(f"bill-{partner}-{day_index}")) - 0.5) * 0.02
    return round(accrued_of(partner, day_index) * drift, 2)


SQL_SUMMARY = """
select (select round(sum(accrued), 2) from mart_reconciliation) as payouts,
       round(sum(abs(diff)), 2) as mismatch,
       sum(case when status = 'open' then 1 else 0 end) as open_cases,
       round(100.0 * sum(case when status = 'matched' then 1 else 0 end) / count(*), 1) as auto_match
from mart_reconciliation
"""

SQL_PARTNERS = """
select partner, accrued, billed, diff, status
from mart_reconciliation
order by abs(diff) desc
"""

SQL_DAILY = """
select p.day as day,
       round(sum(abs(p.accrued - b.billed)), 2) as mismatch
from fact_payouts p
join fact_billing b on b.partner = p.partner and b.day = p.day
group by p.day
order by p.day
"""


def summary(db: object) -> dict:
    return warehouse.query(db, SQL_SUMMARY)[0]


def partners(db: object) -> list[dict]:
    return warehouse.query(db, SQL_PARTNERS)


def daily(db: object) -> list[dict]:
    return warehouse.query(db, SQL_DAILY)


def build_kpis(totals: dict) -> list[dict]:
    return [
        envelope.kpi("payouts", "Начислено, ₽", totals["payouts"], "rub", 3.7),
        envelope.kpi("mismatch", "Расхождение, ₽", totals["mismatch"], "rub", -8.4),
        envelope.kpi("open_cases", "Открытых кейсов", totals["open_cases"], "count", -1.0),
        envelope.kpi("auto_match", "Автосверка, %", totals["auto_match"], "pct", 1.6),
    ]


def dashboard(db: object) -> dict:
    return envelope.dashboard(
        META,
        kpis=build_kpis(summary(db)),
        charts=[envelope.chart("mismatch_daily", "Расхождение по дням", "rub", [(f"Д{row['day'] + 1}", row["mismatch"]) for row in daily(db)])],
        grid=envelope.table(COLUMNS, partners(db)),
        lineage=LINEAGE,
        notes=NOTES,
    )


def widget(db: object, payload: dict) -> dict:
    partner = str(payload.get("partner") or PARTNERS[0])
    return {"partner": partner, "cases": cases_of(db, partner)}


def cases_of(db: object, partner: str) -> list[dict]:
    return warehouse.query(db, "select partner, accrued, billed, diff, status from mart_reconciliation where partner = ?", (partner,))


COLUMNS = [
    envelope.column("partner", "Партнёр"),
    envelope.column("accrued", "Начислено, ₽", "right", "rub"),
    envelope.column("billed", "Биллинг, ₽", "right", "rub"),
    envelope.column("diff", "Разница, ₽", "right", "rub"),
    envelope.column("status", "Статус", "right", "text"),
]

LINEAGE = envelope.pipeline(
    [
        ("stg_payouts", "staging", len(PARTNERS) * DAYS, "ежедневно 05:00"),
        ("stg_billing", "staging", len(PARTNERS) * DAYS, "ежедневно 05:10"),
        ("mart_reconciliation", "mart", len(PARTNERS), "ежедневно 05:40"),
    ]
)

NOTES = [
    "Два каталога Trino соединяются одним запросом: payout из внутреннего DWH, billing — из API партнёров.",
    "Статус matched — расхождение меньше рубля, minor — до 900 ₽, остальное уходит в ручную очередь.",
    "Витрина полная: партнёр без биллинга всё равно попадает в реестр как открытый кейс.",
]
