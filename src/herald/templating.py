from datetime import datetime

from babel.dates import format_datetime
from jinja2 import Environment, Template

from herald.domain import Event


def render_single(template: str, event: Event, locale: str = "de"):
    template = _make_template(template, locale)
    return template.render(event=event, today=datetime.today(), events=[event])


def render_multiple(template: str, events: list[Event], locale: str = "de") -> str:
    tmpl = _make_template(template, locale)
    return tmpl.render(
        events=events,
        count=len(events),
        today=datetime.now(),
    )


def _make_template(template: str, locale: str) -> Template:
    env = Environment()
    env.filters["datefmt"] = lambda dt: format_datetime(dt, locale=locale)
    return env.from_string(template)
