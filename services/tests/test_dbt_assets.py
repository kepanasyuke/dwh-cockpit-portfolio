"""Тесты dbt-слоя: структура проектов, SQL-модели и документация в schema.yml."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
DBT_DIRS = sorted((ROOT / "services").glob("*/dbt"))
SERVICE_NAMES = [directory.parent.name for directory in DBT_DIRS]
MODEL_FILES = sorted(path for directory in DBT_DIRS for path in (directory / "models").rglob("*.sql"))
MODEL_IDS = [str(path.relative_to(ROOT)) for path in MODEL_FILES]

MODELS = pytest.mark.parametrize("path", MODEL_FILES, ids=MODEL_IDS)
SERVICES = pytest.mark.parametrize("service", SERVICE_NAMES)


def text_of(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


def dbt_dir(service: str) -> Path:
    return ROOT / "services" / service / "dbt"


def mart_models(service: str) -> list[Path]:
    return sorted((dbt_dir(service) / "models" / "marts").glob("*.sql"))


def documented_models(service: str) -> set[str]:
    data = yaml.safe_load((dbt_dir(service) / "models" / "marts" / "schema.yml").read_text(encoding="utf-8"))
    return {model["name"] for model in data.get("models", [])}


@MODELS
def test_model_has_select(path: Path) -> None:
    assert "select" in text_of(path)


@MODELS
def test_model_uses_dbt_references(path: Path) -> None:
    assert "ref(" in text_of(path) or "source(" in text_of(path)


@MODELS
def test_model_has_balanced_parentheses(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.count("(") == text.count(")")


@MODELS
def test_mart_models_are_configured(path: Path) -> None:
    assert path.parent.name != "marts" or "config(" in text_of(path)


@SERVICES
def test_dbt_project_is_named(service: str) -> None:
    data = yaml.safe_load((dbt_dir(service) / "dbt_project.yml").read_text(encoding="utf-8"))
    assert data["name"] == service


@SERVICES
def test_dbt_project_declares_profile(service: str) -> None:
    data = yaml.safe_load((dbt_dir(service) / "dbt_project.yml").read_text(encoding="utf-8"))
    assert data["profile"] == "ostrovok_dwh"


@SERVICES
def test_marts_are_documented(service: str) -> None:
    assert {path.stem for path in mart_models(service)} <= documented_models(service)


@SERVICES
def test_schema_declares_tests(service: str) -> None:
    text = (dbt_dir(service) / "models" / "marts" / "schema.yml").read_text(encoding="utf-8")
    assert "tests:" in text


@SERVICES
def test_schema_declares_sources(service: str) -> None:
    text = (dbt_dir(service) / "models" / "marts" / "schema.yml").read_text(encoding="utf-8")
    assert "sources:" in text
