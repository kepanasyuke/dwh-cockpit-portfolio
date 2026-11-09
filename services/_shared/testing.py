"""Поддержка тестов: единый доступ к девяти сервисам и их ответам."""

from __future__ import annotations

import importlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

SERVICES_DIR = Path(__file__).resolve().parent.parent

MODULES = [
    "bookings_marts",
    "cancel_radar",
    "price_elasticity",
    "demand_forecast",
    "data_quality",
    "partner_coverage",
    "commission_recon",
    "nl_sql_copilot",
    "cockpit_bff",
]

PORTS = {
    "bookings_marts": 8101,
    "cancel_radar": 8102,
    "price_elasticity": 8103,
    "demand_forecast": 8104,
    "data_quality": 8105,
    "partner_coverage": 8106,
    "commission_recon": 8107,
    "nl_sql_copilot": 8108,
    "cockpit_bff": 8109,
}

UNITS = {"rub", "pct", "count", "score", "hours", "ratio"}
LAYERS = {"staging", "intermediate", "mart"}
STATUSES = {"ok", "warn", "fail"}

CACHE: dict[str, TestClient] = {}


def load(module: str) -> FastAPI:
    return importlib.import_module(f"{module}.app").app


def client(module: str) -> TestClient:
    return CACHE.setdefault(module, TestClient(load(module)))


def health_of(module: str) -> dict:
    return client(module).get("/health").json()


def dashboard_of(module: str) -> dict:
    return client(module).get("/api/dashboard").json()


def widget_of(module: str, payload: dict | None = None) -> dict:
    return client(module).post("/api/widget", json=payload or {}).json()


def marts_of(module: str) -> object:
    return importlib.import_module(f"{module}.{suffix_of(module)}")


def suffix_of(module: str) -> str:
    return "marts" if (SERVICES_DIR / module / "marts.py").exists() else "service"
