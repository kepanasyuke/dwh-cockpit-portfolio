"""Тонкая обёртка над SQLite: хранилище живёт в памяти, схема и данные создаются при старте."""

from __future__ import annotations

import sqlite3

Row = tuple[object, ...]


def connect() -> sqlite3.Connection:
    return sqlite3.connect(":memory:", check_same_thread=False)


def script(conn: sqlite3.Connection, sql: str) -> sqlite3.Connection:
    conn.executescript(sql)
    return conn


def placeholders(row: Row) -> str:
    return ",".join("?" * len(row))


def insert(conn: sqlite3.Connection, table: str, rows: list[Row]) -> sqlite3.Connection:
    conn.executemany(f"insert into {table} values ({placeholders(rows[0])})", rows)
    return conn


def load(conn: sqlite3.Connection, tables: dict[str, list[Row]]) -> sqlite3.Connection:
    [insert(conn, name, rows) for name, rows in tables.items() if rows]
    return conn


def build(schema: str, tables: dict[str, list[Row]]) -> sqlite3.Connection:
    return load(script(connect(), schema), tables)


def query(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    cursor = conn.execute(sql, params)
    return [dict(zip(names(cursor), row)) for row in cursor.fetchall()]


def names(cursor: sqlite3.Cursor) -> list[str]:
    return [column[0] for column in cursor.description]


def scalar(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> float:
    return conn.execute(sql, params).fetchone()[0] or 0.0


def rows_of(conn: sqlite3.Connection, table: str) -> int:
    return int(scalar(conn, f"select count(*) from {table}"))
