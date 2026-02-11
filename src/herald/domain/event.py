"""Domain models for calendar events."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Event:
    """Represents a calendar event."""

    title: str
    start: datetime
    end: datetime | None = None
    location: str | None = None
    description: str | None = None
    url: str | None = None

    def __lt__(self, other: "Event") -> bool:
        """Events are sorted by start time."""
        return self.start < other.start
