"""HTTP-слой сервиса «Эластичность цен»."""

from __future__ import annotations

from _shared.api import make_app

from . import marts

DB = marts.connect()

app = make_app(marts.META, lambda: marts.dashboard(DB), lambda payload: marts.widget(DB, payload))
