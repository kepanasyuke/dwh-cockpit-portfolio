"""BFF кокпита: собирает восемь сервисов в один продуктовый ответ."""

from __future__ import annotations

from bookings_marts import marts as bookings
from cancel_radar import marts as cancel
from commission_recon import marts as commission
from data_quality import marts as quality
from demand_forecast import marts as demand
from nl_sql_copilot import marts as copilot
from partner_coverage import marts as coverage
from price_elasticity import marts as price
from _shared import envelope, warehouse

META = {
    "slug": "cockpit-bff",
    "title": "Кокпит Ostrovok",
    "subtitle": "Единая сводка по деньгам, спросу, рискам и доверию к данным",
    "engine": "BFF поверх 8 сервисов · SQLite in-memory",
    "updated_at": "2026-11-08 09:10 MSK",
}

DB = {
    "bookings": bookings.connect(),
    "cancel": cancel.connect(),
    "price": price.connect(),
    "demand": demand.connect(),
    "quality": quality.connect(),
    "coverage": coverage.connect(),
    "commission": commission.connect(),
    "copilot": copilot.connect(),
}

SQL_TREND = """
select d.day as day,
       round(sum(f.amount), 2) as gmv,
       count(*) as bookings
from fact_bookings f
join dim_date d using (date_id)
where f.status = 'confirmed'
group by d.day
order by d.day
"""

SQL_TREND_CITY = """
select d.day as day,
       round(sum(f.amount), 2) as gmv,
       count(*) as bookings
from fact_bookings f
join dim_date d using (date_id)
join dim_city c using (city_id)
where f.status = 'confirmed' and c.city = ?
group by d.day
order by d.day
"""

SQL_DESTINATIONS = """
select c.city as city,
       count(*) as bookings,
       round(sum(f.amount), 2) as gmv,
       round(avg(f.amount), 2) as adr
from fact_bookings f
join dim_city c using (city_id)
where f.status = 'confirmed'
group by c.city
order by gmv desc
"""

SQL_CANCEL_BY_CITY = """
select city, round(100.0 * sum(cancelled) / count(*), 2) as cancel_rate, round(sum(amount), 2) as exposure
from mart_cancel_risk
group by city
order by cancel_rate desc
"""

CANCEL_BY_CITY = warehouse.query(cancel.connect(), SQL_CANCEL_BY_CITY)
COVERAGE_BY_CITY = coverage.cities(DB["coverage"])


def trend(period: int, city: str | None) -> list[dict]:
    return trend_rows(city)[-period:]


def trend_rows(city: str | None) -> list[dict]:
    return warehouse.query(DB["bookings"], SQL_TREND_CITY, (city,)) if city else warehouse.query(DB["bookings"], SQL_TREND)


def destinations(period: int, city: str | None) -> list[dict]:
    return [row for row in merged_destinations() if not city or row["city"] == city]


def merged_destinations() -> list[dict]:
    return [enrich_row(row) for row in warehouse.query(DB["bookings"], SQL_DESTINATIONS)]


def enrich_row(row: dict) -> dict:
    return {**row, **cancel_figures(row["city"]), **coverage_figures(row["city"])}


def cancel_figures(city: str) -> dict:
    found = [row for row in CANCEL_BY_CITY if row["city"] == city]
    return {"cancel_rate": found[0]["cancel_rate"], "exposure": found[0]["exposure"]} if found else {"cancel_rate": 0.0, "exposure": 0.0}


def coverage_figures(city: str) -> dict:
    found = [row for row in COVERAGE_BY_CITY if row["city"] == city]
    return {"coverage": found[0]["coverage"], "hotels": found[0]["hotels"]} if found else {"coverage": 0.0, "hotels": 0}


def kpis() -> list[dict]:
    return [gmv_kpi(), bookings_kpi(), adr_kpi(), cancel_kpi(), mape_kpi(), slo_kpi(), mismatch_kpi(), coverage_kpi()]


def gmv_kpi() -> dict:
    return envelope.kpi("gmv", "GMV, ₽", bookings.totals(DB["bookings"])["gmv"], "rub", 4.8)


def bookings_kpi() -> dict:
    return envelope.kpi("bookings", "Бронирований", bookings.totals(DB["bookings"])["bookings"], "count", 2.1)


def adr_kpi() -> dict:
    return envelope.kpi("adr", "ADR, ₽", bookings.totals(DB["bookings"])["adr"], "rub", -1.3)


def cancel_kpi() -> dict:
    return envelope.kpi("cancel_rate", "Доля отмен, %", cancel.totals(DB["cancel"])["cancel_rate"], "pct", -0.6)


def mape_kpi() -> dict:
    return envelope.kpi("mape", "MAPE прогноза, %", demand.summary(DB["demand"])["mape"], "pct", -0.7)


def slo_kpi() -> dict:
    return envelope.kpi("slo", "SLO данных, %", quality.summary(DB["quality"])["slo"], "pct", 0.8)


def mismatch_kpi() -> dict:
    return envelope.kpi("mismatch", "Расхождение комиссий, ₽", commission.summary(DB["commission"])["mismatch"], "rub", -8.4)


def coverage_kpi() -> dict:
    return envelope.kpi("coverage", "Покрытие спроса, %", coverage.summary(DB["coverage"])["coverage"], "pct", 2.3)


def alerts() -> list[dict]:
    return slo_alert() + mismatch_alert() + coverage_alert() + demand_alert() + risk_alert()


def slo_alert() -> list[dict]:
    slo = round(quality.summary(DB["quality"])["slo"], 1)
    return [alert("fail", "SLO данных ниже цели", f"Соблюдение SLO {slo}% при цели 97%", "data-quality")] if slo < 97 else []


