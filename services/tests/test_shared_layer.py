"""Тесты общего слоя: мини-хранилище, конверт ответа и генераторы данных."""

from __future__ import annotations

from _shared import envelope, seeding, warehouse

SCHEMA = "create table t (a integer, b text);"
ROWS = [(1, "x"), (2, "y")]
META = {"slug": "demo", "title": "Демо", "subtitle": "Подзаголовок", "updated_at": "2026-11-08", "engine": "SQLite"}


def test_build_creates_rows() -> None:
    assert warehouse.rows_of(warehouse.build(SCHEMA, {"t": ROWS}), "t") == 2


def test_build_without_data() -> None:
    assert warehouse.rows_of(warehouse.build(SCHEMA, {}), "t") == 0


def test_query_returns_dicts() -> None:
    assert warehouse.query(warehouse.build(SCHEMA, {"t": ROWS}), "select a, b from t order by a")[0] == {"a": 1, "b": "x"}


def test_query_with_parameters() -> None:
    db = warehouse.build(SCHEMA, {"t": ROWS})
    assert warehouse.query(db, "select b from t where a = ?", (2,)) == [{"b": "y"}]


def test_scalar_empty_returns_zero() -> None:
    assert warehouse.scalar(warehouse.build(SCHEMA, {}), "select sum(a) from t") == 0.0


def test_scalar_counts_rows() -> None:
    assert warehouse.scalar(warehouse.build(SCHEMA, {"t": ROWS}), "select count(*) from t") == 2


def test_placeholders_length() -> None:
    assert warehouse.placeholders((1, "x", None)) == "?,?,?"


def test_insert_adds_rows() -> None:
    db = warehouse.build(SCHEMA, {"t": [(1, "x")]})
    assert warehouse.rows_of(warehouse.insert(db, "t", [(2, "y")]), "t") == 2


def test_load_skips_empty_tables() -> None:
    assert warehouse.rows_of(warehouse.build(SCHEMA, {}), "t") == 0


def test_names_returns_columns() -> None:
    db = warehouse.build(SCHEMA, {"t": ROWS})
    assert warehouse.names(db.execute("select a, b from t")) == ["a", "b"]


def test_script_returns_connection() -> None:
    assert warehouse.script(warehouse.connect(), SCHEMA) is not None


def test_kpi_rounds_value() -> None:
    assert envelope.kpi("k", "K", 1.23456, "rub")["value"] == 1.23


def test_kpi_delta_defaults_to_none() -> None:
    assert envelope.kpi("k", "K", 1, "count")["delta"] is None


def test_column_defaults() -> None:
    column = envelope.column("c", "C")
    assert column["align"] == "left" and column["format"] is None


def test_column_with_format() -> None:
    assert envelope.column("c", "C", "right", "rub") == {"key": "c", "title": "C", "align": "right", "format": "rub"}


def test_chart_points_rounded() -> None:
    assert envelope.chart("k", "K", "rub", [("a", 1.239)])["points"][0]["value"] == 1.24


def test_chart_default_type() -> None:
    assert envelope.chart("k", "K", "count", [("a", 1)])["type"] == "bars"


def test_chart_labels_are_strings() -> None:
    assert envelope.chart("k", "K", "count", [(5, 1)])["points"][0]["label"] == "5"


def test_table_structure() -> None:
    grid = envelope.table([envelope.column("c", "C")], [{"c": 1}])
    assert grid == {"columns": [{"key": "c", "title": "C", "align": "left", "format": None}], "rows": [{"c": 1}]}


def test_pipeline_maps_fields() -> None:
    assert envelope.pipeline([("m", "mart", 10, "06:00")]) == [{"model": "m", "layer": "mart", "rows": 10, "sla": "06:00"}]


def test_dashboard_keys() -> None:
    payload = envelope.dashboard(META, [], [], envelope.table([], []), [], [])
    assert payload["project"] == "demo" and payload["updatedAt"] == "2026-11-08"


def test_dashboard_extra_defaults_to_empty() -> None:
    assert envelope.dashboard(META, [], [], envelope.table([], []), [], [])["extra"] == {}


def test_seed_is_deterministic() -> None:
    assert seeding.seed_of("route") == seeding.seed_of("route")


def test_seed_differs_for_different_text() -> None:
    assert seeding.seed_of("route-a") != seeding.seed_of("route-b")


def test_noise_in_unit_interval() -> None:
    assert all(0 <= seeding.noise(seeding.seed_of(str(index))) <= 1 for index in range(50))


def test_series_length() -> None:
    assert len(seeding.series(42, 7)) == 7


def test_series_is_deterministic() -> None:
    assert seeding.series(42, 5) == seeding.series(42, 5)


def test_between_respects_bounds() -> None:
    assert all(10 <= seeding.between(seeding.noise(index), 10, 20) <= 20 for index in range(30))


def test_whole_respects_bounds() -> None:
    assert all(3 <= seeding.whole(seeding.noise(index), 3, 8) <= 8 for index in range(30))


def test_pick_returns_member() -> None:
    assert seeding.pick(["a", "b", "c"], 0.99) in {"a", "b", "c"}


def test_hotel_names_unique_within_city() -> None:
    names = [seeding.hotel_name(index, "Сочи") for index in range(32)]
    assert len(names) == len(set(names))


def test_hotel_name_contains_city() -> None:
    assert seeding.hotel_name(0, "Сочи").endswith("Сочи")


def test_day_format() -> None:
    assert seeding.day(0) == "2026-11-01" and seeding.day(27) == "2026-11-28"


def test_cities_have_coordinates() -> None:
    assert all(len(city) == 4 and -90 <= city[2] <= 90 for city in seeding.CITIES)
