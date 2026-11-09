"""Статический чекер стиля: один выход из функции, 1-2 оператора, без while/break/continue.

Работает по AST, поэтому не зависит от версии Ruff/Flake8 и проверяет ровно те правила,
которые приняты в проекте:

  ST001  у функции больше одного return (один выход)
  ST002  в теле функции больше двух операторов
  ST003  используется while
  ST004  используется break или continue
  ST005  у функции больше одного блока try
  ST006  мутация аргумента через append/extend/update/sort/pop/remove/insert
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET_DIRS = ("services", "tools")
SKIP_PARTS = {"__pycache__", ".pytest_cache", "node_modules", ".next"}
DEF_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)
MUTATORS = {"append", "extend", "update", "sort", "pop", "remove", "insert"}
MAX_RETURNS = 1
MAX_STATEMENTS = 2
MAX_TRIES = 1
OK_MESSAGE = "Стиль в порядке: один выход, ≤2 оператора, без while/break/continue."


def subtree(node: ast.AST) -> list[ast.AST]:
    return [] if is_def(node) else [node, *flatten(ast.iter_child_nodes(node))]


def flatten(nodes: object) -> list[ast.AST]:
    return [found for child in nodes for found in subtree(child)]


def own_nodes(func: ast.AST) -> list[ast.AST]:
    return [func, *flatten(ast.iter_child_nodes(func))]


def nodes_of(func: ast.AST, types: tuple[type, ...]) -> list[ast.AST]:
    return [node for node in own_nodes(func) if isinstance(node, types)]


def is_def(node: ast.AST) -> bool:
    return isinstance(node, DEF_TYPES)


def exceeded(value: int, limit: int, message: str, node: ast.AST) -> list[tuple[int, str]]:
    return [(node.lineno, message)] if limit < value else []


def arg_names(func: ast.AST) -> set[str]:
    return {a.arg for a in func.args.args + func.args.kwonlyargs}


def mutations(func: ast.AST) -> list[ast.Call]:
    return [n for n in own_nodes(func) if is_mutation(n, arg_names(func))]


def is_mutation(node: ast.AST, args: set[str]) -> bool:
    return isinstance(node, ast.Call) and is_mutating_call(node, args)


def is_mutating_call(node: ast.Call, args: set[str]) -> bool:
    return isinstance(node.func, ast.Attribute) and has_mutating_call(node.func, args)


def has_mutating_call(func: ast.Attribute, args: set[str]) -> bool:
    return func.attr in MUTATORS and isinstance(func.value, ast.Name) and func.value.id in args


def function_issues(func: ast.AST) -> list[tuple[int, str]]:
    return (
        exceeded(len(func.body), MAX_STATEMENTS, "ST002 в теле функции больше двух операторов", func)
        + exceeded(len(nodes_of(func, (ast.Return,))), MAX_RETURNS, "ST001 у функции больше одного return", func)
        + exceeded(len(nodes_of(func, (ast.Try,))), MAX_TRIES, "ST005 у функции больше одного блока try", func)
        + [(n.lineno, "ST006 мутация аргумента функции") for n in mutations(func)]
    )


def loop_issues(func: ast.AST) -> list[tuple[int, str]]:
    return [(n.lineno, "ST003 while запрещён") for n in nodes_of(func, (ast.While,))] + [
        (n.lineno, "ST004 break/continue запрещены") for n in nodes_of(func, (ast.Break, ast.Continue))
    ]


def function_all_issues(func: ast.AST) -> list[tuple[int, str]]:
    return function_issues(func) + loop_issues(func)


def functions_of(tree: ast.AST) -> list[ast.AST]:
    return [node for node in ast.walk(tree) if is_def(node)]


def parse_file(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def file_issues(path: Path) -> list[tuple[int, str]]:
    return [issue for func in functions_of(parse_file(path)) for issue in function_all_issues(func)]


def python_files(root: Path) -> list[Path]:
    return sorted(p for d in TARGET_DIRS for p in (root / d).rglob("*.py") if not SKIP_PARTS & set(p.parts))


def collect(root: Path, files: list[Path]) -> list[tuple[Path, int, str]]:
    return [(path, line, message) for path in files for line, message in file_issues(path)]


def render(root: Path, issues: list[tuple[Path, int, str]]) -> str:
    return "\n".join(f"{path.relative_to(root)}:{line}  {message}" for path, line, message in issues) or OK_MESSAGE


def fail(root: Path, issues: list[tuple[Path, int, str]]) -> int:
    print(render(root, issues))
    return 1


def report(root: Path, issues: list[tuple[Path, int, str]]) -> int:
    return 0 if not issues else fail(root, issues)


def main() -> int:
    return report(ROOT, collect(ROOT, python_files(ROOT)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
