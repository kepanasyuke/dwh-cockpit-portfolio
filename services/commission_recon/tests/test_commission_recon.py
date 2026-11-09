"""Тесты сверки комиссий: баланс сторон, статусы и полнота реестра."""

from __future__ import annotations

from fastapi.testclient import TestClient

from commission_recon import marts
from commission_recon.app import app

CLIENT = TestClient(app)


def test_health() -> None:
    assert CLIENT.get("/health").json()["status"] == "ok"


def test_reconciliation_covers_all_partners() -> None:
    assert len(marts.partners(marts.connect())) == len(marts.PARTNERS)


def test_diff_matches_accrued_minus_billed() -> None:
    db = marts.connect()
    assert all(abs(row["accrued"] - row["billed"] - row["diff"]) < 0.01 for row in marts.partners(db))


def test_auto_match_between_bounds() -> None:
    assert 0 <= marts.summary(marts.connect())["auto_match"] <= 100


def test_widget_returns_cases() -> None:
    assert CLIENT.post("/api/widget", json={"partner": marts.PARTNERS[0]}).json()["cases"]
