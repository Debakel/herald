"""Tests for Publisher."""

from datetime import datetime, timedelta
from pathlib import Path

import freezegun

from herald.domain import TimeWindow
from herald.publish import Publisher, PublishMode, TargetEntry
from herald.targets.base import FakeTarget

TESTDATA = Path(__file__).parent / "testdata"


@freezegun.freeze_time("2026-02-03 08:00")
class TestPublisher:
    def test_publishes_rendered_message_to_target(self) -> None:
        target = FakeTarget()
        template = "{% for event in events %}{{ event.title }}\n{% endfor %}"
        now = datetime.now()
        publisher = Publisher(
            source=str(TESTDATA / "multiple-events.ics"),
            entries=[TargetEntry(target, template)],
            time_window=TimeWindow(start=now, end=now + timedelta(hours=24)),
        )

        publisher.publish()

        assert len(target.published_messages) == 1
        assert target.published_messages[0] == "Team Meeting\nProduct Demo\n"

    def test_publishes_to_multiple_targets(self) -> None:
        target_a = FakeTarget()
        target_b = FakeTarget()
        now = datetime.now()
        publisher = Publisher(
            source=str(TESTDATA / "multiple-events.ics"),
            entries=[
                TargetEntry(target_a, "{% for event in events %}{{ event.title }}\n{% endfor %}", publish_mode=PublishMode.GROUPED),
                TargetEntry(target_b, "{{ event.title }}", publish_mode=PublishMode.SINGLE),
            ],
            time_window=TimeWindow(start=now, end=now + timedelta(hours=24)),
        )

        publisher.publish()

        assert target_a.published_messages == ["Team Meeting\nProduct Demo\n"]
        assert target_b.published_messages == ["Team Meeting", "Product Demo"]

    def test_window_filters_events(self) -> None:
        target = FakeTarget()
        template = "{% for event in events %}{{ event.title }}\n{% endfor %}"
        now = datetime.now()
        publisher = Publisher(
            source=str(TESTDATA / "multiple-events.ics"),
            entries=[TargetEntry(target, template)],
            time_window=TimeWindow(start=now, end=now + timedelta(days=7)),
        )

        publisher.publish()

        message = target.published_messages[0]
        assert "Team Meeting" in message
        assert "Product Demo" in message
        assert "Code Review" in message
        assert "Sprint Planning" in message

    def test_shifted_window_filters_early_events(self) -> None:
        target = FakeTarget()
        template = "{% for event in events %}{{ event.title }}\n{% endfor %}"
        now = datetime.now()
        publisher = Publisher(
            source=str(TESTDATA / "multiple-events.ics"),
            entries=[TargetEntry(target, template)],
            time_window=TimeWindow(
                start=now + timedelta(days=1),
                end=now + timedelta(days=2),
            ),
        )

        publisher.publish()

        assert target.published_messages == ["Code Review\n"]
