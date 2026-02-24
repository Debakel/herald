"""Tests for Publisher."""

from datetime import timedelta
from pathlib import Path

import freezegun

from herald.publish import Publisher, TargetEntry
from herald.targets.base import FakeTarget

TESTDATA = Path(__file__).parent / "testdata"


@freezegun.freeze_time("2026-02-03 08:00")
class TestPublisher:
    def test_publishes_rendered_message_to_target(self) -> None:
        target = FakeTarget()
        template = "{% for event in events %}{{ event.title }}\n{% endfor %}"
        publisher = Publisher(
            source=str(TESTDATA / "multiple-events.ics"),
            entries=[TargetEntry(target, template)],
            lookahead=timedelta(hours=24),
        )

        publisher.publish()

        assert len(target.published_messages) == 1
        assert target.published_messages[0] == "Team Meeting\nProduct Demo\n"

    def test_publishes_to_multiple_targets(self) -> None:
        target_a = FakeTarget()
        target_b = FakeTarget()
        publisher = Publisher(
            source=str(TESTDATA / "multiple-events.ics"),
            entries=[
                TargetEntry(target_a, "{{ count }} events"),
                TargetEntry(target_b, "{{ count }} evénements"),
            ],
            lookahead=timedelta(hours=24),
        )

        publisher.publish()

        assert target_a.published_messages == ["2 events"]
        assert target_b.published_messages == ["2 evénements"]

    def test_lookahead_window_filters_events(self) -> None:
        target = FakeTarget()
        template = "{% for event in events %}{{ event.title }}\n{% endfor %}"
        publisher = Publisher(
            source=str(TESTDATA / "multiple-events.ics"),
            entries=[TargetEntry(target, template)],
            lookahead=timedelta(days=7),
        )

        publisher.publish()

        message = target.published_messages[0]
        assert "Team Meeting" in message
        assert "Product Demo" in message
        assert "Code Review" in message
        assert "Sprint Planning" in message

    def test_single_post_mode_publishes_one_message_per_event(self) -> None:
        target = FakeTarget()
        template = "{{ event.title }}"
        publisher = Publisher(
            source=str(TESTDATA / "multiple-events.ics"),
            entries=[TargetEntry(target, template, post_mode="single")],
            lookahead=timedelta(hours=24),
        )

        publisher.publish()

        assert len(target.published_messages) == 2
        assert target.published_messages[0] == "Team Meeting"
        assert target.published_messages[1] == "Product Demo"

    def test_single_and_grouped_targets_together(self) -> None:
        single_target = FakeTarget()
        grouped_target = FakeTarget()
        publisher = Publisher(
            source=str(TESTDATA / "multiple-events.ics"),
            entries=[
                TargetEntry(single_target, "{{ event.title }}", post_mode="single"),
                TargetEntry(grouped_target, "{{ count }} events", post_mode="grouped"),
            ],
            lookahead=timedelta(hours=24),
        )

        publisher.publish()

        assert len(single_target.published_messages) == 2
        assert len(grouped_target.published_messages) == 1
        assert grouped_target.published_messages[0] == "2 events"

    def test_grouped_is_default_post_mode(self) -> None:
        entry = TargetEntry(FakeTarget(), "test")
        assert entry.post_mode == "grouped"
