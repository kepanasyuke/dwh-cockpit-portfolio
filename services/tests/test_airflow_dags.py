"""Тесты DAG Airflow: идентификатор, расписание, теги, ретраи и набор задач."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DAG_FILES = sorted((ROOT / "services").glob("*/dags/*.py"))
DAG_IDS = [str(path.relative_to(ROOT)) for path in DAG_FILES]

DAGS = pytest.mark.parametrize("path", DAG_FILES, ids=DAG_IDS)


def tree_of(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def dag_call(path: Path) -> ast.Call:
    return next(node for node in ast.walk(tree_of(path)) if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "DAG")


def keyword(call: ast.Call, name: str) -> ast.AST | None:
    found = [item.value for item in call.keywords if item.arg == name]
    return found[0] if found else None


def keyword_text(call: ast.Call, name: str) -> str:
    return ast.literal_eval(keyword(call, name)) if keyword(call, name) is not None else ""


def task_count(path: Path) -> int:
    calls = [node for node in ast.walk(tree_of(path)) if isinstance(node, ast.Call)]
    return len([node for node in calls if getattr(node.func, "id", "").endswith("Operator")])


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@DAGS
def test_dag_file_imports_airflow(path: Path) -> None:
    assert "from airflow import DAG" in source(path)


@DAGS
def test_dag_id_matches_file(path: Path) -> None:
    assert keyword_text(dag_call(path), "dag_id") == path.stem


@DAGS
def test_dag_has_schedule(path: Path) -> None:
    call = dag_call(path)
    assert keyword(call, "schedule") is not None or keyword(call, "schedule_interval") is not None


@DAGS
def test_dag_has_description(path: Path) -> None:
    assert keyword_text(dag_call(path), "description")


@DAGS
def test_dag_has_tags(path: Path) -> None:
    assert len(keyword(dag_call(path), "tags").elts) >= 2


@DAGS
def test_dag_disables_catchup(path: Path) -> None:
    assert "catchup=False" in source(path)


@DAGS
def test_dag_has_three_or_more_tasks(path: Path) -> None:
    assert task_count(path) >= 3


@DAGS
def test_dag_has_retries(path: Path) -> None:
    assert "retries" in source(path)


@DAGS
def test_dag_has_start_date(path: Path) -> None:
    assert keyword(dag_call(path), "start_date") is not None
