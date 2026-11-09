"""HTTP-слой кокпита: продуктовые эндпоинты поверх восьми сервисов."""

from __future__ import annotations

from fastapi import FastAPI

from _shared import api

from . import service

DEFAULT_QUESTION = "сколько мы заработали за неделю"


def overview_handler(period: int = 7, city: str = "") -> dict:
    return service.overview(period, city or None)


def ask_handler(q: str = "") -> dict:
    return service.ask(q or DEFAULT_QUESTION)


def routes_of() -> list[tuple]:
    return [
        ("/health", api.health_handler(service.META), "GET"),
        ("/api/dashboard", service.dashboard, "GET"),
        ("/api/overview", overview_handler, "GET"),
        ("/api/money", service.money, "GET"),
        ("/api/trust", service.trust, "GET"),
        ("/api/pricing", service.pricing, "GET"),
        ("/api/risks", service.risks, "GET"),
        ("/api/ask", ask_handler, "GET"),
        ("/api/widget", api.widget_handler(service.widget), "POST"),
    ]


app: FastAPI = api.routes(api.cors(FastAPI(title=service.META["title"], version="1.0.0")), routes_of())
