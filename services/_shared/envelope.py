"""Конверт ответа API. Один контракт для всех сервисов — фронтенд рендерит его одним компонентом."""

from __future__ import annotations

from typing import Any


def kpi(key: str, label: str, value: float, unit: str, delta: float | None = None) -> dict:
    return {"key": key, "label": label, "value": round(float(value), 2), "unit": unit, "delta": delta}


def column(key: str, title: str, align: str = "left", fmt: str | None = None) -> dict:
    return {"key": key, "title": title, "align": align, "format": fmt}


def table(columns: list[dict], rows: list[dict]) -> dict:
    return {"columns": columns, "rows": rows}


def chart(key: str, label: str, unit: str, points: list[tuple[str, float]], kind: str = "bars") -> dict:
    return {
        "key": key,
        "label": label,
        "type": kind,
        "unit": unit,
        "points": [{"label": str(name), "value": round(float(value), 2)} for name, value in points],
    }


def pipeline(items: list[tuple[str, str, int, str]]) -> list[dict]:
    return [{"model": model, "layer": layer, "rows": rows, "sla": sla} for model, layer, rows, sla in items]


def dashboard(
    meta: dict,
    kpis: list[dict],
    charts: list[dict],
    grid: dict,
    lineage: list[dict],
    notes: list[str],
    extra: dict[str, Any] | None = None,
) -> dict:
    return {
        "project": meta["slug"],
        "title": meta["title"],
        "subtitle": meta["subtitle"],
        "updatedAt": meta["updated_at"],
        "engine": meta["engine"],
        "kpis": kpis,
        "charts": charts,
        "table": grid,
        "pipeline": lineage,
        "notes": notes,
        "extra": extra or {},
    }
