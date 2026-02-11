from datetime import datetime
from pathlib import Path

import httpx
import recurring_ical_events
from icalendar import Calendar

from herald.domain.event import Event


class EventRepository:
    def __init__(self, source: str | Path):
        self.source = source

    def list(self, start: datetime, end: datetime) -> list[Event]:
        # Use recurring_ical_events to expand recurring events
        ical_events = recurring_ical_events.of(self.get_calendar()).between(start, end)

        events: list[Event] = []
        for ical_event in ical_events:
            event = self._to_domain(ical_event=ical_event)
            if event:
                events.append(event)

        return events

    def get_calendar(self) -> Calendar:
        if not isinstance(self.source, Path) and (
            self.source.startswith("http://") or self.source.startswith("https://")
        ):
            response = httpx.get(self.source, timeout=3, follow_redirects=True)
            response.raise_for_status()
            return Calendar.from_ical(response.content)
        else:
            with open(self.source, "rb") as f:
                data = f.read()
            return Calendar.from_ical(data)

    def _to_domain(self, ical_event) -> Event:
        """Convert an icalendar event to a domain Event."""
        return Event(
            title=ical_event.get("SUMMARY"),
            start=ical_event.get("DTSTART").dt,
            end=ical_event.get("DTEND").dt,
            location=ical_event.get("LOCATION"),
            description=ical_event.get("DESCRIPTION"),
            url=ical_event.get("URL"),
        )
