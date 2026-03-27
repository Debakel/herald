import logging
from dataclasses import dataclass
from enum import Enum

from herald import templating
from herald.domain.window import TimeWindow
from herald.repo import EventRepository
from herald.targets import Target

logger = logging.getLogger(__name__)


class PublishMode(Enum):
    SINGLE = "single"
    """One message per event."""
    GROUPED = "grouped"
    """All events combined into one message."""

@dataclass
class TargetEntry:
    target: Target
    template: str
    publish_mode: PublishMode = PublishMode.GROUPED


class Publisher:
    def __init__(
        self,
        source: str,
        entries: list[TargetEntry],
        time_window: TimeWindow,
    ):
        """
        :param source: Path or URL to the iCal source file
        :param entries: List of targets to publish
        :param time_window: Absolute time window used to query calendar events
        """

        self.source = source
        self.entries = entries
        self.time_window = time_window
        self.repo = EventRepository(source=self.source)

    def publish(self):
        events = self.repo.list(
            start=self.time_window.start,
            end=self.time_window.end,
        )

        if not events:
            logger.info("No events found in the configured window")
            return

        for entry in self.entries:
            if entry.publish_mode == PublishMode.SINGLE:
                for event in events:
                    message = templating.render_single(entry.template, event=event)
                    entry.target.publish(message)
            elif entry.publish_mode == PublishMode.GROUPED:
                message = templating.render_multiple(entry.template, events=events)
                entry.target.publish(message)
            else:
                raise NotImplementedError(f"Unsupported publish_mode: {entry.publish_mode}")
