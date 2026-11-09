"""Покрытие партнёрской сети: Data Vault 2.0 (hub / link / satellite) и gap-анализ направлений."""

from __future__ import annotations

from _shared import envelope, seeding, warehouse

META = {
    "slug": "partner-coverage",
    "title": "Покрытие сети",
    "subtitle": "Data Vault по поставщикам и gap-анализ направлений",
    "engine": "SQLite · in-memory (прод: Trino + Hive/Iceberg)",
    "updated_at": "2026-11-08 02:30 MSK",
}

SCHEMA = """
create table hub_hotel (hub_key integer primary key, hotel_name text, city text);
create table link_hotel_supplier (link_key integer primary key, hub_key integer, supplier text, external_id text);
create table sat_supplier_terms (hub_key integer, supplier text, commission numeric, active integer, load_date text);
create table market_demand (city text primary key, demand integer);
create table mart_coverage (city text primary key, hotels integer, demand integer, coverage numeric, top_supplier text);
"""

HOTELS_PER_CITY = 14

MART_LOAD = """
insert into mart_coverage
with per_city as (
    select city, count(distinct hub_key) as hotels
    from hub_hotel
    group by city
),
per_supplier as (
    select h.city,
           l.supplier,
           count(*) as cnt,
           row_number() over (partition by h.city order by count(*) desc) as rn
    from hub_hotel h
    join link_hotel_supplier l using (hub_key)
    group by h.city, l.supplier
)
select d.city,
       coalesce(pc.hotels, 0) as hotels,
       d.demand,
       min(100.0, round(100.0 * coalesce(pc.hotels, 0) / max(3, round(d.demand / 600.0)), 1)) as coverage,
       coalesce(ps.supplier, '—') as top_supplier
from market_demand d
left join per_city pc on pc.city = d.city
left join per_supplier ps on ps.city = d.city and ps.rn = 1
"""


def connect() -> object:
    return materialise(warehouse.build(SCHEMA, TABLES))


def materialise(db: object) -> object:
    warehouse.script(db, MART_LOAD)
    return db


def hub_rows() -> list[tuple]:
    return [
        (city_index * 100 + index + 1, seeding.hotel_name(city_index * 100 + index, city), city)
        for city_index, (city, _, _, _) in enumerate(seeding.CITIES)
        for index in range(hotels_in(city))
    ]


def hotels_in(city: str) -> int:
    return seeding.whole(seeding.noise(seeding.seed_of(city + "-hotels")), 4, HOTELS_PER_CITY)


def link_rows() -> list[tuple]:
    return [
        (hub_key * 10 + index + 1, hub_key, supplier, f"EXT-{hub_key}-{index}")
        for hub_key, _, _ in hub_rows()
        for index, supplier in enumerate(suppliers_of(hub_key))
    ]


def suppliers_of(hub_key: int) -> list[str]:
    dice = seeding.series(seeding.seed_of(f"link-{hub_key}"), 2)
    return [str(seeding.pick(seeding.SUPPLIERS, dice[0])), str(seeding.pick(seeding.SUPPLIERS, dice[1]))]


def sat_rows() -> list[tuple]:
    return [
        (row[0], row[1], round(seeding.between(seeding.noise(seeding.seed_of(f"sat-{row[0]}{row[1]}")), 8, 24), 2), 1, "2026-11-07")
        for row in link_rows()
    ]


def demand_rows() -> list[tuple]:
    return [(city, seeding.whole(seeding.noise(seeding.seed_of(city + "-demand")), 400, 9000)) for city, _, _, _ in seeding.CITIES]


TABLES = {
    "hub_hotel": hub_rows(),
    "link_hotel_supplier": link_rows(),
    "sat_supplier_terms": sat_rows(),
    "market_demand": demand_rows(),
}

SQL_SUMMARY = """
select (select count(*) from hub_hotel) as hotels,
       round(avg(coverage), 1) as coverage,
       sum(case when coverage < 60 then 1 else 0 end) as gaps,
       (select count(*) - count(distinct hotel_name || city) from hub_hotel) as duplicates
from mart_coverage
"""

SQL_CITIES = """
select city, hotels, demand, coverage, top_supplier
from mart_coverage
order by coverage asc
"""


def summary(db: object) -> dict:
    return warehouse.query(db, SQL_SUMMARY)[0]


def cities(db: object) -> list[dict]:
    return warehouse.query(db, SQL_CITIES)


def build_kpis(totals: dict) -> list[dict]:
    return [
        envelope.kpi("hotels", "Отелей в каталоге", totals["hotels"], "count", 5.1),
        envelope.kpi("coverage", "Покрытие спроса, %", totals["coverage"], "pct", 2.3),
        envelope.kpi("gaps", "Направлений в дефиците", totals["gaps"], "count", -1.0),
        envelope.kpi("duplicates", "Дублей в хабе", totals["duplicates"], "count", -100.0),
    ]


def dashboard(db: object) -> dict:
    return envelope.dashboard(
        META,
        kpis=build_kpis(summary(db)),
        charts=[envelope.chart("coverage_by_city", "Покрытие спроса по городам", "pct", [(row["city"], row["coverage"]) for row in cities(db)])],
        grid=envelope.table(COLUMNS, cities(db)),
        lineage=LINEAGE,
        notes=NOTES,
    )


def widget(db: object, payload: dict) -> dict:
    city = str(payload.get("city") or "Сочи")
    return {"city": city, "deficit": deficit_of(cities(db), city)}


def deficit_of(rows: list[dict], city: str) -> dict:
    found = [row for row in rows if row["city"] == city]
    return found[0] if found else {"city": city, "coverage": 0, "hotels": 0, "demand": 0, "top_supplier": "—"}


COLUMNS = [
    envelope.column("city", "Город"),
    envelope.column("hotels", "Отелей", "right", "count"),
    envelope.column("demand", "Спрос, брони", "right", "count"),
    envelope.column("coverage", "Покрытие, %", "right", "pct"),
    envelope.column("top_supplier", "Ключевой партнёр"),
]

LINEAGE = envelope.pipeline(
    [
        ("stg_supplier_feeds", "staging", 8 * HOTELS_PER_CITY, "каждые 4 часа"),
        ("hub_hotel + link_hotel_supplier", "intermediate", 8 * HOTELS_PER_CITY, "ежедневно"),
        ("mart_coverage", "mart", len(seeding.CITIES), "ежедневно 08:00"),
    ]
)

NOTES = [
    "Хаб хранит бизнес-ключ отеля, линк связывает его с поставщиками, сателлит — условия и комиссию.",
    "Дубли в хабе считаются по составному ключу hotel_name + city: это готовый DQ-тест для Data Vault.",
    "Покрытие — эвристика: отели города против целевого числа отелей (спрос / 600), потолок 100%.",
]
