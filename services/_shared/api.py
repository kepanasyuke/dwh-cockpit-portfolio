"""Фабрика FastAPI-приложения: маршруты /health, /api/dashboard, /api/widget и CORS для фронтенда."""

from __future__ import annotations

from typing import Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def cors(app: FastAPI) -> FastAPI:
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    return app


def health_handler(meta: dict) -> Callable[[], dict]:
    def health() -> dict:
        return {"status": "ok", "project": meta["slug"], "engine": meta["engine"]}

    return health


def passthrough(fn: Callable[[], dict]) -> Callable[[], dict]:
    def run() -> dict:
        return fn()

    return run


def widget_handler(widget_fn: Callable[[dict], dict]) -> Callable[..., dict]:
    def run(payload: dict | None = None) -> dict:
        return widget_fn(payload or {})

    return run


def specs(meta: dict, dashboard_fn: Callable[[], dict], widget_fn: Callable[[dict], dict]) -> list[tuple]:
    return [
        ("/health", health_handler(meta), "GET"),
        ("/api/dashboard", passthrough(dashboard_fn), "GET"),
        ("/api/widget", widget_handler(widget_fn), "POST"),
    ]


def routes(app: FastAPI, route_specs: list[tuple]) -> FastAPI:
    [app.add_api_route(path, handler, methods=[method]) for path, handler, method in route_specs]
    return app


def make_app(meta: dict, dashboard_fn: Callable[[], dict], widget_fn: Callable[[dict], dict]) -> FastAPI:
    return routes(cors(FastAPI(title=meta["title"], version="1.0.0")), specs(meta, dashboard_fn, widget_fn))
