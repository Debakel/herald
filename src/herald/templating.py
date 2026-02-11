from datetime import datetime

from babel.dates import format_datetime
from jinja2 import Environment

from herald.domain import Event


def render(template: str, events: list[Event], locale: str = "de") -> str:
    env = Environment()
    env.filters["datefmt"] = lambda dt: format_datetime(dt, locale=locale)
    tmpl = env.from_string(template)
    return tmpl.render(
        events=events,
        count=len(events),
        today=datetime.now(),
    )
