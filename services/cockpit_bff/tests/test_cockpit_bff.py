"""Тесты кокпита: сводка, фильтры, алерты, продуктовые срезы и копайлот."""

from __future__ import annotations

from fastapi.testclient import TestClient

from cockpit_bff import service
from cockpit_bff.app import app

CLIENT = TestClient(app)


def overview(period: int = 7, city: str = "") -> dict:
    return CLIENT.get("/api/overview", params={"period": period, "city": city}).json()


def test_health() -> None:
    assert CLIENT.get("/health").json()["status"] == "ok"


def test_overview_contract() -> None:
    payload = overview()
    assert {"period", "city", "updatedAt", "kpis", "trend", "destinations", "alerts", "health"} <= set(payload)


def test_overview_has_eight_kpis() -> None:
    assert len(overview()["kpis"]) == 8


def test_period_slices_trend() -> None:
    assert len(overview(period=5)["trend"]) <= 5 < len(overview(period=28)["trend"]) + 1


def test_city_filter_returns_single_city() -> None:
    assert [row["city"] for row in overview(city="Сочи")["destinations"]] == ["Сочи"]


def test_destinations_sorted_by_gmv() -> None:
    gmv = [row["gmv"] for row in overview()["destinations"]]
    assert gmv == sorted(gmv, reverse=True)


def test_destination_row_is_enriched() -> None:
    row = overview()["destinations"][0]
    assert {"city", "bookings", "gmv", "adr", "cancel_rate", "coverage", "hotels"} <= set(row)


def test_coverage_within_bounds() -> None:
    assert all(0 <= row["coverage"] <= 100 for row in overview()["destinations"])


def test_alerts_have_severity() -> None:
    assert {alert["severity"] for alert in overview()["alerts"]} <= {"fail", "warn", "info"}


def test_health_covers_all_services() -> None:
    assert len(overview()["health"]) == 8


def test_health_statuses_known() -> None:
    assert {row["status"] for row in overview()["health"]} <= {"ok", "warn", "fail"}


def test_money_slice() -> None:
    payload = CLIENT.get("/api/money").json()
    assert payload["reconciliation"] and payload["coverage"]


def test_trust_slice() -> None:
    payload = CLIENT.get("/api/trust").json()
    assert payload["checks"] and payload["models"]


def test_pricing_slice() -> None:
    payload = CLIENT.get("/api/pricing").json()
    assert len(payload["curve"]) == 6 and payload["forecast"]


def test_risks_slice() -> None:
    payload = CLIENT.get("/api/risks").json()
    assert len(payload["policy"]) == 4 and payload["top"]


def test_ask_returns_sql() -> None:
    payload = CLIENT.get("/api/ask", params={"q": "выручка по каналам за неделю"}).json()
    assert payload["sql"] and payload["rows"]


def test_ask_defaults_to_first_question() -> None:
    assert CLIENT.get("/api/ask").json()["question"]


def test_overview_is_reproducible() -> None:
    assert overview() == overview()


def test_cancel_rate_is_realistic() -> None:
    rate = service.cancel.totals(service.DB["cancel"])["cancel_rate"]
    assert 5 <= rate <= 45
