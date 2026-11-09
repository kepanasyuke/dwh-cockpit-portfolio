"""Тесты качества данных: SLO в допустимых границах, статусы и DQ-контракт."""

from __future__ import annotations

from fastapi.testclient import TestClient

from data_quality import marts
from data_quality.app import app

CLIENT = TestClient(app)


def test_health() -> None:
    assert CLIENT.get("/health").json()["status"] == "ok"


def test_slo_is_percentage() -> None:
    assert 0 <= marts.summary(marts.connect())["slo"] <= 100


def test_statuses_are_known() -> None:
    assert {row["status"] for row in marts.models(marts.connect())} <= {"ok", "warn", "fail"}


def test_checks_present_in_dashboard_extra() -> None:
    assert CLIENT.get("/api/dashboard").json()["extra"]["checks"]


def test_widget_returns_checks() -> None:
    payload = CLIENT.post("/api/widget", json={}).json()
    assert payload["checks"] and "slo" in payload
