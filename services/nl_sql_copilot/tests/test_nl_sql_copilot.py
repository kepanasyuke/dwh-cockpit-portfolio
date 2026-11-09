"""Тесты копайлота: маршрутизация вопроса, безопасный SQL и ответ по данным."""

from __future__ import annotations

from fastapi.testclient import TestClient

from nl_sql_copilot import marts
from nl_sql_copilot.app import app

CLIENT = TestClient(app)


def test_health() -> None:
    assert CLIENT.get("/health").json()["status"] == "ok"


def test_router_picks_gmv_for_revenue_question() -> None:
    assert marts.best_metric("сколько мы заработали за неделю")["key"] == "gmv"


def test_router_picks_cancels_metric() -> None:
    assert marts.best_metric("доля отмен по городам")["key"] == "cancels"


def test_city_filter_is_parameterised() -> None:
    sql, params = marts.build_query(marts.plan("выручка по Сочи"))
    assert "?" in sql and params == ("Сочи",)


def test_answer_uses_real_rows() -> None:
    result = marts.ask(marts.connect(), "какая выручка по каналам")
    assert result["rows"] and result["metric"] == "GMV"
