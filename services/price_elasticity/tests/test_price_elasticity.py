"""Тесты эластичности: знак коэффициента, качество регрессии и симметрия симулятора."""

from __future__ import annotations

from fastapi.testclient import TestClient

from price_elasticity import marts
from price_elasticity.app import app

CLIENT = TestClient(app)


def test_health() -> None:
    assert CLIENT.get("/health").json()["status"] == "ok"


def test_elasticity_is_negative() -> None:
    assert all(row["elasticity"] < 0 for row in marts.route_rows(marts.connect()))


def test_regression_quality() -> None:
    assert marts.summary(marts.connect())["confidence"] > 0.3


def test_simulator_neutral_delta() -> None:
    result = marts.simulate(10000, 0.0, -1.4)
    assert result["revenue_factor"] == 1.0 and result["new_price"] == 10000


def test_verdict_direction() -> None:
    assert marts.verdict_of(1.05) == "поднять цену" and marts.verdict_of(0.95) == "снизить цену"


def test_widget_response() -> None:
    assert CLIENT.post("/api/widget", json={"price": 12000, "delta_pct": 10, "elasticity": -1.2}).json()["new_price"] == 13200
