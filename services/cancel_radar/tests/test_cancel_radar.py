"""Тесты радара отмен: границы скора, качество модели и пороги действий."""

from __future__ import annotations

from fastapi.testclient import TestClient

from cancel_radar import marts
from cancel_radar.app import app

CLIENT = TestClient(app)


def test_health() -> None:
    assert CLIENT.get("/health").json()["status"] == "ok"


def test_risk_within_bounds() -> None:
    db = marts.connect()
    assert all(0.0 <= row["risk"] <= 1.0 for row in marts.warehouse.query(db, "select risk from mart_cancel_risk"))


def test_model_learns_signal() -> None:
    db = marts.connect()
    assert marts.auc(marts.warehouse.query(db, "select risk, cancelled from mart_cancel_risk")) > 0.55


def test_action_thresholds() -> None:
    assert marts.action_of(0.7) == "предоплата 30%" and marts.action_of(0.1) == "без предоплаты"


def test_widget_returns_loss() -> None:
    payload = CLIENT.post("/api/widget", json={"lead_time_days": 90, "amount": 100000, "channel": "web"}).json()
    assert 0 <= payload["risk"] <= 1 and payload["expected_loss"] <= 100000
