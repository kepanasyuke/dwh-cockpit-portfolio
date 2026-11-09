"""Снимки интерфейса для README: python tools/screenshots.py."""

from __future__ import annotations

import importlib
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import suppress
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "apps" / "web"
COCKPIT_DIR = ROOT / "apps" / "cockpit"
OUT_DIR = ROOT / "docs" / "screenshots"
PROFILE = Path(tempfile.gettempdir()) / "dwh-shots-profile"

sys.path.insert(0, str(ROOT / "tools"))

CHROME_CANDIDATES = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
]
NODE_CANDIDATES = ["C:/Program Files/nodejs/node.exe", "C:/Program Files (x86)/nodejs/node.exe"]
NEXT_CANDIDATES = [
    str(ROOT / "node_modules" / "next" / "dist" / "bin" / "next"),
    str(WEB_DIR / "node_modules" / "next" / "dist" / "bin" / "next"),
]

PAGES = [
    ("01-landing.png", 3000, "/", "1440,2600"),
    ("02-bookings-marts.png", 3000, "/projects/bookings-marts", "1440,2100"),
    ("03-cancel-radar.png", 3000, "/projects/cancel-radar", "1440,2300"),
    ("04-data-quality.png", 3000, "/projects/data-quality", "1440,2300"),
    ("05-nl-sql-copilot.png", 3000, "/projects/nl-sql-copilot", "1440,2100"),
    ("10-cockpit-overview.png", 3100, "/", "1440,2500"),
    ("11-cockpit-directions.png", 3100, "/directions", "1440,1800"),
    ("12-cockpit-risk.png", 3100, "/risk", "1440,1900"),
    ("13-cockpit-trust.png", 3100, "/trust", "1440,1900"),
    ("14-cockpit-money.png", 3100, "/money", "1440,1800"),
    ("15-cockpit-ask.png", 3100, "/ask", "1440,1400"),
]

FLAGS = [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--no-first-run",
    "--disable-extensions",
    "--virtual-time-budget=10000",
]

OUT_DIR.mkdir(parents=True, exist_ok=True)


def first_existing(candidates: list[str]) -> str:
    return next(path for path in candidates if Path(path).exists())


def reachable(port: int) -> bool:
    with socket.socket() as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0


def poll(port: int, deadline: float) -> bool:
    return reachable(port) or (time.time() < deadline and pause(port, deadline))


def pause(port: int, deadline: float) -> bool:
    time.sleep(1)
    return poll(port, deadline)


def wait_for(port: int, timeout: float = 120.0) -> bool:
    return poll(port, time.time() + timeout)


def args_of(name: str, port: int, path: str, size: str) -> list[str]:
    return [
        first_existing(CHROME_CANDIDATES),
        *FLAGS,
        f"--user-data-dir={PROFILE}-{name}",
        f"--window-size={size}",
        f"--screenshot={OUT_DIR / name}",
        f"http://127.0.0.1:{port}{path}",
    ]


def start_chrome(args: list[str]) -> subprocess.Popen:
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def kill_and_code(process: subprocess.Popen) -> int:
    return process.kill() or 1


def finish_code(process: subprocess.Popen) -> int:
    return kill_and_code(process) if process.poll() is None else process.returncode


def code_of(process: subprocess.Popen) -> int:
    with suppress(subprocess.TimeoutExpired):
        process.wait(timeout=120)
    return finish_code(process)


def guarded(args: list[str]) -> int:
    return code_of(start_chrome(args))


def shot(name: str, port: int, path: str, size: str) -> int:
    return guarded(args_of(name, port, path, size))


def log_shot(name: str, code: int) -> int:
    print(f"{name}: {'ok' if code == 0 else 'fail'}", flush=True)
    return code


def shot_and_log(name: str, port: int, path: str, size: str) -> int:
    return log_shot(name, shot(name, port, path, size))


def start_app(directory: Path, port: int) -> subprocess.Popen:
    return subprocess.Popen([first_existing(NODE_CANDIDATES), first_existing(NEXT_CANDIDATES), "start", "-p", str(port)], cwd=directory)


def start_apis() -> None:
    module = importlib.import_module("dev_apis")
    module.launch([module.server_of(name, port) for name, port in module.SERVICES])


def report(codes: list[int]) -> int:
    print(f"Снимков сохранено: {len([code for code in codes if code == 0])} из {len(codes)} → docs/screenshots")
    return 0 if all(code == 0 for code in codes) else 1


def finish(apps: list[subprocess.Popen], codes: list[int]) -> int:
    [app.terminate() for app in apps]
    return report(codes)


def capture(apps: list[subprocess.Popen]) -> int:
    [wait_for(port) for port in (3000, 3100)]
    return finish(apps, [shot_and_log(name, port, path, size) for name, port, path, size in PAGES])


def boot(apps: list[subprocess.Popen]) -> int:
    start_apis()
    return capture(apps)


def main() -> int:
    return boot([start_app(WEB_DIR, 3000), start_app(COCKPIT_DIR, 3100)])


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
