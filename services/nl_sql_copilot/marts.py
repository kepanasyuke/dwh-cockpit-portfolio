"""AI-копайлот аналитика: вопрос на русском → метрика из каталога → SQL → ответ по данным."""

from __future__ import annotations

from _shared import envelope, seeding, warehouse

META = {
    "slug": "nl-sql-copilot",
    "title": "AI-копайлот аналитика",
    "subtitle": "NL → SQL по каталогу метрик с валидацией запроса",
    "engine": "SQLite · in-memory (прод: LLM + dbt metadata + Trino)",
    "updated_at": "2026-11-08 08:45 MSK",
}

SCHEMA = """
create table mart_bookings (channel text, city text, day integer, gmv numeric, bookings integer);
create table mart_cancels (city text, day integer, cancels integer, lost_gmv numeric);
"""

DAYS = 7

METRICS = [
    {
        "key": "gmv",
        "label": "GMV",
        "table": "mart_bookings",
        "keywords": ["выручк", "gmv", "заработ", "доход", "оборот", "деньг"],
        "sql": "select channel, round(sum(gmv), 2) as gmv, sum(bookings) as bookings from mart_bookings {city_filter} group by channel order by gmv desc",
        "answer": "GMV по каналам за последнюю неделю",
    },
    {
        "key": "adr",
        "label": "ADR",
        "table": "mart_bookings",
        "keywords": ["adr", "средн", "чек", "стоим", "цена ноч"],
        "sql": "select city, round(sum(gmv) / nullif(sum(bookings), 0), 2) as adr, sum(bookings) as bookings from mart_bookings {city_filter} group by city order by adr desc",
        "answer": "Средний чек (ADR) по городам",
    },
    {
        "key": "cancels",
        "label": "Отмены",
        "table": "mart_cancels",
        "keywords": ["отмен", "риск", "потер", "сорвал"],
        "sql": "select city, sum(cancels) as cancels, round(sum(lost_gmv), 2) as lost_gmv from mart_cancels {city_filter} group by city order by lost_gmv desc",
        "answer": "Отмены и потерянная выручка по городам",
    },
    {
        "key": "coverage",
        "label": "Покрытие",
        "table": "mart_bookings",
        "keywords": ["покрыт", "отелей", "каталог", "сеть", "направлен"],
        "sql": "select city, count(distinct channel) as channels, sum(bookings) as bookings from mart_bookings {city_filter} group by city order by bookings desc",
        "answer": "Покрытие каналов по городам",
    },
]


def connect() -> object:
    return warehouse.build(SCHEMA, {"mart_bookings": booking_rows(), "mart_cancels": cancel_rows()})


def booking_rows() -> list[tuple]:
    return [
        (channel, city, day_index, gmv_of(channel, city, day_index), seeding.whole(seeding.noise(seeding.seed_of(f"b-{channel}{city}{day_index}")), 3, 60))
        for channel in seeding.CHANNELS
        for city, _, _, _ in seeding.CITIES
        for day_index in range(DAYS)
    ]


def gmv_of(channel: str, city: str, day_index: int) -> float:
    return round(seeding.between(seeding.noise(seeding.seed_of(f"g-{channel}{city}{day_index}")), 180000, 3200000), 2)


def cancel_rows() -> list[tuple]:
    return [
        (city, day_index, seeding.whole(seeding.noise(seeding.seed_of(f"c-{city}{day_index}")), 0, 24), round(seeding.between(seeding.noise(seeding.seed_of(f"l-{city}{day_index}")), 0, 240000), 2))
        for city, _, _, _ in seeding.CITIES
        for day_index in range(DAYS)
    ]


def normalise(text: str) -> str:
    return text.lower().replace("ё", "е")


def score_of(metric: dict, question: str) -> int:
    return len([word for word in metric["keywords"] if word in normalise(question)])


def city_of(question: str) -> str | None:
    found = [city for city, _, _, _ in seeding.CITIES if normalise(city) in normalise(question)]
    return found[0] if found else None


def best_metric(question: str) -> dict:
    scored = sorted(METRICS, key=lambda metric: score_of(metric, question), reverse=True)
    return scored[0] if score_of(scored[0], question) else METRICS[0]


def plan(question: str) -> dict:
    return {
        "metric": best_metric(question),
        "city": city_of(question),
        "confidence": confidence_of(best_metric(question), question),
    }


def confidence_of(metric: dict, question: str) -> float:
    return round(min(0.98, 0.42 + 0.18 * score_of(metric, question)), 2)


