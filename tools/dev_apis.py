"""Запуск всех девяти сервисов одной командой: python tools/dev_apis.py."""

from __future__ import annotations

import importlib
import sys
import threading
from pathlib import Path

import uvicorn
from fastapi import FastAPI

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "services"))

SERVICES = [
    ("bookings_marts", 8101),
    ("cancel_radar", 8102),
    ("price_elasticity", 8103),
    ("demand_forecast", 8104),
    ("data_quality", 8105),
    ("partner_coverage", 8106),
    ("commission_recon", 8107),
    ("nl_sql_copilot", 8108),
    ("cockpit_bff", 8109),
]


def load(module: str) -> FastAPI:
    return importlib.import_module(f"{module}.app").app


def config_of(module: str, port: int) -> uvicorn.Config:
    return uvicorn.Config(load(module), host="127.0.0.1", port=port, log_level="warning")


def server_of(module: str, port: int) -> uvicorn.Server:
    return uvicorn.Server(config_of(module, port))


def launch(servers: list[uvicorn.Server]) -> None:
    [threading.Thread(target=server.run, daemon=True).start() for server in servers]
    print("Поднято 9 сервисов: 8101–8109 · Swagger: http://127.0.0.1:8101/docs")


def wait_forever() -> int:
    threading.Event().wait()
    return 0


def run_all(servers: list[uvicorn.Server]) -> int:
    launch(servers)
    return wait_forever()


def main() -> int:
    return run_all([server_of(module, port) for module, port in SERVICES])


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nСервисы остановлены")
        sys.exit(0)