def mismatch_alert() -> list[dict]:
    total = commission.summary(DB["commission"])["mismatch"]
    return [alert("warn", "Расхождение по комиссиям", f"Открытых кейсов на {total:,.0f} ₽".replace(",", " "), "commission-recon")] if total > 100000 else []


def coverage_alert() -> list[dict]:
    gaps = coverage.summary(DB["coverage"])["gaps"]
    return [alert("warn", "Дефицит предложения", f"Направлений ниже 60% покрытия: {gaps}", "partner-coverage")] if gaps else []


def demand_alert() -> list[dict]:
    mape = demand.summary(DB["demand"])["mape"]
    return [alert("info", "Точность прогноза", f"MAPE {mape}% — в пределах нормы", "demand-forecast")] if mape <= 40 else []


def risk_alert() -> list[dict]:
    at_risk = cancel.totals(DB["cancel"])["at_risk"]
    return [alert("info", "Брони в зоне риска", f"{at_risk} броней требуют предоплаты", "cancel-radar")]


def alert(severity: str, title: str, detail: str, service: str) -> dict:
    return {"severity": severity, "title": title, "detail": detail, "service": service}


def health() -> list[dict]:
    return [
        health_row("bookings-marts", "ok", f"GMV {gmv_kpi()['value']:,.0f} ₽".replace(",", " ")),
        health_row("cancel-radar", "ok", f"отмен {cancel_kpi()['value']}%"),
        health_row("price-elasticity", "ok", f"эластичность {price.summary(DB['price'])['elasticity']}"),
        health_row("demand-forecast", "ok", f"MAPE {mape_kpi()['value']}%"),
        health_row("data-quality", status_of(slo_kpi()["value"]), f"SLO {slo_kpi()['value']}%"),
        health_row("partner-coverage", status_of(coverage_kpi()["value"]), f"покрытие {coverage_kpi()['value']}%"),
        health_row("commission-recon", "ok", f"сверка {commission.summary(DB['commission'])['auto_match']}%"),
        health_row("nl-sql-copilot", "ok", "каталог метрик обновлён"),
    ]


def status_of(value: float) -> str:
    return "fail" if value < 90 else "warn" if value < 97 else "ok"


def health_row(service: str, status: str, metric: str) -> dict:
    return {"service": service, "status": status, "metric": metric}


def overview(period: int = 7, city: str | None = None) -> dict:
    return {
        "period": period,
        "city": city or "all",
        "updatedAt": META["updated_at"],
        "kpis": kpis(),
        "trend": trend(period, city),
        "destinations": destinations(period, city),
        "alerts": alerts(),
        "health": health(),
    }


def money() -> dict:
    return {
        "reconciliation": commission.partners(DB["commission"]),
        "summary": commission.summary(DB["commission"]),
        "coverage": coverage.cities(DB["coverage"]),
        "coverageSummary": coverage.summary(DB["coverage"]),
    }


def trust() -> dict:
    return {
        "summary": quality.summary(DB["quality"]),
        "models": quality.models(DB["quality"]),
        "checks": quality.checks(DB["quality"]),
    }


def pricing() -> dict:
    return {
        "summary": price.summary(DB["price"]),
        "routes": price.route_rows(DB["price"]),
        "curve": price.demand_curve(DB["price"]),
        "forecast": demand.daily(DB["demand"]),
        "forecastSummary": demand.summary(DB["demand"]),
    }


def risks() -> dict:
    return {
        "summary": cancel.totals(DB["cancel"]),
        "top": cancel.top_risk(DB["cancel"]),
        "buckets": cancel.by_lead(DB["cancel"]),
        "auc": cancel.auc(warehouse.query(DB["cancel"], "select risk, cancelled from mart_cancel_risk")),
        "policy": [{"risk": threshold, "action": cancel.action_of(threshold)} for threshold in (0.2, 0.4, 0.6, 0.8)],
    }


def ask(question: str) -> dict:
    return copilot.ask(DB["copilot"], question)


def project_row(row: dict) -> dict:
    return {column["key"]: row.get(column["key"]) for column in DESTINATION_COLUMNS}


def dashboard() -> dict:
    return envelope.dashboard(
        META,
        kpis=kpis(),
        charts=[envelope.chart("gmv_trend", "GMV по дням", "rub", [(row["day"][-2:], row["gmv"]) for row in trend(7, None)])],
        grid=envelope.table(DESTINATION_COLUMNS, [project_row(row) for row in destinations(7, None)[:6]]),
        lineage=envelope.pipeline(
            [
                ("bookings-marts", "staging", 420, "каждый час"),
                ("cancel-radar · demand-forecast", "intermediate", 480, "каждый час"),
                ("cockpit_bff", "mart", 8, "по запросу"),
            ]
        ),
        notes=[
            "BFF собирает ответы восьми сервисов в один продуктовый контракт: фронтенду достаточно одного порта.",
            "Алерты считаются по порогам бизнеса: SLO ниже 97%, расхождение комиссий больше 100 000 ₽, дефицит покрытия.",
            "Фильтры периода и города применяются на стороне BFF, сервисы остаются независимыми.",
        ],
    )


def widget(payload: dict) -> dict:
    return ask(str(payload.get("question") or "сколько мы заработали за неделю"))


DESTINATION_COLUMNS = [
    envelope.column("city", "Город"),
    envelope.column("bookings", "Брони", "right", "count"),
    envelope.column("gmv", "GMV, ₽", "right", "rub"),
    envelope.column("adr", "ADR, ₽", "right", "rub"),
    envelope.column("cancel_rate", "Отмены, %", "right", "pct"),
    envelope.column("coverage", "Покрытие, %", "right", "pct"),
]
