"""Domain logic for calendar events."""

from .event import Event
from .window import WindowParseError, parse_window

__all__ = [
    "Event",
    "WindowParseError",
    "parse_window",
]
