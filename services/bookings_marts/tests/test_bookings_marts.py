"""Тесты витрины бронирований: контракт API, арифметика витрины и границы модели."""

from __future__ import annotations

from fastapi.testclient import TestClient

from bookings_marts import marts
from bookings_marts.app import app

CLIENT = TestClient(app)


def test_health() -> None:
    assert CLIENT.get("/health").json()["status"] == "ok"


def test_dashboard_contract() -> None:
    payload = CLIENT.get("/api/dashboard").json()
    assert payload["project"] == "bookings-marts" and len(payload["kpis"]) == 4 and payload["table"]["rows"]


def test_gmv_equals_sum_of_channel_gmv() -> None:
    db = marts.connect()
    assert abs(marts.totals(db)["gmv"] - sum(row["gmv"] for row in marts.channel_mart(db))) < 0.01


def test_conversion_within_bounds() -> None:
    assert 0 <= marts.totals(marts.connect())["conversion"] <= 100


def test_widget_unknown_channel_returns_zeros() -> None:
    assert CLIENT.post("/api/widget", json={"channel": "unknown"}).json()["gmv"] == 0


def test_widget_known_channel_returns_mart_row() -> None:
    payload = CLIENT.post("/api/widget", json={"channel": "web"}).json()
    assert payload["channel"] == "web" and payload["bookings"] > 0
