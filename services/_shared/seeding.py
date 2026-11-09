"""Детерминированная генерация данных: одинаковый сид даёт одинаковые цифры в демо и в тестах."""

from __future__ import annotations

MOD = 2147483647
MULT = 48271

CITIES = [
    ("Москва", "Россия", 55.75, 37.62),
    ("Санкт-Петербург", "Россия", 59.93, 30.33),
    ("Сочи", "Россия", 43.58, 39.72),
    ("Казань", "Россия", 55.79, 49.12),
    ("Калининград", "Россия", 54.71, 20.51),
    ("Владивосток", "Россия", 43.11, 131.88),
    ("Тбилиси", "Грузия", 41.69, 44.80),
    ("Стамбул", "Турция", 41.00, 28.97),
]

CHANNELS = ["web", "mobile", "partner", "b2b"]
SUPPLIERS = ["Ostrovok Direct", "Hotelbeds", "Expedia Partner", "WebBeds", "Local DMC"]
HOTEL_PREFIX = ["Гранд", "Сити", "Морской", "Северный", "Парк", "Бутик", "Резиденция", "Апарт"]
HOTEL_KIND = ["отель", "апартаменты", "хостел", "курорт"]


def seed_of(text: str) -> int:
    return (sum((index + 1) * ord(char) for index, char in enumerate(text)) * 7919) % MOD


def noise(seed: int) -> float:
    return (seed * MULT) % MOD / MOD


def series(seed: int, count: int) -> list[float]:
    return [noise(seed + index * 977) for index in range(count)]


def between(ratio: float, low: float, high: float) -> float:
    return low + (high - low) * ratio


def whole(ratio: float, low: int, high: int) -> int:
    return int(between(ratio, low, high + 1))


def pick(items: list, ratio: float) -> object:
    return items[min(len(items) - 1, int(ratio * len(items)))]


def hotel_name(index: int, city: str) -> str:
    return f"{HOTEL_PREFIX[index % len(HOTEL_PREFIX)]} {HOTEL_KIND[(index // len(HOTEL_PREFIX)) % len(HOTEL_KIND)]} {city}"


def day(index: int) -> str:
    return f"2026-11-{(index % 28) + 1:02d}"
