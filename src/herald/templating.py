from datetime import datetime

from babel.dates import format_datetime
from jinja2 import Environment

from herald.domain import Event


def _make_env(locale: str = "de") -> Environment:
    env = Environment()
    env.filters["datefmt"] = lambda dt: format_datetime(dt, locale=locale)
    return env


def render(template: str, events: list[Event], locale: str = "de") -> str:
    env = _make_env(locale)
    tmpl = env.from_string(template)
    return tmpl.render(
        events=events,
        count=len(events),
        today=datetime.now(),
    )


def render_single(template: str, event: Event, locale: str = "de") -> str:
    env = _make_env(locale)
    tmpl = env.from_string(template)
    return tmpl.render(
        event=event,
        today=datetime.now(),
    )
