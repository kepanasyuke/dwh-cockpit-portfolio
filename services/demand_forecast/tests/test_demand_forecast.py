"""Тесты прогноза спроса: бэктест на истории, MAPE и план по дням недели."""

from __future__ import annotations

from fastapi.testclient import TestClient

from demand_forecast import marts
from demand_forecast.app import app

CLIENT = TestClient(app)


def test_health() -> None:
    assert CLIENT.get("/health").json()["status"] == "ok"


def test_backtest_rows_cover_horizon() -> None:
    db = marts.connect()
    assert len(marts.route_rows(db)) == 8 and len(marts.daily(db)) == marts.BACKTEST_DAYS


def test_mape_is_reasonable() -> None:
    assert marts.summary(marts.connect())["mape"] < 40


def test_plan_respects_weekend_peak() -> None:
    assert marts.plan_for(marts.ROUTES[0], 5) > marts.plan_for(marts.ROUTES[0], 1)


def test_widget_returns_seven_days() -> None:
    payload = CLIENT.post("/api/widget", json={"route": marts.ROUTES[1]}).json()
    assert len(payload["days"]) == 7 and payload["route"] == marts.ROUTES[1]
