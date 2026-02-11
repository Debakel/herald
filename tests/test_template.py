"""Tests for template rendering."""

from datetime import datetime
from zoneinfo import ZoneInfo

import freezegun

from herald.domain import Event
from herald import templating

sample_events = [
    Event(
        title="Team Meeting",
        start=datetime(2026, 2, 3, 10, 0, tzinfo=ZoneInfo("UTC")),
        end=datetime(2026, 2, 3, 11, 0, tzinfo=ZoneInfo("UTC")),
        location="Room A",
    ),
    Event(
        title="Code Review",
        start=datetime(2026, 2, 3, 14, 0, tzinfo=ZoneInfo("UTC")),
        end=datetime(2026, 2, 3, 15, 0, tzinfo=ZoneInfo("UTC")),
    ),
]


@freezegun.freeze_time("2000-02-01 12:30")
class TestRenderTemplateString:
    """Tests for render_template_string function."""

    def test_render_basic_template(self) -> None:
        """Test rendering a basic template."""
        template = "Events: {{ count }}"

        result = templating.render(template, sample_events)

        assert result == "Events: 2"

    def test_render_event_list(self) -> None:
        """Test rendering an event list."""
        template = "{% for event in events %}{{ event.title }}\n{% endfor %}"

        result = templating.render(template, sample_events)

        assert result == "Team Meeting\nCode Review\n"

    def test_render_conditional_location(self) -> None:
        """Test rendering with conditional location."""
        template = (
            "{% for event in events %}"
            "{{ event.title }}"
            "{% if event.location %} ({{ event.location }}){% endif %}\n"
            "{% endfor %}"
        )

        result = templating.render(template, sample_events)

        assert result == "Team Meeting (Room A)\nCode Review\n"

    def test_render_date(self) -> None:
        """Test rendering the date."""
        template = "Date: {{ today | datefmt }}"

        result = templating.render(template, sample_events, locale="de")
        assert result == "Date: 01.02.2000, 12:30:00"

        result = templating.render(template, sample_events, locale="en")
        assert result == "Date: Feb 1, 2000, 12:30:00 PM"