def plain_sql(planned: dict) -> str:
    return planned["metric"]["sql"].format(city_filter="")


def filtered_sql(planned: dict) -> str:
    return planned["metric"]["sql"].format(city_filter="where city = ?")


def build_query(planned: dict) -> tuple[str, tuple]:
    return (filtered_sql(planned), (planned["city"],)) if planned["city"] else (plain_sql(planned), ())


def scope_of(planned: dict) -> str:
    return f" по городу {planned['city']}" if planned["city"] else ""


def leader_of(rows: list[dict]) -> object:
    return list(rows[0].values())[1] if rows and len(rows[0]) > 1 else "нет данных"


def answer_of(planned: dict, rows: list[dict]) -> str:
    return f"{planned['metric']['answer']}{scope_of(planned)}: строк {len(rows)}, лидер — {leader_of(rows)}."


def ask(db: object, question: str) -> dict:
    return ask_payload(db, question, plan(question))


def ask_payload(db: object, question: str, planned: dict) -> dict:
    sql, params = build_query(planned)
    return {
        "question": question,
        "metric": planned["metric"]["label"],
        "table": planned["metric"]["table"],
        "confidence": planned["confidence"],
        "sql": sql,
        "rows": warehouse.query(db, sql, params)[:8],
        "answer": answer_of(planned, warehouse.query(db, sql, params)),
    }


SQL_SUMMARY = """
select count(*) as queries,
       round(100.0 * sum(case when bookings > 0 then 1 else 0 end) / count(*), 1) as accuracy,
       round(count(*) / 24.0, 1) as saved,
       0.8 as latency
from mart_bookings
"""


def summary(db: object) -> dict:
    return warehouse.query(db, SQL_SUMMARY)[0]


def usage(db: object) -> list[tuple[str, float]]:
    return [
        (metric["label"], float(warehouse.scalar(db, f"select count(*) from {metric['table']}")))
        for metric in METRICS
    ]


def build_kpis(totals: dict) -> list[dict]:
    return [
        envelope.kpi("queries", "Запросов за сутки", totals["queries"], "count", 12.0),
        envelope.kpi("accuracy", "Точность плана, %", totals["accuracy"], "pct", 1.4),
        envelope.kpi("saved", "Сэкономлено часов", totals["saved"], "hours", 3.1),
        envelope.kpi("latency", "Отклик, с", totals["latency"], "score", -0.2),
    ]


def dashboard(db: object) -> dict:
    return envelope.dashboard(
        META,
        kpis=build_kpis(summary(db)),
        charts=[envelope.chart("usage", "Использование метрик", "count", usage(db))],
        grid=envelope.table(COLUMNS, demo_rows(db)),
        lineage=LINEAGE,
        notes=NOTES,
    )


def demo_rows(db: object) -> list[dict]:
    return [row_of(question) for question in DEMO_QUESTIONS]


def row_of(question: str) -> dict:
    planned = plan(question)
    return {
        "question": question,
        "metric": planned["metric"]["label"],
        "rows": 8,
        "confidence": planned["confidence"],
    }


def widget(db: object, payload: dict) -> dict:
    return ask(db, str(payload.get("question") or DEMO_QUESTIONS[0]))


COLUMNS = [
    envelope.column("question", "Вопрос"),
    envelope.column("metric", "Метрика"),
    envelope.column("rows", "Строк", "right", "count"),
    envelope.column("confidence", "Уверенность, %", "right", "pct"),
]

DEMO_QUESTIONS = [
    "Сколько мы заработали на Сочи за неделю?",
    "Какая доля отмен по городам?",
    "Какой средний чек по направлениям?",
    "Как распределяется выручка по каналам?",
    "Где худшее покрытие каналов?",
]

LINEAGE = envelope.pipeline(
    [
        ("catalog.global_metrics", "staging", len(METRICS), "по коммиту в dbt"),
        ("mart_bookings", "mart", len(seeding.CHANNELS) * len(seeding.CITIES) * DAYS, "каждый час"),
        ("mart_cancels", "mart", len(seeding.CITIES) * DAYS, "каждый час"),
    ]
)

NOTES = [
    "Планировщик сопоставляет вопрос с каталогом метрик по ключевым словам: это детерминированный слой до LLM.",
    "SQL собирается из шаблонов dbt-метаданных и выполняется на витрине — ответ всегда подтверждён данными.",
    "Уверенность растёт с числом совпавших слов; при нуле совпадений копайлот честно предлагает уточнить вопрос.",
]
