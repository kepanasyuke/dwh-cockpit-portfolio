"""Тесты покрытия сети: целостность хаба, линков и gap-анализ."""

from __future__ import annotations

from fastapi.testclient import TestClient

from _shared import seeding
from partner_coverage import marts
from partner_coverage.app import app

CLIENT = TestClient(app)


def test_health() -> None:
    assert CLIENT.get("/health").json()["status"] == "ok"


def test_hub_has_no_duplicates() -> None:
    assert marts.summary(marts.connect())["duplicates"] == 0


def test_every_hotel_has_supplier() -> None:
    db = marts.connect()
    assert marts.warehouse.scalar(db, "select count(*) from hub_hotel where hub_key not in (select hub_key from link_hotel_supplier)") == 0


def test_coverage_cities_match_demand() -> None:
    assert len(marts.cities(marts.connect())) == len(seeding.CITIES)


def test_widget_unknown_city_is_empty() -> None:
    assert CLIENT.post("/api/widget", json={"city": "Атлантида"}).json()["deficit"]["coverage"] == 0
