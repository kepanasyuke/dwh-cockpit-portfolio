"""Контракт API всех девяти сервисов: одинаковый набор гарантий проверен на каждом."""

from __future__ import annotations

import pytest

from _shared import testing

CASES = pytest.mark.parametrize("module", testing.MODULES)


@CASES
def test_health_returns_ok(module: str) -> None:
    assert testing.health_of(module)["status"] == "ok"


@CASES
def test_health_reports_engine(module: str) -> None:
    assert testing.health_of(module)["engine"]


@CASES
def test_health_reports_project(module: str) -> None:
    assert testing.health_of(module)["project"]


@CASES
def test_dashboard_status_200(module: str) -> None:
    assert testing.client(module).get("/api/dashboard").status_code == 200


@CASES
def test_dashboard_has_envelope_keys(module: str) -> None:
    payload = testing.dashboard_of(module)
    assert {"project", "title", "subtitle", "updatedAt", "engine", "kpis", "charts", "table", "pipeline", "notes"} <= set(payload)


@CASES
def test_dashboard_project_matches_slug(module: str) -> None:
    payload = testing.dashboard_of(module)
    assert payload["project"] == testing.marts_of(module).META["slug"]


@CASES
def test_dashboard_title_not_empty(module: str) -> None:
    assert testing.dashboard_of(module)["title"].strip()


@CASES
def test_kpis_count_at_least_four(module: str) -> None:
    assert len(testing.dashboard_of(module)["kpis"]) >= 4


@CASES
def test_kpi_fields_complete(module: str) -> None:
    assert all({"key", "label", "value", "unit"} <= set(kpi) for kpi in testing.dashboard_of(module)["kpis"])


@CASES
def test_kpi_units_allowed(module: str) -> None:
    assert {kpi["unit"] for kpi in testing.dashboard_of(module)["kpis"]} <= testing.UNITS


@CASES
def test_kpi_values_are_numbers(module: str) -> None:
    assert all(isinstance(kpi["value"], (int, float)) for kpi in testing.dashboard_of(module)["kpis"])


@CASES
def test_kpi_keys_unique(module: str) -> None:
    keys = [kpi["key"] for kpi in testing.dashboard_of(module)["kpis"]]
    assert len(keys) == len(set(keys))


@CASES
def test_charts_present(module: str) -> None:
    assert testing.dashboard_of(module)["charts"]


@CASES
def test_chart_points_not_empty(module: str) -> None:
    assert all(chart["points"] for chart in testing.dashboard_of(module)["charts"])


@CASES
def test_chart_units_allowed(module: str) -> None:
    assert {chart["unit"] for chart in testing.dashboard_of(module)["charts"]} <= testing.UNITS


@CASES
def test_chart_labels_unique(module: str) -> None:
    labels = [point["label"] for chart in testing.dashboard_of(module)["charts"] for point in chart["points"]]
    assert len(labels) == len(set(labels))


@CASES
def test_table_columns_present(module: str) -> None:
    assert testing.dashboard_of(module)["table"]["columns"]


@CASES
def test_table_rows_not_empty(module: str) -> None:
    assert testing.dashboard_of(module)["table"]["rows"]


@CASES
def test_table_row_keys_match_columns(module: str) -> None:
    table = testing.dashboard_of(module)["table"]
    assert all(set(row) == {column["key"] for column in table["columns"]} for row in table["rows"])


@CASES
def test_table_columns_have_titles(module: str) -> None:
    assert all(column["title"] for column in testing.dashboard_of(module)["table"]["columns"])


@CASES
def test_pipeline_layers_allowed(module: str) -> None:
    assert {node["layer"] for node in testing.dashboard_of(module)["pipeline"]} <= testing.LAYERS


@CASES
def test_pipeline_has_mart(module: str) -> None:
    assert "mart" in {node["layer"] for node in testing.dashboard_of(module)["pipeline"]}


@CASES
def test_pipeline_rows_positive(module: str) -> None:
    assert all(node["rows"] >= 0 for node in testing.dashboard_of(module)["pipeline"])


@CASES
def test_notes_present(module: str) -> None:
    assert len(testing.dashboard_of(module)["notes"]) >= 2


@CASES
def test_widget_returns_object(module: str) -> None:
    assert isinstance(testing.widget_of(module), dict)


@CASES
def test_widget_is_deterministic(module: str) -> None:
    assert testing.widget_of(module) == testing.widget_of(module)


@CASES
def test_dashboard_is_deterministic(module: str) -> None:
    assert testing.dashboard_of(module) == testing.dashboard_of(module)


@CASES
def test_unknown_path_returns_404(module: str) -> None:
    assert testing.client(module).get("/api/unknown").status_code == 404


@CASES
def test_cors_header_for_browser(module: str) -> None:
    response = testing.client(module).get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.headers.get("access-control-allow-origin") == "*"


@CASES
def test_openapi_documented(module: str) -> None:
    assert "/api/dashboard" in testing.client(module).get("/openapi.json").json()["paths"]
