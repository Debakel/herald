import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from herald.repo import EventRepository
from herald.targets import Target
from herald import templating

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
        lookahead: timedelta,
    ):
        """
        :param source: Path or URL to the iCal source file
        :param entries: List of targets to publish
        :param lookahead: Time period to include
        """

        self.source = source
        self.entries = entries
        self.lookahead = lookahead
        self.repo = EventRepository(source=self.source)

    def publish(self):
        now = datetime.now()
        events = self.repo.list(start=now, end=now + self.lookahead)

        if not events:
            logger.info("No events found in the lookahead window")
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
