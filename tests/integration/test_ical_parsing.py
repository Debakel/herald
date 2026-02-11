"""Integration tests for iCal parsing."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


from herald.repo import EventRepository

TESTDATA_DIR = Path(__file__).parent.parent / "testdata"


class TestParseEvents:
    """Tests for parsing calendar events."""

    def test_parse_multiple_events(self) -> None:
        """Test parsing a calendar with multiple events."""
        tz = ZoneInfo("UTC")
        repo = EventRepository(TESTDATA_DIR / "multiple-events.ics")
        start = datetime(2026, 2, 1, 0, 0, tzinfo=tz)
        end = datetime(2026, 2, 10, 0, 0, tzinfo=tz)

        events = repo.list(start, end)

        assert len(events) == 4
        titles = [e.title for e in events]
        assert "Team Meeting" in titles
        assert "Product Demo" in titles
        assert "Code Review" in titles
        assert "Sprint Planning" in titles

    def test_parse_event_properties(self) -> None:
        """Test that event properties are correctly parsed."""
        tz = ZoneInfo("UTC")
        repo = EventRepository(TESTDATA_DIR / "multiple-events.ics")
        start = datetime(2026, 2, 3, 0, 0, tzinfo=tz)
        end = datetime(2026, 2, 4, 0, 0, tzinfo=tz)

        events = repo.list(start, end)

        team_meeting = next(e for e in events if e.title == "Team Meeting")
        assert team_meeting.location == "Conference Room A"
        assert team_meeting.description == "Weekly team sync"
        assert team_meeting.url == "https://example.com/team-meeting"

    def test_parse_recurring_event(self) -> None:
        """Test parsing recurring events."""
        tz = ZoneInfo("UTC")
        repo = EventRepository(TESTDATA_DIR / "recurring-event.ics")
        start = datetime(2026, 2, 1, 0, 0, tzinfo=tz)
        end = datetime(2026, 3, 1, 0, 0, tzinfo=tz)

        events = repo.list(start, end)

        # Should expand to 4 weekly occurrences
        assert len(events) == 4
        assert all(e.title == "Weekly Standup" for e in events)

    def test_parse_all_day_event(self) -> None:
        """Test parsing all-day events."""
        tz = ZoneInfo("UTC")
        calendar = EventRepository(TESTDATA_DIR / "all-day-event.ics")
        start = datetime(2026, 2, 1, 0, 0, tzinfo=tz)
        end = datetime(2026, 2, 10, 0, 0, tzinfo=tz)

        events = calendar.list(start, end)

        assert len(events) == 1
        assert events[0].title == "Company Holiday"

    def test_parse_empty_calendar(self) -> None:
        """Test parsing an empty calendar."""
        tz = ZoneInfo("UTC")
        calendar = EventRepository(TESTDATA_DIR / "empty.ics")
        start = datetime(2026, 2, 1, 0, 0, tzinfo=tz)
        end = datetime(2026, 2, 10, 0, 0, tzinfo=tz)

        events = calendar.list(start, end)

        assert len(events) == 0
