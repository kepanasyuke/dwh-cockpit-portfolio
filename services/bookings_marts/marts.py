"""Витрина бронирований: схема «звезда», GMV, ADR, конверсия по каналам и направлениям."""

from __future__ import annotations

from _shared import envelope, seeding, warehouse

META = {
    "slug": "bookings-marts",
    "title": "Витрина бронирований",
    "subtitle": "Схема «звезда»: GMV, ADR и конверсия по каналам",
    "engine": "SQLite · in-memory (прод: PostgreSQL + dbt)",
    "updated_at": "2026-11-08 06:12 MSK",
}

SCHEMA = """
create table dim_city (city_id integer primary key, city text, country text);
create table dim_channel (channel_id integer primary key, channel text, kind text);
create table dim_date (date_id integer primary key, day text, week integer, is_weekend integer);
create table fact_bookings (
    booking_id integer primary key,
    date_id integer references dim_date(date_id),
    city_id integer references dim_city(city_id),
    channel_id integer references dim_channel(channel_id),
    nights integer,
    rooms integer,
    amount numeric,
    guests integer,
    status text
);
"""

ROWS = 420


def city_rows() -> list[tuple]:
    return [(index + 1, city, country) for index, (city, country, _, _) in enumerate(seeding.CITIES)]


def channel_rows() -> list[tuple]:
    kinds = ["direct", "direct", "affiliate", "corporate"]
    return [(index + 1, name, kinds[index]) for index, name in enumerate(seeding.CHANNELS)]


def date_rows() -> list[tuple]:
    return [(index + 1, seeding.day(index), index // 7 + 1, int(index % 7 >= 5)) for index in range(28)]


def booking_rows() -> list[tuple]:
    return [booking_of(index) for index in range(ROWS)]


def booking_of(index: int) -> tuple:
    return booking_tuple(index, seeding.series(seeding.seed_of(f"booking-{index}"), 6))


def booking_tuple(index: int, dice: list[float]) -> tuple:
    return (
        index + 1,
        seeding.whole(dice[0], 1, 28),
        seeding.whole(dice[0], 1, len(seeding.CITIES)),
        seeding.whole(dice[1], 1, len(seeding.CHANNELS)),
        nights_of(dice),
        rooms_of(dice),
        amount_of(dice),
        seeding.whole(dice[2], 1, 4),
        status_of(dice),
    )


def nights_of(dice: list[float]) -> int:
    return seeding.whole(dice[2], 1, 9)


def rooms_of(dice: list[float]) -> int:
    return seeding.whole(dice[3], 1, 3)


def amount_of(dice: list[float]) -> float:
    return round(seeding.between(dice[4], 4200, 96000) * rooms_of(dice) * (0.6 + nights_of(dice) / 10), 2)


def status_of(dice: list[float]) -> str:
    return "cancelled" if dice[5] > 0.83 else "confirmed"


TABLES = {
    "dim_city": city_rows(),
    "dim_channel": channel_rows(),
    "dim_date": date_rows(),
    "fact_bookings": booking_rows(),
}

SQL_CHANNEL_MART = """
with paid as (
    select b.channel_id, c.channel, count(*) as bookings, sum(b.amount) as gmv, avg(b.amount) as adr
    from fact_bookings b join dim_channel c using (channel_id)
    where b.status = 'confirmed'
    group by b.channel_id, c.channel
),
all_orders as (
    select channel_id, count(*) as attempts from fact_bookings group by channel_id
)
select p.channel,
       p.bookings,
       round(p.gmv, 2) as gmv,
       round(p.adr, 2) as adr,
       round(100.0 * p.bookings / a.attempts, 2) as conversion
from paid p join all_orders a using (channel_id)
order by gmv desc
"""

SQL_CITY_CHART = """
with city_gmv as (
    select d.city, sum(f.amount) as gmv
    from fact_bookings f
    join dim_city d using (city_id)
    where f.status = 'confirmed'
    group by d.city
)
select city, gmv from city_gmv order by gmv desc limit 7
"""

SQL_TOTALS = """
select coalesce(sum(case when status = 'confirmed' then amount else 0 end), 0) as gmv,
       count(*) as bookings,
       coalesce(avg(case when status = 'confirmed' then amount end), 0) as adr,
       100.0 * sum(case when status = 'confirmed' then 1 else 0 end) / count(*) as conversion
from fact_bookings
"""


def connect() -> object:
    return warehouse.build(SCHEMA, TABLES)


def totals(db: object) -> dict:
    return warehouse.query(db, SQL_TOTALS)[0]


def channel_mart(db: object) -> list[dict]:
    return warehouse.query(db, SQL_CHANNEL_MART)


def city_chart(db: object) -> list[dict]:
    return warehouse.query(db, SQL_CITY_CHART)


def dashboard(db: object) -> dict:
    return envelope.dashboard(
        META,
        kpis=build_kpis(totals(db)),
        charts=build_charts(city_chart(db)),
        grid=envelope.table(TABLE_COLUMNS, channel_mart(db)),
        lineage=LINEAGE,
        notes=NOTES,
    )


def build_kpis(totals_row: dict) -> list[dict]:
    return [
        envelope.kpi("gmv", "GMV, ₽", totals_row["gmv"], "rub", 4.8),
        envelope.kpi("bookings", "Бронирований", totals_row["bookings"], "count", 2.1),
        envelope.kpi("adr", "ADR, ₽", totals_row["adr"], "rub", -1.3),
        envelope.kpi("conversion", "Конверсия, %", totals_row["conversion"], "pct", 0.9),
    ]


def build_charts(cities: list[dict]) -> list[dict]:
    return [envelope.chart("gmv_by_city", "GMV по городам", "rub", [(row["city"], row["gmv"]) for row in cities])]


def widget(db: object, payload: dict) -> dict:
    channel = str(payload.get("channel") or "web")
    return channel_forecast(channel_mart(db), channel)


def channel_forecast(mart: list[dict], channel: str) -> dict:
    return forecast_payload(channel, base_row(mart, channel))


def base_row(mart: list[dict], channel: str) -> dict:
    found = [row for row in mart if row["channel"] == channel]
    return found[0] if found else {"gmv": 0, "adr": 0, "conversion": 0, "bookings": 0}


def forecast_payload(channel: str, base: dict) -> dict:
    return {
        "channel": channel,
        "gmv": base["gmv"],
        "adr": base["adr"],
        "conversion": base["conversion"],
        "bookings": base["bookings"],
        "note": "прогноз на 7 дней: GMV × 1.05, ADR без изменений",
    }


TABLE_COLUMNS = [
    envelope.column("channel", "Канал"),
    envelope.column("bookings", "Брони", "right", "count"),
    envelope.column("gmv", "GMV, ₽", "right", "rub"),
    envelope.column("adr", "ADR, ₽", "right", "rub"),
    envelope.column("conversion", "CR, %", "right", "pct"),
]

LINEAGE = envelope.pipeline(
    [
        ("stg_bookings", "staging", ROWS, "каждый час"),
        ("int_booking_revenue", "intermediate", ROWS, "каждый час"),
        ("mart_channel_performance", "mart", 4, "ежедневно 06:00"),
    ]
)

NOTES = [
    "Факт-таблица ссылается на измерения через суррогатные ключи: схема «звезда» в третьей нормальной форме измерений.",
    "Конверсия считается как доля подтверждённых броней от всех заявок канала.",
    "Витрина mart_channel_performance пересобирается dbt-моделью с тестами not_null и unique на ключ канала.",
]
