"""Тесты правил стиля: AST-чекер проходит по всему коду и сам ловит нарушения."""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

import check_style

ROOT = Path(__file__).resolve().parents[2]
PY_FILES = sorted(
    path
    for directory in ("services", "tools")
    for path in (ROOT / directory).rglob("*.py")
    if not check_style.SKIP_PARTS & set(path.parts)
)
FILE_IDS = [str(path.relative_to(ROOT)) for path in PY_FILES]

FILES = pytest.mark.parametrize("path", PY_FILES, ids=FILE_IDS)

TWO_RETURNS = """
def risky(x):
    if x > 0:
        return 1
    return 0
"""

THREE_STATEMENTS = """
def long_body(x):
    a = x + 1
    b = a + 1
    return b
"""

WHILE_LOOP = """
def spin(x):
    while x > 0:
        x -= 1
    return x
"""

BREAK_STATEMENT = """
def scan(items):
    for item in items:
        if item:
            break
    return items
"""

ARGUMENT_MUTATION = """
def append_all(target, value):
    target.append(value)
    return target
"""

CLEAN_CODE = """
def add(x, y):
    return x + y
"""


def issues_of(code: str) -> list[tuple[int, str]]:
    tree = ast.parse(textwrap.dedent(code))
    return [check_style.function_all_issues(func)[0] for func in check_style.functions_of(tree) if check_style.function_all_issues(func)]


@FILES
def test_file_passes_style_check(path: Path) -> None:
    assert check_style.file_issues(path) == []


def test_two_returns_detected() -> None:
    assert issues_of(TWO_RETURNS)[0][1].startswith("ST001")


def test_three_statements_detected() -> None:
    assert issues_of(THREE_STATEMENTS)[0][1].startswith("ST002")


def test_while_detected() -> None:
    assert any(message.startswith("ST003") for _, message in issues_of(WHILE_LOOP))


def test_break_detected() -> None:
    assert any(message.startswith("ST004") for _, message in issues_of(BREAK_STATEMENT))


def test_argument_mutation_detected() -> None:
    assert any(message.startswith("ST006") for _, message in issues_of(ARGUMENT_MUTATION))


def test_clean_function_has_no_issues() -> None:
    assert issues_of(CLEAN_CODE) == []


def test_repository_is_clean() -> None:
    assert check_style.main() == 0
